<a name="readme-top"></a>

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/Kathy331/resume-ai-agents">
    <img src="ui/images/inky.png" alt="Logo" width="80" height="80">
  </a>

  <h3 align="center">Resume AI Agents</h3>

  <p align="center">
    A modular AI system that automates job search and application workflows using specialized agents.
    Streamlines LinkedIn profile discovery, resume analysis, job matching, personalized emails, and calendar integration. All powered by a Streamlit dashboard.
    <br />
    <a href="https://github.com/Kathy331/resume-ai-agents"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="#">View Demo</a>
    ·
    <a href="https://github.com/Kathy331/resume-ai-agents/issues/new?labels=bug&template=bug-report---.md">Report Bugs</a>
    ·
    <a href="https://github.com/Kathy331/resume-ai-agents/issues/new?labels=enhancement&template=feature-request---.md">Request Features</a>
    <br />
    Contributions, issues, and feature requests are welcome!
    <br />
    Maintained by:<a href="https://github.com/Kathy331"> @Kathy331</a>

  </p>
</div>




<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li><a href="#features">Features</a></li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#setup">Setup</a></li>
      </ul>
    </li>
    <li><a href="#usage">Usage</a></li>
    <li><a href="#contact-and-developers">Contact and Developers</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

Resume AI Agents is a modular AI system designed to automate job search and application workflows. It integrates seamlessly into a user friendly Streamlit interface and supports:

- LinkedIn profile discovery and data extraction  
- Resume to job semantic matching and skill extraction  
- Personalized application emails matching user tone  
- Job recommendations powered by deep learning models  
- Calendar integration for interview scheduling  


<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

#### AI & Machine Learning
* ![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white) - GPT models for intelligent text processing and generation
* ![LangGraph](https://img.shields.io/badge/LangGraph-1C3C3C?style=flat-square&logo=langchain&logoColor=white) - Workflow orchestration with state management and conditional routing
* ![spaCy](https://img.shields.io/badge/spaCy-09A3D5?style=flat-square&logo=spacy&logoColor=white) - Named Entity Recognition for email parsing and resume analysis
* ![scikit-learn](https://img.shields.io/badge/scikit--learn-F7931E?style=flat-square&logo=scikit-learn&logoColor=white) - Machine learning utilities and text classification
* ![LangChain](https://img.shields.io/badge/LangChain-1C3C3C?style=flat-square&logo=langchain&logoColor=white) - LLM application framework

#### Frontend & Interface
* ![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=flat-square&logo=streamlit&logoColor=white) - Interactive web dashboard and user interface
* ![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=flat-square&logo=plotly&logoColor=white) - Data visualizations and analytics charts
* ![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white) - Custom UI components and styling

#### Backend & APIs
* ![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white) - High-performance async web framework
* ![Python](https://img.shields.io/badge/Python-3776AB?style=flat-square&logo=python&logoColor=white) - Core backend language (3.10+)
* ![SQLite](https://img.shields.io/badge/SQLite-07405E?style=flat-square&logo=sqlite&logoColor=white) - Interview data storage with deduplication
* ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) - Data manipulation and analysis

#### Integrations & APIs
* ![Gmail API](https://img.shields.io/badge/Gmail_API-EA4335?style=flat-square&logo=gmail&logoColor=white) - Email fetching and processing automation
* ![Google OAuth](https://img.shields.io/badge/Google_OAuth-4285F4?style=flat-square&logo=google&logoColor=white) - Secure authentication and authorization
* ![Tavily API](https://img.shields.io/badge/Tavily_API-FF6B6B?style=flat-square&logo=search&logoColor=white) - Web search and company research intelligence
* ![LinkedIn](https://img.shields.io/badge/LinkedIn_API-0077B5?style=flat-square&logo=linkedin&logoColor=white) - Professional profile discovery and networking

#### *Data & Storage
* ![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=flat-square&logo=pydantic&logoColor=white) - Data validation and settings management
* ![JSON](https://img.shields.io/badge/JSON-000000?style=flat-square&logo=json&logoColor=white) - Structured data exchange and configuration
* ![Vector Store](https://img.shields.io/badge/Vector_Store-FF69B4?style=flat-square&logo=database&logoColor=white) - Semantic search and document embeddings


<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- FEATURES -->
## Features

- Modular AI agent design for extensibility  
- Orchestrator pattern for flexible workflows  
- Resume to job semantic matching with NLP  
- Personalized email drafting to match user tone  
- Streamlit dashboard for easy interaction  
- Future ready for RAG (Retrieval-Augmented Generation) modules  

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

Follow these steps to get a local copy up and running:

### Prerequisites

Ensure you have Python 3.10+ 

### Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/Kathy331/resume-ai-agents.git
   cd resume-ai-agents
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv.  #On Windows: python -m venv .venv
   source .venv/bin/activate #On Windows: .venv\Scripts\activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Streamlit app:
   ```bash
   streamlit run ui/app.py
   ```

5. Optional: Use Docker for containerized deployment:
    Download Docker for Mac or Windows: https://www.docker.com/  
   ```bash
   docker compose up --build 
   ```
6. Testing:
    to run all test you could run: 
    ```bash
    pytest
    ```
    but please be careful of token limits, to run a single test, run: 
    ```bash
    pytest tests/test_agents/test_keyword_extractor.py
    ```
    there will be an `outputs` file generated for you to better see your test results 


<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE -->
## Usage

Once the app is running, you can:

- Upload your resume and get matched jobs  
- Use the dashboard to view job insights  
- Automatically generate customized emails  
- Sync interviews to your calendar  
- Extend agents or integrate new models as needed  

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- CONTACT -->
## Contact and Developers

Kathy Chen - [@Linkedin](https://www.linkedin.com/in/kathy-chen-b35b532a6/) - email: kathychen331@outlook.com

Grace Chen - [@Linkedin](https://www.linkedin.com/in/chen-p-grace/) - email: chenpgrace1@gmail.com

Julianna Bracamonte - [@Linkedin](https://www.linkedin.com/in/julianna-bracamonte-759644237/) - email: 


<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments
 
* [Dandilyonn SEEDS Program](https://www.dandilyonn.com/)
*  Streamlit for their amazing framework  
*  OpenAI for language models powering the agents  
*  Tavily for intelligent web search APIs 

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINK & IMAGE DEFINITIONS -->
[contributors-shield]: https://img.shields.io/github/contributors/Kathy331/resume-ai-agents.svg?style=flat-square
[contributors-url]: https://github.com/Kathy331/resume-ai-agents/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Kathy331/resume-ai-agents.svg?style=flat-square
[forks-url]: https://github.com/Kathy331/resume-ai-agents/network/members
[stars-shield]: https://img.shields.io/github/stars/Kathy331/resume-ai-agents.svg?style=flat-square
[stars-url]: https://github.com/Kathy331/resume-ai-agents/stargazers
[issues-shield]: https://img.shields.io/github/issues/Kathy331/resume-ai-agents.svg?style=flat-square
[issues-url]: https://github.com/Kathy331/resume-ai-agents/issues