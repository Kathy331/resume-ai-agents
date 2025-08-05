#!/usr/bin/env python3
"""
Research Engine - Simple Tavily Integration
===========================================

Basic research engine for the interview prep workflow
"""

import os
from typing import List, Dict, Any

def search_tavily(query: str, search_depth: str = "basic", max_results: int = 5) -> List[Dict[str, Any]]:
    """
    Simple Tavily search function
    This is a basic implementation that can be expanded
    """
    try:
        # Import tavily client if available
        from tavily import TavilyClient
        
        api_key = os.getenv('TAVILY_API_KEY')
        if not api_key:
            print("⚠️ TAVILY_API_KEY not found in environment variables")
            return []
        
        client = TavilyClient(api_key=api_key)
        
        # Perform search
        response = client.search(
            query=query,
            search_depth=search_depth,
            max_results=max_results
        )
        
        return response.get('results', [])
        
    except ImportError:
        print("⚠️ Tavily client not installed. Install with: pip install tavily-python")
        return []
    except Exception as e:
        print(f"❌ Tavily search error: {str(e)}")
        return []

# Create a simple tavily_client module compatibility
class TavilyClient:
    """Simple compatibility class for tavily client"""
    def __init__(self, api_key: str):
        self.api_key = api_key
    
    def search(self, query: str, search_depth: str = "basic", max_results: int = 5):
        """Simple search method - uses the main search_tavily function"""
        return {"results": search_tavily(query, search_depth, max_results)}

def analyze_research_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze research results and extract key information
    """
    analysis = {
        'total_sources': len(results),
        'validated_sources': [],
        'citations': {},
        'confidence_score': 0.0
    }
    
    # Basic validation and analysis
    for i, result in enumerate(results):
        if result.get('url') and result.get('title'):
            analysis['validated_sources'].append(result)
            analysis['citations'][f'citation_{i+1}'] = {
                'title': result.get('title', 'Unknown'),
                'url': result.get('url', ''),
                'content': result.get('content', '')[:200] + '...' if result.get('content') else ''
            }
    
    # Calculate basic confidence score
    if analysis['total_sources'] > 0:
        analysis['confidence_score'] = len(analysis['validated_sources']) / analysis['total_sources']
    
    return analysis