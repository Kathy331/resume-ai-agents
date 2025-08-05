"""
Research Engine Package
=====================

Provides research functionality for the interview prep workflow
"""

from .tavily_client import search_tavily, EnhancedTavilyClient

__all__ = ['search_tavily', 'EnhancedTavilyClient']