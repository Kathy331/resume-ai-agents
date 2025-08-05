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

The system follows a **sequential pipeline architecture** with the Interview Prep Workflow as the main entry point:

```
� Interview Prep Workflow Entry Point
          ↓
📬 Email Classification (Interview vs Personal vs Other)
          ↓ (if Interview Email)
🔍 Entity Extraction + Memory Check (Company, Role, Interviewer)
          ↓ (if Not Already Processed)
🔬 Deep Research Pipeline (Parallel Multi-agent Research)
          ↓
🤔 Research Quality Reflection (Adequacy Check)
          ↓
📚 Prep Guide Pipeline (Personalized Guide Generation)
          ↓
📁 Individual Output Storage (outputs/fullworkflow/[company_name].md)
```

Each email is processed individually through the complete pipeline, ensuring personalized and focused preparation materials.

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
**Output:** Comprehensive research data with citations for prep guide generation

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

### 2. **Resume Processing Pipeline** 📄

**Purpose:** Extract meaningful career insights from any document format into actionable structured data.

**Key Components:**

- **Resume Uploader**: Supports PDF, DOCX, Notion imports
- **NER-Based Parser**: Temporal hierarchy extraction + concept tagging
- **Semantic Matching Engine**: Aligns resume experiences with job schema templates
- **Experience Timeline Builder**: Constructs time-framed summaries for reference in outbound messages or self-assessment answers

**Data Flow:**
```
Document Parsing → NER Processing → Structured Database Entry → Knowledge Management Portal
```

**Key Outputs:**
- Career timeline timelines as JSON documents
- Skills indexed in searchable formats (topic clusters or vectors)
- Experience details primed for alignment with role expectations

This pipeline is foundational in enabling smart interview prep generation and application targeting decisions.

---

### 3. **Email AI Agent Pipeline** 📧

**Purpose:** Classify and respond intelligently to inbound communication based on intent and sender context.

**Core Components:**

#### Trigger Mechanism:
- Gmail API polling or label watching (e.g., "InterviewPrep")
- Real-time inbox sync or background scanning

#### Core Logic Nodes:
- **Orchestrator**: LangGraph-powered coordinator routing classified emails
- **EmailClassifierAgent**: 
  - **Production-ready** intelligent email classification
  - **Interview Detection**: Advanced pattern matching for interview invitations, scheduling, confirmations
  - **Personal Email Recognition**: Identifies user-sent emails when user_email provided
  - **Fallback Support**: Graceful degradation to rule-based classification if agent fails
  - **Integration**: Fully integrated into `workflows/email_pipeline.py` and orchestration layer

#### Personalization Layers:
- **Vector Store Ingest**: Analyzes user writing style and thematic elements
- **RAG-based Writer Agent**: Generates tonally aligned replies drawing on templates and LLM creativity
- **Reflection System**: Self-modification after feedback triggers or manual adjustments

**Process Example:**
```
Inbox Signal → Gmail Fetch → Classification Module → 
Routing to Respective Agent (Interview Helper / Response Engine) → 
Auto-replies / Prep Package Saved Locally
```

Premise is minimal friction in user interaction while maximizing contextual fidelity in auto-generated replies.

---

### 4. **Research Engine & Question Generator Suite** 🔬 ❓

**Purpose:** Aggregate company, role, and person-specific intelligence across web sources to generate personalized interview recommendations and proactive prep strategies.

#### Research Streams:
- **Company**: Recent news, leadership statements, financials, culture trends
- **Interviewer**: Background checks via social media, publications, and past company pivots
- **Role**: Industry benchmarks, core skills, automation risk profile, scope updates

#### Multi-Domain Question Creation Framework:
1. **Star-Specific Behaviors**: Mapped directly from extracted experiences
2. **Strategic Inquiry Themes**:
   - Financial outlook, DEI status, product roadmap issues (company-related)
   - Background-related probes, advanced-topic dialogs (person-level)
   - Future growth discussions, performance measure queries (position-focused)

**Aggregation Node:**
- Combines all sources of study into one-manual digest for last-minute preview and execution planning
    
**Output Example**: 
```json
{
  "company_name": "AcmeCorp",
  "research_date": "...",
  "topics": [
    { "insight": "Secured funding to expand AI unit" },
    { "talking_point": "How does your focus in algorithms relate?" }
  ],
  ...other blocks...
}
```

Supports not only preparation but also situational awareness for accurate, confident responses.

---

### 5. **Interview Processing Flow** 🎯

**Purpose:** Scanner + Templater fusion to initialize factual capture from email invites and integrate outcome prompts post-conversation.

#### Pipeline Stages:

1. **Entity Extraction Node**: Uses hybrid extraction and OCR methods to pull:

   - Company name
   - All interviewer names
   - Title reference
   - Slot times (to sync with calendar integrations)
   
   Processes both explicit request text and referenced documents if attached directly.

2. **Post-duplication Filtering**:
   Polls local database for existing entries where hashed identifiers match prior communications. If repeat case detected:

   - Applies simple deduplication flag 
   - Recommends suppression or adjustment navigation

3. **Local Store Logger**:
   Mechanism to record conversation outcomes along with:

   - Sentiment tags
   - Idea transfer acceptance/rejection rate
   - Quality of question performance from identified rodlists

4. **Research Initiation Bridge**:
   Calls multiple parallel requests through standard research agents (previously explained).

5. **Question Formulation Loop**:
   After collective research completion, at least four types of cues are interlaced using dynamic prompting templates via LLM:

   - Company-Centric
   - Person-Centric
   - Role-Level
   - Standard Set (STAR-based toolkit)

