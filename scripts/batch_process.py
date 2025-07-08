#!/usr/bin/env python3
"""
Batch processing example for multiple directories with different configurations
"""

import sys
from pathlib import Path
import json
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from financial_pattern_discovery import (
    FinancialPatternDiscovery,
    ClusteringConfig,
    ProcessingConfig
)


def batch_process_servicers():
    """Process multiple servicer directories with custom configurations"""
    
    # Define servicer-specific configurations
    servicer_configs = {
        'servicer_a': {
            'directory': 'data/servicer_a',
            'pattern': '*.xlsx',
            'clustering': {
                'n_clusters': 10,  # More clusters for servicer A
                'min_df': 3,
                'fuzzy_threshold': 85
            }
        },
        'servicer_b': {
            'directory': 'data/servicer_b', 
            'pattern': '*.xlsx',
            'clustering': {
                'n_clusters': 8,
                'min_df': 5,
                'fuzzy_threshold': 80
            }
        },
        'servicer_c': {
            'directory': 'data/servicer_c',
            'pattern': '*monthly*.xlsx',  # Only monthly reports
            'clustering': {
                'n_clusters': 6,
                'min_df': 2,
                'fuzzy_threshold': 90
            }
        }
    }
    
    # Track results
    all_results = {}
    summary_stats = []
    
    print("🚀 Starting batch processing of servicer directories\n")
    
    for servicer, config in servicer_configs.items():
        print(f"📊 Processing {servicer.upper()}...")
        
        try:
            # Create custom configuration
            clustering_config = ClusteringConfig(
                n_clusters=config['clustering'].get('n_clusters', 8),
                min_df=config['clustering'].get('min_df', 5)
            )
            
            processing_config = ProcessingConfig(
                fuzzy_threshold=config['clustering'].get('fuzzy_threshold', 80)
            )
            
            # Initialize discovery system
            discoverer = FinancialPatternDiscovery()
            discoverer.clustering_config = clustering_config
            discoverer.processing_config = processing_config
            
            # Process directory
            results = discoverer.process_directory(
                directory_path=Path(config['directory']),
                pattern=config['pattern'],
                recursive=True,
                output_path=Path(f"patterns_{servicer}_{datetime.now().strftime('%Y%m%d')}.xlsx")
            )
            
            # Store results
            all_results[servicer] = results
            
            # Collect summary stats
            if results:
                summary_stats.append({
                    'servicer': servicer,
                    'files_processed': results['total_files'],
                    'terms_extracted': results['total_terms'],
                    'clusters_found': results['n_clusters'],
                    'high_confidence': results['high_confidence_count'],
                    'processing_time': results['processing_time']
                })
                
                print(f"  ✅ Completed: {results['total_files']} files, {results['n_clusters']} clusters\n")
            else:
                print(f"  ⚠️  No files found or processing failed\n")
                
        except Exception as e:
            print(f"  ❌ Error processing {servicer}: {e}\n")
            continue
    
    # Generate combined summary report
    print("\n📈 BATCH PROCESSING SUMMARY")
    print("=" * 50)
    
    total_files = sum(s['files_processed'] for s in summary_stats)
    total_terms = sum(s['terms_extracted'] for s in summary_stats)
    total_time = sum(s['processing_time'] for s in summary_stats)
    
    print(f"Total servicers processed: {len(summary_stats)}")
    print(f"Total files processed: {total_files}")
    print(f"Total terms extracted: {total_terms}")
    print(f"Total processing time: {total_time:.2f} seconds")
    
    print("\nPer-servicer breakdown:")
    for stat in summary_stats:
        print(f"\n{stat['servicer'].upper()}:")
        print(f"  Files: {stat['files_processed']}")
        print(f"  Terms: {stat['terms_extracted']}")
        print(f"  Clusters: {stat['clusters_found']}")
        print(f"  High confidence: {stat['high_confidence']}")
    
    # Save summary to JSON
    summary_file = f"batch_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'summary_stats': summary_stats,
            'totals': {
                'servicers': len(summary_stats),
                'files': total_files,
                'terms': total_terms,
                'processing_time': total_time
            }
        }, f, indent=2)
    
    print(f"\n📄 Summary saved to: {summary_file}")
    
    return all_results


def process_by_date_range():
    """Process files based on date patterns"""
    
    print("\n📅 Processing files by date range\n")
    
    discoverer = FinancialPatternDiscovery()
    base_dir = Path("data/reports")
    
    # Define date ranges
    date_ranges = {
        'Q1_2024': ['*202401*.xlsx', '*202402*.xlsx', '*202403*.xlsx'],
        'Q2_2024': ['*202404*.xlsx', '*202405*.xlsx', '*202406*.xlsx'],
        'Q3_2024': ['*202407*.xlsx', '*202408*.xlsx', '*202409*.xlsx'],
        'Q4_2024': ['*202410*.xlsx', '*202411*.xlsx', '*202412*.xlsx']
    }
    
    for quarter, patterns in date_ranges.items():
        print(f"Processing {quarter}...")
        
        # Collect all files for this quarter
        quarter_files = []
        for pattern in patterns:
            files = list(base_dir.rglob(pattern))
            quarter_files.extend(files)
        
        if quarter_files:
            print(f"  Found {len(quarter_files)} files")
            
            results = discoverer.process_files(
                quarter_files,
                Path(f"patterns_{quarter}.xlsx")
            )
            
            print(f"  ✅ Completed: {results['n_clusters']} pattern clusters found\n")
        else:
            print(f"  ⚠️  No files found for {quarter}\n")


def incremental_batch_processing():
    """Process new files incrementally"""
    
    print("\n🔄 Incremental batch processing\n")
    
    # Track processed files
    processed_files_log = Path("processed_files.json")
    
    # Load previously processed files
    if processed_files_log.exists():
        with open(processed_files_log, 'r') as f:
            processed_files = set(json.load(f))
    else:
        processed_files = set()
    
    # Find all Excel files
    all_files = list(Path("data").rglob("*.xlsx"))
    
    # Filter new files only
    new_files = [f for f in all_files if str(f) not in processed_files]
    
    if not new_files:
        print("No new files to process")
        return
    
    print(f"Found {len(new_files)} new files to process")
    print(f"Previously processed: {len(processed_files)} files")
    
    # Process new files
    discoverer = FinancialPatternDiscovery()
    results = discoverer.process_files(
        new_files,
        Path(f"incremental_patterns_{datetime.now().strftime('%Y%m%d')}.xlsx")
    )
    
    # Update processed files log
    for f in new_files:
        processed_files.add(str(f))
    
    with open(processed_files_log, 'w') as f:
        json.dump(list(processed_files), f, indent=2)
    
    print(f"\n✅ Processed {len(new_files)} new files")
    print(f"Total files in history: {len(processed_files)}")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch processing examples")
    parser.add_argument(
        '--mode',
        choices=['servicers', 'dates', 'incremental'],
        default='servicers',
        help='Batch processing mode'
    )
    
    args = parser.parse_args()
    
    try:
        if args.mode == 'servicers':
            batch_process_servicers()
        elif args.mode == 'dates':
            process_by_date_range()
        elif args.mode == 'incremental':
            incremental_batch_processing()
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()