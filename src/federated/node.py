"""
Federated Node Implementation
Individual federated nodes that can be deployed separately.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import asyncio
import hashlib
import json
from datetime import datetime
import aiohttp
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

@dataclass
class FederatedNode:
    """Represents a federated node in the network"""
    node_id: str
    endpoint: str
    data_domain: str
    capabilities: List[str]
    privacy_level: str  # 'public', 'confidential', 'restricted'
    latency: float
    available: bool = True

class QueryRequest(BaseModel):
    query: str
    user_context: Dict[str, Any]
    limit: int = 10

class QueryResponse(BaseModel):
    documents: List[Dict[str, Any]]
    result_count: int
    node_id: str
    domain: str
    confidence: float
    success: bool
    error: Optional[str] = None

class FederatedNodeServer:
    """Individual federated node that can be deployed separately"""
    
    def __init__(self, node_config: Dict):
        self.node_id = node_config['node_id']
        self.data_domain = node_config['data_domain']
        self.privacy_level = node_config['privacy_level']
        self.capabilities = node_config.get('capabilities', ['basic_search'])
        
        # Local RAG system for this node
        self.local_rag = LocalRAGSystem(node_config.get('vector_db_path', './local_vector_db'))
        self.access_control = AccessControlManager(node_config.get('access_rules', {}))
        self.query_logger = QueryLogger()
        
        # FastAPI app for the node
        self.app = FastAPI(title=f"Federated Node: {self.node_id}")
        self.setup_routes()
    
    def setup_routes(self):
        """Setup FastAPI routes for the federated node"""
        
        @self.app.get("/health")
        async def health_check():
            return {
                "status": "healthy",
                "node_id": self.node_id,
                "domain": self.data_domain,
                "capabilities": self.capabilities,
                "timestamp": datetime.now().isoformat()
            }
        
        @self.app.post("/search", response_model=QueryResponse)
        async def handle_search(request: QueryRequest):
            """Handle incoming query from federated orchestrator"""
            return await self.handle_query(request.query, request.user_context, request.limit)
        
        @self.app.get("/info")
        async def get_node_info():
            """Get node information"""
            return {
                "node_id": self.node_id,
                "data_domain": self.data_domain,
                "capabilities": self.capabilities,
                "privacy_level": self.privacy_level,
                "available": True
            }
    
    async def handle_query(self, query: str, user_context: Dict, limit: int = 10) -> QueryResponse:
        """Handle incoming query from federated orchestrator"""
        
        try:
            # Step 1: Validate access rights
            if not await self.access_control.check_access(user_context, query):
                return QueryResponse(
                    documents=[],
                    result_count=0,
                    node_id=self.node_id,
                    domain=self.data_domain,
                    confidence=0.0,
                    success=False,
                    error="Access denied"
                )
            
            # Step 2: Log query for auditing
            await self.query_logger.log_query(query, user_context)
            
            # Step 3: Execute local search
            results = await self.local_rag.search(
                query=query,
                filters=user_context.get('filters', {}),
                limit=limit
            )
            
            # Step 4: Apply local privacy transformations
            sanitized_results = self.apply_local_privacy(results, user_context)
            
            # Step 5: Calculate confidence
            confidence = self.calculate_local_confidence(results, query)
            
            return QueryResponse(
                documents=sanitized_results,
                result_count=len(sanitized_results),
                node_id=self.node_id,
                domain=self.data_domain,
                confidence=confidence,
                success=True
            )
            
        except Exception as e:
            return QueryResponse(
                documents=[],
                result_count=0,
                node_id=self.node_id,
                domain=self.data_domain,
                confidence=0.0,
                success=False,
                error=str(e)
            )
    
    def apply_local_privacy(self, results: List[Dict], user_context: Dict) -> List[Dict]:
        """Apply node-specific privacy rules to results"""
        sanitized_results = []
        
        for doc in results:
            sanitized_doc = doc.copy()
            
            # Remove sensitive fields based on privacy level
            if self.privacy_level == 'confidential':
                if 'sensitive_fields' in sanitized_doc.get('metadata', {}):
                    del sanitized_doc['metadata']['sensitive_fields']
            
            elif self.privacy_level == 'restricted':
                # Only return minimal information
                sanitized_doc = {
                    'content': self.summarize_content(doc['content']),
                    'metadata': {'source': f'restricted_{self.node_id}'},
                    'score': doc.get('score', 0)
                }
            
            sanitized_results.append(sanitized_doc)
        
        return sanitized_results
    
    def summarize_content(self, content: str) -> str:
        """Summarize content for restricted privacy nodes"""
        # Simple summarization - in practice, use proper summarization
        sentences = content.split('.')
        return '.'.join(sentences[:2]) + '.' if len(sentences) > 2 else content
    
    def calculate_local_confidence(self, results: List[Dict], query: str) -> float:
        """Calculate confidence score for local results"""
        if not results:
            return 0.0
        
        # Simple confidence calculation based on result quality
        avg_score = sum(doc.get('score', 0) for doc in results) / len(results)
        result_count_factor = min(1.0, len(results) / 10)  # More results = higher confidence
        
        return (avg_score + result_count_factor) / 2

class LocalRAGSystem:
    """Local RAG system for each federated node"""
    
    def __init__(self, vector_db_path: str):
        self.vector_db_path = vector_db_path
        # In a real implementation, this would load the actual vector database
        self.sample_documents = self.load_sample_documents()
    
    def load_sample_documents(self) -> List[Dict]:
        """Load sample documents for demonstration"""
        return [
            {
                'content': 'This is a sample legal document about data privacy regulations.',
                'metadata': {'type': 'legal', 'source': 'legal_database'},
                'score': 0.9
            },
            {
                'content': 'Medical research shows that early detection improves patient outcomes.',
                'metadata': {'type': 'medical', 'source': 'medical_journal'},
                'score': 0.8
            },
            {
                'content': 'Software engineering best practices include code reviews and testing.',
                'metadata': {'type': 'technical', 'source': 'tech_blog'},
                'score': 0.7
            }
        ]
    
    async def search(self, query: str, filters: Dict, limit: int = 10) -> List[Dict]:
        """Execute search on local node's data"""
        
        # Simple keyword matching for demonstration
        query_lower = query.lower()
        matching_docs = []
        
        for doc in self.sample_documents:
            content_lower = doc['content'].lower()
            
            # Simple relevance scoring
            relevance_score = 0.0
            query_words = query_lower.split()
            
            for word in query_words:
                if word in content_lower:
                    relevance_score += 0.1
            
            if relevance_score > 0:
                doc_copy = doc.copy()
                doc_copy['score'] = min(1.0, relevance_score)
                matching_docs.append(doc_copy)
        
        # Sort by relevance and return top results
        matching_docs.sort(key=lambda x: x['score'], reverse=True)
        return matching_docs[:limit]

