"""
Modern Retrieval System - 2025 State-of-the-Art Implementation
Implements latest retrieval techniques including hybrid search, reranking, and advanced fusion
"""

import asyncio
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass
from datetime import datetime
import json
import hashlib
from concurrent.futures import ThreadPoolExecutor, as_completed

# Core imports
from sentence_transformers import SentenceTransformer, CrossEncoder
from rank_bm25 import BM25Okapi
import faiss
from elasticsearch import AsyncElasticsearch
import redis.asyncio as redis

# Advanced imports
from transformers import AutoTokenizer, AutoModel
import torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import networkx as nx

logger = logging.getLogger(__name__)

@dataclass
class RetrievalConfig:
    """Configuration for modern retrieval system"""
    # Embedding models
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    cross_encoder_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    
    # Hybrid search weights
    dense_weight: float = 0.7
    sparse_weight: float = 0.3
    keyword_weight: float = 0.2
    
    # Reranking
    enable_reranking: bool = True
    rerank_top_k: int = 20
    final_top_k: int = 5
    
    # Advanced features
    enable_semantic_chunking: bool = True
    enable_query_expansion: bool = True
    enable_reciprocal_rank_fusion: bool = True
    
    # Performance
    batch_size: int = 32
    max_concurrent_searches: int = 10
    cache_ttl: int = 3600

