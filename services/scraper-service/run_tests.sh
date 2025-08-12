#!/bin/bash
echo "🧪 Running OpenPolicy Scraper Service Tests..."
source venv/bin/activate
export PYTHONPATH=.

case "${1:-all}" in
    "unit")
        echo "Running unit tests..."
        python -m pytest tests/unit/ -v
        ;;
    "integration")
        echo "Running integration tests..."
        python -m pytest tests/integration/ -v
        ;;
    "performance")
        echo "Running performance tests..."
        python -m pytest tests/performance/ -v
        ;;
    "coverage")
        echo "Running coverage tests..."
        python -m pytest tests/coverage/ -v
        ;;
    "all")
        echo "Running all tests..."
        python -m pytest tests/ -v
        ;;
    *)
        echo "Usage: $0 {unit|integration|performance|coverage|all}"
        exit 1
        ;;
esac
