"""
LOBO 1.0 - Intelligent RAG System API
FastAPI-based API with all features enabled.
"""

import asyncio
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
import uvicorn

# Import the LOBO 1.0 RAG system
from .core import LOBORAGSystem, SystemConfig

# Initialize the RAG system
rag_system = None

class QueryRequest(BaseModel):
    query: str = Field(..., description="The user's query")
    context: Optional[Dict] = Field(None, description="Additional context for the query")
    options: Optional[Dict] = Field(None, description="Query options and preferences")
    user_id: Optional[str] = Field(None, description="User ID for personalization")
    session_id: Optional[str] = Field(None, description="Session ID for conversation tracking")

class QueryResponse(BaseModel):
    answer: str = Field(..., description="The generated answer")
    sources: List[Dict] = Field(default=[], description="Source documents used")
    metadata: Dict = Field(default={}, description="Response metadata")
    performance: Dict = Field(default={}, description="Performance metrics")
    cached: bool = Field(default=False, description="Whether response was cached")
    llm_used: str = Field(default="unknown", description="LLM model used")
    retrieval_strategies: List[str] = Field(default=[], description="Retrieval strategies used")

class FeedbackRequest(BaseModel):
    query: str = Field(..., description="Original query")
    response: str = Field(..., description="System response")
    rating: Optional[float] = Field(None, description="User rating (0-1)")
    feedback_type: str = Field(default="explicit_rating", description="Type of feedback")
    corrections: Optional[Dict] = Field(None, description="Corrections or improvements")
    user_id: str = Field(..., description="User ID")

class SystemStatusResponse(BaseModel):
    system_health: Dict
    performance_metrics: Dict
    component_status: Dict
    resource_utilization: Dict
    configuration: Dict

class AnalyticsResponse(BaseModel):
    insights: Dict
    trends: Dict
    recommendations: List[str]
    time_range: str

