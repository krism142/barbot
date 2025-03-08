# Barbot

Barbot is a virtual mixologist chat application that provides cocktail recipes and answers questions about mixology.

## Components

- **Server**: Python backend using FastAPI and the Anthropic API to interact with Claude's AI
- **Web UI**: React-based frontend that provides a chat interface similar to Claude.ai

## Setup

### Option 1: Docker (Recommended)

1. Copy the example environment file and add your Anthropic API key:
   ```
   cp .env.example .env
   # Edit .env with your Anthropic API key
   ```

2. Build and start the Docker containers:
   ```
   docker-compose up -d
   ```

3. Access the application at `http://localhost`

### Option 2: Manual Setup

#### Server

1. Navigate to the server directory:
   ```
   cd server
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file with your Anthropic API key:
   ```
   ANTHROPIC_API_KEY=your-api-key-here
   ```

5. Run the server:
   ```
   uvicorn main:app --reload
   ```

#### Web UI

1. Navigate to the web directory:
   ```
   cd web
   ```

2. Install dependencies:
   ```
   npm install
   ```

3. Run the development server:
   ```
   npm start
   ```

## Usage

Once both the server and web UI are running, open your browser to interact with Barbot.

Ask for cocktail recipes or mixology advice, and Barbot will respond with properly formatted information.

## Development with Docker

### Running in development mode

To run the application in development mode with hot-reloading:

```
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Rebuilding containers

After making changes to the code or dependencies, rebuild the containers:

```
docker-compose build
```

### Viewing logs

To view the logs of the running containers:

```
docker-compose logs -f
```