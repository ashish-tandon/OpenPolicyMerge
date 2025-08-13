#!/bin/bash

# OpenPolicy Complete Service Deployment Script
# This script starts ALL services in the correct order with proper port management

set -e

echo "🚀 OPENPOLICY COMPLETE SERVICE DEPLOYMENT"
echo "=========================================="

# Kill any existing services
echo "🔄 Stopping existing services..."
pkill -f uvicorn 2>/dev/null || true
pkill -f "go run" 2>/dev/null || true
pkill -f "npm run" 2>/dev/null || true
pkill -f "expo start" 2>/dev/null || true
sleep 2

# Create logs directory
mkdir -p /tmp/openpolicy_logs

echo "🐍 Starting Python Services..."

# Start Policy Service
echo "  Starting policy-service on port 9001..."
cd services/policy-service
python -m uvicorn src.api:app --host 0.0.0.0 --port 9001 --reload --log-level debug > /tmp/openpolicy_logs/policy-service.log 2>&1 &
cd - > /dev/null
sleep 1

# Start Search Service
echo "  Starting search-service on port 9002..."
cd services/search-service
python -m uvicorn src.api:app --host 0.0.0.0 --port 9002 --reload --log-level debug > /tmp/openpolicy_logs/search-service.log 2>&1 &
cd - > /dev/null
sleep 1

# Start Auth Service
echo "  Starting auth-service on port 9003..."
cd services/auth-service
python -m uvicorn src.api:app --host 0.0.0.0 --port 9003 --reload --log-level debug > /tmp/openpolicy_logs/auth-service.log 2>&1 &
cd - > /dev/null
sleep 1

# Start Notification Service
echo "  Starting notification-service on port 9004..."
cd services/notification-service
python -m uvicorn src.api:app --host 0.0.0.0 --port 9004 --reload --log-level debug > /tmp/openpolicy_logs/notification-service.log 2>&1 &
cd - > /dev/null
sleep 1

# Start Config Service
echo "  Starting config-service on port 9005..."
cd services/config-service
python -m uvicorn src.api:app --host 0.0.0.0 --port 9005 --reload --log-level debug > /tmp/openpolicy_logs/config-service.log 2>&1 &
cd - > /dev/null
sleep 1

# Start Health Service
echo "  Starting health-service on port 9006..."
cd services/health-service
python -m uvicorn src.api:app --host 0.0.0.0 --port 9006 --reload --log-level debug > /tmp/openpolicy_logs/health-service.log 2>&1 &
cd - > /dev/null
sleep 1

# Start ETL Service
echo "  Starting etl-service on port 9007..."
cd services/etl
python -m uvicorn src.api:app --host 0.0.0.0 --port 9007 --reload --log-level debug > /tmp/openpolicy_logs/etl-service.log 2>&1 &
cd - > /dev/null
sleep 1

# Start Scraper Service
echo "  Starting scraper-service on port 9008..."
cd services/scraper-service
python -m uvicorn src.api:app --host 0.0.0.0 --port 9008 --reload --log-level debug > /tmp/openpolicy_logs/scraper-service.log 2>&1 &
cd - > /dev/null
sleep 1

# Start Monitoring Service
echo "  Starting monitoring-service on port 9010..."
cd services/monitoring-service
python -m uvicorn src.main:app --host 0.0.0.0 --port 9010 --reload --log-level debug > /tmp/openpolicy_logs/monitoring-service.log 2>&1 &
cd - > /dev/null
sleep 1

# Start Plotly Service
echo "  Starting plotly-service on port 9011..."
cd services/plotly-service
python -m uvicorn src.main:app --host 0.0.0.0 --port 9011 --reload --log-level debug > /tmp/openpolicy_logs/plotly-service.log 2>&1 &
cd - > /dev/null
sleep 1

# Start MCP Service
echo "  Starting mcp-service on port 9012..."
cd services/mcp-service
python -m uvicorn src.main:app --host 0.0.0.0 --port 9012 --reload --log-level debug > /tmp/openpolicy_logs/mcp-service.log 2>&1 &
cd - > /dev/null
sleep 1

# Start API Gateway (Go)
echo "🔧 Starting API Gateway (Go)..."
cd services/api-gateway
go run src/main.go > /tmp/openpolicy_logs/api-gateway.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Web Frontend (Next.js)
echo "🌐 Starting Web Frontend (Next.js)..."
cd services/web
npm run dev > /tmp/openpolicy_logs/web-frontend.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Mobile API (Expo)
echo "📱 Starting Mobile API (Expo)..."
cd services/mobile-api
npx expo start --web > /tmp/openpolicy_logs/mobile-api.log 2>&1 &
cd - > /dev/null
sleep 2

# Wait for services to start
echo "⏳ Waiting for services to start..."
sleep 15

# Health Check
echo "🏥 Performing Health Check..."
echo ""
echo "Service Status:"
echo "==============="

# Check Python Services
services=("9001:policy-service" "9002:search-service" "9003:auth-service" "9004:notification-service" "9005:config-service" "9006:health-service" "9007:etl-service" "9008:scraper-service" "9010:monitoring-service" "9011:plotly-service" "9012:mcp-service")

for service in "${services[@]}"; do
    IFS=':' read -r port name <<< "$service"
    if curl -s "http://localhost:$port/healthz" > /dev/null 2>&1; then
        echo "✅ $name (Port $port): RUNNING"
    else
        echo "❌ $name (Port $port): FAILED"
    fi
done

# Check API Gateway
if curl -s "http://localhost:9009/health" > /dev/null 2>&1; then
    echo "✅ API Gateway (Port 9009): RUNNING"
else
    echo "❌ API Gateway (Port 9009): FAILED"
fi

# Check Web Frontend
if curl -s "http://localhost:3000" > /dev/null 2>&1; then
    echo "✅ Web Frontend (Port 3000): RUNNING"
else
    echo "❌ Web Frontend (Port 3000): FAILED"
fi

# Check Mobile API
if curl -s "http://localhost:8081" > /dev/null 2>&1; then
    echo "✅ Mobile API (Port 8081): RUNNING"
else
    echo "❌ Mobile API (Port 8081): FAILED"
fi

echo ""
echo "🎉 Deployment Complete!"
echo "📊 Logs available in: /tmp/openpolicy_logs/"
echo "🔍 Monitor with: tail -f /tmp/openpolicy_logs/*.log"
echo ""
echo "Service URLs:"
echo "============="
echo "Policy Service:     http://localhost:9001"
echo "Search Service:     http://localhost:9002"
echo "Auth Service:       http://localhost:9003"
echo "Notification:       http://localhost:9004"
echo "Config Service:     http://localhost:9005"
echo "Health Service:     http://localhost:9006"
echo "ETL Service:        http://localhost:9007"
echo "Scraper Service:    http://localhost:9008"
echo "API Gateway:        http://localhost:9009"
echo "Monitoring:         http://localhost:9010"
echo "Plotly Service:     http://localhost:9011"
echo "MCP Service:        http://localhost:9012"
echo "Web Frontend:       http://localhost:3000"
echo "Mobile API:         http://localhost:8081"
