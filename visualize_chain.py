#!/usr/bin/env python3
"""
Visualize causation chains between news events
Creates interactive HTML visualizations and static images
"""

import argparse
import sys
import json
from typing import List, Dict, Any, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pyvis.network import Network
import networkx as nx
from datetime import datetime

# Add src to path
sys.path.insert(0, 'src')

from src.relationship_engine import RelationshipDiscoveryEngine
from src.causation_analyzer import CausationAnalyzer
from src.knowledge_graph import KnowledgeGraph
from src.config import GRAPH_NODE_COLORS, GRAPH_EDGE_COLORS, RELATIONSHIP_TYPES


class ChainVisualizer:
    """Visualizes causation chains in various formats"""
    
    def __init__(self):
        """Initialize visualization components"""
        print("Initializing Chain Visualizer...")
        self.relationship_engine = RelationshipDiscoveryEngine()
        self.causation_analyzer = CausationAnalyzer(self.relationship_engine)
        self.knowledge_graph = KnowledgeGraph(
            self.relationship_engine,
            self.causation_analyzer
        )
        print("✓ Engines initialized successfully!")
    
    def visualize_causation_chain(self, 
                                 from_event: str, 
                                 to_event: Optional[str] = None,
                                 output_format: str = "html",
                                 output_file: Optional[str] = None):
        """
        Visualize causation chain(s) from an event
        
        Args:
            from_event: Starting event query
            to_event: Optional target event
            output_format: 'html', 'png', or 'both'
            output_file: Output filename (without extension)
        """
        # Find chains
        if to_event:
            print(f"Finding causation chain from '{from_event}' to '{to_event}'...")
            paths = self.knowledge_graph.query_impact_path(from_event, to_event)
            if not paths:
                print("No causation path found between these events")
                return
            
            # Use first path
            chain_data = self._path_to_chain(paths[0])
            title = f"Causation Chain: {from_event} → {to_event}"
            
        else:
            print(f"Building causation chains from '{from_event}'...")
            chains = self.causation_analyzer.build_causation_chain(from_event)
            if not chains:
                print("No causation chains found")
                return
            
            # Use best chain
            chain_data = chains[0]
            title = f"Causation Chain from: {from_event}"
        
        # Generate output filename
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = f"causation_chain_{timestamp}"
        
        # Create visualizations
        if output_format in ["html", "both"]:
            self._create_interactive_visualization(chain_data, title, f"{output_file}.html")
        
        if output_format in ["png", "both"]:
            self._create_static_visualization(chain_data, title, f"{output_file}.png")
    
    def _path_to_chain(self, path: List[Dict[str, Any]]) -> Any:
        """Convert path format to chain format"""
        from src.causation_analyzer import CausationChain, CausationNode, CausationLink
        
        chain = CausationChain()
        
        for i, node_data in enumerate(path):
            if node_data['type'] == 'event':
                # Extract article ID from node_id
                article_id = int(node_data['node_id'].split('_')[1])
                article = self.relationship_engine.articles[article_id]
                
                node = CausationNode(
                    article_id=article_id,
                    title=article['title'],
                    timestamp=article['timestamp'],
                    impact_score=article.get('impact_score', 5.0),
                    entities=article.get('entities', []),
                    category=article.get('category', 'Unknown')
                )
                chain.nodes.append(node)
                
                # Add link if not last node
                if i < len(path) - 1 and 'edge_to_next' in node_data:
                    edge = node_data['edge_to_next']
                    link = CausationLink(
                        source_id=article_id,
                        target_id=int(path[i+1]['node_id'].split('_')[1]),
                        relationship_type=edge['type'],
                        confidence=edge['weight'],
                        explanation=edge.get('explanation', ''),
                        temporal_gap_days=0  # Would need to calculate
                    )
                    chain.links.append(link)
        
        return chain
    
    def _create_interactive_visualization(self, 
                                        chain_data: Any,
                                        title: str,
                                        output_file: str):
        """Create interactive HTML visualization using pyvis"""
        print(f"Creating interactive visualization: {output_file}")
        
        # Create network
        net = Network(
            height="750px", 
            width="100%", 
            bgcolor="#f0f0f0",
            font_color="black",
            directed=True
        )
        
        # Configure physics
        net.set_options("""
        {
            "physics": {
                "enabled": true,
                "solver": "hierarchicalRepulsion",
                "hierarchicalRepulsion": {
                    "nodeDistance": 200,
                    "springLength": 250
                }
            },
            "layout": {
                "hierarchical": {
                    "enabled": true,
                    "direction": "LR",
                    "sortMethod": "directed",
                    "levelSeparation": 300
                }
            },
            "nodes": {
                "shape": "box",
                "font": {
                    "size": 14
                }
            },
            "edges": {
                "arrows": {
                    "to": {
                        "enabled": true,
                        "scaleFactor": 1.2
                    }
                },
                "smooth": {
                    "type": "curvedCW",
                    "roundness": 0.2
                }
            }
        }
        """)
        
        # Add title
        net.heading = title
        
        # Add nodes
        for i, node in enumerate(chain_data.nodes):
            # Determine node color based on impact
            if node.impact_score >= 8:
                color = "#ff4444"  # High impact - red
            elif node.impact_score >= 6:
                color = "#ffaa00"  # Medium impact - orange
            else:
                color = "#44ff44"  # Low impact - green
            
            # Create node label
            label = self._truncate_text(node.title, 40)
            hover_text = (
                f"{node.title}\n\n"
                f"Category: {node.category}\n"
                f"Impact: {node.impact_score}/10\n"
                f"Date: {node.timestamp[:10]}\n"
                f"Entities: {', '.join(node.entities[:5])}"
            )
            
            net.add_node(
                node.article_id,
                label=label,
                title=hover_text,
                color=color,
                size=25 + (node.impact_score * 2),
                level=i,  # For hierarchical layout
                font={"size": 14, "face": "Arial"}
            )
        
        # Add edges
        for link in chain_data.links:
            # Get edge color
            edge_color = GRAPH_EDGE_COLORS.get(link.relationship_type, "#666666")
            
            # Create edge label
            edge_label = link.relationship_type.replace('_', ' ').title()
            hover_text = (
                f"{edge_label}\n"
                f"Confidence: {link.confidence:.2f}\n"
                f"Time gap: {link.temporal_gap_days} days\n\n"
                f"{link.explanation}"
            )
            
            net.add_edge(
                link.source_id,
                link.target_id,
                title=hover_text,
                label=edge_label,
                color=edge_color,
                width=2 + (link.confidence * 3),
                font={"size": 12, "color": "#666666"}
            )
        
        # Add legend as HTML
        legend_html = self._create_legend_html()
        
        # Save with custom HTML
        html = net.generate_html()
        
        # Insert legend into HTML
        html = html.replace(
            '<body>',
            f'<body>{legend_html}'
        )
        
        with open(output_file, 'w') as f:
            f.write(html)
        
        print(f"✓ Interactive visualization saved to: {output_file}")
    
    def _create_static_visualization(self,
                                   chain_data: Any,
                                   title: str,
                                   output_file: str):
        """Create static PNG visualization using matplotlib"""
        print(f"Creating static visualization: {output_file}")
        
        # Create directed graph
        G = nx.DiGraph()
        
        # Add nodes and edges
        pos = {}
        for i, node in enumerate(chain_data.nodes):
            G.add_node(node.article_id, 
                      label=self._truncate_text(node.title, 30),
                      impact=node.impact_score)
            pos[node.article_id] = (i * 3, 0)  # Horizontal layout
        
        for link in chain_data.links:
            G.add_edge(link.source_id, link.target_id,
                      type=link.relationship_type,
                      confidence=link.confidence)
        
        # Create figure
        plt.figure(figsize=(max(12, len(chain_data.nodes) * 3), 8))
        plt.title(title, fontsize=16, fontweight='bold', pad=20)
        
        # Draw nodes
        for node_id, data in G.nodes(data=True):
            # Color based on impact
            impact = data['impact']
            if impact >= 8:
                color = '#ff4444'
            elif impact >= 6:
                color = '#ffaa00'
            else:
                color = '#44ff44'
            
            nx.draw_networkx_nodes(G, pos, 
                                 nodelist=[node_id],
                                 node_color=color,
                                 node_size=1000 + (impact * 100),
                                 alpha=0.9)
        
        # Draw edges with labels
        for (u, v, data) in G.edges(data=True):
            rel_type = data['type']
            confidence = data['confidence']
            
            # Draw edge
            nx.draw_networkx_edges(G, pos,
                                 edgelist=[(u, v)],
                                 edge_color=GRAPH_EDGE_COLORS.get(rel_type, '#666666'),
                                 width=2 + (confidence * 2),
                                 alpha=0.7,
                                 arrows=True,
                                 arrowsize=20,
                                 connectionstyle="arc3,rad=0.1")
            
            # Add edge label
            edge_label = rel_type.replace('_', ' ').title()
            mid_x = (pos[u][0] + pos[v][0]) / 2
            mid_y = (pos[u][1] + pos[v][1]) / 2 + 0.2
            
            plt.text(mid_x, mid_y, edge_label,
                    fontsize=9,
                    ha='center',
                    bbox=dict(boxstyle="round,pad=0.3", 
                             facecolor='white', 
                             edgecolor=GRAPH_EDGE_COLORS.get(rel_type, '#666666'),
                             alpha=0.8))
        
        # Draw node labels
        labels = nx.get_node_attributes(G, 'label')
        
        # Draw labels below nodes
        label_pos = {node: (coord[0], coord[1] - 0.6) for node, coord in pos.items()}
        nx.draw_networkx_labels(G, label_pos, labels,
                              font_size=10,
                              font_weight='bold')
        
        # Add timeline
        if chain_data.nodes:
            # Draw timeline axis
            timeline_y = -1.5
            plt.axhline(y=timeline_y, color='gray', linestyle='--', alpha=0.5)
            
            # Add dates
            for i, node in enumerate(chain_data.nodes):
                date = node.timestamp[:10]
                plt.text(i * 3, timeline_y - 0.2, date,
                        fontsize=8,
                        ha='center',
                        color='gray')
        
        # Add legend
        legend_elements = [
            mpatches.Patch(color='#ff4444', label='High Impact (8-10)'),
            mpatches.Patch(color='#ffaa00', label='Medium Impact (6-8)'),
            mpatches.Patch(color='#44ff44', label='Low Impact (1-6)')
        ]
        
        # Add relationship type legend
        for rel_type, color in list(GRAPH_EDGE_COLORS.items())[:5]:
            legend_elements.append(
                mpatches.Patch(color=color, 
                             label=rel_type.replace('_', ' ').title())
            )
        
        plt.legend(handles=legend_elements, 
                  loc='upper right',
                  bbox_to_anchor=(1.15, 1))
        
        # Remove axes
        plt.axis('off')
        
        # Adjust layout and save
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close()
        
        print(f"✓ Static visualization saved to: {output_file}")
    
    def _truncate_text(self, text: str, max_length: int) -> str:
        """Truncate text to maximum length"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def _create_legend_html(self) -> str:
        """Create HTML legend for interactive visualization"""
        legend_html = """
        <div style="position: absolute; top: 10px; right: 10px; 
                    background: white; padding: 10px; 
                    border: 1px solid #ccc; border-radius: 5px;
                    font-family: Arial, sans-serif; font-size: 12px;">
            <h4 style="margin-top: 0;">Legend</h4>
            <div style="margin-bottom: 10px;">
                <strong>Node Colors (Impact):</strong><br>
                <span style="color: #ff4444;">●</span> High (8-10)<br>
                <span style="color: #ffaa00;">●</span> Medium (6-8)<br>
                <span style="color: #44ff44;">●</span> Low (1-6)
            </div>
            <div>
                <strong>Edge Types:</strong><br>
        """
        
        for rel_type, color in list(GRAPH_EDGE_COLORS.items())[:5]:
            label = rel_type.replace('_', ' ').title()
            legend_html += f'<span style="color: {color};">―</span> {label}<br>'
        
        legend_html += """
            </div>
        </div>
        """
        
        return legend_html
    
    def visualize_impact_web(self,
                           article_id: int,
                           depth: int = 2,
                           output_file: str = "impact_web.html"):
        """
        Visualize the complete impact web from an article
        
        Args:
            article_id: Source article ID
            depth: How many levels to explore
            output_file: Output HTML file
        """
        print(f"Creating impact web visualization for article {article_id}...")
        
        # Get impact web
        impact_web = self.relationship_engine.get_impact_web(article_id, depth)
        
        # Create network
        net = Network(
            height="750px",
            width="100%",
            bgcolor="#f0f0f0",
            font_color="black"
        )
        
        # Configure for radial layout
        net.set_options("""
        {
            "physics": {
                "enabled": true,
                "solver": "forceAtlas2Based",
                "forceAtlas2Based": {
                    "gravitationalConstant": -50,
                    "centralGravity": 0.01,
                    "springLength": 200
                }
            }
        }
        """)
        
        # Add root node
        root = impact_web['root']
        net.add_node(
            f"root_{root['id']}",
            label=self._truncate_text(root['title'], 40),
            color="#ff0000",
            size=40,
            font={"size": 16, "face": "Arial", "color": "white"}
        )
        
        # Recursively add impact nodes
        self._add_impact_nodes(net, f"root_{root['id']}", impact_web['impacts'], 1)
        
        # Save visualization
        net.save_graph(output_file)
        print(f"✓ Impact web saved to: {output_file}")
    
    def _add_impact_nodes(self, net: Network, parent_id: str, 
                         impacts: List[Dict[str, Any]], level: int):
        """Recursively add impact nodes to network"""
        # Color gradient based on level
        colors = ["#ff6666", "#ffaa66", "#ffff66", "#66ff66", "#66ffff"]
        color = colors[min(level-1, len(colors)-1)]
        
        for impact in impacts[:10]:  # Limit to prevent overcrowding
            article = impact['article']
            rel = impact['relationship']
            
            node_id = f"level{level}_{article['id']}"
            
            # Add node
            net.add_node(
                node_id,
                label=self._truncate_text(article['title'], 30),
                color=color,
                size=30 - (level * 5),
                level=level
            )
            
            # Add edge
            net.add_edge(
                parent_id,
                node_id,
                title=f"{rel['type']}: {rel['explanation'][:100]}...",
                color=GRAPH_EDGE_COLORS.get(rel['type'], "#666666"),
                width=2
            )
            
            # Add downstream impacts
            if 'downstream_impacts' in impact and impact['downstream_impacts']:
                self._add_impact_nodes(net, node_id, impact['downstream_impacts'], level + 1)


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Visualize causation chains between news events"
    )
    
    parser.add_argument('from_event', help='Starting event (search query)')
    parser.add_argument('to_event', nargs='?', help='Target event (optional)')
    parser.add_argument('-f', '--format', 
                       choices=['html', 'png', 'both'],
                       default='html',
                       help='Output format (default: html)')
    parser.add_argument('-o', '--output',
                       help='Output filename (without extension)')
    parser.add_argument('--impact-web',
                       action='store_true',
                       help='Create impact web instead of chain')
    parser.add_argument('--depth',
                       type=int,
                       default=2,
                       help='Depth for impact web (default: 2)')
    
    args = parser.parse_args()
    
    # Initialize visualizer
    visualizer = ChainVisualizer()
    
    if args.impact_web:
        # Find article ID
        articles = visualizer.relationship_engine.search_articles(args.from_event)
        if articles:
            article_id = articles[0]['id']
            output_file = args.output or f"impact_web_{article_id}.html"
            visualizer.visualize_impact_web(article_id, args.depth, output_file)
        else:
            print(f"No articles found for: {args.from_event}")
    else:
        # Create causation chain visualization
        visualizer.visualize_causation_chain(
            args.from_event,
            args.to_event,
            args.format,
            args.output
        )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nVisualization cancelled")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)