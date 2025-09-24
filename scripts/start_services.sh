#!/bin/bash

# RAG System Service Startup Script
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if virtual environment exists
check_venv() {
    if [ ! -d "venv" ]; then
        print_error "Virtual environment not found. Run setup.sh first."
        exit 1
    fi
}

# Check if .env file exists
check_env() {
    if [ ! -f ".env" ]; then
        print_warning ".env file not found. Creating from template..."
        cp env.example .env
        print_warning "Please edit .env file with your API keys before continuing."
        read -p "Press Enter to continue after editing .env file..."
    fi
}

# Start API server
start_api() {
    print_status "Starting RAG API server..."
    source venv/bin/activate
    
    # Check if API is already running
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_warning "API server is already running on port 8000"
    else
        # Start API in background
        nohup python -m uvicorn src.api.main:app --host 0.0.0.0 --port 8000 > logs/api.log 2>&1 &
        API_PID=$!
        echo $API_PID > logs/api.pid
        
        # Wait for API to start
        print_status "Waiting for API to start..."
        for i in {1..30}; do
            if curl -s http://localhost:8000/health > /dev/null 2>&1; then
                print_status "API server started successfully (PID: $API_PID)"
                break
            fi
            sleep 1
        done
        
        if [ $i -eq 30 ]; then
            print_error "API server failed to start"
            exit 1
        fi
    fi
}

# Start Streamlit frontend
start_frontend() {
    print_status "Starting Streamlit frontend..."
    source venv/bin/activate
    
    # Check if frontend is already running
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        print_warning "Frontend is already running on port 8501"
    else
        # Start Streamlit in background
        nohup streamlit run src/frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0 > logs/frontend.log 2>&1 &
        FRONTEND_PID=$!
        echo $FRONTEND_PID > logs/frontend.pid
        
        # Wait for frontend to start
        print_status "Waiting for frontend to start..."
        for i in {1..30}; do
            if curl -s http://localhost:8501 > /dev/null 2>&1; then
                print_status "Frontend started successfully (PID: $FRONTEND_PID)"
                break
            fi
            sleep 1
        done
        
        if [ $i -eq 30 ]; then
            print_error "Frontend failed to start"
            exit 1
        fi
    fi
}

# Start Redis (if available)
start_redis() {
    if command -v redis-server &> /dev/null; then
        print_status "Starting Redis server..."
        
        # Check if Redis is already running
        if redis-cli ping > /dev/null 2>&1; then
            print_warning "Redis is already running"
        else
            nohup redis-server > logs/redis.log 2>&1 &
            REDIS_PID=$!
            echo $REDIS_PID > logs/redis.pid
            print_status "Redis started successfully (PID: $REDIS_PID)"
        fi
    else
        print_warning "Redis not found. Install Redis for caching support."
    fi
}

# Show service status
show_status() {
    print_status "Service Status:"
    echo "=================="
    
    # API status
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        print_status "✅ API Server: http://localhost:8000"
        print_status "   API Docs: http://localhost:8000/docs"
    else
        print_error "❌ API Server: Not running"
    fi
    
    # Frontend status
    if curl -s http://localhost:8501 > /dev/null 2>&1; then
        print_status "✅ Frontend: http://localhost:8501"
    else
        print_error "❌ Frontend: Not running"
    fi
    
    # Redis status
    if redis-cli ping > /dev/null 2>&1; then
        print_status "✅ Redis: Running"
    else
        print_warning "⚠️  Redis: Not running"
    fi
    
    echo ""
    print_status "Logs are available in the logs/ directory"
}

# Stop all services
stop_services() {
    print_status "Stopping all services..."
    
    # Stop API
    if [ -f "logs/api.pid" ]; then
        API_PID=$(cat logs/api.pid)
        if kill -0 $API_PID 2>/dev/null; then
            kill $API_PID
            print_status "API server stopped"
        fi
        rm -f logs/api.pid
    fi
    
    # Stop Frontend
    if [ -f "logs/frontend.pid" ]; then
        FRONTEND_PID=$(cat logs/frontend.pid)
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            print_status "Frontend stopped"
        fi
        rm -f logs/frontend.pid
    fi
    
    # Stop Redis
    if [ -f "logs/redis.pid" ]; then
        REDIS_PID=$(cat logs/redis.pid)
        if kill -0 $REDIS_PID 2>/dev/null; then
            kill $REDIS_PID
            print_status "Redis stopped"
        fi
        rm -f logs/redis.pid
    fi
    
    print_status "All services stopped"
}

# Main function
main() {
    case "${1:-start}" in
        "start")
            print_status "Starting RAG System services..."
            check_venv
            check_env
            
            # Create logs directory
            mkdir -p logs
            
            start_redis
            start_api
            start_frontend
            show_status
            ;;
        "stop")
            stop_services
            ;;
        "restart")
            stop_services
            sleep 2
            main start
            ;;
        "status")
            show_status
            ;;
        "logs")
            print_status "Showing recent logs..."
            echo "=== API Logs ==="
            tail -n 20 logs/api.log 2>/dev/null || echo "No API logs found"
            echo ""
            echo "=== Frontend Logs ==="
            tail -n 20 logs/frontend.log 2>/dev/null || echo "No frontend logs found"
            echo ""
            echo "=== Redis Logs ==="
            tail -n 20 logs/redis.log 2>/dev/null || echo "No Redis logs found"
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|status|logs}"
            echo ""
            echo "Commands:"
            echo "  start   - Start all services"
            echo "  stop    - Stop all services"
            echo "  restart - Restart all services"
            echo "  status  - Show service status"
            echo "  logs    - Show recent logs"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"

