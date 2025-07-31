"""
Company Intelligence Researcher

This module provides comprehensive company research capabilities using
the Tavily search API. It extracts and structures company information
for interview preparation and job application insights.

Features:
- Company overview and background research
- Recent news and developments
- Funding and financial information
- Company culture and values analysis
- Leadership and key personnel information
- Structured data extraction from search results
"""

import re
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from .tavily_client import EnhancedTavilyClient, TavilyResponse, TavilyResult

@dataclass
class CompanyInfo:
    """Structured company information"""
    name: str
    description: str = ""
    industry: str = ""
    size: str = ""
    headquarters: str = ""
    founded: str = ""
    website: str = ""
    linkedin_url: str = ""
    
@dataclass
class CompanyNews:
    """Company news and recent developments"""
    title: str
    content: str
    url: str
    date: str = ""
    source: str = ""
    
@dataclass
class CompanyFinancials:
    """Company financial and funding information"""
    funding_stage: str = ""
    total_funding: str = ""
    valuation: str = ""
    investors: List[str] = None
    recent_funding: str = ""
    
    def __post_init__(self):
        if self.investors is None:
            self.investors = []

@dataclass
class CompanyResearchResult:
    """Complete company research results"""
    company_info: CompanyInfo
    recent_news: List[CompanyNews]
    financials: CompanyFinancials
    key_insights: List[str]
    search_metadata: Dict[str, Any]
    research_timestamp: datetime

