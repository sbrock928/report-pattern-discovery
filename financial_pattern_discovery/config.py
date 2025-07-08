"""
Configuration classes for Financial Pattern Discovery System
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple, Set


@dataclass
class NLTKConfig:
    """Configuration for NLTK-enhanced processing"""
    # Core NLTK features
    use_lemmatization: bool = True
    use_pos_tagging: bool = True
    use_named_entity_recognition: bool = True
    
    # Financial domain customization
    financial_stopwords_to_remove: Set[str] = field(default_factory=lambda: {
        # Generic business terms that add noise
        'company', 'corporation', 'entity', 'organization', 'business',
        'management', 'report', 'statement', 'document', 'filing',
        'section', 'subsection', 'paragraph', 'clause', 'provision',
        'appendix', 'exhibit', 'schedule', 'attachment', 'supplement'
    })
    
    financial_terms_to_preserve: Set[str] = field(default_factory=lambda: {
        # Critical financial terms that should never be filtered
        'fee', 'fees', 'tax', 'taxes', 'rate', 'rates', 'factor', 'factors',
        'balance', 'balances', 'amount', 'amounts', 'payment', 'payments',
        'interest', 'principal', 'yield', 'coupon', 'spread', 'margin',
        'tranche', 'tranches', 'class', 'classes', 'series', 'tier', 'tiers',
        'reserve', 'reserves', 'fund', 'funds', 'account', 'accounts',
        'servicer', 'servicers', 'trustee', 'trustees', 'dealer', 'dealers',
        'collection', 'collections', 'distribution', 'distributions',
        'shortfall', 'shortfalls', 'carryover', 'carryovers', 'deficiency',
        'overcollateralization', 'enhancement', 'support', 'waterfall',
        # Class identifiers (critical for structured finance)
        'a', 'b', 'c', 'd', 'e', 'f', 'i', 'ii', 'iii', 'iv', 'v', 'vi'
    })
    
    # Financial entity patterns for NER enhancement
    financial_entity_patterns: List[str] = field(default_factory=lambda: [
        r'\b[Cc]lass\s+[A-F]\b',           # Class A, Class B, etc.
        r'\b[Tt]ranche\s+[A-F]\b',         # Tranche A, Tranche B, etc.
        r'\b[Ss]eries\s+\d{4}-\d+\b',     # Series 2024-1, etc.
        r'\b[Tt]ier\s+\d+\b',             # Tier 1, Tier 2, etc.
        r'\$[\d,]+(?:\.\d{2})?\b',         # Dollar amounts
        r'\d+\.?\d*%',                     # Percentage values
        r'\b\d{1,2}/\d{1,2}/\d{2,4}\b',   # Dates
    ])
    
    # POS tag priorities for financial context
    important_pos_tags: Dict[str, float] = field(default_factory=lambda: {
        'NN': 1.0,    # Noun (balance, payment, fee)
        'NNS': 1.0,   # Noun plural (balances, payments, fees)
        'NNP': 0.9,   # Proper noun (Class, Servicer names)
        'NNPS': 0.9,  # Proper noun plural
        'CD': 0.8,    # Cardinal number (useful for class identifiers)
        'JJ': 0.6,    # Adjective (outstanding, available, eligible)
        'VBG': 0.5,   # Gerund (servicing, beginning, ending)
        'VBN': 0.5,   # Past participle (accrued, distributed)
    })
    
    # Minimum financial relevance score threshold
    financial_relevance_threshold: float = 0.25
    
    # Lemmatization customization
    preserve_financial_plurals: bool = True  # Keep "fees" vs "fee" distinction
    custom_lemma_exceptions: Dict[str, str] = field(default_factory=lambda: {
        # Financial terms with specific meanings in plural
        'fees': 'fee',
        'taxes': 'tax', 
        'reserves': 'reserve',
        'funds': 'fund',
        'securities': 'security',
        'proceeds': 'proceeds',  # Always plural in finance
        'earnings': 'earnings',  # Always plural in finance
    })


@dataclass
class ClusteringConfig:
    """Configuration for clustering parameters"""
    n_clusters: int = 8
    max_features: int = 10000
    min_df: int = 2  # Lowered from 5 for smaller datasets
    max_df: float = 0.95  # Increased from 0.5 to be more inclusive
    ngram_range: Tuple[int, int] = (1, 2)
    random_state: int = 42
    use_hierarchical: bool = False
    silhouette_threshold: float = 0.2  # Lowered from 0.3 for more flexibility
    
    # Class-aware clustering parameters
    class_separation_enabled: bool = True
    class_clustering_aggressiveness: float = 0.5  # 0.0 = conservative, 1.0 = aggressive
    min_class_cluster_size: int = 1
    
    # Financial domain clustering weights
    financial_term_weight: float = 2.0  # Boost TF-IDF for financial terms
    class_identifier_weight: float = 3.0  # Strong boost for class identifiers
    temporal_term_weight: float = 0.8  # Reduce weight for temporal terms


@dataclass
class ProcessingConfig:
    """Configuration for data processing"""
    chunk_size: int = 10000
    max_workers: int = 4
    output_format: str = 'xlsx'
    temp_dir: Path = Path('./temp')
    fuzzy_threshold: int = 70  # Lowered from 80 for more inclusive matching
    memory_threshold: float = 0.8
    exclude_generic_canonicals: bool = True
    exclude_low_priority_canonicals: bool = True
    
    # NLTK configuration
    nltk_config: NLTKConfig = field(default_factory=NLTKConfig)
    
    # Advanced financial term filtering
    min_term_length: int = 2
    max_term_length: int = 150
    numeric_content_threshold: float = 0.7  # Max ratio of numbers to characters
    
    # Enhanced financial context detection
    require_financial_context: bool = True
    financial_context_threshold: float = 0.3


@dataclass
class FinancialTerms:
    """Enhanced financial terminology mappings with NLTK integration"""
    
    # Core canonical terms (enhanced)
    canonical_terms: Dict[str, List[str]] = field(default_factory=lambda: {
        # Enhanced fee categories
        'servicing_fee': ['servicing fee', 'servicing fees', 'servicer fee', 'servicer fees', 
                         'service fee', 'servicing compensation', 'servicer compensation'],
        'trustee_fee': ['trustee fee', 'trustee fees', 'indenture trustee fee', 'owner trustee fee',
                       'backup trustee fee', 'trustee compensation'],
        'administration_fee': ['administration fee', 'admin fee', 'administrative fee',
                              'administrative costs', 'administration costs'],
        
        # Enhanced amount categories  
        'distributable_amount': ['distributable amount', 'distribution amount', 'available distribution',
                               'distributable funds', 'distribution proceeds'],
        'shortfall_amount': ['shortfall amount', 'shortfall', 'deficiency amount', 'deficiency',
                           'carryover shortfall', 'interest shortfall', 'principal shortfall'],
        'required_amount': ['required amount', 'required payment', 'required distribution',
                          'payment amount', 'required funds'],
        
        # Enhanced balance categories
        'outstanding_balance': ['outstanding balance', 'outstanding principal', 'outstanding amount',
                              'unpaid balance', 'remaining balance'],
        'pool_balance': ['pool balance', 'aggregate balance', 'total balance', 'collective balance',
                        'pool principal', 'aggregate principal'],
        
        # Class-specific enhancements
        'class_a_terms': ['class a', 'class a notes', 'class a certificates', 'class a securities',
                         'senior class', 'class a principal', 'class a interest'],
        'class_b_terms': ['class b', 'class b notes', 'class b certificates', 'class b securities',
                         'subordinate class', 'class b principal', 'class b interest'],
        
        # Temporal terms
        'period_terms': ['collection period', 'interest period', 'payment period', 'calculation period',
                        'determination period', 'distribution period'],
        'date_terms': ['distribution date', 'payment date', 'determination date', 'closing date',
                      'cut-off date', 'calculation date']
    })
    
    # Enhanced financial patterns with NLTK-compatible regex
    financial_patterns: List[str] = field(default_factory=lambda: [
        # Fee patterns
        r'\b(?:servicing|servicer|trustee|administration|admin)\s+fees?\b',
        r'\b(?:backup|owner|indenture)\s+trustee\s+fees?\b',
        
        # Amount patterns
        r'\b(?:distributable|required|payment|shortfall|deficiency)\s+amounts?\b',
        r'\b(?:carryover|interest|principal)\s+shortfalls?\b',
        
        # Balance patterns  
        r'\b(?:outstanding|pool|aggregate|total)\s+balances?\b',
        r'\b(?:beginning|ending|current)\s+balances?\b',
        
        # Class patterns (enhanced)
        r'\bclass\s+[a-f]\s+(?:notes?|certificates?|securities?|principal|interest|amounts?|balances?)\b',
        r'\btranche\s+[a-f]\s+(?:notes?|certificates?|securities?)\b',
        
        # Temporal patterns
        r'\b(?:collection|interest|payment|calculation|determination|distribution)\s+periods?\b',
        r'\b(?:distribution|payment|determination|closing|cut-off|calculation)\s+dates?\b',
        
        # Financial operations
        r'\b(?:overcollateralization|enhancement|support|waterfall|allocation)\b',
        r'\b(?:advance|excess|reserve|fund|account|proceeds)\b'
    ])
    
    # NLTK-enhanced synonym groups for better clustering
    synonym_groups: Dict[str, List[str]] = field(default_factory=lambda: {
        'fee_synonyms': ['fee', 'fees', 'charge', 'charges', 'cost', 'costs', 'expense', 'expenses'],
        'amount_synonyms': ['amount', 'amounts', 'sum', 'sums', 'total', 'totals', 'value', 'values'],
        'balance_synonyms': ['balance', 'balances', 'outstanding', 'remaining', 'unpaid'],
        'period_synonyms': ['period', 'periods', 'term', 'terms', 'duration', 'interval'],
        'date_synonyms': ['date', 'dates', 'day', 'days', 'time', 'timing'],
        'class_synonyms': ['class', 'classes', 'tranche', 'tranches', 'series', 'tier', 'tiers']
    })
    
    # Financial context indicators for NLTK scoring
    strong_financial_indicators: Set[str] = field(default_factory=lambda: {
        'servicing', 'servicer', 'trustee', 'dealer', 'sponsor', 'originator',
        'collateral', 'security', 'securities', 'note', 'notes', 'certificate',
        'waterfall', 'allocation', 'distribution', 'collection', 'advance',
        'overcollateralization', 'enhancement', 'support', 'trigger', 'test',
        'covenant', 'compliance', 'default', 'delinquency', 'prepayment'
    })
    
    weak_financial_indicators: Set[str] = field(default_factory=lambda: {
        'balance', 'amount', 'payment', 'fee', 'rate', 'interest', 'principal',
        'fund', 'account', 'reserve', 'available', 'required', 'eligible',
        'aggregate', 'total', 'net', 'gross', 'current', 'outstanding'
    })