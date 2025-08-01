"""
Interviewer & Professional Background Researcher

This module specializes in researching interviewers and professional contacts
using LinkedIn and other professional platforms. It helps gather context
about the people you'll be interviewing with.

Features:
- LinkedIn profile discovery and analysis (tavily chrome search)
- Professional background extraction
- Company connection analysis
- Educational background research
- Mutual connection discovery
- Professional achievement extraction
"""

import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

from .tavily_client import EnhancedTavilyClient, TavilyResponse

@dataclass
class ProfessionalProfile:
    """Professional profile information"""
    name: str
    current_title: str = ""
    current_company: str = ""
    linkedin_url: str = ""
    location: str = ""
    education: List[str] = None
    previous_roles: List[str] = None
    skills: List[str] = None
    achievements: List[str] = None
    
    def __post_init__(self):
        if self.education is None:
            self.education = []
        if self.previous_roles is None:
            self.previous_roles = []
        if self.skills is None:
            self.skills = []
        if self.achievements is None:
            self.achievements = []

@dataclass
class InterviewerResearchResult:
    """Complete interviewer research results"""
    profile: ProfessionalProfile
    company_connection: str = ""  # How they relate to the target company
    potential_topics: List[str] = None  # Conversation topics based on background
    research_confidence: float = 0.0  # Confidence in profile match
    search_metadata: Dict[str, Any] = None
    research_timestamp: datetime = None
    
    def __post_init__(self):
        if self.potential_topics is None:
            self.potential_topics = []
        if self.search_metadata is None:
            self.search_metadata = {}
        if self.research_timestamp is None:
            self.research_timestamp = datetime.now()

