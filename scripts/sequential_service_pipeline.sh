#!/bin/bash

# OpenPolicy Sequential Service Pipeline
# This script processes each service in sequence: Start → Health Check → Basic Test → Status Report
# Each service runs independently and we can see exactly where each one fails

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Create logs directory
mkdir -p /tmp/openpolicy_logs
mkdir -p /tmp/service_status

# Service definitions with proper ports and entry points
declare -A SERVICES=(
    ["policy-service"]="9001:src.api:app"
    ["search-service"]="9002:src.api:app"
    ["auth-service"]="9003:src.api:app"
    ["notification-service"]="9004:src.api:app"
    ["config-service"]="9005:src.api:app"
    ["health-service"]="9006:src.api:app"
    ["etl"]="9007:src.main:app"
    ["scraper-service"]="9008:src.api:app"
    ["api-gateway"]="9009:go"
    ["monitoring-service"]="9010:src.main:app"
    ["plotly-service"]="9011:src.api:app"
    ["mcp-service"]="9012:src.api:app"
    ["web"]="3000:npm"
    ["mobile-api"]="8081:expo"
    ["legacy-django"]="8000:django"
    ["admin"]="3001:npm"
    ["op-import"]="9013:src.api:app"
)

# Function to completely kill a service
kill_service() {
    local service_name=$1
    local port=$2
    
    echo -e "${YELLOW}🛑 Killing $service_name on port $port...${NC}"
    
    # Kill by port
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    
    # Kill by process name
    pkill -f "$service_name" 2>/dev/null || true
    
    # Kill by uvicorn if Python service
    if [[ $service_name == *"-service" ]] || [[ $service_name == "etl" ]] || [[ $service_name == "monitoring-service" ]] || [[ $service_name == "plotly-service" ]] || [[ $service_name == "mcp-service" ]] || [[ $service_name == "op-import" ]]; then
        pkill -f "uvicorn.*$port" 2>/dev/null || true
    fi
    
    # Kill by go if Go service
    if [[ $service_name == "api-gateway" ]]; then
        pkill -f "go run.*$service_name" 2>/dev/null || true
    fi
    
    # Kill by npm if Node service
    if [[ $service_name == "web" ]] || [[ $service_name == "admin" ]]; then
        pkill -f "npm.*$service_name" 2>/dev/null || true
    fi
    
    # Kill by expo if Expo service
    if [[ $service_name == "mobile-api" ]]; then
        pkill -f "expo.*$service_name" 2>/dev/null || true
    fi
    
    # Wait a moment for process to die
    sleep 2
    
    # Verify port is free
    if lsof -i:$port >/dev/null 2>&1; then
        echo -e "${RED}❌ Port $port still in use after kill attempt${NC}"
        return 1
    else
        echo -e "${GREEN}✅ Port $port is now free${NC}"
        return 0
    fi
}

# Function to start a service
start_service() {
    local service_name=$1
    local port=$2
    local entry_point=$3
    
    echo -e "${BLUE}🚀 Starting $service_name on port $port...${NC}"
    
    cd "services/$service_name"
    
    case $entry_point in
        "src.api:app"|"src.main:app")
            python -m uvicorn $entry_point --host 0.0.0.0 --port $port --reload > "/tmp/openpolicy_logs/${service_name}.log" 2>&1 &
            ;;
        "go")
            go run src/main.go > "/tmp/openpolicy_logs/${service_name}.log" 2>&1 &
            ;;
        "npm")
            npm run dev > "/tmp/openpolicy_logs/${service_name}.log" 2>&1 &
            ;;
        "expo")
            npx expo start --web --port $port > "/tmp/openpolicy_logs/${service_name}.log" 2>&1 &
            ;;
        "django")
            python manage.py runserver 0.0.0.0:$port > "/tmp/openpolicy_logs/${service_name}.log" 2>&1 &
            ;;
    esac
    
    local pid=$!
    echo $pid > "/tmp/service_status/${service_name}.pid"
    
    cd ../..
    
    # Wait for service to start
    echo -e "${YELLOW}⏳ Waiting for $service_name to start...${NC}"
    sleep 5
    
    return 0
}

# Function to health check a service
health_check_service() {
    local service_name=$1
    local port=$2
    
    echo -e "${BLUE}🏥 Health checking $service_name on port $port...${NC}"
    
    # Determine health endpoint based on service type
    local health_endpoint="/healthz"
    if [[ $service_name == "api-gateway" ]]; then
        health_endpoint="/health"
    elif [[ $service_name == "web" ]] || [[ $service_name == "admin" ]] || [[ $service_name == "mobile-api" ]]; then
        health_endpoint="/"
    fi
    
    # Try health check
    if curl -s "http://localhost:$port$health_endpoint" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name health check PASSED${NC}"
        echo "HEALTHY" > "/tmp/service_status/${service_name}.health"
        return 0
    else
        echo -e "${RED}❌ $service_name health check FAILED${NC}"
        echo "UNHEALTHY" > "/tmp/service_status/${service_name}.health"
        return 1
    fi
}

