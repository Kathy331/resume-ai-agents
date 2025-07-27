#to run this file, ensure you have pytest installed and run `python agent.py` in the folder (linkedin_finder)
# run_tavily.py from the shared folder
import sys
import os
#Adjust path to shared folder, idk why it wont work normally
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..')) 
from shared.tavily_client import search_tavily

# Example query
results = search_tavily("Rakesh Gohel, Toronto", search_depth="advanced", max_results=1)

# Display results
for result in results:
    print(f"Title: {result['title']}")
    print(f"URL: {result['url']}")
    print(f"Content: {result['content']}\n")
