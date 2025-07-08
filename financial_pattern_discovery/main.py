"""
Main orchestrator module for Financial Pattern Discovery System
"""

import time
import logging
import configparser
from pathlib import Path
from typing import Dict, List, Any

import numpy as np
from tqdm import tqdm

from .config import ClusteringConfig, ProcessingConfig
from .extractor import FinancialTermExtractor
from .clustering import FinancialTermClustering
from .canonical import CanonicalNameGenerator
from .fuzzy_matcher import FuzzyMatcher
from .report_generator import ExcelReportGenerator


class FinancialPatternDiscovery:
    """Main class orchestrating the financial pattern discovery process"""
    
    def __init__(self, config_file: str = "config.ini"):
        self.config_file = config_file
        self.clustering_config = None
        self.processing_config = None
        self.logger = self._setup_logging()
        
        # Load configuration
        self._load_configuration()
        
        # Initialize components
        self.extractor = FinancialTermExtractor(self.processing_config)
        self.clusterer = FinancialTermClustering(self.clustering_config)
        self.name_generator = CanonicalNameGenerator()
        self.fuzzy_matcher = FuzzyMatcher(self.processing_config)
        self.report_generator = ExcelReportGenerator(self.processing_config)
        
    def _setup_logging(self) -> logging.Logger:
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('financial_pattern_discovery.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _load_configuration(self):
        """Load configuration from file or use defaults"""
        try:
            config = configparser.ConfigParser()
            config.read(self.config_file)
            
            # Clustering configuration
            if 'clustering' in config:
                clustering_section = config['clustering']
                self.clustering_config = ClusteringConfig(
                    n_clusters=int(clustering_section.get('n_clusters', 8)),
                    max_features=int(clustering_section.get('max_features', 10000)),
                    min_df=int(clustering_section.get('min_df', 5)),
                    max_df=float(clustering_section.get('max_df', 0.5)),
                    ngram_range=eval(clustering_section.get('ngram_range', '(1, 2)')),
                    random_state=int(clustering_section.get('random_state', 42)),
                    use_hierarchical=clustering_section.get('use_hierarchical', 'false').lower() == 'true',
                    silhouette_threshold=float(clustering_section.get('silhouette_threshold', 0.3))
                )
            else:
                self.clustering_config = ClusteringConfig()
            
            # Processing configuration
            if 'processing' in config:
                processing_section = config['processing']
                self.processing_config = ProcessingConfig(
                    chunk_size=int(processing_section.get('chunk_size', 10000)),
                    max_workers=int(processing_section.get('max_workers', 4)),
                    output_format=processing_section.get('output_format', 'xlsx'),
                    temp_dir=Path(processing_section.get('temp_dir', './temp')),
                    fuzzy_threshold=int(processing_section.get('fuzzy_threshold', 80)),
                    memory_threshold=float(processing_section.get('memory_threshold', 0.8))
                )
            else:
                self.processing_config = ProcessingConfig()
            
        except Exception as e:
            self.logger.warning(f"Failed to load configuration: {e}. Using defaults.")
            self.clustering_config = ClusteringConfig()
            self.processing_config = ProcessingConfig()
    
    def process_directory(self, directory_path: Path, pattern: str = "*.xlsx", 
                         recursive: bool = False, output_path: Path = None) -> Dict[str, Any]:
        """Process all Excel files in a directory
        
        Args:
            directory_path: Path to directory containing Excel files
            pattern: File pattern to match (default: *.xlsx)
            recursive: Whether to search subdirectories recursively
            output_path: Path for output report (optional)
            
        Returns:
            Dictionary containing processing results
        """
        if not directory_path.exists():
            raise ValueError(f"Directory {directory_path} does not exist")
        
        if not directory_path.is_dir():
            raise ValueError(f"{directory_path} is not a directory")
        
        # Find Excel files
        if recursive:
            file_paths = list(directory_path.rglob(pattern))
        else:
            file_paths = list(directory_path.glob(pattern))
        
        if not file_paths:
            self.logger.warning(f"No files matching '{pattern}' found in {directory_path}")
            return {}
        
        self.logger.info(f"Found {len(file_paths)} files in {directory_path}")
        
        # Process files
        return self.process_files(file_paths, output_path)
    
    def process_files(self, file_paths: List[Path], output_path: Path = None) -> Dict[str, Any]:
        """Process multiple Excel files and generate pattern discovery report"""
        
        start_time = time.time()
        self.logger.info(f"Starting pattern discovery for {len(file_paths)} files")
        
        # Create output path if not provided
        if output_path is None:
            output_path = Path(f"financial_patterns_{int(time.time())}.xlsx")
        
        # Step 1: Extract terms from all files
        self.logger.info("Extracting financial terms from Excel files...")
        all_terms = []
        all_term_info = []
        file_term_mapping = {}
        
        progress_bar = tqdm(file_paths, desc="Processing files")
        
        for file_path in progress_bar:
            try:
                term_info_list = self.extractor.extract_headers_from_excel(file_path)
                if term_info_list:
                    # Extract just the terms for clustering
                    terms = [info['term'] for info in term_info_list]
                    all_terms.extend(terms)
                    all_term_info.extend(term_info_list)
                    file_term_mapping[str(file_path)] = term_info_list
                    progress_bar.set_postfix({"Terms extracted": len(terms)})
                else:
                    self.logger.warning(f"No terms extracted from {file_path.name}")
                
            except Exception as e:
                self.logger.error(f"Failed to process {file_path}: {e}")
                continue
        
        progress_bar.close()
        
        if not all_terms:
            self.logger.error("No terms extracted from any files")
            return {}
        
        # Log extraction statistics
        unique_terms = set(all_terms)
        self.logger.info(f"Extracted {len(all_terms)} total terms ({len(unique_terms)} unique)")
        
        # Warn if very few unique terms
        if len(unique_terms) < 10:
            self.logger.warning(f"Only {len(unique_terms)} unique terms found. This may limit clustering effectiveness.")
            self.logger.info("Consider: 1) Processing more files, 2) Checking file formats, 3) Verifying headers exist")
        
        # Step 2: Cluster terms
        self.logger.info("Clustering financial terms...")
        clustering_results = self.clusterer.cluster_terms(all_terms)
        
        if not clustering_results['clusters']:
            self.logger.error("Clustering failed")
            return {}
        
        # Step 3: Generate canonical names
        self.logger.info("Generating canonical names...")
        canonical_names = self.name_generator.generate_canonical_names(clustering_results['clusters'])
        
        # Step 4: Create fuzzy mappings with location information
        self.logger.info("Creating fuzzy mappings...")
        mappings = self.fuzzy_matcher.create_mappings(clustering_results['clusters'], canonical_names)
        
        # Add detailed location information to mappings
        for mapping in mappings:
            original_term = mapping['original_term']
            # Find the first occurrence of this term with location info
            for term_info in all_term_info:
                if term_info['term'] == original_term:
                    mapping.update({
                        'source_file': term_info['file_name'],
                        'file_path': term_info['file_path'],
                        'sheet_name': term_info['sheet_name'],
                        'row': term_info['row'],
                        'column': term_info['column'],
                        'column_letter': term_info['column_letter'],
                        'cell_address': term_info['cell_address'],
                        'original_text': term_info['original_text']
                    })
                    break
        
        # Step 5: Compile results
        processing_time = time.time() - start_time
        
        results = {
            'total_files': len(file_paths),
            'total_terms': len(all_terms),
            'unique_terms': len(set(all_terms)),
            'n_clusters': len(clustering_results['clusters']),
            'avg_cluster_size': np.mean([cluster['count'] for cluster in clustering_results['clusters'].values()]),
            'silhouette_score': clustering_results['metrics'].get('silhouette_score', 0),
            'high_confidence_count': len([m for m in mappings if m['confidence'] in ['high', 'very_high']]),
            'processing_time': processing_time,
            'clusters': clustering_results['clusters'],
            'canonical_names': canonical_names,
            'mappings': mappings,
            'file_term_mapping': file_term_mapping
        }
        
        # Step 6: Generate report
        self.logger.info("Generating Excel report...")
        self.report_generator.generate_report(results, output_path)
        
        self.logger.info(f"Pattern discovery completed in {processing_time:.2f} seconds")
        self.logger.info(f"Found {results['n_clusters']} term clusters with {results['high_confidence_count']} high-confidence mappings")
        
        return results
    
    def create_default_config(self, config_path: str = "config.ini"):
        """Create default configuration file"""
        config = configparser.ConfigParser()
        
        config['clustering'] = {
            'n_clusters': '8',
            'max_features': '10000',
            'min_df': '5',
            'max_df': '0.5',
            'ngram_range': '(1, 2)',
            'random_state': '42',
            'use_hierarchical': 'false',
            'silhouette_threshold': '0.3'
        }
        
        config['processing'] = {
            'chunk_size': '10000',
            'max_workers': '4',
            'output_format': 'xlsx',
            'temp_dir': './temp',
            'fuzzy_threshold': '80',
            'memory_threshold': '0.8'
        }
        
        with open(config_path, 'w') as configfile:
            config.write(configfile)
        
        print(f"Default configuration created at {config_path}")