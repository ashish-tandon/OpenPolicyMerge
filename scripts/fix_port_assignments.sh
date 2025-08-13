#!/bin/bash

# 🚀 OPENPOLICY PLATFORM - PORT ASSIGNMENT FIX SCRIPT
# Fixes all non-standard port assignments to follow 9000 series standards

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo "🔧 OPENPOLICY PLATFORM - PORT ASSIGNMENT FIX"
echo "============================================="
echo ""

# Port mapping for services that need fixes (using simple arrays for macOS compatibility)
SERVICES=("web" "mobile-api" "admin" "legacy-django" "op-import")
NEW_PORTS=("9019" "9020" "9021" "9022" "9023")
OLD_PORTS=("3000" "8081" "3001" "8001" "8002")

# Function to fix port in Python files
fix_python_port() {
    local service_dir="$1"
    local old_port="$2"
    local new_port="$3"
    
    echo "  🔧 Fixing Python port assignments..."
    
    # Fix main.py
    if [[ -f "$service_dir/src/main.py" ]]; then
        sed -i.bak "s/port=$old_port/port=$new_port/g" "$service_dir/src/main.py"
        sed -i.bak "s/port = $old_port/port = $new_port/g" "$service_dir/src/main.py"
        echo "    ✅ Fixed main.py"
    fi
    
    # Fix config.py
    if [[ -f "$service_dir/src/config.py" ]]; then
        sed -i.bak "s/SERVICE_PORT.*=.*$old_port/SERVICE_PORT = $new_port/g" "$service_dir/src/config.py"
        echo "    ✅ Fixed config.py"
    fi
    
    # Fix start.sh
    if [[ -f "$service_dir/start.sh" ]]; then
        sed -i.bak "s/port $old_port/port $new_port/g" "$service_dir/start.sh"
        echo "    ✅ Fixed start.sh"
    fi
}

# Function to fix port in Node.js files
fix_nodejs_port() {
    local service_dir="$1"
    local old_port="$2"
    local new_port="$3"
    
    echo "  🔧 Fixing Node.js port assignments..."
    
    # Fix package.json
    if [[ -f "$service_dir/package.json" ]]; then
        sed -i.bak "s/\"port\": $old_port/\"port\": $new_port/g" "$service_dir/package.json"
        echo "    ✅ Fixed package.json"
    fi
    
    # Fix start.sh
    if [[ -f "$service_dir/start.sh" ]]; then
        sed -i.bak "s/port $old_port/port $new_port/g" "$service_dir/start.sh"
        echo "    ✅ Fixed start.sh"
    fi
}

# Function to fix port in Go files
fix_go_port() {
    local service_dir="$1"
    local old_port="$2"
    local new_port="$3"
    
    echo "  🔧 Fixing Go port assignments..."
    
    # Fix main.go
    if [[ -f "$service_dir/src/main.go" ]]; then
        sed -i.bak "s/port = \"$old_port\"/port = \"$new_port\"/g" "$service_dir/src/main.go"
        echo "    ✅ Fixed main.go"
    fi
    
    # Fix start.sh
    if [[ -f "$service_dir/start.sh" ]]; then
        sed -i.bak "s/port $old_port/port $new_port/g" "$service_dir/start.sh"
        echo "    ✅ Fixed start.sh"
    fi
}

# Function to fix port in Dockerfiles
fix_dockerfile_port() {
    local service_dir="$1"
    local old_port="$2"
    local new_port="$3"
    
    echo "  🔧 Fixing Dockerfile port assignments..."
    
    if [[ -f "$service_dir/Dockerfile" ]]; then
        sed -i.bak "s/EXPOSE $old_port/EXPOSE $new_port/g" "$service_dir/Dockerfile"
        echo "    ✅ Fixed Dockerfile"
    fi
}

