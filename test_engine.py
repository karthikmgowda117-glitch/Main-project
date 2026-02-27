import os
import numpy as np
import faiss
from tavily import TavilyClient
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

# 1. Load Environment Variables from .env file
load_dotenv()

def run_test():
    print("--- 🚀 Starting Research Engine Test ---")
    
    # Get API Keys
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if not tavily_key:
        print("❌ ERROR: TAVILY_API_KEY not found in environment or .env file.")
        return

    try:
        # 2. Test Tavily (The "Eyes")
        print("📡 Connecting to Tavily AI...")
        tavily = TavilyClient(api_key=tavily_key)
        search_result = tavily.search(
            query="Top AI startups in Bangalore 2026", 
            search_depth="advanced", 
            max_results=1
        )
        
        result_title = search_result['results'][0]['title']
        result_content = search_result['results'][0]['content']
        
        print(f"✅ Tavily Success! Found: {result_title}")

        # 3. Test Embedding & FAISS (The "Memory")
        print("🧠 Initializing Vector Memory (FAISS)...")
        model = SentenceTransformer('all-MiniLM-L6-v2')
        embedding = model.encode([result_content])

        dimension = embedding.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(np.array(embedding).astype('float32'))

        print(f"✅ Memory Success! FAISS now has {index.ntotal} knowledge chunk(s) stored.")
        print("\n--- ✨ Test Completed Successfully! ---")

    except Exception as e:
        print(f"❌ AN ERROR OCCURRED: {e}")

if __name__ == "__main__":
    run_test()