#!/usr/bin/env python3
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
        """Generate comprehensive personalized prep guide with citations"""
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
            
            # Build research context with citations
            research_context = self._build_research_context_with_citations(research_result)
            citations_database = research_result.get('citations_database', {})
            
            # Create comprehensive prompt for personalized prep guide
            prompt = f"""
            Generate a comprehensive, personalized interview preparation guide based on this SPECIFIC interview email and sophisticated research findings:
            
            **SPECIFIC INTERVIEW EMAIL DETAILS:**
            From: {from_sender}
            Subject: {email_subject}
            Interview Dates: {', '.join(dates) if dates else 'Not specified'}
            Format: {format_type}
            
            **EXTRACTED INTERVIEW DETAILS:**
            - Company: {company}
            - Role: {role}
            - Interviewer: {interviewer}
            
            **SOPHISTICATED RESEARCH FINDINGS WITH CITATIONS:**
            {research_context}
            
            Create a PERSONALIZED and ACTIONABLE prep guide with these sections:
            
            1. **Before the Interview** - SPECIFIC actions based on THIS email:
               - Response deadline and exact timing from the email
               - Specific time slots mentioned in the email to choose from
               - Who to reply to and contact information
               - Company mission, products, and current projects to research
               - Specific technologies and approaches to understand based on research
               
            2. **Company Analysis** - Based on research findings:
               - What problems they solve and their approach
               - Recent developments and market position
               - Technologies they use (include specific findings from research)
               - Key insights from company research with citations
               
            3. **Role Analysis** - Tailored to this specific role:
               - What they're looking for in this role based on research
               - Key skills and qualifications needed
               - How to demonstrate relevant experience
               - Technical requirements and expectations
               
            4. **Interviewer Background** - Based on LinkedIn and professional research:
               - Professional background and expertise areas
               - Recent posts, articles, or achievements found in research
               - Common interests or connection points to discuss
               - LinkedIn profile insights and recommendations
               
            5. **Questions to Ask** - Intelligent questions based on research findings:
               - Company-specific questions based on recent developments
               - Role-specific questions about expectations and growth
               - Interviewer-specific questions based on their background
               - Technical questions relevant to the role
               
            6. **Strategic Recommendations** - How to position yourself:
               - Key talking points based on research findings
               - How to align your experience with their needs
               - Conversation starters based on interviewer research
               - Follow-up strategies
            
            **CRITICAL REQUIREMENTS:**
            - Include specific citations [Citation 1], [Citation 2], etc. for ALL findings and recommendations
            - Use the numbered citation system from the research database
            - Base timing and logistics on the ACTUAL email content provided
            - Include SPECIFIC findings from LinkedIn profiles, company websites, and research
            - Make every recommendation immediately actionable with clear next steps
            - Every fact, insight, and recommendation MUST have a citation number
            - Format citations as [Citation X] where X corresponds to the citation number
            - Ensure all advice is personalized to this specific interview opportunity
            """
            
            # Generate prep guide using LLM
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                prep_guide_content = loop.run_until_complete(call_llm(prompt))
                
                # Count sections and citations
                sections_generated = self._count_sections(prep_guide_content)
                citations_used = len(citations_database)
                
                print(f"   ✅ Prep guide generated ({len(prep_guide_content)} characters)")
                sections_count = len(sections_generated) if isinstance(sections_generated, list) else sections_generated
                print(f"   📚 Sections: {sections_count}")
                print(f"   📝 Citations: {citations_used}")
                
                return {
                    'success': True,
                    'prep_guide_content': prep_guide_content,
                    'citations_used': citations_used,
                    'sections_generated': sections_generated
                }
                
            finally:
                loop.close()
                
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
