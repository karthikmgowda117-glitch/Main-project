import os
from agents.core.llm_client import GroqClient
from dotenv import load_dotenv

# Load keys
load_dotenv()

class AnalysisAgent:
    def __init__(self):
        """
        Initializes the AnalysisAgent with a Groq LLM client.
        This agent is responsible for reasoning over raw search data.
        """
        self.llm = GroqClient()
        self.system_prompt = (
            "You are the Analysis Agent for ResearchPilot AI. Your goal is to process raw "
            "search results and extract high-quality, factual insights. \n\n"
            "STRICT RULES:\n"
            "1. Only use the information provided in the search results.\n"
            "2. If results are conflicting, mention the discrepancy.\n"
            "3. Format your output with clear headings and bullet points.\n"
            "4. Cite sources (URLs) next to the facts you extract."
        )

    def analyze_results(self, research_topic: str, raw_data: str):
        """
        Takes raw search data and synthesizes it into a structured analysis.
        """
        print(f"🧠 AnalysisAgent: Processing data for '{research_topic}'...")
        
        prompt = (
            f"Research Topic: {research_topic}\n\n"
            f"Raw Search Data:\n{raw_data}\n\n"
            "Please provide a detailed analysis of the above data. "
            "Identify major breakthroughs, key players, and any technical limitations mentioned."
        )

        try:
            analysis = self.llm.generate(prompt, system_message=self.system_prompt)
            return analysis
        except Exception as e:
            return f"Error during analysis: {str(e)}"

# Test Logic
if __name__ == "__main__":
    analyzer = AnalysisAgent()
    
    # Dummy data for testing
    topic = "Agentic AI in 2026"
    mock_data = (
        "SOURCE: https://tech-example.com/ai-news\n"
        "CONTENT: In 2026, Agentic AI shifted from simple chatbots to autonomous 'Action Agents' "
        "capable of managing entire software development lifecycles."
    )
    
    report = analyzer.analyze_results(topic, mock_data)
    print("\n--- ANALYSIS REPORT ---")
    print(report)