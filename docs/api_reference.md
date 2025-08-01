# API Reference Guide

## **OpenAI API Integration**

For detailed pricing information, check: https://openai.com/api/pricing/

### Model Selection Guide

| **Task** | **Recommended Model** | **Why** | **Usage in Project** |
|---|---|---|---|
| Email classification & entity extraction | `gpt-4o-mini` | Cost-efficient, fast NLP tasks | `agents/email_classifier/`, `agents/entity_extractor/` |
| Interview question generation | `gpt-4o` | High-quality reasoning for personalized content | `agents/question_generation/` |
| Company & role research synthesis | `gpt-4-turbo-preview` | Advanced reasoning for complex research tasks | `agents/research_engine/` |
| Resume analysis & skill extraction | `gpt-4o-mini` | Structured data extraction | `agents/resume_analyzer/` |
| Email writing & personalization | `gpt-4o` | Creative writing with context awareness | `agents/email_writer/` |
| Code generation & debugging | `gpt-4o` | Technical task support | Development utilities |
| Text embeddings for similarity | `text-embedding-3-small` | Vector search & deduplication | `shared/vector_store.py`, memory systems |

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

| **Component** | **Purpose** | **Search Depth** |
|---|---|---|
| `agents/research_engine/company_researcher.py` | Company intelligence gathering | `advanced` |
| `agents/research_engine/interviewer_researcher.py` | Professional background research | `basic` |
| `agents/research_engine/role_researcher.py` | Job market and role analysis | `advanced` |

### API Limits & Best Practices
- **Rate Limiting**: Monitor usage to avoid hitting API limits
- **Search Depth**: Use `advanced` for comprehensive research, `basic` for quick facts
- **Caching**: Implement result caching to reduce redundant API calls

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

