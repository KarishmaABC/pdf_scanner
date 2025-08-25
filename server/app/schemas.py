from pydantic import BaseModel
from typing import List, Literal, Optional

class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str

class ChatRequest(BaseModel):
    doc_id: str
    question: str
    history: Optional[List[ChatMessage]] = []

class UploadResponse(BaseModel):
    doc_id: str
    page_count: int
    chunks: int
