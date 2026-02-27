import asyncio
import json
# Direct import to ensure AgentMemory is found
from agents.core.memory import AgentMemory

class ResearchOrchestrator:
    def __init__(self):
        print("--- Initializing ResearchOrchestrator ---")
        self.memory = AgentMemory()
        
        # Initialize your logic agents
        from agents.logic.planner_agent import PlannerAgent
        from agents.logic.search_agent import SearchAgent
        from agents.logic.analysis_agent import AnalysisAgent
        from agents.logic.hypothesis_agent import HypothesisAgent
        from agents.logic.synthesis_agent import SynthesisAgent
        
        self.planner = PlannerAgent()
        self.searcher = SearchAgent()
        self.analyzer = AnalysisAgent()
        self.hypothesizer = HypothesisAgent()
        self.synthesizer = SynthesisAgent()

    async def run_mission(self, topic: str, file_path: str = None):
        try:
            file_context = ""
            if file_path:
                yield {"agent": "Analyzer", "status": "active", "msg": "Reading attached file..."}
                try:
                    import os
                    if os.path.exists(file_path):
                        ext = file_path.lower().split('.')[-1]
                        if ext == 'pdf':
                            import PyPDF2
                            with open(file_path, 'rb') as f:
                                reader = PyPDF2.PdfReader(f)
                                for page in reader.pages:
                                    if page.extract_text():
                                        file_context += page.extract_text() + "\n"
                        elif ext in ['png', 'jpg', 'jpeg', 'webp']:
                            try:
                                import pytesseract
                                from PIL import Image
                                img = Image.open(file_path)
                                file_context = pytesseract.image_to_string(img)
                            except Exception as ocr_e:
                                print(f"OCR Error: {ocr_e}")
                                file_context = f"Failed to read image via OCR. Error: {ocr_e}"
                        else:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                file_context = f.read()
                        
                        self.memory.add_fact(f"FILE CONTENT UPLOADED BY USER:\n{file_context[:5000]}") # Store in memory
                except Exception as e:
                    print(f"Failed to read file: {e}")

            yield {"agent": "Planner", "status": "active", "msg": "Planning..."}
            plan = await asyncio.to_thread(self.planner.generate_plan, topic, file_context)
            await asyncio.sleep(0.5)

            results = []
            for query in plan:
                yield {"agent": "Search", "status": "active", "msg": f"Searching: {query}"}
                raw_data = await asyncio.to_thread(self.searcher.execute_search, query)
                self.memory.add_fact(raw_data)
                
                yield {"agent": "Analysis", "status": "active", "msg": "Analyzing..."}
                analysis = await asyncio.to_thread(self.analyzer.analyze_results, query, raw_data)
                results.append(analysis)

            yield {"agent": "Hypothesis", "status": "active", "msg": "Generating Hypothesis..."}
            context = "\n".join(self.memory.retrieve_relevant(topic, k=3))
            if file_context:
                context = f"Uploaded File Data:\n{file_context[:3000]}\n\n{context}"
                
            hypotheses = await asyncio.to_thread(self.hypothesizer.generate_hypotheses, topic, context)

            yield {"agent": "Synthesis", "status": "active", "msg": "Synthesizing..."}
            final_report = await asyncio.to_thread(self.synthesizer.synthesize, topic, results + [hypotheses])

            yield {"type": "complete", "content": final_report}
        except Exception as e:
            yield {"type": "error", "msg": str(e)}