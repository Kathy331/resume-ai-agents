# 🤖 Agent Specifications

## 🔧 **Base Agent**

| **Class** | BaseAgent |
|---|---|
| **File** | agents/base_agent.py |
| **Purpose** | Defines abstract methods `execute()` and `validate_input()` for all agents. |
| **Input** | `AgentInput` (data, metadata, previous agent output) |
| **Output** | `AgentOutput` (success flag, data, metadata, errors, next agent suggestions) |

---

## 🕵️‍♀️ **Agent 1: LinkedIn Finder**

| **Folder** | agents/linkedin_finder/ |
|---|---|
| **Purpose** | Finds LinkedIn profiles based on name and company. |
| **Components** | `agent.py`, `scraper.py`, `validator.py`, `config.py` |
| **Input** | name, company |
| **Output** | validated LinkedIn URL(s), confidence score |
| **Technologies** | Tavily API or direct scraping with BeautifulSoup/Selenium. |

---

## 📄 **Agent 2: Resume Analyzer**

| **Folder** | agents/resume_analyzer/ |
|---|---|
| **Purpose** | Parses resumes, extracts skills and experience. |
| **Components** | `agent.py`, `parser.py`, `skills_extractor.py`, `config.py` |
| **Input** | resume file |
| **Output** | structured JSON with skills, experiences, education, projects. |
| **Technologies** | NLP parsing, PDF/Docx parsing libraries. |

---

## 💼 **Agent 3: Job Matcher**

| **Folder** | agents/job_matcher/ |
|---|---|
| **Purpose** | Matches user resumes to job descriptions. |
| **Components** | `agent.py`, `job_scraper.py`, `similarity_engine.py`, `config.py` |
| **Input** | resume data, job description |
| **Output** | match score, missing skills, recommendations. |
| **Technologies** | Semantic similarity, embedding-based matching, Tavily for job data retrieval. |

---

## ✉️ **Agent 4: Email Writer**

| **Folder** | agents/email_writer/ |
|---|---|
| **Purpose** | Generates personalized follow-up or application emails. |
| **Components** | `agent.py`, `templates.py`, `personalization.py`, `config.py` |
| **Input** | recipient info, job info, user tone |
| **Output** | email draft text |
| **Technologies** | Prompt engineering, style transfer with LLMs. |

---

## 📅 **Agent 5: Calendar Manager**

| **Folder** | agents/calendar_manager/ |
|---|---|
| **Purpose** | Reads user calendar, extracts upcoming interviews, integrates scheduling data. |
| **Components** | `agent.py`, `google_integration.py`, `config.py` |
| **Input** | OAuth tokens, date ranges |
| **Output** | List of upcoming interview events with participants and times. |
| **Technologies** | Google Calendar API, OAuth2. |

---

## 🧠 **Agent 6: Orchestrator**

| **Folder** | agents/orchestrator/ |
|---|---|
| **Purpose** | Coordinates execution of multiple agents in workflows. |
| **Components** | `workflow_manager.py`, `data_pipeline.py`, `config.py` |
| **Input** | workflow name, initial input data |
| **Output** | aggregated results from all agents in the workflow. |
| **Technologies** | Async task execution, conditional logic, error handling. |

---

## 🌐 **Shared Utilities**

- **models.py**: Defines `AgentInput` and `AgentOutput` schemas.
- **llm_client.py**: Wraps OpenAI/Tavily calls.
- **vector_store.py**: Handles embeddings and semantic search.
- **utils.py**: Logging, formatting, generic helpers.

---

## ⚡ **Future Expansion**

✅ Add agents for:

- Interview question generation
- Salary benchmarking
- Company research

✅ Extend orchestrator for:

- Parallel agent execution
- Conditional workflows
- Retry and fallback strategies

---

### 📝 **Contribution Guidelines**

1. Extend `BaseAgent` for new agents.  
2. Write unit tests in `tests/unit/test_agents/`.  
3. Update `configs/agent_configs.yaml` for new agent settings.  
4. Document each agent in `agent_specs.md`.

---

*Maintained by: [Your Team or Organization]*

