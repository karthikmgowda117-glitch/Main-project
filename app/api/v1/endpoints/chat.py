from fastapi import APIRouter, HTTPException, Depends
from typing import List
from app.schemas.chat import ChatMessageCreate, ChatMessageResponse
from app.services.ai_bridge import AIBridge

router = APIRouter()
# Initialize the AI Bridge (The logic that talks to Groq)
ai_bridge = AIBridge()

@router.post("/", response_model=ChatMessageResponse)
async def send_message(chat_input: ChatMessageCreate):
    """
    Primary endpoint for the AI Chatbot.
    It receives a user message and returns the Agent's response.
    """
    try:
        # 1. Fetch history from DB (placeholder for now)
        # In the next step, we will replace this with real SQLite data
        history = [] 

        # 2. Send to AI Bridge (Llama 3.3 70B via Groq)
        ai_reply = await ai_bridge.get_response(chat_input.content, history)

        # 3. Format the response for the frontend
        return ChatMessageResponse(
            id=999,  # This will be replaced by the DB auto-increment ID
            role="assistant",
            content=ai_reply,
            session_id=chat_input.session_id,
            created_at="2026-02-26T12:00:00" # Placeholder timestamp
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent Error: {str(e)}")