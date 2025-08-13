#!/bin/bash

# Universal Service Dependency Management Script
# This script sets up ALL services with proper virtual environments and dependencies

set -e

echo "🚀 OPENPOLICY UNIVERSAL DEPENDENCY SETUP"
echo "========================================"

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

# Function to setup a service
setup_service() {
    local service_name=$1
    local service_path="services/$service_name"
    
    if [ ! -d "$service_path" ]; then
        print_warning "Service directory $service_path not found, skipping..."
        return 1
    fi
    
    print_status "Setting up $service_name..."
    cd "$service_path"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment for $service_name..."
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip to latest version
    print_status "Upgrading pip to latest version..."
    pip install --upgrade pip
    
    # Install dependencies if requirements.txt exists
    if [ -f "requirements.txt" ]; then
        print_status "Installing dependencies for $service_name..."
        pip install -r requirements.txt
        print_success "Dependencies installed for $service_name"
    else
        print_warning "No requirements.txt found for $service_name"
    fi
    
    # Install package.json dependencies if it exists
    if [ -f "package.json" ]; then
        print_status "Installing Node.js dependencies for $service_name..."
        npm install
        print_success "Node.js dependencies installed for $service_name"
    fi
    
    # Go modules if go.mod exists
    if [ -f "go.mod" ]; then
        print_status "Installing Go modules for $service_name..."
        go mod download
        print_success "Go modules installed for $service_name"
    fi
    
    cd - > /dev/null
    print_success "$service_name setup complete!"
    echo ""
}

# List of all services
services=(
    "policy-service"
    "search-service"
    "auth-service"
    "notification-service"
    "config-service"
    "health-service"
    "etl"
    "scraper-service"
    "monitoring-service"
    "plotly-service"
    "mcp-service"
    "api-gateway"
    "web"
    "mobile-api"
    "admin"
)

print_status "Starting dependency setup for ${#services[@]} services..."
echo ""

# Setup each service
for service in "${services[@]}"; do
    setup_service "$service"
done

print_success "All service dependencies have been set up!"
echo ""
print_status "Next steps:"
echo "1. Run: ./scripts/deploy_all_services_with_venv.sh"
echo "2. Check service health: ./scripts/check_all_services_health.sh"
echo "3. Monitor logs: tail -f /tmp/openpolicy_logs/*.log"
echo ""
print_status "Note: Virtual environments are now properly configured for all services"
print_status "Dependencies will be automatically managed when services start"
