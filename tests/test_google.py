import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

try:
    from googlesearch import search
except ImportError:
    print("❌ Error: googlesearch-python not installed. Please run: pip install googlesearch-python")
    sys.exit(1)

def test_google():
    print("\n--- 🔍 TESTING GOOGLE SEARCH ---")
    queries = [
        "current weather in Rewari",
        "top tech news today",
        "Python programming"
    ]
    
    for q in queries:
        print(f"\nQuery: {q}")
        try:
            # search() returns a generator of URLs
            # Note: num_results is used for the number of results to fetch
            results = list(search(q, num_results=5))
            if results:
                print(f"✅ Success! Found {len(results)} URLs.")
                for i, url in enumerate(results):
                    print(f"  {i+1}. {url}")
            else:
                print("❌ Failed: 0 results found.")
        except Exception as e:
            print(f"❌ Error during search: {e}")

if __name__ == "__main__":
    test_google()
