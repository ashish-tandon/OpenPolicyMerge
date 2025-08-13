#!/bin/bash

# Service: OPA Service
# Version: 1.0.0
# Port: 8181
# Description: Open Policy Agent service for OpenPolicy platform

set -e

echo "🚀 Starting OPA Service on port 8181..."
echo "  Service: OPA Service"
echo "  Port: 8181"
echo "  Version: 1.0.0"
echo ""

# Check dependencies
echo "  Checking dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 not found"
    exit 1
fi

# Check virtual environment
if [[ ! -d "venv" ]]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "  Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "  Installing dependencies..."
pip install -r requirements.txt

# Start service
echo "  Starting service..."
python -m uvicorn src.main:app --host 0.0.0.0 --port 8181 --reload --log-level info

echo "✅ OPA Service started successfully"
