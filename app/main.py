from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import auth, research
from app.api.v1.endpoints import chat

# 1. Initialize Database Tables
Base.metadata.create_all(bind=engine)

# 2. Create the FastAPI Instance FIRST
app = FastAPI(
    title="ResearchPilot AI API",
    description="AI-powered research synthesis agent",
    version="0.1.0"
)

# 3. Configure CORS Middleware
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Include Routers
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(research.router, prefix="/research", tags=["Research"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chatbot"])

@app.get("/")
async def root():
    return {
        "status": "online",
        "message": "ResearchPilot AI Core is operational",
        "docs": "/docs"
    }