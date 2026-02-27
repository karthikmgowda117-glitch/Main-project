import sys
import os
import time

# Ensure the project root is in the path for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.logic.planner_agent import PlannerAgent
from agents.logic.search_agent import SearchAgent
from agents.logic.analysis_agent import AnalysisAgent
from agents.logic.hypothesis_agent import HypothesisAgent
from agents.logic.synthesis_agent import SynthesisAgent

class ResearchPilot:
    def __init__(self):
        """
        Initializes the full multi-agent research team.
        """
        print("🤖 System: Booting ResearchPilot Multi-Agent Team...")
        self.planner = PlannerAgent()
        self.searcher = SearchAgent()
        self.analyzer = AnalysisAgent()
        self.hypothesizer = HypothesisAgent()
        self.synthesizer = SynthesisAgent()

    def start_mission(self, topic: str):
        """
        Executes the hierarchical research workflow.
        """
        start_time = time.time()
        print(f"\n🚀 MISSION STARTED: {topic}")
        print("=" * 60)

        # 1. STRATEGIC PLANNING
        # Breaks the main topic into 3 searchable sub-queries
        plan = self.planner.generate_plan(topic)
        
        results_pool = []

        # 2. DATA GATHERING & ANALYSIS LOOP
        # Iterates through the plan to build a deep knowledge base
        for i, sub_query in enumerate(plan):
            print(f"\n📍 PHASE {i+1}/{len(plan)}: Investigating '{sub_query}'")
            
            raw_data = self.searcher.execute_search(sub_query)
            analysis = self.analyzer.analyze_results(sub_query, raw_data)
            
            results_pool.append(analysis)
            time.sleep(1) # Respect API rate limits

        # 3. SCIENTIFIC HYPOTHESIS GENERATION
        # Analyzes current findings to propose testable new theories
        print("\n🧪 PHASE 4: Generating Scientific Hypotheses...")
        combined_analysis = "\n\n".join(results_pool)
        hypotheses = self.hypothesizer.generate_hypotheses(topic, combined_analysis)

        # 4. FINAL SYNTHESIS
        # Merges all analyses and hypotheses into a cohesive document
        print("\n✍️ PHASE 5: Final Synthesis & Polishing...")
        final_report = self.synthesizer.synthesize(topic, results_pool + [hypotheses])

        # 5. EXPORT & FINISH
        self.export_report(topic, final_report)
        
        duration = round(time.time() - start_time, 2)
        print(f"\n✅ SUCCESS: Research complete in {duration}s.")
        print(f"📄 Report saved as: Final_Research_Report.md")
        print("=" * 60)

    def export_report(self, topic, content):
        """Saves the final output as a Markdown file."""
        filename = "Final_Research_Report.md"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(content)

if __name__ == "__main__":
    # Ensure environment variables are loaded
    from dotenv import load_dotenv
    load_dotenv()

    pilot = ResearchPilot()
    user_input = input("Enter your research topic: ")
    pilot.start_mission(user_input)