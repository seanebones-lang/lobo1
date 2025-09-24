# Makefile for RAG System

.PHONY: help install setup test run clean docker-build docker-run lint format

# Default target
help:
	@echo "🤖 Advanced RAG System - Available Commands"
	@echo "=============================================="
	@echo ""
	@echo "Setup & Installation:"
	@echo "  setup          - Run complete setup (install deps, create venv, etc.)"
	@echo "  install        - Install Python dependencies"
	@echo "  install-dev    - Install development dependencies"
	@echo ""
	@echo "Development:"
	@echo "  run-api        - Start API server in development mode"
	@echo "  run-frontend   - Start Streamlit frontend"
	@echo "  run-all        - Start both API and frontend"
	@echo "  demo           - Run demonstration script"
	@echo ""
	@echo "Testing:"
	@echo "  test           - Run all tests"
	@echo "  test-unit      - Run unit tests only"
	@echo "  test-integration - Run integration tests"
	@echo "  test-coverage  - Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint           - Run linting (flake8, mypy)"
	@echo "  format         - Format code (black)"
	@echo "  format-check   - Check code formatting"
	@echo ""
	@echo "Docker:"
	@echo "  docker-build   - Build Docker images"
	@echo "  docker-run     - Run with Docker Compose"
	@echo "  docker-stop    - Stop Docker containers"
	@echo "  docker-clean   - Clean Docker resources"
	@echo ""
	@echo "Utilities:"
	@echo "  clean          - Clean temporary files"
	@echo "  logs           - Show recent logs"
	@echo "  status         - Show service status"
	@echo "  evaluation     - Run system evaluation"

# Setup and Installation
setup:
	@echo "🚀 Setting up RAG System..."
	chmod +x scripts/setup.sh
	./scripts/setup.sh

install:
	@echo "📦 Installing dependencies..."
	pip install -r requirements.txt

install-dev:
	@echo "🔧 Installing development dependencies..."
	pip install -r requirements.txt
	pip install pytest black flake8 mypy jupyter

# Development
run-api:
	@echo "🌐 Starting API server..."
	python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000

run-frontend:
	@echo "💻 Starting Streamlit frontend..."
	streamlit run src/frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0

run-all:
	@echo "🚀 Starting all services..."
	chmod +x scripts/start_services.sh
	./scripts/start_services.sh start

demo:
	@echo "🎯 Running demonstration..."
	python scripts/demo.py

# Testing
test:
	@echo "🧪 Running all tests..."
	pytest tests/ -v

test-unit:
	@echo "🧪 Running unit tests..."
	pytest tests/ -v -m "not integration"

test-integration:
	@echo "🧪 Running integration tests..."
	pytest tests/ -v -m "integration"

test-coverage:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=src --cov-report=html --cov-report=term

# Code Quality
lint:
	@echo "🔍 Running linting..."
	flake8 src/ tests/
	mypy src/

format:
	@echo "🎨 Formatting code..."
	black src/ tests/ scripts/ examples/

format-check:
	@echo "🎨 Checking code formatting..."
	black --check src/ tests/ scripts/ examples/

# Docker
docker-build:
	@echo "🐳 Building Docker images..."
	docker-compose build

docker-run:
	@echo "🐳 Starting services with Docker..."
	docker-compose up -d

docker-stop:
	@echo "🐳 Stopping Docker services..."
	docker-compose down

docker-clean:
	@echo "🐳 Cleaning Docker resources..."
	docker-compose down -v --rmi all

# Utilities
clean:
	@echo "🧹 Cleaning temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	rm -rf logs/
	rm -rf chroma_db/
	rm -rf data/
	rm -rf temp/

logs:
	@echo "📋 Showing recent logs..."
	chmod +x scripts/start_services.sh
	./scripts/start_services.sh logs

status:
	@echo "📊 Checking service status..."
	chmod +x scripts/start_services.sh
	./scripts/start_services.sh status

evaluation:
	@echo "📊 Running system evaluation..."
	python scripts/run_evaluation.py --create-sample
	python scripts/run_evaluation.py --quick-test

# Development workflow
dev-setup: setup install-dev
	@echo "✅ Development environment ready!"

dev-test: format lint test
	@echo "✅ All quality checks passed!"

# Production deployment
prod-build:
	@echo "🏭 Building production image..."
	docker build --target production -t rag-system:latest .

prod-run:
	@echo "🏭 Running production deployment..."
	docker-compose -f docker-compose.prod.yml up -d

# Documentation
docs:
	@echo "📚 Generating documentation..."
	@echo "API Documentation: http://localhost:8000/docs"
	@echo "Frontend: http://localhost:8501"

# Quick start
quick-start: setup run-all
	@echo "🎉 RAG System is ready!"
	@echo "Frontend: http://localhost:8501"
	@echo "API: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"
