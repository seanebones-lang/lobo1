"""
Hybrid search implementation combining vector search and BM25.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from rank_bm25 import BM25Okapi
import logging

logger = logging.getLogger(__name__)


class BM25Retriever:
    """BM25-based text retrieval."""
    
    def __init__(self, documents: List[str]):
        """Initialize BM25 retriever with documents."""
        self.documents = documents
        self.tokenized_docs = [doc.split() for doc in documents]
        self.bm25 = BM25Okapi(self.tokenized_docs)
        logger.info(f"BM25 retriever initialized with {len(documents)} documents")
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant documents using BM25."""
        try:
            tokenized_query = query.split()
            scores = self.bm25.get_scores(tokenized_query)
            
            # Get top k results
            top_indices = np.argsort(scores)[::-1][:k]
            
            results = []
            for idx in top_indices:
                if scores[idx] > 0:  # Only include documents with positive scores
                    results.append({
                        "document": self.documents[idx],
                        "score": float(scores[idx]),
                        "index": int(idx)
                    })
            
            return results
        except Exception as e:
            logger.error(f"Error in BM25 search: {e}")
            return []
    
    def add_documents(self, documents: List[str]):
        """Add new documents to the BM25 index."""
        self.documents.extend(documents)
        self.tokenized_docs.extend([doc.split() for doc in documents])
        self.bm25 = BM25Okapi(self.tokenized_docs)
        logger.info(f"Added {len(documents)} documents to BM25 index")


class HybridRetriever:
    """Hybrid retrieval combining vector search and BM25."""
    
    def __init__(
        self, 
        vector_store,
        documents: List[str],
        alpha: float = 0.7,
        bm25_weight: float = 0.3
    ):
        """
        Initialize hybrid retriever.
        
        Args:
            vector_store: Vector store instance
            documents: List of documents for BM25
            alpha: Weight for vector search (0-1)
            bm25_weight: Weight for BM25 search (0-1)
        """
        self.vector_store = vector_store
        self.bm25_retriever = BM25Retriever(documents)
        self.alpha = alpha
        self.bm25_weight = bm25_weight
        self.documents = documents
        
        # Ensure weights sum to 1
        total_weight = alpha + bm25_weight
        if total_weight > 0:
            self.alpha = alpha / total_weight
            self.bm25_weight = bm25_weight / total_weight
        
        logger.info(f"Hybrid retriever initialized with alpha={self.alpha}, bm25_weight={self.bm25_weight}")
    
    def hybrid_search(
        self, 
        query: str, 
        query_embedding: np.ndarray,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Perform hybrid search combining vector and BM25 results."""
        try:
            # Vector search
            vector_results = self.vector_store.search(
                query_embedding=query_embedding,
                n_results=k * 2,  # Get more results for fusion
                filter_metadata=filter_metadata
            )
            
            # BM25 search
            bm25_results = self.bm25_retriever.search(query, k=k * 2)
            
            # Fuse results
            fused_results = self._fuse_results(
                vector_results, 
                bm25_results, 
                query
            )
            
            return fused_results[:k]
            
        except Exception as e:
            logger.error(f"Error in hybrid search: {e}")
            # Fallback to vector search only
            try:
                vector_results = self.vector_store.search(
                    query_embedding=query_embedding,
                    n_results=k,
                    filter_metadata=filter_metadata
                )
                return self._format_vector_results(vector_results)
            except Exception as fallback_error:
                logger.error(f"Fallback vector search also failed: {fallback_error}")
                return []
    
    def _fuse_results(
        self, 
        vector_results: Dict[str, Any], 
        bm25_results: List[Dict[str, Any]], 
        query: str
    ) -> List[Dict[str, Any]]:
        """Fuse vector and BM25 results using reciprocal rank fusion."""
        # Create document ID to index mapping for BM25
        doc_to_bm25_idx = {doc["document"]: idx for idx, doc in enumerate(bm25_results)}
        
        # Create document ID to index mapping for vector results
        doc_to_vector_idx = {}
        for idx, doc in enumerate(vector_results.get("documents", [])):
            if doc not in doc_to_vector_idx:
                doc_to_vector_idx[doc] = idx
        
        # Calculate fusion scores
        fusion_scores = {}
        
        # Score vector results
        for idx, doc in enumerate(vector_results.get("documents", [])):
            if doc in fusion_scores:
                # Use the better score if document appears multiple times
                current_score = fusion_scores[doc]
                vector_score = self.alpha * (1 / (idx + 1))
                fusion_scores[doc] = max(current_score, vector_score)
            else:
                fusion_scores[doc] = self.alpha * (1 / (idx + 1))
        
        # Score BM25 results
        for idx, bm25_result in enumerate(bm25_results):
            doc = bm25_result["document"]
            bm25_score = self.bm25_weight * (1 / (idx + 1))
            
            if doc in fusion_scores:
                fusion_scores[doc] += bm25_score
            else:
                fusion_scores[doc] = bm25_score
        
        # Sort by fusion score
        sorted_docs = sorted(fusion_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Format results
        fused_results = []
        for doc, score in sorted_docs:
            result = {
                "document": doc,
                "fusion_score": score,
                "source": "hybrid"
            }
            
            # Add vector search metadata if available
            if doc in doc_to_vector_idx:
                vector_idx = doc_to_vector_idx[doc]
                result.update({
                    "vector_score": vector_results.get("distances", [])[vector_idx],
                    "vector_metadata": vector_results.get("metadatas", [])[vector_idx],
                    "vector_id": vector_results.get("ids", [])[vector_idx]
                })
            
            # Add BM25 metadata if available
            if doc in doc_to_bm25_idx:
                bm25_idx = doc_to_bm25_idx[doc]
                result.update({
                    "bm25_score": bm25_results[bm25_idx]["score"],
                    "bm25_index": bm25_results[bm25_idx]["index"]
                })
            
            fused_results.append(result)
        
        return fused_results
    
    def _format_vector_results(self, vector_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Format vector search results."""
        results = []
        for i, doc in enumerate(vector_results.get("documents", [])):
            results.append({
                "document": doc,
                "vector_score": vector_results.get("distances", [])[i],
                "vector_metadata": vector_results.get("metadatas", [])[i],
                "vector_id": vector_results.get("ids", [])[i],
                "source": "vector_only"
            })
        return results
    
    def update_documents(self, new_documents: List[str]):
        """Update the document collection."""
        self.documents.extend(new_documents)
        self.bm25_retriever.add_documents(new_documents)
        logger.info(f"Updated documents. Total: {len(self.documents)}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get retriever statistics."""
        return {
            "total_documents": len(self.documents),
            "alpha": self.alpha,
            "bm25_weight": self.bm25_weight,
            "vector_store_type": self.vector_store.vector_db_type
        }

