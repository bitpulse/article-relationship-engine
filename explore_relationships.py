#!/usr/bin/env python3
"""
Interactive CLI tool for exploring news relationships
"""

import argparse
import json
import sys
from typing import List, Dict, Any
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.panel import Panel
from rich.columns import Columns
from rich import print as rprint

# Add src to path
sys.path.insert(0, 'src')

from src.relationship_engine import RelationshipDiscoveryEngine
from src.causation_analyzer import CausationAnalyzer
from src.impact_predictor import ImpactPredictor
from src.knowledge_graph import KnowledgeGraph

# Initialize console
console = Console()


class RelationshipExplorer:
    """Interactive explorer for news relationships"""
    
    def __init__(self):
        """Initialize all engines"""
        console.print("[bold cyan]Initializing Relationship Explorer...[/bold cyan]")
        
        try:
            self.relationship_engine = RelationshipDiscoveryEngine()
            self.causation_analyzer = CausationAnalyzer(self.relationship_engine)
            self.impact_predictor = ImpactPredictor(
                self.relationship_engine, 
                self.causation_analyzer
            )
            self.knowledge_graph = KnowledgeGraph(
                self.relationship_engine,
                self.causation_analyzer
            )
            console.print("[bold green]✓ All engines initialized successfully![/bold green]")
        except Exception as e:
            console.print(f"[bold red]Error initializing engines: {e}[/bold red]")
            sys.exit(1)
    
    def search_articles(self, query: str) -> List[Dict[str, Any]]:
        """Search for articles matching query"""
        results = []
        query_lower = query.lower()
        
        for article in self.relationship_engine.articles.values():
            score = 0
            if query_lower in article['title'].lower():
                score += 2
            if query_lower in article['content'].lower():
                score += 1
            
            if score > 0:
                results.append((article, score))
        
        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        return [article for article, _ in results[:10]]
    
    def display_article_summary(self, article: Dict[str, Any]):
        """Display article summary"""
        panel = Panel.fit(
            f"[bold]{article['title']}[/bold]\n\n"
            f"[dim]ID:[/dim] {article['id']} | "
            f"[dim]Date:[/dim] {article['timestamp'][:10]} | "
            f"[dim]Category:[/dim] {article['category']}\n"
            f"[dim]Impact:[/dim] {article['impact_score']}/10 | "
            f"[dim]Sentiment:[/dim] {article['sentiment']}\n\n"
            f"{article['content'][:200]}...",
            title=f"[cyan]Article #{article['id']}[/cyan]",
            border_style="cyan"
        )
        console.print(panel)
    
    def explore_relationships(self, article_id: int):
        """Explore relationships for an article"""
        article = self.relationship_engine.articles.get(article_id)
        if not article:
            console.print(f"[red]Article {article_id} not found[/red]")
            return
        
        # Display article
        self.display_article_summary(article)
        
        # Get relationships
        console.print("\n[bold cyan]Discovering relationships...[/bold cyan]")
        relationships = self.relationship_engine.discover_relationships(article_id)
        
        if not relationships:
            console.print("[yellow]No significant relationships found[/yellow]")
            return
        
        # Display relationships table
        table = Table(title="Discovered Relationships", show_header=True)
        table.add_column("Target Article", style="cyan", width=50)
        table.add_column("Type", style="magenta")
        table.add_column("Confidence", style="green")
        table.add_column("Impact", style="yellow")
        
        for rel in relationships[:10]:
            target = self.relationship_engine.articles[rel.target_id]
            table.add_row(
                f"{target['title'][:47]}...",
                rel.relationship_type,
                f"{rel.confidence:.2f}",
                rel.impact_level
            )
        
        console.print(table)
        
        # Show explanations
        console.print("\n[bold]Relationship Explanations:[/bold]")
        for i, rel in enumerate(relationships[:5], 1):
            target = self.relationship_engine.articles[rel.target_id]
            console.print(f"\n{i}. [cyan]{target['title']}[/cyan]")
            console.print(f"   [dim]{rel.explanation}[/dim]")
    
    def trace_causation_chain(self, query: str):
        """Trace causation chains for a query"""
        console.print(f"\n[bold cyan]Building causation chains for: {query}[/bold cyan]")
        
        chains = self.causation_analyzer.build_causation_chain(query)
        
        if not chains:
            console.print("[yellow]No causation chains found[/yellow]")
            return
        
        # Display chains
        for i, chain in enumerate(chains[:3], 1):
            console.print(f"\n[bold]Chain {i}[/bold] (Confidence: {chain.confidence:.2f})")
            
            # Build tree visualization
            tree = Tree(f"[bold cyan]{chain.nodes[0].title}[/bold cyan]")
            current_branch = tree
            
            for j in range(1, len(chain.nodes)):
                node = chain.nodes[j]
                link = chain.links[j-1]
                
                node_text = (
                    f"[yellow]→[/yellow] {node.title}\n"
                    f"    [dim]{link.relationship_type} "
                    f"({link.confidence:.2f})[/dim]"
                )
                current_branch = current_branch.add(node_text)
            
            console.print(tree)
            
            if chain.pattern_match:
                console.print(f"   [green]Matches pattern: {chain.pattern_match}[/green]")
    
    def predict_impacts(self, article_id: int):
        """Predict future impacts of an article"""
        article = self.relationship_engine.articles.get(article_id)
        if not article:
            console.print(f"[red]Article {article_id} not found[/red]")
            return
        
        # Display article
        self.display_article_summary(article)
        
        # Get predictions
        console.print("\n[bold cyan]Predicting future impacts...[/bold cyan]")
        predictions = self.impact_predictor.predict_ripple_effects(article)
        
        if not predictions:
            console.print("[yellow]No significant impacts predicted[/yellow]")
            return
        
        # Display predictions
        for i, pred in enumerate(predictions[:5], 1):
            timeframe = f"{pred.estimated_timeframe_days[0]}-{pred.estimated_timeframe_days[1]} days"
            
            panel = Panel(
                f"[bold]{pred.predicted_impact}[/bold]\n\n"
                f"[dim]Industries:[/dim] {', '.join(pred.affected_industries)}\n"
                f"[dim]Entities:[/dim] {', '.join(pred.affected_entities[:3])}\n"
                f"[dim]Impact Type:[/dim] {pred.impact_type}\n"
                f"[dim]Timeframe:[/dim] {timeframe}\n"
                f"[dim]Confidence:[/dim] {pred.confidence:.2%}\n\n"
                f"[italic]{pred.reasoning}[/italic]",
                title=f"[yellow]Prediction {i}[/yellow]",
                border_style="yellow"
            )
            console.print(panel)
    
    def show_ripple_effects(self, article_id: int):
        """Show ripple effects from an article"""
        article = self.relationship_engine.articles.get(article_id)
        if not article:
            console.print(f"[red]Article {article_id} not found[/red]")
            return
        
        # Display article
        self.display_article_summary(article)
        
        # Get ripple effects
        console.print("\n[bold cyan]Tracking ripple effects...[/bold cyan]")
        ripple_effects = self.causation_analyzer.track_ripple_effects(article_id)
        
        # Display by impact level
        for level in ['PRIMARY', 'SECONDARY', 'TERTIARY']:
            effects = ripple_effects.get(level, [])
            if effects:
                console.print(f"\n[bold]{level} IMPACTS:[/bold]")
                
                for effect in effects[:5]:
                    article = effect['article']
                    rel = effect['relationship']
                    console.print(
                        f"• [cyan]{article['title']}[/cyan]\n"
                        f"  [dim]{rel['relationship_type']} - "
                        f"{rel['explanation'][:100]}...[/dim]"
                    )
        
        # Show cross-industry impacts
        cross_industry = ripple_effects.get('cross_industry_impacts', {})
        if cross_industry:
            console.print("\n[bold]CROSS-INDUSTRY IMPACTS:[/bold]")
            for industry, impacts in list(cross_industry.items())[:5]:
                console.print(f"\n[yellow]{industry}:[/yellow]")
                for impact in impacts[:3]:
                    console.print(f"  • {self.relationship_engine.articles[impact['article_id']]['title']}")
    
    def find_path(self, from_query: str, to_query: str):
        """Find causal path between two events"""
        console.print(f"\n[bold cyan]Finding path from '{from_query}' to '{to_query}'...[/bold cyan]")
        
        paths = self.knowledge_graph.query_impact_path(from_query, to_query)
        
        if not paths:
            console.print("[yellow]No causal path found[/yellow]")
            return
        
        # Display paths
        for i, path in enumerate(paths[:3], 1):
            console.print(f"\n[bold]Path {i}:[/bold]")
            
            for j, node in enumerate(path):
                if node['type'] == 'event':
                    console.print(f"{j+1}. [cyan]{node['label']}[/cyan]")
                    
                    if 'edge_to_next' in node:
                        edge = node['edge_to_next']
                        console.print(
                            f"   [yellow]↓[/yellow] {edge['type']} "
                            f"[dim](confidence: {edge['weight']:.2f})[/dim]"
                        )
                        if edge['explanation']:
                            console.print(f"   [dim]{edge['explanation'][:80]}...[/dim]")
    
    def show_statistics(self):
        """Show knowledge graph statistics"""
        stats = self.knowledge_graph.get_graph_statistics()
        
        # Create statistics panels
        panels = []
        
        # Overall stats
        overall = Panel(
            f"[bold]Nodes:[/bold] {stats['total_nodes']}\n"
            f"[bold]Edges:[/bold] {stats['total_edges']}\n"
            f"[bold]Patterns:[/bold] {stats['patterns_detected']}\n"
            f"[bold]Avg Degree:[/bold] {stats['avg_degree']:.2f}\n"
            f"[bold]Density:[/bold] {stats['density']:.4f}\n"
            f"[bold]Components:[/bold] {stats['components']}",
            title="[cyan]Overall Statistics[/cyan]",
            border_style="cyan"
        )
        panels.append(overall)
        
        # Node types
        node_types_text = "\n".join([
            f"[bold]{node_type}:[/bold] {count}"
            for node_type, count in stats['node_types'].items()
        ])
        node_panel = Panel(
            node_types_text,
            title="[green]Node Types[/green]",
            border_style="green"
        )
        panels.append(node_panel)
        
        # Edge types
        edge_types_text = "\n".join([
            f"[bold]{edge_type}:[/bold] {count}"
            for edge_type, count in list(stats['edge_types'].items())[:6]
        ])
        edge_panel = Panel(
            edge_types_text,
            title="[yellow]Relationship Types[/yellow]",
            border_style="yellow"
        )
        panels.append(edge_panel)
        
        console.print(Columns(panels))


