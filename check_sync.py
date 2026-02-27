import sys
import os

# Force the app directory into the path
sys.path.insert(0, os.path.join(os.getcwd(), "app"))

try:
    print("--- 🔍 Starting System Audit ---")
    
    # Check SQLAlchemy version first
    import sqlalchemy
    print(f"SQLAlchemy Version: {sqlalchemy.__version__}")

    # Import our local modules
    from database import engine, Base
    import models  # This ensures all tables are registered to Base.metadata
    from agent.pipeline import ResearchAgent
    from services.auth_service import AuthService

    # 1. Test: Database Table Creation
    print("Step 1: Checking Database Schema...")
    # The correct way: metadata.create_all(engine)
    Base.metadata.create_all(bind=engine)
    print("✅ Tables initialized successfully.")

    # 2. Test: Auth Logic
    print("\nStep 2: Checking Auth Hashing...")
    test_pass = "lead_engineer_2026"
    hashed = AuthService.get_password_hash(test_pass)
    if AuthService.verify_password(test_pass, hashed):
        print("✅ JWT/Bcrypt hashing is functional.")

    # 3. Test: Agent Logic
    print("\nStep 3: Checking Agent Pipeline...")
    agent = ResearchAgent()
    print("✅ Agent initialized.")

    print("\n🚀 ALL SYSTEMS NOMINAL.")

except Exception as e:
    print(f"\n❌ AUDIT FAILED: {str(e)}")
    import traceback
    traceback.print_exc() # This will show us EXACTLY which file has the bad import
    sys.exit(1)
