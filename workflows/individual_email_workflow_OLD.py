#!/usr/bin/env python3
"""
Individual Email Processing Workflow
Processes emails one by one through the complete pipeline:
1. Email Classification → 2. Entity Extraction → 3. Deep Research → 4. Prep Guide Generation
"""

import os
import sys
import asyncio
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.google_oauth.google_email_setup import get_gmail_service
from shared.google_oauth.google_email_functions import get_email_messages, get_email_message_details
from shared.tavily_cache import cached_search_tavily, get_tavily_cache
from agents.email_classifier.agent import EmailClassifierAgent
from agents.entity_extractor.agent import EntityExtractor
from agents.keyword_extractor.agent_email import EmailKeywordExtractor
from agents.memory_systems.shared_memory import SharedMemorySystem
from shared.tavily_client import client as tavily_client
from shared.models import AgentInput, AgentOutput
from dotenv import load_dotenv


class IndividualEmailWorkflow:
    """
    Complete end-to-end workflow processor for individual emails
    """
    
    def __init__(self):
        load_dotenv()
        self.memory_system = SharedMemorySystem()
        self.keyword_extractor = EmailKeywordExtractor()
        
        # Initialize agents with configuration
        agent_config = {'model': 'gpt-4', 'temperature': 0.7}
        self.classifier = EmailClassifierAgent(config=agent_config)
        self.entity_extractor = EntityExtractor(config=agent_config)
        
        # Create outputs directory structure
        self.outputs_dir = "outputs/fullworkflow"
        os.makedirs(self.outputs_dir, exist_ok=True)
    
    def _add_citation_with_deduplication(self, citations_database: Dict, citation: Dict, agent_source: str) -> str:
        """
        Add citation to database with deduplication based on URL/source
        
        Args:
            citations_database: Main citations database
            citation: Citation to add with keys 'id', 'source', 'url'
            agent_source: Name of the agent adding the citation
            
        Returns:
            The citation ID to use (either new or existing)
        """
        citation_url = citation.get('url', '').strip()
        citation_source = citation.get('source', '').strip()
        
        # Skip irrelevant citations
        if any(skip_term in citation_source.lower() for skip_term in ['instagram', 'istock', 'piano class', 'minor piano']):
            return None
        
        # Check for existing citation with same URL or source
        for existing_id, existing_data in citations_database.items():
            existing_url = existing_data.get('url', '').strip()
            existing_source = existing_data.get('source', '').strip()
            
            # Match by URL (primary) or source name (secondary)
            if citation_url and existing_url and citation_url == existing_url:
                print(f"   🔗 Reusing Citation [{existing_id}]: {citation_source} (found by {agent_source})")
                return existing_id
            elif not citation_url and citation_source and existing_source and citation_source.lower() == existing_source.lower():
                print(f"   🔗 Reusing Citation [{existing_id}]: {citation_source} (found by {agent_source})")
                return existing_id
        
        # Add new unique citation with sequential numbering
        new_citation_id = str(len(citations_database) + 1)
        citations_database[new_citation_id] = {
            'source': citation_source,
            'url': citation_url,
            'agent': agent_source
        }
        return new_citation_id
    
    def run_complete_individual_workflow(self, max_emails: int = 10) -> Dict[str, Any]:
        """
        Run the complete workflow processing emails individually
        
        Args:
            max_emails: Maximum number of emails to process
            
        Returns:
            Comprehensive results dictionary
        """
        print("🚀 INDIVIDUAL EMAIL PROCESSING WORKFLOW")
        print("=" * 80)
        start_time = datetime.now()
        
        # Get interview folder from .env
        interview_folder = os.getenv('INTERVIEW_FOLDER', 'INBOX').strip('"').strip("'")
        if not interview_folder:
            interview_folder = 'INBOX'
        
        print(f"📁 Using folder from INTERVIEW_FOLDER: {interview_folder}")
        
        try:
            # Step 1: Fetch emails from Gmail
            print(f"\n📧 Step 1: Fetching emails from {interview_folder}")
            emails = self._fetch_emails_from_gmail(interview_folder, max_emails)
            
            if not emails:
                print("❌ No emails found in the specified folder")
                return {
                    'success': False,
                    'error': 'No emails found',
                    'emails_processed': 0,
                    'interviews_found': 0
                }
            
            print(f"✅ Found {len(emails)} emails to process")
            
            # Step 2: Process each email individually
            results = {
                'success': True,
                'emails_processed': len(emails),
                'interviews_found': 0,
                'prep_guides_generated': 0,
                'processing_time': 0,
                'individual_results': []
            }
            
            for i, email in enumerate(emails, 1):
                print(f"\n" + "=" * 60)
                print(f"📧 PROCESSING EMAIL {i}/{len(emails)}")
                print("=" * 60)
                
                email_result = self._process_single_email(email, i)
                results['individual_results'].append(email_result)
                
                if email_result.get('is_interview'):
                    results['interviews_found'] += 1
                
                if email_result.get('prep_guide_generated'):
                    results['prep_guides_generated'] += 1
            
            results['processing_time'] = (datetime.now() - start_time).total_seconds()
            
            # Step 3: Display final summary
            self._display_final_summary(results)
            
            return results
            
        except Exception as e:
            error_result = {
                'success': False,
                'error': str(e),
                'emails_processed': 0,
                'interviews_found': 0,
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
            print(f"💥 Workflow failed: {str(e)}")
            return error_result
    
    def _fetch_emails_from_gmail(self, folder_name: str, max_results: int) -> List[Dict[str, Any]]:
        """Fetch emails from Gmail folder"""
        try:
            service = get_gmail_service()
            raw_emails = get_email_messages(service, folder_name=folder_name, max_results=max_results)
            
            emails = []
            for email_msg in raw_emails:
                email_details = get_email_message_details(service, email_msg['id'])
                emails.append(email_details)
            
            return emails
            
        except Exception as e:
            print(f"❌ Error fetching emails: {str(e)}")
            return []
    
    def _process_single_email(self, email: Dict[str, Any], email_index: int) -> Dict[str, Any]:
        """
        Process a single email through the complete pipeline
        
        Args:
            email: Email data dictionary
            email_index: Index of the email being processed
            
        Returns:
            Results dictionary for this email
        """
        email_start_time = datetime.now()
        
        print(f"📤 From: {email.get('from', 'Unknown')}")
        print(f"📧 Subject: {email.get('subject', 'No subject')}")
        print(f"📅 Date: {email.get('date', 'Unknown')}")
        
        result = {
            'email_index': email_index,
            'from': email.get('from', 'Unknown'),
            'subject': email.get('subject', 'No subject'),
            'date': email.get('date', 'Unknown'),
            'is_interview': False,
            'already_prepped': False,
            'entities_extracted': {},
            'research_completed': False,
            'prep_guide_generated': False,
            'company_keyword': None,
            'output_file': None,
            'processing_time': 0,
            'errors': []
        }
        
        try:
            # Phase 1: Email Classification
            print(f"\n🔍 Phase 1: Email Classification")
            classification_result = self._classify_email(email)
            
            if not classification_result.get('is_interview'):
                print(f"📋 Classification: {classification_result.get('category', 'Unknown')} (Non-interview)")
                print("⏭️  Skipping non-interview email")
                result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
                return result
            
            print(f"🎯 Classification: INTERVIEW EMAIL DETECTED!")
            result['is_interview'] = True
            result['entities_extracted'] = True  # Track that entity extraction was used
            
            # Phase 2: Entity Extraction & Memory Check
            print(f"\n🧩 Phase 2: Entity Extraction & Memory Check")
            entity_result = self._extract_entities_and_check_memory(email)
            result['entities_extracted_data'] = entity_result.get('entities', {})
            result['already_prepped'] = entity_result.get('already_prepped', False)
            
            if result['already_prepped']:
                print("✅ Interview already prepped - skipping research")
                result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
                return result
            
            # Phase 3: Deep Research Pipeline
            print(f"\n🔬 Phase 3: Deep Research with Tavily Integration")
            research_result = self._perform_deep_research(entity_result.get('entities', {}))
            result['research_completed'] = research_result.get('success', False)
            result['research_conducted'] = True  # Track that research pipeline was used
            
            # Store citations database for later access
            result['citations_database'] = research_result.get('citations_database', {})
            
            if not result['research_completed']:
                print("❌ Research failed - skipping prep guide generation")
                result['errors'].append(f"Research failed: {research_result.get('error', 'Unknown')}")
                result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
                return result
            
            # Phase 4: Deep Reflection on Research Quality
            print(f"\n🤔 Phase 4: Deep Reflection on Research Quality")
            reflection_result = self._reflect_on_research_quality(research_result)
            result['reflection_completed'] = True  # Track that reflection pipeline was used
            
            if not reflection_result.get('sufficient_for_prep_guide'):
                print("❌ Research insufficient for prep guide generation")
                result['errors'].append("Research quality insufficient for prep guide")
                result['failure_reason'] = "Research quality insufficient for prep guide"
                result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
                return result
            
            print("✅ Research quality sufficient - proceeding to prep guide generation")
            
            # Phase 5: Extract Company Keyword for File Naming
            print(f"\n🏷️  Phase 5: Extract Company Keyword")
            company_keyword = self._extract_company_keyword(email)
            result['company_keyword'] = company_keyword
            print(f"🏢 Company keyword: {company_keyword}")
            
            # Phase 6: Generate Personalized Prep Guide
            print(f"\n📚 Phase 6: Generate Personalized Prep Guide")
            prep_guide_result = self._generate_comprehensive_prep_guide(
                entity_result.get('entities', {}), 
                research_result,
                company_keyword,
                email  # Pass the original email data
            )
            result['prep_guide_generated'] = prep_guide_result.get('success', False)
            
            if result['prep_guide_generated']:
                # Phase 7: Save Individual Output File
                print(f"\n💾 Phase 7: Save Individual Output File")
                output_file = self._save_individual_output(
                    email, 
                    result, 
                    prep_guide_result.get('prep_guide_content', ''),
                    company_keyword,
                    research_result  # Pass the full research result
                )
                result['output_file'] = output_file
                print(f"📝 Saved: {output_file}")
            
            result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
            
            # Display final result for this email
            print(f"\n✅ Email {email_index} processing completed:")
            print(f"   📧 Subject: {result['subject'][:50]}...")
            print(f"   🏢 Company: {result['company_keyword']}")
            print(f"   🎯 Interview: {'Yes' if result['is_interview'] else 'No'}")
            print(f"   📊 Research: {'Completed' if result['research_completed'] else 'Skipped'}")
            print(f"   📚 Prep Guide: {'Generated' if result['prep_guide_generated'] else 'Skipped'}")
            print(f"   ⏱️  Processing Time: {result['processing_time']:.2f}s")
            
            return result
            
        except Exception as e:
            result['errors'].append(str(e))
            result['processing_time'] = (datetime.now() - email_start_time).total_seconds()
            print(f"❌ Error processing email {email_index}: {str(e)}")
            return result
    
    def _classify_email(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Classify email using EmailClassifierAgent"""
        try:
            # The classifier expects a list of emails with specific fields
            input_data = AgentInput(
                data={"emails": [email]},
                metadata={}
            )
            
            # Use asyncio to run the classifier
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(self.classifier.execute(input_data))
                
                # Get classification results - classifier returns 'interview', 'personal', 'other' keys
                interview_ids = result.data.get('interview', [])
                
                # Check if this email was classified as interview
                email_id = email.get('id', '')
                is_interview = email_id in interview_ids
                
                category = 'Interview_invite' if is_interview else 'Other'
                
                return {
                    'success': True,
                    'category': category,
                    'is_interview': is_interview
                }
            finally:
                loop.close()
                
        except Exception as e:
            print(f"❌ Classification error: {str(e)}")
            return {
                'success': False,
                'category': 'Unknown',
                'is_interview': False,
                'error': str(e)
            }
    
    def _extract_entities_and_check_memory(self, email: Dict[str, Any]) -> Dict[str, Any]:
        """Extract entities and check if already in memory"""
        try:
            # Extract entities
            email_text = f"Subject: {email.get('subject', '')}\n\nFrom: {email.get('from', '')}\n\nBody: {email.get('body', '')}"
            
            input_data = AgentInput(
                data={"text": email_text},
                metadata={}
            )
            
            # Use asyncio to run the entity extractor
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(self.entity_extractor.execute(input_data))
                raw_entities = result.data if result.success else {}
                
                # Map uppercase keys to lowercase for consistency
                entities = {}
                for key, value in raw_entities.items():
                    if isinstance(value, list) and value:
                        entities[key.lower()] = value[0] if len(value) == 1 else value
                    else:
                        entities[key.lower()] = value
                
                print(f"🧩 Entities extracted:")
                if entities:
                    for key, value in entities.items():
                        if value and key not in ['email_id']:
                            print(f"   {key.upper()}: {value}")
                else:
                    print(f"   No entities found")
                
                # Check if already in memory (simplified check based on company + role + interviewer)
                company = entities.get('company', '')
                role = entities.get('role', '')
                interviewer = entities.get('interviewer', '')
                
                if company:
                    # Check memory for similar interviews
                    all_interviews = self.memory_system.get_all_interviews()
                    for existing in all_interviews:
                        if (existing.get('company_name', '').lower() == company.lower() and
                            existing.get('role', '').lower() == role.lower() and
                            existing.get('status', '').lower() in ['prepped', 'completed']):
                            print(f"✅ Similar interview found in memory - ALREADY PREPPED")
                            return {
                                'success': True,
                                'entities': entities,
                                'already_prepped': True
                            }
                
                print(f"🆕 New interview - NOT YET PREPPED")
                return {
                    'success': True,
                    'entities': entities,
                    'already_prepped': False
                }
                
            finally:
                loop.close()
                
        except Exception as e:
            print(f"❌ Entity extraction error: {str(e)}")
            return {
                'success': False,
                'entities': {},
                'already_prepped': False,
                'error': str(e)
            }
    
    def _perform_deep_research(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Perform SOPHISTICATED deep research with Company/Role/Interviewer analysis, LinkedIn focus, and reflection loops"""
        try:
            from shared.tavily_client import search_tavily
            
            # Display cache statistics
            cache = get_tavily_cache()
            cache_stats = cache.get_cache_stats()
            print(f"   💾 TAVILY CACHE STATUS:")
            print(f"      📁 Valid Cache Files: {cache_stats.get('valid_cache_files', 0)}")
            print(f"      🗑️ Expired Cache Files: {cache_stats.get('expired_cache_files', 0)}")
            print(f"      📊 Total Cached Results: {cache_stats.get('total_cached_results', 0)}")
            
            # Clean expired cache
            removed = cache.clear_expired_cache()
            
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
            
            print(f"\n🧠 === SOPHISTICATED DEEP RESEARCH WITH ANALYSIS AGENTS ===")
            print(f"🔍 Research targets:")
            print(f"   🏢 Company: {company}")
            print(f"   💼 Role: {role}")
            print(f"   👤 Interviewer: {interviewer}")
            print(f"   🏷️ Email Keywords: {', '.join(email_keywords[:5])}...")
            
            research_data = {}
            citations_database = {}
            citation_counter = 1
            deep_thinking_log = []
            reflection_loops = 0
            max_reflection_loops = 3
            
            validation_metrics = {
                'sources_discovered': 0,
                'sources_validated': 0,
                'confidence_scores': [],
                'validation_phases_completed': 0,
                'linkedin_profiles_found': 0,
                'citation_count': 0
            }
            
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
                    deep_thinking_log.extend(company_analysis['thinking_log'])
                    
                    print(f"   ✅ COMPANY ANALYSIS: {company_analysis['analysis_summary']}")
                    print(f"   📊 Industry Insights: {company_analysis['industry_analysis']}")
                    print(f"   📈 Confidence: {company_analysis['confidence_score']:.2f}")
                    
                    # Display top validated sources with confidence scores and URLs
                    print(f"\n   🔍 **PHASE 3: Enhanced Source Validation & Filtering**")
                    top_sources = company_analysis.get('validated_sources', [])[:5]  # Show top 5
                    for i, source_data in enumerate(top_sources, 1):
                        source = source_data.get('source', {})
                        confidence = source_data.get('relevance_score', 0) / 10.0  # Convert to 0-1 scale
                        title = source.get('title', 'Unknown Title')[:60] + '...' if len(source.get('title', '')) > 60 else source.get('title', 'Unknown Title')
                        url = source.get('url', 'No URL')
                        evidence = source_data.get('evidence', [])
                        
                        print(f"   ✅ VALIDATED ({i}): {title} (confidence: {confidence:.2f})")
                        print(f"      🔗 URL: {url}")
                        print(f"      📝 Reasons: {', '.join(evidence[:3])}")  # Show top 3 reasons
                    
                    print(f"   📊 Validation Summary: {len(company_analysis['validated_sources'])} sources validated from {company_analysis['sources_processed']} discovered")
                    
                    # Store citations in main database with deduplication
                    for citation in company_analysis['citations']:
                        actual_citation_id = self._add_citation_with_deduplication(citations_database, citation, 'company_analysis')
                        if actual_citation_id:
                            print(f"   📝 Citation [{actual_citation_id}]: {citation['source']}")
            
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
                    deep_thinking_log.extend(role_analysis['thinking_log'])
                    
                    print(f"   ✅ ROLE ANALYSIS: {role_analysis['analysis_summary']}")
                    print(f"   🎯 Skills Gap: {role_analysis['skills_analysis']}")
                    print(f"   📈 Confidence: {role_analysis['confidence_score']:.2f}")
                    
                    # Display top validated sources with confidence scores and URLs
                    print(f"\n   🔍 **PHASE 3: Enhanced Role Source Validation & Filtering**")
                    top_sources = role_analysis.get('validated_sources', [])[:3]  # Show top 3
                    for i, source_data in enumerate(top_sources, 1):
                        source = source_data.get('source', {})
                        confidence = source_data.get('relevance_score', 0) / 10.0
                        title = source.get('title', 'Unknown Title')[:60] + '...' if len(source.get('title', '')) > 60 else source.get('title', 'Unknown Title')
                        url = source.get('url', 'No URL')
                        evidence = source_data.get('evidence', [])
                        
                        print(f"   ✅ VALIDATED ({i}): {title} (confidence: {confidence:.2f})")
                        print(f"      🔗 URL: {url}")
                        print(f"      🎯 Reasons: {', '.join(evidence[:3])}")
                    
                    print(f"   📊 Validation Summary: {len(role_analysis['validated_sources'])} sources validated from {role_analysis['sources_processed']} discovered")
                    
                    # Store citations in main database with deduplication
                    for citation in role_analysis['citations']:
                        actual_citation_id = self._add_citation_with_deduplication(citations_database, citation, 'role_analysis')
                        if actual_citation_id:
                            print(f"   📝 Citation [{actual_citation_id}]: {citation['source']}")
            
            # ========== INTERVIEWER ANALYSIS AGENT (LINKEDIN FOCUSED) ==========
            if interviewer:
                print(f"\n👤 === INTERVIEWER ANALYSIS AGENT ACTIVATED (LINKEDIN FOCUS) ===")
                interviewer_analysis = self._interviewer_analysis_agent(interviewer, company, email_keywords, citations_database, citation_counter)
                if interviewer_analysis['success']:
                    research_data['interviewer_analysis'] = interviewer_analysis
                    validation_metrics['sources_discovered'] += interviewer_analysis['sources_processed']
                    validation_metrics['sources_validated'] += len(interviewer_analysis['validated_sources'])
                    validation_metrics['confidence_scores'].append(interviewer_analysis['confidence_score'])
                    validation_metrics['citation_count'] += len(interviewer_analysis['citations'])
                    validation_metrics['linkedin_profiles_found'] += interviewer_analysis['linkedin_profiles_found']
                    citation_counter += len(interviewer_analysis['citations'])
                    deep_thinking_log.extend(interviewer_analysis['thinking_log'])
                    
                    print(f"   ✅ INTERVIEWER ANALYSIS: {interviewer_analysis['analysis_summary']}")
                    print(f"   🔗 LinkedIn Discovery: {interviewer_analysis['linkedin_analysis']}")
                    print(f"   📈 Confidence: {interviewer_analysis['confidence_score']:.2f}")
                    
                    # Display detailed source validation with LinkedIn focus
                    print(f"\n   🔍 **PHASE 3: Enhanced LinkedIn Source Validation & Filtering**")
                    all_sources = interviewer_analysis.get('validated_sources', [])
                    linkedin_sources = [s for s in all_sources if 'linkedin.com' in s.get('source', {}).get('url', '').lower()]
                    other_sources = [s for s in all_sources if 'linkedin.com' not in s.get('source', {}).get('url', '').lower()]
                    
                    # Show LinkedIn sources first (highest priority)
                    for i, source_data in enumerate(linkedin_sources[:2], 1):
                        source = source_data.get('source', {})
                        confidence = source_data.get('relevance_score', 0) / 10.0
                        title = source.get('title', 'Unknown Title')[:60] + '...' if len(source.get('title', '')) > 60 else source.get('title', 'Unknown Title')
                        url = source.get('url', 'No URL')
                        evidence = source_data.get('evidence', [])
                        
                        print(f"   ✅ VALIDATED (LinkedIn {i}): {title} (confidence: {confidence:.2f})")
                        print(f"      🔗 URL: {url}")
                        print(f"      👤 Reasons: {', '.join(evidence[:3])}")
                    
                    # Show other validated sources
                    for i, source_data in enumerate(other_sources[:3], 1):
                        source = source_data.get('source', {})
                        confidence = source_data.get('relevance_score', 0) / 10.0
                        title = source.get('title', 'Unknown Title')[:60] + '...' if len(source.get('title', '')) > 60 else source.get('title', 'Unknown Title')
                        url = source.get('url', 'No URL')
                        evidence = source_data.get('evidence', [])
                        
                        print(f"   ✅ VALIDATED ({i}): {title} (confidence: {confidence:.2f})")
                        print(f"      🔗 URL: {url}")
                        print(f"      📄 Reasons: {', '.join(evidence[:3])}")
                    
                    # Show rejected sources (if any)
                    rejected_count = interviewer_analysis['sources_processed'] - len(interviewer_analysis['validated_sources'])
                    if rejected_count > 0:
                        print(f"   ❌ REJECTED: {rejected_count} sources (low confidence or irrelevant)")
                    
                    print(f"   📊 Validation Summary: {len(interviewer_analysis['validated_sources'])} sources validated from {interviewer_analysis['sources_processed']} discovered")
                    print(f"   🔗 LinkedIn Profiles Found: {interviewer_analysis['linkedin_profiles_found']}")
                    
                    # Store citations in main database with deduplication
                    for citation in interviewer_analysis['citations']:
                        actual_citation_id = self._add_citation_with_deduplication(citations_database, citation, 'interviewer_analysis')
                        if actual_citation_id:
                            print(f"   📝 Citation [{actual_citation_id}]: {citation['source']}")
            
            # ========== REFLECTION LOOP SYSTEM ==========
            while reflection_loops < max_reflection_loops:
                print(f"\n🔄 === REFLECTION LOOP {reflection_loops + 1}/{max_reflection_loops} ===")
                reflection_result = self._sophisticated_reflection_analysis(research_data, email_keywords, citations_database)
                
                if reflection_result['research_sufficient']:
                    print(f"   ✅ Research Quality SUFFICIENT: {reflection_result['quality_assessment']}")
                    break
                else:
                    print(f"   ⚠️ Research Quality INSUFFICIENT: {reflection_result['quality_assessment']}")
                    print(f"   🔍 Additional Research Needed: {reflection_result['research_gaps']}")
                    
                    # Perform additional targeted research based on gaps
                    additional_research = self._perform_additional_research(reflection_result['research_gaps'], entities, citations_database, citation_counter)
                    if additional_research['sources_found'] > 0:
                        # Merge additional research into main data
                        for key, value in additional_research['research_updates'].items():
                            if key in research_data:
                                research_data[key].update(value)
                        validation_metrics['sources_discovered'] += additional_research['sources_found']
                        validation_metrics['citation_count'] += additional_research['citations_added']
                        citation_counter += additional_research['citations_added']
                        deep_thinking_log.extend(additional_research['thinking_log'])
                    
                    reflection_loops += 1
            
            # Calculate sophisticated confidence score
            overall_confidence = self._calculate_sophisticated_confidence(research_data, validation_metrics)
            
            print(f"\n📊 === SOPHISTICATED RESEARCH SUMMARY ===")
            print(f"   🔍 Total Sources Discovered: {validation_metrics['sources_discovered']}")
            print(f"   ✅ Sources Validated: {validation_metrics['sources_validated']}")
            print(f"   🔗 LinkedIn Profiles Found: {validation_metrics['linkedin_profiles_found']}")
            print(f"   📝 Citations Generated: {validation_metrics['citation_count']}")
            print(f"   🔄 Reflection Loops: {reflection_loops}")
            print(f"   📈 Sophisticated Confidence: {overall_confidence:.2f}")
            print(f"   🧠 Deep Thinking Insights: {len(deep_thinking_log)} recorded")
            
            # Final quality assessment
            research_quality = "EXCELLENT" if overall_confidence >= 0.85 else "HIGH" if overall_confidence >= 0.7 else "MEDIUM" if overall_confidence >= 0.5 else "LOW"
            print(f"   🏆 Research Quality: {research_quality}")
            
            print(f"   📝 Total Citations: {len(citations_database)} unique citations generated")
            
            return {
                'success': True,
                'research_data': research_data,
                'citations_database': citations_database,
                'validation_metrics': validation_metrics,
                'overall_confidence': overall_confidence,
                'deep_thinking_log': deep_thinking_log,
                'reflection_loops': reflection_loops,
                'research_quality': research_quality,
                'email_keywords': email_keywords
            }
            
        except Exception as e:
            print(f"❌ Sophisticated deep research error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'research_data': {},
                'overall_confidence': 0.0,
                'deep_thinking_log': [f"Error during sophisticated research: {str(e)}"]
            }
    
    def _validate_sources(self, sources: List[Dict], target: str, source_type: str, context: str = None) -> Dict[str, Any]:
        """Validate source relevance and quality"""
        relevant_sources = []
        target_lower = target.lower()
        context_lower = context.lower() if context else ""
        
        for source in sources:
            title = source.get('title', '').lower()
            content = source.get('content', '').lower()
            url = source.get('url', '').lower()
            
            relevance_score = 0
            quality_indicators = []
            
            # Check for target presence
            if target_lower in title:
                relevance_score += 3
                quality_indicators.append(f"Target '{target}' in title")
            elif target_lower in content:
                relevance_score += 2
                quality_indicators.append(f"Target '{target}' in content")
            
            # Check for context (e.g., company name)
            if context and context_lower in title:
                relevance_score += 2
                quality_indicators.append(f"Context '{context}' in title")
            elif context and context_lower in content:
                relevance_score += 1
                quality_indicators.append(f"Context '{context}' in content")
            
            # Source type specific validation
            if source_type == 'company':
                company_indicators = ['about', 'company', 'overview', 'business', 'careers', 'news']
                matches = sum(1 for indicator in company_indicators if indicator in title or indicator in content)
                relevance_score += matches
                if matches > 0:
                    quality_indicators.append(f"{matches} company indicators")
            
            elif source_type == 'role':
                role_indicators = ['job', 'position', 'role', 'requirements', 'skills', 'interview']
                matches = sum(1 for indicator in role_indicators if indicator in title or indicator in content)
                relevance_score += matches
                if matches > 0:
                    quality_indicators.append(f"{matches} role indicators")
            
            elif source_type == 'interviewer':
                if 'linkedin.com' in url:
                    relevance_score += 5
                    quality_indicators.append("LinkedIn profile")
                
                interviewer_indicators = ['profile', 'about', 'bio', 'background', 'experience']
                matches = sum(1 for indicator in interviewer_indicators if indicator in title or indicator in content)
                relevance_score += matches
                if matches > 0:
                    quality_indicators.append(f"{matches} profile indicators")
            
            # Include if relevance score is sufficient
            if relevance_score >= 2:
                relevant_sources.append({
                    'source': source,
                    'relevance_score': relevance_score,
                    'quality_indicators': quality_indicators
                })
        
        confidence_score = min(0.95, (len(relevant_sources) / max(1, len(sources))) * 0.8 + 0.2)
        
        return {
            'is_relevant': len(relevant_sources) >= 1,
            'relevant_sources': relevant_sources,
            'confidence_score': confidence_score,
            'total_sources': len(sources)
        }
    
    def _reflect_on_research_quality(self, research_result: Dict[str, Any]) -> Dict[str, Any]:
        """Deep reflection on research quality to determine if sufficient for prep guide"""
        try:
            research_data = research_result.get('research_data', {})
            overall_confidence = research_result.get('overall_confidence', 0.0)
            
            print(f"🤔 Analyzing research quality...")
            
            quality_factors = []
            quality_score = 0
            
            # Factor 1: Overall confidence threshold
            if overall_confidence >= 0.7:
                quality_factors.append("High research confidence")
                quality_score += 3
            elif overall_confidence >= 0.5:
                quality_factors.append("Moderate research confidence")
                quality_score += 2
            else:
                quality_factors.append("Low research confidence")
                quality_score += 1
            
            # Factor 2: Company research quality
            company_research = research_data.get('company_research', {})
            if company_research.get('is_relevant'):
                company_sources = len(company_research.get('relevant_sources', []))
                if company_sources >= 3:
                    quality_factors.append("Strong company research")
                    quality_score += 2
                elif company_sources >= 1:
                    quality_factors.append("Basic company research")
                    quality_score += 1
            
            # Factor 3: Role research quality
            role_research = research_data.get('role_research', {})
            if role_research.get('is_relevant'):
                role_sources = len(role_research.get('relevant_sources', []))
                if role_sources >= 2:
                    quality_factors.append("Good role research")
                    quality_score += 2
                elif role_sources >= 1:
                    quality_factors.append("Basic role research")
                    quality_score += 1
            
            # Factor 4: Interviewer research (bonus points)
            interviewer_research = research_data.get('interviewer_research', {})
            if interviewer_research.get('is_relevant'):
                # Check for LinkedIn profile
                linkedin_found = any(
                    'linkedin.com' in source.get('source', {}).get('url', '').lower()
                    for source in interviewer_research.get('relevant_sources', [])
                )
                if linkedin_found:
                    quality_factors.append("LinkedIn profile found")
                    quality_score += 3
                else:
                    quality_factors.append("Interviewer information found")
                    quality_score += 1
            
            # Decision threshold: need at least 2 points for prep guide (lowered from 4 to see sophisticated research)
            sufficient_for_prep_guide = quality_score >= 2
            
            print(f"📊 Quality Analysis:")
            for factor in quality_factors:
                print(f"   ✅ {factor}")
            print(f"   🎯 Quality Score: {quality_score}/10")
            print(f"   📋 Sufficient for Prep Guide: {'Yes' if sufficient_for_prep_guide else 'No'}")
            
            if not sufficient_for_prep_guide:
                print(f"⚠️  Research quality insufficient - need more validated sources")
            
            return {
                'sufficient_for_prep_guide': sufficient_for_prep_guide,
                'quality_score': quality_score,
                'quality_factors': quality_factors,
                'confidence_score': overall_confidence
            }
            
        except Exception as e:
            print(f"❌ Research reflection error: {str(e)}")
            return {
                'sufficient_for_prep_guide': False,
                'error': str(e)
            }
    
    def _extract_company_keyword(self, email: Dict[str, Any]) -> str:
        """Extract company keyword using EmailKeywordExtractor"""
        try:
            keyword = self.keyword_extractor.extract_keyword_from_email(email)
            return keyword if keyword else "Unknown_Company"
        except Exception as e:
            print(f"❌ Keyword extraction error: {str(e)}")
            return "Unknown_Company"
    
    def _generate_comprehensive_prep_guide(self, entities: Dict[str, Any], research_result: Dict[str, Any], company_keyword: str, email: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive prep guide with sophisticated research citations"""
        try:
            from shared.llm_client import call_llm
            
            company = entities.get('company', 'Unknown Company')
            role = entities.get('role', 'Unknown Role')
            interviewer = entities.get('interviewer', 'Unknown Interviewer')
            dates = entities.get('date', [])
            format_type = entities.get('format', 'Unknown Format')
            
            # Extract specific email details for actionable advice
            email_subject = email.get('subject', '')
            email_body = email.get('body', '')
            from_sender = email.get('from', '')
            
            research_data = research_result.get('research_data', {})
            citations_database = research_result.get('citations_database', {})
            
            # Build comprehensive context with citations from all analysis agents
            context_with_citations = self._build_sophisticated_research_context(research_data, citations_database)
            
            prompt = f"""
            Generate a comprehensive interview preparation guide based on this SPECIFIC interview email and sophisticated research:
            
            **SPECIFIC INTERVIEW EMAIL:**
            From: {from_sender}
            Subject: {email_subject}
            Interview Dates: {', '.join(dates) if dates else 'Not specified'}
            Format: {format_type}
            
            **Extracted Details:**
            - Company: {company}
            - Role: {role}
            - Interviewer: {interviewer}
            
            **Sophisticated Research Context with Citations:**
            {context_with_citations}
            
            Create a SPECIFIC and ACTIONABLE prep guide with these sections:
            
            1. **Before the Interview** - SPECIFIC next steps based on THIS email:
               - Exact response deadline and timing from the email
               - Specific time slots to choose from this email
               - Who to reply to and how
               - Company mission, products, and current projects to research
               - Specific technologies and approaches to understand
               
            2. **Company Analysis** - Based on research findings:
               - What problems they solve and their approach
               - Recent developments and market position
               - Technologies they use (include specific GitHub/LinkedIn findings)
               
            3. **Role Analysis** - Tailored to this specific role:
               - What they're looking for in this role
               - Key skills and qualifications needed
               - How to demonstrate relevant experience
               
            4. **Interviewer Background** - Based on LinkedIn research:
               - Professional background and expertise
               - Recent posts, articles, or achievements
               - Common interests or connection points
               
            5. **Questions to Ask** - Intelligent questions based on research
            6. **Strategic Recommendations** - How to position yourself
            
            CRITICAL REQUIREMENTS:
            - Include specific citations [Citation 1], [Citation 2], etc. for ALL findings and recommendations
            - Use the numbered citation system from the research database
            - Base timing and logistics on the ACTUAL email content
            - Show SPECIFIC findings from LinkedIn, GitHub, company website research
            - Make it immediately actionable with clear next steps
            - Every fact, insight, and recommendation MUST have a citation number
            - Format citations as [Citation X] where X is the citation number
            """
            
            # Use asyncio to call LLM
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                prep_guide_content = loop.run_until_complete(call_llm(prompt))
                
                print(f"✅ Sophisticated prep guide generated ({len(prep_guide_content)} characters)")
                
                # Display the prep guide content in terminal with citation summary
                print(f"\n" + "=" * 80)
                print(f"📚 SOPHISTICATED PREP GUIDE FOR {company.upper()}")
                print(f"🔍 Based on {research_result.get('validation_metrics', {}).get('citation_count', 0)} research citations")
                print(f"🔗 LinkedIn profiles found: {research_result.get('validation_metrics', {}).get('linkedin_profiles_found', 0)}")
                print(f"=" * 80)
                print(prep_guide_content)
                print(f"=" * 80)
                
                # Add citation appendix if available
                if citations_database:
                    print(f"\n📝 RESEARCH CITATIONS:")
                    for citation_id, citation_data in citations_database.items():
                        source_info = citation_data.get('source', 'Unknown source')
                        url = citation_data.get('url', '')
                        if url:
                            print(f"[Citation {citation_id}] {source_info} - {url}")
                        else:
                            print(f"[Citation {citation_id}] {source_info}")
                    print(f"=" * 80)
                
                return {
                    'success': True,
                    'prep_guide_content': prep_guide_content,
                    'company': company,
                    'role': role,
                    'interviewer': interviewer,
                    'citations_count': len(citations_database),
                    'research_quality': research_result.get('research_quality', 'Unknown')
                }
                
            finally:
                loop.close()
                
        except Exception as e:
            print(f"❌ Prep guide generation error: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'prep_guide_content': ''
            }
    
    def _build_sophisticated_research_context(self, research_data: Dict[str, Any], citations_db: Dict) -> str:
        """Build sophisticated research context with citations from all analysis agents"""
        context_parts = []
        
        # Company Analysis Context
        company_analysis = research_data.get('company_analysis', {})
        if company_analysis.get('success'):
            context_parts.append("**COMPANY ANALYSIS:**")
            context_parts.append(f"Industry Analysis: {company_analysis.get('industry_analysis', 'Not available')}")
            context_parts.append(f"Financial Insights: {company_analysis.get('financial_insights', 'Not available')}")
            context_parts.append(f"Company Identity Validation: {company_analysis.get('company_identity', {}).get('reasoning', 'Not validated')}")
            
            # Add company citations
            for citation in company_analysis.get('citations', []):
                context_parts.append(f"Citation [{citation['id']}]: {citation['source']}")
                context_parts.append(f"  -> {citation.get('content_snippet', 'No snippet available')}")
        
        # Role Analysis Context
        role_analysis = research_data.get('role_analysis', {})
        if role_analysis.get('success'):
            context_parts.append("\n**ROLE ANALYSIS:**")
            context_parts.append(f"Skills Analysis: {role_analysis.get('skills_analysis', 'Not available')}")
            context_parts.append(f"Interview Preparation: {role_analysis.get('interview_preparation', 'Not available')}")
            context_parts.append(f"Role Requirements: {role_analysis.get('role_requirements', {}).get('reasoning', 'Not analyzed')}")
            
            # Add role citations
            for citation in role_analysis.get('citations', []):
                context_parts.append(f"Citation [{citation['id']}]: {citation['source']}")
                context_parts.append(f"  -> {citation.get('content_snippet', 'No snippet available')}")
        
        # Interviewer Analysis Context (LinkedIn Focus)
        interviewer_analysis = research_data.get('interviewer_analysis', {})
        if interviewer_analysis.get('success'):
            context_parts.append("\n**INTERVIEWER ANALYSIS (LINKEDIN FOCUSED):**")
            context_parts.append(f"LinkedIn Analysis: {interviewer_analysis.get('linkedin_analysis', 'Not available')}")
            context_parts.append(f"Professional Background: {interviewer_analysis.get('professional_background', 'Not available')}")
            context_parts.append(f"Employee Validation: {interviewer_analysis.get('employee_validation', {}).get('reasoning', 'Not validated')}")
            context_parts.append(f"LinkedIn Profiles Found: {interviewer_analysis.get('linkedin_profiles_found', 0)}")
            
            # Add interviewer citations
            for citation in interviewer_analysis.get('citations', []):
                context_parts.append(f"Citation [{citation['id']}]: {citation['source']}")
                context_parts.append(f"  -> {citation.get('content_snippet', 'No snippet available')}")
        
        # Research Quality Summary
        context_parts.append("\n**RESEARCH QUALITY SUMMARY:**")
        total_citations = sum(len(data.get('citations', [])) for data in research_data.values() if isinstance(data, dict))
        context_parts.append(f"Total Citations: {total_citations}")
        context_parts.append(f"Research Agents Used: {len([k for k in research_data.keys() if research_data[k].get('success')])}")
        
        return "\n".join(context_parts)
    
    def _build_research_context_with_citations(self, research_data: Dict[str, Any]) -> str:
        """Build research context with proper citations"""
        context_parts = []
        citation_counter = 1
        citations = []
        
        # Company research
        company_research = research_data.get('company_research', {})
        if company_research.get('is_relevant'):
            context_parts.append("**Company Research:**")
            for source_data in company_research.get('relevant_sources', []):
                source = source_data.get('source', {})
                title = source.get('title', 'Unknown Title')
                url = source.get('url', '')
                content_snippet = source.get('content', '')[:200] + "..."
                
                context_parts.append(f"[{citation_counter}] {title}")
                context_parts.append(f"    {content_snippet}")
                citations.append(f"[{citation_counter}] {title} - {url}")
                citation_counter += 1
        
        # Role research
        role_research = research_data.get('role_research', {})
        if role_research.get('is_relevant'):
            context_parts.append("\n**Role Research:**")
            for source_data in role_research.get('relevant_sources', []):
                source = source_data.get('source', {})
                title = source.get('title', 'Unknown Title')
                url = source.get('url', '')
                content_snippet = source.get('content', '')[:200] + "..."
                
                context_parts.append(f"[{citation_counter}] {title}")
                context_parts.append(f"    {content_snippet}")
                citations.append(f"[{citation_counter}] {title} - {url}")
                citation_counter += 1
        
        # Interviewer research
        interviewer_research = research_data.get('interviewer_research', {})
        if interviewer_research.get('is_relevant'):
            context_parts.append("\n**Interviewer Research:**")
            for source_data in interviewer_research.get('relevant_sources', []):
                source = source_data.get('source', {})
                title = source.get('title', 'Unknown Title')
                url = source.get('url', '')
                content_snippet = source.get('content', '')[:200] + "..."
                
                context_parts.append(f"[{citation_counter}] {title}")
                context_parts.append(f"    {content_snippet}")
                citations.append(f"[{citation_counter}] {title} - {url}")
                citation_counter += 1
        
        # Add citations section
        if citations:
            context_parts.append("\n**Citations:**")
            context_parts.extend(citations)
        
        return "\n".join(context_parts)
    
    def _save_individual_output(self, email: Dict[str, Any], result: Dict[str, Any], prep_guide_content: str, company_keyword: str, research_result: Dict[str, Any] = None) -> str:
        """Save individual email processing results to company-specific .txt file"""
        try:
            # Ensure research_result has a default value
            if research_result is None:
                research_result = {}
            
            # Create safe filename
            safe_company_name = "".join(c for c in company_keyword if c.isalnum() or c in ('-', '_')).rstrip()
            if not safe_company_name:
                safe_company_name = f"Email_{result['email_index']}"
            
            filename = f"{safe_company_name}.txt"
            filepath = os.path.join(self.outputs_dir, filename)
            
            # Generate comprehensive text file content
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Generate research validation section if available
            research_validation_section = ""
            if research_result:
                research_validation_section = self._format_research_validation_for_output(research_result)
            
            # Generate complete phase-by-phase processing details
            phase_details = self._generate_complete_phase_details(email, result, research_result)
            
            file_content = f"""
================================================================================
INDIVIDUAL EMAIL PROCESSING RESULTS
================================================================================
Company: {company_keyword}
Generated: {timestamp}
Processing Time: {result['processing_time']:.2f}s

This file contains the complete results from processing a single interview email
through the Individual Email Processing Workflow including Classification,
Entity Extraction, Deep Research, and Comprehensive Prep Guide generation.

================================================================================
ORIGINAL EMAIL DATA
================================================================================
From: {email.get('from', 'Unknown')}
Subject: {email.get('subject', 'No subject')}
Date: {email.get('date', 'Unknown')}
Body: {email.get('body', 'No content')[:500]}{'...' if len(email.get('body', '')) > 500 else ''}

================================================================================
DETAILED RESEARCH VALIDATION PROCESS
================================================================================
{research_validation_section}

================================================================================
PROCESSING RESULTS
================================================================================
Email Index: {result.get('email_index', 'Unknown')}
Is Interview: {result.get('is_interview', False)}
Classification: {'Interview Email' if result.get('is_interview') else 'Non-Interview Email'}
Entities Extracted: {result.get('entities_extracted', {})}
Research Conducted: {result.get('research_conducted', False)}
Research Quality Score: {result.get('research_quality_score', 'N/A')}
Prep Guide Generated: {result.get('prep_guide_generated', False)}

================================================================================
COMPLETE PHASE-BY-PHASE PROCESSING LOG
================================================================================
{phase_details}

================================================================================
COMPREHENSIVE INTERVIEW PREPARATION GUIDE
================================================================================

{prep_guide_content}

================================================================================
RESEARCH CITATIONS DATABASE
================================================================================
{self._format_citation_database(research_result)}

================================================================================
TECHNICAL METADATA
================================================================================
Workflow Version: Individual Email Processing v2.0
Pipeline Stages Completed:
- ✅ Email Classification
- {'✅' if result.get('entities_extracted') else '❌'} Entity Extraction
- {'✅' if result.get('research_conducted') else '❌'} Deep Research with Tavily
- {'✅' if result.get('reflection_completed') else '❌'} Research Quality Reflection
- {'✅' if result.get('prep_guide_generated') else '❌'} Prep Guide Generation
- ✅ File Output

Processing Errors: {result.get('errors', [])}
Company Keyword: {company_keyword}
Output File: {filename}

Generated by Resume AI Agents - Individual Email Processing Workflow
================================================================================
"""
            
            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            return filename
            
        except Exception as e:
            print(f"❌ Error saving output file: {str(e)}")
            return f"Error_{result.get('email_index', 'unknown')}.txt"
    
    def _format_research_validation_for_output(self, research_result: Dict[str, Any]) -> str:
        """Format the research validation process for output file"""
        try:
            research_data = research_result.get('research_data', {})
            validation_metrics = research_result.get('validation_metrics', {})
            
            output_lines = []
            output_lines.append("🧠 === SOPHISTICATED DEEP RESEARCH WITH ANALYSIS AGENTS ===")
            output_lines.append(f"🔍 Total Sources Discovered: {validation_metrics.get('sources_discovered', 0)}")
            output_lines.append(f"✅ Sources Validated: {validation_metrics.get('sources_validated', 0)}")
            output_lines.append(f"📝 Citations Generated: {validation_metrics.get('citation_count', 0)}")
            output_lines.append(f"🔗 LinkedIn profiles found: {validation_metrics.get('linkedin_profiles_found', 0)}")
            output_lines.append("")
            
            # Company Analysis Agent Details
            if 'company_analysis' in research_data:
                company_data = research_data['company_analysis']
                output_lines.append("🏢 === COMPANY ANALYSIS AGENT ===")
                output_lines.append(f"✅ Analysis: {company_data.get('analysis_summary', 'No summary')}")
                output_lines.append(f"📊 Industry Insights: {company_data.get('industry_analysis', 'No insights')}")
                output_lines.append(f"📈 Confidence: {company_data.get('confidence_score', 0):.2f}")
                output_lines.append("")
                
                # Show validated sources with URLs
                output_lines.append("🔍 **PHASE 3: Enhanced Source Validation & Filtering**")
                validated_sources = company_data.get('validated_sources', [])[:5]  # Top 5
                for i, source_data in enumerate(validated_sources, 1):
                    source = source_data.get('source', {})
                    confidence = source_data.get('relevance_score', 0) / 10.0
                    title = source.get('title', 'Unknown Title')[:60] + '...' if len(source.get('title', '')) > 60 else source.get('title', 'Unknown Title')
                    url = source.get('url', 'No URL')
                    evidence = source_data.get('evidence', [])
                    
                    output_lines.append(f"✅ VALIDATED ({i}): {title} (confidence: {confidence:.2f})")
                    output_lines.append(f"   🔗 URL: {url}")
                    output_lines.append(f"   📝 Reasons: {', '.join(evidence[:3])}")
                
                output_lines.append(f"📊 Validation Summary: {len(company_data.get('validated_sources', []))} sources validated from {company_data.get('sources_processed', 0)} discovered")
                output_lines.append("")
            
            # Role Analysis Agent Details
            if 'role_analysis' in research_data:
                role_data = research_data['role_analysis']
                output_lines.append("💼 === ROLE ANALYSIS AGENT ===")
                output_lines.append(f"✅ Analysis: {role_data.get('analysis_summary', 'No summary')}")
                output_lines.append(f"🎯 Skills Gap: {role_data.get('skills_analysis', 'No analysis')}")
                output_lines.append(f"📈 Confidence: {role_data.get('confidence_score', 0):.2f}")
                output_lines.append("")
                
                # Show validated sources with URLs
                output_lines.append("🔍 **PHASE 3: Enhanced Role Source Validation & Filtering**")
                validated_sources = role_data.get('validated_sources', [])[:3]  # Top 3
                for i, source_data in enumerate(validated_sources, 1):
                    source = source_data.get('source', {})
                    confidence = source_data.get('relevance_score', 0) / 10.0
                    title = source.get('title', 'Unknown Title')[:60] + '...' if len(source.get('title', '')) > 60 else source.get('title', 'Unknown Title')
                    url = source.get('url', 'No URL')
                    evidence = source_data.get('evidence', [])
                    
                    output_lines.append(f"✅ VALIDATED ({i}): {title} (confidence: {confidence:.2f})")
                    output_lines.append(f"   🔗 URL: {url}")
                    output_lines.append(f"   🎯 Reasons: {', '.join(evidence[:3])}")
                
                output_lines.append(f"📊 Validation Summary: {len(role_data.get('validated_sources', []))} sources validated from {role_data.get('sources_processed', 0)} discovered")
                output_lines.append("")
            
            # Interviewer Analysis Agent Details
            if 'interviewer_analysis' in research_data:
                interviewer_data = research_data['interviewer_analysis']
                output_lines.append("👤 === INTERVIEWER ANALYSIS AGENT (LINKEDIN FOCUS) ===")
                output_lines.append(f"✅ Analysis: {interviewer_data.get('analysis_summary', 'No summary')}")
                output_lines.append(f"🔗 LinkedIn Discovery: {interviewer_data.get('linkedin_analysis', 'No LinkedIn data')}")
                output_lines.append(f"📈 Confidence: {interviewer_data.get('confidence_score', 0):.2f}")
                output_lines.append("")
                
                # Show LinkedIn-focused validation
                output_lines.append("🔍 **PHASE 3: Enhanced LinkedIn Source Validation & Filtering**")
                all_sources = interviewer_data.get('validated_sources', [])
                linkedin_sources = [s for s in all_sources if 'linkedin.com' in s.get('source', {}).get('url', '').lower()]
                other_sources = [s for s in all_sources if 'linkedin.com' not in s.get('source', {}).get('url', '').lower()]
                
                # Show LinkedIn sources first
                for i, source_data in enumerate(linkedin_sources[:2], 1):
                    source = source_data.get('source', {})
                    confidence = source_data.get('relevance_score', 0) / 10.0
                    title = source.get('title', 'Unknown Title')[:60] + '...' if len(source.get('title', '')) > 60 else source.get('title', 'Unknown Title')
                    url = source.get('url', 'No URL')
                    evidence = source_data.get('evidence', [])
                    
                    output_lines.append(f"✅ VALIDATED (LinkedIn {i}): {title} (confidence: {confidence:.2f})")
                    output_lines.append(f"   🔗 URL: {url}")
                    output_lines.append(f"   👤 Reasons: {', '.join(evidence[:3])}")
                
                # Show other sources
                for i, source_data in enumerate(other_sources[:3], 1):
                    source = source_data.get('source', {})
                    confidence = source_data.get('relevance_score', 0) / 10.0
                    title = source.get('title', 'Unknown Title')[:60] + '...' if len(source.get('title', '')) > 60 else source.get('title', 'Unknown Title')
                    url = source.get('url', 'No URL')
                    evidence = source_data.get('evidence', [])
                    
                    output_lines.append(f"✅ VALIDATED ({i}): {title} (confidence: {confidence:.2f})")
                    output_lines.append(f"   🔗 URL: {url}")
                    output_lines.append(f"   📄 Reasons: {', '.join(evidence[:3])}")
                
                # Show rejected sources
                rejected_count = interviewer_data.get('sources_processed', 0) - len(interviewer_data.get('validated_sources', []))
                if rejected_count > 0:
                    output_lines.append(f"❌ REJECTED: {rejected_count} sources (low confidence or irrelevant)")
                
                output_lines.append(f"📊 Validation Summary: {len(interviewer_data.get('validated_sources', []))} sources validated from {interviewer_data.get('sources_processed', 0)} discovered")
                output_lines.append(f"🔗 LinkedIn Profiles Found: {interviewer_data.get('linkedin_profiles_found', 0)}")
                output_lines.append("")
            
            return "\n".join(output_lines)
            
        except Exception as e:
            return f"❌ Error formatting research validation: {str(e)}"
    
    def _format_citation_database(self, research_result: Dict[str, Any]) -> str:
        """Format the complete citation database for output file"""
        try:
            citations_database = research_result.get('citations_database', {})
            
            if not citations_database:
                return "No citations available."
            
            output_lines = []
            output_lines.append("Complete database of all research citations used in the preparation guide:\n")
            
            # Sort citations by number
            sorted_citations = sorted(citations_database.items(), key=lambda x: int(x[0]))
            
            for citation_id, citation_data in sorted_citations[:25]:  # Show top 25 citations
                source_info = citation_data.get('source', 'Unknown source')
                url = citation_data.get('url', '')
                
                if url:
                    output_lines.append(f"📝 Citation [{citation_id}]: {source_info} - {url}")
                else:
                    output_lines.append(f"📝 Citation [{citation_id}]: {source_info}")
            
            if len(citations_database) > 25:
                output_lines.append(f"\n... and {len(citations_database) - 25} more citations used in research.")
            
            output_lines.append(f"\nTotal Citations: {len(citations_database)}")
            
            return "\n".join(output_lines)
            
        except Exception as e:
            return f"❌ Error formatting citation database: {str(e)}"
    
    def _generate_complete_phase_details(self, email: Dict[str, Any], result: Dict[str, Any], research_result: Dict[str, Any] = None) -> str:
        """Generate complete phase-by-phase processing details for output file"""
        try:
            phase_lines = []
            
            # Phase 1: Email Classification
            phase_lines.append("🔍 PHASE 1: EMAIL CLASSIFICATION")
            phase_lines.append(f"   📧 Email Subject: {email.get('subject', 'No subject')}")
            phase_lines.append(f"   📤 From: {email.get('from', 'Unknown')}")
            phase_lines.append(f"   📅 Date: {email.get('date', 'Unknown')}")
            phase_lines.append(f"   🎯 Classification Result: {'INTERVIEW EMAIL DETECTED!' if result.get('is_interview') else 'NON-INTERVIEW EMAIL'}")
            phase_lines.append(f"   ✅ Status: COMPLETED")
            phase_lines.append("")
            
            # Phase 2: Entity Extraction & Memory Check
            phase_lines.append("🧩 PHASE 2: ENTITY EXTRACTION & MEMORY CHECK")
            entities = result.get('entities_extracted', {})
            if entities and isinstance(entities, dict):
                for entity_type, entity_value in entities.items():
                    if isinstance(entity_value, list):
                        phase_lines.append(f"   {entity_type.upper()}: {entity_value}")
                    else:
                        phase_lines.append(f"   {entity_type.upper()}: {entity_value}")
            elif entities:
                phase_lines.append(f"   ✅ Entities extracted successfully")
            else:
                phase_lines.append("   ❌ No entities extracted")
            
            phase_lines.append(f"   🆕 Memory Status: {'Already prepped' if result.get('already_prepped') else 'New interview - NOT YET PREPPED'}")
            phase_lines.append(f"   ✅ Status: COMPLETED")
            phase_lines.append("")
            
            # Phase 3: Deep Research with Tavily Integration
            phase_lines.append("🔬 PHASE 3: DEEP RESEARCH WITH TAVILY INTEGRATION")
            if research_result:
                validation_metrics = research_result.get('validation_metrics', {})
                research_data = research_result.get('research_data', {})
                
                phase_lines.append(f"   🔍 Total Sources Discovered: {validation_metrics.get('sources_discovered', 0)}")
                phase_lines.append(f"   ✅ Sources Validated: {validation_metrics.get('sources_validated', 0)}")
                phase_lines.append(f"   📝 Citations Generated: {validation_metrics.get('citation_count', 0)}")
                phase_lines.append(f"   🔗 LinkedIn Profiles Found: {validation_metrics.get('linkedin_profiles_found', 0)}")
                phase_lines.append(f"   📈 Overall Confidence: {research_result.get('overall_confidence', 0):.2f}")
                phase_lines.append(f"   🏆 Research Quality: {research_result.get('research_quality', 'Unknown')}")
                
                # Show analysis agents used
                if 'company_analysis' in research_data:
                    phase_lines.append(f"   🏢 Company Analysis Agent: ACTIVATED")
                    company_data = research_data['company_analysis']
                    phase_lines.append(f"      📊 Sources Processed: {company_data.get('sources_processed', 0)}")
                    phase_lines.append(f"      ✅ Sources Validated: {len(company_data.get('validated_sources', []))}")
                    phase_lines.append(f"      🎯 Cache Hits: {company_data.get('cache_hits', 0)}")
                
                if 'role_analysis' in research_data:
                    phase_lines.append(f"   💼 Role Analysis Agent: ACTIVATED")
                    role_data = research_data['role_analysis']
                    phase_lines.append(f"      📊 Sources Processed: {role_data.get('sources_processed', 0)}")
                    phase_lines.append(f"      ✅ Sources Validated: {len(role_data.get('validated_sources', []))}")
                    phase_lines.append(f"      🎯 Cache Hits: {role_data.get('cache_hits', 0)}")
                
                if 'interviewer_analysis' in research_data:
                    phase_lines.append(f"   👤 Interviewer Analysis Agent: ACTIVATED (LINKEDIN FOCUS)")
                    interviewer_data = research_data['interviewer_analysis']
                    phase_lines.append(f"      📊 Sources Processed: {interviewer_data.get('sources_processed', 0)}")
                    phase_lines.append(f"      ✅ Sources Validated: {len(interviewer_data.get('validated_sources', []))}")
                    phase_lines.append(f"      🔗 LinkedIn Profiles Found: {interviewer_data.get('linkedin_profiles_found', 0)}")
                    phase_lines.append(f"      🎯 Cache Hits: {interviewer_data.get('cache_hits', 0)}")
                
                phase_lines.append(f"   ✅ Status: COMPLETED")
            else:
                phase_lines.append("   ❌ No research conducted")
                phase_lines.append(f"   ❌ Status: FAILED")
            phase_lines.append("")
            
            # Phase 4: Deep Reflection on Research Quality
            phase_lines.append("🤔 PHASE 4: DEEP REFLECTION ON RESEARCH QUALITY")
            if result.get('reflection_completed'):
                phase_lines.append(f"   🔍 Research Quality Analysis: COMPLETED")
                phase_lines.append(f"   📊 Quality Factors Analyzed: Company research, Role research, Interviewer research")
                phase_lines.append(f"   🎯 Research Sufficient: {'YES' if research_result and research_result.get('overall_confidence', 0) > 0.5 else 'NO'}")
                phase_lines.append(f"   ✅ Status: COMPLETED")
            else:
                phase_lines.append("   ❌ Status: SKIPPED")
            phase_lines.append("")
            
            # Phase 5: Extract Company Keyword
            phase_lines.append("🏷️ PHASE 5: EXTRACT COMPANY KEYWORD")
            company_keyword = result.get('company_keyword', 'Unknown')
            phase_lines.append(f"   🏢 Company Keyword Extracted: {company_keyword}")
            phase_lines.append(f"   📝 File Naming: {company_keyword}.txt")
            phase_lines.append(f"   ✅ Status: COMPLETED")
            phase_lines.append("")
            
            # Phase 6: Generate Personalized Prep Guide
            phase_lines.append("📚 PHASE 6: GENERATE PERSONALIZED PREP GUIDE")
            if result.get('prep_guide_generated'):
                phase_lines.append(f"   📝 Prep Guide Generation: SUCCESSFUL")
                phase_lines.append(f"   🔍 Based on Research Citations: {len(research_result.get('citations_database', {})) if research_result else 0}")
                phase_lines.append(f"   🎯 Tailored for Company: {company_keyword}")
                phase_lines.append(f"   📊 LinkedIn Profiles Utilized: {research_result.get('validation_metrics', {}).get('linkedin_profiles_found', 0) if research_result else 0}")
                phase_lines.append(f"   ✅ Status: COMPLETED")
            else:
                phase_lines.append("   ❌ Status: FAILED")
            phase_lines.append("")
            
            # Phase 7: Save Individual Output File
            phase_lines.append("💾 PHASE 7: SAVE INDIVIDUAL OUTPUT FILE")
            output_file = result.get('output_file', 'Unknown')
            phase_lines.append(f"   📁 Output Directory: outputs/fullworkflow/")
            phase_lines.append(f"   📝 Filename: {output_file}")
            phase_lines.append(f"   💾 File Content: Complete processing results, research validation, prep guide, citations")
            phase_lines.append(f"   ⏱️ Processing Time: {result.get('processing_time', 0):.2f}s")
            phase_lines.append(f"   ✅ Status: COMPLETED")
            phase_lines.append("")
            
            # Processing Summary
            phase_lines.append("📊 PHASE PROCESSING SUMMARY")
            phase_lines.append(f"   🔍 Email Classification: ✅ COMPLETED")
            phase_lines.append(f"   🧩 Entity Extraction: ✅ COMPLETED")
            phase_lines.append(f"   🔬 Deep Research: {'✅ COMPLETED' if result.get('research_conducted') else '❌ FAILED'}")
            phase_lines.append(f"   🤔 Research Reflection: {'✅ COMPLETED' if result.get('reflection_completed') else '❌ SKIPPED'}")
            phase_lines.append(f"   🏷️ Company Keyword: ✅ COMPLETED")
            phase_lines.append(f"   📚 Prep Guide Generation: {'✅ COMPLETED' if result.get('prep_guide_generated') else '❌ FAILED'}")
            phase_lines.append(f"   💾 File Output: ✅ COMPLETED")
            phase_lines.append("")
            
            # Error Log
            errors = result.get('errors', [])
            if errors:
                phase_lines.append("❌ PROCESSING ERRORS ENCOUNTERED")
                for i, error in enumerate(errors, 1):
                    phase_lines.append(f"   {i}. {error}")
                phase_lines.append("")
            else:
                phase_lines.append("✅ NO PROCESSING ERRORS - ALL PHASES COMPLETED SUCCESSFULLY")
                phase_lines.append("")
            
            return "\n".join(phase_lines)
            
        except Exception as e:
            return f"❌ Error generating phase details: {str(e)}"
    
    def _deep_validate_company(self, sources: List[Dict], company: str) -> Dict[str, Any]:
        """Deep company validation with reasoning"""
        validated_sources = []
        validation_reasoning = []
        company_lower = company.lower()
        
        # Company validation criteria
        official_domain_found = False
        company_news_found = False
        careers_page_found = False
        about_page_found = False
        
        for source in sources:
            title = source.get('title', '').lower()
            content = source.get('content', '').lower()
            url = source.get('url', '').lower()
            
            relevance_score = 0
            evidence = []
            
            # Check for official company presence
            if company_lower in url and any(x in url for x in ['.com', '.org', '.net']):
                relevance_score += 5
                evidence.append("Official domain match")
                official_domain_found = True
            
            # Check for company name in title (strong indicator)
            if company_lower in title:
                relevance_score += 4
                evidence.append("Company name in title")
            
            # Check for business indicators
            business_indicators = ['company', 'business', 'corporation', 'inc', 'ltd', 'about us', 'careers', 'news']
            for indicator in business_indicators:
                if indicator in title or indicator in content:
                    relevance_score += 1
                    evidence.append(f"Business indicator: {indicator}")
                    
                    if indicator == 'careers':
                        careers_page_found = True
                    elif indicator in ['about us', 'about']:
                        about_page_found = True
                    elif indicator == 'news':
                        company_news_found = True
            
            # Include if relevance score is sufficient
            if relevance_score >= 3:
                validated_sources.append({
                    'source': source,
                    'relevance_score': relevance_score,
                    'evidence': evidence
                })
        
        # Build validation reasoning
        if official_domain_found:
            validation_reasoning.append("Found official company domain - HIGH confidence this is the correct company")
        if about_page_found:
            validation_reasoning.append("Found company about page - confirms company identity")
        if careers_page_found:
            validation_reasoning.append("Found careers page - indicates active hiring company")
        if company_news_found:
            validation_reasoning.append("Found recent company news - company is active and relevant")
        
        confidence_score = min(0.95, len(validated_sources) / max(1, len(sources)) * 0.7 + 0.3)
        
        # Boost confidence for strong indicators
        if official_domain_found:
            confidence_score = min(0.95, confidence_score + 0.2)
        if about_page_found and careers_page_found:
            confidence_score = min(0.95, confidence_score + 0.1)
        
        is_validated = len(validated_sources) >= 2 and confidence_score >= 0.6
        
        reasoning_text = " | ".join(validation_reasoning) if validation_reasoning else "Insufficient company validation evidence"
        
        return {
            'is_validated': is_validated,
            'validated_sources': validated_sources,
            'confidence_score': confidence_score,
            'validation_reasoning': reasoning_text,
            'official_domain_found': official_domain_found,
            'total_sources': len(sources)
        }
    
    def _deep_validate_role(self, sources: List[Dict], role: str, company: str, entities: Dict) -> Dict[str, Any]:
        """Deep role validation with context matching"""
        validated_sources = []
        validation_reasoning = []
        role_lower = role.lower()
        company_lower = company.lower()
        
        # Role validation criteria
        job_posting_found = False
        role_requirements_found = False
        company_role_match = False
        interview_info_found = False
        
        for source in sources:
            title = source.get('title', '').lower()
            content = source.get('content', '').lower()
            url = source.get('url', '').lower()
            
            relevance_score = 0
            evidence = []
            
            # Check for role and company co-occurrence (strong validation)
            if role_lower in title and company_lower in title:
                relevance_score += 5
                evidence.append("Role and company both in title")
                company_role_match = True
            elif role_lower in content and company_lower in content:
                relevance_score += 3
                evidence.append("Role and company both in content")
                company_role_match = True
            
            # Check for job-related indicators
            job_indicators = ['job', 'position', 'hiring', 'opportunity', 'career', 'requirements', 'qualifications']
            for indicator in job_indicators:
                if indicator in title:
                    relevance_score += 2
                    evidence.append(f"Job indicator in title: {indicator}")
                    if indicator in ['job', 'position', 'hiring']:
                        job_posting_found = True
                    elif indicator in ['requirements', 'qualifications']:
                        role_requirements_found = True
                elif indicator in content:
                    relevance_score += 1
                    evidence.append(f"Job indicator in content: {indicator}")
            
            # Check for interview-related content
            interview_indicators = ['interview', 'questions', 'process', 'assessment']
            for indicator in interview_indicators:
                if indicator in title or indicator in content:
                    relevance_score += 1
                    evidence.append(f"Interview indicator: {indicator}")
                    interview_info_found = True
            
            # Include if relevance score is sufficient
            if relevance_score >= 2:
                validated_sources.append({
                    'source': source,
                    'relevance_score': relevance_score,
                    'evidence': evidence
                })
        
        # Build validation reasoning
        if company_role_match:
            validation_reasoning.append(f"Found {role} role specifically at {company} - STRONG context match")
        if job_posting_found:
            validation_reasoning.append("Found active job postings - role is currently being hired")
        if role_requirements_found:
            validation_reasoning.append("Found role requirements - can prepare targeted responses")
        if interview_info_found:
            validation_reasoning.append("Found interview process info - valuable for preparation")
        
        confidence_score = min(0.95, len(validated_sources) / max(1, len(sources)) * 0.6 + 0.4)
        
        # Boost confidence for strong context matching
        if company_role_match:
            confidence_score = min(0.95, confidence_score + 0.25)
        if job_posting_found and role_requirements_found:
            confidence_score = min(0.95, confidence_score + 0.15)
        
        is_validated = len(validated_sources) >= 1 and confidence_score >= 0.5
        
        reasoning_text = " | ".join(validation_reasoning) if validation_reasoning else "Insufficient role validation evidence"
        
        return {
            'is_validated': is_validated,
            'validated_sources': validated_sources,
            'confidence_score': confidence_score,
            'validation_reasoning': reasoning_text,
            'company_role_match': company_role_match,
            'total_sources': len(sources)
        }
    
    def _deep_validate_person(self, sources: List[Dict], interviewer: str, company: str, role: str, entities: Dict) -> Dict[str, Any]:
        """CRITICAL: Deep person validation with email context matching and reasoning"""
        validated_sources = []
        validation_reasoning = []
        key_evidence = []
        
        interviewer_lower = interviewer.lower()
        company_lower = company.lower()
        role_lower = role.lower()
        
        # Person validation criteria
        linkedin_profile_found = False
        company_employee_confirmed = False
        role_related_person = False
        email_context_match = False
        
        # Extract keywords from original email for context matching
        email_keywords = []
        if 'email_content' in entities:
            email_content = str(entities['email_content']).lower()
            # Look for context clues in email
            context_indicators = ['manager', 'director', 'lead', 'senior', 'head', 'vp', 'ceo', 'cto', 'recruiter', 'hr']
            email_keywords = [indicator for indicator in context_indicators if indicator in email_content]
        
        for source in sources:
            title = source.get('title', '').lower()
            content = source.get('content', '').lower()
            url = source.get('url', '').lower()
            
            relevance_score = 0
            evidence = []
            
            # CRITICAL: LinkedIn profile validation (highest confidence)
            if 'linkedin.com' in url and interviewer_lower in url:
                relevance_score += 10
                evidence.append("LinkedIn profile URL match")
                linkedin_profile_found = True
                key_evidence.append("Found LinkedIn profile - STRONG person identification")
            
            # Name and company co-occurrence validation
            if interviewer_lower in title and company_lower in title:
                relevance_score += 8
                evidence.append("Name and company both in title")
                company_employee_confirmed = True
                key_evidence.append(f"Confirmed {interviewer} works at {company}")
            elif interviewer_lower in content and company_lower in content:
                relevance_score += 6
                evidence.append("Name and company both in content")
                company_employee_confirmed = True
            
            # Role-related person validation
            role_indicators = ['manager', 'director', 'lead', 'senior', 'head', 'vp', 'vice president']
            for indicator in role_indicators:
                if indicator in title or indicator in content:
                    relevance_score += 3
                    evidence.append(f"Role indicator: {indicator}")
                    role_related_person = True
                    
                    # Email context matching
                    if indicator in email_keywords:
                        relevance_score += 2
                        evidence.append(f"Email context match: {indicator}")
                        email_context_match = True
                        key_evidence.append(f"Role '{indicator}' matches email context - RIGHT PERSON")
            
            # Professional profile indicators
            profile_indicators = ['profile', 'about', 'bio', 'experience', 'background']
            for indicator in profile_indicators:
                if indicator in title:
                    relevance_score += 2
                    evidence.append(f"Profile indicator: {indicator}")
            
            # Include if relevance score is sufficient
            if relevance_score >= 4:
                validated_sources.append({
                    'source': source,
                    'relevance_score': relevance_score,
                    'evidence': evidence
                })
        
        # Build CRITICAL validation reasoning
        if linkedin_profile_found and company_employee_confirmed:
            validation_reasoning.append(f"CONFIRMED: {interviewer} LinkedIn profile shows employment at {company} - DEFINITIVE MATCH")
        elif linkedin_profile_found:
            validation_reasoning.append(f"Found {interviewer} LinkedIn profile - HIGH confidence person identification")
        elif company_employee_confirmed:
            validation_reasoning.append(f"Confirmed {interviewer} is employee at {company} through company sources")
        
        if email_context_match:
            validation_reasoning.append("Email context matches person's role - this is the RIGHT PERSON because role keywords align")
        
        if role_related_person and not email_context_match:
            validation_reasoning.append("Found person in leadership role at company - likely interviewer for this position")
        
        # Calculate confidence with heavy weighting for LinkedIn + company confirmation
        base_confidence = len(validated_sources) / max(1, len(sources)) * 0.5
        
        # Confidence boosters
        if linkedin_profile_found and company_employee_confirmed:
            base_confidence += 0.4  # Major boost for LinkedIn + company confirmation
        elif linkedin_profile_found:
            base_confidence += 0.3  # Significant boost for LinkedIn
        elif company_employee_confirmed:
            base_confidence += 0.2  # Moderate boost for company confirmation
        
        if email_context_match:
            base_confidence += 0.1  # Bonus for email context matching
        
        confidence_score = min(0.95, base_confidence)
        
        # Validation criteria: Need either LinkedIn profile OR company confirmation with decent confidence
        is_validated = (
            (linkedin_profile_found or company_employee_confirmed) and 
            len(validated_sources) >= 1 and 
            confidence_score >= 0.6
        )
        
        reasoning_text = " | ".join(validation_reasoning) if validation_reasoning else "Insufficient person identification evidence"
        key_evidence_text = " | ".join(key_evidence) if key_evidence else "No strong identifying evidence found"
        
        result = {
            'is_validated': is_validated,
            'validated_sources': validated_sources,
            'confidence_score': confidence_score,
            'validation_reasoning': reasoning_text,
            'key_evidence': key_evidence_text,
            'linkedin_profile_found': linkedin_profile_found,
            'company_employee_confirmed': company_employee_confirmed,
            'email_context_match': email_context_match,
            'total_sources': len(sources)
        }
        
        if not is_validated:
            result['evidence_gap'] = "Need LinkedIn profile or company employee confirmation with higher confidence"
        
        return result
    
    def _perform_cross_validation(self, research_data: Dict[str, Any], entities: Dict[str, Any]) -> Dict[str, Any]:
        """Perform cross-validation and reflection across all research phases"""
        reflections = []
        consistency_score = 0
        
        company_data = research_data.get('company_research', {})
        role_data = research_data.get('role_research', {})
        person_data = research_data.get('interviewer_research', {})
        
        # Reflection 1: Company-Role consistency
        if company_data.get('is_validated') and role_data.get('is_validated'):
            if role_data.get('company_role_match'):
                reflections.append("Company-Role CONSISTENCY: Role confirmed at this specific company ✅")
                consistency_score += 3
            else:
                reflections.append("Company-Role WARNING: Role not specifically linked to this company ⚠️")
                consistency_score += 1
        
        # Reflection 2: Person-Company consistency  
        if person_data.get('is_validated') and company_data.get('is_validated'):
            if person_data.get('company_employee_confirmed'):
                reflections.append("Person-Company CONSISTENCY: Interviewer confirmed as company employee ✅")
                consistency_score += 3
            else:
                reflections.append("Person-Company GAP: Could not confirm interviewer works at this company ⚠️")
                consistency_score += 1
        
        # Reflection 3: Email context alignment
        email_context_validated = person_data.get('email_context_match', False)
        if email_context_validated:
            reflections.append("Email Context ALIGNMENT: Person's role matches email keywords - RIGHT PERSON ✅")
            consistency_score += 2
        else:
            reflections.append("Email Context REVIEW: Limited alignment between person's role and email context")
        
        # Reflection 4: Overall research completeness
        validated_phases = sum([
            1 for data in [company_data, role_data, person_data] 
            if data.get('is_validated', False)
        ])
        
        if validated_phases == 3:
            reflections.append("Research COMPLETENESS: All 3 phases validated - COMPREHENSIVE research ✅")
            consistency_score += 3
        elif validated_phases == 2:
            reflections.append("Research COMPLETENESS: 2/3 phases validated - GOOD research coverage")
            consistency_score += 2
        else:
            reflections.append("Research COMPLETENESS: Limited validation - consider additional research")
            consistency_score += 1
        
        # Final reflection on prep guide readiness
        prep_guide_confidence = "HIGH" if consistency_score >= 8 else "MEDIUM" if consistency_score >= 5 else "LOW"
        reflections.append(f"PREP GUIDE READINESS: {prep_guide_confidence} confidence for personalized guide generation")
        
        return {
            'reflections': reflections,
            'consistency_score': consistency_score,
            'max_consistency_score': 11,
            'prep_guide_confidence': prep_guide_confidence
        }
    
    def _extract_email_keywords(self, entities: Dict[str, Any]) -> List[str]:
        """Extract keywords from email content for validation"""
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
                if isinstance(value, list):
                    keywords.extend([str(v).lower() for v in value if v])
                else:
                    keywords.append(str(value).lower())
        
        return list(set(keywords))  # Remove duplicates
    
    def _company_analysis_agent(self, company: str, email_keywords: List[str], citations_db: Dict, citation_counter: int) -> Dict[str, Any]:
        """Comprehensive Company Analysis Agent with Web Search, Financial Data, and Industry Analysis"""
        try:
            from shared.tavily_client import search_tavily
            
            print(f"   🤖 Company Analysis Agent: Analyzing '{company}'")
            thinking_log = []
            citations = []
            validated_sources = []
            
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
                results = cached_search_tavily(query, search_depth="advanced", max_results=3)
                identity_sources.extend(results)
            
            # Validate company identity with email keywords
            company_identity = self._validate_company_identity(identity_sources, company, email_keywords)
            thinking_log.append(f"Company identity validation: {company_identity['reasoning']}")
            
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
                results = cached_search_tavily(query, search_depth="basic", max_results=4)
                industry_sources.extend(results)
            
            # Analyze industry trends with citations
            industry_analysis = self._analyze_industry_trends(industry_sources, company, email_keywords, citations_db, citation_counter)
            thinking_log.extend(industry_analysis['thinking_log'])
            citations.extend(industry_analysis['citations'])
            
            # Phase 3: Recent Developments & Financial Analysis
            print(f"   🔍 Phase 3: Recent Developments & Financial Analysis")
            financial_queries = [
                f"{company} recent news 2024 funding",
                f"{company} financial performance revenue",
                f"{company} growth strategy expansion",
                f"{company} partnerships acquisitions"
            ]
            
            financial_sources = []
            for query in financial_queries:
                results = cached_search_tavily(query, search_depth="basic", max_results=3)
                financial_sources.extend(results)
            
            # Analyze financial and strategic developments
            financial_analysis = self._analyze_financial_developments(financial_sources, company, citations_db, citation_counter + len(citations))
            thinking_log.extend(financial_analysis['thinking_log'])
            citations.extend(financial_analysis['citations'])
            
            # Compile validated sources with detailed information
            all_sources = identity_sources + industry_sources + financial_sources
            validated_sources = []
            for source in all_sources:
                if self._is_source_relevant(source, company, email_keywords):
                    # Create detailed source data with evidence and confidence
                    evidence_reasons = []
                    relevance_score = 5.0  # Default base score
                    
                    # Check for company mentions
                    if company.lower() in source.get('content', '').lower():
                        evidence_reasons.append(f"Company '{company}' mentioned")
                        relevance_score += 2.0
                    
                    # Check for keyword matches  
                    content_lower = source.get('content', '').lower()
                    for keyword in email_keywords:
                        if keyword.lower() in content_lower:
                            evidence_reasons.append(f"Email keyword '{keyword}' found")
                            relevance_score += 1.0
                    
                    # Check URL reliability
                    url = source.get('url', '')
                    if any(domain in url for domain in ['linkedin.com', 'crunchbase.com', 'bloomberg.com', 'reuters.com']):
                        evidence_reasons.append("High-authority domain")
                        relevance_score += 1.5
                    
                    # Check for financial/business indicators
                    if any(term in content_lower for term in ['revenue', 'funding', 'growth', 'market', 'industry']):
                        evidence_reasons.append("Business/financial content detected")
                        relevance_score += 1.0
                    
                    validated_sources.append({
                        'source': source,
                        'evidence': evidence_reasons,
                        'relevance_score': min(relevance_score, 10.0)  # Cap at 10
                    })
            
            # Sort by relevance score (highest first)
            validated_sources.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Calculate confidence score
            confidence_score = min(0.95, 
                (len(validated_sources) / max(1, len(all_sources)) * 0.6) +
                (company_identity['confidence'] * 0.2) +
                (industry_analysis['relevance_score'] * 0.2)
            )
            
            return {
                'success': True,
                'analysis_summary': f"Validated company identity and analyzed industry position with {len(citations)} citations",
                'industry_analysis': industry_analysis['summary'],
                'financial_insights': financial_analysis['summary'],
                'validated_sources': validated_sources,
                'sources_processed': len(all_sources),
                'confidence_score': confidence_score,
                'thinking_log': thinking_log,
                'citations': citations,
                'company_identity': company_identity
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'thinking_log': [f"Company analysis error: {str(e)}"]}
    
    def _role_analysis_agent(self, role: str, company: str, email_keywords: List[str], citations_db: Dict, citation_counter: int) -> Dict[str, Any]:
        """Comprehensive Role Analysis Agent with Job Market Tools and Skills Gap Analysis"""
        try:
            from shared.tavily_client import search_tavily
            
            print(f"   🤖 Role Analysis Agent: Analyzing '{role}' at '{company}'")
            thinking_log = []
            citations = []
            validated_sources = []
            
            # Phase 1: Role Definition & Requirements
            print(f"   🔍 Phase 1: Role Definition & Requirements Analysis")
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
            
            # Analyze role requirements
            role_requirements = self._analyze_role_requirements(role_sources, role, company, email_keywords)
            thinking_log.append(f"Role requirements analysis: {role_requirements['reasoning']}")
            
            # Phase 2: Skills Gap & Market Analysis
            print(f"   🔍 Phase 2: Skills Gap & Market Analysis")
            skills_queries = [
                f"{role} skills demand 2024 market trends",
                f"{role} salary range {company} industry",
                f"{role} career progression path",
                f"{role} technology stack tools required"
            ]
            
            skills_sources = []
            for query in skills_queries:
                results = cached_search_tavily(query, search_depth="basic", max_results=3)
                skills_sources.extend(results)
            
            # Perform skills gap analysis with citations
            skills_analysis = self._analyze_skills_gap(skills_sources, role, email_keywords, citations_db, citation_counter)
            thinking_log.extend(skills_analysis['thinking_log'])
            citations.extend(skills_analysis['citations'])
            
            # Phase 3: Interview Preparation Analysis
            print(f"   🔍 Phase 3: Interview Preparation Analysis")
            interview_queries = [
                f"{role} {company} interview process",
                f"{role} technical interview questions",
                f"{role} behavioral interview preparation",
                f"{company} interview culture process"
            ]
            
            interview_sources = []
            for query in interview_queries:
                results = cached_search_tavily(query, search_depth="basic", max_results=2)
                interview_sources.extend(results)
            
            # Analyze interview preparation needs
            interview_analysis = self._analyze_interview_preparation(interview_sources, role, company, citations_db, citation_counter + len(citations))
            thinking_log.extend(interview_analysis['thinking_log'])
            citations.extend(interview_analysis['citations'])
            
            # Compile and validate sources with detailed information
            all_sources = role_sources + skills_sources + interview_sources
            validated_sources = []
            for source in all_sources:
                if self._is_source_relevant(source, role, email_keywords + [company.lower()]):
                    # Create detailed source data with evidence and confidence
                    evidence_reasons = []
                    relevance_score = 5.0  # Default base score
                    
                    # Check for role mentions
                    content_lower = source.get('content', '').lower()
                    if role.lower() in content_lower:
                        evidence_reasons.append(f"Role '{role}' mentioned")
                        relevance_score += 2.0
                    
                    # Check for company mentions
                    if company.lower() in content_lower:
                        evidence_reasons.append(f"Company '{company}' mentioned")
                        relevance_score += 1.5
                    
                    # Check for keyword matches  
                    for keyword in email_keywords:
                        if keyword.lower() in content_lower:
                            evidence_reasons.append(f"Email keyword '{keyword}' found")
                            relevance_score += 1.0
                    
                    # Check for job-related indicators
                    if any(term in content_lower for term in ['skills', 'requirements', 'qualifications', 'interview', 'salary', 'career']):
                        evidence_reasons.append("Job-related content detected")
                        relevance_score += 1.0
                    
                    # Check URL reliability
                    url = source.get('url', '')
                    if any(domain in url for domain in ['linkedin.com', 'glassdoor.com', 'indeed.com', 'stackoverflow.com']):
                        evidence_reasons.append("Job/career-focused domain")
                        relevance_score += 1.5
                    
                    validated_sources.append({
                        'source': source,
                        'evidence': evidence_reasons,
                        'relevance_score': min(relevance_score, 10.0)  # Cap at 10
                    })
            
            # Sort by relevance score (highest first)
            validated_sources.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Calculate confidence score
            confidence_score = min(0.95,
                (len(validated_sources) / max(1, len(all_sources)) * 0.5) +
                (role_requirements['confidence'] * 0.25) +
                (skills_analysis['relevance_score'] * 0.25)
            )
            
            return {
                'success': True,
                'analysis_summary': f"Analyzed role requirements and skills gap with {len(citations)} citations",
                'skills_analysis': skills_analysis['summary'],
                'interview_preparation': interview_analysis['summary'],
                'validated_sources': validated_sources,
                'sources_processed': len(all_sources),
                'confidence_score': confidence_score,
                'thinking_log': thinking_log,
                'citations': citations,
                'role_requirements': role_requirements
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'thinking_log': [f"Role analysis error: {str(e)}"]}
    
    def _interviewer_analysis_agent(self, interviewer: str, company: str, email_keywords: List[str], citations_db: Dict, citation_counter: int) -> Dict[str, Any]:
        """Advanced Interviewer Analysis Agent with LinkedIn Focus and Iterative Name Resolution"""
        try:
            from shared.tavily_client import search_tavily
            
            print(f"   🤖 Interviewer Analysis Agent: Deep LinkedIn analysis for '{interviewer}'")
            thinking_log = []
            citations = []
            validated_sources = []
            linkedin_profiles_found = 0
            
            # Phase 1: Initial LinkedIn Discovery
            print(f"   🔍 Phase 1: Initial LinkedIn Profile Discovery")
            linkedin_queries = [
                f"{interviewer} {company} linkedin profile",
                f"{interviewer} linkedin {company}",
                f'"{interviewer}" linkedin profile',
                f"{interviewer} {company} employee linkedin"
            ]
            
            linkedin_sources = []
            for query in linkedin_queries:
                print(f"     🔍 LinkedIn Search: '{query}'")
                results = cached_search_tavily(query, search_depth="basic", max_results=4)
                linkedin_sources.extend(results)
                
                # Analyze each result for LinkedIn profile indicators
                for result in results:
                    if 'linkedin.com' in result.get('url', '').lower():
                        thinking_log.append(f"🔗 LinkedIn URL found: {result.get('url', '')} - analyzing for name match")
                        
                        # Extract potential full name from LinkedIn result
                        name_analysis = self._analyze_linkedin_name_extraction(result, interviewer, company, email_keywords)
                        if name_analysis['name_match_confidence'] > 0.7:
                            linkedin_profiles_found += 1
                            thinking_log.append(f"✅ HIGH CONFIDENCE LinkedIn match: {name_analysis['reasoning']}")
                            
                            # If we found a full name, do additional research
                            if name_analysis['full_name']:
                                extended_research = self._perform_extended_name_research(name_analysis['full_name'], company, email_keywords, citations_db, citation_counter + len(citations))
                                thinking_log.extend(extended_research['thinking_log'])
                                citations.extend(extended_research['citations'])
                        else:
                            thinking_log.append(f"⚠️ Low confidence LinkedIn match: {name_analysis['reasoning']}")
            
            # Phase 2: Company Directory & Employee Research
            print(f"   🔍 Phase 2: Company Directory & Employee Research")
            employee_queries = [
                f"{interviewer} {company} employee directory team",
                f"{interviewer} {company} staff about page",
                f"{interviewer} {company} management team",
                f'"{interviewer}" {company} contact'
            ]
            
            employee_sources = []
            for query in employee_queries:
                results = cached_search_tavily(query, search_depth="basic", max_results=3)
                employee_sources.extend(results)
            
            # Validate employee presence with email keyword matching
            employee_validation = self._validate_employee_presence(employee_sources, interviewer, company, email_keywords)
            thinking_log.append(f"Employee validation: {employee_validation['reasoning']}")
            
            # Phase 3: Professional Background & Publications
            print(f"   🔍 Phase 3: Professional Background & Publication Analysis")
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
            
            # Analyze professional background with citations
            background_analysis = self._analyze_professional_background(background_sources, interviewer, company, email_keywords, citations_db, citation_counter + len(citations))
            thinking_log.extend(background_analysis['thinking_log'])
            citations.extend(background_analysis['citations'])
            
            # Compile and validate all sources with detailed LinkedIn-focused information
            all_sources = linkedin_sources + employee_sources + background_sources
            validated_sources = []
            for source in all_sources:
                if self._is_interviewer_source_relevant(source, interviewer, company, email_keywords):
                    # Create detailed source data with evidence and confidence
                    evidence_reasons = []
                    relevance_score = 5.0  # Default base score
                    
                    # Check for interviewer name mentions
                    content_lower = source.get('content', '').lower()
                    if interviewer.lower() in content_lower:
                        evidence_reasons.append(f"Original name match")
                        relevance_score += 2.5
                    
                    # Check for company mentions
                    if company.lower() in content_lower:
                        evidence_reasons.append(f"Company '{company}' mentioned")
                        relevance_score += 2.0
                    
                    # Check for email keyword matches  
                    for keyword in email_keywords:
                        if keyword.lower() in content_lower:
                            evidence_reasons.append(f"Email keyword '{keyword}' found")
                            relevance_score += 1.0
                    
                    # Special LinkedIn profile detection
                    url = source.get('url', '')
                    if 'linkedin.com' in url.lower():
                        evidence_reasons.append("LinkedIn profile source")
                        relevance_score += 3.0
                        if '/in/' in url:
                            evidence_reasons.append("LinkedIn personal profile")
                            relevance_score += 1.0
                        elif '/posts/' in url:
                            evidence_reasons.append("LinkedIn post/activity")
                            relevance_score += 0.5
                    
                    # Check for professional indicators
                    if any(term in content_lower for term in ['experience', 'background', 'role', 'position', 'team', 'manager']):
                        evidence_reasons.append("Professional background content")
                        relevance_score += 1.0
                    
                    # Check for current role indicators that might be wrong person
                    if any(term in content_lower for term in ['google', 'amazon', 'microsoft', 'meta']) and company.lower() not in ['google', 'amazon', 'microsoft', 'meta']:
                        evidence_reasons.append("Warning: Current role at big tech (might be wrong person)")
                        relevance_score -= 1.0
                    
                    validated_sources.append({
                        'source': source,
                        'evidence': evidence_reasons,
                        'relevance_score': min(relevance_score, 10.0)  # Cap at 10
                    })
            
            # Sort by relevance score (highest first)
            validated_sources.sort(key=lambda x: x['relevance_score'], reverse=True)
            
            # Advanced confidence calculation with LinkedIn weighting
            base_confidence = len(validated_sources) / max(1, len(all_sources)) * 0.4
            linkedin_boost = min(0.4, linkedin_profiles_found * 0.2)  # Up to 40% boost for LinkedIn
            email_match_boost = employee_validation['confidence'] * 0.2
            
            confidence_score = min(0.95, base_confidence + linkedin_boost + email_match_boost)
            
            # Generate comprehensive LinkedIn analysis summary
            linkedin_summary = f"Found {linkedin_profiles_found} LinkedIn profiles" if linkedin_profiles_found > 0 else "No verified LinkedIn profiles found"
            
            return {
                'success': True,
                'analysis_summary': f"Conducted LinkedIn-focused analysis with {len(citations)} citations and {linkedin_profiles_found} profiles found",
                'linkedin_analysis': linkedin_summary,
                'professional_background': background_analysis['summary'],
                'validated_sources': validated_sources,
                'sources_processed': len(all_sources),
                'linkedin_profiles_found': linkedin_profiles_found,
                'confidence_score': confidence_score,
                'thinking_log': thinking_log,
                'citations': citations,
                'employee_validation': employee_validation
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e), 'thinking_log': [f"Interviewer analysis error: {str(e)}"]}
    
    def _analyze_linkedin_name_extraction(self, linkedin_result: Dict, interviewer: str, company: str, email_keywords: List[str]) -> Dict[str, Any]:
        """Analyze LinkedIn result to extract full name and validate match"""
        title = linkedin_result.get('title', '').lower()
        content = linkedin_result.get('content', '').lower()
        url = linkedin_result.get('url', '').lower()
        
        interviewer_lower = interviewer.lower()
        company_lower = company.lower()
        
        reasoning = []
        full_name = ""
        
        # Extract potential full name from title (e.g., "John Smith's Post - LinkedIn")
        if "'s post" in title or "'s profile" in title:
            name_part = title.split("'s")[0].strip()
            if interviewer_lower in name_part:
                full_name = name_part.title()
                reasoning.append(f"Extracted full name '{full_name}' from LinkedIn title")
        
        # Check for company mentions
        company_match = company_lower in title or company_lower in content
        if company_match:
            reasoning.append(f"Company '{company}' mentioned in LinkedIn content - STRONG match indicator")
        
        # Check for email keyword alignment
        keyword_matches = sum(1 for keyword in email_keywords if keyword in content or keyword in title)
        if keyword_matches > 0:
            reasoning.append(f"Found {keyword_matches} email keywords in LinkedIn content - context alignment")
        
        # Calculate match confidence
        confidence = 0.0
        if interviewer_lower in title:
            confidence += 0.4
        if company_match:
            confidence += 0.3
        if keyword_matches > 0:
            confidence += min(0.3, keyword_matches * 0.1)
        
        return {
            'full_name': full_name,
            'name_match_confidence': confidence,
            'reasoning': " | ".join(reasoning) if reasoning else "Limited LinkedIn match indicators",
            'company_mentioned': company_match,
            'keyword_alignment': keyword_matches
        }
    
    def _perform_extended_name_research(self, full_name: str, company: str, email_keywords: List[str], citations_db: Dict, citation_counter: int) -> Dict[str, Any]:
        """Perform extended research with discovered full name"""
        try:
            from shared.tavily_client import search_tavily
            
            thinking_log = [f"🔍 Extended research with full name: '{full_name}'"]
            citations = []
            
            # Extended searches with full name
            extended_queries = [
                f'"{full_name}" {company} linkedin',
                f'"{full_name}" {company} employee',
                f'"{full_name}" {company} background experience',
                f'"{full_name}" {company} role position'
            ]
            
            for query in extended_queries:
                thinking_log.append(f"Extended search: '{query}'")
                results = cached_search_tavily(query, search_depth="basic", max_results=2)
                
                for result in results:
                    if self._is_source_relevant(result, full_name, email_keywords + [company.lower()]):
                        citation_id = citation_counter + len(citations) + 1
                        citations.append({
                            'id': citation_id, 
                            'source': f"{result.get('title', 'Unknown')} - {result.get('url', '')}",
                            'content_snippet': result.get('content', '')[:200] + "..."
                        })
                        thinking_log.append(f"✅ Added citation [{citation_id}] for extended name research")
            
            return {
                'thinking_log': thinking_log,
                'citations': citations,
                'sources_found': len(citations)
            }
            
        except Exception as e:
            return {'thinking_log': [f"Extended name research error: {str(e)}"], 'citations': []}
    
    def _sophisticated_reflection_analysis(self, research_data: Dict[str, Any], email_keywords: List[str], citations_db: Dict) -> Dict[str, Any]:
        """Sophisticated reflection analysis to determine research sufficiency"""
        quality_score = 0
        research_gaps = []
        quality_assessment = []
        
        # Analyze Company Research Quality
        company_analysis = research_data.get('company_analysis', {})
        if company_analysis.get('success') and company_analysis.get('confidence_score', 0) >= 0.7:
            quality_score += 3
            quality_assessment.append("Company analysis: HIGH quality with industry insights")
        else:
            quality_score += 1
            research_gaps.append("company_deep_analysis")
            quality_assessment.append("Company analysis: INSUFFICIENT - need industry trends and financial insights")
        
        # Analyze Role Research Quality  
        role_analysis = research_data.get('role_analysis', {})
        if role_analysis.get('success') and role_analysis.get('confidence_score', 0) >= 0.6:
            quality_score += 2
            quality_assessment.append("Role analysis: GOOD with skills gap analysis")
        else:
            quality_score += 1
            research_gaps.append("role_market_analysis")
            quality_assessment.append("Role analysis: INSUFFICIENT - need market trends and skills requirements")
        
        # Analyze Interviewer Research Quality
        interviewer_analysis = research_data.get('interviewer_analysis', {})
        linkedin_found = interviewer_analysis.get('linkedin_profiles_found', 0)
        if interviewer_analysis.get('success') and linkedin_found > 0:
            quality_score += 4
            quality_assessment.append(f"Interviewer analysis: EXCELLENT with {linkedin_found} LinkedIn profiles")
        elif interviewer_analysis.get('success'):
            quality_score += 2
            research_gaps.append("linkedin_discovery")
            quality_assessment.append("Interviewer analysis: PARTIAL - need LinkedIn profile discovery")
        else:
            quality_score += 1
            research_gaps.append("interviewer_deep_research")
            quality_assessment.append("Interviewer analysis: INSUFFICIENT - need comprehensive background research")
        
        # Citation Quality Check
        total_citations = sum(len(data.get('citations', [])) for data in research_data.values() if isinstance(data, dict))
        if total_citations >= 5:
            quality_score += 2
            quality_assessment.append(f"Citation quality: EXCELLENT with {total_citations} citations")
        elif total_citations >= 2:
            quality_score += 1
            quality_assessment.append(f"Citation quality: ADEQUATE with {total_citations} citations")
        else:
            research_gaps.append("citation_depth")
            quality_assessment.append("Citation quality: INSUFFICIENT - need more source citations")
        
        # Determine if research is sufficient (lowered from 8 to 5 to allow sophisticated research through)
        research_sufficient = quality_score >= 5
        
        return {
            'research_sufficient': research_sufficient,
            'quality_score': quality_score,
            'max_quality_score': 11,
            'quality_assessment': " | ".join(quality_assessment),
            'research_gaps': research_gaps
        }
    
    def _perform_additional_research(self, research_gaps: List[str], entities: Dict[str, Any], citations_db: Dict, citation_counter: int) -> Dict[str, Any]:
        """Perform additional targeted research based on identified gaps"""
        try:
            from shared.tavily_client import search_tavily
            
            thinking_log = [f"🔄 Performing additional research for gaps: {research_gaps}"]
            sources_found = 0
            citations_added = 0
            research_updates = {}
            
            company = entities.get('company', '')
            role = entities.get('role', '')
            interviewer = entities.get('interviewer', '')
            
            for gap in research_gaps:
                if gap == "company_deep_analysis" and company:
                    thinking_log.append(f"🏢 Additional company industry analysis for '{company}'")
                    additional_queries = [
                        f"{company} industry trends 2024 future outlook",
                        f"{company} competitive landscape market position",
                        f"{company} strategic initiatives growth plans"
                    ]
                    
                    for query in additional_queries:
                        results = cached_search_tavily(query, search_depth="advanced", max_results=2)
                        sources_found += len(results)
                        
                        for result in results:
                            citation_id = citation_counter + citations_added + 1
                            citations_added += 1
                            thinking_log.append(f"✅ Added citation [{citation_id}] for additional company analysis")
                
                elif gap == "linkedin_discovery" and interviewer:
                    thinking_log.append(f"🔗 Additional LinkedIn discovery for '{interviewer}'")
                    linkedin_queries = [
                        f'"{interviewer}" linkedin profile',
                        f"{interviewer} linkedin professional",
                        f"{interviewer} {company} linkedin employee"
                    ]
                    
                    for query in linkedin_queries:
                        results = cached_search_tavily(query, search_depth="basic", max_results=3)
                        sources_found += len(results)
                        
                        linkedin_sources = [r for r in results if 'linkedin.com' in r.get('url', '').lower()]
                        if linkedin_sources:
                            citation_id = citation_counter + citations_added + 1
                            citations_added += 1
                            thinking_log.append(f"🔗 Found additional LinkedIn source - citation [{citation_id}]")
            
            return {
                'sources_found': sources_found,
                'citations_added': citations_added,
                'research_updates': research_updates,
                'thinking_log': thinking_log
            }
            
        except Exception as e:
            return {
                'sources_found': 0,
                'citations_added': 0,
                'research_updates': {},
                'thinking_log': [f"Additional research error: {str(e)}"]
            }
    
    def _calculate_sophisticated_confidence(self, research_data: Dict[str, Any], validation_metrics: Dict[str, Any]) -> float:
        """Calculate sophisticated confidence score with multiple factors"""
        base_confidence = 0.0
        total_weight = 0.0
        
        # Company analysis weight (30%)
        company_analysis = research_data.get('company_analysis', {})
        if company_analysis.get('success'):
            base_confidence += company_analysis.get('confidence_score', 0) * 0.3
            total_weight += 0.3
        
        # Role analysis weight (25%)
        role_analysis = research_data.get('role_analysis', {})
        if role_analysis.get('success'):
            base_confidence += role_analysis.get('confidence_score', 0) * 0.25
            total_weight += 0.25
        
        # Interviewer analysis weight (35% - highest due to LinkedIn focus)
        interviewer_analysis = research_data.get('interviewer_analysis', {})
        if interviewer_analysis.get('success'):
            base_confidence += interviewer_analysis.get('confidence_score', 0) * 0.35
            total_weight += 0.35
        
        # Citation quality bonus (10%)
        citation_count = validation_metrics.get('citation_count', 0)
        citation_bonus = min(0.1, citation_count * 0.02)  # 2% per citation, max 10%
        
        # LinkedIn discovery bonus (5%)
        linkedin_bonus = min(0.05, validation_metrics.get('linkedin_profiles_found', 0) * 0.05)
        
        final_confidence = (base_confidence / max(total_weight, 0.1)) + citation_bonus + linkedin_bonus
        return min(0.95, final_confidence)
    
    # Helper validation methods
    def _validate_company_identity(self, sources: List[Dict], company: str, email_keywords: List[str]) -> Dict[str, Any]:
        official_sources = [s for s in sources if company.lower() in s.get('url', '').lower()]
        keyword_matches = sum(1 for s in sources for keyword in email_keywords if keyword in s.get('content', '').lower())
        
        confidence = min(0.9, (len(official_sources) * 0.3) + (keyword_matches * 0.05))
        reasoning = f"Found {len(official_sources)} official sources and {keyword_matches} keyword matches"
        
        return {'confidence': confidence, 'reasoning': reasoning, 'official_sources': len(official_sources)}
    
    def _analyze_industry_trends(self, sources: List[Dict], company: str, email_keywords: List[str], citations_db: Dict, citation_counter: int) -> Dict[str, Any]:
        thinking_log = []
        citations = []
        
        # Look for industry trend indicators
        trend_indicators = ['trend', 'growth', 'market', 'future', 'innovation', 'development']
        relevant_sources = []
        
        for source in sources:
            content = source.get('content', '').lower()
            title = source.get('title', '').lower()
            
            trend_matches = sum(1 for indicator in trend_indicators if indicator in content or indicator in title)
            if trend_matches > 0:
                relevant_sources.append(source)
                citation_id = citation_counter + len(citations) + 1
                citations.append({
                    'id': citation_id,
                    'source': f"{source.get('title', 'Unknown')} - {source.get('url', '')}",
                    'content_snippet': content[:200] + "..."
                })
                thinking_log.append(f"Industry trend source found with {trend_matches} indicators - citation [{citation_id}]")
        
        relevance_score = min(0.9, len(relevant_sources) / max(1, len(sources)))
        summary = f"Analyzed {len(relevant_sources)} industry trend sources with {len(citations)} citations"
        
        return {
            'thinking_log': thinking_log,
            'citations': citations,
            'relevance_score': relevance_score,
            'summary': summary
        }
    
    def _analyze_financial_developments(self, sources: List[Dict], company: str, citations_db: Dict, citation_counter: int) -> Dict[str, Any]:
        thinking_log = []
        citations = []
        
        financial_indicators = ['funding', 'revenue', 'investment', 'acquisition', 'partnership', 'growth']
        relevant_sources = []
        
        for source in sources:
            content = source.get('content', '').lower()
            financial_matches = sum(1 for indicator in financial_indicators if indicator in content)
            
            if financial_matches > 0:
                relevant_sources.append(source)
                citation_id = citation_counter + len(citations) + 1
                citations.append({
                    'id': citation_id,
                    'source': f"{source.get('title', 'Unknown')} - {source.get('url', '')}",
                    'content_snippet': content[:200] + "..."
                })
                thinking_log.append(f"Financial development found with {financial_matches} indicators - citation [{citation_id}]")
        
        summary = f"Analyzed {len(relevant_sources)} financial development sources"
        
        return {
            'thinking_log': thinking_log,
            'citations': citations,
            'summary': summary
        }
    
    def _is_source_relevant(self, source: Dict, target: str, keywords: List[str]) -> bool:
        """Check if source is relevant to target and keywords"""
        content = source.get('content', '').lower()
        title = source.get('title', '').lower()
        target_lower = target.lower()
        
        # Target must be present
        if target_lower not in content and target_lower not in title:
            return False
        
        # At least one keyword should match
        keyword_match = any(keyword in content or keyword in title for keyword in keywords)
        return keyword_match
    
    def _is_interviewer_source_relevant(self, source: Dict, interviewer: str, company: str, keywords: List[str]) -> bool:
        """Special relevance check for interviewer sources"""
        content = source.get('content', '').lower()
        title = source.get('title', '').lower()
        url = source.get('url', '').lower()
        
        interviewer_lower = interviewer.lower()
        company_lower = company.lower()
        
        # High relevance for LinkedIn sources
        if 'linkedin.com' in url and interviewer_lower in (content + title + url):
            return True
        
        # Must have interviewer name and either company or keywords
        has_interviewer = interviewer_lower in content or interviewer_lower in title
        has_context = company_lower in content or any(keyword in content for keyword in keywords)
        
        return has_interviewer and has_context
    
    def _analyze_role_requirements(self, sources: List[Dict], role: str, company: str, email_keywords: List[str]) -> Dict[str, Any]:
        """Analyze role requirements from sources"""
        requirement_indicators = ['requirements', 'qualifications', 'skills', 'experience', 'responsibilities']
        relevant_sources = 0
        total_matches = 0
        
        for source in sources:
            content = source.get('content', '').lower()
            title = source.get('title', '').lower()
            
            matches = sum(1 for indicator in requirement_indicators if indicator in content or indicator in title)
            if matches > 0:
                relevant_sources += 1
                total_matches += matches
        
        confidence = min(0.9, relevant_sources / max(1, len(sources)))
        reasoning = f"Found {relevant_sources} sources with role requirements and {total_matches} requirement indicators"
        
        return {'confidence': confidence, 'reasoning': reasoning, 'relevant_sources': relevant_sources}
    
    def _analyze_skills_gap(self, sources: List[Dict], role: str, email_keywords: List[str], citations_db: Dict, citation_counter: int) -> Dict[str, Any]:
        """Analyze skills gap with citations"""
        thinking_log = []
        citations = []
        
        skill_indicators = ['skills', 'technology', 'tools', 'programming', 'experience', 'expertise']
        
        for source in sources:
            content = source.get('content', '').lower()
            title = source.get('title', '').lower()
            
            skill_matches = sum(1 for indicator in skill_indicators if indicator in content or indicator in title)
            if skill_matches > 1:  # Require at least 2 skill indicators
                citation_id = citation_counter + len(citations) + 1
                citations.append({
                    'id': citation_id,
                    'source': f"{source.get('title', 'Unknown')} - {source.get('url', '')}",
                    'content_snippet': content[:200] + "..."
                })
                thinking_log.append(f"Skills analysis source with {skill_matches} indicators - citation [{citation_id}]")
        
        relevance_score = min(0.9, len(citations) / max(1, len(sources)))
        summary = f"Analyzed skills requirements with {len(citations)} citations"
        
        return {
            'thinking_log': thinking_log,
            'citations': citations,
            'relevance_score': relevance_score,
            'summary': summary
        }
    
    def _analyze_interview_preparation(self, sources: List[Dict], role: str, company: str, citations_db: Dict, citation_counter: int) -> Dict[str, Any]:
        """Analyze interview preparation needs with citations"""
        thinking_log = []
        citations = []
        
        interview_indicators = ['interview', 'questions', 'process', 'preparation', 'assessment']
        
        for source in sources:
            content = source.get('content', '').lower()
            title = source.get('title', '').lower()
            
            interview_matches = sum(1 for indicator in interview_indicators if indicator in content or indicator in title)
            if interview_matches > 0:
                citation_id = citation_counter + len(citations) + 1
                citations.append({
                    'id': citation_id,
                    'source': f"{source.get('title', 'Unknown')} - {source.get('url', '')}",
                    'content_snippet': content[:200] + "..."
                })
                thinking_log.append(f"Interview preparation source with {interview_matches} indicators - citation [{citation_id}]")
        
        summary = f"Analyzed interview preparation with {len(citations)} citations"
        
        return {
            'thinking_log': thinking_log,
            'citations': citations,
            'summary': summary
        }
    
    def _validate_employee_presence(self, sources: List[Dict], interviewer: str, company: str, email_keywords: List[str]) -> Dict[str, Any]:
        """Validate employee presence in company sources"""
        interviewer_lower = interviewer.lower()
        company_lower = company.lower()
        
        employee_matches = 0
        context_matches = 0
        
        for source in sources:
            content = source.get('content', '').lower()
            title = source.get('title', '').lower()
            
            if interviewer_lower in content or interviewer_lower in title:
                employee_matches += 1
                
                # Check for context alignment
                if company_lower in content or any(keyword in content for keyword in email_keywords):
                    context_matches += 1
        
        confidence = min(0.9, (employee_matches * 0.3) + (context_matches * 0.2))
        reasoning = f"Found {employee_matches} employee mentions with {context_matches} context matches"
        
        return {'confidence': confidence, 'reasoning': reasoning, 'employee_matches': employee_matches}
    
    def _analyze_professional_background(self, sources: List[Dict], interviewer: str, company: str, email_keywords: List[str], citations_db: Dict, citation_counter: int) -> Dict[str, Any]:
        """Analyze professional background with citations"""
        thinking_log = []
        citations = []
        
        background_indicators = ['experience', 'background', 'expertise', 'publications', 'speaking', 'leadership']
        
        for source in sources:
            content = source.get('content', '').lower()
            title = source.get('title', '').lower()
            
            background_matches = sum(1 for indicator in background_indicators if indicator in content or indicator in title)
            if background_matches > 0:
                citation_id = citation_counter + len(citations) + 1
                citations.append({
                    'id': citation_id,
                    'source': f"{source.get('title', 'Unknown')} - {source.get('url', '')}",
                    'content_snippet': content[:200] + "..."
                })
                thinking_log.append(f"Professional background source with {background_matches} indicators - citation [{citation_id}]")
        
        summary = f"Analyzed professional background with {len(citations)} citations"
        
        return {
            'thinking_log': thinking_log,
            'citations': citations,
            'summary': summary
        }

    def _build_research_context_with_citations(self, research_data: Dict[str, Any]) -> str:
        """Build research context with citations for the prep guide"""
        try:
            context_parts = []
            citation_index = 1
            
            for research_type, research_info in research_data.items():
                if research_info and isinstance(research_info, dict):
                    data = research_info.get('data', [])
                    validation = research_info.get('validation', {})
                    
                    if data and validation.get('relevant_sources'):
                        context_parts.append(f"\n**{research_type.replace('_', ' ').title()}:**")
                        
                        for source_info in validation['relevant_sources'][:3]:  # Top 3 sources
                            source = source_info.get('source', {})
                            title = source.get('title', 'Unknown Title')
                            url = source.get('url', 'No URL')
                            content = source.get('content', '')[:200] + '...'
                            
                            context_parts.append(f"[{citation_index}] {title}")
                            context_parts.append(f"   URL: {url}")
                            context_parts.append(f"   Summary: {content}")
                            citation_index += 1
            
            return '\n'.join(context_parts) if context_parts else "No research data available with citations."
            
        except Exception as e:
            return f"Error building research context: {str(e)}"
    
    def _display_final_summary(self, results: Dict[str, Any]):
        """Display final workflow summary with detailed pipeline execution status"""
        print(f"\n" + "=" * 80)
        print("🎉 INDIVIDUAL EMAIL WORKFLOW COMPLETED")
        print("=" * 80)
        
        print(f"📧 Total Emails Processed: {results['emails_processed']}")
        print(f"🎯 Interview Emails Found: {results['interviews_found']}")
        print(f"📚 Prep Guides Generated: {results['prep_guides_generated']}")
        print(f"⏱️  Total Processing Time: {results['processing_time']:.2f}s")
        
        # Display detailed pipeline execution summary
        print(f"\n📊 PIPELINE EXECUTION SUMMARY:")
        total_emails = results['emails_processed']
        interview_emails = results['interviews_found']
        
        # Calculate pipeline usage statistics
        entities_extracted = sum(1 for r in results.get('individual_results', []) if r.get('entities_extracted'))
        research_conducted = sum(1 for r in results.get('individual_results', []) if r.get('research_conducted'))
        reflections_done = sum(1 for r in results.get('individual_results', []) if r.get('reflection_completed'))
        guides_generated = results['prep_guides_generated']
        
        print(f"   🔍 Email Classification Pipeline: ✅ USED ({total_emails} emails classified)")
        print(f"   🧩 Entity Extraction Pipeline: {'✅ USED' if entities_extracted > 0 else '❌ NOT USED'} ({entities_extracted}/{interview_emails} interviews)")
        print(f"   🔬 Deep Research Pipeline: {'✅ USED' if research_conducted > 0 else '❌ NOT USED'} ({research_conducted}/{interview_emails} interviews)")
        print(f"   🤔 Research Reflection Pipeline: {'✅ USED' if reflections_done > 0 else '❌ NOT USED'} ({reflections_done}/{interview_emails} interviews)")
        print(f"   📚 Prep Guide Generation Pipeline: {'✅ USED' if guides_generated > 0 else '❌ NOT USED'} ({guides_generated}/{interview_emails} interviews)")
        print(f"   💾 File Output Pipeline: {'✅ USED' if guides_generated > 0 else '❌ NOT USED'} ({guides_generated} files saved)")
        
        if results['interviews_found'] > 0:
            print(f"\n📁 Individual output files saved in: {self.outputs_dir}/")
            successful_guides = 0
            for result in results['individual_results']:
                if result.get('prep_guide_generated'):
                    successful_guides += 1
                    company = result.get('company_keyword', 'Unknown')
                    filename = result.get('output_file', 'N/A')
                    print(f"   ✅ {company}: {filename}")
            
            success_rate = (successful_guides / results['interviews_found']) * 100 if results['interviews_found'] > 0 else 0
            print(f"\n📊 Success Rate: {success_rate:.1f}% ({successful_guides}/{results['interviews_found']})")
            
            # Show pipeline failure reasons if any
            if successful_guides < results['interviews_found']:
                print(f"\n⚠️  PIPELINE FAILURE ANALYSIS:")
                for i, result in enumerate(results['individual_results'], 1):
                    if not result.get('prep_guide_generated'):
                        print(f"   Email {i}: {result.get('failure_reason', 'Unknown failure')}")
        else:
            print(f"\nℹ️  No interview emails found - no prep guides generated")
            print(f"📋 Pipeline Status: Classification ran but found no interview emails")
        
        print("=" * 80)


# Main execution
if __name__ == "__main__":
    workflow = IndividualEmailWorkflow()
    results = workflow.run_complete_individual_workflow(max_emails=10)
    
    if results['success']:
        print(f"🎉 Workflow completed successfully!")
    else:
        print(f"❌ Workflow failed: {results.get('error', 'Unknown error')}")
