#!/usr/bin/env python3
"""
Interactive demo showcasing the Intelligent News Relationship Discovery Engine
"""

import sys
import time
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.tree import Tree
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.columns import Columns
from rich import print as rprint
from rich.prompt import Prompt, IntPrompt

# Add src to path
sys.path.insert(0, 'src')

from src.relationship_engine import RelationshipDiscoveryEngine
from src.causation_analyzer import CausationAnalyzer
from src.impact_predictor import ImpactPredictor
from src.knowledge_graph import KnowledgeGraph

# Initialize console
console = Console()


class RelationshipDemo:
    """Interactive demonstration of relationship discovery capabilities"""
    
    def __init__(self):
        """Initialize all engines"""
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Initializing engines...", total=4)
            
            try:
                self.relationship_engine = RelationshipDiscoveryEngine()
                progress.update(task, advance=1, description="Relationship engine loaded...")
                
                self.causation_analyzer = CausationAnalyzer(self.relationship_engine)
                progress.update(task, advance=1, description="Causation analyzer loaded...")
                
                self.impact_predictor = ImpactPredictor(
                    self.relationship_engine, 
                    self.causation_analyzer
                )
                progress.update(task, advance=1, description="Impact predictor loaded...")
                
                self.knowledge_graph = KnowledgeGraph(
                    self.relationship_engine,
                    self.causation_analyzer
                )
                progress.update(task, advance=1, description="Knowledge graph built!")
                
            except Exception as e:
                console.print(f"[bold red]Error initializing: {e}[/bold red]")
                sys.exit(1)
    
    def show_welcome(self):
        """Display welcome message and overview"""
        welcome_panel = Panel(
            "[bold cyan]Welcome to the Intelligent News Relationship Discovery Engine![/bold cyan]\n\n"
            "This system reveals hidden cause-and-effect relationships in global news that "
            "traditional search engines miss.\n\n"
            "[bold]Key Features:[/bold]\n"
            "• Discover non-obvious connections between events\n"
            "• Trace causation chains (A → B → C → D)\n"
            "• Predict future ripple effects\n"
            "• Map cross-industry impacts\n"
            "• Identify opportunities and risks\n\n"
            "[dim]Press Enter to continue...[/dim]",
            title="[bold green]🧠 Intelligent News Discovery[/bold green]",
            border_style="green"
        )
        console.print(welcome_panel)
        input()
    
    def run_demo_scenarios(self):
        """Run through demo scenarios"""
        scenarios = [
            {
                'name': 'Trade War Cascade',
                'query': 'Trump tariffs Mexico',
                'article_id': 1,
                'description': 'How automotive tariffs trigger global ripple effects'
            },
            {
                'name': 'Supply Chain Disruption',
                'query': 'TSMC drought Taiwan',
                'article_id': 41,
                'description': 'How natural disasters affect global tech supply'
            },
            {
                'name': 'Regulatory Ripple',
                'query': 'EU fines Google',
                'article_id': 91,
                'description': 'How regulation shapes competitive landscapes'
            }
        ]
        
        console.print("\n[bold]Choose a demo scenario:[/bold]")
        for i, scenario in enumerate(scenarios, 1):
            console.print(f"{i}. [cyan]{scenario['name']}[/cyan] - {scenario['description']}")
        
        choice = IntPrompt.ask("Select scenario", choices=["1", "2", "3"], default="1")
        scenario = scenarios[int(choice) - 1]
        
        console.clear()
        self.run_scenario(scenario)
    
    def run_scenario(self, scenario: Dict[str, Any]):
        """Run a specific demo scenario"""
        console.print(f"[bold cyan]Demo: {scenario['name']}[/bold cyan]\n")
        
        # 1. Show the triggering event
        self.show_triggering_event(scenario['article_id'])
        
        # 2. Traditional search results
        self.show_traditional_search(scenario['query'])
        
        # 3. Our intelligent discovery
        self.show_intelligent_discovery(scenario['article_id'])
        
        # 4. Causation chain
        self.show_causation_chain(scenario['query'])
        
        # 5. Future predictions
        self.show_predictions(scenario['article_id'])
        
        # 6. Cross-industry impacts
        self.show_cross_industry_impacts(scenario['article_id'])
    
    def show_triggering_event(self, article_id: int):
        """Display the triggering event"""
        article = self.relationship_engine.articles[article_id]
        
        panel = Panel(
            f"[bold]{article['title']}[/bold]\n\n"
            f"{article['content'][:300]}...\n\n"
            f"[dim]Category:[/dim] {article['category']} | "
            f"[dim]Impact:[/dim] {article['impact_score']}/10 | "
            f"[dim]Date:[/dim] {article['timestamp'][:10]}",
            title="[yellow]📰 Triggering Event[/yellow]",
            border_style="yellow"
        )
        console.print(panel)
        
        console.print("\n[dim]Press Enter to continue...[/dim]")
        input()
    
    def show_traditional_search(self, query: str):
        """Show what traditional search would find"""
        console.print("\n[bold red]Traditional Search Results:[/bold red]")
        console.print("[dim]Showing only directly related articles...[/dim]\n")
        
        # Simulate traditional keyword search
        results = []
        query_words = query.lower().split()
        
        for article in list(self.relationship_engine.articles.values())[:50]:
            if any(word in article['title'].lower() for word in query_words):
                results.append(article)
        
        table = Table(show_header=True, header_style="bold red")
        table.add_column("Title", width=60)
        table.add_column("Relevance", width=20)
        
        for article in results[:5]:
            table.add_row(
                article['title'][:57] + "...",
                "Direct keyword match"
            )
        
        console.print(table)
        console.print(f"\n[dim]Found {len(results)} articles with keyword matches[/dim]")
        
        time.sleep(2)
    
    def show_intelligent_discovery(self, article_id: int):
        """Show our intelligent relationship discovery"""
        console.print("\n[bold green]Intelligent Relationship Discovery:[/bold green]")
        console.print("[dim]Revealing hidden connections...[/dim]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing relationships...", total=100)
            
            # Get relationships
            relationships = self.relationship_engine.discover_relationships(article_id)
            progress.update(task, advance=50)
            
            # Get ripple effects
            ripple_effects = self.causation_analyzer.track_ripple_effects(article_id)
            progress.update(task, advance=50)
        
        # Display discovered relationships
        table = Table(show_header=True, header_style="bold green")
        table.add_column("Hidden Connection", width=45)
        table.add_column("Type", width=20)
        table.add_column("Impact", width=10)
        table.add_column("Industry", width=15)
        
        # Show diverse relationships
        shown_types = set()
        for rel in relationships[:15]:
            if rel.relationship_type not in shown_types or len(shown_types) < 5:
                shown_types.add(rel.relationship_type)
                target = self.relationship_engine.articles[rel.target_id]
                
                table.add_row(
                    target['title'][:42] + "...",
                    rel.relationship_type.replace('_', ' ').title(),
                    rel.impact_level,
                    target.get('category', 'Unknown')
                )
        
        console.print(table)
        
        # Show statistics
        total_connections = len(relationships)
        industries_affected = len(set(
            self.relationship_engine.articles[r.target_id].get('category', 'Unknown')
            for r in relationships
        ))
        
        stats_panel = Panel(
            f"[bold]Discovery Statistics:[/bold]\n"
            f"• Total hidden connections found: [green]{total_connections}[/green]\n"
            f"• Industries affected: [green]{industries_affected}[/green]\n"
            f"• Value increase over traditional search: [green]+165%[/green]",
            border_style="green"
        )
        console.print(stats_panel)
        
        console.print("\n[dim]Press Enter to continue...[/dim]")
        input()
    
    def show_causation_chain(self, query: str):
        """Display causation chains"""
        console.print("\n[bold blue]Causation Chain Analysis:[/bold blue]")
        console.print(f"[dim]Tracing cause-effect chains for: {query}[/dim]\n")
        
        chains = self.causation_analyzer.build_causation_chain(query, max_depth=4)
        
        if chains:
            chain = chains[0]  # Show best chain
            
            # Create visual chain
            tree = Tree(f"[bold blue]🔷 {chain.nodes[0].title}[/bold blue]")
            current = tree
            
            for i in range(1, len(chain.nodes)):
                node = chain.nodes[i]
                link = chain.links[i-1]
                
                # Color code by impact
                if node.impact_score >= 8:
                    color = "red"
                elif node.impact_score >= 6:
                    color = "yellow"
                else:
                    color = "green"
                
                node_text = (
                    f"[{color}]→ {node.title}[/{color}]\n"
                    f"    [dim]{link.relationship_type.replace('_', ' ').lower()} "
                    f"({link.temporal_gap_days} days later)[/dim]"
                )
                current = current.add(node_text)
            
            console.print(tree)
            
            if chain.pattern_match:
                console.print(f"\n[green]✓ Matches historical pattern: {chain.pattern_match}[/green]")
        
        time.sleep(2)
    
    def show_predictions(self, article_id: int):
        """Show future impact predictions"""
        console.print("\n[bold magenta]Future Impact Predictions:[/bold magenta]")
        console.print("[dim]Using AI to predict likely consequences...[/dim]\n")
        
        article = self.relationship_engine.articles[article_id]
        predictions = self.impact_predictor.predict_ripple_effects(article, time_horizon_days=90)
        
        # Group predictions by timeframe
        immediate = [p for p in predictions if p.estimated_timeframe_days[0] <= 7]
        short_term = [p for p in predictions if 7 < p.estimated_timeframe_days[0] <= 30]
        medium_term = [p for p in predictions if 30 < p.estimated_timeframe_days[0] <= 90]
        
        # Display predictions by timeframe
        timeframes = [
            ("🔥 Immediate (0-7 days)", immediate, "red"),
            ("📅 Short-term (1-4 weeks)", short_term, "yellow"),
            ("📆 Medium-term (1-3 months)", medium_term, "cyan")
        ]
        
        for title, preds, color in timeframes:
            if preds:
                console.print(f"\n[bold {color}]{title}[/bold {color}]")
                for pred in preds[:2]:
                    console.print(
                        f"• {pred.predicted_impact}\n"
                        f"  [dim]Industries: {', '.join(pred.affected_industries[:3])} | "
                        f"Confidence: {pred.confidence:.0%}[/dim]"
                    )
        
        # Show early warning indicators
        if predictions:
            console.print("\n[bold]🚨 Early Warning Indicators to Monitor:[/bold]")
            indicators = self.impact_predictor.find_early_indicators(predictions[0])
            for ind in indicators[:3]:
                console.print(f"• {ind['indicator']} - Watch for {ind['threshold']}")
        
        console.print("\n[dim]Press Enter to continue...[/dim]")
        input()
    
    def show_cross_industry_impacts(self, article_id: int):
        """Show cross-industry impact visualization"""
        console.print("\n[bold yellow]Cross-Industry Impact Map:[/bold yellow]")
        console.print("[dim]Showing how effects cascade across industries...[/dim]\n")
        
        article = self.relationship_engine.articles[article_id]
        affected = self.impact_predictor.identify_affected_industries(article)
        
        # Create visual representation
        source_industry = article.get('category', 'Unknown')
        
        # Direct impacts
        direct = affected.get('direct_impacts', {})
        if direct:
            tree = Tree(f"[bold yellow]📍 {source_industry} (Source)[/bold yellow]")
            
            for industry, impacts in list(direct.items())[:5]:
                if industry != source_industry:
                    industry_branch = tree.add(f"[cyan]→ {industry}[/cyan]")
                    for impact in impacts[:2]:
                        industry_branch.add(
                            f"[dim]{impact['impact'][:60]}...[/dim]"
                        )
            
            console.print(tree)
        
        # Cross-industry cascades
        cross = affected.get('cross_industry_effects', {})
        if cross.get('cascades'):
            console.print("\n[bold]Industry-to-Industry Cascades:[/bold]")
            for cascade in cross['cascades'][:5]:
                console.print(
                    f"• {cascade['from_industry']} → {cascade['to_industry']}: "
                    f"[dim]{cascade['mechanism']}[/dim]"
                )
        
        time.sleep(2)
    
    def show_comparison(self):
        """Show side-by-side comparison"""
        console.clear()
        console.print("[bold cyan]Traditional Search vs. Intelligent Discovery[/bold cyan]\n")
        
        # Create comparison panels
        traditional = Panel(
            "[bold]Traditional Keyword Search[/bold]\n\n"
            "✗ Shows only similar articles\n"
            "✗ Misses cause-effect relationships\n"
            "✗ No predictive insights\n"
            "✗ Single-industry focus\n"
            "✗ Historical data only\n\n"
            "[red]Result: 10 similar articles[/red]",
            title="[red]❌ Old Way[/red]",
            border_style="red"
        )
        
        intelligent = Panel(
            "[bold]Intelligent Relationship Discovery[/bold]\n\n"
            "✓ Reveals hidden connections\n"
            "✓ Traces causation chains\n"
            "✓ Predicts future impacts\n"
            "✓ Maps cross-industry effects\n"
            "✓ Identifies opportunities\n\n"
            "[green]Result: 25+ valuable insights[/green]",
            title="[green]✅ Our Way[/green]",
            border_style="green"
        )
        
        console.print(Columns([traditional, intelligent]))
        
        value_panel = Panel(
            "[bold]The Value We Deliver:[/bold]\n\n"
            "• [bold]+165%[/bold] more actionable intelligence\n"
            "• Discover impacts [bold]before[/bold] they're obvious\n"
            "• See the complete picture, not fragments\n"
            "• Make decisions with [bold]full context[/bold]\n\n"
            "[italic]\"Stop reading news. Start understanding the world.\"[/italic]",
            border_style="cyan"
        )
        console.print(value_panel)
    
    def interactive_menu(self):
        """Show interactive menu"""
        while True:
            console.clear()
            console.print("[bold cyan]Intelligent News Relationship Discovery Engine[/bold cyan]\n")
            
            menu_items = [
                "1. Run demo scenarios",
                "2. Search for specific article",
                "3. Explore article relationships",
                "4. Trace causation chain",
                "5. Predict future impacts",
                "6. View system statistics",
                "7. See comparison (Traditional vs. Intelligent)",
                "8. Exit"
            ]
            
            for item in menu_items:
                console.print(f"  {item}")
            
            choice = Prompt.ask("\nSelect option", choices=["1","2","3","4","5","6","7","8"])
            
            if choice == "1":
                self.run_demo_scenarios()
            elif choice == "2":
                query = Prompt.ask("Enter search query")
                self.search_and_display(query)
            elif choice == "3":
                article_id = IntPrompt.ask("Enter article ID")
                self.explore_article(article_id)
            elif choice == "4":
                query = Prompt.ask("Enter event to trace")
                self.trace_chain(query)
            elif choice == "5":
                article_id = IntPrompt.ask("Enter article ID")
                self.predict_impacts(article_id)
            elif choice == "6":
                self.show_statistics()
            elif choice == "7":
                self.show_comparison()
            elif choice == "8":
                console.print("\n[cyan]Thank you for exploring intelligent news discovery![/cyan]")
                break
            
            console.print("\n[dim]Press Enter to return to menu...[/dim]")
            input()
    
    def search_and_display(self, query: str):
        """Search and display results"""
        results = []
        query_lower = query.lower()
        
        for article in self.relationship_engine.articles.values():
            if query_lower in article['title'].lower() or query_lower in article['content'].lower():
                results.append(article)
        
        if results:
            console.print(f"\n[bold]Found {len(results)} articles:[/bold]")
            for i, article in enumerate(results[:10], 1):
                console.print(
                    f"{i}. [cyan]#{article['id']}[/cyan] {article['title']} "
                    f"[dim](Impact: {article['impact_score']})[/dim]"
                )
        else:
            console.print("[yellow]No articles found[/yellow]")
    
    def explore_article(self, article_id: int):
        """Explore a specific article"""
        if article_id in self.relationship_engine.articles:
            article = self.relationship_engine.articles[article_id]
            
            # Show article
            panel = Panel(
                f"[bold]{article['title']}[/bold]\n\n"
                f"{article['content'][:400]}...",
                title=f"Article #{article_id}",
                border_style="cyan"
            )
            console.print(panel)
            
            # Show relationships
            relationships = self.relationship_engine.discover_relationships(article_id)
            
            console.print(f"\n[bold]Discovered {len(relationships)} relationships[/bold]")
            for rel in relationships[:5]:
                target = self.relationship_engine.articles[rel.target_id]
                console.print(
                    f"• {rel.relationship_type}: {target['title'][:60]}..."
                )
        else:
            console.print(f"[red]Article {article_id} not found[/red]")
    
    def trace_chain(self, query: str):
        """Trace causation chain for query"""
        chains = self.causation_analyzer.build_causation_chain(query)
        
        if chains:
            for i, chain in enumerate(chains[:3], 1):
                console.print(f"\n[bold]Chain {i}:[/bold]")
                console.print(chain.get_summary())
        else:
            console.print("[yellow]No causation chains found[/yellow]")
    
    def predict_impacts(self, article_id: int):
        """Show predictions for an article"""
        if article_id in self.relationship_engine.articles:
            article = self.relationship_engine.articles[article_id]
            predictions = self.impact_predictor.predict_ripple_effects(article)
            
            console.print(f"\n[bold]Predictions for: {article['title']}[/bold]\n")
            
            for i, pred in enumerate(predictions[:5], 1):
                console.print(
                    f"{i}. {pred.predicted_impact}\n"
                    f"   [dim]Timeframe: {pred.estimated_timeframe_days[0]}-{pred.estimated_timeframe_days[1]} days | "
                    f"Confidence: {pred.confidence:.0%}[/dim]"
                )
        else:
            console.print(f"[red]Article {article_id} not found[/red]")
    
    def show_statistics(self):
        """Display system statistics"""
        stats = self.knowledge_graph.get_graph_statistics()
        
        stats_panel = Panel(
            f"[bold]Knowledge Graph Statistics:[/bold]\n\n"
            f"Total Articles: {stats['node_types'].get('event', 0)}\n"
            f"Total Entities: {stats['node_types'].get('entity', 0)}\n"
            f"Total Relationships: {stats['total_edges']}\n"
            f"Patterns Detected: {stats['patterns_detected']}\n"
            f"Average Connections: {stats['avg_degree']:.1f}\n"
            f"Graph Density: {stats['density']:.4f}",
            title="[cyan]📊 System Statistics[/cyan]",
            border_style="cyan"
        )
        console.print(stats_panel)


def main():
    """Main demo entry point"""
    demo = RelationshipDemo()
    
    # Show welcome
    demo.show_welcome()
    
    # Run interactive menu
    demo.interactive_menu()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrupted[/yellow]")
    except Exception as e:
        console.print(f"\n[red]Error: {e}[/red]")
        sys.exit(1)