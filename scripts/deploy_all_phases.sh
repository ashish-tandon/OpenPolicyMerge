#!/bin/bash

# 🚀 OpenPolicy Platform - Master Deployment Script
# 
# This script orchestrates the complete deployment of all 26 services
# across 5 phases with proper validation and monitoring.

set -e

# Configuration
NAMESPACE="openpolicy-platform"
LOG_FILE="complete_deployment.log"
PHASE_SCRIPTS_DIR="scripts"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
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

# Check prerequisites
check_prerequisites() {
    log_info "Checking deployment prerequisites..."
    
    # Check kubectl
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    # Check cluster connection
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    # Check namespace
    if ! kubectl get namespace $NAMESPACE &> /dev/null; then
        log_error "Namespace '$NAMESPACE' does not exist"
        exit 1
    fi
    
    # Check if cluster is clean (no running pods)
    local running_pods=$(kubectl get pods -n $NAMESPACE 2>/dev/null | grep -v "NAME" | wc -l)
    if [ "$running_pods" -gt 0 ]; then
        log_warning "Found $running_pods existing pods in namespace"
        log_info "This deployment will replace existing services"
    else
        log_success "Cluster is clean and ready for deployment"
    fi
    
    # Check cluster resources
    local total_memory=$(kubectl describe nodes 2>/dev/null | grep -A 5 "Allocated resources" | grep "memory" | head -1 | awk '{print $2}' | sed 's/Mi//')
    if [ -n "$total_memory" ] && [ "$total_memory" -lt 8000 ]; then
        log_warning "Cluster has limited memory: ${total_memory}Mi (recommended: 8Gi+)"
    fi
    
    log_success "Prerequisites check completed"
}

# Initialize deployment
initialize_deployment() {
    log_info "Initializing OpenPolicy Platform deployment..."
    
    # Create log file
    echo "OpenPolicy Platform Complete Deployment Log" > "$LOG_FILE"
    echo "Started: $(date)" >> "$LOG_FILE"
    echo "Namespace: $NAMESPACE" >> "$LOG_FILE"
    echo "" >> "$LOG_FILE"
    
    # Display deployment plan
    echo "🚀 OpenPolicy Platform - Complete Deployment Plan"
    echo "================================================="
    echo ""
    echo "Phase 1: Infrastructure Foundation (4 services)"
    echo "  - postgresql (1Gi memory, 500m CPU)"
    echo "  - scraper-service (1Gi memory, 500m CPU)"
    echo "  - redis (512Mi memory, 200m CPU)"
    echo "  - rabbitmq (512Mi memory, 250m CPU)"
    echo ""
    echo "Phase 2: Core Business Services (9 services)"
    echo "  - Batch 2.1: Data Services (3 services)"
    echo "  - Batch 2.2: Business Logic (3 services)"
    echo "  - Batch 2.3: Security Services (3 services)"
    echo ""
    echo "Phase 3: Operational Services (6 services)"
    echo "  - Batch 3.1: Monitoring Services (3 services)"
    echo "  - Batch 3.2: Intelligence Services (3 services)"
    echo ""
    echo "Phase 4: User Interface Services (3 services)"
    echo "  - api-gateway, notification-service, mcp-service"
    echo ""
    echo "Phase 5: Utility Services (4 services)"
    echo "  - cache-service, web, admin, mobile-api"
    echo ""
    echo "Total: 26 services across 5 phases"
    echo "Expected Duration: 60-90 minutes"
    echo "Target Resource Usage: <80% memory"
    echo ""
    
    # Confirm deployment
    read -p "Do you want to proceed with the deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        log_info "Deployment cancelled by user"
        exit 0
    fi
    
    log_success "Deployment initialization completed"
}

# Execute Phase 1: Infrastructure Foundation
execute_phase1() {
    log_phase "Starting Phase 1: Infrastructure Foundation"
    
    if [ -f "$PHASE_SCRIPTS_DIR/deploy_phase1.sh" ]; then
        log_info "Executing Phase 1 deployment script..."
        if "$PHASE_SCRIPTS_DIR/deploy_phase1.sh"; then
            log_success "Phase 1 completed successfully"
            return 0
        else
            log_error "Phase 1 deployment failed"
            return 1
        fi
    else
        log_error "Phase 1 deployment script not found: $PHASE_SCRIPTS_DIR/deploy_phase1.sh"
        return 1
    fi
}

