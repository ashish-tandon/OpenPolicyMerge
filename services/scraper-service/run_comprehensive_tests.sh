#!/bin/bash

# OpenPolicy Scraper Service - Comprehensive Test Suite Runner
# This script runs all test categories with comprehensive reporting

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PYTEST_CMD="python -m pytest"
COVERAGE_THRESHOLD=85
TEST_DIRS=(
    "tests/unit"
    "tests/integration"
    "tests/legacy_migration"
    "tests/performance"
    "tests/coverage"
    "tests/quality"
)

# Test categories with their markers
TEST_CATEGORIES=(
    "unit:unit"
    "integration:integration"
    "legacy:legacy"
    "performance:performance"
    "coverage:coverage"
    "quality:quality"
)

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to run tests for a specific category
run_test_category() {
    local category=$1
    local marker=$2
    local test_dir=$3
    
    print_status $BLUE "Running $category tests..."
    
    if [ -d "$test_dir" ]; then
        # Run tests with the specific marker
        if PYTHONPATH=. $PYTEST_CMD "$test_dir" -m "$marker" -v --tb=short; then
            print_status $GREEN "✓ $category tests passed"
            return 0
        else
            print_status $RED "✗ $category tests failed"
            return 1
        fi
    else
        print_status $YELLOW "⚠️  Test directory $test_dir not found, skipping $category tests"
        return 0
    fi
}

# Function to run basic infrastructure tests
run_basic_tests() {
    print_status $BLUE "Running basic infrastructure tests..."
    
    if PYTHONPATH=. $PYTEST_CMD tests/test_basic_infrastructure.py -v; then
        print_status $GREEN "✓ Basic infrastructure tests passed"
        return 0
    else
        print_status $RED "✗ Basic infrastructure tests failed"
        return 1
    fi
}

# Function to run all tests
run_all_tests() {
    print_status $PURPLE "🚀 Running comprehensive test suite..."
    print_status $PURPLE "================================================"
    
    local total_passed=0
    local total_failed=0
    
    # Run basic tests first
    if run_basic_tests; then
        ((total_passed++))
    else
        ((total_failed++))
    fi
    
    # Run each test category
    for category_info in "${TEST_CATEGORIES[@]}"; do
        IFS=':' read -r category marker <<< "$category_info"
        test_dir="tests/${category}"
        
        if run_test_category "$category" "$marker" "$test_dir"; then
            ((total_passed++))
        else
            ((total_failed++))
        fi
    done
    
    # Summary
    print_status $PURPLE "================================================"
    print_status $PURPLE "📊 Test Summary:"
    print_status $GREEN "  Passed: $total_passed"
    if [ $total_failed -gt 0 ]; then
        print_status $RED "  Failed: $total_failed"
    else
        print_status $GREEN "  Failed: $total_failed"
    fi
    
    if [ $total_failed -eq 0 ]; then
        print_status $GREEN "🎉 All test categories completed successfully!"
        return 0
    else
        print_status $YELLOW "⚠️  Some test categories had failures"
        return 1
    fi
}

# Function to run tests with coverage
run_tests_with_coverage() {
    print_status $BLUE "Running tests with coverage analysis..."
    
    if PYTHONPATH=. $PYTEST_CMD tests/ --cov=src --cov-report=html --cov-report=term-missing --cov-fail-under=$COVERAGE_THRESHOLD; then
        print_status $GREEN "✓ Coverage requirements met (threshold: $COVERAGE_THRESHOLD%)"
        return 0
    else
        print_status $RED "✗ Coverage requirements not met"
        return 1
    fi
}

# Function to show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo ""
    echo "Options:"
    echo "  all              Run all test categories (default)"
    echo "  basic            Run only basic infrastructure tests"
    echo "  coverage         Run tests with coverage analysis"
    echo "  unit             Run only unit tests"
    echo "  integration      Run only integration tests"
    echo "  legacy           Run only legacy migration tests"
    echo "  performance      Run only performance tests"
    echo "  quality          Run only quality assurance tests"
    echo "  help             Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0               # Run all tests"
    echo "  $0 basic         # Run basic tests only"
    echo "  $0 coverage      # Run tests with coverage"
}

# Main execution
main() {
    case "${1:-all}" in
        "all")
            run_all_tests
            ;;
        "basic")
            run_basic_tests
            ;;
        "coverage")
            run_tests_with_coverage
            ;;
        "unit")
            run_test_category "unit" "unit" "tests/unit"
            ;;
        "integration")
            run_test_category "integration" "integration" "tests/integration"
            ;;
        "legacy")
            run_test_category "legacy" "legacy" "tests/legacy_migration"
            ;;
        "performance")
            run_test_category "performance" "performance" "tests/performance"
            ;;
        "quality")
            run_test_category "quality" "quality" "tests/quality"
            ;;
        "help"|"-h"|"--help")
            show_help
            ;;
        *)
            print_status $RED "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"