6. **Final Output Node**:
   Consolidated resource package containing:
   - Full intel summary doc
   - Compiled questions separated into deeper chunks (by concern domain)
   - Interview cards offering flashcard-style rehearsal semantics

All designed to enhance ecosystemically managed readiness rather than temporary per-perception tactics.

---

### 6. **Deep Research Pipeline** 🤖

**Purpose:** Advanced interview preparation through multi-agent intelligence analysis, providing strategic question generation and comprehensive preparation packages.

**Core Architecture:** Multi-agent research coordination system with specialized agents for company research, role analysis, and interview preparation guide generation.

#### Key Components:

**Research Coordination Agents:**
- **Company Researcher**: Deep company intelligence and culture analysis
- **Role Analyzer**: Position requirements and skill matching analysis  
- **Interview Guide Generator**: Comprehensive preparation package assembly with strategic insights

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

#### Output Categories:
- **Company Strategy & Vision**: Strategic insights and forward-looking questions
- **Role-Specific & Technical**: Position-focused and technical competency questions
- **Behavioral & Cultural**: Culture fit and experience-based behavioral questions
- **Strategic & Forward-Looking**: Industry trends and future-oriented discussions

#### Integration Points:
- **Workflow Runner**: Primary orchestration through `deep_research_pipeline.py`
- **Research Engine**: Consumes multi-source company and role intelligence
- **Email Pipeline**: Triggered by interview invitation classification
- **Memory Systems**: Stores preparation packages and tracks interview outcomes

#### Performance Characteristics:
- Generates 12-16 strategic questions per interview context
- Differentiates strategy based on company characteristics (e.g., sustainability vs. tech focus)
- Context-aware question prioritization and strategic recommendation generation
- Quality assessment with relevance scoring and strategic value evaluation

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

This allows systems to build proficiency organically as it receives continuous signals from developers and users like yourself!

### 🌉 Contextual Messaging Belt:

Purpose: Acts as an API layer between subsystems, translating outputs from one component into inputs for another, maintaining data consistency.

**Facilitates:**
- Receipt from social identity generator to textual relay nodes within application drafts and cold starter chains.
- Use of historical context to pre-fill likely next-step responses during feedback sequences
- user centric prompt derivation from role level criteria aligned with current openings offered or resume-derived stepladders.

Set up approximates relay point jumpers with defined priority trails of term usage depending upon receiving component's goal — opening angle development vs. tone mimicry in sensible contexts.

### 🔄 Feedback Loop Controller:

**Purpose:** Retro-influences agent behavior, questions quality, and reinforcement criteria based on outcome markers gathered automagically.

**Feedback Metrics Tracked:**
- Reply success/neglect ratios within interpersonal dialog modules
- Performance scores tagged to items presented in interview matrices
- Proactive research accuracy level testing via attitude-embedded sample quoting tags
- Response rate increases and delays observed in consecutive rounds of scheduled messaging

Such insights ultimately redirect ongoing training validations toward refined linguistic vector directions and internal fidelity settings.

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

### Security Posture:
- Opaque reverse proxy separation maintained between personal identity modules and exposed public agent nodes
- On-device classification of sensitive messages such that only output summaries propagate beyond sandboxed compute paths
- Two-tiered access management — entry request disambiguator codes

### Accessibility Controls:
- Configurable level profiles tailored to individual comfort (candidate-assistant mode to recruiter-aware boilerplate builder flow)
- Stepwise controls embedded natively into each intent pipe allowing throttling or full trial reviews under certain thresholds

With this layered security, it provides customized transparency balances while operating under identical foundational design withdrawn behind umbrella sandbox protection.

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

### 2. **Smart Interview Prep Sheet Making**
```
Received Interview Invitation Email via Inbox Monitor →
Pulled Through Orchestrator Agent Pipe (via Shared Context Stop Point) →
Parsed Subject Line & Embedded Calendar Elements for Entity Tags →
Checked Against Internal Archive First for Repetition Indicators →
If Fresh Request Collected, Be Ready Request Initiated to Company/Person/Role Analyses Schemes →
Extract Final Results Then Feed Into Tailored Question Builder System →
Create Custom Prep Card Bundle With Experience Anchors Embedded →
Sent Securely as Highlighted Data Blob(s) inside Upcoming Date Alert & Link Preloads Page for Presentation
```

### 3. **Advanced Deep Research Intelligence Processing**
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

---

## Deployment Plan Highlights

### Development Platform:
- Containerization Either Locally via Docker or Remotely via GCP/AWS Instances
- Real-Time Mirroring Enabled Through Git-Repos atop Watchful Merger Scripts keeping Track on External IP Rotations for Source Availability Denoted Features interactions

### Deployment Safety:
- API Usage Monitored Monthly Burn Accounts Configured for Test Cycling Before Live Production Rollouts
- Message Drift Tracking by Profiling Each Interaction Aggregations Alongside Trigger to Conscious Adjustments to Restore Legibility Opinion Instantaneously

Systems tied to familiar monitoring dashboards enabling live editing besides raw action debugging — comfortably letting stakeholders observe actual internal decision making through traceability lenses.

---

## Future Enhancement Roadmap

| Area                             | Description                                           | ETA         |
|----------------------------------|-------------------------------------------------------|-------------|
| Auto Job Matching                | Machine Learning Model for Role Accuracy Matching     | Q1 2025     |
| Enhanced Persona Embedding       | Fine-tuned end-to-end aliased aliases per country/culture| Q2 2025  |
| Full CRM Integration             | Connect LinkedIn Sales Navigator/Data unlock paths    | Q2 2025     |
| Analytics Dashboard Expansion    | Show performance scorecards with analytics visualizations| Mid 2025 |
| Voice-to-Text Module             | Interview practice spoken optimum extracting assist config| TBD       |

