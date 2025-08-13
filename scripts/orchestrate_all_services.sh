#!/bin/bash

# OpenPolicy Central Service Orchestrator
# This script calls each individual service startup script

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🎼 OPENPOLICY CENTRAL SERVICE ORCHESTRATOR${NC}"
echo "================================================"
echo "This script orchestrates all individual service startup scripts"
echo ""

# Create monitoring directories
mkdir -p /tmp/openpolicy_logs
mkdir -p /tmp/service_reports
mkdir -p /tmp/health_checks

# Service definitions with their startup scripts
declare -a SERVICES=(
    "policy-service:9001:start.sh"
    "search-service:9002:start.sh"
    "auth-service:9003:start.sh"
    "notification-service:9004:start.sh"
    "config-service:9005:start.sh"
    "health-service:9006:start.sh"
    "etl:9007:start.sh"
    "scraper-service:9008:start.sh"
    "api-gateway:9009:start.sh"
    "monitoring-service:9010:start.sh"
    "plotly-service:9011:start.sh"
    "mcp-service:9012:start.sh"
    "op-import:9013:start.sh"
    "web:3000:start.sh"
    "admin:3001:start.sh"
    "mobile-api:8081:start.sh"
    "legacy-django:8000:start.sh"
)

# Function to start auto-monitoring
start_auto_monitoring() {
    echo -e "${BLUE}🔍 Starting auto-monitoring system...${NC}"
    
    # Start the auto-monitoring script
    ./scripts/auto_monitor_services.sh > /tmp/openpolicy_logs/auto_monitor.log 2>&1 &
    local monitor_pid=$!
    echo $monitor_pid > "/tmp/service_reports/auto_monitor.pid"
    
    echo -e "${GREEN}✅ Auto-monitoring started (PID: $monitor_pid)${NC}"
}

# Function to start a single service
start_service() {
    local service_info=$1
    local action=${2:-start}
    
    IFS=':' read -r service_name port script_name <<< "$service_info"
    
    echo -e "${BLUE}🚀 Starting $service_name...${NC}"
    
    # Check if startup script exists
    local script_path="services/$service_name/$script_name"
    if [[ ! -f "$script_path" ]]; then
        echo -e "${RED}❌ Startup script not found: $script_path${NC}"
        echo -e "${YELLOW}⚠️  Creating default startup script for $service_name...${NC}"
        create_default_startup_script "$service_name" "$port"
    fi
    
    # Make script executable
    chmod +x "$script_path"
    
    # Run the startup script
    if "$script_path" "$action"; then
        echo -e "${GREEN}✅ $service_name started successfully${NC}"
        return 0
    else
        echo -e "${RED}❌ $service_name failed to start${NC}"
        return 1
    fi
}

# Function to create default startup script for missing services
create_default_startup_script() {
    local service_name=$1
    local port=$2
    local script_path="services/$service_name/start.sh"
    
    # Determine service type and create appropriate startup script
    case $service_name in
        *"-service"|"etl"|"monitoring-service"|"plotly-service"|"mcp-service"|"op-import")
            create_python_startup_script "$service_name" "$port" "$script_path"
            ;;
        "api-gateway")
            create_go_startup_script "$service_name" "$port" "$script_path"
            ;;
        "web"|"admin")
            create_node_startup_script "$service_name" "$port" "$script_path"
            ;;
        "mobile-api")
            create_expo_startup_script "$service_name" "$port" "$script_path"
            ;;
        "legacy-django")
            create_django_startup_script "$service_name" "$port" "$script_path"
            ;;
        *)
            create_python_startup_script "$service_name" "$port" "$script_path"
            ;;
    esac
    
    echo -e "${GREEN}✅ Default startup script created for $service_name${NC}"
}

