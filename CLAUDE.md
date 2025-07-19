# CLAUDE.md - Intelligent News Relationship Discovery Engine

This file provides guidance to Claude Code (claude.ai/code) when working with the Article Relationship Engine - an intelligent system that discovers hidden cause-and-effect relationships in global news.

## 🧠 Core Concept

**Transform isolated news articles into a living knowledge graph that reveals hidden cause-and-effect relationships across seemingly unrelated events.**

Instead of just finding similar articles, we:
- Understand causation chains (A causes B causes C)
- Track ripple effects across industries and borders
- Identify retaliation patterns and competitive responses
- Predict likely future developments
- Map all affected stakeholders, not just the obvious ones

## 🎯 The Intelligence We Provide

### Traditional News Search
Query: "Ford stock drop"
Result: More articles about Ford's stock

### Our Intelligent Discovery
Query: "Ford stock drop"
Result: 
- Ford's stock decline (obvious)
- Mexican auto tariffs causing the drop (root cause)
- Steel prices rising due to reshoring (supply chain effect)
- Chinese EV makers targeting Mexico (competitive response)
- Auto loan rates rising (consumer impact)
- Michigan real estate boom (reshoring opportunity)
- Brazil benefiting from trade war (spillover effect)

**We reveal the hidden web of cause and effect.**

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    News Ingestion Pipeline                   │
│  - GPT-powered entity extraction                            │
│  - Impact scoring (1-10 scale)                              │
│  - Sentiment analysis with context                          │
│  - Automatic categorization                                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Relationship Discovery Engine                   │
│                                                             │
│  ┌─────────────────┐  ┌─────────────────┐                 │
│  │ Direct Matching │  │ Context Analysis │                 │
│  │ (FAISS Vectors) │  │  (GPT-3.5/4)    │                 │
│  └────────┬────────┘  └────────┬────────┘                 │
│           │                     │                           │
│           ▼                     ▼                           │
│  ┌─────────────────────────────────────┐                   │
│  │    Relationship Type Detection      │                   │
│  │  • Supply Chain Impacts             │                   │
│  │  • Regulatory/Legal Implications    │                   │
│  │  • Competitive Dynamics             │                   │
│  │  • Financial/Market Effects         │                   │
│  │  • Technological Dependencies       │                   │
│  │  • Geopolitical Factors            │                   │
│  └─────────────────────┬───────────────┘                   │
│                        │                                    │
│                        ▼                                    │
│  ┌─────────────────────────────────────┐                   │
│  │    Causation Chain Builder          │                   │
│  │  • Temporal sequencing              │                   │
│  │  • Impact propagation               │                   │
│  │  • Confidence scoring               │                   │
│  └─────────────────────┬───────────────┘                   │
└────────────────────────┼───────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Knowledge Graph Builder                     │
│  - Nodes: Events, Entities, Concepts                       │
│  - Edges: Causal relationships with type & strength        │
│  - Temporal dimension for evolution tracking               │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   Predictive Insights                        │
│  - What happens next based on patterns                     │
│  - Early warning indicators                                │
│  - Opportunity identification                              │
└─────────────────────────────────────────────────────────────┘
```

## 📁 Project Structure

```
article-relationship-engine/
├── src/
│   ├── __init__.py               # Package initialization
│   ├── news_ingestion.py         # Intelligent news processing with GPT
│   ├── config.py                 # Configuration and constants
│   ├── relationship_engine.py    # Core relationship discovery ✅
│   ├── causation_analyzer.py     # Cause-effect chain builder ✅
│   ├── impact_predictor.py       # Future impact prediction ✅
│   └── knowledge_graph.py        # Graph construction & queries ✅
├── data/
│   └── news.json                 # Rich dataset with hidden connections
├── explore_relationships.py      # CLI tool for exploration ✅
├── demo_relationship_discovery.py # Interactive demonstration ✅
├── visualize_chain.py            # Causation chain visualization ✅
└── requirements.txt              # Dependencies (updated)
```

## 🔧 Current Implementation

### ✅ Completed Features

1. **News Ingestion System** (`src/news_ingestion.py`)
   - GPT-powered entity extraction
   - Intelligent sentiment analysis
   - Impact scoring (1-10 scale)
   - Automatic categorization
   - No fallback - GPT is required for quality

2. **Rich News Dataset** (`news.json`)
   - 200+ interconnected articles
   - Real causation chains (tariffs → retaliation → spillover)
   - Multiple domains (auto, agriculture, finance, etc.)
   - Temporal progression showing cause and effect

3. **Relationship Discovery Engine** (`src/relationship_engine.py`) ✅
   - Entity overlap and temporal proximity detection
   - GPT-powered relationship classification
   - Batch processing for API efficiency
   - Confidence scoring and result caching
   - Impact web exploration

4. **Causation Analyzer** (`src/causation_analyzer.py`) ✅
   - Directed graph construction from all relationships
   - Chain building with pattern matching
   - Root cause identification
   - Ripple effect tracking across industries
   - Feedback loop detection
   - Cross-industry impact analysis

5. **Impact Predictor** (`src/impact_predictor.py`) ✅
   - Historical pattern database construction
   - GPT-4 powered prediction generation
   - Timeline estimation with confidence
   - Cross-industry cascade analysis
   - Early warning indicator identification
   - Similar event matching

6. **Knowledge Graph** (`src/knowledge_graph.py`) ✅
   - NetworkX-based graph construction
   - Multi-type nodes (events, entities, concepts)
   - Pattern detection (cascades, hubs, loops)
   - Path finding with detailed explanations
   - Interactive pyvis visualizations
   - Graph statistics and analysis

7. **CLI Tools** ✅
   - `explore_relationships.py`: Interactive exploration
   - `demo_relationship_discovery.py`: Showcase scenarios
   - `visualize_chain.py`: HTML/PNG visualizations

## 🧪 Key Algorithms

### 1. Relationship Type Classification
```python
RELATIONSHIP_TYPES = {
    'CAUSES': 'Direct causation',
    'TRIGGERS_RETALIATION': 'Provokes counter-action',
    'CREATES_OPPORTUNITY': 'Opens market/business opportunity',
    'DISRUPTS_SUPPLY_CHAIN': 'Affects production/distribution',
    'SHIFTS_COMPETITION': 'Changes competitive landscape',
    'AFFECTS_REGULATION': 'Influences policy/law',
    'IMPACTS_FINANCE': 'Affects markets/currency/rates',
}
```

### 2. Impact Propagation Model
- Primary impact: Direct effect on mentioned entities
- Secondary impact: Effects on suppliers, customers, competitors
- Tertiary impact: Broader market and economic effects
- Quaternary impact: Geopolitical and social implications

### 3. Temporal Analysis
- Event sequencing: Order matters (A must happen before B)
- Lag effects: Some impacts take time to materialize
- Feedback loops: Effects that reinforce or dampen the original cause

## 💡 Intelligence Patterns

### Pattern 1: Trade War Cascade
```
US Tariff Action
  → Target Country Retaliation
    → Third Country Opportunity
      → Supply Chain Realignment
        → Currency Impacts
          → Investment Flows
