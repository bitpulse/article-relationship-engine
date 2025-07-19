"""
Knowledge Graph Builder - Constructs and queries the news relationship knowledge graph
"""

import json
import logging
from typing import List, Dict, Any, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import numpy as np

from .config import (
    GRAPH_NODE_COLORS, GRAPH_EDGE_COLORS,
    RELATIONSHIP_TYPES, IMPACT_LEVELS
)
from .relationship_engine import RelationshipDiscoveryEngine, Relationship
from .causation_analyzer import CausationAnalyzer, CausationChain

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class GraphNode:
    """Represents a node in the knowledge graph"""
    node_id: str
    node_type: str  # 'event', 'entity', 'concept', 'impact'
    label: str
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.node_id,
            'type': self.node_type,
            'label': self.label,
            'properties': self.properties
        }


@dataclass
class GraphEdge:
    """Represents an edge in the knowledge graph"""
    source_id: str
    target_id: str
    edge_type: str
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source': self.source_id,
            'target': self.target_id,
            'type': self.edge_type,
            'weight': self.weight,
            'properties': self.properties
        }


@dataclass
class Pattern:
    """Represents a recurring pattern in the graph"""
    pattern_id: str
    pattern_type: str
    nodes: List[str]
    edges: List[Tuple[str, str, str]]  # (source, target, edge_type)
    frequency: int
    examples: List[Dict[str, Any]]


