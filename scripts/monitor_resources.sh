#!/bin/bash

# 📊 OpenPolicy Platform - Resource Monitoring Script
# 
# This script provides real-time monitoring of:
# - Cluster resource usage (memory, CPU)
# - Service health status
# - Pod status and resource allocation
# - Performance metrics

set -e

# Configuration
NAMESPACE="openpolicy-platform"
REFRESH_INTERVAL=30  # Refresh every 30 seconds
LOG_FILE="deployment_monitoring.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [INFO] $1" >> "$LOG_FILE"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [SUCCESS] $1" >> "$LOG_FILE"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [WARNING] $1" >> "$LOG_FILE"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] $1" >> "$LOG_FILE"
}

log_phase() {
    echo -e "${PURPLE}[PHASE]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [PHASE] $1" >> "$LOG_FILE"
}

log_metric() {
    echo -e "${CYAN}[METRIC]${NC} $1"
    echo "$(date '+%Y-%m-%d %H:%M:%S') [METRIC] $1" >> "$LOG_FILE"
}

# Clear screen and show header
show_header() {
    clear
    echo "📊 OpenPolicy Platform - Resource Monitoring Dashboard"
    echo "====================================================="
    echo "Namespace: $NAMESPACE | Refresh: ${REFRESH_INTERVAL}s | Log: $LOG_FILE"
    echo "Press Ctrl+C to stop monitoring"
    echo ""
}

# Get cluster resource usage
get_cluster_resources() {
    local resource_info=$(kubectl describe nodes 2>/dev/null | grep -A 10 "Allocated resources" || echo "")
    
    if [ -n "$resource_info" ]; then
        local memory_line=$(echo "$resource_info" | grep "memory" | head -1)
        local cpu_line=$(echo "$resource_info" | grep "cpu" | head -1)
        
        local memory_usage=$(echo "$memory_line" | sed 's/.*(\([0-9]*\)%).*/\1/')
        local cpu_usage=$(echo "$cpu_line" | sed 's/.*(\([0-9]*\)%).*/\1/')
        
        echo "$memory_usage|$cpu_usage"
    else
        echo "0|0"
    fi
}

# Display cluster resource status
display_cluster_status() {
    local resource_data=$(get_cluster_resources)
    local memory_usage=$(echo "$resource_data" | cut -d'|' -f1)
    local cpu_usage=$(echo "$resource_data" | cut -d'|' -f2)
    
    echo "🏗️  CLUSTER RESOURCES"
    echo "─────────────────────"
    
    if [ "$memory_usage" != "0" ] && [ "$cpu_usage" != "0" ]; then
        # Memory status
        if [ "$memory_usage" -lt 50 ]; then
            echo -e "Memory: ${GREEN}${memory_usage}%${NC} (Healthy)"
        elif [ "$memory_usage" -lt 80 ]; then
            echo -e "Memory: ${YELLOW}${memory_usage}%${NC} (Warning)"
        else
            echo -e "Memory: ${RED}${memory_usage}%${NC} (Critical)"
        fi
        
        # CPU status
        if [ "$cpu_usage" -lt 50 ]; then
            echo -e "CPU:    ${GREEN}${cpu_usage}%${NC} (Healthy)"
        elif [ "$cpu_usage" -lt 80 ]; then
            echo -e "CPU:    ${YELLOW}${cpu_usage}%${NC} (Warning)"
        else
            echo -e "CPU:    ${RED}${cpu_usage}%${NC} (Critical)"
        fi
        
        log_metric "Cluster: Memory ${memory_usage}%, CPU ${cpu_usage}%"
    else
        echo "Memory: Unknown"
        echo "CPU:    Unknown"
        log_warning "Could not determine cluster resource usage"
    fi
    
    echo ""
}

# Get service status summary
get_service_summary() {
    local total_pods=$(kubectl get pods -n $NAMESPACE 2>/dev/null | grep -v "NAME" | wc -l)
    local running_pods=$(kubectl get pods -n $NAMESPACE 2>/dev/null | grep -v "NAME" | grep "Running" | wc -l)
    local pending_pods=$(kubectl get pods -n $NAMESPACE 2>/dev/null | grep -v "NAME" | grep "Pending" | wc -l)
    local failed_pods=$(kubectl get pods -n $NAMESPACE 2>/dev/null | grep -v "NAME" | grep -E "(Failed|CrashLoopBackOff|Error)" | wc -l)
    
    echo "$total_pods|$running_pods|$pending_pods|$failed_pods"
}

