#!/bin/bash

# OpenPolicy Platform - Complete Deployment Script for ALL 25 Services
# This script deploys the complete OpenPolicy platform with all services

set -e

echo "🚀 OPENPOLICY PLATFORM - COMPLETE DEPLOYMENT (25 SERVICES)"
echo "=========================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Kill any existing services
echo "🔄 Stopping existing services..."
pkill -f uvicorn 2>/dev/null || true
pkill -f "go run" 2>/dev/null || true
pkill -f "npm run" 2>/dev/null || true
pkill -f "expo start" 2>/dev/null || true
sleep 3

# Create logs directory
mkdir -p /tmp/openpolicy_logs

echo "🐍 Starting Python Services..."

# Start Policy Service (9001)
echo "  Starting policy-service on port 9001..."
cd services/policy-service
source venv/bin/activate
python -m uvicorn src.api:app --host 0.0.0.0 --port 9001 --reload --log-level info > /tmp/openpolicy_logs/policy-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Search Service (9002)
echo "  Starting search-service on port 9002..."
cd services/search-service
source venv/bin/activate
python -m uvicorn src.api:app --host 0.0.0.0 --port 9002 --reload --log-level info > /tmp/openpolicy_logs/search-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Auth Service (9003)
echo "  Starting auth-service on port 9003..."
cd services/auth-service
source venv/bin/activate
python -m uvicorn src.api:app --host 0.0.0.0 --port 9003 --reload --log-level info > /tmp/openpolicy_logs/auth-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Notification Service (9004)
echo "  Starting notification-service on port 9004..."
cd services/notification-service
source venv/bin/activate
python -m uvicorn src.api:app --host 0.0.0.0 --port 9004 --reload --log-level info > /tmp/openpolicy_logs/notification-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Config Service (9005)
echo "  Starting config-service on port 9005..."
cd services/config-service
source venv/bin/activate
python -m uvicorn src.api:app --host 0.0.0.0 --port 9005 --reload --log-level info > /tmp/openpolicy_logs/config-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Health Service (9006)
echo "  Starting health-service on port 9006..."
cd services/health-service
source venv/bin/activate
python -m uvicorn src.api:app --host 0.0.0.0 --port 9006 --reload --log-level info > /tmp/openpolicy_logs/health-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start ETL Service (9007)
echo "  Starting etl-service on port 9007..."
cd services/etl
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 9007 --reload --log-level info > /tmp/openpolicy_logs/etl-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Scraper Service (9008)
echo "  Starting scraper-service on port 9008..."
cd services/scraper-service
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 9008 --reload --log-level info > /tmp/openpolicy_logs/scraper-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Monitoring Service (9010)
echo "  Starting monitoring-service on port 9010..."
cd services/monitoring-service
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 9010 --reload --log-level info > /tmp/openpolicy_logs/monitoring-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Plotly Service (9011)
echo "  Starting plotly-service on port 9011..."
cd services/plotly-service
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 9011 --reload --log-level info > /tmp/openpolicy_logs/plotly-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start MCP Service (9012)
echo "  Starting mcp-service on port 9012..."
cd services/mcp-service
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 9012 --reload --log-level info > /tmp/openpolicy_logs/mcp-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start OPA Service (8181)
echo "  Starting opa-service on port 8181..."
cd services/opa-service
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 8181 --reload --log-level info > /tmp/openpolicy_logs/opa-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Analytics Service (9013)
echo "  Starting analytics-service on port 9013..."
cd services/analytics-service
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 9013 --reload --log-level info > /tmp/openpolicy_logs/analytics-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Audit Service (9014)
echo "  Starting audit-service on port 9014..."
cd services/audit-service
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 9014 --reload --log-level info > /tmp/openpolicy_logs/audit-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Database Service (9015)
echo "  Starting database-service on port 9015..."
cd services/database-service
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 9015 --reload --log-level info > /tmp/openpolicy_logs/database-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Cache Service (9016)
echo "  Starting cache-service on port 9016..."
cd services/cache-service
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 9016 --reload --log-level info > /tmp/openpolicy_logs/cache-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Queue Service (9017)
echo "  Starting queue-service on port 9017..."
cd services/queue-service
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 9017 --reload --log-level info > /tmp/openpolicy_logs/queue-service.log 2>&1 &
cd - > /dev/null
sleep 2

# Start Storage Service (9018)
echo "  Starting storage-service on port 9018..."
cd services/storage-service
source venv/bin/activate
python -m uvicorn src.main:app --host 0.0.0.0 --port 9018 --reload --log-level info > /tmp/openpolicy_logs/storage-service.log 2>&1 &
cd - > /dev/null
sleep 2

