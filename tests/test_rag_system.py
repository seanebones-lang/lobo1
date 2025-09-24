"""
Comprehensive tests for the RAG system.
"""

import pytest
import os
import tempfile
import shutil
from unittest.mock import Mock, patch
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
from evaluation.rag_evaluator import RAGEvaluator


class TestDocumentProcessor:
    """Test document processing functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.processor = DocumentProcessor()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_text_cleaning(self):
        """Test text cleaning functionality."""
        from src.data_processing.document_processor import TextCleaner
        
        cleaner = TextCleaner()
        
        # Test basic cleaning
        dirty_text = "  This   is   a   test   text  with   extra   spaces  "
        clean_text = cleaner.clean_text(dirty_text)
        assert clean_text == "This is a test text with extra spaces"
        
        # Test HTML removal
        html_text = "<p>This is <b>bold</b> text</p>"
        clean_text = cleaner.clean_text(html_text)
        assert clean_text == "This is bold text"
    
    def test_document_processing(self):
        """Test document processing pipeline."""
        # Create test document
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("This is a test document. It contains multiple sentences. Each sentence should be processed correctly.")
        
        # Process document
        documents = self.processor.process_documents([test_file])
        
        assert len(documents) > 0
        assert all(hasattr(doc, 'page_content') for doc in documents)
        assert all(hasattr(doc, 'metadata') for doc in documents)


class TestEmbeddingGenerator:
    """Test embedding generation functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.embedding_generator = EmbeddingGenerator(
            model_name="all-MiniLM-L6-v2"
        )
    
    def test_embedding_generation(self):
        """Test embedding generation."""
        texts = ["This is a test sentence.", "Another test sentence."]
        embeddings = self.embedding_generator.generate_embeddings(texts)
        
        assert len(embeddings) == 2
        assert embeddings.shape[1] > 0  # Should have embedding dimension
    
    def test_caching(self):
        """Test embedding caching."""
        text = "Test caching functionality"
        
        # First call
        embedding1 = self.embedding_generator.generate_embeddings(text)
        
        # Second call (should use cache)
        embedding2 = self.embedding_generator.generate_embeddings(text)
        
        # Should be identical
        assert (embedding1 == embedding2).all()
    
    def test_cache_stats(self):
        """Test cache statistics."""
        stats = self.embedding_generator.get_cache_stats()
        
        assert "cache_size" in stats
        assert "max_cache_size" in stats
        assert "model_name" in stats


class TestVectorStore:
    """Test vector store functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.vector_store = VectorStore(
            vector_db_type="chroma",
            persist_directory=self.temp_dir
        )
    
    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_add_documents(self):
        """Test adding documents to vector store."""
        documents = ["Document 1", "Document 2"]
        embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        metadatas = [{"source": "test1"}, {"source": "test2"}]
        
        ids = self.vector_store.add_documents(documents, embeddings, metadatas)
        
        assert len(ids) == 2
        assert all(isinstance(id, str) for id in ids)
    
    def test_search(self):
        """Test vector search functionality."""
        # Add test documents
        documents = ["Machine learning is AI", "Deep learning uses neural networks"]
        embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        
        self.vector_store.add_documents(documents, embeddings)
        
        # Search
        query_embedding = [0.2, 0.3, 0.4]
        results = self.vector_store.search(query_embedding, n_results=2)
        
        assert "documents" in results
        assert "distances" in results
        assert len(results["documents"]) <= 2


class TestHybridRetriever:
    """Test hybrid retrieval functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.vector_store = Mock()
        self.documents = ["Document 1", "Document 2", "Document 3"]
        self.hybrid_retriever = HybridRetriever(
            vector_store=self.vector_store,
            documents=self.documents
        )
    
    def test_hybrid_search(self):
        """Test hybrid search functionality."""
        # Mock vector store search
        self.vector_store.search.return_value = {
            "documents": ["Document 1", "Document 2"],
            "distances": [0.1, 0.2],
            "metadatas": [{"source": "1"}, {"source": "2"}],
            "ids": ["id1", "id2"]
        }
        
        query = "test query"
        query_embedding = [0.1, 0.2, 0.3]
        
        results = self.hybrid_retriever.hybrid_search(
            query=query,
            query_embedding=query_embedding,
            k=2
        )
        
        assert len(results) <= 2
        assert all("document" in result for result in results)
    
    def test_update_documents(self):
        """Test document update functionality."""
        new_docs = ["New Document 1", "New Document 2"]
        
        self.hybrid_retriever.update_documents(new_docs)
        
        # Should have original + new documents
        assert len(self.hybrid_retriever.documents) == 5


class TestPromptManager:
    """Test prompt management functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.prompt_manager = PromptManager()
    
    def test_available_prompts(self):
        """Test available prompt types."""
        prompts = self.prompt_manager.get_available_prompts()
        
        assert "qa" in prompts
        assert "summarization" in prompts
        assert "analysis" in prompts
    
    def test_prompt_formatting(self):
        """Test prompt formatting."""
        formatted = self.prompt_manager.format_prompt(
            "qa",
            context="Test context",
            question="Test question"
        )
        
        assert "Test context" in formatted
        assert "Test question" in formatted
    
    def test_custom_prompt(self):
        """Test custom prompt creation."""
        template = "Answer this: {question}"
        custom_prompt = self.prompt_manager.create_custom_prompt(
            template, "custom"
        )
        
        assert "custom" in self.prompt_manager.get_available_prompts()
        
        formatted = custom_prompt.format(question="What is AI?")
        assert "What is AI?" in formatted


class TestLLMManager:
    """Test LLM management functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        # Mock API keys for testing
        self.llm_manager = LLMManager(
            openai_api_key="test_key",
            anthropic_api_key="test_key"
        )
    
    def test_available_models(self):
        """Test available models."""
        models = self.llm_manager.get_available_models()
        
        assert len(models) > 0
        assert all(isinstance(model, str) for model in models)
    
    def test_model_info(self):
        """Test model information."""
        models = self.llm_manager.get_available_models()
        if models:
            info = self.llm_manager.get_model_info(models[0])
            assert "name" in info
            assert "type" in info


