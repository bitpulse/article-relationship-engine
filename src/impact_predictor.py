"""
Impact Predictor - Predicts future impacts based on historical patterns and current events
"""

import json
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
from openai import OpenAI
from collections import defaultdict

from .config import (
    OPENAI_API_KEY, DEFAULT_MODEL, ADVANCED_MODEL,
    CAUSATION_PATTERNS, INDUSTRY_CATEGORIES,
    IMPACT_LEVELS, RELATIONSHIP_TYPES
)
from .relationship_engine import RelationshipDiscoveryEngine
from .causation_analyzer import CausationAnalyzer, CausationChain

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class Prediction:
    """Represents a predicted future impact"""
    prediction_id: str = field(default_factory=lambda: datetime.now().isoformat())
    source_event: Dict[str, Any] = field(default_factory=dict)
    predicted_impact: str = ""
    affected_industries: List[str] = field(default_factory=list)
    affected_entities: List[str] = field(default_factory=list)
    impact_type: str = ""
    confidence: float = 0.0
    estimated_timeframe_days: Tuple[int, int] = (0, 0)  # (min_days, max_days)
    reasoning: str = ""
    historical_precedents: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'prediction_id': self.prediction_id,
            'source_event': {
                'id': self.source_event.get('id'),
                'title': self.source_event.get('title')
            },
            'predicted_impact': self.predicted_impact,
            'affected_industries': self.affected_industries,
            'affected_entities': self.affected_entities,
            'impact_type': self.impact_type,
            'confidence': self.confidence,
            'estimated_timeframe_days': self.estimated_timeframe_days,
            'reasoning': self.reasoning,
            'precedent_count': len(self.historical_precedents)
        }


@dataclass
class PatternMatch:
    """Represents a match with a historical pattern"""
    pattern_name: str
    similarity_score: float
    matched_sequence: List[str]
    expected_next_steps: List[str]
    typical_duration_days: int


