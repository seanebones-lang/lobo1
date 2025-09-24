"""
Federated RAG Orchestrator
Core orchestrator for managing federated RAG operations across multiple nodes.
"""

from typing import Dict, List, Optional, Any
import asyncio
from dataclasses import dataclass
import hashlib
import json
import time
from datetime import datetime
import aiohttp
import numpy as np

from .node import FederatedNode
from .privacy import PrivacyManager
from .aggregation import FederatedResultAggregator
from .management import NodeHealthChecker

@dataclass
class QueryAnalysis:
    domain: str
    privacy_requirements: str
    required_capabilities: List[str]
    max_nodes: int
    ranking_strategy: str
    user_context: Dict

class FederatedRAGOrchestrator:
    """Main orchestrator for federated RAG operations"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.nodes: Dict[str, FederatedNode] = {}
        self.query_router = QueryRouter()
        self.result_aggregator = FederatedResultAggregator()
        self.privacy_manager = PrivacyManager()
        self.performance_monitor = NodeHealthChecker()
        self.session = None
        
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def register_node(self, node: FederatedNode) -> bool:
        """Register a new federated node"""
        try:
            self.nodes[node.node_id] = node
            await self.health_check_node(node)
            print(f"✅ Registered node: {node.node_id} ({node.data_domain})")
            return True
        except Exception as e:
            print(f"❌ Failed to register node {node.node_id}: {e}")
            return False
    
    async def health_check_node(self, node: FederatedNode) -> bool:
        """Check if a node is healthy and responsive"""
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()
                
            start_time = time.time()
            async with self.session.get(f"{node.endpoint}/health", timeout=5) as response:
                latency = time.time() - start_time
                is_healthy = response.status == 200
                
                if is_healthy:
                    node.latency = latency
                    node.available = True
                    print(f"✅ Node {node.node_id} is healthy (latency: {latency:.3f}s)")
                else:
                    node.available = False
                    print(f"❌ Node {node.node_id} health check failed")
                
                return is_healthy
                
        except Exception as e:
            node.available = False
            print(f"❌ Node {node.node_id} health check error: {e}")
            return False
    
    async def federated_search(self, query: str, user_context: Dict) -> Dict:
        """Execute federated search across multiple nodes"""
        
        print(f"🔍 Starting federated search for: '{query}'")
        
        # Step 1: Analyze query and determine node routing
        query_analysis = await self.analyze_query_for_federation(query, user_context)
        print(f"📊 Query analysis: {query_analysis.domain} domain, {query_analysis.privacy_requirements} privacy")
        
        # Step 2: Select appropriate nodes based on query analysis
        selected_nodes = self.select_nodes_for_query(query_analysis)
        print(f"🎯 Selected {len(selected_nodes)} nodes: {[n.node_id for n in selected_nodes]}")
        
        # Step 3: Execute parallel searches across nodes
        node_results = await self.execute_federated_search(query, selected_nodes, user_context)
        
        # Step 4: Aggregate and rank results
        aggregated_results = await self.aggregate_federated_results(node_results, query_analysis)
        
        # Step 5: Generate unified response
        final_response = await self.generate_federated_response(aggregated_results, query, user_context)
        
        return {
            'response': final_response,
            'nodes_queried': [node.node_id for node in selected_nodes],
            'result_breakdown': self.create_result_breakdown(node_results),
            'performance_metrics': self.performance_monitor.get_metrics(),
            'query_analysis': query_analysis.__dict__
        }
    
    async def analyze_query_for_federation(self, query: str, user_context: Dict) -> QueryAnalysis:
        """Analyze query to determine federation strategy"""
        
        # Simple domain detection (in practice, use ML models)
        domain_keywords = {
            'legal': ['law', 'legal', 'court', 'regulation', 'compliance'],
            'medical': ['medical', 'health', 'clinical', 'patient', 'diagnosis'],
            'technical': ['code', 'software', 'technical', 'engineering', 'development'],
            'financial': ['finance', 'banking', 'investment', 'money', 'financial']
        }
        
        query_lower = query.lower()
        detected_domain = 'general'
        
        for domain, keywords in domain_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                detected_domain = domain
                break
        
        # Determine privacy requirements
        privacy_requirements = user_context.get('privacy_requirements', 'standard')
        if any(word in query_lower for word in ['confidential', 'private', 'sensitive']):
            privacy_requirements = 'high'
        
        # Determine required capabilities
        required_capabilities = ['basic_search']
        if 'semantic' in query_lower or 'meaning' in query_lower:
            required_capabilities.append('semantic_search')
        if 'image' in query_lower or 'picture' in query_lower:
            required_capabilities.append('image_search')
        
        return QueryAnalysis(
            domain=detected_domain,
            privacy_requirements=privacy_requirements,
            required_capabilities=required_capabilities,
            max_nodes=min(5, len(self.nodes)),
            ranking_strategy='quality_weighted',
            user_context=user_context
        )
    
    def select_nodes_for_query(self, query_analysis: QueryAnalysis) -> List[FederatedNode]:
        """Select which nodes to query based on query analysis"""
        suitable_nodes = []
        
        for node in self.nodes.values():
            if not node.available:
                continue
            
            # Match data domain
            if (query_analysis.domain != 'general' and 
                node.data_domain != query_analysis.domain and 
                node.data_domain != 'general'):
                continue
            
            # Check privacy compatibility
            if not self.privacy_manager.check_privacy_compatibility(
                query_analysis.privacy_requirements, node.privacy_level
            ):
                continue
            
            # Check capability requirements
            if not self.check_capability_match(query_analysis.required_capabilities, node.capabilities):
                continue
            
            suitable_nodes.append(node)
        
        # Rank nodes by relevance and performance
        ranked_nodes = self.rank_nodes(suitable_nodes, query_analysis)
        
        return ranked_nodes[:query_analysis.max_nodes]
    
    def check_capability_match(self, required: List[str], available: List[str]) -> bool:
        """Check if node has required capabilities"""
        return all(cap in available for cap in required)
    
    def rank_nodes(self, nodes: List[FederatedNode], query_analysis: QueryAnalysis) -> List[FederatedNode]:
        """Rank nodes by relevance and performance"""
        
        def node_score(node: FederatedNode) -> float:
            score = 0.0
            
            # Domain match bonus
            if node.data_domain == query_analysis.domain:
                score += 2.0
            elif node.data_domain == 'general':
                score += 1.0
            
            # Performance bonus (lower latency = higher score)
            score += max(0, 2.0 - node.latency)
            
            # Capability bonus
            capability_match = sum(1 for cap in query_analysis.required_capabilities if cap in node.capabilities)
            score += capability_match * 0.5
            
            return score
        
        return sorted(nodes, key=node_score, reverse=True)
    
    async def execute_federated_search(self, query: str, nodes: List[FederatedNode], user_context: Dict) -> Dict[str, Any]:
        """Execute search across multiple nodes in parallel"""
        
        async def search_single_node(node: FederatedNode):
            try:
                start_time = time.time()
                
                # Apply privacy transformations if needed
                transformed_query = await self.privacy_manager.transform_query_for_node(
                    query, node, user_context
                )
                
                # Execute search on node
                result = await self.query_node(node, transformed_query, user_context)
                latency = time.time() - start_time
                
                # Update node performance metrics
                self.performance_monitor.record_node_performance(node.node_id, latency, True)
                
                return {
                    'node_id': node.node_id,
                    'results': result,
                    'latency': latency,
                    'success': True,
                    'result_count': len(result.get('documents', [])),
                    'query_used': transformed_query
                }
                
            except Exception as e:
                self.performance_monitor.record_node_performance(node.node_id, 0, False)
                return {
                    'node_id': node.node_id,
                    'error': str(e),
                    'success': False,
                    'results': {'documents': []}
                }
        
        # Execute all node searches concurrently
        tasks = [search_single_node(node) for node in nodes]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        return {result['node_id']: result for result in results if isinstance(result, dict)}
    
    async def query_node(self, node: FederatedNode, query: str, user_context: Dict) -> Dict:
        """Query a specific federated node"""
        
        if not self.session:
            self.session = aiohttp.ClientSession()
        
        payload = {
            'query': query,
            'user_context': user_context,
            'limit': user_context.get('limit', 10)
        }
        
        async with self.session.post(
            f"{node.endpoint}/search",
            json=payload,
            timeout=30
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(f"Node {node.node_id} returned status {response.status}")
    
    async def aggregate_federated_results(self, node_results: Dict, query_analysis: QueryAnalysis) -> Dict:
        """Aggregate results from multiple federated nodes"""
        return await self.result_aggregator.aggregate_federated_results(node_results, query_analysis)
    
    async def generate_federated_response(self, aggregated_results: Dict, query: str, user_context: Dict) -> Dict:
        """Generate unified response from aggregated results"""
        
        # Simple response generation (in practice, use LLM)
        documents = aggregated_results.get('documents', [])
        
        # Create summary
        summary = f"Found {len(documents)} relevant documents from {aggregated_results.get('nodes_contributing', 0)} federated nodes."
        
        # Extract top results
        top_results = documents[:10]  # Top 10 results
        
        return {
            'summary': summary,
            'documents': top_results,
            'total_results': len(documents),
            'nodes_contributing': aggregated_results.get('nodes_contributing', 0),
            'aggregation_metadata': aggregated_results.get('node_breakdown', {})
        }
    
    def create_result_breakdown(self, node_results: Dict) -> Dict:
        """Create breakdown of results by node"""
        breakdown = {}
        
        for node_id, result in node_results.items():
            breakdown[node_id] = {
                'success': result.get('success', False),
                'result_count': result.get('result_count', 0),
                'latency': result.get('latency', 0),
                'error': result.get('error', None)
            }
        
        return breakdown

class QueryRouter:
    """Route queries to appropriate federated nodes"""
    
    def __init__(self):
        self.routing_rules = {
            'legal': ['legal_db', 'compliance_db'],
            'medical': ['medical_db', 'clinical_db'],
            'technical': ['tech_kb', 'code_repo'],
            'financial': ['finance_db', 'market_data']
        }
    
    def get_routing_suggestions(self, domain: str) -> List[str]:
        """Get suggested nodes for a domain"""
        return self.routing_rules.get(domain, ['general_kb'])
