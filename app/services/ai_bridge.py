import os
from groq import Groq
from typing import List, Dict

class AIBridge:
    def __init__(self):
        # This will look for the GROQ_API_KEY we discussed in your .env
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        # Using Llama 3.3 70B as per the ResearchHub AI project requirements
        self.model = "llama-3.3-70b-specdec"

    async def get_response(self, user_message: str, chat_history: List[Dict[str, str]] = None):
        """
        Orchestrates the conversation. 
        chat_history should be a list of: {"role": "user/assistant", "content": "..."}
        """
        if chat_history is None:
            chat_history = []

        # Construct the full prompt history
        messages = chat_history + [{"role": "user", "content": user_message}]

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                top_p=1,
                stream=False,
            )
            return completion.choices[0].message.content
        except Exception as e:
            return f"Error connecting to AI Agents: {str(e)}"