class KnowledgeGraph:
    """
    Builds and queries a comprehensive knowledge graph from news relationships:
    1. Events as primary nodes
    2. Entities, concepts, and impacts as secondary nodes
    3. Causal relationships as edges
    4. Pattern detection and matching
    5. Path finding and analysis
    """
    
    def __init__(self, 
                 relationship_engine: RelationshipDiscoveryEngine,
                 causation_analyzer: CausationAnalyzer):
        """Initialize with relationship and causation engines"""
        self.relationship_engine = relationship_engine
        self.causation_analyzer = causation_analyzer
        
        # Initialize graph
        self.graph = nx.MultiDiGraph()
        
        # Node and edge registries
        self.nodes = {}
        self.edges = {}
        
        # Pattern registry
        self.patterns = {}
        
        # Build initial graph
        self._build_graph()
        
        logger.info(f"Initialized KnowledgeGraph with {self.graph.number_of_nodes()} nodes "
                   f"and {self.graph.number_of_edges()} edges")
    
    def _build_graph(self):
        """Build the complete knowledge graph"""
        logger.info("Building knowledge graph...")
        
        # 1. Add all articles as event nodes
        for article_id, article in self.relationship_engine.articles.items():
            self.add_event(article)
        
        # 2. Add entities as nodes and connect to events
        self._add_entity_nodes()
        
        # 3. Add relationships between events
        self._add_event_relationships()
        
        # 4. Add concept nodes for categories and impacts
        self._add_concept_nodes()
        
        # 5. Detect and store patterns
        self._detect_patterns()
        
        logger.info("Knowledge graph construction complete")
    
    def add_event(self, 
                  event: Dict[str, Any], 
                  relationships: Optional[List[Relationship]] = None):
        """
        Add an event and its relationships to the graph
        
        Args:
            event: Event article data
            relationships: Optional pre-discovered relationships
        """
        event_id = f"event_{event['id']}"
        
        # Create event node
        event_node = GraphNode(
            node_id=event_id,
            node_type='event',
            label=event['title'][:50] + '...' if len(event['title']) > 50 else event['title'],
            properties={
                'full_title': event['title'],
                'timestamp': event['timestamp'],
                'category': event.get('category', 'Unknown'),
                'impact_score': event.get('impact_score', 5.0),
                'sentiment': event.get('sentiment', 'neutral'),
                'source': event.get('source', 'Unknown'),
                'content_preview': event['content'][:200]
            }
        )
        
        # Add to graph
        self.graph.add_node(
            event_id,
            **event_node.properties,
            node_type='event',
            label=event_node.label
        )
        self.nodes[event_id] = event_node
        
        # Add relationships if provided
        if relationships:
            for rel in relationships:
                self.add_relationship(rel)
    
    def add_relationship(self, relationship: Relationship):
        """Add a relationship edge to the graph"""
        source_id = f"event_{relationship.source_id}"
        target_id = f"event_{relationship.target_id}"
        
        # Create edge
        edge = GraphEdge(
            source_id=source_id,
            target_id=target_id,
            edge_type=relationship.relationship_type,
            weight=relationship.confidence,
            properties={
                'explanation': relationship.explanation,
                'impact_level': relationship.impact_level,
                'discovered_at': relationship.discovered_at
            }
        )
        
        # Add to graph
        self.graph.add_edge(
            source_id,
            target_id,
            key=relationship.relationship_type,
            weight=edge.weight,
            **edge.properties
        )
        
        edge_key = (source_id, target_id, relationship.relationship_type)
        self.edges[edge_key] = edge
    
    def _add_entity_nodes(self):
        """Add entity nodes and connect them to events"""
        entity_events = defaultdict(list)
        
        # Collect entities from all events
        for article_id, article in self.relationship_engine.articles.items():
            event_id = f"event_{article_id}"
            
            for entity in article.get('entities', []):
                entity_id = f"entity_{entity.lower().replace(' ', '_')}"
                entity_events[entity_id].append(event_id)
                
                # Add entity node if not exists
                if entity_id not in self.graph:
                    entity_node = GraphNode(
                        node_id=entity_id,
                        node_type='entity',
                        label=entity,
                        properties={'entity_type': 'organization'}  # Could be enhanced
                    )
                    
                    self.graph.add_node(
                        entity_id,
                        **entity_node.properties,
                        node_type='entity',
                        label=entity_node.label
                    )
                    self.nodes[entity_id] = entity_node
                
                # Connect entity to event
                self.graph.add_edge(
                    entity_id,
                    event_id,
                    key='MENTIONED_IN',
                    weight=1.0
                )
    
    def _add_event_relationships(self):
        """Add relationships between events"""
        processed = set()
        
        for article_id in self.relationship_engine.articles.keys():
            if article_id in processed:
                continue
                
            # Discover relationships
            relationships = self.relationship_engine.discover_relationships(article_id)
            
            for rel in relationships:
                self.add_relationship(rel)
            
            processed.add(article_id)
    
    def _add_concept_nodes(self):
        """Add concept nodes for categories and impact types"""
        # Add category nodes
        categories = set()
        for article in self.relationship_engine.articles.values():
            category = article.get('category', 'Unknown')
            categories.add(category)
        
        for category in categories:
            category_id = f"concept_category_{category.lower()}"
            
            if category_id not in self.graph:
                concept_node = GraphNode(
                    node_id=category_id,
                    node_type='concept',
                    label=f"Category: {category}",
                    properties={'concept_type': 'category'}
                )
                
                self.graph.add_node(
                    category_id,
                    **concept_node.properties,
                    node_type='concept',
                    label=concept_node.label
                )
                self.nodes[category_id] = concept_node
            
            # Connect events to their category
            for article_id, article in self.relationship_engine.articles.items():
                if article.get('category') == category:
                    event_id = f"event_{article_id}"
                    self.graph.add_edge(
                        event_id,
                        category_id,
                        key='BELONGS_TO',
                        weight=1.0
                    )
    
    def _detect_patterns(self):
        """Detect recurring patterns in the graph"""
        # Find common subgraphs (simplified)
        patterns_found = []
        
        # Pattern 1: Cascade patterns (A → B → C)
        cascades = self._find_cascade_patterns()
        patterns_found.extend(cascades)
        
        # Pattern 2: Hub patterns (multiple events affecting one entity)
        hubs = self._find_hub_patterns()
        patterns_found.extend(hubs)
        
        # Pattern 3: Feedback loops
        loops = self._find_feedback_loops()
        patterns_found.extend(loops)
        
        # Store patterns
        for pattern in patterns_found:
            self.patterns[pattern.pattern_id] = pattern
        
        logger.info(f"Detected {len(self.patterns)} patterns")
    
    def _find_cascade_patterns(self) -> List[Pattern]:
        """Find cascade patterns (chain reactions)"""
        patterns = []
        pattern_counter = defaultdict(int)
        
        # Look for paths of length 3+
        for node in self.graph.nodes():
            if not node.startswith('event_'):
                continue
                
            paths = nx.single_source_shortest_path(self.graph, node, cutoff=3)
            
            for target, path in paths.items():
                if len(path) >= 3 and target.startswith('event_'):
                    # Extract pattern signature
                    pattern_sig = []
                    for i in range(len(path) - 1):
                        edges = self.graph.get_edge_data(path[i], path[i + 1])
                        if edges:
                            edge_types = list(edges.keys())
                            pattern_sig.append(edge_types[0])
                    
                    if pattern_sig:
                        pattern_key = tuple(pattern_sig)
                        pattern_counter[pattern_key] += 1
        
        # Create pattern objects for frequent patterns
        for pattern_sig, count in pattern_counter.items():
            if count >= 2:  # At least 2 occurrences
                pattern = Pattern(
                    pattern_id=f"cascade_{len(patterns)}",
                    pattern_type='cascade',
                    nodes=[],  # Would be filled with specific instances
                    edges=list(pattern_sig),
                    frequency=count,
                    examples=[]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _find_hub_patterns(self) -> List[Pattern]:
        """Find hub patterns (central nodes with many connections)"""
        patterns = []
        
        # Find nodes with high in-degree or out-degree
        for node in self.graph.nodes():
            in_degree = self.graph.in_degree(node)
            out_degree = self.graph.out_degree(node)
            
            if in_degree > 5 or out_degree > 5:
                pattern = Pattern(
                    pattern_id=f"hub_{node}",
                    pattern_type='hub',
                    nodes=[node],
                    edges=[],
                    frequency=max(in_degree, out_degree),
                    examples=[]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _find_feedback_loops(self) -> List[Pattern]:
        """Find feedback loop patterns"""
        patterns = []
        
        # Find simple cycles
        try:
            cycles = list(nx.simple_cycles(self.graph))
            
            for cycle in cycles:
                if 2 <= len(cycle) <= 4:  # Reasonable cycle length
                    pattern = Pattern(
                        pattern_id=f"loop_{len(patterns)}",
                        pattern_type='feedback_loop',
                        nodes=cycle,
                        edges=[],
                        frequency=1,
                        examples=[{'cycle': cycle}]
                    )
                    patterns.append(pattern)
        except:
            pass
        
        return patterns
    
    def query_impact_path(self, 
                         from_event: str, 
                         to_effect: str,
                         max_length: int = 5) -> List[List[Dict[str, Any]]]:
        """
        Find causal paths between two events
        
        Args:
            from_event: Starting event (title or ID)
            to_effect: Target effect (title or ID)
            max_length: Maximum path length
            
        Returns:
            List of paths with details
        """
        # Convert to node IDs
        from_id = self._find_node_id(from_event, 'event')
        to_id = self._find_node_id(to_effect, 'event')
        
        if not from_id or not to_id:
            logger.warning(f"Could not find nodes for {from_event} → {to_effect}")
            return []
        
        # Find all simple paths
        paths = []
        try:
            for path in nx.all_simple_paths(self.graph, from_id, to_id, cutoff=max_length):
                path_details = self._get_path_details(path)
                paths.append(path_details)
        except nx.NetworkXNoPath:
            logger.info(f"No path found from {from_event} to {to_effect}")
        
        return paths[:5]  # Return top 5 paths
    
    def _find_node_id(self, query: str, node_type: str = None) -> Optional[str]:
        """Find node ID by query string"""
        query_lower = query.lower()
        
        for node_id, node_data in self.graph.nodes(data=True):
            # Check node type if specified
            if node_type and not node_id.startswith(node_type):
                continue
            
            # Check label
            if 'label' in node_data and query_lower in node_data['label'].lower():
                return node_id
            
            # Check full title for events
            if 'full_title' in node_data and query_lower in node_data['full_title'].lower():
                return node_id
        
        return None
    
    def _get_path_details(self, path: List[str]) -> List[Dict[str, Any]]:
        """Get detailed information about a path"""
        path_details = []
        
        for i in range(len(path)):
            node_data = self.graph.nodes[path[i]]
            node_info = {
                'node_id': path[i],
                'label': node_data.get('label', ''),
                'type': node_data.get('node_type', ''),
                'properties': {k: v for k, v in node_data.items() 
                             if k not in ['label', 'node_type']}
            }
            
            # Add edge information
            if i < len(path) - 1:
                edge_data = self.graph.get_edge_data(path[i], path[i + 1])
                if edge_data:
                    # Get first edge (in case of multi-edge)
                    first_edge_key = list(edge_data.keys())[0]
                    edge_info = edge_data[first_edge_key]
                    node_info['edge_to_next'] = {
                        'type': first_edge_key,
                        'weight': edge_info.get('weight', 1.0),
                        'explanation': edge_info.get('explanation', '')
                    }
            
            path_details.append(node_info)
        
        return path_details
    
    def find_similar_patterns(self, event: Dict[str, Any]) -> List[Pattern]:
        """
        Find historical patterns similar to the given event
        
        Args:
            event: Event to match patterns against
            
        Returns:
            List of similar patterns
        """
        similar_patterns = []
        
        # Get event's relationships
        if 'id' in event:
            event_id = f"event_{event['id']}"
            
            # Check cascade patterns
            for pattern in self.patterns.values():
                if pattern.pattern_type == 'cascade':
                    # Simple similarity: check if event participates in similar cascades
                    similarity = self._calculate_pattern_similarity(event_id, pattern)
                    if similarity > 0.5:
                        similar_patterns.append(pattern)
        
        return similar_patterns
    
    def _calculate_pattern_similarity(self, 
                                    event_id: str, 
                                    pattern: Pattern) -> float:
        """Calculate similarity between an event and a pattern"""
        # Simplified similarity calculation
        similarity = 0.0
        
        # Check if event has similar connections
        event_edges = list(self.graph.edges(event_id, keys=True))
        pattern_edge_types = set(pattern.edges)
        
        for _, _, edge_type in event_edges:
            if edge_type in pattern_edge_types:
                similarity += 0.2
        
        return min(similarity, 1.0)
    
    def visualize_subgraph(self, 
                          center_node: str,
                          depth: int = 2,
                          output_file: str = "knowledge_graph.html"):
        """
        Visualize a subgraph centered on a specific node
        
        Args:
            center_node: Central node (event title or ID)
            depth: How many hops to include
            output_file: Output HTML file
        """
        # Find center node ID
        center_id = self._find_node_id(center_node)
        if not center_id:
            logger.warning(f"Could not find node: {center_node}")
            return
        
        # Get subgraph
        subgraph_nodes = set([center_id])
        current_level = [center_id]
        
        for _ in range(depth):
            next_level = []
            for node in current_level:
                # Add predecessors and successors
                predecessors = list(self.graph.predecessors(node))
                successors = list(self.graph.successors(node))
                
                for neighbor in predecessors + successors:
                    if neighbor not in subgraph_nodes:
                        subgraph_nodes.add(neighbor)
                        next_level.append(neighbor)
            
            current_level = next_level
        
        # Create subgraph
        subgraph = self.graph.subgraph(subgraph_nodes)
        
        # Create interactive visualization
        net = Network(height="750px", width="100%", bgcolor="#222222", font_color="white")
        net.from_nx(subgraph)
        
        # Customize appearance
        for node in net.nodes:
            node_id = node['id']
            if node_id.startswith('event_'):
                node['color'] = GRAPH_NODE_COLORS['event']
                node['size'] = 25
            elif node_id.startswith('entity_'):
                node['color'] = GRAPH_NODE_COLORS['entity']
                node['size'] = 20
            elif node_id.startswith('concept_'):
                node['color'] = GRAPH_NODE_COLORS['concept']
                node['size'] = 15
            
            # Highlight center node
            if node_id == center_id:
                node['size'] = 40
                node['font'] = {'size': 20}
        
        # Customize edges
        for edge in net.edges:
            edge_type = edge.get('key', 'UNKNOWN')
            if edge_type in GRAPH_EDGE_COLORS:
                edge['color'] = GRAPH_EDGE_COLORS[edge_type]
            edge['title'] = f"{edge_type}: {edge.get('explanation', '')}"
        
        # Set physics options
        net.set_options("""
        {
            "physics": {
                "enabled": true,
                "solver": "forceAtlas2Based",
                "stabilization": {
                    "iterations": 100
                }
            }
        }
        """)
        
        # Save visualization
        net.save_graph(output_file)
        logger.info(f"Saved graph visualization to {output_file}")
    
    def get_graph_statistics(self) -> Dict[str, Any]:
        """Get statistics about the knowledge graph"""
        stats = {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'node_types': defaultdict(int),
            'edge_types': defaultdict(int),
            'patterns_detected': len(self.patterns),
            'avg_degree': 0,
            'density': nx.density(self.graph),
            'components': nx.number_weakly_connected_components(self.graph)
        }
        
        # Count node types
        for node_id, node_data in self.graph.nodes(data=True):
            node_type = node_data.get('node_type', 'unknown')
            stats['node_types'][node_type] += 1
        
        # Count edge types
        for _, _, edge_data in self.graph.edges(data=True):
            edge_type = edge_data.get('key', 'unknown')
            stats['edge_types'][edge_type] += 1
        
        # Calculate average degree
        degrees = [self.graph.degree(node) for node in self.graph.nodes()]
        stats['avg_degree'] = np.mean(degrees) if degrees else 0
        
        return stats