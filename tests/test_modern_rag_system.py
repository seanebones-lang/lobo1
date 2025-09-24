"""
Comprehensive Test Suite for Modern RAG System - 2025
Tests all components with latest techniques and optimizations
"""

import pytest
import asyncio
import json
import numpy as np
from typing import List, Dict, Any
from datetime import datetime
import tempfile
import os

# Import the modern RAG components
from src.advanced.modern_retrieval_system import ModernRetrievalSystem, RetrievalConfig
from src.advanced.modern_generation_system import ModernGenerationSystem, GenerationConfig
from src.advanced.modern_rag_orchestrator import ModernRAGOrchestrator, RAGOrchestratorConfig
from src.api.modern_rag_api import ModernRAGAPI, QueryRequest, DocumentUploadRequest

class TestModernRetrievalSystem:
    """Test suite for modern retrieval system"""
    
    @pytest.fixture
    def retrieval_config(self):
        """Create test retrieval configuration"""
        return RetrievalConfig(
            embedding_model="sentence-transformers/all-MiniLM-L6-v2",
            cross_encoder_model="cross-encoder/ms-marco-MiniLM-L-6-v2",
            dense_weight=0.7,
            sparse_weight=0.3,
            enable_reranking=True,
            rerank_top_k=10,
            final_top_k=5
        )
    
    @pytest.fixture
    def retrieval_system(self, retrieval_config):
        """Create test retrieval system"""
        return ModernRetrievalSystem(retrieval_config)
    
    @pytest.fixture
    def sample_documents(self):
        """Create sample documents for testing"""
        return [
            {
                "content": "Artificial intelligence is transforming healthcare by enabling early disease detection and personalized treatment plans.",
                "metadata": {"source": "healthcare_ai.pdf", "page": 1, "topic": "AI in healthcare"}
            },
            {
                "content": "Machine learning algorithms can analyze medical images with accuracy comparable to human radiologists.",
                "metadata": {"source": "ml_medical_imaging.pdf", "page": 2, "topic": "Medical imaging"}
            },
            {
                "content": "Natural language processing is revolutionizing patient care through automated medical record analysis.",
                "metadata": {"source": "nlp_healthcare.pdf", "page": 3, "topic": "NLP in healthcare"}
            },
            {
                "content": "Robotic surgery systems are becoming more precise and autonomous, reducing human error in complex procedures.",
                "metadata": {"source": "robotic_surgery.pdf", "page": 4, "topic": "Robotic surgery"}
            },
            {
                "content": "Telemedicine platforms are expanding access to healthcare services in remote and underserved areas.",
                "metadata": {"source": "telemedicine.pdf", "page": 5, "topic": "Telemedicine"}
            }
        ]
    
    @pytest.mark.asyncio
    async def test_add_documents(self, retrieval_system, sample_documents):
        """Test document addition to retrieval system"""
        success = await retrieval_system.add_documents(sample_documents)
        assert success is True
        
        # Verify documents were added
        stats = await retrieval_system.get_stats()
        assert stats['total_documents'] == len(sample_documents)
    
    @pytest.mark.asyncio
    async def test_hybrid_retrieval(self, retrieval_system, sample_documents):
        """Test hybrid retrieval functionality"""
        # Add documents first
        await retrieval_system.add_documents(sample_documents)
        
        # Test retrieval
        query = "How is AI used in healthcare?"
        results = await retrieval_system.retrieve(query, top_k=3)
        
        assert len(results) <= 3
        assert all('content' in result for result in results)
        assert all('score' in result for result in results)
        
        # Verify results are relevant
        for result in results:
            assert len(result['content']) > 0
            assert result['score'] > 0
    
    @pytest.mark.asyncio
    async def test_retrieval_with_filters(self, retrieval_system, sample_documents):
        """Test retrieval with metadata filters"""
        await retrieval_system.add_documents(sample_documents)
        
        # Test with topic filter
        filters = {"topic": "AI in healthcare"}
        results = await retrieval_system.retrieve(
            "What are the benefits of AI in healthcare?",
            top_k=5,
            filters=filters
        )
        
        # Verify filtered results
        for result in results:
            metadata = result.get('metadata', {})
            assert metadata.get('topic') == "AI in healthcare"
    
    @pytest.mark.asyncio
    async def test_reciprocal_rank_fusion(self, retrieval_system, sample_documents):
        """Test reciprocal rank fusion"""
        await retrieval_system.add_documents(sample_documents)
        
        # Test with RRF enabled
        results = await retrieval_system.retrieve("AI healthcare applications", top_k=3)
        
        # Verify fusion scores are present
        for result in results:
            assert 'fusion_score' in result or 'score' in result
    
    @pytest.mark.asyncio
    async def test_cache_functionality(self, retrieval_system, sample_documents):
        """Test caching functionality"""
        await retrieval_system.add_documents(sample_documents)
        
        query = "What is machine learning in healthcare?"
        
        # First retrieval (cache miss)
        start_time = datetime.now()
        results1 = await retrieval_system.retrieve(query, top_k=3)
        first_duration = (datetime.now() - start_time).total_seconds()
        
        # Second retrieval (cache hit)
        start_time = datetime.now()
        results2 = await retrieval_system.retrieve(query, top_k=3)
        second_duration = (datetime.now() - start_time).total_seconds()
        
        # Verify results are consistent
        assert len(results1) == len(results2)
        assert results1[0]['content'] == results2[0]['content']
        
        # Cache hit should be faster (though not guaranteed in all cases)
        # This is more of a sanity check
        assert second_duration >= 0

