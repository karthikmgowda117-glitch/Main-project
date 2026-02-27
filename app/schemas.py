from pydantic import BaseModel, EmailStr, ConfigDict
from typing import List, Optional
from datetime import datetime

# --- User & Auth Schemas ---
class UserBase(BaseModel):
    email: EmailStr
    username: str # Added username to match typical JWT logic

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None

# --- Research Schemas ---

class PaperSchema(BaseModel):
    id: int  # Added ID for frontend keys/references
    title: str
    authors: str
    url: str
    summary: str # Renamed from abstract to match typical ArXiv API naming

    model_config = ConfigDict(from_attributes=True)

class SessionCreate(BaseModel):
    topic: str

class SessionResponse(BaseModel):
    id: int
    topic: str
    status: str  # CRITICAL: Added for the polling state machine
    ai_analysis: Optional[str] = None # Renamed from briefing to match your DB model
    created_at: datetime
    # This triggers the Many-to-Many serialization
    papers: List[PaperSchema] = []

    model_config = ConfigDict(from_attributes=True)

class ResearchRequest(BaseModel):
    topic: str
    max_results: Optional[int] = 5

    # --- Chatbot Schemas (Missing for Integration) ---

class ChatMessageBase(BaseModel):
    role: str  # 'user' or 'assistant'
    content: str

class ChatMessageCreate(ChatMessageBase):
    session_id: int

class ChatMessageResponse(ChatMessageBase):
    id: int
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)

# --- Enhanced Research Request ---
class ResearchAnalysisRequest(BaseModel):
    session_id: int
    query: str
    focus_papers: Optional[List[int]] = [] # IDs of papers to analyze