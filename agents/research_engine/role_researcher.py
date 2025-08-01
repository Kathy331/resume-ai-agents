"""
Role & Job Market Researcher

This module provides comprehensive job market analysis and role research
to help with interview preparation and career planning.

Features:
- Job market analysis for specific roles
- Salary and compensation research
- Required skills and qualifications analysis
- Industry trends and growth projections
- Company-specific role insights
- Career progression pathways
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .tavily_client import EnhancedTavilyClient, TavilyResponse

@dataclass
class SalaryInfo:
    """Salary and compensation information"""
    base_salary_range: str = ""
    total_compensation: str = ""
    location_factor: str = ""
    experience_level: str = ""
    source: str = ""

@dataclass
class SkillRequirements:
    """Skill requirements for a role"""
    required_skills: List[str] = None
    preferred_skills: List[str] = None
    programming_languages: List[str] = None
    tools_technologies: List[str] = None
    soft_skills: List[str] = None
    
    def __post_init__(self):
        if self.required_skills is None:
            self.required_skills = []
        if self.preferred_skills is None:
            self.preferred_skills = []
        if self.programming_languages is None:
            self.programming_languages = []
        if self.tools_technologies is None:
            self.tools_technologies = []
        if self.soft_skills is None:
            self.soft_skills = []

@dataclass
class MarketTrends:
    """Job market trends and insights"""
    demand_level: str = ""  # High, Medium, Low
    growth_projection: str = ""
    emerging_skills: List[str] = None
    industry_insights: List[str] = None
    
    def __post_init__(self):
        if self.emerging_skills is None:
            self.emerging_skills = []
        if self.industry_insights is None:
            self.industry_insights = []

@dataclass
class RoleResearchResult:
    """Complete role research results"""
    role_title: str
    role_description: str = ""
    salary_info: SalaryInfo = None
    skill_requirements: SkillRequirements = None
    market_trends: MarketTrends = None
    career_progression: List[str] = None
    company_specific_insights: Dict[str, str] = None
    search_metadata: Dict[str, Any] = None
    research_timestamp: datetime = None
    
    def __post_init__(self):
        if self.salary_info is None:
            self.salary_info = SalaryInfo()
        if self.skill_requirements is None:
            self.skill_requirements = SkillRequirements()
        if self.market_trends is None:
            self.market_trends = MarketTrends()
        if self.career_progression is None:
            self.career_progression = []
        if self.company_specific_insights is None:
            self.company_specific_insights = {}
        if self.search_metadata is None:
            self.search_metadata = {}
        if self.research_timestamp is None:
            self.research_timestamp = datetime.now()

class RoleResearcher:
    """
    Intelligent job role and market research
    """
    
    def __init__(self, tavily_client: Optional[EnhancedTavilyClient] = None):
        self.tavily_client = tavily_client or EnhancedTavilyClient()
        
        # Predefined skill mappings for common roles
        self.role_skill_mapping = {
            'software engineer': ['Python', 'Java', 'JavaScript', 'Git', 'SQL', 'Algorithms', 'System Design'],
            'data scientist': ['Python', 'R', 'SQL', 'Machine Learning', 'Statistics', 'Pandas', 'Scikit-learn'],
            'product manager': ['Strategy', 'Analytics', 'User Research', 'Roadmapping', 'Stakeholder Management'],
            'frontend developer': ['JavaScript', 'React', 'Vue.js', 'HTML', 'CSS', 'TypeScript', 'Responsive Design'],
            'backend developer': ['Python', 'Java', 'Node.js', 'Databases', 'APIs', 'Cloud Services', 'Docker'],
            'devops engineer': ['AWS', 'Docker', 'Kubernetes', 'CI/CD', 'Infrastructure as Code', 'Monitoring'],
            'ux designer': ['Figma', 'Adobe Creative Suite', 'User Research', 'Prototyping', 'Wireframing'],
            'marketing manager': ['Digital Marketing', 'Analytics', 'Content Strategy', 'SEO', 'Social Media']
        }
    
    def research_role(
        self, 
        role_title: str, 
        company: str = "", 
        location: str = "", 
        experience_level: str = ""
    ) -> RoleResearchResult:
        """
        Research comprehensive information about a job role
        
        Args:
            role_title: The job title to research
            company: Optional company context
            location: Optional location context
            experience_level: Optional experience level (entry, mid, senior)
            
        Returns:
            RoleResearchResult with comprehensive role information
        """
        print(f"🔍 Researching role: {role_title} at {company}")
        
        # Primary role market search
        primary_response = self.tavily_client.search_role_market(
            role_title=role_title,
            company=company,
            location=location,
            search_depth="advanced",
            max_results=6
        )
        
        # Extract role information
        role_description = self._extract_role_description(role_title, primary_response)
        salary_info = self._extract_salary_info(primary_response, location, experience_level)
        skill_requirements = self._extract_skill_requirements(role_title, primary_response)
        market_trends = self._extract_market_trends(role_title, primary_response)
        career_progression = self._extract_career_progression(role_title, primary_response)
        
        # Company-specific insights if company provided
        company_insights = {}
        if company:
            company_response = self.tavily_client.search_general(
                f"{role_title} at {company} interview process culture team",
                search_depth="basic",
                max_results=3
            )
            company_insights = self._extract_company_insights(company, company_response)
        
        return RoleResearchResult(
            role_title=role_title,
            role_description=role_description,
            salary_info=salary_info,
            skill_requirements=skill_requirements,
            market_trends=market_trends,
            career_progression=career_progression,
            company_specific_insights=company_insights,
            search_metadata={
                "search_queries": [primary_response.query],
                "total_results": len(primary_response.results),
                "company_provided": bool(company),
                "location_provided": bool(location),
                "response_time": primary_response.response_time
            },
            research_timestamp=datetime.now()
        )
    
    def compare_roles(self, role_titles: List[str], company: str = "") -> Dict[str, RoleResearchResult]:
        """
        Compare multiple roles side by side
        
        Args:
            role_titles: List of role titles to compare
            company: Optional company context
            
        Returns:
            Dictionary mapping role titles to research results
        """
        results = {}
        
        for role in role_titles:
            if role.strip():
                results[role] = self.research_role(role, company)
        
        return results
    
    def _extract_role_description(self, role_title: str, response: TavilyResponse) -> str:
        """Extract role description from search results"""
        # Look for job description patterns
        all_content = " ".join([result.content for result in response.results])
        
        # Find sentences that describe what the role does
        description_patterns = [
            rf"{re.escape(role_title)}.*?(?:responsible for|duties include|will|involve)[^.]*\.",
            rf"(?:role|position|job).*?{re.escape(role_title)}.*?[^.]*\.",
            r"responsibilities.*?include[^.]*\.",
            r"(?:The|A)\s+[^.]*?(?:is responsible|will be|duties)[^.]*\."
        ]
        
        for pattern in description_patterns:
            matches = re.search(pattern, all_content, re.IGNORECASE | re.DOTALL)
            if matches:
                description = matches.group(0).strip()
                if len(description) > 50:
                    return description[:300] + "..." if len(description) > 300 else description
        
        # Fallback: use first substantial paragraph
        paragraphs = all_content.split('\n')
        for paragraph in paragraphs:
            if len(paragraph.strip()) > 100 and role_title.lower() in paragraph.lower():
                return paragraph.strip()[:300] + "..." if len(paragraph) > 300 else paragraph.strip()
        
        return f"Research for {role_title} role"
    
    def _extract_salary_info(self, response: TavilyResponse, location: str, experience_level: str) -> SalaryInfo:
        """Extract salary and compensation information"""
        salary_info = SalaryInfo()
        
        all_content = " ".join([result.content for result in response.results])
        
        # Extract salary ranges
        salary_patterns = [
            r"\$([0-9]{2,3}(?:,\d{3})*)\s*[-–—]\s*\$([0-9]{2,3}(?:,\d{3})*)",
            r"\$([0-9]{2,3}(?:,\d{3})*)\s*(?:to|and)\s*\$([0-9]{2,3}(?:,\d{3})*)",
            r"salary.*?\$([0-9]{2,3}(?:,\d{3})*)",
            r"compensation.*?\$([0-9]{2,3}(?:,\d{3})*)"
        ]
        
        for pattern in salary_patterns:
            matches = re.search(pattern, all_content, re.IGNORECASE)
            if matches:
                if len(matches.groups()) >= 2:
                    salary_info.base_salary_range = f"${matches.group(1)} - ${matches.group(2)}"
                else:
                    salary_info.base_salary_range = f"${matches.group(1)}"
                break
        
        # Extract total compensation mentions
        comp_patterns = [
            r"total compensation.*?\$([0-9]{2,3}(?:,\d{3})*)",
            r"package.*?\$([0-9]{2,3}(?:,\d{3})*)",
            r"(?:TC|total comp).*?\$([0-9]{2,3}(?:,\d{3})*)"
        ]
        
        for pattern in comp_patterns:
            matches = re.search(pattern, all_content, re.IGNORECASE)
            if matches:
                salary_info.total_compensation = f"${matches.group(1)}"
                break
        
        # Set context information
        salary_info.location_factor = location if location else ""
        salary_info.experience_level = experience_level if experience_level else ""
        
        # Extract source information
        if response.results:
            best_result = max(response.results, key=lambda r: r.score)
            salary_info.source = self._extract_source_name(best_result.url)
        
        return salary_info
    
    def _extract_skill_requirements(self, role_title: str, response: TavilyResponse) -> SkillRequirements:
        """Extract skill requirements from search results"""
        skills = SkillRequirements()
        
        all_content = " ".join([result.content for result in response.results])
        
        # Use predefined skill mapping if available
        role_key = role_title.lower()
        for key, predefined_skills in self.role_skill_mapping.items():
            if key in role_key:
                skills.required_skills.extend(predefined_skills[:5])
                break
        
        # Extract skills from content
        skill_patterns = [
            r"(?:required|must have|needs?).*?skills?[:\-]?\s*([^.]{20,100})",
            r"(?:experience with|proficient in|knowledge of)[:\-]?\s*([^.]{10,80})",
            r"(?:technologies?|tools?)[:\-]?\s*([^.]{10,80})"
        ]
        
        programming_languages = ['Python', 'Java', 'JavaScript', 'TypeScript', 'C++', 'C#', 'Go', 'Rust', 'Swift', 'Kotlin', 'PHP', 'Ruby', 'R', 'SQL', 'HTML', 'CSS']
        tools_tech = ['Docker', 'Kubernetes', 'AWS', 'Azure', 'GCP', 'Git', 'Jenkins', 'React', 'Vue', 'Angular', 'Node.js', 'Django', 'Flask', 'Spring', 'Redis', 'MongoDB', 'PostgreSQL']
        soft_skills = ['Leadership', 'Communication', 'Teamwork', 'Problem Solving', 'Critical Thinking', 'Adaptability', 'Project Management']
        
        content_lower = all_content.lower()
        
        # Extract programming languages
        for lang in programming_languages:
            if lang.lower() in content_lower and lang not in skills.programming_languages:
                skills.programming_languages.append(lang)
        
        # Extract tools and technologies
        for tool in tools_tech:
            if tool.lower() in content_lower and tool not in skills.tools_technologies:
                skills.tools_technologies.append(tool)
        
        # Extract soft skills
        for soft_skill in soft_skills:
            if soft_skill.lower() in content_lower and soft_skill not in skills.soft_skills:
                skills.soft_skills.append(soft_skill)
        
        # Extract skills from patterns
        for pattern in skill_patterns:
            matches = re.finditer(pattern, all_content, re.IGNORECASE)
            for match in matches:
                skill_text = match.group(1).strip()
                # Simple skill extraction from comma-separated lists
                potential_skills = [s.strip() for s in skill_text.split(',')]
                for skill in potential_skills[:3]:  # Limit extraction
                    if len(skill) > 2 and len(skill) < 30:
                        if skill not in skills.preferred_skills:
                            skills.preferred_skills.append(skill)
        
        # Limit all lists
        skills.required_skills = skills.required_skills[:8]
        skills.preferred_skills = skills.preferred_skills[:6]
        skills.programming_languages = skills.programming_languages[:6]
        skills.tools_technologies = skills.tools_technologies[:8]
        skills.soft_skills = skills.soft_skills[:5]
        
        return skills
    
    def _extract_market_trends(self, role_title: str, response: TavilyResponse) -> MarketTrends:
        """Extract market trends and insights"""
        trends = MarketTrends()
        
        all_content = " ".join([result.content for result in response.results])
        
        # Determine demand level
        demand_indicators = {
            'high': ['high demand', 'growing field', 'in-demand', 'hot job', 'shortage', 'competitive market'],
            'medium': ['steady demand', 'stable market', 'moderate growth'],
            'low': ['declining', 'oversaturated', 'limited opportunities']
        }
        
        content_lower = all_content.lower()
        for level, indicators in demand_indicators.items():
            if any(indicator in content_lower for indicator in indicators):
                trends.demand_level = level.title()
                break
        
        # Extract growth projections
        growth_patterns = [
            r"(?:growth|projected|expected).*?(\d+%)",
            r"(\d+%)\s*(?:growth|increase|rise)",
            r"(?:growing|expanding).*?(\d+.*?years?)"
        ]
        
        for pattern in growth_patterns:
            matches = re.search(pattern, all_content, re.IGNORECASE)
            if matches:
                trends.growth_projection = matches.group(1)
                break
        
        # Extract emerging skills
        emerging_patterns = [
            r"(?:emerging|trending|new)\s+(?:skills?|technologies?)[:\-]?\s*([^.]{10,100})",
            r"(?:future|next|upcoming)\s+(?:skills?|technologies?)[:\-]?\s*([^.]{10,100})"
        ]
        
        for pattern in emerging_patterns:
            matches = re.finditer(pattern, all_content, re.IGNORECASE)
            for match in matches:
                skill_text = match.group(1).strip()
                skills = [s.strip() for s in skill_text.split(',')]
                trends.emerging_skills.extend([s for s in skills[:3] if len(s) > 2])
        
        # Extract industry insights
        insight_patterns = [
            r"(?:trend|industry|market).*?(?:shows?|indicates?|suggests?)[^.]*\.",
            r"(?:according to|research shows?|studies? indicate)[^.]*\.",
            r"(?:experts? (?:say|believe|predict))[^.]*\."
        ]
        
        for pattern in insight_patterns:
            matches = re.finditer(pattern, all_content, re.IGNORECASE)
            for match in matches:
                insight = match.group(0).strip()
                if len(insight) > 30 and insight not in trends.industry_insights:
                    trends.industry_insights.append(insight[:150] + "..." if len(insight) > 150 else insight)
                    if len(trends.industry_insights) >= 3:
                        break
        
        return trends
    
    def _extract_career_progression(self, role_title: str, response: TavilyResponse) -> List[str]:
        """Extract career progression pathways"""
        progression = []
        
        all_content = " ".join([result.content for result in response.results])
        
        # Common progression patterns
        progression_patterns = [
            r"(?:can progress to|advance to|move to|become)[^.]*\.",
            r"(?:career path|progression|advancement)[^.]*\.",
            r"(?:next role|senior|lead|principal|director)[^.]*\."
        ]
        
        for pattern in progression_patterns:
            matches = re.finditer(pattern, all_content, re.IGNORECASE)
            for match in matches:
                path = match.group(0).strip()
                if len(path) > 20 and path not in progression:
                    progression.append(path[:100] + "..." if len(path) > 100 else path)
                    if len(progression) >= 4:
                        break
        
        # Add common role progressions based on role type
        role_lower = role_title.lower()
        if 'engineer' in role_lower or 'developer' in role_lower:
            progression.append("Senior Engineer → Staff Engineer → Principal Engineer → Engineering Manager")
        elif 'manager' in role_lower:
            progression.append("Manager → Senior Manager → Director → VP")
        elif 'analyst' in role_lower:
            progression.append("Analyst → Senior Analyst → Manager → Director")
        
        return progression[:4]
    
    def _extract_company_insights(self, company: str, response: TavilyResponse) -> Dict[str, str]:
        """Extract company-specific role insights"""
        insights = {}
        
        all_content = " ".join([result.content for result in response.results])
        
        # Interview process insights
        interview_patterns = [
            r"(?:interview process|interview|hiring)[^.]*\.",
            r"(?:technical interview|coding interview|system design)[^.]*\.",
            r"(?:onsite|phone screen|behavioral)[^.]*\."
        ]
        
        for pattern in interview_patterns:
            matches = re.search(pattern, all_content, re.IGNORECASE)
            if matches:
                insights['interview_process'] = matches.group(0).strip()
                break
        
        # Culture insights
        culture_patterns = [
            r"(?:culture|environment|team|work-life)[^.]*\.",
            r"(?:values|mission|vision)[^.]*\."
        ]
        
        for pattern in culture_patterns:
            matches = re.search(pattern, all_content, re.IGNORECASE)
            if matches:
                insights['culture'] = matches.group(0).strip()
                break
        
        return insights
    
    def _extract_source_name(self, url: str) -> str:
        """Extract source name from URL"""
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            domain = parsed.netloc.replace('www.', '')
            return domain.split('.')[0].title()
        except:
            return "Unknown"
    
    def format_role_summary(self, research: RoleResearchResult) -> str:
        """Format role research into readable summary"""
        summary = []
        
        # Header
        summary.append(f"## {research.role_title}")
        if research.role_description:
            summary.append(f"\n**Role Description:**\n{research.role_description}")
        
        # Salary information
        if research.salary_info.base_salary_range:
            summary.append(f"\n**Compensation:**")
            summary.append(f"• Base Salary: {research.salary_info.base_salary_range}")
            if research.salary_info.total_compensation:
                summary.append(f"• Total Compensation: {research.salary_info.total_compensation}")
        
        # Skills
        skills = research.skill_requirements
        if skills.required_skills or skills.programming_languages:
            summary.append(f"\n**Required Skills:**")
            if skills.required_skills:
                summary.append(f"• Core: {', '.join(skills.required_skills)}")
            if skills.programming_languages:
                summary.append(f"• Programming: {', '.join(skills.programming_languages)}")
            if skills.tools_technologies:
                summary.append(f"• Tools: {', '.join(skills.tools_technologies)}")
        
        # Market trends
        if research.market_trends.demand_level:
            summary.append(f"\n**Market Analysis:**")
            summary.append(f"• Demand Level: {research.market_trends.demand_level}")
            if research.market_trends.growth_projection:
                summary.append(f"• Growth: {research.market_trends.growth_projection}")
        
        # Career progression
        if research.career_progression:
            summary.append(f"\n**Career Progression:**")
            for path in research.career_progression:
                summary.append(f"• {path}")
        
        # Company insights
        if research.company_specific_insights:
            summary.append(f"\n**Company-Specific Insights:**")
            for key, value in research.company_specific_insights.items():
                summary.append(f"• {key.replace('_', ' ').title()}: {value}")
        
        return "\n".join(summary)

# Create global instance for easy importing
role_researcher = RoleResearcher()
