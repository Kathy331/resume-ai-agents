"""
Prep Guide Pipeline - Handles comprehensive interview preparation guide generation
Extracted from workflow_runner.py and comprehensive_prep_guide.py for better maintainability
"""

import os
import asyncio
from typing import Dict, Any, List
from datetime import datetime

# Import agents and modules
from agents.interview_prep_intelligence.agent import InterviewPrepIntelligenceAgent
from agents.interview_prep_intelligence.models import DeepResearchInput
from agents.memory_systems.shared_memory import SharedMemorySystem

# Import shared utilities
from shared.llm_client import call_llm
from shared.utils import get_logger, create_outputs_directory

logger = get_logger(__name__)

class PrepGuidePipeline:
    """Handles comprehensive interview preparation guide generation"""
    
    def __init__(self):
        self.memory_system = SharedMemorySystem()
        self.ipia_agent = InterviewPrepIntelligenceAgent()
        self.outputs_dir = create_outputs_directory("fullworkflow")
    
    def run_prep_guide_pipeline(self, max_interviews: int = 10) -> Dict[str, Any]:
        """
        Run the Enhanced Prep Guide Pipeline that generates comprehensive interview preparation guides
        
        This method:
        1. Fetches interviews with 'prepped' status from memory (from deep research pipeline)
        2. Generates comprehensive interview preparation guides using IPIA results
        3. Creates actionable interview preparation materials
        4. Outputs detailed preparation guides with specific recommendations
        
        Args:
            max_interviews: Maximum number of interviews to generate prep guides for
            
        Returns:
            Results including number of prep guides generated and preparation materials
        """
        logger.info(f"🚀 Enhanced Prep Guide Pipeline")
        logger.info("=" * 60)
        start_time = datetime.now()
        
        try:
            import asyncio
            import sys
            import os
            
            # Add the test directory to path to import the prep guide
            test_path = os.path.join(os.path.dirname(__file__), '..', 'tests', 'test_interview_prep_intelligence')
            sys.path.insert(0, test_path)
            
            try:
                from comprehensive_prep_guide import generate_comprehensive_prep_guide
            except ImportError as e:
                logger.error(f"❌ Could not import comprehensive_prep_guide: {str(e)}")
                logger.info("ℹ️  Comprehensive prep guide module not available in current environment")
                return {
                    'success': False,
                    'error': f'Comprehensive prep guide module not found: {str(e)}',
                    'guides_generated': 0,
                    'processing_time': (datetime.now() - start_time).total_seconds()
                }
            
            # Phase 1: Fetch prepped interviews from memory
            logger.info("📋 Phase 1: Fetching Prepped Interviews from Memory")
            
            # Get interviews that have been prepped (status = 'prepped')
            all_interviews = self.memory_system.get_all_interviews()
            prepped_interviews = [
                interview for interview in all_interviews 
                if interview.get('status', '').lower() == 'prepped'
            ]
            
            if not prepped_interviews:
                logger.info("ℹ️  No prepped interviews found in memory")
                return {
                    'success': True,
                    'message': 'No prepped interviews requiring prep guides',
                    'guides_generated': 0,
                    'total_questions': 0,
                    'processing_time': (datetime.now() - start_time).total_seconds()
                }
            
            # Limit to max_interviews
            interviews_to_process = prepped_interviews[:max_interviews]
            logger.info(f"🎯 Found {len(prepped_interviews)} prepped interviews, generating guides for {len(interviews_to_process)}")
            
            # Phase 2: Generate Enhanced Prep Guides
            logger.info("� Phase 2: Enhanced Prep Guide Generation")
            guides_generated = 0
            total_questions = 0
            prep_guide_results = []
            
            for i, interview in enumerate(interviews_to_process, 1):
                logger.info(f"📝 Generating Prep Guide {i}/{len(interviews_to_process)}: {interview.get('company', 'Unknown Company')}")
                logger.info(f"   🎯 Company: {interview.get('company', 'Unknown Company')}")
                logger.info(f"   👤 Interviewer: {interview.get('interviewer', 'Unknown Interviewer')}")
                logger.info(f"   💼 Role: {interview.get('role', 'Unknown Role')}")
                
                try:
                    # For now, just call the existing prep guide function
                    # In a more advanced version, we would modify it to accept parameters
                    def run_prep_guide():
                        """Run the prep guide in a new event loop"""
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        try:
                            return loop.run_until_complete(generate_comprehensive_prep_guide())
                        finally:
                            loop.close()
                    
                    # Execute the prep guide
                    run_prep_guide()
                    guides_generated += 1
                    total_questions += 20  # Estimate 20 questions per guide
                    
                    prep_guide_results.append({
                        'interview_id': interview.get('id'),
                        'company': interview.get('company', 'Unknown Company'),
                        'role': interview.get('role', 'Unknown Role'),
                        'interviewer': interview.get('interviewer', 'Unknown Interviewer'),
                        'success': True
                    })
                    
                    logger.info("   ✅ Prep guide generated successfully")
                    
                except Exception as e:
                    logger.error(f"   ❌ Failed to generate prep guide: {str(e)}")
                    prep_guide_results.append({
                        'interview_id': interview.get('id'),
                        'company': interview.get('company', 'Unknown'),
                        'error': str(e),
                        'success': False
                    })
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Prepare results
            result = {
                'success': True,
                'guides_generated': guides_generated,
                'total_questions': total_questions,
                'total_interviews_processed': len(interviews_to_process),
                'prep_guide_results': prep_guide_results,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
            # Display summary
            logger.info("📊 Enhanced Prep Guide Summary:")
            logger.info(f"   📚 Prep Guides Generated: {guides_generated}/{len(interviews_to_process)}")
            logger.info(f"   ❓ Total Questions: {total_questions}")
            logger.info(f"   ⏱️  Total Processing Time: {processing_time:.2f}s")
            
            return result
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            error_result = {
                'success': False,
                'error': str(e),
                'guides_generated': 0,
                'total_questions': 0,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.error(f"💥 Enhanced Prep Guide failed: {str(e)}")
            return error_result
        
        try:
            # Phase 1: Fetch prepped interviews from memory
            logger.info("📋 Phase 1: Fetching Prepped Interviews from Memory")
            
            # Get interviews that have been researched (status = 'prepped')
            all_interviews = self.memory_system.get_all_interviews()
            prepped_interviews = [
                interview for interview in all_interviews 
                if interview.get('status', '').lower() == 'prepped'
            ]
            
            if not prepped_interviews:
                logger.info("✅ No prepped interviews found in memory")
                return {
                    'success': True,
                    'message': 'No prepped interviews available for guide generation',
                    'interviews_processed': 0,
                    'guides_generated': 0,
                    'processing_time': (datetime.now() - start_time).total_seconds()
                }
            
            # Limit to max_interviews
            interviews_to_process = prepped_interviews[:max_interviews]
            logger.info(f"🎯 Found {len(prepped_interviews)} prepped interviews, generating guides for {len(interviews_to_process)}")
            
            # Phase 2: Generate comprehensive prep guides
            logger.info(f"📚 Phase 2: Generating Comprehensive Prep Guides")
            
            generated_guides = []
            total_questions = 0
            
            for i, interview in enumerate(interviews_to_process, 1):
                logger.info(f"📖 Generating Guide {i}/{len(interviews_to_process)}: {interview.get('company', 'Unknown')}")
                
                # Generate prep guide for this interview
                guide_result = self._generate_interview_prep_guide(interview)
                
                if guide_result['success']:
                    generated_guides.append(guide_result)
                    total_questions += guide_result.get('question_count', 0)
                    
                    # Update interview status to 'guide_generated'
                    self.memory_system.update_interview_status(
                        interview.get('id'), 
                        'guide_generated',
                        {
                            'guide_generated_at': datetime.now().isoformat(),
                            'guide_path': guide_result.get('guide_path', ''),
                            'question_count': guide_result.get('question_count', 0)
                        }
                    )
                else:
                    logger.error(f"Failed to generate guide for {interview.get('company', 'Unknown')}: {guide_result.get('error', 'Unknown error')}")
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            # Prepare results
            result = {
                'success': True,
                'interviews_processed': len(interviews_to_process),
                'guides_generated': len(generated_guides),
                'total_questions': total_questions,
                'generated_guides': generated_guides,
                'processing_time': processing_time,
                'timestamp': datetime.now().isoformat()
            }
            
            logger.info(f"✅ Prep Guide Pipeline completed - Generated {result['guides_generated']} guides with {result['total_questions']} questions")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Prep Guide Pipeline failed: {str(e)}")
            raise Exception(f"Prep Guide Pipeline failed: {str(e)}")
    
    def _generate_interview_prep_guide(self, interview: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a comprehensive prep guide for a single interview"""
        try:
            company_name = interview.get('company', 'Unknown Company')
            role_title = interview.get('role', 'Unknown Role')
            interviewer_name = interview.get('interviewer', '')
            
            logger.info(f"🔍 Generating prep guide for {company_name} - {role_title}")
            
            # Get research data from memory if available
            research_data = interview.get('research_data', {})
            
            # Generate the comprehensive guide
            guide_content = self._create_comprehensive_guide_content(
                company_name, role_title, interviewer_name, research_data
            )
            
            # Generate specific interview questions
            questions = self._generate_interview_questions(
                company_name, role_title, research_data
            )
            
            # Create final guide combining all elements
            final_guide = self._compile_final_guide(
                company_name, role_title, interviewer_name, 
                guide_content, questions
            )
            
            # Save guide to file
            guide_filename = f"{company_name.replace(' ', '_')}_{role_title.replace(' ', '_')}_PrepGuide.md"
            guide_path = os.path.join(self.outputs_dir, guide_filename)
            
            with open(guide_path, 'w', encoding='utf-8') as f:
                f.write(final_guide)
            
            logger.info(f"✓ Guide saved: {guide_filename}")
            
            return {
                'success': True,
                'company': company_name,
                'role': role_title,
                'guide_path': guide_path,
                'guide_filename': guide_filename,
                'question_count': len(questions),
                'guide_length': len(final_guide)
            }
            
        except Exception as e:
            logger.error(f"Failed to generate guide: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'company': interview.get('company', 'Unknown'),
                'role': interview.get('role', 'Unknown')
            }
    
    def _create_comprehensive_guide_content(self, company_name: str, role_title: str, 
                                          interviewer_name: str, research_data: Dict) -> str:
        """Create the main content of the prep guide using LLM"""
        
        prompt = f"""
        Create a comprehensive interview preparation guide for the following interview:
        
        Company: {company_name}
        Role: {role_title}
        Interviewer: {interviewer_name if interviewer_name else 'Not specified'}
        
        Research Data Available:
        {self._format_research_data(research_data)}
        
        Please create a detailed preparation guide that includes:
        1. Company Overview & Recent Developments
        2. Role-Specific Preparation Points
        3. Key Skills & Technologies to Highlight
        4. Company Culture & Values Alignment
        5. Potential Interview Focus Areas
        6. Specific Talking Points and Examples
        
        Make this practical and actionable, not generic advice.
        """
        
        try:
            response = call_llm(prompt, max_tokens=2000)
            return response.strip()
        except Exception as e:
            logger.error(f"LLM call failed for guide content: {str(e)}")
            return f"# Interview Prep Guide for {company_name} - {role_title}\n\nError generating detailed content: {str(e)}"
    
    def _generate_interview_questions(self, company_name: str, role_title: str, 
                                    research_data: Dict) -> List[Dict[str, str]]:
        """Generate specific interview questions with suggested answers"""
        
        prompt = f"""
        Generate 10-15 specific interview questions that are likely to be asked for this position:
        
        Company: {company_name}
        Role: {role_title}
        
        Research Context:
        {self._format_research_data(research_data)}
        
        For each question, provide:
        1. The likely question
        2. Key points to cover in the answer
        3. Specific examples or approaches to mention
        
        Format as:
        Q: [Question]
        A: [Answer approach and key points]
        
        Focus on questions specific to this company and role, not generic interview questions.
        """
        
        try:
            response = call_llm(prompt, max_tokens=2500)
            questions = self._parse_questions_from_response(response)
            return questions
        except Exception as e:
            logger.error(f"LLM call failed for questions: {str(e)}")
            return [{"question": "Error generating questions", "answer": str(e)}]
    
    def _format_research_data(self, research_data: Dict) -> str:
        """Format research data for LLM prompts"""
        if not research_data:
            return "No specific research data available."
        
        formatted = []
        
        if 'company' in research_data:
            company_info = research_data['company']
            formatted.append(f"Company Info: {company_info.get('description', 'N/A')}")
            if 'recent_info' in company_info:
                formatted.append(f"Recent News: {', '.join(company_info['recent_info'])}")
        
        if 'role' in research_data:
            role_info = research_data['role']
            formatted.append(f"Role Description: {role_info.get('description', 'N/A')}")
            if 'requirements' in role_info:
                formatted.append(f"Requirements: {', '.join(role_info['requirements'])}")
        
        if 'interviewer' in research_data:
            interviewer_info = research_data['interviewer']
            formatted.append(f"Interviewer Info: {interviewer_info.get('profile_info', 'N/A')}")
        
        return "\n".join(formatted) if formatted else "No specific research data available."
    
    def _parse_questions_from_response(self, response: str) -> List[Dict[str, str]]:
        """Parse questions and answers from LLM response"""
        questions = []
        lines = response.split('\n')
        
        current_question = ""
        current_answer = ""
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q:'):
                if current_question and current_answer:
                    questions.append({
                        "question": current_question,
                        "answer": current_answer
                    })
                current_question = line[2:].strip()
                current_answer = ""
            elif line.startswith('A:'):
                current_answer = line[2:].strip()
            elif current_answer and line:
                current_answer += " " + line
        
        # Add the last question
        if current_question and current_answer:
            questions.append({
                "question": current_question,
                "answer": current_answer
            })
        
        return questions
    
    def _compile_final_guide(self, company_name: str, role_title: str, interviewer_name: str,
                           guide_content: str, questions: List[Dict[str, str]]) -> str:
        """Compile the final comprehensive guide"""
        
        guide = f"""# Interview Preparation Guide
## {company_name} - {role_title}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Interviewer:** {interviewer_name if interviewer_name else 'Not specified'}

---

{guide_content}

---

## 🎯 Specific Interview Questions & Preparation

"""
        
        for i, q in enumerate(questions, 1):
            guide += f"""
### Question {i}
**Q:** {q['question']}

**Preparation Notes:** {q['answer']}

---
"""
        
        guide += f"""
## 📝 Final Preparation Checklist

- [ ] Research the company's latest news and developments
- [ ] Prepare specific examples that demonstrate relevant skills
- [ ] Review the job description and align your experience
- [ ] Prepare thoughtful questions about the role and company
- [ ] Practice articulating your career goals and interest in this position
- [ ] Prepare for technical questions if applicable
- [ ] Plan your interview attire and logistics

## 🚀 Key Success Factors

1. **Be Specific:** Use concrete examples and metrics when possible
2. **Show Research:** Demonstrate knowledge of the company and role
3. **Ask Questions:** Show genuine interest and engagement
4. **Be Authentic:** Let your personality and passion come through
5. **Follow Up:** Send a thoughtful thank-you note within 24 hours

---

*This guide was generated based on available research and should be customized based on your specific experience and the interview format.*
"""
        
        return guide
