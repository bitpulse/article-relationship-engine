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
    
    def __init__(self, news_file_path: str = "news.json", use_gpt: bool = True):
        self.news_file_path = news_file_path
        self.articles = self._load_existing_articles()
        self.use_gpt = use_gpt
        
        if self.use_gpt:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                print("Warning: OPENAI_API_KEY not found. Falling back to basic processing.")
                self.use_gpt = False
            else:
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
    
    def _extract_entities_gpt(self, title: str, content: str) -> List[str]:
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
            print(f"GPT entity extraction failed: {e}")
            return self._extract_entities_basic(title, content)
    
    def _extract_entities_basic(self, title: str, content: str) -> List[str]:
        """Basic entity extraction without GPT"""
        # Simple entity extraction - find capitalized words and phrases
        text = f"{title} {content}"
        
        # Common patterns for entities
        entities = set()
        
        # Company names and organizations
        org_pattern = r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b'
        potential_orgs = re.findall(org_pattern, text)
        
        # Filter out common words
        common_words = {'The', 'This', 'That', 'These', 'Those', 'In', 'On', 'At', 
                       'For', 'To', 'From', 'With', 'By', 'Of', 'And', 'Or', 'But'}
        
        for org in potential_orgs:
            if org not in common_words and len(org) > 2:
                entities.add(org)
        
        # Add quoted entities
        quoted_pattern = r'"([^"]+)"'
        quoted_items = re.findall(quoted_pattern, text)
        entities.update(quoted_items)
        
        return sorted(list(entities))[:10]  # Limit to 10 entities
    
    def _extract_entities(self, title: str, content: str) -> List[str]:
        """Extract named entities from title and content"""
        if self.use_gpt:
            return self._extract_entities_gpt(title, content)
        else:
            return self._extract_entities_basic(title, content)
    
    def _generate_tags_gpt(self, title: str, content: str, category: str) -> List[str]:
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
            print(f"GPT tag generation failed: {e}")
            return self._generate_tags_basic(title, content, category)
    
    def _generate_tags_basic(self, title: str, content: str, category: str) -> List[str]:
        """Basic tag generation without GPT"""
        text = f"{title} {content} {category}".lower()
        
        # Keywords to look for
        tag_keywords = {
            'trade': ['trade', 'tariff', 'import', 'export'],
            'policy': ['policy', 'regulation', 'government'],
            'market': ['market', 'stock', 'investment', 'financial'],
            'technology': ['technology', 'tech', 'innovation', 'digital'],
            'manufacturing': ['manufacturing', 'production', 'factory'],
            'supply-chain': ['supply chain', 'logistics', 'distribution'],
            'employment': ['employment', 'jobs', 'workers', 'labor'],
            'economic': ['economic', 'economy', 'growth'],
            'international': ['international', 'global', 'foreign'],
            'automotive': ['automotive', 'auto', 'vehicle', 'car'],
            'mexico': ['mexico', 'mexican'],
            'china': ['china', 'chinese'],
            'agriculture': ['agriculture', 'farming', 'crops']
        }
        
        tags = []
        for tag, keywords in tag_keywords.items():
            if any(keyword in text for keyword in keywords):
                tags.append(tag)
        
        return tags[:5]  # Limit to 5 tags
    
    def _generate_tags(self, title: str, content: str, category: str) -> List[str]:
        """Generate relevant tags for the article"""
        if self.use_gpt:
            return self._generate_tags_gpt(title, content, category)
        else:
            return self._generate_tags_basic(title, content, category)
    
    def _analyze_sentiment_gpt(self, title: str, content: str) -> str:
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
            print(f"GPT sentiment analysis failed: {e}")
            return self._analyze_sentiment_basic(title, content)
    
    def _analyze_sentiment_basic(self, title: str, content: str) -> str:
        """Basic sentiment analysis without GPT"""
        text = f"{title} {content}".lower()
        
        # Simple sentiment analysis based on keywords
        positive_words = ['growth', 'increase', 'surge', 'expand', 'improve', 'gain', 
                         'positive', 'optimistic', 'opportunity', 'benefit']
        negative_words = ['decline', 'fall', 'drop', 'concern', 'warning', 'threat',
                         'negative', 'pessimistic', 'risk', 'loss', 'plunge']
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count + 2:
            return "positive"
        elif negative_count > positive_count + 2:
            return "negative"
        else:
            return "neutral"
    
    def _analyze_sentiment(self, title: str, content: str) -> str:
        """Analyze sentiment of the article"""
        if self.use_gpt:
            return self._analyze_sentiment_gpt(title, content)
        else:
            return self._analyze_sentiment_basic(title, content)
    
    def _calculate_impact_score_gpt(self, title: str, content: str, category: str) -> float:
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
            print(f"GPT impact scoring failed: {e}")
            return self._calculate_impact_score_basic(title, content, category)
    
    def _calculate_impact_score_basic(self, title: str, content: str, category: str) -> float:
        """Basic impact score calculation without GPT"""
        score = 5.0  # Base score
        
        # Adjust based on category
        high_impact_categories = ['Politics', 'Finance', 'International', 'Economics']
        if category in high_impact_categories:
            score += 1.5
        
        # Adjust based on keywords
        high_impact_keywords = ['billion', 'million', 'percent', 'crisis', 'major',
                               'significant', 'emergency', 'breaking']
        text = f"{title} {content}".lower()
        
        for keyword in high_impact_keywords:
            if keyword in text:
                score += 0.5
        
        # Cap the score
        return min(max(score, 3.0), 10.0)
    
    def _calculate_impact_score(self, title: str, content: str, category: str) -> float:
        """Calculate impact score based on various factors"""
        if self.use_gpt:
            return self._calculate_impact_score_gpt(title, content, category)
        else:
            return self._calculate_impact_score_basic(title, content, category)
    
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
            print(f"GPT comprehensive analysis failed: {e}")
            # Fall back to individual methods
            return {
                "entities": self._extract_entities_basic(title, content),
                "tags": self._generate_tags_basic(title, content, category),
                "sentiment": self._analyze_sentiment_basic(title, content),
                "impact_score": self._calculate_impact_score_basic(title, content, category),
                "summary": ""
            }
    
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
        
        # If using GPT and batch analysis, get all fields at once
        if self.use_gpt and hasattr(self, 'use_batch_analysis') and self.use_batch_analysis:
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
        else:
            # Auto-generate missing fields individually
            if entities is None:
                entities = self._extract_entities(title, content)
            
            if tags is None:
                tags = self._generate_tags(title, content, category)
            
            if sentiment is None:
                sentiment = self._analyze_sentiment(title, content)
            
            if impact_score is None:
                impact_score = self._calculate_impact_score(title, content, category)
        
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
    """Connector for external news APIs with category detection"""
    
    def __init__(self, api_key: Optional[str] = None, use_gpt_categorization: bool = True):
        self.api_key = api_key
        self.use_gpt_categorization = use_gpt_categorization
        
        if self.use_gpt_categorization:
            openai_key = os.getenv("OPENAI_API_KEY")
            if openai_key:
                self.client = OpenAI(api_key=openai_key)
            else:
                self.use_gpt_categorization = False
    
    def _detect_category(self, title: str, content: str) -> str:
        """Detect category using GPT"""
        if not self.use_gpt_categorization:
            return self._detect_category_basic(title, content)
        
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
            print(f"GPT categorization failed: {e}")
            return self._detect_category_basic(title, content)
    
    def _detect_category_basic(self, title: str, content: str) -> str:
        """Basic category detection without GPT"""
        text = f"{title} {content}".lower()
        
        category_keywords = {
            'Politics': ['government', 'president', 'congress', 'senate', 'policy', 'election'],
            'Finance': ['market', 'stock', 'bank', 'investment', 'financial', 'economy'],
            'Technology': ['tech', 'software', 'ai', 'digital', 'cyber', 'innovation'],
            'Business': ['company', 'ceo', 'merger', 'acquisition', 'revenue', 'profit'],
            'International': ['global', 'international', 'foreign', 'trade', 'export'],
            'Environment': ['climate', 'environment', 'carbon', 'renewable', 'pollution'],
            'Healthcare': ['health', 'medical', 'hospital', 'vaccine', 'disease', 'drug']
        }
        
        scores = {}
        for category, keywords in category_keywords.items():
            scores[category] = sum(1 for keyword in keywords if keyword in text)
        
        if scores:
            return max(scores, key=scores.get)
        return "Business"  # Default category
    
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