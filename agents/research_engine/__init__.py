"""
Research Engine Package

This package provides comprehensive research capabilities for interview preparation,
including company research, role analysis, and interviewer background research.

Main Components:
- EnhancedTavilyClient: Advanced Tavily API wrapper with caching
- CompanyResearcher: Company intelligence and background research
- InterviewerResearcher: Professional profile and LinkedIn research  
- RoleResearcher: Job market analysis and salary research
- ResearchOrchestrator: Coordinates all research activities

Usage Examples:

    # Quick company research
    from agents.research_engine import research_orchestrator
    company_result = research_orchestrator.quick_company_research("OpenAI")
    
    # Comprehensive research from email entities
    entities = {
        'COMPANY': ['Google'], 
        'ROLE': ['Software Engineer'],
        'INTERVIEWER': ['John Smith', 'Sarah Johnson']
    }
    result = research_orchestrator.research_from_email_entities(entities)
    
    # Custom research request
    from agents.research_engine import ResearchRequest
    request = ResearchRequest(
        company_name="Microsoft",
        role_title="Product Manager", 
        interviewer_names=["Alex Chen"],
        research_depth="comprehensive"
    )
    result = research_orchestrator.conduct_comprehensive_research(request)
"""

from .tavily_client import (
    EnhancedTavilyClient,
    TavilyCache,
    TavilyResult,
    TavilyResponse
)

from .company_researcher import (
    CompanyResearcher,
    CompanyInfo,
    CompanyFinancials,
    CompanyNews,
    CompanyResearchResult
)

from .interviewer_researcher import (
    InterviewerResearcher,
    ProfessionalProfile,
    InterviewerResearchResult
)

from .role_researcher import (
    RoleResearcher,
    SalaryInfo,
    SkillRequirements,
    MarketTrends,
    RoleResearchResult
)

from .research_orchestrator import (
    ResearchOrchestrator,
    ResearchRequest,
    ComprehensiveResearchResult,
    research_orchestrator  # Global instance
)

from .config import (
    ResearchEngineConfig,
    TavilyConfig,
    CompanyResearchConfig,
    RoleResearchConfig,
    InterviewerResearchConfig,
    ResearchOrchestratorConfig,
    research_config,  # Global config instance
    load_environment_config
)

# Package metadata
__version__ = "1.0.0"
__author__ = "Resume AI Agents Team"
__description__ = "Comprehensive research engine for interview preparation"

# Export main classes and functions
__all__ = [
    # Main orchestrator
    'ResearchOrchestrator',
    'research_orchestrator',
    'ResearchRequest', 
    'ComprehensiveResearchResult',
    
    # Individual researchers
    'CompanyResearcher',
    'InterviewerResearcher', 
    'RoleResearcher',
    
    # Tavily client
    'EnhancedTavilyClient',
    'TavilyCache',
    'TavilyResult',
    'TavilyResponse',
    
    # Data models
    'CompanyInfo',
    'CompanyFinancials',
    'CompanyNews',
    'CompanyResearchResult',
    'ProfessionalProfile',
    'InterviewerResearchResult',
    'SalaryInfo',
    'SkillRequirements', 
    'MarketTrends',
    'RoleResearchResult',
    
    # Configuration
    'ResearchEngineConfig',
    'research_config',
    'load_environment_config',
    'TavilyConfig',
    'CompanyResearchConfig',
    'RoleResearchConfig',
    'InterviewerResearchConfig',
    'ResearchOrchestratorConfig'
]

# Initialize package
def initialize_research_engine(tavily_api_key: str = None, environment: str = 'production'):
    """
    Initialize the research engine with configuration
    
    Args:
        tavily_api_key: Optional API key override
        environment: Environment configuration to load
    """
    if tavily_api_key:
        research_config.tavily.api_key = tavily_api_key
        print("✅ Tavily API key configured")
    
    load_environment_config(environment)
    
    # Validate configuration
    config_summary = research_config.get_config_summary()
    if config_summary['tavily_configured']:
        print("✅ Research engine initialized successfully")
    else:
        print("⚠️  Research engine initialized without Tavily API key")
    
    return config_summary

# Auto-initialize on import (optional)
def get_package_info():
    """Get package information"""
    return {
        'version': __version__,
        'description': __description__,
        'components': {
            'orchestrator': 'Coordinates comprehensive research workflows',
            'company_researcher': 'Company intelligence and background research', 
            'interviewer_researcher': 'Professional profile and LinkedIn research',
            'role_researcher': 'Job market analysis and salary research',
            'tavily_client': 'Enhanced Tavily API wrapper with caching'
        },
        'config_status': research_config.get_config_summary()
    }

# Package health check
def health_check():
    """Perform package health check"""
    health_status = {
        'package_loaded': True,
        'config_valid': bool(research_config),
        'tavily_configured': bool(research_config.tavily.api_key),
        'orchestrator_ready': bool(research_orchestrator),
        'components_loaded': {
            'company_researcher': 'CompanyResearcher' in globals(),
            'interviewer_researcher': 'InterviewerResearcher' in globals(),
            'role_researcher': 'RoleResearcher' in globals(),
            'tavily_client': 'EnhancedTavilyClient' in globals()
        }
    }
    
    # Calculate overall health score
    health_checks = [
        health_status['config_valid'],
        health_status['tavily_configured'], 
        health_status['orchestrator_ready'],
        all(health_status['components_loaded'].values())
    ]
    
    health_status['health_score'] = sum(health_checks) / len(health_checks)
    health_status['status'] = 'healthy' if health_status['health_score'] > 0.75 else 'degraded'
    
    return health_status

# Display package info on import
print(f"📚 Research Engine v{__version__} loaded")
print(f"🎯 {__description__}")

# Show health status
health = health_check()
if health['status'] == 'healthy':
    print("✅ All components loaded successfully")
elif not health['tavily_configured']:
    print("⚠️  Note: Set TAVILY_API_KEY environment variable for full functionality")
else:
    print("⚠️  Some components may not be fully configured")
