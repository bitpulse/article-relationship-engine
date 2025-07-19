#!/usr/bin/env python3
"""
Test runner for the article relationship engine
"""
import sys
from pathlib import Path

# Add src to Python path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import and run the test
from test_engine import test_basic_search

if __name__ == "__main__":
    print("Running Article Relationship Engine Tests...")
    print("=" * 60)
    
    try:
        results = test_basic_search()
        print("\n✅ All tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)