from fastapi import APIRouter, Request, HTTPException, UploadFile, File
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
import uuid
import os
from dotenv import load_dotenv
import base64

from app.services.session_service import SessionService
from app.services.chat_service import ChatService
from core.ollama_service import OllamaService

# Load environment variables
load_dotenv()

router = APIRouter()
templates = Jinja2Templates(directory="templates")
MODEL_NAME = os.getenv("MODEL_NAME", "gemma4:31b-cloud")

# Initialize services
session_service = SessionService()
chat_service = ChatService()

class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    model: Optional[str] = MODEL_NAME

@router.get("/", response_class=HTMLResponse)
async def get_index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@router.get("/api/sessions")
async def get_sessions():
    return session_service.list_all_sessions()

@router.get("/api/sessions/{session_id}")
async def get_session_history(session_id: str):
    messages = session_service.get_session_history(session_id)
    return {"messages": messages}

@router.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    session_service.remove_session(session_id)
    return {"status": "success"}

@router.post("/api/chat")
async def chat_endpoint(request: ChatRequest):
    user_message = request.message
    session_id = request.session_id
    selected_model = request.model or MODEL_NAME

    if not session_id:
        session_id = str(uuid.uuid4())
        session_service.create_new_session(session_id, user_message[:30] + "...")

    session_service.save_message(session_id, "user", user_message)
    return StreamingResponse(
        chat_service.stream_chat(user_message, session_id, selected_model),
        media_type="text/plain",
        headers={"X-Session-ID": session_id}
    )

@router.get("/api/models")
async def get_model():
    return chat_service.ollama.list_models()

@router.get("/api/models/{model_name}")
def get_model_info(model_name: str):
    try:
        return OllamaService().get_model_info(model_name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
