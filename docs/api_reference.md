# API Reference Guide

## **OpenAI API Integration**

For detailed pricing information, check: https://openai.com/api/pricing/

### Model Selection Guide

| **Task** | **Recommended Model** | **Why** | **Usage in Project** |
|---|---|---|---|
| Email classification & entity extraction | `gpt-4o-mini` | Cost-efficient, fast NLP tasks | `agents/email_classifier/`, `agents/entity_extractor/` |
| Interview guide generation | `gpt-4o` | High-quality reasoning for comprehensive guides | `shared/openai_cache.py` |
| Company & role research synthesis | Tavily API | Web search and intelligence gathering | `api/run_tavily.py`, `shared/tavily_client.py` |
| Keyword extraction & company matching | `gpt-4o-mini` | Structured data extraction | `agents/keyword_extractor/` |
| Memory and deduplication | `text-embedding-3-small` | Vector search & similarity matching | `agents/memory_systems/` |

### API Configuration

```python
# shared/llm_client.py
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEFAULT_MODEL = "gpt-4o-mini"  # Cost-efficient default
EMBEDDING_MODEL = "text-embedding-3-small"
```

---

## **Tavily AI Search API**

Advanced AI-powered web search for research intelligence.

### Configuration
```python
# api/run_tavily.py
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
```

### Usage in Project

| **Component** | **Purpose** | **Integration Type** |
|---|---|---|
| `api/run_tavily.py` | Company intelligence gathering | `API integration` |
| `shared/tavily_client.py` | Tavily API client with caching | `Client library` |
| `shared/openai_cache.py` | OpenAI API with response caching | `Cached client` |

### API Limits & Best Practices
- **Rate Limiting**: Monitor Tavily and OpenAI usage to avoid hitting API limits
- **Caching Strategy**: Implement intelligent caching to reduce redundant API calls
- **Cost Optimization**: Use cached responses for development and repeated queries

---

## **Google APIs Integration**

### Gmail API
- **Purpose**: Automated email fetching and processing
- **Scopes**: `https://mail.google.com/` (full Gmail access)
- **Authentication**: OAuth 2.0 flow
- **Implementation**: `shared/google_oauth/`

### Google OAuth 2.0
- **Configuration File**: `client_secret.json`
- **Token Storage**: `token_files/token_gmail_v1.json`
- **Security**: Secure token refresh and validation

---

## **Development APIs**

### Local Development
- **Streamlit Server**: `http://localhost:8501`
- **FastAPI Server**: `http://localhost:8000` (if enabled)
- **Debug Mode**: Environment-based configuration

### Testing Considerations
- **Token Limits**: Be mindful of API usage during testing
- **Mock Data**: Use sample data in `tests/sample_data/` for development
- **Rate Limiting**: Implement delays between API calls in tests

---

## **Error Handling & Monitoring**

### Common Issues
1. **API Rate Limits**: Implement exponential backoff
2. **Token Expiration**: Automatic refresh mechanisms
3. **Network Timeouts**: Retry logic with circuit breakers
4. **Invalid Responses**: Schema validation and fallback handling

### Monitoring
- **API Usage Tracking**: Log all external API calls
- **Performance Metrics**: Response times and success rates
- **Cost Monitoring**: Track token usage and API costs

