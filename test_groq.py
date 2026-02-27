import os
from groq import Groq
from dotenv import load_dotenv
from pathlib import Path

# Load .env from this script's directory (override existing env vars)
dotenv_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=dotenv_path, override=True)

api_key = os.getenv("GROQ_API_KEY")
model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

if not api_key:
    print("Error: GROQ_API_KEY is missing from .env or environment.")
else:
    try:
        client = Groq(api_key=api_key)
        print(f"Using model: {model}")
        completion = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": "Confirm ResearchPilot status."}],
        )
        print("✅ SUCCESS: ResearchPilot is Online!")
        print(f"AI Response: {completion.choices[0].message.content}")
    except Exception as e:
        err = str(e)
        print(f"❌ CONNECTION FAILED: {err}")
        if "decommissioned" in err or "model" in err:
            print("Suggestion: set a supported model via the GROQ_MODEL env var.")