class AccessControlManager:
    """Manage access control for federated nodes"""
    
    def __init__(self, access_rules: Dict):
        self.access_rules = access_rules
        self.default_rules = {
            'public': ['read'],
            'confidential': ['read', 'search'],
            'restricted': ['search']
        }
    
    async def check_access(self, user_context: Dict, query: str) -> bool:
        """Check if user has access to query this node"""
        
        # Simple access control for demonstration
        user_role = user_context.get('role', 'guest')
        required_permissions = self.access_rules.get('required_permissions', ['read'])
        
        # Check if user role has required permissions
        role_permissions = {
            'admin': ['read', 'write', 'search', 'delete'],
            'user': ['read', 'search'],
            'guest': ['read']
        }
        
        user_permissions = role_permissions.get(user_role, ['read'])
        
        return any(perm in user_permissions for perm in required_permissions)

class QueryLogger:
    """Log queries for auditing and analytics"""
    
    def __init__(self):
        self.query_log = []
    
    async def log_query(self, query: str, user_context: Dict):
        """Log query for auditing"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'query': query[:100],  # Truncate for privacy
            'user_id': user_context.get('user_id', 'anonymous'),
            'domain': user_context.get('domain', 'unknown')
        }
        
        self.query_log.append(log_entry)
        
        # Keep only last 1000 entries
        if len(self.query_log) > 1000:
            self.query_log = self.query_log[-1000:]
    
    def get_query_stats(self) -> Dict:
        """Get query statistics"""
        if not self.query_log:
            return {'total_queries': 0}
        
        return {
            'total_queries': len(self.query_log),
            'unique_users': len(set(entry['user_id'] for entry in self.query_log)),
            'domains': list(set(entry['domain'] for entry in self.query_log))
        }
