#!/usr/bin/env python3
"""
Simple script to process all Excel files in a directory
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from financial_pattern_discovery import FinancialPatternDiscovery

# =============================================================================
# CONFIGURATION - Modify these paths as needed
# =============================================================================
SOURCE_DIRECTORY = str(Path(__file__).parent.parent / "reports")  # Points to the reports subfolder
OUTPUT_FILE = "financial_patterns.xlsx"         # Change this to your desired output file
FILE_PATTERN = "*.xlsx"                         # File pattern to match
RECURSIVE = True                                # Search subdirectories recursively
CONFIG_FILE = "config.ini"                     # Configuration file to use
# =============================================================================


def main():
    """Simple directory processing"""
    
    # Validate directory
    dir_path = Path(SOURCE_DIRECTORY)
    if not dir_path.exists():
        print(f"❌ Error: Directory '{dir_path}' does not exist")
        print(f"Please update SOURCE_DIRECTORY in the script to point to your Excel files")
        return 1
    
    if not dir_path.is_dir():
        print(f"❌ Error: '{dir_path}' is not a directory")
        return 1
    
    output_path = Path(OUTPUT_FILE)
    
    print(f"📁 Processing directory: {dir_path}")
    print(f"🔍 Pattern: {FILE_PATTERN}")
    print(f"🔄 Recursive: {'Yes' if RECURSIVE else 'No'}")
    print(f"📄 Output: {output_path}\n")
    
    try:
        # Initialize discovery system
        discoverer = FinancialPatternDiscovery(CONFIG_FILE)
        
        # Process directory
        results = discoverer.process_directory(
            directory_path=dir_path,
            pattern=FILE_PATTERN,
            recursive=RECURSIVE,
            output_path=output_path
        )
        
        if results:
            print(f"\n✅ Success! Pattern discovery complete")
            print(f"📊 Files processed: {results['total_files']}")
            print(f"📝 Terms extracted: {results['total_terms']}")
            print(f"🎯 Pattern clusters: {results['n_clusters']}")
            print(f"✨ High-confidence mappings: {results['high_confidence_count']}")
            print(f"⏱️  Processing time: {results['processing_time']:.2f} seconds")
            print(f"\n📈 Report saved to: {output_path}")
            return 0
        else:
            print("\n❌ No results generated. Check the log for details.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        return 130
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())