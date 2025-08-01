"""
Research Orchestrator

This module coordinates all research activities across different research engines.
It provides a unified interface for conducting comprehensive interview preparation
research, combining company, interviewer, and role research.

Features:
- Unified research coordination
- Intelligent research prioritization
- Cross-research correlation and insights
- Comprehensive interview prep package generation
- Research result aggregation and formatting
- Cached research management
"""

import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import json

from .tavily_client import EnhancedTavilyClient
from .company_researcher import CompanyResearcher, CompanyResearchResult
from .interviewer_researcher import InterviewerResearcher, InterviewerResearchResult
from .role_researcher import RoleResearcher, RoleResearchResult

@dataclass
class ResearchRequest:
    """Research request specification"""
    company_name: str = ""
    role_title: str = ""
    interviewer_names: List[str] = None
    additional_context: Dict[str, str] = None
    research_depth: str = "standard"  # basic, standard, comprehensive
    
    def __post_init__(self):
        if self.interviewer_names is None:
            self.interviewer_names = []
        if self.additional_context is None:
            self.additional_context = {}

@dataclass
class ComprehensiveResearchResult:
    """Complete research results package"""
    request: ResearchRequest
    company_research: Optional[CompanyResearchResult] = None
    role_research: Optional[RoleResearchResult] = None
    interviewer_research: List[InterviewerResearchResult] = None
    cross_insights: List[str] = None
    research_summary: str = ""
    confidence_score: float = 0.0
    research_timestamp: datetime = None
    
    def __post_init__(self):
        if self.interviewer_research is None:
            self.interviewer_research = []
        if self.cross_insights is None:
            self.cross_insights = []
        if self.research_timestamp is None:
            self.research_timestamp = datetime.now()