# Display service status
display_service_status() {
    local service_data=$(get_service_summary)
    local total_pods=$(echo "$service_data" | cut -d'|' -f1)
    local running_pods=$(echo "$service_data" | cut -d'|' -f2)
    local pending_pods=$(echo "$service_data" | cut -d'|' -f3)
    local failed_pods=$(echo "$service_data" | cut -d'|' -f4)
    
    echo "🔧 SERVICE STATUS"
    echo "─────────────────"
    
    if [ "$total_pods" -gt 0 ]; then
        echo "Total Pods:  $total_pods"
        
        if [ "$running_pods" -gt 0 ]; then
            echo -e "Running:     ${GREEN}$running_pods${NC}"
        else
            echo -e "Running:     ${RED}$running_pods${NC}"
        fi
        
        if [ "$pending_pods" -gt 0 ]; then
            echo -e "Pending:     ${YELLOW}$pending_pods${NC}"
        else
            echo -e "Pending:     ${GREEN}$pending_pods${NC}"
        fi
        
        if [ "$failed_pods" -gt 0 ]; then
            echo -e "Failed:      ${RED}$failed_pods${NC}"
        else
            echo -e "Failed:      ${GREEN}$failed_pods${NC}"
        fi
        
        # Calculate success rate
        local success_rate=0
        if [ "$total_pods" -gt 0 ]; then
            success_rate=$(( (running_pods * 100) / total_pods ))
        fi
        
        if [ "$success_rate" -ge 80 ]; then
            echo -e "Success Rate: ${GREEN}${success_rate}%${NC}"
        elif [ "$success_rate" -ge 60 ]; then
            echo -e "Success Rate: ${YELLOW}${success_rate}%${NC}"
        else
            echo -e "Success Rate: ${RED}${success_rate}%${NC}"
        fi
        
        log_metric "Services: $running_pods/$total_pods running (${success_rate}%)"
    else
        echo "No pods found in namespace"
        log_warning "No services detected in namespace"
    fi
    
    echo ""
}

# Get resource usage by service tier
get_tier_resources() {
    echo "📊 RESOURCE USAGE BY TIER"
    echo "─────────────────────────"
    
    # Infrastructure tier
    local infra_pods=$(kubectl get pods -n $NAMESPACE -l tier=infrastructure 2>/dev/null | grep -v "NAME" | wc -l)
    local infra_memory=$(kubectl get pods -n $NAMESPACE -l tier=infrastructure -o custom-columns="MEMORY:.spec.containers[0].resources.requests.memory" 2>/dev/null | grep -v "MEMORY" | grep -v "<none>" | sed 's/Mi//' | awk '{sum+=$1} END {print sum+0}')
    
    echo "Infrastructure: $infra_pods pods, ${infra_memory}Mi memory"
    
    # Business tier
    local business_pods=$(kubectl get pods -n $NAMESPACE -l tier=business 2>/dev/null | grep -v "NAME" | wc -l)
    local business_memory=$(kubectl get pods -n $NAMESPACE -l tier=business -o custom-columns="MEMORY:.spec.containers[0].resources.requests.memory" 2>/dev/null | grep -v "MEMORY" | grep -v "<none>" | sed 's/Mi//' | awk '{sum+=$1} END {print sum+0}')
    
    echo "Business:       $business_pods pods, ${business_memory}Mi memory"
    
    # Operational tier
    local operational_pods=$(kubectl get pods -n $NAMESPACE -l tier=operational 2>/dev/null | grep -v "NAME" | wc -l)
    local operational_memory=$(kubectl get pods -n $NAMESPACE -l tier=operational -o custom-columns="MEMORY:.spec.containers[0].resources.requests.memory" 2>/dev/null | grep -v "MEMORY" | grep -v "<none>" | sed 's/Mi//' | awk '{sum+=$1} END {print sum+0}')
    
    echo "Operational:    $operational_pods pods, ${operational_memory}Mi memory"
    
    # UI tier
    local ui_pods=$(kubectl get pods -n $NAMESPACE -l tier=ui 2>/dev/null | grep -v "NAME" | wc -l)
    local ui_memory=$(kubectl get pods -n $NAMESPACE -l tier=ui -o custom-columns="MEMORY:.spec.containers[0].resources.requests.memory" 2>/dev/null | grep -v "MEMORY" | grep -v "<none>" | sed 's/Mi//' | awk '{sum+=$1} END {print sum+0}')
    
    echo "UI:             $ui_pods pods, ${ui_memory}Mi memory"
    
    echo ""
}

