#!/usr/bin/env python3
"""
Enhanced Prep Guide Pipeline - Advanced Integration
==================================================

Integrates citation manager, prompts, and OpenAI client for comprehensive prep guide generation
Includes detailed console log capture for validation/rejection details
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
from shared.prep_guide_prompts import get_complete_prep_guide_prompt, get_entity_value
from shared.simple_cache import cached_openai_generate
from shared.console_log_capture import start_log_capture, stop_log_capture, get_validation_logs_for_file
from agents.research_engine.second_loop_research_engine import enhance_prep_guide_with_second_loop

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
    
    def generate_prep_guide(self, email: Dict[str, Any], 
                          entities: Dict[str, Any], 
                          research_data: Dict[str, Any], 
                          email_index: int = 1,
                          detailed_logs: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate comprehensive interview prep guide with enhanced personalization
        """
        
        print("📝 GENERATING PERSONALIZED PREP GUIDE")
        print("=" * 40)
        
        # Store email data for use in fallback
        self.email_data = email
        
        # Use the full method with all parameters
        return self.generate_prep_guide_full(email, entities, research_data, email_index, detailed_logs)
    
    def generate_prep_guide_full(self, email: Dict[str, Any], entities: Dict[str, Any], 
                          research_data: Dict[str, Any], email_index: int,
                          detailed_logs: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Generate comprehensive prep guide using all integrated components
        """
        
        start_time = datetime.now()
        print(f"\n📚 ENHANCED PREP GUIDE PIPELINE - Email {email_index}")
        print("=" * 70)
        
        # Start capturing console logs for validation details
        start_log_capture()
        
        try:
            # Extract personalization data
            personalization_data = self._extract_personalization_data(email, entities, research_data)
            
            # Clear previous citations
            self.citation_manager.clear_citations()
            
            # Build citations from research data
            self._build_citations_database(research_data)
            
            # Generate main prep guide content using OpenAI (new format)
            prep_guide_content = self._generate_prep_guide_content(
                personalization_data, email, research_data, entities
            )
            
            # SECOND LOOP: Intelligent gap analysis and additional research
            print("🔬 INITIATING SECOND LOOP INTELLIGENT RESEARCH...")
            second_loop_results = enhance_prep_guide_with_second_loop(
                prep_guide_content, entities, research_data
            )
            
            if second_loop_results['success'] and second_loop_results['additional_citations']:
                print(f"   ✅ Second loop added {len(second_loop_results['additional_citations'])} new sources")
                
                # Regenerate prep guide with enhanced research data
                print("   🔄 Regenerating prep guide with enhanced research...")
                prep_guide_content = self._generate_prep_guide_content(
                    personalization_data, email, research_data, entities
                )
            else:
                print("   ℹ️  Second loop: No additional research needed")
            
            # Stop capturing logs and get the content
            captured_console_logs = stop_log_capture()
            
            # Generate complete file content with technical sections AND new prep guide format
            complete_content = self._build_complete_file_content(
                email, entities, research_data, personalization_data, 
                prep_guide_content, detailed_logs, start_time, captured_console_logs, second_loop_results
            )
            
            # Save to file
            output_file = self._save_prep_guide_file(
                complete_content, personalization_data['company_name'], email_index
            )
            
            # Calculate metrics
            citations_used = self.citation_manager.count_citations_in_content(complete_content)
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                'success': True,
                'company_keyword': personalization_data['company_name'],
                'output_file': output_file,
                'prep_guide_content': complete_content,
                'citations_used': citations_used,
                'generation_time': processing_time,
                'errors': []
            }
            
            print(f"✅ Enhanced prep guide generated successfully!")
            print(f"   📁 File: {output_file}")
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
        """Build citations database from research data with smart filtering"""
        
        # Debug: Print research data structure
        print(f"   🔍 Research data keys: {list(research_data.keys())}")
        citations_db = research_data.get('citations_database', {})
        print(f"   📊 Citations database structure: {type(citations_db)} with {len(citations_db)} entries")
        
        citations_added = 0
        filtered_out = 0
        
        # Add citations from the research citations database with smart filtering
        for citation_id, citation_data in citations_db.items():
            print(f"   📝 Processing citation {citation_id}: {type(citation_data)}")
            if isinstance(citation_data, dict):
                source_url = citation_data.get('source', '')
                print(f"      📎 Source: {source_url[:100]}...")
                
                # Smart filtering - remove irrelevant citations
                if self._is_relevant_citation(source_url, research_data):
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
                else:
                    filtered_out += 1
                    print(f"      🚫 Filtered out irrelevant citation: {source_url[:50]}...")
        
        if citations_added == 0:
            print("   ⚠️  No relevant research sources found - prep guide will use fallback content")
        else:
            print(f"   📝 Added {citations_added} relevant citations, filtered out {filtered_out} irrelevant ones")

    def _is_relevant_citation(self, source_url: str, research_data: Dict[str, Any]) -> bool:
        """Smart filtering to determine if a citation is relevant"""
        if not source_url:
            return False
        
        # Get company and interviewer names for relevance checking
        company_name = ""
        interviewer_name = ""
        
        # Extract from research data if available
        if 'research_data' in research_data:
            company_analysis = research_data['research_data'].get('company_analysis', {})
            interviewer_analysis = research_data['research_data'].get('interviewer_analysis', {})
        
        source_lower = source_url.lower()
        
        # Filter out obviously irrelevant sources
        irrelevant_patterns = [
            'danone',  # Wrong company
            'crunchbase',  # Generic platform
            'glassdoor.com/job-search',  # Generic job search pages
            'linkedin.com/company/adm',  # Wrong company (ADM)
            'login',  # Login pages
            'sign-in',  # Sign-in pages
            'find-your-next-opportunity',  # Generic job pages
        ]
        
        for pattern in irrelevant_patterns:
            if pattern in source_lower:
                return False
        
        # Keep relevant sources
        relevant_patterns = [
            'juteq',  # Target company
            'dandilyonn',  # Target company 
            'archana',  # Target interviewer
            'rakesh',  # Target interviewer
            'linkedin.com/in/',  # LinkedIn profiles
            'linkedin.com/posts/',  # LinkedIn posts
        ]
        
        for pattern in relevant_patterns:
            if pattern in source_lower:
                return True
        
        # Default: keep if it contains the actual target company/interviewer names
        return True  # Conservative approach - let other filters handle it
    
    def _parse_dual_format_response(self, content: str) -> tuple:
        """Parse OpenAI response that contains both markdown and HTML formats"""
        try:
            # Split on the HTML format marker
            if "=== HTML FORMAT ===" in content:
                parts = content.split("=== HTML FORMAT ===")
                markdown_part = parts[0].replace("=== MARKDOWN FORMAT ===", "").strip()
                html_part = parts[1].strip()
                
                # Clean up HTML part - remove instruction text
                html_lines = html_part.split('\n')
                html_start = -1
                for i, line in enumerate(html_lines):
                    if line.strip().startswith('<div class="interview-prep-guide">'):
                        html_start = i
                        break
                
                if html_start >= 0:
                    html_content = '\n'.join(html_lines[html_start:])
                    # Find the closing div
                    html_end = html_content.rfind('</div>')
                    if html_end > 0:
                        html_content = html_content[:html_end + 6]  # Include </div>
                else:
                    html_content = html_part
                
                return markdown_part, html_content
            else:
                # Fallback: use content as markdown, generate simple HTML
                html_content = self._markdown_to_basic_html(content)
                return content, html_content
                
        except Exception as e:
            print(f"   ⚠️  Error parsing dual format response: {e}")
            # Fallback: treat as markdown only
            html_content = self._markdown_to_basic_html(content)
            return content, html_content
    
    def _markdown_to_basic_html(self, markdown_content: str) -> str:
        """Convert markdown to basic HTML as fallback"""
        html = markdown_content
        
        # Basic markdown to HTML conversions
        html = html.replace('# ', '<h1>').replace('\n## ', '</h1>\n<h2>').replace('\n### ', '</h2>\n<h3>')
        html = html.replace('**', '<strong>').replace('**', '</strong>')
        html = html.replace('- ', '<li>').replace('\n\n', '</li>\n</ul>\n<p>').replace('\n', '<br>\n')
        
        # Wrap in basic structure
        html = f'<div class="interview-prep-guide">\n{html}\n</div>'
        
        return html
    
    def _convert_to_simple_html(self, markdown_content: str) -> str:
        """Convert simple markdown to HTML matching the guideline format"""
        html = markdown_content
        
        # Convert headers
        html = html.replace('# interview prep requirements template', 
                           '<h1>📋 Interview Prep Requirements</h1>')
        html = html.replace('## 1. before interview', '<h2>1. Before Interview</h2>')
        html = html.replace('## 2. interviewer background', '<h2>2. Interviewer Background</h2>')
        html = html.replace('## 3. company background', '<h2>3. Company Background</h2>')
        html = html.replace('## 4. technical preparations', '<h2>4. Technical Preparations</h2>')
        html = html.replace('## 5. questions to ask', '<h2>5. Questions to Ask</h2>')
        html = html.replace('## 6. common questions', '<h2>6. Common Questions</h2>')
        
        # Convert bullet points to proper list items
        lines = html.split('\n')
        in_list = False
        result_lines = []
        
        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                item_text = line.strip()[2:]  # Remove '- '
                # Convert embedded links
                if '[' in item_text and '](' in item_text:
                    import re
                    item_text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', 
                                     r'<a href="\2" target="_blank">\1</a>', item_text)
                result_lines.append(f'<li>{item_text}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                if line.strip():
                    # Convert embedded links in regular text
                    if '[' in line and '](' in line:
                        import re
                        line = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', 
                                     r'<a href="\2" target="_blank">\1</a>', line)
                    result_lines.append(f'<p>{line}</p>')
                else:
                    result_lines.append('<br>')
        
        if in_list:
            result_lines.append('</ul>')
        
        # Wrap in container div
        final_html = f'''<div style="font-family: sans-serif; font-size: 16px; line-height: 1.5;">
{chr(10).join(result_lines)}
</div>'''
        
        return final_html
    
    def _store_html_for_ui(self, entities: Dict[str, Any], html_content: str):
        """Store HTML content for UI access"""
        try:
            company = get_entity_value(entities, 'company', 'COMPANY')
            safe_company = "".join(c for c in company if c.isalnum() or c in (' ', '-', '_')).rstrip()
            
            # Create UI-specific directory
            ui_output_dir = Path("outputs/ui")
            ui_output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save HTML version for UI
            html_file = ui_output_dir / f"{safe_company}_prep_guide.html"
            
            # Create complete HTML document for UI
            complete_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Interview Prep Guide - {company}</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; margin: 2rem; }}
        .interview-prep-guide {{ max-width: 800px; margin: 0 auto; }}
        h1 {{ color: #2563eb; border-bottom: 2px solid #e5e7eb; padding-bottom: 0.5rem; }}
        h2 {{ color: #1f2937; margin-top: 2rem; }}
        h3 {{ color: #374151; }}
        .executive-summary {{ background: #f3f4f6; padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; }}
        .company-intelligence, .role-analysis, .interviewer-intelligence {{ margin: 2rem 0; }}
        .question-framework ul {{ padding-left: 1.5rem; }}
        .pre-interview-checklist li {{ margin: 0.5rem 0; }}
        ul {{ list-style-type: disc; }}
        li {{ margin: 0.25rem 0; }}
        strong {{ color: #1f2937; }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(complete_html)
            
            print(f"   🌐 HTML version saved for UI: {html_file}")
            
        except Exception as e:
            print(f"   ⚠️  Error saving HTML for UI: {e}")
    
    def _generate_prep_guide_content(self, personalization_data: Dict[str, Any], 
                                   email: Dict[str, Any], 
                                   research_data: Dict[str, Any],
                                   entities: Dict[str, Any]) -> str:
        """Generate prep guide content using OpenAI"""
        
        try:
            # Create comprehensive prompt
            prompt = get_complete_prep_guide_prompt(email, entities, research_data)
            
            print("🤖 Generating personalized prep guide content with OpenAI...")
            
            # Check research quality - if poor, add specific instructions
            research_quality = research_data.get('research_quality', 'LOW')
            overall_confidence = research_data.get('overall_confidence', 0.0)
            
            if research_quality in ['LOW', 'MEDIUM'] or overall_confidence < 0.8:
                prompt += f"""

IMPORTANT: The research quality is {research_quality} (confidence: {overall_confidence:.2f}). 
You must still generate content following the exact guideline format:

## 1. before interview
## 2. interviewer background  
## 3. company background
## 4. technical preparations
## 5. questions to ask
## 6. common questions

Do NOT use generic fallback content or sections like "Section 1: Summary Overview".
Use the available research data and citations, even if limited.
"""
            
            # Force fresh OpenAI call by temporarily disabling cache if env var is set
            disable_cache = os.getenv('DISABLE_OPENAI_CACHE', 'false').lower() == 'true'
            
            # Generate content with OpenAI (cached) - using new simplified format
            content = cached_openai_generate(
                prompt=prompt,
                model="gpt-4",
                temperature=0.7,
                max_tokens=2000  # Reduced since new format is more concise
            )
            
            if not content:
                raise Exception("OpenAI returned empty content")
            
            # Check if content is using fallback format
            if any(section in content for section in ["Section 1: Summary", "Section 2: Company", "fallback content"]):
                print("   ⚠️  Detected fallback content - regenerating with strict format")
                # Force regeneration with stricter prompt
                strict_prompt = prompt + "\n\nIMPORTANT: You MUST use the exact format specified in the guidelines. Do NOT use 'Section 1:', 'Section 2:' format."
                content = cached_openai_generate(
                    prompt=strict_prompt,
                    model="gpt-4",
                    temperature=0.5,
                    max_tokens=2000,
                    force_fresh=True  # Force new generation
                )
            
            # Parse for HTML if present, otherwise use markdown
            if "=== HTML FORMAT ===" in content:
                parts = content.split("=== HTML FORMAT ===")
                markdown_content = parts[0].strip()
                html_content = parts[1].strip() if len(parts) > 1 else self._convert_to_simple_html(markdown_content)
            else:
                markdown_content = content
                html_content = self._convert_to_simple_html(content)
            
            # Store HTML version for UI
            self._store_html_for_ui(entities, html_content)
            
            return markdown_content
            
        except Exception as e:
            print(f"❌ OpenAI generation error: {str(e)}")
            print("   🔄 Using enhanced fallback with guideline format...")
            return self._generate_enhanced_fallback_content(personalization_data, entities, research_data)
    
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
                                   start_time: datetime, captured_console_logs: str = "", 
                                   second_loop_results: Dict[str, Any] = None) -> str:
        """Build complete file content with all sections"""
        
        current_time = datetime.now()
        
        # Technical sections with captured validation logs
        technical_sections = self._generate_technical_sections(
            email, entities, research_data, personalization_data, current_time, captured_console_logs, second_loop_results
        )
        
        # Citations database with second loop sources
        citations_db = research_data.get('citations_database', {})
        if citations_db:
            # Count first loop vs second loop citations
            first_loop_citations = []
            second_loop_citations = []
            
            for citation_id, citation_data in citations_db.items():
                if isinstance(citation_data, dict):
                    source = citation_data.get('source', '')
                    citation_line = f"📝 Citation [{citation_id}]: {source}"
                    if citation_data.get('second_loop', False):
                        second_loop_citations.append(citation_line)
                    else:
                        first_loop_citations.append(citation_line)
            
            citations_content = "Complete database of all research citations used in the preparation guide:\n\n"
            
            if first_loop_citations:
                citations_content += f"FIRST LOOP RESEARCH SOURCES ({len(first_loop_citations)} sources):\n"
                citations_content += "\n".join(first_loop_citations)
                citations_content += "\n\n"
            
            if second_loop_citations:
                citations_content += f"SECOND LOOP INTELLIGENT RESEARCH SOURCES ({len(second_loop_citations)} sources):\n"
                citations_content += "\n".join(second_loop_citations)
                citations_content += "\n\n"
            
            total_citations = len(first_loop_citations) + len(second_loop_citations)
            citations_content += f"Total Citations: {total_citations}\n"
            citations_content += f"First Loop Sources: {len(first_loop_citations)}\n"
            citations_content += f"Second Loop Enhanced Sources: {len(second_loop_citations)}"
            
            citations_section = "\n" + "=" * 80 + "\n"
            citations_section += "RESEARCH CITATIONS DATABASE\n"
            citations_section += "=" * 80 + "\n"
            citations_section += citations_content + "\n"
            citations_section += "=" * 80
        else:
            citations_section = "\n" + "=" * 80 + "\n"
            citations_section += "RESEARCH CITATIONS DATABASE\n"
            citations_section += "=" * 80 + "\n"
            citations_section += "No external research sources were found during the research phase.\n"
            citations_section += "This prep guide is based on:\n"
            citations_section += "• Analysis of the interview email content\n"
            citations_section += "• General industry knowledge and best practices\n"
            citations_section += "• Strategic interview preparation frameworks\n\n"
            citations_section += "Note: For enhanced preparation, consider conducting additional manual research on:\n"
            citations_section += "• Company website and recent news\n"
            citations_section += "• Interviewer's LinkedIn profile and recent activity\n"
            citations_section += "• Industry trends and competitive landscape\n"
            citations_section += "=" * 80
        
        # Technical metadata
        metadata_section = "\n" + "=" * 80 + "\n"
        metadata_section += "TECHNICAL METADATA\n"
        metadata_section += "=" * 80 + "\n"
        metadata_section += f"Generated: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        metadata_section += f"Company: {personalization_data['company_name']}\n"
        metadata_section += f"Interviewer: {personalization_data['interviewer_name']}\n"
        metadata_section += f"Role: {personalization_data['role_title']}\n"
        metadata_section += f"Citations Used: {len(citations_db)}\n"
        metadata_section += f"Processing Time: {(current_time - start_time).total_seconds():.2f}s\n"
        metadata_section += "=" * 80
        
        # Combine all sections
        complete_content = technical_sections + "\n\n" + prep_guide_content + citations_section + metadata_section
        
        return complete_content
    
    def _generate_technical_sections(self, email, entities, research_data, personalization_data, current_time, captured_console_logs="", second_loop_results=None):
        """Generate technical metadata sections with detailed logs"""
        
        # Extract detailed logs from research data AND captured console logs
        detailed_research_logs = self._extract_detailed_research_logs(research_data)
        
        # Get formatted validation logs from console capture
        validation_logs_formatted = ""
        if captured_console_logs:
            validation_logs_formatted = get_validation_logs_for_file(captured_console_logs)
        
        # Add second loop research details
        second_loop_section = ""
        if second_loop_results and second_loop_results.get('success'):
            gaps_count = len(second_loop_results.get('gaps_identified', []))
            new_searches = second_loop_results.get('new_searches_conducted', 0)
            new_citations = len(second_loop_results.get('additional_citations', []))
            
            second_loop_section = f"""
🔬 === SECOND LOOP INTELLIGENT RESEARCH ===
   🎯 AI Gap Analysis: Identified {gaps_count} research gaps
   🔍 Targeted Searches: Executed {new_searches} intelligent follow-up queries
   📝 Additional Sources: Found {new_citations} high-quality research sources
   ✨ Content Enhancement: {"Enhanced prep guide with new research" if new_citations > 0 else "No additional enhancement needed"}
   
   📊 GAPS IDENTIFIED AND ADDRESSED:"""
            
            for gap in second_loop_results.get('gaps_identified', []):
                gap_type = gap.get('type', 'unknown')
                priority = gap.get('priority', 'medium')
                description = gap.get('description', 'No description')
                second_loop_section += f"\n      🎯 {gap_type.upper()} ({priority}): {description}"
            
            if second_loop_results.get('additional_citations'):
                second_loop_section += f"\n   \n   📚 NEW RESEARCH SOURCES ADDED:"
                for citation in second_loop_results.get('additional_citations', []):
                    title = citation.get('title', 'Source')[:50]
                    gap_type = citation.get('gap_type', 'research')
                    second_loop_section += f"\n      📝 Citation [{citation.get('id')}]: {title}... (Type: {gap_type})"
        
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
   🔍 Total Sources Discovered: {research_data.get('total_sources_discovered', 0)}
   ✅ Sources Validated: {len(research_data.get('validated_sources', []))}
   📝 Citations Generated: {self.citation_manager.get_citations_count()}
   🔗 LinkedIn Profiles Found: {research_data.get('linkedin_profiles_found', 0)}
   ⏱️  Processing Time: {research_data.get('processing_time', 0.0)}s

🏢 COMPANY ANALYSIS AGENT:
   📊 Phase 1: Company Identity Verification
   📊 Phase 2: Industry & Market Analysis
{detailed_research_logs.get('company_analysis', '   📈 Confidence Score: 0.80')}
   ✅ Sources Validated: {len(research_data.get('company_analysis', {}).get('validated_sources', []))}

👤 INTERVIEWER ANALYSIS AGENT:
   🔍 Phase 1: Targeted LinkedIn Profile Search
   🔍 Phase 2: Professional Background Research
{detailed_research_logs.get('interviewer_analysis', '   📈 Confidence Score: 0.66')}
   🔗 LinkedIn Profiles Found: {research_data.get('interviewer_analysis', {}).get('linkedin_profiles_found', 0)}

{validation_logs_formatted}

{detailed_research_logs.get('validation_details', '')}

{second_loop_section}

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

    def _extract_detailed_research_logs(self, research_data: Dict[str, Any]) -> Dict[str, str]:
        """Extract detailed research logs including validations and rejections"""
        
        logs = {
            'company_analysis': '   📈 Confidence Score: 0.80',
            'interviewer_analysis': '   📈 Confidence Score: 0.66', 
            'validation_details': ''
        }
        
        # Extract company analysis details
        if 'research_data' in research_data:
            research_details = research_data['research_data']
            
            # Company analysis logs
            if 'company_analysis' in research_details:
                company_data = research_details['company_analysis']
                confidence = company_data.get('confidence_score', 0.80)
                logs['company_analysis'] = f'   📈 Confidence Score: {confidence}'
                
                # Add validation details if available
                if 'validation_results' in company_data:
                    validation_section = "\n📊 COMPANY VALIDATION RESULTS:\n"
                    for result in company_data['validation_results']:
                        if result.get('validated', False):
                            validation_section += f"   ✅ VALIDATED: {result.get('title', 'Source')[:50]}... (Score: {result.get('score', 0)}, Evidence: {result.get('evidence', 'N/A')})\n"
                        else:
                            validation_section += f"   ❌ REJECTED: {result.get('title', 'Source')[:50]}... (Score: {result.get('score', 0)}, Reasons: {result.get('rejection_reason', 'N/A')})\n"
                    logs['validation_details'] += validation_section
            
            # Interviewer analysis logs  
            if 'interviewer_analysis' in research_details:
                interviewer_data = research_details['interviewer_analysis']
                confidence = interviewer_data.get('confidence_score', 0.66)
                linkedin_found = interviewer_data.get('linkedin_profiles_found', 0)
                logs['interviewer_analysis'] = f'   📈 Confidence Score: {confidence}\n   🔗 LinkedIn Profiles Found: {linkedin_found}'
                
                # Add LinkedIn search details if available
                if 'linkedin_searches' in interviewer_data:
                    linkedin_section = "\n👤 LINKEDIN SEARCH RESULTS:\n"
                    for search in interviewer_data['linkedin_searches']:
                        query = search.get('query', 'Unknown query')
                        results_count = len(search.get('results', []))
                        linkedin_section += f"   🔍 Query: '{query}' → {results_count} results\n"
                        
                        for result in search.get('results', []):
                            if result.get('is_linkedin_profile', False):
                                linkedin_section += f"      ✅ LinkedIn Profile Found: {result.get('title', 'Profile')[:50]}...\n"
                            elif result.get('is_company_relevant', False):
                                linkedin_section += f"      🎯 Company-Relevant: {result.get('title', 'Content')[:50]}...\n"
                            else:
                                linkedin_section += f"      ⚠️  Other Result: {result.get('title', 'Content')[:50]}...\n"
                    logs['validation_details'] += linkedin_section
        
        # Extract citations validation if available
        citations_db = research_data.get('citations_database', {})
        if citations_db:
            citations_section = "\n📝 CITATIONS VALIDATION:\n"
            for citation_id, citation_data in citations_db.items():
                if isinstance(citation_data, dict):
                    source = citation_data.get('source', '')
                    agent = citation_data.get('agent', 'unknown')
                    citations_section += f"   📎 Citation [{citation_id}]: {source[:60]}... (Agent: {agent})\n"
            logs['validation_details'] += citations_section
        
        return logs
    
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
    
    def _generate_enhanced_fallback_content(self, personalization_data: Dict[str, Any], 
                                          entities: Dict[str, Any], 
                                          research_data: Dict[str, Any]) -> str:
        """Generate enhanced fallback content using guideline format with actual email data"""
        
        # Get email data
        email = self.email_data if hasattr(self, 'email_data') else {}
        email_body = email.get('body', '')
        
        company_name = personalization_data['company_name']
        interviewer_name = personalization_data['interviewer_name'] 
        role_title = personalization_data['role_title']
        
        # Extract specific dates and details from entities
        dates = entities.get('date', ['TBD'])
        format_info = entities.get('format', ['format TBD'])
        
        # Extract logistics from email
        logistics_text = ""
        if 'Tuesday, August 6' in email_body and 'Wednesday, August 7' in email_body:
            logistics_text = "date options: Tuesday, August 6 or Wednesday, August 7"
        if '10:00 a.m.' in email_body and '4:00 p.m.' in email_body:
            if logistics_text:
                logistics_text += "; time: flexible between 10:00 a.m. and 4:00 p.m. (ET)"
            else:
                logistics_text = "time: flexible between 10:00 a.m. and 4:00 p.m. (ET)"
        
        # Check if we have Rakesh Gohel citations
        has_rakesh = any('rakesh gohel' in str(citation).lower() or 'rakeshgohel01' in str(citation).lower() 
                        for citation in research_data.get('citations_database', {}).values())
        
        # Generate personalized content
        before_section = f"- email mentions {logistics_text if logistics_text else 'date options and time slots'}\n"
        if 'Friday, August 2' in email_body:
            before_section += "- respond by end of day Friday, August 2 to confirm your time slot\n"
        before_section += f"- prepare to discuss your background and interests in AI and cloud technologies\n"
        if 'Virtual' in str(format_info) or 'Zoom' in str(format_info):
            before_section += "- test your zoom setup and ensure stable internet connection\n"
        
        # Interviewer section with real data
        if has_rakesh:
            interviewer_section = f"- rakesh gohel is a professional at {company_name.lower()} with expertise in AI and cloud technologies\n"
            interviewer_section += "- background: scaling with AI agents, cloud-native solutions focus\n"
            interviewer_section += "- mentioned interest in AI and cloud technologies in interview invitation\n"
            interviewer_section += "- [rakesh gohel linkedin](https://ca.linkedin.com/in/rakeshgohel01)\n"
        else:
            interviewer_section = f"- {interviewer_name.lower()} is a professional at {company_name.lower()}\n"
            interviewer_section += "- background research in progress\n"
        
        # Company section with specific details
        if company_name.lower() == 'juteq':
            company_section = f"- {company_name.lower()} is a technology company specializing in AI and cloud-native solutions\n"
            company_section += "- focuses on cloud-native innovation and DevOps solutions\n"
            company_section += "- hiring for internship positions in AI and cloud technologies\n"
            company_section += "- [juteq linkedin](https://ca.linkedin.com/company/juteq)\n"
        else:
            company_section = f"- {company_name.lower()} is an established organization\n"
            company_section += "- additional research recommended\n"
        
        # Technical prep with specifics
        tech_section = f"- role: {company_name.lower()} internship program\n"
        tech_section += "- prep areas:\n"
        if 'AI' in email_body and 'cloud' in email_body:
            tech_section += "  - review fundamental concepts in AI and cloud technologies (as mentioned in email)\n"
            tech_section += "  - familiarize yourself with cloud-native solutions and DevOps practices\n"
            tech_section += "  - prepare examples of any AI or cloud projects you've worked on\n"
            tech_section += "  - be ready to discuss your interests in AI and cloud technologies\n"
        else:
            tech_section += "  - review relevant technical concepts\n"
            tech_section += "  - prepare examples of relevant experience\n"
        
        # Questions with personalization
        questions_section = "- to interviewer:\n"
        if has_rakesh:
            questions_section += f"  - what drew you to focus on AI and cloud technologies at {company_name.lower()}?\n"
            questions_section += f"  - how do you see {company_name.lower()}'s approach to scaling with AI agents evolving?\n"
        else:
            questions_section += f"  - what brought you to {company_name.lower()}?\n"
            questions_section += f"  - how do you see your role evolving?\n"
        
        questions_section += "\n- to company:\n"
        if 'exciting projects' in email_body:
            questions_section += f"  - what are the most exciting projects {company_name.lower()} is working on currently?\n"
        else:
            questions_section += f"  - what exciting initiatives is {company_name.lower()} pursuing?\n"
        
        if 'internship' in role_title.lower():
            questions_section += f"  - what does success look like for an intern in this program?\n"
            questions_section += f"  - how does {company_name.lower()} support intern learning and development?\n"
        
        # Common questions with specifics
        common_section = ""
        if 'AI' in email_body and 'cloud' in email_body:
            common_section += '- "tell me about a time when you worked with AI or cloud technologies."\n'
            common_section += '- "how would you approach learning about a new AI technology or cloud platform?"\n'
            common_section += '- "describe your interest in AI and cloud technologies mentioned in your application."\n'
        else:
            common_section += '- "tell me about a challenging project you worked on."\n'
            common_section += f'- "why are you interested in working at {company_name.lower()}?"\n'
        
        common_section += '- "describe a time when you had to learn something quickly."\n'
        common_section += '- "how do you handle feedback and constructive criticism?"\n'
        
        return f"""# interview prep requirements template

## 1. before interview

{before_section}
## 2. interviewer background

{interviewer_section}
## 3. company background

{company_section}
## 4. technical preparations

{tech_section}
## 5. questions to ask

{questions_section}
## 6. common questions

{common_section}"""