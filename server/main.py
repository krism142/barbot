import os
import json
import re
import uuid
import logging
from datetime import timedelta
from typing import List, Dict, Any, Optional, Tuple, Set
from fastapi import FastAPI, HTTPException, Depends, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic
import structlog
from sqlalchemy.orm import Session

# Import authentication modules
from auth import (
    Token, UserResponse, UserCreate, authenticate_user, 
    create_access_token, get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES, add_user, User,
    create_admin_user
)

from database import get_db

# Load environment variables
load_dotenv()

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Initialize logger
logger = structlog.get_logger()

# Initialize FastAPI app
app = FastAPI(title="Barbot API")

# Configure CORS
allowed_origins = os.getenv(
    "ALLOWED_ORIGINS", 
    "http://localhost:3000,http://localhost:8081,http://127.0.0.1:3000,http://127.0.0.1:8081"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

# Add correlation ID and logging middleware
@app.middleware("http")
async def add_correlation_id_and_logging(request: Request, call_next):
    correlation_id = str(uuid.uuid4())
    
    # Bind correlation ID to logger context
    logger_with_context = logger.bind(
        correlation_id=correlation_id,
        method=request.method,
        path=request.url.path,
        client_ip=request.client.host if request.client else None
    )
    
    # Log request start
    logger_with_context.info("Request started")
    
    # Store correlation ID in request state
    request.state.correlation_id = correlation_id
    request.state.logger = logger_with_context
    
    try:
        response = await call_next(request)
        
        # Log successful response
        logger_with_context.info(
            "Request completed",
            status_code=response.status_code,
            response_time_ms=(getattr(request.state, 'start_time', 0) - getattr(request.state, 'start_time', 0)) * 1000
        )
        
        # Add correlation ID to response headers
        response.headers["X-Correlation-ID"] = correlation_id
        return response
        
    except Exception as e:
        # Log error
        logger_with_context.error(
            "Request failed",
            error=str(e),
            error_type=type(e).__name__
        )
        raise

# Initialize Anthropic client
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    raise ValueError("ANTHROPIC_API_KEY environment variable not set")

client = anthropic.Anthropic(api_key=api_key)

# System prompt for the mixologist
SYSTEM_PROMPT = """
You are a mixologist with over 20 years of experience. When asked about a specific cocktail or for a cocktail recipe, respond ONLY with a JSON object in the following format:
{
  "name": "Cocktail Name",
  "ingredients": ["Ingredient 1", "Ingredient 2", .],
  "instructions": ["Step 1", "Step 2", .],
  "description": "A brief description of the cocktail"
}
For all other questions or topics, respond with:
{
  "response": "Your detailed answer here"
}
Do not include any text outside of these JSON objects in your responses.
"""


# Pydantic models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    response: Dict[str, Any]

# Cocktail-related keywords for efficient validation
COCKTAIL_KEYWORDS = {
    # Drink types
    'cocktail', 'drink', 'beverage', 'shot', 'martini', 'manhattan', 'mojito', 'margarita',
    'old fashioned', 'negroni', 'whiskey sour', 'cosmopolitan', 'daiquiri', 'gimlet',
    'bloody mary', 'mai tai', 'pina colada', 'long island', 'moscow mule', 'mudslide',
    
    # Spirits and liquors
    'vodka', 'gin', 'whiskey', 'whisky', 'rum', 'tequila', 'bourbon', 'scotch', 'brandy',
    'cognac', 'liqueur', 'schnapps', 'absinthe', 'mezcal', 'rye', 'irish', 'single malt',
    
    # Wine and beer
    'wine', 'champagne', 'prosecco', 'beer', 'ale', 'lager', 'stout', 'porter', 'ipa',
    'sangria', 'punch', 'mulled wine', 'sherry', 'port', 'vermouth',
    
    # Mixers and ingredients
    'mixer', 'tonic', 'soda', 'ginger beer', 'simple syrup', 'bitters', 'garnish',
    'lime', 'lemon', 'orange', 'cherry', 'olive', 'mint', 'basil', 'muddle', 'shake',
    'stir', 'strain', 'rocks', 'neat', 'dirty', 'dry', 'sweet', 'sour',
    
    # Bar terms and equipment
    'bartender', 'mixology', 'mixologist', 'bar', 'shaker', 'jigger', 'strainer',
    'muddler', 'recipe', 'ingredients', 'glass', 'rocks glass', 'martini glass',
    'highball', 'lowball', 'coupe', 'flute', 'shot glass', 'pint',
    
    # Preparation methods
    'on the rocks', 'straight up', 'with a twist', 'extra dry', 'extra dirty',
    'double', 'triple', 'float', 'layered', 'frozen', 'blended', 'chilled',
    'garnished', 'rimmed', 'salted', 'sugared'
}

def is_cocktail_related(message: str) -> Tuple[bool, str]:
    """
    Efficiently determine if the message is related to cocktails or mixed drinks using keywords.
    
    Args:
        message: The user's message
        
    Returns:
        A tuple of (is_valid, reason)
    """
    message_lower = message.lower()
    
    # Check if any cocktail-related keywords are present
    for keyword in COCKTAIL_KEYWORDS:
        if keyword in message_lower:
            return True, ""
    
    # If no keywords found, it's likely not cocktail-related
    return False, "I'm a mixologist specializing in cocktails and drinks. Please ask me questions related to mixology, cocktails, or drink recipes."

# Authentication routes
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
    req: Request = None
):
    req_logger = getattr(req.state, 'logger', logger) if req else logger
    req_logger.info("Login attempt", username=form_data.username)
    
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        req_logger.warning("Login failed - invalid credentials", username=form_data.username)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    req_logger.info("Login successful", user_id=user.id, username=user.username)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=UserResponse)
async def register_user(
    user_data: UserCreate, 
    db: Session = Depends(get_db),
    req: Request = None
):
    req_logger = getattr(req.state, 'logger', logger) if req else logger
    req_logger.info("User registration attempt", username=user_data.username, email=user_data.email)
    
    db_user = add_user(db, user_data)
    if not db_user:
        req_logger.warning("Registration failed - user already exists", username=user_data.username, email=user_data.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )
    
    req_logger.info("User registration successful", user_id=db_user.id, username=db_user.username)
    return db_user

