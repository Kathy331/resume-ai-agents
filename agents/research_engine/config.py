"""
Research Engine Configuration

This module contains configuration settings for all research engine components.
Centralizes API keys, search parameters, caching settings, and research thresholds.
"""

import os
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class TavilyConfig:
    """Tavily API configuration"""
    api_key: str = os.getenv('TAVILY_API_KEY', '')
    base_url: str = "https://api.tavily.com"
    max_results: int = 5
    search_depth: str = "advanced"
    include_images: bool = False
    include_answer: bool = True
    include_raw_content: bool = False
    max_tokens: int = 4000
    
    # Rate limiting
    requests_per_minute: int = 60
    requests_per_hour: int = 1000
    
    # Cache settings
    cache_ttl_hours: int = 24  # 24 hours
    max_cache_size: int = 1000

@dataclass
class CompanyResearchConfig:
    """Company research specific configuration"""
    # Search parameters
    basic_search_queries: List[str] = None
    deep_search_queries: List[str] = None
    news_search_days: int = 90  # Look for news in last 90 days
    
    # Confidence thresholds
    min_confidence_score: float = 0.3
    high_confidence_threshold: float = 0.8
    
    # Information requirements
    required_company_fields: List[str] = None
    preferred_news_sources: List[str] = None
    
    def __post_init__(self):
        if self.basic_search_queries is None:
            self.basic_search_queries = [
                "{company_name} company overview",
                "{company_name} business model",
                "{company_name} headquarters location"
            ]
        
        if self.deep_search_queries is None:
            self.deep_search_queries = [
                "{company_name} recent news 2024",
                "{company_name} funding financial information",
                "{company_name} company culture values",
                "{company_name} leadership team executives",
                "{company_name} products services offerings",
                "{company_name} competitors industry analysis"
            ]
        
        if self.required_company_fields is None:
            self.required_company_fields = [
                'name', 'industry', 'description', 'website'
            ]
        
        if self.preferred_news_sources is None:
            self.preferred_news_sources = [
                'techcrunch.com', 'bloomberg.com', 'reuters.com',
                'wsj.com', 'businessinsider.com', 'fortune.com'
            ]

@dataclass
class RoleResearchConfig:
    """Role research specific configuration"""
    # Search parameters
    role_search_queries: List[str] = None
    salary_search_queries: List[str] = None
    skills_search_queries: List[str] = None
    
    # Market analysis
    market_analysis_locations: List[str] = None
    experience_levels: List[str] = None
    
    # Confidence thresholds
    min_confidence_score: float = 0.4
    salary_confidence_threshold: float = 0.6
    
    def __post_init__(self):
        if self.role_search_queries is None:
            self.role_search_queries = [
                "{role_title} job description requirements",
                "{role_title} responsibilities duties",
                "{role_title} career path progression"
            ]
        
        if self.salary_search_queries is None:
            self.salary_search_queries = [
                "{role_title} salary {location} 2024",
                "{role_title} compensation package {company}",
                "{role_title} market rate {experience_level}"
            ]
        
        if self.skills_search_queries is None:
            self.skills_search_queries = [
                "{role_title} required skills qualifications",
                "{role_title} technical skills programming",
                "{role_title} soft skills competencies"
            ]
        
        if self.market_analysis_locations is None:
            self.market_analysis_locations = [
                'San Francisco', 'New York', 'Seattle', 'Austin',
                'Boston', 'Los Angeles', 'Chicago', 'Remote'
            ]
        
        if self.experience_levels is None:
            self.experience_levels = [
                'entry-level', 'junior', 'mid-level', 'senior', 'lead', 'principal'
            ]

@dataclass
class InterviewerResearchConfig:
    """Interviewer research specific configuration"""
    # Search parameters
    linkedin_search_queries: List[str] = None
    background_search_queries: List[str] = None
    
    # LinkedIn search patterns
    linkedin_url_patterns: List[str] = None
    
    # Confidence thresholds
    min_confidence_score: float = 0.3
    profile_match_threshold: float = 0.7
    
    # Professional networks
    professional_platforms: List[str] = None
    
    def __post_init__(self):
        if self.linkedin_search_queries is None:
            self.linkedin_search_queries = [
                '"{interviewer_name}" LinkedIn {company}',
                '"{interviewer_name}" {company} profile',
                '"{interviewer_name}" professional background'
            ]
        
        if self.background_search_queries is None:
            self.background_search_queries = [
                '"{interviewer_name}" {company} biography',
                '"{interviewer_name}" work experience career',
                '"{interviewer_name}" education background'
            ]
        
        if self.linkedin_url_patterns is None:
            self.linkedin_url_patterns = [
                r'linkedin\.com/in/[\w-]+',
                r'linkedin\.com/pub/[\w-]+',
                r'www\.linkedin\.com/in/[\w-]+'
            ]
        
        if self.professional_platforms is None:
            self.professional_platforms = [
                'LinkedIn', 'AngelList', 'Crunchbase', 'GitHub',
                'Twitter', 'Medium', 'Personal Website'
            ]

