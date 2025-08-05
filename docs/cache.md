# Cache Management System Documentation

## Overview

The Interview Prep Workflow system uses sophisticated caching to improve performance and reduce API costs. However, when developing or testing enhanced features, caching can mask new improvements by returning old responses instead of fresh AI-generated content.

## Cache Types

### 1. OpenAI LLM Cache (`.openai_cache/`)
- **Purpose**: Caches OpenAI API responses for prep guide generation
- **Impact**: Can return old generic content instead of new enhanced features
- **Location**: `.openai_cache/` directory in project root
- **TTL**: 1 week (168 hours)

### 2. Tavily Research Cache (`cache/tavily/`)
- **Purpose**: Caches research results to avoid re-querying external sources
- **Impact**: Generally helpful for performance without affecting content quality
- **Location**: `cache/tavily/` directory
- **TTL**: 3 days (72 hours)

## Problem: Enhanced Features Masked by Cache

### Issue Description
When new enhanced features are implemented (e.g., personalized questions, detailed interviewer profiles), the OpenAI cache can return old responses that don't include these improvements. This creates a discrepancy between:
- **Claimed capabilities**: System reports generating enhanced content (e.g., "4,512+ characters of personalized questions")
- **Actual output**: Files contain generic content from cached responses

### Evidence of Caching Issues
- Terminal shows: `🗄️ Using cached response for async call`
- Processing time: ~0.01s (cached) vs 40+ seconds (fresh API calls)
- Character counts are reported but detailed content isn't visible in output

## Solutions

### 1. Command-Line Cache Management

#### Clear OpenAI Cache Before Running Workflow
```bash
# Clear cache and force fresh content generation
python -m workflows.interview_prep_workflow --clear-openai-cache

# Alternative: Use cache manager directly
python workflows/cache_manager.py --clear-openai
```

#### Check Cache Status
```bash
# View all cache statistics
python workflows/cache_manager.py --status

# Get detailed cache information
python workflows/cache_manager.py --info
```

#### Clear All Caches
```bash
# Nuclear option - clear everything
python workflows/cache_manager.py --clear-all
```

### 2. Manual Cache Clearing

#### Remove OpenAI Cache Directory
```bash
# From project root
rm -rf .openai_cache
```

#### Remove All Cache Files
```bash
# Remove Python cache
find . -name "*.cache" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Remove OpenAI cache
rm -rf .openai_cache

# Remove output files to ensure fresh generation
rm -rf outputs/fullworkflow/*.txt
```

### 3. Environment Variable Control

Set `DISABLE_OPENAI_CACHE=true` to disable caching for a single run:
```bash
DISABLE_OPENAI_CACHE=true python -m workflows.interview_prep_workflow
```

## Integration with Workflow

### Enhanced Workflow Features

The workflow now includes integrated cache management:

```bash
# Basic usage (uses cache)
python -m workflows.interview_prep_workflow

# Force fresh content generation
python -m workflows.interview_prep_workflow --clear-openai-cache

# Specify folder and clear cache
python -m workflows.interview_prep_workflow --clear-openai-cache --folder demo --max-emails 5
```

### Cache Status Reporting

The workflow automatically reports:
- Current cache status before execution
- Whether responses will be cached or fresh
- Final cache status after execution
- Guidance on when to clear cache

## Visual Indicators

### Cache Status Messages
- `🗄️ Using cached response for async call` - **OLD CONTENT WARNING**
- `🌐 Making async OpenAI API call` - **FRESH CONTENT GENERATION**
- `🌐 Making async OpenAI API call (cache disabled)` - **CACHING DISABLED**
- `💾 Caching disabled - response not cached` - **NO CACHING THIS RUN**

### Performance Indicators
- **Cached responses**: Processing time ~0.01s per email
- **Fresh API calls**: Processing time 30-40s per email
- **Character counts**: Higher counts indicate more detailed content

## Best Practices

### For Development
1. **Always clear cache** when testing new features
2. **Use `--clear-openai-cache`** flag during development
3. **Monitor character counts** to verify enhanced content generation
4. **Check terminal messages** for cache vs fresh indicators

### For Production
1. **Use cache normally** for performance benefits
2. **Clear cache periodically** to get updated research
3. **Monitor cache size** to prevent disk space issues
4. **Use cache manager** for maintenance

### For Testing Enhanced Features
1. **Clear OpenAI cache first**: `python -m workflows.interview_prep_workflow --clear-openai-cache`
2. **Verify fresh generation**: Look for `🌐 Making async OpenAI API call` messages
3. **Check character counts**: Enhanced features should show higher counts
4. **Review output files**: Verify detailed content is present

## Cache Manager Commands Reference

### Status Commands
```bash
# Overall status
python workflows/cache_manager.py --status

# Detailed information
python workflows/cache_manager.py --info
```

### Clearing Commands
```bash
# Clear OpenAI cache only
python workflows/cache_manager.py --clear-openai

# Clear Tavily cache only
python workflows/cache_manager.py --clear-tavily

# Clear all caches
python workflows/cache_manager.py --clear-all
```

### Help
```bash
python workflows/cache_manager.py --help
```

## Troubleshooting

### Problem: Generic content despite enhanced features
**Solution**: Clear OpenAI cache and re-run
```bash
python -m workflows.interview_prep_workflow --clear-openai-cache
```

### Problem: Low character counts for personalized questions
**Cause**: Cached responses from before enhancements were implemented
**Solution**: Force fresh generation
```bash
rm -rf .openai_cache
python -m workflows.interview_prep_workflow
```

### Problem: System claims enhancements but output is generic
**Diagnosis**: Check terminal for cache messages
**Fix**: Use `--clear-openai-cache` flag

### Problem: Cache corruption or errors
**Nuclear solution**: Clear everything and start fresh
```bash
python workflows/cache_manager.py --clear-all
rm -rf outputs/fullworkflow/*.txt
```

## Implementation Notes

### Cache Integration Points
1. **LLM Client** (`shared/llm_client.py`): Core caching logic
2. **Cache Manager** (`workflows/cache_manager.py`): Command-line interface
3. **Interview Workflow** (`workflows/interview_prep_workflow.py`): Integrated cache control
4. **OpenAI Cache** (`shared/openai_cache.py`): Cache storage and retrieval

### Environment Variables
- `DISABLE_OPENAI_CACHE=true`: Disables caching for current run
- `OPENAI_API_KEY`: Required for fresh API calls (falls back to mock if missing)

### Cache Files Structure
```
.openai_cache/
├── _cache_info.json          # Cache metadata
├── [hash1].json             # Cached response 1
├── [hash2].json             # Cached response 2
└── ...                      # More cached responses

cache/tavily/
├── _cache_info.json         # Tavily cache metadata  
├── [query_hash1].json       # Research result 1
└── ...                      # More research results
```

This documentation should be referenced whenever:
- Implementing new AI-powered features
- Testing enhanced content generation
- Debugging content quality issues
- Setting up development environments
- Troubleshooting workflow problems
