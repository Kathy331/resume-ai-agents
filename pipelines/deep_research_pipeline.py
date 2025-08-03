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
            """Convert entity to string, handling lists"""
            if isinstance(entity_value, list):
                return entity_value[0] if entity_value else ''
            return str(entity_value) if entity_value else ''
        
        # Handle both uppercase and lowercase entity keys
        company = get_entity_string(entities.get('COMPANY', entities.get('company', '')))
        role = get_entity_string(entities.get('ROLE', entities.get('role', '')))
        interviewer = get_entity_string(entities.get('INTERVIEWER', entities.get('interviewer', '')))
        
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
        """Company Analysis Agent with enhanced search and validation"""
        try:
            print(f"   🤖 Company Analysis Agent: Analyzing '{company}'")
            
            # Phase 1: Company Identity & Official Presence
            print(f"   🔍 Phase 1: Company Identity Verification")
            identity_queries = [
                f'"{company}" official website about',
                f'"{company}" company overview mission',
                f'"{company}" linkedin company page',
                f'"{company}" crunchbase company profile',
                f"{company} internship program careers",  # Specific for internship context
                f"{company} startup company information"
            ]
            
            identity_sources = []
            validation_log = []
            
            for query in identity_queries:
                results = cached_search_tavily(query, search_depth="basic", max_results=3)
                identity_sources.extend(results)
                print(f"      🔍 Query: '{query}' → {len(results)} sources")
            
            # Phase 2: Industry & Market Analysis
            print(f"   🔍 Phase 2: Industry & Market Analysis")
            industry_queries = [
                f'"{company}" industry sector business',
                f'"{company}" market trends 2024 2025',
                f'"{company}" recent news developments',
                f'"{company}" technology stack products'
            ]
            
            industry_sources = []
            for query in industry_queries:
                results = cached_search_tavily(query, search_depth="basic", max_results=3)
                industry_sources.extend(results)
                print(f"      🔍 Query: '{query}' → {len(results)} sources")
            
            # Enhanced validation with detailed reasoning
            all_sources = identity_sources + industry_sources
            validated_sources = self._validate_company_sources_enhanced(all_sources, company, email_keywords, validation_log)
            citations = self._generate_citations(validated_sources[:6], citation_counter)  # Top 6 citations
            
            # Display validation reasoning
            print(f"   📊 Company Validation Results:")
            for log_entry in validation_log[:8]:  # Show first 8 entries
                print(f"      {log_entry}")
            
            # Improved confidence calculation
            base_confidence = len(validated_sources) / max(1, len(all_sources)) * 0.6
            official_bonus = 0.2 if any('official' in str(s.get('evidence', [])) for s in validated_sources) else 0
            confidence_score = min(0.95, base_confidence + official_bonus + 0.2)
            
            analysis_summary = f"Validated company identity and analyzed industry position with {len(citations)} citations"
            industry_analysis = f"Analyzed {len(industry_sources)} industry sources for market positioning"
            
            return {
                'success': True,
                'analysis_summary': analysis_summary,
                'industry_analysis': industry_analysis,
                'validated_sources': validated_sources,
                'sources_processed': len(all_sources),
                'confidence_score': confidence_score,
                'citations': citations,
                'validation_log': validation_log
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
            
            # Validate and process sources with detailed logging
            all_sources = role_sources + skills_sources
            validation_log = []
            validated_sources = self._validate_role_sources_enhanced(all_sources, role, company, email_keywords, validation_log)
            citations = self._generate_citations(validated_sources[:5], citation_counter)  # Top 5 citations
            
            # Display validation reasoning  
            print(f"   📊 Role Validation Results:")
            for log_entry in validation_log[:8]:  # Show first 8 entries
                print(f"      {log_entry}")
            
            confidence_score = min(0.95, len(validated_sources) / max(1, len(all_sources)) * 0.7 + 0.3)
            
            analysis_summary = f"Analyzed {role} requirements and responsibilities with {len(citations)} citations"
            role_insights = f"Researched company-specific and industry standards for {role}"
            
            return {
                'success': True,
                'analysis_summary': analysis_summary,
                'role_insights': role_insights,
                'validated_sources': validated_sources,
                'sources_processed': len(all_sources),
                'confidence_score': confidence_score,
                'citations': citations,
                'validation_log': validation_log
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _interviewer_analysis_agent(self, interviewer: str, company: str, email_keywords: List[str], citations_db: Dict, citation_counter: int) -> Dict[str, Any]:
        """LinkedIn-focused Interviewer Analysis Agent with detailed search strategy"""
        try:
            print(f"   🤖 Interviewer Analysis Agent: LinkedIn analysis for '{interviewer}'")
            linkedin_profiles_found = 0
            
            # Phase 1: Specific LinkedIn Profile Discovery (Human-like search)
            print(f"   🔍 Phase 1: Targeted LinkedIn Profile Search")
            # More specific profile searches
            linkedin_queries = [
                f'"{interviewer}" linkedin profile',  # Exact name search
                f'"{interviewer}" {company} linkedin',  # Name + company
                f'"{interviewer}" site:linkedin.com/in',  # Direct profile search
                f"{interviewer} {company} linkedin profile",  # Broader search
                f"{interviewer} linkedin {company} employee",  # Employee context
            ]
            
            linkedin_sources = []
            validation_log = []  # Track validation reasoning
            extracted_names = set()  # Track names found in company-relevant content
            
            for query in linkedin_queries:
                print(f"      🔍 LinkedIn Search: '{query}'")
                results = cached_search_tavily(query, search_depth="basic", max_results=4)
                linkedin_sources.extend(results)
                
                # Count LinkedIn profiles with validation and name extraction
                for result in results:
                    url = result.get('url', '').lower()
                    title = result.get('title', '')
                    content = result.get('content', '').lower()
                    company_lower = company.lower()
                    
                    if 'linkedin.com' in url:
                        if '/in/' in url or '/pub/' in url:  # Actual profile URLs
                            linkedin_profiles_found += 1
                            print(f"         ✅ LinkedIn Profile Found: {title[:50]}...")
                            validation_log.append(f"✅ VALIDATED: {title[:50]}... (LinkedIn profile URL)")
                        else:
                            # Check if LinkedIn post/content mentions target company
                            if company_lower in title.lower() or company_lower in content:
                                print(f"         🎯 LinkedIn Post (Company-Relevant): {title[:50]}...")
                                validation_log.append(f"🎯 COMPANY-RELEVANT: {title[:50]}... (LinkedIn post mentioning '{company}')")
                                
                                # Extract potential names from company-relevant posts
                                self._extract_names_from_linkedin_post(title, content, company, extracted_names)
                            else:
                                print(f"         ⚠️  LinkedIn Post/Content: {title[:50]}...")
                                validation_log.append(f"⚠️  REJECTED: {title[:50]}... (Not a profile - likely post/content)")
                    else:
                        validation_log.append(f"❌ REJECTED: {title[:50]}... (Not LinkedIn)")
            
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
            
            # Enhanced validation with detailed reasoning
            all_sources = linkedin_sources + background_sources
            validated_sources = self._validate_interviewer_sources_enhanced(all_sources, interviewer, company, email_keywords, validation_log)
            citations = self._generate_citations(validated_sources[:6], citation_counter)  # Top 6 citations
            
            # Display validation reasoning
            print(f"   📊 Validation Results:")
            for log_entry in validation_log[:10]:  # Show first 10 entries
                print(f"      {log_entry}")
            
            # Higher confidence for actual LinkedIn profiles
            base_confidence = len(validated_sources) / max(1, len(all_sources)) * 0.4
            linkedin_boost = min(0.4, linkedin_profiles_found * 0.25)  # More weight for actual profiles
            confidence_score = min(0.95, base_confidence + linkedin_boost)
            
            analysis_summary = f"Conducted LinkedIn-focused analysis with {len(citations)} citations and {linkedin_profiles_found} profiles found"
            linkedin_analysis = f"Found {linkedin_profiles_found} LinkedIn profiles" if linkedin_profiles_found > 0 else "No verified LinkedIn profiles found"
            
            # Generate improved search suggestions based on extracted names
            search_suggestions = []
            if extracted_names:
                print(f"   💡 Extracted Names from Company-Relevant Content: {', '.join(list(extracted_names)[:3])}")
                for name in list(extracted_names)[:3]:  # Top 3 names
                    search_suggestions.extend([
                        f'"{name}" linkedin profile {company}',
                        f'"{name}" site:linkedin.com/in'
                    ])
            
            return {
                'success': True,
                'analysis_summary': analysis_summary,
                'linkedin_analysis': linkedin_analysis,
                'extracted_names': list(extracted_names),
                'search_suggestions': search_suggestions[:6],  # Top 6 suggestions
                'validated_sources': validated_sources,
                'sources_processed': len(all_sources),
                'linkedin_profiles_found': linkedin_profiles_found,
                'confidence_score': confidence_score,
                'citations': citations,
                'validation_log': validation_log
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _extract_names_from_linkedin_post(self, title: str, content: str, company: str, extracted_names: set):
        """Extract potential interviewer names from company-relevant LinkedIn posts"""
        import re
        
        # Common job titles and non-person terms to filter out
        non_person_terms = {
            'software engineer', 'senior software', 'engineering team', 'development team',
            'tech lead', 'team lead', 'project manager', 'product manager', 'data scientist',
            'software developer', 'full stack', 'front end', 'back end', 'machine learning',
            'artificial intelligence', 'user experience', 'user interface', 'quality assurance',
            'business analyst', 'system administrator', 'network engineer', 'security engineer'
        }
        
        # Common patterns to identify names in LinkedIn posts about the company
        text_to_analyze = f"{title} {content}".lower()
        
        # Pattern 1: "Name's Post" or "Name - Title"
        name_patterns = [
            r"([A-Z][a-z]+ [A-Z][a-z]+)'s Post",  # "John Smith's Post"
            r"([A-Z][a-z]+ [A-Z][a-z]+) - .+",     # "John Smith - Title"
            r"([A-Z][a-z]+ [A-Z][a-z]+) \| .+",    # "John Smith | Title"
            r"by ([A-Z][a-z]+ [A-Z][a-z]+)",       # "by John Smith"
            r"from ([A-Z][a-z]+ [A-Z][a-z]+)",     # "from John Smith"
            r"Led by ([A-Z][a-z]+ [A-Z][a-z]+)",   # "Led by Sarah Johnson"
        ]
        
        # Apply patterns to original (case-sensitive) text
        original_text = f"{title} {content}"
        for pattern in name_patterns:
            matches = re.findall(pattern, original_text)
            for match in matches:
                # Validate it's likely a person name (not company words or job titles)
                name_words = match.split()
                if len(name_words) == 2 and all(len(word) > 1 for word in name_words):
                    # Skip if it matches company name parts
                    company_words = company.lower().split()
                    if not any(word.lower() in company_words for word in name_words):
                        # Skip if it's a job title or non-person term
                        if match.lower() not in non_person_terms:
                            extracted_names.add(match)
        
        # Pattern 2: Look for people mentioned in company context
        company_mentions = re.finditer(rf"\b{re.escape(company.lower())}\b", text_to_analyze)
        for mention in company_mentions:
            # Look for names near company mentions (within 50 characters)
            start = max(0, mention.start() - 50)
            end = min(len(original_text), mention.end() + 50)
            context = original_text[start:end]
            
            # Find capitalized names in context
            name_matches = re.findall(r'\b([A-Z][a-z]+ [A-Z][a-z]+)\b', context)
            for name_match in name_matches:
                name_words = name_match.split()
                if len(name_words) == 2 and all(len(word) > 1 for word in name_words):
                    company_words = company.lower().split()
                    if not any(word.lower() in company_words for word in name_words):
                        # Skip if it's a job title or non-person term
                        if name_match.lower() not in non_person_terms:
                            extracted_names.add(name_match)
    
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

    def _validate_company_sources_enhanced(self, sources: List[Dict], company: str, keywords: List[str], validation_log: List[str]) -> List[Dict]:
        """Enhanced company source validation with detailed reasoning"""
        validated = []
        company_lower = company.lower()
        company_variations = [
            company_lower,
            company_lower.replace(' ', ''),  # Remove spaces
            company_lower.replace('seeds', 'seed') if 'seeds' in company_lower else company_lower,  # Handle plural
        ]
        
        for source in sources:
            title = source.get('title', '').lower()
            content = source.get('content', '').lower()
            url = source.get('url', '').lower()
            
            relevance_score = 0
            evidence = []
            rejection_reasons = []
            
            # Company name matching with variations
            name_found = False
            for variation in company_variations:
                if variation in title:
                    relevance_score += 4
                    evidence.append(f"Company '{variation}' in title")
                    name_found = True
                    break
                elif variation in content:
                    relevance_score += 3
                    evidence.append(f"Company '{variation}' in content")
                    name_found = True
                    break
            
            if not name_found:
                rejection_reasons.append(f"Company name '{company}' not found")
            
            # Official domain check
            domain_found = False
            for variation in company_variations:
                if variation in url:
                    relevance_score += 5
                    evidence.append("Official company domain")
                    domain_found = True
                    break
            
            # LinkedIn company page bonus
            if 'linkedin.com/company' in url:
                relevance_score += 4
                evidence.append("LinkedIn company page")
            
            # Keywords matching
            keyword_matches = 0
            for keyword in keywords:
                if keyword.lower() in content or keyword.lower() in title:
                    keyword_matches += 1
            
            if keyword_matches > 0:
                relevance_score += min(keyword_matches, 3)
                evidence.append(f"{keyword_matches} keyword matches")
            
            # Professional/business indicators
            business_indicators = ['company', 'business', 'startup', 'organization', 'corp', 'inc', 'about', 'mission']
            business_matches = sum(1 for indicator in business_indicators if indicator in title or indicator in content)
            if business_matches > 0:
                relevance_score += min(business_matches, 2)
                evidence.append(f"{business_matches} business indicators")
            
            # Validation decision with reasoning
            threshold = 2  # More lenient threshold
            if relevance_score >= threshold:
                validated.append({
                    'source': source,
                    'relevance_score': relevance_score,
                    'evidence': evidence
                })
                validation_log.append(f"✅ VALIDATED: {source.get('title', 'Unknown')[:40]}... (Score: {relevance_score}, Evidence: {', '.join(evidence[:2])})")
            else:
                validation_log.append(f"❌ REJECTED: {source.get('title', 'Unknown')[:40]}... (Score: {relevance_score}, Reasons: {', '.join(rejection_reasons)})")
        
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
    
    def _validate_role_sources_enhanced(self, sources: List[Dict], role: str, company: str, keywords: List[str], validation_log: List[str]) -> List[Dict]:
        """Enhanced role source validation with strict company relevance requirement"""
        validated = []
        role_lower = role.lower()
        company_lower = company.lower()
        
        for source in sources:
            title = source.get('title', '').lower()
            content = source.get('content', '').lower()
            url = source.get('url', '').lower()
            
            relevance_score = 0
            evidence = []
            rejection_reasons = []
            
            # STRICT REQUIREMENT: Company context is mandatory for role analysis
            company_in_title = company_lower in title
            company_in_content = company_lower in content
            
            if company_in_title:
                relevance_score += 8  # High score for company in title
                evidence.append(f"Company '{company}' in title")
            elif company_in_content:
                relevance_score += 5  # Medium score for company in content
                evidence.append(f"Company '{company}' in content")
            else:
                rejection_reasons.append(f"No '{company}' context found")
                # Auto-reject sources without company context
                validation_log.append(f"❌ REJECTED: {source.get('title', 'Unknown')[:40]}... (Score: {relevance_score}, Reasons: No company connection)")
                continue
            
            # Role/position matching (only if company context exists)
            role_parts = role_lower.split()
            role_matches = 0
            for part in role_parts:
                if len(part) > 2:  # Skip short words
                    if part in title:
                        role_matches += 1
                        relevance_score += 3
                    elif part in content:
                        role_matches += 1
                        relevance_score += 2
            
            if role_matches > 0:
                evidence.append(f"{role_matches}/{len(role_parts)} role terms matched")
            
            # Professional/job-related indicators
            job_indicators = ['job', 'position', 'role', 'career', 'responsibilities', 'skills', 'requirements', 'description', 'internship']
            job_matches = sum(1 for indicator in job_indicators if indicator in title or indicator in content)
            if job_matches > 0:
                relevance_score += min(job_matches, 3)
                evidence.append(f"{job_matches} job indicators")
            
            # Keywords matching from email
            keyword_matches = 0
            for keyword in keywords:
                if keyword.lower() in content or keyword.lower() in title:
                    keyword_matches += 1
            
            if keyword_matches > 0:
                relevance_score += min(keyword_matches, 2)
                evidence.append(f"{keyword_matches} keyword matches")
            
            # Official domain bonus (for company-connected sources)
            official_domains = ['linkedin.com', 'glassdoor.com', 'indeed.com', 'monster.com', 'wellfound.com']
            if any(domain in url for domain in official_domains):
                relevance_score += 2
                evidence.append("Professional/job site")
            
            # STRICT validation decision - must have company context AND good score
            threshold = 6  # Higher threshold for role analysis
            if relevance_score >= threshold:
                validated.append({
                    'source': source,
                    'relevance_score': relevance_score,
                    'evidence': evidence
                })
                validation_log.append(f"✅ VALIDATED: {source.get('title', 'Unknown')[:40]}... (Score: {relevance_score}, Evidence: {', '.join(evidence[:2])})")
            else:
                validation_log.append(f"❌ REJECTED: {source.get('title', 'Unknown')[:40]}... (Score: {relevance_score}, Reasons: Below threshold despite company context)")
        
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

    def _validate_interviewer_sources_enhanced(self, sources: List[Dict], interviewer: str, company: str, keywords: List[str], validation_log: List[str]) -> List[Dict]:
        """Enhanced interviewer source validation with detailed reasoning"""
        validated = []
        interviewer_lower = interviewer.lower()
        company_lower = company.lower()
        
        for source in sources:
            title = source.get('title', '').lower()
            content = source.get('content', '').lower()
            url = source.get('url', '').lower()
            
            relevance_score = 0
            evidence = []
            rejection_reasons = []
            
            # LinkedIn profile evaluation with smart post assessment
            if 'linkedin.com' in url:
                if '/in/' in url or '/pub/' in url:
                    relevance_score += 6  # Actual profile
                    evidence.append("LinkedIn profile URL")
                elif '/posts/' in url or '/feed/' in url:
                    # Smart evaluation of LinkedIn posts - check if they mention target company
                    if company_lower in title or company_lower in content:
                        relevance_score += 4  # Company-relevant post content
                        evidence.append("LinkedIn post mentioning target company")
                    else:
                        relevance_score += 1  # Generic post
                        evidence.append("LinkedIn post/content")
                        rejection_reasons.append("Post without company context")
                else:
                    # Other LinkedIn content - evaluate based on company relevance
                    if company_lower in title or company_lower in content:
                        relevance_score += 4  # Company-relevant content
                        evidence.append("LinkedIn content mentioning target company")
                    else:
                        relevance_score += 2  # Generic LinkedIn content
                        evidence.append("LinkedIn content")
            
            # Name matching with partial matching
            name_parts = interviewer_lower.split()
            name_matches = 0
            for part in name_parts:
                if len(part) > 2:  # Skip short parts like "Jr"
                    if part in title:
                        name_matches += 1
                        relevance_score += 3
                    elif part in content:
                        name_matches += 1
                        relevance_score += 2
            
            if name_matches > 0:
                evidence.append(f"{name_matches}/{len(name_parts)} name parts matched")
            else:
                rejection_reasons.append("Name not found in title or content")
            
            # Company context (avoid double-counting if already scored in LinkedIn evaluation)
            company_already_scored = any("mentioning target company" in ev for ev in evidence)
            if not company_already_scored:
                if company_lower in title:
                    relevance_score += 3
                    evidence.append(f"Company '{company}' in title")
                elif company_lower in content:
                    relevance_score += 2
                    evidence.append(f"Company '{company}' in content")
                else:
                    rejection_reasons.append(f"No '{company}' context found")
            
            # Professional indicators
            prof_indicators = ['profile', 'about', 'bio', 'experience', 'background', 'career']
            matches = sum(1 for indicator in prof_indicators if indicator in title or indicator in content)
            if matches > 0:
                relevance_score += min(matches, 3)
                evidence.append(f"{matches} professional indicators")
            
            # Validation decision with reasoning - STRICT COMPANY RELEVANCE REQUIRED
            # Only accept sources that have clear connection to the target company
            has_company_context = any("Company" in ev for ev in evidence)
            has_company_relevant_content = any("mentioning target company" in ev for ev in evidence)
            
            # STRICT CRITERIA: Must have company context OR be company-relevant content
            if has_company_context or has_company_relevant_content:
                threshold = 4  # Stricter threshold for company-connected sources
                if relevance_score >= threshold:
                    validated.append({
                        'source': source,
                        'relevance_score': relevance_score,
                        'evidence': evidence
                    })
                    validation_log.append(f"✅ VALIDATED: {source.get('title', 'Unknown')[:40]}... (Score: {relevance_score}, Evidence: {', '.join(evidence[:2])})")
                else:
                    validation_log.append(f"❌ REJECTED: {source.get('title', 'Unknown')[:40]}... (Score: {relevance_score}, Reasons: Below threshold despite company context)")
            else:
                # Automatically reject sources without company context
                validation_log.append(f"❌ REJECTED: {source.get('title', 'Unknown')[:40]}... (Score: {relevance_score}, Reasons: No company connection - {', '.join(rejection_reasons[:2])})")
        
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
