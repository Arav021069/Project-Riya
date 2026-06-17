# Riyagpt - Gemma4 AI Chatbot

A full-stack local AI chatbot application featuring a FastAPI backend, an SQLite database for history persistence, and a modern React + TypeScript frontend. It leverages Ollama for local LLM inference and supports real-time streaming responses.

## Features

- **Real-time Streaming:** Smooth, token-by-token response rendering in both frontends.
- **Session Management:** Persistent chat history stored locally using SQLite (`riya.db`).
- **Ollama Integration:** Optimized for running local models like `gemma4:31b-cloud` or `gemma4:e2b`.
- **Modern UI (`riya-ui`):** Clean, dark-mode React + TypeScript interface with a sidebar for chat history, interactive model specs header, and responsive layout.
- **Legacy UI:** Simple static Jinja template frontend (`templates/index.html`) available for direct backend testing.
- **Docker Ready:** Easy multi-container orchestration.

## Project Structure

```text
project Riya/
├── main.py             # FastAPI backend server
├── database.py         # SQLite database connector & operations
├── tools.py            # Custom LangChain tools
├── templates/          # Jinja2 template index.html (testing frontend)
├── riya-ui/            # React + TypeScript + Vite modern frontend
│   ├── src/            # App code (App.tsx, App.css)
│   └── package.json    # React dependencies
├── riya.db             # Local SQLite database (ignored by git)
├── Dockerfile          # Python application container config
└── docker-compose.yml  # Local services orchestration
```

## Getting Started

### 1. Prerequisites

- Python 3.11+
- Node.js 18+ (for `riya-ui`)
- [Ollama](https://ollama.ai/) running locally on your system.

### 2. Pull the Model

Ensure Ollama is running and pull the desired model:
```bash
ollama pull gemma4:31b-cloud
```

### 3. Backend Setup

1. **Install Python Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment:**
   Create or edit the `.env` file in the root directory:
   ```env
   HOST=127.0.0.1
   PORT=8000
   RELOAD=True
   MODEL_NAME=gemma4:31b-cloud
   OLLAMA_HOST=127.0.0.1:11434
   ```

3. **Run the FastAPI Server:**
   ```bash
   python main.py
   ```
   The backend will be live at `http://127.0.0.1:8000`. You can access the testing UI at `http://127.0.0.1:8000/`.

### 4. Frontend Setup (`riya-ui`)

1. **Navigate and Install Dependencies:**
   ```bash
   cd riya-ui
   npm install
   ```

2. **Run in Development Mode:**
   ```bash
   npm run dev
   ```
   The Vite dev server will start at `http://localhost:5173/`, proxying all `/api` calls automatically to the backend on port 8000.
