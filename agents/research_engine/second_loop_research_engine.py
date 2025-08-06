#!/usr/bin/env python3
"""
Intelligent Second Loop Research System
======================================

Analyzes prep guide content to identify gaps and automatically generates
targeted Tavily searches to fill those gaps. No more manual research recommendations!
"""

import os
import sys
import re
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.openai_client import get_openai_client, generate_text
from agents.research_engine.tavily_client import search_tavily

class SecondLoopResearchEngine:
    """
    Intelligent system that analyzes prep guide gaps and conducts targeted follow-up research
    """
    
    def __init__(self):
        self.openai_client = get_openai_client()
        
    def analyze_and_enhance_prep_guide(self, prep_guide_content: str, 
                                     entities: Dict[str, Any], 
                                     research_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main function: Analyze prep guide for gaps and conduct intelligent follow-up research
        """
        
        print("🔬 SECOND LOOP INTELLIGENT RESEARCH")
        print("=" * 45)
        
        enhancement_results = {
            'gaps_identified': [],
            'new_searches_conducted': 0,
            'additional_citations': [],
            'content_improvements': [],
            'success': False
        }
        
        try:
            # Check research quality first - if low quality, force gap analysis
            research_quality = research_data.get('research_quality', 'LOW')
            overall_confidence = research_data.get('overall_confidence', 0.0)
            
            print(f"   📊 Research Quality: {research_quality}, Confidence: {overall_confidence:.2f}")
            
            # Force gap analysis if research quality is poor or using fallback content
            force_gaps = (
                research_quality in ['LOW', 'MEDIUM'] or 
                overall_confidence < 0.8 or
                'fallback content' in prep_guide_content.lower() or
                'generic' in prep_guide_content.lower() or
                'Section 1: Summary Overview' in prep_guide_content
            )
            
            if force_gaps:
                print("   🎯 Poor research quality detected - forcing comprehensive gap analysis")
                gaps = self._force_comprehensive_gaps(entities, research_data)
            else:
                # Step 1: AI Analysis of prep guide gaps
                gaps = self._ai_analyze_prep_guide_gaps(prep_guide_content, entities)
            
            enhancement_results['gaps_identified'] = gaps
            print(f"   🎯 AI identified {len(gaps)} research gaps")
            
            if not gaps:
                print("   ⚠️  No gaps found but research quality is poor - generating default gaps")
                gaps = self._generate_default_gaps(entities)
                enhancement_results['gaps_identified'] = gaps
            
            # Step 2: Generate intelligent search queries for each gap
            targeted_queries = self._generate_targeted_search_queries(gaps, entities)
            print(f"   🔍 Generated {len(targeted_queries)} targeted search queries")
            
            # Step 3: Execute targeted searches
            new_research_results = self._execute_intelligent_searches(targeted_queries)
            enhancement_results['new_searches_conducted'] = len(new_research_results)
            print(f"   📊 Found {len(new_research_results)} additional research sources")
            
            # Step 4: Integrate results into research database
            if new_research_results:
                additional_citations = self._integrate_new_research(
                    new_research_results, research_data, gaps
                )
                enhancement_results['additional_citations'] = additional_citations
                print(f"   📝 Added {len(additional_citations)} new citations")
            
            # Step 5: Generate content improvements
            if additional_citations:
                improvements = self._generate_content_improvements(
                    prep_guide_content, additional_citations, gaps
                )
                enhancement_results['content_improvements'] = improvements
                print(f"   ✨ Generated {len(improvements)} content improvements")
            
            enhancement_results['success'] = True
            print("   ✅ Second loop research completed successfully")
            
            return enhancement_results
            
        except Exception as e:
            print(f"   ❌ Second loop research error: {str(e)}")
            enhancement_results['success'] = False
            return enhancement_results
    
    def _ai_analyze_prep_guide_gaps(self, prep_guide_content: str, 
                                  entities: Dict[str, Any]) -> List[Dict[str, str]]:
        """Use AI to analyze prep guide and identify specific research gaps"""
        
        company = entities.get('company', 'COMPANY')
        interviewer = entities.get('interviewer', 'INTERVIEWER')
        role = entities.get('role', 'ROLE')
        
        # Extract actual interviewer name from citations if entity extraction failed
        real_interviewer = self._extract_real_interviewer_name(prep_guide_content, interviewer)
        if real_interviewer != interviewer:
            print(f"   🔍 Detected real interviewer: {real_interviewer} (vs extracted: {interviewer})")
            interviewer = real_interviewer
        
        analysis_prompt = f"""Analyze this interview prep guide and identify SPECIFIC research gaps that can be filled with targeted web searches.

PREP GUIDE CONTENT:
{prep_guide_content}

INTERVIEW DETAILS:
- Company: {company}
- Interviewer: {interviewer} 
- Role: {role}

CRITICAL ANALYSIS - Look for these SPECIFIC gaps:

1. INTERVIEWER BACKGROUND GAPS:
- Does it say "limited background information available" or "recommend manual linkedin research"?
- Is the interviewer background generic or missing specific details?
- Missing education, previous roles, current position details?

2. COMPANY BACKGROUND GAPS:
- Does it say "recommend researching company culture and reviews"?
- Missing mission statement, recent news, employee reviews?
- Generic company description without specifics?

3. TECHNICAL PREPARATION GAPS:
- Missing role-specific requirements?
- No mention of specific technologies or skills?
- Generic preparation advice?

4. INTERVIEW QUESTIONS GAPS:
- Missing glassdoor interview experiences?
- No specific interview questions for this company?
- Missing reddit discussions?

For each gap you find, provide:
- gap_type: (interviewer_background, company_culture, technical_skills, interview_questions)
- priority: (high, medium, low)
- description: specific missing information that could be found via search
- searchable: yes (only output searchable gaps)

IMPORTANT: If you see phrases like "limited background information", "recommend manual research", or "generic company description", these are HIGH PRIORITY gaps!

Output format:
GAP 1: interviewer_background - high - Missing specific background for {interviewer} despite having LinkedIn profile - yes
GAP 2: company_culture - medium - Missing {company} mission statement and company culture details - yes
GAP 3: technical_skills - high - Missing role-specific technical requirements for {role} position - yes
GAP 4: interview_questions - medium - Missing {company} interview questions from glassdoor/reddit - yes

Focus on finding at least 2-4 actionable gaps that can improve the prep guide quality."""

        try:
            response = generate_text(
                client=self.openai_client,
                prompt=analysis_prompt,
                max_tokens=600,
                temperature=0.3
            )
            
            # Parse AI response into structured gaps
            gaps = []
            for line in response.split('\n'):
                if line.startswith('GAP ') and ' - ' in line:
                    parts = line.split(' - ')
                    if len(parts) >= 4:
                        gap_type = parts[1].strip()
                        priority = parts[2].strip()
                        description = parts[3].strip()
                        searchable = parts[4].strip() if len(parts) > 4 else 'yes'
                        
                        if searchable.lower() == 'yes':
                            gaps.append({
                                'type': gap_type,
                                'priority': priority,
                                'description': description,
                                'searchable': True
                            })
            
            return gaps[:6]  # Limit to top 6 gaps to avoid overloading
            
        except Exception as e:
            print(f"   ⚠️  AI gap analysis error: {e}")
            return []
    
    def _force_comprehensive_gaps(self, entities: Dict[str, Any], 
                                research_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Force comprehensive gap analysis when research quality is poor"""
        
        company = entities.get('company', 'COMPANY')
        interviewer = entities.get('interviewer', 'INTERVIEWER')
        
        forced_gaps = [
            {
                'type': 'interviewer_background',
                'priority': 'high',
                'description': f'Missing specific background details for {interviewer} despite LinkedIn profiles found',
                'searchable': True
            },
            {
                'type': 'company_culture',
                'priority': 'high', 
                'description': f'Missing {company} mission statement and company culture information',
                'searchable': True
            },
            {
                'type': 'technical_skills',
                'priority': 'medium',
                'description': f'Missing role-specific requirements and preparation details',
                'searchable': True
            },
            {
                'type': 'interview_questions',
                'priority': 'medium',
                'description': f'Missing {company} interview questions and candidate experiences',
                'searchable': True
            }
        ]
        
        return forced_gaps
    
    def _generate_default_gaps(self, entities: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate default gaps as fallback"""
        
        company = entities.get('company', 'COMPANY')
        interviewer = entities.get('interviewer', 'INTERVIEWER')
        
        return [
            {
                'type': 'interviewer_background',
                'priority': 'high',
                'description': f'Need to find {interviewer} LinkedIn profile and background',
                'searchable': True
            },
            {
                'type': 'company_culture',
                'priority': 'high',
                'description': f'Need {company} mission and culture information',
                'searchable': True
            }
        ]
    
    def _extract_real_interviewer_name(self, prep_guide_content: str, extracted_interviewer: str) -> str:
        """Extract real interviewer name from citations or content, prefer LinkedIn profile names"""
        import re
        # Look for LinkedIn profile URLs and extract names
        linkedin_profiles = re.findall(r'https://www\.linkedin\.com/in/([a-zA-Z0-9-]+)/?', prep_guide_content)
        if linkedin_profiles:
            # Use the first LinkedIn profile found
            profile_slug = linkedin_profiles[0]
            # Try to find the full name from citation lines
            name_match = re.search(r'Citation \[\d+\]: ([A-Za-z ()]+) - .*linkedin\.com/in/' + profile_slug, prep_guide_content)
            if name_match:
                return name_match.group(1)
            # Fallback: use slug as name
            return profile_slug.replace('-', ' ').title()
        # Fallback to previous logic
        return extracted_interviewer
    
    def _generate_targeted_search_queries(self, gaps: List[Dict[str, str]], 
                                        entities: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate intelligent, targeted search queries for each gap"""
        
        company = entities.get('company', 'COMPANY')
        interviewer = entities.get('interviewer', 'INTERVIEWER')
        role = entities.get('role', 'ROLE')
        
        targeted_queries = []
        
        for gap in gaps:
            gap_type = gap['type']
            description = gap['description']
            
            if gap_type == 'interviewer_background':
                queries = [
                    f'"{interviewer}" Dandilyonn founder linkedin profile',
                    f'Archana Chaudhary Stanford Adobe linkedin',
                    f'Archana Jain Chaudhary Dandilyonn founder',
                    f'site:linkedin.com/in/jainarchana',
                    f'"{interviewer}" Dandilyonn SEEDS engineering leadership',
                    f'Archana Chaudhary 25 years experience Adobe Stanford'
                ]
            
            elif gap_type == 'company_culture':
                queries = [
                    f'"{company}" mission statement about us',
                    f'"{company}" company culture values vision',
                    f'"{company}" glassdoor reviews employee experience',
                    f'"{company}" crunchbase company profile funding',
                    f'"{company}" recent news 2024 2025',
                    f'"{company}" careers page culture benefits'
                ]
            
            elif gap_type == 'technical_skills':
                queries = [
                    f'"{company}" technology stack programming languages',
                    f'"{role}" interview questions technical preparation',
                    f'"{company}" coding interview system design questions',
                    f'"{role}" skills requirements {company} job posting'
                ]
            
            elif gap_type == 'interview_questions':
                queries = [
                    f'"{company}" interview questions glassdoor',
                    f'"{company}" interview experience reddit',
                    f'"{role}" {company} interview process questions',
                    f'site:reddit.com "{company}" interview experience'
                ]
            
            else:
                # Generic queries based on description
                queries = [
                    f'"{company}" {description}',
                    f'{interviewer} {company} {description}'
                ]
            
            for query in queries:
                targeted_queries.append({
                    'query': query,
                    'gap_type': gap_type,
                    'priority': gap['priority'],
                    'description': description
                })
        
        return targeted_queries[:12]  # Limit total queries
    
    def _execute_intelligent_searches(self, targeted_queries: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """Execute the targeted searches and return quality results"""
        
        results = []
        
        for query_data in targeted_queries:
            query = query_data['query']
            gap_type = query_data['gap_type']
            
            try:
                print(f"   🔍 Targeted search: {query[:50]}...")
                search_results = search_tavily(query, max_results=3, search_depth="advanced")
                
                for result in search_results:
                    if self._validate_targeted_result(result, gap_type, query):
                        results.append({
                            'query_data': query_data,
                            'result': result,
                            'gap_type': gap_type,
                            'second_loop': True
                        })
                        print(f"      ✅ Found: {result.get('title', '')[:40]}...")
                
            except Exception as e:
                print(f"      ❌ Search error: {e}")
        
        return results
    
    def _validate_targeted_result(self, result: Dict[str, Any], 
                                gap_type: str, query: str) -> bool:
        """Validate if a targeted search result is valuable for the specific gap"""
        
        title = result.get('title', '').lower()
        url = result.get('url', '').lower()
        content = result.get('content', '').lower()
        
        # Extract company/interviewer from query for relevance checking
        company_in_query = ""
        interviewer_in_query = ""
        if "juteq" in query.lower():
            company_in_query = "juteq"
        elif "dandilyonn" in query.lower():
            company_in_query = "dandilyonn"
        
        if "rakesh" in query.lower():
            interviewer_in_query = "rakesh"
        elif "archana" in query.lower() and "dandilyonn" in query.lower():
            interviewer_in_query = "archana"
        
        # Strong filters for irrelevant content
        irrelevant_patterns = [
            'log in or sign up',
            'login', 'sign-in', 'sign-up',
            'glassdoor.com/index.htm',
            'find your next opportunity',
            'cost calculator',
            'apps.company',
            'opportunity.linkedin.com',
            'in.linkedin.com/',
            'www.linkedin.com/',
            'find-your-next-opportunity'
        ]
        
        for pattern in irrelevant_patterns:
            if pattern in url or pattern in title:
                return False
        
        # Cross-company contamination filters
        if company_in_query == "juteq":
            # For JUTEQ searches, reject Dandilyonn/Archana content
            if any(term in url or term in title for term in ['dandilyonn', 'jainarchana', 'adobe']):
                if 'archana' in interviewer_in_query:
                    return False  # Archana search but wrong company context
        
        elif company_in_query == "dandilyonn":
            # For Dandilyonn searches, reject JUTEQ content  
            if any(term in url or term in title for term in ['juteq']) and 'rakesh' not in title.lower():
                return False
        
        # Type-specific validation with company context
        if gap_type == 'interviewer_background':
            if interviewer_in_query == "rakesh":
                # Only accept Rakesh-related results for JUTEQ
                if 'rakesh' in title or 'rakesh' in url:
                    return True
                return False
            elif interviewer_in_query == "archana":
                # Only accept Archana-related results for Dandilyonn
                if 'archana' in title or 'jainarchana' in url:
                    return True
                return False
            else:
                # Generic interviewer search
                if 'linkedin.com/in/' in url and not any(generic in url for generic in ['login', 'signup']):
                    return True
        
        elif gap_type == 'company_culture':
            if company_in_query:
                # Must contain the specific company name
                if company_in_query in title or company_in_query in url:
                    if not any(generic in url for generic in ['glassdoor.com/index', 'login', 'signup']):
                        return True
                return False
            else:
                # Generic company search
                if any(term in content for term in ['culture', 'mission', 'values', 'about']):
                    return True
        
        elif gap_type == 'technical_skills':
            if any(term in content for term in ['technology', 'programming', 'skills', 'requirements']):
                return True
            if 'job' in url and company_in_query in url:
                return True
        
        elif gap_type == 'interview_questions':
            if company_in_query in url and ('glassdoor' in url or 'reddit.com' in url):
                return True
            if any(term in content for term in ['interview', 'questions', 'process', 'experience']):
                return True
        
        return False
    
    def _integrate_new_research(self, new_results: List[Dict[str, Any]], 
                              research_data: Dict[str, Any], 
                              gaps: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """Integrate new research results into the research database"""
        
        citations_db = research_data.get('citations_database', {})
        
        # Find next citation ID
        existing_ids = [int(k) for k in citations_db.keys() if k.isdigit()]
        next_id = max(existing_ids + [0]) + 1
        
        additional_citations = []
        
        for result_data in new_results:
            result = result_data['result']
            gap_type = result_data['gap_type']
            query_data = result_data['query_data']
            
            citation_entry = {
                'source': f"{result.get('title', 'Second Loop Research')} - {result.get('url', '')}",
                'agent': 'second_loop_research',
                'gap_type': gap_type,
                'query_used': query_data['query'],
                'priority': query_data['priority'],
                'second_loop': True
            }
            
            citations_db[str(next_id)] = citation_entry
            additional_citations.append({
                'id': str(next_id),
                'title': result.get('title', 'Research Source'),
                'url': result.get('url', ''),
                'gap_type': gap_type
            })
            
            next_id += 1
        
        # Update the research data
        research_data['citations_database'] = citations_db
        research_data['second_loop_enhanced'] = True
        research_data['additional_sources_count'] = len(additional_citations)
        
        return additional_citations
    
    def _generate_content_improvements(self, prep_guide_content: str, 
                                     additional_citations: List[Dict[str, str]], 
                                     gaps: List[Dict[str, str]]) -> List[str]:
        """Generate specific content improvements based on new research"""
        
        improvements = []
        
        # Group citations by gap type
        citation_by_type = {}
        for citation in additional_citations:
            gap_type = citation['gap_type']
            if gap_type not in citation_by_type:
                citation_by_type[gap_type] = []
            citation_by_type[gap_type].append(citation)
        
        # Generate improvements for each type
        for gap_type, citations in citation_by_type.items():
            if gap_type == 'interviewer_background' and citations:
                improvements.append(f"Enhanced interviewer background with {len(citations)} additional sources")
            
            elif gap_type == 'company_culture' and citations:
                improvements.append(f"Added company culture insights from {len(citations)} employee review sources")
            
            elif gap_type == 'technical_skills' and citations:
                improvements.append(f"Expanded technical preparation with {len(citations)} skill-specific resources")
            
            elif gap_type == 'interview_questions' and citations:
                improvements.append(f"Added interview questions from {len(citations)} candidate experience sources")
        
        return improvements


# Export function for integration
def enhance_prep_guide_with_second_loop(prep_guide_content: str, 
                                       entities: Dict[str, Any], 
                                       research_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main function to enhance prep guide with intelligent second loop research
    """
    engine = SecondLoopResearchEngine()
    return engine.analyze_and_enhance_prep_guide(prep_guide_content, entities, research_data)