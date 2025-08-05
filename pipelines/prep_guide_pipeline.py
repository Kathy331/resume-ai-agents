#pipelines/prep_guide_pipeline.py
"""
Prep Guide Pipeline - Personalized Interview Preparation Guide Generation
========================================================================
Handles:
1. Personalized "Before the Interview" sections with specific email details
2. Technical Prep sections based on role analysis
3. Personalized interviewer background from LinkedIn research
4. Validated links and citations from research
5. Personalized questions to ask the interviewer
6. Strategic recommendations with citations
7. Terminal display of prep guide content
8. Individual file storage with company-specific naming
"""

import asyncio
import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.llm_client import call_llm
from agents.keyword_extractor.agent_email import EmailKeywordExtractor


class PrepGuidePipeline:
    """
    Prep Guide Pipeline: Generate personalized interview preparation guides
    """
    
    def __init__(self):
        self.keyword_extractor = EmailKeywordExtractor()
        # Create output directory
        self.outputs_dir = "outputs/fullworkflow"
        os.makedirs(self.outputs_dir, exist_ok=True)
    
    def generate_prep_guide(self, email: Dict[str, Any], entities: Dict[str, Any], research_result: Dict[str, Any], email_index: int, processing_logs: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Generate comprehensive personalized prep guide with detailed processing logs
        
        Args:
            email: Original email data
            entities: Extracted entities from email
            research_result: Results from deep research pipeline
            email_index: Index of email being processed
            processing_logs: Detailed logs from all pipeline stages
            
        Returns:
            Prep guide generation result
        """
        print(f"\n📚 PREP GUIDE PIPELINE - Email {email_index}")
        print("=" * 60)
        
        prep_start_time = datetime.now()
        
        result = {
            'success': False,
            'prep_guide_content': '',
            'company_keyword': '',
            'output_file': '',
            'citations_used': 0,
            'sections_generated': [],
            'processing_time': 0,
            'errors': []
        }
        
        try:
            # Extract company keyword for file naming
            print(f"🏷️ Step 1: Extract Company Keyword")
            company_keyword = self._extract_company_keyword(email)
            result['company_keyword'] = company_keyword
            print(f"   🏢 Company Keyword: {company_keyword}")
            
            # Check research sufficiency
            if not research_result.get('sufficient_for_prep_guide', False):
                result['errors'].append("Research insufficient for prep guide generation")
                print(f"❌ Research insufficient for prep guide generation")
                return result
            
            # Generate comprehensive prep guide
            print(f"\n📝 Step 2: Generate Personalized Prep Guide") 
            prep_guide_result = self._generate_comprehensive_prep_guide(email, entities, research_result)
            
            if not prep_guide_result.get('success'):
                result['errors'].append(f"Prep guide generation failed: {prep_guide_result.get('error', 'Unknown')}")
                return result
            
            result['prep_guide_content'] = prep_guide_result['prep_guide_content']
            result['citations_used'] = prep_guide_result['citations_used']
            result['sections_generated'] = prep_guide_result['sections_generated']
            
            # Display prep guide in terminal
            print(f"\n📺 Step 3: Display Prep Guide in Terminal")
            self._display_prep_guide_in_terminal(result['prep_guide_content'], company_keyword, result['citations_used'])
            
            # Save to individual file
            print(f"\n💾 Step 4: Save Individual Output File")
            output_result = self._save_individual_output_file(email, entities, result['prep_guide_content'], company_keyword, research_result, processing_logs or {})
            
            if output_result.get('success'):
                result['output_file'] = output_result['filename']
                print(f"   📁 Saved: {result['output_file']}")
            else:
                result['errors'].append(f"File save failed: {output_result.get('error', 'Unknown')}")
            
            result['success'] = True
            result['processing_time'] = (datetime.now() - prep_start_time).total_seconds()
            
            print(f"\n✅ PREP GUIDE PIPELINE COMPLETED")
            print(f"   🏢 Company: {company_keyword}")
            sections_gen = result['sections_generated']
            sections_count = len(sections_gen) if isinstance(sections_gen, list) else sections_gen
            print(f"   📚 Sections: {sections_count}")
            print(f"   📝 Citations: {result['citations_used']}")
            print(f"   📁 Output: {result['output_file']}")
            print(f"   ⏱️  Processing Time: {result['processing_time']:.2f}s")
            
            return result
            
        except Exception as e:
            result['errors'].append(str(e))
            result['processing_time'] = (datetime.now() - prep_start_time).total_seconds()
            print(f"❌ PREP GUIDE PIPELINE ERROR: {str(e)}")
            return result
    
    def _extract_company_keyword(self, email: Dict[str, Any]) -> str:
        """Extract company keyword using EmailKeywordExtractor"""
        try:
            keyword = self.keyword_extractor.extract_keyword_from_email(email)
            return keyword if keyword else "Unknown_Company"
        except Exception as e:
            print(f"   ❌ Keyword extraction error: {str(e)}")
            return "Unknown_Company"
    
    def _generate_comprehensive_prep_guide(self, email: Dict[str, Any], entities: Dict[str, Any], research_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive personalized prep guide with intelligent analysis and reflection loops"""
        try:
            # Extract entity values (handle both string and list formats)
            def get_entity_string(entity_value):
                if isinstance(entity_value, list):
                    return entity_value[0] if entity_value else ''
                return str(entity_value) if entity_value else ''
            
            company = get_entity_string(entities.get('company', 'Unknown Company'))
            role = get_entity_string(entities.get('role', 'Unknown Role'))
            interviewer = get_entity_string(entities.get('interviewer', 'Unknown Interviewer'))
            dates = entities.get('date', [])
            format_type = get_entity_string(entities.get('format', 'Unknown Format'))
            
            # Extract specific email details
            email_subject = email.get('subject', '')
            email_body = email.get('body', '')
            from_sender = email.get('from', '')
            
            # Build research context with detailed analysis
            research_context = self._build_research_context_with_citations(research_result)
            citations_database = research_result.get('citations_database', {})
            
            print(f"   🧠 Starting intelligent prep guide generation with reflection...")
            
            # PHASE 1: Generate Deep Insights from Research Data
            insights_result = self._generate_deep_insights(research_result, company, role, interviewer)
            
            # PHASE 2: Create Personalized Interviewer Profile 
            interviewer_profile = self._create_detailed_interviewer_profile(research_result, company, interviewer)
            
            # PHASE 3: Extract Conversation Hooks and Rapport Points
            conversation_hooks = self._extract_conversation_hooks(research_result, company, interviewer)
            
            # PHASE 4: Generate Highly Personalized Questions
            personalized_questions = self._generate_personalized_questions(research_result, company, role, interviewer)
            
            # PHASE 5: Generate Additional Enhancements
            additional_enhancements = self._generate_additional_enhancements(email, entities, research_result, company, interviewer)
            
            # PHASE 6: Generate Dynamic Prep Guide with Reflection Loop
            prep_guide_result = self._generate_enhanced_prep_guide_with_all_features(
                email, entities, research_result, insights_result, interviewer_profile, 
                conversation_hooks, personalized_questions, additional_enhancements
            )
            
            if not prep_guide_result.get('success'):
                return prep_guide_result
            
            # Count sections and citations
            sections_generated = self._count_sections(prep_guide_result['prep_guide_content'])
            citations_used = len(citations_database)
            
            print(f"   ✅ Enhanced prep guide generated ({len(prep_guide_result['prep_guide_content'])} characters)")
            sections_count = len(sections_generated) if isinstance(sections_generated, list) else sections_generated
            print(f"   📚 Sections: {sections_count}")
            print(f"   📝 Citations: {citations_used}")
            print(f"   🎯 Insights Generated: {len(str(insights_result.get('insights', '')))}")
            print(f"   🤝 Conversation Hooks: {len(str(conversation_hooks.get('hooks', '')))}")
            print(f"   ❓ Personalized Questions: {len(str(personalized_questions.get('questions', '')))}")
            print(f"   🎁 Additional Features: {len(str(additional_enhancements.get('enhancements', '')))}")
            
            return {
                'success': True,
                'prep_guide_content': prep_guide_result['prep_guide_content'],
                'citations_used': citations_used,
                'sections_generated': sections_generated,
                'insights_generated': len(str(insights_result.get('insights', ''))),
                'conversation_hooks': len(str(conversation_hooks.get('hooks', ''))),
                'personalized_questions': len(str(personalized_questions.get('questions', ''))),
                'additional_features': len(str(additional_enhancements.get('enhancements', ''))),
                'reflection_iterations': prep_guide_result.get('reflection_iterations', 0)
            }
                
        except Exception as e:
            print(f"   ❌ Prep guide generation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_research_context_with_citations(self, research_result: Dict[str, Any]) -> str:
        """Build comprehensive research context with citations for prep guide"""
        context_parts = []
        research_data = research_result.get('research_data', {})
        
        # Company Analysis Context
        company_analysis = research_data.get('company_analysis', {})
        if company_analysis.get('success'):
            context_parts.append("**COMPANY RESEARCH FINDINGS:**")
            context_parts.append(f"Industry Analysis: {company_analysis.get('industry_analysis', 'Not available')}")
            context_parts.append(f"Company Analysis Summary: {company_analysis.get('analysis_summary', 'Not available')}")
            context_parts.append(f"Confidence Score: {company_analysis.get('confidence_score', 0):.2f}")
            
            # Add top company sources
            for i, source_data in enumerate(company_analysis.get('validated_sources', [])[:3], 1):
                source = source_data.get('source', {})
                context_parts.append(f"Company Source {i}: {source.get('title', 'Unknown')[:100]}...")
        
        # Role Analysis Context
        role_analysis = research_data.get('role_analysis', {})
        if role_analysis.get('success'):
            context_parts.append("\n**ROLE RESEARCH FINDINGS:**")
            context_parts.append(f"Skills Analysis: {role_analysis.get('skills_analysis', 'Not available')}")
            context_parts.append(f"Role Analysis Summary: {role_analysis.get('analysis_summary', 'Not available')}")
            context_parts.append(f"Confidence Score: {role_analysis.get('confidence_score', 0):.2f}")
            
            # Add top role sources
            for i, source_data in enumerate(role_analysis.get('validated_sources', [])[:2], 1):
                source = source_data.get('source', {})
                context_parts.append(f"Role Source {i}: {source.get('title', 'Unknown')[:100]}...")
        
        # Interviewer Analysis Context (LinkedIn Focus)
        interviewer_analysis = research_data.get('interviewer_analysis', {})
        if interviewer_analysis.get('success'):
            context_parts.append("\n**INTERVIEWER RESEARCH FINDINGS (LINKEDIN FOCUSED):**")
            context_parts.append(f"LinkedIn Analysis: {interviewer_analysis.get('linkedin_analysis', 'Not available')}")
            context_parts.append(f"LinkedIn Profiles Found: {interviewer_analysis.get('linkedin_profiles_found', 0)}")
            context_parts.append(f"Analysis Summary: {interviewer_analysis.get('analysis_summary', 'Not available')}")
            context_parts.append(f"Confidence Score: {interviewer_analysis.get('confidence_score', 0):.2f}")
            
            # Add top interviewer sources with LinkedIn priority
            linkedin_sources = [s for s in interviewer_analysis.get('validated_sources', []) 
                             if 'linkedin.com' in s.get('source', {}).get('url', '').lower()]
            other_sources = [s for s in interviewer_analysis.get('validated_sources', []) 
                           if 'linkedin.com' not in s.get('source', {}).get('url', '').lower()]
            
            for i, source_data in enumerate(linkedin_sources[:2], 1):
                source = source_data.get('source', {})
                context_parts.append(f"LinkedIn Source {i}: {source.get('title', 'Unknown')[:100]}...")
            
            for i, source_data in enumerate(other_sources[:1], 1):
                source = source_data.get('source', {})
                context_parts.append(f"Professional Source {i}: {source.get('title', 'Unknown')[:100]}...")
        
        # Research Quality Summary
        context_parts.append(f"\n**RESEARCH QUALITY SUMMARY:**")
        context_parts.append(f"Overall Confidence: {research_result.get('overall_confidence', 0):.2f}")
        context_parts.append(f"Research Quality: {research_result.get('research_quality', 'Unknown')}")
        context_parts.append(f"Total Citations Available: {len(research_result.get('citations_database', {}))}")
        context_parts.append(f"LinkedIn Profiles Found: {research_result.get('validation_metrics', {}).get('linkedin_profiles_found', 0)}")
        
        return "\n".join(context_parts)
    
    def _count_sections(self, prep_guide_content: str) -> List[str]:
        """Count sections in the generated prep guide"""
        sections = []
        section_headers = [
            "Before the Interview",
            "Company Analysis", 
            "Role Analysis",
            "Interviewer Background",
            "Questions to Ask",
            "Strategic Recommendations"
        ]
        
        for header in section_headers:
            if header in prep_guide_content:
                sections.append(header)
        
        return sections
    
    def _display_prep_guide_in_terminal(self, prep_guide_content: str, company_keyword: str, citations_count: int):
        """Display the complete prep guide in terminal with formatting"""
        print(f"\n" + "=" * 80)
        print(f"📚 PERSONALIZED INTERVIEW PREP GUIDE FOR {company_keyword.upper()}")
        print(f"🔍 Based on {citations_count} research citations")
        print(f"⏰ Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"=" * 80)
        
        # Display the prep guide content with proper formatting
        lines = prep_guide_content.split('\n')
        for line in lines:
            # Add extra spacing for major sections
            if line.startswith('**') and line.endswith('**'):
                print(f"\n{line}")
                print("-" * 50)
            elif line.startswith('*') or line.startswith('-'):
                print(f"  {line}")
            elif '[Citation' in line:
                print(f"    {line}")
            else:
                print(line)
        
        print(f"\n" + "=" * 80)
        print(f"📝 Prep guide displayed successfully")
        print(f"📊 Total characters: {len(prep_guide_content)}")
        print(f"📚 Citations referenced: {citations_count}")
        print(f"=" * 80)
    
    def _save_individual_output_file(self, email: Dict[str, Any], entities: Dict[str, Any], prep_guide_content: str, company_keyword: str, research_result: Dict[str, Any], processing_logs: Dict[str, Any]) -> Dict[str, Any]:
        """Save comprehensive output to individual company-specific file"""
        try:
            # Create safe filename
            safe_company_name = "".join(c for c in company_keyword if c.isalnum() or c in ('-', '_')).rstrip()
            if not safe_company_name:
                safe_company_name = "Unknown_Company"
            
            filename = f"{safe_company_name}.txt"
            filepath = os.path.join(self.outputs_dir, filename)
            
            # Generate comprehensive file content
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Build complete file content
            file_content = self._build_complete_file_content(
                email, entities, prep_guide_content, company_keyword, research_result, timestamp, processing_logs
            )
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            print(f"   📁 File saved: {filename}")
            print(f"   📊 File size: {len(file_content)} characters")
            
            return {
                'success': True,
                'filename': filename,
                'filepath': filepath,
                'file_size': len(file_content)
            }
            
        except Exception as e:
            print(f"   ❌ File save error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_complete_file_content(self, email: Dict[str, Any], entities: Dict[str, Any], prep_guide_content: str, company_keyword: str, research_result: Dict[str, Any], timestamp: str, processing_logs: Dict[str, Any]) -> str:
        """Build complete file content with all sections"""
        
        # Extract entity values for display
        def get_entity_string(entity_value):
            if isinstance(entity_value, list):
                return entity_value[0] if entity_value else 'Unknown'
            return str(entity_value) if entity_value else 'Unknown'
        
        company = get_entity_string(entities.get('company', 'Unknown'))
        role = get_entity_string(entities.get('role', 'Unknown'))
        interviewer = get_entity_string(entities.get('interviewer', 'Unknown'))
        
        content_parts = []
        
        # Header
        content_parts.append("=" * 80)
        content_parts.append("INDIVIDUAL EMAIL PROCESSING RESULTS")
        content_parts.append("=" * 80)
        content_parts.append(f"Company: {company_keyword}")
        content_parts.append(f"Generated: {timestamp}")
        content_parts.append(f"Processing Time: {research_result.get('processing_time', 0):.2f}s")
        content_parts.append("")
        content_parts.append("This file contains the complete results from processing a single interview email")
        content_parts.append("through the Interview Prep Workflow including Classification, Entity Extraction,")
        content_parts.append("Deep Research, and Personalized Prep Guide generation.")
        
        # Original Email Data
        content_parts.append("\n" + "=" * 80)
        content_parts.append("ORIGINAL EMAIL DATA")
        content_parts.append("=" * 80)
        content_parts.append(f"From: {email.get('from', 'Unknown')}")
        content_parts.append(f"Subject: {email.get('subject', 'No subject')}")
        content_parts.append(f"Date: {email.get('date', 'Unknown')}")
        content_parts.append(f"Body: {email.get('body', 'No body')[:500]}...")
        
        # Detailed Pipeline Processing Logs
        if processing_logs:
            content_parts.append(self._format_detailed_processing_logs(processing_logs))
        
        # Research Validation Process
        if research_result.get('validation_metrics'):
            content_parts.append(self._format_research_validation_section(research_result))
        
        # Processing Results Summary
        content_parts.append("\n" + "=" * 80)
        content_parts.append("PROCESSING RESULTS")
        content_parts.append("=" * 80)
        content_parts.append(f"Is Interview: True")
        content_parts.append(f"Classification: Interview Email")
        content_parts.append(f"Entities Extracted: True")
        content_parts.append(f"Research Conducted: True")
        content_parts.append(f"Research Quality Score: {research_result.get('overall_confidence', 0):.2f}")
        content_parts.append(f"Prep Guide Generated: True")
        
        # Comprehensive Interview Preparation Guide
        content_parts.append("\n" + "=" * 80)
        content_parts.append("COMPREHENSIVE INTERVIEW PREPARATION GUIDE")
        content_parts.append("=" * 80)
        content_parts.append(prep_guide_content)
        
        # Research Citations Database
        citations_database = research_result.get('citations_database', {})
        if citations_database:
            content_parts.append("\n" + "=" * 80)
            content_parts.append("RESEARCH CITATIONS DATABASE")
            content_parts.append("=" * 80)
            content_parts.append("Complete database of all research citations used in the preparation guide:")
            content_parts.append("")
            
            for citation_id, citation_data in citations_database.items():
                content_parts.append(f"📝 Citation [{citation_id}]: {citation_data.get('source', 'Unknown source')}")
            
            content_parts.append(f"\nTotal Citations: {len(citations_database)}")
        
        # Technical Metadata
        content_parts.append("\n" + "=" * 80)
        content_parts.append("TECHNICAL METADATA")
        content_parts.append("=" * 80)
        content_parts.append("Workflow Version: Interview Prep Workflow v1.0")
        content_parts.append("Pipeline Stages Completed:")
        content_parts.append("- ✅ Email Classification")
        content_parts.append("- ✅ Entity Extraction")
        content_parts.append("- ✅ Deep Research with Tavily")
        content_parts.append("- ✅ Research Quality Reflection")
        content_parts.append("- ✅ Prep Guide Generation")
        content_parts.append("- ✅ File Output")
        content_parts.append("")
        content_parts.append("Processing Errors: []")
        content_parts.append(f"Company Keyword: {company_keyword}")
        content_parts.append(f"Output File: {company_keyword}.txt")
        content_parts.append("")
        content_parts.append("Generated by Resume AI Agents - Interview Prep Workflow")
        content_parts.append("=" * 80)
        
        return "\n".join(content_parts)
    
    def _format_research_validation_section(self, research_result: Dict[str, Any]) -> str:
        """Format research validation section for output"""
        validation_parts = []
        
        validation_parts.append("\n" + "=" * 80)
        validation_parts.append("DETAILED RESEARCH VALIDATION PROCESS")
        validation_parts.append("=" * 80)
        
        metrics = research_result.get('validation_metrics', {})
        research_data = research_result.get('research_data', {})
        
        validation_parts.append("🧠 === SOPHISTICATED DEEP RESEARCH WITH ANALYSIS AGENTS ===")
        validation_parts.append(f"🔍 Total Sources Discovered: {metrics.get('sources_discovered', 0)}")
        validation_parts.append(f"✅ Sources Validated: {metrics.get('sources_validated', 0)}")
        validation_parts.append(f"📝 Citations Generated: {metrics.get('citation_count', 0)}")
        validation_parts.append(f"🔗 LinkedIn profiles found: {metrics.get('linkedin_profiles_found', 0)}")
        
        # Add agent-specific results
        for agent_name, agent_data in research_data.items():
            if agent_data.get('success'):
                validation_parts.append(f"\n{self._format_agent_results(agent_name, agent_data)}")
        
        return "\n".join(validation_parts)
    
    def _format_agent_results(self, agent_name: str, agent_data: Dict[str, Any]) -> str:
        """Format individual agent results"""
        agent_parts = []
        
        if agent_name == 'company_analysis':
            agent_parts.append("🏢 === COMPANY ANALYSIS AGENT ===")
        elif agent_name == 'role_analysis':
            agent_parts.append("💼 === ROLE ANALYSIS AGENT ===")
        elif agent_name == 'interviewer_analysis':
            agent_parts.append("👤 === INTERVIEWER ANALYSIS AGENT (LINKEDIN FOCUS) ===")
        
        agent_parts.append(f"✅ Analysis: {agent_data.get('analysis_summary', 'Not available')}")
        
        if agent_name == 'interviewer_analysis':
            agent_parts.append(f"🔗 LinkedIn Discovery: {agent_data.get('linkedin_analysis', 'Not available')}")
        
        agent_parts.append(f"📈 Confidence: {agent_data.get('confidence_score', 0):.2f}")
        
        return "\n".join(agent_parts)
    
    def _format_detailed_processing_logs(self, processing_logs: Dict[str, Any]) -> str:
        """Format detailed processing logs from all pipeline stages"""
        log_parts = []
        
        log_parts.append("\n" + "=" * 80)
        log_parts.append("DETAILED PIPELINE PROCESSING LOGS")
        log_parts.append("=" * 80)
        log_parts.append("Complete step-by-step processing details from terminal output:")
        log_parts.append("")
        
        # Email Pipeline Logs
        if 'email_pipeline' in processing_logs:
            email_logs = processing_logs['email_pipeline']
            log_parts.append("📧 === EMAIL PIPELINE PROCESSING ===")
            
            # Classification details
            if 'classification' in email_logs:
                classification_data = email_logs['classification']
                log_parts.append("🔍 STEP 1: Email Classification")
                log_parts.append(f"   📋 Classification Result: {classification_data.get('result', 'Unknown')}")
                log_parts.append(f"   📊 Confidence: {classification_data.get('confidence', 0):.2f}")
                if classification_data.get('reasoning'):
                    log_parts.append(f"   💭 Reasoning: {classification_data.get('reasoning')}")
                log_parts.append("")
            
            # Entity extraction details  
            if 'entity_extraction' in email_logs:
                entity_data = email_logs['entity_extraction']
                log_parts.append("🏷️  STEP 2: Entity Extraction")
                log_parts.append(f"   ✅ Success: {entity_data.get('success', False)}")
                if entity_data.get('entities'):
                    log_parts.append("   📋 Extracted Entities:")
                    for key, value in entity_data['entities'].items():
                        if isinstance(value, list):
                            log_parts.append(f"      • {key}: {value} (LIST)")
                        else:
                            log_parts.append(f"      • {key}: {value}")
                log_parts.append("")
            
            # Memory check details
            if 'memory_check' in email_logs:
                memory_data = email_logs['memory_check']
                log_parts.append("💾 STEP 3: Memory Store Check")
                log_parts.append(f"   🆕 Status: {memory_data.get('status', 'Unknown')}")
                log_parts.append(f"   ✅ Already Prepped: {memory_data.get('already_prepped', False)}")
                if memory_data.get('match_details'):
                    match_details = memory_data['match_details']
                    log_parts.append("   📋 Match Details:")
                    log_parts.append(f"      • Company: {match_details.get('matched_company', 'N/A')}")
                    log_parts.append(f"      • Role: {match_details.get('matched_role', 'N/A')}")
                    log_parts.append(f"      • Date: {match_details.get('prep_date', 'N/A')}")
                log_parts.append("")
        
        # Deep Research Pipeline Logs
        if 'deep_research' in processing_logs:
            research_logs = processing_logs['deep_research']
            log_parts.append("🔬 === DEEP RESEARCH PIPELINE PROCESSING ===")
            
            # Overall research metrics
            if 'metrics' in research_logs:
                metrics = research_logs['metrics']
                log_parts.append("📊 RESEARCH OVERVIEW:")
                log_parts.append(f"   🔍 Total Sources Discovered: {metrics.get('sources_discovered', 0)}")
                log_parts.append(f"   ✅ Sources Validated: {metrics.get('sources_validated', 0)}")
                log_parts.append(f"   📝 Citations Generated: {metrics.get('citations_generated', 0)}")
                log_parts.append(f"   🔗 LinkedIn Profiles Found: {metrics.get('linkedin_profiles_found', 0)}")
                log_parts.append(f"   ⏱️  Processing Time: {metrics.get('processing_time', 0):.1f}s")
                log_parts.append("")
            
            # Company analysis details
            if 'company_analysis' in research_logs:
                company_data = research_logs['company_analysis']
                log_parts.append("🏢 COMPANY ANALYSIS AGENT:")
                log_parts.append(f"   📊 Phase 1: Company Identity Verification")
                log_parts.append(f"   📊 Phase 2: Industry & Market Analysis")
                log_parts.append(f"   📈 Confidence Score: {company_data.get('confidence_score', 0):.2f}")
                log_parts.append(f"   ✅ Sources Validated: {company_data.get('sources_validated', 0)}")
                
                # Company validation reasoning
                if company_data.get('validation_log'):
                    log_parts.append("   📊 Company Validation Results:")
                    for validation_entry in company_data['validation_log'][:8]:  # Show top 8
                        log_parts.append(f"      {validation_entry}")
                log_parts.append("")
            
            # Role analysis details
            if 'role_analysis' in research_logs:
                role_data = research_logs['role_analysis'] 
                log_parts.append("💼 ROLE ANALYSIS AGENT:")
                log_parts.append(f"   🔍 Phase 1: Role Requirements Analysis")
                log_parts.append(f"   🔍 Phase 2: Skills & Market Analysis")
                log_parts.append(f"   📈 Confidence Score: {role_data.get('confidence_score', 0):.2f}")
                log_parts.append(f"   ✅ Sources Validated: {role_data.get('sources_validated', 0)}")
                log_parts.append("")
            
            # Interviewer analysis details
            if 'interviewer_analysis' in research_logs:
                interviewer_data = research_logs['interviewer_analysis']
                log_parts.append("👤 INTERVIEWER ANALYSIS AGENT:")
                log_parts.append(f"   🔍 Phase 1: Targeted LinkedIn Profile Search")
                log_parts.append(f"   🔍 Phase 2: Professional Background Research")
                log_parts.append(f"   📈 Confidence Score: {interviewer_data.get('confidence_score', 0):.2f}")
                log_parts.append(f"   🔗 LinkedIn Profiles Found: {interviewer_data.get('linkedin_profiles_found', 0)}")
                
                # LinkedIn search queries
                if interviewer_data.get('search_queries'):
                    log_parts.append("   🔍 Search Queries Used:")
                    for query in interviewer_data['search_queries'][:5]:  # Show top 5
                        log_parts.append(f"      • {query}")
                
                # Profile validation reasoning
                if interviewer_data.get('validation_log'):
                    log_parts.append("   📊 Profile Validation Results:")
                    for validation_entry in interviewer_data['validation_log'][:8]:  # Show top 8
                        log_parts.append(f"      {validation_entry}")
                
                # Name extraction results
                if interviewer_data.get('extracted_names'):
                    log_parts.append(f"   💡 Names Extracted: {', '.join(interviewer_data['extracted_names'][:3])}")
                
                # Search suggestions
                if interviewer_data.get('search_suggestions'):
                    log_parts.append("   🎯 Search Suggestions Generated:")
                    for suggestion in interviewer_data['search_suggestions'][:3]:
                        log_parts.append(f"      • {suggestion}")
                log_parts.append("")
            
            # Research quality reflection
            if 'quality_reflection' in research_logs:
                quality_data = research_logs['quality_reflection']
                log_parts.append("🤔 RESEARCH QUALITY REFLECTION:")
                log_parts.append(f"   📊 Overall Confidence: {quality_data.get('overall_confidence', 0):.2f}")
                log_parts.append(f"   🏆 Research Quality: {quality_data.get('quality_rating', 'Unknown')}")
                log_parts.append(f"   📚 Sufficient for Prep Guide: {quality_data.get('sufficient_for_prep_guide', False)}")
                if quality_data.get('reflection_reasoning'):
                    log_parts.append(f"   💭 Reasoning: {quality_data.get('reflection_reasoning')}")
                log_parts.append("")
        
        # Prep Guide Generation Logs
        if 'prep_guide_generation' in processing_logs:
            prep_logs = processing_logs['prep_guide_generation']
            log_parts.append("📚 === PREP GUIDE GENERATION ===")
            log_parts.append(f"   ✅ Success: {prep_logs.get('success', False)}")
            log_parts.append(f"   📝 Guide Length: {prep_logs.get('guide_length', 0)} characters")
            log_parts.append(f"   🔗 Citations Used: {prep_logs.get('citations_used', 0)}")
            if prep_logs.get('generation_time'):
                log_parts.append(f"   ⏱️  Generation Time: {prep_logs.get('generation_time', 0):.2f}s")
            log_parts.append("")
        
        return "\n".join(log_parts)

    def _generate_deep_insights(self, research_result: Dict[str, Any], company: str, role: str, interviewer: str) -> Dict[str, Any]:
        """Generate deep insights from research data using AI analysis"""
        try:
            research_data = research_result.get('research_data', {})
            confidence_scores = research_result.get('validation_metrics', {}).get('confidence_scores', [])
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            # Build comprehensive research summary for analysis
            research_summary = self._build_research_summary(research_data)
            
            insights_prompt = f"""
            Analyze the following research data and generate deep, actionable insights for interview preparation:
            
            **RESEARCH DATA SUMMARY:**
            {research_summary}
            
            **TARGET DETAILS:**
            - Company: {company}
            - Role: {role} 
            - Interviewer: {interviewer}
            - Average Confidence Score: {avg_confidence:.2f}
            
            Generate specific insights in these categories:
            
            1. **Company Strategy Insights** - What does this research reveal about their strategic direction?
            2. **Role-Specific Insights** - What unique aspects of this role can be inferred?
            3. **Interviewer Insights** - What can we learn about the interviewer's priorities and background?
            4. **Market Position Insights** - How is this company positioned in their market?
            5. **Technology Stack Insights** - What technologies and approaches do they prioritize?
            6. **Culture & Values Insights** - What does the research suggest about company culture?
            
            For each insight, provide:
            - The specific insight (1-2 sentences)
            - Supporting evidence from research
            - How to leverage this in the interview
            - Confidence level (High/Medium/Low)
            
            Focus on non-obvious, strategic insights that go beyond surface-level information.
            """
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                insights_response = loop.run_until_complete(call_llm(insights_prompt))
                return {
                    'success': True,
                    'insights': insights_response,
                    'confidence_score': avg_confidence
                }
            finally:
                loop.close()
                
        except Exception as e:
            print(f"   ⚠️ Insights generation error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _create_detailed_interviewer_profile(self, research_result: Dict[str, Any], company: str, interviewer: str) -> Dict[str, Any]:
        """Create a detailed interviewer profile with conversation hooks"""
        try:
            research_data = research_result.get('research_data', {})
            interviewer_data = research_data.get('interviewer_analysis', {})
            
            if not interviewer_data.get('success'):
                return {'success': False, 'error': 'No interviewer research data available'}
            
            # Extract interviewer research details
            linkedin_analysis = interviewer_data.get('linkedin_analysis', '')
            validated_sources = interviewer_data.get('validated_sources', [])
            linkedin_profiles_found = interviewer_data.get('linkedin_profiles_found', 0)
            
            profile_prompt = f"""
            Create a comprehensive interviewer profile based on research findings:
            
            **INTERVIEWER:** {interviewer}
            **COMPANY:** {company}
            **LINKEDIN PROFILES FOUND:** {linkedin_profiles_found}
            
            **RESEARCH FINDINGS:**
            {linkedin_analysis}
            
            **VALIDATED SOURCES:** {len(validated_sources)} sources found
            
            Create a detailed profile including:
            
            1. **Professional Summary** (2-3 sentences about their background and expertise)
            2. **Current Role & Responsibilities** (what they likely do at the company)
            3. **Professional Interests** (areas they seem passionate about)
            4. **Recent Activity** (any recent posts, achievements, or projects mentioned)
            5. **Communication Style** (inferred from their online presence)
            6. **Potential Connection Points** (topics that might resonate with them)
            7. **Interview Approach** (how they might conduct the interview based on their background)
            
            **CONFIDENCE ASSESSMENT:**
            - Profile Confidence: [High/Medium/Low] based on available data
            - Data Quality: [Strong/Moderate/Limited] based on research depth
            
            Be specific and actionable. If information is limited, clearly state that and focus on what can be reasonably inferred.
            """
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                profile_response = loop.run_until_complete(call_llm(profile_prompt))
                return {
                    'success': True,
                    'profile': profile_response,
                    'linkedin_profiles_found': linkedin_profiles_found,
                    'sources_count': len(validated_sources)
                }
            finally:
                loop.close()
                
        except Exception as e:
            print(f"   ⚠️ Interviewer profile generation error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _extract_conversation_hooks(self, research_result: Dict[str, Any], company: str, interviewer: str) -> Dict[str, Any]:
        """Extract specific conversation hooks and rapport points"""
        try:
            research_data = research_result.get('research_data', {})
            citations_database = research_result.get('citations_database', {})
            
            # Gather all validated sources for conversation hook analysis
            all_sources = []
            for analysis_type in ['company_analysis', 'role_analysis', 'interviewer_analysis']:
                analysis_data = research_data.get(analysis_type, {})
                if analysis_data.get('success'):
                    sources = analysis_data.get('validated_sources', [])
                    for source_data in sources[:3]:  # Top 3 from each category
                        source = source_data.get('source', {})
                        all_sources.append({
                            'title': source.get('title', ''),
                            'url': source.get('url', ''),
                            'content': source.get('content', '')[:500],  # First 500 chars
                            'type': analysis_type
                        })
            
            hooks_prompt = f"""
            Analyze these research sources to identify specific conversation hooks and rapport-building opportunities:
            
            **TARGET:**
            - Company: {company}
            - Interviewer: {interviewer}
            
            **RESEARCH SOURCES:**
            {chr(10).join([f"• {s['title'][:100]} ({s['type']})" for s in all_sources[:10]])}
            
            **AVAILABLE CITATIONS:** {len(citations_database)} citations
            
            Generate specific conversation hooks in these categories:
            
            1. **Recent Company News/Developments** - Specific recent events or announcements to reference
            2. **Industry Trends** - Current trends the company is involved in or affected by
            3. **Technology Discussions** - Specific tech stacks, tools, or approaches they use
            4. **Interviewer's Interests** - Specific topics the interviewer has shown interest in
            5. **Company Culture** - Cultural elements or values that could be discussion points
            6. **Career Growth** - Opportunities or paths that could be explored
            
            For each hook, provide:
            - The specific talking point
            - Why it's relevant to this company/interviewer
            - How to naturally bring it up in conversation
            - Which citation to reference (if applicable)
            
            Make each hook specific and actionable, not generic advice.
            """
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                hooks_response = loop.run_until_complete(call_llm(hooks_prompt))
                return {
                    'success': True,
                    'hooks': hooks_response,
                    'sources_analyzed': len(all_sources)
                }
            finally:
                loop.close()
                
        except Exception as e:
            print(f"   ⚠️ Conversation hooks generation error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _generate_personalized_questions(self, research_result: Dict[str, Any], company: str, role: str, interviewer: str) -> Dict[str, Any]:
        """Generate highly personalized questions based on specific research findings"""
        try:
            research_data = research_result.get('research_data', {})
            citations_database = research_result.get('citations_database', {})
            
            # Extract specific research insights for question generation
            company_analysis = research_data.get('company_analysis', {})
            interviewer_analysis = research_data.get('interviewer_analysis', {})
            
            # Build detailed context for question generation
            question_context = []
            
            # Company-specific insights
            if company_analysis.get('success'):
                question_context.append(f"Company Analysis: {company_analysis.get('analysis_summary', '')}")
                question_context.append(f"Industry Position: {company_analysis.get('industry_analysis', '')}")
            
            # Interviewer-specific insights
            if interviewer_analysis.get('success'):
                question_context.append(f"Interviewer Background: {interviewer_analysis.get('linkedin_analysis', '')}")
                question_context.append(f"LinkedIn Profiles Found: {interviewer_analysis.get('linkedin_profiles_found', 0)}")
            
            # Citation details for reference
            citation_details = []
            for citation_key, citation_data in citations_database.items():
                title = citation_data.get('title', '')[:100]
                url = citation_data.get('url', '')
                citation_details.append(f"Citation {citation_key}: {title} - {url}")
            
            questions_prompt = f"""
            Generate highly personalized, research-backed questions for this specific interview scenario:
            
            **INTERVIEW CONTEXT:**
            - Company: {company}
            - Role: {role}
            - Interviewer: {interviewer}
            
            **SPECIFIC RESEARCH INSIGHTS:**
            {chr(10).join(question_context)}
            
            **AVAILABLE CITATIONS FOR REFERENCE:**
            {chr(10).join(citation_details[:8])}  # Top 8 citations
            
            Generate 3 categories of questions:
            
            **1. COMPANY-SPECIFIC QUESTIONS** (5-7 questions)
            Based on specific research findings about {company}:
            - Questions about recent developments mentioned in research
            - Strategic direction questions based on market analysis
            - Technology/product questions based on findings
            - Culture/values questions based on company insights
            
            **2. INTERVIEWER-SPECIFIC QUESTIONS** (3-5 questions)  
            Based on {interviewer}'s background and interests:
            - Questions about their professional experience/expertise
            - Questions about their role and responsibilities
            - Questions about their perspective on industry trends
            - Questions that show you've researched their background
            
            **3. ROLE & GROWTH QUESTIONS** (4-6 questions)
            Based on the {role} position and company context:
            - Specific expectations for this role
            - Growth opportunities and career progression
            - Team dynamics and collaboration
            - Success metrics and performance evaluation
            
            **REQUIREMENTS:**
            - Each question should reference specific research findings when possible
            - Include the citation number [Citation X] where applicable
            - Make questions conversational, not interrogative
            - Ensure questions demonstrate genuine interest and research
            - Avoid generic questions that could apply to any company
            - Include follow-up question suggestions for deeper conversations
            
            **FORMAT:**
            For each question, provide:
            1. The question itself
            2. Why this question is relevant (based on research)
            3. Potential follow-up questions
            4. Citation reference if applicable
            """
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                questions_response = loop.run_until_complete(call_llm(questions_prompt))
                return {
                    'success': True,
                    'questions': questions_response,
                    'citations_used': len(citations_database)
                }
            finally:
                loop.close()
                
        except Exception as e:
            print(f"   ⚠️ Personalized questions generation error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _generate_additional_enhancements(self, email: Dict[str, Any], entities: Dict[str, Any], 
                                        research_result: Dict[str, Any], company: str, interviewer: str) -> Dict[str, Any]:
        """Generate additional enhancements like timeline, red flags, post-interview plan"""
        try:
            # Extract interview details
            dates = entities.get('date', [])
            format_type = entities.get('format', ['Unknown Format'])[0] if isinstance(entities.get('format'), list) else entities.get('format', 'Unknown Format')
            
            # Build enhancement context
            email_body = email.get('body', '')
            research_confidence = research_result.get('overall_confidence', 0.5)
            
            enhancements_prompt = f"""
            Generate additional interview preparation enhancements for this specific scenario:
            
            **INTERVIEW DETAILS:**
            - Company: {company}
            - Interviewer: {interviewer}
            - Dates: {', '.join(dates) if dates else 'Not specified'}
            - Format: {format_type}
            - Research Confidence: {research_confidence:.2f}
            
            **EMAIL CONTEXT:**
            {email_body[:1000]}  # First 1000 chars of email
            
            Generate these enhancement sections:
            
            **1. INTERVIEW TIMELINE & LOGISTICS**
            - Pre-interview checklist (24h, 2h, 30min before)
            - Technical setup for virtual interviews
            - What to bring/prepare
            - Backup plans for technical issues
            
            **2. RED FLAGS TO AVOID**
            - Topics/questions to avoid based on company research
            - Communication style mistakes
            - Cultural missteps based on company values
            - Technical or professional red flags
            
            **3. POST-INTERVIEW ACTION PLAN**
            - Thank you email template with specific references
            - Follow-up timeline and strategy
            - How to reference specific discussion points
            - Next steps and timeline expectations
            
            **4. KEY METRICS TO TRACK**
            - How to gauge interviewer interest
            - Positive signals to look for
            - Questions that indicate strong mutual fit
            - Warning signs about company/role
            
            **5. INDUSTRY-SPECIFIC TALKING POINTS**
            - Current industry trends relevant to this company
            - Competitive landscape insights
            - Future outlook and challenges
            - Innovation opportunities
            
            Make each section specific to this company and interview context, not generic advice.
            """
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                enhancements_response = loop.run_until_complete(call_llm(enhancements_prompt))
                return {
                    'success': True,
                    'enhancements': enhancements_response,
                    'research_confidence': research_confidence
                }
            finally:
                loop.close()
                
        except Exception as e:
            print(f"   ⚠️ Additional enhancements generation error: {str(e)}")
            return {'success': False, 'error': str(e)}

    def _generate_enhanced_prep_guide_with_all_features(self, email: Dict[str, Any], entities: Dict[str, Any], 
                                                      research_result: Dict[str, Any], insights_result: Dict[str, Any],
                                                      interviewer_profile: Dict[str, Any], conversation_hooks: Dict[str, Any],
                                                      personalized_questions: Dict[str, Any], additional_enhancements: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive prep guide with all enhanced features"""
        try:
            # Extract entity values
            def get_entity_string(entity_value):
                if isinstance(entity_value, list):
                    return entity_value[0] if entity_value else ''
                return str(entity_value) if entity_value else ''
            
            company = get_entity_string(entities.get('company', 'Unknown Company'))
            role = get_entity_string(entities.get('role', 'Unknown Role'))
            interviewer = get_entity_string(entities.get('interviewer', 'Unknown Interviewer'))
            dates = entities.get('date', [])
            format_type = get_entity_string(entities.get('format', 'Unknown Format'))
            
            # Email details
            email_subject = email.get('subject', '')
            from_sender = email.get('from', '')
            
            # Build comprehensive context
            research_context = self._build_research_context_with_citations(research_result)
            
            # Create the most comprehensive prompt yet
            enhanced_prompt = f"""
            Generate the most comprehensive and personalized interview preparation guide possible based on extensive research and analysis:
            
            **SPECIFIC INTERVIEW DETAILS:**
            From: {from_sender}
            Subject: {email_subject}
            Company: {company}
            Role: {role}
            Interviewer: {interviewer}
            Interview Dates: {', '.join(dates) if dates else 'Not specified'}
            Format: {format_type}
            
            **DEEP RESEARCH INSIGHTS:**
            {insights_result.get('insights', 'No deep insights available')}
            
            **DETAILED INTERVIEWER PROFILE:**
            {interviewer_profile.get('profile', 'Limited interviewer information available')}
            
            **CONVERSATION HOOKS & RAPPORT POINTS:**
            {conversation_hooks.get('hooks', 'No specific conversation hooks identified')}
            
            **HIGHLY PERSONALIZED QUESTIONS:**
            {personalized_questions.get('questions', 'No personalized questions available')}
            
            **ADDITIONAL ENHANCEMENTS:**
            {additional_enhancements.get('enhancements', 'No additional enhancements available')}
            
            **RESEARCH CONTEXT WITH CITATIONS:**
            {research_context}
            
            Create the ultimate interview preparation guide with these enhanced sections:
            
            **1. Before the Interview (Pre-Game Strategy)**
            - Specific response requirements from the email
            - Exact scheduling details and contact information
            - Pre-interview research tasks with priorities and timelines
            - Company-specific preparation points with citations
            - Technical setup and backup plans
            
            **2. Company Deep Dive (Strategic Intelligence)**
            - Strategic insights about their market position with evidence
            - Recent developments and their implications
            - Technology stack and approach analysis
            - Cultural insights and values alignment
            - Competitive landscape understanding
            
            **3. Role Analysis & Positioning (Perfect Fit Strategy)**
            - Role expectations based on research findings
            - Required skills with specific examples to highlight
            - Technical requirements and how to demonstrate competency
            - Growth opportunities and career progression
            - Success metrics and performance expectations
            
            **4. Interviewer Intelligence (Personal Connection)**
            - Professional background summary with confidence assessment
            - Communication style and likely interview approach
            - Specific interests and expertise areas
            - Connection points and rapport-building opportunities
            - Recent activities or achievements to reference
            
            **5. Personalized Questions to Ask (Show Your Research)**
            IMPORTANT: Include the specific detailed personalized questions from the "HIGHLY PERSONALIZED QUESTIONS" section above. 
            Do not summarize or paraphrase - include the actual questions with their research context, relevance explanations, and follow-up questions exactly as provided.
            
            **6. Conversation Hooks & Talking Points (Natural Flow)**
            - Recent company news to reference naturally
            - Industry trends to discuss knowledgeably
            - Technology topics for technical connection
            - Career growth discussions and future vision
            - Personal interest connections with interviewer
            
            **7. Interview Timeline & Logistics (Execution Plan)**
            - 24-hour countdown checklist
            - 2-hour pre-interview preparation
            - 30-minute final setup
            - During interview key points
            - Technical backup plans
            
            **8. Red Flags to Avoid (Risk Mitigation)**
            - Topics/questions to avoid based on company research
            - Communication style mistakes
            - Cultural missteps based on company values
            - Technical or professional pitfalls
            
            **9. Post-Interview Action Plan (Follow-Through)**
            - Thank you email template with specific references
            - Follow-up timeline and strategy
            - How to reference specific discussion points
            - Next steps and timeline expectations
            
            **10. Success Metrics & Evaluation (Real-Time Assessment)**
            - How to gauge interviewer interest during the conversation
            - Positive signals to look for
            - Questions that indicate strong mutual fit
            - Warning signs about company/role fit
            
            **QUALITY REQUIREMENTS:**
            - Include ALL detailed content from the sections above - do not summarize or paraphrase
            - Use the exact personalized questions, conversation hooks, and insights as provided
            - Every recommendation must be specific and actionable
            - Include confidence levels for different insights
            - Use citations [Citation X] for all factual claims
            - Make talking points naturally conversational
            - Ensure recommendations are immediately implementable
            - Highlight areas where research is strong vs. limited
            - Reference specific research findings throughout
            - CRITICAL: The personalized questions section should include the full detailed questions with research context
            
            **CITATION FORMAT:** Use [Citation X] where X matches the research database numbers
            """
            
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                prep_guide_content = loop.run_until_complete(call_llm(enhanced_prompt))
                
                # Evaluate quality
                quality_score = self._evaluate_prep_guide_quality(prep_guide_content, research_result)
                
                return {
                    'success': True,
                    'prep_guide_content': prep_guide_content,
                    'reflection_iterations': 1,
                    'final_quality_score': quality_score
                }
            finally:
                loop.close()
                
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def _evaluate_prep_guide_quality(self, prep_guide_content: str, research_result: Dict[str, Any]) -> float:
        """Evaluate the quality of generated prep guide"""
        try:
            quality_factors = []
            
            # Factor 1: Length and comprehensiveness
            length_score = min(len(prep_guide_content) / 5000, 1.0)  # Target ~5000 chars for enhanced guide
            quality_factors.append(length_score)
            
            # Factor 2: Citation usage
            citation_count = prep_guide_content.count('[Citation')
            expected_citations = len(research_result.get('citations_database', {}))
            citation_score = min(citation_count / max(expected_citations, 1), 1.0) if expected_citations > 0 else 0.5
            quality_factors.append(citation_score)
            
            # Factor 3: Specific vs generic content
            specific_indicators = ['specific', 'recent', 'latest', 'current', 'noted', 'found', 'identified', 'particular']
            generic_indicators = ['general', 'typical', 'common', 'standard', 'basic', 'usual']
            
            specific_count = sum(prep_guide_content.lower().count(word) for word in specific_indicators)
            generic_count = sum(prep_guide_content.lower().count(word) for word in generic_indicators)
            
            specificity_score = min(specific_count / max(specific_count + generic_count, 1), 1.0)
            quality_factors.append(specificity_score)
            
            # Factor 4: Research confidence integration
            research_confidence = research_result.get('overall_confidence', 0.5)
            quality_factors.append(research_confidence)
            
            # Factor 5: Enhanced features presence
            enhanced_features = ['Timeline', 'Red Flags', 'Post-Interview', 'Questions to Ask', 'Conversation Hooks']
            features_count = sum(1 for feature in enhanced_features if feature.lower() in prep_guide_content.lower())
            features_score = features_count / len(enhanced_features)
            quality_factors.append(features_score)
            
            # Calculate overall quality score
            overall_quality = sum(quality_factors) / len(quality_factors)
            
            return overall_quality
            
        except Exception as e:
            print(f"   ⚠️ Quality evaluation error: {str(e)}")
            return 0.5

    def _build_research_summary(self, research_data: Dict[str, Any]) -> str:
        """Build a comprehensive research summary for insight generation"""
        summary_parts = []
        
        # Company analysis summary
        company_analysis = research_data.get('company_analysis', {})
        if company_analysis.get('success'):
            summary_parts.append("**COMPANY ANALYSIS:**")
            summary_parts.append(f"- Industry Analysis: {company_analysis.get('industry_analysis', 'Not available')}")
            summary_parts.append(f"- Analysis Summary: {company_analysis.get('analysis_summary', 'Not available')}")
            summary_parts.append(f"- Confidence: {company_analysis.get('confidence_score', 0):.2f}")
            summary_parts.append(f"- Sources Validated: {len(company_analysis.get('validated_sources', []))}")
        
        # Role analysis summary
        role_analysis = research_data.get('role_analysis', {})
        if role_analysis.get('success'):
            summary_parts.append("\n**ROLE ANALYSIS:**")
            summary_parts.append(f"- Skills Analysis: {role_analysis.get('skills_analysis', 'Not available')}")
            summary_parts.append(f"- Analysis Summary: {role_analysis.get('analysis_summary', 'Not available')}")
            summary_parts.append(f"- Confidence: {role_analysis.get('confidence_score', 0):.2f}")
        
        # Interviewer analysis summary
        interviewer_analysis = research_data.get('interviewer_analysis', {})
        if interviewer_analysis.get('success'):
            summary_parts.append("\n**INTERVIEWER ANALYSIS:**")
            summary_parts.append(f"- LinkedIn Analysis: {interviewer_analysis.get('linkedin_analysis', 'Not available')}")
            summary_parts.append(f"- Profiles Found: {interviewer_analysis.get('linkedin_profiles_found', 0)}")
            summary_parts.append(f"- Confidence: {interviewer_analysis.get('confidence_score', 0):.2f}")
        
        return "\n".join(summary_parts) if summary_parts else "No comprehensive research data available"
