#!/usr/bin/env python3
"""
Evaluation script for the RAG system.
"""

import os
import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from evaluation.rag_evaluator import RAGEvaluator
from generation.rag_generator import RAGGenerator
from generation.llm_manager import LLMManager
from retrieval.embedding_generator import EmbeddingGenerator
from retrieval.vector_store import VectorStore
from retrieval.hybrid_search import HybridRetriever
from retrieval.reranker import Reranker


def load_test_data(test_file: str) -> Dict[str, List[str]]:
    """Load test data from JSON file."""
    with open(test_file, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_sample_test_data(output_file: str):
    """Create sample test data for evaluation."""
    sample_data = {
        "questions": [
            "What is artificial intelligence?",
            "How does machine learning work?",
            "What are the benefits of deep learning?",
            "Explain neural networks",
            "What is natural language processing?"
        ],
        "ground_truths": [
            "Artificial intelligence (AI) is the simulation of human intelligence in machines that are programmed to think and learn like humans.",
            "Machine learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed.",
            "Deep learning offers benefits like automatic feature extraction, handling of unstructured data, and improved accuracy with large datasets.",
            "Neural networks are computing systems inspired by biological neural networks that can learn to perform tasks by considering examples.",
            "Natural language processing (NLP) is a branch of AI that helps computers understand, interpret and manipulate human language."
        ],
        "contexts": [
            ["AI is the simulation of human intelligence in machines.", "Machine learning is a subset of AI."],
            ["Machine learning enables computers to learn from experience.", "ML algorithms improve through training data."],
            ["Deep learning uses neural networks with multiple layers.", "Deep learning excels at pattern recognition."],
            ["Neural networks are inspired by biological neurons.", "Neural networks can learn complex patterns."],
            ["NLP helps computers understand human language.", "NLP combines computational linguistics with machine learning."]
        ]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(sample_data, f, indent=2)
    
    print(f"Sample test data created: {output_file}")


def initialize_rag_system() -> RAGGenerator:
    """Initialize the RAG system for evaluation."""
    print("Initializing RAG system...")
    
    # Load environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_api_key:
        print("Warning: OPENAI_API_KEY not found. Some features may not work.")
    
    # Initialize components
    llm_manager = LLMManager(
        openai_api_key=openai_api_key,
        anthropic_api_key=anthropic_api_key
    )
    
    embedding_generator = EmbeddingGenerator(
        model_name=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        openai_api_key=openai_api_key
    )
    
    vector_store = VectorStore(
        vector_db_type=os.getenv("VECTOR_DB_TYPE", "chroma"),
        persist_directory=os.getenv("VECTOR_DB_PATH", "./chroma_db")
    )
    
    hybrid_retriever = HybridRetriever(
        vector_store=vector_store,
        documents=[]  # Will be populated when documents are added
    )
    
    # Initialize reranker if possible
    reranker = None
    try:
        reranker = Reranker()
        print("Reranker initialized successfully")
    except Exception as e:
        print(f"Warning: Could not initialize reranker: {e}")
    
    # Create RAG generator
    rag_generator = RAGGenerator(
        llm_manager=llm_manager,
        embedding_generator=embedding_generator,
        hybrid_retriever=hybrid_retriever,
        reranker=reranker,
        use_reranking=reranker is not None
    )
    
    print("RAG system initialized successfully")
    return rag_generator


def run_evaluation(
    test_data: Dict[str, List[str]],
    rag_generator: RAGGenerator,
    output_dir: str = "./evaluation_results"
) -> Dict[str, Any]:
    """Run comprehensive evaluation."""
    print("Starting evaluation...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Initialize evaluator
    evaluator = RAGEvaluator(
        embedding_model=os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2"),
        use_ragas=True
    )
    
    # Run evaluation
    results = evaluator.evaluate_rag_system(
        test_questions=test_data["questions"],
        ground_truths=test_data["ground_truths"],
        rag_system=rag_generator,
        contexts=test_data.get("contexts")
    )
    
    # Save results
    results_file = os.path.join(output_dir, "evaluation_results.json")
    with open(results_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str)
    
    print(f"Results saved to: {results_file}")
    
    # Generate report
    report_file = os.path.join(output_dir, "evaluation_report.md")
    report = evaluator.create_evaluation_report(results, report_file)
    
    print(f"Report saved to: {report_file}")
    
    # Print summary
    summary = results.get("summary", {})
    print("\n" + "="*50)
    print("EVALUATION SUMMARY")
    print("="*50)
    print(f"Overall Score: {summary.get('overall_score', 0.0):.3f}")
    
    key_metrics = summary.get("key_metrics", {})
    for metric, value in key_metrics.items():
        print(f"{metric}: {value:.3f}")
    
    recommendations = summary.get("recommendations", [])
    if recommendations:
        print("\nRecommendations:")
        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. {rec}")
    
    return results


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="Evaluate RAG system")
    parser.add_argument(
        "--test-data",
        type=str,
        default="test_data.json",
        help="Path to test data JSON file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./evaluation_results",
        help="Output directory for results"
    )
    parser.add_argument(
        "--create-sample",
        action="store_true",
        help="Create sample test data"
    )
    parser.add_argument(
        "--quick-test",
        action="store_true",
        help="Run quick test with minimal data"
    )
    
    args = parser.parse_args()
    
    # Create sample data if requested
    if args.create_sample:
        create_sample_test_data(args.test_data)
        print("Sample test data created. Please add your documents to the RAG system first.")
        return
    
    # Check if test data exists
    if not os.path.exists(args.test_data):
        print(f"Test data file not found: {args.test_data}")
        print("Use --create-sample to create sample test data")
        return
    
    # Load test data
    print(f"Loading test data from: {args.test_data}")
    test_data = load_test_data(args.test_data)
    
    # Quick test mode
    if args.quick_test:
        test_data["questions"] = test_data["questions"][:2]
        test_data["ground_truths"] = test_data["ground_truths"][:2]
        if "contexts" in test_data:
            test_data["contexts"] = test_data["contexts"][:2]
        print("Running in quick test mode (2 questions)")
    
    # Initialize RAG system
    try:
        rag_generator = initialize_rag_system()
    except Exception as e:
        print(f"Error initializing RAG system: {e}")
        return
    
    # Run evaluation
    try:
        results = run_evaluation(test_data, rag_generator, args.output_dir)
        print("\nEvaluation completed successfully!")
    except Exception as e:
        print(f"Error during evaluation: {e}")
        return


if __name__ == "__main__":
    main()