# Execute Phase 2: Core Business Services
execute_phase2() {
    log_phase "Starting Phase 2: Core Business Services"
    
    log_info "Deploying Batch 2.1: Data Services..."
    kubectl apply -f deploy/k8s/dev/data-services.yaml
    
    log_info "Deploying Batch 2.2: Business Logic Services..."
    kubectl apply -f deploy/k8s/dev/business-services.yaml
    
    log_info "Deploying Batch 2.3: Security Services..."
    kubectl apply -f deploy/k8s/dev/security-services.yaml
    
    # Wait for all services to be ready
    log_info "Waiting for all Phase 2 services to be ready..."
    local timeout=600  # 10 minutes
    local start_time=$(date +%s)
    local end_time=$((start_time + timeout))
    
    while [ $(date +%s) -lt $end_time ]; do
        local ready_services=$(kubectl get pods -n $NAMESPACE -l tier=business 2>/dev/null | grep "Running" | wc -l)
        local total_services=9
        
        if [ "$ready_services" -eq "$total_services" ]; then
            log_success "Phase 2 completed successfully (${ready_services}/${total_services} services running)"
            return 0
        fi
        
        log_info "Phase 2 progress: ${ready_services}/${total_services} services ready"
        sleep 30
    done
    
    log_error "Phase 2 deployment timed out"
    return 1
}

# Execute Phase 3: Operational Services
execute_phase3() {
    log_phase "Starting Phase 3: Operational Services"
    
    log_info "Deploying Batch 3.1: Monitoring Services..."
    kubectl apply -f deploy/k8s/dev/monitoring-services.yaml
    
    log_info "Deploying Batch 3.2: Intelligence Services..."
    kubectl apply -f deploy/k8s/dev/intelligence-services.yaml
    
    # Wait for all services to be ready
    log_info "Waiting for all Phase 3 services to be ready..."
    local timeout=600  # 10 minutes
    local start_time=$(date +%s)
    local end_time=$((start_time + timeout))
    
    while [ $(date +%s) -lt $end_time ]; do
        local ready_services=$(kubectl get pods -n $NAMESPACE -l tier=operational 2>/dev/null | grep "Running" | wc -l)
        local total_services=6
        
        if [ "$ready_services" -eq "$total_services" ]; then
            log_success "Phase 3 completed successfully (${ready_services}/${total_services} services running)"
            return 0
        fi
        
        log_info "Phase 3 progress: ${ready_services}/${total_services} services ready"
        sleep 30
    done
    
    log_error "Phase 3 deployment timed out"
    return 1
}

# Execute Phase 4: User Interface Services
execute_phase4() {
    log_phase "Starting Phase 4: User Interface Services"
    
    log_info "Deploying UI services..."
    kubectl apply -f deploy/k8s/dev/ui-services.yaml
    
    # Wait for all services to be ready
    log_info "Waiting for all Phase 4 services to be ready..."
    local timeout=300  # 5 minutes
    local start_time=$(date +%s)
    local end_time=$((start_time + timeout))
    
    while [ $(date +%s) -lt $end_time ]; do
        local ready_services=$(kubectl get pods -n $NAMESPACE -l tier=ui 2>/dev/null | grep "Running" | wc -l)
        local total_services=3
        
        if [ "$ready_services" -eq "$total_services" ]; then
            log_success "Phase 4 completed successfully (${ready_services}/${total_services} services running)"
            return 0
        fi
        
        log_info "Phase 4 progress: ${ready_services}/${total_services} services ready"
        sleep 30
    done
    
    log_error "Phase 4 deployment timed out"
    return 1
}

# Execute Phase 5: Utility Services
execute_phase5() {
    log_phase "Starting Phase 5: Utility Services"
    
    log_info "Deploying utility services..."
    kubectl apply -f deploy/k8s/dev/utility-services.yaml
    
    # Wait for all services to be ready
    log_info "Waiting for all Phase 5 services to be ready..."
    local timeout=300  # 5 minutes
    local start_time=$(date +%s)
    local end_time=$((start_time + timeout))
    
    while [ $(date +%s) -lt $end_time ]; do
        local ready_services=$(kubectl get pods -n $NAMESPACE -l tier=utility 2>/dev/null | grep "Running" | wc -l)
        local total_services=4
        
        if [ "$ready_services" -eq "$total_services" ]; then
            log_success "Phase 5 completed successfully (${ready_services}/${total_services} services running)"
            return 0
        fi
        
        log_info "Phase 5 progress: ${ready_services}/${total_services} services ready"
        sleep 30
    done
    
    log_error "Phase 5 deployment timed out"
    return 1
}

