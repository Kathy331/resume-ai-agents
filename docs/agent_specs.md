# Agent Specifications - Resume AI Agents

This document outlines the design and functionality of each agent in the Resume AI Agents Interview Prep Workflow system. All agents follow a consistent architecture and integrate seamlessly through the three-pipeline system.

---

## System Overview

The Resume AI Agents system consists of specialized agents organized into three core pipelines:

```
📧 Email Pipeline → 🔬 Deep Research Pipeline → 📚 Prep Guide Pipeline
```

Each agent serves a specific purpose in transforming interview invitation emails into comprehensive, personalized preparation guides.

---

## Base Agent Architecture

| **Class** | `BaseAgent` |
|----------|--------------|
| **File** | `agents/base_agent.py` |
| **Purpose** | Defines common interface and shared functionality for all agents |
| **Features** | Configuration management, error handling, logging integration |
| **Usage** | All agents inherit from this base class for consistency |

---

## Email Pipeline Agents 📧

### 1. Email Classifier Agent

| **Class**   | `EmailClassifierAgent`                 |
|-------------|----------------------------------------|
| **Location**  | `agents/email_classifier/agent.py`   |
| **Purpose** | Classifies emails into Interview, Personal, or Other categories for intelligent routing |
| **Input**   | Email content, subject, sender information |
| **Output**  | Classification result with confidence score |
| **Features** | Advanced pattern recognition, keyword matching, context analysis |
| **Terminal Output** | "📧 Email classified as: INTERVIEW/PERSONAL/OTHER" |

**Integration**: Main entry point for email processing - determines workflow routing

### 2. Entity Extractor Agent

| **Class**   | `EntityExtractorAgent`                |
|-------------|----------------------------------------|
| **Location**  | `agents/entity_extractor/agent.py`   |
| **Purpose** | Extracts structured information from interview emails |
| **Input**   | Raw interview email content |
| **Output**  | Structured entity data (company, interviewer, role, timing) |
| **Features** | NER models, custom patterns, date/time parsing |
| **Extracted Data** | 
- **Company Name**: Organization conducting interview
- **Interviewer Names**: All interviewing participants  
- **Role Details**: Position title, department, level
- **Interview Timing**: Date, time, duration, timezone
- **Interview Format**: Video, phone, in-person

**Integration**: Feeds structured data to both memory systems and research pipeline

### 3. Keyword Extractor Agent

| **Class**   | `KeywordExtractorAgent`               |
|-------------|----------------------------------------|
| **Location**  | `agents/keyword_extractor/agent.py`  |
| **Purpose** | Extracts company names for filename generation |
| **Input**   | Email content or entity data |
| **Output**  | Clean company name for file naming |
| **Features** | Company name normalization, special character handling |
| **Usage** | Generates `[company_name].md` filenames for individual outputs |

**Integration**: Used by output system to create organized file structure

---

## Memory System Agents 🧠

### 4. Interview Store Manager

| **Class**   | `InterviewStoreManager`               |
|-------------|----------------------------------------|
| **Location**  | `agents/memory_systems/interview_store/` |
| **Purpose** | Manages local storage of interview data and processing history |
| **Input**   | Entity data, processing status |
| **Output**  | Duplicate detection results, storage confirmation |
| **Features** | Duplicate prevention, processing history, status tracking |
| **Terminal Output** | "🧠 Already Prepped: [Company]" or "🧠 New Email: Processing [Company]" |

**Integration**: Prevents duplicate processing and maintains interview context

### 5. Shared Memory Agent

| **Class**   | `SharedMemoryAgent`                   |
|-------------|----------------------------------------|
| **Location**  | `agents/memory_systems/shared_memory.py` |
| **Purpose** | Facilitates data sharing between pipeline components |
| **Input**   | Cross-pipeline data requirements |
| **Output**  | Contextualized data for agent coordination |
| **Features** | Pipeline coordination, context bridging, data consistency |

**Integration**: Enables seamless data flow between Email, Research, and Prep Guide pipelines

---

## Deep Research Pipeline Agents 🔬

### 6. Research Coordinator Agent

| **Class**   | `ResearchCoordinatorAgent`            |
|-------------|----------------------------------------|
| **Location**  | `pipelines/deep_research_pipeline.py` |
| **Purpose** | Orchestrates parallel research execution and validates entity data |
| **Input**   | Entity data from Email Pipeline |
| **Output**  | Research coordination plan and validation results |
| **Features** | Parallel coordination, data validation, error handling |