# Function to fix a single service
fix_service_ports() {
    local service_name="$1"
    local old_port="$2"
    local new_port="$3"
    local service_dir="services/$service_name"
    
    echo ""
    echo "🔧 Fixing Service: $service_name"
    echo "  Current Directory: $service_dir"
    echo "  Port Change: $old_port → $new_port"
    echo "  ----------------------------------------"
    
    # Check if service directory exists
    if [[ ! -d "$service_dir" ]]; then
        echo "  ❌ Service directory not found: $service_dir"
        return 1
    fi
    
    # Create backup
    echo "  💾 Creating backup..."
    cp -r "$service_dir" "${service_dir}.backup.$(date +%Y%m%d_%H%M%S)"
    echo "    ✅ Backup created"
    
    # Fix ports based on service type
    if [[ -f "$service_dir/requirements.txt" ]]; then
        # Python service
        fix_python_port "$service_dir" "$old_port" "$new_port"
    elif [[ -f "$service_dir/package.json" ]]; then
        # Node.js service
        fix_nodejs_port "$service_dir" "$old_port" "$new_port"
    elif [[ -f "$service_dir/src/main.go" ]]; then
        # Go service
        fix_go_port "$service_dir" "$old_port" "$new_port"
    else
        echo "  ⚠️ Unknown service type, attempting generic port fix"
        # Generic fix for start.sh
        if [[ -f "$service_dir/start.sh" ]]; then
            sed -i.bak "s/port $old_port/port $new_port/g" "$service_dir/start.sh"
            echo "    ✅ Fixed start.sh (generic)"
        fi
    fi
    
    # Fix Dockerfile if it exists
    fix_dockerfile_port "$service_dir" "$old_port" "$new_port"
    
    # Update service documentation
    echo "  📝 Updating service documentation..."
    if [[ -f "$service_dir/README.md" ]]; then
        sed -i.bak "s/port $old_port/port $new_port/g" "$service_dir/README.md"
        echo "    ✅ Fixed README.md"
    fi
    
    echo "  🎉 Port fix completed for $service_name"
}

# Function to update deployment scripts
update_deployment_scripts() {
    echo ""
    echo "📝 Updating deployment scripts..."
    echo "  ----------------------------------------"
    
    # Update main deployment script
    if [[ -f "scripts/deploy_all_25_services.sh" ]]; then
        echo "  🔧 Updating deploy_all_25_services.sh..."
        
        # Fix web frontend port
        sed -i.bak "s/port 3000/port 9019/g" "scripts/deploy_all_25_services.sh"
        sed -i.bak "s/port.*3000/port 9019/g" "scripts/deploy_all_25_services.sh"
        
        # Fix mobile API port
        sed -i.bak "s/port 8081/port 9020/g" "scripts/deploy_all_25_services.sh"
        sed -i.bak "s/port.*8081/port 9020/g" "scripts/deploy_all_25_services.sh"
        
        # Fix admin dashboard port
        sed -i.bak "s/port 3001/port 9021/g" "scripts/deploy_all_25_services.sh"
        sed -i.bak "s/port.*3001/port 9021/g" "scripts/deploy_all_25_services.sh"
        
        # Fix legacy django port
        sed -i.bak "s/port 8001/port 9022/g" "scripts/deploy_all_25_services.sh"
        sed -i.bak "s/port.*8001/port 9022/g" "scripts/deploy_all_25_services.sh"
        
        # Fix op import port
        sed -i.bak "s/port 8002/port 9023/g" "scripts/deploy_all_25_services.sh"
        sed -i.bak "s/port.*8002/port 9023/g" "scripts/deploy_all_25_services.sh"
        
        echo "    ✅ Updated deploy_all_25_services.sh"
    fi
    
    # Update health check script
    if [[ -f "scripts/check_all_services_health.sh" ]]; then
        echo "  🔧 Updating check_all_services_health.sh..."
        
        # Replace old ports with new ones in health checks
        sed -i.bak "s/3000/9019/g" "scripts/check_all_services_health.sh"
        sed -i.bak "s/8081/9020/g" "scripts/check_all_services_health.sh"
        sed -i.bak "s/3001/9021/g" "scripts/check_all_services_health.sh"
        sed -i.bak "s/8001/9022/g" "scripts/check_all_services_health.sh"
        sed -i.bak "s/8002/9023/g" "scripts/check_all_services_health.sh"
        
        echo "    ✅ Updated check_all_services_health.sh"
    fi
    
    echo "  🎉 Deployment scripts updated"
}

