#!/bin/bash
# Service: Error Reporting Service
# Version: 1.0.0
# Port: 9024
set -e

echo "🚀 Starting Error Reporting Service on port 9024..."

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

# Start service
echo "  Starting service..."
if [ "$ENVIRONMENT" = "production" ]; then
    echo "  Running in production mode..."
    python3 -m uvicorn src.main:app --host 0.0.0.0 --port 9024 --workers 4
else
    echo "  Running in development mode..."
    python3 -m uvicorn src.main:app --host 0.0.0.0 --port 9024 --reload
fi

echo "✅ Error Reporting Service started successfully"
