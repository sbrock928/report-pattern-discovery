"""
Fuzzy matching module for Financial Pattern Discovery System
"""

import logging
from typing import Dict, List, Any

from rapidfuzz import process, fuzz

from .config import ProcessingConfig


class FuzzyMatcher:
    """Fuzzy matching for financial terms"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.match_cache = {}
        
    def create_mappings(self, clusters: Dict[int, Dict[str, Any]], 
                       canonical_names: Dict[int, str]) -> List[Dict[str, Any]]:
        """Create direct mappings between terms and their cluster's canonical names"""
        mappings = []
        
        for cluster_id, cluster_data in clusters.items():
            canonical_name = canonical_names[cluster_id]
            
            for term in cluster_data['terms']:
                # Calculate confidence based on how well the term matches the canonical name
                confidence_score = self._calculate_term_confidence(term, canonical_name, cluster_data)
                
                # Only include mappings that meet the threshold
                if confidence_score >= self.config.fuzzy_threshold:
                    mapping = {
                        'original_term': term,
                        'canonical_name': canonical_name,
                        'cluster_id': cluster_id,
                        'fuzzy_score': confidence_score,
                        'fuzzy_match': canonical_name,
                        'confidence': self._calculate_confidence_level(confidence_score)
                    }
                    mappings.append(mapping)
                else:
                    # Log terms that don't meet the threshold
                    self.logger.info(f"Term '{term}' excluded: confidence {confidence_score:.1f} below threshold {self.config.fuzzy_threshold}")
        
        self.logger.info(f"Created {len(mappings)} mappings meeting {self.config.fuzzy_threshold}% threshold")
        return mappings
    
    def _calculate_term_confidence(self, term: str, canonical_name: str, cluster_data: Dict[str, Any]) -> float:
        """Calculate how well a term fits its canonical name"""
        
        # Direct fuzzy match between term and canonical name
        direct_score = fuzz.WRatio(term.lower(), canonical_name.lower())
        
        # Boost score if term contains key words from canonical name
        canonical_words = set(canonical_name.split('_'))
        term_words = set(term.lower().split())
        
        word_overlap = len(canonical_words.intersection(term_words))
        if word_overlap > 0:
            overlap_bonus = min(20, word_overlap * 10)
            direct_score = min(100, direct_score + overlap_bonus)
        
        # Additional boost for exact substring matches
        if canonical_name.replace('_', ' ') in term.lower():
            direct_score = min(100, direct_score + 15)
        
        # If the cluster is large and this term is representative, boost confidence
        if cluster_data['count'] > 3:
            # Check if this term appears in the top features
            if 'top_features' in cluster_data:
                term_words_in_features = any(word in cluster_data['top_features'] 
                                           for word in term.lower().split())
                if term_words_in_features:
                    direct_score = min(100, direct_score + 10)
        
        return direct_score
    
    def _calculate_confidence_level(self, score: float) -> str:
        """Calculate confidence level for mapping"""
        if score >= 95:
            return 'very_high'
        elif score >= 85:
            return 'high'
        elif score >= self.config.fuzzy_threshold:
            return 'medium'
        else:
            return 'low'