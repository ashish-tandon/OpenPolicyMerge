#!/bin/bash

# Monitoring Service Individual Startup Script
# This script handles cleanup, rebuild, and startup for the monitoring service

set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SERVICE_NAME="monitoring-service"
SERVICE_PORT="9010"
SERVICE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}🚀 $SERVICE_NAME Startup Script${NC}"
echo "====================================="

# Function to cleanup service
cleanup_service() {
    echo -e "${YELLOW}🧹 Cleaning up $SERVICE_NAME...${NC}"
    
    # Kill existing processes
    pkill -f "uvicorn.*$SERVICE_PORT" 2>/dev/null || true
    lsof -ti:$SERVICE_PORT | xargs kill -9 2>/dev/null || true
    
    # Clean Python cache
    find "$SERVICE_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find "$SERVICE_DIR" -name "*.pyc" -delete 2>/dev/null || true
    
    # Clean temporary files
    rm -rf "$SERVICE_DIR/.pytest_cache" 2>/dev/null || true
    rm -rf "$SERVICE_DIR/.coverage" 2>/dev/null || true
    
    echo -e "${GREEN}✅ Cleanup completed${NC}"
}

# Function to rebuild service
rebuild_service() {
    echo -e "${YELLOW}🔨 Rebuilding $SERVICE_NAME...${NC}"
    
    cd "$SERVICE_DIR"
    
    # Install/update dependencies
    if [[ -f "requirements.txt" ]]; then
        echo "Installing Python dependencies..."
        pip install -r requirements.txt
    fi
    
    # Install monitoring-specific dependencies
    echo "Installing monitoring-specific dependencies..."
    pip install prometheus-client psutil
    
    # Run any build steps
    if [[ -f "build.sh" ]]; then
        echo "Running build script..."
        chmod +x build.sh
        ./build.sh
    fi
    
    # Run tests if available
    if [[ -d "tests" ]]; then
        echo "Running tests..."
        python -m pytest tests/ -v --tb=short || echo "Tests completed with some failures"
    fi
    
    cd - > /dev/null
    
    echo -e "${GREEN}✅ Rebuild completed${NC}"
}

# Function to start service
start_service() {
    echo -e "${YELLOW}🚀 Starting $SERVICE_NAME on port $SERVICE_PORT...${NC}"
    
    cd "$SERVICE_DIR"
    
    # Check if service is already running
    if lsof -i:$SERVICE_PORT >/dev/null 2>&1; then
        echo -e "${RED}❌ Port $SERVICE_PORT is already in use${NC}"
        return 1
    fi
    
    # Start service with logging
    python -m uvicorn src.api:app --host 0.0.0.0 --port $SERVICE_PORT --reload > "/tmp/openpolicy_logs/${SERVICE_NAME}.log" 2>&1 &
    local pid=$!
    
    # Save PID for central monitoring
    echo $pid > "/tmp/service_reports/${SERVICE_NAME}.pid"
    
    cd - > /dev/null
    
    # Wait for service to start
    echo -e "${YELLOW}⏳ Waiting for service to start...${NC}"
    sleep 5
    
    # Test health endpoint
    if curl -s "http://localhost:$SERVICE_PORT/healthz" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $SERVICE_NAME started successfully (PID: $pid)${NC}"
        echo -e "${GREEN}✅ Health check passed${NC}"
        return 0
    else
        echo -e "${RED}❌ $SERVICE_NAME failed to start properly${NC}"
        return 1
    fi
}

# Function to stop service
stop_service() {
    echo -e "${YELLOW}🛑 Stopping $SERVICE_NAME...${NC}"
    
    # Kill by PID if available
    if [[ -f "/tmp/service_reports/${SERVICE_NAME}.pid" ]]; then
        local pid=$(cat "/tmp/service_reports/${SERVICE_NAME}.pid")
        kill $pid 2>/dev/null || true
        rm -f "/tmp/service_reports/${SERVICE_NAME}.pid"
    fi
    
    # Kill by port
    lsof -ti:$SERVICE_PORT | xargs kill -9 2>/dev/null || true
    
    echo -e "${GREEN}✅ Service stopped${NC}"
}

# Function to restart service
restart_service() {
    echo -e "${YELLOW}🔄 Restarting $SERVICE_NAME...${NC}"
    stop_service
    sleep 2
    start_service
}

# Function to show service status
show_status() {
    echo -e "${BLUE}📊 $SERVICE_NAME Status${NC}"
    echo "========================"
    
    # Check if running
    if [[ -f "/tmp/service_reports/${SERVICE_NAME}.pid" ]]; then
        local pid=$(cat "/tmp/service_reports/${SERVICE_NAME}.pid")
        if kill -0 $pid 2>/dev/null; then
            echo -e "${GREEN}✅ Status: RUNNING (PID: $pid)${NC}"
        else
            echo -e "${RED}❌ Status: STOPPED${NC}"
        fi
    else
        echo -e "${RED}❌ Status: NOT STARTED${NC}"
    fi
    
    # Check port
    if lsof -i:$SERVICE_PORT >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Port $SERVICE_PORT: IN USE${NC}"
    else
        echo -e "${RED}❌ Port $SERVICE_PORT: FREE${NC}"
    fi
    
    # Check health
    if curl -s "http://localhost:$SERVICE_PORT/healthz" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Health Check: PASSED${NC}"
    else
        echo -e "${RED}❌ Health Check: FAILED${NC}"
    fi
    
    # Show recent logs
    echo ""
    echo -e "${BLUE}Recent Logs:${NC}"
    if [[ -f "/tmp/openpolicy_logs/${SERVICE_NAME}.log" ]]; then
        tail -5 "/tmp/openpolicy_logs/${SERVICE_NAME}.log"
    else
        echo "No logs available"
    fi
}

# Main execution
main() {
    case "${1:-start}" in
        "start")
            cleanup_service
            rebuild_service
            start_service
            ;;
        "stop")
            stop_service
            ;;
        "restart")
            restart_service
            ;;
        "cleanup")
            cleanup_service
            ;;
        "rebuild")
            rebuild_service
            ;;
        "status")
            show_status
            ;;
        "redeploy")
            echo -e "${BLUE}🔄 Redeploying $SERVICE_NAME...${NC}"
            cleanup_service
            rebuild_service
            start_service
            ;;
        *)
            echo "Usage: $0 {start|stop|restart|cleanup|rebuild|status|redeploy}"
            echo "  start     - Clean, rebuild, and start service"
            echo "  stop      - Stop service"
            echo "  restart   - Restart service"
            echo "  cleanup   - Clean up service files"
            echo "  rebuild   - Rebuild service dependencies"
            echo "  status    - Show service status"
            echo "  redeploy  - Full redeploy (cleanup + rebuild + start)"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
