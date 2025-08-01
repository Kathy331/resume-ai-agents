"""
Enhanced Tavily API Wrapper for Research Engine

This module provides a comprehensive wrapper around the Tavily search API
with specialized search methods for different types of research:
- Company research with business-focused queries
- People/LinkedIn research with professional context
- Role/job market analysis with industry insights
- General research with customizable parameters

Features:
- Intelligent query construction for different research types
- Caching mechanism to avoid redundant API calls
- Error handling and fallback strategies
- Response parsing and data extraction
- Rate limiting and API optimization
"""

import os
import json
import time
import hashlib
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from tavily import TavilyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

@dataclass
class TavilyResult:
    """Structured representation of a Tavily search result"""
    url: str
    title: str
    content: str
    score: float
    raw_content: Optional[str] = None
    
@dataclass 
class TavilyResponse:
    """Complete Tavily API response with metadata"""
    query: str
    results: List[TavilyResult]
    follow_up_questions: Optional[List[str]]
    answer: Optional[str]
    images: List[str]
    response_time: float
    search_depth: str
    max_results: int
    timestamp: datetime

class TavilyCache:
    """Simple file-based cache for Tavily responses"""
    
    def __init__(self, cache_dir: str = ".tavily_cache", ttl_hours: int = 24):
        self.cache_dir = cache_dir
        self.ttl_hours = ttl_hours
        os.makedirs(cache_dir, exist_ok=True)
        
    def _get_cache_key(self, query: str, search_depth: str, max_results: int) -> str:
        """Generate cache key from query parameters"""
        cache_data = f"{query}_{search_depth}_{max_results}"
        return hashlib.md5(cache_data.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get full path to cache file"""
        return os.path.join(self.cache_dir, f"{cache_key}.json")
    
    def get(self, query: str, search_depth: str, max_results: int) -> Optional[TavilyResponse]:
        """Retrieve cached response if available and not expired"""
        cache_key = self._get_cache_key(query, search_depth, max_results)
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
            
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                cached_data = json.load(f)
                
            # Check if cache is expired
            cached_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cached_time > timedelta(hours=self.ttl_hours):
                os.remove(cache_path)  # Remove expired cache
                return None
                
            # Reconstruct TavilyResponse from cached data
            results = [TavilyResult(**result) for result in cached_data['results']]
            response = TavilyResponse(
                query=cached_data['query'],
                results=results,
                follow_up_questions=cached_data['follow_up_questions'],
                answer=cached_data['answer'],
                images=cached_data['images'],
                response_time=cached_data['response_time'],
                search_depth=cached_data['search_depth'],
                max_results=cached_data['max_results'],
                timestamp=datetime.fromisoformat(cached_data['timestamp'])
            )
            return response
            
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Remove corrupted cache file
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return None
    
    def set(self, response: TavilyResponse) -> None:
        """Cache a Tavily response"""
        cache_key = self._get_cache_key(response.query, response.search_depth, response.max_results)
        cache_path = self._get_cache_path(cache_key)
        
        try:
            # Convert to serializable format
            cache_data = {
                'query': response.query,
                'results': [asdict(result) for result in response.results],
                'follow_up_questions': response.follow_up_questions,
                'answer': response.answer,
                'images': response.images,
                'response_time': response.response_time,
                'search_depth': response.search_depth,
                'max_results': response.max_results,
                'timestamp': response.timestamp.isoformat()
            }
            
            with open(cache_path, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Warning: Failed to cache Tavily response: {e}")

class EnhancedTavilyClient:
    """
    Enhanced Tavily client with caching, specialized search methods,
    and intelligent query construction for different research types
    """
    
    def __init__(self, cache_enabled: bool = True, cache_ttl_hours: int = 24):
        # Initialize Tavily client
        self.api_key = os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not found in environment variables")
            
        self.client = TavilyClient(api_key=self.api_key)
        
        # Setup caching
        self.cache_enabled = cache_enabled
        self.cache = TavilyCache(ttl_hours=cache_ttl_hours) if cache_enabled else None
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # 100ms between requests
        
    def _rate_limit(self):
        """Ensure minimum interval between API requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            time.sleep(self.min_request_interval - time_since_last)
        self.last_request_time = time.time()
        
    def _search_raw(self, query: str, search_depth: str = "basic", max_results: int = 3) -> TavilyResponse:
        """
        Raw Tavily search with caching and error handling
        
        Args:
            query: Search query string
            search_depth: 'basic' or 'advanced'
            max_results: Maximum number of results to return
            
        Returns:
            TavilyResponse object with structured results
        """
        # Check cache first
        if self.cache_enabled and self.cache:
            cached_response = self.cache.get(query, search_depth, max_results)
            if cached_response:
                print(f"🗄️ Using cached result for: {query[:50]}...")
                return cached_response
        
        # Rate limiting
        self._rate_limit()
        
        # Make API request
        start_time = time.time()
        try:
            response = self.client.search(
                query=query,
                search_depth=search_depth,
                max_results=max_results
            )
            response_time = time.time() - start_time
            
            # Parse response
            results = []
            for result in response.get("results", []):
                results.append(TavilyResult(
                    url=result.get("url", ""),
                    title=result.get("title", ""),
                    content=result.get("content", ""),
                    score=result.get("score", 0.0),
                    raw_content=result.get("raw_content")
                ))
            
            tavily_response = TavilyResponse(
                query=query,
                results=results,
                follow_up_questions=response.get("follow_up_questions"),
                answer=response.get("answer"),
                images=response.get("images", []),
                response_time=response_time,
                search_depth=search_depth,
                max_results=max_results,
                timestamp=datetime.now()
            )
            
            # Cache the response
            if self.cache_enabled and self.cache:
                self.cache.set(tavily_response)
                
            return tavily_response
            
        except Exception as e:
            raise RuntimeError(f"Tavily search failed for query '{query}': {str(e)}")
    
    def search_company(self, company_name: str, search_depth: str = "advanced", max_results: int = 5) -> TavilyResponse:
        """
        Search for comprehensive company information
        
        Args:
            company_name: Name of the company to research
            search_depth: 'basic' or 'advanced' 
            max_results: Number of results to return
            
        Returns:
            TavilyResponse with company information
        """
        # Construct comprehensive company research query
        query = f"{company_name} company overview news funding culture recent developments"
        return self._search_raw(query, search_depth, max_results)
    
    def search_person_linkedin(self, person_name: str, company: str = "", university: str = "", search_depth: str = "advanced", max_results: int = 3) -> TavilyResponse:
        """
        Search for LinkedIn profiles and professional information
        
        Args:
            person_name: Name of the person to research
            company: Optional company context
            university: Optional university context
            search_depth: 'basic' or 'advanced'
            max_results: Number of results to return
            
        Returns:
            TavilyResponse with LinkedIn and professional information
        """
        # Construct LinkedIn-focused query
        query_parts = [person_name, "LinkedIn"]
        if company:
            query_parts.append(company)
        if university:
            query_parts.append(university)
            
        query = ", ".join(query_parts)
        return self._search_raw(query, search_depth, max_results)
    
    def search_role_market(self, role_title: str, company: str = "", location: str = "", search_depth: str = "basic", max_results: int = 4) -> TavilyResponse:
        """
        Search for job market information and role insights
        
        Args:
            role_title: Job title to research
            company: Optional company context
            location: Optional location context
            search_depth: 'basic' or 'advanced'
            max_results: Number of results to return
            
        Returns:
            TavilyResponse with job market and role information
        """
        # Construct role/market research query
        query_parts = [role_title, "job market", "salary", "requirements", "skills"]
        if company:
            query_parts.insert(1, f"at {company}")
        if location:
            query_parts.append(location)
            
        query = " ".join(query_parts)
        return self._search_raw(query, search_depth, max_results)
    
    def search_general(self, query: str, search_depth: str = "basic", max_results: int = 3) -> TavilyResponse:
        """
        General-purpose search method
        
        Args:
            query: Custom search query
            search_depth: 'basic' or 'advanced'
            max_results: Number of results to return
            
        Returns:
            TavilyResponse with search results
        """
        return self._search_raw(query, search_depth, max_results)
    
    def get_best_result(self, response: TavilyResponse) -> Optional[TavilyResult]:
        """Get the highest-scoring result from a response"""
        if not response.results:
            return None
        return max(response.results, key=lambda r: r.score)
    
    def extract_linkedin_urls(self, response: TavilyResponse) -> List[str]:
        """Extract LinkedIn URLs from search results"""
        linkedin_urls = []
        for result in response.results:
            if "linkedin.com" in result.url.lower():
                linkedin_urls.append(result.url)
        return linkedin_urls
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics"""
        if not self.cache_enabled or not self.cache:
            return {"cache_enabled": False}
            
        cache_files = [f for f in os.listdir(self.cache.cache_dir) if f.endswith('.json')]
        return {
            "cache_enabled": True,
            "cache_dir": self.cache.cache_dir,
            "cached_queries": len(cache_files),
            "ttl_hours": self.cache.ttl_hours
        }

# Convenience functions for backward compatibility
def search_tavily(query: str, search_depth: str = "basic", max_results: int = 3) -> list:
    """
    Legacy compatibility function - returns raw results list
    """
    client = EnhancedTavilyClient()
    response = client.search_general(query, search_depth, max_results)
    # Convert back to old format for compatibility
    return [asdict(result) for result in response.results]

# Create global instance for easy importing
tavily_client = EnhancedTavilyClient()
