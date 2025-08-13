#!/bin/bash
# Service: Admin Dashboard Service
# Version: 1.0.0
# Port: 9021
set -e

echo "🚀 Starting Admin Dashboard Service on port 9021..."

# Check dependencies
echo "  Checking dependencies..."
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

if ! command -v npm &> /dev/null; then
    echo "❌ npm not found. Please install npm"
    exit 1
fi

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "  Installing dependencies..."
    npm install
fi

# Check environment
echo "  Checking environment..."
if [ ! -f ".env" ]; then
    echo "⚠️  No environment file found. Using defaults."
fi

# Start service
echo "  Starting service..."
if [ "$NODE_ENV" = "production" ]; then
    echo "  Running in production mode..."
    npm start
else
    echo "  Running in development mode..."
    npm run dev
fi

echo "✅ Admin Dashboard Service started successfully"
