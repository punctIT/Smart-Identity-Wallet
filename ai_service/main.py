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

from chat_bot import ChatBot
from ocr_identitycard import IDCardProcessor
chatbot = ChatBot()
ocr = IDCardProcessor()
@app.get("/health")
async def health():
    return "salut"

@app.post("/chat")
async def chat(request: MessageRequest):
    print(request.content)
    response = await chatbot.get_response(request.content) 
    return response

@app.post("/ocr")
async def ocr_endpoint(request: MessageRequest):
    print("ceva")
    result = ocr.process_id_card_from_base64(request.content)
    return {"result": str(result)}