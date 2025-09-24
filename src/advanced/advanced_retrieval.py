"""
Advanced Retrieval Strategies
Multi-vector retrieval, graph-based retrieval, and hybrid approaches
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import networkx as nx
from dataclasses import dataclass
import logging
from collections import defaultdict
import json

logger = logging.getLogger(__name__)

@dataclass
class RetrievalResult:
    document_id: str
    content: str
    score: float
    source: str
    metadata: Dict[str, Any]

class MultiVectorRetriever:
    def __init__(self, vector_store, text_splitter, embedding_generator):
        """
        Multi-vector retriever that creates multiple representations of documents
        
        Args:
            vector_store: Vector database for storing embeddings
            text_splitter: Text splitter for chunking documents
            embedding_generator: Embedding generator for creating vectors
        """
        self.vector_store = vector_store
        self.text_splitter = text_splitter
        self.embedding_generator = embedding_generator
        self.representation_types = ['chunk', 'summary', 'keywords', 'entities']
    
    def create_document_representations(self, document: str, doc_id: str) -> List[Dict[str, Any]]:
        """Create multiple representations of a document"""
        representations = []
        
        # 1. Original chunks
        chunks = self.text_splitter.split_text(document)
        for i, chunk in enumerate(chunks):
            representations.append({
                'type': 'chunk',
                'content': chunk,
                'doc_id': doc_id,
                'chunk_id': f"{doc_id}_chunk_{i}",
                'embedding_type': 'text'
            })
        
        # 2. Summary
        summary = self.generate_summary(document)
        representations.append({
            'type': 'summary',
            'content': summary,
            'doc_id': doc_id,
            'chunk_id': f"{doc_id}_summary",
            'embedding_type': 'text'
        })
        
        # 3. Keywords
        keywords = self.extract_keywords(document)
        representations.append({
            'type': 'keywords',
            'content': ' '.join(keywords),
            'doc_id': doc_id,
            'chunk_id': f"{doc_id}_keywords",
            'embedding_type': 'text'
        })
        
        # 4. Entities (if available)
        entities = self.extract_entities(document)
        if entities:
            representations.append({
                'type': 'entities',
                'content': ' '.join(entities),
                'doc_id': doc_id,
                'chunk_id': f"{doc_id}_entities",
                'embedding_type': 'text'
            })
        
        return representations
    
    def generate_summary(self, document: str, max_length: int = 200) -> str:
        """Generate a summary of the document"""
        # Simple extractive summarization
        sentences = document.split('.')
        if len(sentences) <= 3:
            return document
        
        # Take first few sentences as summary
        summary_sentences = sentences[:3]
        return '. '.join(summary_sentences) + '.'
    
    def extract_keywords(self, document: str, top_k: int = 10) -> List[str]:
        """Extract keywords from the document"""
        # Simple keyword extraction (in production, use proper NLP)
        words = document.lower().split()
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Count word frequency
        word_freq = defaultdict(int)
        for word in filtered_words:
            word_freq[word] += 1
        
        # Return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_k]]
    
    def extract_entities(self, document: str) -> List[str]:
        """Extract named entities from the document"""
        # Simplified entity extraction
        # In production, use spaCy or similar
        entities = []
        
        # Look for capitalized words (potential proper nouns)
        words = document.split()
        for word in words:
            if word[0].isupper() and len(word) > 2:
                entities.append(word)
        
        return list(set(entities))[:5]  # Remove duplicates and limit
    
    def hybrid_retrieval(self, query: str, weights: Optional[Dict[str, float]] = None, 
                        k: int = 10) -> List[RetrievalResult]:
        """Retrieve using multiple strategies and fuse results"""
        if weights is None:
            weights = {'chunk': 0.6, 'summary': 0.3, 'keywords': 0.1, 'entities': 0.1}
        
        results = {}
        
        # Retrieve from each representation type
        for rep_type, weight in weights.items():
            try:
                type_results = self.vector_store.search(
                    query, 
                    filter={'type': rep_type},
                    k=k * 2  # Get more results for better fusion
                )
                results[rep_type] = {
                    'documents': type_results,
                    'weight': weight
                }
            except Exception as e:
                logger.warning(f"Error retrieving {rep_type} results: {e}")
                results[rep_type] = {'documents': [], 'weight': weight}
        
        # Fuse results
        fused_results = self.fuse_results(results, k)
        return fused_results
    
    def fuse_results(self, results: Dict[str, Dict], k: int) -> List[RetrievalResult]:
        """Fuse results from different representations using reciprocal rank fusion"""
        scored_docs = {}
        
        for rep_type, result in results.items():
            weight = result['weight']
            documents = result['documents']
            
            for i, doc in enumerate(documents):
                doc_id = doc.get('id', doc.get('doc_id', 'unknown'))
                score = weight * (1 / (i + 1))  # Reciprocal rank fusion
                
                if doc_id in scored_docs:
                    scored_docs[doc_id]['score'] += score
                    scored_docs[doc_id]['sources'].append(rep_type)
                else:
                    scored_docs[doc_id] = {
                        'document': doc,
                        'score': score,
                        'sources': [rep_type]
                    }
        
        # Sort by combined score and return top k
        sorted_docs = sorted(scored_docs.values(), key=lambda x: x['score'], reverse=True)
        
        retrieval_results = []
        for doc_info in sorted_docs[:k]:
            doc = doc_info['document']
            retrieval_results.append(RetrievalResult(
                document_id=doc.get('id', doc.get('doc_id', 'unknown')),
                content=doc.get('content', doc.get('text', '')),
                score=doc_info['score'],
                source=doc.get('source', 'unknown'),
                metadata={
                    'sources': doc_info['sources'],
                    'original_score': doc.get('score', 0),
                    **doc.get('metadata', {})
                }
            ))
        
        return retrieval_results

class KnowledgeGraphRetriever:
    def __init__(self):
        """Initialize knowledge graph retriever"""
        self.graph = nx.Graph()
        self.entity_cache = {}
        self.document_entities = defaultdict(set)
    
    def build_graph_from_documents(self, documents: List[Dict[str, Any]]):
        """Build knowledge graph from documents"""
        for doc in documents:
            doc_id = doc.get('id', doc.get('doc_id', 'unknown'))
            content = doc.get('content', doc.get('text', ''))
            
            entities = self.extract_entities(content)
            relationships = self.extract_relationships(content, entities)
            
            self.add_entities_to_graph(doc_id, entities, content)
            self.add_relationships_to_graph(relationships)
    
    def extract_entities(self, text: str) -> List[Tuple[str, str]]:
        """Extract entities and their types from text"""
        entities = []
        
        # Simple entity extraction (in production, use spaCy NER)
        words = text.split()
        
        for i, word in enumerate(words):
            # Look for capitalized words (potential entities)
            if word[0].isupper() and len(word) > 2:
                # Determine entity type based on context
                entity_type = self.classify_entity_type(word, words, i)
                entities.append((word, entity_type))
        
        return entities
    
    def classify_entity_type(self, word: str, context: List[str], position: int) -> str:
        """Classify entity type based on context"""
        # Simple rule-based classification
        if any(char.isdigit() for char in word):
            return 'NUMBER'
        elif word.lower() in ['company', 'corporation', 'inc', 'ltd']:
            return 'ORGANIZATION'
        elif word.lower() in ['mr', 'ms', 'dr', 'prof']:
            return 'PERSON'
        else:
            return 'MISC'
    
    def extract_relationships(self, text: str, entities: List[Tuple[str, str]]) -> List[Tuple[str, str, str]]:
        """Extract relationships between entities"""
        relationships = []
        
        # Simple relationship extraction
        # Look for patterns like "A is B", "A has B", etc.
        words = text.split()
        for i, word in enumerate(words):
            if word.lower() in ['is', 'has', 'contains', 'includes']:
                # Look for entities before and after the relationship word
                if i > 0 and i < len(words) - 1:
                    entity1 = words[i-1]
                    entity2 = words[i+1]
                    relationships.append((entity1, word.lower(), entity2))
        
        return relationships
    
    def add_entities_to_graph(self, doc_id: str, entities: List[Tuple[str, str]], content: str):
        """Add entities and relationships to the graph"""
        for entity, entity_type in entities:
            if entity not in self.graph:
                self.graph.add_node(entity, type=entity_type, docs=set())
            
            self.graph.nodes[entity]['docs'].add(doc_id)
            self.document_entities[doc_id].add(entity)
    
    def add_relationships_to_graph(self, relationships: List[Tuple[str, str, str]]):
        """Add relationships to the graph"""
        for entity1, relation, entity2 in relationships:
            if entity1 in self.graph and entity2 in self.graph:
                self.graph.add_edge(entity1, entity2, relation=relation)
    
    def graph_based_retrieval(self, query: str, k: int = 5) -> List[str]:
        """Retrieve documents using graph traversal"""
        query_entities = [entity for entity, _ in self.extract_entities(query)]
        relevant_docs = set()
        
        for entity in query_entities:
            if entity in self.graph:
                # Get documents containing this entity
                relevant_docs.update(self.graph.nodes[entity]['docs'])
                
                # Get documents containing related entities (neighbors)
                neighbors = list(self.graph.neighbors(entity))
                for neighbor in neighbors[:5]:  # Limit expansion
                    relevant_docs.update(self.graph.nodes[neighbor]['docs'])
        
        return list(relevant_docs)[:k]
    
    def get_entity_subgraph(self, entity: str, depth: int = 2) -> nx.Graph:
        """Get subgraph around a specific entity"""
        if entity not in self.graph:
            return nx.Graph()
        
        # Get nodes within specified depth
        nodes = {entity}
        current_level = {entity}
        
        for _ in range(depth):
            next_level = set()
            for node in current_level:
                next_level.update(self.graph.neighbors(node))
            nodes.update(next_level)
            current_level = next_level
        
        return self.graph.subgraph(nodes)
    
    def find_similar_entities(self, entity: str, top_k: int = 5) -> List[Tuple[str, float]]:
        """Find entities similar to the given entity"""
        if entity not in self.graph:
            return []
        
        # Use graph structure to find similar entities
        entity_neighbors = set(self.graph.neighbors(entity))
        similar_entities = []
        
        for other_entity in self.graph.nodes():
            if other_entity == entity:
                continue
            
            other_neighbors = set(self.graph.neighbors(other_entity))
            
            # Calculate Jaccard similarity
            intersection = len(entity_neighbors & other_neighbors)
            union = len(entity_neighbors | other_neighbors)
            
            if union > 0:
                similarity = intersection / union
                similar_entities.append((other_entity, similarity))
        
        return sorted(similar_entities, key=lambda x: x[1], reverse=True)[:top_k]

class HybridRetriever:
    def __init__(self, vector_retriever, graph_retriever, fusion_strategy: str = 'weighted'):
        """
        Hybrid retriever combining vector and graph-based approaches
        
        Args:
            vector_retriever: Multi-vector retriever
            graph_retriever: Knowledge graph retriever
            fusion_strategy: Strategy for fusing results ('weighted', 'reciprocal_rank', 'comb_sum')
        """
        self.vector_retriever = vector_retriever
        self.graph_retriever = graph_retriever
        self.fusion_strategy = fusion_strategy
    
    def retrieve(self, query: str, k: int = 10, 
                vector_weight: float = 0.7, graph_weight: float = 0.3) -> List[RetrievalResult]:
        """Retrieve documents using hybrid approach"""
        
        # Get vector-based results
        vector_results = self.vector_retriever.hybrid_retrieval(query, k=k*2)
        
        # Get graph-based results
        graph_doc_ids = self.graph_retriever.graph_based_retrieval(query, k=k)
        
        # Convert graph results to RetrievalResult format
        graph_results = []
        for doc_id in graph_doc_ids:
            graph_results.append(RetrievalResult(
                document_id=doc_id,
                content="",  # Would need to fetch from document store
                score=1.0,  # Placeholder score
                source="graph",
                metadata={'source': 'graph_retrieval'}
            ))
        
        # Fuse results
        if self.fusion_strategy == 'weighted':
            return self._weighted_fusion(vector_results, graph_results, vector_weight, graph_weight, k)
        elif self.fusion_strategy == 'reciprocal_rank':
            return self._reciprocal_rank_fusion(vector_results, graph_results, k)
        else:
            return self._comb_sum_fusion(vector_results, graph_results, k)
    
    def _weighted_fusion(self, vector_results: List[RetrievalResult], 
                        graph_results: List[RetrievalResult], 
                        vector_weight: float, graph_weight: float, k: int) -> List[RetrievalResult]:
        """Weighted fusion of results"""
        all_results = {}
        
        # Add vector results
        for result in vector_results:
            doc_id = result.document_id
            if doc_id in all_results:
                all_results[doc_id].score += result.score * vector_weight
            else:
                all_results[doc_id] = RetrievalResult(
                    document_id=doc_id,
                    content=result.content,
                    score=result.score * vector_weight,
                    source=result.source,
                    metadata=result.metadata
                )
        
        # Add graph results
        for result in graph_results:
            doc_id = result.document_id
            if doc_id in all_results:
                all_results[doc_id].score += result.score * graph_weight
            else:
                all_results[doc_id] = RetrievalResult(
                    document_id=doc_id,
                    content=result.content,
                    score=result.score * graph_weight,
                    source=result.source,
                    metadata=result.metadata
                )
        
        # Sort by combined score
        sorted_results = sorted(all_results.values(), key=lambda x: x.score, reverse=True)
        return sorted_results[:k]
    
    def _reciprocal_rank_fusion(self, vector_results: List[RetrievalResult], 
                               graph_results: List[RetrievalResult], k: int) -> List[RetrievalResult]:
        """Reciprocal rank fusion"""
        doc_scores = {}
        
        # Vector results
        for i, result in enumerate(vector_results):
            doc_id = result.document_id
            score = 1 / (i + 1)  # Reciprocal rank
            if doc_id in doc_scores:
                doc_scores[doc_id] += score
            else:
                doc_scores[doc_id] = score
        
        # Graph results
        for i, result in enumerate(graph_results):
            doc_id = result.document_id
            score = 1 / (i + 1)  # Reciprocal rank
            if doc_id in doc_scores:
                doc_scores[doc_id] += score
            else:
                doc_scores[doc_id] = score
        
        # Sort by combined score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top k results
        results = []
        for doc_id, score in sorted_docs[:k]:
            # Find the original result to get content
            original_result = next((r for r in vector_results if r.document_id == doc_id), None)
            if original_result:
                results.append(RetrievalResult(
                    document_id=doc_id,
                    content=original_result.content,
                    score=score,
                    source=original_result.source,
                    metadata=original_result.metadata
                ))
        
        return results
    
    def _comb_sum_fusion(self, vector_results: List[RetrievalResult], 
                        graph_results: List[RetrievalResult], k: int) -> List[RetrievalResult]:
        """Combination sum fusion"""
        doc_scores = {}
        
        # Vector results
        for result in vector_results:
            doc_id = result.document_id
            if doc_id in doc_scores:
                doc_scores[doc_id] += result.score
            else:
                doc_scores[doc_id] = result.score
        
        # Graph results
        for result in graph_results:
            doc_id = result.document_id
            if doc_id in doc_scores:
                doc_scores[doc_id] += result.score
            else:
                doc_scores[doc_id] = result.score
        
        # Sort by combined score
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Return top k results
        results = []
        for doc_id, score in sorted_docs[:k]:
            original_result = next((r for r in vector_results if r.document_id == doc_id), None)
            if original_result:
                results.append(RetrievalResult(
                    document_id=doc_id,
                    content=original_result.content,
                    score=score,
                    source=original_result.source,
                    metadata=original_result.metadata
                ))
        
        return results
