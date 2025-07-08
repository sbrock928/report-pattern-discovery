#!/usr/bin/env python3
"""
NLTK Customization Script for Financial Pattern Discovery
"""

import sys
import json
from pathlib import Path
from typing import Dict, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from financial_pattern_discovery.config import NLTKConfig, ProcessingConfig, FinancialTerms
from financial_pattern_discovery.extractor import EnhancedFinancialTermExtractor, NLTKCustomizer


class NLTKCustomizer:
    """Interactive customization tool for NLTK financial settings"""
    
    def __init__(self):
        self.config_file = Path("nltk_financial_config.json")
        self.current_config = self._load_or_create_config()
    
    def _load_or_create_config(self) -> Dict:
        """Load existing config or create default"""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        else:
            return self._create_default_config()
    
    def _create_default_config(self) -> Dict:
        """Create default configuration"""
        nltk_config = NLTKConfig()
        return {
            "nltk_features": {
                "use_lemmatization": nltk_config.use_lemmatization,
                "use_pos_tagging": nltk_config.use_pos_tagging,
                "use_named_entity_recognition": nltk_config.use_named_entity_recognition,
                "financial_relevance_threshold": nltk_config.financial_relevance_threshold,
                "preserve_financial_plurals": nltk_config.preserve_financial_plurals
            },
            "financial_terms_to_preserve": list(nltk_config.financial_terms_to_preserve),
            "financial_stopwords_to_remove": list(nltk_config.financial_stopwords_to_remove),
            "custom_lemma_exceptions": nltk_config.custom_lemma_exceptions,
            "pos_tag_weights": nltk_config.important_pos_tags,
            "entity_patterns": nltk_config.financial_entity_patterns
        }
    
    def save_config(self):
        """Save current configuration to file"""
        with open(self.config_file, 'w') as f:
            json.dump(self.current_config, f, indent=2)
        print(f"✅ Configuration saved to {self.config_file}")
    
    def show_current_settings(self):
        """Display current NLTK settings"""
        print("\n🔧 Current NLTK Financial Settings")
        print("=" * 50)
        
        features = self.current_config["nltk_features"]
        print(f"Lemmatization: {'✅ Enabled' if features['use_lemmatization'] else '❌ Disabled'}")
        print(f"POS Tagging: {'✅ Enabled' if features['use_pos_tagging'] else '❌ Disabled'}")
        print(f"Named Entity Recognition: {'✅ Enabled' if features['use_named_entity_recognition'] else '❌ Disabled'}")
        print(f"Financial Relevance Threshold: {features['financial_relevance_threshold']}")
        print(f"Preserve Financial Plurals: {'✅ Yes' if features['preserve_financial_plurals'] else '❌ No'}")
        
        print(f"\n📋 Financial Terms to Preserve: {len(self.current_config['financial_terms_to_preserve'])} terms")
        print(f"🚫 Stopwords to Remove: {len(self.current_config['financial_stopwords_to_remove'])} terms")
        print(f"🔄 Custom Lemma Exceptions: {len(self.current_config['custom_lemma_exceptions'])} mappings")
        print(f"🏷️  POS Tag Weights: {len(self.current_config['pos_tag_weights'])} tags configured")
        print(f"🎯 Entity Patterns: {len(self.current_config['entity_patterns'])} patterns")
    
    def add_financial_terms(self, terms: List[str]):
        """Add terms that should always be preserved"""
        existing = set(self.current_config["financial_terms_to_preserve"])
        new_terms = [term.lower().strip() for term in terms if term.lower().strip() not in existing]
        
        if new_terms:
            self.current_config["financial_terms_to_preserve"].extend(new_terms)
            print(f"✅ Added {len(new_terms)} new financial terms: {new_terms}")
        else:
            print("ℹ️  All terms already in preserved list")
    
    def add_stopwords(self, words: List[str]):
        """Add words that should be filtered out as noise"""
        existing = set(self.current_config["financial_stopwords_to_remove"])
        new_words = [word.lower().strip() for word in words if word.lower().strip() not in existing]
        
        if new_words:
            self.current_config["financial_stopwords_to_remove"].extend(new_words)
            print(f"✅ Added {len(new_words)} new stopwords: {new_words}")
        else:
            print("ℹ️  All words already in stopword list")
    
    def add_lemma_exceptions(self, mappings: Dict[str, str]):
        """Add custom lemmatization mappings"""
        existing = self.current_config["custom_lemma_exceptions"]
        new_mappings = {k.lower(): v.lower() for k, v in mappings.items() if k.lower() not in existing}
        
        if new_mappings:
            existing.update(new_mappings)
            print(f"✅ Added {len(new_mappings)} new lemma mappings: {new_mappings}")
        else:
            print("ℹ️  All mappings already exist")
    
    def add_entity_patterns(self, patterns: List[str]):
        """Add regex patterns for financial entity recognition"""
        existing = set(self.current_config["entity_patterns"])
        new_patterns = [pattern for pattern in patterns if pattern not in existing]
        
        if new_patterns:
            self.current_config["entity_patterns"].extend(new_patterns)
            print(f"✅ Added {len(new_patterns)} new entity patterns")
        else:
            print("ℹ️  All patterns already exist")
    
    def tune_relevance_threshold(self, threshold: float):
        """Adjust the financial relevance detection threshold"""
        if 0.0 <= threshold <= 1.0:
            old_threshold = self.current_config["nltk_features"]["financial_relevance_threshold"]
            self.current_config["nltk_features"]["financial_relevance_threshold"] = threshold
            print(f"✅ Financial relevance threshold changed: {old_threshold} → {threshold}")
            if threshold < 0.2:
                print("⚠️  Low threshold may include more noise")
            elif threshold > 0.5:
                print("⚠️  High threshold may miss relevant terms")
        else:
            print("❌ Threshold must be between 0.0 and 1.0")
    
    def optimize_for_document_type(self, doc_type: str):
        """Optimize settings for specific document types"""
        optimizations = {
            "asset_backed_securities": {
                "preserve_terms": ["tranche", "tranches", "waterfall", "overcollateralization", 
                                 "enhancement", "trigger", "subordination", "senior", "subordinate"],
                "entity_patterns": [
                    r'\b[Cc]lass\s+[A-F]\s+[Nn]otes?\b',
                    r'\b[Ss]enior\s+[Nn]otes?\b',
                    r'\b[Ss]ubordinate\s+[Nn]otes?\b'
                ],
                "stopwords": ["security", "securities", "notes", "note"]
            },
            "servicing_reports": {
                "preserve_terms": ["servicer", "servicing", "collection", "distribution", 
                                 "advances", "fees", "compensations"],
                "entity_patterns": [
                    r'\b[Ss]ervicer\s+[Ff]ee\b',
                    r'\b[Cc]ollection\s+[Pp]eriod\b',
                    r'\b[Dd]istribution\s+[Dd]ate\b'
                ],
                "stopwords": ["report", "statement", "monthly", "quarterly"]
            },
            "trustee_reports": {
                "preserve_terms": ["trustee", "indenture", "owner", "backup", 
                                 "administration", "fees"],
                "entity_patterns": [
                    r'\b[Tt]rustee\s+[Ff]ee\b',
                    r'\b[Ii]ndenture\s+[Tt]rustee\b',
                    r'\b[Oo]wner\s+[Tt]rustee\b'
                ],
                "stopwords": ["trustee", "report", "administration"]
            }
        }
        
        if doc_type in optimizations:
            opt = optimizations[doc_type]
            self.add_financial_terms(opt["preserve_terms"])
            self.add_entity_patterns(opt["entity_patterns"])
            self.add_stopwords(opt["stopwords"])
            print(f"✅ Optimized settings for {doc_type.replace('_', ' ').title()}")
        else:
            available = list(optimizations.keys())
            print(f"❌ Unknown document type. Available: {available}")
    
    def generate_config_object(self) -> NLTKConfig:
        """Generate NLTKConfig object from current settings"""
        config = NLTKConfig()
        
        # Update features
        features = self.current_config["nltk_features"]
        config.use_lemmatization = features["use_lemmatization"]
        config.use_pos_tagging = features["use_pos_tagging"]
        config.use_named_entity_recognition = features["use_named_entity_recognition"]
        config.financial_relevance_threshold = features["financial_relevance_threshold"]
        config.preserve_financial_plurals = features["preserve_financial_plurals"]
        
        # Update term sets
        config.financial_terms_to_preserve = set(self.current_config["financial_terms_to_preserve"])
        config.financial_stopwords_to_remove = set(self.current_config["financial_stopwords_to_remove"])
        config.custom_lemma_exceptions = self.current_config["custom_lemma_exceptions"]
        config.important_pos_tags = self.current_config["pos_tag_weights"]
        config.financial_entity_patterns = self.current_config["entity_patterns"]
        
        return config


