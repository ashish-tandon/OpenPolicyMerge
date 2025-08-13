#!/bin/bash

# 🚀 OPENPOLICY PLATFORM - COMPREHENSIVE SERVICE AUDIT
# Audits all services for compliance, ports, I/O variables, and documentation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Directories
SERVICES_DIR="services"
REPORTS_DIR="comprehensive_audit_reports"
STANDARDS_FILE="docs/SERVICE_STANDARDS.md"
MASTER_REPORT="$REPORTS_DIR/MASTER_SERVICE_REPORT.md"

# Create reports directory
mkdir -p "$REPORTS_DIR"

echo "🔍 OPENPOLICY PLATFORM - COMPREHENSIVE SERVICE AUDIT"
echo "====================================================="
echo "Standards File: $STANDARDS_FILE"
echo "Services Directory: $SERVICES_DIR"
echo "Reports Directory: $REPORTS_DIR"
echo "Master Report: $MASTER_REPORT"
echo ""

# Function to check if file exists
check_file_exists() {
    local file_path="$1"
    local description="$2"
    if [[ -f "$file_path" ]]; then
        echo -e "  ✅ $description: $file_path"
        return 0
    else
        echo -e "  ❌ $description: MISSING - $file_path"
        return 1
    fi
}

# Function to check if directory exists
check_dir_exists() {
    local dir_path="$1"
    local description="$2"
    if [[ -d "$dir_path" ]]; then
        echo -e "  ✅ $description: $dir_path"
        return 0
    else
        echo -e "  ❌ $description: MISSING - $dir_path"
        return 1
    fi
}

# Function to check if file is executable
check_executable() {
    local file_path="$1"
    local description="$2"
    if [[ -x "$file_path" ]]; then
        echo -e "  ✅ $description: EXECUTABLE - $file_path"
        return 0
    else
        echo -e "  ❌ $description: NOT EXECUTABLE - $file_path"
        return 1
    fi
}

# Function to extract port from configuration files
extract_port() {
    local service_dir="$1"
    local port="UNKNOWN"
    
    # Check main.py
    if [[ -f "$service_dir/src/main.py" ]]; then
        local extracted=$(grep -o "port=[0-9]*" "$service_dir/src/main.py" | head -1 | cut -d= -f2)
        if [[ -n "$extracted" ]]; then
            port="$extracted"
        fi
    fi
    
    # Check config.py
    if [[ -f "$service_dir/src/config.py" ]]; then
        local extracted=$(grep -o "SERVICE_PORT.*[0-9]*" "$service_dir/src/config.py" | head -1 | grep -o "[0-9]*" | head -1)
        if [[ -n "$extracted" ]]; then
            port="$extracted"
        fi
    fi
    
    # Check start.sh
    if [[ -f "$service_dir/start.sh" ]]; then
        local extracted=$(grep -o "port [0-9]*" "$service_dir/start.sh" | head -1 | cut -d' ' -f2)
        if [[ -n "$extracted" ]]; then
            port="$extracted"
        fi
    fi
    
    # Check package.json for Node.js services
    if [[ -f "$service_dir/package.json" ]]; then
        local extracted=$(grep -o '"port": [0-9]*' "$service_dir/package.json" | head -1 | cut -d' ' -f2)
        if [[ -n "$extracted" ]]; then
            port="$extracted"
        fi
    fi
    
    echo "$port"
}

