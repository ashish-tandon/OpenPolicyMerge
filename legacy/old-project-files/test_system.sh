#!/bin/bash

echo "🧪 Testing OpenPolicy Merge System"
echo "=================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to test endpoint
test_endpoint() {
    local name=$1
    local url=$2
    local expected_status=$3
    
    echo -n "Testing $name... "
    
    if command -v curl &> /dev/null; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
        if [ "$response" = "$expected_status" ]; then
            echo -e "${GREEN}✅ PASS${NC}"
            return 0
        else
            echo -e "${RED}❌ FAIL (Status: $response, Expected: $expected_status)${NC}"
            return 1
        fi
    else
        echo -e "${YELLOW}⚠️  SKIP (curl not available)${NC}"
        return 0
    fi
}

# Function to test Docker service
test_service() {
    local service=$1
    echo -n "Testing Docker service $service... "
    
    if docker-compose ps | grep -q "$service.*Up"; then
        echo -e "${GREEN}✅ RUNNING${NC}"
        return 0
    else
        echo -e "${RED}❌ NOT RUNNING${NC}"
        return 1
    fi
}

echo ""
echo "🔍 Checking Docker services..."
echo "-----------------------------"

# Test all Docker services
services=("api" "django" "laravel" "represent" "frontend" "postgres" "redis" "opa" "nginx" "prometheus" "grafana")
all_services_running=true

for service in "${services[@]}"; do
    if ! test_service "$service"; then
        all_services_running=false
    fi
done

echo ""
echo "🌐 Testing API endpoints..."
echo "--------------------------"

# Test API endpoints
all_apis_working=true

# Test main API health endpoint
if ! test_endpoint "Main API Health" "http://localhost:8080/api/v1/health" "200"; then
    all_apis_working=false
fi

# Test frontend
if ! test_endpoint "Web Frontend" "http://localhost:3000" "200"; then
    all_apis_working=false
fi

# Test Django backend
if ! test_endpoint "Django Backend" "http://localhost:8000" "200"; then
    all_apis_working=false
fi

# Test Laravel backend
if ! test_endpoint "Laravel Backend" "http://localhost:8001" "200"; then
    all_apis_working=false
fi

# Test Represent service
if ! test_endpoint "Represent Service" "http://localhost:8002" "200"; then
    all_apis_working=false
fi

# Test Nginx proxy
if ! test_endpoint "Nginx Proxy" "http://localhost:80" "200"; then
    all_apis_working=false
fi

echo ""
echo "📊 Testing monitoring services..."
echo "--------------------------------"

# Test monitoring services
all_monitoring_working=true

if ! test_endpoint "Prometheus" "http://localhost:9090" "200"; then
    all_monitoring_working=false
fi

if ! test_endpoint "Grafana" "http://localhost:3001" "200"; then
    all_monitoring_working=false
fi

echo ""
echo "📋 System Test Summary"
echo "======================"

if [ "$all_services_running" = true ] && [ "$all_apis_working" = true ] && [ "$all_monitoring_working" = true ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED!${NC}"
    echo ""
    echo "✅ Docker services: RUNNING"
    echo "✅ API endpoints: WORKING"
    echo "✅ Monitoring: OPERATIONAL"
    echo ""
    echo "🚀 OpenPolicy Merge is fully operational!"
    echo ""
    echo "📱 Access your platform:"
    echo "   • Web Frontend: http://localhost:3000"
    echo "   • API Server: http://localhost:8080"
    echo "   • Monitoring: http://localhost:3001"
    echo ""
    echo "✨ Happy exploring Canadian civic data!"
else
    echo -e "${RED}❌ SOME TESTS FAILED${NC}"
    echo ""
    if [ "$all_services_running" = false ]; then
        echo "❌ Docker services: Some services not running"
    fi
    if [ "$all_apis_working" = false ]; then
        echo "❌ API endpoints: Some endpoints not responding"
    fi
    if [ "$all_monitoring_working" = false ]; then
        echo "❌ Monitoring: Some monitoring services not working"
    fi
    echo ""
    echo "🔧 Troubleshooting tips:"
    echo "   • Check Docker status: docker-compose ps"
    echo "   • View service logs: docker-compose logs -f [service-name]"
    echo "   • Restart services: docker-compose restart"
    echo "   • Full restart: docker-compose down && docker-compose up -d"
fi

echo ""
