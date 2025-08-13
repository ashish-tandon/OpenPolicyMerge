#!/bin/bash

# 🚀 OpenPolicy Platform - Phase 1 Deployment Script
# Infrastructure Foundation Services
# 
# This script deploys the core infrastructure services:
# - postgresql (1Gi memory, 500m CPU)
# - scraper-service (1Gi memory, 500m CPU)  
# - redis (512Mi memory, 200m CPU)
# - rabbitmq (512Mi memory, 250m CPU)

set -e  # Exit on any error

# Configuration
NAMESPACE="openpolicy-platform"
PHASE="Phase 1: Infrastructure Foundation"
TIMEOUT=300  # 5 minutes timeout for each service
CHECK_INTERVAL=10  # Check every 10 seconds

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        log_error "kubectl is not installed or not in PATH"
        exit 1
    fi
    
    if ! kubectl cluster-info &> /dev/null; then
        log_error "Cannot connect to Kubernetes cluster"
        exit 1
    fi
    
    log_success "Kubernetes cluster connection verified"
}

# Check cluster resources
check_cluster_resources() {
    log_info "Checking cluster resource availability..."
    
    # Get cluster capacity
    TOTAL_MEMORY=$(kubectl describe nodes | grep -A 5 "Allocated resources" | grep "memory" | head -1 | awk '{print $2}' | sed 's/Mi//')
    TOTAL_CPU=$(kubectl describe nodes | grep -A 5 "Allocated resources" | grep "cpu" | head -1 | awk '{print $2}' | sed 's/m//')
    
    if [ -z "$TOTAL_MEMORY" ] || [ -z "$TOTAL_CPU" ]; then
        log_error "Could not determine cluster capacity"
        exit 1
    fi
    
    log_info "Cluster capacity: ${TOTAL_MEMORY}Mi memory, ${TOTAL_CPU}m CPU"
    
    # Check if we have enough resources for Phase 1
    REQUIRED_MEMORY=3072  # 3Gi in Mi
    REQUIRED_CPU=1450     # 1.45 cores in m
    
    if [ "$TOTAL_MEMORY" -lt "$REQUIRED_MEMORY" ]; then
        log_error "Insufficient memory: ${TOTAL_MEMORY}Mi available, ${REQUIRED_MEMORY}Mi required"
        exit 1
    fi
    
    if [ "$TOTAL_CPU" -lt "$REQUIRED_CPU" ]; then
        log_error "Insufficient CPU: ${TOTAL_CPU}m available, ${REQUIRED_CPU}m required"
        exit 1
    fi
    
    log_success "Cluster has sufficient resources for Phase 1"
}

# Wait for service to be ready
wait_for_service() {
    local service_name=$1
    local expected_replicas=$2
    local timeout=$3
    
    log_info "Waiting for $service_name to be ready (timeout: ${timeout}s)..."
    
    local start_time=$(date +%s)
    local end_time=$((start_time + timeout))
    
    while [ $(date +%s) -lt $end_time ]; do
        local ready_replicas=$(kubectl get deployment $service_name -n $NAMESPACE -o jsonpath='{.status.readyReplicas}' 2>/dev/null || echo "0")
        local total_replicas=$(kubectl get deployment $service_name -n $NAMESPACE -o jsonpath='{.status.replicas}' 2>/dev/null || echo "0")
        
        if [ "$ready_replicas" = "$expected_replicas" ] && [ "$total_replicas" = "$expected_replicas" ]; then
            log_success "$service_name is ready (${ready_replicas}/${total_replicas} replicas)"
            return 0
        fi
        
        log_info "$service_name status: ${ready_replicas}/${total_replicas} replicas ready"
        sleep $CHECK_INTERVAL
    done
    
    log_error "$service_name failed to become ready within ${timeout}s"
    return 1
}

