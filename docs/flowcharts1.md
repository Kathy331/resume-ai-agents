# Interview Prep Workflow - System Flowchart

## High-Level Workflow

1. **Email Fetching & Classification**
   - Fetch emails from Gmail using Google API
   - Classify emails (interview invite, other)

2. **Entity Extraction & Memory Check**
   - Extract entities (company, interviewer, date, etc.)
   - Check memory store for duplicate interviews

3. **Deep Research Pipeline**
   - Multi-agent research using Tavily API
   - Company, interviewer, and role analysis
   - Citation manager collects sources
   - RAG (Retrieval-Augmented Generation) for context enrichment

4. **Research Quality Reflection**
   - Assess research quality/confidence
   - Reflection loop for gap analysis

5. **Prep Guide Generation**
   - Generate personalized prep guide using OpenAI (GPT)
   - Incorporate citations and research findings
   - Output markdown and HTML files per company

6. **UI Integration**
   - Streamlit dashboard loads guides from output folder
   - Tabs for each company, editing, email sending

---

## AI Concepts Used
- **Retrieval-Augmented Generation (RAG):**
  - Combines search results (Tavily) with LLM (OpenAI) for richer context
- **OpenAI GPT:**
  - Used for text generation and guide synthesis
- **Tavily API:**
  - Used for web search and company/interviewer research
- **Citation Manager:**
  - Tracks sources and validates research
- **chains and Workflow Orchestration** 
  - currently, the system did not use LangChain, but we use custom orchestration instead
  - Multi-stage pipeline: Email → Entity Extraction → Research → Reflection → Guide Generation
  - Sequential agent execution with data passing between stages 
  - Conditional routing based on research quality assessment (for ex, if research is insufficient, it can trigger a re-run of the research stage)

---

## Agent Orchestration
- **Email Pipeline Agent:**
  - Classification, entity extraction, memory check
- **Company Analysis Agent:**
  - Validates company identity, gathers market info
- **Interviewer Analysis Agent:**
  - Finds LinkedIn profiles, background research
- **Prep Guide Agent:**
  - Synthesizes all data into a personalized guide

---

## Data Flow
1. Gmail → Email Pipeline → Entity Extraction → Deep Research → Reflection → Prep Guide → Output Files → UI

---

## Output Files
- `outputs/fullworkflow/COMPANY.txt` (raw guide)
- `outputs/ui/COMPANY_prep_guide.html` (styled for UI/email)

---

## Diagram
```
[Gmail API] → [Email Pipeline] → [Entity Extraction] → [Deep Research (Tavily)] → [Citation Manager] → [Reflection] → [Prep Guide Generation (OpenAI)] → [Output Files] → [Streamlit UI]
```

---

## Notes
- All cache management is handled via `cache_manager.py` and UI cache button
- All guides are generated per company and can be sent via Gmail API
- All research is citation-backed and validated
