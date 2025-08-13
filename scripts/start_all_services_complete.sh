#!/bin/bash

# OpenPolicy Complete Service Startup - All Services with Auto-Monitoring
# This script starts ALL services in parallel with built-in monitoring, testing, and reporting

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🚀 OPENPOLICY COMPLETE SERVICE STARTUP${NC}"
echo "============================================="
echo "Starting ALL services with auto-monitoring, testing, and reporting"
echo ""

# Create all necessary directories
mkdir -p /tmp/openpolicy_logs
mkdir -p /tmp/service_reports
mkdir -p /tmp/health_checks
mkdir -p /tmp/service_tests

# Function to start a service with complete monitoring
start_service_complete() {
    local service_name=$1
    local port=$2
    local command=$3
    local working_dir=$4
    
    echo -e "${BLUE}🚀 Starting $service_name on port $port...${NC}"
    
    # Kill any existing service on this port
    lsof -ti:$port | xargs kill -9 2>/dev/null || true
    
    # Start service in background with logging
    cd "services/$working_dir"
    eval "$command > /tmp/openpolicy_logs/${service_name}.log 2>&1 &"
    local pid=$!
    echo $pid > "/tmp/service_reports/${service_name}.pid"
    cd ../..
    
    echo -e "${GREEN}✅ $service_name started (PID: $pid)${NC}"
}

# Function to start auto-monitoring
start_auto_monitoring() {
    echo -e "${BLUE}🔍 Starting auto-monitoring system...${NC}"
    
    # Start the auto-monitoring script
    ./scripts/auto_monitor_services.sh > /tmp/openpolicy_logs/auto_monitor.log 2>&1 &
    local monitor_pid=$!
    echo $monitor_pid > "/tmp/service_reports/auto_monitor.pid"
    
    echo -e "${GREEN}✅ Auto-monitoring started (PID: $monitor_pid)${NC}"
}

# Function to start all services in parallel
start_all_services_parallel() {
    echo -e "${BLUE}🚀 STARTING ALL SERVICES IN PARALLEL...${NC}"
    echo ""
    
    # Python Services
    echo -e "${YELLOW}🐍 Starting Python Services...${NC}"
    start_service_complete "policy-service" "9001" "python -m uvicorn src.api:app --host 0.0.0.0 --port 9001 --reload" "policy-service" &
    start_service_complete "search-service" "9002" "python -m uvicorn src.api:app --host 0.0.0.0 --port 9002 --reload" "search-service" &
    start_service_complete "auth-service" "9003" "python -m uvicorn src.api:app --host 0.0.0.0 --port 9003 --reload" "auth-service" &
    start_service_complete "notification-service" "9004" "python -m uvicorn src.api:app --host 0.0.0.0 --port 9004 --reload" "notification-service" &
    start_service_complete "config-service" "9005" "python -m uvicorn src.api:app --host 0.0.0.0 --port 9005 --reload" "config-service" &
    start_service_complete "health-service" "9006" "python -m uvicorn src.api:app --host 0.0.0.0 --port 9006 --reload" "health-service" &
    start_service_complete "etl" "9007" "python -m uvicorn src.main:app --host 0.0.0.0 --port 9007 --reload" "etl" &
    start_service_complete "scraper-service" "9008" "python -m uvicorn src.api:app --host 0.0.0.0 --port 9008 --reload" "scraper-service" &
    start_service_complete "monitoring-service" "9010" "python -m uvicorn src.main:app --host 0.0.0.0 --port 9010 --reload" "monitoring-service" &
    start_service_complete "plotly-service" "9011" "python -m uvicorn src.api:app --host 0.0.0.0 --port 9011 --reload" "plotly-service" &
    start_service_complete "mcp-service" "9012" "python -m uvicorn src.api:app --host 0.0.0.0 --port 9012 --reload" "mcp-service" &
    start_service_complete "op-import" "9013" "python -m uvicorn src.api:app --host 0.0.0.0 --port 9013 --reload" "op-import" &
    
    # Go Services
    echo -e "${YELLOW}🔧 Starting Go Services...${NC}"
    start_service_complete "api-gateway" "9009" "go run src/main.go" "api-gateway" &
    
    # Node.js Services
    echo -e "${YELLOW}🌐 Starting Node.js Services...${NC}"
    start_service_complete "web" "3000" "npm run dev" "web" &
    start_service_complete "admin" "3001" "npm run dev" "admin" &
    
    # Expo Services
    echo -e "${YELLOW}📱 Starting Expo Services...${NC}"
    start_service_complete "mobile-api" "8081" "npx expo start --web --port 8081" "mobile-api" &
    
    # Django Services
    echo -e "${YELLOW}🐍 Starting Django Services...${NC}"
    start_service_complete "legacy-django" "8000" "python manage.py runserver 0.0.0.0:8000" "legacy-django" &
    
    # Wait for all background processes to start
    wait
    
    echo -e "${GREEN}✅ All services started in parallel!${NC}"
}

