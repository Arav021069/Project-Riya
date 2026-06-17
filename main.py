from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import uvicorn
import ollama
import os
import uuid
from dotenv import load_dotenv
from typing import Optional
from pathlib import Path

import database
from core.ollama_service import OllamaService

# Load environment variables
load_dotenv()

app = FastAPI()

database.init_db()

templates = Jinja2Templates(directory="templates")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma4:e2b")

# If OLLAMA_HOST is provided in .env, set it for the environment
if os.getenv("OLLAMA_HOST"):
    os.environ["OLLAMA_HOST"] = os.getenv("OLLAMA_HOST")


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    model: Optional[str] = MODEL_NAME


@app.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")


@app.get("/api/sessions")
async def get_sessions():
    return database.get_all_sessions()


@app.get("/api/sessions/{session_id}")
async def get_session_history(session_id: str):
    messages = database.get_messages(session_id)
    return {"messages": messages}


@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    database.delete_session(session_id)
    return {"status": "success"}


@app.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    user_message = request.message
    session_id = request.session_id
    selected_model = request.model or MODEL_NAME

    if not session_id:
        session_id = str(uuid.uuid4())
        # Create a new session entry
        database.create_session(session_id, user_message[:30] + "...")

    database.add_message(session_id, "user", user_message)

    def generate():
        full_response = ""
        try:
            # Fetch history from DB for Ollama context
            history_messages = database.get_messages(session_id)
            # for msg in history[session_id]["messages"]:
            #     role = msg["role"]
            #     normalized_messages.append({"role": role, "content": msg["content"]})

            stream = ollama.chat(
                model=MODEL_NAME,
                messages=history_messages,
                stream=True,
                options={
                    "num_ctx": 4096
                }
            )
            for chunk in stream:
                content = chunk.get("message", {}).get("content", "")
                if content:
                    full_response += content
                    yield content

        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"ERROR: {error_msg}")
            yield error_msg
            full_response = error_msg   # Store the error in history for context

        finally:
            if full_response.strip():
                # Save AI response to DB
                database.add_message(session_id, "assistant", full_response)

    return StreamingResponse(generate(), media_type="text/plain", headers={"X-Session-ID": session_id})


@app.get("/api/models")
async def get_model():
    try:
        models_info = ollama.list()
        # Extract just the names from the models list
        model_names = [model["name"] for model in models_info.get("models", [])]
        return {"models": model_names}
    except Exception as e:
        return {"models": [MODEL_NAME], "error": str(e)}

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "True").lower() == "true"
    uvicorn.run("main:app", host=host, port=port, reload=reload)
