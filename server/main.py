import os
import json
from typing import List, Dict, Any, Optional
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
  "ingredients": ["Ingredient 1", "Ingredient 2", ...],
  "instructions": ["Step 1", "Step 2", ...],
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

@app.get("/")
async def root():
    return {"message": "Welcome to the Barbot API! Send POST requests to /chat to interact with the mixologist."}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # Convert messages to the format expected by Anthropic
        formatted_messages = [{"role": msg.role, "content": msg.content} for msg in request.messages]
        
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