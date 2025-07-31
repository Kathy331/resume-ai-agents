# Research Engine Documentation

## Overview

The Research Engine is a sophisticated AI-powered system that automatically researches companies, interviewers, and job roles using real-time web search capabilities. It integrates with the Tavily API to provide comprehensive intelligence gathering for job application workflows.

## Architecture

```
Research Engine
├── EnhancedTavilyClient     # Core API client with caching
├── CompanyResearcher        # Company intelligence gathering
├── InterviewerResearcher    # Interviewer background research
├── RoleResearcher          # Job role market analysis
└── research_orchestrator    # Workflow coordination
```

## Components

### 1. EnhancedTavilyClient

The core client that handles all Tavily API interactions with intelligent caching.

**Features:**
- 24-hour TTL caching system
- Automatic cache management
- Cost optimization through request deduplication
- Robust error handling and retries

**Usage:**
```python
from agents.research_engine import EnhancedTavilyClient

client = EnhancedTavilyClient(api_key="your_tavily_key")
results = await client.search(
    query="JUTEQ company AI technology",
    search_depth="advanced",
    max_results=10
)
```

**Cache System:**
- Cache Location: `.tavily_cache/` directory
- Cache Key: MD5 hash of search query
- TTL: 24 hours (86400 seconds)
- Format: JSON files with metadata

### 2. CompanyResearcher

Specialized agent for comprehensive company intelligence gathering.

**Research Areas:**
- Company overview and industry
- Recent news and developments
- Leadership and key personnel
- Technology stack and focus areas
- Market position and competitors

**Usage:**
```python
from agents.research_engine import CompanyResearcher

researcher = CompanyResearcher()
result = await researcher.research_company(
    company_name="JUTEQ",
    deep_search=True
)

# Access results
print(result.company_info.name)
print(result.company_info.industry)
print(result.recent_news)
print(result.key_insights)
```

**Output Structure:**
```python
class CompanyResearchResult:
    company_info: CompanyInfo        # Basic company details
    recent_news: List[NewsItem]      # Latest developments
    key_insights: List[str]          # Strategic insights
    search_metadata: Dict[str, Any]  # Search statistics
```

### 3. InterviewerResearcher

Agent focused on researching interview personnel and hiring managers.

**Research Areas:**
- Professional background and experience
- LinkedIn profile and connections
- Current role and responsibilities
- Educational background
- Published content and thought leadership

**Usage:**
```python
from agents.research_engine import InterviewerResearcher

researcher = InterviewerResearcher()
result = await researcher.research_interviewer(
    interviewer_name="Rakesh Gohel",
    company="JUTEQ",
    additional_context="Founder CEO AI Agents"
)

# Access results
print(result.profile.name)
print(result.profile.current_title)
print(result.profile.linkedin_url)
print(f"Research confidence: {result.research_confidence:.1%}")
```

**Output Structure:**
```python
class InterviewerResearchResult:
    profile: InterviewerProfile      # Personal/professional details
    research_confidence: float       # Confidence score (0.0-1.0)
    search_metadata: Dict[str, Any]  # Search statistics
```

### 4. RoleResearcher

Market intelligence agent for job roles and career opportunities.

**Research Areas:**
- Role requirements and responsibilities
- Salary ranges and compensation
- Market demand and trends
- Required skills and qualifications
- Career progression paths

**Usage:**
```python
from agents.research_engine import RoleResearcher

researcher = RoleResearcher()
result = await researcher.research_role(
    role_title="AI and Cloud Technologies Intern",
    company="JUTEQ",
    location="Remote",
    experience_level="Entry Level"
)

# Access results
print(result.role_title)
print(result.salary_info.base_salary_range)
print(result.skill_requirements.required_skills)
```

**Output Structure:**
```python
class RoleResearchResult:
    role_title: str
    salary_info: SalaryInfo          # Compensation details
    skill_requirements: SkillReqs     # Technical/soft skills
    market_trends: MarketTrends      # Industry insights
    search_metadata: Dict[str, Any]  # Search statistics
```

### 5. Research Orchestrator

High-level workflow manager that coordinates multiple research agents.