class InterviewerResearcher:
    """
    Intelligent interviewer and professional background research
    """
    
    def __init__(self, tavily_client: Optional[EnhancedTavilyClient] = None):
        self.tavily_client = tavily_client or EnhancedTavilyClient()
    
    def research_interviewer(
        self, 
        name: str, 
        company: str = "", 
        title: str = "", 
        additional_context: str = ""
    ) -> InterviewerResearchResult:
        """
        Research an interviewer's professional background
        
        Args:
            name: Full name of the interviewer
            company: Company they work for
            title: Their job title (if known)
            additional_context: Any additional context (university, etc.)
            
        Returns:
            InterviewerResearchResult with structured professional information
        """
        print(f"🔍 Researching interviewer: {name} at {company}")
        
        # Construct comprehensive search
        response = self.tavily_client.search_person_linkedin(
            person_name=name,
            company=company,
            university=additional_context,
            search_depth="advanced",
            max_results=5
        )
        
        # Extract professional profile
        profile = self._extract_professional_profile(name, response)
        
        # Analyze company connection
        company_connection = self._analyze_company_connection(profile, company, response)
        
        # Generate conversation topics
        potential_topics = self._generate_conversation_topics(profile, company)
        
        # Calculate research confidence
        confidence = self._calculate_confidence(profile, response, company)
        
        return InterviewerResearchResult(
            profile=profile,
            company_connection=company_connection,
            potential_topics=potential_topics,
            research_confidence=confidence,
            search_metadata={
                "search_query": response.query,
                "total_results": len(response.results),
                "linkedin_urls_found": len(self.tavily_client.extract_linkedin_urls(response)),
                "response_time": response.response_time
            },
            research_timestamp=datetime.now()
        )
    
    def research_multiple_interviewers(
        self, 
        interviewers: List[Dict[str, str]], 
        company: str = ""
    ) -> List[InterviewerResearchResult]:
        """
        Research multiple interviewers in batch
        
        Args:
            interviewers: List of dicts with 'name', 'title', etc.
            company: Company context
            
        Returns:
            List of InterviewerResearchResult objects
        """
        results = []
        
        for interviewer in interviewers:
            name = interviewer.get('name', '')
            title = interviewer.get('title', '')
            context = interviewer.get('context', '')
            
            if name:
                result = self.research_interviewer(name, company, title, context)
                results.append(result)
        
        return results
    
    def _extract_professional_profile(self, name: str, response: TavilyResponse) -> ProfessionalProfile:
        """Extract professional profile from search results"""
        profile = ProfessionalProfile(name=name)
        
        # Find the best LinkedIn result
        linkedin_result = self._find_best_linkedin_result(response)
        if linkedin_result:
            profile.linkedin_url = linkedin_result.url
            content = linkedin_result.content
            
            # Extract current position
            profile.current_title = self._extract_current_title(content, name)
            profile.current_company = self._extract_current_company(content)
            profile.location = self._extract_location(content)
            
            # Extract education
            profile.education = self._extract_education(content)
            
            # Extract previous roles
            profile.previous_roles = self._extract_previous_roles(content)
            
            # Extract skills
            profile.skills = self._extract_skills(content)
            
            # Extract achievements
            profile.achievements = self._extract_achievements(content)
        
        # If no LinkedIn result, use general results
        if not linkedin_result and response.results:
            best_result = max(response.results, key=lambda r: r.score)
            content = best_result.content
            
            profile.current_title = self._extract_current_title(content, name)
            profile.current_company = self._extract_current_company(content)
        
        return profile
    
    def _find_best_linkedin_result(self, response: TavilyResponse) -> Optional[Any]:
        """Find the most relevant LinkedIn profile result"""
        linkedin_results = [r for r in response.results if 'linkedin.com/in/' in r.url]
        
        if not linkedin_results:
            return None
        
        # Return highest scoring LinkedIn result
        return max(linkedin_results, key=lambda r: r.score)
    
    def _extract_current_title(self, content: str, name: str) -> str:
        """Extract current job title"""
        # Look for title patterns near the person's name
        name_variations = [name, name.split()[0], name.split()[-1]]
        
        title_patterns = [
            rf"{re.escape(name)}\s*[-–—]\s*([^|•\n]+?)(?:\s*@|\s*at|\s*\||\n)",
            rf"([^|•\n]+?)\s*@\s*[^|•\n]+",
            rf"([^|•\n]+?)\s*at\s*[^|•\n]+",
            r"(CEO|CTO|VP|Director|Manager|Engineer|Developer|Analyst|Consultant|Senior|Lead|Principal)[^|•\n]*"
        ]
        
        for pattern in title_patterns:
            matches = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
            if matches:
                title = matches.group(1).strip()
                if len(title) > 5 and len(title) < 100:  # Reasonable title length
                    return title
        
        return ""
    
    def _extract_current_company(self, content: str) -> str:
        """Extract current company"""
        company_patterns = [
            r"@\s*([^|•\n]+?)(?:\s*\||\n|$)",
            r"at\s*([^|•\n]+?)(?:\s*\||\n|$)",
            r"currently\s*(?:at|with)\s*([^|•\n]+?)(?:\s*\||\n|$)"
        ]
        
        for pattern in company_patterns:
            matches = re.search(pattern, content, re.IGNORECASE)
            if matches:
                company = matches.group(1).strip()
                if len(company) > 2 and len(company) < 50:
                    return company
        
        return ""
    
    def _extract_location(self, content: str) -> str:
        """Extract location information"""
        location_patterns = [
            r"([A-Z][a-z]+,\s*[A-Z][a-z]+,\s*[A-Z]{2})",  # City, State, Country
            r"([A-Z][a-z]+,\s*[A-Z]{2})",  # City, State
            r"([A-Z][a-z]+\s*Area)",  # City Area
            r"([A-Z][a-z]+,\s*[A-Z][a-z]+)"  # City, Country
        ]
        
        for pattern in location_patterns:
            matches = re.search(pattern, content)
            if matches:
                return matches.group(1).strip()
        
        return ""
    
    def _extract_education(self, content: str) -> List[str]:
        """Extract educational background"""
        education = []
        
        # Look for university patterns
        edu_patterns = [
            r"(University of [^|•\n]+)",
            r"([A-Z][a-z]+\s+University)",
            r"([A-Z][a-z]+\s+College)",
            r"([A-Z]+)\s*(?:University|College)",
            r"(Stanford|Harvard|MIT|Berkeley|UCLA|USC|NYU|Columbia|Yale|Princeton)"
        ]
        
        content_lower = content.lower()
        for pattern in edu_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                edu = match.group(1).strip()
                if edu and edu not in education and len(edu) > 3:
                    education.append(edu)
        
        return education[:3]  # Limit to 3 entries
    
    def _extract_previous_roles(self, content: str) -> List[str]:
        """Extract previous job roles"""
        roles = []
        
        # Look for role transition patterns
        role_patterns = [
            r"Previously\s*([^|•\n]+)",
            r"Former\s*([^|•\n]+)",
            r"Ex-([^|•\n]+)"
        ]
        
        for pattern in role_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                role = match.group(1).strip()
                if role and len(role) > 5 and role not in roles:
                    roles.append(role)
        
        return roles[:3]  # Limit to 3 entries
    
    def _extract_skills(self, content: str) -> List[str]:
        """Extract professional skills"""
        skills = []
        
        # Common tech/business skills
        skill_keywords = [
            'Python', 'Java', 'JavaScript', 'React', 'Node.js', 'AWS', 'Docker', 
            'Kubernetes', 'Machine Learning', 'AI', 'Data Science', 'SQL',
            'Leadership', 'Management', 'Strategy', 'Marketing', 'Sales',
            'Product Management', 'Engineering', 'Design', 'Analytics'
        ]
        
        content_lower = content.lower()
        for skill in skill_keywords:
            if skill.lower() in content_lower:
                skills.append(skill)
        
        return skills[:8]  # Limit to 8 skills
    
    def _extract_achievements(self, content: str) -> List[str]:
        """Extract notable achievements"""
        achievements = []
        
        achievement_patterns = [
            r"(led\s+[^|•\n]+)",
            r"(built\s+[^|•\n]+)",
            r"(founded\s+[^|•\n]+)", 
            r"(awarded\s+[^|•\n]+)",
            r"(published\s+[^|•\n]+)",
            r"(speaker\s+[^|•\n]+)"
        ]
        
        for pattern in achievement_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                achievement = match.group(1).strip()
                if achievement and len(achievement) > 10 and achievement not in achievements:
                    achievements.append(achievement[:100])  # Truncate long achievements
        
        return achievements[:3]  # Limit to 3 achievements
    
    def _analyze_company_connection(self, profile: ProfessionalProfile, target_company: str, response: TavilyResponse) -> str:
        """Analyze how the person connects to the target company"""
        if not target_company:
            return ""
        
        target_lower = target_company.lower()
        
        # Direct company match
        if profile.current_company and target_lower in profile.current_company.lower():
            return f"Current employee at {profile.current_company}"
        
        # Check previous roles
        for role in profile.previous_roles:
            if target_lower in role.lower():
                return f"Previously worked at {target_company}"
        
        # Check all content for company mentions
        all_content = " ".join([r.content for r in response.results])
        if target_lower in all_content.lower():
            return f"Has connection to {target_company}"
        
        return "No direct company connection found"
    
    def _generate_conversation_topics(self, profile: ProfessionalProfile, company: str) -> List[str]:
        """Generate potential conversation topics based on profile"""
        topics = []
        
        # Education-based topics
        for edu in profile.education:
            topics.append(f"Education at {edu}")
        
        # Skill-based topics  
        if profile.skills:
            topics.append(f"Technical expertise in {', '.join(profile.skills[:3])}")
        
        # Achievement-based topics
        for achievement in profile.achievements:
            topics.append(f"Professional achievement: {achievement}")
        
        # Role transition topics
        if profile.previous_roles:
            topics.append(f"Career progression from {profile.previous_roles[0] if profile.previous_roles else 'previous role'}")
        
        # Company/industry topics
        if profile.current_company and company:
            topics.append(f"Industry experience at {profile.current_company}")
        
        return topics[:5]  # Limit to 5 topics
    
    def _calculate_confidence(self, profile: ProfessionalProfile, response: TavilyResponse, target_company: str) -> float:
        """Calculate confidence score for the research results"""
        confidence = 0.0
        
        # LinkedIn profile found
        if profile.linkedin_url:
            confidence += 0.4
        
        # Company information extracted
        if profile.current_company:
            confidence += 0.2
        
        # Title information extracted  
        if profile.current_title:
            confidence += 0.2
        
        # High-scoring search results
        if response.results:
            max_score = max(r.score for r in response.results)
            confidence += min(0.2, max_score * 0.2)
        
        # Company connection
        if target_company and (
            (profile.current_company and target_company.lower() in profile.current_company.lower()) or
            any(target_company.lower() in role.lower() for role in profile.previous_roles)
        ):
            confidence += 0.1
        
        return min(1.0, confidence)  # Cap at 1.0
    
    def format_interviewer_summary(self, research: InterviewerResearchResult) -> str:
        """Format interviewer research into readable summary"""
        summary = []
        
        profile = research.profile
        
        # Header
        summary.append(f"## {profile.name}")
        if profile.current_title and profile.current_company:
            summary.append(f"**{profile.current_title}** at **{profile.current_company}**")
        elif profile.current_title:
            summary.append(f"**{profile.current_title}**")
        elif profile.current_company:
            summary.append(f"**{profile.current_company}**")
        
        if profile.location:
            summary.append(f"📍 {profile.location}")
        
        # Education
        if profile.education:
            summary.append(f"\n**Education:** {', '.join(profile.education)}")
        
        # Skills
        if profile.skills:
            summary.append(f"**Skills:** {', '.join(profile.skills)}")
        
        # Company connection
        if research.company_connection:
            summary.append(f"\n**Company Connection:** {research.company_connection}")
        
        # Conversation topics
        if research.potential_topics:
            summary.append(f"\n**Potential Conversation Topics:**")
            for topic in research.potential_topics:
                summary.append(f"• {topic}")
        
        # Achievements
        if profile.achievements:
            summary.append(f"\n**Notable Achievements:**")
            for achievement in profile.achievements:
                summary.append(f"• {achievement}")
        
        # Research metadata
        summary.append(f"\n**Research Confidence:** {research.research_confidence:.1%}")
        if profile.linkedin_url:
            summary.append(f"**LinkedIn:** {profile.linkedin_url}")
        
        return "\n".join(summary)

# Create global instance for easy importing
interviewer_researcher = InterviewerResearcher()
