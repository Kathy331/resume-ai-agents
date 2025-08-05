#pipelines/prep_guide_pipeline.py
"""
Enhanced Prep Guide Pipeline - Better Structure and Citations
============================================================
Generates comprehensive, well-structured interview prep guides with:
1. Professional formatting and clear sections
2. Proper citation integration with source validation
3. Strategic content organization
4. Actionable advice and talking points
5. Clean, readable output format
"""

import os
import sys
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.openai_client import get_openai_client


class PrepGuidePipeline:
    """
    Enhanced Prep Guide Pipeline with improved structure and citations
    """
    
    def __init__(self):
        self.client = get_openai_client()
    
    def generate_prep_guide(self, email: Dict[str, Any], entities: Dict[str, Any], 
                          research_result: Dict[str, Any], email_index: int,
                          detailed_logs: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive interview prep guide with proper citations
        
        Args:
            email: Original email data
            entities: Extracted entities
            research_result: Deep research results
            email_index: Email index
            detailed_logs: Processing logs
            
        Returns:
            Prep guide generation result
        """
        print(f"\n📚 PREP GUIDE PIPELINE - Email {email_index}")
        print("=" * 60)
        
        generation_start_time = datetime.now()
        
        # Extract key information
        company = self._get_entity_string(entities.get('company', ''))
        role = self._get_entity_string(entities.get('role', ''))
        interviewer = self._get_entity_string(entities.get('interviewer', ''))
        
        if not company:
            return {
                'success': False,
                'error': 'No company identified for prep guide generation',
                'company_keyword': '',
                'output_file': ''
            }
        
        # Prepare citations database
        citations_db = research_result.get('citations_database', {})
        validated_citations = self._prepare_citations_for_guide(citations_db)
        
        print(f"🎯 Generating prep guide for: {company}")
        print(f"💼 Role: {role}")
        print(f"👤 Interviewer: {interviewer}")
        print(f"📝 Available Citations: {len(validated_citations)}")
        
        try:
            # Generate the prep guide content
            prep_guide_content = self._generate_prep_guide_content(
                email, entities, research_result, validated_citations
            )
            
            # Generate processing summary
            processing_summary = self._generate_processing_summary(
                email, entities, research_result, detailed_logs
            )
            
            # Create complete output
            complete_output = self._create_complete_output(
                email, entities, research_result, prep_guide_content, 
                processing_summary, validated_citations
            )
            
            # Save to file
            company_keyword = self._clean_company_name(company)
            output_file = self._save_prep_guide(complete_output, company_keyword)
            
            result = {
                'success': True,
                'prep_guide_content': prep_guide_content,
                'citations_used': len(validated_citations),
                'company_keyword': company_keyword,
                'output_file': output_file,
                'generation_time': (datetime.now() - generation_start_time).total_seconds()
            }
            
            print(f"✅ Prep guide generated successfully!")
            print(f"📁 Saved as: {output_file}")
            print(f"📊 Citations used: {len(validated_citations)}")
            print(f"⏱️  Generation time: {result['generation_time']:.2f}s")
            
            return result
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'company_keyword': company_keyword if 'company_keyword' in locals() else '',
                'output_file': '',
                'generation_time': (datetime.now() - generation_start_time).total_seconds()
            }
    
    def _get_entity_string(self, entity_value):
        """Convert entity to string, handling lists"""
        if isinstance(entity_value, list):
            return entity_value[0] if entity_value else ''
        return str(entity_value) if entity_value else ''
    
    def _prepare_citations_for_guide(self, citations_db: Dict) -> List[Dict]:
        """Prepare and validate citations for the prep guide"""
        validated_citations = []
        
        for citation_id, citation_data in citations_db.items():
            if isinstance(citation_data, dict) and citation_data.get('source'):
                # Parse the source to extract title and URL
                source_text = citation_data.get('source', '')
                
                # Try to split title and URL
                if ' - http' in source_text:
                    title, url = source_text.split(' - http', 1)
                    url = 'http' + url
                elif ' - ' in source_text:
                    parts = source_text.split(' - ', 1)
                    title = parts[0]
                    url = parts[1] if len(parts) > 1 else ''
                else:
                    title = source_text
                    url = ''
                
                validated_citations.append({
                    'id': citation_id,
                    'title': title.strip(),
                    'url': url.strip(),
                    'snippet': citation_data.get('content_snippet', ''),
                    'agent': citation_data.get('agent', 'research')
                })
        
        return validated_citations
    
    def _generate_prep_guide_content(self, email: Dict, entities: Dict, 
                                   research_result: Dict, citations: List[Dict]) -> str:
        """Generate the main prep guide content using OpenAI"""
        
        # Prepare context for AI
        company = self._get_entity_string(entities.get('company', ''))
        role = self._get_entity_string(entities.get('role', ''))
        interviewer = self._get_entity_string(entities.get('interviewer', ''))
        
        # Extract research insights
        research_data = research_result.get('research_data', {})
        company_analysis = research_data.get('company_analysis', {})
        role_analysis = research_data.get('role_analysis', {})
        interviewer_analysis = research_data.get('interviewer_analysis', {})
        
        # Prepare citation context
        citation_context = ""
        for i, citation in enumerate(citations[:10], 1):  # Use top 10 citations
            citation_context += f"Citation {i}: {citation['title']}\nSource: {citation['url']}\nContent: {citation['snippet'][:300]}...\n\n"
        
        prompt = f"""
You are an expert interview preparation consultant. Create a comprehensive, professional interview prep guide.

**INTERVIEW CONTEXT:**
- Company: {company}
- Role: {role}
- Interviewer: {interviewer}
- Email Subject: {email.get('subject', '')}

**RESEARCH INSIGHTS:**
Company Analysis: {company_analysis.get('analysis_summary', 'No company analysis available')}
Role Analysis: {role_analysis.get('analysis_summary', 'No role analysis available')}  
Interviewer Analysis: {interviewer_analysis.get('analysis_summary', 'No interviewer analysis available')}

**AVAILABLE CITATIONS:**
{citation_context}

**INSTRUCTIONS:**
1. Create a comprehensive, actionable prep guide with 7 main sections
2. Use citations naturally within the content using the format [Citation X]
3. Provide specific, actionable advice rather than generic tips
4. Include strategic questions to ask the interviewer
5. Make the content professional and interview-focused
6. Ensure each section has substantial, valuable content

**OUTPUT FORMAT:**
Generate a well-structured prep guide with these sections:

## 1. Executive Summary & Strategy
- Key interview objectives and positioning strategy
- 3-4 bullet points with specific preparation priorities

## 2. Company Intelligence Deep Dive  
- Company background, recent developments, and strategic position
- Industry context and competitive landscape
- Culture and values alignment points
- Use citations where appropriate: [Citation X]

## 3. Role Analysis & Positioning
- Detailed role responsibilities and requirements
- Key skills to emphasize during the interview
- Success metrics and growth opportunities
- Strategic positioning for this specific role

## 4. Interviewer Intelligence & Connection Strategy
- Interviewer background and expertise areas
- Professional interests and recent activities  
- Strategic connection points and conversation topics
- Communication style recommendations

## 5. Strategic Questions Framework
- Company-specific questions (3-4 strategic questions)
- Role and growth questions (2-3 focused questions)
- Interviewer-specific questions (2 personalized questions)
- Industry and market questions (2 forward-looking questions)

## 6. Conversation Flow & Talking Points
- Natural conversation starters and hooks
- Key achievements to highlight strategically
- Industry trends and insights to discuss
- Professional stories that demonstrate value

## 7. Execution Checklist & Timeline
- 24-48 hours before: Research and preparation tasks
- Day of interview: Setup and mindset preparation  
- During interview: Key tactics and approaches
- Post-interview: Follow-up strategy

Make this comprehensive, specific, and immediately actionable for interview success.
"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert interview preparation consultant who creates comprehensive, actionable prep guides."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"❌ Error generating prep guide content: {str(e)}")
            return f"Error generating prep guide: {str(e)}"
    
    def _generate_processing_summary(self, email: Dict, entities: Dict, 
                                   research_result: Dict, detailed_logs: Dict) -> str:
        """Generate detailed processing summary"""
        
        # Extract metrics from research results
        validation_metrics = research_result.get('validation_metrics', {})
        
        summary = f"""
================================================================================
INTERVIEW PREPARATION PROCESSING SUMMARY
================================================================================
Company: {self._get_entity_string(entities.get('company', 'Unknown'))}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Processing Quality: {research_result.get('research_quality', 'Unknown')}

This file contains the complete results from processing an interview email
through the Interview Prep Workflow including Classification, Entity Extraction,
Deep Research, and Personalized Prep Guide generation.

================================================================================
ORIGINAL EMAIL DATA
================================================================================
From: {email.get('from', 'Unknown')}
Subject: {email.get('subject', 'No subject')}
Date: {email.get('date', 'Unknown')}
Body: {email.get('body', 'No body')[:500]}{'...' if len(email.get('body', '')) > 500 else ''}

================================================================================
PROCESSING PIPELINE RESULTS
================================================================================

📧 EMAIL PIPELINE PROCESSING:
✅ Email Classification: Interview Email Detected
✅ Entity Extraction: {len(entities)} entities extracted
✅ Memory Check: New interview (not previously processed)

🔬 DEEP RESEARCH PIPELINE PROCESSING:
📊 Research Overview:
   🔍 Total Sources Discovered: {validation_metrics.get('sources_discovered', 0)}
   ✅ Sources Validated: {validation_metrics.get('sources_validated', 0)}
   📝 Citations Generated: {validation_metrics.get('citation_count', 0)}
   🔗 LinkedIn Profiles Found: {validation_metrics.get('linkedin_profiles_found', 0)}
   ⏱️  Processing Time: {research_result.get('processing_time', 0):.1f}s

🏢 Company Analysis Results:
   📈 Confidence Score: {research_result.get('research_data', {}).get('company_analysis', {}).get('confidence_score', 0):.2f}
   ✅ Sources Validated: {len(research_result.get('research_data', {}).get('company_analysis', {}).get('validated_sources', []))}

👤 Interviewer Analysis Results:
   📈 Confidence Score: {research_result.get('research_data', {}).get('interviewer_analysis', {}).get('confidence_score', 0):.2f}
   🔗 LinkedIn Profiles Found: {research_result.get('research_data', {}).get('interviewer_analysis', {}).get('linkedin_profiles_found', 0)}

🤔 Research Quality Assessment:
   📊 Overall Confidence: {research_result.get('overall_confidence', 0):.2f}
   🏆 Research Quality: {research_result.get('research_quality', 'Unknown')}
   📚 Sufficient for Prep Guide: {'Yes' if research_result.get('sufficient_for_prep_guide', False) else 'No'}

================================================================================
CITATIONS DATABASE
================================================================================
Complete database of all research citations used in the preparation guide:
"""
        return summary
    
    def _create_complete_output(self, email: Dict, entities: Dict, research_result: Dict,
                              prep_guide_content: str, processing_summary: str, 
                              citations: List[Dict]) -> str:
        """Create the complete output file content"""
        
        company = self._get_entity_string(entities.get('company', 'Unknown'))
        
        # Create citation database section
        citations_section = ""
        for citation in citations:
            citations_section += f"📝 Citation [{citation['id']}]: {citation['title']} - {citation['url']}\n"
        
        complete_output = f"""{processing_summary}

{citations_section}

Total Citations: {len(citations)}

================================================================================
COMPREHENSIVE INTERVIEW PREPARATION GUIDE
================================================================================

{prep_guide_content}

================================================================================
TECHNICAL METADATA
================================================================================
Workflow Version: Interview Prep Workflow v2.0
Pipeline Stages Completed:
- ✅ Email Classification
- ✅ Entity Extraction  
- ✅ Deep Research with Tavily
- ✅ Research Quality Assessment
- ✅ Prep Guide Generation
- ✅ File Output

Processing Errors: {research_result.get('errors', [])}
Company Keyword: {company}
Research Quality: {research_result.get('research_quality', 'Unknown')}
Overall Confidence: {research_result.get('overall_confidence', 0):.2f}

Generated by Interview Prep AI Agent - Enhanced Pipeline v2.0
================================================================================"""
        
        return complete_output
    
    def _clean_company_name(self, company: str) -> str:
        """Clean company name for file naming"""
        # Remove special characters and spaces, keep only alphanumeric
        cleaned = re.sub(r'[^a-zA-Z0-9]', '', company)
        return cleaned[:20] if cleaned else 'Unknown'
    
    def _save_prep_guide(self, content: str, company_keyword: str) -> str:
        """Save prep guide to file"""
        try:
            # Create output directory
            output_dir = 'outputs/fullworkflow'
            os.makedirs(output_dir, exist_ok=True)
            
            # Generate filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{company_keyword}_{timestamp}.txt"
            filepath = os.path.join(output_dir, filename)
            
            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return filename
            
        except Exception as e:
            print(f"❌ Error saving prep guide: {str(e)}")
            return f"Error_saving_{company_keyword}.txt"