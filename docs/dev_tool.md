# Developer Tools & Environment

## Main Tools Used
- **Python 3.10+**
- **Streamlit** (UI dashboard)
- **OpenAI GPT** (text generation)
- **Tavily API** (web search)
- **Google Gmail API** (email fetching/sending)
- **Citation Manager** (source tracking)
- **pytest** (testing)
- **cache_manager.py** (cache and output cleanup)

## AI Concepts
- **Retrieval-Augmented Generation (RAG):**
  - Combines Tavily search results with LLM context
- **Memory Management:**
  - Caches and retrieves relevant information
- **Agent Orchestration:**
  - Custom pipeline for and sequential agent execution
- **Workflow Orchestration:**
  - Custom multi-stage pipeline with conditional routing based on research quality
- **Streamlit UI:**
  - Interactive dashboard for viewing and editing guides


## Folder Structure
- `ui/` - Streamlit UI and pages
- `workflows/` - Main workflow scripts
- `pipelines/` - Pipeline components (email, research, guide)
- `outputs/` - Generated guides and HTML files
- `shared/` - Gmail authentication and services
- `docs/` - Documentation and flowcharts

## Setup
- See `README.md` for full setup instructions
- Use `python setup_bot_email.py` for Gmail authentication
- Use UI cache button to clear cache and output files

## Testing
- Run `pytest` for all tests
- Individual tests in `tests/`

## Notes
- All agents and pipelines are modular and can be extended
- All guides are citation-backed and validated

