import unittest
from unittest.mock import patch, MagicMock
import json
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '')))

from main import app
import auth
from database import User, Base, get_db

# Set up a test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

class TestAuthentication(unittest.TestCase):
    def setUp(self):
        # Create test database and tables
        Base.metadata.create_all(bind=engine)
        
        # Add test user
        db = TestingSessionLocal()
        try:
            # Clean up any existing users
            db.query(User).delete()
            db.commit()
            
            # Add test user
            hashed_password = auth.get_password_hash("testpassword")
            test_user = User(
                username="testuser",
                email="test@example.com",
                full_name="Test User",
                hashed_password=hashed_password,
                disabled=False
            )
            db.add(test_user)
            db.commit()
        finally:
            db.close()
    
    def tearDown(self):
        # Clean up the test database
        Base.metadata.drop_all(bind=engine)
    
    def test_get_password_hash(self):
        # Test that hashing a password works
        hashed = auth.get_password_hash("password123")
        self.assertTrue(hashed)
        self.assertNotEqual(hashed, "password123")
    
    def test_verify_password(self):
        # Test password verification
        password = "password123"
        hashed = auth.get_password_hash(password)
        self.assertTrue(auth.verify_password(password, hashed))
        self.assertFalse(auth.verify_password("wrongpassword", hashed))
    
    def test_create_access_token(self):
        # Test token creation
        data = {"sub": "testuser"}
        expires_delta = timedelta(minutes=15)
        token = auth.create_access_token(data, expires_delta)
        self.assertTrue(token)
    
    def test_login_endpoint_successful(self):
        # Test successful login
        response = client.post(
            "/token",
            data={"username": "testuser", "password": "testpassword"}
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertIn("access_token", result)
        self.assertEqual(result["token_type"], "bearer")
    
    def test_login_endpoint_invalid_credentials(self):
        # Test login with invalid credentials
        response = client.post(
            "/token",
            data={"username": "testuser", "password": "wrongpassword"}
        )
        self.assertEqual(response.status_code, 401)
    
    def test_register_endpoint(self):
        # Test user registration
        response = client.post(
            "/register",
            json={
                "username": "newuser",
                "email": "new@example.com",
                "password": "newpassword"
            }
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["username"], "newuser")
        self.assertEqual(result["email"], "new@example.com")
        
        # Verify user was added to database
        db = TestingSessionLocal()
        try:
            user = db.query(User).filter(User.username == "newuser").first()
            self.assertIsNotNone(user)
            self.assertEqual(user.email, "new@example.com")
        finally:
            db.close()
    
    def test_register_duplicate_username(self):
        # Test registration with existing username
        response = client.post(
            "/register",
            json={
                "username": "testuser",
                "email": "another@example.com",
                "password": "password123"
            }
        )
        self.assertEqual(response.status_code, 400)
    
    def test_get_current_user(self):
        # Test authentication middleware
        # First login to get token
        response = client.post(
            "/token",
            data={"username": "testuser", "password": "testpassword"}
        )
        token = response.json()["access_token"]
        
        # Use token to access protected endpoint
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result["username"], "testuser")
    
    def test_protected_endpoint_no_token(self):
        # Test protected endpoint without token
        response = client.get("/users/me")
        self.assertEqual(response.status_code, 401)
    
    def test_chat_endpoint_authentication(self):
        # Test chat endpoint authentication
        # First login to get token
        response = client.post(
            "/token", 
            data={"username": "testuser", "password": "testpassword"}
        )
        token = response.json()["access_token"]
        
        # Use token to access protected chat endpoint
        with patch('anthropic.Anthropic.messages.create') as mock_create:
            # Create a mock response for the Anthropic API
            mock_response = MagicMock()
            mock_response.content = [MagicMock(text='{"response": "Test response"}')]
            mock_create.return_value = mock_response
            
            response = client.post(
                "/chat",
                headers={"Authorization": f"Bearer {token}"},
                json={"messages": [{"role": "user", "content": "Hello"}]}
            )
        
        self.assertEqual(response.status_code, 200)
    
    def test_chat_endpoint_no_token(self):
        # Test chat endpoint without token
        response = client.post(
            "/chat",
            json={"messages": [{"role": "user", "content": "Hello"}]}
        )
        self.assertEqual(response.status_code, 401)

if __name__ == "__main__":
    unittest.main()
