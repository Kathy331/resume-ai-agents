#!/usr/bin/env python3
"""
Intelligent Research Engine - Advanced AI-Powered Research Enhancement
====================================================================

This adds a layer of AI intelligence to improve research quality:
1. Analyze initial Tavily results
2. Infer missing information and generate new search queries
3. Validate findings and suggest additional searches
4. Improve interviewer name extraction and company analysis
"""

import os
import sys
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.openai_client import get_openai_client, generate_text
from agents.research_engine.tavily_client import search_tavily

class IntelligentResearchEngine:
    """
    AI-powered research enhancement engine
    """
    
    def __init__(self):
        self.openai_client = get_openai_client()
        
    def enhance_research_quality(self, initial_research_data: Dict[str, Any], 
                               entities: Dict[str, Any], 
                               email_content: str) -> Dict[str, Any]:
        """
        Enhance research quality using AI inference and additional targeted searches
        """
        
        print("🧠 INTELLIGENT RESEARCH ENHANCEMENT")
        print("=" * 50)
        
        enhanced_research = initial_research_data.copy()
        
        try:
            # Step 1: Analyze current research gaps
            gaps = self._analyze_research_gaps(initial_research_data, entities)
            print(f"   🔍 Identified {len(gaps)} research gaps")
            
            # Step 2: Generate intelligent follow-up queries
            if gaps:
                follow_up_queries = self._generate_intelligent_queries(gaps, entities, email_content)
                print(f"   🎯 Generated {len(follow_up_queries)} intelligent follow-up queries")
                
                # Step 3: Execute targeted searches
                additional_results = self._execute_targeted_searches(follow_up_queries)
                print(f"   📊 Executed searches, found {len(additional_results)} additional sources")
                
                # Step 4: Integrate results
                enhanced_research = self._integrate_enhanced_results(
                    initial_research_data, additional_results, gaps
                )
            
            # Step 5: Final quality assessment
            final_quality = self._assess_final_quality(enhanced_research, entities)
            enhanced_research['intelligence_enhanced'] = True
            enhanced_research['final_quality_score'] = final_quality
            
            print(f"   ✅ Research enhancement completed - Quality score: {final_quality:.2f}")
            
            return enhanced_research
            
        except Exception as e:
            print(f"   ❌ Research enhancement error: {str(e)}")
            return initial_research_data
    
    def _analyze_research_gaps(self, research_data: Dict[str, Any], 
                             entities: Dict[str, Any]) -> List[Dict[str, str]]:
        """Analyze current research to identify gaps"""
        
        gaps = []
        
        # Check interviewer research quality
        interviewer_name = entities.get('interviewer', '')
        if interviewer_name and interviewer_name != 'Not specified':
            # Check if we found the actual interviewer's LinkedIn profile
            citations = research_data.get('citations_database', {})
            interviewer_found = False
            
            for citation_data in citations.values():
                if isinstance(citation_data, dict):
                    source = citation_data.get('source', '').lower()
                    if 'linkedin.com/in/' in source and interviewer_name.lower() in source:
                        interviewer_found = True
                        break
            
            if not interviewer_found:
                gaps.append({
                    'type': 'interviewer_profile',
                    'description': f'No LinkedIn profile found for {interviewer_name}',
                    'priority': 'high',
                    'target': interviewer_name
                })
        
        # Check company research depth
        company_name = entities.get('company', '')
        if company_name:
            company_citations = 0
            for citation_data in research_data.get('citations_database', {}).values():
                if isinstance(citation_data, dict):
                    source = citation_data.get('source', '').lower()
                    if company_name.lower() in source and 'linkedin.com/company/' in source:
                        company_citations += 1
            
            if company_citations < 2:
                gaps.append({
                    'type': 'company_depth',
                    'description': f'Insufficient company information for {company_name}',
                    'priority': 'medium',
                    'target': company_name
                })
        
        return gaps
    
    def _generate_intelligent_queries(self, gaps: List[Dict[str, str]], 
                                    entities: Dict[str, Any], 
                                    email_content: str) -> List[str]:
        """Generate intelligent follow-up queries based on gaps and AI inference"""
        
        queries = []
        
        for gap in gaps:
            if gap['type'] == 'interviewer_profile':
                # Try intelligent name variations and company connections
                interviewer_name = gap['target']
                company_name = entities.get('company', '')
                
                # Infer possible name variations and search strategies
                inferred_queries = self._infer_interviewer_searches(interviewer_name, company_name, email_content)
                queries.extend(inferred_queries)
            
            elif gap['type'] == 'company_depth':
                # Generate deeper company research queries
                company_name = gap['target']
                company_queries = self._generate_company_depth_queries(company_name)
                queries.extend(company_queries)
        
        return queries[:8]  # Limit to avoid overloading
    
    def _infer_interviewer_searches(self, interviewer_name: str, 
                                  company_name: str, 
                                  email_content: str) -> List[str]:
        """Use AI to infer better interviewer search strategies"""
        
        try:
            # Use AI to analyze the interviewer name and suggest search variations
            prompt = f"""Analyze this interviewer name and suggest intelligent LinkedIn search queries:

Interviewer: {interviewer_name}
Company: {company_name}
Email context: {email_content[:200]}...

Based on the name "{interviewer_name}", suggest 4 intelligent search variations that might find their LinkedIn profile:

1. Consider if this might be a first name, last name, or partial name
2. Look for cultural/linguistic variations
3. Consider professional title inferences
4. Think about company-specific search strategies

Output format:
- Query 1: [specific search string]
- Query 2: [specific search string]  
- Query 3: [specific search string]
- Query 4: [specific search string]

Keep queries practical for LinkedIn/professional search."""

            response = generate_text(
                client=self.openai_client,
                prompt=prompt,
                max_tokens=300,
                temperature=0.3
            )
            
            # Parse the response to extract queries
            queries = []
            for line in response.split('\n'):
                if '- Query' in line and ':' in line:
                    query = line.split(':', 1)[1].strip()
                    if query and len(query) > 10:
                        queries.append(query)
            
            return queries
            
        except Exception as e:
            print(f"   ⚠️  AI inference error: {e}")
            # Fallback to rule-based approach
            return [
                f'"{interviewer_name}" "{company_name}" LinkedIn profile',
                f'site:linkedin.com/in "{interviewer_name}"',
                f'{interviewer_name} {company_name} employee',
                f'LinkedIn "{interviewer_name}" {company_name} team'
            ]
    
    def _generate_company_depth_queries(self, company_name: str) -> List[str]:
        """Generate deeper company research queries"""
        
        return [
            f'"{company_name}" about us mission values',
            f'"{company_name}" recent news 2025 funding',
            f'"{company_name}" glassdoor reviews culture',
            f'"{company_name}" leadership team founders executives'
        ]
    
    def _execute_targeted_searches(self, queries: List[str]) -> List[Dict[str, Any]]:
        """Execute the intelligent follow-up searches"""
        
        results = []
        
        for query in queries:
            try:
                print(f"   🔍 Intelligent search: {query[:50]}...")
                search_results = search_tavily(query, max_results=3)
                
                for result in search_results:
                    if self._validate_enhanced_result(result, query):
                        results.append({
                            'query': query,
                            'result': result,
                            'intelligence_enhanced': True
                        })
                        print(f"      ✅ Found relevant result: {result.get('title', '')[:40]}...")
                
            except Exception as e:
                print(f"      ❌ Search error for '{query}': {e}")
        
        return results
    
    def _validate_enhanced_result(self, result: Dict[str, Any], query: str) -> bool:
        """Validate if an enhanced search result is valuable"""
        
        title = result.get('title', '').lower()
        url = result.get('url', '').lower()
        content = result.get('content', '').lower()
        
        # Quality filters
        if 'linkedin.com/in/' in url:
            return True  # LinkedIn profiles are valuable
        
        if 'linkedin.com/company/' in url:
            return True  # Company pages are valuable
        
        if any(term in url for term in ['about', 'careers', 'team', 'leadership']):
            return True  # Company info pages are valuable
        
        if 'glassdoor' in url and 'reviews' in url:
            return True  # Company reviews are valuable
        
        # Avoid generic or low-quality results
        avoid_patterns = ['login', 'sign-in', 'register', 'search?', 'find-job']
        if any(pattern in url for pattern in avoid_patterns):
            return False
        
        return True
    
    def _integrate_enhanced_results(self, original_research: Dict[str, Any], 
                                  additional_results: List[Dict[str, Any]], 
                                  gaps: List[Dict[str, str]]) -> Dict[str, Any]:
        """Integrate enhanced results into the original research"""
        
        enhanced_research = original_research.copy()
        
        # Add new citations from enhanced research
        citations_db = enhanced_research.get('citations_database', {})
        new_citation_id = max([int(k) for k in citations_db.keys() if k.isdigit()] + [0]) + 1
        
        for result_data in additional_results:
            result = result_data['result']
            citations_db[str(new_citation_id)] = {
                'source': f"{result.get('title', 'Enhanced Research')} - {result.get('url', '')}",
                'agent': 'intelligent_research',
                'intelligence_enhanced': True,
                'query_used': result_data['query']
            }
            new_citation_id += 1
        
        enhanced_research['citations_database'] = citations_db
        enhanced_research['enhanced_sources_count'] = len(additional_results)
        
        # Update quality metrics
        if 'overall_confidence' in enhanced_research:
            # Boost confidence if we found valuable additional sources
            boost = min(0.1, len(additional_results) * 0.02)
            enhanced_research['overall_confidence'] = min(1.0, enhanced_research['overall_confidence'] + boost)
        
        return enhanced_research
    
    def _assess_final_quality(self, research_data: Dict[str, Any], 
                            entities: Dict[str, Any]) -> float:
        """Assess the final quality of enhanced research"""
        
        quality_score = 0.0
        
        # Base score from original research
        quality_score += research_data.get('overall_confidence', 0.5) * 0.6
        
        # Bonus for finding interviewer profile
        interviewer_name = entities.get('interviewer', '')
        if interviewer_name:
            for citation_data in research_data.get('citations_database', {}).values():
                if isinstance(citation_data, dict):
                    source = citation_data.get('source', '').lower()
                    if 'linkedin.com/in/' in source and interviewer_name.lower() in source:
                        quality_score += 0.2
                        break
        
        # Bonus for company depth
        company_citations = 0
        for citation_data in research_data.get('citations_database', {}).values():
            if isinstance(citation_data, dict):
                source = citation_data.get('source', '').lower()
                if any(term in source for term in ['company', 'about', 'glassdoor']):
                    company_citations += 1
        
        quality_score += min(0.2, company_citations * 0.05)
        
        return min(1.0, quality_score)


# Export function for easy integration
def enhance_research_with_intelligence(research_data: Dict[str, Any], 
                                     entities: Dict[str, Any], 
                                     email_content: str) -> Dict[str, Any]:
    """
    Main function to enhance research using intelligent analysis
    """
    engine = IntelligentResearchEngine()
    return engine.enhance_research_quality(research_data, entities, email_content)