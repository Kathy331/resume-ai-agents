#!/usr/bin/env python3
"""
Enhanced Prep Guide Pipeline with Reflection System
==================================================
Implements the comprehensive prep guide guidelines with:
1. 8-section structured format with emoji organization
2. Three-stage reflection and validation loops
3. Proper citation system with working links
4. Quality metrics and scoring
5. Content completeness validation
6. Personalization enhancement
7. Actionability verification
"""

import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import re

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.llm_client import call_llm
from shared.tavily_client import search_tavily


class EnhancedPrepGuidePipeline:
    """
    Enhanced Prep Guide Pipeline with comprehensive guidelines implementation
    """
    
    def __init__(self):
        self.outputs_dir = "outputs/fullworkflow"
        os.makedirs(self.outputs_dir, exist_ok=True)
        self.guidelines_path = "docs/guidelines/prep_guide.md"
        self.max_reflections = 3
    
    def generate_enhanced_prep_guide(self, email: Dict[str, Any], entities: Dict[str, Any], 
                                   research_result: Dict[str, Any], email_index: int) -> Dict[str, Any]:
        """
        Generate comprehensive prep guide following structured guidelines with reflection loops
        """
        print(f"\n📚 ENHANCED PREP GUIDE PIPELINE - Email {email_index}")
        print("=" * 70)
        
        result = {
            'success': False,
            'prep_guide_content': '',
            'company_keyword': '',
            'output_file': '',
            'quality_scores': {
                'content_depth': 0,
                'personalization': 0,
                'citation_quality': 0,
                'overall': 0
            },
            'reflection_iterations': 0,
            'sections_completed': [],
            'citations_count': 0,
            'processing_time': 0,
            'errors': []
        }
        
        start_time = datetime.now()
        
        try:
            # Load guidelines
            guidelines = self._load_prep_guide_guidelines()
            
            # Extract basic information
            company = self._extract_entity_string(entities.get('COMPANY', entities.get('company', '')))
            role = self._extract_entity_string(entities.get('ROLE', entities.get('role', '')))
            interviewer = self._extract_entity_string(entities.get('INTERVIEWER', entities.get('interviewer', '')))
            
            result['company_keyword'] = company.replace(' ', '_').lower() if company else 'unknown_company'
            
            print(f"🎯 Target: {company} - {role} - {interviewer}")
            
            # Stage 1: Initial prep guide generation
            print(f"\n📝 STAGE 1: Initial Prep Guide Generation")
            initial_guide = self._generate_initial_prep_guide(email, entities, research_result, guidelines)
            
            if not initial_guide['success']:
                result['errors'] = initial_guide['errors']
                return result
            
            current_guide = initial_guide['content']
            
            # Reflection Loop System
            for reflection_num in range(1, self.max_reflections + 1):
                print(f"\n🔍 REFLECTION {reflection_num}: Quality Enhancement")
                
                reflection_result = self._perform_reflection_loop(
                    current_guide, reflection_num, email, entities, research_result, guidelines
                )
                
                if reflection_result['improved']:
                    current_guide = reflection_result['enhanced_content']
                    print(f"✅ Reflection {reflection_num}: Content enhanced")
                else:
                    print(f"✅ Reflection {reflection_num}: No further improvements needed")
                    break
            
            result['reflection_iterations'] = reflection_num
            
            # Final quality assessment
            quality_scores = self._assess_guide_quality(current_guide)
            result['quality_scores'] = quality_scores
            
            # Extract sections and citations
            sections = self._extract_sections(current_guide)
            citations = self._count_citations(current_guide)
            
            result['prep_guide_content'] = current_guide
            result['sections_completed'] = sections
            result['citations_count'] = citations
            result['success'] = True
            
            # Save to file
            output_file = self._save_prep_guide(current_guide, result['company_keyword'], email_index)
            result['output_file'] = output_file
            
            # Display results
            self._display_prep_guide_results(result)
            
        except Exception as e:
            result['errors'].append(f"Pipeline error: {str(e)}")
            print(f"❌ Pipeline Error: {e}")
        
        result['processing_time'] = (datetime.now() - start_time).total_seconds()
        return result
    
    def _load_prep_guide_guidelines(self) -> str:
        """Load the prep guide guidelines from markdown file"""
        try:
            with open(self.guidelines_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"⚠️ Guidelines not found at {self.guidelines_path}")
            return ""
    
    def _extract_entity_string(self, entity_value) -> str:
        """Convert entity to string, handling lists"""
        if isinstance(entity_value, list):
            return entity_value[0] if entity_value else ''
        return str(entity_value) if entity_value else ''
    
    def _generate_initial_prep_guide(self, email: Dict[str, Any], entities: Dict[str, Any], 
                                   research_result: Dict[str, Any], guidelines: str) -> Dict[str, Any]:
        """Generate initial prep guide following structured format"""
        
        # Extract research data
        research_data = research_result.get('research_data', {})
        citations_db = research_result.get('citations_database', {})
        
        # Build citations reference
        citations_text = "\n".join([
            f"[{key}]: {citation.get('url', '#')} - {citation.get('title', 'Source')} ({citation.get('date', 'Date Unknown')})"
            for key, citation in citations_db.items()
        ])
        
        prompt = f"""
TASK: Generate a comprehensive interview prep guide following the structured guidelines below.

=== PREP GUIDE GUIDELINES ===
{guidelines}

=== INTERVIEW INFORMATION ===
Email Subject: {email.get('subject', 'Unknown')}
Email Content: {email.get('body', 'No content')[:1000]}...

Company: {entities.get('COMPANY', 'Unknown')}
Role: {entities.get('ROLE', 'Unknown')}  
Interviewer: {entities.get('INTERVIEWER', 'Unknown')}
Date/Time: {entities.get('DATE', 'Unknown')}

=== RESEARCH DATA ===
{research_data}

=== AVAILABLE CITATIONS ===
{citations_text}

REQUIREMENTS:
1. Follow the EXACT 8-section structure with emoji headers
2. Include specific, actionable content for each section
3. Use proper citations [Citation X] format throughout
4. Provide personalized, research-backed recommendations
5. Include working links and specific details
6. Make content immediately actionable for the candidate

Generate a comprehensive prep guide that follows the guidelines precisely.
"""
        
        try:
            response = call_llm(prompt, model="gpt-4o")
            
            if response and len(response.strip()) > 500:  # Ensure substantial content
                return {
                    'success': True,
                    'content': response,
                    'errors': []
                }
            else:
                return {
                    'success': False,
                    'content': '',
                    'errors': ['Generated content too short or empty']
                }
                
        except Exception as e:
            return {
                'success': False,
                'content': '',
                'errors': [f'LLM generation error: {str(e)}']
            }
    
    def _perform_reflection_loop(self, current_guide: str, reflection_num: int, 
                               email: Dict[str, Any], entities: Dict[str, Any], 
                               research_result: Dict[str, Any], guidelines: str) -> Dict[str, Any]:
        """Perform a reflection loop to enhance the prep guide"""
        
        reflection_prompts = {
            1: """
REFLECTION 1: Content Completeness Assessment

Analyze the prep guide below against the guidelines and identify:
1. Missing or incomplete sections
2. Claims lacking proper citations
3. Generic content that needs specific details
4. Information gaps requiring additional research

Focus on CONTENT COMPLETENESS and CITATION QUALITY.
""",
            2: """
REFLECTION 2: Personalization and Relevance Assessment

Analyze the prep guide for:
1. Company-specific insights and culture alignment
2. Interviewer-specific talking points and connection opportunities
3. Role-specific technical preparation and requirements
4. Authenticity and genuine research depth

Focus on PERSONALIZATION and RELEVANCE to the specific opportunity.
""",
            3: """
REFLECTION 3: Actionability and Practicality Assessment

Evaluate the prep guide for:
1. Realistic and achievable preparation timeline
2. Specific, actionable recommendations
3. Clear prioritization of most impactful activities
4. Practical execution guidance

Focus on ACTIONABILITY and PRACTICAL IMPLEMENTATION.
"""
        }
        
        reflection_prompt = f"""
{reflection_prompts.get(reflection_num, reflection_prompts[1])}

=== CURRENT PREP GUIDE ===
{current_guide}

=== GUIDELINES FOR REFERENCE ===
{guidelines[:2000]}...

=== AVAILABLE RESEARCH DATA ===
{research_result.get('research_data', {})}

TASK:
1. Identify specific areas for improvement
2. If improvements are needed, provide an ENHANCED version of the prep guide
3. If no significant improvements needed, respond with "NO_IMPROVEMENTS_NEEDED"

Focus on the reflection stage's specific criteria and make targeted enhancements.
"""
        
        try:
            response = call_llm(reflection_prompt, model="gpt-4o")
            
            if "NO_IMPROVEMENTS_NEEDED" in response.upper():
                return {
                    'improved': False,
                    'enhanced_content': current_guide,
                    'improvements': []
                }
            else:
                return {
                    'improved': True,
                    'enhanced_content': response,
                    'improvements': ['Content enhanced based on reflection']
                }
                
        except Exception as e:
            print(f"❌ Reflection {reflection_num} error: {e}")
            return {
                'improved': False,
                'enhanced_content': current_guide,
                'improvements': []
            }
    
    def _assess_guide_quality(self, guide_content: str) -> Dict[str, int]:
        """Assess the quality of the prep guide using defined metrics"""
        
        # Content Depth Assessment
        sections_present = len(re.findall(r'#{1,3}\s*\d+\.|\*\*\d+\.', guide_content))
        citations_present = len(re.findall(r'\[Citation \w+\]|\[\w+\]:', guide_content))
        specific_details = len(re.findall(r'https?://|@\w+|linkedin\.com|\d{4}-\d{2}-\d{2}', guide_content))
        
        content_depth = min(10, max(1, (sections_present * 2 + citations_present + specific_details // 2)))
        
        # Personalization Assessment
        company_mentions = len(re.findall(r'[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+Inc\.|Corp\.|LLC)?', guide_content))
        personal_references = len(re.findall(r'your|you\'re|candidate|interviewer', guide_content, re.IGNORECASE))
        specific_questions = len(re.findall(r'\?', guide_content))
        
        personalization = min(10, max(1, (company_mentions + personal_references // 3 + specific_questions // 2)))
        
        # Citation Quality Assessment
        working_links = len(re.findall(r'https?://[^\s\]]+', guide_content))
        citation_format = len(re.findall(r'\[.+?\]\(.+?\)', guide_content))
        
        citation_quality = min(10, max(1, (working_links + citation_format * 2)))
        
        # Overall Score
        overall = (content_depth + personalization + citation_quality) // 3
        
        return {
            'content_depth': content_depth,
            'personalization': personalization,
            'citation_quality': citation_quality,
            'overall': overall
        }
    
    def _extract_sections(self, guide_content: str) -> List[str]:
        """Extract completed sections from the guide"""
        sections = []
        
        section_patterns = [
            r'📄.*?Summary Overview',
            r'🏢.*?Company Snapshot',
            r'👔.*?Role Deep Dive',
            r'👩‍💻.*?Interviewer Intel',
            r'❓.*?Questions to Ask',
            r'📚.*?Technical Prep',
            r'🧠.*?Strategy.*?Framing',
            r'📋.*?Execution Plan'
        ]
        
        for pattern in section_patterns:
            if re.search(pattern, guide_content, re.IGNORECASE):
                sections.append(pattern.split('.*?')[1] if '.*?' in pattern else pattern)
        
        return sections
    
    def _count_citations(self, guide_content: str) -> int:
        """Count citations in the guide"""
        citations = len(re.findall(r'\[Citation \w+\]|\[\w+\]:', guide_content))
        links = len(re.findall(r'https?://[^\s\]]+', guide_content))
        return citations + links
    
    def _save_prep_guide(self, guide_content: str, company_keyword: str, email_index: int) -> str:
        """Save the prep guide to a file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"enhanced_prep_guide_{company_keyword}_email{email_index}_{timestamp}.txt"
        filepath = os.path.join(self.outputs_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"ENHANCED INTERVIEW PREP GUIDE\n")
                f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Company: {company_keyword.replace('_', ' ').title()}\n")
                f.write(f"Email Index: {email_index}\n")
                f.write("=" * 80 + "\n\n")
                f.write(guide_content)
                
            print(f"💾 Saved enhanced prep guide: {filename}")
            return filepath
            
        except Exception as e:
            print(f"❌ Error saving prep guide: {e}")
            return ""
    
    def _display_prep_guide_results(self, result: Dict[str, Any]) -> None:
        """Display comprehensive results of the prep guide generation"""
        
        print(f"\n📊 ENHANCED PREP GUIDE RESULTS")
        print("=" * 50)
        
        print(f"✅ Success: {result['success']}")
        print(f"🔄 Reflection Iterations: {result['reflection_iterations']}")
        print(f"📝 Sections Completed: {len(result['sections_completed'])}")
        print(f"🔗 Citations Count: {result['citations_count']}")
        print(f"⏱️ Processing Time: {result['processing_time']:.2f}s")
        
        print(f"\n📊 Quality Scores:")
        scores = result['quality_scores']
        print(f"   📖 Content Depth: {scores['content_depth']}/10")
        print(f"   🎯 Personalization: {scores['personalization']}/10")
        print(f"   🔗 Citation Quality: {scores['citation_quality']}/10")
        print(f"   📈 Overall Score: {scores['overall']}/10")
        
        if result['sections_completed']:
            print(f"\n✅ Completed Sections:")
            for section in result['sections_completed']:
                print(f"   • {section}")
        
        if result['errors']:
            print(f"\n❌ Errors:")
            for error in result['errors']:
                print(f"   • {error}")
        
        print(f"\n📄 Output File: {result['output_file']}")
        
        # Display preview of the content
        if result['prep_guide_content']:
            preview = result['prep_guide_content'][:500] + "..." if len(result['prep_guide_content']) > 500 else result['prep_guide_content']
            print(f"\n📖 Content Preview:")
            print("-" * 50)
            print(preview)
            print("-" * 50)
