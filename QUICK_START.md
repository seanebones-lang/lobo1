# 🚀 Quick Start Guide

Get your RAG system up and running in minutes!

## ⚡ Super Quick Start (Docker)

```bash
# 1. Clone and setup
git clone <your-repo>
cd LoboLobo
cp env.example .env

# 2. Edit .env with your API keys
nano .env

# 3. Start everything
docker-compose up -d

# 4. Access your system
# Frontend: http://localhost:8501
# API: http://localhost:8000
# API Docs: http://localhost:8000/docs
```

## 🛠️ Local Development

```bash
# 1. Automated setup
chmod +x scripts/setup.sh
./scripts/setup.sh

# 2. Start services
./scripts/start_services.sh start

# 3. Or use Makefile
make quick-start
```

## 📋 What You Need

### Required
- Python 3.9+
- OpenAI API key

### Optional (for full features)
- Anthropic API key (for Claude models)
- Cohere API key (for reranking)
- Redis (for caching)

## 🔑 API Keys Setup

Edit your `.env` file:

```env
# Required
OPENAI_API_KEY=your_openai_key_here

# Optional
ANTHROPIC_API_KEY=your_anthropic_key_here
COHERE_API_KEY=your_cohere_key_here
```

## 🎯 First Steps

1. **Upload Documents**: Use the Documents tab in the frontend
2. **Ask Questions**: Use the Chat tab to interact
3. **Monitor Performance**: Check the Analytics tab
4. **Explore API**: Visit http://localhost:8000/docs

## 🧪 Test the System

```bash
# Run the demo
python scripts/demo.py

# Run examples
python examples/basic_usage.py

# Test API
python examples/api_client.py
```

## 📊 Available Commands

```bash
# Development
make run-api          # Start API server
make run-frontend     # Start frontend
make run-all         # Start everything

# Testing
make test            # Run all tests
make test-coverage   # Run with coverage

# Docker
make docker-run      # Start with Docker
make docker-stop     # Stop Docker services

# Utilities
make clean           # Clean temporary files
make logs            # Show logs
make status          # Check status
```

## 🌐 Access Points

- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 🆘 Troubleshooting

### API Not Starting
```bash
# Check logs
make logs

# Check status
make status

# Restart services
./scripts/start_services.sh restart
```

### Missing API Keys
```bash
# Check your .env file
cat .env

# Make sure keys are set
export OPENAI_API_KEY=your_key_here
```

### Docker Issues
```bash
# Clean and rebuild
make docker-clean
make docker-build
make docker-run
```

## 🎉 You're Ready!

Your RAG system is now running! Start by uploading some documents and asking questions.

For more detailed information, see the [full README](README.md).
