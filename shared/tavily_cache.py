"""
Tavily Search Results Caching System
Reduces redundant API calls by caching search results
"""

import json
import hashlib
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path

class TavilyCache:
    """Cache system for Tavily search results to reduce API calls"""
    
    def __init__(self, cache_dir: str = "cache/tavily", cache_expiry_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_expiry = timedelta(hours=cache_expiry_hours)
    
    def _generate_cache_key(self, query: str, search_depth: str = "basic", max_results: int = 5) -> str:
        """Generate unique cache key for query parameters"""
        cache_string = f"{query.lower().strip()}|{search_depth}|{max_results}"
        return hashlib.md5(cache_string.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get file path for cache key"""
        return self.cache_dir / f"{cache_key}.json"
    
    def get_cached_results(self, query: str, search_depth: str = "basic", max_results: int = 5) -> Optional[List[Dict[str, Any]]]:
        """Retrieve cached results if available and not expired"""
        try:
            cache_key = self._generate_cache_key(query, search_depth, max_results)
            cache_path = self._get_cache_path(cache_key)
            
            if not cache_path.exists():
                return None
            
            with open(cache_path, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cached_time > self.cache_expiry:
                # Remove expired cache
                cache_path.unlink(missing_ok=True)
                return None
            
            print(f"   🎯 CACHE HIT: '{query[:50]}...' ({len(cache_data['results'])} results)")
            return cache_data['results']
            
        except Exception as e:
            print(f"   ⚠️ Cache read error: {str(e)}")
            return None
    
    def cache_results(self, query: str, results: List[Dict[str, Any]], search_depth: str = "basic", max_results: int = 5) -> None:
        """Cache search results for future use"""
        try:
            cache_key = self._generate_cache_key(query, search_depth, max_results)
            cache_path = self._get_cache_path(cache_key)
            
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'query': query,
                'search_depth': search_depth,
                'max_results': max_results,
                'results': results
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
            
            print(f"   💾 CACHED: '{query[:50]}...' ({len(results)} results)")
            
        except Exception as e:
            print(f"   ⚠️ Cache write error: {str(e)}")
    
    def clear_expired_cache(self) -> int:
        """Clear all expired cache files and return count of files removed"""
        removed_count = 0
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cache_data['timestamp'])
                    if datetime.now() - cached_time > self.cache_expiry:
                        cache_file.unlink()
                        removed_count += 1
                        
                except Exception:
                    # Remove corrupted cache files
                    cache_file.unlink(missing_ok=True)
                    removed_count += 1
            
            if removed_count > 0:
                print(f"   🧹 Cleaned {removed_count} expired cache files")
                
        except Exception as e:
            print(f"   ⚠️ Cache cleanup error: {str(e)}")
        
        return removed_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            cache_files = list(self.cache_dir.glob("*.json"))
            total_files = len(cache_files)
            
            valid_files = 0
            expired_files = 0
            total_results = 0
            
            for cache_file in cache_files:
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    cached_time = datetime.fromisoformat(cache_data['timestamp'])
                    if datetime.now() - cached_time > self.cache_expiry:
                        expired_files += 1
                    else:
                        valid_files += 1
                        total_results += len(cache_data.get('results', []))
                        
                except Exception:
                    expired_files += 1
            
            return {
                'total_cache_files': total_files,
                'valid_cache_files': valid_files,
                'expired_cache_files': expired_files,
                'total_cached_results': total_results,
                'cache_directory': str(self.cache_dir)
            }
            
        except Exception as e:
            return {'error': str(e)}


# Global cache instance
_tavily_cache = None

def get_tavily_cache() -> TavilyCache:
    """Get global Tavily cache instance"""
    global _tavily_cache
    if _tavily_cache is None:
        _tavily_cache = TavilyCache()
    return _tavily_cache


def cached_search_tavily(query: str, search_depth: str = "basic", max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Cached version of search_tavily function
    First checks cache, then calls API if needed and caches result
    """
    try:
        from shared.tavily_client import search_tavily
        
        cache = get_tavily_cache()
        
        # Try to get from cache first
        cached_results = cache.get_cached_results(query, search_depth, max_results)
        if cached_results is not None:
            return cached_results
        
        # Cache miss - call API
        print(f"   🔍 API CALL: '{query[:50]}...'")
        results = search_tavily(query, search_depth, max_results)
        
        # Cache the results
        cache.cache_results(query, results, search_depth, max_results)
        
        return results
        
    except Exception as e:
        print(f"   ❌ Cached search error: {str(e)}")
        return []
