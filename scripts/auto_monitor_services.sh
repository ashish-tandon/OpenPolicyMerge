#!/bin/bash

# OpenPolicy Auto-Monitoring Chain
# This script automatically monitors all services and generates reports

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Create monitoring directories
mkdir -p /tmp/openpolicy_logs
mkdir -p /tmp/service_reports
mkdir -p /tmp/health_checks

# Service definitions using indexed arrays for compatibility
SERVICE_NAMES=(
    "policy-service" "search-service" "auth-service" "notification-service" 
    "config-service" "health-service" "etl" "scraper-service" "api-gateway" 
    "monitoring-service" "plotly-service" "mcp-service" "op-import" 
    "web" "admin" "mobile-api" "legacy-django"
)

SERVICE_PORTS=(
    "9001" "9002" "9003" "9004" "9005" "9006" "9007" "9008" "9009" 
    "9010" "9011" "9012" "9013" "3000" "3001" "8081" "8000"
)

SERVICE_ENDPOINTS=(
    "/healthz" "/healthz" "/healthz" "/healthz" "/healthz" "/healthz" 
    "/healthz" "/healthz" "/health" "/healthz" "/healthz" "/healthz" 
    "/healthz" "/" "/" "/" "/"
)

# Function to check service health
check_service_health() {
    local service_name=$1
    local port=$2
    local endpoint=$3
    
    local health_file="/tmp/health_checks/${service_name}.health"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    if curl -s "http://localhost:$port$endpoint" > /dev/null 2>&1; then
        echo "✅ $service_name: HEALTHY" > "$health_file"
        echo "$timestamp|$service_name|HEALTHY|$port" >> "/tmp/service_reports/health_history.log"
        return 0
    else
        echo "❌ $service_name: UNHEALTHY" > "$health_file"
        echo "$timestamp|$service_name|UNHEALTHY|$port" >> "/tmp/service_reports/health_history.log"
        return 1
    fi
}

# Function to generate service report
generate_service_report() {
    local service_name=$1
    local port=$2
    
    local report_file="/tmp/service_reports/${service_name}_report.txt"
    local log_file="/tmp/openpolicy_logs/${service_name}.log"
    local health_file="/tmp/health_checks/${service_name}.health"
    
    # Get health status
    local health_status="UNKNOWN"
    if [[ -f "$health_file" ]]; then
        health_status=$(cat "$health_file")
    fi
    
    # Get recent logs
    local recent_logs=""
    if [[ -f "$log_file" ]]; then
        recent_logs=$(tail -10 "$log_file" 2>/dev/null || echo "No logs available")
    fi
    
    # Get port status
    local port_status="FREE"
    if lsof -i:$port >/dev/null 2>&1; then
        port_status="IN_USE"
    fi
    
    # Generate report
    cat > "$report_file" << EOF
SERVICE AUTO-REPORT: $service_name
=====================================
Generated: $(date)
Port: $port
Port Status: $port_status
Health Status: $health_status

Recent Logs (last 10 lines):
$recent_logs

Port Usage:
$(lsof -i:$port 2>/dev/null || echo "Port is free")

Health Check History:
$(tail -5 "/tmp/service_reports/health_history.log" | grep "$service_name" || echo "No health history")
EOF

    echo "$(date)|$service_name|REPORT_GENERATED" >> "/tmp/service_reports/report_history.log"
}

# Function to compile master report
compile_master_report() {
    local master_report="/tmp/service_reports/MASTER_SERVICE_REPORT.txt"
    
    cat > "$master_report" << EOF
OPENPOLICY MASTER SERVICE REPORT
================================
Generated: $(date)
Total Services: ${#SERVICE_NAMES[@]}

SERVICE STATUS SUMMARY:
$(for i in "${!SERVICE_NAMES[@]}"; do
    service_name="${SERVICE_NAMES[$i]}"
    port="${SERVICE_PORTS[$i]}"
    health_file="/tmp/health_checks/${service_name}.health"
    if [[ -f "$health_file" ]]; then
        echo "$(cat "$health_file") - Port $port"
    else
        echo "❓ $service_name: UNKNOWN - Port $port"
    fi
done)

HEALTH CHECK HISTORY:
$(tail -20 "/tmp/service_reports/health_history.log" 2>/dev/null || echo "No health history")

REPORT GENERATION HISTORY:
$(tail -10 "/tmp/service_reports/report_history.log" 2>/dev/null || echo "No report history")

ALL SERVICE REPORTS:
$(ls -la /tmp/service_reports/*_report.txt 2>/dev/null || echo "No individual reports")

MONITORING COMMANDS:
- View all logs: tail -f /tmp/openpolicy_logs/*.log
- View health status: cat /tmp/health_checks/*.health
- View master report: cat /tmp/service_reports/MASTER_SERVICE_REPORT.txt
- View individual reports: cat /tmp/service_reports/*_report.txt
EOF

    echo "$(date)|MASTER_REPORT_COMPILED" >> "/tmp/service_reports/report_history.log"
}

# Function to monitor all services
monitor_all_services() {
    echo -e "${BLUE}🔍 AUTO-MONITORING ALL SERVICES...${NC}"
    
    for i in "${!SERVICE_NAMES[@]}"; do
        local service_name="${SERVICE_NAMES[$i]}"
        local port="${SERVICE_PORTS[$i]}"
        local endpoint="${SERVICE_ENDPOINTS[$i]}"
        
        echo -e "${YELLOW}Checking $service_name on port $port...${NC}"
        
        # Health check
        if check_service_health "$service_name" "$port" "$endpoint"; then
            echo -e "${GREEN}✅ $service_name is healthy${NC}"
        else
            echo -e "${RED}❌ $service_name is unhealthy${NC}"
        fi
        
        # Generate report
        generate_service_report "$service_name" "$port"
        echo -e "${BLUE}📊 Report generated for $service_name${NC}"
    done
    
    # Compile master report
    compile_master_report
    echo -e "${GREEN}📋 Master report compiled${NC}"
}

# Function to continuous monitoring
continuous_monitoring() {
    echo -e "${BLUE}🔄 STARTING CONTINUOUS AUTO-MONITORING...${NC}"
    echo "Press Ctrl+C to stop monitoring"
    echo ""
    
    while true; do
        monitor_all_services
        echo ""
        echo -e "${YELLOW}⏳ Waiting 30 seconds before next check...${NC}"
        echo "Last check: $(date)"
        echo ""
        sleep 30
    done
}

# Main execution
main() {
    echo -e "${BLUE}🚀 OPENPOLICY AUTO-MONITORING CHAIN${NC}"
    echo "=========================================="
    echo "This script will:"
    echo "1. ✅ Check all service health automatically"
    echo "2. 📊 Generate individual service reports"
    echo "3. 📋 Compile master service report"
    echo "4. 🔄 Run continuously every 30 seconds"
    echo "5. 📝 Log all health checks and reports"
    echo ""
    
    # Initial monitoring
    monitor_all_services
    
    echo ""
    echo -e "${GREEN}🎉 Initial monitoring complete!${NC}"
    echo "Reports available in: /tmp/service_reports/"
    echo "Health checks in: /tmp/health_checks/"
    echo "Logs in: /tmp/openpolicy_logs/"
    echo ""
    
    # Start continuous monitoring
    continuous_monitoring
}

# Run main function
main "$@"
