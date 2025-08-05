# Development Tools & Utilities - Resume AI Agents

## Overview

This document outlines the development tools, utilities, and workflows available for working with the Resume AI Agents Interview Prep Workflow system.

---

## Core Entry Points

### **Interview Prep Workflow** (Main Entry Point)
- **Location**: `workflows/interview_prep_workflow.py`
- **Purpose**: Main orchestrator for the complete interview preparation system
- **Usage**: 
  ```bash
  # Run complete workflow
  python workflows/interview_prep_workflow.py
  
  # Process maximum 5 emails
  python workflows/interview_prep_workflow.py --max-emails 5
  ```
- **Features**:
  - Individual email processing (one-by-one)
  - Real-time terminal feedback
  - Complete pipeline orchestration
  - Cache integration and optimization

### **Cache Manager** (System Optimization)
- **Location**: `workflows/cache_manager.py`
- **Purpose**: Command-line tool for managing Tavily and OpenAI caches
- **Usage**:
  ```bash
  # Check cache status
  python workflows/cache_manager.py --status
  
  # Clear all caches
  python workflows/cache_manager.py --clear-all
  
  # Clear specific caches
  python workflows/cache_manager.py --clear-tavily
  python workflows/cache_manager.py --clear-openai
  
  # Optimize caches
  python workflows/cache_manager.py --optimize
  
  # Detailed cache information
  python workflows/cache_manager.py --info
  ```
- **Features**:
  - Real-time cache status monitoring
  - Individual and bulk cache clearing
  - Cache optimization and cleanup
  - API usage statistics and cost tracking

---

## Pipeline Development Tools

### **Email Pipeline**
- **Location**: `pipelines/email_pipeline.py`
- **Purpose**: Email classification, entity extraction, and memory management
- **Usage**:
  ```python
  from pipelines.email_pipeline import EmailPipeline
  
  pipeline = EmailPipeline()
  result = pipeline.process_email(email_data)
  ```
- **Features**:
  - Email classification with advanced pattern recognition
  - Entity extraction for company, role, and interviewer data
  - Memory-based duplicate detection
  - Structured output for research pipeline

### **Deep Research Pipeline**
- **Location**: `pipelines/deep_research_pipeline.py`
- **Purpose**: Multi-agent research coordination with Tavily API integration
- **Usage**:
  ```python
  from pipelines.deep_research_pipeline import DeepResearchPipeline
  
  pipeline = DeepResearchPipeline()
  research_data = pipeline.conduct_research(entity_data)
  ```
- **Features**:
  - Parallel research execution (company, role, interviewer)
  - Tavily API integration with intelligent caching
  - Research quality validation and reflection
  - Additional research loops for completeness

### **Prep Guide Pipeline**
- **Location**: `pipelines/prep_guide_pipeline.py` 
- **Purpose**: Personalized interview preparation guide generation
- **Usage**:
  ```python
  from pipelines.prep_guide_pipeline import PrepGuidePipeline
  
  pipeline = PrepGuidePipeline()
  guide = pipeline.generate_guide(research_data)
  ```
- **Features**:
  - Multi-section guide generation
  - OpenAI API integration with caching
  - Citation integration for all research-backed content
  - Individual file output with company-based naming

---

## Development Utilities

### **Agent Testing Framework**
- **Location**: `tests/test_agents/`
- **Purpose**: Comprehensive testing suite organized by agent categories
- **Structure**:
  ```
  tests/test_agents/
  ├── email_classifier/     # Email classification tests
  ├── entity_extractor/     # Entity extraction validation  
  ├── keyword_extractor/    # Company name extraction tests
  └── research_engine/      # Research integration tests
  ```
- **Usage**:
  ```bash
  # Run all agent tests
  python -m pytest tests/test_agents/ -v
  
  # Run specific agent tests
  python -m pytest tests/test_agents/email_classifier/ -v
  python tests/test_agents/entity_extractor/run_entity_tests.py
  ```

