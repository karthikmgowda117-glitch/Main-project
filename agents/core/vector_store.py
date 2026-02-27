import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer

class VectorStore:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        """
        Initializes the VectorStore with a pre-trained embedding model.
        Default: all-MiniLM-L6-v2 (fast and efficient for local use).
        """
        print(f"Initializing VectorStore with model: {model_name}...")
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.documents = []

    def add_texts(self, texts: list[str]):
        """
        Converts a list of strings into embeddings and adds them to the FAISS index.
        """
        if not texts:
            return

        self.documents.extend(texts)
        # Convert text to numerical vectors
        embeddings = self.model.encode(texts)
        
        # Initialize the FAISS index if this is the first time adding data
        if self.index is None:
            dimension = embeddings.shape[1]
            # IndexFlatL2 uses Euclidean distance for similarity search
            self.index = faiss.IndexFlatL2(dimension)
        
        # FAISS requires float32 numpy arrays
        self.index.add(np.array(embeddings).astype('float32'))
        print(f"Added {len(texts)} chunks to the vector store.")

    def search(self, query: str, k: int = 3):
        """
        Searches the index for the top 'k' most relevant snippets for a given query.
        """
        if self.index is None or not self.documents:
            print("Vector store is empty. No search performed.")
            return []
        
        # Convert the user query into the same vector space
        query_vector = self.model.encode([query])
        
        # Search for the nearest neighbors
        distances, indices = self.index.search(np.array(query_vector).astype('float32'), k)
        
        # Retrieve the original text snippets based on the indices found
        results = [self.documents[i] for i in indices[0] if i != -1]
        return results

# Self-test logic
if __name__ == "__main__":
    store = VectorStore()
    sample_data = [
        "Agentic AI uses autonomous agents to complete complex tasks.",
        "Vector databases like FAISS allow for efficient semantic search.",
        "Bangalore is a major tech hub in India known for its startup ecosystem."
    ]
    store.add_texts(sample_data)
    
    query = "Where do tech startups thrive in India?"
    matches = store.search(query, k=1)
    
    print(f"\nQuery: {query}")
    print(f"Top Result: {matches[0] if matches else 'No match found.'}")