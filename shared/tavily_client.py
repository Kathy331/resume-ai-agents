# This file handles interactions with the Tavily search client.
# It includes a function to perform a search with a given query and return results.

import os
from tavily import TavilyClient
from dotenv import load_dotenv

# Load .env file 
load_dotenv()

# Initialize Tavily client
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY not found in environment variables.")

client = TavilyClient(api_key=tavily_api_key)

def search_tavily(query: str, search_depth: str = "basic", max_results: int = 3) -> list:
    """
    Performs a Tavily search for the given query.
    
    Args:
        query (str): The search query string.
        search_depth (str): The depth of the search ('basic' or 'advanced').
        max_results (int): Maximum number of results to return.
    
    Returns:
        list: A list of search results (each a dict with title, url, content).
    """
    try:
        response = client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results
        )
        return response.get("results", [])
    except Exception as e:
        raise RuntimeError(f"Tavily search failed: {str(e)}")
