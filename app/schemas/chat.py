from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

# --- Chatbot Schemas ---
class ChatMessageBase(BaseModel):
    role: str
    content: str

class ChatMessageCreate(ChatMessageBase):
    session_id: int

class ChatMessageResponse(ChatMessageBase):
    id: int
    session_id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

# --- Research/Session Schemas ---
class SessionCreate(BaseModel):
    topic: str

class SessionResponse(BaseModel):
    id: int
    topic: str
    status: str
    summary: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)

class ResearchAnalysisRequest(BaseModel):
    session_id: int
    query: str
    focus_papers: Optional[List[int]] = []