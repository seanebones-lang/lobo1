"""
Vector store implementation supporting multiple backends.
"""

import os
import uuid
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
import chromadb
from chromadb.config import Settings
import pinecone
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """Unified interface for vector storage operations."""
    
    def __init__(
        self, 
        vector_db_type: str = "chroma",
        persist_directory: str = "./chroma_db",
        collection_name: str = "documents",
        **kwargs
    ):
        self.vector_db_type = vector_db_type
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
        if vector_db_type == "chroma":
            self._init_chroma(persist_directory)
        elif vector_db_type == "pinecone":
            self._init_pinecone(**kwargs)
        elif vector_db_type == "qdrant":
            self._init_qdrant(**kwargs)
        else:
            raise ValueError(f"Unsupported vector database type: {vector_db_type}")
    
    def _init_chroma(self, persist_directory: str):
        """Initialize ChromaDB client."""
        try:
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            self.collection = self.client.get_or_create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"}
            )
            logger.info(f"ChromaDB initialized with collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error initializing ChromaDB: {e}")
            raise
    
    def _init_pinecone(self, api_key: str, environment: str, index_name: str = "rag-index"):
        """Initialize Pinecone client."""
        try:
            pinecone.init(api_key=api_key, environment=environment)
            self.index_name = index_name
            
            # Create index if it doesn't exist
            if index_name not in pinecone.list_indexes():
                pinecone.create_index(
                    name=index_name,
                    dimension=1536,  # OpenAI embedding dimension
                    metric="cosine"
                )
            
            self.collection = pinecone.Index(index_name)
            logger.info(f"Pinecone initialized with index: {index_name}")
        except Exception as e:
            logger.error(f"Error initializing Pinecone: {e}")
            raise
    
    def _init_qdrant(self, url: str = "http://localhost:6333", api_key: Optional[str] = None):
        """Initialize Qdrant client."""
        try:
            self.client = QdrantClient(url=url, api_key=api_key)
            self.collection = self.client.get_collection(self.collection_name)
            logger.info(f"Qdrant initialized with collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Error initializing Qdrant: {e}")
            # Create collection if it doesn't exist
            try:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
                )
                self.collection = self.client.get_collection(self.collection_name)
                logger.info(f"Created new Qdrant collection: {self.collection_name}")
            except Exception as create_error:
                logger.error(f"Error creating Qdrant collection: {create_error}")
                raise
    
    def add_documents(
        self, 
        documents: List[str], 
        embeddings: np.ndarray, 
        metadatas: Optional[List[Dict[str, Any]]] = None,
        ids: Optional[List[str]] = None
    ) -> List[str]:
        """Add documents to the vector store."""
        if not documents or len(documents) == 0:
            return []
        
        if ids is None:
            ids = [str(uuid.uuid4()) for _ in documents]
        
        if metadatas is None:
            metadatas = [{} for _ in documents]
        
        try:
            if self.vector_db_type == "chroma":
                return self._add_to_chroma(documents, embeddings, metadatas, ids)
            elif self.vector_db_type == "pinecone":
                return self._add_to_pinecone(documents, embeddings, metadatas, ids)
            elif self.vector_db_type == "qdrant":
                return self._add_to_qdrant(documents, embeddings, metadatas, ids)
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            raise
    
    def _add_to_chroma(self, documents, embeddings, metadatas, ids):
        """Add documents to ChromaDB."""
        self.collection.add(
            documents=documents,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            ids=ids
        )
        return ids
    
    def _add_to_pinecone(self, documents, embeddings, metadatas, ids):
        """Add documents to Pinecone."""
        vectors = []
        for i, (doc, embedding, metadata, doc_id) in enumerate(zip(documents, embeddings, metadatas, ids)):
            vectors.append({
                "id": doc_id,
                "values": embedding.tolist(),
                "metadata": {**metadata, "text": doc}
            })
        
        # Upsert in batches
        batch_size = 100
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.collection.upsert(vectors=batch)
        
        return ids
    
    def _add_to_qdrant(self, documents, embeddings, metadatas, ids):
        """Add documents to Qdrant."""
        points = []
        for i, (doc, embedding, metadata, doc_id) in enumerate(zip(documents, embeddings, metadatas, ids)):
            points.append(PointStruct(
                id=doc_id,
                vector=embedding.tolist(),
                payload={**metadata, "text": doc}
            ))
        
        # Insert in batches
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
        
        return ids
    
    def search(
        self, 
        query_embedding: np.ndarray, 
        n_results: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Search for similar documents."""
        try:
            if self.vector_db_type == "chroma":
                return self._search_chroma(query_embedding, n_results, filter_metadata)
            elif self.vector_db_type == "pinecone":
                return self._search_pinecone(query_embedding, n_results, filter_metadata)
            elif self.vector_db_type == "qdrant":
                return self._search_qdrant(query_embedding, n_results, filter_metadata)
        except Exception as e:
            logger.error(f"Error searching: {e}")
            raise
    
    def _search_chroma(self, query_embedding, n_results, filter_metadata):
        """Search in ChromaDB."""
        where_clause = filter_metadata if filter_metadata else None
        
        results = self.collection.query(
            query_embeddings=[query_embedding.tolist()],
            n_results=n_results,
            where=where_clause
        )
        
        return {
            "documents": results["documents"][0] if results["documents"] else [],
            "metadatas": results["metadatas"][0] if results["metadatas"] else [],
            "distances": results["distances"][0] if results["distances"] else [],
            "ids": results["ids"][0] if results["ids"] else []
        }
    
    def _search_pinecone(self, query_embedding, n_results, filter_metadata):
        """Search in Pinecone."""
        results = self.collection.query(
            vector=query_embedding.tolist(),
            top_k=n_results,
            include_metadata=True,
            filter=filter_metadata
        )
        
        documents = []
        metadatas = []
        distances = []
        ids = []
        
        for match in results.matches:
            documents.append(match.metadata.get("text", ""))
            metadatas.append({k: v for k, v in match.metadata.items() if k != "text"})
            distances.append(1 - match.score)  # Convert similarity to distance
            ids.append(match.id)
        
        return {
            "documents": documents,
            "metadatas": metadatas,
            "distances": distances,
            "ids": ids
        }
    
    def _search_qdrant(self, query_embedding, n_results, filter_metadata):
        """Search in Qdrant."""
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=n_results,
            query_filter=filter_metadata
        )
        
        documents = []
        metadatas = []
        distances = []
        ids = []
        
        for result in results:
            documents.append(result.payload.get("text", ""))
            metadatas.append({k: v for k, v in result.payload.items() if k != "text"})
            distances.append(1 - result.score)  # Convert similarity to distance
            ids.append(str(result.id))
        
        return {
            "documents": documents,
            "metadatas": metadatas,
            "distances": distances,
            "ids": ids
        }
    
    def delete_documents(self, ids: List[str]) -> bool:
        """Delete documents by IDs."""
        try:
            if self.vector_db_type == "chroma":
                self.collection.delete(ids=ids)
            elif self.vector_db_type == "pinecone":
                self.collection.delete(ids=ids)
            elif self.vector_db_type == "qdrant":
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=ids
                )
            return True
        except Exception as e:
            logger.error(f"Error deleting documents: {e}")
            return False
    
    def get_collection_info(self) -> Dict[str, Any]:
        """Get information about the collection."""
        try:
            if self.vector_db_type == "chroma":
                count = self.collection.count()
                return {"count": count, "type": "chroma"}
            elif self.vector_db_type == "pinecone":
                stats = self.collection.describe_index_stats()
                return {"count": stats.total_vector_count, "type": "pinecone"}
            elif self.vector_db_type == "qdrant":
                info = self.client.get_collection(self.collection_name)
                return {"count": info.points_count, "type": "qdrant"}
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return {"count": 0, "type": self.vector_db_type, "error": str(e)}

