#!/bin/bash

# VERBOSE MASS DEPLOYMENT SCRIPT
# This script deploys all 25 OpenPolicy services with detailed output
# Shows exactly what's happening and catches all errors

set -e  # Exit on any error

echo "🚀 VERBOSE MASS DEPLOYMENT: ALL 25 OPENPOLICY SERVICES"
echo "================================================================"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
print_status "Checking prerequisites..."
if ! command -v kubectl &> /dev/null; then
    print_error "kubectl is not installed"
    exit 1
fi

if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed"
    exit 1
fi

print_success "Prerequisites check passed"

# Check cluster status
print_status "Checking cluster status..."
if ! kubectl cluster-info &> /dev/null; then
    print_error "Cannot connect to Kubernetes cluster"
    exit 1
fi

print_success "Connected to cluster: $(kubectl cluster-info | grep 'Kubernetes control plane')"

# Check namespace
print_status "Checking namespace..."
if ! kubectl get namespace openpolicy-platform &> /dev/null; then
    print_warning "Namespace openpolicy-platform does not exist, creating..."
    kubectl create namespace openpolicy-platform
    print_success "Namespace created"
else
    print_success "Namespace exists"
fi

# Phase 1: Deploy Error Reporting Service FIRST
echo ""
print_status "PHASE 1: Deploying Error Reporting Service (Port 9024)..."
echo "================================================================"

print_status "Creating error reporting service deployment..."
kubectl apply -f deploy/k8s/FRESH_START_DEPLOYMENT.yaml --dry-run=client

if [ $? -eq 0 ]; then
    print_status "Dry run successful, applying for real..."
    kubectl apply -f deploy/k8s/FRESH_START_DEPLOYMENT.yaml --verbose=6
    
    if [ $? -eq 0 ]; then
        print_success "Error reporting service deployed successfully"
    else
        print_error "Failed to deploy error reporting service"
        exit 1
    fi
else
    print_error "Dry run failed, there are configuration errors"
    exit 1
fi

# Wait for error reporting service to be ready
print_status "Waiting for error reporting service to be ready..."
kubectl wait --for=condition=ready pod -l app=error-reporting-service -n openpolicy-platform --timeout=300s

if [ $? -eq 0 ]; then
    print_success "Error reporting service is ready"
else
    print_warning "Error reporting service not ready within timeout"
fi

# Phase 2: Deploy ALL other services in parallel
echo ""
print_status "PHASE 2: Deploying ALL remaining services in parallel..."
echo "================================================================"

print_status "Checking current pod status..."
kubectl get pods -n openpolicy-platform

print_status "Checking current service status..."
kubectl get svc -n openpolicy-platform

print_status "Checking current deployment status..."
kubectl get deployments -n openpolicy-platform

# Show detailed deployment progress
echo ""
print_status "Monitoring deployment progress..."
echo "================================================================"

# Function to monitor deployment
monitor_deployment() {
    local service_name=$1
    local max_wait=300  # 5 minutes
    
    print_status "Monitoring deployment of $service_name..."
    
    for i in $(seq 1 $max_wait); do
        local status=$(kubectl get deployment $service_name -n openpolicy-platform -o jsonpath='{.status.conditions[?(@.type=="Available")].status}' 2>/dev/null || echo "Unknown")
        
        if [ "$status" = "True" ]; then
            print_success "$service_name deployment successful"
            return 0
        elif [ "$status" = "False" ]; then
            print_error "$service_name deployment failed"
            kubectl describe deployment $service_name -n openpolicy-platform
            return 1
        fi
        
        if [ $((i % 10)) -eq 0 ]; then
            print_status "Waiting for $service_name... ($i seconds)"
        fi
        
        sleep 1
    done
    
    print_warning "$service_name deployment timeout"
    return 1
}

# Monitor all deployments
services=("api-gateway" "search-service" "policy-service" "notification-service" "config-service" "health-service" "monitoring-service" "scraper-service" "etl-service" "analytics-service" "audit-service" "auth-service" "mcp-service" "postgresql" "redis" "rabbitmq" "prometheus" "grafana")

for service in "${services[@]}"; do
    monitor_deployment $service &
done

# Wait for all monitoring to complete
wait

# Final status check
echo ""
print_status "FINAL STATUS CHECK"
echo "================================================================"

print_status "All pods:"
kubectl get pods -n openpolicy-platform -o wide

print_status "All services:"
kubectl get svc -n openpolicy-platform -o wide

print_status "All deployments:"
kubectl get deployments -n openpolicy-platform

# Test service connectivity
echo ""
print_status "TESTING SERVICE CONNECTIVITY"
echo "================================================================"

# Test error reporting service
print_status "Testing error reporting service..."
if kubectl get svc error-reporting-service -n openpolicy-platform &> /dev/null; then
    print_success "Error reporting service is accessible"
else
    print_error "Error reporting service is not accessible"
fi

# Test API gateway
print_status "Testing API gateway..."
if kubectl get svc api-gateway -n openpolicy-platform &> /dev/null; then
    print_success "API gateway is accessible"
else
    print_error "API gateway is not accessible"
fi

# Show service endpoints
echo ""
print_status "SERVICE ENDPOINTS"
echo "================================================================"
kubectl get endpoints -n openpolicy-platform

print_success "Deployment completed! Check the output above for any errors."
echo ""
print_status "Next steps:"
echo "1. Check error reporting service logs: kubectl logs -f deployment/error-reporting-service -n openpolicy-platform"
echo "2. Test API gateway: kubectl port-forward svc/api-gateway 9001:9001 -n openpolicy-platform"
echo "3. Monitor all services: kubectl get pods -n openpolicy-platform -w"