def interactive_customization():
    """Interactive customization session"""
    print("🎯 NLTK Financial Customization Tool")
    print("=" * 50)
    
    customizer = NLTKCustomizer()
    customizer.show_current_settings()
    
    while True:
        print(f"\n📋 Available Actions:")
        print("1. Add financial terms to preserve")
        print("2. Add stopwords to remove")  
        print("3. Add custom lemmatization rules")
        print("4. Add entity recognition patterns")
        print("5. Tune relevance threshold")
        print("6. Optimize for document type")
        print("7. Show current settings")
        print("8. Save and exit")
        print("9. Exit without saving")
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == "1":
            terms = input("Enter financial terms (comma-separated): ").split(",")
            customizer.add_financial_terms([t.strip() for t in terms if t.strip()])
            
        elif choice == "2":
            words = input("Enter stopwords to remove (comma-separated): ").split(",")
            customizer.add_stopwords([w.strip() for w in words if w.strip()])
            
        elif choice == "3":
            print("Enter lemma mappings (format: 'word1:lemma1,word2:lemma2'):")
            mappings_str = input()
            try:
                mappings = {}
                for pair in mappings_str.split(","):
                    if ":" in pair:
                        word, lemma = pair.split(":", 1)
                        mappings[word.strip()] = lemma.strip()
                customizer.add_lemma_exceptions(mappings)
            except Exception as e:
                print(f"❌ Invalid format: {e}")
                
        elif choice == "4":
            patterns = input("Enter regex patterns (comma-separated): ").split(",")
            customizer.add_entity_patterns([p.strip() for p in patterns if p.strip()])
            
        elif choice == "5":
            try:
                threshold = float(input("Enter relevance threshold (0.0-1.0): "))
                customizer.tune_relevance_threshold(threshold)
            except ValueError:
                print("❌ Invalid number")
                
        elif choice == "6":
            doc_type = input("Enter document type (asset_backed_securities/servicing_reports/trustee_reports): ")
            customizer.optimize_for_document_type(doc_type.lower())
            
        elif choice == "7":
            customizer.show_current_settings()
            
        elif choice == "8":
            customizer.save_config()
            print("✅ Configuration saved! Use load_custom_config() in your scripts.")
            break
            
        elif choice == "9":
            print("👋 Exiting without saving")
            break
            
        else:
            print("❌ Invalid choice")


