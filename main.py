from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn
import ollama
import json
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
from typing import Optional
from pathlib import Path

# Load environment variables
load_dotenv()

app = FastAPI()

templates = Jinja2Templates(directory="templates")

HISTORY_FILE = os.getenv("HISTORY_FILE", "history.json")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma4:e2b")

# If OLLAMA_HOST is provided in .env, set it for the environment
if os.getenv("OLLAMA_HOST"):
    os.environ["OLLAMA_HOST"] = os.getenv("OLLAMA_HOST")


def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}


def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    try:
        template = templates.get_template("index.html")
        content = template.render({"request": request})
        return HTMLResponse(content=content)
    except Exception as e:
        import traceback
        traceback.print_exc()
        return HTMLResponse(content=f"MANUAL RENDER ERROR: {str(e)}", status_code=500)

@app.get("/api/sessions")
async def get_sessions():
    history = load_history()
    sessions = []
    for sid, data in history.items():
        sessions.append({
            "id": sid,
            "title": data.get("title", "New Chat"),
            "timestamp": data.get("timestamp", "")
        })
    # Sort by timestamp descending
    sessions.sort(key=lambda x: x["timestamp"], reverse=True)
    return sessions


@app.get("/api/sessions/{session_id}")
async def get_session_history(session_id: str):
    history = load_history()
    return history.get(session_id, {"messages": []})


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    user_message = request.message
    session_id = request.session_id

    if not session_id:
        session_id = str(uuid.uuid4())
    
    history = load_history()
    if session_id not in history:
        history[session_id] = {
            "title": user_message[:30] + "...",
            "timestamp": datetime.now().isoformat(),
            "messages": []
        }
    
    history[session_id]["messages"].append({"role": "user", "content": user_message})
    save_history(history)

    def generate():
        try:
            full_response = ""
            stream = ollama.chat(
                model=MODEL_NAME,
                messages=history[session_id]["messages"],
                stream=True,
            )
            for chunk in stream:
                content = chunk["message"]["content"]
                if content:
                    full_response += content
                    yield content

        except Exception as e:
            print(f"!!! GENERATOR ERROR: {e}")
            yield f"Error: {str(e)}"

        # Save AI response after the stream completes
        final_history = load_history()
        final_history[session_id]["messages"].append({"role": "ai", "content": full_response})
        save_history(final_history)

    return StreamingResponse(generate(), media_type="text/plain", headers={"X-Session-ID": session_id})

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "True").lower() == "true"
    uvicorn.run("main:app", host=host, port=port, reload=reload)