# Function to basic test a service
basic_test_service() {
    local service_name=$1
    local port=$2
    
    echo -e "${BLUE}🧪 Basic testing $service_name on port $port...${NC}"
    
    # Basic connectivity test
    if curl -s "http://localhost:$port" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $service_name basic connectivity PASSED${NC}"
        echo "PASSED" > "/tmp/service_status/${service_name}.test"
        return 0
    else
        echo -e "${RED}❌ $service_name basic connectivity FAILED${NC}"
        echo "FAILED" > "/tmp/service_status/${service_name}.test"
        return 1
    fi
}

# Function to generate status report for a service
generate_status_report() {
    local service_name=$1
    local port=$2
    
    echo -e "${BLUE}📊 Generating status report for $service_name...${NC}"
    
    local health_status="UNKNOWN"
    local test_status="UNKNOWN"
    local pid="UNKNOWN"
    
    if [[ -f "/tmp/service_status/${service_name}.health" ]]; then
        health_status=$(cat "/tmp/service_status/${service_name}.health")
    fi
    
    if [[ -f "/tmp/service_status/${service_name}.test" ]]; then
        test_status=$(cat "/tmp/service_status/${service_name}.test")
    fi
    
    if [[ -f "/tmp/service_status/${service_name}.pid" ]]; then
        pid=$(cat "/tmp/service_status/${service_name}.pid")
    fi
    
    # Check if process is still running
    local process_status="STOPPED"
    if [[ $pid != "UNKNOWN" ]] && kill -0 $pid 2>/dev/null; then
        process_status="RUNNING"
    fi
    
    # Check port status
    local port_status="FREE"
    if lsof -i:$port >/dev/null 2>&1; then
        port_status="IN_USE"
    fi
    
    # Generate report
    cat > "/tmp/service_status/${service_name}.report" << EOF
SERVICE STATUS REPORT: $service_name
=====================================
Timestamp: $(date)
Port: $port
Process ID: $pid
Process Status: $process_status
Port Status: $port_status
Health Check: $health_status
Basic Test: $test_status

Recent Logs (last 10 lines):
$(tail -10 "/tmp/openpolicy_logs/${service_name}.log" 2>/dev/null || echo "No logs available")

Port Usage:
$(lsof -i:$port 2>/dev/null || echo "Port is free")
EOF

    echo -e "${GREEN}✅ Status report generated for $service_name${NC}"
}

# Function to process a single service through the pipeline
process_service() {
    local service_name=$1
    local port=$2
    local entry_point=$3
    
    echo ""
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}PROCESSING SERVICE: $service_name${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    # Step 1: Kill existing service
    if ! kill_service "$service_name" "$port"; then
        echo -e "${RED}❌ Failed to kill $service_name, skipping...${NC}"
        return 1
    fi
    
    # Step 2: Start service
    if ! start_service "$service_name" "$port" "$entry_point"; then
        echo -e "${RED}❌ Failed to start $service_name${NC}"
        return 1
    fi
    
    # Step 3: Health check
    if ! health_check_service "$service_name" "$port"; then
        echo -e "${YELLOW}⚠️  $service_name health check failed, but continuing...${NC}"
    fi
    
    # Step 4: Basic test
    if ! basic_test_service "$service_name" "$port"; then
        echo -e "${YELLOW}⚠️  $service_name basic test failed, but continuing...${NC}"
    fi
    
    # Step 5: Generate status report
    generate_status_report "$service_name" "$port"
    
    echo -e "${GREEN}✅ Completed pipeline for $service_name${NC}"
    echo ""
}

# Main execution
main() {
    echo -e "${BLUE}🚀 OPENPOLICY SEQUENTIAL SERVICE PIPELINE${NC}"
    echo -e "${BLUE}========================================${NC}"
    echo "Processing ${#SERVICES[@]} services sequentially"
    echo "Each service will be: Started → Health Checked → Tested → Status Reported"
    echo ""
    
    # Process each service
    for service_name in "${!SERVICES[@]}"; do
        IFS=':' read -r port entry_point <<< "${SERVICES[$service_name]}"
        process_service "$service_name" "$port" "$entry_point"
        
        # Small delay between services
        sleep 2
    done
    
    # Generate final summary
    echo -e "${BLUE}========================================${NC}"
    echo -e "${BLUE}FINAL SUMMARY${NC}"
    echo -e "${BLUE}========================================${NC}"
    
    for service_name in "${!SERVICES[@]}"; do
        if [[ -f "/tmp/service_status/${service_name}.report" ]]; then
            echo -e "${GREEN}✅ $service_name: Report generated${NC}"
        else
            echo -e "${RED}❌ $service_name: No report generated${NC}"
        fi
    done
    
    echo ""
    echo -e "${GREEN}🎉 Pipeline complete! Check /tmp/service_status/ for individual reports${NC}"
    echo -e "${GREEN}📊 Monitor logs with: tail -f /tmp/openpolicy_logs/*.log${NC}"
}

# Run main function
main "$@"