### **Configuration Management**
- **Location**: `configs/`
- **Purpose**: Centralized configuration management
- **Files**:
  - `agent_configs.yaml`: Agent-specific configurations
  - `llm_prompts.yaml`: LLM prompt templates
  - `logging.yaml`: Logging configuration
  - `deployment.yaml`: Deployment settings

### **Environment Setup**
- **Location**: `.env` (root directory)
- **Purpose**: Environment variable configuration
- **Required Variables**:
  ```bash
  # API Keys
  OPENAI_API_KEY=your_openai_key
  TAVILY_API_KEY=your_tavily_key
  
  # Email Configuration
  INTERVIEW_FOLDER=/path/to/interview/emails
  GMAIL_CREDENTIALS_PATH=/path/to/gmail/credentials.json
  
  # Output Configuration
  OUTPUT_FOLDER=outputs/fullworkflow
  
  # Cache Configuration
  CACHE_EXPIRY_HOURS=24
  MAX_EMAILS_PER_RUN=10
  ```

---

## Data Flow Visualization Tools

### **ASCII Flow Diagrams**
All pipeline documentation includes ASCII-style flow diagrams for easy visualization:

```
📂 INTERVIEW_FOLDER → 📬 Email Classifier → 🎯 Entity Extractor → 🧠 Memory Check → 🔬 Research Pipeline
```

### **Terminal Output Monitoring**
Real-time feedback during workflow execution:
- **Email Classification**: "📧 Email classified as: INTERVIEW"
- **Memory Status**: "🧠 Already Prepped: [Company]" or "🧠 New Email: Processing [Company]"
- **Research Progress**: Real-time research coordination and quality validation
- **Guide Generation**: Complete preparation guide display before storage

---

## API Integration Tools

### **Tavily Research Integration**
- **Location**: `shared/tavily_client.py`
- **Purpose**: Tavily API client with caching and optimization
- **Features**:
  - Query optimization and caching
  - Rate limiting and error handling
  - Source citation tracking
  - Cache hit rate monitoring

### **OpenAI Integration**
- **Location**: `shared/openai_cache.py`
- **Purpose**: OpenAI API client with response caching
- **Features**:
  - Response caching for cost optimization
  - Token usage tracking
  - Error handling and retry logic
  - Cache statistics and monitoring

### **Gmail Integration**
- **Location**: `shared/google_oauth/`
- **Purpose**: Gmail API integration for email processing
- **Features**:
  - OAuth authentication setup
  - Email fetching and parsing
  - Label-based email filtering
  - Attachment handling

---

## Performance Monitoring Tools

### **Cache Performance Analytics**
```bash
# View cache statistics
python workflows/cache_manager.py --status

# Output shows:
# 📊 TAVILY RESEARCH CACHE:
#    📊 Cached Queries: 72
#    💾 Size: 15.3 MB
#    🟢 Status: Active with cached data
#
# 🤖 OPENAI LLM CACHE:
#    📊 Cached Responses: 45
#    💾 Size: 8.7 MB
#    💰 Estimated Savings: $12.45
```

### **Workflow Statistics**
The main workflow provides comprehensive statistics:
- Number of emails processed
- Classification success rates  
- Cache hit rates and API usage
- Guide generation success rates
- Processing time per email

### **Error Tracking and Debugging**
- **Logging**: Comprehensive logging throughout all pipeline stages
- **Error Recovery**: Graceful degradation and recovery mechanisms
- **Debug Mode**: Verbose output for troubleshooting
- **Performance Profiling**: Execution time tracking per component

---

## Development Workflows

### **Local Development Setup**
```bash
# 1. Clone repository
git clone [repository-url]
cd resume-ai-agents

# 2. Set up environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys and configurations

# 4. Run tests
python -m pytest tests/ -v

# 5. Run workflow
python workflows/interview_prep_workflow.py
```

### **Docker Development**
```bash
# Build container
docker build -t resume-ai-agents .

# Run with environment file
docker run --env-file .env -v $(pwd)/outputs:/app/outputs resume-ai-agents

# Run with cache persistence
docker run --env-file .env -v $(pwd)/cache:/app/cache -v $(pwd)/.openai_cache:/app/.openai_cache resume-ai-agents
```

