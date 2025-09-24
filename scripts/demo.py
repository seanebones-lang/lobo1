#!/usr/bin/env python3
"""
Demo script to showcase the RAG system capabilities.
"""

import os
import sys
import time
import json
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

from generation.rag_generator import RAGGenerator
from generation.llm_manager import LLMManager
from generation.prompt_manager import PromptManager
from retrieval.embedding_generator import EmbeddingGenerator
from retrieval.vector_store import VectorStore
from retrieval.hybrid_search import HybridRetriever
from retrieval.reranker import Reranker
from data_processing.document_processor import DocumentProcessor
from evaluation.rag_evaluator import RAGEvaluator
from evaluation.monitoring import RAGMonitor


def create_sample_documents():
    """Create sample documents for demonstration."""
    sample_docs = {
        "ai_basics.txt": """
Artificial Intelligence (AI) is a branch of computer science that aims to create intelligent machines that can perform tasks that typically require human intelligence. AI systems can learn, reason, perceive, and make decisions.

Key areas of AI include:
- Machine Learning: Algorithms that improve through experience
- Natural Language Processing: Understanding and generating human language
- Computer Vision: Interpreting visual information
- Robotics: Creating intelligent machines that can interact with the physical world

AI has applications in healthcare, finance, transportation, entertainment, and many other fields. The goal is to create systems that can assist humans and solve complex problems.
        """,
        
        "machine_learning.txt": """
Machine Learning (ML) is a subset of artificial intelligence that focuses on algorithms and statistical models that enable computer systems to improve their performance on a specific task through experience.

Types of Machine Learning:
1. Supervised Learning: Learning with labeled training data
2. Unsupervised Learning: Finding patterns in data without labels
3. Reinforcement Learning: Learning through interaction with an environment

Popular ML algorithms include:
- Linear Regression
- Decision Trees
- Neural Networks
- Support Vector Machines
- Random Forests

Machine learning is used in recommendation systems, image recognition, speech processing, and predictive analytics.
        """,
        
        "deep_learning.txt": """
Deep Learning is a subset of machine learning that uses artificial neural networks with multiple layers (deep networks) to model and understand complex patterns in data.

Key concepts:
- Neural Networks: Computing systems inspired by biological neural networks
- Deep Networks: Networks with many hidden layers
- Backpropagation: Algorithm for training neural networks
- Convolutional Neural Networks (CNNs): For image processing
- Recurrent Neural Networks (RNNs): For sequential data
- Transformers: Modern architecture for natural language processing

Deep learning has revolutionized fields like computer vision, natural language processing, and speech recognition. It's behind technologies like self-driving cars, voice assistants, and image generation.
        """,
        
        "nlp.txt": """
Natural Language Processing (NLP) is a field of artificial intelligence that focuses on the interaction between computers and humans through natural language.

NLP tasks include:
- Text Classification: Categorizing text into predefined classes
- Sentiment Analysis: Determining emotional tone of text
- Named Entity Recognition: Identifying entities in text
- Machine Translation: Translating between languages
- Question Answering: Answering questions based on text
- Text Summarization: Creating concise summaries

Modern NLP uses transformer models like BERT, GPT, and T5. These models have achieved human-level performance on many language tasks.

Applications include chatbots, search engines, language translation services, and content generation.
        """
    }
    
    # Create data directory
    os.makedirs("data", exist_ok=True)
    
    # Write sample documents
    for filename, content in sample_docs.items():
        filepath = Path("data") / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        print(f"Created sample document: {filepath}")
    
    return list(sample_docs.keys())


