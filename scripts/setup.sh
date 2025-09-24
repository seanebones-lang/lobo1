#!/bin/bash

# RAG System Setup Script
set -e

echo "🚀 Setting up Advanced RAG System..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.9+ is installed
check_python() {
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [[ $(echo "$PYTHON_VERSION >= 3.9" | bc -l) -eq 1 ]]; then
            print_status "Python $PYTHON_VERSION found"
        else
            print_error "Python 3.9+ is required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
}

# Check if pip is installed
check_pip() {
    if command -v pip3 &> /dev/null; then
        print_status "pip3 found"
    else
        print_error "pip3 is not installed"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment
activate_venv() {
    print_status "Activating virtual environment..."
    source venv/bin/activate
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p chroma_db
    mkdir -p logs
    mkdir -p data
    mkdir -p ssl
    mkdir -p temp
}

# Setup environment file
setup_env() {
    if [ ! -f ".env" ]; then
        print_status "Creating environment file..."
        cp env.example .env
        print_warning "Please edit .env file with your API keys and configuration"
    else
        print_warning ".env file already exists"
    fi
}

# Check for required API keys
check_api_keys() {
    if [ -f ".env" ]; then
        if grep -q "your_.*_api_key_here" .env; then
            print_warning "Please update .env file with your actual API keys"
        else
            print_status "API keys appear to be configured"
        fi
    else
        print_warning "No .env file found. Please create one from env.example"
    fi
}

# Install system dependencies (Ubuntu/Debian)
install_system_deps() {
    if command -v apt-get &> /dev/null; then
        print_status "Installing system dependencies..."
        sudo apt-get update
        sudo apt-get install -y \
            build-essential \
            curl \
            git \
            bc
    else
        print_warning "System dependency installation skipped (not Ubuntu/Debian)"
    fi
}

# Setup Docker (optional)
setup_docker() {
    if command -v docker &> /dev/null; then
        print_status "Docker is already installed"
    else
        print_warning "Docker not found. Install Docker for containerized deployment"
        read -p "Would you like to install Docker? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            curl -fsSL https://get.docker.com -o get-docker.sh
            sudo sh get-docker.sh
            sudo usermod -aG docker $USER
            print_status "Docker installed. Please log out and back in for group changes to take effect"
        fi
    fi
}

# Test installation
test_installation() {
    print_status "Testing installation..."
    source venv/bin/activate
    
    # Test Python imports
    python3 -c "
import sys
try:
    import langchain
    import streamlit
    import fastapi
    import chromadb
    print('✅ Core dependencies imported successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
    
    if [ $? -eq 0 ]; then
        print_status "Installation test passed"
    else
        print_error "Installation test failed"
        exit 1
    fi
}

# Main setup function
main() {
    print_status "Starting RAG System setup..."
    
    # Check prerequisites
    check_python
    check_pip
    
    # Install system dependencies
    install_system_deps
    
    # Setup Python environment
    create_venv
    activate_venv
    install_dependencies
    
    # Setup project structure
    create_directories
    setup_env
    check_api_keys
    
    # Optional Docker setup
    setup_docker
    
    # Test installation
    test_installation
    
    print_status "🎉 Setup completed successfully!"
    print_status ""
    print_status "Next steps:"
    print_status "1. Edit .env file with your API keys"
    print_status "2. Run: source venv/bin/activate"
    print_status "3. Start the API: python -m uvicorn src.api.main:app --reload"
    print_status "4. Start the frontend: streamlit run src/frontend/streamlit_app.py"
    print_status "5. Or use Docker: docker-compose up"
    print_status ""
    print_status "For more information, see README.md"
}

# Run main function
main "$@"