### **Testing Workflows**
```bash
# Unit tests
python -m pytest tests/test_agents/ -v

# Integration tests  
python -m pytest tests/test_shared/ -v

# End-to-end workflow tests
python -m pytest tests/test_workflows/ -v

# Performance tests
python scripts/test_research_pipeline.py
```

---

## Debugging and Troubleshooting

### **Common Issues and Solutions**

#### Cache Issues
```bash
# Clear corrupted caches
python workflows/cache_manager.py --clear-all

# Check cache health
python workflows/cache_manager.py --status
```

#### API Errors
```bash
# Check API key configuration
python -c "import os; print('OpenAI:', bool(os.getenv('OPENAI_API_KEY'))); print('Tavily:', bool(os.getenv('TAVILY_API_KEY')))"

# Test API connections
python scripts/test_agents.py
```

#### Email Processing Issues
```bash
# Validate email folder configuration
python -c "import os; print('Email folder:', os.getenv('INTERVIEW_FOLDER'))"

# Test email classification
python tests/test_agents/email_classifier/test_email_classifier.py
```

### **Debug Mode Execution**
```bash
# Run with verbose logging
LOGLEVEL=DEBUG python workflows/interview_prep_workflow.py

# Run with performance profiling
PROFILE=true python workflows/interview_prep_workflow.py
```

### **Performance Optimization**
```bash
# Monitor cache performance
python workflows/cache_manager.py --info

# Optimize caches
python workflows/cache_manager.py --optimize

# Clear expired cache entries
python workflows/cache_manager.py --clear-expired
```

---

## Production Deployment Tools

### **Deployment Scripts**
- **Location**: `scripts/deploy.sh`
- **Purpose**: Automated deployment setup
- **Features**: Environment validation, dependency installation, configuration setup

### **Database Migration**
- **Location**: `scripts/migrate_db.py`
- **Purpose**: Database schema migration and data updates

### **Environment Setup**
- **Location**: `scripts/setup_env.py` 
- **Purpose**: Production environment configuration and validation

---

## Integration with External Tools

### **VS Code Integration**
- **Tasks**: Pre-configured VS Code tasks for common workflows
- **Debug Configuration**: Launch configurations for debugging
- **Extensions**: Recommended extensions for Python development

### **Git Hooks**
- **Pre-commit**: Code formatting and linting
- **Pre-push**: Test execution and validation

### **CI/CD Integration**
- **GitHub Actions**: Automated testing and deployment
- **Docker**: Containerized deployment and scaling

This comprehensive development toolkit ensures efficient development, testing, and deployment of the Resume AI Agents Interview Prep Workflow system.

### **Entity Extraction Tools**

#### **Custom NER Model Training**
- **Location**: `agents/entity_extractor/train_ner.py`
- **Purpose**: Train custom spaCy models for interview-specific entity extraction
- **Usage**:
  ```bash
  python agents/entity_extractor/train_ner.py
  ```

#### **Model Testing & Validation**
- **Location**: `agents/entity_extractor/spacy_test.ipynb`
- **Purpose**: Interactive Jupyter notebook for testing NER model performance
- **Features**: Visual entity recognition display, performance metrics

### **Research & Intelligence Tools**

#### **Research Integration**
- **Location**: `api/run_tavily.py`
- **Purpose**: Web search and company intelligence gathering via Tavily API
- **Usage**:
  ```bash
  cd api && python run_tavily.py
  ```
- **Note**: Monitor API credits and rate limits for cost optimization

### **Memory & Storage Systems**

#### **Interview Store Management**
- **Location**: `agents/memory_systems/interview_store/`
- **Components**:
  - **InterviewStorage**: Store new interview data
  - **InterviewLookup**: Query existing records
  - **InterviewUpdater**: Update interview lifecycle status
- **Features**: Automatic deduplication, smart similarity matching