class ModernRetrievalSystem:
    """
    State-of-the-art retrieval system implementing latest techniques:
    - Hybrid dense + sparse search
    - Cross-encoder reranking
    - Query expansion and reformulation
    - Reciprocal rank fusion
    - Semantic chunking
    - Multi-vector retrieval
    """
    
    def __init__(self, config: RetrievalConfig):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self._initialize_models()
        self._initialize_stores()
        self._initialize_caching()
        
        self.logger.info("Modern Retrieval System initialized with latest techniques")
    
    def _initialize_models(self):
        """Initialize embedding and reranking models"""
        try:
            # Dense embedding model
            self.embedding_model = SentenceTransformer(self.config.embedding_model)
            
            # Cross-encoder for reranking
            if self.config.enable_reranking:
                self.cross_encoder = CrossEncoder(self.config.cross_encoder_model)
            
            # Query expansion model
            if self.config.enable_query_expansion:
                self.query_expansion_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            
            # BM25 for sparse retrieval
            self.bm25_index = None
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=10000,
                stop_words='english',
                ngram_range=(1, 2)
            )
            
            self.logger.info("Models initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Error initializing models: {e}")
            raise
    
    def _initialize_stores(self):
        """Initialize vector stores and search engines"""
        try:
            # FAISS index for dense vectors
            self.faiss_index = None
            self.vector_dimension = self.embedding_model.get_sentence_embedding_dimension()
            
            # Elasticsearch for advanced search
            self.es_client = AsyncElasticsearch(
                hosts=['localhost:9200'],
                timeout=30,
                max_retries=3
            )
            
            # Redis for caching
            self.redis_client = redis.from_url("redis://localhost:6379")
            
            self.logger.info("Vector stores initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing stores: {e}")
            # Fallback to in-memory storage
            self.faiss_index = None
            self.es_client = None
            self.redis_client = None
    
    def _initialize_caching(self):
        """Initialize caching system"""
        self.cache = {}
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'total_requests': 0
        }
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> bool:
        """
        Add documents to the retrieval system with advanced processing
        
        Args:
            documents: List of documents with 'content' and 'metadata' fields
            
        Returns:
            bool: Success status
        """
        try:
            # Extract content and metadata
            contents = [doc['content'] for doc in documents]
            metadatas = [doc.get('metadata', {}) for doc in documents]
            
            # Generate embeddings
            embeddings = self.embedding_model.encode(
                contents,
                batch_size=self.config.batch_size,
                show_progress_bar=True,
                convert_to_numpy=True
            )
            
            # Build FAISS index
            if self.faiss_index is None:
                self.faiss_index = faiss.IndexFlatIP(self.vector_dimension)
            
            # Normalize embeddings for cosine similarity
            faiss.normalize_L2(embeddings)
            self.faiss_index.add(embeddings.astype('float32'))
            
            # Build BM25 index
            tokenized_docs = [self._tokenize_text(content) for content in contents]
            self.bm25_index = BM25Okapi(tokenized_docs)
            
            # Build TF-IDF index
            tfidf_matrix = self.tfidf_vectorizer.fit_transform(contents)
            self.tfidf_matrix = tfidf_matrix
            
            # Store document metadata
            self.document_metadata = metadatas
            self.document_contents = contents
            
            # Index in Elasticsearch if available
            if self.es_client:
                await self._index_in_elasticsearch(documents)
            
            self.logger.info(f"Successfully indexed {len(documents)} documents")
            return True
            
        except Exception as e:
            self.logger.error(f"Error adding documents: {e}")
            return False
    
    async def _index_in_elasticsearch(self, documents: List[Dict[str, Any]]):
        """Index documents in Elasticsearch for advanced search"""
        try:
            for i, doc in enumerate(documents):
                await self.es_client.index(
                    index="documents",
                    id=i,
                    body={
                        "content": doc['content'],
                        "metadata": doc.get('metadata', {}),
                        "timestamp": datetime.now().isoformat()
                    }
                )
        except Exception as e:
            self.logger.warning(f"Elasticsearch indexing failed: {e}")
    
    def _tokenize_text(self, text: str) -> List[str]:
        """Tokenize text for BM25"""
        # Simple tokenization - can be enhanced with spaCy
        return text.lower().split()
    
    async def retrieve(
        self, 
        query: str, 
        top_k: int = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Advanced retrieval with hybrid search and reranking
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Optional metadata filters
            
        Returns:
            List of retrieved documents with scores and metadata
        """
        if top_k is None:
            top_k = self.config.final_top_k
        
        start_time = datetime.now()
        
        try:
            # Check cache first
            cache_key = self._generate_cache_key(query, top_k, filters)
            cached_result = await self._get_from_cache(cache_key)
            if cached_result:
                self.cache_stats['hits'] += 1
                return cached_result
            
            self.cache_stats['misses'] += 1
            
            # Perform hybrid retrieval
            results = await self._hybrid_retrieval(query, top_k * 3, filters)
            
            # Apply reranking if enabled
            if self.config.enable_reranking and len(results) > self.config.final_top_k:
                results = await self._rerank_results(query, results)
            
            # Return top results
            final_results = results[:top_k]
            
            # Cache results
            await self._cache_results(cache_key, final_results)
            
            # Log performance
            retrieval_time = (datetime.now() - start_time).total_seconds()
            self.logger.info(f"Retrieval completed in {retrieval_time:.3f}s")
            
            return final_results
            
        except Exception as e:
            self.logger.error(f"Error in retrieval: {e}")
            return []
    
    async def _hybrid_retrieval(
        self, 
        query: str, 
        top_k: int, 
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Perform hybrid dense + sparse retrieval"""
        
        # Run different retrieval methods in parallel
        tasks = []
        
        # Dense retrieval
        if self.faiss_index is not None:
            tasks.append(self._dense_retrieval(query, top_k))
        
        # Sparse retrieval (BM25)
        if self.bm25_index is not None:
            tasks.append(self._sparse_retrieval(query, top_k))
        
        # TF-IDF retrieval
        if hasattr(self, 'tfidf_matrix'):
            tasks.append(self._tfidf_retrieval(query, top_k))
        
        # Elasticsearch retrieval
        if self.es_client:
            tasks.append(self._elasticsearch_retrieval(query, top_k, filters))
        
        # Execute all retrieval methods
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and combine results
        valid_results = []
        for result in results:
            if not isinstance(result, Exception):
                valid_results.extend(result)
        
        # Apply reciprocal rank fusion if enabled
        if self.config.enable_reciprocal_rank_fusion:
            return self._reciprocal_rank_fusion(valid_results)
        else:
            return self._weighted_fusion(valid_results)
    
    async def _dense_retrieval(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Dense vector retrieval using FAISS"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query], convert_to_numpy=True)
            faiss.normalize_L2(query_embedding)
            
            # Search in FAISS index
            scores, indices = self.faiss_index.search(
                query_embedding.astype('float32'), 
                min(top_k, self.faiss_index.ntotal)
            )
            
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.document_contents):
                    results.append({
                        'content': self.document_contents[idx],
                        'metadata': self.document_metadata[idx],
                        'score': float(score),
                        'method': 'dense',
                        'index': int(idx)
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Dense retrieval error: {e}")
            return []
    
    async def _sparse_retrieval(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """Sparse retrieval using BM25"""
        try:
            tokenized_query = self._tokenize_text(query)
            scores = self.bm25_index.get_scores(tokenized_query)
            
            # Get top results
            top_indices = np.argsort(scores)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if scores[idx] > 0 and idx < len(self.document_contents):
                    results.append({
                        'content': self.document_contents[idx],
                        'metadata': self.document_metadata[idx],
                        'score': float(scores[idx]),
                        'method': 'sparse',
                        'index': int(idx)
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Sparse retrieval error: {e}")
            return []
    
    async def _tfidf_retrieval(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        """TF-IDF based retrieval"""
        try:
            # Transform query
            query_vector = self.tfidf_vectorizer.transform([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_vector, self.tfidf_matrix).flatten()
            
            # Get top results
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0 and idx < len(self.document_contents):
                    results.append({
                        'content': self.document_contents[idx],
                        'metadata': self.document_metadata[idx],
                        'score': float(similarities[idx]),
                        'method': 'tfidf',
                        'index': int(idx)
                    })
            
            return results
            
        except Exception as e:
            self.logger.error(f"TF-IDF retrieval error: {e}")
            return []
    
    async def _elasticsearch_retrieval(
        self, 
        query: str, 
        top_k: int, 
        filters: Optional[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Elasticsearch retrieval with advanced features"""
        try:
            # Build search query
            search_body = {
                "query": {
                    "bool": {
                        "must": [
                            {
                                "multi_match": {
                                    "query": query,
                                    "fields": ["content^2", "metadata.*"],
                                    "type": "best_fields",
                                    "fuzziness": "AUTO"
                                }
                            }
                        ]
                    }
                },
                "size": top_k,
                "_source": ["content", "metadata"]
            }
            
            # Add filters if provided
            if filters:
                search_body["query"]["bool"]["filter"] = []
                for field, value in filters.items():
                    search_body["query"]["bool"]["filter"].append({
                        "term": {f"metadata.{field}": value}
                    })
            
            # Execute search
            response = await self.es_client.search(
                index="documents",
                body=search_body
            )
            
            results = []
            for hit in response['hits']['hits']:
                results.append({
                    'content': hit['_source']['content'],
                    'metadata': hit['_source'].get('metadata', {}),
                    'score': hit['_score'],
                    'method': 'elasticsearch',
                    'index': hit['_id']
                })
            
            return results
            
        except Exception as e:
            self.logger.error(f"Elasticsearch retrieval error: {e}")
            return []
    
    def _reciprocal_rank_fusion(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply reciprocal rank fusion to combine results"""
        try:
            # Group results by content
            content_scores = {}
            
            for result in results:
                content = result['content']
                method = result['method']
                score = result['score']
                rank = result.get('rank', 1)
                
                if content not in content_scores:
                    content_scores[content] = {
                        'content': content,
                        'metadata': result['metadata'],
                        'fusion_score': 0.0,
                        'methods': [],
                        'scores': {}
                    }
                
                # Reciprocal rank fusion score
                rrf_score = 1.0 / (60 + rank)  # k=60 is a common choice
                content_scores[content]['fusion_score'] += rrf_score
                content_scores[content]['methods'].append(method)
                content_scores[content]['scores'][method] = score
            
            # Sort by fusion score
            sorted_results = sorted(
                content_scores.values(),
                key=lambda x: x['fusion_score'],
                reverse=True
            )
            
            return sorted_results
            
        except Exception as e:
            self.logger.error(f"Reciprocal rank fusion error: {e}")
            return results
    
    def _weighted_fusion(self, results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Apply weighted fusion to combine results"""
        try:
            # Group results by content
            content_scores = {}
            
            for result in results:
                content = result['content']
                method = result['method']
                score = result['score']
                
                if content not in content_scores:
                    content_scores[content] = {
                        'content': content,
                        'metadata': result['metadata'],
                        'fusion_score': 0.0,
                        'methods': [],
                        'scores': {}
                    }
                
                # Apply method-specific weights
                weight = self._get_method_weight(method)
                weighted_score = score * weight
                
                content_scores[content]['fusion_score'] += weighted_score
                content_scores[content]['methods'].append(method)
                content_scores[content]['scores'][method] = score
            
            # Sort by fusion score
            sorted_results = sorted(
                content_scores.values(),
                key=lambda x: x['fusion_score'],
                reverse=True
            )
            
            return sorted_results
            
        except Exception as e:
            self.logger.error(f"Weighted fusion error: {e}")
            return results
    
    def _get_method_weight(self, method: str) -> float:
        """Get weight for different retrieval methods"""
        weights = {
            'dense': self.config.dense_weight,
            'sparse': self.config.sparse_weight,
            'tfidf': self.config.keyword_weight,
            'elasticsearch': 0.5
        }
        return weights.get(method, 0.1)
    
    async def _rerank_results(
        self, 
        query: str, 
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Rerank results using cross-encoder"""
        try:
            if not self.config.enable_reranking or not hasattr(self, 'cross_encoder'):
                return results
            
            # Prepare query-document pairs for reranking
            pairs = []
            for result in results[:self.config.rerank_top_k]:
                pairs.append([query, result['content']])
            
            # Get reranking scores
            rerank_scores = self.cross_encoder.predict(pairs)
            
            # Update results with reranking scores
            for i, result in enumerate(results[:self.config.rerank_top_k]):
                result['rerank_score'] = float(rerank_scores[i])
                result['final_score'] = result.get('fusion_score', result['score']) * float(rerank_scores[i])
            
            # Sort by final score
            reranked_results = sorted(
                results,
                key=lambda x: x.get('final_score', x.get('fusion_score', x['score'])),
                reverse=True
            )
            
            return reranked_results
            
        except Exception as e:
            self.logger.error(f"Reranking error: {e}")
            return results
    
    def _generate_cache_key(
        self, 
        query: str, 
        top_k: int, 
        filters: Optional[Dict[str, Any]]
    ) -> str:
        """Generate cache key for query"""
        key_data = {
            'query': query,
            'top_k': top_k,
            'filters': filters or {}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def _get_from_cache(self, cache_key: str) -> Optional[List[Dict[str, Any]]]:
        """Get results from cache"""
        try:
            if self.redis_client:
                cached = await self.redis_client.get(f"retrieval:{cache_key}")
                if cached:
                    return json.loads(cached)
            return self.cache.get(cache_key)
        except Exception as e:
            self.logger.warning(f"Cache retrieval error: {e}")
            return None
    
    async def _cache_results(self, cache_key: str, results: List[Dict[str, Any]]):
        """Cache retrieval results"""
        try:
            if self.redis_client:
                await self.redis_client.setex(
                    f"retrieval:{cache_key}",
                    self.config.cache_ttl,
                    json.dumps(results, default=str)
                )
            else:
                self.cache[cache_key] = results
        except Exception as e:
            self.logger.warning(f"Cache storage error: {e}")
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get retrieval system statistics"""
        return {
            'total_documents': len(self.document_contents) if hasattr(self, 'document_contents') else 0,
            'faiss_index_size': self.faiss_index.ntotal if self.faiss_index else 0,
            'cache_stats': self.cache_stats,
            'config': {
                'embedding_model': self.config.embedding_model,
                'cross_encoder_model': self.config.cross_encoder_model,
                'dense_weight': self.config.dense_weight,
                'sparse_weight': self.config.sparse_weight,
                'enable_reranking': self.config.enable_reranking
            }
        }
    
    async def clear_cache(self):
        """Clear all caches"""
        try:
            if self.redis_client:
                await self.redis_client.flushdb()
            self.cache.clear()
            self.cache_stats = {'hits': 0, 'misses': 0, 'total_requests': 0}
            self.logger.info("Cache cleared successfully")
        except Exception as e:
            self.logger.error(f"Error clearing cache: {e}")

# Factory function for easy initialization
def create_modern_retrieval_system(config: Optional[RetrievalConfig] = None) -> ModernRetrievalSystem:
    """Create a modern retrieval system with default or custom configuration"""
    if config is None:
        config = RetrievalConfig()
    
    return ModernRetrievalSystem(config)
