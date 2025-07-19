# search_engine.py
import json
from typing import List, Dict, Any
from datetime import datetime
import numpy as np
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import diskcache

from config import Config
from faiss_index import FAISSIndexManager

class ContextualSearchEngine:
    def __init__(self):
        self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        self.encoder = SentenceTransformer(Config.EMBEDDING_MODEL)
        self.cache = diskcache.Cache(Config.CACHE_DIR)
        
        # Store articles in memory
        self.articles = {}
        self.article_list = []
        
        # Initialize FAISS index
        self.faiss_index = FAISSIndexManager(dimension=384)
        
    def add_articles(self, articles: List[Dict[str, Any]]):
        """Add articles to the search engine with FAISS indexing"""
        self.article_list = articles
        
        # Create article lookup dict
        self.articles = {art['id']: art for art in articles}
        
        # Generate embeddings for all articles
        texts = [f"{art['title']} {art.get('content', '')[:500]}" for art in articles]
        embeddings = self.encoder.encode(texts, show_progress_bar=True)
        
        # Add to FAISS index (normalization handled by FAISSIndexManager)
        article_ids = [art['id'] for art in articles]
        self.faiss_index.add_embeddings(embeddings, article_ids)
        
    def search(self, query: str) -> Dict[str, Any]:
        """Enhanced search that finds context"""
        
        # Step 1: Understand the query intent
        query_understanding = self._understand_query(query)
        
        # Step 2: Find directly matching articles
        direct_results = self._find_direct_matches(query)
        
        # Step 3: Find contextually related articles
        contextual_results = self._find_contextual_matches(
            query, 
            query_understanding,
            direct_results
        )
        
        # Step 4: Generate insights
        insights = self._generate_insights(query, direct_results, contextual_results)
        
        return {
            "query": query,
            "understanding": query_understanding,
            "direct_results": direct_results,
            "contextual_results": contextual_results,
            "insights": insights,
            "stats": {
                "total_articles_searched": len(self.articles),
                "direct_matches": len(direct_results),
                "contextual_discoveries": len(contextual_results),
                "improvement_factor": self._calculate_improvement(direct_results, contextual_results)
            }
        }
    
    def _understand_query(self, query: str) -> Dict[str, Any]:
        """Use GPT to understand what the user is really looking for"""
        
        # Check cache first
        cache_key = f"understanding_{query}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        prompt = f"""
        Analyze this search query: "{query}"
        
        Return a JSON object with:
        {{
            "primary_intent": "what the user is directly looking for",
            "related_topics": ["list", "of", "related", "topics", "they", "should", "know"],
            "hidden_factors": ["factors", "that", "might", "affect", "this", "topic"],
            "entity_types": ["companies", "people", "technologies", "etc"],
            "time_sensitivity": "high/medium/low",
            "search_expansion_terms": ["additional", "search", "terms"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=Config.GPT_MODEL,
                messages=[
                    {"role": "system", "content": "You are a search query analyzer."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                temperature=0.3
            )
            
            result = json.loads(response.choices[0].message.content)
            self.cache.set(cache_key, result, expire=Config.CACHE_EXPIRY)
            return result
            
        except Exception as e:
            print(f"Error understanding query: {e}")
            return {
                "primary_intent": query,
                "related_topics": [],
                "hidden_factors": [],
                "entity_types": [],
                "time_sensitivity": "medium",
                "search_expansion_terms": []
            }
    
    def _find_direct_matches(self, query: str) -> List[Dict[str, Any]]:
        """Find articles that directly match the query using FAISS"""
        
        if not self.articles:
            return []
        
        # Generate query embedding
        query_embedding = self.encoder.encode(query)
        
        # Search using FAISS
        search_results = self.faiss_index.search(
            query_embedding, 
            k=Config.MAX_SEARCH_RESULTS,
            similarity_threshold=Config.SIMILARITY_THRESHOLD
        )
        
        results = []
        for article_id, score in search_results:
            article = self.articles[article_id].copy()
            article['relevance_score'] = score
            article['match_type'] = 'direct'
            results.append(article)
        
        return results
    
    def _find_contextual_matches(
        self, 
        query: str, 
        understanding: Dict[str, Any],
        direct_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find articles that provide important context"""
        
        # Expand search based on understanding
        expanded_queries = [query] + understanding.get('search_expansion_terms', [])
        expanded_queries += understanding.get('related_topics', [])[:3]
        
        contextual_articles = []
        seen_ids = {art.get('id', art.get('url', '')) for art in direct_results}
        
        # Full scan mode: Check ALL articles for contextual relevance
        if Config.ENABLE_FULL_SCAN:
            # Process articles in batches for efficiency
            batch_size = 5
            for i in range(0, len(self.article_list), batch_size):
                batch = self.article_list[i:i+batch_size]
                
                for article in batch:
                    article_id = article.get('id', article.get('url', ''))
                    
                    if article_id not in seen_ids:
                        # Use GPT to check contextual relevance
                        relevance = self._check_contextual_relevance(
                            query, 
                            article,
                            understanding
                        )
                        
                        if relevance['is_relevant']:
                            article_copy = article.copy()
                            # Get similarity score for ranking
                            article_embedding = self.faiss_index.get_embedding(article_id)
                            query_embedding = self.encoder.encode(query)
                            similarity = np.dot(article_embedding, query_embedding) if article_embedding is not None else 0.5
                            
                            article_copy['relevance_score'] = float(similarity)
                            article_copy['match_type'] = 'contextual'
                            article_copy['context_explanation'] = relevance['explanation']
                            article_copy['impact_level'] = relevance['impact']
                            article_copy['confidence'] = relevance.get('confidence', 0.7)
                            contextual_articles.append(article_copy)
                            seen_ids.add(article_id)
        else:
            # Original expansion-based search using FAISS
            for expanded_query in expanded_queries[1:]:  # Skip original query
                exp_embedding = self.encoder.encode(expanded_query)
                search_results = self.faiss_index.search(exp_embedding, k=5)
                
                for article_id, score in search_results:
                    if article_id not in seen_ids and score > 0.6:
                        article = self.articles[article_id]
                        relevance = self._check_contextual_relevance(
                            query, 
                            article,
                            understanding
                        )
                        
                        if relevance['is_relevant']:
                            article_copy = article.copy()
                            article_copy['relevance_score'] = score
                            article_copy['match_type'] = 'contextual'
                            article_copy['context_explanation'] = relevance['explanation']
                            article_copy['impact_level'] = relevance['impact']
                            contextual_articles.append(article_copy)
                            seen_ids.add(article_id)
        
        # Sort by relevance and impact
        contextual_articles.sort(
            key=lambda x: (x.get('impact_level', '') == 'high', x['relevance_score']), 
            reverse=True
        )
        
        return contextual_articles[:Config.CONTEXT_SEARCH_DEPTH]
    
    def _check_contextual_relevance(
        self, 
        query: str, 
        article: Dict[str, Any],
        understanding: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Use GPT to check if an article provides relevant context"""
        
        # Quick check to save API calls
        cache_key = f"relevance_{query}_{article.get('url', article.get('title', ''))}"
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        prompt = f"""
        Original search: "{query}"
        User is looking for: {understanding.get('primary_intent', query)}
        
        Found article: "{article.get('title', '')}"
        Preview: {article.get('content', '')[:200]}
        
        Does this article provide important context for the original search?
        Consider these connection types:
        - Supply chain: Does this affect production, sourcing, or logistics?  
        - Regulatory: Legal/compliance impacts?
        - Competitive: Market dynamics or competitor actions?
        - Financial: Revenue, costs, or market impacts?
        - Technological: Dependencies or innovations?
        - Geopolitical: Trade, sanctions, or international relations?
        
        Return JSON:
        {{
            "is_relevant": true/false,
            "explanation": "one sentence explaining the connection",
            "impact": "high/medium/low",
            "connection_type": "supply_chain/regulatory/competitive/financial/technological/geopolitical/other",
            "confidence": 0.0-1.0
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=Config.GPT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.3,
                max_tokens=150
            )
            
            result = json.loads(response.choices[0].message.content)
            self.cache.set(cache_key, result, expire=Config.CACHE_EXPIRY)
            return result
            
        except Exception as e:
            print(f"Error checking relevance: {e}")
            return {"is_relevant": False, "explanation": "", "impact": "low"}
    
    def _generate_insights(
        self, 
        query: str,
        direct_results: List[Dict[str, Any]],
        contextual_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate insights about the search results"""
        
        if not contextual_results:
            return {
                "summary": f"Found {len(direct_results)} articles about {query}",
                "key_findings": [],
                "hidden_factors": []
            }
        
        # Prepare context for GPT
        context = f"Search query: {query}\n\n"
        context += "Direct results:\n"
        for r in direct_results[:3]:
            context += f"- {r.get('title', '')}\n"
        
        context += "\nContextual discoveries:\n"
        for r in contextual_results:
            context += f"- {r.get('title', '')} ({r.get('context_explanation', '')})\n"
        
        prompt = f"""
        {context}
        
        Generate insights about what these results reveal together.
        Return JSON:
        {{
            "summary": "2-3 sentence executive summary",
            "key_findings": ["list", "of", "key", "insights"],
            "hidden_factors": ["factors affecting this topic not obvious from direct search"],
            "action_items": ["what the searcher should investigate next"]
        }}
        """
        
        try:
            response = self.client.chat.completions.create(
                model=Config.GPT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                temperature=0.5
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error generating insights: {e}")
            return {
                "summary": "Analysis complete",
                "key_findings": [],
                "hidden_factors": []
            }
    
    def _calculate_improvement(
        self, 
        direct_results: List[Dict[str, Any]], 
        contextual_results: List[Dict[str, Any]]
    ) -> float:
        """Calculate how much we improved the search"""
        
        if not direct_results:
            return 0.0
        
        direct_count = len(direct_results)
        total_count = direct_count + len(contextual_results)
        
        # Calculate improvement percentage
        improvement = ((total_count / direct_count) - 1) * 100 if direct_count > 0 else 0
        
        # Bonus for high-impact discoveries
        high_impact_count = sum(1 for r in contextual_results if r.get('impact_level') == 'high')
        improvement += high_impact_count * 20
        
        return round(improvement)