#!/usr/bin/env python3
"""
Simple Cache System for Interview Prep Workflow
===============================================

Provides caching for both Tavily API calls and OpenAI API calls
to avoid repeated API requests for the same content.
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

class SimpleCache:
    """Simple file-based cache system"""
    
    def __init__(self, cache_dir: str, ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl_hours = ttl_hours
    
    def _get_cache_key(self, data: str) -> str:
        """Generate cache key from data"""
        return hashlib.md5(data.encode()).hexdigest()
    
    def _get_cache_file(self, key: str) -> Path:
        """Get cache file path"""
        return self.cache_dir / f"{key}.json"
    
    def _is_expired(self, file_path: Path) -> bool:
        """Check if cache file is expired"""
        if not file_path.exists():
            return True
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            cached_time = datetime.fromisoformat(data.get('timestamp', ''))
            expiry_time = cached_time + timedelta(hours=self.ttl_hours)
            
            return datetime.now() > expiry_time
        except:
            return True
    
    def get(self, key_data: str) -> Optional[Any]:
        """Get cached data"""
        key = self._get_cache_key(key_data)
        file_path = self._get_cache_file(key)
        
        if self._is_expired(file_path):
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            return data.get('content')
        except:
            return None
    
    def set(self, key_data: str, content: Any):
        """Set cached data"""
        key = self._get_cache_key(key_data)
        file_path = self._get_cache_file(key)
        
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'content': content
        }
        
        try:
            with open(file_path, 'w') as f:
                json.dump(cache_data, f, indent=2)
        except Exception as e:
            print(f"Cache write error: {e}")
    
    def clear(self) -> int:
        """Clear all cache files"""
        count = 0
        for file_path in self.cache_dir.glob("*.json"):
            try:
                file_path.unlink()
                count += 1
            except:
                pass
        return count
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        files = list(self.cache_dir.glob("*.json"))
        valid_files = []
        expired_files = []
        
        for file_path in files:
            if self._is_expired(file_path):
                expired_files.append(file_path)
            else:
                valid_files.append(file_path)
        
        total_size = sum(f.stat().st_size for f in files)
        
        return {
            'total_files': len(files),
            'valid_files': len(valid_files),
            'expired_files': len(expired_files),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }


# Global cache instances
_tavily_cache = None
_openai_cache = None

def get_tavily_cache() -> SimpleCache:
    """Get Tavily cache instance"""
    global _tavily_cache
    if _tavily_cache is None:
        _tavily_cache = SimpleCache("cache/tavily", ttl_hours=24)
    return _tavily_cache

def get_openai_cache() -> SimpleCache:
    """Get OpenAI cache instance"""
    global _openai_cache
    if _openai_cache is None:
        _openai_cache = SimpleCache("cache/openai", ttl_hours=168)  # 1 week
    return _openai_cache

def cached_tavily_search(query: str, max_results: int = 5) -> list:
    """Cached Tavily search"""
    cache = get_tavily_cache()
    cache_key = f"tavily_{query}_{max_results}"
    
    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        print(f"   💾 Using cached Tavily result for: {query[:50]}...")
        return cached_result
    
    # Make API call
    try:
        from agents.research_engine.tavily_client import search_tavily
        results = search_tavily(query, max_results=max_results)
        
        # Cache the result
        cache.set(cache_key, results)
        print(f"   🔍 Fresh Tavily search cached: {query[:50]}...")
        
        return results
    except Exception as e:
        print(f"   ❌ Tavily search error: {e}")
        return []

def cached_openai_generate(prompt: str, model: str = "gpt-4", **kwargs) -> str:
    """Cached OpenAI generation"""
    cache = get_openai_cache()
    cache_key = f"openai_{model}_{prompt}_{str(sorted(kwargs.items()))}"
    
    # Try cache first
    cached_result = cache.get(cache_key)
    if cached_result is not None:
        print(f"   💾 Using cached OpenAI response...")
        return cached_result
    
    # Make API call
    try:
        from shared.openai_client import generate_text
        result = generate_text(prompt=prompt, model=model, **kwargs)
        
        # Cache the result
        cache.set(cache_key, result)
        print(f"   🤖 Fresh OpenAI response cached...")
        
        return result
    except Exception as e:
        print(f"   ❌ OpenAI generation error: {e}")
        return ""