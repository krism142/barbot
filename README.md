# Barbot

Barbot is a virtual mixologist chat application that provides cocktail recipes and answers questions about mixology.

## Components

- **Server**: Python backend using FastAPI and the Anthropic API to interact with Claude's AI
- **Web UI**: React-based frontend that provides a chat interface similar to Claude.ai

## Setup

### Server

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

### Web UI

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
   npm run dev
   ```

## Usage

Once both the server and web UI are running, open your browser to `http://localhost:3000` to interact with Barbot.

Ask for cocktail recipes or mixology advice, and Barbot will respond with properly formatted information.