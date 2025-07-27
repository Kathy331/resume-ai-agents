# run_tavily.py from the shared folder
from shared.tavily_client import search_tavily

# Example query
results = search_tavily("Rakesh Gohel, Toronto", search_depth="advanced", max_results=1)

# Display results
for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Content: {result['content']}\n")
