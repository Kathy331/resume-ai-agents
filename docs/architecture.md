# Resume AI Agents - Architecture Documentation

## Overview

**Project Name:** Resume AI Agents  
**Goal:** Comprehensive AI-powered interview preparation system that processes interview invitation emails through specialized agents to generate personalized interview preparation guides with company research, interviewer insights, and role-specific guidance.

The system consists of **three core pipelines** that work together to provide comprehensive interview preparation:
1. **Email Pipeline** - Email classification, entity extraction, and memory management
2. **Deep Research Pipeline** - Multi-agent research using Tavily API for comprehensive data gathering
3. **Prep Guide Pipeline** - Personalized interview preparation guide generation with citations

---

## System Architecture Overview

## Components
- **Streamlit UI:**
  - Multi-tab dashboard for guide management, editing, and email sending
- **Workflow Orchestrator:**
  - Main entry: `workflows/interview_prep_workflow.py`
  - Handles email fetching, pipeline execution, output file generation
- **Email Pipeline:**
  - Classification, entity extraction, memory check
- **Deep Research Pipeline:**
  - Multi-agent research using Tavily API
  - RAG (Retrieval-Augmented Generation) for context enrichment
  - Citation manager for source tracking
- **Prep Guide Generator:**
  - Uses OpenAI GPT for personalized guide synthesis
  - Incorporates citations and research findings
- **Cache Manager:**
  - Handles OpenAI cache and output file cleanup


## Data Flow
1. Gmail API → Email Pipeline → Entity Extraction → Deep Research → Reflection → Prep Guide → Output Files → UI

## Output
- Guides saved to `outputs/fullworkflow/`
- HTML guides for UI/email in `outputs/ui/`

## Orchestration
- All agents are modular and can be extended
- Workflow is fully automated from email to guide

## Notes
- All cache and output cleanup is handled via UI and `cache_manager.py`
- All guides are citation-backed and validated

---

## Pipeline Breakdown

### 1. **Email Pipeline** 📧

**Purpose:** Process emails from the INTERVIEW_FOLDER, classify them, extract entities, and check memory store for previous processing.

**Key Components:**

- **Email Classifier Agent**: Determines if email is interview-related, personal, or other
- **Entity Extractor Agent**: Extracts company name, interviewer names, role details, and interview timing
- **Memory Systems**: Local interview store to prevent duplicate processing and maintain context
- **Keyword Extractor Agent**: Generates company-based filenames for organized output

**Data Flow:**
```
INTERVIEW_FOLDER Emails → Email Classification → Entity Extraction → Memory Check → Research Pipeline
```

**Input:** Raw email files from configured folder  
**Output:** Classified and structured interview data for research pipeline

---

### 2. **Deep Research Pipeline** 🔬

**Purpose:** Conduct comprehensive multi-agent research on company, role, and interviewer using Tavily API with intelligent caching.

**Key Components:**

- **Research Coordinator**: Manages parallel research calls and validates data quality
- **Company Research Agent**: Gathers company information, culture, recent news, and developments
- **Role Research Agent**: Analyzes job market trends, skill requirements, and role expectations
- **Interviewer Research Agent**: Researches interviewer backgrounds, LinkedIn profiles, and professional history
- **Tavily Cache Integration**: Caches research queries to optimize API usage and improve performance
- **Research Quality Reflection**: Validates research adequacy before proceeding to guide generation

**Data Flow:**
```
Entity Data → Research Coordination → Parallel API Calls → Cache Integration → Quality Validation → Prep Guide Pipeline
```

**Input:** Structured entity data from Email Pipeline  
**Output Categories:**
- **Company Strategy & Vision**: Strategic insights and forward-looking questions
- **Role-Specific & Technical**: Position-focused and technical competency questions
- **Behavioral & Cultural**: Culture fit and experience-based behavioral questions
- **Strategic & Forward-Looking**: Industry trends and future-oriented discussions

