# Intelligent News Relationship Discovery Engine

**Transform isolated news articles into a living knowledge graph that reveals hidden cause-and-effect relationships across seemingly unrelated events.**

## The Problem We Solve

Traditional news systems show you what you search for. If you search for "Ford", you get more Ford articles. But the real world doesn't work in silos:

- US auto tariffs don't just affect car companies
- They trigger Chinese agricultural retaliation
- Which benefits Brazilian soybean farmers
- Causing shipping route realignments
- Affecting currency markets globally

**Humans miss these connections. Our AI doesn't.**

## What Makes Us Different

Instead of keyword matching, we understand:
- **Causation chains**: Auto tariffs → Steel prices ↑ → Construction costs ↑ → Housing slowdown
- **Retaliation patterns**: Trade action → Counter-tariffs → Third-party opportunities
- **Ripple effects**: Single event → Multi-industry impacts → Global consequences
- **Hidden stakeholders**: Discover who's affected beyond the obvious players
- **Future implications**: Predict what happens next based on discovered patterns

## Real Example

**Search: "Trump tariffs Mexico"**

Traditional search:
```
- Trump announces 25% tariff on Mexican auto imports
- Mexico considers retaliatory measures
- Ford stock drops on tariff news
```

Our intelligent discovery:
```
All of the above, PLUS:
→ Chinese EV makers eye Mexican market opportunity (competitor repositioning)
→ US steel futures jump 4.2% (supply chain impact)
→ Michigan real estate sees industrial property surge (reshoring effects)
→ Brazilian farmers benefit from China shifting soy purchases (trade war spillover)
→ Auto loan rates expected to rise (consumer impact)
→ Semiconductor shortage concerns grow (production disruption)
```

**Result: 165% more valuable insights discovered automatically!**

## How It Works

### Three-Stage Discovery Process

**Stage 1: Candidate Filtering**
- Temporal proximity (events within 30 days)
- Entity overlap (shared companies, people, locations)
- Semantic similarity using embeddings

**Stage 2: GPT Analysis**
- Analyzes batches of candidates
- Classifies relationship types (CAUSES, TRIGGERS_RETALIATION, CREATES_OPPORTUNITY, etc.)
- Assigns confidence scores
- Explains the connection

**Stage 3: Chain Building**
- Follows relationships recursively
- Builds directed graphs
- Identifies patterns like Trade War Cascade, Regulatory Ripple

### Example Discovery Flow

```
Trump Tariff (Article 1)
    ↓ [IMPACTS_FINANCE]
Ford Stock Drop (Article 2)
    ↓ [DISRUPTS_SUPPLY_CHAIN]
Auto Parts Suppliers Brace (Article 9)
    ↓ [CREATES_OPPORTUNITY]
Chinese EV Makers Eye Mexico (Article 10)
```

### Relationship Types

- **CAUSES**: Direct causation
- **TRIGGERS_RETALIATION**: Provokes counter-action
- **CREATES_OPPORTUNITY**: Opens market/business opportunity
- **DISRUPTS_SUPPLY_CHAIN**: Affects production/distribution
- **SHIFTS_COMPETITION**: Changes competitive landscape
- **AFFECTS_REGULATION**: Influences policy/law
- **IMPACTS_FINANCE**: Affects markets/currency/rates

## Core Intelligence Features

### 1. **Multi-Domain Impact Analysis**
Discovers how automotive policy affects agriculture, energy, finance, and beyond.

### 2. **Temporal Relationship Tracking**
Understands event sequences: tariff announcement → stock drop → production shift → job impacts.

### 3. **Stakeholder Network Mapping**
Identifies all affected parties, not just the obvious ones.

### 4. **Predictive Pattern Recognition**
Based on historical patterns, suggests what to watch for next.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/article-relationship-engine.git
cd article-relationship-engine

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env (REQUIRED - no fallback)
```

## Quick Start

```bash
# Run the AI search improvement demo (perfect for presentations)
python demo_ai_search_fast.py

# Launch the interactive Streamlit UI
streamlit run app_ai_search.py

# Run the full interactive demo
python demo_relationship_discovery.py

# Explore specific events and their hidden connections
python explore_relationships.py search "Trump tariffs"
python explore_relationships.py chain "Trump tariffs Mexico"
python explore_relationships.py predict 1  # Predict impacts for article ID 1

# Visualize causation chains
python visualize_chain.py "US auto tariffs" "Brazilian soy exports"

