#!/usr/bin/env python3
"""
Comprehensive API Endpoint Testing Script
Tests all RAG system API endpoints for functionality
"""

import asyncio
import aiohttp
import json
import time
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

class APITester:
    """Comprehensive API endpoint tester"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.test_results = []
        self.session = None
        
        # Test endpoints
        self.endpoints = {
            'health': '/health',
            'stats': '/stats',
            'query': '/query',
            'conversation': '/conversation',
            'batch_query': '/query/batch',
            'models': '/models',
            'prompts': '/prompts',
            'upload': '/documents/upload'
        }
        
        # Test data
        self.test_queries = [
            "What is a traditional tattoo?",
            "How much does a sleeve tattoo cost?",
            "What's the healing process for tattoos?",
            "Tell me about geometric tattoo styles",
            "What are the best aftercare practices?"
        ]
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def test_all_endpoints(self):
        """Test all API endpoints"""
        logger.info("🧪 Starting comprehensive API endpoint testing...")
        
        tests = [
            self.test_health_endpoint,
            self.test_stats_endpoint,
            self.test_query_endpoint,
            self.test_conversation_endpoint,
            self.test_batch_query_endpoint,
            self.test_models_endpoint,
            self.test_prompts_endpoint,
            self.test_upload_endpoint
        ]
        
        for test in tests:
            try:
                await test()
            except Exception as e:
                logger.error(f"Test failed: {test.__name__}: {e}")
                self.test_results.append({
                    'test': test.__name__,
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
        
        await self.generate_test_report()
    
    async def test_health_endpoint(self):
        """Test health endpoint"""
        logger.info("Testing health endpoint...")
        
        start_time = time.time()
        async with self.session.get(f"{self.base_url}/health") as response:
            response_time = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                
                # Validate response structure
                required_fields = ['status', 'version', 'timestamp', 'components']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    raise ValueError(f"Missing required fields: {missing_fields}")
                
                self.test_results.append({
                    'test': 'health_endpoint',
                    'status': 'passed',
                    'response_time': response_time,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info("✅ Health endpoint test passed")
            else:
                raise ValueError(f"Health endpoint returned status {response.status}")
    
    async def test_stats_endpoint(self):
        """Test stats endpoint"""
        logger.info("Testing stats endpoint...")
        
        start_time = time.time()
        async with self.session.get(f"{self.base_url}/stats") as response:
            response_time = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                
                # Validate response structure
                required_fields = ['llm_stats', 'embedding_stats', 'retriever_stats', 'uptime']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    raise ValueError(f"Missing required fields: {missing_fields}")
                
                self.test_results.append({
                    'test': 'stats_endpoint',
                    'status': 'passed',
                    'response_time': response_time,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info("✅ Stats endpoint test passed")
            else:
                raise ValueError(f"Stats endpoint returned status {response.status}")
    
    async def test_query_endpoint(self):
        """Test query endpoint"""
        logger.info("Testing query endpoint...")
        
        test_payload = {
            "question": self.test_queries[0],
            "prompt_type": "qa",
            "top_k": 5,
            "rerank_top_k": 3,
            "include_sources": True,
            "system_role": "assistant",
            "temperature": 0.1,
            "max_tokens": 500
        }
        
        start_time = time.time()
        async with self.session.post(
            f"{self.base_url}/query",
            json=test_payload
        ) as response:
            response_time = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                
                # Validate response structure
                required_fields = ['answer', 'sources', 'confidence', 'retrieval_time', 'generation_time']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    raise ValueError(f"Missing required fields: {missing_fields}")
                
                # Validate answer quality
                if not data.get('answer') or len(data['answer']) < 10:
                    raise ValueError("Answer is too short or empty")
                
                self.test_results.append({
                    'test': 'query_endpoint',
                    'status': 'passed',
                    'response_time': response_time,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info("✅ Query endpoint test passed")
            else:
                error_text = await response.text()
                raise ValueError(f"Query endpoint returned status {response.status}: {error_text}")
    
    async def test_conversation_endpoint(self):
        """Test conversation endpoint"""
        logger.info("Testing conversation endpoint...")
        
        test_payload = {
            "message": "I'm interested in getting a tattoo",
            "conversation_history": [
                {"human": "Hello", "assistant": "Hi! How can I help you with tattoos today?"}
            ],
            "top_k": 5,
            "system_role": "assistant",
            "temperature": 0.1
        }
        
        start_time = time.time()
        async with self.session.post(
            f"{self.base_url}/conversation",
            json=test_payload
        ) as response:
            response_time = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                
                # Validate response structure
                required_fields = ['response', 'conversation_id', 'sources', 'confidence']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    raise ValueError(f"Missing required fields: {missing_fields}")
                
                self.test_results.append({
                    'test': 'conversation_endpoint',
                    'status': 'passed',
                    'response_time': response_time,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info("✅ Conversation endpoint test passed")
            else:
                error_text = await response.text()
                raise ValueError(f"Conversation endpoint returned status {response.status}: {error_text}")
    
    async def test_batch_query_endpoint(self):
        """Test batch query endpoint"""
        logger.info("Testing batch query endpoint...")
        
        test_payload = {
            "queries": self.test_queries[:3],  # Test with first 3 queries
            "prompt_type": "qa",
            "top_k": 5,
            "include_sources": True
        }
        
        start_time = time.time()
        async with self.session.post(
            f"{self.base_url}/query/batch",
            json=test_payload
        ) as response:
            response_time = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                
                # Validate response structure
                required_fields = ['results', 'total_processing_time', 'success_count', 'error_count']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    raise ValueError(f"Missing required fields: {missing_fields}")
                
                # Validate results
                if not isinstance(data['results'], list):
                    raise ValueError("Results should be a list")
                
                if len(data['results']) != len(test_payload['queries']):
                    raise ValueError("Number of results doesn't match number of queries")
                
                self.test_results.append({
                    'test': 'batch_query_endpoint',
                    'status': 'passed',
                    'response_time': response_time,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info("✅ Batch query endpoint test passed")
            else:
                error_text = await response.text()
                raise ValueError(f"Batch query endpoint returned status {response.status}: {error_text}")
    
    async def test_models_endpoint(self):
        """Test models endpoint"""
        logger.info("Testing models endpoint...")
        
        start_time = time.time()
        async with self.session.get(f"{self.base_url}/models") as response:
            response_time = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                
                # Validate response structure
                required_fields = ['llm_models', 'embedding_model', 'prompt_types']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    raise ValueError(f"Missing required fields: {missing_fields}")
                
                self.test_results.append({
                    'test': 'models_endpoint',
                    'status': 'passed',
                    'response_time': response_time,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info("✅ Models endpoint test passed")
            else:
                raise ValueError(f"Models endpoint returned status {response.status}")
    
    async def test_prompts_endpoint(self):
        """Test prompts endpoint"""
        logger.info("Testing prompts endpoint...")
        
        start_time = time.time()
        async with self.session.get(f"{self.base_url}/prompts") as response:
            response_time = time.time() - start_time
            
            if response.status == 200:
                data = await response.json()
                
                # Validate response structure
                if not isinstance(data, dict):
                    raise ValueError("Response should be a dictionary")
                
                if len(data) == 0:
                    raise ValueError("No prompt types available")
                
                self.test_results.append({
                    'test': 'prompts_endpoint',
                    'status': 'passed',
                    'response_time': response_time,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info("✅ Prompts endpoint test passed")
            else:
                raise ValueError(f"Prompts endpoint returned status {response.status}")
    
    async def test_upload_endpoint(self):
        """Test upload endpoint"""
        logger.info("Testing upload endpoint...")
        
        # Create a test document payload
        test_payload = {
            "file_paths": ["test_document.txt"],
            "chunk_method": "recursive",
            "chunk_size": 1000,
            "chunk_overlap": 200
        }
        
        start_time = time.time()
        async with self.session.post(
            f"{self.base_url}/documents/upload",
            json=test_payload
        ) as response:
            response_time = time.time() - start_time
            
            # Note: This test might fail if test document doesn't exist, which is expected
            if response.status == 200:
                data = await response.json()
                
                # Validate response structure
                required_fields = ['success', 'documents_processed', 'chunks_created', 'processing_time']
                missing_fields = [field for field in required_fields if field not in data]
                
                if missing_fields:
                    raise ValueError(f"Missing required fields: {missing_fields}")
                
                self.test_results.append({
                    'test': 'upload_endpoint',
                    'status': 'passed',
                    'response_time': response_time,
                    'data': data,
                    'timestamp': datetime.now().isoformat()
                })
                logger.info("✅ Upload endpoint test passed")
            elif response.status == 400:
                # Expected for missing test file
                self.test_results.append({
                    'test': 'upload_endpoint',
                    'status': 'expected_failure',
                    'response_time': response_time,
                    'note': 'Expected failure due to missing test file',
                    'timestamp': datetime.now().isoformat()
                })
                logger.info("⚠️  Upload endpoint test expected failure (no test file)")
            else:
                error_text = await response.text()
                raise ValueError(f"Upload endpoint returned status {response.status}: {error_text}")
    
    async def test_nextjs_endpoints(self):
        """Test Next.js API endpoints"""
        logger.info("Testing Next.js API endpoints...")
        
        nextjs_base_url = "http://localhost:3000"
        nextjs_endpoints = {
            'tattoo_knowledge': '/api/tattoo-knowledge',
            'customer_service': '/api/customer-service',
            'sales': '/api/sales',
            'conversation': '/api/conversation',
            'analytics': '/api/analytics',
            'pipeline_status': '/api/pipelines/status'
        }
        
        for name, endpoint in nextjs_endpoints.items():
            try:
                start_time = time.time()
                async with self.session.get(f"{nextjs_base_url}{endpoint}") as response:
                    response_time = time.time() - start_time
                    
                    if response.status == 200:
                        data = await response.json()
                        
                        self.test_results.append({
                            'test': f'nextjs_{name}_endpoint',
                            'status': 'passed',
                            'response_time': response_time,
                            'data': data,
                            'timestamp': datetime.now().isoformat()
                        })
                        logger.info(f"✅ Next.js {name} endpoint test passed")
                    else:
                        self.test_results.append({
                            'test': f'nextjs_{name}_endpoint',
                            'status': 'failed',
                            'response_time': response_time,
                            'status_code': response.status,
                            'timestamp': datetime.now().isoformat()
                        })
                        logger.warning(f"⚠️  Next.js {name} endpoint returned status {response.status}")
                        
            except Exception as e:
                self.test_results.append({
                    'test': f'nextjs_{name}_endpoint',
                    'status': 'failed',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
                logger.error(f"❌ Next.js {name} endpoint test failed: {e}")
    
    async def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("📊 Generating test report...")
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'passed'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'failed'])
        expected_failures = len([r for r in self.test_results if r['status'] == 'expected_failure'])
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'expected_failures': expected_failures,
                'success_rate': success_rate
            },
            'test_results': self.test_results,
            'recommendations': self.generate_recommendations()
        }
        
        # Save report
        with open('logs/api_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📈 Test Results Summary:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Passed: {passed_tests}")
        logger.info(f"   Failed: {failed_tests}")
        logger.info(f"   Expected Failures: {expected_failures}")
        logger.info(f"   Success Rate: {success_rate:.1f}%")
        
        if success_rate >= 80:
            logger.info("🎉 API testing completed successfully!")
        else:
            logger.warning("⚠️  API testing shows issues that need attention")
        
        return report
    
    def generate_recommendations(self) -> List[str]:
        """Generate recommendations based on test results"""
        recommendations = []
        
        failed_tests = [r for r in self.test_results if r['status'] == 'failed']
        
        if len(failed_tests) > 0:
            recommendations.append("Review failed tests and fix underlying issues")
        
        slow_tests = [r for r in self.test_results if r.get('response_time', 0) > 5.0]
        if len(slow_tests) > 0:
            recommendations.append("Optimize slow endpoints to improve response times")
        
        if len(self.test_results) == 0:
            recommendations.append("No tests were run - check API availability")
        
        return recommendations

async def main():
    """Main testing function"""
    logger.info("🚀 Starting API endpoint testing...")
    
    async with APITester() as tester:
        await tester.test_all_endpoints()
        await tester.test_nextjs_endpoints()

if __name__ == "__main__":
    asyncio.run(main())
