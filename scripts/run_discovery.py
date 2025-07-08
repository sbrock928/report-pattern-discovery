#!/usr/bin/env python3
"""
Command-line interface for Financial Pattern Discovery System
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from financial_pattern_discovery import FinancialPatternDiscovery

# =============================================================================
# CONFIGURATION - Modify these paths as needed
# =============================================================================
SOURCE_DIRECTORIES = [str(Path(__file__).parent.parent / "reports")]  # Points to the reports subfolder
SOURCE_FILES = []                                   # List of specific files to process (optional)
OUTPUT_FILE = None                                  # Output report file (None = auto-generate with timestamp)
FILE_PATTERN = "*.xlsx"                            # File pattern to match
RECURSIVE = True                                   # Process directories recursively
CONFIG_FILE = "config.ini"                        # Configuration file to use
# =============================================================================


def main():
    """Main function for processing"""
    
    print("Financial Pattern Discovery System")
    print("=" * 40)
    
    # Collect files from various sources
    file_paths = []
    
    # Process directories if provided
    if SOURCE_DIRECTORIES:
        for directory in SOURCE_DIRECTORIES:
            dir_path = Path(directory)
            if not dir_path.exists():
                print(f"Error: Directory '{dir_path}' does not exist")
                print(f"Please update SOURCE_DIRECTORIES in the script")
                return 1
            if not dir_path.is_dir():
                print(f"Error: '{dir_path}' is not a directory")
                return 1
            
            # Find Excel files in directory
            if RECURSIVE:
                # Recursive search
                pattern_files = list(dir_path.rglob(FILE_PATTERN))
            else:
                # Non-recursive search
                pattern_files = list(dir_path.glob(FILE_PATTERN))
            
            if not pattern_files:
                print(f"Warning: No files matching '{FILE_PATTERN}' found in {dir_path}")
            else:
                print(f"Found {len(pattern_files)} files in {dir_path}")
                file_paths.extend(pattern_files)
    
    # Process individual files if provided
    if SOURCE_FILES:
        for file_path_str in SOURCE_FILES:
            path = Path(file_path_str)
            if not path.exists():
                print(f"Error: File '{path}' does not exist")
                return 1
            if not path.is_file():
                print(f"Error: '{path}' is not a file")
                return 1
            file_paths.append(path)
    
    # Check if any files were found
    if not file_paths:
        print("Error: No files found to process.")
        print("Please update SOURCE_DIRECTORIES or SOURCE_FILES in the script")
        return 1
    
    # Remove duplicates and filter for Excel files
    file_paths = list(set(file_paths))
    excel_extensions = {'.xlsx', '.xls', '.xlsm', '.xlsb'}
    file_paths = [f for f in file_paths if f.suffix.lower() in excel_extensions]
    
    if not file_paths:
        print("Error: No Excel files found to process")
        return 1
    
    # Sort files for consistent processing
    file_paths.sort()
    
    print(f"\n📊 Found {len(file_paths)} Excel file(s) to process")
    
    # Show file summary
    if len(file_paths) <= 10:
        print("\nFiles to process:")
        for f in file_paths:
            print(f"  • {f}")
    else:
        print(f"\nShowing first 10 of {len(file_paths)} files:")
        for f in file_paths[:10]:
            print(f"  • {f}")
        print(f"  ... and {len(file_paths) - 10} more files")
    
    # Show directory summary if processing directories
    if SOURCE_DIRECTORIES:
        dir_summary = {}
        for f in file_paths:
            parent = f.parent
            dir_summary[parent] = dir_summary.get(parent, 0) + 1
        
        print("\nFiles by directory:")
        for directory, count in sorted(dir_summary.items()):
            print(f"  • {directory}: {count} files")
    
    # Initialize discovery system
    try:
        discoverer = FinancialPatternDiscovery(CONFIG_FILE)
    except Exception as e:
        print(f"Error initializing discovery system: {e}")
        return 1
    
    # Process files
    try:
        output_path = Path(OUTPUT_FILE) if OUTPUT_FILE else None
        results = discoverer.process_files(file_paths, output_path)
        
        if results:
            # Get the actual output filename from the results or use the passed output_path
            actual_output = results.get('output_file', output_path)
            
            print(f"\n✅ Pattern Discovery Complete!")
            print(f"📊 Files processed: {results['total_files']}")
            print(f"📝 Terms extracted: {results['total_terms']} ({results['unique_terms']} unique)")
            print(f"🎯 Clusters found: {results['n_clusters']}")
            print(f"✨ High-confidence mappings: {results['high_confidence_count']}")
            print(f"⏱️  Processing time: {results['processing_time']:.2f} seconds")
            print(f"\n📄 Report saved to: {actual_output}")
            
            return 0
        else:
            print("\n❌ Pattern discovery failed. Check the log file for details.")
            return 1
            
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        return 130
    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())