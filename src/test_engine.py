# test_engine.py
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from search_engine import ContextualSearchEngine
import json

def test_basic_search():
    """Test the search engine with sample data"""
    
    # Initialize engine
    engine = ContextualSearchEngine()
    
    # Load dummy articles from JSON file
    import os
    json_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'dummy_articles.json')
    
    if os.path.exists(json_path):
        with open(json_path, 'r') as f:
            test_articles = json.load(f)
        print(f"Loaded {len(test_articles)} articles from dummy dataset")
    else:
        # Fallback to basic test articles
        test_articles = [
            {
                "id": "1",
                "title": "Apple Reports Record iPhone Sales in Q4",
                "content": "Apple Inc. announced record-breaking iPhone sales for the fourth quarter, driven by strong demand for the iPhone 15 Pro models. Revenue exceeded analyst expectations by 8%.",
                "date": "2024-01-15",
                "source": "TechCrunch"
            },
            {
                "id": "2",
                "title": "TSMC Faces Production Delays Due to Taiwan Drought",
                "content": "Taiwan Semiconductor Manufacturing Company warns of potential production delays as severe drought conditions affect water supply to fabrication plants. The company produces chips for major tech firms including Apple.",
                "date": "2024-01-14",
                "source": "Reuters"
            },
            {
                "id": "3",
                "title": "Samsung Gains Smartphone Market Share",
                "content": "Samsung Electronics reported increased smartphone market share in Q4, capitalizing on strong Galaxy S23 sales and competitive pricing in emerging markets.",
                "date": "2024-01-13",
                "source": "Bloomberg"
            }
        ]
    
    engine.add_articles(test_articles)
    
    # Test search
    query = "Apple iPhone sales"
    print(f"\n🔍 Testing search for: '{query}'")
    
    results = engine.search(query)
    
    # Display results
    print(f"\n📊 Search Stats:")
    print(f"   Direct matches: {results['stats']['direct_matches']}")
    print(f"   Contextual discoveries: {results['stats']['contextual_discoveries']}")
    print(f"   Improvement: {results['stats']['improvement_factor']}%")
    
    print(f"\n💡 Understanding:")
    print(f"   Intent: {results['understanding']['primary_intent']}")
    print(f"   Related topics: {results['understanding']['related_topics']}")
    
    print(f"\n📄 Direct Results:")
    for r in results['direct_results']:
        print(f"   - {r['title']} (score: {r['relevance_score']:.2f})")
    
    print(f"\n🔗 Contextual Discoveries:")
    for r in results['contextual_results']:
        print(f"   - {r['title']}")
        print(f"     ↳ {r.get('context_explanation', 'Related article')}")
    
    print(f"\n🎯 Insights:")
    insights = results['insights']
    print(f"   Summary: {insights.get('summary', '')}")
    
    return results

if __name__ == "__main__":
    results = test_basic_search()
    
    # Save results for inspection
    with open('test_results.json', 'w') as f:
        json.dump(results, f, indent=2, default=str)
    
    print("\n✅ Test completed! Results saved to test_results.json")