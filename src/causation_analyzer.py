"""
Causation Analyzer - Builds cause-effect chains from discovered relationships
"""

import json
import logging
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict, deque
import networkx as nx
from openai import OpenAI

from .config import (
    OPENAI_API_KEY, DEFAULT_MODEL, ADVANCED_MODEL,
    MAX_CHAIN_DEPTH, CAUSATION_PATTERNS,
    IMPACT_LEVELS, TEMPORAL_WINDOW_DAYS
)
from .relationship_engine import RelationshipDiscoveryEngine, Relationship

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CausationNode:
    """Represents a node in a causation chain"""
    article_id: int
    title: str
    timestamp: str
    impact_score: float
    entities: List[str]
    category: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.article_id,
            'title': self.title,
            'timestamp': self.timestamp,
            'impact_score': self.impact_score,
            'entities': self.entities,
            'category': self.category
        }


@dataclass
class CausationLink:
    """Represents a causal link between nodes"""
    source_id: int
    target_id: int
    relationship_type: str
    confidence: float
    explanation: str
    temporal_gap_days: float
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source_id': self.source_id,
            'target_id': self.target_id,
            'type': self.relationship_type,
            'confidence': self.confidence,
            'explanation': self.explanation,
            'temporal_gap_days': self.temporal_gap_days
        }


@dataclass
class CausationChain:
    """Represents a complete cause-effect chain"""
    chain_id: str = field(default_factory=lambda: datetime.now().isoformat())
    nodes: List[CausationNode] = field(default_factory=list)
    links: List[CausationLink] = field(default_factory=list)
    pattern_match: Optional[str] = None
    total_impact: float = 0.0
    confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'chain_id': self.chain_id,
            'nodes': [node.to_dict() for node in self.nodes],
            'links': [link.to_dict() for link in self.links],
            'pattern_match': self.pattern_match,
            'total_impact': self.total_impact,
            'confidence': self.confidence,
            'length': len(self.nodes)
        }
    
    def get_summary(self) -> str:
        """Get a human-readable summary of the chain"""
        if not self.nodes:
            return "Empty chain"
        
        summary_parts = []
        for i, node in enumerate(self.nodes):
            if i == 0:
                summary_parts.append(f"STARTS WITH: {node.title}")
            elif i == len(self.nodes) - 1:
                summary_parts.append(f"LEADS TO: {node.title}")
            else:
                summary_parts.append(f"THEN: {node.title}")
        
        return " → ".join(summary_parts)