#### **SQLite Database Tools**
- **Purpose**: Persistent storage for interview history and research results
- **Schema**: Includes company, role, interviewer, dates, status, and similarity scores
- **Benefits**: Prevents redundant research, tracks interview preparation progress

### **Testing & Quality Assurance**

#### **Agent Testing Framework**
- **Location**: `tests/test_agents/`
- **Coverage**: Individual agent testing, integration testing, mock data validation
- **Usage**:
  ```bash
  # Run all tests
  pytest
  
  # Run specific agent tests
  pytest tests/test_agents/test_keyword_extractor.py
  ```

#### **Agent Testing Framework**
- **Location**: `tests/test_agents/`
- **Purpose**: Comprehensive testing suite for individual agent components
- **Components**:
  - **Email Classification Tests**: `email_classifier/` - Email classification validation
  - **Entity Extraction Tests**: `entity_extractor/` - Entity extraction validation
  - **Keyword Extraction Tests**: `keyword_extractor/` - Company name extraction tests
- **Features**:
  - Individual agent component testing
  - Integration testing with real email data
  - Performance validation and benchmarking
  - Mock data generation for development
- **Usage**:
  ```bash
  # Run all agent tests
  pytest tests/test_agents/ -v
  
  # Run specific agent tests
  pytest tests/test_agents/email_classifier/ -v
  pytest tests/test_agents/entity_extractor/ -v
  ```

### **OpenAI Caching System**

#### **OpenAI Cache Management**
- **Location**: `shared/openai_cache.py`
- **Purpose**: Reduce API costs and improve development speed with intelligent response caching
- **Features**:
  - File-based persistent caching with TTL (Time-To-Live)
  - Company-specific cache tracking for SEEDS and JUTEQ
  - Automatic cache expiration (default: 1 week)
  - Mock response generation when API key unavailable
  - Cache statistics and performance monitoring
- **Cache Directory**: `.openai_cache/` (auto-created, gitignored)
- **Usage**:
  ```python
  from shared.openai_cache import OpenAICache
  
  # Create cache instance
  cache = OpenAICache()
  
  # Check cache stats
  stats = cache.get_cache_stats()
  print(f"Cached companies: {stats['companies_cached']}")
  
  # Clear cache if needed
  cleared = cache.clear()
  ```
- **Benefits**:
  - Significant cost reduction during development
  - Faster response times for repeated queries
  - Offline development capability with mock responses
  - Company-specific cache organization

#### **Sample Data Management**
- **Location**: `tests/sample_data/`
- **Files**: `resumes.json`, `sample_emails.json`, `interview_invites.json`
- **Purpose**: Consistent test data for development and validation

### **UI Development Tools**

#### **Streamlit Dashboard**
- **Location**: `ui/app.py`
- **Launch**: `streamlit run ui/app.py`
- **Features**: Real-time pipeline monitoring, interactive agent control

#### **Custom UI Components**
- **Location**: `ui/testui/`
- **Files**: `testing.html`, `testingpy.py`
- **Purpose**: Advanced UI prototyping and custom component development

### **Configuration Management**

#### **Agent Configuration**
- **Location**: `configs/agent_configs.yaml`
- **Purpose**: Centralized agent settings and parameters

#### **Environment Setup**
- **Location**: `scripts/setup_env.py`
- **Purpose**: Automated environment configuration and dependency setup

#### **Deployment Configuration**
- **Files**: `dockerfile`, `docker-compose.yml`
- **Purpose**: Containerized deployment and development environment

## Best Practices

### **Development Workflow**
1. **Environment Setup**: Use virtual environments and requirements.txt
2. **Testing**: Run tests before committing changes
3. **API Limits**: Monitor token usage, especially during development
4. **Documentation**: Update docs when adding new tools or features

### **Development Guidelines**
1. **Multi-Agent Coordination**: Test individual components before integration
2. **Email Processing**: Validate email classification and entity extraction accuracy
3. **Memory Integration**: Ensure proper integration with interview store and deduplication
4. **Cache Management**: Leverage caching systems for development and testing
5. **Performance Monitoring**: Track processing metrics and API usage
6. **Error Handling**: Implement robust error recovery mechanisms

