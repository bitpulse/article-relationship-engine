"""
Enhanced Streamlit UI for AI Search Improvement Hackathon Demo
Now with more content display and article browsing
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import networkx as nx
import json
import time
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="AI News Intelligence",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
    }
    .traditional-search {
        background-color: #ffe6e6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #ff4444;
    }
    .ai-search {
        background-color: #e6ffe6;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #44ff44;
    }
    .stCaption {
        font-style: italic;
        color: #555;
        margin-left: 20px;
        margin-top: -5px;
        margin-bottom: 10px;
    }
    .impact-high {
        color: #ff4444;
        font-weight: bold;
    }
    .impact-medium {
        color: #ff8800;
        font-weight: bold;
    }
    .impact-low {
        color: #44ff44;
        font-weight: bold;
    }
    .article-card {
        background-color: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid #1f77b4;
    }
    .article-title {
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 5px;
    }
    .article-meta {
        color: #666;
        font-size: 0.9rem;
    }
    .connection-card {
        background-color: #e8f4fd;
        padding: 15px;
        border-radius: 8px;
        margin-bottom: 10px;
        border-left: 4px solid #2196F3;
        color: #333;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .connection-card strong {
        color: #1976D2;
        font-size: 1.05rem;
    }
    .connection-card em {
        color: #666;
        font-style: normal;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_news_data():
    """Load the news dataset"""
    with open('news.json', 'r') as f:
        data = json.load(f)
    return {article['id']: article for article in data['articles']}

@st.cache_data
def get_demo_connections():
    """Get pre-computed connections for demo"""
    ford_data = {
        "traditional": [
            {"title": "Ford Stock Plunges 8% on Tariff Announcement", "relevance": "Direct match"},
            {"title": "Ford Motor Company Shares Fall in Pre-Market", "relevance": "Direct match"},
            {"title": "Analysts Downgrade Ford on Mexico Exposure", "relevance": "Direct match"}
        ],
        "ai_discovered": [
            {"id": 1, "title": "Trump Announces 25% Tariff on Mexican Auto Imports", "type": "ROOT_CAUSE", "confidence": 0.95, "explanation": "The tariff announcement directly impacts Ford's Mexican production facilities"},
            {"id": 3, "title": "Mexican Peso Hits 6-Month Low Against Dollar", "type": "IMPACTS_FINANCE", "confidence": 0.92, "explanation": "Currency devaluation affects import/export economics"},
            {"id": 4, "title": "GM Evaluates Production Shift from Mexico to US", "type": "SHIFTS_COMPETITION", "confidence": 0.88, "explanation": "Competitors responding similarly creates industry-wide shifts"},
            {"id": 7, "title": "US Steel Futures Rise 3.8% on Reshoring Hopes", "type": "DISRUPTS_SUPPLY_CHAIN", "confidence": 0.94, "explanation": "Domestic production increase drives steel demand"},
            {"id": 27, "title": "Mexican Economic Minister Warns of Retaliation", "type": "TRIGGERS_RETALIATION", "confidence": 0.91, "explanation": "Trade tensions escalate with retaliatory measures"},
            {"id": 34, "title": "Real Estate Markets in Auto Towns Show Activity", "type": "CREATES_OPPORTUNITY", "confidence": 0.83, "explanation": "Manufacturing shifts create real estate opportunities"},
            {"id": 10, "title": "Chinese EV Makers Eye Mexican Market Opportunity", "type": "SHIFTS_COMPETITION", "confidence": 0.87, "explanation": "Market vacuum creates entry opportunity for competitors"},
            {"id": 81, "title": "China Announces Counter-Tariffs on US Agricultural Products", "type": "TRIGGERS_RETALIATION", "confidence": 0.89, "explanation": "Trade war escalates beyond automotive sector"},
            {"id": 85, "title": "Brazilian Soybean Exports to China Surge", "type": "CREATES_OPPORTUNITY", "confidence": 0.94, "explanation": "Agricultural retaliation benefits third-party exporters"}
        ],
        "causation_chain": [
            {"from": "Ford Stock Drop", "to": "Trump Tariffs", "type": "caused by"},
            {"from": "Trump Tariffs", "to": "Mexican Peso Decline", "type": "triggers"},
            {"from": "Trump Tariffs", "to": "Mexico Retaliation", "type": "provokes"},
            {"from": "Mexico Retaliation", "to": "China Shifts Sources", "type": "causes"},
            {"from": "China Shifts Sources", "to": "Brazil Soy Surge", "type": "benefits"}
        ],
        "predictions": [
            {"impact": "Michigan real estate industrial surge", "timeline": "14-30 days", "confidence": 87},
            {"impact": "Chinese EV makers announce Mexico plans", "timeline": "30-60 days", "confidence": 78},
            {"impact": "Auto loan rates increase 0.5-0.75%", "timeline": "7-14 days", "confidence": 92},
            {"impact": "Brazilian agribusiness stocks +10-15%", "timeline": "7-21 days", "confidence": 83}
        ]
    }
    
    return {
        "Ford stock drop": ford_data,
        "Steel prices rising": {
            "traditional": [
                {"title": "US Steel Futures Rise 3.8% on Demand", "relevance": "Direct match"},
                {"title": "Iron Ore Prices Support Steel Rally", "relevance": "Direct match"},
                {"title": "Steel Producers Report Strong Orders", "relevance": "Direct match"}
            ],
            "ai_discovered": [
                {"id": 7, "title": "US Steel Futures Rise 3.8% on Reshoring Hopes", "type": "ROOT_CAUSE", "confidence": 0.94, "explanation": "Reshoring manufacturing drives steel demand"},
                {"id": 14, "title": "US Auto Dealers Warn of Price Increases", "type": "IMPACTS_FINANCE", "confidence": 0.91, "explanation": "Higher material costs pass to consumers"},
                {"id": 9, "title": "Auto Parts Suppliers Brace for Supply Chain Disruption", "type": "DISRUPTS_SUPPLY_CHAIN", "confidence": 0.87, "explanation": "Component availability affects production"},
                {"id": 30, "title": "Environmental Groups Split on Manufacturing Reshoring", "type": "AFFECTS_REGULATION", "confidence": 0.83, "explanation": "Environmental standards may change for domestic production"},
                {"id": 45, "title": "Automotive Paint and Coating Suppliers Adjust", "type": "SHIFTS_COMPETITION", "confidence": 0.79, "explanation": "Material suppliers repositioning for market changes"},
                {"id": 201, "title": "Housing Starts Decline on Material Costs", "type": "IMPACTS_FINANCE", "confidence": 0.88, "explanation": "Construction industry affected by steel prices"},
                {"id": 18, "title": "Aluminum Prices Jump on Auto Manufacturing", "type": "CREATES_OPPORTUNITY", "confidence": 0.82, "explanation": "Alternative materials see increased demand"},
                {"id": 22, "title": "Ohio Steel Mills Report Surge in Inquiries", "type": "CREATES_OPPORTUNITY", "confidence": 0.85, "explanation": "Domestic steel producers benefit from demand"}
            ],
            "causation_chain": ford_data["causation_chain"],
            "predictions": [
                {"impact": "New car prices increase 5-8%", "timeline": "60-90 days", "confidence": 86},
                {"impact": "Q3 housing market slowdown", "timeline": "90-120 days", "confidence": 82},
                {"impact": "Aluminum demand spikes 20%", "timeline": "30-45 days", "confidence": 79},
                {"impact": "Infrastructure projects delayed", "timeline": "45-60 days", "confidence": 88}
            ]
        }
    }

def create_network_graph(connections, query):
    """Create an interactive network visualization"""
    G = nx.DiGraph()
    
    # Add the central node
    G.add_node(query, size=30, color='#ff6666', type='query')
    
    # Add connected nodes
    for conn in connections:
        G.add_node(conn['title'][:40] + '...', 
                  size=20 + conn['confidence'] * 10,
                  color='#66b3ff' if conn['type'].startswith('CREATE') else '#ff9999',
                  type=conn['type'])
        G.add_edge(query, conn['title'][:40] + '...', 
                  weight=conn['confidence'],
                  type=conn['type'])
    
    # Create layout
    pos = nx.spring_layout(G, k=3, iterations=50)
    
    # Create edge trace
    edge_trace = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_trace.append(go.Scatter(x=[x0, x1, None], 
                                   y=[y0, y1, None],
                                   mode='lines',
                                   line=dict(width=2, color='#888'),
                                   hoverinfo='none'))
    
    # Create node trace
    node_trace = go.Scatter(
        x=[pos[node][0] for node in G.nodes()],
        y=[pos[node][1] for node in G.nodes()],
        mode='markers+text',
        text=[node for node in G.nodes()],
        textposition="bottom center",
        hoverinfo='text',
        marker=dict(
            size=[G.nodes[node]['size'] for node in G.nodes()],
            color=[G.nodes[node]['color'] for node in G.nodes()],
            line=dict(color='white', width=2)
        )
    )
    
    # Create figure
    fig = go.Figure(data=edge_trace + [node_trace],
                   layout=go.Layout(
                       showlegend=False,
                       hovermode='closest',
                       margin=dict(b=0,l=0,r=0,t=0),
                       xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                       height=500
                   ))
    
    return fig

def create_causation_flow():
    """Create a Sankey diagram for causation flow"""
    labels = ["Ford Stock Drop", "Trump Tariffs", "Mexican Peso ↓", 
              "Mexico Retaliation", "China Shifts", "Brazil Benefits"]
    
    source = [1, 1, 1, 3, 4]
    target = [0, 2, 3, 4, 5]
    value = [100, 80, 90, 85, 95]
    
    fig = go.Figure(data=[go.Sankey(
        node=dict(
            pad=15,
            thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=["red", "orange", "yellow", "orange", "lightblue", "green"]
        ),
        link=dict(
            source=source,
            target=target,
            value=value,
            color="rgba(0,0,0,0.2)"
        )
    )])
    
    fig.update_layout(title_text="Causation Chain: How Ford Affects Brazil", 
                     font_size=12, height=400)
    return fig

def create_timeline_chart(predictions):
    """Create a timeline visualization for predictions"""
    fig = go.Figure()
    
    colors = ['#ff6b6b', '#ffd93d', '#6bcf7f', '#4ecdc4']
    
    for i, pred in enumerate(predictions):
        # Parse timeline
        timeline_parts = pred['timeline'].split('-')
        min_days = int(timeline_parts[0])
        max_days = int(timeline_parts[1].split()[0])
        
        # Add to timeline
        fig.add_trace(go.Scatter(
            x=[min_days, max_days],
            y=[i, i],
            mode='lines+markers+text',
            name=pred['impact'][:30] + '...',
            line=dict(color=colors[i % len(colors)], width=10),
            marker=dict(size=15),
            text=[f"{pred['confidence']}%", f"{pred['confidence']}%"],
            textposition="top center"
        ))
    
    fig.update_layout(
        title="AI Predictions Timeline",
        xaxis_title="Days from Now",
        yaxis=dict(
            tickmode='array',
            tickvals=list(range(len(predictions))),
            ticktext=[p['impact'][:40] + '...' for p in predictions],
            autorange='reversed'
        ),
        height=400,
        showlegend=False
    )
    
    return fig

def create_comparison_metrics():
    """Create comparison metrics visualization"""
    categories = ['Articles Found', 'Industries Covered', 'Countries Involved', 
                  'Predictive Insights', 'Hidden Connections']
    
    traditional = [3, 1, 1, 0, 0]
    ai_powered = [87, 8, 5, 12, 45]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        name='Traditional Search',
        x=categories,
        y=traditional,
        marker_color='#ff6666'
    ))
    
    fig.add_trace(go.Bar(
        name='AI-Powered Discovery',
        x=categories,
        y=ai_powered,
        marker_color='#66ff66'
    ))
    
    fig.update_layout(
        title="Search Performance Comparison",
        barmode='group',
        height=400,
        yaxis_title="Count"
    )
    
    return fig

def display_article_card(article):
    """Display a single article in a nice card format"""
    impact_color = "#ff4444" if article['impact_score'] >= 8 else "#ff8800" if article['impact_score'] >= 6 else "#44ff44"
    
    st.markdown(f"""
    <div class="article-card">
        <div class="article-title">{article['title']}</div>
        <div class="article-meta">
            <strong>Source:</strong> {article['source']} | 
            <strong>Category:</strong> {article['category']} | 
            <strong>Impact:</strong> <span style="color: {impact_color}">{article['impact_score']}/10</span> |
            <strong>Sentiment:</strong> {article['sentiment']}
        </div>
        <div style="margin-top: 10px;">
            <strong>Entities:</strong> {', '.join(article['entities'][:5])}
        </div>
        <div style="margin-top: 5px;">
            <strong>Tags:</strong> {', '.join(article['tags'][:5])}
        </div>
    </div>
    """, unsafe_allow_html=True)

def main():
    # Header
    st.markdown("<h1 class='main-header'>🧠 AI-Powered News Intelligence</h1>", 
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>Transform search from keyword matching to intelligent discovery</p>", 
                unsafe_allow_html=True)
    
    # Load data
    articles = load_news_data()
    demo_data = get_demo_connections()
    
    # Create tabs for navigation
    tab1, tab2, tab3 = st.tabs(["🔍 Live Demo", "📰 All Articles", "📊 Analytics"])
    
    with tab1:
        # The Hook
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.error("🤔 **The $10 Million Question**")
            st.markdown("""
            **Your company's stock just dropped 8% because of Ford.**
            
            But you don't work in automotive. You're in agriculture. In Brazil.
            
            *How is this possible? And how could you have seen it coming?*
            """)
        
        st.markdown("---")
        
        # Search Demo
        st.header("🔍 Live Search Comparison")
        
        search_query = st.selectbox(
            "Choose a search query:",
            ["Ford stock drop", "Steel prices rising"]
        )
        
        if st.button("🚀 Run Search Comparison", type="primary"):
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Traditional search
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("<div class='traditional-search'>", unsafe_allow_html=True)
                st.subheader("❌ Traditional Search")
                status_text.text("Running traditional keyword search...")
                progress_bar.progress(25)
                time.sleep(0.5)
                
                traditional_results = demo_data[search_query]["traditional"]
                st.metric("Articles Found", len(traditional_results))
                
                for result in traditional_results:
                    st.write(f"• {result['title']}")
                
                st.warning("⚠️ Limited to direct keyword matches only!")
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("<div class='ai-search'>", unsafe_allow_html=True)
                st.subheader("✅ AI-Powered Discovery")
                status_text.text("AI analyzing relationships...")
                progress_bar.progress(50)
                time.sleep(0.5)
                
                ai_results = demo_data[search_query]["ai_discovered"]
                st.metric("Connected Events Found", len(ai_results))
                
                # Group by type with explanations
                st.write("**Root Cause:**")
                for result in [r for r in ai_results if r['type'] == 'ROOT_CAUSE']:
                    confidence = int(result['confidence'] * 100)
                    st.write(f"• {result['title']} ({confidence}% confidence)")
                    st.caption(f"  → {result.get('explanation', 'Direct causal relationship')}")
                
                st.write("\n**Impacts Finance:**")
                for result in [r for r in ai_results if r['type'] == 'IMPACTS_FINANCE'][:2]:
                    confidence = int(result['confidence'] * 100)
                    st.write(f"• {result['title']} ({confidence}% confidence)")
                    st.caption(f"  → {result.get('explanation', 'Financial market impact')}")
                
                st.write("\n**Disrupts Supply Chain:**")
                for result in [r for r in ai_results if r['type'] == 'DISRUPTS_SUPPLY_CHAIN'][:2]:
                    confidence = int(result['confidence'] * 100)
                    st.write(f"• {result['title']} ({confidence}% confidence)")
                    st.caption(f"  → {result.get('explanation', 'Supply chain disruption')}")
                
                # Show other types briefly
                st.write("\n**Affects Regulation:**")
                for result in [r for r in ai_results if r['type'] == 'AFFECTS_REGULATION'][:1]:
                    confidence = int(result['confidence'] * 100)
                    st.write(f"• {result['title']} ({confidence}% confidence)")
                    st.caption(f"  → {result.get('explanation', 'Regulatory impact')}")
                
                st.write("\n**Shifts Competition:**")
                for result in [r for r in ai_results if r['type'] == 'SHIFTS_COMPETITION'][:1]:
                    confidence = int(result['confidence'] * 100)
                    st.write(f"• {result['title']} ({confidence}% confidence)")
                    st.caption(f"  → {result.get('explanation', 'Competitive dynamics shift')}")
                
                st.success(f"**+{len(ai_results)/len(traditional_results)*100:.0f}% more insights!**")
                st.markdown("</div>", unsafe_allow_html=True)
            
            progress_bar.progress(100)
            status_text.text("Analysis complete!")
            time.sleep(0.5)
            status_text.empty()
            progress_bar.empty()
            
            # Show detailed connections with explanations
            st.markdown("---")
            st.subheader("📋 Detailed Connection Analysis")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Top 5 Connected Events:**")
                for i, result in enumerate(ai_results[:5], 1):
                    # Create a colored box for each connection
                    confidence_pct = int(result['confidence'] * 100)
                    relationship_type = result['type'].replace('_', ' ').title()
                    explanation = result.get('explanation', 'Direct causal relationship identified')
                    
                    # Use Streamlit's native components for better rendering
                    with st.container():
                        st.info(f"""
