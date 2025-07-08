# Financial Pattern Discovery System

An automated pattern discovery system for financial Excel reports using unsupervised machine learning, TF-IDF clustering, and fuzzy matching to identify and normalize financial terminology across multiple servicers.

## 🚀 Features

- **Automated Term Extraction**: Intelligently extracts financial headers and labels from Excel files
- **Unsupervised Clustering**: Uses TF-IDF and clustering algorithms to group similar financial terms
- **Canonical Name Generation**: Automatically generates standardized names for term clusters
- **Fuzzy Matching**: High-performance fuzzy matching with confidence scoring
- **Comprehensive Reporting**: Multi-sheet Excel reports with detailed analysis
- **Scalable Architecture**: Handles hundreds of files with configurable parallel processing
- **No Manual Setup Required**: Works without pre-existing templates or labeled data
- **Offline Ready**: Works completely offline - no internet connection required
- **Corporate Firewall Friendly**: No external API calls or model downloads

## 📋 Requirements

- Python 3.8 or higher
- No internet connection required after initial package installation
- See `requirements.txt` for all dependencies

## 🛠️ Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/financial-pattern-discovery.git
cd financial-pattern-discovery
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create default configuration:
```bash
python scripts/run_discovery.py --create-config
```

## 🎯 Quick Start

### Basic Usage

```python
from pathlib import Path
from financial_pattern_discovery import FinancialPatternDiscovery

# Initialize the discovery system
discoverer = FinancialPatternDiscovery("config.ini")

# Process your Excel files
file_paths = [
    Path("servicer_a_example.xlsx"),
    Path("servicer_b_example.xlsx")
]

results = discoverer.process_files(file_paths, Path("patterns_report.xlsx"))
```

### Command Line Usage

```bash
# Process all Excel files in a directory
python scripts/run_discovery.py --dir data/excel_files -o report.xlsx

# Process files in multiple directories
python scripts/run_discovery.py --dir data/servicer_a data/servicer_b -o combined.xlsx

# Process files recursively
python scripts/run_discovery.py --dir data --recursive -o all_patterns.xlsx

# Process files with specific pattern
python scripts/run_discovery.py --dir data/reports --pattern "*2024*.xlsx" -o 2024_report.xlsx

# Mix directory and individual files
python scripts/run_discovery.py --dir data/batch1 extra_file.xlsx -o complete.xlsx

# Use custom configuration
python scripts/run_discovery.py --dir data -c custom_config.ini -o report.xlsx
```

## 📊 Output Report Structure

The system generates a comprehensive Excel report with the following sheets:

1. **Summary**: Key metrics and processing statistics
2. **Cluster Details**: Detailed information about each term cluster
3. **Term Mappings**: Complete mapping of original terms to canonical names
4. **Statistics**: Term frequency analysis and distribution metrics

## ⚙️ Configuration

Edit `config.ini` to customize the system behavior:

```ini
[clustering]
n_clusters = 8              # Number of clusters (auto-optimized)
max_features = 10000        # Maximum TF-IDF features
min_df = 5                  # Minimum document frequency
max_df = 0.5               # Maximum document frequency
ngram_range = (1, 2)       # N-gram range for TF-IDF
use_hierarchical = false   # Use hierarchical clustering
silhouette_threshold = 0.3 # Clustering quality threshold

[processing]
chunk_size = 10000         # Batch processing chunk size
max_workers = 4            # Parallel processing threads
fuzzy_threshold = 80       # Fuzzy matching threshold (0-100)
memory_threshold = 0.8     # Memory usage limit
```

## 📁 Project Structure

```
financial_pattern_discovery/
│
├── config.ini                    # Configuration file
├── requirements.txt              # Python dependencies
├── setup.py                      # Package setup
├── README.md                     # This file
├── QUICKSTART.md                # Quick start guide
│
├── financial_pattern_discovery/  # Main package
│   ├── __init__.py
│   ├── config.py                 # Configuration classes
│   ├── extractor.py              # Excel term extraction
│   ├── clustering.py             # TF-IDF clustering
│   ├── canonical.py              # Canonical name generation
│   ├── fuzzy_matcher.py          # Fuzzy matching
│   ├── report_generator.py       # Excel report generation
│   └── main.py                   # Main orchestrator
│
├── scripts/
│   ├── run_discovery.py          # Full-featured CLI script
│   ├── process_directory.py      # Simple directory processor
│   ├── diagnose_extraction.py    # Diagnostic tool for debugging
│   └── generate_test_data.py     # Test data generator
│
└── examples/
    └── example_usage.py          # Usage examples
```

## 🔧 Advanced Usage

### Custom Configuration

```python
from financial_pattern_discovery import (
    FinancialPatternDiscovery,
    ClusteringConfig,
    ProcessingConfig
)

# Custom clustering configuration
clustering_config = ClusteringConfig(
    n_clusters=12,
    max_features=15000,
    use_hierarchical=True,
    silhouette_threshold=0.4
)

# Custom processing configuration
processing_config = ProcessingConfig(
    max_workers=8,
    fuzzy_threshold=85
)

# Initialize with custom config
discoverer = FinancialPatternDiscovery()
discoverer.clustering_config = clustering_config
discoverer.processing_config = processing_config
```

### Processing by Servicer

```python
# Process files grouped by servicer
servicer_files = {
    'SERVICER_A': list(Path("data/servicer_a").glob("*.xlsx")),
    'SERVICER_B': list(Path("data/servicer_b").glob("*.xlsx"))
}

for servicer, files in servicer_files.items():
    results = discoverer.process_files(
        files,
        Path(f"patterns_{servicer.lower()}.xlsx")
    )
```

## 📈 How It Works

1. **Term Extraction**: Scans Excel files to identify potential financial headers and labels
2. **Text Preprocessing**: Cleans and normalizes extracted terms
3. **TF-IDF Vectorization**: Converts terms to numerical vectors based on term frequency
4. **Clustering**: Groups similar terms using K-means or hierarchical clustering
5. **Canonical Naming**: Generates standardized names for each cluster
6. **Fuzzy Matching**: Maps all terms to canonical names with confidence scores
7. **Report Generation**: Creates comprehensive Excel report with analysis

## 🏆 Benefits

- **No Manual Setup**: Works immediately without templates or training data
- **Scalable**: Processes hundreds of files efficiently
- **Accurate**: Achieves high accuracy through intelligent clustering
- **Flexible**: Easily configurable for different use cases
- **Comprehensive**: Provides detailed analysis and mappings

## 🐛 Troubleshooting

### Common Issues

1. **Memory Error**: Reduce `chunk_size` in config.ini
2. **Poor Clustering**: Adjust `n_clusters` or try `use_hierarchical = true`
3. **Missing Terms**: Lower `min_df` value in configuration
4. **Too Many Clusters**: Increase `silhouette_threshold`

### Few Terms / Clustering Warnings

If you see warnings like "Number of distinct clusters found smaller than n_clusters":

```bash
# Run diagnostic tool
python scripts/diagnose_extraction.py --dir "C:\Your\Excel\Files"
```

This helps identify:
- What terms are being extracted
- Why clustering might be limited
- How to improve results

### Logging

Check `financial_pattern_discovery.log` for detailed processing information.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues or questions, please open an issue on GitHub or contact the development team.