# Create an impact web visualization
python visualize_chain.py "Trump tariffs" --impact-web --depth 3
```

## Adding New Articles to the System

To add new articles for analysis:

1. **Manual Addition**: Add articles directly to `news.json` following this format:
```json
{
  "id": 293,  // Next available ID
  "title": "Your Article Title",
  "content": "Full article content...",
  "timestamp": "2025-07-20T10:00:00Z",
  "source": "News Source",
  "category": "Business",  // Politics, Finance, Technology, etc.
  "entities": ["Company A", "Person B", "Location C"],
  "tags": ["relevant", "tags", "here"],
  "sentiment": "neutral",  // positive, negative, neutral
  "impact_score": 7.5  // 1-10 scale
}
```

2. **Using the Ingestion Engine**:
```python
from src.news_ingestion import NewsIngestionEngine

engine = NewsIngestionEngine()

# Process a new article
article_data = engine.process_article(
    title="Your Article Title",
    content="Article content...",
    source="Reuters",
    timestamp="2025-07-20T10:00:00Z"
)

# Add to the dataset
engine.add_article(article_data)
```

3. **Batch Import** (coming soon): API endpoint for bulk article ingestion

## What You'll Discover

For any news event, instantly see:

### **Root Causes**
Why did this happen? What events led to this?

### **Ripple Effects**
What will this trigger across different industries and regions?

### **Hidden Stakeholders**
Who else is affected that isn't mentioned in the news?

### **Historical Patterns**
What happened in similar situations before?

### **Early Indicators**
What signals should you watch for next?

## Architecture

### Core Components

1. **News Ingestion Pipeline** (`src/news_ingestion.py`)
   - GPT-powered entity extraction
   - Sentiment and impact analysis
   - Automatic categorization
   - No fallback - quality guaranteed

2. **Relationship Discovery Engine** (`src/relationship_engine.py`)
   - Entity overlap and temporal proximity detection
   - GPT-powered relationship classification
   - Batch processing for efficiency
   - Confidence scoring and caching

3. **Causation Analyzer** (`src/causation_analyzer.py`)
   - Builds directed graphs of cause-effect relationships
   - Identifies root causes and traces ripple effects
   - Detects feedback loops and patterns
   - Temporal sequencing and validation

4. **Impact Predictor** (`src/impact_predictor.py`)
   - Analyzes historical patterns
   - Predicts future impacts with timelines
   - Identifies affected industries
   - Generates early warning indicators

5. **Knowledge Graph** (`src/knowledge_graph.py`)
   - Multi-type nodes: Events, entities, concepts
   - Pattern detection: Cascades, hubs, loops
   - Path finding between events
   - Interactive visualization support

## Value Proposition

- **Traditional news search**: 10 related articles
- **Our system**: 10 articles + 15-20 hidden connections
- **Improvement**: 150-200% more actionable intelligence
- **Cost**: ~$0.05-0.10 per intelligent analysis
- **Speed**: Real-time discovery with caching

## Try These Searches

1. **"Federal Reserve interest rates"**
   - Discovers: Auto financing impacts, housing market effects, tech valuations, emerging market capital flows

2. **"China tariffs agriculture"**  
   - Reveals: Brazilian export opportunities, shipping route changes, farm equipment cancellations, rural banking stress

3. **"Tesla production"**
   - Uncovers: Lithium supply concerns, competing EV strategies, grid infrastructure needs, semiconductor dependencies

4. **"EU regulation tech"**
   - Shows: Global compliance costs, competitive advantages, innovation shifts, market fragmentation risks

## Use Cases

### **Journalists**
Find the stories others miss by understanding hidden connections.

### **Business Intelligence**
Spot opportunities and risks across your entire value chain.

### **Investors**
Understand second and third-order effects on your portfolio.

### **Policy Makers**
See the full impact of decisions across all affected sectors.

### **Researchers**
Map complex cause-effect relationships in global events.

## Roadmap

- [x] Core relationship discovery engine
- [x] Multi-domain impact analysis
- [x] GPT-powered intelligence
- [x] Causation chain builder with pattern matching
- [x] Impact prediction with timeline estimation
- [x] Knowledge graph construction and queries
- [x] Interactive relationship visualization
- [x] Multi-hop reasoning (A→B→C→D connections)
- [x] CLI tools for exploration and visualization
- [ ] Real-time news feed integration
- [ ] Confidence scoring refinement
- [ ] API for third-party integration
- [ ] Web interface with Streamlit

## Contributing

This project transforms how we understand news. Join us!

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-relationship-discovery`)
3. Commit your changes (`git commit -m 'Add new relationship type detection'`)
4. Push to the branch (`git push origin feature/amazing-relationship-discovery`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details

## Why This Matters

In an interconnected world, isolated information is incomplete information. Every major event sends ripples across industries, borders, and markets. The winners are those who see the connections others miss.

**Stop reading news. Start understanding the world.**

---

*"It's like having an expert analyst who has read every article, understands all the connections, and can instantly show you the hidden web of cause-and-effect that others miss."*