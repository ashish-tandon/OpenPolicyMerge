#!/bin/bash

# OpenPolicy Complete Service Health Check - All Services in Parallel
# This script checks ALL services simultaneously and provides immediate results

echo "🏥 OPENPOLICY COMPLETE SERVICE HEALTH CHECK"
echo "=========================================="
echo "Checking all services in parallel..."
echo ""

# Function to check service health and display result immediately
check_service() {
    local port=$1
    local name=$2
    local endpoint=$3
    
    if curl -s "http://localhost:$port$endpoint" > /dev/null 2>&1; then
        echo "✅ $name (Port $port): RUNNING"
    else
        echo "❌ $name (Port $port): FAILED"
    fi
}

# Check all services in parallel - NO WAITING, immediate results
echo "🐍 Checking Python Services..."
check_service "9001" "policy-service" "/healthz" &
check_service "9002" "search-service" "/healthz" &
check_service "9003" "auth-service" "/healthz" &
check_service "9004" "notification-service" "/healthz" &
check_service "9005" "config-service" "/healthz" &
check_service "9006" "health-service" "/healthz" &
check_service "9007" "etl-service" "/healthz" &
check_service "9008" "scraper-service" "/healthz" &
check_service "9010" "monitoring-service" "/healthz" &
check_service "9011" "plotly-service" "/healthz" &
check_service "9012" "mcp-service" "/healthz" &

echo "🔧 Checking API Gateway..."
check_service "9009" "api-gateway" "/health" &

echo "🌐 Checking Web Frontend..."
check_service "9019" "web-frontend" "/" &

echo "📱 Checking Mobile API..."
check_service "9020" "mobile-api" "/" &

echo ""
echo "📊 Service URLs:"
echo "==============="
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
echo "Web Frontend:       http://localhost:9019"
echo "Mobile API:         http://localhost:9020"

echo ""
echo "📊 Logs available in: /tmp/openpolicy_logs/"
echo "🔍 Monitor with: tail -f /tmp/openpolicy_logs/*.log"
echo ""
echo "🚀 All health checks running in parallel - results will appear above!"