# Function to check I/O variables and dependencies
check_io_variables() {
    local service_dir="$1"
    local report_file="$2"
    
    echo "### I/O Variables & Dependencies" >> "$report_file"
    echo "" >> "$report_file"
    
    # Check requirements.txt
    if [[ -f "$service_dir/requirements.txt" ]]; then
        echo "#### Python Dependencies (requirements.txt):" >> "$report_file"
        echo '```' >> "$report_file"
        cat "$service_dir/requirements.txt" >> "$report_file"
        echo '```' >> "$report_file"
        echo "" >> "$report_file"
    fi
    
    # Check package.json
    if [[ -f "$service_dir/package.json" ]]; then
        echo "#### Node.js Dependencies (package.json):" >> "$report_file"
        echo '```json' >> "$report_file"
        cat "$service_dir/package.json" >> "$report_file"
        echo '```' >> "$report_file"
        echo "" >> "$report_file"
    fi
    
    # Check .env.example
    if [[ -f "$service_dir/.env.example" ]]; then
        echo "#### Environment Variables (.env.example):" >> "$report_file"
        echo '```bash' >> "$report_file"
        cat "$service_dir/.env.example" >> "$report_file"
        echo '```' >> "$report_file"
        echo "" >> "$report_file"
    else
        echo "#### Environment Variables (.env.example):" >> "$report_file"
        echo "❌ MISSING - No environment configuration found" >> "$report_file"
        echo "" >> "$report_file"
    fi
    
    # Check Dockerfile
    if [[ -f "$service_dir/Dockerfile" ]]; then
        echo "#### Container Configuration (Dockerfile):" >> "$report_file"
        echo '```dockerfile' >> "$report_file"
        cat "$service_dir/Dockerfile" >> "$report_file"
        echo '```' >> "$report_file"
        echo "" >> "$report_file"
    fi
}