def initialize_rag_system():
    """Initialize the complete RAG system."""
    print("🔧 Initializing RAG System...")
    
    # Load environment variables
    openai_api_key = os.getenv("OPENAI_API_KEY")
    anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
    
    if not openai_api_key:
        print("⚠️  Warning: OPENAI_API_KEY not found. Some features may not work.")
        print("   Please set your OpenAI API key in the .env file")
    
    # Initialize components
    print("   📝 Initializing LLM Manager...")
    llm_manager = LLMManager(
        openai_api_key=openai_api_key,
        anthropic_api_key=anthropic_api_key
    )
    
    print("   🔤 Initializing Embedding Generator...")
    embedding_generator = EmbeddingGenerator(
        model_name=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"),
        openai_api_key=openai_api_key
    )
    
    print("   🗄️  Initializing Vector Store...")
    vector_store = VectorStore(
        vector_db_type=os.getenv("VECTOR_DB_TYPE", "chroma"),
        persist_directory=os.getenv("VECTOR_DB_PATH", "./chroma_db")
    )
    
    print("   🔍 Initializing Hybrid Retriever...")
    hybrid_retriever = HybridRetriever(
        vector_store=vector_store,
        documents=[]  # Will be populated with documents
    )
    
    print("   🎯 Initializing Reranker...")
    reranker = None
    try:
        reranker = Reranker()
        print("   ✅ Reranker initialized successfully")
    except Exception as e:
        print(f"   ⚠️  Reranker initialization failed: {e}")
    
    print("   🤖 Initializing RAG Generator...")
    rag_generator = RAGGenerator(
        llm_manager=llm_manager,
        embedding_generator=embedding_generator,
        hybrid_retriever=hybrid_retriever,
        reranker=reranker,
        use_reranking=reranker is not None
    )
    
    print("✅ RAG System initialized successfully!")
    return rag_generator


def load_documents(rag_generator, file_paths):
    """Load and process documents into the RAG system."""
    print(f"📚 Loading {len(file_paths)} documents...")
    
    # Initialize document processor
    processor = DocumentProcessor()
    
    # Process documents
    documents = processor.process_documents(
        file_paths=file_paths,
        chunk_method="recursive",
        chunk_size=1000,
        chunk_overlap=200
    )
    
    if not documents:
        print("❌ No documents could be processed")
        return False
    
    print(f"   📄 Created {len(documents)} chunks from documents")
    
    # Extract texts and metadata
    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]
    
    # Generate embeddings
    print("   🔤 Generating embeddings...")
    embeddings = rag_generator.embedding_generator.generate_embeddings(texts)
    
    # Add to vector store
    print("   💾 Storing in vector database...")
    ids = rag_generator.hybrid_retriever.vector_store.add_documents(
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )
    
    # Update hybrid retriever
    rag_generator.hybrid_retriever.update_documents(texts)
    
    print(f"✅ Successfully loaded {len(documents)} document chunks")
    return True


def run_demo_queries(rag_generator):
    """Run demonstration queries."""
    print("\n🎯 Running Demo Queries")
    print("=" * 50)
    
    demo_queries = [
        {
            "question": "What is artificial intelligence?",
            "prompt_type": "qa",
            "description": "Basic question about AI"
        },
        {
            "question": "Explain the difference between machine learning and deep learning",
            "prompt_type": "analysis",
            "description": "Comparative analysis"
        },
        {
            "question": "Summarize the key concepts in natural language processing",
            "prompt_type": "summarization",
            "description": "Summarization task"
        },
        {
            "question": "What are the main types of machine learning algorithms?",
            "prompt_type": "qa",
            "description": "List-based question"
        }
    ]
    
    for i, query_info in enumerate(demo_queries, 1):
        print(f"\n📝 Query {i}: {query_info['description']}")
        print(f"Question: {query_info['question']}")
        print("-" * 40)
        
        try:
            start_time = time.time()
            
            result = rag_generator.generate_answer(
                query=query_info['question'],
                prompt_type=query_info['prompt_type'],
                top_k=5,
                rerank_top_k=3,
                include_sources=True
            )
            
            processing_time = time.time() - start_time
            
            print(f"Answer: {result['answer']}")
            print(f"Confidence: {result['confidence']:.3f}")
            print(f"Processing Time: {processing_time:.2f}s")
            print(f"Sources: {len(result['sources'])}")
            
            if result['sources']:
                print("Top Sources:")
                for j, source in enumerate(result['sources'][:2], 1):
                    print(f"  {j}. {source['text'][:100]}... (Score: {source['score']:.3f})")
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
        
        print()


def run_streaming_demo(rag_generator):
    """Demonstrate streaming responses."""
    print("\n🌊 Streaming Response Demo")
    print("=" * 50)
    
    query = "Explain how neural networks work in deep learning"
    print(f"Question: {query}")
    print("Streaming response:")
    print("-" * 40)
    
    try:
        for chunk in rag_generator.generate_streaming_answer(
            query=query,
            prompt_type="qa",
            top_k=3
        ):
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
    except Exception as e:
        print(f"❌ Streaming error: {e}")