@app.get("/users/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

# API endpoints
@app.get("/")
async def root():
    return {"message": "Welcome to the Barbot API! Send POST requests to /chat to interact with the mixologist."}

@app.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest, 
    current_user: User = Depends(get_current_active_user),
    req: Request = None
):
    req_logger = getattr(req.state, 'logger', logger) if req else logger
    req_logger = req_logger.bind(user_id=current_user.id, username=current_user.username)
    
    req_logger.info("Chat request received", message_count=len(request.messages))
    
    try:
        # Convert messages to the format expected by Anthropic
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Get the user's most recent message (the last user message)
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if user_messages:
            latest_user_message = user_messages[-1].content
            req_logger.info("Validating user message", message_length=len(latest_user_message))
            
            # Validate if the message is cocktail-related
            is_valid, reason = is_cocktail_related(latest_user_message)
            
            if not is_valid:
                req_logger.warning("Message validation failed", reason=reason)
                return {"response": {"response": reason}}
            
            req_logger.info("Message validation passed")
        
        # Call Anthropic API for the main response
        req_logger.info("Calling Anthropic API with Claude Sonnet 4")
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            system=SYSTEM_PROMPT,
            max_tokens=2000,
            messages=formatted_messages
        )
        
        # The response from Claude will be a JSON string in the content
        response_text = response.content[0].text
        req_logger.info("Received response from Anthropic", response_length=len(response_text))
        
        # Parse the JSON response
        try:
            parsed_response = json.loads(response_text)
            req_logger.info("Successfully parsed JSON response")
            return {"response": parsed_response}
        except json.JSONDecodeError as json_error:
            req_logger.warning("Failed to parse JSON response", error=str(json_error))
            # If for some reason Claude doesn't return valid JSON, wrap it in our format
            return {"response": {"response": response_text}}
            
    except anthropic.BadRequestError as e:
        req_logger.error("Bad request to Anthropic API", error=str(e))
        raise HTTPException(status_code=400, detail="Invalid request to AI service")
    except anthropic.AuthenticationError as e:
        req_logger.error("Authentication error with Anthropic API", error=str(e))
        raise HTTPException(status_code=500, detail="AI service authentication failed")
    except anthropic.RateLimitError as e:
        req_logger.error("Rate limit exceeded for Anthropic API", error=str(e))
        raise HTTPException(status_code=429, detail="AI service rate limit exceeded")
            
    except Exception as e:
        req_logger.error("Chat request failed", error=str(e), error_type=type(e).__name__)
        raise HTTPException(status_code=500, detail=str(e))

# Startup event to initialize admin user
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup initiated")
    try:
        db = next(get_db())
        create_admin_user(db)
        logger.info("Application startup completed successfully")
    except Exception as e:
        logger.error("Application startup failed", error=str(e), error_type=type(e).__name__)
        raise

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
