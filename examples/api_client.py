"""
API client examples for interacting with the RAG system.
"""

import requests
import json
import time
from typing import Dict, Any, List


class RAGAPIClient:
    """Client for interacting with the RAG API."""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health."""
        try:
            response = self.session.get(f"{self.base_url}/health")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def query(self, question: str, **kwargs) -> Dict[str, Any]:
        """Send a query to the RAG system."""
        payload = {"question": question, **kwargs}
        
        try:
            response = self.session.post(f"{self.base_url}/query", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def stream_query(self, question: str, **kwargs):
        """Stream a query response."""
        payload = {"question": question, **kwargs}
        
        try:
            response = self.session.post(
                f"{self.base_url}/query/stream",
                json=payload,
                stream=True
            )
            response.raise_for_status()
            
            for line in response.iter_lines():
                if line:
                    try:
                        chunk = json.loads(line.decode())
                        yield chunk
                    except json.JSONDecodeError:
                        continue
        except requests.exceptions.RequestException as e:
            yield {"type": "error", "content": str(e)}
    
    def upload_documents(self, file_paths: List[str], **kwargs) -> Dict[str, Any]:
        """Upload documents to the system."""
        payload = {"file_paths": file_paths, **kwargs}
        
        try:
            response = self.session.post(f"{self.base_url}/documents/upload", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def batch_query(self, queries: List[str], **kwargs) -> Dict[str, Any]:
        """Process multiple queries in batch."""
        payload = {"queries": queries, **kwargs}
        
        try:
            response = self.session.post(f"{self.base_url}/query/batch", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def conversation(self, message: str, history: List[Dict] = None, **kwargs) -> Dict[str, Any]:
        """Send a conversational message."""
        payload = {
            "message": message,
            "conversation_history": history or [],
            **kwargs
        }
        
        try:
            response = self.session.post(f"{self.base_url}/conversation", json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics."""
        try:
            response = self.session.get(f"{self.base_url}/stats")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}
    
    def get_models(self) -> Dict[str, Any]:
        """Get available models."""
        try:
            response = self.session.get(f"{self.base_url}/models")
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}


def example_1_basic_query():
    """Example 1: Basic query."""
    print("Example 1: Basic Query")
    print("=" * 30)
    
    client = RAGAPIClient()
    
    # Check health
    health = client.health_check()
    if "error" in health:
        print(f"❌ API not available: {health['error']}")
        return
    
    print(f"✅ API Status: {health.get('status', 'unknown')}")
    
    # Send query
    result = client.query("What is artificial intelligence?")
    
    if "error" in result:
        print(f"❌ Query failed: {result['error']}")
        return
    
    print(f"Question: What is artificial intelligence?")
    print(f"Answer: {result['answer']}")
    print(f"Confidence: {result['confidence']:.3f}")
    print(f"Processing Time: {result['total_time']:.2f}s")


def example_2_streaming_query():
    """Example 2: Streaming query."""
    print("\nExample 2: Streaming Query")
    print("=" * 30)
    
    client = RAGAPIClient()
    
    query = "Explain how machine learning works"
    print(f"Question: {query}")
    print("Streaming response:")
    print("-" * 40)
    
    for chunk in client.stream_query(query):
        if chunk["type"] == "content":
            print(chunk["content"], end="", flush=True)
        elif chunk["type"] == "sources":
            print(f"\n\nSources: {len(chunk['content'])}")
        elif chunk["type"] == "done":
            print("\n\n✅ Streaming completed")
            break
        elif chunk["type"] == "error":
            print(f"\n❌ Error: {chunk['content']}")
            break


def example_3_different_prompt_types():
    """Example 3: Different prompt types."""
    print("\nExample 3: Different Prompt Types")
    print("=" * 30)
    
    client = RAGAPIClient()
    
    queries = [
        {
            "question": "What is deep learning?",
            "prompt_type": "qa",
            "description": "Question-Answering"
        },
        {
            "question": "Summarize the benefits of AI",
            "prompt_type": "summarization",
            "description": "Summarization"
        },
        {
            "question": "Analyze the impact of AI on society",
            "prompt_type": "analysis",
            "description": "Analysis"
        }
    ]
    
    for query_info in queries:
        result = client.query(**query_info)
        
        if "error" in result:
            print(f"❌ {query_info['description']} failed: {result['error']}")
            continue
        
        print(f"\n{query_info['description']}:")
        print(f"Question: {query_info['question']}")
        print(f"Answer: {result['answer'][:100]}...")
        print(f"Confidence: {result['confidence']:.3f}")


def example_4_batch_processing():
    """Example 4: Batch processing."""
    print("\nExample 4: Batch Processing")
    print("=" * 30)
    
    client = RAGAPIClient()
    
    queries = [
        "What is machine learning?",
        "How do neural networks work?",
        "What are the applications of NLP?",
        "Explain deep learning concepts"
    ]
    
    print(f"Processing {len(queries)} queries in batch...")
    
    result = client.batch_query(queries)
    
    if "error" in result:
        print(f"❌ Batch processing failed: {result['error']}")
        return
    
    print(f"✅ Batch processing completed")
    print(f"Success Count: {result['success_count']}")
    print(f"Error Count: {result['error_count']}")
    print(f"Total Time: {result['total_processing_time']:.2f}s")
    
    print("\nResults:")
    for i, query_result in enumerate(result['results'], 1):
        print(f"{i}. {query_result['answer'][:80]}...")
        print(f"   Confidence: {query_result['confidence']:.3f}")


