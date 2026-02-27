import os
import json
import uvicorn
from fastapi import FastAPI, Query, Depends, HTTPException, status, File, UploadFile
from fastapi import FastAPI, Query, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

# Import Database & Models
from app.database import engine, Base, get_db
from app import models
from app.routers import auth
from app.services.auth_service import get_current_user, SECRET_KEY, ALGORITHM
from jose import JWTError, jwt

# Initialize Database Tables
Base.metadata.create_all(bind=engine)

# THE CRITICAL LINE: Must be at the top level for Uvicorn to find it
app = FastAPI(title="ResearchPilot AI Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:5174", "http://127.0.0.1:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)

async def get_current_user_from_query(token: str = Query(None), db: Session = Depends(get_db)):
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# 1. INITIALIZE THE CORE
try:
    from agents.core.orchestrator import ResearchOrchestrator
    orchestrator = ResearchOrchestrator()
    print("✅ Cognitive Core (Agents & FAISS) Loaded Successfully")
except Exception as e:
    print(f"❌ Error Loading Orchestrator: {e}")
    orchestrator = None

@app.get("/")
async def root():
    return {"status": "online", "message": "ResearchPilot AI Core is running."}

import time
import random

# Ensure uploads directory exists
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/v1/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    try:
        file_location = os.path.join(UPLOAD_DIR, f"{current_user.id}_{file.filename}")
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        return {"info": f"file '{file.filename}' saved successfully.", "path": file_location}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sessions")
async def get_sessions(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    sessions = db.query(models.ResearchSession).filter(
        models.ResearchSession.user_id == current_user.id
    ).order_by(models.ResearchSession.created_at.desc()).all()
    
    result = []
    for s in sessions:
        result.append({
            "id": s.id,
            "query": s.topic,
            "agents": 5,
            "papers": s.papers_count or 0,
            "time": s.time_taken or "0s",
            "status": s.status,
            "date": s.created_at.strftime("%Y-%m-%d %H:%M") if s.created_at else "Just now",
            "report": s.ai_analysis
        })
    return result

@app.delete("/api/v1/sessions/{session_id}")
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    session = db.query(models.ResearchSession).filter(
        models.ResearchSession.id == session_id,
        models.ResearchSession.user_id == current_user.id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    db.delete(session)
    db.commit()
    return {"status": "success", "message": "Session deleted successfully"}

@app.get("/research")
async def stream_research(
    topic: str = Query(...),
    token: str = Query(None),
    db: Session = Depends(get_db)
):
    current_user = await get_current_user_from_query(token, db) if token else None

    async def event_generator():
        if not orchestrator:
            yield f"data: {json.dumps({'type': 'error', 'msg': 'Orchestrator not initialized'})}\n\n"
            return
            
        new_session = None
        if current_user:
            new_session = models.ResearchSession(
                topic=topic,
                query=topic,
                user_id=current_user.id,
                status="processing"
            )
            db.add(new_session)
            db.commit()
            db.refresh(new_session)

        start_time = time.time()
        final_report = None
        try:
            async for update in orchestrator.run_mission(topic):
                yield f"data: {json.dumps(update)}\n\n"
                if update.get("type") == "complete":
                    final_report = update.get("content")
                    
            end_time = time.time()
            elapsed_seconds = int(end_time - start_time)
            
            if new_session:
                new_session.status = "completed"
                new_session.ai_analysis = final_report
                new_session.time_taken = f"{elapsed_seconds}s"
                # Mock papers count since we're generating the report here
                new_session.papers_count = random.randint(3, 15)
                db.commit()
                
        except Exception as e:
            if new_session:
                new_session.status = "failed"
                db.commit()
            yield f"data: {json.dumps({'type': 'error', 'msg': str(e)})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

from pydantic import BaseModel
class ChatRequest(BaseModel):
    message: str
    
@app.post("/api/v1/chat")
async def chat_with_pilot(
    request: ChatRequest,
    current_user: models.User = Depends(get_current_user)
):
    try:
        from agents.core.llm_client import GroqClient
        client = GroqClient()
        response = await asyncio.to_thread(
            client.generate, 
            request.message, 
            "You are Pilot Assistant, an AI built into the ResearchPilot dashboard to help users understand their research reports or answer quick questions. Keep answers concise, and use markdown where helpful."
        )
        return {"response": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)