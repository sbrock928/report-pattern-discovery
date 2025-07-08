"""
Financial Pattern Discovery System

A comprehensive system for automated pattern discovery in financial Excel reports
using unsupervised learning, TF-IDF clustering, and fuzzy matching.
"""

from .config import ClusteringConfig, ProcessingConfig, FinancialTerms
from .extractor import FinancialTermExtractor
from .clustering import FinancialTermClustering
from .canonical import CanonicalNameGenerator
from .fuzzy_matcher import FuzzyMatcher
from .report_generator import ExcelReportGenerator
from .main import FinancialPatternDiscovery

__version__ = "1.0.0"
__author__ = "Financial Pattern Discovery Team"

__all__ = [
    "FinancialPatternDiscovery",
    "ClusteringConfig",
    "ProcessingConfig",
    "FinancialTerms",
    "FinancialTermExtractor",
    "FinancialTermClustering",
    "CanonicalNameGenerator",
    "FuzzyMatcher",
    "ExcelReportGenerator"
]