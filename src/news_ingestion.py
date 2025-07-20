"""
News Ingestion System for Article Relationship Engine
Automatically processes and adds news articles to news.json
"""

import json
import os
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field, asdict
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class NewsArticle:
    """Data structure for a news article"""
    id: int
    title: str
    content: str
    timestamp: str
    source: str
    category: str
    entities: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    sentiment: str = "neutral"
    impact_score: float = 5.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return asdict(self)


class NewsIngestionEngine:
    """Handles ingestion of news articles into the JSON storage"""
    
    def __init__(self, news_file_path: str = "news.json"):
        self.news_file_path = news_file_path
        self.articles = self._load_existing_articles()
        
        # GPT is required - no fallback
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file.")
        
        self.client = OpenAI(api_key=api_key)
        self.use_batch_analysis = True  # Use single API call for all analysis
        
    def _load_existing_articles(self) -> Dict[str, Any]:
        """Load existing articles from JSON file"""
        if os.path.exists(self.news_file_path):
            try:
                with open(self.news_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except json.JSONDecodeError:
                print(f"Warning: Could not parse {self.news_file_path}, starting fresh")
                return {"articles": []}
        return {"articles": []}
    
    def _get_next_id(self) -> int:
        """Get the next available article ID"""
        if not self.articles.get("articles"):
            return 1
        max_id = max(article["id"] for article in self.articles["articles"])
        return max_id + 1
    
    def _extract_entities(self, title: str, content: str) -> List[str]:
        """Extract named entities using GPT"""
        try:
            prompt = f"""
Extract key named entities from this news article. Focus on:
- People (political figures, CEOs, etc.)
- Organizations (companies, government bodies, etc.)  
- Locations (countries, cities, regions)
- Products/Technologies
- Financial instruments

Title: {title}
Content: {content[:500]}...

Return a JSON object with a single key "entities" containing a list of the most important entities (max 10).
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("entities", [])[:10]
            
        except Exception as e:
            raise RuntimeError(f"GPT entity extraction failed: {e}")
    
    
    def _generate_tags(self, title: str, content: str, category: str) -> List[str]:
        """Generate tags using GPT"""
        try:
            prompt = f"""
Generate relevant tags for this news article. Consider:
- Main topic/theme
- Industry sector
- Geographic relevance
- Economic/political implications
- Key concepts

Title: {title}
Category: {category}
Content: {content[:400]}...

Return a JSON object with a single key "tags" containing a list of 3-5 lowercase hyphenated tags (e.g., "supply-chain", "trade-war").
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("tags", [])[:5]
            
        except Exception as e:
            raise RuntimeError(f"GPT tag generation failed: {e}")
    
    
    def _analyze_sentiment(self, title: str, content: str) -> str:
        """Analyze sentiment using GPT"""
        try:
            prompt = f"""
Analyze the sentiment of this news article. Consider:
- Overall tone and language
- Impact on stakeholders mentioned
- Economic/social implications
- Forward-looking statements

Title: {title}
Content: {content[:400]}...

Return a JSON object with:
- "sentiment": one of "positive", "negative", "neutral", "mixed"
- "confidence": a number between 0 and 1
- "reasoning": brief explanation (1-2 sentences)

If the sentiment is clearly mixed, return "neutral".
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            sentiment = result.get("sentiment", "neutral")
            
            # Normalize to our expected values
            if sentiment == "mixed":
                sentiment = "neutral"
                
            return sentiment
            
        except Exception as e:
            raise RuntimeError(f"GPT sentiment analysis failed: {e}")
    
    
    def _calculate_impact_score(self, title: str, content: str, category: str) -> float:
        """Calculate impact score using GPT"""
        try:
            prompt = f"""
Assess the potential impact of this news article on a scale of 1-10. Consider:
- Market/economic implications
- Number of people/organizations affected
- Geographic scope (local/national/global)
- Urgency and time sensitivity
- Potential for cascading effects
- Political/regulatory implications

Title: {title}
Category: {category}
Content: {content[:400]}...

Return a JSON object with:
- "impact_score": a number between 1.0 and 10.0
- "factors": list of 2-3 key impact factors
- "reasoning": brief explanation (1-2 sentences)

Guidelines:
- 1-3: Low impact, local or minor news
- 4-6: Moderate impact, regional or sector-specific
- 7-8: High impact, national or cross-industry
- 9-10: Critical impact, global or systemic consequences
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            score = float(result.get("impact_score", 5.0))
            
            # Ensure score is within bounds
            return min(max(score, 1.0), 10.0)
            
        except Exception as e:
            raise RuntimeError(f"GPT impact scoring failed: {e}")
    
    
    def _comprehensive_analysis_gpt(self, title: str, content: str, category: str) -> Dict[str, Any]:
        """Perform comprehensive analysis in a single GPT call"""
        try:
            prompt = f"""
Analyze this news article comprehensively. Provide:

1. ENTITIES: Key named entities (people, organizations, locations, products/tech)
2. TAGS: 3-5 relevant lowercase hyphenated tags
3. SENTIMENT: "positive", "negative", or "neutral"
4. IMPACT_SCORE: 1-10 based on market/economic/social implications

Title: {title}
Category: {category}
Content: {content[:600]}...

Return a JSON object with:
{{
    "entities": ["entity1", "entity2", ...],  // max 10
    "tags": ["tag1", "tag2", ...],  // 3-5 tags
    "sentiment": "positive/negative/neutral",
    "impact_score": 7.5,  // 1.0-10.0
    "analysis_summary": "Brief 1-2 sentence summary of the article's significance"
}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Validate and normalize the results
            return {
                "entities": result.get("entities", [])[:10],
                "tags": result.get("tags", [])[:5],
                "sentiment": result.get("sentiment", "neutral"),
                "impact_score": min(max(float(result.get("impact_score", 5.0)), 1.0), 10.0),
                "summary": result.get("analysis_summary", "")
            }
            
        except Exception as e:
            raise RuntimeError(f"GPT comprehensive analysis failed: {e}")
    
    def ingest_article(self, 
                      title: str,
                      content: str,
                      source: str,
                      category: str,
                      timestamp: Optional[str] = None,
                      entities: Optional[List[str]] = None,
                      tags: Optional[List[str]] = None,
                      sentiment: Optional[str] = None,
                      impact_score: Optional[float] = None) -> NewsArticle:
        """
        Ingest a new article into the system
        
        Args:
            title: Article title
            content: Article content
            source: News source
            category: Article category
            timestamp: Optional ISO timestamp (defaults to current time)
            entities: Optional list of entities (auto-extracted if not provided)
            tags: Optional list of tags (auto-generated if not provided)
            sentiment: Optional sentiment (auto-analyzed if not provided)
            impact_score: Optional impact score (auto-calculated if not provided)
            
        Returns:
            NewsArticle object that was added
        """
        # Generate timestamp if not provided
        if timestamp is None:
            timestamp = datetime.now(timezone.utc).isoformat()
        
        # Use batch analysis to get all fields at once for efficiency
        if entities is None or tags is None or sentiment is None or impact_score is None:
            analysis = self._comprehensive_analysis_gpt(title, content, category)
            
            # Use analysis results for any missing fields
            if entities is None:
                entities = analysis["entities"]
            if tags is None:
                tags = analysis["tags"]
            if sentiment is None:
                sentiment = analysis["sentiment"]
            if impact_score is None:
                impact_score = analysis["impact_score"]
        
        # Create article object
        article = NewsArticle(
            id=self._get_next_id(),
            title=title,
            content=content,
            timestamp=timestamp,
            source=source,
            category=category,
            entities=entities,
            tags=tags,
            sentiment=sentiment,
            impact_score=round(impact_score, 1)
        )
        
        # Add to articles list
        self.articles["articles"].append(article.to_dict())
        
        # Save to file
        self._save_articles()
        
        return article
    
    def ingest_batch(self, articles: List[Dict[str, Any]]) -> List[NewsArticle]:
        """Ingest multiple articles at once"""
        ingested = []
        for article_data in articles:
            article = self.ingest_article(**article_data)
            ingested.append(article)
        return ingested
    
    def _save_articles(self):
        """Save articles to JSON file"""
        with open(self.news_file_path, 'w', encoding='utf-8') as f:
            json.dump(self.articles, f, indent=2, ensure_ascii=False)
    
    def get_recent_articles(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get most recent articles"""
        sorted_articles = sorted(
            self.articles["articles"], 
            key=lambda x: x["timestamp"], 
            reverse=True
        )
        return sorted_articles[:limit]
    
    def search_articles(self, query: str) -> List[Dict[str, Any]]:
        """Simple search through articles"""
        query_lower = query.lower()
        results = []
        
        for article in self.articles["articles"]:
            if (query_lower in article["title"].lower() or 
                query_lower in article["content"].lower() or
                any(query_lower in entity.lower() for entity in article.get("entities", []))):
                results.append(article)
        
        return results


class NewsAPIConnector:
    """Connector for external news APIs with GPT-powered category detection"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        
        # GPT is required for categorization
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY is required for NewsAPIConnector")
        
        self.client = OpenAI(api_key=openai_key)
    
    def _detect_category(self, title: str, content: str) -> str:
        """Detect category using GPT"""
        
        try:
            prompt = f"""
Categorize this news article into one of these categories:
- Politics
- Finance  
- Technology
- Business
- International
- Environment
- Labor
- Legal
- Energy
- Healthcare
- Sports
- Entertainment
- Science
- Education
- Real Estate
- Transportation
- Agriculture
- Manufacturing
- Defense
- Commodities

Title: {title}
Content: {content[:300]}...

Return a JSON object with:
{{"category": "chosen category"}}
"""
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get("category", "Business")
            
        except Exception as e:
            raise RuntimeError(f"GPT categorization failed: {e}")
    
    
    def fetch_latest_news(self) -> List[Dict[str, Any]]:
        """
        Fetch latest news from external API
        This is a placeholder - implement actual API integration
        """
        # Example structure for incoming news
        # In real implementation, this would fetch from NewsAPI, RSS feeds, etc.
        sample_news = [
            {
                "title": "Breaking: Major Tech Company Announces AI Breakthrough",
                "content": "Leading technology firm reveals groundbreaking artificial intelligence system that promises to revolutionize natural language processing...",
                "source": "Tech News Daily"
            },
            {
                "title": "Federal Reserve Signals Rate Cut Possibility",
                "content": "Fed officials hint at potential interest rate reduction amid cooling inflation data and concerns about economic growth...",
                "source": "Financial Times"
            }
        ]
        
        # Add categories to news items
        processed_news = []
        for item in sample_news:
            if "category" not in item:
                item["category"] = self._detect_category(item["title"], item["content"])
            processed_news.append(item)
        
        return processed_news


def monitor_and_ingest(ingestion_engine: NewsIngestionEngine, 
                      api_connector: NewsAPIConnector,
                      interval_seconds: int = 300):
    """
    Monitor for new articles and automatically ingest them
    
    Args:
        ingestion_engine: The ingestion engine instance
        api_connector: API connector for fetching news
        interval_seconds: How often to check for new articles
    """
    import time
    
    print(f"Starting news monitoring (checking every {interval_seconds} seconds)...")
    
    while True:
        try:
            # Fetch latest news
            new_articles = api_connector.fetch_latest_news()
            
            if new_articles:
                print(f"Found {len(new_articles)} new articles")
                ingested = ingestion_engine.ingest_batch(new_articles)
                
                for article in ingested:
                    print(f"Ingested: {article.title} (ID: {article.id})")
            
            # Wait before next check
            time.sleep(interval_seconds)
            
        except KeyboardInterrupt:
            print("\nStopping news monitor...")
            break
        except Exception as e:
            print(f"Error during ingestion: {e}")
            time.sleep(interval_seconds)