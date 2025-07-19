# data_generator.py
import json
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any

class ArticleDataGenerator:
    """Generate interconnected articles with hidden relationships"""
    
    def __init__(self):
        self.article_id_counter = 1
        self.articles = []
        
    def generate_date(self, days_ago_max=30):
        """Generate a random date within the last N days"""
        days_ago = random.randint(0, days_ago_max)
        date = datetime.now() - timedelta(days=days_ago)
        return date.strftime("%Y-%m-%d")
    
    def create_article(self, title: str, content: str, source: str, category: str, 
                      entities: List[str] = None, hidden_connections: List[str] = None):
        """Create a single article with metadata"""
        article = {
            "id": str(self.article_id_counter),
            "title": title,
            "content": content,
            "date": self.generate_date(),
            "source": source,
            "category": category,
            "entities": entities or [],
            "hidden_connections": hidden_connections or []
        }
        self.article_id_counter += 1
        self.articles.append(article)
        return article
    
    def generate_tech_supply_chain_cluster(self):
        """Articles about tech supply chain with hidden connections"""
        
        # Main Apple article
        self.create_article(
            title="Apple Reports Record iPhone 16 Sales in Q4 2024",
            content="Apple Inc. announced record-breaking iPhone 16 sales for the fourth quarter, with revenue up 15% year-over-year. The new AI features and improved camera system drove strong demand, particularly in China and India. CEO Tim Cook highlighted the successful launch despite supply chain challenges.",
            source="TechCrunch",
            category="technology",
            entities=["Apple", "iPhone", "Tim Cook"],
            hidden_connections=["TSMC", "supply_chain", "semiconductors"]
        )
        
        # TSMC drought - hidden connection
        self.create_article(
            title="Taiwan Faces Worst Drought in 50 Years, TSMC Operations at Risk",
            content="Taiwan Semiconductor Manufacturing Company (TSMC) warns of potential production delays as severe drought conditions affect water supply to fabrication plants. The company, which produces chips for Apple, NVIDIA, and AMD, is implementing water conservation measures. Analysts worry about impact on global chip supply.",
            source="Reuters",
            category="business",
            entities=["TSMC", "Taiwan", "semiconductors"],
            hidden_connections=["Apple", "chip_shortage", "iPhone_production"]
        )
        
        # Rare earth mining - deeper connection
        self.create_article(
            title="Congo Cobalt Mines Face Labor Strikes, EV Battery Supply Threatened",
            content="Major cobalt mining operations in the Democratic Republic of Congo are experiencing widespread labor strikes. Cobalt is essential for lithium-ion batteries used in smartphones and electric vehicles. Apple, Tesla, and Samsung rely heavily on Congolese cobalt for their products.",
            source="Bloomberg",
            category="commodities",
            entities=["Congo", "cobalt", "mining"],
            hidden_connections=["Apple", "batteries", "supply_chain", "Tesla"]
        )
        
        # Shipping delays
        self.create_article(
            title="Major Port Congestion in Asia Delays Electronics Shipments",
            content="Severe congestion at major Asian ports including Shanghai and Shenzhen is causing significant delays in electronics shipments. Container ships are waiting up to two weeks to unload. The delays affect consumer electronics heading to US and European markets for the holiday season.",
            source="Wall Street Journal",
            category="logistics",
            entities=["shipping", "ports", "Asia"],
            hidden_connections=["Apple", "electronics", "supply_chain", "holidays"]
        )
        
        # Foxconn labor
        self.create_article(
            title="Foxconn Struggles with Worker Retention at iPhone Assembly Plants",
            content="Foxconn, Apple's primary manufacturing partner, reports difficulty retaining workers at its massive Zhengzhou facility. The company is offering bonuses and improving conditions to attract workers for iPhone production. Labor shortages could impact Apple's ability to meet holiday demand.",
            source="Nikkei Asia",
            category="manufacturing",
            entities=["Foxconn", "Apple", "manufacturing"],
            hidden_connections=["iPhone", "production", "labor", "supply_chain"]
        )
        
    def generate_regulatory_cluster(self):
        """Articles about tech regulation with interconnected impacts"""
        
        self.create_article(
            title="EU Digital Markets Act Forces Apple to Allow App Sideloading",
            content="The European Union's Digital Markets Act comes into full effect, requiring Apple to allow alternative app stores on iOS. This fundamental change to Apple's walled garden approach could impact app security and Apple's services revenue. Google and Meta also face significant changes.",
            source="The Verge",
            category="regulation",
            entities=["EU", "Apple", "DMA", "regulation"],
            hidden_connections=["iOS", "App_Store", "revenue_impact", "Google", "Meta"]
        )
        
        self.create_article(
            title="DOJ Antitrust Ruling Could Force Google to Sell Chrome Browser",
            content="The Department of Justice is considering asking a federal judge to force Google to sell its Chrome browser following an antitrust ruling. This could reshape the browser market and impact Google's advertising dominance. Apple's Safari and Microsoft's Edge could benefit.",
            source="New York Times",
            category="legal",
            entities=["Google", "DOJ", "Chrome", "antitrust"],
            hidden_connections=["Apple", "Safari", "Microsoft", "advertising", "search"]
        )
        
        self.create_article(
            title="Meta Fined $1.3 Billion for EU Privacy Violations",
            content="Meta faces its largest fine yet for violating EU privacy regulations by transferring user data to US servers. The ruling could force fundamental changes to how US tech companies handle European user data. Apple has positioned itself as the privacy-focused alternative.",
            source="Financial Times",
            category="privacy",
            entities=["Meta", "EU", "privacy", "GDPR"],
            hidden_connections=["Apple", "data_transfer", "Facebook", "Instagram"]
        )
        
        self.create_article(
            title="UK Proposes AI Safety Regulations Affecting All Major Tech Firms",
            content="The UK government unveiled comprehensive AI safety regulations that would require companies like OpenAI, Google, Apple, and Microsoft to submit their AI models for safety testing. The rules could slow AI deployment and increase development costs significantly.",
            source="BBC",
            category="regulation",
            entities=["UK", "AI", "regulation", "safety"],
            hidden_connections=["Apple", "Google", "Microsoft", "OpenAI", "AI_development"]
        )
        
    def generate_competition_cluster(self):
        """Articles about market competition"""
        
        self.create_article(
            title="Samsung Galaxy S24 Outsells iPhone in Key Asian Markets",
            content="Samsung's latest Galaxy S24 series has overtaken iPhone sales in South Korea, India, and Southeast Asian markets. The success is attributed to aggressive pricing, AI features, and local market customization. Apple is responding with rare discounts in these regions.",
            source="Korea Herald",
            category="technology",
            entities=["Samsung", "Galaxy S24", "Apple", "iPhone"],
            hidden_connections=["smartphone_market", "Asia", "competition", "pricing"]
        )
        
        self.create_article(
            title="Google Pixel 9 AI Features Set New Benchmark for Smartphones",
            content="Google's Pixel 9 showcases advanced AI capabilities that surpass both iPhone and Samsung devices. Features like real-time translation, AI photo editing, and personalized assistance are winning over users. Apple is reportedly accelerating its AI development in response.",
            source="The Information",
            category="technology",
            entities=["Google", "Pixel", "AI", "smartphones"],
            hidden_connections=["Apple", "iPhone", "AI_race", "competition"]
        )
        
        self.create_article(
            title="Chinese Smartphone Makers Gain 40% Market Share Globally",
            content="Xiaomi, Oppo, and Vivo collectively reached 40% global smartphone market share, pressuring both Apple and Samsung. Their success in emerging markets with feature-rich, affordable devices is reshaping the industry. Apple maintains premium segment but faces volume pressure.",
            source="IDC Report",
            category="market_research",
            entities=["Xiaomi", "Oppo", "Vivo", "China"],
            hidden_connections=["Apple", "Samsung", "market_share", "emerging_markets"]
        )
        
    def generate_financial_cluster(self):
        """Articles about financial markets affecting tech"""
        
        self.create_article(
            title="Fed Signals Higher Interest Rates for Longer, Tech Stocks Plunge",
            content="The Federal Reserve indicated interest rates will remain elevated through 2025, sending tech stocks tumbling. High-growth companies like Apple, Microsoft, and Google saw significant declines. Higher rates make future earnings less valuable and increase borrowing costs.",
            source="CNBC",
            category="finance",
            entities=["Fed", "interest rates", "tech stocks"],
            hidden_connections=["Apple", "Microsoft", "Google", "valuation", "growth"]
        )
        
        self.create_article(
            title="Semiconductor ETFs See Record Inflows Despite Volatility",
            content="Investors poured record amounts into semiconductor ETFs, betting on long-term AI and data center growth. Holdings include NVIDIA, TSMC, ASML, and AMD. The sector's importance to everything from smartphones to AI is driving investment despite geopolitical risks.",
            source="ETF.com",
            category="investing",
            entities=["semiconductors", "ETF", "NVIDIA", "TSMC"],
            hidden_connections=["Apple", "AI", "chips", "smartphones", "data_centers"]
        )
        
        self.create_article(
            title="Dollar Strength Hurts US Tech Companies' International Revenue",
            content="The strong US dollar is cutting into international revenue for major tech companies. Apple, which generates over 60% of revenue overseas, faces significant currency headwinds. Companies are raising prices internationally, potentially impacting demand.",
            source="Reuters",
            category="forex",
            entities=["USD", "currency", "Apple", "revenue"],
            hidden_connections=["iPhone_pricing", "international_sales", "profit_margins"]
        )
        
        self.create_article(
            title="Venture Capital Funding for AI Startups Hits Record $50 Billion",
            content="VC investment in AI startups reached unprecedented levels, with major funds competing for stakes in promising companies. This threatens established players like Apple, Google, and Microsoft who face nimble competitors. Talent acquisition costs are soaring as startups poach from big tech.",
            source="PitchBook",
            category="venture_capital",
            entities=["VC", "AI", "startups", "funding"],
            hidden_connections=["Apple", "Google", "Microsoft", "talent_war", "competition"]
        )
        
    def generate_additional_diverse_articles(self):
        """Generate additional articles for variety"""
        
        # Environmental impact
        self.create_article(
            title="Data Centers' Water Usage Under Scrutiny Amid Global Droughts",
            content="Tech companies' data centers consume millions of gallons of water for cooling, facing criticism during water shortages. Google, Microsoft, and Meta are investing in water recycling. This adds to challenges like the TSMC drought situation affecting chip production.",
            source="Environmental Times",
            category="environment",
            entities=["data centers", "water", "Google", "Microsoft"],
            hidden_connections=["TSMC", "drought", "sustainability", "tech_infrastructure"]
        )
        
        # Cybersecurity
        self.create_article(
            title="Major iPhone Security Flaw Discovered, Emergency Patch Released",
            content="Apple released an emergency security update for a critical vulnerability in iOS that could allow remote code execution. The flaw affects all iPhone models and was actively exploited. Security researchers praise Apple's quick response compared to Android fragmentation.",
            source="Wired",
            category="security",
            entities=["Apple", "iPhone", "iOS", "security"],
            hidden_connections=["software_updates", "Android", "vulnerability", "privacy"]
        )
        
        # Energy and sustainability
        self.create_article(
            title="Apple's 2030 Carbon Neutral Goal Faces Supply Chain Challenges",
            content="Apple's ambitious goal to be carbon neutral across its entire supply chain by 2030 encounters obstacles. Key suppliers like Foxconn and TSMC struggle with renewable energy adoption in Asia. The company may need to reconsider its manufacturing partnerships.",
            source="GreenTech Media",
            category="sustainability",
            entities=["Apple", "carbon neutral", "supply chain"],
            hidden_connections=["TSMC", "Foxconn", "renewable_energy", "manufacturing"]
        )
        
        # Labor and social issues
        self.create_article(
            title="Tech Workers Unionization Efforts Gain Momentum at Apple Stores",
            content="Apple retail workers at multiple locations vote to unionize, following successful efforts at several stores. The movement reflects broader labor activism in tech, with workers at Amazon and Google also organizing. This could impact Apple's retail operations and costs.",
            source="Labor Notes",
            category="labor",
            entities=["Apple", "unions", "retail", "workers"],
            hidden_connections=["labor_costs", "retail_operations", "employee_satisfaction"]
        )
        
        # Geopolitics
        self.create_article(
            title="US-China Tech Tensions: Biden Expands Chip Export Controls",
            content="The Biden administration announced expanded restrictions on semiconductor technology exports to China. This affects companies like Apple who rely on Chinese manufacturing and sales. TSMC and Samsung must choose between US technology access and Chinese markets.",
            source="Politico",
            category="geopolitics",
            entities=["US", "China", "semiconductors", "Biden"],
            hidden_connections=["Apple", "TSMC", "manufacturing", "supply_chain", "trade_war"]
        )
        
        # Innovation and R&D
        self.create_article(
            title="Apple's Secret AR Glasses Project Faces Technical Delays",
            content="Internal sources reveal Apple's augmented reality glasses project encounters significant technical challenges. Battery life, display technology, and heat dissipation remain unsolved. Competitors like Meta and Google advance their own AR initiatives, potentially beating Apple to market.",
            source="The Information",
            category="technology",
            entities=["Apple", "AR", "glasses", "innovation"],
            hidden_connections=["Meta", "Google", "wearables", "R&D", "competition"]
        )
        
        # Telecommunications
        self.create_article(
            title="5G Network Expansion Slows, Affecting iPhone 16 Key Features",
            content="Telecom providers scale back 5G infrastructure investments due to high costs and lower-than-expected returns. This could limit adoption of bandwidth-intensive features in new devices like iPhone 16. Apple may need to adjust its product strategy.",
            source="Telecom News",
            category="telecommunications",
            entities=["5G", "telecoms", "infrastructure"],
            hidden_connections=["Apple", "iPhone", "network_features", "product_strategy"]
        )
        
        # Retail and consumer behavior
        self.create_article(
            title="Holiday Shopping Trends: Consumers Choose Refurbished Over New iPhones",
            content="Economic uncertainty drives consumers toward refurbished and older model iPhones this holiday season. Apple's refurbished store sees 40% increase in sales. This trend affects Apple's average selling prices and could impact quarterly revenue targets.",
            source="Retail Dive",
            category="retail",
            entities=["Apple", "iPhone", "refurbished", "consumer"],
            hidden_connections=["revenue", "pricing", "economic_conditions", "sustainability"]
        )
        
    def generate_all_articles(self) -> List[Dict[str, Any]]:
        """Generate all article clusters"""
        self.generate_tech_supply_chain_cluster()
        self.generate_regulatory_cluster()
        self.generate_competition_cluster()
        self.generate_financial_cluster()
        self.generate_additional_diverse_articles()
        
        # Shuffle articles to mix categories
        random.shuffle(self.articles)
        
        return self.articles
    
    def save_articles(self, filepath: str):
        """Save articles to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.articles, f, indent=2)
        print(f"Generated {len(self.articles)} articles with hidden connections")
        
    def get_connection_graph(self) -> Dict[str, List[str]]:
        """Extract connection graph for visualization"""
        graph = {}
        for article in self.articles:
            connections = []
            # Find articles that mention this article's entities
            for other in self.articles:
                if article['id'] != other['id']:
                    # Check if entities overlap or hidden connections match
                    if (any(entity in other['content'] for entity in article['entities']) or
                        any(conn in other['hidden_connections'] for conn in article['entities'])):
                        connections.append(other['id'])
            graph[article['id']] = connections
        return graph


if __name__ == "__main__":
    generator = ArticleDataGenerator()
    articles = generator.generate_all_articles()
    generator.save_articles("data/dummy_articles.json")
    
    # Show some statistics
    print(f"\nArticle categories:")
    categories = {}
    for article in articles:
        cat = article['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")
    
    print(f"\nExample connections:")
    print("- Apple articles connect to: TSMC, supply chain, regulation, competition")
    print("- TSMC articles connect to: Apple, drought, semiconductors, production")
    print("- Regulatory articles connect to: All major tech companies")