**{i}. {result['title']}**

📊 **Type:** {relationship_type}  
🎯 **Confidence:** {confidence_pct}%  
💡 **Why:** {explanation}
                        """)
            
            with col2:
                # Create network visualization
                st.write("**Relationship Network:**")
                network_fig = create_network_graph(ai_results[:6], search_query)
                st.plotly_chart(network_fig, use_container_width=True)
        
        # Visualizations
        st.markdown("---")
        st.header("📊 Intelligence Visualizations")
        
        tab1_1, tab1_2, tab1_3, tab1_4 = st.tabs(["🌊 Causation Flow", "📅 Predictions Timeline", 
                                                   "📈 Performance", "🎯 Key Insights"])
        
        with tab1_1:
            st.subheader("Causation Chain Visualization")
            if search_query == "Ford stock drop":
                sankey_fig = create_causation_flow()
                st.plotly_chart(sankey_fig, use_container_width=True)
                st.success("**Discovery:** Ford stock drop → US tariffs → Mexico retaliation → China shifts → Brazil benefits!")
        
        with tab1_2:
            st.subheader("AI Predictions with Timeline")
            if search_query in demo_data:
                timeline_fig = create_timeline_chart(demo_data[search_query]["predictions"])
                st.plotly_chart(timeline_fig, use_container_width=True)
                
                # Show prediction cards
                cols = st.columns(2)
                for i, pred in enumerate(demo_data[search_query]["predictions"][:2]):
                    with cols[i % 2]:
                        st.metric(
                            pred['impact'][:30] + '...',
                            f"{pred['timeline']}",
                            f"{pred['confidence']}% confidence"
                        )
        
        with tab1_3:
            st.subheader("Search Performance Comparison")
            metrics_fig = create_comparison_metrics()
            st.plotly_chart(metrics_fig, use_container_width=True)
            
            # Key metrics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Improvement", "+2,800%", "vs traditional search")
            with col2:
                st.metric("Response Time", "<2 sec", "Real-time analysis")
            with col3:
                st.metric("Cost per Search", "$0.08", "High ROI")
            with col4:
                st.metric("Advance Warning", "30 days", "Before markets react")
        
        with tab1_4:
            st.subheader("Key Intelligence Insights")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("""
                **🔍 Pattern Discovered: Trade War Cascade**
                1. US announces tariffs
                2. Target country currency weakens
                3. Retaliatory tariffs announced
                4. Third countries benefit from trade diversion
                5. Supply chains permanently altered
                """)
                
                st.warning("""
                **⚠️ Early Warning Indicators:**
                - Steel price movements (14-day lead)
                - Currency fluctuations (7-day lead)
                - Shipping route changes (21-day lead)
                - Real estate activity in manufacturing zones
                """)
            
            with col2:
                st.success("""
                **💡 Actionable Intelligence:**
                - Brazilian agriculture stocks: BUY signal
                - Mexican peso: Hedging recommended
                - US auto sector: Margin pressure ahead
                - Chinese EV sector: Mexico opportunity
                """)
                
                st.error("""
                **🚨 Risk Factors Identified:**
                - Supply chain disruption imminent
                - Input cost inflation accelerating
                - Regulatory uncertainty increasing
                - Competitive landscape shifting
                """)
    
    with tab2:
        st.header("📰 Complete News Article Database")
        
        # Filter options
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            category_filter = st.selectbox(
                "Filter by Category",
                ["All"] + sorted(list(set(article['category'] for article in articles.values())))
            )
        
        with col2:
            impact_filter = st.selectbox(
                "Filter by Impact Score",
                ["All", "High (8-10)", "Medium (6-8)", "Low (0-6)"]
            )
        
        with col3:
            sentiment_filter = st.selectbox(
                "Filter by Sentiment",
                ["All"] + sorted(list(set(article['sentiment'] for article in articles.values())))
            )
        
        with col4:
            sort_by = st.selectbox(
                "Sort by",
                ["Date (Newest)", "Date (Oldest)", "Impact Score (High)", "Impact Score (Low)"]
            )
        
        # Search box
        search_term = st.text_input("🔍 Search articles by title, content, or entities", "")
        
        # Filter articles
        filtered_articles = []
        for article_id, article in articles.items():
            # Category filter
            if category_filter != "All" and article['category'] != category_filter:
                continue
            
            # Impact filter
            if impact_filter == "High (8-10)" and article['impact_score'] < 8:
                continue
            elif impact_filter == "Medium (6-8)" and (article['impact_score'] < 6 or article['impact_score'] >= 8):
                continue
            elif impact_filter == "Low (0-6)" and article['impact_score'] >= 6:
                continue
            
            # Sentiment filter
            if sentiment_filter != "All" and article['sentiment'] != sentiment_filter:
                continue
            
            # Search filter
            if search_term:
                search_lower = search_term.lower()
                if not any(search_lower in str(field).lower() for field in 
                          [article['title'], article['content'], ' '.join(article['entities'])]):
                    continue
            
            filtered_articles.append(article)
        
        # Sort articles
        if sort_by == "Date (Newest)":
            filtered_articles.sort(key=lambda x: x['timestamp'], reverse=True)
        elif sort_by == "Date (Oldest)":
            filtered_articles.sort(key=lambda x: x['timestamp'])
        elif sort_by == "Impact Score (High)":
            filtered_articles.sort(key=lambda x: x['impact_score'], reverse=True)
        elif sort_by == "Impact Score (Low)":
            filtered_articles.sort(key=lambda x: x['impact_score'])
        
        # Display stats
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Articles", len(articles))
        with col2:
            st.metric("Filtered Articles", len(filtered_articles))
        with col3:
            st.metric("Categories Covered", len(set(a['category'] for a in filtered_articles)) if filtered_articles else 0)
        
        st.markdown("---")
        
        # Display articles in a scrollable container
        st.subheader(f"📄 Articles ({len(filtered_articles)} results)")
        
        # Pagination
        articles_per_page = 10
        if len(filtered_articles) > 0:
            total_pages = (len(filtered_articles) - 1) // articles_per_page + 1
            page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
            
            start_idx = (page - 1) * articles_per_page
            end_idx = min(start_idx + articles_per_page, len(filtered_articles))
            
            for article in filtered_articles[start_idx:end_idx]:
                display_article_card(article)
                
                # Expandable content section
                with st.expander("View full content"):
                    st.write(article['content'])
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write("**Full Entity List:**")
                        st.write(", ".join(article['entities']))
                    with col2:
                        st.write("**Full Tags:**")
                        st.write(", ".join(article['tags']))
        else:
            st.warning("No articles match your filters.")
    
    with tab3:
        st.header("📊 Dataset Analytics")
        
        # Overview metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Articles", len(articles))
            st.metric("Avg Impact Score", f"{sum(a['impact_score'] for a in articles.values()) / len(articles):.1f}")
        
        with col2:
            categories = [a['category'] for a in articles.values()]
            st.metric("Categories", len(set(categories)))
            st.metric("Most Common", max(set(categories), key=categories.count))
        
        with col3:
            sentiments = [a['sentiment'] for a in articles.values()]
            st.metric("Sentiment Types", len(set(sentiments)))
            st.metric("Most Common", max(set(sentiments), key=sentiments.count))
        
        with col4:
            all_entities = []
            for a in articles.values():
                all_entities.extend(a['entities'])
            st.metric("Unique Entities", len(set(all_entities)))
            st.metric("Total Entity Mentions", len(all_entities))
        
        st.markdown("---")
        
        # Visualizations
        col1, col2 = st.columns(2)
        
        with col1:
            # Category distribution
            st.subheader("📊 Articles by Category")
            category_counts = pd.DataFrame.from_dict(
                {cat: sum(1 for a in articles.values() if a['category'] == cat) 
                 for cat in set(a['category'] for a in articles.values())},
                orient='index', columns=['Count']
            ).sort_values('Count', ascending=False)
            
            fig = px.bar(category_counts, y=category_counts.index, x='Count', 
                        orientation='h', color='Count', color_continuous_scale='Blues')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Impact score distribution
            st.subheader("📈 Impact Score Distribution")
            impact_scores = [a['impact_score'] for a in articles.values()]
            fig = px.histogram(x=impact_scores, nbins=20, 
                             labels={'x': 'Impact Score', 'y': 'Number of Articles'},
                             color_discrete_sequence=['#1f77b4'])
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment analysis
        st.subheader("😊 Sentiment Distribution by Category")
        sentiment_data = []
        for article in articles.values():
            sentiment_data.append({
                'Category': article['category'],
                'Sentiment': article['sentiment'],
                'Impact': article['impact_score']
            })
        
        sentiment_df = pd.DataFrame(sentiment_data)
        fig = px.sunburst(sentiment_df, path=['Category', 'Sentiment'], 
                         values='Impact', color='Impact',
                         color_continuous_scale='RdYlGn')
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # Entity network
        st.subheader("🔗 Most Connected Entities")
        entity_connections = {}
        for article in articles.values():
            for entity in article['entities']:
                if entity not in entity_connections:
                    entity_connections[entity] = 0
                entity_connections[entity] += 1
        
        top_entities = sorted(entity_connections.items(), key=lambda x: x[1], reverse=True)[:20]
        
        col1, col2 = st.columns(2)
        with col1:
            st.write("**Top 10 Most Mentioned Entities:**")
            for i, (entity, count) in enumerate(top_entities[:10], 1):
                st.write(f"{i}. **{entity}**: {count} articles")
        
        with col2:
            # Create entity bar chart
            entity_df = pd.DataFrame(top_entities[:10], columns=['Entity', 'Mentions'])
            fig = px.bar(entity_df, x='Mentions', y='Entity', orientation='h',
                        color='Mentions', color_continuous_scale='Viridis')
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    

if __name__ == "__main__":
    main()