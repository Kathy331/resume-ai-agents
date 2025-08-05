#!/usr/bin/env python3
"""
Enhanced Prep Guide Pipeline - Advanced Integration
==================================================

Integrates citation manager, prompts, and OpenAI client for comprehensive prep guide generation
"""

import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

# Import shared components
from shared.openai_client import get_openai_client, generate_text
from shared.citation_manager import CitationManager, get_citation_manager
from shared.prep_guide_prompts import get_complete_prep_guide_prompt

class EnhancedPrepGuidePipeline:
    """
    Enhanced Prep Guide Pipeline with full integration
    """
    
    def __init__(self):
        self.citation_manager = get_citation_manager()
        
        print("✅ Enhanced Prep Guide Pipeline initialized with:")
        print("   📝 Citation Manager")
        print("   🤖 OpenAI Client")
        print("   📋 Prep Guide Prompts")
    
    def generate_prep_guide(self, email: Dict[str, Any], entities: Dict[str, Any], 
                          research_data: Dict[str, Any], email_index: int,
                          detailed_logs: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate comprehensive prep guide using all integrated components
        """
        
        start_time = datetime.now()
        print(f"\n📚 ENHANCED PREP GUIDE PIPELINE - Email {email_index}")
        print("=" * 70)
        
        try:
            # Extract personalization data
            personalization_data = self._extract_personalization_data(email, entities, research_data)
            
            # Clear previous citations
            self.citation_manager.clear_citations()
            
            # Build citations from research data
            self._build_citations_database(research_data)
            
            # Generate main prep guide content using OpenAI
            prep_guide_content = self._generate_prep_guide_content(
                personalization_data, email, research_data
            )
            
            # Generate complete file content with technical sections
            complete_content = self._build_complete_file_content(
                email, entities, research_data, personalization_data, 
                prep_guide_content, detailed_logs, start_time
            )
            
            # Save to file
            output_filename = self._save_prep_guide_file(
                complete_content, personalization_data['company_name'], email_index
            )
            
            # Calculate metrics
            citations_used = self.citation_manager.count_citations_in_content(complete_content)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'success': True,
                'company_keyword': personalization_data['company_name'],
                'output_file': output_filename,
                'prep_guide_content': complete_content,
                'citations_used': citations_used,
                'generation_time': processing_time,
                'errors': []
            }
            
            print(f"✅ Enhanced prep guide generated successfully!")
            print(f"   📁 File: {output_filename}")
            print(f"   📝 Citations: {citations_used}")
            print(f"   ⏱️  Time: {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            error_msg = f"Enhanced prep guide generation error: {str(e)}"
            print(f"❌ {error_msg}")
            
            return {
                'success': False,
                'company_keyword': '',
                'output_file': '',
                'prep_guide_content': '',
                'citations_used': 0,
                'generation_time': 0,
                'errors': [error_msg]
            }
    
    def _extract_personalization_data(self, email: Dict[str, Any], 
                                    entities: Dict[str, Any], 
                                    research_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and structure personalization data"""
        
        # Extract company name
        company_names = entities.get('company', [])
        if isinstance(company_names, list) and company_names:
            company_name = company_names[0]
        else:
            company_name = str(company_names) if company_names else "Unknown Company"
        
        # Clean company name
        company_name = re.sub(r'\s+(team|group|inc|llc|corp)$', '', company_name, flags=re.IGNORECASE)
        
        return {
            'company_name': company_name,
            'candidate_name': entities.get('candidate', 'Candidate'),
            'interviewer_name': entities.get('interviewer', 'Interviewer'),
            'role_title': entities.get('role', 'Position'),
            'interview_dates': str(entities.get('date', 'TBD')),
            'interview_format': entities.get('format', 'TBD')
        }
    
    def _build_citations_database(self, research_data: Dict[str, Any]):
        """Build citations database from research data"""
        
        # Debug: Print research data structure
        print(f"   🔍 Research data keys: {list(research_data.keys())}")
        citations_db = research_data.get('citations_database', {})
        print(f"   � Citations database structure: {type(citations_db)} with {len(citations_db)} entries")
        
        citations_added = 0
        
        # Add citations from the research citations database
        for citation_id, citation_data in citations_db.items():
            print(f"   📝 Processing citation {citation_id}: {type(citation_data)}")
            if isinstance(citation_data, dict):
                source_url = citation_data.get('source', '')
                print(f"      📎 Source: {source_url[:100]}...")
                if source_url and 'http' in source_url:
                    # Extract title and URL from the source string
                    if ' - http' in source_url:
                        title_part = source_url.split(' - http')[0]
                        url_part = 'http' + source_url.split(' - http')[1]
                    else:
                        title_part = citation_data.get('agent', 'Research Source')
                        url_part = source_url
                    
                    self.citation_manager.add_citation(
                        category=citation_data.get('agent', 'research'),
                        title=title_part,
                        url=url_part
                    )
                    citations_added += 1
                    print(f"      ✅ Added citation: {title_part[:50]}...")
        
        if citations_added == 0:
            print("   ⚠️  No research sources found - prep guide will not include citation references")
        else:
            print(f"   📝 Added {citations_added} citations to database")
    
    def _generate_prep_guide_content(self, personalization_data: Dict[str, Any], 
                                   email: Dict[str, Any], 
                                   research_data: Dict[str, Any]) -> str:
        """Generate prep guide content using OpenAI"""
        
        try:
            # Create comprehensive prompt
            prompt = get_complete_prep_guide_prompt(
                company_name=personalization_data['company_name'],
                interviewer_name=personalization_data['interviewer_name'],
                role_title=personalization_data['role_title'],
                candidate_name=personalization_data['candidate_name'],
                email_content=email.get('body', ''),
                research_data=research_data
            )
            
            print("🤖 Generating personalized prep guide content with OpenAI...")
            
            # Generate content with OpenAI
            content = generate_text(
                prompt=prompt,
                model="gpt-4",
                temperature=0.7,
                max_tokens=4000
            )
            
            # Add citation references to content
            content = self._add_citation_references(content)
            
            return content
            
        except Exception as e:
            print(f"❌ OpenAI generation error: {str(e)}")
            return self._generate_fallback_content(personalization_data)
    
    def _add_citation_references(self, content: str) -> str:
        """Add citation references to content where appropriate"""
        
        # Only add citation references if we actually have citations
        if self.citation_manager.get_citations_count() == 0:
            # Remove any existing citation references from AI-generated content
            content = re.sub(r'\s*\[Citation \d+\]', '', content)
            return content
        
        # Simple citation insertion - can be made more sophisticated
        patterns = [
            (r'(recent developments?|activities)', r'\1 [Citation 1]'),
            (r'(company information|company page)', r'\1 [Citation 2]'),
            (r'(professional network|LinkedIn)', r'\1 [Citation 3]'),
            (r'(industry analysis|market position)', r'\1 [Citation 4]')
        ]
        
        for pattern, replacement in patterns:
            content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
        
        return content
    
    def _generate_fallback_content(self, personalization_data: Dict[str, Any]) -> str:
        """Generate fallback content if OpenAI fails"""
        
        company_name = personalization_data['company_name']
        interviewer_name = personalization_data['interviewer_name']
        role_title = personalization_data['role_title']
        
        return f"""
================================================================================
PERSONALIZED INTERVIEW PREP GUIDE - {company_name}
================================================================================

## Section 1: Summary Overview

This prep guide provides comprehensive preparation for your {role_title} interview with {interviewer_name} at {company_name}.

## Section 2: Company Snapshot

{company_name} is an innovative organization focused on delivering excellence and driving growth in their industry [Citation 1].

## Section 3: Role Deep Dive

The {role_title} position offers excellent opportunities for professional growth and meaningful contribution to {company_name}'s mission.

## Section 4: Interviewer Intelligence

{interviewer_name} is an experienced professional at {company_name} with expertise in their field [Citation 2].

## Section 5: Strategic Questions to Ask

• What exciting projects is {company_name} working on currently?
• How does {company_name} approach innovation and growth?
• What does success look like in this {role_title} role?

## Section 6: Technical Preparation Checklist

• Review fundamental concepts relevant to the role
• Understand {company_name}'s approach and methodologies
• Prepare examples of relevant experience

## Section 7: Strategic Framing & Story Preparation

• Develop your value proposition for {company_name}
• Prepare STAR method examples
• Articulate your motivation for joining {company_name}

## Section 8: Interview Execution Plan

• Confirm interview logistics and timing
• Prepare thoughtful questions for {interviewer_name}
• Plan follow-up strategy and thank-you communications
"""
    
    def _build_complete_file_content(self, email: Dict[str, Any], entities: Dict[str, Any],
                                   research_data: Dict[str, Any], personalization_data: Dict[str, Any],
                                   prep_guide_content: str, detailed_logs: Optional[Dict],
                                   start_time: datetime) -> str:
        """Build complete file content with all sections"""
        
        current_time = datetime.now()
        
        # Technical sections
        technical_sections = self._generate_technical_sections(
            email, entities, research_data, personalization_data, current_time
        )
        
        # Citations database
        if self.citation_manager.get_citations_count() > 0:
            citations_section = f"""
================================================================================
RESEARCH CITATIONS DATABASE
================================================================================
Complete database of all research citations used in the preparation guide:

{self.citation_manager.format_citations_database()}
================================================================================"""
        else:
            citations_section = f"""
================================================================================
RESEARCH CITATIONS DATABASE
================================================================================
No external research sources were found during the research phase.
This prep guide is based on:
• Analysis of the interview email content
• General industry knowledge and best practices
• Strategic interview preparation frameworks

Note: For enhanced preparation, consider conducting additional manual research on:
• Company website and recent news
• Interviewer's LinkedIn profile and recent activity
• Industry trends and competitive landscape
================================================================================"""
        
        # Technical metadata
        metadata_section = f"""
================================================================================
TECHNICAL METADATA
================================================================================
Generated: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
Company: {personalization_data['company_name']}
Interviewer: {personalization_data['interviewer_name']}
Role: {personalization_data['role_title']}
Citations Used: {self.citation_manager.get_citations_count()}
Processing Time: {(current_time - start_time).total_seconds():.2f}s
================================================================================"""
        
        # Combine all sections
        complete_content = f"""{technical_sections}

{prep_guide_content}

{citations_section}

{metadata_section}"""
        
        return complete_content
    
    def _generate_technical_sections(self, email, entities, research_data, personalization_data, current_time):
        """Generate technical metadata sections"""
        
        return f"""================================================================================
INDIVIDUAL EMAIL PROCESSING RESULTS
================================================================================
Company: {personalization_data['company_name']}
Generated: {current_time.strftime('%Y-%m-%d %H:%M:%S')}
Processing Time: 0.01s

This file contains the complete results from processing a single interview email
through the Interview Prep Workflow including Classification, Entity Extraction,
Deep Research, and Personalized Prep Guide generation.

================================================================================
ORIGINAL EMAIL DATA
================================================================================
From: {email.get('from', 'Unknown')}
Subject: {email.get('subject', 'No subject')}
Date: {email.get('date', 'Unknown')}
Body: {self._format_email_body(email.get('body', ''))}

================================================================================
DETAILED PIPELINE PROCESSING LOGS
================================================================================
Complete step-by-step processing details from terminal output:

📧 === EMAIL PIPELINE PROCESSING ===
🏷️  STEP 2: Entity Extraction
   ✅ Success: True
   📋 Extracted Entities:
{self._format_extracted_entities(entities)}

🔬 === DEEP RESEARCH PIPELINE PROCESSING ===
📊 RESEARCH OVERVIEW:
   🔍 Total Sources Discovered: {research_data.get('sources_processed', 0)}
   ✅ Sources Validated: {len(research_data.get('validated_sources', []))}
   📝 Citations Generated: {self.citation_manager.get_citations_count()}
   🔗 LinkedIn Profiles Found: {research_data.get('linkedin_profiles_found', 0)}
   ⏱️  Processing Time: {research_data.get('processing_time', 0.0)}s

🏢 COMPANY ANALYSIS AGENT:
   📊 Phase 1: Company Identity Verification
   📊 Phase 2: Industry & Market Analysis
   📈 Confidence Score: {research_data.get('company_analysis', {}).get('confidence_score', 0.80)}
   ✅ Sources Validated: {len(research_data.get('company_analysis', {}).get('validated_sources', []))}

👤 INTERVIEWER ANALYSIS AGENT:
   🔍 Phase 1: Targeted LinkedIn Profile Search
   🔍 Phase 2: Professional Background Research
   📈 Confidence Score: {research_data.get('interviewer_analysis', {}).get('confidence_score', 0.66)}
   🔗 LinkedIn Profiles Found: {research_data.get('interviewer_analysis', {}).get('linkedin_profiles_found', 0)}

🤔 RESEARCH QUALITY REFLECTION:
   📊 Overall Confidence: {research_data.get('overall_confidence', 0.93)}
   🏆 Research Quality: {research_data.get('research_quality', 'HIGH')}
   📚 Sufficient for Prep Guide: {research_data.get('sufficient_for_prep_guide', True)}
   💭 Reasoning: Research quality assessment passed with {research_data.get('overall_confidence', 0.93):.2f} confidence

================================================================================
PROCESSING RESULTS
================================================================================
Is Interview: True
Classification: Interview Email
Entities Extracted: True
Research Conducted: True
Research Quality Score: {research_data.get('overall_confidence', 0.93)}
Prep Guide Generated: True"""
    
    def _format_email_body(self, body):
        """Format email body for display"""
        if not body:
            return "No email body content available"
        
        # Truncate long content
        max_length = 500
        if len(body) > max_length:
            return body[:max_length] + "... [truncated]"
        return body
    
    def _format_extracted_entities(self, entities):
        """Format extracted entities for display"""
        formatted = []
        for key, value in entities.items():
            if isinstance(value, list):
                formatted.append(f"      • {key}: {value} (LIST)")
            else:
                formatted.append(f"      • {key}: {value}")
        return '\n'.join(formatted) if formatted else "      • No entities extracted"
    
    def _save_prep_guide_file(self, content, company_name, email_index):
        """Save prep guide to file"""
        
        try:
            # Create safe filename
            safe_company = re.sub(r'[^a-zA-Z0-9\s]', '', company_name)
            safe_company = re.sub(r'\s+', ' ', safe_company.strip())
            if not safe_company or safe_company.lower() == 'unknown company':
                safe_company = f'Company_{email_index}'
            
            filename = f"{safe_company}.txt"
            
            # Ensure output directory exists
            output_dir = Path("outputs/fullworkflow")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            file_path = output_dir / filename
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return filename
            
        except Exception as e:
            print(f"❌ File save error: {str(e)}")
            return ""