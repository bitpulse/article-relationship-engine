# News Ingestion System with GPT Integration

## Overview

The news ingestion system automatically processes incoming news articles and adds them to `news.json` with intelligent analysis powered by GPT-3.5.

## Features

### 🤖 GPT-Powered Analysis

- **Entity Extraction**: Identifies people, organizations, locations, and technologies
- **Tag Generation**: Creates relevant, searchable tags
- **Sentiment Analysis**: Determines positive/negative/neutral tone
- **Impact Scoring**: Rates articles 1-10 based on significance
- **Category Detection**: Auto-categorizes uncategorized news

### 📊 Data Structure

Each article is stored with:

```json
{
  "id": 123,
  "title": "Article Title",
  "content": "Full article content...",
  "timestamp": "2025-07-19T12:00:00Z",
  "source": "News Source",
  "category": "Technology",
  "entities": ["Microsoft", "Satya Nadella", "AI"],
  "tags": ["technology", "artificial-intelligence", "investment"],
  "sentiment": "positive",
  "impact_score": 8.5
}
```

## Installation

```bash
# Ensure you have the required dependencies
pip install openai python-dotenv

# Set your OpenAI API key
echo "OPENAI_API_KEY=your_key_here" > .env
```

## Basic Usage

```python
from src.news_ingestion import NewsIngestionEngine

# Initialize engine (automatically uses GPT if API key is available)
engine = NewsIngestionEngine("news.json")

# Ingest a single article
article = engine.ingest_article(
    title="Breaking News Title",
    content="Article content here...",
    source="News Agency",
    category="Finance"
)

# The system automatically:
# - Extracts entities using GPT
# - Generates relevant tags
# - Analyzes sentiment
# - Calculates impact score
```

## Advanced Features

### Batch Processing

```python
articles = [
    {"title": "...", "content": "...", "source": "...", "category": "..."},
    {"title": "...", "content": "...", "source": "...", "category": "..."}
]
ingested = engine.ingest_batch(articles)
```

### Auto-Categorization

```python
from src.news_ingestion import NewsAPIConnector

connector = NewsAPIConnector()
category = connector._detect_category(title, content)
```

### Search Functionality

```python
# Search for articles
results = engine.search_articles("keyword")

# Get recent articles
recent = engine.get_recent_articles(limit=10)
```

## GPT Integration Details

### Single API Call Optimization

When using GPT, the system makes a single comprehensive API call to analyze:

- Named entities
- Relevant tags
- Sentiment
- Impact score

This reduces API costs and improves performance.

### Fallback Mechanism

If GPT is unavailable or fails, the system automatically falls back to rule-based analysis for:

- Basic entity extraction (capitalized phrases)
- Keyword-based tagging
- Simple sentiment analysis
- Category-based impact scoring

### Cost Considerations

- Each article analysis costs approximately $0.001-0.002
- Batch processing is recommended for large volumes
- Results are cached in the JSON file

## Monitoring & Automation

```python
from src.news_ingestion import monitor_and_ingest

# Set up automatic monitoring
monitor_and_ingest(
    ingestion_engine=engine,
    api_connector=connector,
    interval_seconds=300  # Check every 5 minutes
)
```

## Examples

See `example_news_ingestion.py` for complete examples of:

1. Single article ingestion with GPT
2. Auto-categorization
3. Batch processing
4. Search functionality
5. High-impact article filtering

## Performance

- GPT analysis: ~1-2 seconds per article
- Batch processing: Supports concurrent analysis
- Storage: Efficient JSON format
- Search: In-memory for fast queries

## Error Handling

The system includes robust error handling:

- Automatic fallback if GPT fails
- Validation of all fields
- Duplicate detection by content hash
- Graceful handling of malformed data

## Future Enhancements

Potential additions:

- Real NewsAPI integration
- RSS feed support
- Webhook notifications
- Database backend (PostgreSQL/MongoDB)
- Real-time streaming ingestion
- Multi-language support
- Custom entity types
- Trend detection

## Troubleshooting

**No GPT analysis occurring:**

- Check that OPENAI_API_KEY is set in .env
- Verify API key is valid
- Check console for error messages

**Slow performance:**

- Consider batch processing
- Implement caching layer
- Use GPT-3.5-turbo for speed

**High API costs:**

- Reduce content length sent to GPT
- Cache analysis results
- Use fallback for low-priority news