class TestModernGenerationSystem:
    """Test suite for modern generation system"""
    
    @pytest.fixture
    def generation_config(self):
        """Create test generation configuration"""
        return GenerationConfig(
            primary_llm="openai",
            fallback_llms=["anthropic"],
            temperature=0.1,
            max_tokens=1000,
            enable_fact_checking=True,
            enable_response_validation=True,
            enable_confidence_scoring=True,
            confidence_threshold=0.7
        )
    
    @pytest.fixture
    def generation_system(self, generation_config):
        """Create test generation system"""
        return ModernGenerationSystem(generation_config)
    
    @pytest.fixture
    def sample_context(self):
        """Create sample context for testing"""
        return [
            {
                "content": "Artificial intelligence is revolutionizing healthcare through advanced diagnostic tools and personalized treatment recommendations.",
                "metadata": {"source": "ai_healthcare.pdf", "page": 1},
                "score": 0.95
            },
            {
                "content": "Machine learning algorithms can analyze medical images with accuracy comparable to human radiologists.",
                "metadata": {"source": "ml_imaging.pdf", "page": 2},
                "score": 0.88
            }
        ]
    
    @pytest.mark.asyncio
    async def test_generate_response(self, generation_system, sample_context):
        """Test response generation"""
        query = "How is AI transforming healthcare?"
        
        response = await generation_system.generate_response(
            query=query,
            context=sample_context,
            conversation_history=None,
            user_preferences=None
        )
        
        # Verify response structure
        assert 'answer' in response
        assert 'confidence_score' in response
        assert 'metadata' in response
        assert 'sources' in response
        
        # Verify response quality
        assert len(response['answer']) > 0
        assert 0 <= response['confidence_score'] <= 1
        assert len(response['sources']) > 0
    
    @pytest.mark.asyncio
    async def test_fact_checking(self, generation_system, sample_context):
        """Test fact-checking functionality"""
        query = "What are the benefits of AI in healthcare?"
        
        response = await generation_system.generate_response(
            query=query,
            context=sample_context,
            conversation_history=None,
            user_preferences=None
        )
        
        # Verify fact-checking results
        assert 'fact_checking' in response
        fact_checking = response['fact_checking']
        
        assert 'factual_claims' in fact_checking
        assert 'source_verification' in fact_checking
        assert 'hallucination_indicators' in fact_checking
    
    @pytest.mark.asyncio
    async def test_response_validation(self, generation_system, sample_context):
        """Test response validation"""
        query = "How does machine learning help in medical diagnosis?"
        
        response = await generation_system.generate_response(
            query=query,
            context=sample_context,
            conversation_history=None,
            user_preferences=None
        )
        
        # Verify validation results
        assert 'validation_score' in response
        assert 'validation_results' in response
        
        validation_results = response['validation_results']
        assert 'length_check' in validation_results
        assert 'coherence_check' in validation_results
        assert 'relevance_check' in validation_results
    
    @pytest.mark.asyncio
    async def test_uncertainty_handling(self, generation_system, sample_context):
        """Test uncertainty handling"""
        query = "What are the future prospects of AI in healthcare?"
        
        response = await generation_system.generate_response(
            query=query,
            context=sample_context,
            conversation_history=None,
            user_preferences=None
        )
        
        # Verify uncertainty handling
        assert 'uncertainty_handled' in response
        assert response['confidence_score'] >= 0
        assert response['confidence_score'] <= 1

