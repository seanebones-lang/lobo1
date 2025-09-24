#!/bin/bash

# RAG System Health Check Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[OK]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

# Configuration
DOMAIN=${1:-"localhost"}
API_URL="http://$DOMAIN:8000"
FRONTEND_URL="http://$DOMAIN:8501"
MLFLOW_URL="http://$DOMAIN:5000"

echo "🔍 RAG System Health Check"
echo "=========================="
echo "Domain: $DOMAIN"
echo "API URL: $API_URL"
echo "Frontend URL: $FRONTEND_URL"
echo "MLflow URL: $MLFLOW_URL"
echo ""

# Check API health
print_info "Checking API health..."
if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
    print_status "API is healthy"
    
    # Get API health details
    HEALTH_RESPONSE=$(curl -s "$API_URL/health" 2>/dev/null || echo "{}")
    if command -v jq &> /dev/null; then
        echo "Health details:"
        echo "$HEALTH_RESPONSE" | jq '.' 2>/dev/null || echo "$HEALTH_RESPONSE"
    else
        echo "Health response: $HEALTH_RESPONSE"
    fi
else
    print_error "API is not responding"
fi

echo ""

# Check API endpoints
print_info "Checking API endpoints..."
ENDPOINTS=("/" "/docs" "/stats" "/models")

for endpoint in "${ENDPOINTS[@]}"; do
    if curl -s -f "$API_URL$endpoint" > /dev/null 2>&1; then
        print_status "API endpoint $endpoint is accessible"
    else
        print_warning "API endpoint $endpoint is not accessible"
    fi
done

echo ""

# Check frontend
print_info "Checking frontend..."
if curl -s -f "$FRONTEND_URL" > /dev/null 2>&1; then
    print_status "Frontend is accessible"
else
    print_error "Frontend is not accessible"
fi

echo ""

# Check MLflow
print_info "Checking MLflow..."
if curl -s -f "$MLFLOW_URL" > /dev/null 2>&1; then
    print_status "MLflow is accessible"
else
    print_warning "MLflow is not accessible (optional service)"
fi

echo ""

# Check Docker services (if running in Docker)
if command -v docker-compose &> /dev/null && [ -f "docker-compose.yml" ]; then
    print_info "Checking Docker services..."
    
    SERVICES=$(docker-compose ps --services 2>/dev/null || echo "")
    if [ -n "$SERVICES" ]; then
        for service in $SERVICES; do
            STATUS=$(docker-compose ps $service --format "table {{.State}}" | tail -n +2)
            if [ "$STATUS" = "running" ]; then
                print_status "Docker service $service is running"
            else
                print_error "Docker service $service is not running (Status: $STATUS)"
            fi
        done
    else
        print_warning "No Docker services found or docker-compose not running"
    fi
fi

echo ""

# Check system resources
print_info "Checking system resources..."

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ "$DISK_USAGE" -lt 80 ]; then
    print_status "Disk usage: ${DISK_USAGE}% (OK)"
else
    print_warning "Disk usage: ${DISK_USAGE}% (High)"
fi

# Check memory usage
if command -v free &> /dev/null; then
    MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
    if [ "$MEMORY_USAGE" -lt 80 ]; then
        print_status "Memory usage: ${MEMORY_USAGE}% (OK)"
    else
        print_warning "Memory usage: ${MEMORY_USAGE}% (High)"
    fi
fi

# Check CPU load
if command -v uptime &> /dev/null; then
    LOAD_AVG=$(uptime | awk -F'load average:' '{print $2}' | awk '{print $1}' | sed 's/,//')
    print_info "Load average: $LOAD_AVG"
fi

echo ""

# Check logs for errors
print_info "Checking recent logs for errors..."

if [ -d "logs" ]; then
    ERROR_COUNT=$(find logs -name "*.log" -exec grep -l "ERROR\|CRITICAL\|FATAL" {} \; 2>/dev/null | wc -l)
    if [ "$ERROR_COUNT" -eq 0 ]; then
        print_status "No critical errors found in logs"
    else
        print_warning "Found $ERROR_COUNT log files with errors"
        echo "Recent errors:"
        find logs -name "*.log" -exec grep -H "ERROR\|CRITICAL\|FATAL" {} \; 2>/dev/null | tail -5
    fi
else
    print_warning "Logs directory not found"
fi

echo ""

# Performance test
print_info "Running performance test..."
if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
    RESPONSE_TIME=$(curl -o /dev/null -s -w '%{time_total}' "$API_URL/health" 2>/dev/null || echo "N/A")
    if [ "$RESPONSE_TIME" != "N/A" ]; then
        RESPONSE_MS=$(echo "$RESPONSE_TIME * 1000" | bc 2>/dev/null || echo "N/A")
        if [ "$RESPONSE_MS" != "N/A" ]; then
            if (( $(echo "$RESPONSE_MS < 1000" | bc -l) )); then
                print_status "API response time: ${RESPONSE_MS}ms (Good)"
            else
                print_warning "API response time: ${RESPONSE_MS}ms (Slow)"
            fi
        fi
    fi
fi

echo ""

# Summary
print_info "Health Check Summary:"
echo "========================"

# Count successful checks
TOTAL_CHECKS=0
PASSED_CHECKS=0

# API health
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if curl -s -f "$API_URL/health" > /dev/null 2>&1; then
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

# Frontend
TOTAL_CHECKS=$((TOTAL_CHECKS + 1))
if curl -s -f "$FRONTEND_URL" > /dev/null 2>&1; then
    PASSED_CHECKS=$((PASSED_CHECKS + 1))
fi

# Calculate percentage
if [ "$TOTAL_CHECKS" -gt 0 ]; then
    PERCENTAGE=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
    echo "Overall Health: $PASSED_CHECKS/$TOTAL_CHECKS checks passed ($PERCENTAGE%)"
    
    if [ "$PERCENTAGE" -ge 80 ]; then
        print_status "System is healthy! 🎉"
    elif [ "$PERCENTAGE" -ge 60 ]; then
        print_warning "System has some issues but is mostly functional"
    else
        print_error "System has significant issues and needs attention"
    fi
fi

echo ""
echo "For detailed logs, run: ./scripts/start_services.sh logs"
echo "For system status, run: ./scripts/start_services.sh status"
echo "For restart, run: ./scripts/start_services.sh restart"
