"""Robust AgentMemory with optional FAISS + SentenceTransformer support.

If FAISS or sentence-transformers are not installed in the environment
we fall back to a simple in-memory store with heuristic retrieval so the
package can be imported and the app can start.
"""

try:
    import faiss
    import numpy as np
    from sentence_transformers import SentenceTransformer
    _HAS_FAISS = True
except Exception:
    # Missing native deps (faiss / sentence-transformers). Use fallback.
    import numpy as np
    _HAS_FAISS = False


class AgentMemory:
    def __init__(self, dimension=384):
        self.dimension = dimension
        if _HAS_FAISS:
            # Initialize the embedding model and FAISS index
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.index = faiss.IndexFlatL2(dimension)
            self.metadata = []
            self.use_faiss = True
        else:
            # Fallback: simple in-memory storage (no embeddings)
            self.documents = []
            self.use_faiss = False

    def add_fact(self, text: str):
        if not text or not text.strip():
            return

        if self.use_faiss:
            embedding = self.model.encode([text]).astype('float32')
            self.index.add(embedding)
            self.metadata.append(text)
        else:
            self.documents.append(text)

    def retrieve_relevant(self, query: str, k=3):
        if self.use_faiss:
            if self.index.ntotal == 0:
                return []
            query_vec = self.model.encode([query]).astype('float32')
            distances, indices = self.index.search(query_vec, k)
            return [self.metadata[i] for i in indices[0] if i != -1]

        # Fallback heuristic: keyword overlap + recency
        if not self.documents:
            return []

        qwords = set(w.lower() for w in query.split() if w.strip())
        scored = []
        for doc in self.documents:
            lc = doc.lower()
            score = sum(1 for w in qwords if w in lc)
            scored.append((score, doc))

        # Prefer higher score, then earlier index (which keeps relative order)
        scored.sort(key=lambda x: (x[0], self.documents.index(x[1])), reverse=True)
        results = [d for s, d in scored if s > 0][:k]
        if len(results) < k:
            recent = list(reversed(self.documents))
            for r in recent:
                if r not in results:
                    results.append(r)
                if len(results) >= k:
                    break

        return results[:k]