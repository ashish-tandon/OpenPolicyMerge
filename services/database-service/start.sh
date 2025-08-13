#!/bin/bash

# Service: Database Service
# Version: 1.0.0
# Port: 9015

set -e

echo "🚀 Starting Database Service on port 9015..."

# Check dependencies
echo "  Checking dependencies..."
# Add dependency checks here

# Start service
echo "  Starting service..."
python -m uvicorn src.main:app --host 0.0.0.0 --port 9015 --reload --log-level info

echo "✅ Database Service started successfully"