def load_custom_config() -> NLTKConfig:
    """Load saved custom configuration"""
    customizer = NLTKCustomizer()
    if customizer.config_file.exists():
        return customizer.generate_config_object()
    else:
        print("⚠️  No custom config found, using defaults")
        return NLTKConfig()


def quick_optimization_examples():
    """Show examples of quick optimizations"""
    print("\n🚀 Quick Optimization Examples")
    print("=" * 50)
    
    examples = {
        "Asset-Backed Securities": [
            "customizer.add_financial_terms(['waterfall', 'overcollateralization', 'enhancement'])",
            "customizer.add_entity_patterns([r'\\b[Cc]lass\\s+[A-F]\\s+[Nn]otes?\\b'])",
            "customizer.tune_relevance_threshold(0.35)"
        ],
        "Servicing Reports": [
            "customizer.add_financial_terms(['servicer', 'advances', 'collections'])", 
            "customizer.add_stopwords(['monthly', 'report', 'statement'])",
            "customizer.tune_relevance_threshold(0.25)"
        ],
        "Trustee Reports": [
            "customizer.add_financial_terms(['indenture', 'backup', 'administration'])",
            "customizer.add_lemma_exceptions({'trustees': 'trustee', 'administrations': 'administration'})",
            "customizer.tune_relevance_threshold(0.30)"
        ]
    }
    
    for doc_type, code_examples in examples.items():
        print(f"\n📄 {doc_type}:")
        for example in code_examples:
            print(f"  • {example}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--examples":
        quick_optimization_examples()
    else:
        interactive_customization()