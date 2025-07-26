from tavily import TavilyClient
from dotenv import load_dotenv
import os

#make sure to run this in the environment
#double check your credits

# to run this file, use the command after cd into api directory:
# python3 run_tavily.py

load_dotenv()

tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
  raise ValueError("TAVILY_API_KEY not found in environment variables.")


tavily = TavilyClient(api_key = tavily_api_key)

response = tavily.search(
  query="What is the capital of France?")

# print(response)

for result in response['results']:
  print(f"Title: {result['title']}")
  print(f"URL: {result['url']}")
  print(f"Content: {result['content']}")

