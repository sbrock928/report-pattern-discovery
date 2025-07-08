#!/usr/bin/env python3
"""
Diagnostic tool to analyze term extraction from Excel files
Helps understand what terms are being found and why clustering might be limited
"""

import sys
from pathlib import Path
from collections import Counter

sys.path.insert(0, str(Path(__file__).parent.parent))

from financial_pattern_discovery import FinancialTermExtractor, ProcessingConfig

# =============================================================================
# CONFIGURATION - Modify these paths as needed
# =============================================================================
SOURCE_DIRECTORY = str(Path(__file__).parent.parent / "reports")  # Points to the reports subfolder
SOURCE_FILE = None                              # Set to a specific file path to analyze just one file, or None to analyze directory
FILE_PATTERN = "*.xlsx"                         # File pattern to match when analyzing directory
MAX_FILES_TO_ANALYZE = 5                        # Maximum number of files to analyze in detail
# =============================================================================


def diagnose_file(file_path: Path, show_all: bool = False):
    """Diagnose term extraction from a single file"""
    print(f"\n{'='*70}")
    print(f"Analyzing: {file_path.name}")
    print(f"{'='*70}")
    
    # Initialize extractor
    config = ProcessingConfig()
    extractor = FinancialTermExtractor(config)
    
    # Extract terms
    terms = extractor.extract_headers_from_excel(file_path)
    
    print(f"\nExtraction Results:")
    print(f"  Total terms found: {len(terms)}")
    print(f"  Unique terms: {len(set(terms))}")
    
    if not terms:
        print("\n⚠️  No terms were extracted from this file!")
        print("\nPossible reasons:")
        print("  1. The file might not contain recognizable financial headers")
        print("  2. Headers might be in unexpected formats")
        print("  3. The file might be using numeric codes instead of text labels")
        return []
    
    # Count term frequency
    term_counts = Counter(terms)
    
    print(f"\nMost common terms:")
    for term, count in term_counts.most_common(10):
        print(f"  - '{term}' (appears {count} times)")
    
    if show_all or len(set(terms)) <= 20:
        print(f"\nAll unique terms found:")
        for term in sorted(set(terms)):
            print(f"  - '{term}'")
    
    return terms


def diagnose_directory(directory: Path, pattern: str = "*.xlsx", limit: int = 5):
    """Diagnose term extraction from a directory"""
    print(f"\n{'='*70}")
    print(f"Diagnosing Directory: {directory}")
    print(f"Pattern: {pattern}")
    print(f"{'='*70}")
    
    # Find files
    files = list(directory.glob(pattern))
    if not files:
        print(f"\n❌ No files matching '{pattern}' found in {directory}")
        return
    
    print(f"\nFound {len(files)} files")
    
    # Process files
    all_terms = []
    file_term_map = {}
    
    # Analyze first few files in detail
    print(f"\nAnalyzing first {min(limit, len(files))} files in detail:")
    
    for i, file_path in enumerate(files[:limit]):
        terms = diagnose_file(file_path, show_all=True)
        all_terms.extend(terms)
        file_term_map[file_path.name] = terms
    
    # Overall statistics
    print(f"\n{'='*70}")
    print(f"OVERALL STATISTICS")
    print(f"{'='*70}")
    
    unique_terms = set(all_terms)
    print(f"\nTotal terms extracted: {len(all_terms)}")
    print(f"Unique terms: {len(unique_terms)}")
    
    # Term frequency across files
    overall_counts = Counter(all_terms)
    
    print(f"\nMost common terms across all files:")
    for term, count in overall_counts.most_common(20):
        print(f"  - '{term}' (appears {count} times)")
    
    # Clustering feasibility
    print(f"\n{'='*70}")
    print(f"CLUSTERING FEASIBILITY")
    print(f"{'='*70}")
    
    if len(unique_terms) < 5:
        print("\n⚠️  WARNING: Very few unique terms found!")
        print(f"  Only {len(unique_terms)} unique terms is too few for meaningful clustering.")
        print("\nRecommendations:")
        print("  1. Check if files contain expected financial headers")
        print("  2. Verify files are not password protected or corrupted")
        print("  3. Consider processing more files to get more variety")
    elif len(unique_terms) < 20:
        print(f"\n⚠️  Limited variety: {len(unique_terms)} unique terms")
        print("  Clustering will work but with limited granularity.")
        print(f"  Recommended clusters: {min(len(unique_terms) // 2, 5)}")
    else:
        print(f"\n✅ Good variety: {len(unique_terms)} unique terms")
        print(f"  Clustering should work well.")
        print(f"  Recommended clusters: {min(len(unique_terms) // 3, 15)}")
    
    # File variety analysis
    print(f"\n{'='*70}")
    print(f"FILE VARIETY ANALYSIS")
    print(f"{'='*70}")
    
    terms_per_file = [len(set(terms)) for terms in file_term_map.values()]
    if terms_per_file:
        avg_terms = sum(terms_per_file) / len(terms_per_file)
        print(f"\nAverage unique terms per file: {avg_terms:.1f}")
        print(f"Min terms in a file: {min(terms_per_file)}")
        print(f"Max terms in a file: {max(terms_per_file)}")
    
    # Check for common issues
    print(f"\n{'='*70}")
    print(f"COMMON ISSUES CHECK")
    print(f"{'='*70}")
    
    # Check if all terms are very similar
    if unique_terms:
        # Check if most terms contain the same words
        word_counter = Counter()
        for term in unique_terms:
            words = term.split()
            word_counter.update(words)
        
        common_words = word_counter.most_common(5)
        if common_words and common_words[0][1] > len(unique_terms) * 0.8:
            print(f"\n⚠️  Most terms contain '{common_words[0][0]}' - low variety")
    
    # Provide recommendations
    print(f"\n{'='*70}")
    print(f"RECOMMENDATIONS")
    print(f"{'='*70}")
    
    if len(unique_terms) < 10:
        print("\nTo improve pattern discovery:")
        print("1. Process more files from different time periods")
        print("2. Include files from different servicers")
        print("3. Check if files use standardized headers")
        print("4. Consider lowering min_df in config.ini")
    else:
        print("\n✅ Your files appear suitable for pattern discovery!")
        print("\nNext steps:")
        print("1. Run the full pattern discovery process")
        print("2. Review the generated report")
        print("3. Adjust clustering parameters if needed")


def main():
    """Main diagnostic function"""
    
    print("Financial Pattern Discovery - Diagnostic Tool")
    print("=" * 50)
    
    try:
        if SOURCE_FILE:
            # Analyze single file
            file_path = Path(SOURCE_FILE)
            if not file_path.exists():
                print(f"❌ File not found: {file_path}")
                print(f"Please update SOURCE_FILE in the script to point to your Excel file")
                return 1
            diagnose_file(file_path, show_all=True)
        else:
            # Analyze directory
            dir_path = Path(SOURCE_DIRECTORY)
            if not dir_path.exists():
                print(f"❌ Directory not found: {dir_path}")
                print(f"Please update SOURCE_DIRECTORY in the script to point to your Excel files directory")
                return 1
            diagnose_directory(dir_path, FILE_PATTERN, MAX_FILES_TO_ANALYZE)
        
        return 0
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())