```

### Pattern 2: Regulatory Ripple
```
New Regulation Announced
  → Compliance Costs Rise
    → Small Players Exit
      → Market Consolidation
        → Innovation Shift
          → Consumer Impact
```

### Pattern 3: Technology Disruption
```
Tech Breakthrough
  → Incumbent Threat
    → Strategic Pivots
      → M&A Activity
        → Talent War
          → Regional Advantages
```

## 🔮 Advanced Features

### ✅ Implemented
- **Multi-Hop Reasoning**: Connect A to D through B and C using path finding
- **Pattern Detection**: Identify cascades, hubs, and feedback loops
- **Timeline Prediction**: Estimate when impacts will materialize
- **Cross-Industry Analysis**: Track effects across different sectors

### 🚧 Planned
- **Counterfactual Analysis**: "What if X hadn't happened?"
- **Scenario Planning**: Generate likely future scenarios
- **Anomaly Detection**: Identify when patterns break
- **Real-time Monitoring**: Track predictions vs actual outcomes

## 📝 Development Guidelines

### Adding New Relationship Types
1. Define the relationship in `RELATIONSHIP_TYPES`
2. Add detection logic to `RelationshipDiscoveryEngine`
3. Create test cases with real examples
4. Update impact propagation rules

### Improving Intelligence
1. Study real causation chains in the news data
2. Identify patterns that repeat across domains
3. Encode these patterns as detection rules
4. Validate with historical examples

### Performance Optimization
- Cache relationship discoveries
- Batch GPT calls for efficiency
- Pre-compute common causation chains
- Use FAISS for initial candidate selection

## 🎯 Success Metrics

1. **Relationship Coverage**: % of actual relationships discovered
2. **Causation Accuracy**: Correctness of cause-effect chains
3. **Prediction Hit Rate**: % of predicted impacts that materialize
4. **Discovery Speed**: Time to find all relationships
5. **Insight Value**: User-rated usefulness of discoveries

## 🚀 Vision

This isn't just another search engine. It's an intelligence system that:
- Understands the world as an interconnected system
- Reveals hidden dependencies and opportunities
- Predicts cascading effects before they're obvious
- Helps users make decisions with complete information

**We're building the lens through which professionals understand global events.**

## 🛠️ Quick Development Tasks

```bash
# Test news ingestion
python -c "from src.news_ingestion import NewsIngestionEngine; engine = NewsIngestionEngine(); print(engine.get_recent_articles(5))"

# Run interactive demo
python demo_relationship_discovery.py

# Explore relationships
python explore_relationships.py search "Trump tariffs"
python explore_relationships.py relationships 1  # For article ID 1
python explore_relationships.py chain "Trump tariffs Mexico"
python explore_relationships.py predict 41  # Predict impacts for TSMC drought
python explore_relationships.py ripple 1   # Show ripple effects
python explore_relationships.py path "US auto tariffs" "Brazilian soy exports"
python explore_relationships.py stats      # Show system statistics

# Visualize causation chains
python visualize_chain.py "auto tariffs" "brazilian soy exports" -f both
python visualize_chain.py "Trump tariffs" --impact-web -o my_impact_web

# Generate all visualizations
for event in "Trump tariffs" "TSMC drought" "EU fines Google"; do
    python visualize_chain.py "$event" --impact-web --depth 3
done
```

Remember: Every news event is connected to others. Our job is to reveal these hidden connections and help users see the complete picture.