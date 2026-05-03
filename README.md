# Gemma4 AI Chatbot

A full-stack AI chatbot application featuring a FastAPI backend and a responsive, ChatGPT-inspired web interface. It leverages Ollama for local LLM inference and supports real-time streaming responses and persistent chat history.

## Features

- **Real-time Streaming:** Smooth, token-by-token response rendering.
- **Session Management:** Persistent chat history stored locally.
- **Ollama Integration:** Optimized for running local models like `gemma4:e2b`.
- **Modern UI:** Clean, dark-mode interface with a sidebar for chat history.
- **Docker Ready:** Easy deployment using Docker and Docker Compose.
- **Extensible Tools:** Built-in support for LangChain-style tools (e.g., directory creation).

## Project Structure

```text
gemma4/
├── backend.py          # FastAPI application logic
├── tools.py            # LangChain-based tools for AI capabilities
├── templates/          # HTML/CSS/JS frontend
├── history.json        # Persistent chat records
├── Dockerfile          # Container configuration
└── docker-compose.yml  # Multi-container orchestration
```

## Prerequisites

- Python 3.11+
- [Ollama](https://ollama.ai/) installed and running locally.
- (Optional) Docker and Docker Compose.

## Getting Started

### Local Setup

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Pull the Model:**
   Ensure Ollama is running and pull the required model:
   ```bash
   ollama pull gemma4:e2b
   ```

3. **Run the Backend:**
   ```bash
   python main.py
   ```
   The app will be available at `http://localhost:8000`.

### Docker Setup

1. **Run with Docker Compose:**
   ```bash
   docker-compose up -d
   ```
   This command starts both the Ollama engine and the Python application.

## Configuration

Environment variables can be configured in a `.env` file:

- `MODEL_NAME`: The Ollama model to use (default: `gemma4:e2b`).
- `OLLAMA_HOST`: The URL of your Ollama instance.
- `HISTORY_FILE`: Path to the JSON file for storing chats.
- `PORT`: The port the backend runs on (default: `8000`).

## Usage

- **New Chat:** Click the "+ New chat" button in the sidebar to start a fresh session.
- **History:** Previous conversations are automatically saved and accessible via the sidebar.
- **Markdown Support:** The chatbot supports markdown formatting, including code blocks with syntax highlighting.