# Function to create Python service startup script
create_python_startup_script() {
    local service_name=$1
    local port=$2
    local script_path=$3
    
    cat > "$script_path" << 'EOF'
#!/bin/bash

# Auto-generated Python Service Startup Script
set -e

SERVICE_NAME="SERVICE_NAME_PLACEHOLDER"
SERVICE_PORT="PORT_PLACEHOLDER"
SERVICE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to cleanup service
cleanup_service() {
    pkill -f "uvicorn.*$SERVICE_PORT" 2>/dev/null || true
    lsof -ti:$SERVICE_PORT | xargs kill -9 2>/dev/null || true
    find "$SERVICE_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$SERVICE_DIR" -name "*.pyc" -delete 2>/dev/null || true
}

# Function to start service
start_service() {
    cd "$SERVICE_DIR"
    
    # Determine entry point
    local entry_point="src.api:app"
    if [[ -f "src/main.py" ]]; then
        entry_point="src.main:app"
    fi
    
    python -m uvicorn $entry_point --host 0.0.0.0 --port $SERVICE_PORT --reload > "/tmp/openpolicy_logs/${SERVICE_NAME}.log" 2>&1 &
    local pid=$!
    echo $pid > "/tmp/service_reports/${SERVICE_NAME}.pid"
    
    cd - > /dev/null
    sleep 5
    
    # Test health endpoint
    if curl -s "http://localhost:$SERVICE_PORT/healthz" > /dev/null 2>&1; then
        echo "✅ $SERVICE_NAME started successfully (PID: $pid)"
        return 0
    else
        echo "❌ $SERVICE_NAME failed to start properly"
        return 1
    fi
}

# Main execution
case "${1:-start}" in
    "start")
        cleanup_service
        start_service
        ;;
    *)
        start_service
        ;;
esac
EOF
    
    # Replace placeholders
    sed -i '' "s/SERVICE_NAME_PLACEHOLDER/$service_name/g" "$script_path"
    sed -i '' "s/PORT_PLACEHOLDER/$port/g" "$script_path"
}

# Function to create Go service startup script
create_go_startup_script() {
    local service_name=$1
    local port=$2
    local script_path=$3
    
    cat > "$script_path" << 'EOF'
#!/bin/bash

# Auto-generated Go Service Startup Script
set -e

SERVICE_NAME="SERVICE_NAME_PLACEHOLDER"
SERVICE_PORT="PORT_PLACEHOLDER"
SERVICE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to cleanup service
cleanup_service() {
    lsof -ti:$SERVICE_PORT | xargs kill -9 2>/dev/null || true
    pkill -f "go run.*$SERVICE_NAME" 2>/dev/null || true
}

# Function to start service
start_service() {
    cd "$SERVICE_DIR"
    
    go run src/main.go > "/tmp/openpolicy_logs/${SERVICE_NAME}.log" 2>&1 &
    local pid=$!
    echo $pid > "/tmp/service_reports/${SERVICE_NAME}.pid"
    
    cd - > /dev/null
    sleep 5
    
    # Test health endpoint
    if curl -s "http://localhost:$SERVICE_PORT/health" > /dev/null 2>&1; then
        echo "✅ $SERVICE_NAME started successfully (PID: $pid)"
        return 0
    else
        echo "❌ $SERVICE_NAME failed to start properly"
        return 1
    fi
}

# Main execution
case "${1:-start}" in
    "start")
        cleanup_service
        start_service
        ;;
    *)
        start_service
        ;;
esac
EOF
    
    # Replace placeholders
    sed -i '' "s/SERVICE_NAME_PLACEHOLDER/$service_name/g" "$script_path"
    sed -i '' "s/PORT_PLACEHOLDER/$port/g" "$script_path"
}

