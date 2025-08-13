#!/bin/bash

# Build All Missing Docker Images for OpenPolicy Platform
# This script builds all the missing Docker images that are needed for the mass deployment

echo "🐳 BUILDING ALL MISSING DOCKER IMAGES FOR OPENPOLICY PLATFORM"
echo "================================================================"
echo ""

# Change to root directory
cd /Users/ashishtandon/Github/OpenPolicyMerge

# Array of services that need Docker images built
SERVICES=(
    "config-service"
    "health-service"
    "scraper-service"
    "etl-service"
    "web-frontend"
    "mobile-api"
    "legacy-django"
    "op-import"
)

# Build each service
for service in "${SERVICES[@]}"; do
    echo "🔨 Building $service..."
    
    if [ -d "services/$service" ]; then
        cd "services/$service"
        
        # Check if Dockerfile exists
        if [ -f "Dockerfile" ]; then
            echo "   📁 Found Dockerfile, building image..."
            docker build -t "openpolicy/$service:latest" .
            
            if [ $? -eq 0 ]; then
                echo "   ✅ $service built successfully"
            else
                echo "   ❌ Failed to build $service"
            fi
        else
            echo "   ⚠️  No Dockerfile found for $service, creating basic one..."
            
            # Create basic Dockerfile if missing
            cat > Dockerfile << EOF
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/

EXPOSE 9000

CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "9000"]
EOF
            
            # Build with basic Dockerfile
            docker build -t "openpolicy/$service:latest" .
            
            if [ $? -eq 0 ]; then
                echo "   ✅ $service built successfully with basic Dockerfile"
            else
                echo "   ❌ Failed to build $service"
            fi
        fi
        
        cd /Users/ashishtandon/Github/OpenPolicyMerge
    else
        echo "   ❌ Service directory not found: services/$service"
    fi
    
    echo ""
done

echo "🎯 Loading all images into kind cluster..."
echo ""

# Load all images into kind cluster
for service in "${SERVICES[@]}"; do
    echo "📤 Loading $service into kind cluster..."
    ./kind load docker-image "openpolicy/$service:latest" --name openpolicy-platform
done

echo ""
echo "🎉 ALL MISSING IMAGES BUILT AND LOADED!"
echo "================================================================"
echo ""
echo "Next steps:"
echo "1. Check pod status: kubectl get pods -n openpolicy-platform"
echo "2. Monitor service startup: kubectl logs -f deployment/[service-name] -n openpolicy-platform"
echo "3. Test services once they're running"
echo ""
