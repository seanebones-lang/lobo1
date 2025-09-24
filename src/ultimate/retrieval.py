"""
Ultimate Retrieval Orchestrator
Orchestrates all retrieval strategies with intelligent routing.
"""

import asyncio
import numpy as np
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import hashlib

class UltimateRetrievalOrchestrator:
    """Orchestrates all retrieval strategies with intelligent routing"""
    
    def __init__(self, vector_stores, config):
        self.vector_stores = vector_stores
        self.config = config
        
        # Initialize all retrieval strategies
        self.retrieval_strategies = {
            'vector_similarity': VectorSimilarityRetriever(),
            'keyword_search': BM25Retriever(),
            'semantic_search': SemanticSearchRetriever(),
            'hybrid_search': HybridFusionRetriever(),
            'graph_based': KnowledgeGraphRetriever(),
            'multimodal': MultiModalRetriever(),
            'federated': FederatedRetriever() if config.enable_federation else None,
            'self_querying': SelfQueryingRetriever() if config.enable_self_querying else None
        }
        
        self.router = IntelligentRetrievalRouter()
        self.reranker = MultiModelReranker()
        self.fusion_engine = AdvancedFusionEngine()
    
    async def retrieve(self, query: str, context: Dict, options: Dict = None) -> Dict:
        """Intelligent retrieval with automatic strategy selection"""
        
        print(f"🔍 Starting retrieval for query: '{query[:50]}...'")
        
        # Analyze query to determine best strategies
        strategy_analysis = await self.analyze_query_for_retrieval(query, context)
        strategies = strategy_analysis['recommended_strategies']
        
        print(f"📊 Selected strategies: {strategies}")
        
        # Execute retrieval in parallel
        retrieval_tasks = []
        for strategy_name in strategies:
            retriever = self.retrieval_strategies.get(strategy_name)
            if retriever:
                task = self.execute_retrieval(retriever, query, context, strategy_name)
                retrieval_tasks.append(task)
        
        # Wait for all retrievals to complete
        strategy_results = await asyncio.gather(*retrieval_tasks, return_exceptions=True)
        
        # Process results and handle exceptions
        processed_results = {}
        for i, result in enumerate(strategy_results):
            strategy_name = strategies[i]
            if isinstance(result, Exception):
                print(f"❌ Strategy {strategy_name} failed: {result}")
                processed_results[strategy_name] = {'documents': [], 'error': str(result)}
            else:
                processed_results[strategy_name] = result
        
        # Fusion of results
        fused_results = await self.fuse_retrieval_results(processed_results, query, strategy_analysis)
        
        # Rerank results
        if self.config.enable_reranking:
            reranked_results = await self.reranker.rerank(query, fused_results)
        else:
            reranked_results = fused_results
        
        return {
            'documents': reranked_results,
            'retrieval_strategies_used': strategies,
            'strategy_effectiveness': await self.analyze_strategy_effectiveness(
                processed_results, query
            ),
            'fusion_method': 'weighted_reciprocal_rank',
            'total_documents': len(reranked_results),
            'retrieval_metadata': {
                'query_analysis': strategy_analysis,
                'strategy_results': {k: len(v.get('documents', [])) for k, v in processed_results.items()},
                'fusion_weights': await self.calculate_fusion_weights(strategy_analysis)
            }
        }
    
    async def execute_retrieval(self, retriever, query: str, context: Dict, strategy_name: str) -> Dict:
        """Execute retrieval with a specific strategy"""
        try:
            start_time = datetime.now()
            
            result = await retriever.retrieve(query, context)
            
            latency = (datetime.now() - start_time).total_seconds()
            
            return {
                'documents': result.get('documents', []),
                'strategy': strategy_name,
                'latency': latency,
                'result_count': len(result.get('documents', [])),
                'confidence': result.get('confidence', 0.5),
                'metadata': result.get('metadata', {})
            }
            
        except Exception as e:
            print(f"❌ Retrieval strategy {strategy_name} failed: {e}")
            return {
                'documents': [],
                'strategy': strategy_name,
                'error': str(e),
                'latency': 0,
                'result_count': 0
            }
    
    async def analyze_query_for_retrieval(self, query: str, context: Dict) -> Dict:
        """Determine best retrieval strategies for a query"""
        
        analysis = {
            'query_complexity': await self.assess_complexity(query),
            'query_type': await self.classify_query_type(query),
            'domain': context.get('domain', 'general'),
            'historical_performance': await self.get_historical_performance(query),
            'recommended_strategies': []
        }
        
        # Rule-based strategy selection
        strategies = []
        
        if analysis['query_type'] == 'factual':
            strategies.extend(['keyword_search', 'vector_similarity'])
        elif analysis['query_type'] == 'exploratory':
            strategies.extend(['semantic_search', 'graph_based'])
        elif analysis['query_type'] == 'complex_analytical':
            strategies.extend(['hybrid_search', 'self_querying'])
        elif analysis['query_type'] == 'multimodal':
            strategies.extend(['multimodal', 'hybrid_search'])
        
        # Add domain-specific strategies
        if analysis['domain'] == 'cross_domain':
            strategies.append('federated')
        elif analysis['domain'] == 'knowledge_graph':
            strategies.append('graph_based')
        
        # Add complexity-based strategies
        if analysis['query_complexity'] == 'high':
            strategies.extend(['self_querying', 'hybrid_search'])
        
        # Remove duplicates and limit to top strategies
        strategies = list(set(strategies))[:3]
        
        # Ensure we have at least one strategy
        if not strategies:
            strategies = ['vector_similarity', 'keyword_search']
        
        analysis['recommended_strategies'] = strategies
        return analysis
    
    async def assess_complexity(self, query: str) -> str:
        """Assess query complexity"""
        complexity_indicators = {
            'high': ['analyze', 'compare', 'explain', 'why', 'how', 'what if', 'relationship'],
            'medium': ['find', 'search', 'locate', 'identify'],
            'low': ['what', 'when', 'where', 'who']
        }
        
        query_lower = query.lower()
        
        for level, indicators in complexity_indicators.items():
            if any(indicator in query_lower for indicator in indicators):
                return level
        
        return 'medium'
    
    async def classify_query_type(self, query: str) -> str:
        """Classify query type"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['image', 'picture', 'photo', 'diagram']):
            return 'multimodal'
        elif any(word in query_lower for word in ['analyze', 'compare', 'relationship', 'why']):
            return 'complex_analytical'
        elif any(word in query_lower for word in ['explore', 'discover', 'find similar']):
            return 'exploratory'
        elif any(word in query_lower for word in ['what', 'when', 'where', 'who']):
            return 'factual'
        else:
            return 'general'
    
    async def get_historical_performance(self, query: str) -> Dict:
        """Get historical performance data for similar queries"""
        # Mock implementation - in practice, query performance database
        return {
            'avg_latency': 0.5,
            'success_rate': 0.95,
            'preferred_strategies': ['vector_similarity', 'keyword_search']
        }
    
    async def fuse_retrieval_results(self, strategy_results: Dict, query: str, analysis: Dict) -> List[Dict]:
        """Advanced fusion of multiple retrieval strategies"""
        
        # Calculate strategy weights based on performance and query analysis
        strategy_weights = await self.calculate_strategy_weights(strategy_results, analysis)
        
        fused_documents = {}
        
        for strategy_name, result in strategy_results.items():
            if not result or 'documents' not in result:
                continue
                
            weight = strategy_weights.get(strategy_name, 0.1)
            documents = result['documents']
            
            for i, doc in enumerate(documents):
                doc_id = doc.get('doc_id', self.generate_doc_id(doc))
                
                # Calculate score with strategy weighting
                base_score = doc.get('score', 0.5)
                rank_score = 1.0 / (i + 1)  # Reciprocal rank
                strategy_score = weight * base_score * rank_score
                
                # Apply latency penalty for slow strategies
                latency_penalty = max(0.5, 1.0 - (result.get('latency', 0) / 5.0))
                final_score = strategy_score * latency_penalty
                
                if doc_id in fused_documents:
                    # Existing document - combine scores
                    fused_documents[doc_id]['score'] += final_score
                    fused_documents[doc_id]['strategies'].append(strategy_name)
                    fused_documents[doc_id]['strategy_scores'][strategy_name] = final_score
                else:
                    # New document
                    fused_documents[doc_id] = {
                        **doc,
                        'score': final_score,
                        'strategies': [strategy_name],
                        'strategy_scores': {strategy_name: final_score},
                        'original_scores': {strategy_name: base_score}
                    }
        
        # Convert to list and sort by combined score
        sorted_documents = sorted(
            fused_documents.values(), 
            key=lambda x: x['score'], 
            reverse=True
        )
        
        # Apply diversity filtering
        diverse_documents = await self.apply_diversity_filtering(sorted_documents)
        
        return diverse_documents
    
    async def calculate_strategy_weights(self, strategy_results: Dict, analysis: Dict) -> Dict:
        """Calculate weights for different retrieval strategies"""
        weights = {}
        
        for strategy_name, result in strategy_results.items():
            if not result or 'error' in result:
                weights[strategy_name] = 0.0
                continue
            
            base_weight = 1.0
            
            # Adjust based on result count
            result_count = result.get('result_count', 0)
            if result_count > 0:
                base_weight *= min(1.5, result_count / 10.0)
            
            # Adjust based on latency
            latency = result.get('latency', 1.0)
            if latency > 0:
                base_weight *= max(0.5, 1.0 - (latency / 10.0))
            
            # Adjust based on query type
            query_type = analysis.get('query_type', 'general')
            if query_type == 'factual' and strategy_name == 'keyword_search':
                base_weight *= 1.2
            elif query_type == 'exploratory' and strategy_name == 'semantic_search':
                base_weight *= 1.2
            elif query_type == 'complex_analytical' and strategy_name == 'hybrid_search':
                base_weight *= 1.2
            
            weights[strategy_name] = base_weight
        
        # Normalize weights
        total_weight = sum(weights.values())
        if total_weight > 0:
            weights = {k: v / total_weight for k, v in weights.items()}
        
        return weights
    
    async def apply_diversity_filtering(self, documents: List[Dict]) -> List[Dict]:
        """Apply diversity filtering to avoid redundant results"""
        diverse_documents = []
        seen_content_hashes = set()
        
        for doc in documents:
            content_hash = self.calculate_content_hash(doc.get('content', ''))
            
            if content_hash not in seen_content_hashes:
                seen_content_hashes.add(content_hash)
                diverse_documents.append(doc)
            
            # Limit to top diverse results
            if len(diverse_documents) >= 20:
                break
        
        return diverse_documents
    
    def generate_doc_id(self, doc: Dict) -> str:
        """Generate document ID for deduplication"""
        content = doc.get('content', '')
        metadata = doc.get('metadata', {})
        key_string = f"{content}_{json.dumps(metadata, sort_keys=True)}"
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def calculate_content_hash(self, content: str) -> str:
        """Calculate content hash for diversity filtering"""
        return hashlib.md5(content.encode()).hexdigest()
    
    async def analyze_strategy_effectiveness(self, strategy_results: Dict, query: str) -> Dict:
        """Analyze effectiveness of different strategies"""
        effectiveness = {}
        
        for strategy_name, result in strategy_results.items():
            if 'error' in result:
                effectiveness[strategy_name] = {
                    'success': False,
                    'error': result['error'],
                    'effectiveness_score': 0.0
                }
            else:
                result_count = result.get('result_count', 0)
                latency = result.get('latency', 0)
                confidence = result.get('confidence', 0.5)
                
                # Calculate effectiveness score
                effectiveness_score = (
                    min(1.0, result_count / 10.0) * 0.4 +  # Result count factor
                    max(0.5, 1.0 - (latency / 5.0)) * 0.3 +  # Latency factor
                    confidence * 0.3  # Confidence factor
                )
                
                effectiveness[strategy_name] = {
                    'success': True,
                    'result_count': result_count,
                    'latency': latency,
                    'confidence': confidence,
                    'effectiveness_score': effectiveness_score
                }
        
        return effectiveness
    
    async def warm_up(self):
        """Warm up retrieval system"""
        print("🔥 Warming up retrieval orchestrator...")
        
        # Warm up individual retrievers
        for name, retriever in self.retrieval_strategies.items():
            if retriever:
                try:
                    await retriever.warm_up()
                except Exception as e:
                    print(f"⚠️ Warning: {name} warm-up failed: {e}")
        
        print("✅ Retrieval orchestrator warmed up!")
    
    async def get_status(self) -> Dict:
        """Get retrieval system status"""
        status = {
            'total_strategies': len(self.retrieval_strategies),
            'active_strategies': len([s for s in self.retrieval_strategies.values() if s is not None]),
            'reranking_enabled': self.config.enable_reranking,
            'fusion_method': 'weighted_reciprocal_rank'
        }
        
        # Get individual strategy status
        strategy_status = {}
        for name, retriever in self.retrieval_strategies.items():
            if retriever:
                try:
                    strategy_status[name] = await retriever.get_status()
                except:
                    strategy_status[name] = {'status': 'error'}
            else:
                strategy_status[name] = {'status': 'disabled'}
        
        status['strategy_status'] = strategy_status
        return status

class IntelligentRetrievalRouter:
    """Intelligently routes queries to optimal retrieval strategies"""
    
    def __init__(self):
        self.routing_rules = {
            'factual': ['keyword_search', 'vector_similarity'],
            'exploratory': ['semantic_search', 'graph_based'],
            'complex_analytical': ['hybrid_search', 'self_querying'],
            'multimodal': ['multimodal', 'hybrid_search']
        }
    
    async def get_routing_suggestions(self, query_analysis: Dict) -> List[str]:
        """Get routing suggestions based on query analysis"""
        query_type = query_analysis.get('query_type', 'general')
        complexity = query_analysis.get('query_complexity', 'medium')
        
        suggestions = self.routing_rules.get(query_type, ['vector_similarity'])
        
        # Add complexity-based suggestions
        if complexity == 'high':
            suggestions.extend(['hybrid_search', 'self_querying'])
        
        return list(set(suggestions))

class MultiModelReranker:
    """Multi-model reranking system"""
    
    def __init__(self):
        self.rerankers = {
            'cross_encoder': CrossEncoderReranker(),
            'bm25': BM25Reranker(),
            'semantic': SemanticReranker(),
            'hybrid': HybridReranker()
        }
    
    async def rerank(self, query: str, documents: List[Dict]) -> List[Dict]:
        """Rerank documents using multiple models"""
        if not documents:
            return documents
        
        # Use cross-encoder for final reranking
        reranked = await self.rerankers['cross_encoder'].rerank(query, documents)
        
        return reranked

class AdvancedFusionEngine:
    """Advanced fusion engine for combining results"""
    
    async def fuse_results(self, strategy_results: Dict, weights: Dict) -> List[Dict]:
        """Fuse results from multiple strategies"""
        # Implementation of advanced fusion algorithms
        pass

# Mock retriever classes
class VectorSimilarityRetriever:
    async def retrieve(self, query: str, context: Dict) -> Dict:
        return {'documents': [{'content': 'Mock vector result', 'score': 0.9}], 'confidence': 0.8}
    
    async def warm_up(self):
        pass
    
    async def get_status(self):
        return {'status': 'healthy'}

class BM25Retriever:
    async def retrieve(self, query: str, context: Dict) -> Dict:
        return {'documents': [{'content': 'Mock BM25 result', 'score': 0.8}], 'confidence': 0.7}
    
    async def warm_up(self):
        pass
    
    async def get_status(self):
        return {'status': 'healthy'}

class SemanticSearchRetriever:
    async def retrieve(self, query: str, context: Dict) -> Dict:
        return {'documents': [{'content': 'Mock semantic result', 'score': 0.85}], 'confidence': 0.9}
    
    async def warm_up(self):
        pass
    
    async def get_status(self):
        return {'status': 'healthy'}

class HybridFusionRetriever:
    async def retrieve(self, query: str, context: Dict) -> Dict:
        return {'documents': [{'content': 'Mock hybrid result', 'score': 0.95}], 'confidence': 0.9}
    
    async def warm_up(self):
        pass
    
    async def get_status(self):
        return {'status': 'healthy'}

class KnowledgeGraphRetriever:
    async def retrieve(self, query: str, context: Dict) -> Dict:
        return {'documents': [{'content': 'Mock graph result', 'score': 0.8}], 'confidence': 0.8}
    
    async def warm_up(self):
        pass
    
    async def get_status(self):
        return {'status': 'healthy'}

class MultiModalRetriever:
    async def retrieve(self, query: str, context: Dict) -> Dict:
        return {'documents': [{'content': 'Mock multimodal result', 'score': 0.9}], 'confidence': 0.85}
    
    async def warm_up(self):
        pass
    
    async def get_status(self):
        return {'status': 'healthy'}

class FederatedRetriever:
    async def retrieve(self, query: str, context: Dict) -> Dict:
        return {'documents': [{'content': 'Mock federated result', 'score': 0.8}], 'confidence': 0.8}
    
    async def warm_up(self):
        pass
    
    async def get_status(self):
        return {'status': 'healthy'}

class SelfQueryingRetriever:
    async def retrieve(self, query: str, context: Dict) -> Dict:
        return {'documents': [{'content': 'Mock self-querying result', 'score': 0.9}], 'confidence': 0.9}
    
    async def warm_up(self):
        pass
    
    async def get_status(self):
        return {'status': 'healthy'}

# Mock reranker classes
class CrossEncoderReranker:
    async def rerank(self, query: str, documents: List[Dict]) -> List[Dict]:
        # Mock reranking - in practice, use cross-encoder model
        return sorted(documents, key=lambda x: x.get('score', 0), reverse=True)

class BM25Reranker:
    async def rerank(self, query: str, documents: List[Dict]) -> List[Dict]:
        return documents

class SemanticReranker:
    async def rerank(self, query: str, documents: List[Dict]) -> List[Dict]:
        return documents

class HybridReranker:
    async def rerank(self, query: str, documents: List[Dict]) -> List[Dict]:
        return documents
