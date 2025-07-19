"""
Demo script for the News Ingestion System
Shows how to use the ingestion engine to add news articles
"""

from src.news_ingestion import NewsIngestionEngine, NewsAPIConnector
from datetime import datetime, timezone, timedelta
import json


def demo_single_article_ingestion():
    """Demonstrate ingesting a single article"""
    print("=== Single Article Ingestion Demo ===\n")
    
    # Initialize the ingestion engine
    engine = NewsIngestionEngine("news.json")
    
    # Create a sample article
    article = engine.ingest_article(
        title="OpenAI Announces GPT-5 with Revolutionary Capabilities",
        content="OpenAI unveiled GPT-5 today, featuring unprecedented reasoning abilities and multimodal understanding. The new model represents a significant leap in artificial intelligence capabilities, with improved safety measures and reduced hallucinations.",
        source="AI News Network",
        category="Technology"
    )
    
    print(f"Ingested article:")
    print(f"  ID: {article.id}")
    print(f"  Title: {article.title}")
    print(f"  Entities: {', '.join(article.entities)}")
    print(f"  Tags: {', '.join(article.tags)}")
    print(f"  Sentiment: {article.sentiment}")
    print(f"  Impact Score: {article.impact_score}")
    print()


def demo_batch_ingestion():
    """Demonstrate batch ingestion of multiple articles"""
    print("=== Batch Ingestion Demo ===\n")
    
    engine = NewsIngestionEngine("news.json")
    
    # Sample batch of articles
    batch_articles = [
        {
            "title": "Federal Reserve Announces Interest Rate Decision",
            "content": "The Federal Reserve held interest rates steady at 5.25-5.5% citing ongoing inflation concerns. Markets reacted positively to the announcement, with major indices gaining ground.",
            "source": "Financial Times",
            "category": "Finance"
        },
        {
            "title": "Climate Summit Reaches Historic Agreement",
            "content": "World leaders at the UN Climate Summit agreed to triple renewable energy investments by 2030. The landmark agreement includes commitments from 150 nations to reduce carbon emissions.",
            "source": "Environmental Daily",
            "category": "Environment"
        },
        {
            "title": "Tech Giants Report Q4 Earnings Beat Expectations",
            "content": "Major technology companies including Apple, Microsoft, and Google reported stronger than expected quarterly earnings. Cloud computing and AI services drove significant revenue growth.",
            "source": "Tech Business Journal",
            "category": "Business"
        }
    ]
    
    ingested = engine.ingest_batch(batch_articles)
    
    print(f"Ingested {len(ingested)} articles:")
    for article in ingested:
        print(f"  - [{article.id}] {article.title[:50]}... ({article.sentiment}, score: {article.impact_score})")
    print()


def demo_search_functionality():
    """Demonstrate searching through ingested articles"""
    print("=== Search Functionality Demo ===\n")
    
    engine = NewsIngestionEngine("news.json")
    
    # Search for articles
    search_queries = ["Trump", "China", "automotive", "technology"]
    
    for query in search_queries:
        results = engine.search_articles(query)
        print(f"Search for '{query}': Found {len(results)} articles")
        if results:
            for i, article in enumerate(results[:3]):  # Show first 3 results
                print(f"  {i+1}. {article['title'][:60]}...")
        print()


def demo_recent_articles():
    """Show recent articles"""
    print("=== Recent Articles Demo ===\n")
    
    engine = NewsIngestionEngine("news.json")
    recent = engine.get_recent_articles(limit=5)
    
    print(f"Most recent {len(recent)} articles:")
    for article in recent:
        timestamp = datetime.fromisoformat(article['timestamp'].replace('Z', '+00:00'))
        time_ago = datetime.now(timezone.utc) - timestamp
        
        if time_ago.days > 0:
            time_str = f"{time_ago.days} days ago"
        elif time_ago.seconds > 3600:
            time_str = f"{time_ago.seconds // 3600} hours ago"
        else:
            time_str = f"{time_ago.seconds // 60} minutes ago"
        
        print(f"  - {article['title'][:60]}...")
        print(f"    Source: {article['source']} | {time_str} | Impact: {article['impact_score']}")
    print()


def demo_api_simulation():
    """Simulate automatic ingestion from API"""
    print("=== API Integration Simulation ===\n")
    
    engine = NewsIngestionEngine("news.json")
    
    # Simulate incoming news from API
    simulated_news = [
        {
            "title": "Breaking: Major Cryptocurrency Exchange Faces Regulatory Action",
            "content": "Securities regulators announced enforcement action against one of the world's largest cryptocurrency exchanges, citing violations of investor protection rules. The exchange's native token fell 15% on the news.",
            "source": "Crypto News Wire",
            "category": "Finance",
            "timestamp": datetime.now(timezone.utc).isoformat()
        },
        {
            "title": "Electric Vehicle Sales Surge 45% in Q4",
            "content": "Electric vehicle sales reached record highs in the fourth quarter, with Tesla, BYD, and traditional automakers all reporting significant growth. The surge reflects growing consumer acceptance and improved charging infrastructure.",
            "source": "Auto Industry Report",
            "category": "Automotive",
            "timestamp": (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
        }
    ]
    
    print("Simulating API news fetch...")
    for news in simulated_news:
        article = engine.ingest_article(**news)
        print(f"  ✓ Ingested: {article.title[:50]}...")
    print()


def show_statistics():
    """Show statistics about the news database"""
    print("=== News Database Statistics ===\n")
    
    engine = NewsIngestionEngine("news.json")
    articles = engine.articles["articles"]
    
    if not articles:
        print("No articles in database yet.")
        return
    
    # Calculate statistics
    total_articles = len(articles)
    categories = {}
    sentiments = {"positive": 0, "negative": 0, "neutral": 0}
    sources = {}
    
    for article in articles:
        # Count by category
        cat = article.get("category", "Unknown")
        categories[cat] = categories.get(cat, 0) + 1
        
        # Count by sentiment
        sent = article.get("sentiment", "neutral")
        if sent in sentiments:
            sentiments[sent] += 1
        
        # Count by source
        src = article.get("source", "Unknown")
        sources[src] = sources.get(src, 0) + 1
    
    print(f"Total articles: {total_articles}")
    print(f"\nTop categories:")
    for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {cat}: {count} articles ({count/total_articles*100:.1f}%)")
    
    print(f"\nSentiment distribution:")
    for sent, count in sentiments.items():
        print(f"  - {sent}: {count} articles ({count/total_articles*100:.1f}%)")
    
    print(f"\nTop sources:")
    for src, count in sorted(sources.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"  - {src}: {count} articles")
    
    # Average impact score
    avg_impact = sum(article.get("impact_score", 5.0) for article in articles) / total_articles
    print(f"\nAverage impact score: {avg_impact:.2f}")


def main():
    """Run all demos"""
    print("🚀 News Ingestion System Demo\n")
    
    # Run demos
    demo_single_article_ingestion()
    demo_batch_ingestion()
    demo_search_functionality()
    demo_recent_articles()
    demo_api_simulation()
    show_statistics()
    
    print("\n✅ Demo completed! The news ingestion system is ready to use.")
    print("\nTo use in your code:")
    print("  from src.news_ingestion import NewsIngestionEngine")
    print("  engine = NewsIngestionEngine('news.json')")
    print("  article = engine.ingest_article(title='...', content='...', source='...', category='...')")
    print("\nFor automatic monitoring (with real API):")
    print("  from src.news_ingestion import monitor_and_ingest")
    print("  monitor_and_ingest(engine, api_connector, interval_seconds=300)")


if __name__ == "__main__":
    main()