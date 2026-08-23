from fastapi import FastAPI
import uvicorn
import os
from dotenv import load_dotenv
from app.db.manager import DatabaseManager
from app.api.endpoints.chat import router as chat_router

load_dotenv()

app = FastAPI()

# Initialize Database
db_manager = DatabaseManager()
db_manager.init_db()

# Include routes
app.include_router(chat_router)

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "True").lower() == "true"
    uvicorn.run("main:app", host=host, port=port, reload=reload)