### **Debugging Tools**
- **Logging**: Comprehensive logging throughout the pipeline
- **Error Handling**: Robust error handling with retry mechanisms
- **State Inspection**: Workflow state visualization for debugging
- **Agent Tracing**: Individual agent component debugging and performance analysis

### **Performance Optimization**
- **Caching**: Research result caching to reduce API calls
- **OpenAI Caching**: Intelligent response caching with company-specific tracking
- **Async Processing**: Concurrent email and research processing
- **Memory Management**: Efficient database queries and memory usage
  - **Where:** Data manipulation in UI dashboards, CSV processing, metrics calculation
  - **Why:** Essential for data analysis and manipulation, particularly useful for processing interview statistics and generating insights
- **Mock Responses**: Fallback system for development without API keys
- **Cache-First Strategy**: Check cache before making expensive API calls

#### 🔗 Integrations & APIs
* ![Gmail API](https://img.shields.io/badge/Gmail_API-EA4335?style=flat-square&logo=gmail&logoColor=white) **Gmail API Integration**
  - **Where:** Email fetching (`shared/google_oauth/`), automated email processing, OAuth authentication
  - **Why:** Enables real-time email monitoring and processing, automatically detecting interview invitations without manual intervention

* ![Google OAuth](https://img.shields.io/badge/Google_OAuth-4285F4?style=flat-square&logo=google&logoColor=white) **Google OAuth 2.0**
  - **Where:** Authentication flow (`shared/google_oauth/google_apis_start.py`), token management
  - **Why:** Provides secure, industry-standard authentication for accessing user's Gmail data with proper permission scoping

* ![Tavily API](https://img.shields.io/badge/Tavily_API-FF6B6B?style=flat-square&logo=search&logoColor=white) **Tavily Search API**
  - **Where:** Company research (`api/run_tavily.py`), interviewer background checks, market intelligence
  - **Why:** Advanced AI-powered web search that provides structured, relevant information about companies and interviewers for interview preparation


#### 🗄️ Data & Storage
* ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white) **Pydantic Models**
  - **Where:** Data validation (`shared/models.py`), agent input/output schemas, configuration management
  - **Why:** Ensures type safety and data validation across all agent interactions, preventing runtime errors and maintaining data integrity

* ![JSON](https://img.shields.io/badge/JSON-000000?style=flat-square&logo=json&logoColor=white) **JSON Configuration**
  - **Where:** Configuration files (`configs/`), structured data exchange, test data (`tests/sample_data/`)
  - **Why:** Lightweight, human-readable format for configuration management and structured data storage

* ![Vector Store](https://img.shields.io/badge/Vector_Store-FF69B4?style=flat-square&logo=database&logoColor=white) **Vector Database**
  - **Where:** Semantic search (`shared/vector_store.py`), document embeddings, similarity matching
  - **Why:** Enables semantic search capabilities for finding similar emails and documents, powering intelligent deduplication and content recommendations

#### 🚀 DevOps & Deployment
* ![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white) **Docker Containerization**
  - **Where:** Application containerization (`dockerfile`), environment isolation, consistent deployments
  - **Why:** Ensures consistent runtime environment across development and production, simplifying deployment and dependency management

* ![Docker Compose](https://img.shields.io/badge/Docker_Compose-2496ED?style=flat-square&logo=docker&logoColor=white) **Docker Compose**
  - **Where:** Multi-container orchestration (`docker-compose.yml`), service coordination
  - **Why:** Manages complex multi-service applications with database, API, and UI components working together seamlessly

* ![pytest](https://img.shields.io/badge/pytest-0A9EDC?style=flat-square&logo=pytest&logoColor=white) **pytest Testing**
  - **Where:** Comprehensive test suite (`tests/`), agent testing, integration testing
  - **Why:** Ensures code reliability and agent functionality through automated testing, with special attention to API rate limits and token usage

<p align="right">(<a href="#readme-top">back to top</a>)</p>