def create_app(config_path: str = None) -> FastAPI:
    """Create the FastAPI application"""
    
    global rag_system
    
    # Initialize the LOBO 1.0 RAG system
    rag_system = LOBORAGSystem(config_path)
    
    app = FastAPI(
        title="LOBO 1.0 - Intelligent RAG System API",
        description="The Alpha of RAG Systems - Complete with every advanced feature",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Security
    security = HTTPBearer()
    
    # Authentication dependency
    async def authenticate_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Authenticate user (mock implementation)"""
        # In production, implement proper JWT validation
        return {
            'user_id': 'demo_user',
            'role': 'user',
            'permissions': ['read', 'write']
        }
    
    # Admin authentication
    async def authenticate_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Authenticate admin user"""
        user_context = await authenticate_user(credentials)
        if user_context.get('role') != 'admin':
            raise HTTPException(status_code=403, detail="Admin access required")
        return user_context
    
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "🐺 LOBO 1.0 - Intelligent RAG System API",
            "version": "1.0.0",
            "status": "operational",
            "pack_features": [
                "🐺 Pack Search",
                "🐺 Multi-Modal Processing", 
                "🐺 Cross-Pack RAG",
                "🐺 Pack Security",
                "🐺 Pack Monitoring",
                "🐺 Pack Learning"
            ]
        }
    
    @app.post("/query", response_model=QueryResponse)
    async def query_rag_system(
        request: QueryRequest,
        background_tasks: BackgroundTasks,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Main query endpoint with all features enabled"""
        
        try:
            # Authenticate and authorize
            user_context = await authenticate_user(credentials)
            
            # Add user context to request
            user_context.update({
                'user_id': request.user_id or user_context.get('user_id', 'anonymous'),
                'session_id': request.session_id,
                'domain': request.context.get('domain', 'general') if request.context else 'general'
            })
            
            # Process query with all features
            start_time = datetime.now()
            
            result = await rag_system.process_query(
                query=request.query,
                user_context=user_context,
                options=request.options
            )
            
            latency = (datetime.now() - start_time).total_seconds()
            
            # Track interaction for analytics
            background_tasks.add_task(
                rag_system.monitoring_system.track_interaction,
                {
                    'query': request.query,
                    'response': result,
                    'user_context': user_context,
                    'latency': latency,
                    'timestamp': datetime.now()
                }
            )
            
            # Audit logging
            if rag_system.config.audit_logging:
                background_tasks.add_task(
                    rag_system.audit_system.log_interaction,
                    {
                        'query': request.query,
                        'response': result,
                        'user_context': user_context,
                        'security_checks': result.get('security_checks', [])
                    }
                )
            
            return QueryResponse(
                answer=result['answer'],
                sources=result.get('sources', []),
                metadata=result.get('metadata', {}),
                performance={'latency': latency, 'llm_used': result.get('llm_used')},
                cached=result.get('cached', False),
                llm_used=result.get('llm_used', 'unknown'),
                retrieval_strategies=result.get('retrieval_strategies_used', [])
            )
            
        except Exception as e:
            # Track error
            if rag_system.config.enable_monitoring:
                rag_system.monitoring_system.error_rate.inc()
            
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/feedback")
    async def submit_feedback(
        request: FeedbackRequest,
        background_tasks: BackgroundTasks,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Submit feedback for continuous learning"""
        
        try:
            user_context = await authenticate_user(credentials)
            
            feedback_data = {
                'query': request.query,
                'response': request.response,
                'rating': request.rating,
                'type': request.feedback_type,
                'corrections': request.corrections,
                'user_id': request.user_id,
                'timestamp': datetime.now()
            }
            
            # Process feedback for learning
            if rag_system.config.enable_continuous_learning:
                background_tasks.add_task(
                    rag_system.learning_system.process_feedback_loop,
                    feedback_data
                )
            
            return {
                "message": "Feedback submitted successfully",
                "feedback_id": f"feedback_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "learning_enabled": rag_system.config.enable_continuous_learning
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/status", response_model=SystemStatusResponse)
    async def get_system_status(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Get comprehensive system status"""
        
        try:
            user_context = await authenticate_user(credentials)
            
            status = await rag_system.get_system_status()
            
            return SystemStatusResponse(
                system_health=status['system_health'],
                performance_metrics=status['performance_metrics'],
                component_status=status['component_status'],
                resource_utilization=status['resource_utilization'],
                configuration=status['configuration']
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/admin/dashboard")
    async def get_system_dashboard(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Get real-time system dashboard (admin only)"""
        
        try:
            user_context = await authenticate_admin(credentials)
            
            dashboard_data = await rag_system.monitoring_system.generate_real_time_dashboard()
            
            return dashboard_data
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/admin/analytics", response_model=AnalyticsResponse)
    async def get_analytics(
        time_range: str = "7d",
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Get advanced analytics (admin only)"""
        
        try:
            user_context = await authenticate_admin(credentials)
            
            insights = await rag_system.analytics_engine.generate_insights(time_range)
            
            return AnalyticsResponse(
                insights=insights,
                trends=insights.get('performance_insights', {}),
                recommendations=insights.get('recommendations', []),
                time_range=time_range
            )
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/admin/feedback")
    async def submit_admin_feedback(
        feedback: Dict,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Submit admin feedback for system improvement"""
        
        try:
            user_context = await authenticate_admin(credentials)
            
            improvement_report = await rag_system.learning_system.process_feedback_loop(feedback)
            
            return improvement_report
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        try:
            # Basic health check
            health_status = await rag_system.get_system_status()
            
            return {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "components": health_status['component_status']
            }
            
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={
                    "status": "unhealthy",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
            )
    
    @app.get("/metrics")
    async def get_metrics(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Get system metrics"""
        
        try:
            user_context = await authenticate_user(credentials)
            
            metrics = await rag_system.monitoring_system.get_current_metrics()
            
            return metrics
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/config")
    async def get_configuration(credentials: HTTPAuthorizationCredentials = Depends(security)):
        """Get system configuration"""
        
        try:
            user_context = await authenticate_user(credentials)
            
            return {
                "configuration": rag_system.config.__dict__,
                "features_enabled": {
                    "hybrid_search": rag_system.config.enable_hybrid_search,
                    "reranking": rag_system.config.enable_reranking,
                    "multimodal": rag_system.config.enable_multimodal,
                    "federation": rag_system.config.enable_federation,
                    "caching": rag_system.config.enable_caching,
                    "monitoring": rag_system.config.enable_monitoring,
                    "security": rag_system.config.enable_security,
                    "continuous_learning": rag_system.config.enable_continuous_learning
                }
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/admin/ab-test")
    async def create_ab_test(
        test_config: Dict,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Create A/B test (admin only)"""
        
        try:
            user_context = await authenticate_admin(credentials)
            
            if not rag_system.config.enable_ab_testing:
                raise HTTPException(status_code=400, detail="A/B testing not enabled")
            
            # Create A/B test
            test_id = await rag_system.analytics_engine.ab_test_manager.create_test(test_config)
            
            return {
                "test_id": test_id,
                "status": "created",
                "config": test_config
            }
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/admin/ab-test/{test_id}")
    async def get_ab_test_results(
        test_id: str,
        credentials: HTTPAuthorizationCredentials = Depends(security)
    ):
        """Get A/B test results (admin only)"""
        
        try:
            user_context = await authenticate_admin(credentials)
            
            report = await rag_system.analytics_engine.generate_ab_test_report(test_id)
            
            return report
            
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        """Global exception handler"""
        
        # Log error
        print(f"❌ Unhandled exception: {exc}")
        
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(exc),
                "timestamp": datetime.now().isoformat()
            }
        )
    
    return app

def run_server(host: str = "0.0.0.0", port: int = 8000, config_path: str = None):
    """Run the API server"""
    
    app = create_app(config_path)
    
    print(f"🐺 Starting LOBO 1.0 - Intelligent RAG System API on {host}:{port}")
    print(f"📚 Pack documentation available at http://{host}:{port}/docs")
    print(f"🔍 Pack health check available at http://{host}:{port}/health")
    
    uvicorn.run(app, host=host, port=port, log_level="info")

if __name__ == "__main__":
    run_server()
