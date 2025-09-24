"""
Federated RAG System Demo
Demonstrates the federated RAG system with multiple nodes and privacy features.
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List

from .orchestrator import FederatedRAGOrchestrator
from .node import FederatedNode, FederatedNodeServer
from .privacy import PrivacyManager
from .aggregation import FederatedResultAggregator
from .knowledge_graph import FederatedKnowledgeGraph
from .management import FederationManager, NodeHealthChecker

class FederatedRAGDemo:
    """Demo class for federated RAG system"""
    
    def __init__(self):
        self.orchestrator = None
        self.federation_manager = FederationManager()
        self.demo_nodes = []
    
    async def setup_demo_environment(self):
        """Setup demo environment with mock nodes"""
        print("🚀 Setting up Federated RAG Demo Environment")
        
        # Initialize orchestrator
        self.orchestrator = FederatedRAGOrchestrator({
            'max_nodes_per_query': 5,
            'privacy_mode': 'strict',
            'result_limit': 20
        })
        
        # Create demo nodes
        demo_nodes = [
            {
                'node_id': 'legal_db',
                'endpoint': 'http://localhost:8001',
                'data_domain': 'legal',
                'capabilities': ['full_text_search', 'citation_linking', 'semantic_search'],
                'privacy_level': 'confidential',
                'latency': 0.5
            },
            {
                'node_id': 'medical_db',
                'endpoint': 'http://localhost:8002',
                'data_domain': 'medical',
                'capabilities': ['semantic_search', 'clinical_terms', 'image_search'],
                'privacy_level': 'restricted',
                'latency': 0.8
            },
            {
                'node_id': 'tech_kb',
                'endpoint': 'http://localhost:8003',
                'data_domain': 'technical',
                'capabilities': ['vector_search', 'keyword_search', 'code_search'],
                'privacy_level': 'public',
                'latency': 0.3
            },
            {
                'node_id': 'general_kb',
                'endpoint': 'http://localhost:8004',
                'data_domain': 'general',
                'capabilities': ['basic_search', 'vector_search'],
                'privacy_level': 'public',
                'latency': 0.2
            }
        ]
        
        # Register nodes with orchestrator
        for node_config in demo_nodes:
            node = FederatedNode(**node_config)
            await self.orchestrator.register_node(node)
            self.demo_nodes.append(node)
        
        print(f"✅ Registered {len(self.demo_nodes)} demo nodes")
        return True
    
    async def run_demo_queries(self):
        """Run demonstration queries"""
        print("\n🔍 Running Federated RAG Demo Queries")
        
        demo_queries = [
            {
                'query': 'What are the legal requirements for medical data privacy in clinical trials?',
                'user_context': {
                    'user_id': 'demo_user_1',
                    'domain': 'cross_domain',
                    'privacy_requirements': 'high',
                    'role': 'researcher'
                },
                'description': 'Cross-domain query requiring both legal and medical knowledge'
            },
            {
                'query': 'How to implement secure authentication in microservices architecture?',
                'user_context': {
                    'user_id': 'demo_user_2',
                    'domain': 'technical',
                    'privacy_requirements': 'standard',
                    'role': 'developer'
                },
                'description': 'Technical query requiring specialized knowledge'
            },
            {
                'query': 'What are the benefits of machine learning in healthcare?',
                'user_context': {
                    'user_id': 'demo_user_3',
                    'domain': 'medical',
                    'privacy_requirements': 'confidential',
                    'role': 'medical_professional'
                },
                'description': 'Medical query with confidentiality requirements'
            }
        ]
        
        for i, query_data in enumerate(demo_queries, 1):
            print(f"\n--- Demo Query {i} ---")
            print(f"Description: {query_data['description']}")
            print(f"Query: {query_data['query']}")
            print(f"User Context: {query_data['user_context']}")
            
            try:
                results = await self.orchestrator.federated_search(
                    query_data['query'],
                    query_data['user_context']
                )
                
                print(f"\n📊 Results Summary:")
                print(f"  - Nodes queried: {len(results['nodes_queried'])}")
                print(f"  - Total documents: {results['response']['total_results']}")
                print(f"  - Nodes contributing: {results['response']['nodes_contributing']}")
                
                print(f"\n📋 Top Results:")
                for j, doc in enumerate(results['response']['documents'][:3], 1):
                    print(f"  {j}. Score: {doc.get('federated_score', 0):.3f}")
                    print(f"     Source: {doc.get('federated_metadata', {}).get('source_node', 'unknown')}")
                    print(f"     Content: {doc.get('content', '')[:100]}...")
                    print()
                
                print(f"🔧 Performance Metrics:")
                metrics = results.get('performance_metrics', {})
                print(f"  - Health percentage: {metrics.get('health_percentage', 0):.1f}%")
                print(f"  - Total nodes: {metrics.get('total_nodes', 0)}")
                print(f"  - Healthy nodes: {metrics.get('healthy_nodes', 0)}")
                
            except Exception as e:
                print(f"❌ Query failed: {e}")
    
    async def demonstrate_privacy_features(self):
        """Demonstrate privacy-preserving features"""
        print("\n🔒 Demonstrating Privacy Features")
        
        privacy_manager = PrivacyManager()
        
        # Test query transformation
        test_queries = [
            "Find patient records for John Smith with SSN 123-45-6789",
            "Company financial data for Acme Corp",
            "Legal case details for lawsuit #2024-001"
        ]
        
        for query in test_queries:
            print(f"\nOriginal Query: {query}")
            
            # Test anonymization
            anonymized = privacy_manager.query_anonymizer.anonymize_query(query)
            print(f"Anonymized: {anonymized}")
            
            # Test generalization
            generalized = await privacy_manager.generalize_query(query, {'domain': 'general'})
            print(f"Generalized: {generalized}")
            
            # Test differential privacy
            noisy = privacy_manager.differential_privacy.add_noise_to_query(query)
            print(f"With Noise: {noisy}")
    
    async def demonstrate_knowledge_graph(self):
        """Demonstrate cross-node knowledge graph"""
        print("\n🔗 Demonstrating Cross-Node Knowledge Graph")
        
        knowledge_graph = FederatedKnowledgeGraph(self.orchestrator)
        
        # Build knowledge graph for entities
        entities = ['artificial intelligence', 'machine learning', 'healthcare', 'privacy']
        
        try:
            graph_data = await knowledge_graph.build_cross_node_knowledge_graph(entities)
            
            print(f"📊 Knowledge Graph Statistics:")
            stats = graph_data.get('graph_stats', {})
            print(f"  - Total entities: {stats.get('total_entities', 0)}")
            print(f"  - Total relationships: {stats.get('total_relationships', 0)}")
            print(f"  - Connected components: {stats.get('connected_components', 0)}")
            print(f"  - Graph density: {stats.get('density', 0):.3f}")
            
            print(f"\n🏷️ Entity Information:")
            for entity, info in graph_data.get('entities', {}).items():
                print(f"  {entity}:")
                print(f"    - Confidence: {info.get('confidence', 0):.3f}")
                print(f"    - Sources: {len(info.get('sources', []))}")
                print(f"    - Properties: {len(info.get('properties', {}))}")
            
        except Exception as e:
            print(f"❌ Knowledge graph demo failed: {e}")
    
    async def demonstrate_federation_management(self):
        """Demonstrate federation management features"""
        print("\n⚙️ Demonstrating Federation Management")
        
        # Show current federation status
        health_checker = NodeHealthChecker()
        
        print("📊 Federation Health Status:")
        for node in self.demo_nodes:
            status = health_checker.get_health_status(node.node_id)
            if status:
                print(f"  {node.node_id}: {'✅ Healthy' if status.is_healthy else '❌ Unhealthy'}")
                print(f"    - Uptime: {status.uptime_percentage:.1f}%")
                print(f"    - Latency: {status.latency:.3f}s")
                print(f"    - Last check: {status.last_check}")
            else:
                print(f"  {node.node_id}: ⏳ No status data")
        
        # Show performance metrics
        metrics = health_checker.get_metrics()
        print(f"\n📈 Federation Metrics:")
        print(f"  - Total nodes: {metrics.get('total_nodes', 0)}")
        print(f"  - Healthy nodes: {metrics.get('healthy_nodes', 0)}")
        print(f"  - Health percentage: {metrics.get('health_percentage', 0):.1f}%")
    
    async def run_complete_demo(self):
        """Run the complete federated RAG demo"""
        print("🌟 Starting Complete Federated RAG System Demo")
        print("=" * 60)
        
        try:
            # Setup environment
            await self.setup_demo_environment()
            
            # Run demo queries
            await self.run_demo_queries()
            
            # Demonstrate privacy features
            await self.demonstrate_privacy_features()
            
            # Demonstrate knowledge graph
            await self.demonstrate_knowledge_graph()
            
            # Demonstrate federation management
            await self.demonstrate_federation_management()
            
            print("\n🎉 Federated RAG Demo Complete!")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ Demo failed: {e}")
            import traceback
            traceback.print_exc()

async def main():
    """Main demo function"""
    demo = FederatedRAGDemo()
    await demo.run_complete_demo()

if __name__ == "__main__":
    asyncio.run(main())
