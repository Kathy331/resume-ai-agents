#!/usr/bin/env python3
"""
Comprehensive Interview Prep Report Generator
Shows detailed questions and preparation materials for SEEDS and JUTEQ interviews
"""

import asyncio
import sys
import os
from datetime import datetime

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from workflows.deep_research_pipeline import DeepResearchPipeline, create_sample_user_profile
from tests.test_interview_prep_intelligence.mock_data import MockResearchData


def print_banner(title: str, emoji: str = "🎯"):
    """Print a nice banner"""
    print("\n" + "=" * 100)
    print(f"{emoji} {title}")
    print("=" * 100)


def print_section(title: str, emoji: str = "📋"):
    """Print a section header"""
    print(f"\n{emoji} {title}")
    print("-" * 80)


def print_questions_detailed(summary, company_name: str):
    """Print detailed questions for a company"""
    print_section(f"DETAILED PREP QUESTIONS FOR {company_name.upper()}", "❓")
    
    # Get all question clusters from the summary
    clusters = []
    if hasattr(summary, 'company_questions') and summary.company_questions:
        clusters.append(summary.company_questions)
    if hasattr(summary, 'interviewer_questions') and summary.interviewer_questions:
        clusters.append(summary.interviewer_questions)
    if hasattr(summary, 'role_questions') and summary.role_questions:
        clusters.append(summary.role_questions)
    if hasattr(summary, 'behavioral_questions') and summary.behavioral_questions:
        clusters.append(summary.behavioral_questions)
    
    if not clusters:
        print("   ❌ No questions generated")
        return
    
    total_questions = 0
    total_time = 0
    
    for cluster in clusters:
        if not cluster or not cluster.questions:
            continue
            
        cluster_questions = len(cluster.questions)
        total_questions += cluster_questions
        total_time += cluster.estimated_time_minutes
        
        print(f"\n   📂 {cluster.cluster_name} ({cluster_questions} questions)")
        print(f"      ⏰ Time: {cluster.estimated_time_minutes} min | 🎯 Priority: {cluster.priority_score:.1f}")
        
        for i, question in enumerate(cluster.questions, 1):
            print(f"\n      {i}. {question.question_text}")
            print(f"         💡 Context: {question.context}")
            print(f"         📊 Level: {question.difficulty_level}")
            
            if question.expected_answer_points:
                points_str = ", ".join(question.expected_answer_points[:3])
                if len(question.expected_answer_points) > 3:
                    points_str += "..."
                print(f"         🎯 Key Points: {points_str}")
            
            if question.follow_up_questions and question.follow_up_questions[0]:
                print(f"         🔄 Follow-up: {question.follow_up_questions[0]}")
    
    print(f"\n   📊 TOTALS: {total_questions} questions, {total_time} minutes prep time")


def print_strategic_recommendations(summary, company_name: str):
    """Print strategic recommendations"""
    print_section(f"STRATEGIC PREP FOR {company_name.upper()}", "🎯")
    
    if hasattr(summary, 'success_strategies') and summary.success_strategies:
        print("   💡 SUCCESS STRATEGIES:")
        for i, strategy in enumerate(summary.success_strategies, 1):
            print(f"      {i}. {strategy}")
    
    if hasattr(summary, 'key_talking_points') and summary.key_talking_points:
        print("\n   🗣️  KEY TALKING POINTS:")
        for i, point in enumerate(summary.key_talking_points, 1):
            print(f"      {i}. {point}")
    
    if hasattr(summary, 'potential_concerns') and summary.potential_concerns:
        print("\n   ⚠️  POTENTIAL CONCERNS TO ADDRESS:")
        for i, concern in enumerate(summary.potential_concerns, 1):
            print(f"      {i}. {concern}")


