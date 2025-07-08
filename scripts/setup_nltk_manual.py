#!/usr/bin/env python3
"""
Manual NLTK Data Setup Script for Corporate Environments
Download NLTK data manually when pip/firewall blocks automatic downloads
"""

import os
import shutil
from pathlib import Path
import zipfile
import urllib.request
import ssl

def create_nltk_directories():
    """Create the NLTK data directory structure"""
    home = Path.home()
    nltk_data_dir = home / "nltk_data"
    
    directories = [
        nltk_data_dir / "tokenizers",
        nltk_data_dir / "corpora", 
        nltk_data_dir / "taggers",
        nltk_data_dir / "chunkers"
    ]
    
    for dir_path in directories:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Created directory: {dir_path}")
    
    return nltk_data_dir

def download_with_fallback(url, filename):
    """Download file with SSL fallback for corporate environments"""
    try:
        # First try normal download
        urllib.request.urlretrieve(url, filename)
        return True
    except:
        try:
            # Try with unverified SSL context
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            with urllib.request.urlopen(url, context=ssl_context) as response:
                with open(filename, 'wb') as f:
                    shutil.copyfileobj(response, f)
            return True
        except Exception as e:
            print(f"Download failed for {url}: {e}")
            return False

def setup_nltk_data_manually():
    """
    Setup NLTK data manually for corporate environments
    
    Instructions for manual download:
    1. Go to https://github.com/nltk/nltk_data
    2. Download these ZIP files:
       - packages/tokenizers/punkt.zip
       - packages/corpora/stopwords.zip  
       - packages/corpora/wordnet.zip
    3. Place them in your ~/nltk_data/ directory as shown below
    """
    
    print("NLTK Manual Setup for Corporate Environments")
    print("=" * 50)
    
    nltk_data_dir = create_nltk_directories()
    
    # Essential data packages with download URLs
    essential_packages = {
        'punkt': {
            'url': 'https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt.zip',
            'local_dir': nltk_data_dir / "tokenizers",
            'description': 'Tokenization (sentence and word splitting)'
        },
        'stopwords': {
            'url': 'https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/stopwords.zip', 
            'local_dir': nltk_data_dir / "corpora",
            'description': 'Common stopwords in multiple languages'
        },
        'wordnet': {
            'url': 'https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/corpora/wordnet.zip',
            'local_dir': nltk_data_dir / "corpora", 
            'description': 'WordNet lexical database for lemmatization'
        }
    }
    
    print(f"\nNLTK data directory: {nltk_data_dir}")
    print("\nAttempting automatic download (may fail in corporate environments)...")
    
    success_count = 0
    
    for package_name, info in essential_packages.items():
        print(f"\n📦 Processing {package_name} - {info['description']}")
        
        zip_file = info['local_dir'] / f"{package_name}.zip"
        
        # Try automatic download first
        if download_with_fallback(info['url'], zip_file):
            try:
                # Extract the ZIP file
                with zipfile.ZipFile(zip_file, 'r') as zip_ref:
                    zip_ref.extractall(info['local_dir'])
                
                # Remove the ZIP file after extraction
                zip_file.unlink()
                
                print(f"✅ {package_name} installed successfully")
                success_count += 1
                
            except Exception as e:
                print(f"❌ Failed to extract {package_name}: {e}")
        else:
            print(f"⚠️  Automatic download failed for {package_name}")
    
    print(f"\n{'='*50}")
    print(f"Automatic setup complete: {success_count}/{len(essential_packages)} packages installed")
    
    if success_count < len(essential_packages):
        print_manual_instructions(nltk_data_dir, essential_packages)
    
    # Test NLTK functionality
    test_nltk_setup()

def print_manual_instructions(nltk_data_dir, packages):
    """Print manual download instructions"""
    
    print(f"\n🔧 MANUAL DOWNLOAD INSTRUCTIONS")
    print(f"{'='*50}")
    print(f"If automatic download failed, manually download these files:")
    print(f"")
    print(f"1. Visit: https://github.com/nltk/nltk_data/tree/gh-pages/packages")
    print(f"2. Download these ZIP files to your computer:")
    
    for package_name, info in packages.items():
        if package_name == 'punkt':
            print(f"   📁 tokenizers/punkt.zip")
        else:
            print(f"   📁 corpora/{package_name}.zip") 
    
    print(f"\n3. Create this directory structure:")
    print(f"   {nltk_data_dir}/")
    print(f"   ├── tokenizers/")
    print(f"   │   └── punkt/")
    print(f"   └── corpora/")
    print(f"       ├── stopwords/")
    print(f"       └── wordnet/")
    
    print(f"\n4. Extract each ZIP file to its corresponding directory:")
    print(f"   - Extract punkt.zip to {nltk_data_dir}/tokenizers/")
    print(f"   - Extract stopwords.zip to {nltk_data_dir}/corpora/")  
    print(f"   - Extract wordnet.zip to {nltk_data_dir}/corpora/")
    
    print(f"\n5. Final structure should look like:")
    print(f"   {nltk_data_dir}/")
    print(f"   ├── tokenizers/punkt/")
    print(f"   └── corpora/")
    print(f"       ├── stopwords/")
    print(f"       └── wordnet/")

def test_nltk_setup():
    """Test if NLTK is working with the installed data"""
    print(f"\n🧪 Testing NLTK Setup...")
    
    try:
        import nltk
        from nltk.tokenize import word_tokenize
        from nltk.corpus import stopwords
        from nltk.stem import WordNetLemmatizer
        
        # Test tokenization
        test_text = "Class A Interest Distributable Amount"
        tokens = word_tokenize(test_text)
        print(f"✅ Tokenization working: {tokens}")
        
        # Test stopwords
        stop_words = set(stopwords.words('english'))
        print(f"✅ Stopwords loaded: {len(stop_words)} English stopwords")
        
        # Test lemmatization  
        lemmatizer = WordNetLemmatizer()
        lemma = lemmatizer.lemmatize("balances")
        print(f"✅ Lemmatization working: 'balances' → '{lemma}'")
        
        print(f"\n🎉 NLTK setup is working perfectly!")
        return True
        
    except Exception as e:
        print(f"❌ NLTK test failed: {e}")
        print(f"The system will fall back to basic text processing.")
        return False

if __name__ == "__main__":
    setup_nltk_data_manually()