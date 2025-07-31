# Agent Specifications

This document outlines the design and functionality of each agent in the system. All agents inherit from a common `BaseAgent` class and follow a consistent I/O schema using `AgentInput` and `AgentOutput` models.

---

## Base Agent (Abstract)

| **Class** | `BaseAgent` |
|----------|--------------|
| **File** | `agents/base_agent.py` |
| **Purpose** | Defines interface for all agents. Enforces `execute()` and `validate_input()` methods. |
| **Input** | `AgentInput` — structured input including data, metadata, and previous outputs |
| **Output** | `AgentOutput` — structured output including data, status flags, metadata, and next-agent hints |

---
## Tier 0: Experimental Agent

### Keyword Extractor Agent

| **Class**   | `KeywordExtractorAgent`               |
|-------------|----------------------------------------|
| **Folder**  | `agents/keyword_extractor/`           |
| **Purpose** | Extracts keywords from raw text using an LLM. Used for initial Tavily prompt tuning. |
| **Input**   | Text string (`data["text"]`)          |
| **Output**  | Extracted keywords as a string list or comma-separated string |
| **Tech**    | Prompt-engineered OpenAI LLM (via `call_llm` wrapper) |

---

## Tier 1: Input Classification & Routing

### Email Classifier Agent

| **Class**   | `EmailClassifierAgent`                 |
|-------------|----------------------------------------|
| **Folder**  | `agents/email_classifier/`            |
| **Purpose** | Classifies emails into categories: interview invites, personal emails, and others. Supports intelligent routing. |
| **Input**   | List of email dictionaries with id, subject, body, from, to fields. Optional user_email for personal classification. |
| **Output**  | Dictionary with 'interview', 'personal', 'other' keys containing email IDs for each category |
| **Tech**    | Keyword-based classification with comprehensive interview-related pattern matching |
| **Features** | 
- **Multi-category Classification**: Automatically categorizes emails into Interview, Personal, and Other buckets
- **Personal Email Detection**: Identifies emails sent by the user when user_email is provided  
- **Interview Detection**: Advanced pattern recognition for various interview-related keywords and phrases
- **Production Ready**: Fully integrated into the email processing pipeline with fallback support

**Integration Status**: ✅ **ACTIVE** - Replaces previous temporary email classification rules. Used by:
- `workflows/email_pipeline.py` - Main email processing pipeline
- `agents/orchestrator/langgraph_coordinator.py` - LangGraph workflow coordinator  
- `agents/orchestrator/workflow_runner.py` - Workflow execution engine

### Job Matcher Agent

- **Folder:** `agents/job_matcher/`  
- **Purpose:** Matches job descriptions with user profiles and resumes using semantic similarity.  
- **Components:** `agent.py`, `similarity_engine.py`, `job_scraper.py`, `config.py`  
- **Input:** Job descriptions, resume data, user preferences  
- **Output:** Compatibility scores, skill gap analysis, match recommendations  
- **Technologies:** Semantic similarity algorithms, job data scraping, skill mapping, ML-based matching  
- **Key Features:**
  - **Semantic Matching**: Advanced similarity scoring beyond keyword matching
  - **Skill Gap Analysis**: Identifies missing skills and development opportunities
  - **Job Scraping**: Automated job description collection and parsing
  - **Preference Learning**: Adapts to user feedback and preferences  

---

## Tier 2: Entity & Metadata Extraction

### Entity Extractor Agent

- **Folder:** `agents/entity_extractor/`  
- **Purpose:** Extracts structured metadata such as names, dates, roles from unstructured email text using advanced NLP techniques.  
- **Components:** `agent.py`, `patterns.py`, `train_ner.py`, `use_model.py`, `spacy_test.ipynb`, `invitation_email_ner_model/`  
- **Input:** Raw email text  
- **Output:** Structured entities (company, role, interviewer, candidate, date, location, duration) in JSON format  
- **Technologies:** Custom spaCy NER model, pattern matching, fine-tuned entity recognition, spaCy matcher patterns
- **Key Features:** 
  - Custom trained NER model for interview-specific entities
  - Advanced pattern matching for email parsing
  - Jupyter notebook for model testing and validation
  - Production-ready model artifacts in `invitation_email_ner_model/`  

---

## Tier 3: Research Intelligence

### Company Researcher

- **File:** `agents/research_engine/company_researcher.py`  
- **Purpose:** Gathers comprehensive insights about target companies using AI-powered web search.  
- **Components:** `company_researcher.py`, `research_orchestrator.py`, `config.py`  
- **Input:** Company name from extracted entities  
- **Output:** Company overview, recent news, culture insights, funding status, strategic direction  
- **Technologies:** Tavily AI API, prompt-based summarization, structured data extraction  

### Interviewer Researcher

- **File:** `agents/research_engine/interviewer_researcher.py`  
- **Purpose:** Researches professional background and context for interview personalization.  
- **Input:** Interviewer name, company context  
- **Output:** Professional background, role details, potential conversation starters  
- **Technologies:** Tavily AI search, LinkedIn intelligence, professional network analysis  

### Role Researcher

- **File:** `agents/research_engine/role_researcher.py`  
- **Purpose:** Analyzes job roles and industry trends for interview preparation.  
- **Input:** Role title and company context  
- **Output:** Role expectations, skill requirements, industry benchmarks, career progression paths  
- **Technologies:** Market intelligence APIs, trend analysis, structured role profiling  

---

## Tier 4: Question Generation

### Question Generator Suite

- **Folder:** `agents/question_generation/`  
- **Purpose:** Generates high-quality interview questions across categories.  
- **Components:** `company_questions.py`, `role_questions.py`, `interviewer_questions.py`, `general_questions.py`, `question_orchestrator.py`  
- **Input:** Research context (company/role/person)  
- **Output:** Questions grouped by category and topic  
- **Technologies:** LLM prompting, template-based tuning, STAR mapping  

