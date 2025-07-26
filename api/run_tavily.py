from tavily import TavilyClient
from dotenv import load_dotenv
import os

#make sure to run this in the environment
#double check your credits

# to run this file, use the command after cd into api directory:
# python3 run_tavily.py
# https://www.youtube.com/watch?v=PDy9qnbD7VA (tavily tutorial)

load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
  raise ValueError("TAVILY_API_KEY not found in environment variables.")


tavily = TavilyClient(api_key = tavily_api_key)

# Test query
response = tavily.search(
  query="Rakesh Gohel, Toronto",
  search_depth="advanced",
  max_results=1
)
print(response)

# for result in response['results']:
#   print(f"Title: {result['title']}")
#   print(f"URL: {result['url']}")
#   print(f"Content: {result['content']}")

