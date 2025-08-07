
# Agent Specifications
## Email Classification
- **Purpose:** Classify emails into categories (e.g., interview invite, other)
- **Inputs:** Raw email content
- **Outputs:** Classification label (e.g., interview invite, personal, other)

## Company Analysis Agent
- **Purpose:** Validates company identity, gathers market info
- **Inputs:** Company name, email context
- **Outputs:** Company validation, industry analysis, citations

## Interviewer Analysis Agent
- **Purpose:** Finds LinkedIn profiles, background research
- **Inputs:** Interviewer name, company context
- **Outputs:** LinkedIn profiles, professional background, citations

## Prep Guide Agent
- **Purpose:** Synthesizes all data into a personalized prep guide
- **Inputs:** Entities, research data, citations
- **Outputs:** Markdown and HTML prep guide files


# Pipeline Overview


## Email Pipeline Agent
- **Purpose:** Classifies emails, extracts entities, checks memory for duplicates
- **Inputs:** Raw email data from Gmail API
- **Outputs:** Entities (company, interviewer, date, etc.), classification result

## Deep Research Pipeline
- **Purpose:** Conducts multi-agent research using Tavily API
- **Inputs:** Entities from Email Pipeline, classification result
- **Outputs:** Company and interviewer analysis, citations collected by Citation Manager

## Reflection
- **Purpose:** Assesses research quality and identifies gaps
- **Inputs:** Research data from Deep Research Pipeline
- **Outputs:** Reflection report, confidence score

## Prep Guide Generation
- **Purpose:** Generates personalized prep guide using OpenAI GPT
- **Inputs:** Entities, research findings, citations
- **Outputs:** Markdown and HTML files for each company

## UI Integration
- **Generate Prep Guide:**
  - Streamlit dashboard loads guides from output folder
  - Tabs for each company. 
- **View/Edit Guides:**
  - Interactive dashboard for viewing and editing guides 
- **Send Emails:**
  - Email sending button for all guides and individual guides
- **Cache Management:**
  - UI cache button to clear cache and output files
- **Output Files:**
  - Guides saved to `outputs/fullworkflow/`
- **Download Prep guides:**
  - Download HTML prep guides

## Output
- Guides saved to `outputs/fullworkflow/`
- HTML guides for UI/email in `outputs/ui/`

## Notes
- All agents are modular and can be extended
- All guides are citation-backed and validated
