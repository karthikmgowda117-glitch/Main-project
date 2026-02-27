from agents.core.llm_client import GroqClient
from dotenv import load_dotenv

load_dotenv()

class HypothesisAgent:
    def __init__(self):
        """
        Initializes the HypothesisAgent. 
        Its role is to generate testable and novel scientific propositions.
        """
        self.llm = GroqClient()
        self.system_prompt = (
            "You are the Lead Scientist for ResearchPilot AI. "
            "Your goal is to generate NOVEL and TESTABLE hypotheses based on research data. \n\n"
            "STRICT RULES:\n"
            "1. Each hypothesis must be Falsifiable (can be proven wrong).\n"
            "2. Identify the Independent and Dependent variables.\n"
            "3. Suggest a 'Verification Method' (how a human would test this).\n"
            "4. Focus on 'XOR' discoveries—find gaps or contradictions in the data."
        )

    def generate_hypotheses(self, topic: str, analyzed_data: str):
        print(f"🔬 HypothesisAgent: Ideating new theories for '{topic}'...")
        
        prompt = (
            f"Topic: {topic}\n\n"
            f"Current Knowledge/Analysis:\n{analyzed_data}\n\n"
            "Based on this current knowledge, propose 2-3 innovative hypotheses. "
            "What is the next logical discovery? What is missing from current research?"
        )

        try:
            return self.llm.generate(prompt, system_message=self.system_prompt)
        except Exception as e:
            return f"Error during hypothesis generation: {str(e)}"