### Built With

#### 🧠 AI & Machine Learning
* ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white) **OpenAI GPT Models**
  - **Where:** Core LLM client (`shared/llm_client.py`), question generation, email writing, resume analysis
  - **Why:** Provides state-of-the-art natural language understanding and generation for creating personalized interview questions, analyzing resumes, and drafting professional emails

* ![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square&logo=langchain&logoColor=white) **LangGraph Orchestration**
  - **Where:** Email pipeline coordinator (`agents/orchestrator/langgraph_coordinator.py`), workflow management
  - **Why:** Enables sophisticated state-driven workflows with conditional routing, allowing the system to make intelligent decisions about email processing and agent coordination

* ![spaCy](https://img.shields.io/badge/spaCy-09A3D5?style=flat-square&logo=spacy&logoColor=white) **spaCy NLP**
  - **Where:** Entity extraction (`agents/entity_extractor/`), interview email parsing, custom NER training
  - **Why:** Extracts structured data (company names, dates, interviewer names) from unstructured email text with high accuracy and custom domain adaptation

* ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white) **scikit-learn**
  - **Where:** Text classification models, similarity scoring, evaluation metrics
  - **Why:** Provides robust machine learning utilities for email classification and performance evaluation of NLP models

* ![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white) **LangChain Framework**
  - **Where:** Agent base classes, prompt management, LLM abstraction layers
  - **Why:** Standardizes LLM interactions and provides a consistent framework for building modular AI agents

#### 🎛️ Frontend & Interface
* ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) **Streamlit Dashboard**
  - **Where:** Main UI (`ui/app.py`), dashboard pages (`ui/pages/`), interactive components
  - **Why:** Provides rapid prototyping for data-driven web applications with real-time updates, perfect for AI agent monitoring and user interaction

* ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white) **Plotly Visualizations**
  - **Where:** Dashboard analytics (`ui/pages/dashboard.py`), performance charts, timeline visualizations
  - **Why:** Creates interactive, publication-quality charts for visualizing interview preparation success rates, question quality metrics, and system performance

* ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) **Custom HTML Components**
  - **Where:** UI styling (`ui/testui/`), custom layouts, enhanced visual elements
  - **Why:** Enables advanced styling and layout control beyond Streamlit's default components for a professional user experience

#### 🔧 Backend & APIs
* ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) **FastAPI Framework**
  - **Where:** API endpoints (`api/main.py`), async request handling, RESTful services
  - **Why:** High-performance async web framework ideal for AI agent APIs, providing automatic documentation and type validation

* ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) **Python 3.10+**
  - **Where:** All agent implementations, workflow orchestration, data processing pipelines
  - **Why:** Excellent ecosystem for AI/ML development with async/await support for concurrent processing of multiple emails and research tasks

* ![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat-square&logo=sqlite&logoColor=white) **SQLite Database**
  - **Where:** Interview storage (`agents/memory_systems/interview_store/`), duplicate detection, lifecycle tracking
  - **Why:** Lightweight, serverless database perfect for storing interview history with built-in similarity matching to prevent redundant research

* ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) **Pandas Analysis**
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

* ![LinkedIn](https://img.shields.io/badge/LinkedIn_API-0077B5?style=flat-square&logo=linkedin&logoColor=white) **LinkedIn Integration**
  - **Where:** Professional profile discovery (`agents/linkedin_finder/`), networking analysis
  - **Why:** Finds hiring managers and key personnel for targeted outreach and networking opportunities

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

