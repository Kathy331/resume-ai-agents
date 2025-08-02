"""
Deep Research Pipeline - Handles Tavily search, validation, and IPIA integration
Extracted from workflow_runner.py for better maintainability
"""

import os
import asyncio
from typing import Dict, Any, List
from datetime import datetime

# Import agents and modules
from agents.interview_prep_intelligence.agent import InterviewPrepIntelligenceAgent
from agents.interview_prep_intelligence.models import (
    DeepResearchInput, ResearchContext, UserProfile
)
from agents.memory_systems.shared_memory import SharedMemorySystem

# Import shared utilities
from shared.tavily_client import search_tavily
from shared.utils import get_logger

logger = get_logger(__name__)

class DeepResearchPipeline:
    """Handles deep research with Tavily search, validation loops, and IPIA integration"""
    
    def __init__(self):
        self.memory_system = SharedMemorySystem()
        self.ipia_agent = InterviewPrepIntelligenceAgent()
    
    def run_deep_research_pipeline(self, max_interviews: int = 10) -> Dict[str, Any]:
        """
        Enhanced Deep Research Pipeline with integrated IPIA and 3-phase validation system
        
        This pipeline:
        1. Fetches non-prepped interviews from memory (from email pipeline)
        2. Performs 3-phase validation (Source Discovery → Validation → Primary Selection)
        3. Conducts research with confidence scoring
        4. Integrates IPIA for comprehensive interview prep generation
        
        Args:
            max_interviews: Maximum number of interviews to process
            
        Returns:
            Comprehensive results including IPIA outputs and validation metrics
        """
        print(f"🚀 Enhanced Deep Research Pipeline with IPIA Integration")
        print("=" * 60)
        start_time = datetime.now()
        
        try:
            # Phase 1: Fetch non-prepped interviews from memory
            print("📋 Phase 1: Fetching Non-Prepped Interviews from Memory")
            
            # Get interviews that need research (not 'prepped' status)
            all_interviews = self.memory_system.get_all_interviews()
            non_prepped_interviews = [
                interview for interview in all_interviews 
                if interview.get('status', '').lower() not in ['prepped', 'completed', 'cancelled']
            ]
            
            if not non_prepped_interviews:
                print("✅ No interviews requiring research found in memory")
                return {
                    'success': True,
                    'message': 'No interviews requiring research',
                    'interviews_processed': 0,
                    'total_questions_generated': 0,
                    'processing_time': (datetime.now() - start_time).total_seconds()
                }
            
            # Limit to max_interviews
            interviews_to_process = non_prepped_interviews[:max_interviews]
            print(f"🎯 Found {len(non_prepped_interviews)} non-prepped interviews, processing {len(interviews_to_process)}")
            
            # Phase 2: Enhanced Research with 3-Phase Validation
            print(f"\n🔬 Phase 2: Enhanced Research with 3-Phase Validation")
            research_contexts = []
            validation_metrics = {
                'total_sources_discovered': 0,
                'total_sources_validated': 0,
                'company_validation_rate': 0,
                'role_validation_rate': 0,
                'interviewer_validation_rate': 0
            }
            
            for i, interview in enumerate(interviews_to_process, 1):
                print(f"\n📊 Processing Interview {i}/{len(interviews_to_process)}: {interview.get('company', 'Unknown')}")
                
                # Extract interview details
                company_name = interview.get('company', 'Unknown Company')
                role_title = interview.get('role', 'Unknown Role')
                interviewer_name = interview.get('interviewer', '')
                
                # Perform research with validation
                research_result = self._perform_validated_research(
                    company_name, role_title, interviewer_name
                )
                
                # Update validation metrics
                if 'validation_metrics' in research_result:
                    metrics = research_result['validation_metrics']
                    validation_metrics['total_sources_discovered'] += metrics.get('sources_discovered', 0)
                    validation_metrics['total_sources_validated'] += metrics.get('sources_validated', 0)
                
                # Create ResearchContext for IPIA
                research_context = ResearchContext(
                    interview_id=str(interview.get('id', f'interview_{i}')),  # Convert to string
                    company_name=company_name,
                    role_title=role_title,
                    interviewer_name=interviewer_name,
                    research_data=research_result.get('research_data', {}),
                    confidence_score=research_result.get('confidence_score', 0.0),
                    validation_passed=research_result.get('validation_passed', False)
                )
                
                research_contexts.append(research_context)
            
            # Calculate overall validation rates
            total_discovered = validation_metrics['total_sources_discovered']
            total_validated = validation_metrics['total_sources_validated']
            overall_validation_rate = (total_validated / total_discovered) if total_discovered > 0 else 0
            
            print(f"\n📊 Validation Summary:")
            print(f"   🔍 Total Sources Discovered: {total_discovered}")
            print(f"   ✅ Total Sources Validated: {total_validated}")
            print(f"   📈 Overall Validation Rate: {overall_validation_rate:.1%}")
            
            # Phase 3: IPIA Integration - Comprehensive Interview Prep Generation
            print(f"\n🧠 Phase 3: IPIA - Comprehensive Interview Prep Generation")
            
            # Create user profile (this could be enhanced to use real user data)
            user_profile = UserProfile(
                name="Candidate",
                experience_level="entry",
                skills=["Python", "Data Analysis", "Machine Learning"],
                interests=["AI", "Technology", "Innovation"]
            )
            
            # Create IPIA input
            deep_research_input = DeepResearchInput(
                research_contexts=research_contexts,
                user_profile=user_profile
            )
            
            # Run IPIA asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                ipia_result = loop.run_until_complete(
                    self.ipia_agent.process_research_contexts(deep_research_input)
                )
            finally:
                loop.close()
            
            # Update interview status in memory to 'prepped'
            for interview in interviews_to_process:
                self.memory_system.update_interview_status(
                    interview.get('id'), 
                    'prepped',
                    {'prep_generated_at': datetime.now().isoformat()}
                )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Prepare comprehensive results
            result = {
                'success': True,
                'interviews_processed': len(interviews_to_process),
                'total_questions_generated': ipia_result.total_questions_generated if ipia_result.success else 0,
                'avg_confidence_score': ipia_result.avg_confidence_score if ipia_result.success else 0.0,
                'overall_validation_rate': overall_validation_rate,
                'validation_metrics': validation_metrics,
                'ipia_success': ipia_result.success,
                'ipia_errors': ipia_result.errors if hasattr(ipia_result, 'errors') else [],
                'prep_summaries': ipia_result.prep_summaries if ipia_result.success else [],
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
            # Display results
            self._display_enhanced_pipeline_results(result)
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_result = {
                'success': False,
                'error': str(e),
                'interviews_processed': 0,
                'total_questions_generated': 0,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
            print(f"💥 Enhanced Deep Research Pipeline failed: {str(e)}")
            return error_result

    def _perform_validated_research(self, company_name: str, role_title: str, interviewer_name: str) -> Dict[str, Any]:
        """
        Perform research with 3-phase validation system
        
        Returns research data with validation metrics and confidence scoring
        """
        import time
        
        validation_metrics = {
            'sources_discovered': 0,
            'sources_validated': 0,
            'company_sources': 0,
            'role_sources': 0,
            'interviewer_sources': 0
        }
        
        research_data = {}
        confidence_scores = []
        
        try:
            # Phase 1: Source Discovery
            print(f"   🔍 Phase 1: Source Discovery")
            
            # Company research
            if company_name and company_name != 'Unknown Company':
                company_query = f"{company_name} company overview industry technology"
                print(f"   🔍 Company query: '{company_query}' (depth: advanced, max: 5)")
                company_results = search_tavily(company_query, search_depth="advanced", max_results=5)
                validation_metrics['sources_discovered'] += len(company_results)
                validation_metrics['company_sources'] = len(company_results)
                
                # Phase 2: Validate company sources
                validated_company = self._validate_company_source_relevance(company_results, company_name)
                if validated_company['is_relevant']:
                    validation_metrics['sources_validated'] += len(validated_company['relevant_sources'])
                    confidence_scores.append(validated_company['confidence_score'])
                    research_data['company_research'] = {
                        'data': company_results,
                        'validation': validated_company,
                        'confidence': validated_company['confidence_score']
                    }
                    print(f"   ✅ Company: {len(validated_company['relevant_sources'])}/{len(company_results)} sources validated")
                else:
                    print(f"   ❌ Company: Low relevance ({validated_company['confidence_score']:.2f})")
            
            # Role research
            if role_title and role_title != 'Unknown Role':
                role_query = f"{role_title} {company_name} job requirements skills responsibilities"
                role_results = search_tavily(role_query, search_depth="basic", max_results=4)
                validation_metrics['sources_discovered'] += len(role_results)
                validation_metrics['role_sources'] = len(role_results)
                
                # Phase 2: Validate role sources
                validated_role = self._validate_role_source_relevance(role_results, role_title, company_name)
                if validated_role['is_relevant']:
                    validation_metrics['sources_validated'] += len(validated_role['relevant_sources'])
                    confidence_scores.append(validated_role['confidence_score'])
                    research_data['role_research'] = {
                        'data': role_results,
                        'validation': validated_role,
                        'confidence': validated_role['confidence_score']
                    }
                    print(f"   ✅ Role: {len(validated_role['relevant_sources'])}/{len(role_results)} sources validated")
                else:
                    print(f"   ❌ Role: Low relevance ({validated_role['confidence_score']:.2f})")
            
            # Interviewer research (if available)
            if interviewer_name:
                interviewer_query = f"{interviewer_name} {company_name} LinkedIn profile"
                interviewer_results = search_tavily(interviewer_query, search_depth="basic", max_results=3)
                validation_metrics['sources_discovered'] += len(interviewer_results)
                validation_metrics['interviewer_sources'] = len(interviewer_results)
                
                # Phase 2: Validate interviewer sources (prioritize LinkedIn)
                validated_interviewer = self._validate_interviewer_sources(interviewer_results, interviewer_name)
                if validated_interviewer['linkedin_found'] or validated_interviewer['is_relevant']:
                    validation_metrics['sources_validated'] += len(validated_interviewer['relevant_sources'])
                    confidence_scores.append(validated_interviewer['confidence_score'])
                    research_data['interviewer_research'] = {
                        'data': interviewer_results,
                        'validation': validated_interviewer,
                        'confidence': validated_interviewer['confidence_score']
                    }
                    status = "LinkedIn found" if validated_interviewer['linkedin_found'] else "Relevant sources found"
                    print(f"   ✅ Interviewer: {status}")
                else:
                    print(f"   ❌ Interviewer: No relevant sources found")
            
            # Phase 3: Calculate overall confidence
            overall_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            validation_passed = overall_confidence >= 0.6  # 60% threshold
            
            return {
                'research_data': research_data,
                'confidence_score': overall_confidence,
                'validation_passed': validation_passed,
                'validation_metrics': validation_metrics
            }
            
        except Exception as e:
            print(f"   ❌ Research validation failed: {str(e)}")
            return {
                'research_data': {},
                'confidence_score': 0.0,
                'validation_passed': False,
                'validation_metrics': validation_metrics,
                'error': str(e)
            }

    def _validate_company_source_relevance(self, sources: list, company_name: str) -> Dict[str, Any]:
        """Validate company sources for relevance and quality"""
        relevant_sources = []
        company_lower = company_name.lower()
        
        for source in sources:
            title = source.get('title', '').lower()
            content = source.get('content', '').lower()
            
            # Check if company name appears in title or content
            if company_lower in title or company_lower in content:
                # Additional quality checks
                quality_indicators = ['about', 'company', 'overview', 'business', 'industry', 'careers']
                quality_score = sum(1 for indicator in quality_indicators if indicator in title or indicator in content)
                
                if quality_score >= 2:  # At least 2 quality indicators
                    relevant_sources.append({
                        'source': source,
                        'quality_score': quality_score,
                        'relevance_reason': f'Company name found with {quality_score} quality indicators'
                    })
        
        confidence_score = min(0.9, len(relevant_sources) / max(1, len(sources)) + 0.3)
        
        return {
            'is_relevant': len(relevant_sources) >= 2,  # At least 2 relevant sources
            'relevant_sources': relevant_sources,
            'confidence_score': confidence_score,
            'total_sources': len(sources)
        }

    def _validate_role_source_relevance(self, sources: list, role_title: str, company_name: str) -> Dict[str, Any]:
        """Validate role sources for relevance and quality"""
        relevant_sources = []
        role_keywords = role_title.lower().split()
        company_lower = company_name.lower()
        
        for source in sources:
            title = source.get('title', '').lower()
            content = source.get('content', '').lower()
            
            # Check for role keywords and company name
            role_matches = sum(1 for keyword in role_keywords if keyword in title or keyword in content)
            company_match = company_lower in title or company_lower in content
            
            if role_matches >= 1:  # At least one role keyword
                quality_indicators = ['job', 'position', 'role', 'requirements', 'skills', 'responsibilities', 'salary']
                quality_score = sum(1 for indicator in quality_indicators if indicator in title or indicator in content)
                
                relevance_score = role_matches + (1 if company_match else 0) + min(quality_score, 3)
                
                if relevance_score >= 2:
                    relevant_sources.append({
                        'source': source,
                        'relevance_score': relevance_score,
                        'role_matches': role_matches,
                        'company_match': company_match,
                        'quality_score': quality_score
                    })
        
        confidence_score = min(0.8, len(relevant_sources) / max(1, len(sources)) + 0.2)
        
        return {
            'is_relevant': len(relevant_sources) >= 1,  # At least 1 relevant source
            'relevant_sources': relevant_sources,
            'confidence_score': confidence_score,
            'total_sources': len(sources)
        }

    def _validate_interviewer_sources(self, sources: list, interviewer_name: str) -> Dict[str, Any]:
        """Validate interviewer sources with LinkedIn prioritization"""
        relevant_sources = []
        linkedin_found = False
        interviewer_lower = interviewer_name.lower()
        
        for source in sources:
            title = source.get('title', '').lower()
            url = source.get('url', '').lower()
            content = source.get('content', '').lower()
            
            # Check for LinkedIn profile
            if 'linkedin.com' in url and 'profile' in url:
                linkedin_found = True
                relevant_sources.append({
                    'source': source,
                    'type': 'linkedin_profile',
                    'priority': 'high',
                    'relevance_reason': 'LinkedIn profile found'
                })
            # Check if interviewer name appears
            elif interviewer_lower in title or interviewer_lower in content:
                professional_indicators = ['profile', 'about', 'experience', 'background', 'bio']
                quality_score = sum(1 for indicator in professional_indicators if indicator in title or indicator in content)
                
                if quality_score >= 1:
                    relevant_sources.append({
                        'source': source,
                        'type': 'professional_info',
                        'priority': 'medium',
                        'quality_score': quality_score
                    })
        
        # Higher confidence if LinkedIn found
        base_confidence = 0.8 if linkedin_found else 0.4
        confidence_score = min(0.9, base_confidence + (len(relevant_sources) * 0.1))
        
        return {
            'linkedin_found': linkedin_found,
            'is_relevant': len(relevant_sources) >= 1,
            'relevant_sources': relevant_sources,
            'confidence_score': confidence_score,
            'total_sources': len(sources)
        }

    def _display_enhanced_pipeline_results(self, result: Dict[str, Any]):
        """Display comprehensive results from enhanced pipeline with IPIA"""
        print(f"\n🎯 Enhanced Deep Research Pipeline Results")
        print("=" * 60)
        
        if result.get('success'):
            print(f"✅ Pipeline Status: SUCCESS")
            print(f"📊 Interviews Processed: {result.get('interviews_processed', 0)}")
            print(f"🧠 IPIA Status: {'SUCCESS' if result.get('ipia_success') else 'FAILED'}")
            print(f"❓ Total Questions Generated: {result.get('total_questions_generated', 0)}")
            print(f"📈 Average Confidence Score: {result.get('avg_confidence_score', 0):.2f}")
            print(f"✅ Overall Validation Rate: {result.get('overall_validation_rate', 0):.1%}")
            print(f"⏱️  Total Processing Time: {result.get('processing_time', 0):.2f}s")
            
            # Display validation metrics
            validation_metrics = result.get('validation_metrics', {})
            if validation_metrics:
                print(f"\n📊 Validation Metrics:")
                print(f"   🔍 Sources Discovered: {validation_metrics.get('total_sources_discovered', 0)}")
                print(f"   ✅ Sources Validated: {validation_metrics.get('total_sources_validated', 0)}")
            
            # Display prep summaries overview
            prep_summaries = result.get('prep_summaries', [])
            if prep_summaries:
                print(f"\n📝 Interview Prep Summaries Generated:")
                for i, summary in enumerate(prep_summaries, 1):
                    company = getattr(summary, 'company_name', 'Unknown Company') if hasattr(summary, 'company_name') else 'Unknown Company'
                    questions = getattr(summary, 'total_questions', 0) if hasattr(summary, 'total_questions') else 0
                    confidence = getattr(summary, 'confidence_score', 0) if hasattr(summary, 'confidence_score') else 0
                    print(f"   {i}. {company}: {questions} questions (confidence: {confidence:.2f})")
            
            # Display any errors
            errors = result.get('ipia_errors', [])
            if errors:
                print(f"\n⚠️ IPIA Errors ({len(errors)}):")
                for error in errors[:3]:  # Show first 3 errors
                    print(f"   - {error}")
        else:
            print(f"❌ Pipeline Status: FAILED")
            print(f"💥 Error: {result.get('error', 'Unknown error')}")
            print(f"⏱️  Processing Time: {result.get('processing_time', 0):.2f}s")
        
        print("=" * 60)
