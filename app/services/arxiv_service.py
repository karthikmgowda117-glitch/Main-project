import httpx
import feedparser

class ArxivService:
    def __init__(self):
        self.base_url = "https://export.arxiv.org/api/query"

    async def search_papers(self, query: str, max_results: int = 5):
        params = {
            "search_query": f"all:{query}",
            "start": 0,
            "max_results": max_results
        }
        
        # ArXiv requires a specific User-Agent to avoid being flagged as a scraper
        headers = {
            "User-Agent": "ResearchPilotAI/1.0 (contact: your-email@example.com)"
        }

        async with httpx.AsyncClient(follow_redirects=True) as client:
            try:
                # Use a slightly longer timeout for ArXiv's XML response
                response = await client.get(
                    self.base_url, 
                    params=params, 
                    headers=headers, 
                    timeout=15.0
                )
                response.raise_for_status()
                
                # feedparser handles the Atom XML format returned by ArXiv
                feed = feedparser.parse(response.text)
                
                if not feed.entries:
                    return []

                papers = []
                for entry in feed.entries:
                    papers.append({
                        "title": entry.title.replace('\n', ' ').strip(),
                        "abstract": entry.summary.strip(),
                        "url": entry.link,
                        "authors": ", ".join([a.name for a in entry.authors]),
                        "arxiv_id": entry.id.split('/abs/')[-1]
                    })
                return papers

            except Exception as e:
                # This is what's currently triggering your 'Failed to fetch' debug
                print(f"CRITICAL: ArXiv Fetch Error -> {e}")
                return {"error": str(e)}