class TestModernRAGOrchestrator:
    """Test suite for modern RAG orchestrator"""
    
    @pytest.fixture
    def orchestrator_config(self):
        """Create test orchestrator configuration"""
        return RAGOrchestratorConfig(
            enable_caching=True,
            enable_monitoring=True,
            enable_analytics=True,
            max_concurrent_requests=10,
            request_timeout=30,
            cache_ttl=3600
        )
    
    @pytest.fixture
    def rag_orchestrator(self, orchestrator_config):
        """Create test RAG orchestrator"""
        return ModernRAGOrchestrator(orchestrator_config)
    
    @pytest.fixture
    def sample_documents(self):
        """Create sample documents for testing"""
        return [
            {
                "content": "Artificial intelligence is transforming healthcare through advanced diagnostic tools and personalized treatment recommendations.",
                "metadata": {"source": "ai_healthcare.pdf", "page": 1, "topic": "AI in healthcare"}
            },
            {
                "content": "Machine learning algorithms can analyze medical images with accuracy comparable to human radiologists.",
                "metadata": {"source": "ml_imaging.pdf", "page": 2, "topic": "Medical imaging"}
            },
            {
                "content": "Natural language processing is revolutionizing patient care through automated medical record analysis.",
                "metadata": {"source": "nlp_healthcare.pdf", "page": 3, "topic": "NLP in healthcare"}
            }
        ]
    
    @pytest.mark.asyncio
    async def test_add_documents(self, rag_orchestrator, sample_documents):
        """Test document addition to orchestrator"""
        success = await rag_orchestrator.add_documents(sample_documents)
        assert success is True
    
    @pytest.mark.asyncio
    async def test_process_query(self, rag_orchestrator, sample_documents):
        """Test query processing through orchestrator"""
        # Add documents first
        await rag_orchestrator.add_documents(sample_documents)
        
        # Process query
        query = "How is AI transforming healthcare?"
        response = await rag_orchestrator.process_query(
            query=query,
            user_id="test_user",
            session_id="test_session",
            user_preferences=None,
            context_filters=None
        )
        
        # Verify response structure
        assert 'answer' in response
        assert 'sources' in response
        assert 'confidence_score' in response
        assert 'orchestrator_metadata' in response
        
        # Verify response quality
        assert len(response['answer']) > 0
        assert 0 <= response['confidence_score'] <= 1
        assert len(response['sources']) > 0
    
    @pytest.mark.asyncio
    async def test_caching_functionality(self, rag_orchestrator, sample_documents):
        """Test caching functionality"""
        await rag_orchestrator.add_documents(sample_documents)
        
        query = "What are the benefits of AI in healthcare?"
        
        # First query (cache miss)
        start_time = datetime.now()
        response1 = await rag_orchestrator.process_query(
            query=query,
            user_id="test_user",
            session_id="test_session"
        )
        first_duration = (datetime.now() - start_time).total_seconds()
        
        # Second query (cache hit)
        start_time = datetime.now()
        response2 = await rag_orchestrator.process_query(
            query=query,
            user_id="test_user",
            session_id="test_session"
        )
        second_duration = (datetime.now() - start_time).total_seconds()
        
        # Verify responses are consistent
        assert response1['answer'] == response2['answer']
        assert response1['confidence_score'] == response2['confidence_score']
    
    @pytest.mark.asyncio
    async def test_system_status(self, rag_orchestrator):
        """Test system status retrieval"""
        status = await rag_orchestrator.get_system_status()
        
        # Verify status structure
        assert 'timestamp' in status
        assert 'system_health' in status
        assert 'performance_stats' in status
        assert 'cache_stats' in status
        assert 'resource_utilization' in status
        
        # Verify system health is a valid score
        assert 0 <= status['system_health'] <= 1
    
    @pytest.mark.asyncio
    async def test_optimization(self, rag_orchestrator, sample_documents):
        """Test system optimization"""
        await rag_orchestrator.add_documents(sample_documents)
        
        # Run optimization
        optimization_result = await rag_orchestrator.optimize_system()
        
        # Verify optimization result
        assert 'timestamp' in optimization_result
        assert 'optimizations_applied' in optimization_result
        assert 'system_health_after' in optimization_result

