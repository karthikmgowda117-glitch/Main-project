from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

# Association table for Many-to-Many: Session <-> Papers
# This allows one paper to belong to multiple research sessions.
session_papers = Table(
    'session_papers',
    Base.metadata,
    Column('session_id', Integer, ForeignKey('research_sessions.id'), primary_key=True),
    Column('paper_id', Integer, ForeignKey('papers.id'), primary_key=True),
    extend_existing=True
)

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    
    # Relationship to sessions
    sessions = relationship("ResearchSession", back_populates="owner")

class ResearchPaper(Base):
    __tablename__ = "papers"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    arxiv_id = Column(String, unique=True, index=True)
    title = Column(String)
    summary = Column(Text)
    url = Column(String)
    authors = Column(String)  # FIXED: Added this to resolve the TypeError
    published_date = Column(String, nullable=True)

class ResearchSession(Base):
    __tablename__ = "research_sessions"
    __table_args__ = {'extend_existing': True}
    
    id = Column(Integer, primary_key=True, index=True)
    topic = Column(String)
    query = Column(String)
    status = Column(String, default="pending") 
    ai_analysis = Column(Text, nullable=True)
    time_taken = Column(String, nullable=True)
    papers_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))

    # Relationships
    owner = relationship("User", back_populates="sessions")
    # Many-to-Many relationship with ResearchPaper
    papers = relationship("ResearchPaper", secondary=session_papers)