async def generate_comprehensive_prep_guide():
    """Generate comprehensive prep guide for SEEDS and JUTEQ"""
    
    print_banner("COMPREHENSIVE INTERVIEW PREP GUIDE", "📚")
    print("🎯 Advanced AI-Generated Interview Preparation")
    print("🌱 SEEDS Program (Sustainability)")
    print("🤖 JUTEQ (AI & Cloud Engineering)")
    print(f"📅 Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}")
    
    # Initialize pipeline
    pipeline = DeepResearchPipeline()
    user_profile = create_sample_user_profile()
    
    # Create mock workflow results
    workflow_results = MockResearchData.create_mock_workflow_results()
    
    print_section("SYSTEM INFORMATION", "🤖")
    print("   🔧 Engine: Interview Prep Intelligence Agent (IPIA) v2.0")
    print("   🧠 AI Techniques: Chain-of-Thought, Multi-Agent RAG, Strategic Prompting")
    print("   🔄 Research Flow: Deep Research → Synthesis → Reflection → Dynamic Questions")
    print("   📊 Cache Status: Active (reduces API costs)")
    print("   🎯 Context-Aware: Yes (adapts to company culture)")
    print("   ⚡ New Features: Content Synthesis, Reflection Loops, Dynamic Question Generation")
    
    # Process through IPIA
    print_section("PROCESSING INTERVIEWS", "🚀")
    print("   🧩 Extracting research contexts...")
    print("   🧠 Running multi-agent analysis...")
    print("   🌐 Performing deep web research...")
    print("   🔬 Synthesizing insights with LLM...")
    print("   🔄 Running reflection loops...")
    print("   ❓ Generating dynamic questions...")
    print("   📝 Creating prep summaries...")
    
    try:
        # Create research contexts directly for enhanced pipeline testing
        from workflows.deep_research_pipeline import ResearchContext
        
        research_contexts = [
            ResearchContext(
                interview_id="seeds_ai_researcher_001",
                company_name="SEEDS",
                role_title="AI Researcher",
                interviewer_name="Dr. Emily Chen",
                quality_score=0.85,
                research_confidence=0.9
            ),
            ResearchContext(
                interview_id="juteq_cloud_engineer_001", 
                company_name="JUTEQ",
                role_title="Cloud Engineer",
                interviewer_name="Alex Rodriguez",
                quality_score=0.88,
                research_confidence=0.92
            )
        ]
        
        # Create enhanced research input
        from workflows.deep_research_pipeline import DeepResearchInput
        deep_research_input = DeepResearchInput(
            research_contexts=research_contexts,
            user_profile=user_profile
        )
        
        # Process through enhanced pipeline with REAL research
        deep_research_output = await pipeline.async_process(deep_research_input)
        
        if not deep_research_output or not deep_research_output.prep_summaries:
            print("   ❌ No prep summaries generated")
            return
        
        print(f"   ✅ Generated {len(deep_research_output.prep_summaries)} comprehensive prep packages")
        
        # Process each interview
        for i, summary in enumerate(deep_research_output.prep_summaries):
            company_name = "SEEDS" if "seeds" in summary.interview_id.lower() else "JUTEQ"
            
            print_banner(f"INTERVIEW #{i+1}: {company_name}", "🎯")
            
            # Basic info
            print(f"🏢 Company: {company_name}")
            print(f"📧 Interview ID: {summary.interview_id}")
            
            # Count total questions
            total_questions = 0
            if hasattr(summary, 'company_questions') and summary.company_questions:
                total_questions += len(summary.company_questions.questions)
            if hasattr(summary, 'interviewer_questions') and summary.interviewer_questions:
                total_questions += len(summary.interviewer_questions.questions)
            if hasattr(summary, 'role_questions') and summary.role_questions:
                total_questions += len(summary.role_questions.questions)
            if hasattr(summary, 'behavioral_questions') and summary.behavioral_questions:
                total_questions += len(summary.behavioral_questions.questions)
            
            print(f"❓ Questions Generated: {total_questions}")
            print(f"⏰ Total Prep Time: {getattr(summary, 'estimated_prep_time_minutes', 0)} minutes")
            print(f"🎯 Confidence Score: {getattr(summary, 'confidence_score', 0):.2f}")
            
            # Detailed questions
            print_questions_detailed(summary, company_name)
            
            # Strategic recommendations
            print_strategic_recommendations(summary, company_name)
            
            # Company-specific insights
            if company_name == "SEEDS":
                print_section("SEEDS-SPECIFIC INSIGHTS", "🌱")
                print("   🌍 Focus: Environmental sustainability and social impact")
                print("   💡 Strategy: Emphasize environmental awareness and sustainable practices")
                print("   🎯 Keywords: Sustainability, impact, environmental responsibility, social good")
                print("   📈 Growth Areas: Green technology, carbon reduction, social entrepreneurship")
            
            elif company_name == "JUTEQ":
                print_section("JUTEQ-SPECIFIC INSIGHTS", "🤖")
                print("   💻 Focus: AI & Cloud Engineering, technical innovation")
                print("   💡 Strategy: Highlight technical skills and cloud/AI experience")
                print("   🎯 Keywords: Artificial Intelligence, Cloud Computing, Engineering, Innovation")
                print("   📈 Growth Areas: AI/ML development, cloud architecture, technical leadership")
        
        # Final recommendations
        print_banner("FINAL PREPARATION RECOMMENDATIONS", "🎯")
        print("📚 STUDY PLAN:")
        print("   1. Review each company's recent news and developments")
        print("   2. Practice STAR method for behavioral questions")
        print("   3. Prepare specific examples from your experience")
        print("   4. Research the interviewers' backgrounds on LinkedIn")
        print("   5. Prepare thoughtful questions about company culture and growth")
        
        print("\n🎯 SUCCESS METRICS:")
        print("   • Demonstrate genuine interest in each company's mission")
        print("   • Show alignment between your skills and role requirements")
        print("   • Provide concrete examples using the STAR method")
        print("   • Ask insightful questions about company direction")
        
        print("\n📊 CACHE PERFORMANCE:")
        from shared.openai_cache import OpenAICache
        from shared.tavily_client import get_tavily_cache_stats
        
        # OpenAI Cache Stats
        openai_cache = OpenAICache()
        openai_stats = openai_cache.get_cache_stats()
        print(f"   🤖 OpenAI Cache Entries: {openai_stats['total_entries']}")
        print(f"   🤖 OpenAI Companies Cached: {len(openai_stats['companies_cached'])}")
        if openai_stats['companies_cached']:
            print(f"   🤖 OpenAI Cached: {', '.join(openai_stats['companies_cached'])}")
        
        # Tavily Cache Stats
        tavily_stats = get_tavily_cache_stats()
        if tavily_stats.get('cache_enabled', False):
            print(f"   🌐 Tavily Cache Entries: {tavily_stats.get('total_entries', 0)}")
            print(f"   🌐 Tavily Cache Hits: {tavily_stats.get('cache_hits', 0)}")
            print(f"   🌐 Tavily API Calls Saved: ${tavily_stats.get('estimated_savings', 0):.2f}")
        else:
            print(f"   🌐 Tavily Cache: {tavily_stats.get('message', 'Not available')}")
        
        print_banner("PREP GUIDE COMPLETE - GOOD LUCK! 🍀", "🎉")
        
    except Exception as e:
        print(f"   ❌ Error generating prep guide: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(generate_comprehensive_prep_guide())