# Function to create Node.js service startup script
create_node_startup_script() {
    local service_name=$1
    local port=$2
    local script_path=$3
    
    cat > "$script_path" << 'EOF'
#!/bin/bash

# Auto-generated Node.js Service Startup Script
set -e

SERVICE_NAME="SERVICE_NAME_PLACEHOLDER"
SERVICE_PORT="PORT_PLACEHOLDER"
SERVICE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to cleanup service
cleanup_service() {
    lsof -ti:$SERVICE_PORT | xargs kill -9 2>/dev/null || true
    pkill -f "npm.*$SERVICE_NAME" 2>/dev/null || true
}

# Function to start service
start_service() {
    cd "$SERVICE_DIR"
    
    npm run dev > "/tmp/openpolicy_logs/${SERVICE_NAME}.log" 2>&1 &
    local pid=$!
    echo $pid > "/tmp/service_reports/${SERVICE_NAME}.pid"
    
    cd - > /dev/null
    sleep 10
    
    # Test endpoint
    if curl -s "http://localhost:$SERVICE_PORT/" > /dev/null 2>&1; then
        echo "✅ $SERVICE_NAME started successfully (PID: $pid)"
        return 0
    else
        echo "❌ $SERVICE_NAME failed to start properly"
        return 1
    fi
}

# Main execution
case "${1:-start}" in
    "start")
        cleanup_service
        start_service
        ;;
    *)
        start_service
        ;;
esac
EOF
    
    # Replace placeholders
    sed -i '' "s/SERVICE_NAME_PLACEHOLDER/$service_name/g" "$script_path"
    sed -i '' "s/PORT_PLACEHOLDER/$port/g" "$script_path"
}

# Function to create Expo service startup script
create_expo_startup_script() {
    local service_name=$1
    local port=$2
    local script_path=$3
    
    cat > "$script_path" << 'EOF'
#!/bin/bash

# Auto-generated Expo Service Startup Script
set -e

SERVICE_NAME="SERVICE_NAME_PLACEHOLDER"
SERVICE_PORT="PORT_PLACEHOLDER"
SERVICE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to cleanup service
cleanup_service() {
    lsof -ti:$SERVICE_PORT | xargs kill -9 2>/dev/null || true
    pkill -f "expo.*$SERVICE_NAME" 2>/dev/null || true
}

# Function to start service
start_service() {
    cd "$SERVICE_DIR"
    
    npx expo start --web --port $SERVICE_PORT > "/tmp/openpolicy_logs/${SERVICE_NAME}.log" 2>&1 &
    local pid=$!
    echo $pid > "/tmp/service_reports/${SERVICE_NAME}.pid"
    
    cd - > /dev/null
    sleep 15
    
    # Test endpoint
    if curl -s "http://localhost:$SERVICE_PORT/" > /dev/null 2>&1; then
        echo "✅ $SERVICE_NAME started successfully (PID: $pid)"
        return 0
    else
        echo "❌ $SERVICE_NAME failed to start properly"
        return 1
    fi
}

# Main execution
case "${1:-start}" in
    "start")
        cleanup_service
        start_service
        ;;
    *)
        start_service
        ;;
esac
EOF
    
    # Replace placeholders
    sed -i '' "s/SERVICE_NAME_PLACEHOLDER/$service_name/g" "$script_path"
    sed -i '' "s/PORT_PLACEHOLDER/$port/g" "$script_path"
}

# Function to create Django service startup script
create_django_startup_script() {
    local service_name=$1
    local port=$2
    local script_path=$3
    
    cat > "$script_path" << 'EOF'
#!/bin/bash

# Auto-generated Django Service Startup Script
set -e

SERVICE_NAME="SERVICE_NAME_PLACEHOLDER"
SERVICE_PORT="PORT_PLACEHOLDER"
SERVICE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Function to cleanup service
cleanup_service() {
    lsof -ti:$SERVICE_PORT | xargs kill -9 2>/dev/null || true
    pkill -f "python.*manage.py" 2>/dev/null || true
}

# Function to start service
start_service() {
    cd "$SERVICE_DIR"
    
    python manage.py runserver 0.0.0.0:$SERVICE_PORT > "/tmp/openpolicy_logs/${SERVICE_NAME}.log" 2>&1 &
    local pid=$!
    echo $pid > "/tmp/service_reports/${SERVICE_NAME}.pid"
    
    cd - > /dev/null
    sleep 10
    
    # Test endpoint
    if curl -s "http://localhost:$SERVICE_PORT/" > /dev/null 2>&1; then
        echo "✅ $SERVICE_NAME started successfully (PID: $pid)"
        return 0
    else
        echo "❌ $SERVICE_NAME failed to start properly"
        return 1
    fi
}

# Main execution
case "${1:-start}" in
    "start")
        cleanup_service
        start_service
        ;;
    *)
        start_service
        ;;
