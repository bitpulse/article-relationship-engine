"""
Example: How to use the News Ingestion System

This shows how to ingest news articles with automatic GPT-powered analysis
"""

from src.news_ingestion import NewsIngestionEngine, NewsAPIConnector
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize the ingestion engine
# GPT is required - will raise error if OPENAI_API_KEY is not set
engine = NewsIngestionEngine("news.json")

# Example 1: Ingest a single article (GPT will analyze it automatically)
print("Example 1: Ingesting a single article with GPT analysis")
print("-" * 50)

article = engine.ingest_article(
    title="Microsoft Invests $10 Billion in Quantum Computing Research",
    content="""Microsoft announced a major investment in quantum computing research, 
    partnering with leading universities and research institutions. The initiative 
    aims to accelerate the development of practical quantum applications for 
    drug discovery, materials science, and cryptography. CEO Satya Nadella 
    called it a 'transformative moment' for computing.""",
    source="Tech Business Wire",
    category="Technology"
)

print(f"Article ingested successfully!")
print(f"ID: {article.id}")
print(f"Entities detected: {', '.join(article.entities)}")
print(f"Tags generated: {', '.join(article.tags)}")
print(f"Sentiment: {article.sentiment}")
print(f"Impact Score: {article.impact_score}")
print()

# Example 2: Ingest news without specifying category (GPT will detect it)
print("Example 2: Auto-categorization with GPT")
print("-" * 50)

# Initialize API connector (GPT categorization is required)
api_connector = NewsAPIConnector()

# Simulate incoming news without category
raw_news = {
    "title": "European Central Bank Raises Interest Rates by 0.5%",
    "content": """The ECB surprised markets with a larger than expected rate hike, 
    citing persistent inflation concerns across the eurozone. Bank President 
    Christine Lagarde emphasized the need for decisive action to bring inflation 
    back to target levels.""",
    "source": "Reuters"
}

# Auto-detect category
category = api_connector._detect_category(raw_news["title"], raw_news["content"])
print(f"Auto-detected category: {category}")

# Ingest with detected category
article2 = engine.ingest_article(
    title=raw_news["title"],
    content=raw_news["content"],
    source=raw_news["source"],
    category=category
)

print(f"Article ingested with auto-detected category!")
print(f"Analysis results:")
print(f"  - Entities: {article2.entities}")
print(f"  - Tags: {article2.tags}")
print(f"  - Sentiment: {article2.sentiment}")
print(f"  - Impact: {article2.impact_score}")
print()

# Example 3: Batch processing with GPT
print("Example 3: Batch processing multiple articles")
print("-" * 50)

batch_articles = [
    {
        "title": "Tesla Announces New Gigafactory in India",
        "content": "Tesla confirmed plans to build its first manufacturing facility in India, with production expected to begin in 2026.",
        "source": "Economic Times",
        "category": "Automotive"
    },
    {
        "title": "Global Chip Shortage Shows Signs of Easing",
        "content": "Semiconductor manufacturers report improved production capacity as supply chain bottlenecks begin to clear.",
        "source": "Semiconductor Weekly",
        "category": "Technology"
    }
]

ingested = engine.ingest_batch(batch_articles)
print(f"Ingested {len(ingested)} articles in batch")
for article in ingested:
    print(f"  - {article.title[:40]}... (Impact: {article.impact_score})")
print()

# Example 4: Search through ingested articles
print("Example 4: Searching articles")
print("-" * 50)

search_results = engine.search_articles("Microsoft")
print(f"Found {len(search_results)} articles mentioning 'Microsoft'")
for result in search_results[:3]:
    print(f"  - {result['title']}")
print()

# Example 5: Get recent high-impact articles
print("Example 5: Recent high-impact articles")
print("-" * 50)

recent = engine.get_recent_articles(limit=5)
high_impact = [a for a in recent if a.get('impact_score', 0) >= 7.0]
print(f"High-impact articles (score >= 7.0):")
for article in high_impact:
    print(f"  - {article['title'][:50]}... (Score: {article['impact_score']})")

print("\n✅ All examples completed successfully!")
print("\nNote: The GPT features provide:")
print("  - Intelligent entity extraction")
print("  - Contextual sentiment analysis")
print("  - Sophisticated impact scoring")
print("  - Automatic category detection")
print("  - Relevant tag generation")