class ImpactPredictor:
    """
    Predicts future impacts of news events by:
    1. Analyzing historical patterns
    2. Identifying similar past events
    3. Extrapolating likely consequences
    4. Estimating timelines based on precedents
    """
    
    def __init__(self, 
                 relationship_engine: RelationshipDiscoveryEngine,
                 causation_analyzer: CausationAnalyzer):
        """Initialize with relationship and causation engines"""
        self.relationship_engine = relationship_engine
        self.causation_analyzer = causation_analyzer
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Build historical pattern database
        self._build_pattern_database()
        
        logger.info("Initialized ImpactPredictor")
    
    def _build_pattern_database(self):
        """Build database of historical cause-effect patterns"""
        self.pattern_database = defaultdict(list)
        
        # Analyze all articles to extract patterns
        for article_id in self.relationship_engine.articles.keys():
            # Get ripple effects for this article
            ripple_effects = self.causation_analyzer.track_ripple_effects(
                article_id, 
                max_hops=3
            )
            
            # Store patterns by category and impact type
            article = self.relationship_engine.articles[article_id]
            category = article.get('category', 'Unknown')
            
            for impact_level, effects in ripple_effects.items():
                if impact_level == 'cross_industry_impacts':
                    continue
                    
                for effect in effects:
                    pattern_key = (category, effect['relationship']['relationship_type'])
                    self.pattern_database[pattern_key].append({
                        'source': article,
                        'effect': effect['article'],
                        'relationship': effect['relationship'],
                        'temporal_gap': effect['relationship']['temporal_gap_days']
                    })
        
        logger.info(f"Built pattern database with {len(self.pattern_database)} patterns")
    
    def predict_ripple_effects(self, 
                              event: Dict[str, Any], 
                              time_horizon_days: int = 90) -> List[Prediction]:
        """
        Predict ripple effects for a given event
        
        Args:
            event: The event article or description
            time_horizon_days: How far into the future to predict
            
        Returns:
            List of predictions
        """
        predictions = []
        
        # If event is a string, find matching article
        if isinstance(event, str):
            event = self._find_event_article(event)
            if not event:
                logger.warning(f"No matching article found for: {event}")
                return []
        
        # 1. Find similar historical events
        similar_events = self._find_similar_events(event)
        
        # 2. Analyze patterns from similar events
        pattern_analysis = self._analyze_event_patterns(event, similar_events)
        
        # 3. Generate predictions using GPT
        gpt_predictions = self._generate_gpt_predictions(event, pattern_analysis)
        
        # 4. Validate and score predictions
        for pred_data in gpt_predictions:
            prediction = Prediction(
                source_event=event,
                predicted_impact=pred_data['impact'],
                affected_industries=pred_data['industries'],
                affected_entities=pred_data['entities'],
                impact_type=pred_data['impact_type'],
                confidence=self._calculate_confidence(pred_data, similar_events),
                estimated_timeframe_days=pred_data['timeframe'],
                reasoning=pred_data['reasoning'],
                historical_precedents=similar_events[:3]
            )
            
            # Only include predictions within time horizon
            if prediction.estimated_timeframe_days[0] <= time_horizon_days:
                predictions.append(prediction)
        
        # Sort by confidence
        predictions.sort(key=lambda p: p.confidence, reverse=True)
        
        return predictions[:10]  # Top 10 predictions
    
    def _find_event_article(self, event_description: str) -> Optional[Dict[str, Any]]:
        """Find article matching event description"""
        event_lower = event_description.lower()
        best_match = None
        best_score = 0
        
        for article in self.relationship_engine.articles.values():
            score = 0
            if event_lower in article['title'].lower():
                score += 2
            if event_lower in article['content'].lower():
                score += 1
            
            if score > best_score:
                best_score = score
                best_match = article
        
        return best_match
    
    def _find_similar_events(self, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find historically similar events"""
        similar_events = []
        
        # Get event characteristics
        event_category = event.get('category', 'Unknown')
        event_entities = set(event.get('entities', []))
        event_impact = event.get('impact_score', 5.0)
        
        for article in self.relationship_engine.articles.values():
            if article['id'] == event.get('id'):
                continue
            
            # Calculate similarity
            similarity_score = 0
            
            # Category match
            if article.get('category') == event_category:
                similarity_score += 0.3
            
            # Entity overlap
            article_entities = set(article.get('entities', []))
            if event_entities and article_entities:
                overlap = len(event_entities & article_entities) / len(event_entities)
                similarity_score += overlap * 0.3
            
            # Impact similarity
            impact_diff = abs(article.get('impact_score', 5.0) - event_impact)
            similarity_score += (10 - impact_diff) / 10 * 0.2
            
            # Content similarity (via embeddings if available)
            if 'embedding' in event and 'embedding' in article:
                embedding_sim = np.dot(event['embedding'], article['embedding'])
                similarity_score += float(embedding_sim) * 0.2
            
            if similarity_score > 0.5:
                similar_events.append({
                    'article': article,
                    'similarity': similarity_score
                })
        
        # Sort by similarity
        similar_events.sort(key=lambda x: x['similarity'], reverse=True)
        
        return [se['article'] for se in similar_events[:10]]
    
    def _analyze_event_patterns(self, 
                              event: Dict[str, Any], 
                              similar_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze patterns from similar historical events"""
        pattern_analysis = {
            'common_effects': defaultdict(int),
            'typical_timelines': defaultdict(list),
            'affected_industries': defaultdict(int),
            'relationship_types': defaultdict(int)
        }
        
        # Analyze effects of similar events
        for similar_event in similar_events:
            # Get causation chains from this event
            chains = self.causation_analyzer.build_causation_chain(
                similar_event['title'], 
                max_depth=3
            )
            
            for chain in chains:
                # Analyze each effect in the chain
                for i, node in enumerate(chain.nodes[1:]):  # Skip source
                    # Record effect type
                    effect_key = (node.category, chain.links[i].relationship_type)
                    pattern_analysis['common_effects'][effect_key] += 1
                    
                    # Record timeline
                    pattern_analysis['typical_timelines'][effect_key].append(
                        chain.links[i].temporal_gap_days
                    )
                    
                    # Record affected industries
                    pattern_analysis['affected_industries'][node.category] += 1
                    
                    # Record relationship types
                    pattern_analysis['relationship_types'][
                        chain.links[i].relationship_type
                    ] += 1
        
        return pattern_analysis
    
    def _generate_gpt_predictions(self, 
                                event: Dict[str, Any], 
                                pattern_analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate predictions using GPT based on patterns"""
        
        # Prepare pattern summary
        top_effects = sorted(
            pattern_analysis['common_effects'].items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        top_industries = sorted(
            pattern_analysis['affected_industries'].items(),
            key=lambda x: x[1],
            reverse=True
        )[:5]
        
        prompt = f"""
Based on historical patterns, predict the likely future impacts of this event:

EVENT:
Title: {event['title']}
Category: {event.get('category', 'Unknown')}
Impact Score: {event.get('impact_score', 5.0)}
Content: {event['content'][:400]}...

HISTORICAL PATTERNS:
Common Effects: {[f"{cat}-{rel}" for (cat, rel), count in top_effects]}
Typically Affected Industries: {[ind for ind, count in top_industries]}

Generate 5 specific predictions for what will likely happen as a result of this event.

For each prediction, provide:
1. predicted_impact: Specific description of what will happen
2. affected_industries: List of industries that will be affected
3. affected_entities: Specific companies/organizations/countries likely affected
4. impact_type: One of {list(RELATIONSHIP_TYPES.keys())}
5. timeframe_days: [min_days, max_days] when this will occur
6. reasoning: Brief explanation based on historical patterns

Return a JSON object:
{{
    "predictions": [
        {{
            "impact": "Specific prediction",
            "industries": ["Industry1", "Industry2"],
            "entities": ["Entity1", "Entity2"],
            "impact_type": "CAUSES",
            "timeframe": [7, 30],
            "reasoning": "Based on similar events..."
        }},
        ...
    ]
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=ADVANCED_MODEL,  # Use advanced model for predictions
                messages=[{"role": "user", "content": prompt}],
                temperature=0.4,  # Slightly higher for creative predictions
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('predictions', [])
            
        except Exception as e:
            logger.error(f"Error generating GPT predictions: {e}")
            return []
    
    def _calculate_confidence(self, 
                            prediction_data: Dict[str, Any], 
                            similar_events: List[Dict[str, Any]]) -> float:
        """Calculate confidence score for a prediction"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence based on number of similar events
        if len(similar_events) > 5:
            confidence += 0.2
        elif len(similar_events) > 2:
            confidence += 0.1
        
        # Boost for well-established impact types
        if prediction_data['impact_type'] in ['CAUSES', 'TRIGGERS_RETALIATION']:
            confidence += 0.1
        
        # Boost for near-term predictions
        if prediction_data['timeframe'][0] < 30:
            confidence += 0.1
        
        # Cap at 0.95
        return min(confidence, 0.95)
    
    def identify_affected_industries(self, 
                                   event: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Identify which industries will be affected by an event
        
        Args:
            event: The source event
            
        Returns:
            Dictionary mapping industries to predicted impacts
        """
        affected_industries = defaultdict(list)
        
        # Get predictions
        predictions = self.predict_ripple_effects(event)
        
        # Group by industry
        for prediction in predictions:
            for industry in prediction.affected_industries:
                affected_industries[industry].append({
                    'impact': prediction.predicted_impact,
                    'confidence': prediction.confidence,
                    'timeframe': prediction.estimated_timeframe_days,
                    'impact_type': prediction.impact_type
                })
        
        # Add cross-industry analysis
        cross_industry_impacts = self._analyze_cross_industry_effects(
            event, 
            affected_industries
        )
        
        return {
            'direct_impacts': dict(affected_industries),
            'cross_industry_effects': cross_industry_impacts
        }
    
    def _analyze_cross_industry_effects(self, 
                                      event: Dict[str, Any],
                                      direct_impacts: Dict[str, List]) -> Dict[str, Any]:
        """Analyze how impacts spread across industries"""
        
        prompt = f"""
Analyze how this event will create cascading effects across industries:

EVENT: {event['title']}

DIRECT INDUSTRY IMPACTS:
{json.dumps(dict(direct_impacts), indent=2)}

Identify:
1. Secondary effects (Industry A affected → Industry B affected)
2. Supply chain cascades
3. Financial contagion paths
4. Regulatory spillovers

Return JSON:
{{
    "cascades": [
        {{
            "from_industry": "Industry A",
            "to_industry": "Industry B",
            "mechanism": "How the effect spreads",
            "severity": "high/medium/low"
        }}
    ],
    "systemic_risks": ["Risk 1", "Risk 2"]
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error analyzing cross-industry effects: {e}")
            return {"cascades": [], "systemic_risks": []}
    
    def estimate_timeline(self, 
                         source_event: Dict[str, Any],
                         target_impact: str) -> Optional[Tuple[int, int]]:
        """
        Estimate when a specific impact will occur
        
        Args:
            source_event: The triggering event
            target_impact: Description of the expected impact
            
        Returns:
            Tuple of (min_days, max_days) or None
        """
        # Find similar patterns in history
        similar_patterns = []
        
        for pattern_key, pattern_instances in self.pattern_database.items():
            for instance in pattern_instances:
                # Check if this pattern matches
                if (instance['source']['category'] == source_event.get('category') and
                    target_impact.lower() in instance['effect']['title'].lower()):
                    similar_patterns.append(instance['temporal_gap'])
        
        if not similar_patterns:
            # Use GPT to estimate
            return self._estimate_timeline_gpt(source_event, target_impact)
        
        # Calculate timeline range from historical data
        min_days = int(np.percentile(similar_patterns, 10))
        max_days = int(np.percentile(similar_patterns, 90))
        
        return (max(0, min_days), max_days)
    
    def _estimate_timeline_gpt(self, 
                             source_event: Dict[str, Any],
                             target_impact: str) -> Tuple[int, int]:
        """Use GPT to estimate timeline when no historical data exists"""
        
        prompt = f"""
Estimate the timeline for this cause-effect relationship:

CAUSE: {source_event['title']}
EXPECTED EFFECT: {target_impact}

Based on typical market dynamics and historical patterns, estimate:
- Minimum days until effect becomes visible
- Maximum days for full effect to materialize

Consider factors like:
- Market reaction speed
- Regulatory processes
- Supply chain adjustments
- Implementation timelines

Return JSON:
{{
    "min_days": <number>,
    "max_days": <number>,
    "reasoning": "Brief explanation"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return (result['min_days'], result['max_days'])
            
        except Exception as e:
            logger.error(f"Error estimating timeline: {e}")
            return (7, 90)  # Default: 1 week to 3 months
    
    def find_early_indicators(self, predicted_impact: Prediction) -> List[Dict[str, Any]]:
        """
        Identify early indicators to watch for a predicted impact
        
        Args:
            predicted_impact: The prediction to monitor
            
        Returns:
            List of early indicators
        """
        indicators = []
        
        prompt = f"""
For this predicted impact, identify early warning indicators to monitor:

PREDICTED IMPACT: {predicted_impact.predicted_impact}
AFFECTED INDUSTRIES: {predicted_impact.affected_industries}
TIMEFRAME: {predicted_impact.estimated_timeframe_days} days

List 5 specific, measurable early indicators that would signal this impact is beginning.

For each indicator:
1. indicator: What to monitor
2. threshold: Specific threshold or change to watch for
3. data_source: Where to find this data
4. lead_time_days: How early this indicator typically appears

Return JSON:
{{
    "indicators": [
        {{
            "indicator": "Stock price of major auto manufacturers",
            "threshold": "5% decline",
            "data_source": "Financial markets",
            "lead_time_days": 3
        }},
        ...
    ]
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            result = json.loads(response.choices[0].message.content)
            return result.get('indicators', [])
            
        except Exception as e:
            logger.error(f"Error finding early indicators: {e}")
            return []