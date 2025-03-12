import os
import json
import re
from datetime import timedelta
from typing import List, Dict, Any, Optional, Tuple, Set
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic
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

# Initialize FastAPI app
app = FastAPI(title="Barbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, you should specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# System prompt for the input validation
VALIDATION_PROMPT = """
You are a validation system that determines if user messages are related to cocktails, mixology, bartending, or alcoholic beverages.

Respond with ONLY "YES" or "NO" based on whether the user's input is related to any of these topics:
- Cocktails, mixed drinks, or drink recipes
- Alcoholic beverages (spirits, liquors, beer, wine, etc.)
- Bartending techniques or equipment
- Ingredients used in cocktails
- Drinking culture or customs

Do not include ANY explanations or additional text in your response, just "YES" or "NO".
"""

# Pydantic models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    response: Dict[str, Any]

# Function to validate if the message is related to cocktails or mixed drinks using Claude
async def is_cocktail_related(message: str) -> Tuple[bool, str]:
    """
    Use Claude to determine if the message is related to cocktails or mixed drinks.
    
    Args:
        message: The user's message
        
    Returns:
        A tuple of (is_valid, reason)
    """
    try:
        # Call Claude with a validation prompt
        validation_response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            system=VALIDATION_PROMPT,
            max_tokens=10,  # We only need YES or NO
            messages=[
                {"role": "user", "content": message}
            ]
        )
        
        # Extract the response text
        response_text = validation_response.content[0].text.strip().upper()
        
        # Check if the response is "YES"
        if response_text == "YES":
            return True, ""
        else:
            return False, "I'm a mixologist specializing in cocktails and drinks. Please ask me questions related to mixology, cocktails, or drink recipes."
    except Exception as e:
        # If validation fails, default to allowing the message to avoid blocking legitimate queries
        print(f"Validation error: {e}")
        return True, ""

# Authentication routes
@app.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/register", response_model=UserResponse)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    db_user = add_user(db, user_data)
    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already exists",
        )
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
    current_user: User = Depends(get_current_active_user)
):
    try:
        # Convert messages to the format expected by Anthropic
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Get the user's most recent message (the last user message)
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if user_messages:
            latest_user_message = user_messages[-1].content
            # Validate if the message is cocktail-related
            is_valid, reason = await is_cocktail_related(latest_user_message)
            
            if not is_valid:
                # Return a helpful error message
                return {"response": {"response": reason}}
        
        # Call Anthropic API for the main response
        response = client.messages.create(
            model="claude-3-7-sonnet-20250219",
            system=SYSTEM_PROMPT,
            max_tokens=2000,
            messages=formatted_messages
        )
        
        # The response from Claude will be a JSON string in the content
        response_text = response.content[0].text
        
        # Parse the JSON response
        try:
            parsed_response = json.loads(response_text)
            return {"response": parsed_response}
        except json.JSONDecodeError:
            # If for some reason Claude doesn't return valid JSON, wrap it in our format
            return {"response": {"response": response_text}}
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Startup event to initialize admin user
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    create_admin_user(db)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
