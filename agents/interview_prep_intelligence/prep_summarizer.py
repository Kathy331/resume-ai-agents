# agents/interview_prep_intelligence/prep_summarizer.py
"""
Comprehensive Prep Summary Generator

Generates final structured prep summaries using:
- Multi-agent RAG for comprehensive insights
- JSON structured output for easy consumption
- Vector-based similarity for content optimization
- Memory-augmented context for personalization
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime

from .models import PrepSummary, QuestionCluster, ResearchContext
from .config import QUALITY_WEIGHTS, OUTPUT_TEMPLATES
from shared.llm_client import get_llm_client


class PrepSummarizer:
    """
    Creates comprehensive interview preparation summaries
    combining all research insights and generated questions
    """
    
    def __init__(self):
        self.llm_client = get_llm_client()
        
    def create_prep_summary(
        self, 
        research_context: ResearchContext,
        question_clusters: Dict[str, QuestionCluster],
        insights: Dict[str, Any],
        user_profile: Optional[Dict] = None
    ) -> PrepSummary:
        """
        Create comprehensive preparation summary
        
        Args:
            research_context: Original research context
            question_clusters: Generated question clusters
            insights: Decomposed context insights
            user_profile: User's profile for personalization
            
        Returns:
            Complete PrepSummary with all components
        """
        
        # Calculate summary metrics
        total_questions = sum(len(cluster.questions) for cluster in question_clusters.values())
        estimated_prep_time = sum(cluster.estimated_time_minutes for cluster in question_clusters.values())
        
        # Generate key insights for each category
        company_insights = self._generate_company_insights(insights.get("company_insights", {}))
        interviewer_insights = self._generate_interviewer_insights(insights.get("interviewer_insights", {}))
        role_insights = self._generate_role_insights(insights.get("role_insights", {}))
        
        # Generate success strategies
        success_strategies = self._generate_success_strategies(insights, question_clusters)
        
        # Extract and organize sources
        sources_used = self._extract_sources(research_context)
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(insights, question_clusters)
        
        # Create prep summary
        prep_summary = PrepSummary(
            interview_id=research_context.interview_id,
            generated_at=datetime.now(),
            
            # Question clusters (with defaults for missing clusters)
            company_questions=question_clusters.get("company", self._create_empty_cluster("company")),
            interviewer_questions=question_clusters.get("interviewer", self._create_empty_cluster("interviewer")),
            role_questions=question_clusters.get("role", self._create_empty_cluster("role")),
            behavioral_questions=question_clusters.get("behavioral", self._create_empty_cluster("behavioral")),
            
            # Summary metrics
            total_questions=total_questions,
            estimated_prep_time_minutes=estimated_prep_time,
            confidence_score=confidence_score,
            
            # Key insights
            company_insights=company_insights,
            interviewer_insights=interviewer_insights,
            role_insights=role_insights,
            success_strategies=success_strategies,
            
            # Sources
            sources_used=sources_used
        )
        
        return prep_summary
    
    def _generate_company_insights(self, company_insights: Dict[str, Any]) -> List[str]:
        """Generate key company insights for the summary"""
        
        if "error" in company_insights:
            return ["Company research was limited - prepare general company questions"]
        
        insights = []
        
        # Business focus insights
        if company_insights.get("business_focus"):
            insights.append(f"Focus areas: {', '.join(company_insights['business_focus'][:3])}")
        
        # Values and culture
        if company_insights.get("company_values"):
            insights.append(f"Core values: {', '.join(company_insights['company_values'][:3])}")
        
        # Recent developments
        if company_insights.get("recent_developments"):
            insights.append(f"Recent developments: {company_insights['recent_developments'][0]}")
        
        # Competitive advantages
        if company_insights.get("competitive_advantages"):
            insights.append(f"Key strengths: {', '.join(company_insights['competitive_advantages'][:2])}")
        
        return insights[:4]  # Limit to top 4 insights
    
    def _generate_interviewer_insights(self, interviewer_insights: Dict[str, Any]) -> List[str]:
        """Generate key interviewer insights for the summary"""
        
        if "error" in interviewer_insights:
            return ["Interviewer background research was limited - prepare general professional questions"]
        
        insights = []
        
        # Professional background
        if interviewer_insights.get("professional_background"):
            insights.append(f"Background: {', '.join(interviewer_insights['professional_background'][:2])}")
        
        # Expertise areas
        if interviewer_insights.get("expertise_areas"):
            insights.append(f"Expertise: {', '.join(interviewer_insights['expertise_areas'][:2])}")
        
        # Communication style
        if interviewer_insights.get("communication_style"):
            insights.append(f"Communication style: {interviewer_insights['communication_style']}")
        
        # Interview focus
        if interviewer_insights.get("likely_interview_focus"):
            insights.append(f"Likely focus: {', '.join(interviewer_insights['likely_interview_focus'][:2])}")
        
        return insights[:3]  # Limit to top 3 insights
    
    def _generate_role_insights(self, role_insights: Dict[str, Any]) -> List[str]:
        """Generate key role insights for the summary"""
        
        if "error" in role_insights:
            return ["Role research was limited - prepare general competency questions"]
        
        insights = []
        
        # Technical skills
        if role_insights.get("core_technical_skills"):
            insights.append(f"Key skills: {', '.join(role_insights['core_technical_skills'][:3])}")
        
        # Responsibilities
        if role_insights.get("key_responsibilities"):
            insights.append(f"Main responsibilities: {role_insights['key_responsibilities'][0]}")
        
        # Common challenges
        if role_insights.get("common_challenges"):
            insights.append(f"Typical challenges: {role_insights['common_challenges'][0]}")
        
        # Growth opportunities
        if role_insights.get("growth_opportunities"):
            insights.append(f"Growth path: {role_insights['growth_opportunities'][0]}")
        
        return insights[:4]  # Limit to top 4 insights
    
    def _generate_success_strategies(self, insights: Dict[str, Any], question_clusters: Dict[str, QuestionCluster]) -> List[str]:
        """Generate success strategies based on all available insights"""
        
        strategies = []
        
        # Strategy based on company insights
        company_data = insights.get("company_insights", {})
        if "error" not in company_data and company_data.get("company_values"):
            strategies.append(f"Align responses with company values: {', '.join(company_data['company_values'][:2])}")
        
        # Strategy based on interviewer insights  
        interviewer_data = insights.get("interviewer_insights", {})
        if "error" not in interviewer_data and interviewer_data.get("communication_style"):
            style = interviewer_data["communication_style"]
            if style == "technical":
                strategies.append("Prepare detailed technical examples and be ready for deep-dive questions")
            elif style == "casual":
                strategies.append("Be conversational and show your personality while maintaining professionalism")
            else:
                strategies.append("Maintain professional tone while showing enthusiasm and engagement")
        
        # Strategy based on role insights
        role_data = insights.get("role_insights", {})
        if "error" not in role_data and role_data.get("core_technical_skills"):
            strategies.append(f"Highlight experience with: {', '.join(role_data['core_technical_skills'][:2])}")
        
        # Strategy based on question distribution
        total_questions = sum(len(cluster.questions) for cluster in question_clusters.values())
        if total_questions > 20:
            strategies.append("Prioritize high-impact questions - you have extensive preparation material")
        elif total_questions < 10:
            strategies.append("Focus on general competency and behavioral examples")
        
        # Cross-cutting themes strategy
        cross_themes = insights.get("cross_cutting_themes", [])
        if cross_themes:
            strategies.append(f"Key themes to weave throughout: {', '.join(cross_themes[:2])}")
        
        # Default strategies if none generated
        if not strategies:
            strategies = [
                "Prepare concrete STAR method examples for behavioral questions",
                "Research the company's recent news and developments", 
                "Practice explaining your technical experience clearly",
                "Prepare thoughtful questions about the role and team"
            ]
        
        return strategies[:5]  # Limit to top 5 strategies
    
    def _extract_sources(self, research_context: ResearchContext) -> List[Dict[str, str]]:
        """Extract and organize sources from research context"""
        
        sources = []
        
        # Extract company sources
        if research_context.company_research:
            company_sources = self._extract_sources_from_research_data(
                research_context.company_research, 
                "Company Research"
            )
            sources.extend(company_sources)
        
        # Extract interviewer sources
        if research_context.interviewer_research:
            interviewer_sources = self._extract_sources_from_research_data(
                research_context.interviewer_research,
                "Interviewer Research"
            )
            sources.extend(interviewer_sources)
        
        # Extract role sources  
        if research_context.role_research:
            role_sources = self._extract_sources_from_research_data(
                research_context.role_research,
                "Role Research"
            )
            sources.extend(role_sources)
        
        return sources[:10]  # Limit to top 10 sources
    
    def _extract_sources_from_research_data(self, research_data: Dict[str, Any], source_type: str) -> List[Dict[str, str]]:
        """Extract sources from individual research data"""
        
        sources = []
        
        # Try to extract search results
        search_results = []
        if isinstance(research_data, dict):
            if 'data' in research_data and isinstance(research_data['data'], dict):
                search_results = research_data['data'].get('search_results', [])
            elif 'search_results' in research_data:
                search_results = research_data['search_results']
        
        # Convert search results to source format
        for result in search_results[:3]:  # Top 3 per category
            if isinstance(result, dict):
                sources.append({
                    "title": result.get('title', 'Unknown Title')[:80],
                    "url": result.get('url', ''),
                    "relevance_score": source_type
                })
        
        return sources
    
    def _calculate_confidence_score(self, insights: Dict[str, Any], question_clusters: Dict[str, QuestionCluster]) -> float:
        """Calculate overall confidence score for the prep summary"""
        
        scores = []
        
        # Research completeness score
        research_completeness = 0.0
        research_categories = ["company_insights", "interviewer_insights", "role_insights"]
        
        for category in research_categories:
            if category in insights and "error" not in insights[category]:
                research_completeness += 1.0
        
        research_completeness /= len(research_categories)
        scores.append(research_completeness * QUALITY_WEIGHTS["research_completeness"])
        
        # Question generation score
        question_score = 0.0
        expected_clusters = ["company", "interviewer", "role", "behavioral"]
        
        for cluster_type in expected_clusters:
            if cluster_type in question_clusters:
                cluster = question_clusters[cluster_type]
                if len(cluster.questions) > 0:
                    question_score += 1.0
        
        question_score /= len(expected_clusters)
        scores.append(question_score * QUALITY_WEIGHTS["question_relevance"])
        
        # Difficulty balance score
        all_questions = []
        for cluster in question_clusters.values():
            all_questions.extend(cluster.questions)
        
        if all_questions:
            difficulty_counts = {"easy": 0, "medium": 0, "hard": 0}
            for question in all_questions:
                difficulty_counts[question.difficulty_level] += 1
            
            total_questions = len(all_questions)
            difficulty_balance = 1.0 - abs(0.5 - (difficulty_counts["medium"] / total_questions))
            scores.append(difficulty_balance * QUALITY_WEIGHTS["difficulty_balance"])
        else:
            scores.append(0.0)
        
        # Overall confidence
        if scores:
            return sum(scores) / len(scores)
        else:
            return 0.0
    
    def _create_empty_cluster(self, cluster_type: str) -> QuestionCluster:
        """Create an empty question cluster for missing data"""
        
        from .models import QuestionCluster
        import uuid
        
        return QuestionCluster(
            cluster_id=str(uuid.uuid4()),
            cluster_name=f"{cluster_type.title()} Questions",
            focus_area=cluster_type,
            questions=[],
            priority_score=0.0,
            estimated_time_minutes=0
        )