esac
EOF
    
    # Replace placeholders
    sed -i '' "s/SERVICE_NAME_PLACEHOLDER/$service_name/g" "$script_path"
    sed -i '' "s/PORT_PLACEHOLDER/$port/g" "$script_path"
}

# Function to start all services in parallel
start_all_services_parallel() {
    echo -e "${BLUE}🚀 STARTING ALL SERVICES IN PARALLEL...${NC}"
    echo ""
    
    local failed_services=()
    
    for service_info in "${SERVICES[@]}"; do
        # Start service in background
        start_service "$service_info" &
        
        # Small delay between starts
        sleep 1
    done
    
    # Wait for all background processes
    wait
    
    echo ""
    echo -e "${GREEN}✅ All services startup initiated${NC}"
}

# Function to show overall status
show_overall_status() {
    echo ""
    echo -e "${BLUE}📊 OVERALL SERVICE STATUS${NC}"
    echo "================================"
    
    local running=0
    local stopped=0
    
    for service_info in "${SERVICES[@]}"; do
        IFS=':' read -r service_name port script_name <<< "$service_info"
        
        if [[ -f "/tmp/service_reports/${service_name}.pid" ]]; then
            local pid=$(cat "/tmp/service_reports/${service_name}.pid")
            if kill -0 $pid 2>/dev/null; then
                echo -e "${GREEN}✅ $service_name: RUNNING (PID: $pid)${NC}"
                ((running++))
            else
                echo -e "${RED}❌ $service_name: STOPPED${NC}"
                ((stopped++))
            fi
        else
            echo -e "${RED}❌ $service_name: NOT STARTED${NC}"
            ((stopped++))
        fi
    done
    
    echo ""
    echo -e "${BLUE}Summary:${NC}"
    echo -e "${GREEN}Running: $running${NC}"
    echo -e "${RED}Stopped/Not Started: $stopped${NC}"
    echo -e "${BLUE}Total: ${#SERVICES[@]}${NC}"
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
    echo ""
    echo -e "${GREEN}🔍 Monitoring Commands:${NC}"
    echo "  - View all logs: tail -f /tmp/openpolicy_logs/*.log"
    echo "  - View health status: cat /tmp/health_checks/*.health"
    echo "  - View master report: cat /tmp/service_reports/MASTER_SERVICE_REPORT.txt"
    echo "  - View individual reports: cat /tmp/service_reports/*_report.txt"
    echo ""
    echo -e "${GREEN}🌐 Service URLs:${NC}"
    for service_info in "${SERVICES[@]}"; do
        IFS=':' read -r service_name port script_name <<< "$service_info"
        echo "  - $service_name: http://localhost:$port"
    done
}

# Main execution
main() {
    case "${1:-start}" in
        "start")
            echo -e "${BLUE}🚀 Starting all services with orchestration...${NC}"
            start_all_services_parallel
            
            echo -e "${YELLOW}⏳ Waiting for services to start...${NC}"
            sleep 30
            
            start_auto_monitoring
            
            echo -e "${YELLOW}⏳ Waiting for auto-monitoring to initialize...${NC}"
            sleep 15
            
            show_overall_status
            show_monitoring_info
            
            echo ""
            echo -e "${GREEN}🎉 Orchestration complete! All services should be running.${NC}"
            ;;
        "status")
            show_overall_status
            ;;
        "monitoring")
            show_monitoring_info
            ;;
        "redeploy")
            echo -e "${BLUE}🔄 Redeploying all services...${NC}"
            # This would call each service's redeploy function
            echo "Redeploy functionality to be implemented"
            ;;
        *)
            echo "Usage: $0 {start|status|monitoring|redeploy}"
            echo "  start      - Start all services with orchestration"
            echo "  status     - Show overall service status"
            echo "  monitoring - Show monitoring information"
            echo "  redeploy   - Redeploy all services"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