# Function to audit a single service comprehensively
audit_service() {
    local service_name="$1"
    local service_dir="$2"
    local report_file="$REPORTS_DIR/${service_name}_comprehensive_audit.md"
    
    echo ""
    echo "🔍 Auditing Service: $service_name"
    echo "----------------------------------------"
    
    # Initialize compliance counters
    local total_checks=0
    local passed_checks=0
    local failed_checks=0
    
    # Extract port
    local assigned_port=$(extract_port "$service_dir")
    
    # Start comprehensive report
    cat > "$report_file" << EOF
# 📊 COMPREHENSIVE AUDIT REPORT: $service_name

> **Generated**: $(date)
> **Service**: $service_name
> **Assigned Port**: $assigned_port
> **Standards Version**: 1.0.0

## 📋 COMPLIANCE SUMMARY

EOF
    
    echo "## 📋 FILE STRUCTURE COMPLIANCE" >> "$report_file"
    echo "" >> "$report_file"
    
    # 1. FILE STRUCTURE REQUIREMENTS
    echo "### 1. File Structure Requirements" >> "$report_file"
    echo "" >> "$report_file"
    
    # Check Dockerfile
    ((total_checks++))
    if check_file_exists "$service_dir/Dockerfile" "Dockerfile"; then
        ((passed_checks++))
        echo "✅ Dockerfile exists" >> "$report_file"
    else
        ((failed_checks++))
        echo "❌ Dockerfile missing" >> "$report_file"
    fi
    
    # Check requirements.txt or package.json
    ((total_checks++))
    if [[ -f "$service_dir/requirements.txt" ]] || [[ -f "$service_dir/package.json" ]]; then
        ((passed_checks++))
        echo "✅ Dependencies file exists" >> "$report_file"
    else
        ((failed_checks++))
        echo "❌ Dependencies file missing" >> "$report_file"
    fi
    
    # Check start.sh
    ((total_checks++))
    if check_file_exists "$service_dir/start.sh" "start.sh"; then
        ((passed_checks++))
        echo "✅ start.sh exists" >> "$report_file"
        # Check if executable
        ((total_checks++))
        if check_executable "$service_dir/start.sh" "start.sh"; then
            ((passed_checks++))
            echo "✅ start.sh is executable" >> "$report_file"
        else
            ((failed_checks++))
            echo "❌ start.sh is not executable" >> "$report_file"
        fi
    else
        ((failed_checks++))
        echo "❌ start.sh missing" >> "$report_file"
    fi
    
    # Check src directory
    ((total_checks++))
    if check_dir_exists "$service_dir/src" "src directory"; then
        ((passed_checks++))
        echo "✅ src directory exists" >> "$report_file"
        
        # Check required source files
        ((total_checks++))
        if check_file_exists "$service_dir/src/__init__.py" "src/__init__.py"; then
            ((passed_checks++))
            echo "✅ src/__init__.py exists" >> "$report_file"
        else
            ((failed_checks++))
            echo "❌ src/__init__.py missing" >> "$report_file"
        fi
        
        ((total_checks++))
        if check_file_exists "$service_dir/src/main.py" "src/main.py"; then
            ((passed_checks++))
            echo "✅ src/main.py exists" >> "$report_file"
        else
            ((failed_checks++))
            echo "❌ src/main.py missing" >> "$report_file"
        fi
        
        ((total_checks++))
        if check_file_exists "$service_dir/src/config.py" "src/config.py"; then
            ((passed_checks++))
            echo "✅ src/config.py exists" >> "$report_file"
        else
            ((failed_checks++))
            echo "❌ src/config.py missing" >> "$report_file"
        fi
        
        ((total_checks++))
        if check_file_exists "$service_dir/src/api.py" "src/api.py"; then
            ((passed_checks++))
            echo "✅ src/api.py exists" >> "$report_file"
        else
            ((failed_checks++))
            echo "❌ src/api.py missing" >> "$report_file"
        fi
    else
        ((failed_checks++))
        echo "❌ src directory missing" >> "$report_file"
    fi
    
    # Check tests directory
    ((total_checks++))
    if check_dir_exists "$service_dir/tests" "tests directory"; then
        ((passed_checks++))
        echo "✅ tests directory exists" >> "$report_file"
        
        # Check for test files
        local test_files=$(find "$service_dir/tests" -name "*.py" 2>/dev/null | wc -l)
        if [[ $test_files -gt 0 ]]; then
            ((passed_checks++))
            echo "✅ Test files exist ($test_files found)" >> "$report_file"
        else
            ((failed_checks++))
            echo "❌ No test files found" >> "$report_file"
        fi
    else
        ((failed_checks++))
        echo "❌ tests directory missing" >> "$report_file"
    fi
    
    # Check logs directory
    ((total_checks++))
    if check_dir_exists "$service_dir/logs" "logs directory"; then
        ((passed_checks++))
        echo "✅ logs directory exists" >> "$report_file"
    else
        ((failed_checks++))
        echo "❌ logs directory missing" >> "$report_file"
    fi
    
    # Check venv directory (Python services)
    if [[ -f "$service_dir/requirements.txt" ]]; then
        ((total_checks++))
        if check_dir_exists "$service_dir/venv" "venv directory"; then
            ((passed_checks++))
            echo "✅ venv directory exists" >> "$report_file"
        else
            ((failed_checks++))
            echo "❌ venv directory missing" >> "$report_file"
        fi
    fi
    
    # Check .env.example
    ((total_checks++))
    if check_file_exists "$service_dir/.env.example" ".env.example"; then
        ((passed_checks++))
        echo "✅ .env.example exists" >> "$report_file"
    else
        ((failed_checks++))
        echo "❌ .env.example missing" >> "$report_file"
    fi
    
    # Add I/O variables and dependencies section
    echo "" >> "$report_file"
    check_io_variables "$service_dir" "$report_file"
    
    # Add port assignment section
    echo "## 🔌 PORT ASSIGNMENT" >> "$report_file"
    echo "" >> "$report_file"
    echo "**Current Assigned Port**: $assigned_port" >> "$report_file"
    echo "" >> "$report_file"
    
    # Check if port follows 9000 series standard
    if [[ "$assigned_port" =~ ^90[0-9][0-9]$ ]] || [[ "$assigned_port" == "8181" ]]; then
        echo "✅ Port follows OpenPolicy standards" >> "$report_file"
    else
        echo "❌ Port does NOT follow OpenPolicy standards (should be 9000 series)" >> "$report_file"
    fi
    
    echo "" >> "$report_file"
    echo "## 📊 COMPLIANCE SCORE" >> "$report_file"
    echo "" >> "$report_file"
    
    local compliance_percentage=$(( (passed_checks * 100) / total_checks ))
    
    echo "**Total Checks**: $total_checks" >> "$report_file"
    echo "**Passed**: $passed_checks" >> "$report_file"
    echo "**Failed**: $failed_checks" >> "$report_file"
    echo "**Compliance**: $compliance_percentage%" >> "$report_file"
    echo "" >> "$report_file"
    
    if [[ $compliance_percentage -eq 100 ]]; then
        echo "**Status**: 🎉 FULLY COMPLIANT" >> "$report_file"
    elif [[ $compliance_percentage -ge 80 ]]; then
        echo "**Status**: ✅ MOSTLY COMPLIANT" >> "$report_file"
    elif [[ $compliance_percentage -ge 60 ]]; then
        echo "**Status**: ⚠️ PARTIALLY COMPLIANT" >> "$report_file"
    else
        echo "**Status**: ❌ NON-COMPLIANT" >> "$report_file"
    fi
    
    echo "" >> "$report_file"
    echo "## 🚀 RECOMMENDATIONS" >> "$report_file"
    echo "" >> "$report_file"
    
    if [[ $failed_checks -gt 0 ]]; then
        echo "### Missing Components:" >> "$report_file"
        echo "" >> "$report_file"
        echo "- Review the audit output above for specific missing components" >> "$report_file"
        echo "- Implement missing components according to priority order" >> "$report_file"
        echo "- Re-run audit after implementation" >> "$report_file"
    else
        echo "🎉 All required components are present!" >> "$report_file"
        echo "" >> "$report_file"
        echo "Next steps:" >> "$report_file"
        echo "- Review code quality and implementation details" >> "$report_file"
        echo "- Test functionality and integration" >> "$report_file"
        echo "- Validate against additional standards requirements" >> "$report_file"
    fi
    
    # Print summary to console
    echo -e "${BLUE}📊 Comprehensive Audit Summary for $service_name:${NC}"
    echo -e "  Total Checks: $total_checks"
    echo -e "  Passed: ${GREEN}$passed_checks${NC}"
    echo -e "  Failed: ${RED}$failed_checks${NC}"
    echo -e "  Compliance: ${BLUE}$compliance_percentage%${NC}"
    echo -e "  Assigned Port: ${CYAN}$assigned_port${NC}"
    
    if [[ $compliance_percentage -eq 100 ]]; then
        echo -e "  Status: ${GREEN}🎉 FULLY COMPLIANT${NC}"
    elif [[ $compliance_percentage -ge 80 ]]; then
        echo -e "  Status: ${GREEN}✅ MOSTLY COMPLIANT${NC}"
    elif [[ $compliance_percentage -ge 60 ]]; then
        echo -e "  Status: ${YELLOW}⚠️ PARTIALLY COMPLIANT${NC}"
    else
        echo -e "  Status: ${RED}❌ NON-COMPLIANT${NC}"
    fi
    
    echo "  Report saved to: $report_file"
    
    return $failed_checks
}