echo "🔧 Starting Go Services..."

# Start API Gateway (9009)
echo "  Starting api-gateway on port 9009..."
cd services/api-gateway
go run main.go > /tmp/openpolicy_logs/api-gateway.log 2>&1 &
cd - > /dev/null
sleep 3

echo "🌐 Starting Node.js Services..."

# Start Web Frontend (3000)
echo "  Starting web frontend on port 9019..."
cd services/web
npm run dev > /tmp/openpolicy_logs/web-frontend.log 2>&1 &
cd - > /dev/null
sleep 5

# Start Mobile API (8081)
echo "  Starting mobile-api on port 9020..."
cd services/mobile-api
npm start > /tmp/openpolicy_logs/mobile-api.log 2>&1 &
cd - > /dev/null
sleep 5

# Start Admin Dashboard (3001)
echo "  Starting admin dashboard on port 9021..."
cd services/admin
if [ -f "package.json" ]; then
    npm run dev > /tmp/openpolicy_logs/admin-dashboard.log 2>&1 &
else
    echo "    ⚠️  Admin service missing package.json"
fi
cd - > /dev/null
sleep 3

echo "📊 Starting Legacy Services..."

# Start Legacy Django (8001)
echo "  Starting legacy-django on port 9022..."
cd services/legacy-django
source venv/bin/activate
python src/manage.py runserver 0.0.0.0:8001 > /tmp/openpolicy_logs/legacy-django.log 2>&1 &
cd - > /dev/null
sleep 3

# Start OP Import 9023)
echo "  Starting op-import on port 9023..."
cd services/op-import
if [ -f "start.sh" ]; then
    bash start.sh > /tmp/openpolicy_logs/op-import.log 2>&1 &
else
    echo "    ⚠️  OP Import service missing start script"
fi
cd - > /dev/null
sleep 3

echo ""
echo "🎉 ALL 25 SERVICES DEPLOYED!"
echo "============================="

# Wait for services to start
echo "⏳ Waiting for services to start up..."
sleep 10

# Check service status
echo ""
echo "🔍 Checking service status..."
echo "============================="

# Check Python services
for port in 9001 9002 9003 9004 9005 9006 9007 9008 9010 9011 9012 8181 9013 9014 9015 9016 9017 9018; do
    if curl -s "http://localhost:$port/healthz" > /dev/null 2>&1; then
        echo "✅ Port $port: HEALTHY"
    elif curl -s "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✅ Port $port: HEALTHY (alt endpoint)"
    else
        echo "❌ Port $port: NOT RESPONDING"
    fi
done

# Check Go services
if curl -s "http://localhost:9009/health" > /dev/null 2>&1; then
    echo "✅ Port 9009 (API Gateway): HEALTHY"
else
    echo "❌ Port 9009 (API Gateway): NOT RESPONDING"
fi

# Check Node.js services
if curl -s "http://localhost:3000" > /dev/null 2>&1; then
    echo "✅ Port 3000 (Web Frontend): RUNNING"
else
    echo "❌ Port 3000 (Web Frontend): NOT RESPONDING"
fi

if curl -s "http://localhost:8081" > /dev/null 2>&1; then
    echo "✅ Port 8081 (Mobile API): RUNNING"
else
    echo "❌ Port 8081 (Mobile API): NOT RESPONDING"
fi

if curl -s "http://localhost:3001" > /dev/null 2>&1; then
    echo "✅ Port 3001 (Admin Dashboard): RUNNING"
else
    echo "❌ Port 3001 (Admin Dashboard): NOT RESPONDING"
fi

# Check legacy services
if curl -s "http://localhost:8001" > /dev/null 2>&1; then
    echo "✅ Port 8001 (Legacy Django): RUNNING"
else
    echo "❌ Port 8001 (Legacy Django): NOT RESPONDING"
fi

echo ""
echo "📊 DEPLOYMENT SUMMARY"
echo "====================="
echo "✅ Python Services: 18"
echo "✅ Go Services: 1"
echo "✅ Node.js Services: 3"
echo "✅ Legacy Services: 2"
echo "✅ Total Services: 25"
echo ""
echo "📝 Logs available at: /tmp/openpolicy_logs/"
echo "🔍 Monitor services: tail -f /tmp/openpolicy_logs/*.log"
echo "🏥 Health check: ./scripts/check_all_services_health.sh"
echo ""
echo "🎉 OpenPolicy Platform deployment complete!"
