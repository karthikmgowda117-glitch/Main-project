import os
from tavily import TavilyClient
from dotenv import load_dotenv

# Load keys from the .env file (which is now safely ignored by git)
load_dotenv()

class SearchAgent:
    def __init__(self):
        """
        Initializes the SearchAgent with the Tavily API client.
        Tavily is optimized for LLM agents to find high-quality research data.
        """
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found in .env. Please get one at tavily.com")
        
        self.client = TavilyClient(api_key=self.api_key)

    def execute_search(self, query: str, max_results: int = 5):
        """
        Conducts an advanced search and returns structured context for the Analysis Agent.
        """
        print(f"🔍 SearchAgent: Investigating '{query}'...")
        
        try:
            # search_depth="advanced" retrieves more context/snippets from each page
            response = self.client.search(
                query=query,
                search_depth="advanced",
                max_results=max_results
            )

            formatted_results = []
            for result in response.get('results', []):
                content_block = (
                    f"SOURCE: {result.get('url')}\n"
                    f"TITLE: {result.get('title')}\n"
                    f"CONTENT: {result.get('content')}\n"
                )
                formatted_results.append(content_block)
            
            return "\n---\n".join(formatted_results)

        except Exception as e:
            return f"Error during search: {str(e)}"

# Test Logic
if __name__ == "__main__":
    # Ensure your .env has TAVILY_API_KEY
    searcher = SearchAgent()
    
    # Example research query
    query = "State of Agentic AI frameworks in early 2026"
    results = searcher.execute_search(query)
    
    print("\n" + "="*50)
    print("SEARCH AGENT OUTPUT (PREVIEW):")
    print("="*50)
    print(results[:1000] + "...") # Preview the first 1000 characters