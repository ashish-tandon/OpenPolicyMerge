#!/bin/bash
# Service: Legacy Django Service
# Version: 1.0.0
# Port: 9022
set -e

echo "🚀 Starting Legacy Django Service on port 9022..."

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

# Run Django migrations
echo "  Running Django migrations..."
python3 src/manage.py migrate --noinput

# Collect static files
echo "  Collecting static files..."
python3 src/manage.py collectstatic --noinput

# Start service
echo "  Starting service..."
if [ "$DJANGO_DEBUG" = "true" ]; then
    echo "  Running in development mode..."
    python3 src/manage.py runserver 0.0.0.0:9022
else
    echo "  Running in production mode..."
    gunicorn represent.wsgi:application --bind 0.0.0.0:9022 --workers 4
fi

echo "✅ Legacy Django Service started successfully"