@dataclass
class ResearchOrchestratorConfig:
    """Research orchestrator configuration"""
    # Research depth definitions
    research_depth_definitions: Dict[str, List[str]] = None
    
    # Confidence calculation weights
    confidence_weights: Dict[str, float] = None
    
    # Cross-insights settings
    max_cross_insights: int = 5
    insight_relevance_threshold: float = 0.5
    
    # Export settings
    export_formats: List[str] = None
    max_summary_length: int = 2000
    
    def __post_init__(self):
        if self.research_depth_definitions is None:
            self.research_depth_definitions = {
                'basic': ['company'],
                'standard': ['company', 'role'],
                'comprehensive': ['company', 'role', 'interviewer']
            }
        
        if self.confidence_weights is None:
            self.confidence_weights = {
                'company': 0.4,
                'role': 0.3,
                'interviewer': 0.3
            }
        
        if self.export_formats is None:
            self.export_formats = ['json', 'markdown', 'text']

# Main configuration class
class ResearchEngineConfig:
    """Main research engine configuration"""
    
    def __init__(self):
        self.tavily = TavilyConfig()
        self.company_research = CompanyResearchConfig()
        self.role_research = RoleResearchConfig()
        self.interviewer_research = InterviewerResearchConfig()
        self.orchestrator = ResearchOrchestratorConfig()
        
        # Validate configuration
        self._validate_config()
    
    def _validate_config(self):
        """Validate configuration settings"""
        # Check for required API key
        if not self.tavily.api_key:
            print("⚠️  Warning: TAVILY_API_KEY not found in environment variables")
        
        # Validate confidence thresholds
        for config in [self.company_research, self.role_research, self.interviewer_research]:
            if config.min_confidence_score >= 1.0 or config.min_confidence_score < 0:
                raise ValueError(f"Invalid confidence score: {config.min_confidence_score}")
        
        # Validate weights sum to 1.0
        weight_sum = sum(self.orchestrator.confidence_weights.values())
        if abs(weight_sum - 1.0) > 0.01:
            print(f"⚠️  Warning: Confidence weights sum to {weight_sum:.2f}, not 1.0")
    
    def get_search_query(self, query_type: str, template: str, **kwargs) -> str:
        """
        Get formatted search query based on type and template
        
        Args:
            query_type: Type of query (company, role, interviewer)
            template: Query template string
            **kwargs: Variables to format into template
            
        Returns:
            Formatted search query
        """
        try:
            return template.format(**kwargs)
        except KeyError as e:
            print(f"⚠️  Missing template variable: {e}")
            return template
    
    def update_config(self, section: str, key: str, value: Any):
        """Update configuration value"""
        if hasattr(self, section):
            config_section = getattr(self, section)
            if hasattr(config_section, key):
                setattr(config_section, key, value)
                print(f"✅ Updated {section}.{key} = {value}")
            else:
                print(f"⚠️  Key '{key}' not found in section '{section}'")
        else:
            print(f"⚠️  Section '{section}' not found")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        return {
            'tavily_configured': bool(self.tavily.api_key),
            'cache_ttl_hours': self.tavily.cache_ttl_hours,
            'max_results': self.tavily.max_results,
            'research_depths': list(self.orchestrator.research_depth_definitions.keys()),
            'confidence_weights': self.orchestrator.confidence_weights,
            'company_queries': len(self.company_research.basic_search_queries + self.company_research.deep_search_queries),
            'role_queries': len(self.role_research.role_search_queries),
            'interviewer_queries': len(self.interviewer_research.linkedin_search_queries)
        }

# Global configuration instance
research_config = ResearchEngineConfig()

# Environment-specific configurations
DEVELOPMENT_CONFIG = {
    'tavily': {
        'max_results': 3,
        'cache_ttl_hours': 1
    },
    'company_research': {
        'news_search_days': 30
    }
}

PRODUCTION_CONFIG = {
    'tavily': {
        'max_results': 5,
        'cache_ttl_hours': 24
    },
    'company_research': {
        'news_search_days': 90
    }
}

def load_environment_config(env: str = 'production'):
    """Load environment-specific configuration"""
    config_map = {
        'development': DEVELOPMENT_CONFIG,
        'production': PRODUCTION_CONFIG
    }
    
    env_config = config_map.get(env, PRODUCTION_CONFIG)
    
    # Update global config with environment settings
    for section, settings in env_config.items():
        for key, value in settings.items():
            research_config.update_config(section, key, value)
    
    print(f"📝 Loaded {env} configuration")

# Load default configuration
load_environment_config(os.getenv('ENVIRONMENT', 'production'))
