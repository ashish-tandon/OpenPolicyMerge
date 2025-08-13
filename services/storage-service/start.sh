#!/bin/bash

# Service: Storage Service
# Version: 1.0.0
# Port: 9018
# Description: File storage service for OpenPolicy platform

set -e

echo "🚀 Starting Storage Service on port 9018..."
echo "  Service: Storage Service"
echo "  Port: 9018"
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
python -m uvicorn src.main:app --host 0.0.0.0 --port 9018 --reload --log-level info

echo "✅ Storage Service started successfully"