# Display deployment phases status
display_phase_status() {
    echo "🎯 DEPLOYMENT PHASES"
    echo "────────────────────"
    
    # Phase 1: Infrastructure (4 services)
    local phase1_ready=$(kubectl get pods -n $NAMESPACE -l tier=infrastructure 2>/dev/null | grep "Running" | wc -l)
    local phase1_total=4
    
    if [ "$phase1_ready" -eq "$phase1_total" ]; then
        echo -e "Phase 1 (Infrastructure): ${GREEN}✅ Complete${NC} ($phase1_ready/$phase1_total)"
    else
        echo -e "Phase 1 (Infrastructure): ${YELLOW}🔄 In Progress${NC} ($phase1_ready/$phase1_total)"
    fi
    
    # Phase 2: Core Business (9 services)
    local phase2_ready=$(kubectl get pods -n $NAMESPACE -l tier=business 2>/dev/null | grep "Running" | wc -l)
    local phase2_total=9
    
    if [ "$phase2_ready" -eq "$phase2_total" ]; then
        echo -e "Phase 2 (Business):       ${GREEN}✅ Complete${NC} ($phase2_ready/$phase2_total)"
    elif [ "$phase1_ready" -eq "$phase1_total" ]; then
        echo -e "Phase 2 (Business):       ${YELLOW}🔄 Ready to Deploy${NC} ($phase2_ready/$phase2_total)"
    else
        echo -e "Phase 2 (Business):       ${BLUE}⏳ Waiting${NC} ($phase2_ready/$phase2_total)"
    fi
    
    # Phase 3: Operational (6 services)
    local phase3_ready=$(kubectl get pods -n $NAMESPACE -l tier=operational 2>/dev/null | grep "Running" | wc -l)
    local phase3_total=6
    
    if [ "$phase3_ready" -eq "$phase3_total" ]; then
        echo -e "Phase 3 (Operational):    ${GREEN}✅ Complete${NC} ($phase3_ready/$phase3_total)"
    elif [ "$phase2_ready" -eq "$phase2_total" ]; then
        echo -e "Phase 3 (Operational):    ${YELLOW}🔄 Ready to Deploy${NC} ($phase3_ready/$phase3_total)"
    else
        echo -e "Phase 3 (Operational):    ${BLUE}⏳ Waiting${NC} ($phase3_ready/$phase3_total)"
    fi
    
    # Phase 4: UI (3 services)
    local phase4_ready=$(kubectl get pods -n $NAMESPACE -l tier=ui 2>/dev/null | grep "Running" | wc -l)
    local phase4_total=3
    
    if [ "$phase4_ready" -eq "$phase4_total" ]; then
        echo -e "Phase 4 (UI):             ${GREEN}✅ Complete${NC} ($phase4_ready/$phase4_total)"
    elif [ "$phase3_ready" -eq "$phase3_total" ]; then
        echo -e "Phase 4 (UI):             ${YELLOW}🔄 Ready to Deploy${NC} ($phase4_ready/$phase4_total)"
    else
        echo -e "Phase 4 (UI):             ${BLUE}⏳ Waiting${NC} ($phase4_ready/$phase4_total)"
    fi
    
    echo ""
}

# Display recent events
display_recent_events() {
    echo "📝 RECENT EVENTS"
    echo "────────────────"
    
    local events=$(kubectl get events -n $NAMESPACE --sort-by='.lastTimestamp' 2>/dev/null | tail -5)
    
    if [ -n "$events" ]; then
        echo "$events"
    else
        echo "No recent events found"
    fi
    
    echo ""
}

# Display performance metrics
display_performance_metrics() {
    echo "⚡ PERFORMANCE METRICS"
    echo "──────────────────────"
    
    # Get average response time (if services are running)
    local running_services=$(kubectl get pods -n $NAMESPACE -l tier=infrastructure 2>/dev/null | grep "Running" | wc -l)
    
    if [ "$running_services" -gt 0 ]; then
        echo "Infrastructure Services: $running_services running"
        
        # Check scraper service health if running
        local scraper_pod=$(kubectl get pods -n $NAMESPACE -l app=scraper-service 2>/dev/null | grep "Running" | head -1 | awk '{print $1}')
        
        if [ -n "$scraper_pod" ]; then
            echo "Scraper Service: ✅ Running"
            
            # Check if health endpoint is accessible
            if kubectl exec -n $NAMESPACE $scraper_pod -- curl -f -s http://localhost:9016/healthz > /dev/null 2>&1; then
                echo "Health Check: ✅ Passing"
            else
                echo "Health Check: ❌ Failing"
            fi
        else
            echo "Scraper Service: ❌ Not Running"
        fi
    else
        echo "No infrastructure services running"
    fi
    
    echo ""
}

# Main monitoring loop
monitor_loop() {
    while true; do
        show_header
        
        # Display current timestamp
        echo "🕐 Last Updated: $(date '+%Y-%m-%d %H:%M:%S')"
        echo ""
        
        # Display all monitoring sections
        display_cluster_status
        display_service_status
        get_tier_resources
        display_phase_status
        display_performance_metrics
        display_recent_events
        
        # Footer
        echo "─────────────────────────────────────────────────────────────────"
        echo "Press Ctrl+C to stop monitoring | Log file: $LOG_FILE"
        
        # Wait for next refresh
        sleep $REFRESH_INTERVAL
    done
}

# Main execution
main() {
    echo "📊 OpenPolicy Platform - Resource Monitoring"
    echo "============================================"
    echo ""
    
    # Check if kubectl is available
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check if namespace exists
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        log_error "Namespace '$NAMESPACE' does not exist"
        exit 1
    fi
    
    # Initialize log file
    echo "OpenPolicy Platform Deployment Monitoring Log" > "$LOG_FILE"
    echo "Started: $(date)" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    log_info "Starting resource monitoring for namespace: $NAMESPACE"
    
    # Start monitoring loop
    monitor_loop
}

# Handle Ctrl+C gracefully
trap 'echo ""; log_info "Monitoring stopped by user"; exit 0' INT

# Run main function
main "$@"
