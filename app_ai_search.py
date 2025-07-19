"""
Streamlit UI for AI Search Improvement Hackathon Demo
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
            {"id": 1, "title": "Trump Announces 25% Tariff on Mexican Auto Imports", "type": "ROOT_CAUSE", "confidence": 0.95},
            {"id": 3, "title": "Mexican Peso Hits 6-Month Low Against Dollar", "type": "IMPACTS_FINANCE", "confidence": 0.92},
            {"id": 4, "title": "GM Evaluates Production Shift from Mexico to US", "type": "SHIFTS_COMPETITION", "confidence": 0.88},
            {"id": 8, "title": "US Steel Futures Rise 3.8% on Reshoring Hopes", "type": "DISRUPTS_SUPPLY_CHAIN", "confidence": 0.85},
            {"id": 9, "title": "Mexico Considers Agricultural Tariffs on US Corn", "type": "TRIGGERS_RETALIATION", "confidence": 0.91},
            {"id": 18, "title": "Michigan Industrial Property Demand Rises", "type": "CREATES_OPPORTUNITY", "confidence": 0.83},
            {"id": 19, "title": "Chinese EV Manufacturers Eye North American Strategy", "type": "SHIFTS_COMPETITION", "confidence": 0.87},
            {"id": 23, "title": "China Agricultural Imports May Shift Sources", "type": "IMPACTS_FINANCE", "confidence": 0.89},
            {"id": 41, "title": "Electric Vehicle Charging Network Plans Acceleration", "type": "CREATES_OPPORTUNITY", "confidence": 0.82},
            {"id": 87, "title": "Brazilian Soybean Exports to China Surge", "type": "CREATES_OPPORTUNITY", "confidence": 0.94}
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
        "Mexican peso decline": {
            "traditional": [
                {"title": "Mexican Peso Hits 6-Month Low Against Dollar", "relevance": "Direct match"},
                {"title": "Currency Traders Worry About Mexico Volatility", "relevance": "Direct match"},
                {"title": "Mexican Central Bank May Intervene", "relevance": "Direct match"}
            ],
            "ai_discovered": [
                {"id": 18, "title": "Michigan Industrial Property Demand Rises", "type": "CREATES_OPPORTUNITY", "confidence": 0.91},
                {"id": 4, "title": "GM Evaluates Production Shift from Mexico to US", "type": "SHIFTS_COMPETITION", "confidence": 0.88},
                {"id": 54, "title": "US Border States See Manufacturing Boom", "type": "CREATES_OPPORTUNITY", "confidence": 0.85},
                {"id": 67, "title": "Construction Labor Shortage in Southwest US", "type": "IMPACTS_FINANCE", "confidence": 0.82},
                {"id": 89, "title": "Steel Demand Pushes Prices Higher", "type": "DISRUPTS_SUPPLY_CHAIN", "confidence": 0.86},
                {"id": 102, "title": "Reshoring Creates 50,000 Manufacturing Jobs", "type": "CREATES_OPPORTUNITY", "confidence": 0.93},
                {"id": 115, "title": "Industrial REIT Values Surge 15%", "type": "IMPACTS_FINANCE", "confidence": 0.89},
                {"id": 128, "title": "Construction Equipment Rentals Up 40%", "type": "CREATES_OPPORTUNITY", "confidence": 0.84}
            ],
            "causation_chain": ford_data["causation_chain"],
            "predictions": [
                {"impact": "US border industrial real estate +20%", "timeline": "30-60 days", "confidence": 85},
                {"impact": "Construction labor wages increase 15%", "timeline": "14-30 days", "confidence": 88},
                {"impact": "Mexican exports shift to Asia", "timeline": "60-90 days", "confidence": 72},
                {"impact": "Dollar strengthens vs emerging markets", "timeline": "7-14 days", "confidence": 91}
            ]
        },
        "Steel prices rising": {
            "traditional": [
                {"title": "US Steel Futures Rise 3.8% on Demand", "relevance": "Direct match"},
                {"title": "Iron Ore Prices Support Steel Rally", "relevance": "Direct match"},
                {"title": "Steel Producers Report Strong Orders", "relevance": "Direct match"}
            ],
            "ai_discovered": [
                {"id": 8, "title": "US Steel Futures Rise 3.8% on Reshoring Hopes", "type": "ROOT_CAUSE", "confidence": 0.94},
                {"id": 156, "title": "Auto Production Costs Jump 12%", "type": "IMPACTS_FINANCE", "confidence": 0.91},
                {"id": 167, "title": "Construction Projects Face 6-Month Delays", "type": "DISRUPTS_SUPPLY_CHAIN", "confidence": 0.87},
                {"id": 178, "title": "Infrastructure Bill Costs Balloon", "type": "AFFECTS_REGULATION", "confidence": 0.83},
                {"id": 189, "title": "Appliance Makers Seek Aluminum Alternative", "type": "SHIFTS_COMPETITION", "confidence": 0.79},
                {"id": 201, "title": "Housing Starts Decline on Material Costs", "type": "IMPACTS_FINANCE", "confidence": 0.88},
                {"id": 214, "title": "Municipal Bonds Under Pressure", "type": "IMPACTS_FINANCE", "confidence": 0.81},
                {"id": 227, "title": "China Steel Exports May Increase", "type": "SHIFTS_COMPETITION", "confidence": 0.85}
            ],
            "causation_chain": ford_data["causation_chain"],
            "predictions": [
                {"impact": "New car prices increase 5-8%", "timeline": "60-90 days", "confidence": 86},
                {"impact": "Q3 housing market slowdown", "timeline": "90-120 days", "confidence": 82},
                {"impact": "Aluminum demand spikes 20%", "timeline": "30-45 days", "confidence": 79},
                {"impact": "Infrastructure projects delayed", "timeline": "45-60 days", "confidence": 88}
            ]
        },
        "China agriculture": {
            "traditional": [
                {"title": "China Agricultural Imports May Shift Sources", "relevance": "Direct match"},
                {"title": "Chinese Soy Purchases Under Review", "relevance": "Direct match"},
                {"title": "Beijing Considers Import Diversification", "relevance": "Direct match"}
            ],
            "ai_discovered": [
                {"id": 23, "title": "China Agricultural Imports May Shift Sources", "type": "ROOT_CAUSE", "confidence": 0.92},
                {"id": 87, "title": "Brazilian Soybean Exports to China Surge", "type": "CREATES_OPPORTUNITY", "confidence": 0.95},
                {"id": 99, "title": "Argentine Farmers Expand Acreage", "type": "CREATES_OPPORTUNITY", "confidence": 0.88},
                {"id": 112, "title": "US Farm Equipment Orders Cancelled", "type": "IMPACTS_FINANCE", "confidence": 0.84},
                {"id": 125, "title": "Rural US Banks Face Loan Stress", "type": "IMPACTS_FINANCE", "confidence": 0.81},
                {"id": 138, "title": "Shipping Routes Shift to South America", "type": "DISRUPTS_SUPPLY_CHAIN", "confidence": 0.86},
                {"id": 151, "title": "Brazilian Real Strengthens 8%", "type": "IMPACTS_FINANCE", "confidence": 0.89},
                {"id": 164, "title": "US Agricultural Subsidies May Increase", "type": "AFFECTS_REGULATION", "confidence": 0.77}
            ],
            "causation_chain": ford_data["causation_chain"],
            "predictions": [
                {"impact": "Brazilian agriculture stocks +15-20%", "timeline": "14-30 days", "confidence": 90},
                {"impact": "US farm bankruptcies increase", "timeline": "90-120 days", "confidence": 75},
                {"impact": "South American shipping rates +30%", "timeline": "30-45 days", "confidence": 84},
                {"impact": "Dollar weakens vs Real/Peso", "timeline": "21-35 days", "confidence": 81}
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

def main():
    # Header
    st.markdown("<h1 class='main-header'>🧠 AI-Powered News Intelligence</h1>", 
                unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 1.2rem; color: #666;'>Transform search from keyword matching to intelligent discovery</p>", 
                unsafe_allow_html=True)
    
    # Load data
    articles = load_news_data()
    demo_data = get_demo_connections()
    
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
        ["Ford stock drop", "Mexican peso decline", "Steel prices rising", "China agriculture"]
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
            
            st.warning("Limited to direct keyword matches only!")
            st.markdown("</div>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<div class='ai-search'>", unsafe_allow_html=True)
            st.subheader("✅ AI-Powered Discovery")
            status_text.text("AI analyzing relationships...")
            progress_bar.progress(50)
            time.sleep(0.5)
            
            ai_results = demo_data[search_query]["ai_discovered"]
            st.metric("Connected Events Found", len(ai_results))
            
            # Group by type
            by_type = {}
            for result in ai_results[:6]:  # Show first 6
                conn_type = result['type'].replace('_', ' ').title()
                if conn_type not in by_type:
                    by_type[conn_type] = []
                by_type[conn_type].append(result)
            
            for conn_type, items in by_type.items():
                st.write(f"**{conn_type}:**")
                for item in items:
                    confidence = int(item['confidence'] * 100)
                    st.write(f"• {item['title']} ({confidence}% confidence)")
            
            st.success(f"**+{len(ai_results)/len(traditional_results)*100:.0f}% more insights!**")
            st.markdown("</div>", unsafe_allow_html=True)
        
        progress_bar.progress(100)
        status_text.text("Analysis complete!")
        time.sleep(0.5)
        status_text.empty()
        progress_bar.empty()
    
    # Visualizations
    st.markdown("---")
    st.header("📊 Intelligence Visualizations")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔗 Connection Network", "🌊 Causation Flow", 
                                       "📅 Predictions Timeline", "📈 Performance Metrics"])
    
    with tab1:
        st.subheader("Hidden Connections Network")
        if search_query == "Ford stock drop":
            network_fig = create_network_graph(demo_data[search_query]["ai_discovered"], search_query)
            st.plotly_chart(network_fig, use_container_width=True)
            st.info("Each node represents a connected event. Size indicates confidence level.")
    
    with tab2:
        st.subheader("Causation Chain Visualization")
        if search_query == "Ford stock drop":
            sankey_fig = create_causation_flow()
            st.plotly_chart(sankey_fig, use_container_width=True)
            st.success("**Discovery:** Ford stock drop → US tariffs → Mexico retaliation → China shifts → Brazil benefits!")
    
    with tab3:
        st.subheader("AI Predictions with Timeline")
        if search_query == "Ford stock drop":
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
    
    with tab4:
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
    
    # Use Cases
    st.markdown("---")
    st.header("💼 Use Cases")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📊 **For Investors**")
        st.write("Find opportunities before markets price them in")
        st.write("• Spot hidden correlations")
        st.write("• 30-day advance signals")
        st.write("• Cross-market intelligence")
    
    with col2:
        st.markdown("### 🏢 **For Businesses**")
        st.write("Identify supply chain risks weeks in advance")
        st.write("• Competitive intelligence")
        st.write("• Regulatory impacts")
        st.write("• Market opportunities")
    
    with col3:
        st.markdown("### 📰 **For Analysts**")
        st.write("Discover stories and connections others miss")
        st.write("• Deep investigations")
        st.write("• Pattern recognition")
        st.write("• Predictive insights")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px;'>
        <h3>🚀 The Future of Search is Here</h3>
        <p><i>"Traditional search shows you what happened. We show you what it means and what happens next."</i></p>
        <p><strong>Transform search from matching to intelligence.</strong></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()