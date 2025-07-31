# Development Tools & Utilities

## Core Development Tools

### **Workflow Runner**
- **Location**: `agents/orchestrator/workflow_runner.py`
- **Purpose**: Main entry point for running the complete email processing pipeline
- **Usage**: 
  ```python
  from agents.orchestrator.workflow_runner import WorkflowRunner
  runner = WorkflowRunner()
  results = await runner.run_email_pipeline("INTERVIEW PREP")
  ```

### **Enhanced Email Pipeline**
- **Location**: `workflows/email_pipeline.py`
- **Purpose**: Advanced email processing with memory-based deduplication
- **Features**:
  - Intelligent similarity matching
  - Memory-driven research decisions
  - Lifecycle state management
  - Conditional processing based on interview history

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

#### **Tavily API Integration**
- **Location**: `api/run_tavily.py`
- **Purpose**: Web search and company intelligence gathering
- **Usage**:
  ```bash
  cd api && python run_tavily.py
  ```
- **Note**: Monitor API credits and rate limits

#### **Company Research Orchestrator**
- **Location**: `agents/research_engine/research_orchestrator.py`
- **Purpose**: Coordinates multiple research streams for comprehensive intelligence

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

### **Debugging Tools**
- **Logging**: Comprehensive logging throughout the pipeline
- **Error Handling**: Robust error handling with retry mechanisms
- **State Inspection**: LangGraph state visualization for workflow debugging

### **Performance Optimization**
- **Caching**: Research result caching to reduce API calls
- **Async Processing**: Concurrent email and research processing
- **Memory Management**: Efficient database queries and memory usage
  - **Where:** Data manipulation in UI dashboards, CSV processing, metrics calculation
  - **Why:** Essential for data analysis and manipulation, particularly useful for processing interview statistics and generating insights

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

