# This file handles interactions with the Tavily search client.
# It includes a function to perform a search with a given query and return results.

import os
import time
import hashlib
from tavily import TavilyClient
from dotenv import load_dotenv

# Load .env file 
load_dotenv()

# Initialize Tavily client
tavily_api_key = os.getenv("TAVILY_API_KEY")
if not tavily_api_key:
    raise ValueError("TAVILY_API_KEY not found in environment variables.")

client = TavilyClient(api_key=tavily_api_key)

# Simple in-memory cache implementation
class SimpleTavilyCache:
    def __init__(self, cache_ttl_hours: int = 168):  # 1 week default
        self.cache = {}
        self.cache_ttl_seconds = cache_ttl_hours * 3600
        self.cache_hits = 0
        self.cache_misses = 0
        
    def _get_cache_key(self, query: str, search_depth: str, max_results: int) -> str:
        """Generate cache key from query parameters"""
        key_string = f"{query}|{search_depth}|{max_results}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def get(self, query: str, search_depth: str, max_results: int):
        """Get cached result if available and not expired"""
        cache_key = self._get_cache_key(query, search_depth, max_results)
        if cache_key in self.cache:
            cached_item = self.cache[cache_key]
            if time.time() - cached_item['timestamp'] < self.cache_ttl_seconds:
                self.cache_hits += 1
                return cached_item['result']
            else:
                # Expired, remove from cache
                del self.cache[cache_key]
        self.cache_misses += 1
        return None
    
    def set(self, query: str, search_depth: str, max_results: int, result):
        """Cache the result"""
        cache_key = self._get_cache_key(query, search_depth, max_results)
        self.cache[cache_key] = {
            'result': result,
            'timestamp': time.time()
        }
    
    def get_stats(self):
        """Get cache statistics"""
        total_queries = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total_queries * 100) if total_queries > 0 else 0
        return {
            'cache_enabled': True,
            'cached_queries': len(self.cache),
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': round(hit_rate, 2),
            'total_entries': len(self.cache)
        }

# Initialize cache
tavily_cache = SimpleTavilyCache(cache_ttl_hours=168)  # 1 week cache
print("🗄️ Tavily cache enabled (TTL: 1 week)")

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
        # Check cache first
        cached_result = tavily_cache.get(query, search_depth, max_results)
        if cached_result is not None:
            print(f"🗄️ Cache hit for query: {query[:50]}...")
            return cached_result
        
        # Cache miss - perform actual search
        print(f"🔍 Searching Tavily for: {query[:50]}...")
        response = client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results
        )
        
        results = response.get("results", [])
        
        # Cache the results
        tavily_cache.set(query, search_depth, max_results, results)
        
        return results
        
    except Exception as e:
        print(f"❌ Tavily search failed: {str(e)}")
        raise RuntimeError(f"Tavily search failed: {str(e)}")

def get_tavily_cache_stats() -> dict:
    """Get Tavily cache statistics"""
    stats = tavily_cache.get_stats()
    
    # Add cost savings calculation
    if stats.get('cache_enabled', False):
        # More accurate Tavily pricing estimate
        # Tavily typically charges ~$0.005 per search query (5 requests for $0.025)
        cost_per_query = 0.005  # $0.005 per query
        cache_hits = stats.get('cache_hits', 0)
        stats['estimated_savings'] = round(cache_hits * cost_per_query, 3)
        stats['cost_per_query'] = cost_per_query
        stats['cache_hit_info'] = f"{cache_hits} cache hits saved API calls"
    
    return stats

def clear_tavily_cache() -> dict:
    """Clear the Tavily cache"""
    cache_entries = len(tavily_cache.cache)
    tavily_cache.cache.clear()
    tavily_cache.cache_hits = 0
    tavily_cache.cache_misses = 0
    
    return {
        "message": f"Tavily cache cleared - removed {cache_entries} entries",
        "cleared_entries": cache_entries
    }
