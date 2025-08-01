# workflows/research_engine_pipeline.py
"""
Research Engine Pipeline with LangGraph Workflows

This pipeline implements intelligent research automation for unprepped interviews:
1. Fetch interviews that need research (status != 'prepped')
2. Extract entities from interview data
3. Orchestrated multi-agent research (Company, Interviewer, Role)
4. Quality assessment and validation
5. Memory update with research results

Flow:
Unprepped Interviews -> Entity Validation -> Multi-Agent Research -> 
Quality Assessment -> Memory Update -> Results Formatting
"""

import os
import sys
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from dataclasses import dataclass

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from shared.models import AgentInput, AgentOutput
from agents.memory_systems.interview_store.agents import InterviewStore
from shared.tavily_client import search_tavily


@dataclass
class ResearchRequest:
    """Research request structure"""
    interview_id: str
    company_name: Optional[str] = None
    interviewer_name: Optional[str] = None
    role_title: Optional[str] = None
    additional_context: Optional[str] = None
    priority: str = "normal"  # low, normal, high


@dataclass 
class ResearchResult:
    """Research result structure"""
    interview_id: str
    company_research: Optional[Dict[str, Any]] = None
    interviewer_research: Optional[Dict[str, Any]] = None
    role_research: Optional[Dict[str, Any]] = None
    quality_score: float = 0.0
    research_confidence: float = 0.0
    processing_time: float = 0.0
    errors: List[str] = None

    def __post_init__(self):
        if self.errors is None:
            self.errors = []