class ResearchOrchestrator:
    """
    Coordinates comprehensive interview preparation research
    """
    
    def __init__(self, tavily_client: Optional[EnhancedTavilyClient] = None):
        self.tavily_client = tavily_client or EnhancedTavilyClient()
        
        # Initialize research engines
        self.company_researcher = CompanyResearcher(self.tavily_client)
        self.interviewer_researcher = InterviewerResearcher(self.tavily_client)
        self.role_researcher = RoleResearcher(self.tavily_client)
        
        # Research prioritization
        self.research_priorities = {
            'basic': ['company'],
            'standard': ['company', 'role'],
            'comprehensive': ['company', 'role', 'interviewer']
        }
    
    def conduct_comprehensive_research(self, request: ResearchRequest) -> ComprehensiveResearchResult:
        """
        Conduct comprehensive research based on request
        
        Args:
            request: ResearchRequest with research specifications
            
        Returns:
            ComprehensiveResearchResult with all research findings
        """
        print(f"🎯 Starting comprehensive research for {request.company_name} - {request.role_title}")
        
        result = ComprehensiveResearchResult(request=request)
        
        # Determine research scope
        research_types = self.research_priorities.get(request.research_depth, ['company'])
        
        # Conduct company research
        if 'company' in research_types and request.company_name:
            print(f"📊 Researching company: {request.company_name}")
            deep_search = request.research_depth in ['standard', 'comprehensive']
            result.company_research = self.company_researcher.research_company(
                request.company_name, 
                deep_search=deep_search
            )
        
        # Conduct role research
        if 'role' in research_types and request.role_title:
            print(f"💼 Researching role: {request.role_title}")
            location = request.additional_context.get('location', '')
            experience_level = request.additional_context.get('experience_level', '')
            result.role_research = self.role_researcher.research_role(
                request.role_title,
                company=request.company_name,
                location=location,
                experience_level=experience_level
            )
        
        # Conduct interviewer research
        if 'interviewer' in research_types and request.interviewer_names:
            print(f"👥 Researching interviewers: {', '.join(request.interviewer_names)}")
            for name in request.interviewer_names:
                if name.strip():
                    interviewer_result = self.interviewer_researcher.research_interviewer(
                        name=name,
                        company=request.company_name,
                        additional_context=request.additional_context.get('university', '')
                    )
                    result.interviewer_research.append(interviewer_result)
        
        # Generate cross-insights
        result.cross_insights = self._generate_cross_insights(result)
        
        # Calculate confidence score
        result.confidence_score = self._calculate_overall_confidence(result)
        
        # Generate research summary
        result.research_summary = self._generate_research_summary(result)
        
        print(f"✅ Research complete! Confidence: {result.confidence_score:.1%}")
        return result
    
    def quick_company_research(self, company_name: str) -> CompanyResearchResult:
        """Quick company research for immediate needs"""
        return self.company_researcher.research_company(company_name, deep_search=False)
    
    def quick_role_research(self, role_title: str, company: str = "") -> RoleResearchResult:
        """Quick role research for immediate needs"""
        return self.role_researcher.research_role(role_title, company)
    
    def batch_interviewer_research(self, names: List[str], company: str = "") -> List[InterviewerResearchResult]:
        """Batch interviewer research"""
        results = []
        for name in names:
            if name.strip():
                result = self.interviewer_researcher.research_interviewer(name, company)
                results.append(result)
        return results
    
    def research_from_email_entities(self, entities: Dict[str, List[str]]) -> ComprehensiveResearchResult:
        """
        Conduct research based on extracted email entities
        
        Args:
            entities: Dictionary with extracted entities (COMPANY, ROLE, INTERVIEWER, etc.)
            
        Returns:
            ComprehensiveResearchResult based on entity extraction
        """
        # Build research request from entities
        request = ResearchRequest(
            company_name=entities.get('COMPANY', [''])[0] if entities.get('COMPANY') else '',
            role_title=entities.get('ROLE', [''])[0] if entities.get('ROLE') else '',
            interviewer_names=entities.get('INTERVIEWER', []),
            research_depth='standard'
        )
        
        # Add additional context from entities
        if entities.get('LOCATION'):
            request.additional_context['location'] = entities['LOCATION'][0]
        if entities.get('DATE'):
            request.additional_context['interview_date'] = entities['DATE'][0]
        
        return self.conduct_comprehensive_research(request)
    
    def _generate_cross_insights(self, result: ComprehensiveResearchResult) -> List[str]:
        """Generate insights by correlating different research results"""
        insights = []
        
        # Company-Role correlations
        if result.company_research and result.role_research:
            company = result.company_research.company_info
            role = result.role_research
            
            # Industry alignment
            if company.industry and role.role_title:
                insights.append(f"Role alignment: {role.role_title} in {company.industry} industry")
            
            # Company size vs role expectations
            if company.size and role.skill_requirements.required_skills:
                insights.append(f"Company scale: {company.size} suggests focus on {', '.join(role.skill_requirements.required_skills[:3])}")
        
        # Company-Interviewer correlations
        if result.company_research and result.interviewer_research:
            company = result.company_research.company_info
            for interviewer in result.interviewer_research:
                if interviewer.company_connection:
                    insights.append(f"Interviewer connection: {interviewer.profile.name} - {interviewer.company_connection}")
        
        # Role-Interviewer correlations
        if result.role_research and result.interviewer_research:
            role_skills = result.role_research.skill_requirements.required_skills
            for interviewer in result.interviewer_research:
                common_skills = set(role_skills) & set(interviewer.profile.skills)
                if common_skills:
                    insights.append(f"Skill overlap with {interviewer.profile.name}: {', '.join(list(common_skills)[:3])}")
        
        # Market trends insights
        if result.role_research and result.role_research.market_trends.demand_level:
            demand = result.role_research.market_trends.demand_level
            insights.append(f"Market context: {demand} demand for {result.role_research.role_title}")
        
        return insights[:5]  # Limit to top 5 insights
    
    def _calculate_overall_confidence(self, result: ComprehensiveResearchResult) -> float:
        """Calculate overall confidence score for research results"""
        confidence = 0.0
        weights = {'company': 0.4, 'role': 0.3, 'interviewer': 0.3}
        
        # Company research confidence
        if result.company_research:
            company_conf = 0.8  # Base confidence for successful company research
            if result.company_research.company_info.website:
                company_conf += 0.1
            if result.company_research.recent_news:
                company_conf += 0.1
            confidence += min(1.0, company_conf) * weights['company']
        
        # Role research confidence
        if result.role_research:
            role_conf = 0.7  # Base confidence for role research
            if result.role_research.salary_info.base_salary_range:
                role_conf += 0.15
            if result.role_research.skill_requirements.required_skills:
                role_conf += 0.15
            confidence += min(1.0, role_conf) * weights['role']
        
        # Interviewer research confidence
        if result.interviewer_research:
            interviewer_conf = sum(r.research_confidence for r in result.interviewer_research) / len(result.interviewer_research)
            confidence += interviewer_conf * weights['interviewer']
        
        return min(1.0, confidence)
    
    def _generate_research_summary(self, result: ComprehensiveResearchResult) -> str:
        """Generate comprehensive research summary"""
        summary_parts = []
        
        # Header
        summary_parts.append(f"# Interview Research Summary")
        summary_parts.append(f"**Company:** {result.request.company_name}")
        summary_parts.append(f"**Role:** {result.request.role_title}")
        summary_parts.append(f"**Research Date:** {result.research_timestamp.strftime('%Y-%m-%d %H:%M')}")
        summary_parts.append(f"**Confidence Score:** {result.confidence_score:.1%}")
        
        # Company section
        if result.company_research:
            summary_parts.append(f"\n## Company Overview")
            company = result.company_research
            
            if company.company_info.description:
                summary_parts.append(f"**About:** {company.company_info.description}")
            
            if company.company_info.industry:
                summary_parts.append(f"**Industry:** {company.company_info.industry}")
            
            if company.key_insights:
                summary_parts.append(f"**Key Insights:**")
                for insight in company.key_insights[:3]:
                    summary_parts.append(f"• {insight}")
            
            if company.recent_news:
                summary_parts.append(f"**Recent News:**")
                for news in company.recent_news[:2]:
                    summary_parts.append(f"• {news.title}")
        
        # Role section
        if result.role_research:
            summary_parts.append(f"\n## Role Analysis")
            role = result.role_research
            
            if role.salary_info.base_salary_range:
                summary_parts.append(f"**Salary Range:** {role.salary_info.base_salary_range}")
            
            if role.skill_requirements.required_skills:
                summary_parts.append(f"**Key Skills:** {', '.join(role.skill_requirements.required_skills[:5])}")
            
            if role.market_trends.demand_level:
                summary_parts.append(f"**Market Demand:** {role.market_trends.demand_level}")
        
        # Interviewer section
        if result.interviewer_research:
            summary_parts.append(f"\n## Interviewer Profiles")
            for interviewer in result.interviewer_research:
                profile = interviewer.profile
                summary_parts.append(f"**{profile.name}**")
                if profile.current_title and profile.current_company:
                    summary_parts.append(f"• {profile.current_title} at {profile.current_company}")
                if profile.education:
                    summary_parts.append(f"• Education: {', '.join(profile.education[:2])}")
        
        # Cross insights
        if result.cross_insights:
            summary_parts.append(f"\n## Key Insights")
            for insight in result.cross_insights:
                summary_parts.append(f"• {insight}")
        
        return "\n".join(summary_parts)
    
    def export_research_json(self, result: ComprehensiveResearchResult) -> str:
        """Export research results as JSON"""
        # Convert dataclasses to dictionaries for JSON serialization
        export_data = {
            'request': asdict(result.request),
            'company_research': asdict(result.company_research) if result.company_research else None,
            'role_research': asdict(result.role_research) if result.role_research else None,
            'interviewer_research': [asdict(r) for r in result.interviewer_research],
            'cross_insights': result.cross_insights,
            'research_summary': result.research_summary,
            'confidence_score': result.confidence_score,
            'research_timestamp': result.research_timestamp.isoformat()
        }
        
        return json.dumps(export_data, indent=2, default=str)
    
    def get_research_stats(self) -> Dict[str, Any]:
        """Get research engine statistics"""
        stats = {
            'tavily_cache': self.tavily_client.get_cache_stats(),
            'engines_initialized': {
                'company_researcher': bool(self.company_researcher),
                'interviewer_researcher': bool(self.interviewer_researcher),
                'role_researcher': bool(self.role_researcher)
            },
            'research_priorities': self.research_priorities
        }
        
        return stats

# Create global instance for easy importing
research_orchestrator = ResearchOrchestrator()