class TestRAGEvaluator:
    """Test RAG evaluation functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        self.evaluator = RAGEvaluator(use_ragas=False)
    
    def test_semantic_similarity(self):
        """Test semantic similarity calculation."""
        text1 = "This is a test sentence"
        text2 = "This is another test sentence"
        
        similarity = self.evaluator._calculate_semantic_similarity(text1, text2)
        
        assert 0 <= similarity <= 1
    
    def test_keyword_overlap(self):
        """Test keyword overlap calculation."""
        text1 = "machine learning artificial intelligence"
        text2 = "artificial intelligence deep learning"
        
        overlap = self.evaluator._calculate_keyword_overlap(text1, text2)
        
        assert 0 <= overlap <= 1
        assert overlap > 0  # Should have some overlap


class TestRAGGenerator:
    """Test RAG generator functionality."""
    
    def setup_method(self):
        """Setup for each test."""
        # Create mock components
        self.llm_manager = Mock()
        self.embedding_generator = Mock()
        self.hybrid_retriever = Mock()
        
        # Mock responses
        self.llm_manager.generate.return_value = {
            "text": "Test response",
            "model_used": "test_model",
            "tokens_used": 100,
            "success": True,
            "error": None
        }
        
        self.embedding_generator.generate_embeddings.return_value = [[0.1, 0.2, 0.3]]
        
        self.hybrid_retriever.hybrid_search.return_value = [
            {"document": "Test document", "score": 0.9}
        ]
        
        # Create RAG generator
        self.rag_generator = RAGGenerator(
            llm_manager=self.llm_manager,
            embedding_generator=self.embedding_generator,
            hybrid_retriever=self.hybrid_retriever
        )
    
    def test_generate_answer(self):
        """Test answer generation."""
        result = self.rag_generator.generate_answer("Test question")
        
        assert "answer" in result
        assert "confidence" in result
        assert "sources" in result
        assert result["answer"] == "Test response"
    
    def test_prepare_context(self):
        """Test context preparation."""
        documents = [
            {"document": "Doc 1", "score": 0.9},
            {"document": "Doc 2", "score": 0.8}
        ]
        
        context = self.rag_generator._prepare_context(documents)
        
        assert "Doc 1" in context
        assert "Doc 2" in context
        assert "Source 1:" in context
        assert "Source 2:" in context
    
    def test_extract_sources(self):
        """Test source extraction."""
        documents = [
            {"document": "Test doc 1", "score": 0.9, "metadata": {"source": "file1"}},
            {"document": "Test doc 2", "score": 0.8, "metadata": {"source": "file2"}}
        ]
        
        sources = self.rag_generator._extract_sources(documents)
        
        assert len(sources) == 2
        assert all("text" in source for source in sources)
        assert all("score" in source for source in sources)
    
    def test_calculate_confidence(self):
        """Test confidence calculation."""
        documents = [
            {"score": 0.9, "relevance_score": 0.8},
            {"score": 0.7, "relevance_score": 0.6}
        ]
        
        confidence = self.rag_generator._calculate_confidence(documents, {})
        
        assert 0 <= confidence <= 1


class TestIntegration:
    """Integration tests for the complete RAG system."""
    
    def setup_method(self):
        """Setup for each test."""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Cleanup after each test."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @pytest.mark.integration
    def test_end_to_end_rag(self):
        """Test end-to-end RAG functionality."""
        # This test requires actual API keys and is marked as integration
        # Skip if no API keys available
        if not os.getenv("OPENAI_API_KEY"):
            pytest.skip("No OpenAI API key available")
        
        # Create test document
        test_file = os.path.join(self.temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Artificial intelligence is the simulation of human intelligence in machines.")
        
        # Initialize components
        processor = DocumentProcessor()
        documents = processor.process_documents([test_file])
        
        # This would require actual API calls, so we'll mock the expensive parts
        with patch('src.retrieval.embedding_generator.EmbeddingGenerator') as mock_emb:
            with patch('src.generation.llm_manager.LLMManager') as mock_llm:
                # Mock embedding generation
                mock_emb.return_value.generate_embeddings.return_value = [[0.1] * 384]
                
                # Mock LLM generation
                mock_llm.return_value.generate.return_value = {
                    "text": "AI is the simulation of human intelligence.",
                    "model_used": "test_model",
                    "tokens_used": 50,
                    "success": True,
                    "error": None
                }
                
                # Test would continue here with actual RAG system initialization
                # and query processing


# Fixtures for pytest
@pytest.fixture
def sample_documents():
    """Sample documents for testing."""
    return [
        "Artificial intelligence is the simulation of human intelligence.",
        "Machine learning is a subset of artificial intelligence.",
        "Deep learning uses neural networks with multiple layers."
    ]


@pytest.fixture
def sample_queries():
    """Sample queries for testing."""
    return [
        "What is artificial intelligence?",
        "How does machine learning work?",
        "What is deep learning?"
    ]


# Test configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v"])
