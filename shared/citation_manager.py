#!/usr/bin/env python3
"""
Citation Manager - Manages Research Citations
=============================================

Handles citation formatting, tracking, and database management
"""

import re
from typing import Dict, List, Any, Optional
from urllib.parse import urlparse


class CitationManager:
    """Manages citations for research and prep guide generation"""
    
    def __init__(self):
        self.citations_db = {}
        self.citation_counter = 1
    
    def add_citation(self, category: str, title: str, url: str) -> int:
        """
        Add a citation and return its number
        """
        citation_id = self.citation_counter
        
        if category not in self.citations_db:
            self.citations_db[category] = []
        
        citation = {
            'id': citation_id,
            'title': title,
            'url': url,
            'category': category
        }
        
        self.citations_db[category].append(citation)
        self.citation_counter += 1
        
        return citation_id
    
    def get_citation_reference(self, citation_id: int) -> str:
        """
        Get citation reference string for use in content
        """
        return f"[Citation {citation_id}]"
    
    def format_citations_database(self) -> str:
        """
        Format complete citations database for output
        """
        if not self.citations_db:
            return "Research conducted using available public sources and professional networks"
        
        formatted_citations = []
        citation_num = 1
        
        for category, citations in self.citations_db.items():
            for citation in citations:
                title = citation['title'][:50] + "..." if len(citation['title']) > 50 else citation['title']
                formatted_citations.append(
                    f"📝 Citation [{citation_num}]: {title} - {citation['url']}"
                )
                citation_num += 1
        
        result = '\n'.join(formatted_citations)
        result += f"\n\nTotal Citations: {len(formatted_citations)}"
        
        return result
    
    def count_citations_in_content(self, content: str) -> int:
        """
        Count how many citations are referenced in content
        """
        return len(re.findall(r'\[Citation \d+\]', content))
    
    def get_citations_count(self) -> int:
        """
        Get total number of citations in database
        """
        total = 0
        for citations in self.citations_db.values():
            total += len(citations)
        return total
    
    def clear_citations(self):
        """
        Clear all citations
        """
        self.citations_db = {}
        self.citation_counter = 1
    
    def process_research_citations(self, citations_database: Dict) -> List[Dict]:
        """
        Process raw citations from research pipeline into clean, validated citations
        
        Args:
            citations_database: Raw citations from research pipeline
            
        Returns:
            List of validated, formatted citations
        """
        validated_citations = []
        
        for citation_id, citation_data in citations_database.items():
            if not isinstance(citation_data, dict):
                continue
                
            processed_citation = self._process_single_citation(citation_id, citation_data)
            if processed_citation:
                validated_citations.append(processed_citation)
        
        # Sort by quality score (highest first)
        validated_citations.sort(key=lambda x: x.get('quality_score', 0), reverse=True)
        
        return validated_citations
    
    def _process_single_citation(self, citation_id: str, citation_data: Dict) -> Optional[Dict]:
        """Process and validate a single citation"""
        source_text = citation_data.get('source', '')
        if not source_text:
            return None
        
        # Parse title and URL from source text
        title, url = self._parse_source_text(source_text)
        
        if not title:
            return None
        
        # Calculate quality score
        quality_score = self._calculate_citation_quality(title, url, citation_data)
        
        # Skip low-quality citations
        if quality_score < 2:
            return None
        
        return {
            'id': citation_id,
            'title': title,
            'url': url,
            'snippet': citation_data.get('content_snippet', ''),
            'agent_source': citation_data.get('agent', 'research'),
            'quality_score': quality_score,
            'domain': self._extract_domain(url),
            'citation_type': self._determine_citation_type(url, title)
        }
    
    def _parse_source_text(self, source_text: str) -> tuple:
        """Parse title and URL from source text"""
        source_text = source_text.strip()
        
        # Common patterns for source text
        patterns = [
            r'^(.*?)\s*-\s*(https?://[^\s]+)$',  # Title - URL
            r'^(.*?)\s*\|\s*(https?://[^\s]+)$',  # Title | URL  
            r'^(.*?)\s+(https?://[^\s]+)$',       # Title URL
        ]
        
        for pattern in patterns:
            match = re.match(pattern, source_text)
            if match:
                title = match.group(1).strip()
                url = match.group(2).strip()
                return title, url
        
        # If no URL found, treat entire text as title
        if 'http' not in source_text:
            return source_text, ''
        
        # Extract URL from anywhere in the text
        url_match = re.search(r'https?://[^\s]+', source_text)
        if url_match:
            url = url_match.group(0)
            title = source_text.replace(url, '').strip(' -|')
            return title, url
        
        return source_text, ''
    
    def _calculate_citation_quality(self, title: str, url: str, citation_data: Dict) -> int:
        """Calculate quality score for citation (0-10)"""
        score = 0
        
        # Title quality
        if title and len(title) > 10:
            score += 2
        if title and not title.lower().startswith('untitled'):
            score += 1
        
        # URL quality
        if url:
            score += 2
            domain = self._extract_domain(url)
            
            # Bonus for high-quality domains
            quality_domains = [
                'linkedin.com', 'crunchbase.com', 'techcrunch.com', 
                'bloomberg.com', 'reuters.com', 'wsj.com', 'forbes.com',
                'glassdoor.com', 'indeed.com', 'company websites'
            ]
            
            if any(domain.endswith(qd) for qd in quality_domains):
                score += 2
        
        # Content quality
        snippet = citation_data.get('content_snippet', '')
        if snippet and len(snippet) > 50:
            score += 1
        
        # Agent source bonus
        agent = citation_data.get('agent', '')
        if agent in ['company_analysis', 'interviewer_analysis']:
            score += 1
        
        return min(score, 10)
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return ''
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return ''
    
    def _determine_citation_type(self, url: str, title: str) -> str:
        """Determine the type of citation"""
        domain = self._extract_domain(url)
        title_lower = title.lower()
        
        if 'linkedin.com' in domain:
            if '/company/' in url:
                return 'linkedin_company'
            elif '/in/' in url:
                return 'linkedin_profile'
            else:
                return 'linkedin_post'
        elif 'crunchbase.com' in domain:
            return 'company_profile'
        elif any(news in domain for news in ['techcrunch', 'bloomberg', 'reuters', 'wsj', 'forbes']):
            return 'news_article'
        elif any(job in domain for job in ['glassdoor', 'indeed', 'monster']):
            return 'job_listing'
        elif 'about' in title_lower or 'company' in title_lower:
            return 'company_info'
        else:
            return 'general'
    
    def format_citations_for_guide(self, citations: List[Dict], max_citations: int = 12) -> Dict:
        """
        Format citations for inclusion in prep guide
        
        Args:
            citations: List of processed citations
            max_citations: Maximum number of citations to include
            
        Returns:
            Dictionary with formatted citation text and database
        """
        # Select top citations
        selected_citations = citations[:max_citations]
        
        # Create citation database text
        citation_db_text = "Complete database of all research citations used in the preparation guide:\n\n"
        
        for i, citation in enumerate(selected_citations, 1):
            citation_db_text += f"📝 Citation [{i}]: {citation['title']}"
            if citation['url']:
                citation_db_text += f" - {citation['url']}"
            citation_db_text += f"\n"
        
        citation_db_text += f"\nTotal Citations: {len(selected_citations)}"
        
        # Create citation mapping for content integration
        citation_mapping = {}
        for i, citation in enumerate(selected_citations, 1):
            citation_mapping[citation['id']] = {
                'number': i,
                'title': citation['title'],
                'url': citation['url'],
                'type': citation['citation_type']
            }
        
        return {
            'database_text': citation_db_text,
            'mapping': citation_mapping,
            'count': len(selected_citations),
            'citations': selected_citations
        }
    
    def create_citation_context_for_ai(self, citations: List[Dict], max_citations: int = 8) -> str:
        """
        Create citation context for AI prompt
        
        Args:
            citations: List of processed citations
            max_citations: Maximum citations to include in context
            
        Returns:
            Formatted citation context string
        """
        context = "AVAILABLE RESEARCH CITATIONS:\n"
        context += "Use these citations naturally in your response using [Citation X] format.\n\n"
        
        for i, citation in enumerate(citations[:max_citations], 1):
            context += f"Citation {i}:\n"
            context += f"Title: {citation['title']}\n"
            context += f"Source: {citation['url']}\n"
            context += f"Type: {citation['citation_type']}\n"
            context += f"Content: {citation['snippet'][:200]}...\n\n"
        
        context += f"Total available citations: {len(citations[:max_citations])}\n"
        context += "Instructions: Reference citations naturally within your content using [Citation X] where X is the citation number.\n"
        
        return context
    
    def validate_citation_usage(self, generated_content: str, available_citations: List[Dict]) -> Dict:
        """
        Validate that citations are used properly in generated content
        
        Args:
            generated_content: AI-generated content with citations
            available_citations: List of available citations
            
        Returns:
            Validation results
        """
        # Find all citation references in content
        citation_pattern = r'\[Citation (\d+)\]'
        used_citations = re.findall(citation_pattern, generated_content)
        
        # Convert to integers
        used_citation_numbers = [int(num) for num in used_citations]
        
        # Validate citation numbers
        max_available = len(available_citations)
        invalid_citations = [num for num in used_citation_numbers if num > max_available or num < 1]
        
        return {
            'total_citations_used': len(used_citation_numbers),
            'unique_citations_used': len(set(used_citation_numbers)),
            'invalid_citations': invalid_citations,
            'citation_coverage': len(set(used_citation_numbers)) / max(max_available, 1),
            'is_valid': len(invalid_citations) == 0
        }


def integrate_citations_with_prep_guide(prep_guide_content: str, citations: List[Dict]) -> str:
    """
    Integrate citation references with the prep guide content
    
    Args:
        prep_guide_content: Generated prep guide content
        citations: List of processed citations
        
    Returns:
        Prep guide content with properly formatted citation references
    """
    citation_manager = CitationManager()
    
    # Validate citations are used correctly
    validation = citation_manager.validate_citation_usage(prep_guide_content, citations)
    
    if not validation['is_valid']:
        print(f"⚠️ Citation validation issues found: {validation['invalid_citations']}")
    
    # Add citation summary at the end if citations are used
    if validation['total_citations_used'] > 0:
        prep_guide_content += f"\n\n---\n*This prep guide incorporates insights from {validation['unique_citations_used']} research sources to provide comprehensive, data-driven preparation strategies.*"
    
    return prep_guide_content

# Global citation manager instance
_citation_manager = None

def get_citation_manager() -> CitationManager:
    """Get global citation manager instance"""
    global _citation_manager
    if _citation_manager is None:
        _citation_manager = CitationManager()
    return _citation_manager