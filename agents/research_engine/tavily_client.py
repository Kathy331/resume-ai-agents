#!/usr/bin/env python3
"""
Simple Tavily Client Compatibility
=================================

Provides basic compatibility for the tavily client import
"""

import os
from typing import List, Dict, Any

def search_tavily(query: str, search_depth: str = "basic", max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Simple Tavily search function
    """
    try:
        from tavily import TavilyClient
        
        api_key = os.getenv('TAVILY_API_KEY')
        if not api_key:
            return []
        
        client = TavilyClient(api_key=api_key)
        response = client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results
        )
        
        return response.get('results', [])
        
    except Exception:
        return []

class EnhancedTavilyClient:
    """Enhanced Tavily client wrapper for compatibility"""
    
    def __init__(self, api_key: str = None, cache_enabled: bool = True, cache_ttl_hours: int = 168):
        self.api_key = api_key or os.getenv('TAVILY_API_KEY', '')
        self.cache_enabled = cache_enabled
        self.cache_ttl_hours = cache_ttl_hours
    
    def search(self, query: str, search_depth: str = "basic", max_results: int = 5):
        """Search using tavily"""
        results = search_tavily(query, search_depth, max_results)
        return {"results": results}
    
    def search_general(self, query: str, max_results: int = 5):
        """General search method required by research pipeline"""
        results = search_tavily(query, "basic", max_results)
        return {"results": results}
    
    def search_linkedin(self, query: str, max_results: int = 5):
        """LinkedIn-specific search method"""
        linkedin_query = f"{query} site:linkedin.com"
        results = search_tavily(linkedin_query, "basic", max_results)
        return {"results": results}
    
    def search_company(self, company_name: str, max_results: int = 5):
        """Company-specific search method"""
        company_query = f"{company_name} company website about"
        results = search_tavily(company_query, "basic", max_results)
        return {"results": results}
    
    def get_search_context(self, query: str, search_depth: str = "basic", max_results: int = 5):
        """Get search context"""
        return self.search(query, search_depth, max_results)