class ResearchEnginePipeline:
    """
    Advanced research pipeline for comprehensive interview preparation
    
    Leverages multiple research agents to gather intelligence on:
    - Company background and recent developments
    - Interviewer professional profile and background  
    - Role market analysis and requirements
    """
    
    def __init__(self, tavily_api_key: Optional[str] = None):
        # We'll use the search_tavily function directly instead of a client
        self.tavily_api_key = tavily_api_key
        
        # Initialize InterviewStore with default config
        interview_config = {
            "database_path": "./memory/interviews.db",
            "similarity_threshold": 0.8,
            "max_duplicates": 10
        }
        self.interview_store = InterviewStore(interview_config)
        
        # Research agents (will be initialized when needed)
        self._company_researcher = None
        self._interviewer_researcher = None
        self._role_researcher = None
        
    async def run_research_pipeline(self, max_interviews: int = 10, priority_filter: str = "all") -> Dict[str, Any]:
        """
        Main entry point for research pipeline
        
        Args:
            max_interviews: Maximum number of interviews to research
            priority_filter: Filter by priority level (all, high, normal, low)
            
        Returns:
            Dict containing pipeline results and statistics
        """
        start_time = datetime.now()
        
        try:
            print(f"🔬 Starting Research Engine Pipeline (max: {max_interviews})")
            
            # Step 1: Fetch unprepped interviews
            unprepped_interviews = await self._fetch_unprepped_interviews(max_interviews, priority_filter)
            
            if not unprepped_interviews:
                return {
                    'success': True,
                    'message': 'No unprepped interviews found',
                    'interviews_researched': 0,
                    'processing_time': (datetime.now() - start_time).total_seconds()
                }
            
            print(f"📋 Found {len(unprepped_interviews)} interviews needing research")
            
            # Step 2: Process each interview through research pipeline
            research_results = []
            successful_research = 0
            failed_research = 0
            
            for interview in unprepped_interviews:
                try:
                    research_request = self._create_research_request(interview)
                    result = await self._process_interview_research(research_request)
                    research_results.append(result)
                    
                    if result.quality_score > 0.5:  # Quality threshold
                        successful_research += 1
                        # Update interview status to 'prepped'
                        await self._update_interview_status(interview['id'], 'prepped', result)
                    else:
                        failed_research += 1
                        
                except Exception as e:
                    print(f"⚠️ Failed to research interview {interview.get('id', 'unknown')}: {str(e)}")
                    failed_research += 1
            
            # Step 3: Generate pipeline summary
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'success': True,
                'interviews_found': len(unprepped_interviews),
                'interviews_researched': successful_research,
                'failed_research': failed_research,
                'research_results': research_results,
                'processing_time': processing_time,
                'average_quality': sum(r.quality_score for r in research_results) / len(research_results) if research_results else 0,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'timestamp': datetime.now().isoformat()
            }
    
    async def _fetch_unprepped_interviews(self, max_interviews: int, priority_filter: str) -> List[Dict[str, Any]]:
        """
        Fetch interviews that need research (status != 'prepped')
        
        Returns list of interview records that need research
        """
        try:
            # Query interview store for unprepped interviews
            agent_input = AgentInput(data={
                'action': 'get_unprepped',
                'max_results': max_interviews,
                'priority_filter': priority_filter,
                'exclude_statuses': ['prepped', 'completed', 'archived']
            })
            
            result = await self.interview_store.execute(agent_input)
            
            if result.success:
                interviews = result.data.get('interviews', [])
                print(f"📊 Retrieved {len(interviews)} unprepped interviews")
                return interviews
            else:
                print(f"⚠️ Failed to fetch unprepped interviews: {result.errors}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching unprepped interviews: {str(e)}")
            return []
    
    def _create_research_request(self, interview: Dict[str, Any]) -> ResearchRequest:
        """Create research request from interview data"""
        entities = interview.get('entities', {})
        
        return ResearchRequest(
            interview_id=interview['id'],
            company_name=entities.get('COMPANY', [None])[0] if entities.get('COMPANY') else None,
            interviewer_name=entities.get('INTERVIEWER', [None])[0] if entities.get('INTERVIEWER') else None,
            role_title=entities.get('ROLE', [None])[0] if entities.get('ROLE') else None,
            additional_context=interview.get('email_subject', ''),
            priority=interview.get('priority', 'normal')
        )
    
    async def _process_interview_research(self, request: ResearchRequest) -> ResearchResult:
        """
        Process research for a single interview using multi-agent approach
        """
        research_start = datetime.now()
        result = ResearchResult(interview_id=request.interview_id)
        
        try:
            print(f"🔍 Researching interview: {request.interview_id}")
            
            # Initialize research agents
            await self._initialize_research_agents()
            
            # Execute research (now synchronous)
            research_results = []
            
            # Company research
            if request.company_name:
                company_result = self._research_company(request.company_name, request.additional_context)
                research_results.append(company_result)
            
            # Interviewer research  
            if request.interviewer_name:
                interviewer_result = self._research_interviewer(request.interviewer_name, request.company_name)
                research_results.append(interviewer_result)
            
            # Role research
            if request.role_title:
                role_result = self._research_role(request.role_title, request.company_name)
                research_results.append(role_result)
            
            # Process results
            for i, res in enumerate(research_results):
                if isinstance(res, Exception):
                    result.errors.append(f"Research task {i} failed: {str(res)}")
                    print(f"⚠️ Research task {i} failed: {str(res)}")
                elif isinstance(res, dict):
                    print(f"🔍 Research result {i}: type={res.get('type')}, source={res.get('source')}, has_data={bool(res.get('data'))}")
                    if res.get('type') == 'company':
                        result.company_research = res
                    elif res.get('type') == 'interviewer':
                        result.interviewer_research = res
                    elif res.get('type') == 'role':
                        result.role_research = res
            
            # Calculate quality scores
            result.quality_score = self._calculate_quality_score(result)
            result.research_confidence = self._calculate_confidence_score(result)
            result.processing_time = (datetime.now() - research_start).total_seconds()
            
            print(f"✅ Research completed for {request.interview_id}")
            print(f"   Quality: {result.quality_score:.2f} | Confidence: {result.research_confidence:.2f}")
            print(f"   Company: {bool(result.company_research)} | Interviewer: {bool(result.interviewer_research)} | Role: {bool(result.role_research)}")
            if result.errors:
                print(f"   Errors: {len(result.errors)}")
                for error in result.errors[:2]:  # Show first 2 errors
                    print(f"     - {error}")
            
        except Exception as e:
            result.errors.append(f"Research processing failed: {str(e)}")
            print(f"❌ Research failed for {request.interview_id}: {str(e)}")
        
        return result
    
    async def _initialize_research_agents(self):
        """Initialize research agents if not already done"""
        if not self._company_researcher:
            # Import research agents dynamically to avoid circular imports
            try:
                from agents.research_engine.company_researcher import CompanyResearcher
                from agents.research_engine.interviewer_researcher import InterviewerResearcher  
                from agents.research_engine.role_researcher import RoleResearcher
                
                self._company_researcher = CompanyResearcher()
                self._interviewer_researcher = InterviewerResearcher()
                self._role_researcher = RoleResearcher()
                
            except ImportError as e:
                print(f"⚠️ Could not import research agents: {str(e)}")
                # Fallback to basic Tavily client research
    
    def _research_company(self, company_name: str, context: str = "") -> Dict[str, Any]:
        """Research company using CompanyResearcher or fallback to Tavily"""
        try:
            if self._company_researcher:
                # This would be async if we had the actual research agents
                # result = await self._company_researcher.research_company(company_name, deep_search=True)
                # For now, fall back to Tavily
                pass
            
            # Fallback to direct Tavily search
            query = f"{company_name} company overview recent news technology {context}"
            print(f"🔍 Tavily search query: {query}")
            results = search_tavily(query, search_depth="advanced", max_results=8)
            print(f"🔍 Tavily results: {len(results)} items found")
            return {
                'type': 'company',
                'data': {'search_results': results, 'company_name': company_name, 'query': query},
                'source': 'TavilyClient'
            }
        except Exception as e:
            print(f"❌ Company research error: {str(e)}")
            return {
                'type': 'company',
                'error': str(e),
                'source': 'error'
            }
    
    def _research_interviewer(self, interviewer_name: str, company: str = "") -> Dict[str, Any]:
        """Research interviewer using InterviewerResearcher or fallback to Tavily"""
        try:
            if self._interviewer_researcher:
                # This would be async if we had the actual research agents
                pass
            
            # Fallback to direct Tavily search
            query = f"{interviewer_name} {company} linkedin professional background"
            print(f"🔍 Interviewer search query: {query}")
            results = search_tavily(query, search_depth="advanced", max_results=5)
            print(f"🔍 Interviewer results: {len(results)} items found")
            return {
                'type': 'interviewer',
                'data': {'search_results': results, 'interviewer_name': interviewer_name, 'query': query},
                'source': 'TavilyClient'
            }
        except Exception as e:
            return {
                'type': 'interviewer', 
                'error': str(e),
                'source': 'error'
            }
    
    def _research_role(self, role_title: str, company: str = "") -> Dict[str, Any]:
        """Research role using RoleResearcher or fallback to Tavily"""
        try:
            if self._role_researcher:
                # This would be async if we had the actual research agents
                pass
            
            # Fallback to direct Tavily search
            query = f"{role_title} {company} job requirements salary skills responsibilities"
            print(f"🔍 Role search query: {query}")
            results = search_tavily(query, search_depth="basic", max_results=6)
            print(f"🔍 Role results: {len(results)} items found")
            return {
                'type': 'role',
                'data': {'search_results': results, 'role_title': role_title, 'query': query},
                'source': 'TavilyClient'
            }
        except Exception as e:
            print(f"❌ Role research error: {str(e)}")
            return {
                'type': 'role',
                'error': str(e),
                'source': 'error'
            }
    
    def _calculate_quality_score(self, result: ResearchResult) -> float:
        """Calculate research quality score based on completeness and success"""
        score = 0.0
        max_score = 3.0  # Company + Interviewer + Role
        
        # Company research score
        if result.company_research and not result.company_research.get('error'):
            score += 1.0
            # Bonus for rich data
            company_data = result.company_research.get('data', {})
            if isinstance(company_data, dict) and len(company_data) > 3:
                score += 0.2
        
        # Interviewer research score
        if result.interviewer_research and not result.interviewer_research.get('error'):
            score += 1.0
            # Bonus for professional details
            interviewer_data = result.interviewer_research.get('data', {})
            if isinstance(interviewer_data, dict) and len(interviewer_data) > 2:
                score += 0.15
        
        # Role research score
        if result.role_research and not result.role_research.get('error'): 
            score += 1.0
            # Bonus for detailed requirements
            role_data = result.role_research.get('data', {})
            if isinstance(role_data, dict) and len(role_data) > 2:
                score += 0.15
        
        return min(score / max_score, 1.0)  # Cap at 1.0
    
    def _calculate_confidence_score(self, result: ResearchResult) -> float:
        """Calculate confidence score based on research success and data quality"""
        if result.errors:
            base_confidence = 0.5  # Lower confidence if there were errors
        else:
            base_confidence = 0.8
        
        # Boost confidence based on successful research areas
        successful_areas = 0
        total_areas = 3
        
        if result.company_research and not result.company_research.get('error'):
            successful_areas += 1
        if result.interviewer_research and not result.interviewer_research.get('error'):
            successful_areas += 1  
        if result.role_research and not result.role_research.get('error'):
            successful_areas += 1
        
        coverage_boost = (successful_areas / total_areas) * 0.2
        return min(base_confidence + coverage_boost, 1.0)
    
    async def _update_interview_status(self, interview_id: str, status: str, research_result: ResearchResult):
        """Update interview status and store research results"""
        try:
            agent_input = AgentInput(data={
                'action': 'update_status',
                'interview_id': interview_id,
                'status': status,
                'research_data': {
                    'company': research_result.company_research,
                    'interviewer': research_result.interviewer_research,
                    'role': research_result.role_research,
                    'quality_score': research_result.quality_score,
                    'confidence_score': research_result.research_confidence,
                    'research_timestamp': datetime.now().isoformat()
                }
            })
            
            result = await self.interview_store.execute(agent_input)
            if result.success:
                print(f"✅ Updated interview {interview_id} status to '{status}'")
            else:
                print(f"⚠️ Failed to update interview {interview_id}: {result.errors}")
                
        except Exception as e:
            print(f"❌ Error updating interview status: {str(e)}")


# Convenience functions for integration
def create_research_pipeline(tavily_api_key: Optional[str] = None) -> ResearchEnginePipeline:
    """Factory function to create research pipeline"""
    return ResearchEnginePipeline(tavily_api_key=tavily_api_key)


async def run_research_for_unprepped_interviews(
    max_interviews: int = 10, 
    priority_filter: str = "all",
    tavily_api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Convenience function to run research pipeline
    
    Args:
        max_interviews: Maximum interviews to research
        priority_filter: Priority level filter (all, high, normal, low)  
        tavily_api_key: Tavily API key (optional, can use environment variable)
        
    Returns:
        Pipeline execution results
    """
    pipeline = create_research_pipeline(tavily_api_key)
    return await pipeline.run_research_pipeline(max_interviews, priority_filter)


if __name__ == "__main__":
    # Test the pipeline
    async def test_pipeline():
        result = await run_research_for_unprepped_interviews(max_interviews=5)
        print(f"Research Pipeline Result: {result}")
    
    asyncio.run(test_pipeline())
