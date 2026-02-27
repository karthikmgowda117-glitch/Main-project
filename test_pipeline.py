import asyncio
# Use the exact same import path your models use
from app.database import SessionLocal, engine, Base
import app.models as models  
from app.agent.pipeline import ResearchAgent

async def test_full_flow():
    print("--- Initializing Database ---")
    
    # 1. Create tables using the CORRECT metadata
    Base.metadata.create_all(bind=engine)
    print(f"Verified Tables: {Base.metadata.tables.keys()}")
    
    db = SessionLocal()

    try:
        # 2. Create Dummy User
        test_email = "tester@example.com"
        user = db.query(models.User).filter(models.User.email == test_email).first()
        if not user:
            print("Creating test user...")
            user = models.User(email=test_email, hashed_password="fake_hashed_password")
            db.add(user)
            db.commit()
            db.refresh(user)

        # 3. Create Session (Note: your model uses 'query', not 'topic')
        print(f"--- Creating Session for User ID: {user.id} ---")
        session = models.ResearchSession(query="Quantum Computing", user_id=user.id)
        db.add(session)
        db.commit()
        db.refresh(session)

        # 4. Trigger Agent
        print("--- Running Research Agent ---")
        agent = ResearchAgent()
        # Ensure agent uses session.query or passes the string correctly
        await agent.run_discovery(db, session.id, session.query)

        # 5. Verify
        db.refresh(session)
        print(f"Done! Papers found and linked: {len(session.papers)}")
        for paper in session.papers[:2]:
            print(f"-> {paper.title}")

    except Exception as e:
        print(f"TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_full_flow())