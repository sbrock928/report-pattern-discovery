# Quick Start Guide - Financial Pattern Discovery

This guide will help you get started with the Financial Pattern Discovery System quickly.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd financial-pattern-discovery

# Install dependencies
pip install -r requirements.txt

# Create default configuration
python scripts/run_discovery.py --create-config
```

## Basic Directory Processing

The most common use case is processing all Excel files in a directory:

```bash
# Process all Excel files in a single directory
python scripts/run_discovery.py --dir /path/to/excel/files -o patterns_report.xlsx
```

## Common Usage Patterns

### 1. Process Multiple Directories

```bash
# Process files from multiple servicer directories
python scripts/run_discovery.py --dir data/servicer_a data/servicer_b data/servicer_c -o all_servicers.xlsx
```

### 2. Recursive Directory Processing

```bash
# Process all Excel files recursively in subdirectories
python scripts/run_discovery.py --dir data --recursive -o comprehensive_report.xlsx
```

### 3. Filter by Pattern

```bash
# Process only 2024 files
python scripts/run_discovery.py --dir reports --pattern "*2024*.xlsx" -o 2024_patterns.xlsx

# Process only monthly reports
python scripts/run_discovery.py --dir data --pattern "*monthly*.xlsx" -o monthly_patterns.xlsx
```

### 4. Python Script Usage

```python
from pathlib import Path
from financial_pattern_discovery import FinancialPatternDiscovery

# Initialize the system
discoverer = FinancialPatternDiscovery()

# Process entire directory
results = discoverer.process_directory(
    directory_path=Path("data/excel_files"),
    pattern="*.xlsx",
    recursive=True,
    output_path=Path("output/patterns.xlsx")
)

# Print summary
print(f"Processed {results['total_files']} files")
print(f"Found {results['n_clusters']} pattern clusters")
```

## Directory Structure Example

Organize your files like this for best results:

```
data/
├── servicer_a/
│   ├── servicer_a_202401.xlsx
│   ├── servicer_a_202402.xlsx
│   └── servicer_a_202403.xlsx
├── servicer_b/
│   ├── servicer_b_202401.xlsx
│   ├── servicer_b_202402.xlsx
│   └── servicer_b_202403.xlsx
└── servicer_c/
    ├── servicer_c_202401.xlsx
    ├── servicer_c_202402.xlsx
    └── servicer_c_202403.xlsx
```

Then process all at once:

```bash
python scripts/run_discovery.py --dir data --recursive -o all_patterns.xlsx
```

## Output

The system generates an Excel report with four sheets:

1. **Summary** - Key metrics and statistics
2. **Cluster Details** - Discovered pattern clusters
3. **Term Mappings** - All terms mapped to canonical names
4. **Statistics** - Frequency analysis

## Tips

- **Memory Issues**: If processing hundreds of files, reduce `chunk_size` in config.ini
- **Better Clustering**: For more accurate patterns, increase `n_clusters` in config.ini
- **File Organization**: Group files by servicer in separate directories for better analysis
- **Performance**: Use `--recursive` sparingly on large directory trees

## Next Steps

- Review the generated Excel report
- Adjust configuration parameters if needed
- Use the discovered patterns for your ETL pipeline