**Usage:**
```python
from agents.research_engine import research_orchestrator, ResearchRequest

request = ResearchRequest(
    company_name="JUTEQ",
    interviewer_name="Rakesh Gohel",
    role_title="AI Intern",
    additional_context="Founder CEO AI Agents Cloud"
)

results = await research_orchestrator(request)

# Access comprehensive results
company_data = results['company']
interviewer_data = results['interviewer']
role_data = results['role']
```

## Configuration

### Environment Variables

```bash
# Required
export TAVILY_API_KEY="your_tavily_api_key_here"

# Optional
export TAVILY_CACHE_TTL=86400  # Cache TTL in seconds (default: 24 hours)
export TAVILY_MAX_RETRIES=3    # Max retry attempts (default: 3)
```

### Research Settings

```python
# Company Research
COMPANY_SEARCH_DEPTH = "advanced"  # basic, advanced
COMPANY_MAX_RESULTS = 10
COMPANY_INCLUDE_DOMAINS = ["linkedin.com", "crunchbase.com"]

# Interviewer Research
INTERVIEWER_SEARCH_DEPTH = "advanced"
INTERVIEWER_MAX_RESULTS = 8
INTERVIEWER_FOCUS_PLATFORMS = ["linkedin.com", "github.com"]

# Role Research
ROLE_SEARCH_DEPTH = "basic"
ROLE_MAX_RESULTS = 6
ROLE_SALARY_SOURCES = ["glassdoor.com", "levels.fyi"]
```

## API Reference

### CompanyResearcher Methods

#### `research_company(company_name: str, deep_search: bool = False) -> CompanyResearchResult`

**Parameters:**
- `company_name`: Target company name
- `deep_search`: Enable comprehensive research mode

**Returns:** CompanyResearchResult with complete company intelligence

### InterviewerResearcher Methods

#### `research_interviewer(interviewer_name: str, company: str = None, additional_context: str = None) -> InterviewerResearchResult`

**Parameters:**
- `interviewer_name`: Full name of interviewer
- `company`: Company context for targeted search
- `additional_context`: Additional search context (title, role, etc.)

**Returns:** InterviewerResearchResult with professional profile

### RoleResearcher Methods

#### `research_role(role_title: str, company: str = None, location: str = None, experience_level: str = None) -> RoleResearchResult`

**Parameters:**
- `role_title`: Target job role title
- `company`: Company context
- `location`: Geographic location
- `experience_level`: Experience level (Entry, Mid, Senior)

**Returns:** RoleResearchResult with market intelligence

## Error Handling

The research engine implements robust error handling:

```python
try:
    result = await researcher.research_company("JUTEQ")
except TavilyAPIError as e:
    logger.error(f"Tavily API error: {e}")
except CacheError as e:
    logger.warning(f"Cache error: {e}")
except ResearchError as e:
    logger.error(f"Research failed: {e}")
```

**Common Error Types:**
- `TavilyAPIError`: API key issues, rate limits, network problems
- `CacheError`: Cache read/write issues
- `ResearchError`: Data parsing or processing failures
- `ValidationError`: Invalid input parameters

## Performance Optimization

### Caching Strategy

1. **Query Deduplication**: Identical queries use cached results
2. **TTL Management**: 24-hour cache expiration
3. **Cost Reduction**: Minimize API calls through intelligent caching
4. **Cache Warming**: Pre-populate cache for common queries

### Best Practices

```python
# Good: Use specific, targeted queries
await researcher.research_company("JUTEQ AI cloud technologies")

# Avoid: Generic, broad queries
await researcher.research_company("technology company")

# Good: Provide context for better results
await researcher.research_interviewer(
    "Rakesh Gohel", 
    company="JUTEQ",
    additional_context="Founder CEO"
)

# Good: Enable deep search for important research
result = await researcher.research_company("JUTEQ", deep_search=True)
```

## Integration Examples

### Email Processing Integration

