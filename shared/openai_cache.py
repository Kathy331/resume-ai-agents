# shared/openai_cache.py
"""
OpenAI Response Caching System
Similar to TavilyCache but for OpenAI API responses
Reduces API calls and costs during development and testing
"""

import os
import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class OpenAICacheEntry:
    """Cache entry for OpenAI responses"""
    prompt: str
    model: str
    max_tokens: int
    temperature: float  
    response: str
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'prompt': self.prompt,
            'model': self.model,
            'max_tokens': self.max_tokens,
            'temperature': self.temperature,
            'response': self.response,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'OpenAICacheEntry':
        """Create from dictionary (JSON deserialization)"""
        return cls(
            prompt=data['prompt'],
            model=data['model'],
            max_tokens=data['max_tokens'],
            temperature=data['temperature'],
            response=data['response'],
            timestamp=datetime.fromisoformat(data['timestamp'])
        )


class OpenAICache:
    """File-based cache for OpenAI API responses"""
    
    def __init__(self, cache_dir: str = ".openai_cache", ttl_hours: int = 168):  # 1 week TTL
        """
        Initialize OpenAI cache
        
        Args:
            cache_dir: Directory to store cache files
            ttl_hours: Time-to-live in hours (default: 1 week)
        """
        self.cache_dir = cache_dir
        self.ttl_hours = ttl_hours
        os.makedirs(cache_dir, exist_ok=True)
        
        # Create cache info file if it doesn't exist
        self.info_file = os.path.join(cache_dir, "_cache_info.json")
        if not os.path.exists(self.info_file):
            self._write_cache_info({
                "created": datetime.now().isoformat(),
                "total_entries": 0,
                "companies_cached": [],
                "last_updated": datetime.now().isoformat()
            })
    
    def _get_cache_key(self, prompt: str, model: str, max_tokens: int, temperature: float) -> str:
        """Generate cache key from parameters"""
        # Create a stable hash from all parameters
        cache_data = f"{prompt}_{model}_{max_tokens}_{temperature}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get full path to cache file"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def _write_cache_info(self, info: Dict[str, Any]) -> None:
        """Write cache information"""
        try:
            with open(self.info_file, 'w', encoding='utf-8') as f:
                json.dump(info, f, indent=2)
        except Exception:
            pass  # Fail silently if can't write info
    
    def _update_cache_info(self, company_name: Optional[str] = None) -> None:
        """Update cache information"""
        try:
            if os.path.exists(self.info_file):
                with open(self.info_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
            else:
                info = {"companies_cached": [], "total_entries": 0}
            
            # Count total entries
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json') and f != '_cache_info.json']
            info["total_entries"] = len(cache_files)
            info["last_updated"] = datetime.now().isoformat()
            
            # Add company if provided and not already in list
            if company_name and company_name not in info.get("companies_cached", []):
                info.setdefault("companies_cached", []).append(company_name)
            
            self._write_cache_info(info)
        except Exception:
            pass  # Fail silently
    
    def get(self, prompt: str, model: str, max_tokens: int, temperature: float) -> Optional[str]:
        """
        Retrieve cached response if available and not expired
        
        Returns:
            Cached response string or None if not found/expired
        """
        cache_key = self._get_cache_key(prompt, model, max_tokens, temperature)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
            
            # Check if cache is expired
            entry = OpenAICacheEntry.from_dict(cached_data)
            if datetime.now() - entry.timestamp > timedelta(hours=self.ttl_hours):
                os.remove(cache_path)  # Remove expired cache
                self._update_cache_info()
                return None
            
            return entry.response
            
        except (json.JSONDecodeError, KeyError, ValueError, FileNotFoundError):
            # Remove corrupted cache file
            if os.path.exists(cache_path):
                try:
                    os.remove(cache_path)
                except:
                    pass
            return None
    
    def set(self, prompt: str, model: str, max_tokens: int, temperature: float, response: str, company_name: Optional[str] = None) -> None:
        """
        Cache an OpenAI response
        
        Args:
            prompt: The input prompt
            model: Model used
            max_tokens: Max tokens parameter
            temperature: Temperature parameter  
            response: The response to cache
            company_name: Optional company name for tracking
        """
        cache_key = self._get_cache_key(prompt, model, max_tokens, temperature)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            entry = OpenAICacheEntry(
                prompt=prompt,
                model=model,
                max_tokens=max_tokens,
                temperature=temperature,
                response=response,
                timestamp=datetime.now()
            )
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(entry.to_dict(), f, indent=2, ensure_ascii=False)
            
            self._update_cache_info(company_name)
            
        except Exception as e:
            # If caching fails, continue without caching
            pass
    
    def clear(self) -> int:
        """Clear all cached entries"""
        cleared_count = 0
        try:
            for filename in os.listdir(self.cache_dir):
                if filename.endswith('.json'):
                    file_path = os.path.join(self.cache_dir, filename)
                    os.remove(file_path)
                    cleared_count += 1
            
            # Reset cache info
            self._write_cache_info({
                "created": datetime.now().isoformat(),
                "total_entries": 0,
                "companies_cached": [],
                "last_updated": datetime.now().isoformat()
            })
            
        except Exception:
            pass
        
        return cleared_count
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        try:
            if os.path.exists(self.info_file):
                with open(self.info_file, 'r', encoding='utf-8') as f:
                    info = json.load(f)
            else:
                info = {"total_entries": 0, "companies_cached": []}
            
            # Count actual files
            cache_files = [f for f in os.listdir(self.cache_dir) if f.endswith('.json') and f != '_cache_info.json']
            actual_count = len(cache_files)
            
            return {
                "total_entries": actual_count,
                "companies_cached": info.get("companies_cached", []),
                "cache_dir": self.cache_dir,
                "ttl_hours": self.ttl_hours,
                "last_updated": info.get("last_updated", "Unknown")
            }
        except Exception:
            return {
                "total_entries": 0,
                "companies_cached": [],
                "cache_dir": self.cache_dir,
                "ttl_hours": self.ttl_hours,
                "last_updated": "Unknown"
            }


def create_openai_cache(cache_dir: str = ".openai_cache", ttl_hours: int = 168) -> OpenAICache:
    """Factory function to create OpenAI cache instance"""
    return OpenAICache(cache_dir=cache_dir, ttl_hours=ttl_hours)


# For testing and CLI usage
if __name__ == "__main__":
    print("🗄️ OpenAI Cache System")
    cache = OpenAICache()
    stats = cache.get_cache_stats()
    
    print(f"📊 Cache Statistics:")
    print(f"   Total Entries: {stats['total_entries']}")
    print(f"   Companies Cached: {len(stats['companies_cached'])}")
    print(f"   Cache Directory: {stats['cache_dir']}")
    print(f"   TTL Hours: {stats['ttl_hours']}")
    print(f"   Last Updated: {stats['last_updated']}")
    
    if stats['companies_cached']:
            print(f"   Companies: {', '.join(stats['companies_cached'])}")


# Global cache instance and utility functions
_global_cache = None

def get_global_openai_cache() -> OpenAICache:
    """Get the global OpenAI cache instance"""
    global _global_cache
    if _global_cache is None:
        _global_cache = OpenAICache()
    return _global_cache


def get_openai_cache_stats() -> Dict[str, Any]:
    """Get OpenAI cache statistics from global cache"""
    cache = get_global_openai_cache()
    return cache.get_cache_stats()


def clear_openai_cache() -> Dict[str, Any]:
    """Clear the OpenAI cache"""
    cache = get_global_openai_cache()
    entries_cleared = cache.clear()
    
    return {
        "message": f"OpenAI cache cleared - removed {entries_cleared} entries",
        "cleared_entries": entries_cleared
    }