class CompanyResearcher:
    """
    Intelligent company research using Tavily API
    """
    
    def __init__(self, tavily_client: Optional[EnhancedTavilyClient] = None):
        self.tavily_client = tavily_client or EnhancedTavilyClient()
        
    def research_company(self, company_name: str, deep_search: bool = True) -> CompanyResearchResult:
        """
        Conduct comprehensive company research
        
        Args:
            company_name: Name of the company to research
            deep_search: Whether to perform additional detailed searches
            
        Returns:
            CompanyResearchResult with structured company information
        """
        print(f"🔍 Researching company: {company_name}")
        
        # Primary company search
        search_depth = "advanced" if deep_search else "basic"
        max_results = 7 if deep_search else 4
        
        primary_response = self.tavily_client.search_company(
            company_name, 
            search_depth=search_depth, 
            max_results=max_results
        )
        
        # Extract structured information
        company_info = self._extract_company_info(company_name, primary_response)
        recent_news = self._extract_news(primary_response)
        financials = self._extract_financials(primary_response)
        key_insights = self._extract_insights(primary_response)
        
        # Additional targeted searches if deep search is enabled
        if deep_search:
            # News-specific search
            news_response = self.tavily_client.search_general(
                f"{company_name} news recent developments 2024 2025",
                search_depth="basic",
                max_results=3
            )
            recent_news.extend(self._extract_news(news_response))
            
            # Funding-specific search
            funding_response = self.tavily_client.search_general(
                f"{company_name} funding investment valuation startup",
                search_depth="basic", 
                max_results=3
            )
            funding_financials = self._extract_financials(funding_response)
            financials = self._merge_financials(financials, funding_financials)
        
        # Remove duplicates from news
        recent_news = self._deduplicate_news(recent_news)
        
        return CompanyResearchResult(
            company_info=company_info,
            recent_news=recent_news[:5],  # Limit to top 5 news items
            financials=financials,
            key_insights=key_insights,
            search_metadata={
                "company_name": company_name,
                "deep_search": deep_search,
                "total_results": len(primary_response.results),
                "response_time": primary_response.response_time,
                "search_depth": search_depth
            },
            research_timestamp=datetime.now()
        )
    
    def _extract_company_info(self, company_name: str, response: TavilyResponse) -> CompanyInfo:
        """Extract basic company information from search results"""
        company_info = CompanyInfo(name=company_name)
        
        # Analyze search results for company information
        all_content = " ".join([result.content for result in response.results])
        
        # Extract website (look for official company domains)
        website_patterns = [
            rf"https?://(?:www\.)?([a-zA-Z0-9-]+\.(?:com|org|net|io|co))",
            rf"{re.escape(company_name.lower().replace(' ', ''))}\.(?:com|org|net|io|co)"
        ]
        
        for pattern in website_patterns:
            matches = re.finditer(pattern, all_content, re.IGNORECASE)
            for match in matches:
                potential_website = match.group(0) if match.group(0).startswith('http') else f"https://{match.group(0)}"
                if not company_info.website and self._is_likely_company_website(potential_website, company_name):
                    company_info.website = potential_website
                    break
            if company_info.website:
                break
        
        # Extract LinkedIn URL
        linkedin_pattern = r"https?://(?:www\.)?linkedin\.com/company/[a-zA-Z0-9-]+"
        linkedin_matches = re.finditer(linkedin_pattern, all_content)
        for match in linkedin_matches:
            company_info.linkedin_url = match.group(0)
            break
        
        # Extract description from highest-scoring result
        if response.results:
            best_result = max(response.results, key=lambda r: r.score)
            company_info.description = self._extract_description(best_result.content, company_name)
        
        # Extract industry, size, headquarters from content
        company_info.industry = self._extract_industry(all_content)
        company_info.size = self._extract_company_size(all_content)
        company_info.headquarters = self._extract_headquarters(all_content)
        company_info.founded = self._extract_founded_year(all_content)
        
        return company_info
    
    def _extract_news(self, response: TavilyResponse) -> List[CompanyNews]:
        """Extract recent news from search results"""
        news_items = []
        
        for result in response.results:
            # Look for news-like content
            if self._is_news_content(result):
                news_item = CompanyNews(
                    title=result.title,
                    content=result.content[:500] + "..." if len(result.content) > 500 else result.content,
                    url=result.url,
                    source=self._extract_source_name(result.url)
                )
                news_items.append(news_item)
        
        return news_items
    
    def _extract_financials(self, response: TavilyResponse) -> CompanyFinancials:
        """Extract financial and funding information"""
        financials = CompanyFinancials()
        
        all_content = " ".join([result.content for result in response.results])
        
        # Extract funding information
        funding_patterns = [
            r"raised \$([0-9.,]+(?:\s*(?:million|billion|M|B))?)",
            r"funding of \$([0-9.,]+(?:\s*(?:million|billion|M|B))?)",
            r"Series [A-Z] of \$([0-9.,]+(?:\s*(?:million|billion|M|B))?)",
            r"valuation of \$([0-9.,]+(?:\s*(?:million|billion|M|B))?)"
        ]
        
        for pattern in funding_patterns:
            matches = re.finditer(pattern, all_content, re.IGNORECASE)
            for match in matches:
                if not financials.recent_funding:
                    financials.recent_funding = match.group(0)
                    break
        
        # Extract funding stage
        stage_patterns = [
            r"(Series [A-Z])",
            r"(Seed round)",
            r"(Pre-seed)",
            r"(IPO)",
            r"(Private equity)"
        ]
        
        for pattern in stage_patterns:
            matches = re.search(pattern, all_content, re.IGNORECASE)
            if matches:
                financials.funding_stage = matches.group(1)
                break
        
        return financials
    
    def _extract_insights(self, response: TavilyResponse) -> List[str]:
        """Extract key insights and notable information"""
        insights = []
        
        # Use Tavily's answer if available
        if response.answer:
            insights.append(f"AI Summary: {response.answer}")
        
        # Extract insights from high-scoring results
        for result in response.results[:3]:  # Top 3 results
            if result.score > 0.6:  # High confidence results
                # Look for notable phrases and achievements
                content = result.content
                
                # Extract notable achievements or facts
                achievement_patterns = [
                    r"((?:largest|leading|first|only|pioneer)[^.]*)",
                    r"((?:awarded|recognized|selected)[^.]*)",
                    r"((?:launched|founded|established)[^.]*)",
                    r"(market leader[^.]*)",
                    r"(valued at[^.]*)"
                ]
                
                for pattern in achievement_patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        insight = match.group(1).strip()
                        if len(insight) > 20 and insight not in insights:
                            insights.append(insight[:200] + "..." if len(insight) > 200 else insight)
                            if len(insights) >= 5:
                                break
                    if len(insights) >= 5:
                        break
                if len(insights) >= 5:
                    break
        
        return insights[:5]  # Limit to top 5 insights
    
    def _is_likely_company_website(self, url: str, company_name: str) -> bool:
        """Check if URL is likely the company's official website"""
        company_parts = company_name.lower().replace(' ', '').replace('-', '')
        url_lower = url.lower()
        
        # Simple heuristic: company name should be in domain
        return company_parts in url_lower and not any(exclude in url_lower for exclude in ['linkedin', 'facebook', 'twitter', 'news', 'blog'])
    
    def _extract_description(self, content: str, company_name: str) -> str:
        """Extract company description from content"""
        # Look for sentences that describe what the company does
        sentences = content.split('.')
        for sentence in sentences[:3]:  # Check first 3 sentences
            if len(sentence.strip()) > 50 and company_name.lower() in sentence.lower():
                return sentence.strip()
        
        # Fallback: return first substantial sentence
        for sentence in sentences:
            if len(sentence.strip()) > 50:
                return sentence.strip()
        
        return content[:200] + "..." if len(content) > 200 else content
    
    def _extract_industry(self, content: str) -> str:
        """Extract industry information"""
        industry_keywords = [
            "technology", "software", "fintech", "healthcare", "biotech", 
            "e-commerce", "retail", "manufacturing", "consulting", "financial services",
            "artificial intelligence", "machine learning", "cloud", "cybersecurity"
        ]
        
        content_lower = content.lower()
        for keyword in industry_keywords:
            if keyword in content_lower:
                return keyword.title()
        
        return ""
    
    def _extract_company_size(self, content: str) -> str:
        """Extract company size information"""
        size_patterns = [
            r"(\d+(?:,\d+)*)\s*employees",
            r"team of (\d+(?:,\d+)*)",
            r"(\d+(?:,\d+)*)\s*people"
        ]
        
        for pattern in size_patterns:
            matches = re.search(pattern, content, re.IGNORECASE)
            if matches:
                return f"{matches.group(1)} employees"
        
        return ""
    
    def _extract_headquarters(self, content: str) -> str:
        """Extract headquarters location"""
        location_patterns = [
            r"headquartered in ([^.,]+)",
            r"based in ([^.,]+)",
            r"headquarters in ([^.,]+)"
        ]
        
        for pattern in location_patterns:
            matches = re.search(pattern, content, re.IGNORECASE)
            if matches:
                return matches.group(1).strip()
        
        return ""
    
    def _extract_founded_year(self, content: str) -> str:
        """Extract founding year"""
        year_patterns = [
            r"founded in (\d{4})",
            r"established in (\d{4})", 
            r"started in (\d{4})"
        ]
        
        for pattern in year_patterns:
            matches = re.search(pattern, content, re.IGNORECASE)
            if matches:
                return matches.group(1)
        
        return ""
    
    def _is_news_content(self, result: TavilyResult) -> bool:
        """Determine if a result contains news content"""
        news_indicators = ['news', 'announces', 'launches', 'partners', 'acquired', 'funding', 'investment']
        title_content = (result.title + " " + result.content).lower()
        return any(indicator in title_content for indicator in news_indicators)
    
    def _extract_source_name(self, url: str) -> str:
        """Extract source name from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            return domain.split('.')[0].title()
        except:
            return "Unknown"
    
    def _merge_financials(self, financials1: CompanyFinancials, financials2: CompanyFinancials) -> CompanyFinancials:
        """Merge two CompanyFinancials objects, preferring non-empty values"""
        merged = CompanyFinancials()
        
        for field in ['funding_stage', 'total_funding', 'valuation', 'recent_funding']:
            value1 = getattr(financials1, field)
            value2 = getattr(financials2, field) 
            setattr(merged, field, value1 or value2)
        
        # Merge investor lists
        merged.investors = list(set(financials1.investors + financials2.investors))
        
        return merged
    
    def _deduplicate_news(self, news_items: List[CompanyNews]) -> List[CompanyNews]:
        """Remove duplicate news items based on title similarity"""
        unique_news = []
        seen_titles = set()
        
        for news in news_items:
            title_key = news.title.lower().strip()
            if title_key not in seen_titles:
                unique_news.append(news)
                seen_titles.add(title_key)
        
        return unique_news
    
    def format_research_summary(self, research: CompanyResearchResult) -> str:
        """Format research results into a readable summary"""
        summary = []
        
        # Company overview
        summary.append(f"## {research.company_info.name}")
        summary.append(f"**Industry:** {research.company_info.industry}")
        if research.company_info.description:
            summary.append(f"**Description:** {research.company_info.description}")
        
        if research.company_info.headquarters:
            summary.append(f"**Headquarters:** {research.company_info.headquarters}")
        if research.company_info.founded:
            summary.append(f"**Founded:** {research.company_info.founded}")
        if research.company_info.size:
            summary.append(f"**Size:** {research.company_info.size}")
        
        # Key insights
        if research.key_insights:
            summary.append("\n**Key Insights:**")
            for insight in research.key_insights:
                summary.append(f"• {insight}")
        
        # Recent news
        if research.recent_news:
            summary.append("\n**Recent News:**")
            for news in research.recent_news[:3]:
                summary.append(f"• [{news.title}]({news.url})")
        
        # Financial information
        if research.financials.recent_funding or research.financials.funding_stage:
            summary.append("\n**Financial Information:**")
            if research.financials.funding_stage:
                summary.append(f"• Funding Stage: {research.financials.funding_stage}")
            if research.financials.recent_funding:
                summary.append(f"• Recent Funding: {research.financials.recent_funding}")
        
        return "\n".join(summary)

# Create global instance for easy importing
company_researcher = CompanyResearcher()
