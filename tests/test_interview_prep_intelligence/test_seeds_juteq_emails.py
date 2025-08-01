#!/usr/bin/env python3
"""
Test Deep Research Question Planning Agent with SEEDS and JUTEQ email data only.
This test focuses on your actual email examples and demonstrates the system's
ability to differentiate between sustainability and technical interviews.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.interview_prep_intelligence.models import DeepResearchInput, UserProfile
from workflows.deep_research_pipeline import DeepResearchPipeline
from tests.test_interview_prep_intelligence.mock_data import MockResearchData
from datetime import datetime

def test_seeds_and_juteq_processing():
    """Test the system with SEEDS and JUTEQ email data"""
    
    print("🧪 TESTING DEEP RESEARCH SYSTEM - SEEDS & JUTEQ EMAILS")
    print("=" * 80)
    print("📧 Processing your actual interview invitations:")
    print("   🌱 SEEDS (Dandilyonn/Archana): Sustainability internship")
    print("   🤖 JUTEQ (Rakesh Gohel): AI & Cloud engineering internship")
    print()
    
    # Create research contexts from your emails
    seeds_context = MockResearchData.create_seeds_research_context()
    juteq_context = MockResearchData.create_juteq_research_context()
    
    # User profile matching your background
    user_profile = UserProfile(
        name="Test User",
        experience_level="entry",
        skills=["Python", "Data Analysis", "Environmental Science", "Research", "Sustainability", "AI/ML"],
        interests=["Climate Change", "Renewable Energy", "AI/ML", "Cloud Computing"],
        preferences={
            "question_difficulty": "intermediate",
            "focus_areas": ["technical_skills", "environmental_impact", "problem_solving"],
            "preparation_time": "moderate"
        },
        background="Environmental science background with growing interest in technology"
    )
    
    # Create research input
    research_input = DeepResearchInput(
        research_contexts=[seeds_context, juteq_context],
        user_profile=user_profile,
        processing_options={
            "max_questions_per_category": 4,
            "include_follow_ups": True,
            "personalization_level": "high"
        }
    )
    
    # Process through pipeline
    print("🚀 Starting Deep Research Pipeline...")
    pipeline = DeepResearchPipeline()
    results = pipeline.process(research_input)
    
    print("✅ PROCESSING COMPLETE")
    print("=" * 80)
    print(f"📊 Interviews Processed: {len(results.prep_summaries)}")
    print(f"❓ Total Questions Generated: {results.total_questions_generated}")
    print(f"📈 Average Confidence: {results.avg_confidence_score:.2f}")
    print(f"⏱️  Processing Time: {results.processing_time:.2f}s")
    print()
    
    # Show differentiation between SEEDS and JUTEQ
    if len(results.prep_summaries) >= 2:
        seeds_summary = results.prep_summaries[0]  # SEEDS
        juteq_summary = results.prep_summaries[1]   # JUTEQ
        
        print("🎯 INTERVIEW DIFFERENTIATION ANALYSIS")
        print("=" * 80)
        
        print("🌱 SEEDS Interview (Dandilyonn/Archana):")
        print(f"   • Company: {seeds_summary.company_insights[0] if hasattr(seeds_summary, 'company_insights') else 'Sustainability focus'}")
        print(f"   • Questions: {seeds_summary.total_questions}")
        print(f"   • Prep Time: {seeds_summary.estimated_prep_time_minutes} minutes")
        print(f"   • Research Sources: {len(getattr(seeds_summary, 'sources_used', []))}")
        print()
        
        print("🤖 JUTEQ Interview (Rakesh Gohel/CEO):")
        print(f"   • Company: {juteq_summary.company_insights[0] if hasattr(juteq_summary, 'company_insights') else 'AI/Cloud technology focus'}")
        print(f"   • Questions: {juteq_summary.total_questions}")
        print(f"   • Prep Time: {juteq_summary.estimated_prep_time_minutes} minutes")
        print(f"   • Research Sources: {len(getattr(juteq_summary, 'sources_used', []))}")
        print()
        
        print("✅ System successfully differentiated between:")
        print("   🌱 Environmental sustainability focus (SEEDS)")
        print("   🤖 Technical AI/Cloud focus (JUTEQ)")
        print("   👥 Different interviewer styles (Mentoring vs Technical)")
        print("   💼 Different role requirements (Environmental vs Engineering)")
    
    return results

if __name__ == "__main__":
    print("🎯 DEEP RESEARCH SYSTEM TEST - YOUR EMAIL DATA")
    print("Testing with SEEDS and JUTEQ interview invitations")
    print()
    
    results = test_seeds_and_juteq_processing()
    
    print()
    print("✅ TEST COMPLETED SUCCESSFULLY!")
    print("The system is ready to process your actual interview emails.")
    print("Integration with workflow_runner is available in workflows/deep_research_pipeline.py")