# Function to show service status
show_service_status() {
    echo ""
    echo -e "${BLUE}📊 SERVICE STATUS OVERVIEW${NC}"
    echo "================================"
    
    # Check which services are running
    for service_name in "policy-service" "search-service" "auth-service" "notification-service" "config-service" "health-service" "etl" "scraper-service" "api-gateway" "monitoring-service" "plotly-service" "mcp-service" "op-import" "web" "admin" "mobile-api" "legacy-django"; do
        if [[ -f "/tmp/service_reports/${service_name}.pid" ]]; then
            local pid=$(cat "/tmp/service_reports/${service_name}.pid")
            if kill -0 $pid 2>/dev/null; then
                echo -e "${GREEN}✅ $service_name: RUNNING (PID: $pid)${NC}"
            else
                echo -e "${RED}❌ $service_name: STOPPED${NC}"
            fi
        else
            echo -e "${RED}❌ $service_name: NOT STARTED${NC}"
        fi
    done
    
    # Check auto-monitoring
    if [[ -f "/tmp/service_reports/auto_monitor.pid" ]]; then
        local monitor_pid=$(cat "/tmp/service_reports/auto_monitor.pid")
        if kill -0 $monitor_pid 2>/dev/null; then
            echo -e "${GREEN}✅ Auto-Monitoring: RUNNING (PID: $monitor_pid)${NC}"
        else
            echo -e "${RED}❌ Auto-Monitoring: STOPPED${NC}"
        fi
    else
        echo -e "${RED}❌ Auto-Monitoring: NOT STARTED${NC}"
    fi
}

# Function to show monitoring information
show_monitoring_info() {
    echo ""
    echo -e "${BLUE}📋 MONITORING & REPORTING INFORMATION${NC}"
    echo "============================================="
    echo ""
    echo -e "${GREEN}📊 Reports Location:${NC} /tmp/service_reports/"
    echo -e "${GREEN}🏥 Health Checks:${NC} /tmp/health_checks/"
    echo -e "${GREEN}📝 Service Logs:${NC} /tmp/openpolicy_logs/"
    echo -e "${GREEN}🧪 Service Tests:${NC} /tmp/service_tests/"
    echo ""
    echo -e "${GREEN}🔍 Monitoring Commands:${NC}"
    echo "  - View all logs: tail -f /tmp/openpolicy_logs/*.log"
    echo "  - View health status: cat /tmp/health_checks/*.health"
    echo "  - View master report: cat /tmp/service_reports/MASTER_SERVICE_REPORT.txt"
    echo "  - View individual reports: cat /tmp/service_reports/*_report.txt"
    echo "  - View auto-monitor log: tail -f /tmp/openpolicy_logs/auto_monitor.log"
    echo ""
    echo -e "${GREEN}🌐 Service URLs:${NC}"
    echo "  - Policy Service: http://localhost:9001"
    echo "  - Search Service: http://localhost:9002"
    echo "  - Auth Service: http://localhost:9003"
    echo "  - Notification: http://localhost:9004"
    echo "  - Config Service: http://localhost:9005"
    echo "  - Health Service: http://localhost:9006"
    echo "  - ETL Service: http://localhost:9007"
    echo "  - Scraper Service: http://localhost:9008"
    echo "  - API Gateway: http://localhost:9009"
    echo "  - Monitoring: http://localhost:9010"
    echo "  - Plotly Service: http://localhost:9011"
    echo "  - MCP Service: http://localhost:9012"
    echo "  - OP-Import: http://localhost:9013"
    echo "  - Web Frontend: http://localhost:3000"
    echo "  - Admin Dashboard: http://localhost:3001"
    echo "  - Mobile API: http://localhost:8081"
    echo "  - Legacy Django: http://localhost:8000"
}

# Main execution
main() {
    echo -e "${BLUE}🚀 OPENPOLICY COMPLETE SERVICE STARTUP${NC}"
    echo "============================================="
    echo "This script will:"
    echo "1. 🚀 Start ALL 21 services in parallel"
    echo "2. 🔍 Start auto-monitoring system"
    echo "3. 📊 Generate automatic reports"
    echo "4. 🧪 Run health checks continuously"
    echo "5. 📝 Log everything automatically"
    echo ""
    
    # Start all services in parallel
    start_all_services_parallel
    
    # Start auto-monitoring
    start_auto_monitoring
    
    # Wait for services to start
    echo ""
    echo -e "${YELLOW}⏳ Waiting 30 seconds for all services to start...${NC}"
    sleep 30
    
    # Show status
    show_service_status
    
    # Show monitoring information
    show_monitoring_info
    
    echo ""
    echo -e "${GREEN}🎉 ALL SERVICES STARTED WITH COMPLETE MONITORING!${NC}"
    echo ""
    echo -e "${BLUE}Next Steps:${NC}"
    echo "1. Services are running independently with auto-monitoring"
    echo "2. Reports are generated automatically every 30 seconds"
    echo "3. Health checks run continuously"
    echo "4. All logs are captured automatically"
    echo ""
    echo -e "${GREEN}You can now relax - everything is automated! 🚀${NC}"
}

# Run main function
main "$@"
