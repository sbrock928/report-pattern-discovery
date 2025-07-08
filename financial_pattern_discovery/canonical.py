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
        
        # Define generic terms that shouldn't become standalone canonical names
        self.junk_canonical_names = {
            # Generic qualifiers that aren't actual variables (keep these)
            'net', 'total', 'gross', 'current', 'aggregate', 'outstanding',
            'available', 'required', 'applicable', 'eligible', 'related',
            
            # Generic amounts/values without context (keep these)
            'amount', 'amounts', 'value', 'values', 'sum', 'sums',
            
            # Temporal terms alone (keep these)
            'beginning', 'ending', 'period', 'date', 'time',
            'start', 'end', 'initial', 'final', 'opening', 'closing',
            
            # Generic descriptors (keep these)
            'other', 'additional', 'miscellaneous', 'various', 'general',
            'standard', 'regular', 'normal', 'special', 'extra',
            
            # Single letters or very short terms (keep these)
            'a', 'b', 'c', 'd', 'e', 'f', 'i', 'ii', 'iii'
            
            # REMOVED: 'principal', 'interest', 'balance', 'payment', 'income',
            # 'expense', 'cost', 'fee', 'charge', 'rate', 'factor',
            # 'account', 'fund', 'pool', 'reserve', 'trust'
            # These can be meaningful when combined with class identifiers
        }
        
    def generate_canonical_names(self, clusters: Dict[int, Dict[str, Any]]) -> Dict[int, str]:
        """Generate canonical names for all clusters"""
        canonical_names = {}
        
        for cluster_id, cluster_data in clusters.items():
            canonical_name = self._generate_single_canonical_name(cluster_data['terms'])
            
            # Filter out junk canonical names
            if self._is_junk_canonical_name(canonical_name):
                # Try to create a better name or mark for exclusion
                canonical_name = self._create_better_canonical_name(cluster_data['terms'], canonical_name)
                
            canonical_names[cluster_id] = canonical_name
            
        # Post-process to ensure essential financial terms get proper canonical names
        canonical_names = self._ensure_essential_financial_terms(clusters, canonical_names)
            
        return canonical_names
    
    def _is_junk_canonical_name(self, canonical_name: str) -> bool:
        """Check if a canonical name is too generic to be useful"""
        if not canonical_name or canonical_name == "unknown_cluster":
            return True
            
        # Split the canonical name into parts
        parts = canonical_name.split('_')
        
        # NEVER consider class-specific terms as junk
        if any(part.startswith('class_') for part in parts):
            return False
            
        # NEVER consider tranche-specific terms as junk  
        if any(part.startswith('tranche_') for part in parts):
            return False
            
        # Check if it's a single generic term (but allow some financial terms)
        if len(parts) == 1:
            single_term = parts[0]
            # These single terms are always junk
            always_junk = {'net', 'total', 'gross', 'current', 'amount', 'value', 'sum',
                          'beginning', 'ending', 'period', 'date', 'time', 'other', 'additional',
                          'a', 'b', 'c', 'd', 'e', 'f', 'i', 'ii', 'iii'}
            if single_term in always_junk:
                return True
                
            # Allow single financial terms that have meaning
            meaningful_single_terms = {'interest', 'principal', 'balance', 'fee', 'payment', 
                                     'income', 'expense', 'cost', 'rate', 'factor', 'account',
                                     'fund', 'pool', 'reserve', 'trust', 'servicing', 'trustee'}
            if single_term in meaningful_single_terms:
                return False
        
        # Check if it's entirely composed of very generic terms
        very_generic = {'amount', 'total', 'net', 'gross', 'current', 'value', 'sum',
                       'beginning', 'ending', 'period', 'date', 'time'}
        if all(part in very_generic for part in parts):
            return True
            
        # Check if less than 30% of parts are meaningful (was 50%, now more lenient)
        non_junk_parts = [part for part in parts if part not in self.junk_canonical_names]
        if len(non_junk_parts) < len(parts) * 0.3:
            return True
            
        return False
    
    def _create_better_canonical_name(self, terms: List[str], original_name: str) -> str:
        """Try to create a better canonical name for clusters with junk names"""
        
        # Look for specific financial patterns in the original terms
        all_text = ' '.join(terms).lower()
        
        # Try to find more specific financial concepts
        specific_patterns = [
            (r'\b(servicing|backup|trustee|owner)\s+fee', 'specific_fee'),
            (r'\b(investment|interest)\s+earnings', 'earnings'),
            (r'\b(reserve|trust)\s+fund', 'fund_account'),
            (r'\b(pool|aggregate)\s+balance', 'pool_balance'),
            (r'\b(advance|overcollateralization)\s+rate', 'advance_rate'),
            (r'\b(distribution|payment)\s+date', 'payment_date'),
            (r'\b(beginning|ending)\s+period', 'period_boundary'),
            (r'\bclass\s+[a-f]\s+', 'class_specific'),
        ]
        
        for pattern, replacement in specific_patterns:
            if re.search(pattern, all_text):
                return replacement
                
        # If we still can't find a good name, check if this cluster should be excluded
        if len(terms) == 1 and terms[0].lower().strip() in self.junk_canonical_names:
            return f"excluded_generic_{terms[0].lower().replace(' ', '_')}"
            
        # Try to build from the longest meaningful term
        meaningful_terms = []
        for term in terms:
            term_words = term.lower().split()
            if len(term_words) > 1:  # Multi-word terms are often more meaningful
                meaningful_terms.append(term)
                
        if meaningful_terms:
            # Use the shortest meaningful multi-word term
            best_term = min(meaningful_terms, key=len)
            return self._clean_canonical_name(best_term)
            
        # Last resort: mark as low priority
        return f"low_priority_{original_name}"
    
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
        
        # 3. Amount type (single, specific type)
        if concept_components['amount_type']:
            canonical_parts.append(concept_components['amount_type'])
        
        # 4. Financial action/type
        if concept_components['action']:
            canonical_parts.append(concept_components['action'])
        
        # 5. Financial concept
        if concept_components['concept']:
            canonical_parts.append(concept_components['concept'])
        
        # 6. Temporal aspect
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
            'temporal': None,
            'amount_type': None  # Back to single amount type to create distinct canonical names
        }
        
        # Check for direct financial terms first (highest priority)
        all_text = ' '.join(terms).lower()
        
        # Enhanced direct financial term patterns with amount type distinctions
        direct_financial_patterns = [
            # More specific servicer fee patterns first - handle both "servicer" and "servicing"
            (r'\bbackup\s+servicing\s+fee\b', 'backup_servicing_fee'),
            (r'\bbackup\s+servicer\s+fee\b', 'backup_servicer_fee'),
            (r'\bservicing\s+fee\b', 'servicing_fee'),
            (r'\bservicing\s+fees\b', 'servicing_fees'),
            
            # Other trustee and fee patterns
            (r'\bbackup\s+trustee\s+fee\b', 'backup_trustee_fee'),
            (r'\btrustee\s+fees?\b', 'trustee_fees'),
            (r'\bindenture\s+trustee\s+fee\b', 'indenture_trustee_fee'),
            (r'\bowner\s+trustee\s+fee\b', 'owner_trustee_fee'),
            
            # Fund and reserve patterns
            (r'\bavailable\s+funds\b', 'available_funds'),
            (r'\breserve\s+fund\b', 'reserve_fund'),
            (r'\bpool\s+factor\b', 'pool_factor'),
            (r'\bovercollateralization\b', 'overcollateralization'),
        ]
        
        # Check for direct financial terms first - if found, use them directly
        for pattern, canonical_name in direct_financial_patterns:
            if re.search(pattern, all_text):
                # Return early with the specific financial term
                return {'direct_financial_term': canonical_name}
        
        # Continue with enhanced class-aware logic
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

        # Extract tranche information
        tranche_letters = set()
        for term in terms:
            tranche_match = re.search(r'tranche\s*([a-f])\b', term.lower())
            if tranche_match:
                tranche_letters.add(tranche_match.group(1))
        
        if len(tranche_letters) == 1:
            components['tranche'] = list(tranche_letters)[0]

        # Extract specific amount type (prioritize more specific types)
        amount_type_patterns = [
            (r'\bcarryover\s+shortfall\b', 'carryover_shortfall'),  # Most specific first
            (r'\binterest\s+carryover\s+shortfall\b', 'interest_carryover_shortfall'),
            (r'\bprincipal\s+carryover\s+shortfall\b', 'principal_carryover_shortfall'),
            (r'\binterest\s+distributable\s+amount\b', 'interest_distributable_amount'),
            (r'\bprincipal\s+distributable\s+amount\b', 'principal_distributable_amount'),
            (r'\bdistributable\s+amount\b', 'distributable_amount'),
            (r'\bshortfall\b', 'shortfall'),
            (r'\bdistribution\b', 'distribution'),
            (r'\bdeficiency\b', 'deficiency'),
            (r'\brequired\s+amount\b', 'required_amount'),
            (r'\bpayment\s+amount\b', 'payment_amount'),
            (r'\bcollection\s+amount\b', 'collection_amount'),
        ]
        
        for pattern, amount_type in amount_type_patterns:
            if re.search(pattern, all_text) and not components['amount_type']:
                components['amount_type'] = amount_type
                break

        # FIXED: Extract instrument types with proper principal/interest distinction
        # Check for principal vs interest with more specific logic
        principal_count = len(re.findall(r'\bprincipal\b', all_text))
        interest_count = len(re.findall(r'\binterest\b', all_text))
        
        # Determine which is more dominant in this cluster
        if principal_count > interest_count:
            components['instrument'] = 'principal'
        elif interest_count > principal_count:
            components['instrument'] = 'interest'
        elif principal_count > 0 and interest_count > 0:
            # If equal, check which appears in more individual terms
            principal_terms = len([term for term in terms if 'principal' in term.lower()])
            interest_terms = len([term for term in terms if 'interest' in term.lower()])
            
            if principal_terms > interest_terms:
                components['instrument'] = 'principal'
            elif interest_terms > principal_terms:
                components['instrument'] = 'interest'
            # If still tied, don't set instrument to avoid confusion
        
        # Check for other instrument types if no principal/interest dominance
        if not components['instrument']:
            other_instrument_patterns = [
                (r'\b(note|certificate|bond|security)\b', None),
            ]
            
            for pattern, _ in other_instrument_patterns:
                match = re.search(pattern, all_text)
                if match:
                    components['instrument'] = match.group(1)
                    break
        
        # Extract financial actions/operations
        action_patterns = [
            (r'\b(payment|collection|allocation)\b', None),
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
    
    def _ensure_essential_financial_terms(self, clusters: Dict[int, Dict[str, Any]], 
                                        canonical_names: Dict[int, str]) -> Dict[int, str]:
        """Post-process to ensure essential financial terms get proper canonical names"""
        
        # Essential financial patterns that should always have good names (simplified)
        essential_patterns = {
            'servicing_fee': [r'\bservicing\s+fee', r'\bservicing\s+fees'],
            'trustee_fee': [r'\btrustee\s+fee', r'\bindenture\s+trustee', r'\bowner\s+trustee'],
            'available_funds': [r'\bavailable\s+funds', r'\btotal\s+available'],
            'reserve_fund': [r'\breserve\s+fund', r'\bcash\s+reserve'],
            'pool_factor': [r'\bpool\s+factor', r'\bfactor'],
            'overcollateralization': [r'\bovercollateralization', r'\boc\s+test'],
            'waterfall': [r'\bwaterfall', r'\bpriority\s+of\s+payments'],
        }
        
        # Track which essential patterns we've found
        found_patterns = set()
        
        # First pass: identify clusters that contain essential financial terms (but don't override good class-specific names)
        for cluster_id, cluster_data in clusters.items():
            canonical_name = canonical_names[cluster_id]
            all_text = ' '.join(cluster_data['terms']).lower()
            
            # Skip if this already has a good class-specific name
            if canonical_name.startswith('class_') and not canonical_name.startswith('excluded_') and not canonical_name.startswith('low_priority_'):
                continue
                
            # Check if this cluster contains essential financial terms
            for pattern_name, regex_list in essential_patterns.items():
                if pattern_name not in found_patterns:
                    for regex_pattern in regex_list:
                        if re.search(regex_pattern, all_text):
                            # This cluster contains an essential term - ensure it has a good name
                            if (canonical_name.startswith('excluded_') or 
                                canonical_name.startswith('low_priority_') or 
                                canonical_name in self.junk_canonical_names):
                                
                                # Check if this should be class-specific
                                class_match = re.search(r'class\s*([a-f])\b', all_text)
                                if class_match:
                                    class_letter = class_match.group(1)
                                    enhanced_name = f"class_{class_letter}_{pattern_name}"
                                else:
                                    enhanced_name = pattern_name
                                    
                                canonical_names[cluster_id] = enhanced_name
                                self.logger.info(f"Enhanced cluster {cluster_id} canonical name to '{enhanced_name}' "
                                               f"(was '{canonical_name}')")
                                
                            found_patterns.add(pattern_name)
                            break
        
        return canonical_names