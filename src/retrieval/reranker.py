"""
Reranking module for improving retrieval quality.
"""

import torch
import numpy as np
from typing import List, Dict, Any, Optional, Union
from transformers import AutoModelForSequenceClassification, AutoTokenizer
import logging

logger = logging.getLogger(__name__)


class Reranker:
    """Rerank search results using cross-encoder models."""
    
    def __init__(
        self, 
        model_name: str = "BAAI/bge-reranker-large",
        device: Optional[str] = None,
        max_length: int = 512
    ):
        """
        Initialize reranker.
        
        Args:
            model_name: Name of the reranking model
            device: Device to run the model on (auto-detect if None)
            max_length: Maximum sequence length
        """
        self.model_name = model_name
        self.max_length = max_length
        
        # Auto-detect device if not specified
        if device is None:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:
            self.device = device
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            logger.info(f"Reranker initialized with model: {model_name} on device: {self.device}")
        except Exception as e:
            logger.error(f"Error initializing reranker: {e}")
            raise
    
    def rerank(
        self, 
        query: str, 
        documents: List[str], 
        top_k: int = 5,
        batch_size: int = 32
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents based on query relevance.
        
        Args:
            query: Search query
            documents: List of documents to rerank
            top_k: Number of top documents to return
            batch_size: Batch size for processing
            
        Returns:
            List of reranked documents with scores
        """
        if not documents:
            return []
        
        try:
            scores = self._calculate_relevance_scores(
                query, documents, batch_size
            )
            
            # Sort documents by relevance score
            ranked_indices = np.argsort(scores)[::-1]
            ranked_documents = []
            
            for i, idx in enumerate(ranked_indices[:top_k]):
                ranked_documents.append({
                    "document": documents[idx],
                    "relevance_score": float(scores[idx]),
                    "rank": i + 1
                })
            
            return ranked_documents
            
        except Exception as e:
            logger.error(f"Error in reranking: {e}")
            # Return original order if reranking fails
            return [{"document": doc, "relevance_score": 0.0, "rank": i + 1} 
                   for i, doc in enumerate(documents[:top_k])]
    
    def _calculate_relevance_scores(
        self, 
        query: str, 
        documents: List[str], 
        batch_size: int
    ) -> np.ndarray:
        """Calculate relevance scores for query-document pairs."""
        scores = []
        
        # Process in batches
        for i in range(0, len(documents), batch_size):
            batch_docs = documents[i:i + batch_size]
            batch_scores = self._process_batch(query, batch_docs)
            scores.extend(batch_scores)
        
        return np.array(scores)
    
    def _process_batch(self, query: str, documents: List[str]) -> List[float]:
        """Process a batch of query-document pairs."""
        try:
            # Tokenize query-document pairs
            inputs = self.tokenizer(
                [query] * len(documents),
                documents,
                return_tensors='pt',
                truncation=True,
                max_length=self.max_length,
                padding=True
            )
            
            # Move to device
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            # Calculate scores
            with torch.no_grad():
                outputs = self.model(**inputs)
                scores = torch.softmax(outputs.logits, dim=1)[:, 1].cpu().numpy()
            
            return scores.tolist()
            
        except Exception as e:
            logger.error(f"Error processing batch: {e}")
            # Return neutral scores if processing fails
            return [0.5] * len(documents)
    
    def rerank_with_metadata(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        top_k: int = 5,
        batch_size: int = 32
    ) -> List[Dict[str, Any]]:
        """
        Rerank search results while preserving metadata.
        
        Args:
            query: Search query
            search_results: List of search results with metadata
            top_k: Number of top results to return
            batch_size: Batch size for processing
            
        Returns:
            List of reranked results with preserved metadata
        """
        if not search_results:
            return []
        
        # Extract documents for reranking
        documents = [result.get("document", "") for result in search_results]
        
        # Rerank documents
        reranked_docs = self.rerank(query, documents, top_k, batch_size)
        
        # Create mapping from document to original result
        doc_to_result = {result.get("document", ""): result for result in search_results}
        
        # Combine reranked documents with original metadata
        reranked_results = []
        for reranked_doc in reranked_docs:
            doc_text = reranked_doc["document"]
            if doc_text in doc_to_result:
                original_result = doc_to_result[doc_text]
                # Update with reranking information
                updated_result = original_result.copy()
                updated_result.update({
                    "relevance_score": reranked_doc["relevance_score"],
                    "rerank_rank": reranked_doc["rank"],
                    "reranked": True
                })
                reranked_results.append(updated_result)
        
        return reranked_results
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the reranking model."""
        return {
            "model_name": self.model_name,
            "device": self.device,
            "max_length": self.max_length,
            "model_type": "cross_encoder"
        }


class CohereReranker:
    """Reranker using Cohere's rerank API."""
    
    def __init__(self, api_key: str, model_name: str = "rerank-english-v2.0"):
        """
        Initialize Cohere reranker.
        
        Args:
            api_key: Cohere API key
            model_name: Name of the rerank model
        """
        try:
            import cohere
            self.client = cohere.Client(api_key)
            self.model_name = model_name
            logger.info(f"Cohere reranker initialized with model: {model_name}")
        except ImportError:
            logger.error("Cohere package not installed. Install with: pip install cohere")
            raise
        except Exception as e:
            logger.error(f"Error initializing Cohere reranker: {e}")
            raise
    
    def rerank(
        self, 
        query: str, 
        documents: List[str], 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Rerank documents using Cohere's rerank API.
        
        Args:
            query: Search query
            documents: List of documents to rerank
            top_k: Number of top documents to return
            
        Returns:
            List of reranked documents with scores
        """
        if not documents:
            return []
        
        try:
            response = self.client.rerank(
                model=self.model_name,
                query=query,
                documents=documents,
                top_k=min(top_k, len(documents))
            )
            
            reranked_results = []
            for result in response.results:
                reranked_results.append({
                    "document": result.document["text"],
                    "relevance_score": result.relevance_score,
                    "rank": result.index + 1
                })
            
            return reranked_results
            
        except Exception as e:
            logger.error(f"Error in Cohere reranking: {e}")
            # Return original order if reranking fails
            return [{"document": doc, "relevance_score": 0.0, "rank": i + 1} 
                   for i, doc in enumerate(documents[:top_k])]
    
    def rerank_with_metadata(
        self,
        query: str,
        search_results: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """Rerank search results while preserving metadata using Cohere."""
        if not search_results:
            return []
        
        # Extract documents for reranking
        documents = [result.get("document", "") for result in search_results]
        
        # Rerank documents
        reranked_docs = self.rerank(query, documents, top_k)
        
        # Create mapping from document to original result
        doc_to_result = {result.get("document", ""): result for result in search_results}
        
        # Combine reranked documents with original metadata
        reranked_results = []
        for reranked_doc in reranked_docs:
            doc_text = reranked_doc["document"]
            if doc_text in doc_to_result:
                original_result = doc_to_result[doc_text]
                # Update with reranking information
                updated_result = original_result.copy()
                updated_result.update({
                    "relevance_score": reranked_doc["relevance_score"],
                    "rerank_rank": reranked_doc["rank"],
                    "reranked": True,
                    "reranker": "cohere"
                })
                reranked_results.append(updated_result)
        
        return reranked_results

