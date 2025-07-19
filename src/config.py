"""
Configuration for the Intelligent News Relationship Discovery Engine
"""

import os
from typing import Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is required. Please set it in your .env file.")

# Model Configuration
DEFAULT_MODEL = "gpt-3.5-turbo"
ADVANCED_MODEL = "gpt-4"  # For complex reasoning
MODEL_TEMPERATURE = 0.3  # Low temperature for consistency
MAX_TOKENS = 1000

# Relationship Types
RELATIONSHIP_TYPES = {
    'CAUSES': {
        'description': 'Direct causation',
        'weight': 1.0,
        'keywords': ['causes', 'leads to', 'results in', 'triggers', 'drives']
    },
    'TRIGGERS_RETALIATION': {
        'description': 'Provokes counter-action',
        'weight': 0.9,
        'keywords': ['retaliation', 'response', 'counter', 'backlash', 'revenge']
    },
    'CREATES_OPPORTUNITY': {
        'description': 'Opens market/business opportunity',
        'weight': 0.8,
        'keywords': ['opportunity', 'benefit', 'advantage', 'opening', 'chance']
    },
    'DISRUPTS_SUPPLY_CHAIN': {
        'description': 'Affects production/distribution',
        'weight': 0.85,
        'keywords': ['supply chain', 'production', 'shortage', 'disruption', 'bottleneck']
    },
    'SHIFTS_COMPETITION': {
        'description': 'Changes competitive landscape',
        'weight': 0.7,
        'keywords': ['competition', 'market share', 'rival', 'competitor', 'strategic']
    },
    'AFFECTS_REGULATION': {
        'description': 'Influences policy/law',
        'weight': 0.75,
        'keywords': ['regulation', 'policy', 'law', 'compliance', 'legislation']
    },
    'IMPACTS_FINANCE': {
        'description': 'Affects markets/currency/rates',
        'weight': 0.8,
        'keywords': ['market', 'currency', 'stock', 'bond', 'financial', 'rates']
    },
    'AMPLIFIES_TREND': {
        'description': 'Reinforces existing movement',
        'weight': 0.6,
        'keywords': ['accelerates', 'amplifies', 'strengthens', 'reinforces']
    },
    'REVERSES_TREND': {
        'description': 'Counters existing movement',
        'weight': 0.7,
        'keywords': ['reverses', 'counters', 'undermines', 'weakens', 'opposes']
    }
}

# Impact Levels
IMPACT_LEVELS = {
    'PRIMARY': {
        'description': 'Direct effect on mentioned entities',
        'propagation_factor': 1.0
    },
    'SECONDARY': {
        'description': 'Effects on suppliers, customers, competitors',
        'propagation_factor': 0.7
    },
    'TERTIARY': {
        'description': 'Broader market and economic effects',
        'propagation_factor': 0.4
    },
    'QUATERNARY': {
        'description': 'Geopolitical and social implications',
        'propagation_factor': 0.2
    }
}

# Scoring Thresholds
RELATIONSHIP_CONFIDENCE_THRESHOLD = 0.6  # Minimum confidence to establish relationship
IMPACT_SCORE_THRESHOLD = 5.0  # Minimum impact score to consider significant
TEMPORAL_WINDOW_DAYS = 30  # Look for relationships within this time window
SIMILARITY_THRESHOLD = 0.7  # For entity matching

# Cache Configuration
CACHE_DIR = "cache"
CACHE_TTL_SECONDS = 3600  # 1 hour
ENABLE_CACHE = True

# Analysis Settings
MAX_RELATIONSHIPS_PER_ARTICLE = 20
BATCH_SIZE_FOR_GPT = 5  # Process articles in batches
MAX_CHAIN_DEPTH = 5  # Maximum depth for causation chains
ENABLE_FULL_SCAN = True  # Scan all articles for hidden connections

# Graph Configuration
GRAPH_NODE_COLORS = {
    'event': '#FF6B6B',
    'entity': '#4ECDC4',
    'concept': '#45B7D1',
    'impact': '#FFA07A'
}

GRAPH_EDGE_COLORS = {
    'CAUSES': '#FF4444',
    'TRIGGERS_RETALIATION': '#FF8800',
    'CREATES_OPPORTUNITY': '#00CC00',
    'DISRUPTS_SUPPLY_CHAIN': '#FF00FF',
    'SHIFTS_COMPETITION': '#0088FF',
    'AFFECTS_REGULATION': '#8800FF',
    'IMPACTS_FINANCE': '#FFFF00',
    'AMPLIFIES_TREND': '#00FFFF',
    'REVERSES_TREND': '#FF00AA'
}

# Pattern Templates
CAUSATION_PATTERNS = [
    {
        'name': 'Trade War Cascade',
        'sequence': ['tariff', 'retaliation', 'opportunity', 'realignment'],
        'typical_duration_days': 90
    },
    {
        'name': 'Regulatory Ripple',
        'sequence': ['regulation', 'compliance', 'consolidation', 'innovation'],
        'typical_duration_days': 180
    },
    {
        'name': 'Tech Disruption',
        'sequence': ['breakthrough', 'threat', 'pivot', 'acquisition'],
        'typical_duration_days': 365
    },
    {
        'name': 'Financial Contagion',
        'sequence': ['crisis', 'spread', 'intervention', 'recovery'],
        'typical_duration_days': 60
    },
    {
        'name': 'Supply Shock',
        'sequence': ['disruption', 'shortage', 'substitution', 'normalization'],
        'typical_duration_days': 120
    }
]

# Industry Categories
INDUSTRY_CATEGORIES = [
    'Automotive', 'Technology', 'Finance', 'Agriculture', 
    'Energy', 'Healthcare', 'Real Estate', 'Manufacturing',
    'Retail', 'Transportation', 'Telecommunications', 'Media',
    'Pharmaceuticals', 'Aerospace', 'Defense', 'Mining',
    'Construction', 'Hospitality', 'Education', 'Government'
]

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def get_config() -> Dict[str, Any]:
    """Get full configuration as dictionary"""
    return {
        'api': {
            'openai_key': OPENAI_API_KEY,
            'default_model': DEFAULT_MODEL,
            'advanced_model': ADVANCED_MODEL,
            'temperature': MODEL_TEMPERATURE,
            'max_tokens': MAX_TOKENS
        },
        'relationships': RELATIONSHIP_TYPES,
        'impact_levels': IMPACT_LEVELS,
        'thresholds': {
            'confidence': RELATIONSHIP_CONFIDENCE_THRESHOLD,
            'impact': IMPACT_SCORE_THRESHOLD,
            'temporal_window': TEMPORAL_WINDOW_DAYS,
            'similarity': SIMILARITY_THRESHOLD
        },
        'cache': {
            'directory': CACHE_DIR,
            'ttl': CACHE_TTL_SECONDS,
            'enabled': ENABLE_CACHE
        },
        'analysis': {
            'max_relationships': MAX_RELATIONSHIPS_PER_ARTICLE,
            'batch_size': BATCH_SIZE_FOR_GPT,
            'max_chain_depth': MAX_CHAIN_DEPTH,
            'full_scan': ENABLE_FULL_SCAN
        },
        'patterns': CAUSATION_PATTERNS,
        'industries': INDUSTRY_CATEGORIES
    }