```python
async def process_interview_email(email_data):
    """Process interview email with research intelligence"""
    
    # Extract entities from email
    entities = await extract_entities(email_data['body'])
    
    # Research company and interviewer
    if entities.get('company') and entities.get('interviewer'):
        research_request = ResearchRequest(
            company_name=entities['company'],
            interviewer_name=entities['interviewer'],
            role_title=entities.get('role'),
            additional_context=email_data['subject']
        )
        
        research_results = await research_orchestrator(research_request)
        
        # Generate personalized response
        response = await generate_interview_response(
            email_data=email_data,
            research_data=research_results
        )
        
        return response
```

### Workflow Integration

```python
from workflows.full_job_application import JobApplicationWorkflow

workflow = JobApplicationWorkflow()
workflow.add_research_engine(research_orchestrator)

# Automatic research during application process
result = await workflow.process_application(job_posting)
```

## Testing

### Unit Tests

```bash
# Run research engine unit tests
python -m pytest tests/unit/agents/test_research_engine.py -v

# Run integration tests (requires API key)
python -m pytest tests/integration/test_research_engine_integration.py -v
```

### Integration Testing

```python
# Test with real API calls
python tests/integration/test_real_tavily_research.py

# Expected output:
# ✅ Company research completed
# ✅ Interviewer research completed  
# ✅ Role research completed
# 📊 Overall Research Quality: 76.1%
```

## Monitoring and Analytics

### Research Quality Metrics

```python
def calculate_research_quality(results):
    """Calculate overall research quality score"""
    
    company_score = 0.8 if results.company.website else 0.6
    if results.company.recent_news:
        company_score += 0.1
    
    interviewer_score = results.interviewer.research_confidence
    
    role_score = 0.7
    if results.role.salary_info:
        role_score += 0.15
    
    return (company_score * 0.4 + interviewer_score * 0.3 + role_score * 0.3)
```

### Usage Analytics

- **API Call Volume**: Track daily/monthly API usage
- **Cache Hit Rate**: Monitor cache effectiveness
- **Research Confidence**: Average confidence scores
- **Response Times**: Performance monitoring

## Security Considerations

### API Key Management

```bash
# Use environment variables (recommended)
export TAVILY_API_KEY="tvly-xxxxxxxxxx"

# Or use secure configuration files
echo "TAVILY_API_KEY=tvly-xxxxxxxxxx" > .env.local
```

### Data Privacy

- Research results may contain personal information
- Implement data retention policies
- Consider GDPR/privacy compliance
- Cache files should be excluded from version control

### Rate Limiting

```python
# Built-in rate limiting
client = EnhancedTavilyClient(
    api_key=api_key,
    max_requests_per_minute=60,
    backoff_strategy="exponential"
)
```

## Troubleshooting

### Common Issues

**1. ModuleNotFoundError for agents.research_engine**
```bash
# Ensure correct Python path
export PYTHONPATH="/path/to/resume-ai-agents:$PYTHONPATH"

# Or add to script
sys.path.append('/path/to/resume-ai-agents')
```

**2. Tavily API Key Missing**
```bash
# Set environment variable
export TAVILY_API_KEY="your_key_here"

# Verify it's set
echo $TAVILY_API_KEY
```

**3. Cache Permission Issues**
```bash
# Fix cache directory permissions
chmod 755 .tavily_cache/
chmod 644 .tavily_cache/*.json
```

**4. Low Research Quality**
- Check API key validity
- Verify search queries are specific
- Enable deep_search for better results
- Review search result filtering

### Debug Mode

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('research_engine')

# Research with debug output
result = await researcher.research_company("JUTEQ", debug=True)
```

## Future Enhancements

### Planned Features

1. **Multi-language Support**: Research in different languages
2. **Real-time Monitoring**: Live research quality dashboard
3. **Custom Research Profiles**: Tailored research templates
4. **Advanced Analytics**: Research trend analysis
5. **AI-powered Insights**: LLM-generated strategic insights

### Contributing

See `CONTRIBUTING.md` for guidelines on extending the research engine.

---

## Quick Start

1. **Set API Key**: `export TAVILY_API_KEY="your_key"`
2. **Import**: `from agents.research_engine import CompanyResearcher`
3. **Research**: `result = await CompanyResearcher().research_company("JUTEQ")`
4. **Use Results**: `print(result.company_info.description)`

For more examples, see `tests/integration/test_research_engine_integration.py`.
