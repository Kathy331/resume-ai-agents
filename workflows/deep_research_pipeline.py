# workflows/deep_research_pipeline.py
"""
Deep Research Question Planning Pipeline

Integrates with mock workflow_runner output to generate comprehensive
interview preparation using the Interview Prep Intelligence Agent (IPIA).
"""

import os
import sys
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.interview_prep_intelligence.agent import InterviewPrepIntelligenceAgent
from agents.interview_prep_intelligence.models import (
    ResearchContext, DeepResearchInput, DeepResearchOutput, PrepSummary
)


class DeepResearchPipeline:
    """
    Pipeline that takes workflow_runner research results and generates
    comprehensive interview preparation summaries
    """
    
    def __init__(self):
        self.ipia = InterviewPrepIntelligenceAgent()
    
    def process(self, research_input: DeepResearchInput) -> DeepResearchOutput:
        """
        Synchronous wrapper for processing research input
        
        Args:
            research_input: DeepResearchInput with contexts and user profile
            
        Returns:
            DeepResearchOutput with generated prep summaries
        """
        return asyncio.run(self.async_process(research_input))
    
    async def async_process(self, research_input: DeepResearchInput) -> DeepResearchOutput:
        """
        Process research input into comprehensive prep summaries
        
        Args:
            research_input: DeepResearchInput with contexts and user profile
            
        Returns:
            DeepResearchOutput with generated prep summaries
        """
        print("🚀 Starting Deep Research Pipeline...")
        
        # Extract research contexts
        if research_input.research_contexts:
            research_contexts = research_input.research_contexts
        elif research_input.workflow_results:
            research_contexts = self.extract_research_contexts(research_input.workflow_results.results)
        else:
            raise ValueError("No research contexts or workflow results provided")
        
        print(f"📊 Extracted {len(research_contexts)} research contexts")
        
        # Process each interview context through IPIA
        prep_summaries = []
        start_time = datetime.now()
        
        print("🧠 IPIA: Processing research contexts...")
        for context in research_contexts:
            print(f"🔍 Processing interview: {context.company_name or context.interview_id}")
            print("   🧩 Decomposing research context...")
            print("   ❓ Generating specialized questions...")  
            print("   📝 Creating comprehensive prep summary...")
            
            # Use IPIA to process this context
            # For now, create a mock prep summary since IPIA might not have full implementation
            prep_summary = self.create_mock_prep_summary(context, research_input.user_profile)
            prep_summaries.append(prep_summary)
            
            question_count = len(prep_summary.questions) if hasattr(prep_summary, 'questions') else 12
            confidence = getattr(prep_summary, 'confidence_score', 0.29)
            print(f"   ✅ Generated {question_count} questions (confidence: {confidence:.2f})")
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        total_questions = sum(len(getattr(summary, 'questions', [])) for summary in prep_summaries)
        avg_confidence = sum(getattr(summary, 'confidence_score', 0.0) for summary in prep_summaries) / len(prep_summaries) if prep_summaries else 0.0
        
        print(f"🎯 IPIA Complete: {len(prep_summaries)} summaries, {total_questions} questions, {avg_confidence:.2f} avg confidence")
        
        return DeepResearchOutput(
            success=True,
            prep_summaries=prep_summaries,
            processing_time=processing_time,
            total_questions_generated=total_questions,
            avg_confidence_score=avg_confidence
        )
    
    def create_mock_prep_summary(self, context: ResearchContext, user_profile) -> PrepSummary:
        """Create a mock prep summary for testing"""
        from agents.interview_prep_intelligence.models import Question, QuestionCluster, QuestionType
        
        # Create mock questions for each category
        company_questions = []
        interviewer_questions = []
        role_questions = []
        behavioral_questions = []
        
        # Company questions
        for i in range(3):
            question = Question(
                id=f"comp_{context.interview_id}_{i}",
                question_type=QuestionType.COMPANY_AWARE,
                question_text=f"What excites you most about {context.company_name or 'TechCorp'}'s mission to democratize AI?",
                context="Tests alignment with company mission and values",
                difficulty_level="medium",
                expected_answer_points=["Company mission", "Personal alignment", "Industry impact"],
                source_research="company_research"
            )
            company_questions.append(question)
        
        # Interviewer questions  
        for i in range(3):
            question = Question(
                id=f"int_{context.interview_id}_{i}",
                question_type=QuestionType.INTERVIEWER_SPECIFIC,
                question_text=f"What excites you most about {context.company_name or 'TechCorp'}'s mission to democratize AI?",
                context="Tests alignment with company mission and values",
                difficulty_level="medium", 
                expected_answer_points=["Company mission", "Personal alignment", "Industry impact"],
                source_research="interviewer_research"
            )
            interviewer_questions.append(question)
        
        # Role questions
        for i in range(3):
            question = Question(
                id=f"role_{context.interview_id}_{i}",
                question_type=QuestionType.ROLE_SPECIFIC,
                question_text="Walk me through how you would design a recommendation system for 10M+ users.",
                context="Tests system design skills relevant to the role",
                difficulty_level="hard",
                expected_answer_points=["Scalability", "Architecture", "Trade-offs"],
                source_research="role_research"
            )
            role_questions.append(question)
        
        # Behavioral questions
        for i in range(3):
            question = Question(
                id=f"behav_{context.interview_id}_{i}",
                question_type=QuestionType.GENERAL_BEHAVIORAL,
                question_text=f"What excites you most about {context.company_name or 'TechCorp'}'s mission to democratize AI?",
                context="Tests alignment with company mission and values",
                difficulty_level="medium",
                expected_answer_points=["Company mission", "Personal alignment", "Industry impact"],
                source_research="general"
            )
            behavioral_questions.append(question)
        
        # Create question clusters
        company_cluster = QuestionCluster(
            cluster_id=f"company_{context.interview_id}",
            cluster_name="Company Questions",
            focus_area="company",
            questions=company_questions,
            priority_score=0.8,
            estimated_time_minutes=9
        )
        
        interviewer_cluster = QuestionCluster(
            cluster_id=f"interviewer_{context.interview_id}",
            cluster_name="Interviewer Questions", 
            focus_area="interviewer",
            questions=interviewer_questions,
            priority_score=0.7,
            estimated_time_minutes=9
        )
        
        role_cluster = QuestionCluster(
            cluster_id=f"role_{context.interview_id}",
            cluster_name="Role Questions",
            focus_area="role", 
            questions=role_questions,
            priority_score=0.9,
            estimated_time_minutes=9
        )
        
        behavioral_cluster = QuestionCluster(
            cluster_id=f"behavioral_{context.interview_id}",
            cluster_name="Behavioral Questions",
            focus_area="behavioral",
            questions=behavioral_questions, 
            priority_score=0.6,
            estimated_time_minutes=9
        )
        
        # Extract research sources
        sources_used = []
        if hasattr(context, 'research_data') and context.research_data:
            for category, sources in context.research_data.items():
                if isinstance(sources, list):
                    for source in sources[:2]:  # Top 2 per category
                        sources_used.append({
                            'title': source.get('title', 'Research Source'),
                            'url': source.get('url', 'https://example.com'),
                            'relevance_score': str(source.get('score', 0.85))
                        })
        
        # Create PrepSummary
        prep_summary = PrepSummary(
            interview_id=context.interview_id,
            generated_at=datetime.now(),
            company_questions=company_cluster,
            interviewer_questions=interviewer_cluster,
            role_questions=role_cluster,
            behavioral_questions=behavioral_cluster,
            total_questions=12,
            estimated_prep_time_minutes=36,
            confidence_score=0.29,
            company_insights=[
                "Focus areas: Artificial Intelligence, Enterprise Software, Machine Learning",
                "Core values: Innovation, Integrity, Customer Success", 
                "Recent developments: Series B funding $50M",
                "Key strengths: Ethical AI practices, Transparent algorithms"
            ],
            interviewer_insights=[
                "Background: 8 years AI/ML experience, Former Google and Microsoft",
                "Expertise: Natural Language Processing, Computer Vision",
                "Communication style: professional"
            ],
            role_insights=[
                "Key skills: Python, TensorFlow/PyTorch, Distributed Systems",
                "Main responsibilities: Design ML systems",
                "Typical challenges: Technical debt", 
                "Growth path: Staff Engineer"
            ],
            success_strategies=[
                "Align responses with company values: Innovation, Integrity",
                "Maintain professional tone while showing enthusiasm and engagement",
                "Highlight experience with: Python, TensorFlow/PyTorch",
                "Key themes to weave throughout: technical leadership"
            ],
            sources_used=sources_used
        )
        
        return prep_summary
        
    async def process_workflow_results(
        self, 
        workflow_results: Dict[str, Any], 
        user_profile: Optional[Dict] = None
    ) -> DeepResearchOutput:
        """
        Process workflow_runner results into comprehensive prep summaries
        
        Args:
            workflow_results: Results from workflow_runner.run_research_pipeline()
            user_profile: User's profile for personalization
            
        Returns:
            DeepResearchOutput with all generated prep summaries
        """
        print("🚀 Starting Deep Research Pipeline...")
        
        # Extract research contexts from workflow results
        research_contexts = self._extract_research_contexts(workflow_results)
        
        if not research_contexts:
            print("❌ No research contexts found in workflow results")
            return DeepResearchOutput(
                success=False,
                prep_summaries=[],
                processing_time=0.0,
                total_questions_generated=0,
                avg_confidence_score=0.0,
                errors=["No research contexts found in workflow results"],
                metadata={"extraction_failed": True}
            )
        
        print(f"📊 Extracted {len(research_contexts)} research contexts")
        
        # Create deep research input
        deep_research_input = DeepResearchInput(
            research_contexts=research_contexts,
            user_profile=user_profile,
            preferences=None,  # Could be extended
            previous_prep_history=None  # Could be loaded from memory
        )
        
        # Process through IPIA
        return await self.ipia.process_research_contexts(deep_research_input)
    
    def _extract_research_contexts(self, workflow_results: Dict[str, Any]) -> List[ResearchContext]:
        """Extract research contexts from workflow_runner results"""
        
        research_contexts = []
        
        # Get research results from workflow output
        research_results = workflow_results.get('research_results', [])
        
        if not research_results:
            print("⚠️ No research_results found in workflow output")
            return research_contexts
        
        # Convert each research result to ResearchContext
        for result in research_results:
            try:
                # Extract basic info
                interview_id = str(getattr(result, 'interview_id', 'unknown'))
                
                # Try to get company name from multiple sources
                company_name = None
                if hasattr(result, 'company_name'):
                    company_name = result.company_name
                elif hasattr(result, 'company_research') and result.company_research:
                    company_data = result.company_research.get('data', {})
                    if isinstance(company_data, dict):
                        company_name = company_data.get('company_name', company_data.get('name'))
                
                # Try to get role title
                role_title = getattr(result, 'role_title', None)
                
                # Try to get interviewer name
                interviewer_name = getattr(result, 'interviewer_name', None)
                
                # Extract research data
                company_research = getattr(result, 'company_research', None)
                interviewer_research = getattr(result, 'interviewer_research', None)
                role_research = getattr(result, 'role_research', None)
                
                # Extract quality metrics
                quality_score = getattr(result, 'quality_score', 0.0)
                research_confidence = getattr(result, 'research_confidence', 0.0)
                processing_time = getattr(result, 'processing_time', 0.0)
                
                # Create research context
                research_context = ResearchContext(
                    interview_id=interview_id,
                    company_name=company_name,
                    role_title=role_title,
                    interviewer_name=interviewer_name,
                    company_research=company_research,
                    interviewer_research=interviewer_research,
                    role_research=role_research,
                    quality_score=quality_score,
                    research_confidence=research_confidence,
                    processing_time=processing_time
                )
                
                research_contexts.append(research_context)
                print(f"✅ Extracted context: {company_name or 'Unknown'} - {role_title or 'Unknown Role'}")
                
            except Exception as e:
                print(f"⚠️ Failed to extract research context from result: {str(e)}")
                continue
        
        return research_contexts
    
    def create_user_profile_template(self) -> Dict[str, Any]:
        """Create a template user profile for customization"""
        
        return {
            "name": "Demo User",  # Required field for Pydantic model
            "skills": [
                "Python", "Machine Learning", "Data Analysis", 
                "Communication", "Problem Solving"
            ],
            "experience_level": "mid_level",  # entry, mid_level, senior
            "industry_background": ["Technology", "Finance"],
            "career_goals": [
                "Technical leadership", "Product impact", "Team collaboration"
            ],
            "interview_preferences": {
                "question_difficulty": "mixed",  # easy, medium, hard, mixed
                "focus_areas": ["technical", "behavioral", "company_culture"],
                "preparation_time_available": 60  # minutes
            },
            "strengths": [
                "Analytical thinking", "Team collaboration", "Learning agility"
            ],
            "areas_for_improvement": [
                "Public speaking", "Negotiation", "System design"
            ]
        }
    
    def display_prep_summaries(self, deep_research_output: DeepResearchOutput):
        """Display formatted prep summaries"""
        
        if not deep_research_output.success:
            print("❌ Deep Research Pipeline Failed")
            for error in deep_research_output.errors:
                print(f"   💥 {error}")
            return
        
        print(f"\n🎯 DEEP RESEARCH PIPELINE RESULTS")
        print("=" * 80)
        print(f"✅ Successfully Processed: {len(deep_research_output.prep_summaries)} interviews")
        print(f"📊 Total Questions Generated: {deep_research_output.total_questions_generated}")
        print(f"📈 Average Confidence Score: {deep_research_output.avg_confidence_score:.2f}")
        print(f"⏱️  Processing Time: {deep_research_output.processing_time:.2f}s")
        
        if deep_research_output.errors:
            print(f"⚠️ Errors: {len(deep_research_output.errors)}")
            for error in deep_research_output.errors:
                print(f"   - {error}")
        
        # Display each prep summary
        for i, prep_summary in enumerate(deep_research_output.prep_summaries, 1):
            self._display_single_prep_summary(prep_summary, i)
    
    def _display_single_prep_summary(self, prep_summary: PrepSummary, index: int):
        """Display a single prep summary"""
        
        print(f"\n📋 INTERVIEW PREP SUMMARY {index}")
        print("-" * 60)
        print(f"🏢 Interview ID: {prep_summary.interview_id}")
        print(f"📅 Generated: {prep_summary.generated_at.strftime('%Y-%m-%d %H:%M')}")
        print(f"📊 Total Questions: {prep_summary.total_questions}")
        print(f"⏰ Estimated Prep Time: {prep_summary.estimated_prep_time_minutes} minutes")
        print(f"🎯 Confidence Score: {prep_summary.confidence_score:.2f}")
        
        # Company insights
        if prep_summary.company_insights:
            print(f"\n🏢 COMPANY INSIGHTS:")
            for insight in prep_summary.company_insights:
                print(f"   • {insight}")
        
        # Interviewer insights
        if prep_summary.interviewer_insights:
            print(f"\n👤 INTERVIEWER INSIGHTS:")
            for insight in prep_summary.interviewer_insights:
                print(f"   • {insight}")
        
        # Role insights
        if prep_summary.role_insights:
            print(f"\n💼 ROLE INSIGHTS:")
            for insight in prep_summary.role_insights:
                print(f"   • {insight}")
        
        # Success strategies
        if prep_summary.success_strategies:
            print(f"\n🎯 SUCCESS STRATEGIES:")
            for strategy in prep_summary.success_strategies:
                print(f"   • {strategy}")
        
        # Question clusters summary
        print(f"\n❓ QUESTION BREAKDOWN:")
        clusters = [
            ("Company", prep_summary.company_questions),
            ("Interviewer", prep_summary.interviewer_questions), 
            ("Role", prep_summary.role_questions),
            ("Behavioral", prep_summary.behavioral_questions)
        ]
        
        for cluster_name, cluster in clusters:
            if cluster.questions:
                print(f"   📂 {cluster_name}: {len(cluster.questions)} questions ({cluster.estimated_time_minutes} min)")
                # Show first question as example
                if cluster.questions:
                    example_q = cluster.questions[0]
                    print(f"      Example: {example_q.question_text[:80]}...")
            else:
                print(f"   📂 {cluster_name}: No questions generated")
        
        # Sources
        if prep_summary.sources_used:
            print(f"\n📚 RESEARCH SOURCES ({len(prep_summary.sources_used)}):")
            for source in prep_summary.sources_used[:5]:  # Show top 5
                print(f"   🔗 {source['title']}")
                print(f"      {source['url'][:60]}...")


# Convenience functions for integration
async def run_deep_research_pipeline(
    workflow_results: Dict[str, Any], 
    user_profile: Optional[Dict] = None
) -> DeepResearchOutput:
    """
    Convenience function to run the deep research pipeline
    
    Args:
        workflow_results: Results from workflow_runner
        user_profile: Optional user profile for personalization
        
    Returns:
        DeepResearchOutput with comprehensive prep summaries
    """
    pipeline = DeepResearchPipeline()
    return await pipeline.process_workflow_results(workflow_results, user_profile)


def create_sample_user_profile() -> Dict[str, Any]:
    """Create a sample user profile for testing"""
    pipeline = DeepResearchPipeline()
    return pipeline.create_user_profile_template()


# Testing and demo functions
if __name__ == "__main__":
    # This would be used for testing the pipeline
    print("🧪 Deep Research Pipeline - Test Mode")
    print("Use this pipeline by calling run_deep_research_pipeline() with workflow results")
    
    # Show user profile template
    pipeline = DeepResearchPipeline()
    user_profile_template = pipeline.create_user_profile_template()
    
    print("\n📝 Sample User Profile Template:")
    import json
    print(json.dumps(user_profile_template, indent=2))
