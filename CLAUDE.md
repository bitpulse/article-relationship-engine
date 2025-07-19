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
│   ├── news_ingestion.py         # Intelligent news processing with GPT
│   ├── relationship_engine.py    # Core relationship discovery (TODO)
│   ├── causation_analyzer.py     # Cause-effect chain builder (TODO)
│   ├── impact_predictor.py       # Future impact prediction (TODO)
│   ├── knowledge_graph.py        # Graph construction & queries (TODO)
│   └── config.py                 # Configuration
├── data/
│   └── news.json                 # Rich dataset with hidden connections
├── demo_showcase.py              # Interactive demonstration
├── explore_relationships.py      # Relationship exploration tool (TODO)
└── requirements.txt              # Dependencies
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

### 🚧 Next Implementation Steps

1. **Relationship Discovery Engine** (`relationship_engine.py`)
   ```python
   class RelationshipDiscoveryEngine:
       def discover_relationships(self, article: Dict) -> List[Relationship]:
           """
           For a given article, discover all related articles and their
           relationship types (cause, effect, retaliation, opportunity, etc.)
           """
           
       def build_causation_chain(self, event: str) -> CausationChain:
           """
           Build the full cause-effect chain for an event
           E.g., Tariffs → Stock Drop → Production Shift → Job Impact
           """
   ```

2. **Impact Prediction** (`impact_predictor.py`)
   ```python
   class ImpactPredictor:
       def predict_ripple_effects(self, event: Dict) -> List[Prediction]:
           """
           Based on the event and historical patterns, predict:
           - Which industries will be affected
           - What types of responses to expect
           - Timeline of effects
           """
   ```

3. **Knowledge Graph** (`knowledge_graph.py`)
   ```python
   class KnowledgeGraph:
       def add_event(self, event: Dict, relationships: List[Relationship]):
           """Add event and its relationships to the graph"""
           
       def query_impact_path(self, from_event: str, to_effect: str):
           """Find the causal path between two events"""
           
       def find_similar_patterns(self, event: Dict) -> List[Pattern]:
           """Find historical patterns similar to current event"""
   ```

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

## 🔮 Advanced Features (Planned)

### Multi-Hop Reasoning
Connect A to D through B and C, even when A and D seem unrelated.

### Counterfactual Analysis
"What if X hadn't happened?" - Understand critical dependencies.

### Scenario Planning
Given current events, generate likely future scenarios.

### Anomaly Detection
Identify when patterns break - often the most valuable insight.

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

# Explore specific events
python explore_relationships.py "Trump tariffs"

# Run relationship discovery demo
python demo_relationship_discovery.py

# Visualize a causation chain
python visualize_chain.py "auto tariffs" "brazilian soy exports"
```

Remember: Every news event is connected to others. Our job is to reveal these hidden connections and help users see the complete picture.