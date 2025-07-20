"""
Core Relationship Discovery Engine
Discovers hidden cause-and-effect relationships between news articles
"""

import json
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import diskcache

from .config import (
    OPENAI_API_KEY, DEFAULT_MODEL, ADVANCED_MODEL,
    RELATIONSHIP_TYPES, RELATIONSHIP_CONFIDENCE_THRESHOLD,
    TEMPORAL_WINDOW_DAYS, SIMILARITY_THRESHOLD,
    MAX_RELATIONSHIPS_PER_ARTICLE, BATCH_SIZE_FOR_GPT,
    ENABLE_FULL_SCAN, CACHE_DIR, CACHE_TTL_SECONDS
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Relationship:
    """Represents a relationship between two articles"""
    source_id: int
    target_id: int
    relationship_type: str
    confidence: float
    explanation: str
    impact_level: str = "PRIMARY"
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'type': self.relationship_type,
            'confidence': self.confidence,
            'explanation': self.explanation,
            'impact_level': self.impact_level,
            'discovered_at': self.discovered_at
        }


@dataclass
class RelationshipContext:
    """Context for relationship discovery"""
    source_article: Dict[str, Any]
    candidate_articles: List[Dict[str, Any]]
    time_window: timedelta


class RelationshipDiscoveryEngine:
    """
    Discovers relationships between news articles using:
    1. Entity overlap detection
    2. Temporal proximity analysis
    3. GPT-powered causation inference
    4. Pattern matching against known relationship types
    """
    
    def __init__(self, news_data_path: str = "news.json"):
        """Initialize the relationship discovery engine"""
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.cache = diskcache.Cache(CACHE_DIR) if CACHE_DIR else None
        
        # Load news data
        with open(news_data_path, 'r', encoding='utf-8') as f:
            self.news_data = json.load(f)
        self.articles = {article['id']: article for article in self.news_data['articles']}
        
        # Pre-compute embeddings for all articles
        self._compute_article_embeddings()
        
        logger.info(f"Initialized RelationshipDiscoveryEngine with {len(self.articles)} articles")
    
    def _compute_article_embeddings(self):
        """Pre-compute embeddings for all articles"""
        logger.info("Computing article embeddings...")
        
        # Create text representation for each article
        article_texts = []
        for article in self.articles.values():
            text = f"{article['title']} {article['content'][:500]}"
            article_texts.append(text)
        
        # Compute embeddings
        embeddings = self.embedding_model.encode(article_texts)
        
        # Store embeddings with articles
        for idx, article_id in enumerate(self.articles.keys()):
            self.articles[article_id]['embedding'] = embeddings[idx]
        
        logger.info("Computed embeddings for all articles")
    
    def discover_relationships(self, 
                             article_id: int, 
                             max_relationships: Optional[int] = None) -> List[Relationship]:
        """
        Discover all relationships for a given article
        
        Args:
            article_id: ID of the article to analyze
            max_relationships: Maximum number of relationships to return
            
        Returns:
            List of discovered relationships
        """
        if article_id not in self.articles:
            raise ValueError(f"Article {article_id} not found")
        
        source_article = self.articles[article_id]
        max_rels = max_relationships or MAX_RELATIONSHIPS_PER_ARTICLE
        
        # Check cache first
        cache_key = f"relationships_{article_id}_{max_rels}"
        if self.cache and cache_key in self.cache:
            logger.info(f"Returning cached relationships for article {article_id}")
            return [Relationship(**r) for r in self.cache[cache_key]]
        
        # Find candidate articles
        candidates = self._find_candidate_articles(source_article)
        logger.info(f"Found {len(candidates)} candidate articles for relationship analysis")
        
        # Discover relationships
        relationships = []
        
        # Process in batches for efficiency
        for i in range(0, len(candidates), BATCH_SIZE_FOR_GPT):
            batch = candidates[i:i + BATCH_SIZE_FOR_GPT]
            batch_relationships = self._analyze_relationships_batch(source_article, batch)
            relationships.extend(batch_relationships)
            
            # Stop if we have enough relationships
            if len(relationships) >= max_rels:
                break
        
        # Sort by confidence and limit
        relationships.sort(key=lambda r: r.confidence, reverse=True)
        relationships = relationships[:max_rels]
        
        # Cache results
        if self.cache:
            self.cache.set(
                cache_key, 
                [r.to_dict() for r in relationships],
                expire=CACHE_TTL_SECONDS
            )
        
        logger.info(f"Discovered {len(relationships)} relationships for article {article_id}")
        return relationships
    
    def _find_candidate_articles(self, source_article: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find candidate articles that might be related"""
        candidates = []
        source_timestamp = datetime.fromisoformat(source_article['timestamp'].replace('Z', '+00:00'))
        
        for article in self.articles.values():
            if article['id'] == source_article['id']:
                continue
            
            # Temporal filter
            article_timestamp = datetime.fromisoformat(article['timestamp'].replace('Z', '+00:00'))
            time_diff = abs((article_timestamp - source_timestamp).days)
            
            if time_diff > TEMPORAL_WINDOW_DAYS:
                continue
            
            # Entity overlap filter
            source_entities = set(source_article.get('entities', []))
            article_entities = set(article.get('entities', []))
            entity_overlap = len(source_entities & article_entities) / max(len(source_entities), 1)
            
            # Embedding similarity
            if 'embedding' in source_article and 'embedding' in article:
                similarity = np.dot(source_article['embedding'], article['embedding'])
                similarity = float(similarity)
            else:
                similarity = 0
            
            # Include if there's entity overlap, high similarity, or full scan is enabled
            if entity_overlap > 0 or similarity > SIMILARITY_THRESHOLD or ENABLE_FULL_SCAN:
                candidates.append({
                    **article,
                    'entity_overlap': entity_overlap,
                    'embedding_similarity': similarity,
                    'temporal_distance': time_diff
                })
        
        # Sort by relevance (entity overlap + embedding similarity)
        candidates.sort(
            key=lambda x: x['entity_overlap'] + x['embedding_similarity'], 
            reverse=True
        )
        
        return candidates
    
    def _analyze_relationships_batch(self, 
                                   source_article: Dict[str, Any], 
                                   candidate_articles: List[Dict[str, Any]]) -> List[Relationship]:
        """Analyze relationships for a batch of candidate articles using GPT"""
        relationships = []
        
        # Prepare batch prompt
        prompt = self._create_batch_analysis_prompt(source_article, candidate_articles)
        
        try:
            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            
            # Parse relationships from response
            for rel_data in result.get('relationships', []):
                if rel_data['confidence'] >= RELATIONSHIP_CONFIDENCE_THRESHOLD:
                    relationship = Relationship(
                        source_id=source_article['id'],
                        target_id=rel_data['target_id'],
                        relationship_type=rel_data['type'],
                        confidence=rel_data['confidence'],
                        explanation=rel_data['explanation'],
                        impact_level=rel_data.get('impact_level', 'PRIMARY')
                    )
                    relationships.append(relationship)
        
        except Exception as e:
            logger.error(f"Error in batch relationship analysis: {e}")
        
        return relationships
    
    def _create_batch_analysis_prompt(self, 
                                    source_article: Dict[str, Any], 
                                    candidates: List[Dict[str, Any]]) -> str:
        """Create prompt for batch relationship analysis"""
        
        # Build relationship type descriptions
        rel_types_desc = "\n".join([
            f"- {key}: {value['description']}"
            for key, value in RELATIONSHIP_TYPES.items()
        ])
        
        # Build candidate summaries
        candidate_summaries = []
        for idx, candidate in enumerate(candidates):
            summary = f"""
Article {candidate['id']}:
Title: {candidate['title']}
Category: {candidate['category']}
Entities: {', '.join(candidate.get('entities', [])[:5])}
Content: {candidate['content'][:200]}...
"""
            candidate_summaries.append(summary)
        
        prompt = f"""
Analyze the relationships between the source article and candidate articles.

SOURCE ARTICLE:
ID: {source_article['id']}
Title: {source_article['title']}
Category: {source_article['category']}
Entities: {', '.join(source_article.get('entities', []))}
Content: {source_article['content'][:300]}...

RELATIONSHIP TYPES:
{rel_types_desc}

CANDIDATE ARTICLES:
{chr(10).join(candidate_summaries)}

For each candidate article, determine:
1. If there's a meaningful relationship with the source article
2. The type of relationship from the list above
3. Confidence level (0.0-1.0)
4. Brief explanation of the relationship
5. Impact level (PRIMARY, SECONDARY, TERTIARY, or QUATERNARY)

Focus on cause-effect relationships, not just topical similarity.

Return a JSON object with:
{{
    "relationships": [
        {{
            "target_id": <article_id>,
            "type": "<RELATIONSHIP_TYPE>",
            "confidence": 0.8,
            "explanation": "Brief explanation",
            "impact_level": "PRIMARY"
        }},
        ...
    ]
}}

Only include relationships with confidence >= 0.6.
"""
        
        return prompt
    
    def find_relationship_chains(self, 
                               start_article_id: int, 
                               end_article_id: int,
                               max_depth: int = 3) -> List[List[int]]:
        """
        Find causal chains connecting two articles
        
        Args:
            start_article_id: Starting article ID
            end_article_id: Target article ID
            max_depth: Maximum chain length
            
        Returns:
            List of paths (each path is a list of article IDs)
        """
        # Build relationship graph
        graph = self._build_relationship_graph()
        
        # Find paths using BFS
        paths = []
        queue = [(start_article_id, [start_article_id])]
        visited = set()
        
        while queue and len(paths) < 5:  # Limit to 5 paths
            current_id, path = queue.pop(0)
            
            if len(path) > max_depth:
                continue
            
            if current_id == end_article_id:
                paths.append(path)
                continue
            
            if current_id in visited:
                continue
            visited.add(current_id)
            
            # Get relationships from current article
            relationships = self.discover_relationships(current_id, max_relationships=10)
            
            for rel in relationships:
                if rel.target_id not in path:  # Avoid cycles
                    queue.append((rel.target_id, path + [rel.target_id]))
        
        return paths
    
    def _build_relationship_graph(self) -> Dict[int, List[Tuple[int, Relationship]]]:
        """Build a graph of all relationships"""
        graph = {}
        
        # Discover relationships for all articles
        for article_id in self.articles.keys():
            relationships = self.discover_relationships(article_id)
            graph[article_id] = [(rel.target_id, rel) for rel in relationships]
        
        return graph
    
    def classify_relationship_type(self, 
                                 source_article: Dict[str, Any], 
                                 target_article: Dict[str, Any]) -> Tuple[str, float, str]:
        """
        Classify the relationship type between two specific articles
        
        Returns:
            Tuple of (relationship_type, confidence, explanation)
        """
        prompt = f"""
Analyze the relationship between these two news articles:

ARTICLE 1:
Title: {source_article['title']}
Content: {source_article['content'][:400]}...

ARTICLE 2:
Title: {target_article['title']}
Content: {target_article['content'][:400]}...

RELATIONSHIP TYPES:
{chr(10).join([f"- {k}: {v['description']}" for k, v in RELATIONSHIP_TYPES.items()])}

Determine:
1. The most appropriate relationship type from Article 1 to Article 2
2. Confidence level (0.0-1.0)
3. Brief explanation

Return JSON:
{{
    "relationship_type": "<TYPE>",
    "confidence": 0.8,
    "explanation": "Article 1 causes/triggers/creates..."
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return (
                result['relationship_type'],
                result['confidence'],
                result['explanation']
            )
        
        except Exception as e:
            logger.error(f"Error classifying relationship: {e}")
            return ("UNKNOWN", 0.0, "Error in classification")
    
    def get_impact_web(self, article_id: int, depth: int = 2) -> Dict[str, Any]:
        """
        Get the full impact web for an article
        
        Args:
            article_id: Source article ID
            depth: How many levels deep to explore
            
        Returns:
            Dictionary representing the impact web
        """
        web = {
            'root': self.articles[article_id],
            'impacts': self._explore_impacts(article_id, depth, visited=set())
        }
        
        return web
    
    def _explore_impacts(self, 
                        article_id: int, 
                        remaining_depth: int,
                        visited: set) -> List[Dict[str, Any]]:
        """Recursively explore impacts"""
        if remaining_depth == 0 or article_id in visited:
            return []
        
        visited.add(article_id)
        relationships = self.discover_relationships(article_id, max_relationships=5)
        
        impacts = []
        for rel in relationships:
            impact = {
                'article': self.articles[rel.target_id],
                'relationship': rel.to_dict(),
                'downstream_impacts': self._explore_impacts(
                    rel.target_id, 
                    remaining_depth - 1,
                    visited.copy()
                ) if remaining_depth > 1 else []
            }
            impacts.append(impact)
        
        return impacts