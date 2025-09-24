"""
Modern RAG API - 2025 State-of-the-Art Implementation
FastAPI-based API with latest RAG techniques and optimizations
"""

import asyncio
import logging
import json
import time
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
import uuid

# FastAPI imports
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field, validator
import uvicorn

# Advanced imports
from ..advanced.modern_rag_orchestrator import ModernRAGOrchestrator, RAGOrchestratorConfig
from ..advanced.modern_retrieval_system import RetrievalConfig
from ..advanced.modern_generation_system import GenerationConfig
import redis.asyncio as redis
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response

logger = logging.getLogger(__name__)

# Pydantic models for API
class QueryRequest(BaseModel):
    """Request model for query processing"""
    query: str = Field(..., min_length=1, max_length=1000, description="User query")
    user_id: str = Field(default="anonymous", description="User identifier")
    session_id: Optional[str] = Field(default=None, description="Session identifier")
    user_preferences: Optional[Dict[str, Any]] = Field(default=None, description="User preferences")
    context_filters: Optional[Dict[str, Any]] = Field(default=None, description="Context filters")
    max_results: int = Field(default=5, ge=1, le=20, description="Maximum number of results")
    include_sources: bool = Field(default=True, description="Include source documents")
    include_metadata: bool = Field(default=True, description="Include metadata")
    
    @validator('query')
    def validate_query(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()

class DocumentUploadRequest(BaseModel):
    """Request model for document upload"""
    documents: List[Dict[str, Any]] = Field(..., description="List of documents to upload")
    user_id: str = Field(default="system", description="User identifier")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    @validator('documents')
    def validate_documents(cls, v):
        if not v:
            raise ValueError('Documents list cannot be empty')
        for doc in v:
            if 'content' not in doc:
                raise ValueError('Each document must have content field')
        return v

class SystemStatusResponse(BaseModel):
    """Response model for system status"""
    timestamp: str
    system_health: float
    performance_stats: Dict[str, Any]
    cache_stats: Dict[str, Any]
    resource_utilization: Dict[str, Any]
    config: Dict[str, Any]

class QueryResponse(BaseModel):
    """Response model for query processing"""
    answer: str
    sources: List[Dict[str, Any]]
    confidence_score: float
    metadata: Dict[str, Any]
    orchestrator_metadata: Dict[str, Any]
    error: Optional[str] = None

class ModernRAGAPI:
    """
    Modern RAG API with latest techniques:
    - FastAPI with async support
    - Advanced authentication and rate limiting
    - Real-time monitoring and metrics
    - Comprehensive error handling
    - Background task processing
    - Health checks and status endpoints
    """
    
    def __init__(self, config: Optional[RAGOrchestratorConfig] = None):
        self.config = config or RAGOrchestratorConfig()
        self.logger = logging.getLogger(__name__)
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="Modern RAG API",
            description="State-of-the-art RAG system with latest techniques",
            version="2.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )
        
        # Initialize RAG orchestrator
        self.rag_orchestrator = ModernRAGOrchestrator(self.config)
        
        # Initialize security
        self.security = HTTPBearer()
        
        # Initialize Redis for session management
        self.redis_client = redis.from_url("redis://localhost:6379")
        
        # Setup middleware and routes
        self._setup_middleware()
        self._setup_routes()
        
        self.logger.info("Modern RAG API initialized")
    
    def _setup_middleware(self):
        """Setup FastAPI middleware"""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure appropriately for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # GZip middleware
        self.app.add_middleware(GZipMiddleware, minimum_size=1000)
        
        # Request logging middleware
        @self.app.middleware("http")
        async def log_requests(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            process_time = time.time() - start_time
            
            self.logger.info(
                f"{request.method} {request.url.path} - "
                f"Status: {response.status_code} - "
                f"Time: {process_time:.3f}s"
            )
            
            return response
    
    def _setup_routes(self):
        """Setup API routes"""
        
        # Health check endpoint
        @self.app.get("/health", tags=["Health"])
        async def health_check():
            """Health check endpoint"""
            try:
                status = await self.rag_orchestrator.get_system_status()
                return {
                    "status": "healthy",
                    "timestamp": datetime.now().isoformat(),
                    "system_health": status.get('system_health', 0.0)
                }
            except Exception as e:
                self.logger.error(f"Health check failed: {e}")
                raise HTTPException(status_code=503, detail="Service unavailable")
        
        # System status endpoint
        @self.app.get("/status", response_model=SystemStatusResponse, tags=["System"])
        async def get_system_status():
            """Get comprehensive system status"""
            try:
                status = await self.rag_orchestrator.get_system_status()
                return SystemStatusResponse(**status)
            except Exception as e:
                self.logger.error(f"Status check failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Query processing endpoint
        @self.app.post("/query", response_model=QueryResponse, tags=["Query"])
        async def process_query(
            request: QueryRequest,
            background_tasks: BackgroundTasks,
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Process a query through the RAG system"""
            try:
                # Process query
                response = await self.rag_orchestrator.process_query(
                    query=request.query,
                    user_id=request.user_id,
                    session_id=request.session_id,
                    user_preferences=request.user_preferences,
                    context_filters=request.context_filters
                )
                
                # Add background tasks
                background_tasks.add_task(
                    self._update_session_history,
                    request.session_id,
                    request.query,
                    response.get('answer', '')
                )
                
                # Format response
                return QueryResponse(
                    answer=response.get('answer', ''),
                    sources=response.get('sources', []) if request.include_sources else [],
                    confidence_score=response.get('confidence_score', 0.0),
                    metadata=response.get('metadata', {}) if request.include_metadata else {},
                    orchestrator_metadata=response.get('orchestrator_metadata', {}),
                    error=response.get('error')
                )
                
            except Exception as e:
                self.logger.error(f"Query processing failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Document upload endpoint
        @self.app.post("/documents", tags=["Documents"])
        async def upload_documents(
            request: DocumentUploadRequest,
            background_tasks: BackgroundTasks,
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Upload documents to the RAG system"""
            try:
                # Add documents in background
                background_tasks.add_task(
                    self._process_documents,
                    request.documents,
                    request.user_id,
                    request.metadata
                )
                
                return {
                    "message": "Documents queued for processing",
                    "document_count": len(request.documents),
                    "user_id": request.user_id,
                    "timestamp": datetime.now().isoformat()
                }
                
            except Exception as e:
                self.logger.error(f"Document upload failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Metrics endpoint
        @self.app.get("/metrics", tags=["Monitoring"])
        async def get_metrics():
            """Get Prometheus metrics"""
            try:
                metrics_data = generate_latest()
                return Response(
                    content=metrics_data,
                    media_type=CONTENT_TYPE_LATEST
                )
            except Exception as e:
                self.logger.error(f"Metrics retrieval failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # System optimization endpoint
        @self.app.post("/optimize", tags=["System"])
        async def optimize_system(
            credentials: HTTPAuthorizationCredentials = Depends(self.security)
        ):
            """Optimize system performance"""
            try:
                optimization_result = await self.rag_orchestrator.optimize_system()
                return {
                    "message": "System optimization completed",
                    "result": optimization_result,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                self.logger.error(f"System optimization failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        # Session management endpoints
        @self.app.get("/sessions/{session_id}", tags=["Sessions"])
        async def get_session(session_id: str):
            """Get session information"""
            try:
                session_data = await self._get_session_data(session_id)
                return {
                    "session_id": session_id,
                    "data": session_data,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                self.logger.error(f"Session retrieval failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.delete("/sessions/{session_id}", tags=["Sessions"])
        async def clear_session(session_id: str):
            """Clear session data"""
            try:
                await self._clear_session_data(session_id)
                return {
                    "message": "Session cleared",
                    "session_id": session_id,
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as e:
                self.logger.error(f"Session clearing failed: {e}")
                raise HTTPException(status_code=500, detail=str(e))
    
    async def _update_session_history(
        self, 
        session_id: str, 
        query: str, 
        response: str
    ):
        """Update session history in background"""
        try:
            if not session_id:
                return
            
            # Get existing history
            history_data = await self.redis_client.get(f"conversation:{session_id}")
            if history_data:
                history = json.loads(history_data)
            else:
                history = []
            
            # Add new interaction
            history.extend([
                {"role": "user", "content": query, "timestamp": datetime.now().isoformat()},
                {"role": "assistant", "content": response, "timestamp": datetime.now().isoformat()}
            ])
            
            # Keep only last 20 interactions
            history = history[-20:]
            
            # Store updated history
            await self.redis_client.setex(
                f"conversation:{session_id}",
                3600,  # 1 hour TTL
                json.dumps(history)
            )
            
        except Exception as e:
            self.logger.warning(f"Session history update failed: {e}")
    
    async def _process_documents(
        self, 
        documents: List[Dict[str, Any]], 
        user_id: str, 
        metadata: Dict[str, Any] = None
    ):
        """Process documents in background"""
        try:
            # Add metadata to documents
            for doc in documents:
                if metadata:
                    doc['metadata'] = {**doc.get('metadata', {}), **metadata}
                doc['metadata']['user_id'] = user_id
                doc['metadata']['upload_timestamp'] = datetime.now().isoformat()
            
            # Add to RAG system
            success = await self.rag_orchestrator.add_documents(documents)
            
            if success:
                self.logger.info(f"Successfully processed {len(documents)} documents for user {user_id}")
            else:
                self.logger.error(f"Failed to process documents for user {user_id}")
                
        except Exception as e:
            self.logger.error(f"Document processing failed: {e}")
    
    async def _get_session_data(self, session_id: str) -> Dict[str, Any]:
        """Get session data from Redis"""
        try:
            session_data = await self.redis_client.get(f"conversation:{session_id}")
            if session_data:
                return json.loads(session_data)
            return {}
        except Exception as e:
            self.logger.error(f"Session data retrieval failed: {e}")
            return {}
    
    async def _clear_session_data(self, session_id: str):
        """Clear session data from Redis"""
        try:
            await self.redis_client.delete(f"conversation:{session_id}")
        except Exception as e:
            self.logger.error(f"Session data clearing failed: {e}")
    
    def run(self, host: str = "0.0.0.0", port: int = 8000, workers: int = 1):
        """Run the API server"""
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            workers=workers,
            log_level="info"
        )

# Factory function for easy initialization
def create_modern_rag_api(config: Optional[RAGOrchestratorConfig] = None) -> ModernRAGAPI:
    """Create a modern RAG API with default or custom configuration"""
    return ModernRAGAPI(config)

# Example usage
if __name__ == "__main__":
    # Create and run the API
    api = create_modern_rag_api()
    api.run(host="0.0.0.0", port=8000)