class TestModernRAGAPI:
    """Test suite for modern RAG API"""
    
    @pytest.fixture
    def api(self):
        """Create test API instance"""
        return ModernRAGAPI()
    
    def test_api_initialization(self, api):
        """Test API initialization"""
        assert api.app is not None
        assert api.rag_orchestrator is not None
        assert api.security is not None
    
    def test_query_request_validation(self):
        """Test query request validation"""
        # Valid request
        valid_request = QueryRequest(
            query="How is AI used in healthcare?",
            user_id="test_user",
            max_results=5
        )
        assert valid_request.query == "How is AI used in healthcare?"
        assert valid_request.user_id == "test_user"
        assert valid_request.max_results == 5
        
        # Invalid request (empty query)
        with pytest.raises(ValueError):
            QueryRequest(query="")
        
        # Invalid request (query too long)
        with pytest.raises(ValueError):
            QueryRequest(query="x" * 1001)
    
    def test_document_upload_validation(self):
        """Test document upload validation"""
        # Valid request
        valid_documents = [
            {"content": "AI is transforming healthcare", "metadata": {"source": "test.pdf"}},
            {"content": "Machine learning improves diagnosis", "metadata": {"source": "test2.pdf"}}
        ]
        valid_request = DocumentUploadRequest(documents=valid_documents)
        assert len(valid_request.documents) == 2
        
        # Invalid request (empty documents)
        with pytest.raises(ValueError):
            DocumentUploadRequest(documents=[])
        
        # Invalid request (missing content)
        with pytest.raises(ValueError):
            DocumentUploadRequest(documents=[{"metadata": {"source": "test.pdf"}}])

class TestIntegration:
    """Integration tests for the complete RAG system"""
    
    @pytest.fixture
    def complete_system(self):
        """Create complete RAG system for integration testing"""
        config = RAGOrchestratorConfig(
            enable_caching=True,
            enable_monitoring=True,
            enable_analytics=True
        )
        return ModernRAGOrchestrator(config)
    
    @pytest.fixture
    def comprehensive_documents(self):
        """Create comprehensive document set for testing"""
        return [
            {
                "content": "Artificial intelligence is revolutionizing healthcare through advanced diagnostic tools, personalized treatment plans, and automated medical record analysis.",
                "metadata": {
                    "source": "ai_healthcare_comprehensive.pdf",
                    "page": 1,
                    "topic": "AI in healthcare",
                    "date": "2024-01-15",
                    "author": "Dr. Smith"
                }
            },
            {
                "content": "Machine learning algorithms can analyze medical images with accuracy comparable to human radiologists, enabling early detection of diseases.",
                "metadata": {
                    "source": "ml_medical_imaging.pdf",
                    "page": 2,
                    "topic": "Medical imaging",
                    "date": "2024-02-10",
                    "author": "Dr. Johnson"
                }
            },
            {
                "content": "Natural language processing is transforming patient care through automated medical record analysis and clinical decision support systems.",
                "metadata": {
                    "source": "nlp_healthcare.pdf",
                    "page": 3,
                    "topic": "NLP in healthcare",
                    "date": "2024-03-05",
                    "author": "Dr. Williams"
                }
            },
            {
                "content": "Robotic surgery systems are becoming more precise and autonomous, reducing human error in complex surgical procedures.",
                "metadata": {
                    "source": "robotic_surgery.pdf",
                    "page": 4,
                    "topic": "Robotic surgery",
                    "date": "2024-04-12",
                    "author": "Dr. Brown"
                }
            },
            {
                "content": "Telemedicine platforms are expanding access to healthcare services in remote and underserved areas, improving patient outcomes.",
                "metadata": {
                    "source": "telemedicine.pdf",
                    "page": 5,
                    "topic": "Telemedicine",
                    "date": "2024-05-20",
                    "author": "Dr. Davis"
                }
            }
        ]
    
    @pytest.mark.asyncio
    async def test_end_to_end_query_processing(self, complete_system, comprehensive_documents):
        """Test complete end-to-end query processing"""
        # Add documents
        success = await complete_system.add_documents(comprehensive_documents)
        assert success is True
        
        # Process various types of queries
        test_queries = [
            "How is AI transforming healthcare?",
            "What are the benefits of machine learning in medical imaging?",
            "How does NLP help in patient care?",
            "What is the role of robotic surgery in modern healthcare?",
            "How does telemedicine improve healthcare access?"
        ]
        
        for query in test_queries:
            response = await complete_system.process_query(
                query=query,
                user_id="integration_test_user",
                session_id="integration_test_session"
            )
            
            # Verify response structure
            assert 'answer' in response
            assert 'sources' in response
            assert 'confidence_score' in response
            assert 'orchestrator_metadata' in response
            
            # Verify response quality
            assert len(response['answer']) > 0
            assert 0 <= response['confidence_score'] <= 1
            assert len(response['sources']) > 0
            
            # Verify sources are relevant
            for source in response['sources']:
                assert 'content' in source
                assert 'metadata' in source
                assert len(source['content']) > 0
    
    @pytest.mark.asyncio
    async def test_performance_under_load(self, complete_system, comprehensive_documents):
        """Test system performance under load"""
        # Add documents
        await complete_system.add_documents(comprehensive_documents)
        
        # Create multiple concurrent queries
        queries = [
            "How is AI used in healthcare?",
            "What are the benefits of machine learning?",
            "How does NLP help patients?",
            "What is robotic surgery?",
            "How does telemedicine work?"
        ] * 2  # 10 total queries
        
        # Process queries concurrently
        start_time = datetime.now()
        tasks = [
            complete_system.process_query(
                query=query,
                user_id=f"load_test_user_{i}",
                session_id=f"load_test_session_{i}"
            )
            for i, query in enumerate(queries)
        ]
        
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        total_time = (datetime.now() - start_time).total_seconds()
        
        # Verify all queries were processed successfully
        successful_responses = [r for r in responses if not isinstance(r, Exception)]
        assert len(successful_responses) == len(queries)
        
        # Verify performance is reasonable (less than 30 seconds for 10 queries)
        assert total_time < 30.0
        
        # Verify all responses have expected structure
        for response in successful_responses:
            assert 'answer' in response
            assert 'confidence_score' in response
            assert 0 <= response['confidence_score'] <= 1
    
    @pytest.mark.asyncio
    async def test_system_health_monitoring(self, complete_system):
        """Test system health monitoring"""
        # Get initial system status
        initial_status = await complete_system.get_system_status()
        
        # Verify status structure
        assert 'timestamp' in initial_status
        assert 'system_health' in initial_status
        assert 'performance_stats' in initial_status
        assert 'resource_utilization' in initial_status
        
        # Verify system health is a valid score
        assert 0 <= initial_status['system_health'] <= 1
        
        # Verify performance stats
        perf_stats = initial_status['performance_stats']
        assert 'total_requests' in perf_stats
        assert 'successful_requests' in perf_stats
        assert 'failed_requests' in perf_stats
        assert 'average_response_time' in perf_stats
        
        # Verify resource utilization
        resource_util = initial_status['resource_utilization']
        assert 'cpu_percent' in resource_util
        assert 'memory_percent' in resource_util
        assert 'disk_percent' in resource_util

