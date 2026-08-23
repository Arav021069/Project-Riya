from ddgs import DDGS
from playwright.sync_api import sync_playwright

class WebService:
    def search(self, query: str, max_results: int = 5):
        """Searches DuckDuckGo and returns a list of results."""
        print(f"\n[DEBUG] Starting web search for: '{query}'")
        results = []
        try:
            with DDGS() as ddgs:
                # Primary Search
                search_results = list(ddgs.text(query, max_results=max_results))
                
                # FALLBACK: If 0 results, try a simplified query
                if not search_results:
                    print(f"[DEBUG] Primary search returned 0 results. Trying fallback...")
                    fallback_query = query.replace("current", "").replace("today", "").replace("right now", "").strip()
                    search_results = list(ddgs.text(fallback_query, max_results=max_results))

                if not search_results:
                    print(f"[DEBUG] All searches returned 0 results.")
                    return [{"title": "No Results", "url": "", "snippet": "No web results found."}]

                print(f"[DEBUG] Found {len(search_results)} results.")
                return [{
                    "title": r.get("title", "No Title"),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", "")
                } for r in search_results]
        except Exception as e:
            print(f"[DEBUG] Search Error: {str(e)}")
            return []

    def scrape(self, url: str):
        """Visits a URL using a headless browser and extracts the main text."""
        if not url: return "No URL provided."
        print(f"[DEBUG] Attempting to scrape URL: {url}")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                # Use a modern User-Agent and a standard desktop viewport
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                    viewport={'width': 1280, 'height': 720}
                )
                page = context.new_page()
                
                page.goto(url, timeout=15_000, wait_until="domcontentloaded")
                content = page.inner_text("body")
                browser.close()
                
                # Clean up whitespace to save AI tokens
                cleaned_content = " ".join(content.split())
                print(f"[DEBUG] Successfully scraped {len(cleaned_content)} characters.")
                return cleaned_content[:8000] 
        except Exception as e:
            print(f"[DEBUG] Scrape Error for {url}: {str(e)}")
            return f"Failed to scrape {url}: {str(e)}"
# Singleton instance
web_service = WebService()
