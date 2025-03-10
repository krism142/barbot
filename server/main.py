import os
import json
import re
from typing import List, Dict, Any, Optional, Tuple, Set
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
import anthropic

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

# Cocktail and drink-related keywords for input validation
COCKTAIL_KEYWORDS: Set[str] = {
    "cocktail", "drink", "mixed drink", "mixer", "mixology", "bartend", "bartending", "bar", "liquor",
    "spirit", "alcohol", "rum", "vodka", "gin", "whiskey", "whisky", "bourbon", "scotch", "tequila",
    "mezcal", "brandy", "cognac", "wine", "beer", "ale", "lager", "stout", "ipa", "cider",
    "champagne", "prosecco", "vermouth", "bitters", "amaretto", "aperitif", "digestif",
    "martini", "manhattan", "mojito", "margarita", "daiquiri", "mimosa", "bellini", "spritz",
    "negroni", "old fashioned", "mai tai", "pina colada", "bloody mary", "cosmopolitan", "sour",
    "highball", "lowball", "shot", "shooter", "rocks", "neat", "straight", "up", "on the rocks",
    "garnish", "mixer", "soda", "tonic", "juice", "lime", "lemon", "orange", "cranberry",
    "grenadine", "simple syrup", "sugar", "salt", "ice", "shaken", "stirred", "blend", "muddle",
    "strain", "glass", "cup", "mug", "flute", "tumbler", "coupe", "snifter", "recipe"
}

# Pydantic models
class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

class ChatResponse(BaseModel):
    response: Dict[str, Any]

# Function to validate if the message is related to cocktails or mixed drinks
def is_cocktail_related(message: str) -> Tuple[bool, str]:
    """
    Check if the message is related to cocktails or mixed drinks.
    
    Args:
        message: The user's message
        
    Returns:
        A tuple of (is_valid, reason)
    """
    # Convert to lowercase for case-insensitive matching
    message_lower = message.lower()
    
    # Check if any cocktail keyword is present in the message
    for keyword in COCKTAIL_KEYWORDS:
        if keyword in message_lower:
            return True, ""
    
    return False, "I'm a mixologist specializing in cocktails and drinks. Please ask me questions related to mixology, cocktails, or drink recipes."

@app.get("/")
async def root():
    return {"message": "Welcome to the Barbot API! Send POST requests to /chat to interact with the mixologist."}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Convert messages to the format expected by Anthropic
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
        # Get the user's most recent message (the last user message)
        user_messages = [msg for msg in request.messages if msg.role == "user"]
        if user_messages:
            latest_user_message = user_messages[-1].content
            # Validate if the message is cocktail-related
            is_valid, reason = is_cocktail_related(latest_user_message)
            
            if not is_valid:
                # Return a helpful error message
                return {"response": {"response": reason}}
        
        # Call Anthropic API
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
