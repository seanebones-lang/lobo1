#!/bin/bash

# APOLLO PRE-PRODUCTION TEST RUNNER
# Comprehensive testing script for NextEleven Tattoo AI
# Designed by APOLLO 1.0.0

echo "🧠 APOLLO PRE-PRODUCTION TEST RUNNER"
echo "===================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    case $1 in
        "success") echo -e "${GREEN}✅ $2${NC}" ;;
        "error") echo -e "${RED}❌ $2${NC}" ;;
        "warning") echo -e "${YELLOW}⚠️  $2${NC}" ;;
        "info") echo -e "${BLUE}ℹ️  $2${NC}" ;;
    esac
}

# Check if Node.js is installed
check_node() {
    if ! command -v node &> /dev/null; then
        print_status "error" "Node.js is not installed. Please install Node.js first."
        exit 1
    fi
    print_status "success" "Node.js is installed ($(node --version))"
}

# Check if npm is installed
check_npm() {
    if ! command -v npm &> /dev/null; then
        print_status "error" "npm is not installed. Please install npm first."
        exit 1
    fi
    print_status "success" "npm is installed ($(npm --version))"
}

# Install test dependencies
install_dependencies() {
    print_status "info" "Installing test dependencies..."
    
    if [ ! -f "package.json" ]; then
        print_status "warning" "No package.json found, creating test dependencies..."
        cp test-package.json package.json
    fi
    
    npm install puppeteer jest jest-puppeteer axe-core lighthouse playwright chromedriver selenium-webdriver
    print_status "success" "Dependencies installed"
}

# Check if the application is running
check_app_running() {
    print_status "info" "Checking if NextEleven application is running..."
    
    if curl -s http://localhost:3000 > /dev/null; then
        print_status "success" "Application is running on http://localhost:3000"
    else
        print_status "error" "Application is not running on http://localhost:3000"
        print_status "info" "Please start the application with: npm run dev"
        exit 1
    fi
}

# Run smoke tests
run_smoke_tests() {
    print_status "info" "Running APOLLO Smoke Tests..."
    echo "🔥 Smoke tests validate critical functionality"
    echo ""
    
    node apollo-smoke-tests.js
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_status "success" "Smoke tests completed successfully"
    else
        print_status "error" "Smoke tests failed"
        return 1
    fi
}

# Run button tests
run_button_tests() {
    print_status "info" "Running APOLLO Button Tests..."
    echo "🔘 Button tests validate all interactive elements"
    echo ""
    
    node apollo-button-tests.js
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_status "success" "Button tests completed successfully"
    else
        print_status "error" "Button tests failed"
        return 1
    fi
}

# Run comprehensive test suite
run_comprehensive_tests() {
    print_status "info" "Running APOLLO Comprehensive Test Suite..."
    echo "🧠 Comprehensive tests validate all aspects of the application"
    echo ""
    
    node apollo-pre-production-test-suite.js
    local exit_code=$?
    
    if [ $exit_code -eq 0 ]; then
        print_status "success" "Comprehensive tests completed successfully"
    else
        print_status "error" "Comprehensive tests failed"
        return 1
    fi
}

# Generate final report
generate_final_report() {
    print_status "info" "Generating final APOLLO test report..."
    
    # Combine all test reports
    echo "🧠 APOLLO PRE-PRODUCTION TEST SUMMARY" > apollo-final-report.txt
    echo "=====================================" >> apollo-final-report.txt
    echo "" >> apollo-final-report.txt
    echo "Generated on: $(date)" >> apollo-final-report.txt
    echo "" >> apollo-final-report.txt
    
    # Add smoke test results if available
    if [ -f "apollo-smoke-test-report.json" ]; then
        echo "🔥 SMOKE TEST RESULTS:" >> apollo-final-report.txt
        echo "=====================" >> apollo-final-report.txt
        cat apollo-smoke-test-report.json >> apollo-final-report.txt
        echo "" >> apollo-final-report.txt
    fi
    
    # Add button test results if available
    if [ -f "apollo-button-test-report.json" ]; then
        echo "🔘 BUTTON TEST RESULTS:" >> apollo-final-report.txt
        echo "======================" >> apollo-final-report.txt
        cat apollo-button-test-report.json >> apollo-final-report.txt
        echo "" >> apollo-final-report.txt
    fi
    
    # Add comprehensive test results if available
    if [ -f "apollo-test-report.json" ]; then
        echo "🧠 COMPREHENSIVE TEST RESULTS:" >> apollo-final-report.txt
        echo "=============================" >> apollo-final-report.txt
        cat apollo-test-report.json >> apollo-final-report.txt
        echo "" >> apollo-final-report.txt
    fi
    
    print_status "success" "Final report generated: apollo-final-report.txt"
}

# Main execution
main() {
    echo "🚀 Starting APOLLO Pre-Production Testing..."
    echo ""
    
    # Pre-flight checks
    check_node
    check_npm
    
    # Install dependencies if needed
    if [ "$1" = "--install" ] || [ ! -d "node_modules" ]; then
        install_dependencies
    fi
    
    # Check if app is running
    check_app_running
    
    echo ""
    print_status "info" "Starting test execution..."
    echo ""
    
    # Determine which tests to run
    case "${1:-all}" in
        "smoke")
            run_smoke_tests
            ;;
        "buttons")
            run_button_tests
            ;;
        "comprehensive")
            run_comprehensive_tests
            ;;
        "all"|*)
            echo "🧠 Running ALL APOLLO tests..."
            echo ""
            
            run_smoke_tests
            echo ""
            
            run_button_tests
            echo ""
            
            run_comprehensive_tests
            echo ""
            ;;
    esac
    
    # Generate final report
    generate_final_report
    
    echo ""
    print_status "success" "APOLLO Pre-Production Testing Complete!"
    echo ""
    print_status "info" "Test reports available:"
    print_status "info" "  - apollo-final-report.txt (Summary)"
    print_status "info" "  - apollo-test-report.html (Visual Report)"
    print_status "info" "  - apollo-test-report.json (Detailed JSON)"
    echo ""
}

# Help function
show_help() {
    echo "APOLLO Pre-Production Test Runner"
    echo ""
    echo "Usage: $0 [OPTIONS] [TEST_TYPE]"
    echo ""
    echo "Options:"
    echo "  --install    Install test dependencies"
    echo "  --help       Show this help message"
    echo ""
    echo "Test Types:"
    echo "  smoke        Run only smoke tests (quick validation)"
    echo "  buttons      Run only button tests (comprehensive button testing)"
    echo "  comprehensive Run only comprehensive test suite"
    echo "  all          Run all tests (default)"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run all tests"
    echo "  $0 smoke              # Run only smoke tests"
    echo "  $0 --install all      # Install dependencies and run all tests"
    echo ""
}

# Parse command line arguments
case "$1" in
    "--help"|"-h")
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac
