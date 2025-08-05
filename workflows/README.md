# Interview Prep Workflow - Workflows

This folder contains the main workflow orchestrators and management tools for the Interview Prep system.

## Files

### Main Workflow
- **`interview_prep_workflow.py`** - Main entry point for the complete interview preparation workflow
  - Orchestrates all pipeline components
  - Processes emails individually 
  - Generates company-specific prep guides

### Cache Management
- **`cache_manager.py`** - Command-line tool for managing all caches used by the workflow

## Usage

### Running the Main Workflow
```bash
# Run the complete interview prep workflow
python workflows/interview_prep_workflow.py
```

### Cache Management
```bash
# Check cache status
python workflows/cache_manager.py --status

# View detailed cache information
python workflows/cache_manager.py --info

# Clear specific caches
python workflows/cache_manager.py --clear-tavily
python workflows/cache_manager.py --clear-openai

# Clear all caches
python workflows/cache_manager.py --clear-all

# Optimize caches (remove expired entries)
python workflows/cache_manager.py --optimize
```

## Cache Integration

The cache manager connects to:

- **📧 Email Pipeline**: Entity extraction caching
- **🔬 Deep Research Pipeline**: Tavily API caching for company/role/interviewer research  
- **📚 Prep Guide Pipeline**: OpenAI API caching for personalized guide generation

## Architecture

```
workflows/
├── interview_prep_workflow.py    # Main orchestrator
├── cache_manager.py              # Cache management tool
└── README.md                     # This file
```

The workflow uses the modular pipeline components from the `pipelines/` folder and coordinates cache usage across all components.
