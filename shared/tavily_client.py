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

# Import cached Tavily client
try:
    from agents.research_engine.tavily_client import EnhancedTavilyClient
    cached_client = EnhancedTavilyClient(cache_enabled=True, cache_ttl_hours=168)  # 1 week cache
    print("🗄️ Tavily cache enabled (TTL: 1 week)")
except ImportError as e:
    print(f"⚠️ Cached Tavily client not available: {e}")
    cached_client = None

def search_tavily(query: str, search_depth: str = "basic", max_results: int = 3) -> list:
    """
    Performs a Tavily search for the given query with caching support.
    
    Args:
        query (str): The search query string.
        search_depth (str): The depth of the search ('basic' or 'advanced').
        max_results (int): Maximum number of results to return.
    
    Returns:
        list: A list of search results (each a dict with title, url, content).
    """
    try:
        # Use cached client if available
        if cached_client:
            response = cached_client.search_general(query, search_depth, max_results)
            # Convert to list format for compatibility
            return [
                {
                    "title": result.title,
                    "url": result.url,
                    "content": result.content,
                    "score": result.score
                }
                for result in response.results
            ]
        else:
            # Fallback to direct client
            response = client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results
            )
            return response.get("results", [])
    except Exception as e:
        print(f"❌ Tavily search failed: {str(e)}")
        raise RuntimeError(f"Tavily search failed: {str(e)}")

def get_tavily_cache_stats() -> dict:
    """Get Tavily cache statistics"""
    if cached_client and cached_client.cache:
        stats = cached_client.get_cache_stats()
        # Add more useful info
        if stats.get('cache_enabled', False):
            stats['total_entries'] = stats.get('cached_queries', 0)
            # More accurate Tavily pricing estimate
            # Tavily typically charges ~$0.005 per search query (5 requests for $0.025)
            cost_per_query = 0.005  # $0.005 per query
            cached_queries = stats.get('cached_queries', 0)
            stats['estimated_savings'] = round(cached_queries * cost_per_query, 3)
            stats['cost_per_query'] = cost_per_query
            stats['cache_hit_rate'] = f"{cached_queries} queries cached"
        return stats
    return {"cache_enabled": False, "message": "Cache not available"}
