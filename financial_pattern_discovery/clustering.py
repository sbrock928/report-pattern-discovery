"""
TF-IDF clustering module for Financial Pattern Discovery System
"""

import numpy as np
import logging
from typing import Dict, List, Any
import re

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score
from scipy.cluster.hierarchy import linkage, fcluster

from .config import ClusteringConfig


class FinancialTermClustering:
    """Cluster financial terms using TF-IDF and various clustering algorithms"""
    
    def __init__(self, config: ClusteringConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.vectorizer = None
        self.cluster_model = None
        self.tfidf_matrix = None
        
    def cluster_terms(self, terms: List[str]) -> Dict[str, Any]:
        """Cluster financial terms with class-aware separation"""
        
        if len(terms) < 2:
            return {"clusters": {}, "metrics": {}, "vectorizer": None}
        
        # Remove exact duplicates while preserving order
        seen = set()
        unique_terms = []
        for term in terms:
            if term not in seen:
                seen.add(term)
                unique_terms.append(term)
        
        self.logger.info(f"Clustering {len(unique_terms)} unique terms from {len(terms)} total terms")
        
        # If we have very few unique terms, create simple clusters
        if len(unique_terms) <= 3:
            clusters = {}
            for i, term in enumerate(unique_terms):
                clusters[i] = {
                    'terms': [term],
                    'count': 1,
                    'top_features': [term],
                    'mean_tfidf_scores': [1.0]
                }
            return {
                "clusters": clusters,
                "metrics": {'n_clusters': len(clusters), 'n_terms': len(unique_terms)},
                "vectorizer": None,
                "optimal_k": len(clusters)
            }
        
        # Pre-separate terms by class and general terms
        class_terms, general_terms = self._separate_terms_by_class(unique_terms)
        
        # Create clusters using class-aware approach
        clusters = self._class_aware_clustering(class_terms, general_terms)
        
        # Calculate metrics based on all terms
        total_clusters = len(clusters)
        metrics = {
            'n_clusters': total_clusters,
            'n_terms': len(unique_terms),
            'class_clusters': sum(1 for c in clusters.values() if self._has_class_terms(c['terms'])),
            'general_clusters': sum(1 for c in clusters.values() if not self._has_class_terms(c['terms']))
        }
        
        return {
            "clusters": clusters,
            "metrics": metrics,
            "vectorizer": self.vectorizer,
            "optimal_k": total_clusters
        }
    
    def _separate_terms_by_class(self, terms: List[str]) -> tuple:
        """Separate terms into class-specific and general terms"""
        class_terms = {}  # {class_letter: [terms]}
        general_terms = []
        
        class_pattern = re.compile(r'\bclass\s+([a-f])\b', re.IGNORECASE)
        
        for term in terms:
            match = class_pattern.search(term)
            if match:
                class_letter = match.group(1).lower()
                if class_letter not in class_terms:
                    class_terms[class_letter] = []
                class_terms[class_letter].append(term)
            else:
                general_terms.append(term)
        
        self.logger.info(f"Separated terms: {len(general_terms)} general, "
                        f"{sum(len(terms) for terms in class_terms.values())} class-specific "
                        f"across {len(class_terms)} classes")
        
        return class_terms, general_terms
    
    def _class_aware_clustering(self, class_terms: Dict[str, List[str]], general_terms: List[str]) -> Dict[int, Dict[str, Any]]:
        """Perform clustering that respects class boundaries"""
        clusters = {}
        cluster_id = 0
        
        # Process each class separately
        for class_letter, terms in class_terms.items():
            if len(terms) == 1:
                # Single term gets its own cluster
                clusters[cluster_id] = {
                    'terms': terms,
                    'count': 1,
                    'top_features': [terms[0]],
                    'mean_tfidf_scores': [1.0],
                    'class': class_letter
                }
                cluster_id += 1
            else:
                # Cluster terms within this class
                class_clusters = self._cluster_similar_terms(terms, f"class_{class_letter}")
                for cluster_data in class_clusters:
                    cluster_data['class'] = class_letter
                    clusters[cluster_id] = cluster_data
                    cluster_id += 1
        
        # Process general terms
        if general_terms:
            general_clusters = self._cluster_similar_terms(general_terms, "general")
            for cluster_data in general_clusters:
                cluster_data['class'] = None  # No specific class
                clusters[cluster_id] = cluster_data
                cluster_id += 1
        
        return clusters
    
    def _cluster_similar_terms(self, terms: List[str], group_name: str) -> List[Dict[str, Any]]:
        """Cluster similar terms within a group (class or general)"""
        if len(terms) <= 2:
            # Very few terms - each gets its own cluster
            return [{
                'terms': [term],
                'count': 1,
                'top_features': [term],
                'mean_tfidf_scores': [1.0]
            } for term in terms]
        
        try:
            # Create TF-IDF vectorizer for this group
            vectorizer = TfidfVectorizer(
                max_features=min(self.config.max_features, len(terms) * 10),
                min_df=1,  # Allow rare terms within class
                max_df=0.95,
                ngram_range=self.config.ngram_range,
                stop_words='english'
            )
            
            tfidf_matrix = vectorizer.fit_transform(terms)
            
            # Determine number of clusters for this group
            # More aggressive clustering for class terms to separate different amount types
            if group_name.startswith("class_"):
                # Create more clusters to separate distributable vs shortfall vs other types
                n_clusters = min(len(terms), max(2, len(terms) // 2))  # Back to more aggressive clustering
            else:
                n_clusters = min(len(terms), max(2, len(terms) // 3))
            
            # Perform K-means clustering
            kmeans = KMeans(
                n_clusters=n_clusters,
                random_state=self.config.random_state,
                n_init=10,
                max_iter=300
            )
            
            cluster_labels = kmeans.fit_predict(tfidf_matrix)
            
            # Organize results
            feature_names = vectorizer.get_feature_names_out()
            clusters = []
            
            for cluster_id in set(cluster_labels):
                cluster_terms = [terms[i] for i, label in enumerate(cluster_labels) if label == cluster_id]
                
                # Get top features for this cluster
                cluster_indices = [i for i, label in enumerate(cluster_labels) if label == cluster_id]
                cluster_tfidf = tfidf_matrix[cluster_indices]
                
                # Calculate mean TF-IDF scores for cluster
                mean_scores = np.mean(cluster_tfidf, axis=0).A1
                top_features_idx = np.argsort(mean_scores)[-10:][::-1]
                top_features = [feature_names[i] for i in top_features_idx if mean_scores[i] > 0]
                
                clusters.append({
                    'terms': cluster_terms,
                    'count': len(cluster_terms),
                    'top_features': top_features,
                    'mean_tfidf_scores': mean_scores[top_features_idx]
                })
            
            return clusters
            
        except Exception as e:
            self.logger.warning(f"Failed to cluster {group_name} terms: {e}")
            # Fallback: each term gets its own cluster
            return [{
                'terms': [term],
                'count': 1,
                'top_features': [term],
                'mean_tfidf_scores': [1.0]
            } for term in terms]
    
    def _has_class_terms(self, terms: List[str]) -> bool:
        """Check if any term in the list contains class identifiers"""
        class_pattern = re.compile(r'\bclass\s+[a-f]\b', re.IGNORECASE)
        return any(class_pattern.search(term) for term in terms)

    def _calculate_metrics(self, cluster_labels: np.ndarray) -> Dict[str, float]:
        """Calculate clustering quality metrics"""
        metrics = {}
        
        try:
            metrics['silhouette_score'] = silhouette_score(self.tfidf_matrix, cluster_labels)
        except:
            metrics['silhouette_score'] = 0.0
            
        try:
            metrics['calinski_harabasz_score'] = calinski_harabasz_score(self.tfidf_matrix.toarray(), cluster_labels)
        except:
            metrics['calinski_harabasz_score'] = 0.0
            
        metrics['n_clusters'] = len(set(cluster_labels))
        metrics['n_terms'] = len(cluster_labels)
        
        return metrics