# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

AI-powered contextual search engine that discovers hidden connections between articles for a 48-hour hackathon. When users search for "Apple earnings", we reveal Taiwan droughts affecting chip suppliers, EU regulations, and competitive dynamics - 3x more valuable than keyword matching.

## Tech Stack

- **Python 3.9+**
- **LLM**: OpenAI API (GPT-3.5-turbo for speed, GPT-4 optional)
- **Embeddings**: sentence-transformers (all-MiniLM-L6-v2)
- **Vector Search**: NumPy (FAISS-ready)
- **Caching**: diskcache
- **UI**: Streamlit (planned)
- **Data Source**: NewsAPI (planned)

## Project Structure

```
article-relationship-engine/
├── src/
│   ├── search_engine.py      # Core AI search logic with contextual discovery
│   ├── config.py            # Configuration and environment variables
│   └── __init__.py
├── .env                     # API keys (create from .env.example)
└── CLAUDE.md               # This file
```

## Setup Commands

```bash
# Install dependencies (requirements.txt to be created)
pip install openai sentence-transformers numpy diskcache python-dotenv streamlit plotly networkx newsapi-python

# Set up environment variables
cp .env.example .env
# Add OPENAI_API_KEY and NEWSAPI_KEY to .env

# Run the search engine (when UI is implemented)
streamlit run app.py
```

## Core Architecture

### ContextualSearchEngine (src/search_engine.py)

The search pipeline follows this flow:

1. **Query Understanding** (`_understand_query`):
   - GPT extracts intent, related topics, hidden factors
   - Temperature: 0.3 for consistency
   - Returns structured JSON with search expansion terms

2. **Direct Matching** (`_find_direct_matches`):
   - Embedding-based similarity search
   - Uses pre-computed normalized embeddings
   - Returns top N articles by cosine similarity

3. **Contextual Discovery** (`_find_contextual_matches`):
   - Checks all articles for non-obvious relevance
   - GPT evaluates supply chain, regulatory, competitive connections
   - Cached to avoid repeated API calls

4. **Insight Generation** (`_generate_insights`):
   - Synthesizes findings into executive summary
   - Optional GPT-4 for complex reasoning
   - Temperature: 0.5 for balanced creativity

### Configuration (src/config.py)

Environment-based configuration with sensible defaults:
- `OPENAI_API_KEY`: Required for GPT integration
- `MAX_SEARCH_RESULTS`: 10
- `SIMILARITY_THRESHOLD`: 0.3
- `MAX_CONTEXT_DEPTH`: 2
- Cache TTL: 24 hours

## Key Implementation Patterns

### AI Prompt Engineering

```python
# Always structure prompts clearly
prompt = f"""
Analyze this search query and extract the user's intent.

Query: {query}

Return a JSON object with:
- primary_intent: Main goal
- related_topics: List of related areas
- hidden_factors: Non-obvious considerations
"""

# Request JSON format
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[{"role": "user", "content": prompt}],
    temperature=0.3,
    response_format={"type": "json_object"}
)
```

### Error Handling

```python
try:
    # API calls
except Exception as e:
    logger.error(f"API error: {e}")
    # Return graceful fallback
    return {"error": "temporary", "fallback": cached_result}
```

### Performance Optimization

- Cache all GPT responses with diskcache
- Pre-compute and normalize embeddings
- Batch relevance checks when possible
- Limit article content to 500 chars in prompts

## Next Implementation Steps

1. **Data Pipeline** (`data_fetcher.py`):
   - NewsAPI integration
   - Article deduplication
   - Content extraction

2. **UI Layer** (`app.py`):
   - Streamlit interface
   - Search input with real-time results
   - Visualization of connections

3. **Testing** (`test_engine.py`):
   - Unit tests for each pipeline stage
   - Mock GPT responses for consistency
   - Performance benchmarks

4. **Demo Setup** (`demo_scenarios.py`):
   - Pre-built impressive searches
   - Cached results for reliability
   - Side-by-side comparisons

## Development Guidelines

### When Adding Features:
1. Follow the existing pipeline pattern
2. Add caching for any external API calls
3. Validate all GPT JSON responses
4. Keep prompts under 500 tokens
5. Use type hints and docstrings

### When Testing:
- Mock expensive API calls
- Test error paths and fallbacks
- Verify cache behavior
- Check performance on 1000+ articles

### When Optimizing:
- Profile before optimizing
- Focus on API call reduction
- Consider batch processing
- Implement FAISS when needed

## Common Tasks

```bash
# Test search functionality
python -c "from src.search_engine import ContextualSearchEngine; engine = ContextualSearchEngine(); print(engine.search('Apple earnings'))"

# Clear cache
rm -rf cache/

# Check API usage
# Monitor OpenAI dashboard for token usage
```

## Troubleshooting

- **No API Key**: Set `OPENAI_API_KEY` in .env
- **Import Errors**: Install missing dependencies
- **Slow Search**: Check cache misses, reduce MAX_CONTEXT_DEPTH
- **Rate Limits**: Implement exponential backoff
- **Memory Issues**: Reduce article batch size

## Demo Strategy

Best searches to showcase:
1. "Apple iPhone production" → Supply chain insights
2. "Tesla market share" → EV ecosystem connections
3. "AI regulation" → Industry-wide impacts
4. "semiconductor shortage" → Cross-industry effects

Key metrics:
- 3x more context discovered
- <2 second response time
- $0.08 per enhanced search