#### Advanced AI Techniques:
- **Chain-of-Thought Reasoning**: Structured analytical process for context comprehension
- **Few-Shot Prompting**: Consistent output structure across different interview contexts
- **Template-Based Generation**: Domain-specific question templates with dynamic customization
- **Multi-Agent Coordination**: Specialized task distribution for optimized performance

#### Processing Flow:
```
Research Context Input → Context Decomposer (CoT Analysis) → Question Generator (Multi-Domain) → 
Prep Summarizer (Package Assembly) → Strategic Interview Preparation Package
```

#### Integration Points:
- **Workflow Runner**: Primary orchestration through `deep_research_pipeline.py`
- **Research Engine**: Consumes multi-source company and role intelligence
- **Email Pipeline**: Triggered by interview invitation classification
- **Memory Systems**: Stores preparation packages and tracks interview outcomes

#### Performance Characteristics:
- Generates 12-16 strategic questions per interview context
- Context-aware question prioritization and strategic recommendation generation
- Quality assessment with relevance scoring and strategic value evaluation
---

### 3. **Prep Guide Pipeline** 📚

**Purpose:** Generate personalized interview preparation guides with role-specific technical prep, interviewer insights, and strategic questions.

**Key Components:**

- **Personalized Guide Generator**: Creates tailored preparation materials based on research data
- **Technical Prep Section**: Role-specific technical questions and competency areas
- **Interviewer Background Analysis**: Personal insights and professional background of interviewers
- **Strategic Questions Generator**: Personalized questions to ask the interviewer
- **Citation Engine**: Provides source references for all personalized conclusions
- **Output Organizer**: Stores individual guides in organized folder structure

**Data Flow:**
```
Research Data → Guide Generation → Technical Prep → Interviewer Insights → Strategic Questions → Cited Output
```

**Input:** Validated research data from Deep Research Pipeline  
**Output:** Complete interview preparation guide with citations stored in outputs/fullworkflow/[company_name].md
```
Resume Upload + Job Detail → Matching Analysis → Compatibility Score → 
Application Drafting → Human Review → Delivery + Follow-Up Tracking
```

**Unique Features:**
- **Adaptive Matching Logic**: Continuous scoring calibration
- **Cross-Profile Insights**: Leverages aggregated feedback from multiple candidates during matching
- **Dynamic Templates**: Learning-based email refinement loop

---


**Data Flow Example:**
```
Interview Email Detection → Entity Extraction → Research Aggregation → 
Research Coordination → Multi-Domain Analysis → 
Comprehensive Prep Package → User Delivery + Memory Storage
```

This pipeline represents the most advanced component of the system, utilizing cutting-edge AI techniques to provide personalized, strategic interview preparation that adapts to specific company cultures and role requirements.

---

## Integration Layer 🔗

### 🧠 Shared Memory Layer:

**Purpose:** Centralized state repository enabling context reuse between unrelated agent runs.

**Includes:**
- **User Preference Registry**: Stores accepted reply-thread styles, preferred persona settings, chain feedback encouragements
- **Interview History Logs**: Recursive events noting topics addressed previously alongside reflection markers or response tone drift tracking
- **Vector Cache Stack**: Pre-filled areas storing common expression patterns pulled from resolved historical outputs


### 🔄 Feedback Loop Controller:
**Purpose:** Retro-influences agent behavior, questions quality, and reinforcement criteria based on outcome markers gathered automagically.
**Feedback Metrics Tracked:**
- Reply success/neglect ratios within interpersonal dialog modules
- Performance scores tagged to items presented in interview matrices
- Proactive research accuracy level testing via attitude-embedded sample quoting tags
- Response rate increases and delays observed in consecutive rounds of scheduled messaging

---

## Core Technological Platforms & Design Principles