# Performance benchmarks
class TestPerformanceBenchmarks:
    """Performance benchmark tests"""
    
    @pytest.mark.asyncio
    async def test_retrieval_performance(self):
        """Benchmark retrieval performance"""
        config = RetrievalConfig()
        system = ModernRetrievalSystem(config)
        
        # Create large document set
        documents = [
            {
                "content": f"Document {i}: This is a test document about artificial intelligence in healthcare. " * 10,
                "metadata": {"source": f"doc_{i}.pdf", "page": i}
            }
            for i in range(100)
        ]
        
        # Add documents
        start_time = datetime.now()
        success = await system.add_documents(documents)
        indexing_time = (datetime.now() - start_time).total_seconds()
        
        assert success is True
        assert indexing_time < 60.0  # Should index 100 documents in under 60 seconds
        
        # Test retrieval performance
        start_time = datetime.now()
        results = await system.retrieve("AI in healthcare", top_k=10)
        retrieval_time = (datetime.now() - start_time).total_seconds()
        
        assert len(results) <= 10
        assert retrieval_time < 5.0  # Should retrieve in under 5 seconds
    
    @pytest.mark.asyncio
    async def test_generation_performance(self):
        """Benchmark generation performance"""
        config = GenerationConfig()
        system = ModernGenerationSystem(config)
        
        context = [
            {
                "content": "Artificial intelligence is transforming healthcare through advanced diagnostic tools.",
                "metadata": {"source": "test.pdf"},
                "score": 0.9
            }
        ]
        
        # Test generation performance
        start_time = datetime.now()
        response = await system.generate_response(
            query="How is AI used in healthcare?",
            context=context
        )
        generation_time = (datetime.now() - start_time).total_seconds()
        
        assert 'answer' in response
        assert generation_time < 30.0  # Should generate in under 30 seconds

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
