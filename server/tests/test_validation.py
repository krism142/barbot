import sys
import os
import pytest
from pathlib import Path

# Add the parent directory to the Python path so we can import main
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import is_cocktail_related

def test_is_cocktail_related_positive():
    """Test that cocktail-related queries are correctly identified."""
    cocktail_queries = [
        "How do I make a Mojito?",
        "What's in a Manhattan?",
        "Tell me about the history of martinis",
        "What's a good cocktail with rum?",
        "I need a recipe for margarita",
        "What's the difference between bourbon and whiskey?",
        "How can I garnish my gin and tonic?",
        "What's the best tequila for a paloma?"
    ]

    for query in cocktail_queries:
        is_valid, _ = is_cocktail_related(query)
        assert is_valid, f"Query should be valid: {query}"

def test_is_cocktail_related_negative():
    """Test that non-cocktail queries are correctly rejected."""
    non_cocktail_queries = [
        "What's the weather today?",
        "Tell me a joke",
        "How do I reset my password?",
        "What's the capital of France?",
        "Who won the Super Bowl?",
        "Can you help me with my math homework?",
        "What's the meaning of life?"
    ]

    for query in non_cocktail_queries:
        is_valid, reason = is_cocktail_related(query)
        assert not is_valid, f"Query should be invalid: {query}"
        assert reason, "Reason should not be empty for invalid queries"

def test_edge_cases():
    """Test edge cases for the validation function."""
    # Empty message
    is_valid, reason = is_cocktail_related("")
    assert not is_valid, "Empty message should be invalid"
    
    # Single keyword
    is_valid, _ = is_cocktail_related("gin")
    assert is_valid, "Single keyword should be valid"
    
    # Case insensitivity
    is_valid, _ = is_cocktail_related("MARTINI")
    assert is_valid, "Validation should be case-insensitive"

    # Keyword as part of a different word
    is_valid, _ = is_cocktail_related("I need to bargain for a better price")
    assert not is_valid, "Keyword as part of another word should not match"
