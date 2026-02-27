from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app import models, schemas, database
from app.agent.pipeline import ResearchAgent
from app.services.auth_service import get_current_user
from app.database import get_db
from app import schemas

router = APIRouter(prefix="/research", tags=["Research"])
agent = ResearchAgent()

# Helper function for the background work
async def perform_research(session_id: int, topic: str):
    db = database.SessionLocal()
    try:
        # Update status to 'processing' so the UI can show a spinner
        session = db.query(models.ResearchSession).get(session_id)
        if session:
            session.status = "processing" 
            db.commit()

        # Run the actual ArXiv/LLM discovery
        await agent.run_discovery(db, session_id, topic)
        
        # Mark as completed upon success
        session.status = "completed"
        db.commit()

    except Exception as e:
        print(f"Background Research Error: {e}")
        # Error Handling: Ensure the DB reflects the failure
        session = db.query(models.ResearchSession).get(session_id)
        if session:
            session.status = "failed"
            # Optional: store the error message in a column if you have one
            # session.error_message = str(e)
            db.commit()
    finally:
        db.close()

@router.post("/start", response_model=schemas.SessionResponse, status_code=status.HTTP_201_CREATED)
async def start_research_session(
    request: schemas.SessionCreate, 
    background_tasks: BackgroundTasks, # <-- Inject BackgroundTasks
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(get_current_user)
):
    # 1. Create the record immediately
    new_session = models.ResearchSession(
        topic=request.topic, 
        user_id=current_user.id,
        summary="Processing..." # Set an initial state
    )
    
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # 2. Add the heavy agent logic to the background queue
    background_tasks.add_task(perform_research, new_session.id, request.topic)

    # 3. Return immediately!
    return new_session

@router.get("/sessions/{session_id}", response_model=schemas.SessionResponse)
async def get_research_status(
    session_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    # Fetch the session and ensure it belongs to the current user
    session = db.query(models.ResearchSession).filter(
        models.ResearchSession.id == session_id,
        models.ResearchSession.user_id == current_user.id
    ).first()

    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Research session not found"
        )
    
    return session