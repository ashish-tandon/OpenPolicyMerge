#!/bin/bash

echo "🚀 Starting OpenPolicy Merge - Unified Civic Data Platform"
echo "=========================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install it and try again."
    exit 1
fi

echo "✅ Docker environment check passed"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data
mkdir -p ssl

# Set permissions for data directory
chmod 755 data

echo "🔧 Starting all services..."
docker-compose up -d

echo "⏳ Waiting for services to start..."
sleep 30

echo "🔍 Checking service status..."
docker-compose ps

echo ""
echo "🎉 OpenPolicy Merge is now running!"
echo ""
echo "📱 Access your services at:"
echo "   • Main API: http://localhost:8080"
echo "   • Web Frontend: http://localhost:3000"
echo "   • Django Backend: http://localhost:8000"
echo "   • Laravel Backend: http://localhost:8001"
echo "   • Represent Service: http://localhost:8002"
echo "   • Nginx Proxy: http://localhost:80"
echo "   • Prometheus: http://localhost:9090"
echo "   • Grafana: http://localhost:3001"
echo ""
echo "📊 API Documentation: http://localhost:8080/docs"
echo "🔐 Grafana Login: admin/admin"
echo ""
echo "📋 To view logs: docker-compose logs -f"
echo "🛑 To stop: docker-compose down"
echo ""
echo "✨ Happy exploring Canadian civic data!"
