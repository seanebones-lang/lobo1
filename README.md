# 🤖 Advanced RAG System

A comprehensive, production-ready Retrieval Augmented Generation (RAG) system with hybrid search, reranking, multiple LLM support, and modern UI.

## 🚀 Features

### Core RAG Capabilities
- **Hybrid Search**: Combines vector similarity search with BM25 for better retrieval
- **Advanced Reranking**: Uses cross-encoder models to improve result quality
- **Multiple LLM Support**: OpenAI GPT-4, Anthropic Claude, with automatic fallback
- **Smart Chunking**: Recursive and semantic chunking strategies
- **Vector Databases**: Support for ChromaDB, Pinecone, and Qdrant

### Advanced Features
- **Conversational Memory**: Maintains context across conversations
- **Streaming Responses**: Real-time answer generation
- **Batch Processing**: Handle multiple queries efficiently
- **Comprehensive Evaluation**: RAGAS metrics and custom evaluation framework
- **Monitoring & Analytics**: MLflow integration and performance tracking
- **Modern UI**: Beautiful Streamlit frontend with real-time analytics

### Production Ready
- **Docker Support**: Multi-stage builds with development and production configs
- **API Documentation**: Auto-generated OpenAPI/Swagger docs
- **Rate Limiting**: Built-in request throttling
- **Health Checks**: Comprehensive system monitoring
- **Security**: CORS, authentication, and input validation
- **Scalability**: Kubernetes-ready deployment configs

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Architecture](#architecture)
- [Deployment](#deployment)
- [Evaluation](#evaluation)
- [Contributing](#contributing)
- [License](#license)

## 🚀 Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd LoboLobo

# Copy environment file
cp env.example .env

# Edit .env with your API keys
nano .env

# Start all services
docker-compose up -d

# Access the application
# Frontend: http://localhost:8501
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

### Option 2: Local Development

```bash
# Run setup script
chmod +x scripts/setup.sh
./scripts/setup.sh

# Activate virtual environment
source venv/bin/activate

# Start API server
python -m uvicorn src.api.main:app --reload

# In another terminal, start frontend
streamlit run src/frontend/streamlit_app.py
```

## 📦 Installation

### Prerequisites

- Python 3.9+
- pip
- Git
- Docker (optional, for containerized deployment)

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y build-essential curl git
```

**macOS:**
```bash
brew install python git
```

### Python Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Environment Setup

```bash
# Copy environment template
cp env.example .env

# Edit with your API keys
nano .env
```

Required API keys:
- `OPENAI_API_KEY`: For OpenAI models and embeddings
- `ANTHROPIC_API_KEY`: For Claude models (optional)
- `COHERE_API_KEY`: For Cohere reranking (optional)

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key | Required |
| `ANTHROPIC_API_KEY` | Anthropic API key | Optional |
| `COHERE_API_KEY` | Cohere API key | Optional |
| `VECTOR_DB_TYPE` | Vector database type | `chroma` |
| `VECTOR_DB_PATH` | Vector database path | `./chroma_db` |
| `REDIS_URL` | Redis connection URL | `redis://localhost:6379` |
| `APP_HOST` | API host | `0.0.0.0` |
| `APP_PORT` | API port | `8000` |
| `EMBEDDING_MODEL` | Embedding model | `text-embedding-3-small` |
| `LLM_MODEL` | Primary LLM model | `gpt-4` |
| `TEMPERATURE` | Generation temperature | `0.1` |
| `CHUNK_SIZE` | Document chunk size | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap | `200` |
| `TOP_K` | Documents to retrieve | `5` |

### Vector Database Options

**ChromaDB (Default):**
```env
VECTOR_DB_TYPE=chroma
VECTOR_DB_PATH=./chroma_db
```

**Pinecone:**
```env
VECTOR_DB_TYPE=pinecone
PINECONE_API_KEY=your_key
PINECONE_ENVIRONMENT=your_env
```

**Qdrant:**
```env
VECTOR_DB_TYPE=qdrant
QDRANT_URL=http://localhost:6333
```

## 💻 Usage

### API Usage

**Basic Query:**
```python
import requests

response = requests.post("http://localhost:8000/query", json={
    "question": "What is machine learning?",
    "prompt_type": "qa",
    "top_k": 5,
    "include_sources": True
})

result = response.json()
print(result["answer"])
```

**Streaming Query:**
```python
import requests

response = requests.post(
    "http://localhost:8000/query/stream",
    json={"question": "Explain quantum computing"},
    stream=True
)

for line in response.iter_lines():
    if line:
        print(line.decode())
```

**Document Upload:**
```python
import requests

response = requests.post("http://localhost:8000/documents/upload", json={
    "file_paths": ["/path/to/document.pdf"],
    "chunk_method": "recursive",
    "chunk_size": 1000,
    "chunk_overlap": 200
})
```

### Python SDK Usage

```python
from src.generation.rag_generator import RAGGenerator
from src.retrieval.embedding_generator import EmbeddingGenerator
from src.retrieval.vector_store import VectorStore
from src.retrieval.hybrid_search import HybridRetriever

# Initialize components
embedding_generator = EmbeddingGenerator()
vector_store = VectorStore()
hybrid_retriever = HybridRetriever(vector_store, documents=[])
rag_generator = RAGGenerator(
    llm_manager=llm_manager,
    embedding_generator=embedding_generator,
    hybrid_retriever=hybrid_retriever
)

# Generate answer
result = rag_generator.generate_answer(
    query="What is the capital of France?",
    prompt_type="qa",
    top_k=5
)

print(result["answer"])
```

### Frontend Usage

1. **Start the Streamlit app:**
   ```bash
   streamlit run src/frontend/streamlit_app.py
   ```

2. **Access the interface:**
   - Open http://localhost:8501
   - Upload documents in the Documents tab
   - Ask questions in the Chat tab
   - Monitor performance in the Analytics tab

## 📚 API Reference

### Endpoints

#### Query Endpoints

- `POST /query` - Single query
- `POST /query/stream` - Streaming query
- `POST /query/batch` - Batch queries
- `POST /conversation` - Conversational query

#### Document Management

- `POST /documents/upload` - Upload documents
- `GET /documents/stats` - Document statistics

#### System

- `GET /health` - Health check
- `GET /stats` - System statistics
- `GET /models` - Available models
- `GET /prompts` - Available prompt types

### Request/Response Examples

**Query Request:**
```json
{
  "question": "What is artificial intelligence?",
  "prompt_type": "qa",
  "system_role": "assistant",
  "top_k": 5,
  "rerank_top_k": 3,
  "include_sources": true,
  "temperature": 0.1,
  "max_tokens": 1000
}
```

**Query Response:**
```json
{
  "answer": "Artificial intelligence (AI) is...",
  "sources": [
    {
      "id": 1,
      "text": "AI is the simulation of human intelligence...",
      "score": 0.95,
      "metadata": {"source": "document1.pdf"}
    }
  ],
  "confidence": 0.87,
  "retrieval_time": 0.5,
  "generation_time": 2.1,
  "total_time": 2.6,
  "model_used": "gpt-4",
  "tokens_used": 150
}
```

## 🏗️ Architecture

### System Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway   │    │   Vector Store  │
│   (Streamlit)   │◄──►│   (FastAPI)     │◄──►│   (ChromaDB)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   RAG Engine    │
                       │                 │
                       │ ┌─────────────┐ │
                       │ │ Retrieval  │ │
                       │ │ (Hybrid)   │ │
                       │ └─────────────┘ │
                       │ ┌─────────────┐ │
                       │ │ Generation │ │
                       │ │ (LLM)      │ │
                       │ └─────────────┘ │
                       └─────────────────┘
```

### Data Flow

1. **Document Processing**: Documents → Chunking → Embeddings → Vector Store
2. **Query Processing**: Query → Embedding → Hybrid Search → Reranking → Generation
3. **Response**: Answer + Sources + Metadata

### Key Components

- **Document Processor**: Handles PDF, DOCX, TXT files with smart chunking
- **Embedding Generator**: Creates vector representations using OpenAI or Sentence Transformers
- **Vector Store**: Manages vector database operations (ChromaDB, Pinecone, Qdrant)
- **Hybrid Retriever**: Combines vector search with BM25
- **Reranker**: Improves result quality using cross-encoder models
- **LLM Manager**: Handles multiple LLM providers with fallback
- **RAG Generator**: Orchestrates the complete RAG pipeline

## 🚀 Deployment

### Docker Deployment

**Development:**
```bash
docker-compose -f docker-compose.yml up --build
```

**Production:**
```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Kubernetes Deployment

```bash
# Apply Kubernetes configurations
kubectl apply -f k8s/

# Check deployment status
kubectl get pods
kubectl get services
```

### Environment-Specific Configurations

**Development:**
- Hot reload enabled
- Debug logging
- Local file storage

**Production:**
- Multi-worker setup
- Persistent storage
- Load balancing
- SSL/TLS termination

## 📊 Evaluation

### RAGAS Metrics

The system includes comprehensive evaluation using RAGAS:

- **Faithfulness**: Measures factual consistency
- **Answer Relevancy**: Evaluates answer quality
- **Context Precision**: Assesses retrieval quality
- **Context Recall**: Measures information coverage
- **Answer Correctness**: Compares with ground truth
- **Answer Similarity**: Semantic similarity scoring

### Custom Metrics

- **Semantic Similarity**: Using sentence transformers
- **Keyword Overlap**: Traditional text matching
- **Confidence Scoring**: Model confidence analysis
- **Processing Time**: Performance metrics
- **Source Quality**: Retrieval effectiveness

### Running Evaluation

```python
from src.evaluation.rag_evaluator import RAGEvaluator

evaluator = RAGEvaluator()
results = evaluator.evaluate_rag_system(
    test_questions=["What is AI?"],
    ground_truths=["AI is artificial intelligence"],
    rag_system=rag_generator
)

# Generate report
report = evaluator.create_evaluation_report(results, "evaluation_report.md")
```

## 🔧 Advanced Configuration

### Custom Models

**Custom Embedding Model:**
```python
embedding_generator = EmbeddingGenerator(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
```

**Custom Reranker:**
```python
from src.retrieval.reranker import Reranker

reranker = Reranker(model_name="BAAI/bge-reranker-large")
```

### Prompt Engineering

**Custom Prompts:**
```python
from src.generation.prompt_manager import PromptManager

prompt_manager = PromptManager()
custom_prompt = prompt_manager.create_custom_prompt(
    template="You are a {role}. Answer: {question}",
    prompt_name="custom_qa"
)
```

### Monitoring

**MLflow Integration:**
```python
from src.evaluation.monitoring import RAGMonitor

monitor = RAGMonitor(experiment_name="rag_experiment")
monitor.log_query(
    query="What is AI?",
    response="AI is...",
    confidence=0.9,
    processing_time=1.5
)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests
pytest

# Format code
black src/
flake8 src/

# Type checking
mypy src/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LangChain](https://github.com/langchain-ai/langchain) for the RAG framework
- [RAGAS](https://github.com/explodinggradients/ragas) for evaluation metrics
- [Streamlit](https://streamlit.io/) for the frontend
- [FastAPI](https://fastapi.tiangolo.com/) for the API framework
- [ChromaDB](https://www.trychroma.com/) for vector storage

## 📞 Support

- **Documentation**: [Full Documentation](docs/)
- **Issues**: [GitHub Issues](https://github.com/your-repo/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-repo/discussions)

---

**Built with ❤️ for the AI community**

