"""
Configuration classes for Financial Pattern Discovery System
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


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


@dataclass
class ProcessingConfig:
    """Configuration for data processing"""
    chunk_size: int = 10000
    max_workers: int = 4
    output_format: str = 'xlsx'
    temp_dir: Path = Path('./temp')
    fuzzy_threshold: int = 80
    memory_threshold: float = 0.8
    exclude_generic_canonicals: bool = True  # New option to exclude junk canonical names
    exclude_low_priority_canonicals: bool = True  # Option to exclude low-priority terms


@dataclass
class FinancialTerms:
    """Financial terminology mappings"""
    canonical_terms: Dict[str, List[str]] = field(default_factory=lambda: {
        'revenue': ['sales', 'income', 'turnover', 'receipts', 'gross_revenue'],
        'expense': ['cost', 'expenditure', 'outlay', 'spending', 'operating_expense'],
        'profit': ['earnings', 'net_income', 'surplus', 'profit_loss'],
        'asset': ['holdings', 'property', 'resources', 'current_assets'],
        'liability': ['debt', 'obligation', 'payable', 'current_liabilities'],
        'equity': ['shareholders_equity', 'retained_earnings', 'capital'],
        'cash_flow': ['operating_cash_flow', 'free_cash_flow', 'cash_position'],
        'interest': ['interest_income', 'interest_expense', 'interest_rate'],
        'fee': ['management_fee', 'servicing_fee', 'trustee_fee', 'administration_fee'],
        'balance': ['outstanding_balance', 'principal_balance', 'account_balance']
    })
    
    financial_patterns: List[str] = field(default_factory=lambda: [
        r'\b(revenue|income|sales|turnover)\b',
        r'\b(expense|cost|expenditure|outlay)\b',
        r'\b(profit|earnings|surplus)\b',
        r'\b(asset|property|holdings)\b',
        r'\b(liability|debt|payable)\b',
        r'\b(equity|capital|retained)\b',
        r'\b(cash|flow|liquidity)\b',
        r'\b(interest|rate|yield)\b',
        r'\b(fee|charge|commission)\b',
        r'\b(balance|outstanding|principal)\b'
    ])