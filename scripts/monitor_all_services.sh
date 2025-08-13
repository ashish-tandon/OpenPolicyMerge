#!/bin/bash

# OpenPolicy Continuous Service Monitor - Background Monitoring
# This script runs continuously and shows real-time service status

echo "🔍 OPENPOLICY CONTINUOUS SERVICE MONITOR"
echo "======================================="
echo "Starting background monitoring..."
echo "Press Ctrl+C to stop monitoring"
echo ""

# Function to check service health
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

# Function to display all services status
show_status() {
    clear
    echo "🕐 $(date)"
    echo "🏥 OPENPOLICY SERVICE STATUS - LIVE MONITORING"
    echo "============================================="
    echo ""
    
    # Check all services in parallel
    check_service "9001" "policy-service" "/healthz" &
    check_service "9002" "search-service" "/healthz" &
    check_service "9003" "auth-service" "/healthz" &
    check_service "9004" "notification-service" "/healthz" &
    check_service "9005" "config-service" "/healthz" &
    check_service "9006" "health-service" "/healthz" &
    check_service "9007" "etl-service" "/healthz" &
    check_service "9008" "scraper-service" "/healthz" &
    check_service "9009" "api-gateway" "/health" &
    check_service "9010" "monitoring-service" "/healthz" &
    check_service "9011" "plotly-service" "/healthz" &
    check_service "9012" "mcp-service" "/healthz" &
    check_service "3000" "web-frontend" "/" &
    check_service "8081" "mobile-api" "/" &
    
    # Wait for all checks to complete
    wait
    
    echo ""
    echo "📊 Quick Access URLs:"
    echo "===================="
    echo "🌐 Web Frontend:     http://localhost:3000"
    echo "📱 Mobile API:       http://localhost:8081"
    echo "🔧 API Gateway:      http://localhost:9009"
    echo "📊 Monitoring:       http://localhost:9010"
    echo ""
    echo "📝 Logs: /tmp/openpolicy_logs/"
    echo "🔄 Auto-refresh every 5 seconds..."
    echo "⏹️  Press Ctrl+C to stop"
}

# Main monitoring loop
while true; do
    show_status
    sleep 5
done
