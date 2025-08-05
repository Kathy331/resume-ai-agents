#shared/prep_guide_prompts.py
"""
Prep Guide Prompt Templates - Professional Interview Preparation
===============================================================
Enhanced prompt templates for generating comprehensive, actionable interview prep guides
with proper citation integration and strategic content structure.
"""

from typing import Dict, List, Any, Optional


class PrepGuidePromptTemplates:
    """
    Enhanced prompt templates for interview prep guide generation
    """
    
    @staticmethod
    def get_comprehensive_prep_guide_prompt(
        email: Dict, entities: Dict, research_result: Dict, 
        citation_context: str, research_insights: Dict
    ) -> str:
        """
        Generate the main comprehensive prep guide prompt
        
        Args:
            email: Original email data
            entities: Extracted entities
            research_result: Deep research results
            citation_context: Formatted citation context
            research_insights: Processed research insights
            
        Returns:
            Formatted prompt for AI generation
        """
        
        company = PrepGuidePromptTemplates._get_entity_string(entities.get('company', ''))
        role = PrepGuidePromptTemplates._get_entity_string(entities.get('role', ''))
        interviewer = PrepGuidePromptTemplates._get_entity_string(entities.get('interviewer', ''))
        
        prompt = f"""You are a senior interview preparation consultant with expertise in tech industry interviews. Create a comprehensive, strategic interview prep guide that goes beyond generic advice.

INTERVIEW CONTEXT:
=================
• Company: {company}
• Role: {role}
• Interviewer: {interviewer}
• Email Subject: {email.get('subject', 'No subject')}
• Interview Format: {PrepGuidePromptTemplates._get_entity_string(entities.get('format', 'Not specified'))}
• Interview Date: {PrepGuidePromptTemplates._get_entity_string(entities.get('date', 'Not specified'))}

RESEARCH INTELLIGENCE:
====================
{research_insights.get('company_summary', 'No company analysis available')}

{research_insights.get('role_summary', 'No role analysis available')}

{research_insights.get('interviewer_summary', 'No interviewer analysis available')}

{citation_context}

DELIVERABLE REQUIREMENTS:
========================
Create a comprehensive, immediately actionable prep guide with these exact sections:

## 1. Executive Summary & Strategic Positioning

**Interview Objective:** [Clear 1-sentence goal for this interview]

**Strategic Positioning:** [How to position yourself for maximum impact]

**Key Preparation Priorities:**
• [Priority 1 - specific action item]
• [Priority 2 - specific action item]  
• [Priority 3 - specific action item]

**Success Metrics:** [How to know if the interview went well]

## 2. Company Intelligence & Market Context

**Company Overview:**
[2-3 sentences about the company's mission, stage, and market position. Use citations: [Citation X]]

**Recent Developments:**
[Key recent news, funding, product launches, or strategic moves. Use citations where applicable]

**Industry Position:**
[How the company fits in the competitive landscape]

**Cultural Insights:**
[Key values, work culture, and what they prioritize in employees]

**Strategic Talking Points:**
• [Specific insight about industry trends that shows your market awareness]
• [Company-specific observation that demonstrates research depth]
• [Strategic question or insight about their business model/growth]

## 3. Role Analysis & Technical Positioning

**Role Breakdown:**
[Detailed analysis of key responsibilities and expectations]

**Critical Skills to Emphasize:**
• [Technical skill 1 - why it matters for this role]
• [Technical skill 2 - specific examples to mention]
• [Soft skill - how it applies to their challenges]

**Success Factors:**
[What makes someone successful in this specific role at this company]

**Growth Trajectory:**
[Career progression opportunities and skill development paths]

**Positioning Strategy:**
[How to present your background to align perfectly with their needs]

## 4. Interviewer Intelligence & Connection Strategy

**Interviewer Background:**
[Professional background, expertise areas, and career journey. Use citations: [Citation X]]

**Communication Style:**
[How to adapt your communication approach for this interviewer]

**Expertise Areas:**
[Technical domains or business areas they're passionate about]

**Connection Opportunities:**
• [Shared interest or experience to mention]
• [Professional topic that would engage them]
• [Industry trend or challenge they likely care about]

**Conversation Starters:**
[Specific, personalized ways to build rapport and demonstrate research]

## 5. Strategic Question Framework

**Company Vision & Strategy (Ask 2-3):**
• [Question about company direction/strategy]
• [Question about market opportunity or challenges]
• [Question about competitive positioning]

**Role & Team Dynamics (Ask 2-3):**
• [Question about team structure and collaboration]
• [Question about success metrics and expectations]
• [Question about growth and development opportunities]

**Interviewer-Specific Questions (Ask 1-2):**
• [Personalized question based on their background]
• [Question about their experience or perspective]

**Industry & Technical Questions (Ask 1-2):**
• [Forward-looking question about industry trends]
• [Technical question relevant to the role]

## 6. Value Demonstration & Story Bank

**Core Value Proposition:**
[Your unique value in 2-3 sentences that directly addresses their needs]

**Strategic Stories to Tell:**
• **Technical Achievement:** [Specific example with metrics and impact]
• **Problem-Solving:** [Challenge you solved that's relevant to their business]
• **Leadership/Initiative:** [Time you drove results or led change]
• **Learning/Adaptation:** [How you've grown or adapted to new challenges]

**Metrics to Mention:**
[Specific numbers, percentages, or outcomes that demonstrate impact]

**Industry Insights to Share:**
[1-2 thoughtful observations about industry trends or best practices]

## 7. Execution Timeline & Tactical Checklist

**48 Hours Before:**
□ Review company's latest news and social media
□ Research recent industry developments
□ Prepare 3-4 specific questions about recent company developments
□ Practice your value proposition and key stories

**24 Hours Before:**
□ Review interviewer's recent LinkedIn activity or publications
□ Prepare environment for virtual interview (if applicable)
□ Practice technical explanations if relevant
□ Review job description one final time

**Day of Interview:**
□ Arrive 5-10 minutes early
□ Have notepad ready for taking notes
□ Prepare backup questions in case conversation flows quickly
□ Review your strategic positioning points

**During Interview - Key Tactics:**
• Start with genuine appreciation for their time
• Ask clarifying questions to show engagement
• Use specific examples rather than generic statements
• Reference your research naturally in conversation
• Take notes to show you value their insights

**Post-Interview (Within 24 Hours):**
□ Send personalized thank-you email referencing specific conversation points
□ Connect on LinkedIn with personalized message
□ Follow up on any commitments you made during the interview

CRITICAL REQUIREMENTS:
=====================
1. Use citations naturally throughout the content: [Citation X]
2. Make every recommendation specific and actionable
3. Avoid generic interview advice - everything should be tailored to this specific opportunity
4. Include concrete examples and talking points
5. Provide strategic depth that shows sophisticated preparation
6. Ensure professional tone while being personable and confident
7. Focus on value creation and mutual fit, not just "getting the job"

Generate a comprehensive prep guide that positions the candidate as a strategic, well-prepared professional who has done their homework and understands the business context of this opportunity."""

        return prompt
    
    @staticmethod
    def get_research_insights_summary(research_data: Dict) -> Dict[str, str]:
        """
        Extract and format research insights for prompt inclusion
        
        Args:
            research_data: Research results from deep research pipeline
            
        Returns:
            Dictionary with formatted research summaries
        """
        insights = {}
        
        # Company analysis summary
        company_analysis = research_data.get('company_analysis', {})
        if company_analysis.get('success'):
            insights['company_summary'] = f"""
COMPANY ANALYSIS RESULTS:
• Analysis Quality: {company_analysis.get('confidence_score', 0):.1f}/1.0 confidence
• Sources Validated: {len(company_analysis.get('validated_sources', []))}
• Key Insight: {company_analysis.get('analysis_summary', 'Company analysis completed')}
• Industry Context: {company_analysis.get('industry_analysis', 'Industry position analyzed')}
"""
        else:
            insights['company_summary'] = "COMPANY ANALYSIS: Limited company information available"
        
        # Role analysis summary  
        role_analysis = research_data.get('role_analysis', {})
        if role_analysis.get('success'):
            insights['role_summary'] = f"""
ROLE ANALYSIS RESULTS:
• Analysis Quality: {role_analysis.get('confidence_score', 0):.1f}/1.0 confidence
• Sources Validated: {len(role_analysis.get('validated_sources', []))}
• Key Insight: {role_analysis.get('analysis_summary', 'Role analysis completed')}
• Skills Focus: {role_analysis.get('role_insights', 'Role requirements analyzed')}
"""
        else:
            insights['role_summary'] = "ROLE ANALYSIS: Limited role information available"
        
        # Interviewer analysis summary
        interviewer_analysis = research_data.get('interviewer_analysis', {})
        if interviewer_analysis.get('success'):
            linkedin_count = interviewer_analysis.get('linkedin_profiles_found', 0)
            insights['interviewer_summary'] = f"""
INTERVIEWER ANALYSIS RESULTS:
• Analysis Quality: {interviewer_analysis.get('confidence_score', 0):.1f}/1.0 confidence
• LinkedIn Profiles Found: {linkedin_count}
• Key Insight: {interviewer_analysis.get('analysis_summary', 'Interviewer background researched')}
• Connection Strategy: {interviewer_analysis.get('linkedin_analysis', 'Professional background analyzed')}
"""
        else:
            insights['interviewer_summary'] = "INTERVIEWER ANALYSIS: Limited interviewer information available"
        
        return insights
    
    @staticmethod
    def get_post_generation_review_prompt(prep_guide_content: str, citations_used: int) -> str:
        """
        Generate prompt for reviewing and improving the prep guide
        
        Args:
            prep_guide_content: Generated prep guide content
            citations_used: Number of citations used
            
        Returns:
            Review and improvement prompt
        """
        
        return f"""You are a senior interview preparation consultant reviewing a prep guide for quality and completeness.

REVIEW CRITERIA:
===============
1. **Content Depth**: Are all sections substantial and actionable?
2. **Citation Integration**: Are {citations_used} citations used naturally and appropriately?
3. **Strategic Value**: Does this go beyond generic advice to provide strategic insights?
4. **Actionability**: Can the candidate immediately use these recommendations?
5. **Professional Tone**: Is the tone confident and professional?

PREP GUIDE TO REVIEW:
====================
{prep_guide_content}

REVIEW TASK:
===========
Provide a brief assessment (3-4 sentences) covering:
1. Overall quality rating (Excellent/Good/Needs Improvement)
2. Strongest aspects of the guide
3. Any gaps or areas for improvement
4. Citation usage effectiveness

Then provide an improved version of any sections that need enhancement, maintaining the same structure but improving content quality, specificity, and strategic value.

Focus on making the guide more actionable and strategic rather than generic."""

    @staticmethod
    def _get_entity_string(entity_value) -> str:
        """Convert entity to string, handling lists"""
        if isinstance(entity_value, list):
            return entity_value[0] if entity_value else ''
        return str(entity_value) if entity_value else ''
    
    @staticmethod
    def get_section_enhancement_prompts() -> Dict[str, str]:
        """
        Get specific prompts for enhancing individual sections
        
        Returns:
            Dictionary of section-specific enhancement prompts
        """
        return {
            'executive_summary': """
Make this executive summary more strategic and specific:
• Clear, measurable interview objective
• Unique positioning strategy based on research
• 3 concrete preparation priorities with specific actions
• Measurable success criteria
""",
            
            'company_intelligence': """
Enhance company intelligence with:
• Specific recent developments with dates
• Competitive positioning insights
• Cultural values that matter for hiring
• Strategic business challenges they're facing
• Industry trends affecting their growth
""",
            
            'role_analysis': """
Improve role analysis with:
• Specific technical requirements and tools
• Day-to-day responsibilities breakdown
• Success metrics and KPIs for the role
• Growth trajectory and skill development paths
• Team structure and collaboration patterns
""",
            
            'interviewer_intelligence': """
Enhance interviewer section with:
• Specific professional background details
• Recent activities or publications
• Communication style preferences
• Technical expertise areas
• Personalized conversation starters
""",
            
            'strategic_questions': """
Improve questions with:
• Company-specific strategic questions
• Role-specific tactical questions
• Interviewer-personalized questions
• Forward-looking industry questions
• Follow-up question strategies
""",
            
            'value_demonstration': """
Enhance value demonstration with:
• Quantified achievement examples
• Role-relevant problem-solving stories
• Industry-specific technical insights
• Leadership and initiative examples
• Metrics and measurable outcomes
""",
            
            'execution_checklist': """
Improve execution plan with:
• Time-specific preparation tasks
• Technical setup requirements
• Conversation flow strategies
• Note-taking and engagement tactics
• Post-interview follow-up templates
"""
        }