# Validate service health
validate_service_health() {
    local service_name=$1
    local port=$2
    local health_endpoint=$3
    
    log_info "Validating $service_name health..."
    
    # Get service pod
    local pod_name=$(kubectl get pods -n $NAMESPACE -l app=$service_name -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
    
    if [ -z "$pod_name" ]; then
        log_error "Could not find pod for $service_name"
        return 1
    fi
    
    # Check if pod is running
    local pod_status=$(kubectl get pod $pod_name -n $NAMESPACE -o jsonpath='{.status.phase}' 2>/dev/null)
    
    if [ "$pod_status" != "Running" ]; then
        log_error "$service_name pod is not running (status: $pod_status)"
        return 1
    fi
    
    # Check health endpoint if specified
    if [ -n "$health_endpoint" ]; then
        log_info "Checking health endpoint: $health_endpoint"
        
        # Port forward to access the service
        kubectl port-forward $pod_name -n $NAMESPACE $port:$port > /dev/null 2>&1 &
        local port_forward_pid=$!
        
        # Wait for port forward to be ready
        sleep 5
        
        # Test health endpoint
        if curl -f -s "http://localhost:$port$health_endpoint" > /dev/null 2>&1; then
            log_success "$service_name health check passed"
        else
            log_error "$service_name health check failed"
            kill $port_forward_pid 2>/dev/null || true
            return 1
        fi
        
        # Kill port forward
        kill $port_forward_pid 2>/dev/null || true
    fi
    
    log_success "$service_name validation completed"
    return 0
}

# Check resource usage
check_resource_usage() {
    log_info "Checking current resource usage..."
    
    kubectl describe nodes | grep -A 10 "Allocated resources" || true
    
    # Get memory usage percentage
    local memory_usage=$(kubectl describe nodes | grep -A 10 "Allocated resources" | grep "memory" | head -1 | sed 's/.*(\([0-9]*\)%).*/\1/')
    
    if [ -n "$memory_usage" ] && [ "$memory_usage" -gt 85 ]; then
        log_warning "High memory usage detected: ${memory_usage}%"
    else
        log_success "Memory usage is acceptable: ${memory_usage}%"
    fi
}

# Main deployment function
deploy_phase1() {
    log_info "Starting $PHASE deployment..."
    log_info "Target: 4 infrastructure services with 3Gi total memory"
    
    # Phase 1.1: Deploy PostgreSQL
    log_info "Deploying PostgreSQL (1Gi memory, 500m CPU)..."
    kubectl apply -f deploy/k8s/dev/postgresql.yaml
    
    if wait_for_service "postgresql" 1 $TIMEOUT; then
        validate_service_health "postgresql" 5432 "/healthz"
        check_resource_usage
    else
        log_error "PostgreSQL deployment failed"
        exit 1
    fi
    
    # Phase 1.2: Deploy Scraper Service
    log_info "Deploying Scraper Service (1Gi memory, 500m CPU)..."
    kubectl apply -f deploy/k8s/dev/additional-services.yaml
    
    if wait_for_service "scraper-service" 2 $TIMEOUT; then
        validate_service_health "scraper-service" 9016 "/healthz"
        check_resource_usage
    else
        log_error "Scraper Service deployment failed"
        exit 1
    fi
    
    # Phase 1.3: Deploy Redis
    log_info "Deploying Redis (512Mi memory, 200m CPU)..."
    kubectl apply -f deploy/k8s/dev/redis.yaml
    
    if wait_for_service "redis" 1 $TIMEOUT; then
        validate_service_health "redis" 6379 "/ping"
        check_resource_usage
    else
        log_error "Redis deployment failed"
        exit 1
    fi
    
    # Phase 1.4: Deploy RabbitMQ
    log_info "Deploying RabbitMQ (512Mi memory, 250m CPU)..."
    kubectl apply -f deploy/k8s/dev/rabbitmq.yaml
    
    if wait_for_service "rabbitmq" 1 $TIMEOUT; then
        validate_service_health "rabbitmq" 5672 "/"
        check_resource_usage
    else
        log_error "RabbitMQ deployment failed"
        exit 1
    fi
    
    log_success "$PHASE deployment completed successfully!"
    
    # Final resource check
    log_info "Final resource usage check:"
    check_resource_usage
    
    # Summary
    log_info "Phase 1 Summary:"
    log_info "- PostgreSQL: Running (1Gi memory)"
    log_info "- Scraper Service: Running (1Gi memory)"
    log_info "- Redis: Running (512Mi memory)"
    log_info "- RabbitMQ: Running (512Mi memory)"
    log_info "- Total Memory: ~3Gi"
    log_info "- Expected Usage: <40%"
}

# Main execution
main() {
    echo "🚀 OpenPolicy Platform - Phase 1 Deployment"
    echo "============================================="
    echo ""
    
    # Pre-deployment checks
    check_kubectl
    check_cluster_resources
    
    # Deploy Phase 1
    deploy_phase1
    
    echo ""
    echo "✅ Phase 1 deployment completed successfully!"
    echo "🎯 Next: Execute Phase 2 (Core Business Services)"
    echo ""
}

# Run main function
main "$@"