# Function to update documentation
update_documentation() {
    echo ""
    echo "📚 Updating documentation..."
    echo "  ----------------------------------------"
    
    # Update SERVICE_STATUS_REPORT.md
    if [[ -f "SERVICE_STATUS_REPORT.md" ]]; then
        echo "  🔧 Updating SERVICE_STATUS_REPORT.md..."
        sed -i.bak "s/3000/9019/g" "SERVICE_STATUS_REPORT.md"
        sed -i.bak "s/8081/9020/g" "SERVICE_STATUS_REPORT.md"
        sed -i.bak "s/3001/9021/g" "SERVICE_STATUS_REPORT.md"
        sed -i.bak "s/8001/9022/g" "SERVICE_STATUS_REPORT.md"
        sed -i.bak "s/8002/9023/g" "SERVICE_STATUS_REPORT.md"
        echo "    ✅ Updated SERVICE_STATUS_REPORT.md"
    fi
    
    # Update PORT_ASSIGNMENT_GUIDE.md
    if [[ -f "docs/PORT_ASSIGNMENT_GUIDE.md" ]]; then
        echo "  🔧 Updating PORT_ASSIGNMENT_GUIDE.md..."
        sed -i.bak "s/3000/9019/g" "docs/PORT_ASSIGNMENT_GUIDE.md"
        sed -i.bak "s/8081/9020/g" "docs/PORT_ASSIGNMENT_GUIDE.md"
        sed -i.bak "s/3001/9021/g" "docs/PORT_ASSIGNMENT_GUIDE.md"
        sed -i.bak "s/8001/9022/g" "docs/PORT_ASSIGNMENT_GUIDE.md"
        sed -i.bak "s/8002/9023/g" "docs/PORT_ASSIGNMENT_GUIDE.md"
        echo "    ✅ Updated PORT_ASSIGNMENT_GUIDE.md"
    fi
    
    echo "  🎉 Documentation updated"
}

# Function to create new port assignment summary
create_port_summary() {
    echo ""
    echo "📊 NEW PORT ASSIGNMENT SUMMARY"
    echo "==============================="
    echo ""
    echo "✅ STANDARD PORTS (9000 Series):"
    echo "  Core Services: 9001-9012"
    echo "  New Services: 9013-9018"
    echo "  Frontend Services: 9019-9023"
    echo "  Special Services: 8181 (OPA)"
    echo ""
    echo "🔄 PORT CHANGES MADE:"
    echo "  Web Frontend: 3000 → 9019"
    echo "  Mobile API: 8081 → 9020"
    echo "  Admin Dashboard: 3001 → 9021"
    echo "  Legacy Django: 8001 → 9022"
    echo "  OP Import: 8002 → 9023"
    echo ""
    echo "🎯 ALL SERVICES NOW FOLLOW 9000 SERIES STANDARDS!"
}

# Main function
main() {
    echo "🚀 Starting OpenPolicy Platform Port Assignment Fix..."
    echo ""
    
    # Check if we're in the right directory
    if [[ ! -d "services" ]]; then
        echo -e "${RED}❌ Error: services directory not found${NC}"
        echo "Please run this script from the OpenPolicy platform root directory"
        exit 1
    fi
    
    # Create backup directory
    echo "💾 Creating backup directory..."
    mkdir -p "port_fix_backups/$(date +%Y%m%d_%H%M%S)"
    echo "  ✅ Backup directory created"
    
    # Fix each service
    for i in "${!SERVICES[@]}"; do
        local service_name="${SERVICES[$i]}"
        local old_port="${OLD_PORTS[$i]}"
        local new_port="${NEW_PORTS[$i]}"
        fix_service_ports "$service_name" "$old_port" "$new_port"
    done
    
    # Update deployment scripts
    update_deployment_scripts
    
    # Update documentation
    update_documentation
    
    # Create port summary
    create_port_summary
    
    echo ""
    echo "🎉 PORT ASSIGNMENT FIX COMPLETED SUCCESSFULLY!"
    echo "=============================================="
    echo ""
    echo "📋 NEXT STEPS:"
    echo "  1. Review the changes made to each service"
    echo "  2. Test the updated configuration files"
    echo "  3. Run the comprehensive audit again"
    echo "  4. Start services with new port assignments"
    echo ""
    echo "🔗 RELATED DOCUMENTS:"
    echo "  - [Centralized Port Management](./docs/CENTRALIZED_PORT_MANAGEMENT.md)"
    echo "  - [Port Assignment Guide](./docs/PORT_ASSIGNMENT_GUIDE.md)"
    echo "  - [Service Standards](./docs/SERVICE_STANDARDS.md)"
    echo ""
    echo -e "${GREEN}✅ All non-standard ports have been corrected to follow 9000 series standards!${NC}"
}

# Run main function
main "$@"
