import pytest
from pydantic import ValidationError
from unittest.mock import patch

# Import models from main using the same patch technique
with patch("os.getenv", return_value="fake-api-key"), patch("anthropic.Anthropic"):
    from main import Message, ChatRequest, ChatResponse

def test_message_model_valid():
    """Test valid message creation"""
    message = Message(role="user", content="Hello, world")
    assert message.role == "user"
    assert message.content == "Hello, world"

def test_message_model_invalid_role():
    """Test message validation with invalid role"""
    with pytest.raises(ValidationError):
        # role must be a string
        Message(role=123, content="Hello, world")

def test_message_model_invalid_content():
    """Test message validation with invalid content"""
    with pytest.raises(ValidationError):
        # content must be a string
        Message(role="user", content=123)

def test_message_model_missing_fields():
    """Test message validation with missing fields"""
    with pytest.raises(ValidationError):
        # role is required
        Message(content="Hello, world")

    with pytest.raises(ValidationError):
        # content is required
        Message(role="user")

def test_chat_request_model_valid():
    """Test valid chat request creation"""
    request = ChatRequest(messages=[
        Message(role="user", content="Hello"),
        Message(role="assistant", content="Hi there")
    ])
    assert len(request.messages) == 2
    assert request.messages[0].role == "user"
    assert request.messages[1].role == "assistant"

def test_chat_request_model_invalid():
    """Test chat request validation with invalid messages"""
    with pytest.raises(ValidationError):
        # messages must be a list of Message objects
        ChatRequest(messages="not a list")

def test_chat_response_model_valid():
    """Test valid chat response creation"""
    response = ChatResponse(response={"name": "Mojito", "ingredients": ["rum", "mint"]})
    assert response.response["name"] == "Mojito"
    assert "rum" in response.response["ingredients"]

def test_chat_response_model_invalid():
    """Test chat response validation with invalid response"""
    with pytest.raises(ValidationError):
        # response must be a dictionary
        ChatResponse(response="not a dict")
