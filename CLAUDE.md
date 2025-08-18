# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Barbot is a virtual mixologist chat application that provides cocktail recipes and answers questions about mixology. The application consists of:

- **Backend**: Python FastAPI server using Anthropic's Claude Sonnet 4 API for AI responses
- **Frontend**: React-based web UI with chat interface and authentication
- **Authentication**: JWT-based authentication with PostgreSQL storage
- **Database**: PostgreSQL for persistent user credential storage
- **Logging**: Structured logging with correlation IDs for observability

## Development Commands

### Backend (Python/FastAPI)
```bash
# Setup and run server
cd server
python -m venv venv
source venv/bin/activate  # Windows: venv/Scripts/activate
pip install -r requirements.txt
uvicorn main:app --reload

# Run tests
python -m pytest
python -m pytest --cov  # With coverage

# Test specific files
python -m pytest tests/test_auth.py
python -m pytest tests/test_api.py
```

### Frontend (React)
```bash
# Setup and run
cd web
npm install
npm start

# Run tests
npm test
npm run test:coverage  # With coverage (80% threshold configured)

# Build for production
npm run build
```

### Docker Development
```bash
# Standard development with hot-reload
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up

# Rebuild containers after code changes
docker-compose build

# View logs
docker-compose logs -f

# Access PostgreSQL database
docker exec -it barbot-db psql -U barbot -d barbot
```

## Architecture

### Authentication Flow
- JWT tokens issued via `/token` endpoint with username/password
- Tokens expire after 30 minutes (configurable via ACCESS_TOKEN_EXPIRE_MINUTES)
- Protected endpoints require Bearer token in Authorization header
- Admin user (admin/adminpassword) created automatically on startup
- Full React authentication integration with AuthContext

### AI Integration
- Uses Claude Sonnet 4 (claude-sonnet-4-20250514) for cocktail responses
- Efficient keyword-based validation for cocktail-related queries
- Structured JSON responses for consistent UI rendering
- Comprehensive error handling for API failures

### Database Schema
- **User Model**: id, username (unique), email (unique), full_name, hashed_password, disabled
- **SQLAlchemy ORM**: database.py defines models and session management
- **Migrations**: Uses Alembic for database migrations

### API Structure
- **Authentication**: `/token` (login), `/register` (user creation)
- **Chat**: `/chat` (protected endpoint for AI interactions)
- **Users**: `/users/me` (current user info)

### Frontend Architecture
- **Components**: Auth components (AuthPage, LoginForm, RegisterForm), Chat components (ChatInput, ChatMessage)
- **Context**: AuthContext for global authentication state management
- **Styling**: TailwindCSS for styling
- **Testing**: Jest with React Testing Library, MSW for API mocking

## Environment Variables

Required environment variables:
- `ANTHROPIC_API_KEY`: Your Anthropic API key
- `SECRET_KEY`: JWT signing secret (use strong random key in production)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)
- `DATABASE_URL`: PostgreSQL connection string

## Key Files

- `server/main.py`: FastAPI application and chat endpoint
- `server/auth.py`: JWT authentication logic and user management
- `server/database.py`: SQLAlchemy models and database configuration
- `web/src/App.js`: Main React application with routing
- `web/src/context/AuthContext.js`: Authentication state management
- `web/src/components/auth/`: Authentication UI components

## Testing

### Backend Tests
- `tests/test_auth.py`: Authentication and user management tests
- `tests/test_api.py`: API endpoint tests
- `tests/test_models.py`: Database model tests
- Coverage configured with pytest-cov

### Frontend Tests
- Jest configuration with 80% coverage threshold
- Component tests in `src/components/**/*.test.js`
- Context tests in `src/tests/`
- MSW for API mocking

## Database Operations

The application uses PostgreSQL with SQLAlchemy ORM:
- Tables are created automatically on startup via `create_tables()`
- Admin user is created if not exists on startup
- Session management handled via dependency injection pattern