# agents/interview_prep_intelligence/question_generator.py
"""
Multi-Agent Question Generator

Generates specialized interview questions using:
- Strategy-aware prompts for different question types
- Personalization engine for user-specific questions  
- Memory-augmented generation
- Skill matching and vector-based similarity
"""

import json
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime

from .models import Question, QuestionType, QuestionCluster
from .config import QUESTION_CONFIG, COT_PROMPTS, QUALITY_WEIGHTS
from shared.llm_client import get_llm_client


class QuestionGenerator:
    """
    Multi-agent question generator that creates specialized questions
    for different interview contexts and question types
    """
    
    def __init__(self):
        self.llm_client = get_llm_client()
        self.question_memory = {}  # Store generated questions for similarity checking
        
    def generate_question_clusters(self, insights: Dict[str, Any], user_profile: Optional[Dict] = None) -> Dict[str, QuestionCluster]:
        """
        Generate all question clusters for an interview
        
        Args:
            insights: Decomposed context insights
            user_profile: User's skills, experience, preferences
            
        Returns:
            Dict of question clusters by type
        """
        clusters = {}
        
        # Generate company-aware questions
        if "company_insights" in insights and "error" not in insights["company_insights"]:
            clusters["company"] = self._generate_company_questions(
                insights["company_insights"], user_profile
            )
        
        # Generate interviewer-specific questions  
        if "interviewer_insights" in insights and "error" not in insights["interviewer_insights"]:
            clusters["interviewer"] = self._generate_interviewer_questions(
                insights["interviewer_insights"], user_profile
            )
            
        # Generate role-specific questions
        if "role_insights" in insights and "error" not in insights["role_insights"]:
            clusters["role"] = self._generate_role_questions(
                insights["role_insights"], user_profile
            )
            
        # Generate behavioral questions (always generated)
        clusters["behavioral"] = self._generate_behavioral_questions(
            insights, user_profile
        )
        
        return clusters
    
    def _generate_company_questions(self, company_insights: Dict[str, Any], user_profile: Optional[Dict] = None) -> QuestionCluster:
        """Generate company-aware questions"""
        
        company_name = company_insights.get("company_name", "the company")
        
        # Create strategy-aware prompt
        strategy_prompt = f"""
        Generate interview questions that demonstrate deep company knowledge and cultural fit.
        
        Company Context:
        - Business Focus: {company_insights.get('business_focus', [])}
        - Values: {company_insights.get('company_values', [])}
        - Recent Developments: {company_insights.get('recent_developments', [])}
        - Culture: {company_insights.get('culture_indicators', [])}
        - Challenges: {company_insights.get('potential_challenges', [])}
        
        Question Strategy:
        1. Show you've researched the company thoroughly
        2. Demonstrate alignment with company values
        3. Address recent developments or challenges
        4. Show enthusiasm for the company's mission
        
        User Profile: {user_profile or "General candidate"}
        
        Generate 5-8 questions in this JSON format:
        {{
            "questions": [
                {{
                    "question_text": "Question here?",
                    "context": "Why this question matters",
                    "difficulty_level": "easy/medium/hard",
                    "expected_answer_points": ["point1", "point2"],
                    "follow_up_questions": ["follow up 1?", "follow up 2?"],
                    "source_research": "Which company insight inspired this"
                }}
            ]
        }}
        """
        
        try:
            response = self.llm_client.generate_text(
                prompt=strategy_prompt,
                max_tokens=1500,
                temperature=0.8,
                company_name=company_name
            )
            
            question_data = json.loads(response)
            questions = []
            
            for q_data in question_data.get("questions", []):
                question = Question(
                    id=str(uuid.uuid4()),
                    question_type=QuestionType.COMPANY_AWARE,
                    question_text=q_data["question_text"],
                    context=q_data["context"],
                    difficulty_level=q_data["difficulty_level"],
                    expected_answer_points=q_data["expected_answer_points"],
                    follow_up_questions=q_data.get("follow_up_questions", []),
                    source_research=q_data.get("source_research", "")
                )
                questions.append(question)
            
            return QuestionCluster(
                cluster_id=str(uuid.uuid4()),
                cluster_name=f"Company Knowledge - {company_name}",
                focus_area="company",
                questions=questions,
                priority_score=0.9,  # Company questions are high priority
                estimated_time_minutes=len(questions) * QUESTION_CONFIG["estimated_time_per_question"]
            )
            
        except Exception as e:
            # Return default questions if generation fails
            return self._create_default_company_cluster(company_name, str(e))
    
    def _generate_interviewer_questions(self, interviewer_insights: Dict[str, Any], user_profile: Optional[Dict] = None) -> QuestionCluster:
        """Generate interviewer-specific questions"""
        
        interviewer_name = interviewer_insights.get("interviewer_name", "the interviewer")
        
        strategy_prompt = f"""
        Generate questions tailored to this specific interviewer's background and style.
        
        Interviewer Context:
        - Background: {interviewer_insights.get('professional_background', [])}
        - Expertise: {interviewer_insights.get('expertise_areas', [])}
        - Communication Style: {interviewer_insights.get('communication_style', 'professional')}
        - Interview Focus: {interviewer_insights.get('likely_interview_focus', [])}
        - Interests: {interviewer_insights.get('personal_interests', [])}
        
        Question Strategy:
        1. Show you've researched the interviewer professionally  
        2. Align with their expertise and communication style
        3. Ask about their experience and perspectives
        4. Build rapport through shared interests/background
        
        User Profile: {user_profile or "General candidate"}
        
        Generate 4-6 personalized questions in this JSON format:
        {{
            "questions": [
                {{
                    "question_text": "Question here?",
                    "context": "Why this question works for this interviewer",
                    "difficulty_level": "easy/medium/hard",
                    "expected_answer_points": ["point1", "point2"],
                    "follow_up_questions": ["follow up 1?"],
                    "source_research": "Which interviewer insight inspired this"
                }}
            ]
        }}
        """
        
        try:
            response = self.llm_client.generate_text(
                prompt=strategy_prompt,
                max_tokens=1200,
                temperature=0.8,
                company_name=f"Interviewer: {interviewer_name}"
            )
            
            question_data = json.loads(response)
            questions = []
            
            for q_data in question_data.get("questions", []):
                question = Question(
                    id=str(uuid.uuid4()),
                    question_type=QuestionType.INTERVIEWER_SPECIFIC,
                    question_text=q_data["question_text"],
                    context=q_data["context"],
                    difficulty_level=q_data["difficulty_level"],
                    expected_answer_points=q_data["expected_answer_points"],
                    follow_up_questions=q_data.get("follow_up_questions", []),
                    source_research=q_data.get("source_research", "")
                )
                questions.append(question)
            
            return QuestionCluster(
                cluster_id=str(uuid.uuid4()),
                cluster_name=f"Interviewer Connection - {interviewer_name}",
                focus_area="interviewer",
                questions=questions,
                priority_score=0.8,
                estimated_time_minutes=len(questions) * QUESTION_CONFIG["estimated_time_per_question"]
            )
            
        except Exception as e:
            return self._create_default_interviewer_cluster(interviewer_name, str(e))
    
    def _generate_role_questions(self, role_insights: Dict[str, Any], user_profile: Optional[Dict] = None) -> QuestionCluster:
        """Generate role-specific questions with skill matching"""
        
        role_title = role_insights.get("role_title", "this role")
        
        # Skill matching logic
        user_skills = []
        if user_profile and "skills" in user_profile:
            user_skills = user_profile["skills"]
        
        strategy_prompt = f"""
        Generate role-specific questions that test competencies and demonstrate understanding.
        
        Role Context:
        - Technical Skills: {role_insights.get('core_technical_skills', [])}
        - Soft Skills: {role_insights.get('soft_skills_required', [])}
        - Responsibilities: {role_insights.get('key_responsibilities', [])}
        - Challenges: {role_insights.get('common_challenges', [])}
        - Growth: {role_insights.get('growth_opportunities', [])}
        - Success Metrics: {role_insights.get('success_metrics', [])}
        
        User Skills: {user_skills}
        
        Question Strategy:
        1. Test relevant technical and soft skills
        2. Address common role challenges
        3. Show understanding of success metrics
        4. Demonstrate growth mindset
        5. Match user's existing skills to role requirements
        
        Generate 6-8 role-focused questions in this JSON format:
        {{
            "questions": [
                {{
                    "question_text": "Question here?",
                    "context": "Why this question tests role competency",
                    "difficulty_level": "easy/medium/hard",
                    "expected_answer_points": ["point1", "point2"],
                    "follow_up_questions": ["follow up 1?"],
                    "source_research": "Which role insight inspired this"
                }}
            ]
        }}
        """
        
        try:
            response = self.llm_client.generate_text(
                prompt=strategy_prompt,
                max_tokens=1600,
                temperature=0.7,
                company_name=f"Role: {role_title}"
            )
            
            question_data = json.loads(response)
            questions = []
            
            for q_data in question_data.get("questions", []):
                question = Question(
                    id=str(uuid.uuid4()),
                    question_type=QuestionType.ROLE_SPECIFIC,
                    question_text=q_data["question_text"],
                    context=q_data["context"],
                    difficulty_level=q_data["difficulty_level"],
                    expected_answer_points=q_data["expected_answer_points"],
                    follow_up_questions=q_data.get("follow_up_questions", []),
                    source_research=q_data.get("source_research", "")
                )
                questions.append(question)
            
            return QuestionCluster(
                cluster_id=str(uuid.uuid4()),
                cluster_name=f"Role Competency - {role_title}",
                focus_area="role",
                questions=questions,
                priority_score=1.0,  # Role questions are highest priority
                estimated_time_minutes=len(questions) * QUESTION_CONFIG["estimated_time_per_question"]
            )
            
        except Exception as e:
            return self._create_default_role_cluster(role_title, str(e))
    
    def _generate_behavioral_questions(self, insights: Dict[str, Any], user_profile: Optional[Dict] = None) -> QuestionCluster:
        """Generate behavioral questions using cross-cutting themes"""
        
        # Extract context from insights
        company_name = insights.get("company_insights", {}).get("company_name", "Unknown")
        role_title = insights.get("role_insights", {}).get("role_title", "Unknown")
        interviewer_name = insights.get("interviewer_insights", {}).get("interviewer_name", "Unknown")
        
        cross_themes = insights.get("cross_cutting_themes", [])
        
        strategy_prompt = f"""
        Generate behavioral questions using the STAR method that assess fit and competencies.
        
        Context:
        - Company: {company_name}
        - Role: {role_title}  
        - Interviewer: {interviewer_name}
        - Cross-cutting Themes: {cross_themes}
        
        Question Strategy:
        1. Use STAR method (Situation, Task, Action, Result)
        2. Focus on behaviors that predict success
        3. Include leadership, teamwork, problem-solving
        4. Address conflict resolution and adaptability
        5. Incorporate cross-cutting themes where relevant
        
        User Profile: {user_profile or "General candidate"}
        
        Generate 5-7 behavioral questions in this JSON format:
        {{
            "questions": [
                {{
                    "question_text": "Tell me about a time when...",
                    "context": "What behavior this assesses",
                    "difficulty_level": "easy/medium/hard",
                    "expected_answer_points": ["Situation described", "Task identified", "Action taken", "Result achieved"],
                    "follow_up_questions": ["What would you do differently?"],
                    "source_research": "Cross-cutting theme or general behavioral assessment"
                }}
            ]
        }}
        """
        
        try:
            response = self.llm_client.generate_text(
                prompt=strategy_prompt,
                max_tokens=1400,
                temperature=0.6,
                company_name=f"Behavioral: {company_name}"
            )
            
            question_data = json.loads(response)
            questions = []
            
            for q_data in question_data.get("questions", []):
                question = Question(
                    id=str(uuid.uuid4()),
                    question_type=QuestionType.GENERAL_BEHAVIORAL,
                    question_text=q_data["question_text"],
                    context=q_data["context"],
                    difficulty_level=q_data["difficulty_level"],
                    expected_answer_points=q_data["expected_answer_points"],
                    follow_up_questions=q_data.get("follow_up_questions", []),
                    source_research=q_data.get("source_research", "")
                )
                questions.append(question)
            
            return QuestionCluster(
                cluster_id=str(uuid.uuid4()),
                cluster_name="Behavioral Assessment",
                focus_area="behavioral",
                questions=questions,
                priority_score=0.7,
                estimated_time_minutes=len(questions) * QUESTION_CONFIG["estimated_time_per_question"]
            )
            
        except Exception as e:
            return self._create_default_behavioral_cluster(str(e))
    
    # Default cluster creation methods for error handling
    def _create_default_company_cluster(self, company_name: str, error: str) -> QuestionCluster:
        """Create default company questions when generation fails"""
        
        default_questions = [
            Question(
                id=str(uuid.uuid4()),
                question_type=QuestionType.COMPANY_AWARE,
                question_text=f"What interests you most about working at {company_name}?",
                context="Tests company research and genuine interest",
                difficulty_level="easy",
                expected_answer_points=["Specific company attributes", "Personal alignment", "Career growth"],
                follow_up_questions=["How does this align with your career goals?"],
                source_research=f"Default question (generation error: {error})"
            ),
            Question(
                id=str(uuid.uuid4()),
                question_type=QuestionType.COMPANY_AWARE,
                question_text=f"How do you see yourself contributing to {company_name}'s mission?",
                context="Assesses cultural fit and value alignment",
                difficulty_level="medium",
                expected_answer_points=["Understanding of mission", "Personal skills connection", "Impact vision"],
                follow_up_questions=["What would success look like in your first 90 days?"],
                source_research=f"Default question (generation error: {error})"
            )
        ]
        
        return QuestionCluster(
            cluster_id=str(uuid.uuid4()),
            cluster_name=f"Company Knowledge - {company_name}",
            focus_area="company",
            questions=default_questions,
            priority_score=0.5,
            estimated_time_minutes=len(default_questions) * QUESTION_CONFIG["estimated_time_per_question"]
        )
    
    def _create_default_interviewer_cluster(self, interviewer_name: str, error: str) -> QuestionCluster:
        """Create default interviewer questions when generation fails"""
        
        default_questions = [
            Question(
                id=str(uuid.uuid4()),
                question_type=QuestionType.INTERVIEWER_SPECIFIC,
                question_text=f"I'd love to learn more about your experience at this company. What has been most rewarding about your role?",
                context="Shows interest in interviewer's perspective and experience",
                difficulty_level="easy",
                expected_answer_points=["Active listening", "Professional interest", "Follow-up engagement"],
                follow_up_questions=["What advice would you give to someone starting in this role?"],
                source_research=f"Default question (generation error: {error})"
            )
        ]
        
        return QuestionCluster(
            cluster_id=str(uuid.uuid4()),
            cluster_name=f"Interviewer Connection - {interviewer_name}",
            focus_area="interviewer",
            questions=default_questions,
            priority_score=0.4,
            estimated_time_minutes=len(default_questions) * QUESTION_CONFIG["estimated_time_per_question"]
        )
    
    def _create_default_role_cluster(self, role_title: str, error: str) -> QuestionCluster:
        """Create default role questions when generation fails"""
        
        default_questions = [
            Question(
                id=str(uuid.uuid4()),
                question_type=QuestionType.ROLE_SPECIFIC,
                question_text=f"What are the biggest challenges someone in this {role_title} role faces?",
                context="Tests role understanding and problem-solving mindset",
                difficulty_level="medium",
                expected_answer_points=["Role awareness", "Challenge identification", "Solution thinking"],
                follow_up_questions=["How would you approach solving those challenges?"],
                source_research=f"Default question (generation error: {error})"
            )
        ]
        
        return QuestionCluster(
            cluster_id=str(uuid.uuid4()),
            cluster_name=f"Role Competency - {role_title}",
            focus_area="role",
            questions=default_questions,
            priority_score=0.6,
            estimated_time_minutes=len(default_questions) * QUESTION_CONFIG["estimated_time_per_question"]
        )
    
    def _create_default_behavioral_cluster(self, error: str) -> QuestionCluster:
        """Create default behavioral questions when generation fails"""
        
        default_questions = [
            Question(
                id=str(uuid.uuid4()),
                question_type=QuestionType.GENERAL_BEHAVIORAL,
                question_text="Tell me about a time when you had to solve a difficult problem at work.",
                context="Assesses problem-solving and analytical thinking",
                difficulty_level="medium",
                expected_answer_points=["Clear situation", "Problem definition", "Solution approach", "Measurable result"],
                follow_up_questions=["What would you do differently next time?"],
                source_research=f"Default behavioral question (generation error: {error})"
            )
        ]
        
        return QuestionCluster(
            cluster_id=str(uuid.uuid4()),
            cluster_name="Behavioral Assessment",
            focus_area="behavioral",
            questions=default_questions,
            priority_score=0.3,
            estimated_time_minutes=len(default_questions) * QUESTION_CONFIG["estimated_time_per_question"]
        )