**Integration**: Entry point for Deep Research Pipeline, manages all research agents

### 7. Company Research Agent

| **Class**   | `CompanyResearchAgent`                |
|-------------|----------------------------------------|
| **Location**  | `api/run_tavily.py` (integrated via API) |
| **Purpose** | Conducts comprehensive company research using Tavily API |
| **Input**   | Company name and context |
| **Output**  | Company information, culture, news, financial data |
| **Features** | Tavily API integration, cache optimization, source citation |
| **Research Areas** |
- Company mission, values, culture
- Recent news and developments  
- Financial performance and market position
- Industry reputation and competitive landscape
- Work environment and employee satisfaction

**Cache Integration**: All queries cached in `cache/tavily/` for optimization

### 8. Role Research Agent

| **Class**   | `RoleResearchAgent`                   |
|-------------|----------------------------------------|
| **Location**  | `api/run_tavily.py` (integrated via API) |
| **Purpose** | Analyzes role-specific information and market trends |
| **Input**   | Role title, company context |
| **Output**  | Role requirements, market trends, skill analysis |
| **Features** | Market analysis, skill mapping, salary benchmarking |
| **Research Areas** |
- Job market trends and demand
- Required technical and soft skills
- Salary benchmarks and compensation
- Career progression opportunities
- Daily responsibilities and challenges

**Cache Integration**: Role queries cached with company context for reuse

### 9. Interviewer Research Agent

| **Class**   | `InterviewerResearchAgent`            |
|-------------|----------------------------------------|
| **Location**  | `api/run_tavily.py` (integrated via API) |
| **Purpose** | Researches interviewer backgrounds and professional history |
| **Input**   | Interviewer names, company context |
| **Output**  | Professional backgrounds, expertise areas, career insights |
| **Features** | LinkedIn analysis, publication research, network mapping |
| **Research Areas** |
- LinkedIn profiles and professional background
- Career trajectory and achievements
- Technical specializations and expertise
- Publications, articles, and thought leadership
- Professional networks and affiliations

**Cache Integration**: Interviewer queries cached with professional context

### 10. Research Quality Validator

| **Class**   | `ResearchQualityValidator`            |
|-------------|----------------------------------------|
| **Location**  | `pipelines/deep_research_pipeline.py` |
| **Purpose** | Validates research adequacy and triggers additional research loops |
| **Input**   | Aggregated research data from all agents |
| **Output**  | Quality assessment and adequacy decision |
| **Features** | Completeness checking, source validation, adequacy scoring |
| **Quality Checks** |
- Information completeness verification
- Source reliability assessment  
- Data freshness validation
- Coverage depth analysis

**Integration**: Determines whether to proceed to Prep Guide Pipeline or trigger additional research

---

## Prep Guide Pipeline Agents 📚

### 11. Personalized Guide Generator

| **Class**   | `PersonalizedGuideGenerator`          |
|-------------|----------------------------------------|
| **Location**  | `pipelines/prep_guide_pipeline.py`   |
| **Purpose** | Creates comprehensive interview preparation guides |
| **Input**   | Validated research data from Deep Research Pipeline |
| **Output**  | Complete preparation guide with all sections |
| **Features** | OpenAI integration, template customization, personalization |

**Cache Integration**: Uses OpenAI cache (`.openai_cache/`) for cost optimization

### 12. Technical Prep Generator

| **Class**   | `TechnicalPrepGenerator`              |
|-------------|----------------------------------------|
| **Location**  | `pipelines/prep_guide_pipeline.py`   |
| **Purpose** | Generates role-specific technical preparation content |
| **Input**   | Role research data, skill requirements |
| **Output**  | Technical competencies, sample questions, preparation resources |
| **Features** | Role-based customization, skill mapping, difficulty adjustment |

### 13. Interviewer Insights Generator

| **Class**   | `InterviewerInsightsGenerator`        |
|-------------|----------------------------------------|
| **Location**  | `pipelines/prep_guide_pipeline.py`   |
| **Purpose** | Generates personalized interviewer background analysis |
| **Input**   | Interviewer research data, professional profiles |
| **Output**  | Background insights, expertise areas, conversation topics |
| **Features** | Professional analysis, connection finding, communication insights |

### 14. Strategic Questions Generator