# Final validation
final_validation() {
    log_info "Performing final platform validation..."
    
    # Check total services
    local total_pods=$(kubectl get pods -n $NAMESPACE 2>/dev/null | grep -v "NAME" | wc -l)
    local running_pods=$(kubectl get pods -n $NAMESPACE 2>/dev/null | grep -v "NAME" | grep "Running" | wc -l)
    
    # Check resource usage
    local resource_info=$(kubectl describe nodes 2>/dev/null | grep -A 10 "Allocated resources" || echo "")
    local memory_usage=$(echo "$resource_info" | grep "memory" | head -1 | sed 's/.*(\([0-9]*\)%).*/\1/')
    
    echo ""
    echo "🎯 FINAL DEPLOYMENT VALIDATION"
    echo "==============================="
    echo "Total Services: $total_pods"
    echo "Running Services: $running_pods"
    echo "Memory Usage: ${memory_usage}%"
    echo ""
    
    if [ "$running_pods" -eq 26 ] && [ "$memory_usage" -lt 80 ]; then
        log_success "🎉 OpenPolicy Platform deployment completed successfully!"
        log_success "All 26 services are running with optimal resource usage"
        return 0
    else
        log_warning "Deployment completed with some issues:"
        log_warning "- Expected: 26 services, Found: $running_pods"
        log_warning "- Memory usage: ${memory_usage}% (target: <80%)"
        return 1
    fi
}

# Main deployment execution
main() {
    echo "🚀 OpenPolicy Platform - Complete Deployment"
    echo "============================================"
    echo ""
    
    # Initialize
    initialize_deployment
    
    # Execute phases
    local phase_results=()
    
    # Phase 1
    if execute_phase1; then
        phase_results+=("Phase 1: ✅ SUCCESS")
    else
        phase_results+=("Phase 1: ❌ FAILED")
        log_error "Deployment failed at Phase 1. Stopping deployment."
        exit 1
    fi
    
    # Phase 2
    if execute_phase2; then
        phase_results+=("Phase 2: ✅ SUCCESS")
    else
        phase_results+=("Phase 2: ❌ FAILED")
        log_error "Deployment failed at Phase 2. Stopping deployment."
        exit 1
    fi
    
    # Phase 3
    if execute_phase3; then
        phase_results+=("Phase 3: ✅ SUCCESS")
    else
        phase_results+=("Phase 3: ❌ FAILED")
        log_error "Deployment failed at Phase 3. Stopping deployment."
        exit 1
    fi
    
    # Phase 4
    if execute_phase4; then
        phase_results+=("Phase 4: ✅ SUCCESS")
    else
        phase_results+=("Phase 4: ❌ FAILED")
        log_error "Deployment failed at Phase 4. Stopping deployment."
        exit 1
    fi
    
    # Phase 5
    if execute_phase5; then
        phase_results+=("Phase 5: ✅ SUCCESS")
    else
        phase_results+=("Phase 5: ❌ FAILED")
        log_error "Deployment failed at Phase 5. Stopping deployment."
        exit 1
    fi
    
    # Final validation
    if final_validation; then
        echo ""
        echo "🎉 DEPLOYMENT SUMMARY"
        echo "====================="
        for result in "${phase_results[@]}"; do
            echo "$result"
        done
        echo ""
        echo "✅ All phases completed successfully!"
        echo "🚀 OpenPolicy Platform is now fully operational!"
        echo ""
        echo "Next steps:"
        echo "1. Run monitoring script: ./scripts/monitor_resources.sh"
        echo "2. Test platform functionality"
        echo "3. Review deployment logs: $LOG_FILE"
    else
        echo ""
        echo "⚠️  DEPLOYMENT SUMMARY"
        echo "====================="
        for result in "${phase_results[@]}"; do
            echo "$result"
        done
        echo ""
        echo "⚠️  Deployment completed with issues"
        echo "📋 Review logs and troubleshoot as needed"
        echo "📊 Check resource usage and service health"
    fi
}

# Handle errors gracefully
trap 'log_error "Deployment interrupted by user"; exit 1' INT

# Run main function
main "$@"
