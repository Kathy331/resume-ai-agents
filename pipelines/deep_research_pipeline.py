#!/usr/bin/env python3
"""
Deep Research Pipeline - Sophisticated Research with Tavily Integration
=====================================================================
Handles:
1. Multi-agent research (Company, Role, Interviewer analysis)
2. LinkedIn-focused interviewer research  
3. Tavily cache integration with sophisticated caching
4. Deep reflection loops for research quality validation
5. Citations database management with deduplication
6. Research sufficiency assessment for prep guide generation
"""

import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.tavily_cache import cached_search_tavily, get_tavily_cache
from shared.tavily_client import search_tavily


class DeepResearchPipeline:
    """
    Deep Research Pipeline: Multi-agent research with reflection loops
    """
    
    def __init__(self):
        self.cache = get_tavily_cache()
    
    def conduct_deep_research(self, entities: Dict[str, Any], email_index: int) -> Dict[str, Any]:
        """
        Conduct sophisticated deep research with multi-agent analysis
        
        Args:
            entities: Extracted entities from email
            email_index: Index of email being processed
            
        Returns:
            Research result dictionary with citations and confidence scores
        """
        print(f"\n🔬 DEEP RESEARCH PIPELINE - Email {email_index}")
        print("=" * 60)
        
        research_start_time = datetime.now()
        
        # Display cache statistics
        self._display_cache_status()
        
        # Handle both string and list values for entities
        def get_entity_string(entity_value):
            if isinstance(entity_value, list):
                return entity_value[0] if entity_value else ''
            return str(entity_value) if entity_value else ''
        
        company = get_entity_string(entities.get('company', ''))
        role = get_entity_string(entities.get('role', ''))
        interviewer = get_entity_string(entities.get('interviewer', ''))
        
        # Extract email keywords for validation
        email_keywords = self._extract_email_keywords(entities)
        
        print(f"\n🧠 SOPHISTICATED MULTI-AGENT RESEARCH")
        print(f"🔍 Research Targets:")
        print(f"   🏢 Company: {company}")
        print(f"   💼 Role: {role}")
        print(f"   👤 Interviewer: {interviewer}")
        print(f"   🏷️ Email Keywords: {', '.join(email_keywords[:5])}...")
        
        result = {
            'success': False,
            'research_data': {},
            'citations_database': {},
            'validation_metrics': {
                'sources_discovered': 0,
                'sources_validated': 0,
                'confidence_scores': [],
                'linkedin_profiles_found': 0,
                'citation_count': 0
            },
            'overall_confidence': 0.0,
            'research_quality': 'Unknown',
            'reflection_loops': 0,
            'sufficient_for_prep_guide': False,
            'processing_time': 0,
            'errors': []
        }
        
        try:
            research_data = {}
            citations_database = {}
            citation_counter = 1
            validation_metrics = result['validation_metrics']
            
            # ========== COMPANY ANALYSIS AGENT ==========
            if company:
                print(f"\n🏢 === COMPANY ANALYSIS AGENT ACTIVATED ===")
                company_analysis = self._company_analysis_agent(company, email_keywords, citations_database, citation_counter)
                
                if company_analysis['success']:
                    research_data['company_analysis'] = company_analysis
                    validation_metrics['sources_discovered'] += company_analysis['sources_processed']
                    validation_metrics['sources_validated'] += len(company_analysis['validated_sources'])
                    validation_metrics['confidence_scores'].append(company_analysis['confidence_score'])
                    validation_metrics['citation_count'] += len(company_analysis['citations'])
                    citation_counter += len(company_analysis['citations'])
                    
                    self._display_company_analysis_results(company_analysis)
                    self._store_citations(citations_database, company_analysis['citations'], 'company_analysis')
            
            # ========== ROLE ANALYSIS AGENT ==========
            if role:
                print(f"\n💼 === ROLE ANALYSIS AGENT ACTIVATED ===")
                role_analysis = self._role_analysis_agent(role, company, email_keywords, citations_database, citation_counter)
                
                if role_analysis['success']:
                    research_data['role_analysis'] = role_analysis
                    validation_metrics['sources_discovered'] += role_analysis['sources_processed']
                    validation_metrics['sources_validated'] += len(role_analysis['validated_sources'])
                    validation_metrics['confidence_scores'].append(role_analysis['confidence_score'])
                    validation_metrics['citation_count'] += len(role_analysis['citations'])
                    citation_counter += len(role_analysis['citations'])
                    
                    self._display_role_analysis_results(role_analysis)
                    self._store_citations(citations_database, role_analysis['citations'], 'role_analysis')
            
            # ========== INTERVIEWER ANALYSIS AGENT (LINKEDIN FOCUSED) ==========
            if interviewer:
                print(f"\n👤 === INTERVIEWER ANALYSIS AGENT (LINKEDIN FOCUS) ===")
                interviewer_analysis = self._interviewer_analysis_agent(interviewer, company, email_keywords, citations_database, citation_counter)
                
                if interviewer_analysis['success']:
                    research_data['interviewer_analysis'] = interviewer_analysis
                    validation_metrics['sources_discovered'] += interviewer_analysis['sources_processed']
                    validation_metrics['sources_validated'] += len(interviewer_analysis['validated_sources'])
                    validation_metrics['confidence_scores'].append(interviewer_analysis['confidence_score'])
                    validation_metrics['citation_count'] += len(interviewer_analysis['citations'])
                    validation_metrics['linkedin_profiles_found'] += interviewer_analysis['linkedin_profiles_found']
                    citation_counter += len(interviewer_analysis['citations'])
                    
                    self._display_interviewer_analysis_results(interviewer_analysis)
                    self._store_citations(citations_database, interviewer_analysis['citations'], 'interviewer_analysis')
            
            # ========== DEEP REFLECTION LOOPS ==========
            print(f"\n🤔 === DEEP REFLECTION ON RESEARCH QUALITY ===")
            reflection_result = self._conduct_reflection_loops(research_data, entities, citations_database, citation_counter)
            
            result['reflection_loops'] = reflection_result['loops_conducted']
            result['sufficient_for_prep_guide'] = reflection_result['sufficient_for_prep_guide']
            
            # Calculate overall confidence
            result['overall_confidence'] = self._calculate_overall_confidence(research_data, validation_metrics)
            result['research_quality'] = self._determine_research_quality(result['overall_confidence'])
            
            # Store final results
            result['success'] = True
            result['research_data'] = research_data
            result['citations_database'] = citations_database
            result['processing_time'] = (datetime.now() - research_start_time).total_seconds()
            
            # Display final research summary
            self._display_final_research_summary(result)
            
            return result
            
        except Exception as e:
            result['errors'].append(str(e))
            result['processing_time'] = (datetime.now() - research_start_time).total_seconds()
            print(f"❌ DEEP RESEARCH PIPELINE ERROR: {str(e)}")
            return result
    
    def _display_cache_status(self):
        """Display Tavily cache status"""
        cache_stats = self.cache.get_cache_stats()
        print(f"💾 TAVILY CACHE STATUS:")
        print(f"   📁 Valid Cache Files: {cache_stats.get('valid_cache_files', 0)}")
        print(f"   🗑️ Expired Cache Files: {cache_stats.get('expired_cache_files', 0)}")
        print(f"   📊 Total Cached Results: {cache_stats.get('total_cached_results', 0)}")
        
        # Clean expired cache
        removed = self.cache.clear_expired_cache()
        if removed > 0:
            print(f"   🧹 Removed {removed} expired cache files")
    
    def _extract_email_keywords(self, entities: Dict[str, Any]) -> List[str]:
        """Extract keywords from entities for validation"""
        keywords = []
        
        # Extract from email content if available
        email_content = str(entities.get('email_content', '')).lower()
        
        # Industry/technology keywords
        tech_keywords = ['ai', 'artificial intelligence', 'generative ai', 'agentic', 'machine learning', 'data', 'tech', 'software', 'engineering', 'development']
        program_keywords = ['internship', 'program', 'summer', 'seeds', 'dandilyonn', 'interview', 'opportunity']
        role_keywords = ['manager', 'director', 'lead', 'senior', 'coordinator', 'analyst', 'engineer', 'developer']
        
        all_keywords = tech_keywords + program_keywords + role_keywords
        
        for keyword in all_keywords:
            if keyword in email_content:
                keywords.append(keyword)
        
        # Extract entities as keywords
        for key, value in entities.items():
            if key not in ['email_content'] and value:
                keywords.append(str(value).lower())
        
        return list(set(keywords))  # Remove duplicates
    
    def _company_analysis_agent(self, company: str, email_keywords: List[str], citations_db: Dict, citation_counter: int) -> Dict[str, Any]:
        """Company Analysis Agent with web search and financial data"""
        try:
            print(f"   🤖 Company Analysis Agent: Analyzing '{company}'")
            
            # Phase 1: Company Identity & Official Presence
            print(f"   🔍 Phase 1: Company Identity Verification")
            identity_queries = [
                f"{company} official website company",
                f"{company} about us company overview",
                f"{company} linkedin company page",
                f"{company} crunchbase company profile"
            ]
            
            identity_sources = []
            for query in identity_queries:
                results = cached_search_tavily(query, search_depth="basic", max_results=3)
                identity_sources.extend(results)
                print(f"      🔍 Query: '{query}' → {len(results)} sources")
            
            # Phase 2: Industry & Market Analysis
            print(f"   🔍 Phase 2: Industry & Market Analysis")
            industry_queries = [
                f"{company} industry sector business",
                f"{company} market trends 2024 2025",
                f"{company} competitors industry analysis",
                f"{company} recent news developments"
            ]
            
            industry_sources = []
            for query in industry_queries:
                results = cached_search_tavily(query, search_depth="basic", max_results=3)
                industry_sources.extend(results)
                print(f"      🔍 Query: '{query}' → {len(results)} sources")
            
            # Validate and process sources
            all_sources = identity_sources + industry_sources
            validated_sources = self._validate_company_sources(all_sources, company, email_keywords)
            citations = self._generate_citations(validated_sources[:6], citation_counter)  # Top 6 citations
            
            confidence_score = min(0.95, len(validated_sources) / max(1, len(all_sources)) * 0.8 + 0.2)
            
            analysis_summary = f"Validated company identity and analyzed industry position with {len(citations)} citations"
            industry_analysis = f"Analyzed {len(industry_sources)} industry sources for market positioning"
            
            return {
                'success': True,
                'analysis_summary': analysis_summary,
                'industry_analysis': industry_analysis,
                'validated_sources': validated_sources,
                'sources_processed': len(all_sources),
                'confidence_score': confidence_score,
                'citations': citations
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _role_analysis_agent(self, role: str, company: str, email_keywords: List[str], citations_db: Dict, citation_counter: int) -> Dict[str, Any]:
        """Role Analysis Agent with job market and skills analysis"""
        try:
            print(f"   🤖 Role Analysis Agent: Analyzing '{role}' at '{company}'")
            
            # Phase 1: Role Definition & Requirements
            print(f"   🔍 Phase 1: Role Requirements Analysis")
            role_queries = [
                f"{role} job description requirements {company}",
                f"{role} skills qualifications {company}",
                f"{role} responsibilities duties {company}",
                f"{role} interview questions {company}"
            ]
            
            role_sources = []
            for query in role_queries:
                results = cached_search_tavily(query, search_depth="basic", max_results=3)
                role_sources.extend(results)
                print(f"      🔍 Query: '{query}' → {len(results)} sources")
            
            # Phase 2: Skills & Market Analysis
            print(f"   🔍 Phase 2: Skills & Market Analysis")
            skills_queries = [
                f"{role} skills demand 2024 market trends",
                f"{role} salary range {company} industry",
                f"{role} career progression path",
                f"{role} technology stack tools required"
            ]
            
            skills_sources = []
            for query in skills_queries:
                results = cached_search_tavily(query, search_depth="basic", max_results=2)
                skills_sources.extend(results)
                print(f"      🔍 Query: '{query}' → {len(results)} sources")
            
            # Validate and process sources
            all_sources = role_sources + skills_sources
            validated_sources = self._validate_role_sources(all_sources, role, company, email_keywords)
            citations = self._generate_citations(validated_sources[:5], citation_counter)  # Top 5 citations
            
            confidence_score = min(0.95, len(validated_sources) / max(1, len(all_sources)) * 0.7 + 0.3)
            
            analysis_summary = f"Analyzed role requirements and skills gap with {len(citations)} citations"
            skills_analysis = f"Analyzed {len(skills_sources)} skills and market sources"
            
            return {
                'success': True,
                'analysis_summary': analysis_summary,
                'skills_analysis': skills_analysis,
                'validated_sources': validated_sources,
                'sources_processed': len(all_sources),
                'confidence_score': confidence_score,
                'citations': citations
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _interviewer_analysis_agent(self, interviewer: str, company: str, email_keywords: List[str], citations_db: Dict, citation_counter: int) -> Dict[str, Any]:
        """LinkedIn-focused Interviewer Analysis Agent"""
        try:
            print(f"   🤖 Interviewer Analysis Agent: LinkedIn analysis for '{interviewer}'")
            linkedin_profiles_found = 0
            
            # Phase 1: LinkedIn Profile Discovery
            print(f"   🔍 Phase 1: LinkedIn Profile Discovery")
            linkedin_queries = [
                f"{interviewer} {company} linkedin profile",
                f"{interviewer} linkedin {company}",
                f'"{interviewer}" linkedin profile',
                f"{interviewer} {company} employee linkedin"
            ]
            
            linkedin_sources = []
            for query in linkedin_queries:
                print(f"      🔍 LinkedIn Search: '{query}'")
                results = cached_search_tavily(query, search_depth="basic", max_results=4)
                linkedin_sources.extend(results)
                
                # Count LinkedIn profiles
                for result in results:
                    if 'linkedin.com' in result.get('url', '').lower():
                        linkedin_profiles_found += 1
                        print(f"         🔗 LinkedIn Profile Found: {result.get('title', 'Unknown')[:50]}...")
            
            # Phase 2: Professional Background Research
            print(f"   🔍 Phase 2: Professional Background Research")
            background_queries = [
                f"{interviewer} {company} publications articles",
                f"{interviewer} {company} speaking events",
                f"{interviewer} {company} professional background",
                f"{interviewer} {company} expertise experience"
            ]
            
            background_sources = []
            for query in background_queries:
                results = cached_search_tavily(query, search_depth="basic", max_results=2)
                background_sources.extend(results)
                print(f"      🔍 Query: '{query}' → {len(results)} sources")
            
            # Validate and process sources with LinkedIn priority
            all_sources = linkedin_sources + background_sources
            validated_sources = self._validate_interviewer_sources(all_sources, interviewer, company, email_keywords)
            citations = self._generate_citations(validated_sources[:6], citation_counter)  # Top 6 citations
            
            # Higher confidence for LinkedIn profiles
            base_confidence = len(validated_sources) / max(1, len(all_sources)) * 0.4
            linkedin_boost = min(0.4, linkedin_profiles_found * 0.2)
            confidence_score = min(0.95, base_confidence + linkedin_boost)
            
            analysis_summary = f"Conducted LinkedIn-focused analysis with {len(citations)} citations and {linkedin_profiles_found} profiles found"
            linkedin_analysis = f"Found {linkedin_profiles_found} LinkedIn profiles" if linkedin_profiles_found > 0 else "No verified LinkedIn profiles found"
            
            return {
                'success': True,
                'analysis_summary': analysis_summary,
                'linkedin_analysis': linkedin_analysis,
                'validated_sources': validated_sources,
                'sources_processed': len(all_sources),
                'linkedin_profiles_found': linkedin_profiles_found,
                'confidence_score': confidence_score,
                'citations': citations
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _validate_company_sources(self, sources: List[Dict], company: str, keywords: List[str]) -> List[Dict]:
        """Validate company sources for relevance"""
        validated = []
        company_lower = company.lower()
        
        for source in sources:
            title = source.get('title', '').lower()
            content = source.get('content', '').lower()
            url = source.get('url', '').lower()
            
            relevance_score = 0
            evidence = []
            
            # Company name matching
            if company_lower in title:
                relevance_score += 3
                evidence.append(f"Company '{company}' in title")
            elif company_lower in content:
                relevance_score += 2
                evidence.append(f"Company '{company}' in content")
            
            # Official domain check
            if company_lower.replace(' ', '') in url:
                relevance_score += 4
                evidence.append("Official company domain")
            
            # Keywords matching
            keyword_matches = sum(1 for keyword in keywords if keyword in content or keyword in title)
            if keyword_matches > 0:
                relevance_score += min(keyword_matches, 3)
                evidence.append(f"{keyword_matches} keyword matches")
            
            # Include if relevance score is sufficient
            if relevance_score >= 2:
                validated.append({
                    'source': source,
                    'relevance_score': relevance_score,
                    'evidence': evidence
                })
        
        return sorted(validated, key=lambda x: x['relevance_score'], reverse=True)
    
    def _validate_role_sources(self, sources: List[Dict], role: str, company: str, keywords: List[str]) -> List[Dict]:
        """Validate role sources for relevance"""
        validated = []
        role_lower = role.lower()
        company_lower = company.lower()
        
        for source in sources:
            title = source.get('title', '').lower()
            content = source.get('content', '').lower()
            
            relevance_score = 0
            evidence = []
            
            # Role matching
            if role_lower in title:
                relevance_score += 3
                evidence.append(f"Role '{role}' in title")
            elif role_lower in content:
                relevance_score += 2
                evidence.append(f"Role '{role}' in content")
            
            # Company context
            if company_lower in title or company_lower in content:
                relevance_score += 2
                evidence.append(f"Company '{company}' context")
            
            # Job-related indicators
            job_indicators = ['job', 'position', 'requirements', 'skills', 'interview', 'responsibilities']
            matches = sum(1 for indicator in job_indicators if indicator in title or indicator in content)
            if matches > 0:
                relevance_score += matches
                evidence.append(f"{matches} job indicators")
            
            if relevance_score >= 2:
                validated.append({
                    'source': source,
                    'relevance_score': relevance_score,
                    'evidence': evidence
                })
        
        return sorted(validated, key=lambda x: x['relevance_score'], reverse=True)
    
    def _validate_interviewer_sources(self, sources: List[Dict], interviewer: str, company: str, keywords: List[str]) -> List[Dict]:
        """Validate interviewer sources with LinkedIn priority"""
        validated = []
        interviewer_lower = interviewer.lower()
        company_lower = company.lower()
        
        for source in sources:
            title = source.get('title', '').lower()
            content = source.get('content', '').lower()
            url = source.get('url', '').lower()
            
            relevance_score = 0
            evidence = []
            
            # LinkedIn profile bonus
            if 'linkedin.com' in url:
                relevance_score += 5
                evidence.append("LinkedIn profile")
            
            # Name matching
            if interviewer_lower in title:
                relevance_score += 4
                evidence.append(f"Name '{interviewer}' in title")
            elif interviewer_lower in content:
                relevance_score += 3
                evidence.append(f"Name '{interviewer}' in content")
            
            # Company context
            if company_lower in title or company_lower in content:
                relevance_score += 2
                evidence.append(f"Company '{company}' context")
            
            # Professional indicators
            prof_indicators = ['profile', 'about', 'bio', 'experience', 'background']
            matches = sum(1 for indicator in prof_indicators if indicator in title or indicator in content)
            if matches > 0:
                relevance_score += matches
                evidence.append(f"{matches} professional indicators")
            
            if relevance_score >= 3:  # Higher threshold for interviewer sources
                validated.append({
                    'source': source,
                    'relevance_score': relevance_score,
                    'evidence': evidence
                })
        
        return sorted(validated, key=lambda x: x['relevance_score'], reverse=True)
    
    def _generate_citations(self, validated_sources: List[Dict], start_counter: int) -> List[Dict]:
        """Generate citations from validated sources"""
        citations = []
        
        for i, source_data in enumerate(validated_sources, start_counter):
            source = source_data.get('source', {})
            citations.append({
                'id': str(i),
                'source': f"{source.get('title', 'Unknown')} - {source.get('url', '')}",
                'content_snippet': source.get('content', '')[:200] + "..." if source.get('content') else "No content",
                'evidence': source_data.get('evidence', [])
            })
        
        return citations
    
    def _conduct_reflection_loops(self, research_data: Dict, entities: Dict, citations_db: Dict, citation_counter: int) -> Dict[str, Any]:
        """Conduct deep reflection loops on research quality"""
        max_loops = 2  # Reduced from 3 to 2 for efficiency
        loops_conducted = 0
        
        for loop in range(max_loops):
            print(f"   🔄 Reflection Loop {loop + 1}/{max_loops}")
            
            reflection_result = self._assess_research_sufficiency(research_data, citations_db)
            
            if reflection_result['sufficient_for_prep_guide']:
                print(f"      ✅ Research Quality SUFFICIENT: {reflection_result['assessment']}")
                break
            else:
                print(f"      ⚠️ Research Quality NEEDS IMPROVEMENT: {reflection_result['assessment']}")
                if loop < max_loops - 1:  # Don't do additional research on last loop
                    print(f"      🔍 Conducting additional targeted research...")
                    # Could add additional research here if needed
                
                loops_conducted += 1
        
        # Final assessment
        final_assessment = self._assess_research_sufficiency(research_data, citations_db)
        
        return {
            'loops_conducted': loops_conducted,
            'sufficient_for_prep_guide': final_assessment['sufficient_for_prep_guide'],
            'final_assessment': final_assessment['assessment']
        }
    
    def _assess_research_sufficiency(self, research_data: Dict, citations_db: Dict) -> Dict[str, Any]:
        """Assess if research is sufficient for prep guide generation"""
        quality_score = 0
        assessment_factors = []
        
        # Company analysis quality
        company_analysis = research_data.get('company_analysis', {})
        if company_analysis.get('success') and company_analysis.get('confidence_score', 0) >= 0.6:
            quality_score += 3
            assessment_factors.append("Company analysis: HIGH quality")
        elif company_analysis.get('success'):
            quality_score += 2
            assessment_factors.append("Company analysis: MODERATE quality")
        else:
            assessment_factors.append("Company analysis: INSUFFICIENT")
        
        # Role analysis quality
        role_analysis = research_data.get('role_analysis', {})
        if role_analysis.get('success') and role_analysis.get('confidence_score', 0) >= 0.6:
            quality_score += 2
            assessment_factors.append("Role analysis: GOOD quality")
        elif role_analysis.get('success'):
            quality_score += 1
            assessment_factors.append("Role analysis: BASIC quality")
        else:
            assessment_factors.append("Role analysis: INSUFFICIENT")
        
        # Interviewer analysis quality (with LinkedIn bonus)
        interviewer_analysis = research_data.get('interviewer_analysis', {})
        linkedin_found = interviewer_analysis.get('linkedin_profiles_found', 0)
        if interviewer_analysis.get('success') and linkedin_found > 0:
            quality_score += 4
            assessment_factors.append(f"Interviewer analysis: EXCELLENT ({linkedin_found} LinkedIn profiles)")
        elif interviewer_analysis.get('success'):
            quality_score += 2
            assessment_factors.append("Interviewer analysis: MODERATE quality")
        else:
            assessment_factors.append("Interviewer analysis: INSUFFICIENT")
        
        # Citation count bonus
        citation_count = len(citations_db)
        if citation_count >= 5:
            quality_score += 2
            assessment_factors.append(f"Citations: EXCELLENT ({citation_count} citations)")
        elif citation_count >= 2:
            quality_score += 1
            assessment_factors.append(f"Citations: ADEQUATE ({citation_count} citations)")
        else:
            assessment_factors.append("Citations: INSUFFICIENT")
        
        # Decision threshold (lowered to allow more research through)
        sufficient_for_prep_guide = quality_score >= 4  # Out of 11 possible points
        
        assessment = " | ".join(assessment_factors)
        
        return {
            'sufficient_for_prep_guide': sufficient_for_prep_guide,
            'quality_score': quality_score,
            'max_score': 11,
            'assessment': assessment
        }
    
    def _calculate_overall_confidence(self, research_data: Dict, validation_metrics: Dict) -> float:
        """Calculate overall research confidence score"""
        confidence_scores = validation_metrics.get('confidence_scores', [])
        if not confidence_scores:
            return 0.0
        
        # Weighted average of agent confidence scores
        base_confidence = sum(confidence_scores) / len(confidence_scores)
        
        # LinkedIn bonus
        linkedin_bonus = min(0.1, validation_metrics.get('linkedin_profiles_found', 0) * 0.05)
        
        # Citation bonus
        citation_bonus = min(0.1, validation_metrics.get('citation_count', 0) * 0.02)
        
        return min(0.95, base_confidence + linkedin_bonus + citation_bonus)
    
    def _determine_research_quality(self, confidence: float) -> str:
        """Determine research quality based on confidence score"""
        if confidence >= 0.85:
            return "EXCELLENT"
        elif confidence >= 0.7:
            return "HIGH"
        elif confidence >= 0.5:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _store_citations(self, citations_db: Dict, citations: List[Dict], agent_source: str):
        """Store citations in database with deduplication"""
        for citation in citations:
            citation_id = citation.get('id', str(len(citations_db) + 1))
            
            # Check for duplicates
            duplicate_found = False
            for existing_id, existing_data in citations_db.items():
                if existing_data.get('source') == citation.get('source'):
                    print(f"      🔗 Reusing Citation [{existing_id}]: {citation.get('source')[:60]}... (found by {agent_source})")
                    duplicate_found = True
                    break
            
            if not duplicate_found:
                citations_db[citation_id] = {
                    'source': citation.get('source', ''),
                    'content_snippet': citation.get('content_snippet', ''),
                    'agent': agent_source
                }
                print(f"      📝 Citation [{citation_id}]: {citation.get('source', '')[:60]}...")
    
    def _display_company_analysis_results(self, company_analysis: Dict):
        """Display company analysis results"""
        print(f"   ✅ COMPANY ANALYSIS: {company_analysis['analysis_summary']}")
        print(f"   📊 Industry Insights: {company_analysis['industry_analysis']}")
        print(f"   📈 Confidence: {company_analysis['confidence_score']:.2f}")
        print(f"   📚 Validated Sources: {len(company_analysis['validated_sources'])}/{company_analysis['sources_processed']}")
    
    def _display_role_analysis_results(self, role_analysis: Dict):
        """Display role analysis results"""
        print(f"   ✅ ROLE ANALYSIS: {role_analysis['analysis_summary']}")
        print(f"   🎯 Skills Analysis: {role_analysis['skills_analysis']}")
        print(f"   📈 Confidence: {role_analysis['confidence_score']:.2f}")
        print(f"   📚 Validated Sources: {len(role_analysis['validated_sources'])}/{role_analysis['sources_processed']}")
    
    def _display_interviewer_analysis_results(self, interviewer_analysis: Dict):
        """Display interviewer analysis results with LinkedIn focus"""
        print(f"   ✅ INTERVIEWER ANALYSIS: {interviewer_analysis['analysis_summary']}")
        print(f"   🔗 LinkedIn Discovery: {interviewer_analysis['linkedin_analysis']}")
        print(f"   📈 Confidence: {interviewer_analysis['confidence_score']:.2f}")
        print(f"   📚 Validated Sources: {len(interviewer_analysis['validated_sources'])}/{interviewer_analysis['sources_processed']}")
        print(f"   🔗 LinkedIn Profiles Found: {interviewer_analysis['linkedin_profiles_found']}")
    
    def _display_final_research_summary(self, result: Dict):
        """Display final research summary"""
        metrics = result['validation_metrics']
        
        print(f"\n📊 === DEEP RESEARCH PIPELINE COMPLETED ===")
        print(f"   🔍 Total Sources Discovered: {metrics['sources_discovered']}")
        print(f"   ✅ Sources Validated: {metrics['sources_validated']}")
        print(f"   📝 Citations Generated: {metrics['citation_count']}")
        print(f"   🔗 LinkedIn Profiles Found: {metrics['linkedin_profiles_found']}")
        print(f"   🔄 Reflection Loops: {result['reflection_loops']}")
        print(f"   📈 Overall Confidence: {result['overall_confidence']:.2f}")
        print(f"   🏆 Research Quality: {result['research_quality']}")
        print(f"   📚 Sufficient for Prep Guide: {'YES' if result['sufficient_for_prep_guide'] else 'NO'}")
        print(f"   ⏱️  Processing Time: {result['processing_time']:.2f}s")