| **Class**   | `StrategicQuestionsGenerator`         |
|-------------|----------------------------------------|
| **Location**  | `pipelines/prep_guide_pipeline.py`   |
| **Purpose** | Creates personalized questions to ask the interviewer |
| **Input**   | All research data, role context, interviewer background |
| **Output**  | Categorized strategic questions tailored to context |
| **Features** | Context-aware generation, personalization, strategic focus |
| **Question Categories** |
- Role-specific inquiries
- Company direction questions
- Team dynamics and collaboration
- Personal development opportunities

### 15. Citation Engine

| **Class**   | `CitationEngine`                      |
|-------------|----------------------------------------|
| **Location**  | `pipelines/prep_guide_pipeline.py`   |
| **Purpose** | Integrates source references throughout preparation guides |
| **Input**   | All research data with source information |
| **Output**  | Properly cited content with reference tracking |
| **Features** | Source attribution, credibility validation, reference formatting |

**Integration**: Ensures all personalized conclusions are backed by research sources

---

## Agent Integration Flow

### Sequential Pipeline Processing

```
📧 Email Classifier → 🎯 Entity Extractor → 🧠 Memory Check
                                              ↓
📚 Prep Guide Pipeline ← 🤔 Quality Validator ← 🔬 Research Coordinator
                                              ↓
                        🏢 Company Research + 👤 Interviewer Research + 💼 Role Research
```

### Inter-Agent Communication

- **Structured Data**: Agents communicate through well-defined data models
- **Pipeline Context**: Shared context maintained throughout processing
- **Error Handling**: Graceful degradation and recovery mechanisms
- **Cache Coordination**: Intelligent caching across research agents

### Agent Lifecycle

1. **Initialization**: Load configuration and establish connections
2. **Input Validation**: Verify input data structure and content
3. **Processing**: Execute core agent functionality
4. **Output Generation**: Structure results for next pipeline stage
5. **Cache Management**: Update relevant caches for optimization
6. **Status Reporting**: Provide terminal feedback and logging

---

## Development & Testing

### Agent Testing Structure

```
tests/test_agents/
├── email_classifier/        # Email classification tests
├── entity_extractor/        # Entity extraction validation
├── keyword_extractor/       # Company name extraction tests
└── research_engine/         # Research agent integration tests
```

### Performance Metrics

- **Processing Speed**: Individual agent execution times
- **Accuracy**: Output quality and correctness validation
- **Cache Performance**: Hit rates and optimization effectiveness
- **Integration Success**: Pipeline coordination and data flow

### Configuration Management

All agents support configuration through:
- Environment variables (`.env`)
---

## Current Implementation

The system currently implements **3 core agents** with **2 memory systems** for the Interview Prep Workflow:

### **Core Agents** (Email Pipeline)
1. **Email Classifier Agent** - `agents/email_classifier/agent.py`
2. **Entity Extractor Agent** - `agents/entity_extractor/agent.py` 
3. **Keyword Extractor Agent** - `agents/keyword_extractor/agent.py`

### **Memory Systems**
4. **Interview Store System** - `agents/memory_systems/interview_store/`
5. **Resume Memory System** - `agents/memory_systems/resume_memory/`

### **Integrated Research & Guide Generation**
- **Research Integration**: Tavily API via `api/run_tavily.py`
- **Guide Generation**: OpenAI API via `shared/openai_cache.py`
- **Workflow Coordination**: `workflows/interview_prep_workflow.py`

---

## Shared Components

- `shared/models.py` – Unified dataclasses for inputs/outputs  
- `shared/llm_client.py` – OpenAI API client abstraction
- `shared/openai_cache.py` – Response caching and cost optimization
- `shared/tavily_client.py` – Web search and research integration
- `shared/utils.py` – Logging, formatting, and utility functions
- `agents/base_agent.py` – Base class for all agent implementations

---

## Development Notes

**To add a new agent:**
1. Inherit from `BaseAgent` in `agents/base_agent.py`
2. Create agent folder under `agents/` with descriptive name
3. Add tests under `tests/test_agents/[agent_name]/`
4. Update configuration in `configs/agent_configs.yaml`
5. Update this documentation

**Current System Focus:**
- Email processing and entity extraction
- Memory management and deduplication  
- Research integration via APIs
- Interview guide generation

---

**Maintained by:** Kathy Chen 
**Last Updated:** August 2025