class CausationAnalyzer:
    """
    Analyzes causation chains in news events:
    1. Builds directed graphs of cause-effect relationships
    2. Identifies root causes and downstream effects
    3. Tracks ripple effects across industries
    4. Matches patterns to known causation templates
    """
    
    def __init__(self, relationship_engine: RelationshipDiscoveryEngine):
        """Initialize with a relationship discovery engine"""
        self.relationship_engine = relationship_engine
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.causation_graph = nx.DiGraph()
        
        # Build initial causation graph
        self._build_causation_graph()
        
        logger.info(f"Initialized CausationAnalyzer with {self.causation_graph.number_of_nodes()} nodes")
    
    def _build_causation_graph(self):
        """Build the complete causation graph from all articles"""
        logger.info("Building causation graph...")
        
        # Add all articles as nodes
        for article_id, article in self.relationship_engine.articles.items():
            self.causation_graph.add_node(
                article_id,
                title=article['title'],
                timestamp=article['timestamp'],
                impact_score=article.get('impact_score', 5.0),
                entities=article.get('entities', []),
                category=article.get('category', 'Unknown')
            )
        
        # Add relationships as edges
        processed_articles = set()
        for article_id in self.relationship_engine.articles.keys():
            if article_id in processed_articles:
                continue
            
            relationships = self.relationship_engine.discover_relationships(article_id)
            for rel in relationships:
                # Calculate temporal gap
                source_time = datetime.fromisoformat(
                    self.relationship_engine.articles[rel.source_id]['timestamp'].replace('Z', '+00:00')
                )
                target_time = datetime.fromisoformat(
                    self.relationship_engine.articles[rel.target_id]['timestamp'].replace('Z', '+00:00')
                )
                temporal_gap = (target_time - source_time).days
                
                self.causation_graph.add_edge(
                    rel.source_id,
                    rel.target_id,
                    relationship_type=rel.relationship_type,
                    confidence=rel.confidence,
                    explanation=rel.explanation,
                    temporal_gap_days=temporal_gap
                )
            
            processed_articles.add(article_id)
        
        logger.info(f"Built graph with {self.causation_graph.number_of_edges()} relationships")
    
    def build_causation_chain(self, event_query: str, max_depth: int = None) -> List[CausationChain]:
        """
        Build causation chains for a given event query
        
        Args:
            event_query: Query describing the event (e.g., "Trump tariffs")
            max_depth: Maximum chain depth (default from config)
            
        Returns:
            List of causation chains
        """
        max_depth = max_depth or MAX_CHAIN_DEPTH
        
        # Find relevant starting articles
        starting_articles = self._find_relevant_articles(event_query)
        if not starting_articles:
            logger.warning(f"No articles found for query: {event_query}")
            return []
        
        chains = []
        for article_id in starting_articles[:3]:  # Limit to top 3 starting points
            article_chains = self._trace_causation_from_article(article_id, max_depth)
            chains.extend(article_chains)
        
        # Deduplicate and rank chains
        chains = self._deduplicate_chains(chains)
        chains = self._rank_chains(chains)
        
        # Match patterns
        for chain in chains:
            chain.pattern_match = self._match_causation_pattern(chain)
        
        return chains[:10]  # Return top 10 chains
    
    def _find_relevant_articles(self, query: str) -> List[int]:
        """Find articles relevant to the query"""
        query_lower = query.lower()
        relevant_articles = []
        
        for article_id, article in self.relationship_engine.articles.items():
            relevance_score = 0
            
            # Check title
            if query_lower in article['title'].lower():
                relevance_score += 2
            
            # Check content
            if query_lower in article['content'].lower():
                relevance_score += 1
            
            # Check entities
            for entity in article.get('entities', []):
                if query_lower in entity.lower():
                    relevance_score += 1.5
            
            if relevance_score > 0:
                relevant_articles.append((article_id, relevance_score))
        
        # Sort by relevance
        relevant_articles.sort(key=lambda x: x[1], reverse=True)
        return [article_id for article_id, _ in relevant_articles]
    
    def _trace_causation_from_article(self, 
                                    start_id: int, 
                                    max_depth: int) -> List[CausationChain]:
        """Trace all causation chains from a starting article"""
        chains = []
        
        # Use DFS to find all paths
        def dfs(current_id: int, 
                path: List[int], 
                visited: Set[int],
                depth: int):
            
            if depth >= max_depth:
                # Create chain from path
                chain = self._create_chain_from_path(path)
                if chain and len(chain.nodes) > 1:
                    chains.append(chain)
                return
            
            # Get outgoing edges (effects)
            for successor in self.causation_graph.successors(current_id):
                if successor not in visited:
                    visited.add(successor)
                    path.append(successor)
                    dfs(successor, path, visited, depth + 1)
                    path.pop()
                    visited.remove(successor)
            
            # Also create chain at current depth if meaningful
            if len(path) > 1:
                chain = self._create_chain_from_path(path)
                if chain:
                    chains.append(chain)
        
        # Start DFS
        visited = {start_id}
        dfs(start_id, [start_id], visited, 0)
        
        return chains
    
    def _create_chain_from_path(self, path: List[int]) -> Optional[CausationChain]:
        """Create a causation chain from a path of article IDs"""
        if len(path) < 2:
            return None
        
        chain = CausationChain()
        
        # Add nodes
        for article_id in path:
            node_data = self.causation_graph.nodes[article_id]
            node = CausationNode(
                article_id=article_id,
                title=node_data['title'],
                timestamp=node_data['timestamp'],
                impact_score=node_data['impact_score'],
                entities=node_data['entities'],
                category=node_data['category']
            )
            chain.nodes.append(node)
        
        # Add links
        total_confidence = 0
        for i in range(len(path) - 1):
            edge_data = self.causation_graph.edges[path[i], path[i + 1]]
            link = CausationLink(
                source_id=path[i],
                target_id=path[i + 1],
                relationship_type=edge_data['relationship_type'],
                confidence=edge_data['confidence'],
                explanation=edge_data['explanation'],
                temporal_gap_days=edge_data['temporal_gap_days']
            )
            chain.links.append(link)
            total_confidence += link.confidence
        
        # Calculate chain metrics
        chain.total_impact = sum(node.impact_score for node in chain.nodes)
        chain.confidence = total_confidence / len(chain.links) if chain.links else 0
        
        return chain
    
    def _deduplicate_chains(self, chains: List[CausationChain]) -> List[CausationChain]:
        """Remove duplicate chains"""
        unique_chains = []
        seen_paths = set()
        
        for chain in chains:
            path_key = tuple(node.article_id for node in chain.nodes)
            if path_key not in seen_paths:
                seen_paths.add(path_key)
                unique_chains.append(chain)
        
        return unique_chains
    
    def _rank_chains(self, chains: List[CausationChain]) -> List[CausationChain]:
        """Rank chains by importance"""
        # Calculate scores for each chain
        for chain in chains:
            # Factors: total impact, confidence, length, temporal coherence
            impact_score = chain.total_impact / len(chain.nodes)
            confidence_score = chain.confidence
            length_score = min(len(chain.nodes) / 3, 1.0)  # Prefer moderate length
            
            # Check temporal coherence (events should follow chronologically)
            temporal_score = 1.0
            for i in range(len(chain.nodes) - 1):
                if chain.links[i].temporal_gap_days < 0:
                    temporal_score *= 0.8  # Penalize backwards time flow
            
            chain.score = (
                impact_score * 0.4 +
                confidence_score * 0.3 +
                length_score * 0.2 +
                temporal_score * 0.1
            )
        
        # Sort by score
        chains.sort(key=lambda c: c.score, reverse=True)
        return chains
    
    def _match_causation_pattern(self, chain: CausationChain) -> Optional[str]:
        """Match chain against known causation patterns"""
        # Extract key concepts from chain
        chain_concepts = []
        for node in chain.nodes:
            # Extract concepts from title and tags
            title_lower = node.title.lower()
            for pattern in CAUSATION_PATTERNS:
                for concept in pattern['sequence']:
                    if concept in title_lower:
                        chain_concepts.append(concept)
        
        # Check each pattern
        best_match = None
        best_score = 0
        
        for pattern in CAUSATION_PATTERNS:
            # Calculate how well the chain matches the pattern sequence
            pattern_seq = pattern['sequence']
            matches = 0
            
            for i, concept in enumerate(pattern_seq):
                if i < len(chain_concepts) and concept in chain_concepts[i]:
                    matches += 1
            
            score = matches / len(pattern_seq)
            if score > best_score and score > 0.5:
                best_score = score
                best_match = pattern['name']
        
        return best_match
    
    def identify_root_causes(self, article_id: int) -> List[Dict[str, Any]]:
        """
        Identify root causes that led to a specific event
        
        Args:
            article_id: The event to analyze
            
        Returns:
            List of root cause articles with paths
        """
        root_causes = []
        
        # Find all ancestors (causes) of this article
        ancestors = nx.ancestors(self.causation_graph, article_id)
        
        for ancestor_id in ancestors:
            # Check if this is a root cause (no predecessors or high impact)
            predecessors = list(self.causation_graph.predecessors(ancestor_id))
            node_data = self.causation_graph.nodes[ancestor_id]
            
            is_root = len(predecessors) == 0 or node_data['impact_score'] >= 8.0
            
            if is_root:
                # Find path from root to target
                try:
                    paths = list(nx.all_simple_paths(
                        self.causation_graph, 
                        ancestor_id, 
                        article_id,
                        cutoff=MAX_CHAIN_DEPTH
                    ))
                    
                    for path in paths[:3]:  # Limit to 3 paths per root
                        chain = self._create_chain_from_path(path)
                        if chain:
                            root_causes.append({
                                'root_article': self.relationship_engine.articles[ancestor_id],
                                'chain': chain.to_dict(),
                                'path_summary': chain.get_summary()
                            })
                except nx.NetworkXNoPath:
                    continue
        
        # Sort by impact
        root_causes.sort(
            key=lambda x: x['root_article']['impact_score'], 
            reverse=True
        )
        
        return root_causes[:5]  # Top 5 root causes
    
    def track_ripple_effects(self, article_id: int, max_hops: int = 3) -> Dict[str, Any]:
        """
        Track ripple effects from an event across industries
        
        Args:
            article_id: The source event
            max_hops: Maximum number of hops to trace
            
        Returns:
            Dictionary of ripple effects by impact level
        """
        ripple_effects = {
            'PRIMARY': [],
            'SECONDARY': [],
            'TERTIARY': [],
            'QUATERNARY': []
        }
        
        # BFS to find effects at each level
        visited = {article_id}
        current_level = [(article_id, 'SOURCE')]
        
        for hop in range(1, max_hops + 1):
            next_level = []
            
            for current_id, _ in current_level:
                # Get all effects (successors)
                for successor_id in self.causation_graph.successors(current_id):
                    if successor_id not in visited:
                        visited.add(successor_id)
                        
                        # Determine impact level based on hop distance
                        if hop == 1:
                            impact_level = 'PRIMARY'
                        elif hop == 2:
                            impact_level = 'SECONDARY'
                        elif hop == 3:
                            impact_level = 'TERTIARY'
                        else:
                            impact_level = 'QUATERNARY'
                        
                        # Get relationship details
                        edge_data = self.causation_graph.edges[current_id, successor_id]
                        
                        effect = {
                            'article': self.relationship_engine.articles[successor_id],
                            'relationship': edge_data,
                            'hop_distance': hop,
                            'impact_propagation': IMPACT_LEVELS[impact_level]['propagation_factor']
                        }
                        
                        ripple_effects[impact_level].append(effect)
                        next_level.append((successor_id, impact_level))
            
            current_level = next_level
        
        # Add cross-industry analysis
        ripple_effects['cross_industry_impacts'] = self._analyze_cross_industry_impacts(
            ripple_effects
        )
        
        return ripple_effects
    
    def _analyze_cross_industry_impacts(self, 
                                      ripple_effects: Dict[str, List]) -> Dict[str, List]:
        """Analyze how effects spread across industries"""
        industry_impacts = defaultdict(list)
        
        for impact_level, effects in ripple_effects.items():
            if impact_level == 'cross_industry_impacts':
                continue
                
            for effect in effects:
                article = effect['article']
                category = article.get('category', 'Unknown')
                
                industry_impacts[category].append({
                    'article_id': article['id'],
                    'title': article['title'],
                    'impact_level': impact_level,
                    'relationship': effect['relationship']
                })
        
        return dict(industry_impacts)
    
    def find_feedback_loops(self) -> List[Dict[str, Any]]:
        """Find feedback loops in the causation graph"""
        feedback_loops = []
        
        # Find all simple cycles
        try:
            cycles = list(nx.simple_cycles(self.causation_graph))
            
            for cycle in cycles:
                if len(cycle) >= 2 and len(cycle) <= 5:  # Reasonable cycle length
                    # Create chain for the cycle
                    cycle_path = cycle + [cycle[0]]  # Complete the loop
                    chain = self._create_chain_from_path(cycle_path[:-1])
                    
                    if chain:
                        feedback_loops.append({
                            'cycle': cycle,
                            'chain': chain.to_dict(),
                            'description': self._describe_feedback_loop(cycle)
                        })
        
        except:
            logger.warning("Error finding feedback loops")
        
        return feedback_loops
    
    def _describe_feedback_loop(self, cycle: List[int]) -> str:
        """Generate description of a feedback loop"""
        descriptions = []
        
        for i in range(len(cycle)):
            article = self.relationship_engine.articles[cycle[i]]
            descriptions.append(article['title'])
        
        return " → ".join(descriptions) + " → (back to start)"