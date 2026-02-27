import os
from groq import AsyncGroq # Using Async for better FastAPI performance
from dotenv import load_dotenv

load_dotenv()

class LLMService:
    def __init__(self):
        # 1. Initialize Groq (Required for Llama 3.3 70B)
        self.api_key = os.getenv("GROQ_API_KEY")
        if not self.api_key:
            print("WARNING: GROQ_API_KEY is missing from environment variables!")
            
        self.client = AsyncGroq(api_key=self.api_key)
        
        # 2. Set the model to the one required by project specs
        self.model = "llama-3.3-70b-versatile"

    async def summarize_research(self, context_text: str):
        """
        Generates a professional research briefing using Llama 3.3 70B.
        Matches the call signature in ResearchAgent.run_discovery.
        """
        if not context_text or len(context_text.strip()) < 10:
            return "No significant research data available to analyze."

        # Professional Research Prompt
        prompt = f"""
        You are an AI Research Lead. Analyze the following research context.
        Provide a technical synthesis that includes:
        1. Key Trends: What are the recurring themes?
        2. Methodology: Common techniques used in these papers.
        3. Research Gap: What is missing or needs more study?
        
        Context:
        {context_text}
        """

        try:
            # Using AsyncGroq for non-blocking execution
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a professional research architect specialized in academic synthesis."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2048
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Groq LLM Error: {e}")
            return f"Analysis unavailable due to Groq service error: {str(e)}"