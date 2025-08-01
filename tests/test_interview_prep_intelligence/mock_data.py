# tests/test_interview_prep_intelligence/mock_data.py
"""
Mock data for Interview Prep Intelligence Agent testing
Focus on SEEDS and JUTEQ email data only
"""

from typing import Dict, Any, List
from datetime import datetime
import sys
import os

# Add project root to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from agents.interview_prep_intelligence.models import ResearchContext


class MockResearchData:
    """Mock research data for testing IPIA components with SEEDS and JUTEQ data"""
    
    @staticmethod
    def create_mock_workflow_results() -> Dict[str, Any]:
        """Create mock workflow results with SEEDS and JUTEQ data only"""
        
        # Create mock research contexts for SEEDS and JUTEQ
        seeds_context = MockResearchData.create_seeds_research_context()
        juteq_context = MockResearchData.create_juteq_research_context()
        
        return {
            "success": True,
            "interviews_found": 2,
            "interviews_researched": 2,
            "average_quality": 0.90,
            "processing_time": 8.5,
            "research_results": [seeds_context, juteq_context],
            "metadata": {
                "timestamp": datetime.now(),
                "workflow_version": "1.0.0",
                "research_engine": "tavily"
            }
        }
    
    @staticmethod
    def create_seeds_research_context() -> ResearchContext:
        """Create SEEDS research context based on your actual email"""
        return ResearchContext(
            interview_id="seeds_archana_001",
            company_name="Dandilyonn SEEDS Program",
            interviewer_name="Archana",
            role_title="Sustainability Intern",
            research_data={
                "company_research": [
                    {
                        "title": "SEEDS Program - Environmental Leadership Development",
                        "content": "SEEDS (Sustainability Education and Development Scholars) program at Dandilyonn focuses on developing next-generation environmental leaders. The program emphasizes hands-on sustainability projects, community engagement, and innovative solutions to climate challenges.",
                        "url": "https://dandilyonn.com/seeds",
                        "score": 0.92
                    },
                    {
                        "title": "Dandilyonn Company Culture - Warmth and Growth",
                        "content": "Dandilyonn fosters a collaborative, nurturing environment where personal growth is paramount. The company culture emphasizes mentorship, work-life balance, and creating meaningful impact.",
                        "url": "https://dandilyonn.com/culture",
                        "score": 0.89
                    }
                ],
                "interviewer_research": [
                    {
                        "title": "Archana - SEEDS Program Manager Profile",
                        "content": "Archana has been with Dandilyonn for 5 years, leading the SEEDS program since its inception. Known for her warm, encouraging interview style and focus on candidate potential rather than just experience.",
                        "url": "https://linkedin.com/in/archana-seeds",
                        "score": 0.91
                    },
                    {
                        "title": "Archana's Mentorship Philosophy",
                        "content": "Archana emphasized her belief in 'growth over perfection.' She looks for candidates who show genuine curiosity about environmental issues and willingness to learn.",
                        "url": "https://dandilyonn.com/team/archana",
                        "score": 0.87
                    }
                ],
                "role_research": [
                    {
                        "title": "SEEDS Sustainability Intern Responsibilities",
                        "content": "Interns work on real environmental projects including renewable energy assessments, sustainability reporting, and community outreach programs.",
                        "url": "https://dandilyonn.com/careers/seeds-intern",
                        "score": 0.90
                    }
                ]
            },
            quality_indicators={
                "company_coverage": 0.92,
                "interviewer_insights": 0.89,
                "role_specificity": 0.88,
                "recent_information": 0.85,
                "source_diversity": 0.87
            },
            quality_score=0.89,
            research_confidence=0.88,
            processing_time=2.1
        )
    
    @staticmethod
    def create_juteq_research_context() -> ResearchContext:
        """Create JUTEQ research context based on your actual email"""
        return ResearchContext(
            interview_id="juteq_rakesh_001",
            company_name="JUTEQ",
            interviewer_name="Rakesh Gohel",
            role_title="AI & Cloud Engineering Intern",
            research_data={
                "company_research": [
                    {
                        "title": "JUTEQ - AI Agents and Cloud-Native Platform Leadership",
                        "content": "JUTEQ is a cutting-edge technology company specializing in AI agents and cloud-native solutions. The company develops intelligent automation platforms that help enterprises scale their operations efficiently.",
                        "url": "https://juteq.com/platform",
                        "score": 0.94
                    },
                    {
                        "title": "JUTEQ Technical Innovation and Market Position",
                        "content": "JUTEQ's AI agent technology powers enterprise automation for Fortune 500 companies. The platform handles complex workflow orchestration, intelligent decision-making, and adaptive system optimization.",
                        "url": "https://juteq.com/technology",
                        "score": 0.91
                    }
                ],
                "interviewer_research": [
                    {
                        "title": "Rakesh Gohel - JUTEQ Founder & CEO Technical Leadership",
                        "content": "Rakesh Gohel founded JUTEQ after 12 years in enterprise software and cloud architecture. Previously led engineering teams at major tech companies, with expertise in distributed systems, AI/ML, and cloud infrastructure.",
                        "url": "https://linkedin.com/in/rakesh-gohel-juteq",
                        "score": 0.93
                    },
                    {
                        "title": "Rakesh's Interview and Leadership Style",
                        "content": "Rakesh conducts technical interviews focusing on problem-solving approach rather than memorized solutions. He values candidates who can think through complex system design challenges.",
                        "url": "https://juteq.com/leadership/rakesh",
                        "score": 0.89
                    }
                ],
                "role_research": [
                    {
                        "title": "AI & Cloud Engineering Intern - Technical Responsibilities",
                        "content": "Interns work on production AI agent systems, cloud infrastructure optimization, and distributed system development. Projects include implementing ML algorithms and designing scalable architectures.",
                        "url": "https://juteq.com/careers/ai-cloud-intern",
                        "score": 0.92
                    }
                ]
            },
            quality_indicators={
                "company_coverage": 0.91,
                "interviewer_insights": 0.91,
                "role_specificity": 0.91,
                "recent_information": 0.88,
                "source_diversity": 0.89
            },
            quality_score=0.90,
            research_confidence=0.89,
            processing_time=2.3
        )
    
    @staticmethod
    def create_mock_user_profile() -> Dict[str, Any]:
        """Create user profile matching your background"""
        return {
            "name": "Test User",
            "experience_level": "entry",
            "skills": ["Python", "Data Analysis", "Environmental Science", "Research", "Sustainability", "AI/ML", "Cloud Computing"],
            "interests": ["Climate Change", "Renewable Energy", "AI/ML", "Cloud Computing", "Environmental Policy"],
            "industry_background": ["Environmental Science", "Technology"],
            "career_goals": ["Environmental Impact", "Technical Innovation", "Sustainability Solutions"],
            "strengths": ["Analytical Thinking", "Problem Solving", "Communication", "Learning Agility"],
            "preferences": {
                "question_difficulty": "intermediate",
                "focus_areas": ["technical_skills", "environmental_impact", "problem_solving"],
                "preparation_time": "moderate"
            },
            "background": "Recent graduate with environmental science background and growing interest in technology applications for sustainability"
        }
