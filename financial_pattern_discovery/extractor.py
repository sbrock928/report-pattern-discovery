"""
Excel term extraction module for Financial Pattern Discovery System
"""

import re
import logging
from pathlib import Path
from typing import List, Set
from openpyxl import load_workbook

from .config import ProcessingConfig, FinancialTerms


class FinancialTermExtractor:
    """Extract and preprocess financial terms from Excel files"""
    
    def __init__(self, config: ProcessingConfig):
        self.config = config
        self.financial_terms = FinancialTerms()
        self.logger = logging.getLogger(__name__)
        
        # Built-in stopwords list (no NLTK required)
        self.stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 
            'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself',
            'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them',
            'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this',
            'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been',
            'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
            'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until',  # Removed 'a'
            'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between',
            'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to',
            'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again',
            'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how',
            'all', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
            'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
            's', 't', 'can', 'will', 'just', 'don', 'should', 'now', 'd', 'll', 'm',
            'o', 're', 've', 'y', 'ain', 'aren', 'couldn', 'didn', 'doesn', 'hadn',
            'hasn', 'haven', 'isn', 'ma', 'mightn', 'mustn', 'needn', 'shan', 'shouldn',
            'wasn', 'weren', 'won', 'wouldn'
        }
        
        # Remove financial terms and class identifiers from stopwords
        financial_stop_words = {'annual', 'quarterly', 'monthly', 'total', 'gross', 'net'}
        class_identifiers = {'a', 'b', 'c', 'd', 'e', 'f'}  # Important class letters
        self.stop_words = self.stop_words - financial_stop_words - class_identifiers
        
    def extract_headers_from_excel(self, file_path: Path) -> List[dict]:
        """Extract header/label cells from Excel file with location information"""
        try:
            # Try reading with openpyxl for better format detection
            workbook = load_workbook(file_path, read_only=True)
            headers = []
            file_stats = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'total_sheets': len(workbook.sheetnames),
                'sheets': {}
            }
            
            for sheet_name in workbook.sheetnames:
                try:
                    sheet = workbook[sheet_name]
                    sheet_headers = self._extract_headers_from_sheet(sheet, sheet_name, file_path)
                    headers.extend(sheet_headers)
                    
                    # Collect sheet statistics
                    file_stats['sheets'][sheet_name] = {
                        'max_row': sheet.max_row,
                        'max_column': sheet.max_column,
                        'headers_found': len(sheet_headers)
                    }
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process sheet {sheet_name}: {e}")
                    continue
            
            workbook.close()
            
            # Calculate file totals
            file_stats['total_max_rows'] = max([stats['max_row'] for stats in file_stats['sheets'].values()]) if file_stats['sheets'] else 0
            file_stats['total_max_columns'] = max([stats['max_column'] for stats in file_stats['sheets'].values()]) if file_stats['sheets'] else 0
            file_stats['total_headers_found'] = len(headers)
            
            # Remove duplicates while preserving location info for the first occurrence
            seen_terms = {}
            unique_headers = []
            
            for header_info in headers:
                term = header_info['term']
                if term not in seen_terms:
                    seen_terms[term] = True
                    # Add file statistics to each header info
                    header_info['file_stats'] = file_stats
                    unique_headers.append(header_info)
            
            return unique_headers
            
        except Exception as e:
            self.logger.error(f"Failed to extract headers from {file_path}: {e}")
            return []
    
    def _extract_headers_from_sheet(self, sheet, sheet_name: str, file_path: Path) -> List[dict]:
        """Extract headers from a specific sheet with location information"""
        headers = []
        # Scan more rows to find financial terms throughout the document
        max_rows = min(200, sheet.max_row)  # Increased from 20 to 200 rows
        
        for row_idx in range(1, max_rows + 1):
            row = sheet[row_idx]
            
            for cell in row:
                if self._is_header_cell(cell):
                    cleaned_text = self._clean_financial_text(str(cell.value))
                    if cleaned_text and len(cleaned_text) > 2:
                        header_info = {
                            'term': cleaned_text,
                            'original_text': str(cell.value),
                            'file_path': str(file_path),
                            'file_name': file_path.name,
                            'sheet_name': sheet_name,
                            'row': cell.row,
                            'column': cell.column,
                            'column_letter': cell.column_letter,
                            'cell_address': f"{cell.column_letter}{cell.row}"
                        }
                        headers.append(header_info)
        
        return headers
    
    def _is_header_cell(self, cell) -> bool:
        """Determine if a cell contains header/label text"""
        if not cell.value or not isinstance(cell.value, str):
            return False
            
        text = str(cell.value).strip()
        
        # Skip if too short or too long
        if len(text) < 3 or len(text) > 200:  # Increased max length to capture more complete headers
            return False
            
        # Skip if mostly numbers (but allow some numbers for class identifiers)
        number_ratio = len(re.findall(r'\d', text)) / len(text)
        if number_ratio > 0.7:  # Allow up to 70% numbers (was 100% before)
            return False
            
        # Enhanced financial terminology detection
        financial_keywords = [
            # Core financial terms
            'balance', 'amount', 'payment', 'fee', 'rate', 'interest', 'principal',
            'collection', 'distribution', 'outstanding', 'aggregate', 'eligible',
            'contract', 'loan', 'note', 'servicer', 'dealer', 'purchased',
            'reserve', 'account', 'funds', 'available', 'allocation', 'period',
            'beginning', 'ending', 'date', 'determination', 'closing', 'cut',
            'delinquent', 'default', 'loss', 'charge', 'write', 'prepayment',
            'advance', 'excess', 'carryover', 'factor', 'pool', 'waterfall',
            
            # Class-specific terms (key addition)
            'class', 'tranche', 'series', 'tier',
            
            # Additional structured finance terms
            'subordinate', 'senior', 'mezzanine', 'equity', 'residual',
            'enhancement', 'support', 'overcollateralization', 'coverage',
            'trigger', 'threshold', 'target', 'floor', 'cap', 'spread',
            'margin', 'basis', 'points', 'yield', 'coupon', 'accrual',
            'amortization', 'maturity', 'weighted', 'average', 'life'
        ]
        
        text_lower = text.lower()
        
        # Check if text contains financial keywords
        for keyword in financial_keywords:
            if keyword in text_lower:
                return True
        
        # Enhanced class-based pattern detection
        class_patterns = [
            r'class\s*[a-z]\s*\w+',  # "class a interest", "class b notes"
            r'class\s*[a-z]$',       # "class a"
            r'series\s*\w+',         # "series 2024-1"
            r'tranche\s*[a-z]',      # "tranche a"
            r'tier\s*\d+',           # "tier 1"
        ]
        
        for pattern in class_patterns:
            if re.search(pattern, text_lower):
                return True
        
        # Check for financial terminology patterns
        for pattern in self.financial_terms.financial_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Enhanced header patterns
        header_patterns = [
            r'^\w+\s+(fee|rate|amount|balance|income|expense)',
            r'^(total|net|gross|current|long.term)',
            r'^(description|account|code|reference|date)',
            r'outstanding.*balance',
            r'aggregate.*amount',
            r'eligible.*contract',
            r'class\s+[a-z]\s+',
            r'beginning.*period',
            r'end.*period',
            r'collection.*period',
            r'distribution.*date',
            
            # Additional structured patterns
            r'\w+.*interest.*\w+',
            r'\w+.*balance.*\w+',
            r'\w+.*amount.*\w+',
            r'accrued.*\w+',
            r'available.*\w+',
            r'required.*\w+',
        ]
        
        for pattern in header_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        return False
    
    def _clean_financial_text(self, text: str) -> str:
        """Clean and normalize financial text"""
        if not text:
            return ""
            
        # Convert to lowercase
        text = text.lower().strip()
        
        # Remove percentage values and their patterns
        text = re.sub(r'\d+\.?\d*\s*%', '', text)  # Remove "4.12%", "5.83%", etc.
        text = re.sub(r'\d+\.?\d*\s*percent', '', text)  # Remove "4.12 percent"
        
        # Remove other numeric values that aren't meaningful for categorization
        text = re.sub(r'\$[\d,]+\.?\d*', '', text)  # Remove dollar amounts
        text = re.sub(r'\b\d{1,2}/\d{1,2}/\d{2,4}\b', '', text)  # Remove dates
        text = re.sub(r'\b\d+\.\d+\b', '', text)  # Remove decimal numbers
        text = re.sub(r'\b\d{4,}\b', '', text)  # Remove large numbers (years, IDs, etc.)
        
        # Remove parentheses and their contents (often numbers or codes)
        text = re.sub(r'\([^)]*\)', '', text)
        
        # Remove numbers at the beginning (like {1}, {2}, etc.)
        text = re.sub(r'^\{\d+\}\s*', '', text)
        
        # Remove trailing colons and excessive punctuation
        text = re.sub(r'[:\.,;]+$', '', text)
        
        # Remove common prefixes/suffixes but keep important ones
        text = re.sub(r'\b(the|was|were|equal|to|of|in|at|on|for|with|by)\b', '', text)
        
        # Normalize separators first
        text = re.sub(r'[_\-\s]+', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Simple tokenization without NLTK
        words = text.split()
        
        # Remove stopwords and very short words, but keep important financial terms
        financial_keepers = {'fee', 'tax', 'ytd', 'apr', 'apy', 'cpr', 'psa', 'a', 'b', 'c', 'd', 'e', 'f'}
        cleaned_words = []
        
        for word in words:
            if (len(word) > 2 or word in financial_keepers) and word not in self.stop_words:
                cleaned_words.append(word)
        
        # Remove duplicate consecutive words (this fixes "class class class" issues)
        deduplicated_words = []
        prev_word = None
        
        for word in cleaned_words:
            if word != prev_word:
                deduplicated_words.append(word)
            prev_word = word
        
        return ' '.join(deduplicated_words)