### Build Stack Highlights:
| Feature                       | Tool Used                  |
|------------------------------|----------------------------|
| Agent Orchestration          | LangGraph (Dynamic Decisions Using State) |
| Vector Searching             | Chroma / Pinecone / FAISS Libraries |
| LLM Integration              | OpenAI SDK / Anthropic API |
| NLP & Data Labeling          | spaCy (Name Entity Recognition) |
| Web Scraping & Analysis      | Tavily Advanced Summarization |
| Email I/O Management         | Gmail Unified Messaging Interface|
| Calendar Coordination        | Google & Microsoft Outlook SDK |


---

## Folder Layout Overview (Sample Directory Structure)

```
root/
├── agents/
│   ├── entity_extractor/
│   │   ├── agent.py
│   │   ├── patterns.py
│   │   └── train_ner.py
│   ├── keyword_extractor/
│   │   ├── agent.py
│   │   └── config.py
│   └── memory_systems/
│       ├── shared_memory.py
│       ├── interview_store/
│       └── resume_memory/
│
├── workflows/
│   ├── application_workflow.py
│   ├── interview_prep_flow.py
│   ├── email_agent_flow.py
│   └── deep_research_pipeline.py
│
├── shared/
│   ├── context_bridge.py
│   ├── feedback_system.py
│   ├── memory_store.py
│   └── research_integration.py
│
├── experiments/
│   └── persona_testing_suite.py
│
├── tests/
│   ├── test_agents/
│   │   ├── email_classifier/
│   │   ├── entity_extractor/
│   │   └── keyword_extractor/
│   ├── test_shared/
│   └── sample_data/
│
└── config/
    └── priority_options.yaml
```

Defined modularly where behaviors like tone norms, language preferences, and precomputed experimental rules remain centralized yet mutable without affecting system-wide resource operations.

---

## Example Use Cases
### 1. **Smart Interview Prep Sheet Making**
```
Received Interview Invitation Email via Inbox Monitor →
Pulled Through Orchestrator Agent Pipe (via Shared Context Stop Point) →
Parsed Subject Line & Embedded Calendar Elements for Entity Tags →
Checked Against Internal Archive First for Repetition Indicators →
If Fresh Request Collected, Be Ready Request Initiated to Company/Person/Role Analyses Schemes →
Extract Final Results Then Feed Into Tailored Question Builder System →
Create Custom Prep Card ->
Save to Output Directory with Citation References →
Send Notification to User via Streamlit UI or Email
```


---

## Future Enhancement Roadmap

| Area                             | Description                                           | ETA         |
|----------------------------------|-------------------------------------------------------|-------------|
| Auto Job Matching                | Machine Learning Model for Role Accuracy Matching     |  TBD  |
| Enhanced Persona Embedding       | Fine-tuned end-to-end aliased aliases per country/culture|  TBD |
| Full CRM Integration             | Connect LinkedIn Sales Navigator/Data unlock paths    |  TBD   |
| Analytics Dashboard Expansion    | Show performance scorecards with analytics visualizations| TBD |
| Voice-to-Text Module             | Interview practice spoken optimum extracting assist config| TBD       |

### 1. **Automated Cold Outreach Campaign**
```
User Resume Uploaded →
Resume-Analyzed by Agent v1 → 
Unapplied Job Listed →
Scoped Research Performed About Company → 
Personalized Intro Templates Added Automatically from LinkedIn Data → 
User Approves Drafts through UI Overlay →
Delivered by Calendarropriate Sending Time →
Post-viewing Trigger Starts Enrichment Updates Based on Response Percolation
```

### 2. **Advanced Deep Research Intelligence Processing**
```
Interview Context Detected →
Deep Research Pipeline Triggered via Workflow Runner →
Multi-Source Company Intelligence Gathered (Tavily API + Research Engine) →
Research Coordination Analyzes Multi-Domain Context →
Prep Guide Generator Creates Strategic Interview Guide →
Guide Assembly with Comprehensive Preparation Package →
Quality Assessment & Strategic Value Integration →
Final Package Delivered with Complete Interview Preparation →
Memory Storage for Future Reference & Feedback Integration
```