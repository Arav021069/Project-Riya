import sys
import os

# Add project root to sys.path so we can import from app and core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.web_service import web_service

def test_search():
    print("\n--- 🔍 TESTING SEARCH ---")
    queries = [
        "current weather in Rewari",python -c "from ddgs import DDGS; print(list(DDGS().text('Python programming', max_results=5)))"
        "top tech news today",
        "Python programming"
    ]
    
    for q in queries:
        print(f"\nQuery: {q}")
        results = web_service.search(q)
        if results:
            print(f"✅ Success! Found {len(results)} results.")
            for i, r in enumerate(results[:3]):
                print(f"  {i+1}. {r['title']} -> {r['url']}")
        else:
            print("❌ Failed: 0 results found.")

def test_scrape():
    print("\n--- 🕷️ TESTING SCRAPE ---")
    urls = [
        "https://www.google.com",
        "https://en.wikipedia.org/wiki/Main_Page"
    ]
    
    for url in urls:
        print(f"\nURL: {url}")
        content = web_service.scrape(url)
        if "Failed to scrape" in content:
            print(f"❌ Failed: {content}")
        else:
            print(f"✅ Success! Scraped {len(content)} characters.")
            print(f"Snippet: {content[:100]}...")

if __name__ == "__main__":
    print("=== RIYA AI WEB SERVICE TEST SUITE ===")
    try:
        test_search()
    except Exception as e:
        print(f"Search Test Crashed: {e}")
        
    try:
        test_scrape()
    except Exception as e:
        print(f"Scrape Test Crashed: {e}")
    print("\n=== TESTS COMPLETE ===")
