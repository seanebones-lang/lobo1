"""
Main RAG generator that combines retrieval and generation components.
"""

import time
import logging
from typing import Dict, Any, Optional, List, Union
from .llm_manager import LLMManager
from .prompt_manager import PromptManager
from ..retrieval.embedding_generator import EmbeddingGenerator
from ..retrieval.hybrid_search import HybridRetriever
from ..retrieval.reranker import Reranker, CohereReranker

logger = logging.getLogger(__name__)


class RAGGenerator:
    """Main RAG system that combines retrieval and generation."""
    
    def __init__(
        self,
        llm_manager: LLMManager,
        embedding_generator: EmbeddingGenerator,
        hybrid_retriever: HybridRetriever,
        prompt_manager: Optional[PromptManager] = None,
        reranker: Optional[Union[Reranker, CohereReranker]] = None,
        use_reranking: bool = True,
        max_context_length: int = 4000
    ):
        """
        Initialize RAG generator.
        
        Args:
            llm_manager: LLM manager for text generation
            embedding_generator: Embedding generator for queries
            hybrid_retriever: Hybrid retriever for document search
            prompt_manager: Prompt manager for different query types
            reranker: Optional reranker for improving results
            use_reranking: Whether to use reranking
            max_context_length: Maximum context length for generation
        """
        self.llm_manager = llm_manager
        self.embedding_generator = embedding_generator
        self.hybrid_retriever = hybrid_retriever
        self.prompt_manager = prompt_manager or PromptManager()
        self.reranker = reranker
        self.use_reranking = use_reranking and reranker is not None
        self.max_context_length = max_context_length
        
        logger.info(f"RAG Generator initialized with reranking: {self.use_reranking}")
    
    def generate_answer(
        self,
        query: str,
        prompt_type: str = "qa",
        top_k: int = 5,
        rerank_top_k: int = 3,
        include_sources: bool = True,
        system_role: str = "assistant",
        **generation_kwargs
    ) -> Dict[str, Any]:
        """
        Generate an answer using RAG.
        
        Args:
            query: User query
            prompt_type: Type of prompt to use
            top_k: Number of documents to retrieve
            rerank_top_k: Number of documents to use after reranking
            include_sources: Whether to include source information
            system_role: System role for the LLM
            **generation_kwargs: Additional generation parameters
            
        Returns:
            Dictionary with answer and metadata
        """
        start_time = time.time()
        
        try:
            # Step 1: Generate query embedding
            logger.info("Generating query embedding")
            query_embedding = self.embedding_generator.generate_embeddings(query)
            
            # Step 2: Retrieve relevant documents
            logger.info(f"Retrieving top {top_k} documents")
            retrieved_docs = self.hybrid_retriever.hybrid_search(
                query=query,
                query_embedding=query_embedding,
                k=top_k
            )
            
            if not retrieved_docs:
                return {
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": [],
                    "confidence": 0.0,
                    "retrieval_time": time.time() - start_time,
                    "generation_time": 0.0,
                    "total_time": time.time() - start_time,
                    "model_used": None,
                    "tokens_used": 0,
                    "error": None
                }
            
            # Step 3: Rerank documents if enabled
            if self.use_reranking and len(retrieved_docs) > rerank_top_k:
                logger.info(f"Reranking documents to top {rerank_top_k}")
                if hasattr(self.reranker, 'rerank_with_metadata'):
                    reranked_docs = self.reranker.rerank_with_metadata(
                        query=query,
                        search_results=retrieved_docs,
                        top_k=rerank_top_k
                    )
                else:
                    # Fallback for basic reranker
                    doc_texts = [doc.get("document", "") for doc in retrieved_docs]
                    reranked_docs = self.reranker.rerank(query, doc_texts, top_k=rerank_top_k)
                    # Convert back to full format
                    reranked_docs = [
                        {**doc, "document": reranked_doc["document"], "relevance_score": reranked_doc["relevance_score"]}
                        for doc, reranked_doc in zip(retrieved_docs, reranked_docs)
                    ]
            else:
                reranked_docs = retrieved_docs[:rerank_top_k]
            
            # Step 4: Prepare context
            context = self._prepare_context(reranked_docs)
            
            # Step 5: Generate answer
            logger.info("Generating answer")
            generation_start = time.time()
            
            # Format prompt with context
            if prompt_type in ["conversation"]:
                # For conversation, we need additional parameters
                formatted_prompt = self.prompt_manager.format_with_system_message(
                    prompt_type=prompt_type,
                    system_role=system_role,
                    context=context,
                    question=query,
                    conversation_history="",  # Could be enhanced with actual history
                    message=query
                )
            else:
                formatted_prompt = self.prompt_manager.format_with_system_message(
                    prompt_type=prompt_type,
                    system_role=system_role,
                    context=context,
                    question=query
                )
            
            # Generate response
            response = self.llm_manager.generate(
                prompt=formatted_prompt,
                **generation_kwargs
            )
            
            generation_time = time.time() - generation_start
            total_time = time.time() - start_time
            
            # Step 6: Prepare sources if requested
            sources = []
            if include_sources:
                sources = self._extract_sources(reranked_docs)
            
            # Step 7: Calculate confidence
            confidence = self._calculate_confidence(reranked_docs, response)
            
            return {
                "answer": response["text"],
                "sources": sources,
                "confidence": confidence,
                "retrieval_time": generation_start - start_time,
                "generation_time": generation_time,
                "total_time": total_time,
                "model_used": response.get("model_used"),
                "tokens_used": response.get("tokens_used", 0),
                "error": response.get("error")
            }
            
        except Exception as e:
            logger.error(f"Error in RAG generation: {e}")
            return {
                "answer": f"I encountered an error while processing your request: {str(e)}",
                "sources": [],
                "confidence": 0.0,
                "retrieval_time": 0.0,
                "generation_time": 0.0,
                "total_time": time.time() - start_time,
                "model_used": None,
                "tokens_used": 0,
                "error": str(e)
            }
    
    def generate_streaming_answer(
        self,
        query: str,
        prompt_type: str = "qa",
        top_k: int = 5,
        rerank_top_k: int = 3,
        system_role: str = "assistant",
        **generation_kwargs
    ):
        """
        Generate a streaming answer using RAG.
        
        Args:
            query: User query
            prompt_type: Type of prompt to use
            top_k: Number of documents to retrieve
            rerank_top_k: Number of documents to use after reranking
            system_role: System role for the LLM
            **generation_kwargs: Additional generation parameters
            
        Yields:
            Dictionary with answer chunks and metadata
        """
        try:
            # Step 1: Generate query embedding
            query_embedding = self.embedding_generator.generate_embeddings(query)
            
            # Step 2: Retrieve relevant documents
            retrieved_docs = self.hybrid_retriever.hybrid_search(
                query=query,
                query_embedding=query_embedding,
                k=top_k
            )
            
            if not retrieved_docs:
                yield {
                    "type": "error",
                    "content": "I couldn't find any relevant information to answer your question.",
                    "sources": [],
                    "confidence": 0.0
                }
                return
            
            # Step 3: Rerank documents if enabled
            if self.use_reranking and len(retrieved_docs) > rerank_top_k:
                if hasattr(self.reranker, 'rerank_with_metadata'):
                    reranked_docs = self.reranker.rerank_with_metadata(
                        query=query,
                        search_results=retrieved_docs,
                        top_k=rerank_top_k
                    )
                else:
                    doc_texts = [doc.get("document", "") for doc in retrieved_docs]
                    reranked_docs = self.reranker.rerank(query, doc_texts, top_k=rerank_top_k)
            else:
                reranked_docs = retrieved_docs[:rerank_top_k]
            
            # Step 4: Prepare context
            context = self._prepare_context(reranked_docs)
            
            # Step 5: Format prompt
            formatted_prompt = self.prompt_manager.format_with_system_message(
                prompt_type=prompt_type,
                system_role=system_role,
                context=context,
                question=query
            )
            
            # Step 6: Stream generation
            yield {
                "type": "sources",
                "content": self._extract_sources(reranked_docs),
                "confidence": self._calculate_confidence(reranked_docs, {"text": ""})
            }
            
            for chunk in self.llm_manager.generate_stream(
                prompt=formatted_prompt,
                **generation_kwargs
            ):
                yield {
                    "type": "content",
                    "content": chunk
                }
            
            yield {"type": "done"}
            
        except Exception as e:
            logger.error(f"Error in streaming RAG generation: {e}")
            yield {
                "type": "error",
                "content": f"I encountered an error while processing your request: {str(e)}"
            }
    
    def _prepare_context(self, documents: List[Dict[str, Any]]) -> str:
        """Prepare context from retrieved documents."""
        context_parts = []
        
        for i, doc in enumerate(documents, 1):
            doc_text = doc.get("document", "")
            if doc_text:
                context_parts.append(f"Source {i}:\n{doc_text}\n")
        
        context = "\n".join(context_parts)
        
        # Truncate if too long
        if len(context) > self.max_context_length:
            context = context[:self.max_context_length] + "..."
        
        return context
    
    def _extract_sources(self, documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extract source information from documents."""
        sources = []
        
        for i, doc in enumerate(documents, 1):
            source = {
                "id": i,
                "text": doc.get("document", "")[:200] + "..." if len(doc.get("document", "")) > 200 else doc.get("document", ""),
                "score": doc.get("fusion_score", doc.get("vector_score", 0.0)),
                "metadata": doc.get("vector_metadata", {})
            }
            
            # Add reranking info if available
            if "relevance_score" in doc:
                source["relevance_score"] = doc["relevance_score"]
            
            sources.append(source)
        
        return sources
    
    def _calculate_confidence(
        self, 
        documents: List[Dict[str, Any]], 
        response: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for the response."""
        if not documents:
            return 0.0
        
        # Base confidence on document scores
        scores = []
        for doc in documents:
            if "relevance_score" in doc:
                scores.append(doc["relevance_score"])
            elif "fusion_score" in doc:
                scores.append(doc["fusion_score"])
            elif "vector_score" in doc:
                scores.append(1.0 - doc["vector_score"])  # Convert distance to similarity
        
        if scores:
            avg_score = sum(scores) / len(scores)
            return min(avg_score, 1.0)
        
        return 0.5  # Default confidence
    
    def get_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics."""
        return {
            "llm_stats": self.llm_manager.get_stats(),
            "embedding_stats": self.embedding_generator.get_cache_stats(),
            "retriever_stats": self.hybrid_retriever.get_stats(),
            "reranking_enabled": self.use_reranking,
            "max_context_length": self.max_context_length
        }