def example_5_conversation():
    """Example 5: Conversational interface."""
    print("\nExample 5: Conversational Interface")
    print("=" * 30)
    
    client = RAGAPIClient()
    
    # Start conversation
    conversation_history = []
    
    messages = [
        "Hello, I'm interested in learning about AI",
        "What are the main types of machine learning?",
        "Can you explain supervised learning in more detail?",
        "What are some real-world applications?"
    ]
    
    for message in messages:
        print(f"\nHuman: {message}")
        
        result = client.conversation(
            message=message,
            history=conversation_history
        )
        
        if "error" in result:
            print(f"❌ Conversation error: {result['error']}")
            break
        
        print(f"Assistant: {result['response']}")
        
        # Update conversation history
        conversation_history.append({
            "human": message,
            "assistant": result['response']
        })


def example_6_document_upload():
    """Example 6: Document upload."""
    print("\nExample 6: Document Upload")
    print("=" * 30)
    
    client = RAGAPIClient()
    
    # Create sample document
    sample_doc = """
    Artificial Intelligence (AI) is a branch of computer science that aims to create 
    intelligent machines. AI systems can learn, reason, and make decisions. Key areas 
    include machine learning, natural language processing, computer vision, and robotics.
    """
    
    # Save sample document
    with open("temp_document.txt", "w") as f:
        f.write(sample_doc)
    
    # Upload document
    result = client.upload_documents(
        file_paths=["temp_document.txt"],
        chunk_method="recursive",
        chunk_size=500
    )
    
    if "error" in result:
        print(f"❌ Upload failed: {result['error']}")
    else:
        print(f"✅ Upload successful")
        print(f"Documents processed: {result['documents_processed']}")
        print(f"Chunks created: {result['chunks_created']}")
        print(f"Processing time: {result['processing_time']:.2f}s")
    
    # Clean up
    import os
    if os.path.exists("temp_document.txt"):
        os.remove("temp_document.txt")


def example_7_system_monitoring():
    """Example 7: System monitoring."""
    print("\nExample 7: System Monitoring")
    print("=" * 30)
    
    client = RAGAPIClient()
    
    # Get system stats
    stats = client.get_stats()
    if "error" in stats:
        print(f"❌ Stats error: {stats['error']}")
        return
    
    print("System Statistics:")
    print(f"Uptime: {stats.get('uptime', 0):.1f}s")
    
    llm_stats = stats.get('llm_stats', {})
    print(f"Available Models: {len(llm_stats.get('available_models', []))}")
    
    embedding_stats = stats.get('embedding_stats', {})
    print(f"Embedding Cache: {embedding_stats.get('cache_size', 0)}")
    
    retriever_stats = stats.get('retriever_stats', {})
    print(f"Total Documents: {retriever_stats.get('total_documents', 0)}")
    
    # Get available models
    models = client.get_models()
    if "error" not in models:
        print(f"\nAvailable Models:")
        print(f"LLM Models: {models.get('llm_models', [])}")
        print(f"Embedding Model: {models.get('embedding_model', 'Unknown')}")
        print(f"Prompt Types: {models.get('prompt_types', [])}")


def example_8_performance_testing():
    """Example 8: Performance testing."""
    print("\nExample 8: Performance Testing")
    print("=" * 30)
    
    client = RAGAPIClient()
    
    test_queries = [
        "What is artificial intelligence?",
        "How does machine learning work?",
        "What are neural networks?",
        "Explain deep learning",
        "What is natural language processing?"
    ]
    
    print(f"Running performance test with {len(test_queries)} queries...")
    
    start_time = time.time()
    results = []
    
    for i, query in enumerate(test_queries, 1):
        query_start = time.time()
        result = client.query(query)
        query_time = time.time() - query_start
        
        if "error" not in result:
            results.append({
                "query": query,
                "time": query_time,
                "confidence": result.get('confidence', 0),
                "tokens": result.get('tokens_used', 0)
            })
            print(f"Query {i}: {query_time:.2f}s (confidence: {result.get('confidence', 0):.3f})")
        else:
            print(f"Query {i}: Failed - {result['error']}")
    
    total_time = time.time() - start_time
    
    if results:
        avg_time = sum(r['time'] for r in results) / len(results)
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        total_tokens = sum(r['tokens'] for r in results)
        
        print(f"\nPerformance Summary:")
        print(f"Total Time: {total_time:.2f}s")
        print(f"Average Query Time: {avg_time:.2f}s")
        print(f"Average Confidence: {avg_confidence:.3f}")
        print(f"Total Tokens: {total_tokens}")
        print(f"Queries per Second: {len(results)/total_time:.2f}")


def main():
    """Run all API client examples."""
    print("🌐 RAG API Client Examples")
    print("=" * 50)
    
    try:
        example_1_basic_query()
        example_2_streaming_query()
        example_3_different_prompt_types()
        example_4_batch_processing()
        example_5_conversation()
        example_6_document_upload()
        example_7_system_monitoring()
        example_8_performance_testing()
        
        print("\n✅ All API examples completed!")
        print("\nMake sure the RAG API server is running:")
        print("python -m uvicorn src.api.main:app --reload")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure the API server is running and accessible.")


if __name__ == "__main__":
    main()
