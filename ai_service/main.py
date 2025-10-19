from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import Any

app = FastAPI(
    title="AI microservice",
    description="hackathon",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class MessageRequest(BaseModel):
    message_type: str
    user_id: str
    content: Any


@app.get("/health")
async def health():
    return "salut"

@app.post("/chat")
async def chat(request: MessageRequest):
    return "salut"

@app.post("/ocr")
async def ocr(file: MessageRequest):
    return "salut"

