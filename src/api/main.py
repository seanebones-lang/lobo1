"""
FastAPI main application with all endpoints.
"""

import os
import time
import uuid
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn

from .models import (
    QueryRequest, QueryResponse, StreamingChunk, DocumentUploadRequest,
    DocumentUploadResponse, HealthResponse, StatsResponse, ErrorResponse,
    ConversationRequest, ConversationResponse, BatchQueryRequest, BatchQueryResponse
)
from ..generation.rag_generator import RAGGenerator
from ..generation.llm_manager import LLMManager
from ..generation.prompt_manager import PromptManager
from ..retrieval.embedding_generator import EmbeddingGenerator
from ..retrieval.vector_store import VectorStore
from ..retrieval.hybrid_search import HybridRetriever
from ..retrieval.reranker import Reranker, CohereReranker
from ..data_processing.document_processor import DocumentProcessor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Advanced RAG System API",
    description="A comprehensive RAG (Retrieval Augmented Generation) system with hybrid search, reranking, and multiple LLM support",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Global variables for components
rag_generator: Optional[RAGGenerator] = None
start_time = time.time()

# Dependency to get API key (optional authentication)
def get_api_key(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """Get API key from authorization header."""
    if credentials:
        return credentials.credentials
    return None

# Dependency to get RAG generator
def get_rag_generator() -> RAGGenerator:
    """Get the RAG generator instance."""
    if rag_generator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG system not initialized"
        )
    return rag_generator

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup."""
    global rag_generator
    
    try:
        logger.info("Initializing RAG system...")
        
        # Load environment variables
        openai_api_key = os.getenv("OPENAI_API_KEY")
        anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        cohere_api_key = os.getenv("COHERE_API_KEY")
        
        # Initialize components
        llm_manager = LLMManager(
            openai_api_key=openai_api_key,
            anthropic_api_key=anthropic_api_key
        )
        
        embedding_generator = EmbeddingGenerator(
            model_name=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
            openai_api_key=openai_api_key
        )
        
        vector_store = VectorStore(
            vector_db_type=os.getenv("VECTOR_DB_TYPE", "chroma"),
            persist_directory=os.getenv("VECTOR_DB_PATH", "./chroma_db"),
            collection_name=os.getenv("COLLECTION_NAME", "documents")
        )
        
        # Initialize hybrid retriever (will be updated when documents are added)
        hybrid_retriever = HybridRetriever(
            vector_store=vector_store,
            documents=[],  # Will be populated when documents are added
            alpha=float(os.getenv("VECTOR_WEIGHT", "0.7")),
            bm25_weight=float(os.getenv("BM25_WEIGHT", "0.3"))
        )
        
        # Initialize reranker if API key is available
        reranker = None
        if cohere_api_key:
            try:
                reranker = CohereReranker(api_key=cohere_api_key)
                logger.info("Cohere reranker initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Cohere reranker: {e}")
        else:
            try:
                reranker = Reranker()
                logger.info("Local reranker initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize local reranker: {e}")
        
        # Initialize RAG generator
        rag_generator = RAGGenerator(
            llm_manager=llm_manager,
            embedding_generator=embedding_generator,
            hybrid_retriever=hybrid_retriever,
            reranker=reranker,
            use_reranking=reranker is not None
        )
        
        logger.info("RAG system initialized successfully")
        
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        raise

@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint with basic information."""
    return {
        "message": "Advanced RAG System API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        rag_gen = get_rag_generator()
        stats = rag_gen.get_stats()
        
        return HealthResponse(
            status="healthy",
            version="1.0.0",
            timestamp=datetime.utcnow().isoformat(),
            components={
                "llm": "healthy" if stats["llm_stats"]["available_models"] else "unhealthy",
                "embeddings": "healthy" if stats["embedding_stats"]["cache_size"] >= 0 else "unhealthy",
                "retriever": "healthy" if stats["retriever_stats"]["total_documents"] >= 0 else "unhealthy",
                "vector_store": "healthy"
            }
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            version="1.0.0",
            timestamp=datetime.utcnow().isoformat(),
            components={"error": str(e)}
        )

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get system statistics."""
    try:
        rag_gen = get_rag_generator()
        stats = rag_gen.get_stats()
        
        return StatsResponse(
            llm_stats=stats["llm_stats"],
            embedding_stats=stats["embedding_stats"],
            retriever_stats=stats["retriever_stats"],
            vector_store_info=stats.get("vector_store_info", {}),
            uptime=time.time() - start_time
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query", response_model=QueryResponse)
async def query_rag_system(
    request: QueryRequest,
    rag_gen: RAGGenerator = Depends(get_rag_generator)
):
    """Query the RAG system."""
    try:
        result = rag_gen.generate_answer(
            query=request.question,
            prompt_type=request.prompt_type.value,
            top_k=request.top_k,
            rerank_top_k=request.rerank_top_k,
            include_sources=request.include_sources,
            system_role=request.system_role.value,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            model_name=request.model_name
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in query endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/stream")
async def query_rag_system_stream(
    request: QueryRequest,
    rag_gen: RAGGenerator = Depends(get_rag_generator)
):
    """Query the RAG system with streaming response."""
    try:
        def generate_stream():
            for chunk in rag_gen.generate_streaming_answer(
                query=request.question,
                prompt_type=request.prompt_type.value,
                top_k=request.top_k,
                rerank_top_k=request.rerank_top_k,
                system_role=request.system_role.value,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                model_name=request.model_name
            ):
                yield f"data: {chunk.json()}\n\n"
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/plain",
            headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
        )
        
    except Exception as e:
        logger.error(f"Error in streaming query endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/conversation", response_model=ConversationResponse)
async def conversational_query(
    request: ConversationRequest,
    rag_gen: RAGGenerator = Depends(get_rag_generator)
):
    """Handle conversational queries with context."""
    try:
        # Convert conversation history to string format
        history_str = "\n".join([
            f"Human: {msg.get('human', '')}\nAssistant: {msg.get('assistant', '')}"
            for msg in request.conversation_history
        ])
        
        result = rag_gen.generate_answer(
            query=request.message,
            prompt_type="conversation",
            top_k=request.top_k,
            system_role=request.system_role.value,
            temperature=request.temperature
        )
        
        return ConversationResponse(
            response=result["answer"],
            conversation_id=str(uuid.uuid4()),
            sources=result["sources"],
            confidence=result["confidence"],
            processing_time=result["total_time"]
        )
        
    except Exception as e:
        logger.error(f"Error in conversation endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query/batch", response_model=BatchQueryResponse)
async def batch_query(
    request: BatchQueryRequest,
    rag_gen: RAGGenerator = Depends(get_rag_generator)
):
    """Process multiple queries in batch."""
    try:
        results = []
        start_time = time.time()
        success_count = 0
        error_count = 0
        
        for query in request.queries:
            try:
                result = rag_gen.generate_answer(
                    query=query,
                    prompt_type=request.prompt_type.value,
                    top_k=request.top_k,
                    include_sources=request.include_sources
                )
                results.append(QueryResponse(**result))
                success_count += 1
            except Exception as e:
                logger.error(f"Error processing query '{query}': {e}")
                error_count += 1
                results.append(QueryResponse(
                    answer=f"Error processing query: {str(e)}",
                    sources=[],
                    confidence=0.0,
                    retrieval_time=0.0,
                    generation_time=0.0,
                    total_time=0.0,
                    error=str(e)
                ))
        
        return BatchQueryResponse(
            results=results,
            total_processing_time=time.time() - start_time,
            success_count=success_count,
            error_count=error_count
        )
        
    except Exception as e:
        logger.error(f"Error in batch query endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/documents/upload", response_model=DocumentUploadResponse)
async def upload_documents(
    request: DocumentUploadRequest,
    background_tasks: BackgroundTasks,
    rag_gen: RAGGenerator = Depends(get_rag_generator)
):
    """Upload and process documents."""
    try:
        start_time = time.time()
        
        # Initialize document processor
        processor = DocumentProcessor()
        
        # Process documents
        documents = processor.process_documents(
            file_paths=request.file_paths,
            chunk_method=request.chunk_method,
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap
        )
        
        if not documents:
            return DocumentUploadResponse(
                success=False,
                documents_processed=0,
                chunks_created=0,
                processing_time=time.time() - start_time,
                error="No documents could be processed"
            )
        
        # Extract texts and metadata
        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        
        # Generate embeddings
        embeddings = rag_gen.embedding_generator.generate_embeddings(texts)
        
        # Add to vector store
        ids = rag_gen.hybrid_retriever.vector_store.add_documents(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        
        # Update hybrid retriever with new documents
        rag_gen.hybrid_retriever.update_documents(texts)
        
        return DocumentUploadResponse(
            success=True,
            documents_processed=len(request.file_paths),
            chunks_created=len(documents),
            processing_time=time.time() - start_time
        )
        
    except Exception as e:
        logger.error(f"Error in document upload: {e}")
        return DocumentUploadResponse(
            success=False,
            documents_processed=0,
            chunks_created=0,
            processing_time=time.time() - start_time,
            error=str(e)
        )

@app.get("/models")
async def get_available_models():
    """Get available models."""
    try:
        rag_gen = get_rag_generator()
        return {
            "llm_models": rag_gen.llm_manager.get_available_models(),
            "embedding_model": rag_gen.embedding_generator.model_name,
            "prompt_types": rag_gen.prompt_manager.get_available_prompts()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/prompts")
async def get_available_prompts():
    """Get available prompt types and their metadata."""
    try:
        rag_gen = get_rag_generator()
        prompts = {}
        for prompt_type in rag_gen.prompt_manager.get_available_prompts():
            prompts[prompt_type] = rag_gen.prompt_manager.get_prompt_metadata(prompt_type)
        return prompts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(
        "src.api.main:app",
        host=os.getenv("APP_HOST", "0.0.0.0"),
        port=int(os.getenv("APP_PORT", "8000")),
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )

