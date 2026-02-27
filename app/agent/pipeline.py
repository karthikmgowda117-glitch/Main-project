from sqlalchemy.orm import Session
from app.services.arxiv_service import ArxivService
from app.services.llm_service import LLMService
from app.models import ResearchPaper, ResearchSession
import json

class ResearchAgent:
    def __init__(self):
        self.arxiv = ArxivService()
        self.llm = LLMService()

    async def run_discovery(self, db: Session, session_id: int, query: str):
        # --- 1. Fetch the Session Object First ---
        # This fixes the 'UnboundLocalError' by making 'session' available to the loop
        session = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        if not session:
            print(f"ERROR: Session {session_id} not found in database.")
            return None

        # --- 2. Fetch Papers from ArXiv ---
        raw_papers = await self.arxiv.search_papers(query, max_results=5)
        
        # Handle different response formats (String vs List)
        if isinstance(raw_papers, str):
            raw_papers = json.loads(raw_papers)
        
        if isinstance(raw_papers, dict) and 'error' in raw_papers:
            print(f"ERROR: {raw_papers['error']}")
            return None

        if not isinstance(raw_papers, list):
            raw_papers = [raw_papers]

        # --- 3. Process and Save Papers ---
        for p in raw_papers:
            # Handle nested strings if necessary
            if isinstance(p, str):
                p = json.loads(p)

            # Check for existing paper by URL or ArXiv ID to avoid unique constraint crashes
            existing = db.query(ResearchPaper).filter(
                (ResearchPaper.url == p['url']) | 
                (ResearchPaper.arxiv_id == p.get('arxiv_id'))
            ).first()

            if existing:
                if existing not in session.papers:
                    session.papers.append(existing)
                continue

            # Create new paper object
            db_paper = ResearchPaper(
                title=p.get('title', 'Untitled'),
                summary=p.get('abstract', p.get('summary', 'No summary available')),
                url=p.get('url'),
                authors=p.get('authors', 'Unknown Authors'),
                arxiv_id=p.get('arxiv_id') # Crucial for your ResearchPaper model
            )
            
            db.add(db_paper)
            db.flush() # Flushes to DB to get an ID without committing yet
            session.papers.append(db_paper)

        # --- 4. Generate AI Briefing ---
        # Construct context for the LLM
        context_text = "\n".join([
            f"Title: {p.get('title')}\nAbstract: {p.get('abstract', p.get('summary', ''))}" 
            for p in raw_papers
        ])
        
        print("--- Generating AI Summary ---")
        briefing_content = await self.llm.summarize_research(context_text)

        # --- 5. Update Session Status and Analysis ---
        session.ai_analysis = briefing_content
        session.status = "completed"
        
        db.commit()
        db.refresh(session)
        print(f"--- Session {session_id} Successfully Updated ---")
        return session