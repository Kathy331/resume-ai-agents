# agents/interview_prep_intelligence/context_decomposer.py
"""
Context-Aware Decomposition Agent

Analyzes research context and decomposes it into structured insights
for question generation. Uses multi-source RAG and CoT prompting.
"""

import json
import hashlib
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from .models import ResearchContext, QuestionType
from .config import COT_PROMPTS, RESEARCH_CONFIG
from shared.llm_client import get_llm_client


class ContextDecomposer:
    """
    Decomposes research context into actionable insights for question generation
    
    Uses Chain-of-Thought prompting to analyze:
    - Company background and culture
    - Interviewer expertise and style  
    - Role requirements and challenges
    - Cross-cutting themes
    """
    
    def __init__(self):
        self.llm_client = get_llm_client()
        self.cache = {}  # Simple in-memory cache
        
    def decompose_context(self, research_context: ResearchContext) -> Dict[str, Any]:
        """
        Main decomposition method that analyzes all research contexts
        
        Args:
            research_context: Research data from workflow runner
            
        Returns:
            Dict containing structured insights for each category
        """
        insights = {
            "company_insights": {},
            "interviewer_insights": {},
            "role_insights": {},
            "cross_cutting_themes": [],
            "metadata": {
                "processed_at": datetime.now().isoformat(),
                "quality_indicators": {}
            }
        }
        
        # Analyze company research
        if research_context.company_research:
            insights["company_insights"] = self._analyze_company_context(
                research_context.company_research, 
                research_context.company_name
            )
            
        # Analyze interviewer research  
        if research_context.interviewer_research:
            insights["interviewer_insights"] = self._analyze_interviewer_context(
                research_context.interviewer_research,
                research_context.interviewer_name
            )
            
        # Analyze role research
        if research_context.role_research:
            insights["role_insights"] = self._analyze_role_context(
                research_context.role_research,
                research_context.role_title
            )
            
        # Find cross-cutting themes
        insights["cross_cutting_themes"] = self._identify_cross_cutting_themes(
            insights["company_insights"],
            insights["interviewer_insights"], 
            insights["role_insights"]
        )
        
        # Calculate quality indicators
        insights["metadata"]["quality_indicators"] = self._calculate_quality_indicators(insights)
        
        return insights
    
    def _analyze_company_context(self, company_research: Dict[str, Any], company_name: str) -> Dict[str, Any]:
        """Analyze company research using CoT prompting"""
        
        # Extract search results from research data
        search_results = self._extract_search_results(company_research)
        if not search_results:
            return {"error": "No company search results found"}
            
        # Create cache key
        cache_key = self._create_cache_key("company", search_results)
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # Prepare research data summary
        research_summary = self._summarize_search_results(search_results, max_length=800)
        
        # Apply CoT prompting
        prompt = COT_PROMPTS["company_analysis"].format(research_data=research_summary)
        
        try:
            response = self.llm_client.generate_text(
                prompt=f"""
                Analyze this company research and extract key insights:
                
                {prompt}
                
                Please provide a JSON response with the following structure:
                {{
                    "business_focus": ["area1", "area2"],
                    "company_values": ["value1", "value2"],
                    "recent_developments": ["development1", "development2"],
                    "culture_indicators": ["indicator1", "indicator2"],
                    "competitive_advantages": ["advantage1", "advantage2"],
                    "potential_challenges": ["challenge1", "challenge2"],
                    "question_focus_areas": ["area1", "area2"]
                }}
                """,
                max_tokens=1000,
                temperature=0.7,
                company_name=company_name
            )
            
            insights = json.loads(response)
            insights["source_quality"] = len(search_results)
            insights["company_name"] = company_name
            
            # Cache result
            self.cache[cache_key] = insights
            return insights
            
        except Exception as e:
            return {"error": f"Company analysis failed: {str(e)}"}
    
    def _analyze_interviewer_context(self, interviewer_research: Dict[str, Any], interviewer_name: str) -> Dict[str, Any]:
        """Analyze interviewer research using CoT prompting"""
        
        search_results = self._extract_search_results(interviewer_research)
        if not search_results:
            return {"error": "No interviewer search results found"}
            
        cache_key = self._create_cache_key("interviewer", search_results)
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        research_summary = self._summarize_search_results(search_results, max_length=600)
        prompt = COT_PROMPTS["interviewer_analysis"].format(research_data=research_summary)
        
        try:
            response = self.llm_client.generate_text(
                prompt=f"""
                Analyze this interviewer research and extract key insights:
                
                {prompt}
                
                Please provide a JSON response with the following structure:
                {{
                    "professional_background": ["background1", "background2"],
                    "expertise_areas": ["area1", "area2"],
                    "career_progression": ["role1", "role2"],
                    "communication_style": "professional/casual/technical",
                    "likely_interview_focus": ["focus1", "focus2"],
                    "personal_interests": ["interest1", "interest2"],
                    "question_approach_style": "behavioral/technical/conversational"
                }}
                """,
                max_tokens=800,
                temperature=0.7,
                company_name=f"{interviewer_name} ({interviewer_name})"
            )
            
            insights = json.loads(response)
            insights["source_quality"] = len(search_results)
            insights["interviewer_name"] = interviewer_name
            
            self.cache[cache_key] = insights
            return insights
            
        except Exception as e:
            return {"error": f"Interviewer analysis failed: {str(e)}"}
    
    def _analyze_role_context(self, role_research: Dict[str, Any], role_title: str) -> Dict[str, Any]:
        """Analyze role research using CoT prompting"""
        
        search_results = self._extract_search_results(role_research)
        if not search_results:
            return {"error": "No role search results found"}
            
        cache_key = self._create_cache_key("role", search_results)  
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        research_summary = self._summarize_search_results(search_results, max_length=700)
        prompt = COT_PROMPTS["role_analysis"].format(research_data=research_summary)
        
        try:
            response = self.llm_client.generate_text(
                prompt=f"""
                Analyze this role research and extract key insights:
                
                {prompt}
                
                Please provide a JSON response with the following structure:
                {{
                    "core_technical_skills": ["skill1", "skill2"],
                    "soft_skills_required": ["skill1", "skill2"], 
                    "key_responsibilities": ["resp1", "resp2"],
                    "success_metrics": ["metric1", "metric2"],
                    "common_challenges": ["challenge1", "challenge2"],
                    "growth_opportunities": ["opportunity1", "opportunity2"],
                    "industry_trends": ["trend1", "trend2"],
                    "salary_range": "range if available"
                }}
                """,
                max_tokens=1000,
                temperature=0.7,
                company_name=f"Role: {role_title}"
            )
            
            insights = json.loads(response)
            insights["source_quality"] = len(search_results)
            insights["role_title"] = role_title
            
            self.cache[cache_key] = insights
            return insights
            
        except Exception as e:
            return {"error": f"Role analysis failed: {str(e)}"}
    
    def _identify_cross_cutting_themes(self, company_insights: Dict, interviewer_insights: Dict, role_insights: Dict) -> List[str]:
        """Identify themes that appear across multiple research areas"""
        
        themes = []
        
        # Extract keywords from each insight category
        company_keywords = self._extract_keywords(company_insights)
        interviewer_keywords = self._extract_keywords(interviewer_insights)
        role_keywords = self._extract_keywords(role_insights)
        
        # Find overlapping themes
        all_keywords = [company_keywords, interviewer_keywords, role_keywords]
        
        for keyword in company_keywords:
            overlap_count = sum(1 for kw_set in all_keywords if keyword in kw_set)
            if overlap_count >= 2:  # Appears in at least 2 categories
                themes.append(keyword)
        
        return list(set(themes))  # Remove duplicates
    
    def _extract_search_results(self, research_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract search results from research data structure"""
        
        if isinstance(research_data, dict):
            # Check for nested data structure (like from workflow runner)
            if 'data' in research_data and isinstance(research_data['data'], dict):
                data = research_data['data']
                if 'search_results' in data:
                    return data['search_results']
            
            # Check direct search_results key
            if 'search_results' in research_data:
                return research_data['search_results']
                
            # Check if this is already a list of results
            if isinstance(research_data, list):
                return research_data
        
        return []
    
    def _summarize_search_results(self, search_results: List[Dict[str, Any]], max_length: int = 1000) -> str:
        """Summarize search results into a concise text"""
        
        summary_parts = []
        current_length = 0
        
        for result in search_results:
            title = result.get('title', '')
            content = result.get('content', result.get('snippet', ''))
            url = result.get('url', '')
            
            # Create a summary for this result
            result_summary = f"Title: {title}\nContent: {content[:200]}...\nSource: {url}\n"
            
            if current_length + len(result_summary) <= max_length:
                summary_parts.append(result_summary)
                current_length += len(result_summary)
            else:
                break
                
        return "\n---\n".join(summary_parts)
    
    def _extract_keywords(self, insights: Dict[str, Any]) -> List[str]:
        """Extract keywords from insights for theme identification"""
        
        keywords = []
        
        # Extract from all string and list values
        for key, value in insights.items():
            if isinstance(value, list):
                keywords.extend([str(v).lower() for v in value])
            elif isinstance(value, str):
                # Simple keyword extraction (could be enhanced with NLP)
                words = value.lower().split()
                keywords.extend([w for w in words if len(w) > 3])
        
        return keywords
    
    def _create_cache_key(self, context_type: str, search_results: List[Dict[str, Any]]) -> str:
        """Create a cache key for search results"""
        
        # Create a hash of the search results content
        content = ""
        for result in search_results:
            content += result.get('title', '') + result.get('content', '')
            
        content_hash = hashlib.md5(content.encode()).hexdigest()
        return f"{context_type}_{content_hash}"
    
    def _calculate_quality_indicators(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate quality indicators for the decomposed insights"""
        
        indicators = {
            "company_completeness": 0.0,
            "interviewer_completeness": 0.0,
            "role_completeness": 0.0,
            "cross_theme_richness": 0.0,
            "overall_quality": 0.0
        }
        
        # Calculate completeness scores
        if "error" not in insights["company_insights"]:
            indicators["company_completeness"] = min(1.0, len(insights["company_insights"]) / 5)
            
        if "error" not in insights["interviewer_insights"]:
            indicators["interviewer_completeness"] = min(1.0, len(insights["interviewer_insights"]) / 5)
            
        if "error" not in insights["role_insights"]:
            indicators["role_completeness"] = min(1.0, len(insights["role_insights"]) / 5)
        
        # Cross-cutting theme richness
        indicators["cross_theme_richness"] = min(1.0, len(insights["cross_cutting_themes"]) / 3)
        
        # Overall quality (weighted average)
        indicators["overall_quality"] = (
            indicators["company_completeness"] * 0.3 +
            indicators["interviewer_completeness"] * 0.3 +
            indicators["role_completeness"] * 0.3 +
            indicators["cross_theme_richness"] * 0.1
        )
        
        return indicators
