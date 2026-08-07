# Riya AI

A modular local LLM orchestration framework featuring a FastAPI backend, persistent session management via SQLite, and a modern React + TypeScript frontend. Designed for high-performance local AI inference using Ollama.

## Features

- **Model Agnostic:** Seamlessly switch between different local LLMs via the integrated model selector.
- **Real-time Streaming:** Smooth, token-by-token response rendering for a natural chat experience.
- **Session Management:** Persistent chat history stored locally, allowing for seamless conversation retrieval.
- **Modern UI (`riya-ui`):** A "Void Violet" cosmic-themed React + TypeScript interface with a sidebar for history and a responsive layout.
- **Legacy UI:** Simple static Jinja template frontend (`templates/index.html`) available for direct backend testing.
- **Docker Ready:** Optimized for containerized deployment.

## Project Structure

```text
project Riya/
├── main.py             # FastAPI entry point
├── app/
│   ├── api/            # API routing layer
│   │   └── endpoints/  # Route handlers (chat.py)
│   ├── services/       # Business logic layer (chat_service.py, session_service.py)
│   └── db/             # Data access layer (manager.py)
├── core/               # Core AI orchestration (ollama_service.py, time_tool.py)
├── templates/          # Jinja2 template index.html (testing frontend)
├── riya-ui/            # React + TypeScript + Vite modern frontend
│   ├── src/            # App code (App.tsx, App.css)
│   └── package.json    # React dependencies
├── Dockerfile          # Python application container config
└── docker-compose.yml  # Local services orchestration
```

## Getting Started

### 1. Prerequisites

- Python 3.11+
- Node.js 18+ (for `riya-ui`)
- [Ollama](https://ollama.ai/) running locally on your system.

### 2. Pull a Model

Ensure Ollama is running and pull your preferred model:
```bash
ollama pull <model-name>
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
   MODEL_NAME=your-preferred-model
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