# Function to create master report
create_master_report() {
    local services=("$@")
    
    cat > "$MASTER_REPORT" << EOF
# 🚀 OPENPOLICY PLATFORM - MASTER SERVICE REPORT

> **Generated**: $(date)
> **Total Services**: ${#services[@]}
> **Standards Version**: 1.0.0

## 📊 EXECUTIVE SUMMARY

This report provides a comprehensive overview of all OpenPolicy platform services, including:
- Compliance ratings
- Port assignments
- I/O variables and dependencies
- Documentation status
- Recommendations for improvement

## 🔗 SERVICE REPORTS

EOF
    
    for service_name in "${services[@]}"; do
        local report_file="$REPORTS_DIR/${service_name}_comprehensive_audit.md"
        if [[ -f "$report_file" ]]; then
            echo "- [**$service_name**](./${service_name}_comprehensive_audit.md) - Comprehensive audit report" >> "$MASTER_REPORT"
        fi
    done
    
    echo "" >> "$MASTER_REPORT"
    echo "## 📋 COMPLIANCE OVERVIEW" >> "$MASTER_REPORT"
    echo "" >> "$MASTER_REPORT"
    echo "| Service | Compliance | Port | Status | Report |" >> "$MASTER_REPORT"
    echo "|---------|------------|------|--------|---------|" >> "$MASTER_REPORT"
    
    for service_name in "${services[@]}"; do
        local report_file="$REPORTS_DIR/${service_name}_comprehensive_audit.md"
        if [[ -f "$report_file" ]]; then
            local compliance=$(grep "**Compliance**:" "$report_file" | head -1 | grep -o "[0-9]*%" | head -1)
            local port=$(grep "**Current Assigned Port**:" "$report_file" | head -1 | cut -d: -f2 | xargs)
            local status=$(grep "**Status**:" "$report_file" | head -1 | grep -o "🎉 FULLY COMPLIANT\|✅ MOSTLY COMPLIANT\|⚠️ PARTIALLY COMPLIANT\|❌ NON-COMPLIANT" | head -1)
            echo "| $service_name | $compliance | $port | $status | [View](./${service_name}_comprehensive_audit.md) |" >> "$MASTER_REPORT"
        fi
    done
    
    echo "" >> "$MASTER_REPORT"
    echo "## 🎯 NEXT STEPS" >> "$MASTER_REPORT"
    echo "" >> "$MASTER_REPORT"
    echo "1. **Review individual service reports** for detailed compliance information" >> "$MASTER_REPORT"
    echo "2. **Address compliance gaps** in priority order" >> "$MASTER_REPORT"
    echo "3. **Fix port assignments** to follow 9000 series standards" >> "$MASTER_REPORT"
    echo "4. **Implement missing components** according to service standards" >> "$MASTER_REPORT"
    echo "5. **Re-run comprehensive audit** after improvements" >> "$MASTER_REPORT"
    echo "" >> "$MASTER_REPORT"
    echo "## 📚 DOCUMENTATION LINKS" >> "$MASTER_REPORT"
    echo "" >> "$MASTER_REPORT"
    echo "- [Service Standards](../docs/SERVICE_STANDARDS.md)" >> "$MASTER_REPORT"
    echo "- [Port Assignment Guide](../PORT_ASSIGNMENT_GUIDE.md)" >> "$MASTER_REPORT"
    echo "- [Compliance Action Plan](../COMPLIANCE_ACTION_PLAN.md)" >> "$MASTER_REPORT"
    echo "- [Compliance Implementation Status](../COMPLIANCE_IMPLEMENTATION_STATUS.md)" >> "$MASTER_REPORT"
}

# Main audit function
main() {
    echo "🚀 Starting OpenPolicy Platform Comprehensive Service Audit..."
    echo ""
    
    # Check if standards file exists
    if [[ ! -f "$STANDARDS_FILE" ]]; then
        echo -e "${RED}❌ Standards file not found: $STANDARDS_FILE${NC}"
        exit 1
    fi
    
    # Get list of services
    local services=()
    for service_dir in "$SERVICES_DIR"/*/; do
        if [[ -d "$service_dir" ]]; then
            local service_name=$(basename "$service_dir")
            services+=("$service_name")
        fi
    done
    
    echo -e "${BLUE}📋 Found ${#services[@]} services to audit:${NC}"
    printf "  %s\n" "${services[@]}"
    echo ""
    
    # Audit each service
    local total_services=${#services[@]}
    local compliant_services=0
    local non_compliant_services=0
    
    for service_name in "${services[@]}"; do
        local service_dir="$SERVICES_DIR/$service_name"
        if audit_service "$service_name" "$service_dir"; then
            ((compliant_services++))
        else
            ((non_compliant_services++))
        fi
    done
    
    # Create master report
    create_master_report "${services[@]}"
    
    # Generate summary report
    echo ""
    echo "🎯 COMPREHENSIVE AUDIT COMPLETE - SUMMARY REPORT"
    echo "================================================="
    echo -e "Total Services Audited: ${BLUE}$total_services${NC}"
    echo -e "Compliant Services: ${GREEN}$compliant_services${NC}"
    echo -e "Non-Compliant Services: ${RED}$non_compliant_services${NC}"
    echo ""
    echo -e "📊 Overall Compliance Rate: ${BLUE}$(( (compliant_services * 100) / total_services ))%${NC}"
    echo ""
    echo "📁 Individual reports saved to: $REPORTS_DIR/"
    echo "📋 Master report saved to: $MASTER_REPORT"
    echo ""
    
    if [[ $non_compliant_services -eq 0 ]]; then
        echo -e "${GREEN}🎉 ALL SERVICES ARE COMPLIANT!${NC}"
    else
        echo -e "${YELLOW}⚠️ $non_compliant_services services need attention${NC}"
        echo "Review individual reports for specific requirements"
    fi
    
    echo ""
    echo -e "${CYAN}🔗 View Master Report: $MASTER_REPORT${NC}"
}

# Run main function
main "$@"