# Export the main function for easy importing
__all__ = ['get_complete_prep_guide_prompt', 'PrepGuidePromptTemplates']


# Simple wrapper function for compatibility
def get_complete_prep_guide_prompt(
    company_name: str,
    interviewer_name: str,
    role_title: str,
    candidate_name: str,
    email_content: str,
    research_data: dict
) -> str:
    """Generate comprehensive prep guide prompt - wrapper function"""
    
    # Create mock entities and email objects for the class method
    mock_email = {
        'subject': f"Interview opportunity at {company_name}",
        'body': email_content
    }
    
    mock_entities = {
        'company': company_name,
        'interviewer': interviewer_name,
        'role': role_title,
        'candidate': candidate_name,
        'format': 'Not specified',
        'date': 'Not specified'
    }
    
    # Get research insights
    research_insights = PrepGuidePromptTemplates.get_research_insights_summary(research_data)
    
    # Create citation context
    citations_db = research_data.get('citations_database', {})
    citation_context = "RESEARCH SOURCES AVAILABLE:\n"
    for category, sources in citations_db.items():
        if sources:
            citation_context += f"• {category.title()}: {len(sources)} sources\n"
    
    # Use the class method
    return PrepGuidePromptTemplates.get_comprehensive_prep_guide_prompt(
        email=mock_email,
        entities=mock_entities,
        research_result=research_data,
        citation_context=citation_context,
        research_insights=research_insights
    )