def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Explore hidden relationships in news articles"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Search command
    search_parser = subparsers.add_parser('search', help='Search for articles')
    search_parser.add_argument('query', help='Search query')
    
    # Relationships command
    rel_parser = subparsers.add_parser('relationships', help='Explore relationships')
    rel_parser.add_argument('article_id', type=int, help='Article ID')
    
    # Chain command
    chain_parser = subparsers.add_parser('chain', help='Trace causation chains')
    chain_parser.add_argument('query', help='Event query')
    
    # Predict command
    predict_parser = subparsers.add_parser('predict', help='Predict future impacts')
    predict_parser.add_argument('article_id', type=int, help='Article ID')
    
    # Ripple command
    ripple_parser = subparsers.add_parser('ripple', help='Show ripple effects')
    ripple_parser.add_argument('article_id', type=int, help='Article ID')
    
    # Path command
    path_parser = subparsers.add_parser('path', help='Find causal path')
    path_parser.add_argument('from_query', help='Starting event')
    path_parser.add_argument('to_query', help='Target event')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show statistics')
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize explorer
    explorer = RelationshipExplorer()
    
    # Execute command
    if args.command == 'search':
        results = explorer.search_articles(args.query)
        if results:
            console.print(f"\n[bold]Found {len(results)} articles:[/bold]")
            for i, article in enumerate(results, 1):
                console.print(
                    f"{i}. [cyan]#{article['id']}[/cyan] {article['title']} "
                    f"[dim]({article['category']}, impact: {article['impact_score']})[/dim]"
                )
        else:
            console.print("[yellow]No articles found[/yellow]")
    
    elif args.command == 'relationships':
        explorer.explore_relationships(args.article_id)
    
    elif args.command == 'chain':
        explorer.trace_causation_chain(args.query)
    
    elif args.command == 'predict':
        explorer.predict_impacts(args.article_id)
    
    elif args.command == 'ripple':
        explorer.show_ripple_effects(args.article_id)
    
    elif args.command == 'path':
        explorer.find_path(args.from_query, args.to_query)
    
    elif args.command == 'stats':
        explorer.show_statistics()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)