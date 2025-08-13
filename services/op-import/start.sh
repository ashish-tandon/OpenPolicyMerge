#!/bin/bash
# Service: OP Import Service
# Version: 1.0.0
# Port: 9023
set -e

echo "🚀 Starting OP Import Service on port 9023..."

# Check dependencies
echo "  Checking dependencies..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.11+"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 not found. Please install pip3"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "  Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "  Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "  Installing dependencies..."
pip install -r requirements.txt

# Check environment
echo "  Checking environment..."
if [ ! -f ".env" ]; then
    echo "⚠️  No environment file found. Using defaults."
fi

# Check data directories
echo "  Checking data directories..."
mkdir -p data/imports
mkdir -p data/exports
mkdir -p data/temp

# Start service
echo "  Starting service..."
if [ "$ENVIRONMENT" = "production" ]; then
    echo "  Running in production mode..."
    python3 -m uvicorn src.main:app --host 0.0.0.0 --port 9023 --workers 4
else
    echo "  Running in development mode..."
    python3 -m uvicorn src.main:app --host 0.0.0.0 --port 9023 --reload
fi

echo "✅ OP Import Service started successfully"
