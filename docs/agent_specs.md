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

- **Folder:** `agents/email_classifier/`  
- **Purpose:** Classifies emails into categories like interview invites, personal, spam, etc.  
- **Components:** `agent.py`, `ner.py`, `sentiment.py`, `config.py`  
- **Input:** Email text  
- **Output:** Category label, intent confidence, optional next-action  
- **Technologies:** Rule-based filters + LLM/NLP classification  

---

## Tier 2: Entity & Metadata Extraction

### Entity Extractor Agent

- **Folder:** `agents/entity_extractor/`  
- **Purpose:** Extracts structured metadata such as names, dates, roles from unstructured text.  
- **Components:** `agent.py`, `regex_parser.py`, `interview_parser.py`  
- **Input:** Raw text  
- **Output:** Entities (company, role, interviewer, etc.) in JSON  
- **Technologies:** Regex, spaCy NER, keyword heuristics  

---

## Tier 3: Research Intelligence

### Company Researcher

- **Folder:** `agents/research_engine/`  
- **Purpose:** Gathers insights about a target company.  
- **Components:** `company_researcher.py`, `tavily_client.py`, `config.py`  
- **Input:** Company name  
- **Output:** Summary insights, risks, culture, funding, etc.  
- **Technologies:** Tavily API, scraping, prompt-based summarization  

### Interviewer Researcher

- **File:** `interviewer_researcher.py`  
- **Purpose:** Fetches professional background for interviewers.  
- **Input:** Name, company  
- **Output:** Role, background summary, shared connections  
- **Tech:** LinkedIn search (via Tavily or RAG)  

### Role Researcher

- **File:** `role_researcher.py`  
- **Purpose:** Gathers information about a job role (market trends, typical skills).  
- **Input:** Role title  
- **Output:** Role expectations, career path, automation risk  
- **Tech:** Prompt-based search synthesis  

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

## Tier 5: Resume Processing

### Resume Analyzer

- **Folder:** `agents/resume_processing/`  
- **Purpose:** Extracts structured data (skills, timelines) from resume files.  
- **Components:** `resume_extractor.py`, `resume_parser.py`, `skills_tracker.py`, `config.py`  
- **Input:** PDF, DOCX, Notion, or plain text  
- **Output:** JSON: Skills, timeline, projects, degrees  
- **Technologies:** PDFMiner, python-docx, spaCy, custom taggers  

### Behavioral Prep Agent

- **File:** `behavioral_prep.py`  
- **Purpose:** Generates STAR-format answers from resume highlights  
- **Input:** Experience entry  
- **Output:** Situation → Task → Action → Result breakdown  
- **Tech:** LLM-based summarization, reflection agent  

---

## Tier 6: Email Interaction

### Email Writer Agent

- **Folder:** `agents/email_sender/`  
- **Purpose:** Crafts personalized outreach/follow-up emails.  
- **Components:** `agent.py`, `template_manager.py`, `feedback.py`  
- **Input:** Target info, email type, style preferences  
- **Output:** Email draft  
- **Tech:** Prompt tuning, RAG, templates, tone mirroring  

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
- **Purpose:** Coordinates agent workflows via routing and state management.  
- **Components:** `router.py`, `workflow_runner.py`, `langgraph_coordinator.py`, `pipeline_manager.py`  
- **Input:** Workflow name, input context  
- **Output:** Aggregated pipeline output  
- **Tech:** LangGraph, async runners, fallback logic, memory connectors  

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
