"""
Embedding generation module for creating vector representations of text.
"""

import numpy as np
from typing import List, Union, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
import openai
from langchain_openai import OpenAIEmbeddings
import os
from functools import lru_cache


class EmbeddingGenerator:
    """Generate embeddings for text using various models."""
    
    def __init__(
        self, 
        model_name: str = "all-MiniLM-L6-v2",
        openai_api_key: Optional[str] = None,
        cache_size: int = 1000
    ):
        self.model_name = model_name
        self.openai_api_key = openai_api_key
        self.cache = {}
        self.cache_size = cache_size
        
        # Initialize model based on type
        if model_name.startswith("text-embedding"):
            if not openai_api_key:
                raise ValueError("OpenAI API key required for OpenAI embeddings")
            self.model = OpenAIEmbeddings(openai_api_key=openai_api_key)
            self.model_type = "openai"
        else:
            self.model = SentenceTransformer(model_name)
            self.model_type = "sentence_transformer"
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return f"{self.model_name}:{hash(text)}"
    
    def _update_cache(self, texts: List[str], embeddings: np.ndarray):
        """Update cache with new embeddings."""
        if len(self.cache) >= self.cache_size:
            # Remove oldest entries (simple FIFO)
            keys_to_remove = list(self.cache.keys())[:len(texts)]
            for key in keys_to_remove:
                del self.cache[key]
        
        for text, embedding in zip(texts, embeddings):
            cache_key = self._get_cache_key(text)
            self.cache[cache_key] = embedding
    
    def _get_cached_embeddings(self, texts: List[str]) -> tuple:
        """Get cached embeddings for texts."""
        cached_embeddings = {}
        uncached_texts = []
        
        for text in texts:
            cache_key = self._get_cache_key(text)
            if cache_key in self.cache:
                cached_embeddings[text] = self.cache[cache_key]
            else:
                uncached_texts.append(text)
        
        return cached_embeddings, uncached_texts
    
    def generate_embeddings(
        self, 
        texts: Union[str, List[str]], 
        batch_size: int = 32,
        show_progress: bool = True
    ) -> np.ndarray:
        """Generate embeddings for texts."""
        if isinstance(texts, str):
            texts = [texts]
        
        if not texts:
            return np.array([])
        
        # Check cache first
        cached_embeddings, uncached_texts = self._get_cached_embeddings(texts)
        
        # Generate embeddings for uncached texts
        if uncached_texts:
            if self.model_type == "openai":
                new_embeddings = self._generate_openai_embeddings(
                    uncached_texts, batch_size, show_progress
                )
            else:
                new_embeddings = self._generate_sentence_transformer_embeddings(
                    uncached_texts, batch_size, show_progress
                )
            
            # Update cache
            self._update_cache(uncached_texts, new_embeddings)
            
            # Add to cached embeddings
            for text, embedding in zip(uncached_texts, new_embeddings):
                cached_embeddings[text] = embedding
        
        # Return embeddings in original order
        return np.array([cached_embeddings[text] for text in texts])
    
    def _generate_openai_embeddings(
        self, 
        texts: List[str], 
        batch_size: int, 
        show_progress: bool
    ) -> np.ndarray:
        """Generate embeddings using OpenAI API."""
        embeddings = []
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            try:
                batch_embeddings = self.model.embed_documents(batch)
                embeddings.extend(batch_embeddings)
            except Exception as e:
                print(f"Error generating embeddings for batch {i//batch_size + 1}: {e}")
                # Fill with zeros if error occurs
                embeddings.extend([np.zeros(1536) for _ in batch])
        
        return np.array(embeddings)
    
    def _generate_sentence_transformer_embeddings(
        self, 
        texts: List[str], 
        batch_size: int, 
        show_progress: bool
    ) -> np.ndarray:
        """Generate embeddings using SentenceTransformer."""
        try:
            embeddings = self.model.encode(
                texts,
                batch_size=batch_size,
                show_progress_bar=show_progress,
                convert_to_numpy=True
            )
            return embeddings
        except Exception as e:
            print(f"Error generating embeddings: {e}")
            # Return zero embeddings as fallback
            return np.zeros((len(texts), self.model.get_sentence_embedding_dimension()))
    
    def get_embedding_dimension(self) -> int:
        """Get the dimension of embeddings."""
        if self.model_type == "openai":
            return 1536  # OpenAI text-embedding-3-small dimension
        else:
            return self.model.get_sentence_embedding_dimension()
    
    def clear_cache(self):
        """Clear the embedding cache."""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "cache_size": len(self.cache),
            "max_cache_size": self.cache_size,
            "model_name": self.model_name,
            "model_type": self.model_type
        }