def run_evaluation_demo(rag_generator):
    """Run evaluation demonstration."""
    print("\n📊 Evaluation Demo")
    print("=" * 50)
    
    # Create test data
    test_data = {
        "questions": [
            "What is machine learning?",
            "How do neural networks work?",
            "What are the applications of NLP?"
        ],
        "ground_truths": [
            "Machine learning is a subset of AI that enables computers to learn from data.",
            "Neural networks are computing systems inspired by biological neural networks.",
            "NLP applications include chatbots, translation, and text analysis."
        ],
        "contexts": [
            ["Machine learning algorithms improve through experience.", "ML is used in many applications."],
            ["Neural networks have multiple layers.", "They can learn complex patterns."],
            ["NLP helps computers understand language.", "It's used in many real-world applications."]
        ]
    }
    
    print("Running evaluation with test data...")
    
    try:
        evaluator = RAGEvaluator()
        results = evaluator.evaluate_rag_system(
            test_questions=test_data["questions"],
            ground_truths=test_data["ground_truths"],
            rag_system=rag_generator,
            contexts=test_data["contexts"]
        )
        
        # Print summary
        summary = results.get("summary", {})
        print(f"\n📈 Evaluation Results:")
        print(f"Overall Score: {summary.get('overall_score', 0.0):.3f}")
        
        key_metrics = summary.get("key_metrics", {})
        for metric, value in key_metrics.items():
            print(f"{metric}: {value:.3f}")
        
        # Save results
        os.makedirs("demo_results", exist_ok=True)
        with open("demo_results/evaluation_results.json", 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print("✅ Evaluation results saved to demo_results/evaluation_results.json")
        
    except Exception as e:
        print(f"❌ Evaluation error: {e}")


def show_system_stats(rag_generator):
    """Display system statistics."""
    print("\n📊 System Statistics")
    print("=" * 50)
    
    try:
        stats = rag_generator.get_stats()
        
        print("LLM Statistics:")
        llm_stats = stats.get("llm_stats", {})
        print(f"  Available Models: {len(llm_stats.get('available_models', []))}")
        print(f"  Primary Model: {llm_stats.get('primary_model', 'Unknown')}")
        
        print("\nEmbedding Statistics:")
        embedding_stats = stats.get("embedding_stats", {})
        print(f"  Model: {embedding_stats.get('model_name', 'Unknown')}")
        print(f"  Cache Size: {embedding_stats.get('cache_size', 0)}")
        
        print("\nRetriever Statistics:")
        retriever_stats = stats.get("retriever_stats", {})
        print(f"  Total Documents: {retriever_stats.get('total_documents', 0)}")
        print(f"  Vector Weight: {retriever_stats.get('alpha', 0):.2f}")
        print(f"  BM25 Weight: {retriever_stats.get('bm25_weight', 0):.2f}")
        
        print(f"\nReranking Enabled: {stats.get('reranking_enabled', False)}")
        
    except Exception as e:
        print(f"❌ Error getting stats: {e}")


def main():
    """Main demonstration function."""
    print("🤖 Advanced RAG System Demo")
    print("=" * 50)
    
    # Create sample documents
    print("📄 Creating sample documents...")
    file_paths = create_sample_documents()
    
    # Initialize RAG system
    rag_generator = initialize_rag_system()
    
    # Load documents
    if not load_documents(rag_generator, [f"data/{f}" for f in file_paths]):
        print("❌ Failed to load documents. Exiting.")
        return
    
    # Show system stats
    show_system_stats(rag_generator)
    
    # Run demo queries
    run_demo_queries(rag_generator)
    
    # Run streaming demo
    run_streaming_demo(rag_generator)
    
    # Run evaluation demo
    run_evaluation_demo(rag_generator)
    
    print("\n🎉 Demo completed successfully!")
    print("\nNext steps:")
    print("1. Start the API server: python -m uvicorn src.api.main:app --reload")
    print("2. Start the frontend: streamlit run src/frontend/streamlit_app.py")
    print("3. Access the web interface at http://localhost:8501")
    print("4. View API documentation at http://localhost:8000/docs")


if __name__ == "__main__":
    main()
