"""
Canonical name generation module for Financial Pattern Discovery System
"""

import re
import logging
from typing import Dict, List, Any

from .config import FinancialTerms


class CanonicalNameGenerator:
    """Generate canonical names for term clusters"""
    
    def __init__(self):
        self.financial_terms = FinancialTerms()
        self.logger = logging.getLogger(__name__)
        
    def generate_canonical_names(self, clusters: Dict[int, Dict[str, Any]]) -> Dict[int, str]:
        """Generate canonical names for all clusters"""
        canonical_names = {}
        
        for cluster_id, cluster_data in clusters.items():
            canonical_name = self._generate_single_canonical_name(cluster_data['terms'])
            canonical_names[cluster_id] = canonical_name
            
        # Post-process to ensure essential financial terms get proper canonical names
        canonical_names = self._ensure_essential_financial_terms(clusters, canonical_names)
            
        return canonical_names
    
    def _ensure_essential_financial_terms(self, clusters: Dict[int, Dict[str, Any]], canonical_names: Dict[int, str]) -> Dict[int, str]:
        """Ensure essential financial terms have dedicated canonical names"""
        
        # Essential financial term patterns and their canonical names
        essential_patterns = {
            r'\bservicing\s+fee\b': 'servicing_fee',
            r'\bbackup\s+servicing\s+fees?\b': 'backup_servicing_fees', 
            r'\bindenture\s+trustee\s+fees?\b': 'indenture_trustee_fees',
            r'\bowner\s+trustee\s+fees?\b': 'owner_trustee_fees',
            r'\btrustee\s+fees?\b': 'trustee_fees',
            r'\binvestment\s+earnings\b': 'investment_earnings',
            r'\breserve\s+fund\b': 'reserve_fund',
            r'\bavailable\s+funds\b': 'available_funds',
            r'\bpool\s+factor\b': 'pool_factor',
            r'\badvance\s+rates?\b': 'advance_rates',
            r'\bovercollateralization\b': 'overcollateralization',
            r'\bwaterfall\b': 'waterfall',
        }
        
        # Find clusters containing essential terms and assign proper canonical names
        for cluster_id, cluster_data in clusters.items():
            terms_text = ' '.join(cluster_data['terms']).lower()
            
            for pattern, canonical_name in essential_patterns.items():
                if re.search(pattern, terms_text):
                    # Override the canonical name for this cluster
                    canonical_names[cluster_id] = canonical_name
                    self.logger.info(f"Assigned essential financial term canonical name: {canonical_name}")
                    break  # Use the first match found
                    
        return canonical_names
    
    def _generate_single_canonical_name(self, terms: List[str]) -> str:
        """Generate canonical name for a single cluster"""
        if not terms:
            return "unknown_cluster"
            
        # Look for common patterns across all terms in the cluster
        common_words = self._find_common_words(terms)
        
        # Try to identify the core financial concept
        canonical_name = self._identify_core_concept(terms, common_words)
        
        # If we couldn't identify a good concept, use the shortest meaningful term
        if not canonical_name or len(canonical_name) > 50:
            canonical_name = self._select_best_term(terms)
        
        # Clean and normalize
        canonical_name = self._clean_canonical_name(canonical_name)
        
        return canonical_name
    
    def _find_common_words(self, terms: List[str]) -> List[str]:
        """Find words that appear in multiple terms"""
        word_counts = {}
        
        for term in terms:
            words = term.lower().split()
            for word in words:
                if len(word) > 2:  # Skip very short words
                    word_counts[word] = word_counts.get(word, 0) + 1
        
        # Return words that appear in at least 30% of terms, sorted by frequency
        threshold = max(1, len(terms) * 0.3)
        common_words = [word for word, count in word_counts.items() if count >= threshold]
        return sorted(common_words, key=lambda w: word_counts[w], reverse=True)
    
    def _identify_core_concept(self, terms: List[str], common_words: List[str]) -> str:
        """Identify the core financial concept by analyzing all terms comprehensively"""
        
        # Analyze all terms to extract key components
        concept_components = self._extract_concept_components(terms)
        
        # Check if we found a direct financial term first
        if 'direct_financial_term' in concept_components:
            return concept_components['direct_financial_term']
        
        # Build canonical name from components in order of importance
        canonical_parts = []
        
        # 1. Class/Tranche identifier (highest priority)
        if concept_components['class']:
            canonical_parts.append(f"class_{concept_components['class']}")
        elif concept_components['tranche']:
            canonical_parts.append(f"tranche_{concept_components['tranche']}")
        
        # 2. Financial instrument type
        if concept_components['instrument']:
            canonical_parts.append(concept_components['instrument'])
        
        # 3. Financial action/type
        if concept_components['action']:
            canonical_parts.append(concept_components['action'])
        
        # 4. Financial concept
        if concept_components['concept']:
            canonical_parts.append(concept_components['concept'])
        
        # 5. Temporal aspect
        if concept_components['temporal']:
            canonical_parts.append(concept_components['temporal'])
        
        # If we have parts, join them
        if canonical_parts:
            return '_'.join(canonical_parts)
        
        # Fallback: use common words approach but more comprehensive
        return self._build_from_common_words(common_words, terms)
    
    def _extract_concept_components(self, terms: List[str]) -> Dict[str, str]:
        """Extract key concept components from all terms in cluster"""
        components = {
            'class': None,
            'tranche': None, 
            'instrument': None,
            'action': None,
            'concept': None,
            'temporal': None
        }
        
        # Check for direct financial terms first (highest priority)
        all_text = ' '.join(terms).lower()
        
        # Direct financial term patterns (these get priority)
        direct_financial_patterns = [
            (r'\bservicing\s+fee\b', 'servicing_fee'),
            (r'\bbackup\s+servicing\s+fees?\b', 'backup_servicing_fees'),
            (r'\bindenture\s+trustee\s+fees?\b', 'indenture_trustee_fees'),
            (r'\bowner\s+trustee\s+fees?\b', 'owner_trustee_fees'),
            (r'\btrustee\s+fees?\b', 'trustee_fees'),
            (r'\baccrued\s+fees?\b', 'accrued_fees'),
            (r'\bservicing\s+fees?\b', 'servicing_fees'),
            (r'\binvestment\s+earnings\b', 'investment_earnings'),
            (r'\breserve\s+fund\b', 'reserve_fund'),
            (r'\bavailable\s+funds\b', 'available_funds'),
            (r'\btotal\s+available\s+funds\b', 'total_available_funds'),
            (r'\bpool\s+factor\b', 'pool_factor'),
            (r'\badvance\s+rates?\b', 'advance_rates'),
            (r'\bovercollateralization\b', 'overcollateralization'),
            (r'\bwaterfall\b', 'waterfall'),
        ]
        
        # Check for direct financial terms first - if found, use them directly
        for pattern, canonical_name in direct_financial_patterns:
            if re.search(pattern, all_text):
                # Return early with the specific financial term
                return {'direct_financial_term': canonical_name}
        
        # Continue with class-aware logic if no direct financial terms found
        # With class-aware clustering, we should only have one class per cluster
        # But check all terms to be safe
        class_letters = set()
        for term in terms:
            class_match = re.search(r'class\s*([a-f])\b', term.lower())
            if class_match:
                class_letters.add(class_match.group(1))
        
        # Should only have one class now with class-aware clustering
        if len(class_letters) == 1:
            components['class'] = list(class_letters)[0]
        elif len(class_letters) > 1:
            # This shouldn't happen with class-aware clustering, but handle it
            class_counts = {}
            for term in terms:
                class_match = re.search(r'class\s*([a-f])\b', term.lower())
                if class_match:
                    class_letter = class_match.group(1)
                    class_counts[class_letter] = class_counts.get(class_letter, 0) + 1
            
            most_common_class = max(class_counts, key=class_counts.get)
            components['class'] = most_common_class
            
            # This warning should be rare now
            self.logger.warning(f"Unexpected mixed-class cluster with classes {class_letters}. "
                              f"Using most frequent: {most_common_class}")

        # Extract tranche information
        tranche_letters = set()
        for term in terms:
            tranche_match = re.search(r'tranche\s*([a-f])\b', term.lower())
            if tranche_match:
                tranche_letters.add(tranche_match.group(1))
        
        if len(tranche_letters) == 1:
            components['tranche'] = list(tranche_letters)[0]
        elif len(tranche_letters) > 1:
            # Similar logic for tranches
            tranche_counts = {}
            for term in terms:
                tranche_match = re.search(r'tranche\s*([a-f])\b', term.lower())
                if tranche_match:
                    tranche_letter = tranche_match.group(1)
                    tranche_counts[tranche_letter] = tranche_counts.get(tranche_letter, 0) + 1
            
            most_common_tranche = max(tranche_counts, key=tranche_counts.get)
            components['tranche'] = most_common_tranche

        # Extract instrument types
        all_text = ' '.join(terms).lower()  # Add this line back
        
        instrument_patterns = [
            (r'\b(note|certificate|bond|security)\b', None),
            (r'\b(principal|interest)\b', None),
        ]
        
        for pattern, _ in instrument_patterns:
            match = re.search(pattern, all_text)
            if match and not components['instrument']:
                components['instrument'] = match.group(1)
        
        # Extract financial actions/operations
        action_patterns = [
            (r'\b(distribution|payment|collection|allocation)\b', None),
            (r'\b(purchase|sale|transfer|exchange)\b', None),
            (r'\b(accrual|accrue|accrued)\b', 'accrued'),
            (r'\b(outstanding|aggregate|available|required)\b', None),
        ]
        
        for pattern, replacement in action_patterns:
            match = re.search(pattern, all_text)
            if match and not components['action']:
                components['action'] = replacement or match.group(1)
        
        # Extract financial concepts
        concept_patterns = [
            (r'\b(balance|amount|value|total|sum)\b', None),
            (r'\b(rate|factor|percentage|ratio)\b', None),
            (r'\b(fee|expense|cost|charge)\b', None),
            (r'\b(income|revenue|yield|return)\b', None),
            (r'\b(account|reserve|fund|pool)\b', None),
        ]
        
        for pattern, _ in concept_patterns:
            match = re.search(pattern, all_text)
            if match and not components['concept']:
                components['concept'] = match.group(1)
        
        # Extract temporal aspects
        temporal_patterns = [
            (r'\b(beginning|start|initial|opening)\b', 'beginning'),
            (r'\b(ending|end|final|closing|close)\b', 'ending'),
            (r'\b(current|present|today)\b', 'current'),
            (r'\b(previous|prior|last)\b', 'previous'),
            (r'\b(period|date|time|term)\b', None),
        ]
        
        for pattern, replacement in temporal_patterns:
            match = re.search(pattern, all_text)
            if match and not components['temporal']:
                components['temporal'] = replacement or match.group(1)
        
        return components
    
    def _build_from_common_words(self, common_words: List[str], terms: List[str]) -> str:
        """Build canonical name from common words with better logic"""
        if not common_words:
            return self._select_best_term(terms)
        
        # Enhanced prioritization for financial terminology
        word_priorities = {
            # Financial fees and charges (highest priority for general terms)
            'servicing': 120, 'backup': 115, 'trustee': 115, 'indenture': 115,
            'fee': 110, 'fees': 110, 'expense': 105, 'expenses': 105, 'cost': 105,
            
            # Structure identifiers
            'class': 100, 'tranche': 95, 'series': 90,
            
            # Financial institutions and roles
            'servicer': 100, 'dealer': 95, 'owner': 95,
            
            # Financial instruments
            'note': 85, 'certificate': 85, 'bond': 85, 'security': 85,
            'principal': 80, 'interest': 80,
            
            # Financial actions
            'distribution': 75, 'payment': 75, 'collection': 75,
            'accrued': 70, 'outstanding': 70, 'available': 70,
            
            # Financial concepts
            'balance': 65, 'amount': 40, 'fee': 110, 'account': 65,  # Note: lowered 'amount' priority
            'rate': 60, 'income': 60, 'reserve': 80,
            
            # Temporal (lowered priority to avoid generic names)
            'beginning': 45, 'ending': 45, 'current': 45, 'period': 35, 'date': 35,
            
            # Qualifiers (lowered priority)
            'aggregate': 40, 'total': 40, 'net': 50, 'gross': 50,
            'required': 45, 'eligible': 45, 'applicable': 45,
        }
        
        # Score and sort common words
        scored_words = []
        for word in common_words:
            if word in word_priorities:
                scored_words.append((word, word_priorities[word]))
            elif len(word) > 3:  # Include other meaningful words with lower priority
                scored_words.append((word, 30))
        
        # Sort by priority (descending)
        scored_words.sort(key=lambda x: x[1], reverse=True)
        
        # Enhanced selection logic for better canonical names
        selected_words = []
        
        # Always include high-priority financial terms first
        for word, score in scored_words:
            if score >= 110:  # High priority terms (fees, servicing, etc.)
                selected_words.append(word)
        
        # Add other important terms up to 4 words total
        for word, score in scored_words:
            if len(selected_words) >= 4:
                break
            if 60 <= score < 110 and word not in selected_words:
                selected_words.append(word)
        
        # If we still don't have enough words, add medium priority terms
        for word, score in scored_words:
            if len(selected_words) >= 4:
                break
            if 40 <= score < 60 and word not in selected_words:
                selected_words.append(word)
        
        if selected_words:
            return '_'.join(selected_words)
        else:
            return self._select_best_term(terms)
    
    def _select_best_term(self, terms: List[str]) -> str:
        """Select the best representative term from the cluster"""
        # Score terms by quality
        term_scores = {}
        
        for term in terms:
            score = 0
            term_lower = term.lower()
            
            # Prefer shorter, cleaner terms
            score += max(0, 50 - len(term))
            
            # Boost terms with financial keywords
            financial_keywords = ['class', 'interest', 'balance', 'fee', 'payment', 'amount', 'account', 'date']
            for keyword in financial_keywords:
                if keyword in term_lower:
                    score += 20
            
            # Penalize very long or complex terms
            if len(term) > 80:
                score -= 30
                
            # Penalize terms with too many words
            word_count = len(term.split())
            if word_count > 8:
                score -= word_count * 3
                
            term_scores[term] = score
        
        # Return the highest scoring term
        return max(term_scores, key=term_scores.get)
    
    def _clean_canonical_name(self, term: str) -> str:
        """Clean and normalize canonical name"""
        # Convert to lowercase and replace spaces with underscores
        clean_name = term.lower().replace(' ', '_')
        
        # Remove special characters
        clean_name = re.sub(r'[^\w_]', '', clean_name)
        
        # Remove duplicate underscores
        clean_name = re.sub(r'_+', '_', clean_name)
        
        # Remove leading/trailing underscores
        clean_name = clean_name.strip('_')
        
        return clean_name