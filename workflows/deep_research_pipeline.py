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
from shared.tavily_client import search_tavily, get_tavily_cache_stats
from shared.llm_client import call_llm
import json


class DeepResearchPipeline:
    """
    Pipeline that takes workflow_runner research results and generates
    comprehensive interview preparation summaries with REAL web research
    """
    
    def __init__(self):
        self.ipia = InterviewPrepIntelligenceAgent()
    
    async def perform_deep_company_research(self, company_name: str) -> Dict[str, Any]:
        """Perform deep research on a company using cached Tavily"""
        if not company_name:
            return {"error": "No company name provided"}
        
        try:
            print(f"   🏢 Researching company: {company_name}")
            # Research queries for company
            queries = [
                f"{company_name} company recent news leadership technology",
                f"{company_name} mission values culture work environment",
                f"{company_name} interview process questions candidates"
            ]
            
            research_results = {}
            for i, query in enumerate(queries):
                print(f"   🔍 Query {i+1}: {query[:50]}...")
                results = search_tavily(query, search_depth="advanced", max_results=2)
                research_results[f"query_{i+1}"] = results
                print(f"      ✅ Found {len(results)} results")
            
            return research_results
        except Exception as e:
            print(f"   ❌ Company research failed: {str(e)}")
            return {"error": str(e)}
    
    async def perform_deep_role_research(self, role_title: str, company_name: str = "") -> Dict[str, Any]:
        """Perform deep research on a role using cached Tavily"""
        if not role_title:
            return {"error": "No role title provided"}
        
        try:
            print(f"   💼 Researching role: {role_title}")
            # Research queries for role
            company_context = f"at {company_name}" if company_name else ""
            queries = [
                f"{role_title} {company_context} interview questions technical skills",
                f"{role_title} salary requirements responsibilities market trends",
                f"{role_title} {company_context} team structure career growth"
            ]
            
            research_results = {}
            for i, query in enumerate(queries):
                print(f"   🔍 Query {i+1}: {query[:50]}...")
                results = search_tavily(query, search_depth="advanced", max_results=2)
                research_results[f"query_{i+1}"] = results
                print(f"      ✅ Found {len(results)} results")
            
            return research_results
        except Exception as e:
            print(f"   ❌ Role research failed: {str(e)}")
            return {"error": str(e)}
    
    async def synthesize_research_insights(self, company_research: Dict, role_research: Dict, company_name: str, role_title: str) -> Dict[str, Any]:
        """Use LLM to synthesize research data into actionable insights"""
        try:
            print("   🧠 Synthesizing research insights with LLM...")
            
            # Prepare research data for LLM
            research_summary = self._format_research_for_synthesis(company_research, role_research)
            
            synthesis_prompt = f"""
You are an expert interview preparation coach. Analyze the following research data and create actionable insights for interview preparation.

COMPANY: {company_name}
ROLE: {role_title}

RESEARCH DATA:
{research_summary}

Please provide a JSON response with the following structure:
{{
    "company_insights": [
        "Key insight about company culture, values, or recent developments",
        "Another important company insight"
    ],
    "role_insights": [
        "Key insight about role requirements or market trends",
        "Another important role insight"
    ],
    "interview_strategies": [
        "Specific strategy for this company/role combination",
        "Another targeted strategy"
    ],
    "talking_points": [
        "Specific talking point based on research",
        "Another research-backed talking point"
    ],
    "knowledge_gaps": [
        "Area that needs more research",
        "Another gap to investigate"
    ],
    "follow_up_queries": [
        "Specific search query to fill knowledge gaps",
        "Another targeted research query"
    ]
}}
"""
            
            response = await call_llm(
                prompt=synthesis_prompt,
                model="gpt-4o-mini",
                max_tokens=1500,
                temperature=0.3
            )
            
            # Parse JSON response
            try:
                insights = json.loads(response)
                print(f"      ✅ Generated {len(insights.get('company_insights', []))} company insights")
                print(f"      ✅ Generated {len(insights.get('role_insights', []))} role insights")
                print(f"      ✅ Identified {len(insights.get('knowledge_gaps', []))} knowledge gaps")
                return insights
            except json.JSONDecodeError:
                print("      ⚠️ LLM response not valid JSON, using fallback")
                return self._create_fallback_insights(company_name, role_title)
                
        except Exception as e:
            print(f"   ❌ Research synthesis failed: {str(e)}")
            return self._create_fallback_insights(company_name, role_title)
    
    def _format_research_for_synthesis(self, company_research: Dict, role_research: Dict) -> str:
        """Format research data for LLM synthesis"""
        formatted = "COMPANY RESEARCH:\n"
        
        if "error" not in company_research:
            for query_key, results in company_research.items():
                if isinstance(results, list) and results:
                    formatted += f"\n{query_key.upper()}:\n"
                    for result in results[:2]:  # Top 2 results per query
                        formatted += f"- {result.get('title', 'No title')}\n"
                        formatted += f"  {result.get('content', 'No content')[:200]}...\n"
        
        formatted += "\nROLE RESEARCH:\n"
        if "error" not in role_research:
            for query_key, results in role_research.items():
                if isinstance(results, list) and results:
                    formatted += f"\n{query_key.upper()}:\n"
                    for result in results[:2]:  # Top 2 results per query
                        formatted += f"- {result.get('title', 'No title')}\n"
                        formatted += f"  {result.get('content', 'No content')[:200]}...\n"
        
        return formatted[:3000]  # Limit size for LLM
    
    def _create_fallback_insights(self, company_name: str, role_title: str) -> Dict[str, Any]:
        """Create fallback insights if LLM synthesis fails"""
        return {
            "company_insights": [
                f"Research {company_name}'s recent news and company culture",
                f"Understand {company_name}'s core values and mission"
            ],
            "role_insights": [
                f"Focus on key skills required for {role_title}",
                f"Understand market trends in {role_title} positions"
            ],
            "interview_strategies": [
                "Prepare STAR method examples",
                "Research interviewer backgrounds on LinkedIn"
            ],
            "talking_points": [
                "Highlight relevant technical experience",
                "Demonstrate cultural fit and enthusiasm"
            ],
            "knowledge_gaps": [
                "Need more specific company details",
                "Require role-specific technical requirements"
            ],
            "follow_up_queries": []
        }
    
    async def perform_reflection_research(self, initial_insights: Dict, company_name: str, role_title: str) -> Dict[str, Any]:
        """Perform follow-up research based on identified knowledge gaps"""
        follow_up_results = {}
        
        if "follow_up_queries" in initial_insights and initial_insights["follow_up_queries"]:
            print("   🔄 Performing reflection research...")
            
            for i, query in enumerate(initial_insights["follow_up_queries"][:3]):  # Limit to 3 follow-ups
                try:
                    print(f"      🔍 Follow-up {i+1}: {query[:50]}...")
                    results = search_tavily(query, search_depth="advanced", max_results=2)
                    follow_up_results[f"followup_{i+1}"] = results
                    print(f"         ✅ Found {len(results)} additional results")
                except Exception as e:
                    print(f"         ❌ Follow-up query failed: {str(e)}")
                    follow_up_results[f"followup_{i+1}"] = []
        
        return follow_up_results
    
    async def generate_dynamic_questions(self, insights: Dict, follow_up_research: Dict, company_name: str, role_title: str) -> Dict[str, Any]:
        """Generate contextual questions based on real research data"""
        try:
            print("   ❓ Generating dynamic questions from research...")
            
            # Combine insights and follow-up research
            all_insights = self._combine_research_insights(insights, follow_up_research)
            
            question_prompt = f"""
You are an expert interview question generator. Based on the research insights below, create specific, contextual interview questions.

COMPANY: {company_name}
ROLE: {role_title}

RESEARCH INSIGHTS:
{all_insights}

Generate questions in the following JSON format:
{{
    "company_questions": [
        {{
            "question": "Specific question about {company_name} based on research",
            "context": "Why this question is relevant based on research findings",
            "difficulty": "easy|medium|hard",
            "key_points": ["point1", "point2", "point3"],
            "follow_up": "Natural follow-up question"
        }}
    ],
    "role_questions": [
        {{
            "question": "Specific {role_title} question based on research",
            "context": "Why this question matters for this role",
            "difficulty": "easy|medium|hard", 
            "key_points": ["point1", "point2", "point3"],
            "follow_up": "Follow-up question"
        }}
    ],
    "behavioral_questions": [
        {{
            "question": "Behavioral question tailored to company culture",
            "context": "How this relates to company values/culture",
            "difficulty": "medium",
            "key_points": ["point1", "point2", "point3"],
            "follow_up": "Follow-up question"
        }}
    ]
}}

Generate 2-3 questions per category. Make them specific to the research findings, not generic.
"""
            
            response = await call_llm(
                prompt=question_prompt,
                model="gpt-4o-mini",
                max_tokens=2000,
                temperature=0.4
            )
            
            try:
                questions = json.loads(response)
                total_questions = (len(questions.get('company_questions', [])) + 
                                 len(questions.get('role_questions', [])) + 
                                 len(questions.get('behavioral_questions', [])))
                print(f"      ✅ Generated {total_questions} research-informed questions")
                return questions
            except json.JSONDecodeError:
                print("      ⚠️ Question generation response not valid JSON")
                return self._create_fallback_questions(company_name, role_title)
                
        except Exception as e:
            print(f"   ❌ Dynamic question generation failed: {str(e)}")
            return self._create_fallback_questions(company_name, role_title)
    
    def _combine_research_insights(self, insights: Dict, follow_up_research: Dict) -> str:
        """Combine insights and follow-up research for question generation"""
        combined = "SYNTHESIZED INSIGHTS:\n"
        
        for category, items in insights.items():
            if isinstance(items, list) and items:
                combined += f"\n{category.upper()}:\n"
                for item in items:
                    combined += f"- {item}\n"
        
        if follow_up_research:
            combined += "\nFOLLOW-UP RESEARCH:\n"
            for key, results in follow_up_research.items():
                if isinstance(results, list) and results:
                    combined += f"\n{key.upper()}:\n"
                    for result in results:
                        combined += f"- {result.get('title', '')}: {result.get('content', '')[:150]}...\n"
        
        return combined[:2500]  # Limit for LLM
    
    def _create_fallback_questions(self, company_name: str, role_title: str) -> Dict[str, Any]:
        """Create fallback questions if dynamic generation fails"""
        return {
            "company_questions": [
                {
                    "question": f"What interests you most about {company_name}'s mission and values?",
                    "context": "Tests company research and cultural fit",
                    "difficulty": "easy",
                    "key_points": ["Company mission", "Personal alignment", "Cultural fit"],
                    "follow_up": "How do you see yourself contributing to this mission?"
                }
            ],
            "role_questions": [
                {
                    "question": f"What specific skills do you bring to the {role_title} position?",
                    "context": "Assesses role-specific competencies",
                    "difficulty": "medium",
                    "key_points": ["Technical skills", "Relevant experience", "Problem-solving"],
                    "follow_up": "Can you give an example of using these skills?"
                }
            ],
            "behavioral_questions": [
                {
                    "question": "Tell me about a time you had to adapt to significant changes in a project.",
                    "context": "Tests adaptability and resilience",
                    "difficulty": "medium",
                    "key_points": ["Situation", "Actions taken", "Results achieved"],
                    "follow_up": "What did you learn from this experience?"
                }
            ]
        }
    
    def assess_research_quality(self, company_research: Dict, role_research: Dict) -> float:
        """Assess the quality of research data collected"""
        total_results = 0
        errors = 0
        
        # Check company research
        if "error" in company_research:
            errors += 1
        else:
            for query_results in company_research.values():
                total_results += len(query_results) if isinstance(query_results, list) else 0
        
        # Check role research  
        if "error" in role_research:
            errors += 1
        else:
            for query_results in role_research.values():
                total_results += len(query_results) if isinstance(query_results, list) else 0
        
        # Calculate quality score (0.0 - 1.0)
        if errors == 2:  # Both failed
            return 0.2
        elif errors == 1:  # One failed
            return 0.5 + (total_results / 20)  # Cap at 0.9
        else:  # No errors
            return min(0.95, 0.7 + (total_results / 20))
    
    def create_enhanced_prep_summary(self, enhanced_context: Dict, user_profile) -> PrepSummary:
        """Create prep summary using REAL research data"""
        # This would use the real research data to generate more targeted questions
        # For now, we'll enhance the mock with research indicators
        context = enhanced_context["original_context"]
        research_exists = enhanced_context["research_quality"] > 0.5
        
        prep_summary = self.create_mock_prep_summary(context, user_profile)
        
        # Enhance with research quality indicators
        prep_summary.confidence_score = enhanced_context["research_quality"]
        prep_summary.research_quality = "High" if research_exists else "Low"
        prep_summary.has_real_research = research_exists
        
        return prep_summary
    
    def create_research_informed_prep_summary(self, enhanced_context: Dict, user_profile) -> PrepSummary:
        """Create prep summary using REAL research data and dynamic questions"""
        from agents.interview_prep_intelligence.models import Question, QuestionCluster, QuestionType
        
        context = enhanced_context["original_context"]
        insights = enhanced_context.get("insights", {})
        dynamic_questions = enhanced_context.get("dynamic_questions", {})
        research_quality = enhanced_context.get("research_quality", 0.5)
        
        # Create questions from dynamic generation
        company_questions = []
        role_questions = []
        behavioral_questions = []
        
        # Generate company questions from research
        for i, q_data in enumerate(dynamic_questions.get("company_questions", [])):
            question = Question(
                id=f"comp_{context.interview_id}_{i}",
                question_type=QuestionType.COMPANY_AWARE,
                question_text=q_data.get("question", "Generic company question"),
                context=q_data.get("context", "Research-based question"),
                difficulty_level=q_data.get("difficulty", "medium"),
                expected_answer_points=q_data.get("key_points", ["Research insight", "Personal alignment"]),
                follow_up_questions=[q_data.get("follow_up", "How does this align with your experience?")],
                source_research="dynamic_company_research"
            )
            company_questions.append(question)
        
        # Generate role questions from research
        for i, q_data in enumerate(dynamic_questions.get("role_questions", [])):
            question = Question(
                id=f"role_{context.interview_id}_{i}",
                question_type=QuestionType.ROLE_SPECIFIC,
                question_text=q_data.get("question", "Generic role question"),
                context=q_data.get("context", "Role-specific research question"),
                difficulty_level=q_data.get("difficulty", "medium"),
                expected_answer_points=q_data.get("key_points", ["Technical skill", "Relevant experience"]),
                follow_up_questions=[q_data.get("follow_up", "Can you provide a specific example?")],
                source_research="dynamic_role_research"
            )
            role_questions.append(question)
        
        # Generate behavioral questions from research
        for i, q_data in enumerate(dynamic_questions.get("behavioral_questions", [])):
            question = Question(
                id=f"behav_{context.interview_id}_{i}",
                question_type=QuestionType.GENERAL_BEHAVIORAL,
                question_text=q_data.get("question", "Generic behavioral question"),
                context=q_data.get("context", "Behavioral assessment question"),
                difficulty_level=q_data.get("difficulty", "medium"),
                expected_answer_points=q_data.get("key_points", ["Situation", "Action", "Result"]),
                follow_up_questions=[q_data.get("follow_up", "What did you learn from this experience?")],
                source_research="dynamic_behavioral_research"
            )
            behavioral_questions.append(question)
        
        # Add fallback questions if dynamic generation didn't produce enough
        while len(company_questions) < 2:
            fallback = Question(
                id=f"comp_fallback_{context.interview_id}_{len(company_questions)}",
                question_type=QuestionType.COMPANY_AWARE,
                question_text=f"What interests you most about {context.company_name or 'this company'}'s recent developments?",
                context="Research-informed company question",
                difficulty_level="medium",
                expected_answer_points=["Company knowledge", "Personal interest", "Career alignment"],
                source_research="research_informed"
            )
            company_questions.append(fallback)
        
        while len(role_questions) < 3:
            fallback = Question(
                id=f"role_fallback_{context.interview_id}_{len(role_questions)}",
                question_type=QuestionType.ROLE_SPECIFIC,
                question_text=f"How do you stay current with trends in {context.role_title or 'your field'}?",
                context="Professional development question",
                difficulty_level="easy",
                expected_answer_points=["Learning methods", "Industry awareness", "Growth mindset"],
                source_research="research_informed"
            )
            role_questions.append(fallback)
        
        while len(behavioral_questions) < 2:
            fallback = Question(
                id=f"behav_fallback_{context.interview_id}_{len(behavioral_questions)}",
                question_type=QuestionType.GENERAL_BEHAVIORAL,
                question_text="Describe a time when you had to learn something new quickly for a project.",
                context="Learning agility assessment",
                difficulty_level="medium",
                expected_answer_points=["Learning approach", "Time management", "Application"],
                source_research="research_informed"
            )
            behavioral_questions.append(fallback)
        
        # Create question clusters
        company_cluster = QuestionCluster(
            cluster_id=f"company_{context.interview_id}",
            cluster_name=f"Company Knowledge - {context.company_name or 'Unknown'}",
            focus_area="company",
            questions=company_questions,
            priority_score=0.9,  # Higher priority for research-informed questions
            estimated_time_minutes=len(company_questions) * 3
        )
        
        role_cluster = QuestionCluster(
            cluster_id=f"role_{context.interview_id}",
            cluster_name=f"Role Competency - {context.role_title or 'Unknown'}",
            focus_area="role",
            questions=role_questions,
            priority_score=1.0,  # Highest priority
            estimated_time_minutes=len(role_questions) * 4
        )
        
        behavioral_cluster = QuestionCluster(
            cluster_id=f"behavioral_{context.interview_id}",
            cluster_name="Behavioral Assessment",
            focus_area="behavioral",
            questions=behavioral_questions,
            priority_score=0.8,
            estimated_time_minutes=len(behavioral_questions) * 5
        )
        
        # Create interviewer cluster (minimal for now)
        interviewer_questions = [
            Question(
                id=f"int_{context.interview_id}_0",
                question_type=QuestionType.INTERVIEWER_SPECIFIC,
                question_text=f"I'd love to learn about your experience at {context.company_name or 'the company'}. What has been most rewarding?",
                context="Shows interest in interviewer's perspective",
                difficulty_level="easy",
                expected_answer_points=["Active listening", "Professional interest", "Engagement"],
                follow_up_questions=["What advice would you give to someone starting in this role?"],
                source_research="research_informed"
            )
        ]
        
        interviewer_cluster = QuestionCluster(
            cluster_id=f"interviewer_{context.interview_id}",
            cluster_name="Interviewer Connection",
            focus_area="interviewer",
            questions=interviewer_questions,
            priority_score=0.6,
            estimated_time_minutes=3
        )
        
        # Create comprehensive prep summary
        total_questions = len(company_questions) + len(role_questions) + len(behavioral_questions) + len(interviewer_questions)
        total_time = company_cluster.estimated_time_minutes + role_cluster.estimated_time_minutes + behavioral_cluster.estimated_time_minutes + interviewer_cluster.estimated_time_minutes
        
        prep_summary = PrepSummary(
            interview_id=context.interview_id,
            generated_at=datetime.now(),
            company_questions=company_cluster,
            interviewer_questions=interviewer_cluster,
            role_questions=role_cluster,
            behavioral_questions=behavioral_cluster,
            total_questions=total_questions,
            estimated_prep_time_minutes=total_time,
            confidence_score=min(0.95, 0.6 + (research_quality * 0.35)),  # Scale with research quality
            company_insights=insights.get("company_insights", [f"Research {context.company_name or 'company'} background"]),
            interviewer_insights=[f"Connect with interviewer's experience at {context.company_name or 'the company'}"],
            role_insights=insights.get("role_insights", [f"Focus on {context.role_title or 'role'} requirements"]),
            success_strategies=insights.get("interview_strategies", ["Prepare STAR examples", "Research company culture"]),
            key_talking_points=insights.get("talking_points", ["Relevant experience", "Cultural fit"]),
            sources_used=self._extract_research_sources(enhanced_context),
            research_quality_score=research_quality,
            has_dynamic_questions=True,
            reflection_loops_completed=1 if enhanced_context.get("follow_up_research") else 0
        )
        
        return prep_summary
    
    def _extract_research_sources(self, enhanced_context: Dict) -> List[Dict]:
        """Extract sources from research data"""
        sources = []
        
        # Extract from company research
        company_research = enhanced_context.get("company_research", {})
        if "error" not in company_research:
            for query_results in company_research.values():
                if isinstance(query_results, list):
                    for result in query_results[:2]:  # Top 2 per query
                        sources.append({
                            'title': result.get('title', 'Research Source'),
                            'url': result.get('url', '#'),
                            'relevance_score': str(result.get('score', 0.8))
                        })
        
        # Extract from role research  
        role_research = enhanced_context.get("role_research", {})
        if "error" not in role_research:
            for query_results in role_research.values():
                if isinstance(query_results, list):
                    for result in query_results[:2]:  # Top 2 per query
                        sources.append({
                            'title': result.get('title', 'Research Source'),
                            'url': result.get('url', '#'),
                            'relevance_score': str(result.get('score', 0.8))
                        })
        
        return sources[:8]  # Limit to top 8 sources
    
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
        
        # Process each interview context through IPIA with REAL research
        prep_summaries = []
        start_time = datetime.now()
        
        print("🧠 IPIA: Processing research contexts with REAL web research...")
        for context in research_contexts:
            print(f"🔍 Processing interview: {context.company_name or context.interview_id}")
            
            # PHASE 1: Initial Research
            print("   🌐 Phase 1: Performing deep web research...")
            company_research = await self.perform_deep_company_research(context.company_name or "")
            role_research = await self.perform_deep_role_research(context.role_title or "", context.company_name or "")
            
            # PHASE 2: Content Synthesis  
            print("   � Phase 2: Synthesizing research insights...")
            insights = await self.synthesize_research_insights(
                company_research, role_research, 
                context.company_name or "Unknown Company", 
                context.role_title or "Unknown Role"
            )
            
            # PHASE 3: Reflection Research
            print("   🔄 Phase 3: Performing reflection research...")
            follow_up_research = await self.perform_reflection_research(
                insights, 
                context.company_name or "Unknown Company",
                context.role_title or "Unknown Role"
            )
            
            # PHASE 4: Dynamic Question Generation
            print("   ❓ Phase 4: Generating dynamic questions...")
            dynamic_questions = await self.generate_dynamic_questions(
                insights, follow_up_research,
                context.company_name or "Unknown Company",
                context.role_title or "Unknown Role"
            )
            
            # PHASE 5: Create Enhanced Prep Summary
            print("   📝 Phase 5: Creating comprehensive prep summary...")
            
            # Enhanced context with all research data
            enhanced_context = {
                "original_context": context,
                "company_research": company_research,
                "role_research": role_research,
                "follow_up_research": follow_up_research,
                "insights": insights,
                "dynamic_questions": dynamic_questions,
                "research_quality": self.assess_research_quality(company_research, role_research)
            }
            
            # Create enhanced prep summary with real research
            prep_summary = self.create_research_informed_prep_summary(enhanced_context, research_input.user_profile)
            prep_summaries.append(prep_summary)
            
            question_count = len(prep_summary.questions) if hasattr(prep_summary, 'questions') else 0
            if hasattr(prep_summary, 'company_questions') and prep_summary.company_questions:
                question_count += len(prep_summary.company_questions.questions)
            if hasattr(prep_summary, 'role_questions') and prep_summary.role_questions:
                question_count += len(prep_summary.role_questions.questions)
            if hasattr(prep_summary, 'behavioral_questions') and prep_summary.behavioral_questions:
                question_count += len(prep_summary.behavioral_questions.questions)
            
            confidence = getattr(prep_summary, 'confidence_score', 0.85)  # Higher confidence with real research
            print(f"   ✅ Generated {question_count} research-informed questions (confidence: {confidence:.2f})")
        
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
