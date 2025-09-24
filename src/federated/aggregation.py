"""
Federated Result Aggregation and Ranking
Aggregates and ranks results from multiple federated nodes.
"""

from typing import Dict, List, Optional, Any
import hashlib
import numpy as np
from datetime import datetime, timedelta
from collections import defaultdict
import json

class FederatedResultAggregator:
    """Aggregates results from multiple federated nodes"""
    
    def __init__(self):
        self.ranking_strategies = {
            'score_fusion': self.score_fusion_ranking,
            'round_robin': self.round_robin_ranking,
            'quality_weighted': self.quality_weighted_ranking,
            'diversity_aware': self.diversity_aware_ranking
        }
        self.duplicate_detector = DuplicateDetector()
        self.quality_assessor = QualityAssessor()
    
    async def aggregate_federated_results(self, node_results: Dict, query_analysis) -> Dict:
        """Aggregate results from multiple federated nodes"""
        
        # Extract all documents from node results
        all_documents = []
        node_metadata = {}
        
        for node_id, result in node_results.items():
            if result['success']:
                documents = result['results'].get('documents', [])
                for doc in documents:
                    doc['federated_metadata'] = {
                        'source_node': node_id,
                        'node_confidence': result.get('confidence', 0.5),
                        'retrieval_latency': result['latency'],
                        'timestamp': datetime.now().isoformat()
                    }
                all_documents.extend(documents)
                node_metadata[node_id] = {
                    'result_count': len(documents),
                    'latency': result['latency'],
                    'success': True,
                    'confidence': result.get('confidence', 0.5)
                }
            else:
                node_metadata[node_id] = {
                    'result_count': 0,
                    'latency': result.get('latency', 0),
                    'success': False,
                    'error': result.get('error', 'Unknown error')
                }
        
        # Apply deduplication
        deduplicated_docs = self.deduplicate_documents(all_documents)
        
        # Rank documents using selected strategy
        ranking_strategy = getattr(query_analysis, 'ranking_strategy', 'quality_weighted')
        ranked_documents = await self.ranking_strategies[ranking_strategy](
            deduplicated_docs, node_metadata, query_analysis
        )
        
        return {
            'documents': ranked_documents,
            'total_results': len(ranked_documents),
            'nodes_contributing': len([n for n in node_metadata.values() if n['success']]),
            'node_breakdown': node_metadata,
            'aggregation_metadata': {
                'strategy_used': ranking_strategy,
                'duplicates_removed': len(all_documents) - len(deduplicated_docs),
                'aggregation_timestamp': datetime.now().isoformat()
            }
        }
    
    async def quality_weighted_ranking(self, documents: List[Dict], node_metadata: Dict, query_analysis) -> List[Dict]:
        """Rank documents weighted by node quality and performance"""
        
        scored_documents = []
        
        for doc in documents:
            node_id = doc['federated_metadata']['source_node']
            node_info = node_metadata.get(node_id, {})
            
            # Calculate base score from document relevance
            base_score = doc.get('score', 0.5)
            
            # Calculate node quality factor
            node_quality = self.calculate_node_quality(node_id, node_info)
            
            # Calculate freshness factor (if available)
            freshness_factor = self.calculate_freshness_factor(doc)
            
            # Calculate domain relevance factor
            domain_relevance = self.calculate_domain_relevance(doc, query_analysis)
            
            # Calculate content quality factor
            content_quality = self.quality_assessor.assess_content_quality(doc)
            
            # Combined score with weights
            combined_score = (
                base_score * 0.3 +
                node_quality * 0.25 +
                freshness_factor * 0.15 +
                domain_relevance * 0.15 +
                content_quality * 0.15
            )
            
            doc['federated_score'] = combined_score
            doc['score_breakdown'] = {
                'base_score': base_score,
                'node_quality': node_quality,
                'freshness': freshness_factor,
                'domain_relevance': domain_relevance,
                'content_quality': content_quality
            }
            
            scored_documents.append(doc)
        
        # Sort by combined score
        return sorted(scored_documents, key=lambda x: x['federated_score'], reverse=True)
    
    async def diversity_aware_ranking(self, documents: List[Dict], node_metadata: Dict, query_analysis) -> List[Dict]:
        """Rank documents with diversity awareness to avoid redundancy"""
        
        # First, get quality-weighted ranking
        quality_ranked = await self.quality_weighted_ranking(documents, node_metadata, query_analysis)
        
        # Apply diversity filtering
        diverse_documents = []
        seen_content_hashes = set()
        
        for doc in quality_ranked:
            content_hash = self.create_content_hash(doc['content'])
            
            if content_hash not in seen_content_hashes:
                seen_content_hashes.add(content_hash)
                diverse_documents.append(doc)
            
            # Limit to top diverse results
            if len(diverse_documents) >= 20:
                break
        
        return diverse_documents
    
    async def score_fusion_ranking(self, documents: List[Dict], node_metadata: Dict, query_analysis) -> List[Dict]:
        """Rank documents using score fusion from multiple nodes"""
        
        # Group documents by content similarity
        document_groups = self.group_similar_documents(documents)
        
        fused_documents = []
        
        for group in document_groups:
            if len(group) == 1:
                # Single document, use original score
                fused_doc = group[0].copy()
                fused_doc['federated_score'] = group[0].get('score', 0.5)
            else:
                # Multiple similar documents, fuse scores
                fused_doc = self.fuse_similar_documents(group)
            
            fused_documents.append(fused_doc)
        
        # Sort by fused score
        return sorted(fused_documents, key=lambda x: x['federated_score'], reverse=True)
    
    async def round_robin_ranking(self, documents: List[Dict], node_metadata: Dict, query_analysis) -> List[Dict]:
        """Rank documents using round-robin from different nodes"""
        
        # Group documents by source node
        node_documents = defaultdict(list)
        for doc in documents:
            node_id = doc['federated_metadata']['source_node']
            node_documents[node_id].append(doc)
        
        # Round-robin selection
        ranked_documents = []
        max_per_node = max(1, len(documents) // len(node_documents))
        
        for i in range(max_per_node):
            for node_id, docs in node_documents.items():
                if i < len(docs):
                    ranked_documents.append(docs[i])
        
        return ranked_documents
    
    def calculate_node_quality(self, node_id: str, node_info: Dict) -> float:
        """Calculate quality score for a node"""
        base_quality = 0.5
        
        # Adjust based on latency (lower latency = higher quality)
        latency = node_info.get('latency', 10.0)
        latency_factor = max(0, 1.0 - (latency / 30.0))  # Normalize to 0-1
        
        # Adjust based on confidence
        confidence = node_info.get('confidence', 0.5)
        
        # Adjust based on result count (more results = higher quality)
        result_count = node_info.get('result_count', 0)
        result_factor = min(1.0, result_count / 10.0)
        
        return (base_quality + latency_factor + confidence + result_factor) / 4
    
    def calculate_freshness_factor(self, doc: Dict) -> float:
        """Calculate freshness factor for document"""
        # Check if document has timestamp
        if 'timestamp' in doc.get('metadata', {}):
            try:
                doc_time = datetime.fromisoformat(doc['metadata']['timestamp'])
                age_days = (datetime.now() - doc_time).days
                # Freshness decreases with age
                return max(0, 1.0 - (age_days / 365.0))  # 1 year = 0 freshness
            except:
                pass
        
        # Default freshness for documents without timestamp
        return 0.5
    
    def calculate_domain_relevance(self, doc: Dict, query_analysis) -> float:
        """Calculate domain relevance factor"""
        doc_domain = doc.get('metadata', {}).get('domain', 'general')
        query_domain = getattr(query_analysis, 'domain', 'general')
        
        if doc_domain == query_domain:
            return 1.0
        elif doc_domain == 'general' or query_domain == 'general':
            return 0.7
        else:
            return 0.3
    
    def deduplicate_documents(self, documents: List[Dict]) -> List[Dict]:
        """Remove duplicate documents across federated nodes"""
        seen_hashes = set()
        unique_documents = []
        
        for doc in documents:
            content_hash = self.create_document_hash(doc)
            
            if content_hash not in seen_hashes:
                seen_hashes.add(content_hash)
                unique_documents.append(doc)
            else:
                # If duplicate, keep the one with higher score or better metadata
                existing_doc = next(d for d in unique_documents if self.create_document_hash(d) == content_hash)
                if doc.get('score', 0) > existing_doc.get('score', 0):
                    unique_documents.remove(existing_doc)
                    unique_documents.append(doc)
        
        return unique_documents
    
    def create_document_hash(self, doc: Dict) -> str:
        """Create hash for document deduplication"""
        content = doc.get('content', '') + str(doc.get('metadata', {}))
        return hashlib.md5(content.encode()).hexdigest()
    
    def create_content_hash(self, content: str) -> str:
        """Create hash for content similarity"""
        # Normalize content for similarity comparison
        normalized = content.lower().strip()
        return hashlib.md5(normalized.encode()).hexdigest()
    
    def group_similar_documents(self, documents: List[Dict]) -> List[List[Dict]]:
        """Group documents by content similarity"""
        groups = []
        processed_hashes = set()
        
        for doc in documents:
            content_hash = self.create_content_hash(doc['content'])
            
            if content_hash not in processed_hashes:
                # Find similar documents
                similar_docs = [doc]
                for other_doc in documents:
                    if other_doc != doc:
                        other_hash = self.create_content_hash(other_doc['content'])
                        if content_hash == other_hash:
                            similar_docs.append(other_doc)
                
                groups.append(similar_docs)
                processed_hashes.add(content_hash)
        
        return groups
    
    def fuse_similar_documents(self, similar_docs: List[Dict]) -> Dict:
        """Fuse similar documents from different nodes"""
        if not similar_docs:
            return {}
        
        # Use the document with highest score as base
        base_doc = max(similar_docs, key=lambda x: x.get('score', 0))
        fused_doc = base_doc.copy()
        
        # Calculate fused score (average of all similar documents)
        total_score = sum(doc.get('score', 0) for doc in similar_docs)
        fused_score = total_score / len(similar_docs)
        
        # Add boost for multiple sources
        source_boost = min(0.2, len(similar_docs) * 0.05)
        fused_doc['federated_score'] = fused_score + source_boost
        
        # Update metadata to show multiple sources
        fused_doc['federated_metadata']['source_nodes'] = [
            doc['federated_metadata']['source_node'] for doc in similar_docs
        ]
        fused_doc['federated_metadata']['source_count'] = len(similar_docs)
        
        return fused_doc

class DuplicateDetector:
    """Advanced duplicate detection for federated results"""
    
    def __init__(self):
        self.similarity_threshold = 0.8
    
    def find_duplicates(self, documents: List[Dict]) -> List[List[Dict]]:
        """Find duplicate documents using content similarity"""
        duplicate_groups = []
        processed = set()
        
        for i, doc1 in enumerate(documents):
            if i in processed:
                continue
            
            duplicates = [doc1]
            for j, doc2 in enumerate(documents[i+1:], i+1):
                if j in processed:
                    continue
                
                if self.calculate_similarity(doc1, doc2) > self.similarity_threshold:
                    duplicates.append(doc2)
                    processed.add(j)
            
            if len(duplicates) > 1:
                duplicate_groups.append(duplicates)
                processed.add(i)
        
        return duplicate_groups
    
    def calculate_similarity(self, doc1: Dict, doc2: Dict) -> float:
        """Calculate similarity between two documents"""
        content1 = doc1.get('content', '').lower()
        content2 = doc2.get('content', '').lower()
        
        # Simple Jaccard similarity
        words1 = set(content1.split())
        words2 = set(content2.split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0.0

class QualityAssessor:
    """Assess content quality for ranking"""
    
    def __init__(self):
        self.quality_indicators = {
            'length': self.assess_length,
            'structure': self.assess_structure,
            'completeness': self.assess_completeness,
            'readability': self.assess_readability
        }
    
    def assess_content_quality(self, doc: Dict) -> float:
        """Assess overall content quality"""
        content = doc.get('content', '')
        if not content:
            return 0.0
        
        quality_scores = []
        for indicator, assessor in self.quality_indicators.items():
            score = assessor(content)
            quality_scores.append(score)
        
        return np.mean(quality_scores)
    
    def assess_length(self, content: str) -> float:
        """Assess content length quality"""
        word_count = len(content.split())
        
        # Optimal length range: 50-500 words
        if 50 <= word_count <= 500:
            return 1.0
        elif word_count < 50:
            return word_count / 50.0
        else:
            return max(0.5, 500.0 / word_count)
    
    def assess_structure(self, content: str) -> float:
        """Assess content structure quality"""
        # Check for proper sentence structure
        sentences = content.split('.')
        if len(sentences) < 2:
            return 0.3
        
        # Check for paragraph structure
        paragraphs = content.split('\n\n')
        if len(paragraphs) > 1:
            return 1.0
        
        return 0.7
    
    def assess_completeness(self, content: str) -> float:
        """Assess content completeness"""
        # Simple completeness check
        if len(content.strip()) < 20:
            return 0.2
        
        # Check for common completeness indicators
        completeness_indicators = ['because', 'therefore', 'however', 'additionally']
        indicator_count = sum(1 for indicator in completeness_indicators if indicator in content.lower())
        
        return min(1.0, indicator_count * 0.3 + 0.4)
    
    def assess_readability(self, content: str) -> float:
        """Assess content readability"""
        # Simple readability assessment
        sentences = content.split('.')
        if not sentences:
            return 0.0
        
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Optimal sentence length: 10-20 words
        if 10 <= avg_sentence_length <= 20:
            return 1.0
        elif avg_sentence_length < 10:
            return avg_sentence_length / 10.0
        else:
            return max(0.3, 20.0 / avg_sentence_length)
