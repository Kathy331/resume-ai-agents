# Project Architecture

## Overview

**Project Name:** Resume AI Agents  
**Goal:** Modular AI system with specialized agents for job search automation, integrated through a central orchestrator, with Streamlit frontend and optional FastAPI backend (potentially, not yet as of Jul 22, 2025).

---

### **Key Components**

- **agents/**: Each subfolder is a specialized agent performing one task.
- **orchestrator/**: Combines agents into workflows for end-to-end automation.
- **shared/**: Common utilities, data models, LLM wrappers, database, and vector store integration.
- **api/**: FastAPI backend exposing agent and workflow endpoints. (potentially, not yet as of Jul 22, 2025).
- **ui/**: Streamlit frontend for interactive user workflows.
- **workflows/**: Predefined workflows combining multiple agents.
- **tests/**: Unit and integration tests.
- **configs/**: YAML configuration files for agents, prompts, and deployment.
- **scripts/**: Environment setup, DB migration, testing, and deployment scripts.

---

### **Folder Structure Highlights**

- **agents/**  
  Each agent has:
  - `agent.py`: main logic  
  - supporting modules (e.g. `scraper.py`, `parser.py`, `templates.py`)  
  - `config.py`: agent-specific configurations

- **orchestrator/**  
  Implements orchestrator pattern, defining workflows and agent execution logic.

- **shared/**  
  Contains:
  - `models.py`: Pydantic models for standardized input/output  
  - `llm_client.py`: wrapper for OpenAI or other LLMs  
  - `vector_store.py`: integration with ChromaDB, Pinecone, or Weaviate  
  - `database.py`: relational DB connections (e.g. SQLite, Postgres)

- **workflows/**  
  Defines reusable workflows such as:
  - Full job application automation  
  - LinkedIn → Email generation  
  - Resume optimization pipelines

- **ui/**  
  Streamlit app with:
  - `app.py`: main entry point  
  - `components/`: sidebar, file upload, results display  
  - `static/`: CSS and images

- **api/**  
  Optional FastAPI app with:
  - routes for agents, workflows, and health checks  
  - middleware and dependency injections

---

### **System Design**

1. **Single Responsibility Agents**  
   Each agent performs one isolated task with standardized input and output models (`AgentInput`, `AgentOutput`).

2. **Orchestrator Pattern**  
   Central orchestrator coordinates agents sequentially, conditionally, or in parallel, depending on workflow needs.

3. **Configuration Driven**  
   Agent behaviors are parameterized via YAML configs under `configs/`.

4. **Standard Interfaces**  
   All agents inherit from `BaseAgent` (check base_agent.py in agents folder), implementing:
   - `validate_input()`
   - `execute()`
   - optional `preprocess()` and `postprocess()`

---

### **Data Flow Example: Full Job Application Workflow**

User Input -> ResumeAnalyzerAgent -> LinkedInFinderAgent -> JobMatcherAgent
-> EmailWriterAgent -> Final Output (summary, recommendations, email draft)

### **Deployment**
- **Dockerized** via `Dockerfile` and `docker-compose.yml`.
- **Streamlit Frontend** runs with `streamlit run ui/app.py`.
- **FastAPI Backend** runs with `uvicorn api.main:app --reload`.
---
