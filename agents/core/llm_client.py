import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqClient:
    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in .env file")
        self.client = Groq(api_key=self.api_key)
        # Switched to 3.1 8B model to bypass free-tier rate limits and decommissioned models
        self.model = "llama-3.1-8b-instant" 

    def generate(self, prompt: str, system_message: str = "You are ResearchPilot AI."):
        chat_completion = self.client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            model=self.model,
        )
        return chat_completion.choices[0].message.content