---

## Tier 4.5: Memory & Intelligence Systems

### Interview Store System

- **Folder:** `agents/memory_systems/interview_store/`  
- **Purpose:** Intelligent storage and retrieval of interview data with deduplication capabilities.  
- **Components:** Multiple specialized storage and lookup agents  
- **Key Features:**
  - **InterviewStorage**: Stores new interview data with automatic deduplication
  - **InterviewLookup**: Retrieves and searches existing interview records
  - **InterviewUpdater**: Updates interview lifecycle status (preparing → prepped → completed)
  - **Smart Deduplication**: Prevents redundant research using similarity matching
- **Technologies:** SQLite database, similarity algorithms, lifecycle state management  

### Shared Memory Layer

- **File:** `agents/memory_systems/shared_memory.py`  
- **Purpose:** Cross-agent context sharing and data persistence.  
- **Input:** Agent outputs, research data, user preferences  
- **Output:** Contextual memory for intelligent agent coordination  
- **Technologies:** In-memory caching, persistent storage, context bridging  

---

## Tier 5: Resume Processing

### Resume Analyzer

- **Folder:** `agents/resume_analyzer/`  
- **Purpose:** Extracts and analyzes structured data from resume documents.  
- **Components:** `agent.py`, `parser.py`, `skills_extractor.py`, `config.py`  
- **Input:** PDF, DOCX, or plain text resume documents  
- **Output:** Structured JSON with skills, experience timeline, education, projects  
- **Technologies:** Document parsing libraries, NLP extraction, skill taxonomy mapping  
- **Key Features:**
  - Multi-format document support
  - Advanced skills extraction and categorization
  - Experience timeline construction
  - Integration with job matching algorithms

### Behavioral Prep Agent

- **File:** `behavioral_prep.py` (planned)  
- **Purpose:** Generates STAR-format answers from resume highlights  
- **Input:** Experience entries from resume analysis  
- **Output:** Structured behavioral interview responses (Situation → Task → Action → Result)  
- **Tech:** LLM-based summarization, reflection agent  

---

## Tier 6: Email Interaction

### Email Writer Agent

- **Folder:** `agents/email_writer/`  
- **Purpose:** Crafts personalized outreach and follow-up emails with intelligent tone matching.  
- **Components:** `agent.py`, `templates.py`, `personalization.py`, `config.py`  
- **Input:** Target information, email type, style preferences, research context  
- **Output:** Personalized email drafts with appropriate tone and content  
- **Technologies:** Advanced prompt engineering, template management, personalization algorithms, tone analysis  
- **Key Features:**
  - **Template System**: Flexible email templates for different scenarios
  - **Personalization Engine**: Context-aware content adaptation
  - **Tone Matching**: Adapts writing style to user preferences
  - **Research Integration**: Incorporates company and role research for relevance  

---

## Tier 7: Scheduling & Integration

### Calendar Manager Agent

- **Folder:** `agents/calendar_manager/`  
- **Purpose:** Retrieves upcoming interviews from user calendar.  
- **Components:** `agent.py`, `google_integration.py`, `config.py`  
- **Input:** OAuth tokens, time range  
- **Output:** Calendar events  
- **Tech:** Google Calendar API  

---

## Tier 8: Orchestration & Pipelines

### Orchestrator System

- **Folder:** `agents/orchestrator/`  
- **Purpose:** Coordinates complex multi-agent workflows using advanced state management and conditional routing.  
- **Components:** `workflow_runner.py`, `langgraph_coordinator.py`  
- **Input:** Workflow trigger, email data, state context  
- **Output:** Coordinated pipeline results with intelligent routing decisions  
- **Technologies:** LangGraph state machines, async workflow coordination, conditional routing logic  
- **Key Features:**
  - **LangGraph Integration**: Advanced state-driven workflow orchestration
  - **Conditional Routing**: Intelligent decision-making based on email classification and memory state
  - **State Management**: Persistent workflow state across complex multi-step processes
  - **Error Handling**: Robust retry logic and fallback mechanisms
  - **Memory Integration**: Leverages interview memory for intelligent processing decisions  

---

## Shared Components

- `shared/models.py` – Unified dataclasses for inputs/outputs  
- `shared/llm_client.py` – Abstraction for OpenAI, Anthropic, or local LLMs  
- `shared/vector_store.py` – Vector indexing and retrieval logic  
- `shared/file_processors/` – File parsing for PDFs, DOCX, Notion  
- `shared/utils.py` – Logging, formatting, JSON utils  
- `shared/exceptions.py` – Agent error types and tracing  

---

## Future Agent Plans

| **Agent Type**          | **Purpose**                                      | **Status**      |
|-------------------------|--------------------------------------------------|-----------------|
| Interview Feedback       | Analyze responses and recommend improvements     | Planned         |
| Salary Benchmarking      | Estimate compensation for roles                  | In progress     |
| Cross-Agent Reflection   | Allow feedback loop to influence agent logic     | Prototyped      |

---

## Contribution Guidelines

To add or update an agent:

1. Inherit from `BaseAgent` and implement `execute()` + `validate_input()`  
2. Place code in a new folder under `agents/` with a descriptive name  
3. Add unit tests under `tests/unit/` and integration tests if needed  
4. Register agent in `configs/agent_configs.yaml` if applicable  
5. Update this file (`agent_specs.md`) with a new entry  
6. Run `pre-commit` and ensure all linter/tests pass  

> **Naming Conventions:** Use `snake_case` for filenames, `PascalCase` for classes, and keep methods self-contained for portability.

---

**Maintained by:** Kathy Chen  
**Last Updated:** July 2025
