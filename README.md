# Barbot

Barbot is a virtual mixologist chat application that provides cocktail recipes and answers questions about mixology.

## Components

- **Server**: Python backend using FastAPI and the Anthropic API to interact with Claude's AI
- **Web UI**: React-based frontend that provides a chat interface similar to Claude.ai
- **Authentication**: JWT-based authentication system to secure the application

## Setup

### Option 1: Docker (Recommended)

1. Copy the example environment file and add your Anthropic API key and a secret key for JWT:
   
   cp .env.example .env
   # Edit .env with your Anthropic API key and a secure SECRET_KEY
   

2. Build and start the Docker containers:
   
   docker-compose up -d
   

3. Access the application at http://localhost

### Option 2: Manual Setup

#### Server

1. Navigate to the server directory:
   
   cd server
   

2. Create a virtual environment:
   
   python -m venv venv
   source venv/bin/activate  # On Windows: venv/Scripts/activate
   

3. Install dependencies:
   
   pip install -r requirements.txt
   

4. Create a .env file with your API keys:
   
   ANTHROPIC_API_KEY=your-api-key-here
   SECRET_KEY=your-secure-random-key-here
   ACCESS_TOKEN_EXPIRE_MINUTES=30
   

5. Run the server:
   
   uvicorn main:app --reload
   

#### Web UI

1. Navigate to the web directory:
   
   cd web
   

2. Install dependencies:
   
   npm install
   

3. Run the development server:
   
   npm start
   

## Usage

Once both the server and web UI are running, open your browser to interact with Barbot.

1. Register for an account or use the default credentials:
   - Username: admin
   - Password: adminpassword

2. After logging in, you can ask Barbot for cocktail recipes or mixology advice, and it will respond with properly formatted information.

## Authentication

Barbot uses JWT (JSON Web Token) authentication to secure the API:

- **Registration**: New users can register with a username, email, and password
- **Login**: Users can sign in with their credentials to receive a JWT token
- **Protected Routes**: The chat endpoint is protected and requires authentication
- **Token Expiration**: Tokens expire after a configurable period (default: 30 minutes)

## Development with Docker

### Running in development mode

To run the application in development mode with hot-reloading:


docker-compose -f docker-compose.yml -f docker-compose.dev.yml up


### Rebuilding containers

After making changes to the code or dependencies, rebuild the containers:


docker-compose build


### Viewing logs

To view the logs of the running containers:


docker-compose logs -f


## Testing

### Backend Tests

To run backend tests:


cd server
python -m pytest


### Frontend Tests

To run frontend tests:


cd web
npm test


## Security Considerations

- In production, you should set a strong, random SECRET_KEY
- Enable HTTPS to protect token transmission
- Configure proper CORS settings in the FastAPI server
- Use a proper database instead of the in-memory user storage
