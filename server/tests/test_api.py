import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

# We need to patch anthropic and os.getenv before importing main
with patch("os.getenv", return_value="fake-api-key"), patch("anthropic.Anthropic"):
    from main import app, ChatRequest, Message

client = TestClient(app)

def test_root_endpoint():
    """Test the root endpoint returns the welcome message"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the Barbot API! Send POST requests to /chat to interact with the mixologist."}

class MockContent:
    def __init__(self, text):
        self.text = text

class MockAnthropicResponse:
    def __init__(self, content):
        self.content = [MockContent(content)]

@pytest.mark.parametrize(
    "mock_response,expected_result",
    [
        # Test valid cocktail recipe response
        (
            '{"name":"Mojito","ingredients":["White rum","Fresh lime juice","Sugar","Mint leaves","Soda water"],"instructions":["Muddle mint leaves with sugar and lime juice","Add rum and fill glass with ice","Top with soda water and garnish with mint sprig"],"description":"A refreshing Cuban highball"}',
            {
                "response": {
                    "name": "Mojito",
                    "ingredients": ["White rum", "Fresh lime juice", "Sugar", "Mint leaves", "Soda water"],
                    "instructions": ["Muddle mint leaves with sugar and lime juice", "Add rum and fill glass with ice", "Top with soda water and garnish with mint sprig"],
                    "description": "A refreshing Cuban highball"
                }
            }
        ),
        # Test general response format
        (
            '{"response":"The Manhattan is a classic cocktail made with whiskey, sweet vermouth, and bitters."}',
            {
                "response": {
                    "response": "The Manhattan is a classic cocktail made with whiskey, sweet vermouth, and bitters."
                }
            }
        ),
        # Test handling invalid JSON response
        (
            'This is not valid JSON',
            {
                "response": {
                    "response": "This is not valid JSON"
                }
            }
        )
    ]
)
def test_chat_endpoint(mock_response, expected_result):
    """Test the chat endpoint with different mock responses from Claude"""
    # Prepare the request data
    request_data = {
        "messages": [
            {"role": "user", "content": "What is a mojito?"}
        ]
    }
    
    # Create a mock for the Anthropic client response
    mock_anthropic_response = MockAnthropicResponse(mock_response)
    
    # Patch the client.messages.create method correctly
    with patch("main.client.messages.create", return_value=mock_anthropic_response):
        response = client.post("/chat", json=request_data)
        
        # Check response is successful
        assert response.status_code == 200
        
        # Check the content matches expected result
        assert response.json() == expected_result

def test_chat_endpoint_exception_handling():
    """Test the chat endpoint handles exceptions properly"""
    request_data = {
        "messages": [
            {"role": "user", "content": "What is a mojito?"}
        ]
    }
    
    # Simulate an exception in the Anthropic API call
    with patch("main.client.messages.create", side_effect=Exception("API error")):
        response = client.post("/chat", json=request_data)
        
        # Check response is a 500 error
        assert response.status_code == 500
        assert "API error" in response.json()["detail"]

def test_invalid_request_format():
    """Test the chat endpoint validates the request format properly"""
    # Missing 'messages' field
    invalid_request = {}
    
    response = client.post("/chat", json=invalid_request)
    assert response.status_code == 422  # Unprocessable Entity
    
    # Empty messages array
    invalid_request = {"messages": []}
    
    # Here we need to also mock the Anthropic client to avoid a real API call
    with patch("main.client.messages.create", return_value=MockAnthropicResponse('{"response":"Empty message test"}')):
        response = client.post("/chat", json=invalid_request)
        # This should still be processed, but we should check that it doesn't crash
        assert response.status_code == 200
