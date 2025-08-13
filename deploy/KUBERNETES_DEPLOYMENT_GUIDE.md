# 🚀 OpenPolicy Platform - Kubernetes Deployment Guide

## 🎯 **OVERVIEW**
This guide will walk you through deploying the OpenPolicy platform to Kubernetes, demonstrating the complete orchestration engine in action.

## 📋 **PREREQUISITES CHECKLIST**

### **1. Docker Desktop**
```bash
# Verify Docker is running
docker --version
docker ps

# If Docker is not responding, try:
# 1. Restart Docker Desktop
# 2. Wait for it to fully initialize
# 3. Check Docker Desktop status in system tray
```

### **2. Kubernetes Tools**
```bash
# Verify kubectl is installed
kubectl version --client

# Verify kind is installed (we installed it earlier)
./kind version
```

## 🏗️ **STEP-BY-STEP DEPLOYMENT**

### **Step 1: Create Local Kubernetes Cluster**

```bash
# Create the OpenPolicy platform cluster
./kind create cluster --name openpolicy-platform --config - <<EOF
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
- role: control-plane
  extraPortMappings:
  - containerPort: 80
    hostPort: 80
    protocol: TCP
  - containerPort: 443
    hostPort: 443
    protocol: TCP
- role: worker
- role: worker
EOF

# Verify cluster creation
kubectl cluster-info --context kind-openpolicy-platform
kubectl get nodes
```

### **Step 2: Deploy OpenPolicy Platform**

```bash
# Create namespace
kubectl create namespace openpolicy-platform

# Apply platform configuration
kubectl apply -f deploy/k8s/openpolicy-platform.yaml

# Verify deployment
kubectl get pods -n openpolicy-platform
kubectl get services -n openpolicy-platform
kubectl get deployments -n openpolicy-platform
```

### **Step 3: Monitor Deployment Progress**

```bash
# Watch pods starting up
kubectl get pods -n openpolicy-platform -w

# Check pod status
kubectl describe pods -n openpolicy-platform

# Check service endpoints
kubectl get endpoints -n openpolicy-platform
```

### **Step 4: Access Services**

```bash
# Port forward to API Gateway
kubectl port-forward svc/api-gateway -n openpolicy-platform 9001:9001

# In another terminal, test the service
curl http://localhost:9001/healthz

# Port forward to Error Reporting Service
kubectl port-forward svc/error-reporting-service -n openpolicy-platform 9024:9024

# Test error reporting service
curl http://localhost:9024/healthz
```

## 🔍 **VERIFICATION COMMANDS**

### **Check Service Health**
```bash
# Check all services
kubectl get pods -n openpolicy-platform -o wide

# Check service logs
kubectl logs -f deployment/api-gateway -n openpolicy-platform
kubectl logs -f deployment/error-reporting-service -n openpolicy-platform

# Check service endpoints
kubectl get endpoints -n openpolicy-platform
```

### **Check Resource Usage**
```bash
# Check resource allocation
kubectl top pods -n openpolicy-platform
kubectl top nodes

# Check resource limits
kubectl describe pods -n openpolicy-platform | grep -A 10 "Limits:"
```

## 🚨 **TROUBLESHOOTING**

### **Common Issues and Solutions**

#### **1. Docker Connection Issues**
```bash
# If you see "Cannot connect to Docker daemon":
# 1. Restart Docker Desktop
# 2. Wait for full initialization
# 3. Check Docker Desktop status
# 4. Try: docker system prune -a
```

#### **2. Pod Startup Issues**
```bash
# Check pod events
kubectl describe pod <pod-name> -n openpolicy-platform

# Check pod logs
kubectl logs <pod-name> -n openpolicy-platform

# Check pod status
kubectl get events -n openpolicy-platform --sort-by='.lastTimestamp'
```

#### **3. Service Connection Issues**
```bash
# Check service endpoints
kubectl get endpoints -n openpolicy-platform

# Check service configuration
kubectl describe service <service-name> -n openpolicy-platform

# Test service connectivity
kubectl exec -it <pod-name> -n openpolicy-platform -- curl <service-url>
```

## 📊 **EXPECTED RESULTS**

### **After Successful Deployment**
- **25 services** running in Kubernetes
- **API Gateway** accessible on port 9001
- **Error Reporting Service** operational on port 9024
- **All services** responding to health checks
- **Kubernetes dashboard** showing healthy pods

### **Service Status Indicators**
```bash
# All pods should show "Running" status
kubectl get pods -n openpolicy-platform

# All services should have endpoints
kubectl get endpoints -n openpolicy-platform

# Health checks should pass
curl http://localhost:9001/healthz  # API Gateway
curl http://localhost:9024/healthz  # Error Reporting
```

## 🚀 **NEXT STEPS AFTER DEPLOYMENT**

### **1. Activate CI/CD Pipeline**
```bash
# Push changes to trigger GitHub Actions
git add .
git commit -m "feat: deploy OpenPolicy platform to Kubernetes"
git push origin main
```

### **2. Set Up Monitoring**
```bash
# Install Prometheus and Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace
```

### **3. Implement Service Mesh**
```bash
# Install Istio
istioctl install --set profile=demo -y

# Enable Istio injection
kubectl label namespace openpolicy-platform istio-injection=enabled
```

## 📋 **DEPLOYMENT CHECKLIST**

### **Pre-Deployment**
- [ ] Docker Desktop running and accessible
- [ ] kubectl configured and working
- [ ] kind installed and working
- [ ] All OpenPolicy files in place

### **Deployment**
- [ ] Kubernetes cluster created successfully
- [ ] Namespace created
- [ ] Platform configuration applied
- [ ] All pods starting up
- [ ] Services accessible

### **Post-Deployment**
- [ ] All pods running
- [ ] Health checks passing
- [ ] Services responding
- [ ] Monitoring working
- [ ] CI/CD pipeline active

## 🎯 **SUCCESS METRICS**

### **Technical Metrics**
- **Pod Status**: 100% Running
- **Service Health**: All endpoints responding
- **Resource Usage**: Within limits
- **Response Time**: <2 seconds

### **Business Metrics**
- **Deployment Time**: <10 minutes
- **Service Availability**: 100%
- **Error Rate**: <1%
- **Performance**: Meeting benchmarks

## 🔧 **USEFUL COMMANDS REFERENCE**

```bash
# Cluster management
kubectl cluster-info
kubectl get nodes
kubectl get namespaces

# Pod management
kubectl get pods -n openpolicy-platform
kubectl describe pod <pod-name> -n openpolicy-platform
kubectl logs <pod-name> -n openpolicy-platform

# Service management
kubectl get services -n openpolicy-platform
kubectl get endpoints -n openpolicy-platform
kubectl describe service <service-name> -n openpolicy-platform

# Deployment management
kubectl get deployments -n openpolicy-platform
kubectl rollout status deployment/<deployment-name> -n openpolicy-platform
kubectl scale deployment <deployment-name> --replicas=3 -n openpolicy-platform

# Resource monitoring
kubectl top pods -n openpolicy-platform
kubectl top nodes
kubectl get events -n openpolicy-platform

# Troubleshooting
kubectl exec -it <pod-name> -n openpolicy-platform -- /bin/bash
kubectl port-forward svc/<service-name> -n openpolicy-platform <local-port>:<service-port>
```

---

**Status**: 🚀 **READY FOR KUBERNETES DEPLOYMENT**

**Next Action**: Follow the steps above to deploy your OpenPolicy platform to Kubernetes!

**Expected Outcome**: A fully operational, enterprise-grade microservices platform running in Kubernetes with full orchestration capabilities! 🎉
