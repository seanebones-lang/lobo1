"""
Basic usage examples for the RAG system.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from generation.rag_generator import RAGGenerator
from generation.llm_manager import LLMManager
from generation.prompt_manager import PromptManager
from retrieval.embedding_generator import EmbeddingGenerator
from retrieval.vector_store import VectorStore
from retrieval.hybrid_search import HybridRetriever
from data_processing.document_processor import DocumentProcessor


def example_1_basic_rag():
    """Example 1: Basic RAG setup and usage."""
    print("Example 1: Basic RAG Setup")
    print("=" * 40)
    
    # Initialize components
    llm_manager = LLMManager(openai_api_key=os.getenv("OPENAI_API_KEY"))
    embedding_generator = EmbeddingGenerator(openai_api_key=os.getenv("OPENAI_API_KEY"))
    vector_store = VectorStore()
    hybrid_retriever = HybridRetriever(vector_store, documents=[])
    
    # Create RAG generator
    rag_generator = RAGGenerator(
        llm_manager=llm_manager,
        embedding_generator=embedding_generator,
        hybrid_retriever=hybrid_retriever
    )
    
    # Process documents
    processor = DocumentProcessor()
    documents = processor.process_documents(
        file_paths=["data/ai_basics.txt"],
        chunk_method="recursive"
    )
    
    # Add documents to vector store
    texts = [doc.page_content for doc in documents]
    embeddings = embedding_generator.generate_embeddings(texts)
    vector_store.add_documents(texts, embeddings)
    hybrid_retriever.update_documents(texts)
    
    # Query the system
    result = rag_generator.generate_answer(
        query="What is artificial intelligence?",
        prompt_type="qa"
    )
    
    print(f"Question: What is artificial intelligence?")
    print(f"Answer: {result['answer']}")
    print(f"Confidence: {result['confidence']:.3f}")


def example_2_different_prompt_types():
    """Example 2: Using different prompt types."""
    print("\nExample 2: Different Prompt Types")
    print("=" * 40)
    
    # Initialize RAG system (simplified)
    rag_generator = initialize_simple_rag()
    
    prompt_types = [
        ("qa", "What is machine learning?"),
        ("summarization", "Summarize the key concepts in AI"),
        ("analysis", "Analyze the benefits and challenges of AI"),
        ("creative_writing", "Write a creative story about AI")
    ]
    
    for prompt_type, question in prompt_types:
        result = rag_generator.generate_answer(
            query=question,
            prompt_type=prompt_type,
            top_k=3
        )
        print(f"\nPrompt Type: {prompt_type}")
        print(f"Question: {question}")
        print(f"Answer: {result['answer'][:100]}...")


def example_3_streaming_responses():
    """Example 3: Streaming responses."""
    print("\nExample 3: Streaming Responses")
    print("=" * 40)
    
    rag_generator = initialize_simple_rag()
    
    query = "Explain how neural networks work"
    print(f"Question: {query}")
    print("Streaming response:")
    
    for chunk in rag_generator.generate_streaming_answer(query=query):
        if chunk["type"] == "content":
            print(chunk["content"], end="", flush=True)
        elif chunk["type"] == "done":
            print("\n\nStreaming completed!")


def example_4_custom_prompts():
    """Example 4: Custom prompt engineering."""
    print("\nExample 4: Custom Prompts")
    print("=" * 40)
    
    # Create custom prompt
    prompt_manager = PromptManager()
    custom_prompt = prompt_manager.create_custom_prompt(
        template="""
You are a {role} with expertise in {domain}.
Answer the following question in a {style} manner:

Question: {question}
Context: {context}

Answer:
""",
        prompt_name="custom_expert"
    )
    
    print("Custom prompt created successfully!")
    print("Available prompt types:", prompt_manager.get_available_prompts())


def example_5_batch_processing():
    """Example 5: Batch processing multiple queries."""
    print("\nExample 5: Batch Processing")
    print("=" * 40)
    
    rag_generator = initialize_simple_rag()
    
    queries = [
        "What is deep learning?",
        "How does natural language processing work?",
        "What are the applications of AI?"
    ]
    
    results = []
    for query in queries:
        result = rag_generator.generate_answer(query=query, top_k=3)
        results.append({
            "query": query,
            "answer": result["answer"][:100] + "...",
            "confidence": result["confidence"]
        })
    
    print("Batch processing results:")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['query']}")
        print(f"   Answer: {result['answer']}")
        print(f"   Confidence: {result['confidence']:.3f}")


def example_6_evaluation():
    """Example 6: System evaluation."""
    print("\nExample 6: System Evaluation")
    print("=" * 40)
    
    from evaluation.rag_evaluator import RAGEvaluator
    
    rag_generator = initialize_simple_rag()
    evaluator = RAGEvaluator()
    
    # Test data
    test_questions = ["What is AI?", "How does ML work?"]
    ground_truths = ["AI is artificial intelligence", "ML learns from data"]
    
    # Run evaluation
    results = evaluator.evaluate_rag_system(
        test_questions=test_questions,
        ground_truths=ground_truths,
        rag_system=rag_generator
    )
    
    # Print results
    summary = results.get("summary", {})
    print(f"Overall Score: {summary.get('overall_score', 0.0):.3f}")
    
    key_metrics = summary.get("key_metrics", {})
    for metric, value in key_metrics.items():
        print(f"{metric}: {value:.3f}")


def example_7_monitoring():
    """Example 7: System monitoring."""
    print("\nExample 7: System Monitoring")
    print("=" * 40)
    
    from evaluation.monitoring import RAGMonitor
    
    # Initialize monitor
    monitor = RAGMonitor(experiment_name="rag_demo")
    
    # Log some queries
    monitor.log_query(
        query="What is machine learning?",
        response="Machine learning is a subset of AI...",
        sources=[{"text": "ML is AI subset", "score": 0.9}],
        confidence=0.85,
        processing_time=1.2,
        model_used="gpt-4",
        tokens_used=150
    )
    
    # Get analytics
    analytics = monitor.get_query_analytics()
    print(f"Total Queries: {analytics.get('total_queries', 0)}")
    print(f"Average Confidence: {analytics.get('average_confidence', 0):.3f}")
    print(f"Average Processing Time: {analytics.get('average_processing_time', 0):.3f}s")


def initialize_simple_rag():
    """Initialize a simple RAG system for examples."""
    # This is a simplified version for demonstration
    # In practice, you'd use the full initialization from the main system
    
    llm_manager = LLMManager(openai_api_key=os.getenv("OPENAI_API_KEY"))
    embedding_generator = EmbeddingGenerator(openai_api_key=os.getenv("OPENAI_API_KEY"))
    vector_store = VectorStore()
    hybrid_retriever = HybridRetriever(vector_store, documents=[])
    
    return RAGGenerator(
        llm_manager=llm_manager,
        embedding_generator=embedding_generator,
        hybrid_retriever=hybrid_retriever
    )


def main():
    """Run all examples."""
    print("🤖 RAG System Usage Examples")
    print("=" * 50)
    
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not found.")
        print("   Some examples may not work without proper API keys.")
        print("   Please set your API keys in the .env file.")
        print()
    
    try:
        example_1_basic_rag()
        example_2_different_prompt_types()
        example_3_streaming_responses()
        example_4_custom_prompts()
        example_5_batch_processing()
        example_6_evaluation()
        example_7_monitoring()
        
        print("\n✅ All examples completed successfully!")
        print("\nFor more advanced usage, see the main documentation.")
        
    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        print("Make sure you have set up the environment properly.")


if __name__ == "__main__":
    main()
