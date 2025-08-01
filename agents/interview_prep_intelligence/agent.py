# agents/interview_prep_intelligence/agent.py
"""
Interview Prep Intelligence Agent (IPIA)

Main orchestrator that coordinates all sub-agents to create
comprehensive interview preparation summaries from research data.
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime

from .models import (
    ResearchContext, DeepResearchInput, DeepResearchOutput, 
    PrepSummary, QuestionCluster
)
from .context_decomposer import ContextDecomposer
from .question_generator import QuestionGenerator
from .prep_summarizer import PrepSummarizer
from .config import RESEARCH_CONFIG


class InterviewPrepIntelligenceAgent:
    """
    Main IPIA orchestrator that coordinates:
    1. Context-aware decomposition of research data
    2. Multi-agent question generation 
    3. Comprehensive prep summary creation
    """
    
    def __init__(self):
        self.context_decomposer = ContextDecomposer()
        self.question_generator = QuestionGenerator()
        self.prep_summarizer = PrepSummarizer()
        
    async def process_research_contexts(self, deep_research_input: DeepResearchInput) -> DeepResearchOutput:
        """
        Main entry point - processes multiple research contexts into prep summaries
        
        Args:
            deep_research_input: Input containing research contexts and user profile
            
        Returns:
            DeepResearchOutput with all generated prep summaries
        """
        start_time = datetime.now()
        prep_summaries = []
        errors = []
        total_questions = 0
        confidence_scores = []
        
        try:
            print(f"🧠 IPIA: Processing {len(deep_research_input.research_contexts)} research contexts...")
            
            # Process each research context
            for i, research_context in enumerate(deep_research_input.research_contexts, 1):
                try:
                    print(f"🔍 Processing interview {i}: {research_context.company_name or 'Unknown Company'}")
                    
                    # Step 1: Context decomposition
                    print("   🧩 Decomposing research context...")
                    insights = await self._decompose_context_async(research_context)
                    
                    # Step 2: Question generation
                    print("   ❓ Generating specialized questions...")
                    question_clusters = await self._generate_questions_async(
                        insights, 
                        deep_research_input.user_profile
                    )
                    
                    # Step 3: Prep summary creation
                    print("   📝 Creating comprehensive prep summary...")
                    prep_summary = self.prep_summarizer.create_prep_summary(
                        research_context=research_context,
                        question_clusters=question_clusters,
                        insights=insights,
                        user_profile=deep_research_input.user_profile
                    )
                    
                    prep_summaries.append(prep_summary)
                    total_questions += prep_summary.total_questions
                    confidence_scores.append(prep_summary.confidence_score)
                    
                    print(f"   ✅ Generated {prep_summary.total_questions} questions (confidence: {prep_summary.confidence_score:.2f})")
                    
                except Exception as e:
                    error_msg = f"Failed to process {research_context.company_name}: {str(e)}"
                    errors.append(error_msg)
                    print(f"   ❌ {error_msg}")
            
            # Calculate final metrics
            processing_time = (datetime.now() - start_time).total_seconds()
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0.0
            
            print(f"🎯 IPIA Complete: {len(prep_summaries)} summaries, {total_questions} questions, {avg_confidence:.2f} avg confidence")
            
            return DeepResearchOutput(
                success=len(prep_summaries) > 0,
                prep_summaries=prep_summaries,
                processing_time=processing_time,
                total_questions_generated=total_questions,
                avg_confidence_score=avg_confidence,
                errors=errors,
                metadata={
                    "processed_interviews": len(deep_research_input.research_contexts),
                    "successful_summaries": len(prep_summaries),
                    "failed_summaries": len(errors),
                    "user_profile_used": deep_research_input.user_profile is not None
                }
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return DeepResearchOutput(
                success=False,
                prep_summaries=[],
                processing_time=processing_time,
                total_questions_generated=0,
                avg_confidence_score=0.0,
                errors=[f"IPIA processing failed: {str(e)}"],
                metadata={"fatal_error": True}
            )
    
    async def _decompose_context_async(self, research_context: ResearchContext) -> Dict[str, Any]:
        """Async wrapper for context decomposition"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, 
            self.context_decomposer.decompose_context, 
            research_context
        )
    
    async def _generate_questions_async(self, insights: Dict[str, Any], user_profile: Optional[Dict] = None) -> Dict[str, QuestionCluster]:
        """Async wrapper for question generation"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.question_generator.generate_question_clusters,
            insights,
            user_profile
        )
    
    def process_single_context(self, research_context: ResearchContext, user_profile: Optional[Dict] = None) -> PrepSummary:
        """
        Synchronous processing of a single research context
        
        Args:
            research_context: Single research context to process
            user_profile: Optional user profile for personalization
            
        Returns:
            PrepSummary for the single context
        """
        print(f"🧠 IPIA: Processing single context for {research_context.company_name or 'Unknown Company'}")
        
        try:
            # Step 1: Context decomposition
            print("   🧩 Decomposing research context...")
            insights = self.context_decomposer.decompose_context(research_context)
            
            # Step 2: Question generation
            print("   ❓ Generating specialized questions...")
            question_clusters = self.question_generator.generate_question_clusters(insights, user_profile)
            
            # Step 3: Prep summary creation
            print("   📝 Creating comprehensive prep summary...")
            prep_summary = self.prep_summarizer.create_prep_summary(
                research_context=research_context,
                question_clusters=question_clusters,
                insights=insights,
                user_profile=user_profile
            )
            
            print(f"   ✅ Generated {prep_summary.total_questions} questions (confidence: {prep_summary.confidence_score:.2f})")
            return prep_summary
            
        except Exception as e:
            print(f"   ❌ Single context processing failed: {str(e)}")
            # Return minimal prep summary on failure
            return self._create_minimal_prep_summary(research_context, str(e))
    
    def _create_minimal_prep_summary(self, research_context: ResearchContext, error: str) -> PrepSummary:
        """Create a minimal prep summary when processing fails"""
        
        from .models import PrepSummary, QuestionCluster
        import uuid
        
        # Create empty clusters
        empty_cluster = QuestionCluster(
            cluster_id=str(uuid.uuid4()),
            cluster_name="Default Questions",
            focus_area="general",
            questions=[],
            priority_score=0.0,
            estimated_time_minutes=0
        )
        
        return PrepSummary(
            interview_id=research_context.interview_id,
            generated_at=datetime.now(),
            
            company_questions=empty_cluster,
            interviewer_questions=empty_cluster,
            role_questions=empty_cluster,
            behavioral_questions=empty_cluster,
            
            total_questions=0,
            estimated_prep_time_minutes=0,
            confidence_score=0.0,
            
            company_insights=[f"Processing failed: {error}"],
            interviewer_insights=[],
            role_insights=[],
            success_strategies=["Focus on general interview preparation"],
            
            sources_used=[]
        )
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about the IPIA system"""
        
        return {
            "name": "Interview Prep Intelligence Agent (IPIA)",
            "version": "1.0.0",
            "description": "Multi-agent system for intelligent interview question generation",
            "capabilities": [
                "Context-aware decomposition of research data",
                "Multi-source RAG for comprehensive insights",
                "Chain-of-Thought prompting for question generation", 
                "Strategy-aware prompts for different question types",
                "Personalization engine based on user profile",
                "Memory-augmented generation with similarity checking",
                "Skill matching for role-specific questions",
                "Vector-based similarity for content optimization",
                "Behavioral RAG for STAR method questions",
                "State-persistent context across processing",
                "Multi-agent RAG for comprehensive prep summaries",
                "JSON structured output for easy integration"
            ],
            "sub_agents": [
                "ContextDecomposer - Research insight extraction",
                "QuestionGenerator - Specialized question creation", 
                "PrepSummarizer - Comprehensive summary generation"
            ],
            "supported_question_types": [
                "Company-Aware Questions",
                "Interviewer-Specific Questions", 
                "Role-Specific Questions",
                "General Behavioral Questions"
            ]
        }
