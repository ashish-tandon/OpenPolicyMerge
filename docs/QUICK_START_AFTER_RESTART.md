# 🚀 **QUICK START GUIDE - AFTER DEVICE RESTART**
## OpenPolicy Platform - Planned Deployment Execution

---

## 📋 **IMMEDIATE ACTIONS AFTER RESTART**

### **1. Verify Cluster Status** ✅
```bash
# Check if cluster is running
kubectl cluster-info

# Verify namespace exists
kubectl get namespace openpolicy-platform

# Check current resource availability
kubectl describe nodes | grep -A 10 "Allocated resources"
```

**Expected Result**: Clean cluster with 8Gi+ memory available

---

## 🎯 **DEPLOYMENT EXECUTION OPTIONS**

### **Option A: Complete Automated Deployment** 🚀
**Recommended for first-time deployment**
```bash
# Navigate to project directory
cd /Users/ashishtandon/Github/OpenPolicyMerge

# Execute complete deployment (all 5 phases)
./scripts/deploy_all_phases.sh
```

**Duration**: 60-90 minutes  
**Outcome**: All 26 services operational  
**Monitoring**: Automated validation and health checks

---

### **Option B: Phase-by-Phase Deployment** 📊
**Recommended for controlled deployment**
```bash
# Navigate to project directory
cd /Users/ashishtandon/Github/OpenPolicyMerge

# Phase 1: Infrastructure Foundation
./scripts/deploy_phase1.sh

# Phase 2: Core Business Services
kubectl apply -f deploy/k8s/dev/additional-services.yaml

# Phase 3: Operational Services
kubectl apply -f deploy/k8s/dev/core-business-services-fixed.yaml

# Phase 4: UI Services
kubectl apply -f deploy/k8s/dev/api-gateway.yaml

# Phase 5: Utility Services
kubectl apply -f deploy/k8s/dev/additional-services.yaml
```

**Duration**: 90-120 minutes  
**Outcome**: Controlled service deployment  
**Monitoring**: Manual validation between phases

---

### **Option C: Individual Service Deployment** 🔧
**Recommended for troubleshooting specific services**
```bash
# Navigate to project directory
cd /Users/ashishtandon/Github/OpenPolicyMerge

# Deploy individual services as needed
kubectl apply -f deploy/k8s/dev/postgresql.yaml
kubectl apply -f deploy/k8s/dev/redis.yaml
kubectl apply -f deploy/k8s/dev/rabbitmq.yaml
# ... continue with other services
```

**Duration**: Variable  
**Outcome**: Selective service deployment  
**Monitoring**: Manual validation per service

---

## 📊 **REAL-TIME MONITORING**

### **Start Resource Monitoring** 📈
```bash
# Navigate to project directory
cd /Users/ashishtandon/Github/OpenPolicyMerge

# Start real-time monitoring dashboard
./scripts/monitor_resources.sh
```

**Features**:
- Real-time cluster resource usage
- Service health status
- Deployment phase progress
- Performance metrics
- Recent events and errors

---

## 🔍 **DEPLOYMENT VALIDATION**

### **Phase 1 Success Criteria** ✅
- **postgresql**: 1/1 Running, 1Gi memory
- **scraper-service**: 2/2 Running, 1Gi memory each
- **redis**: 1/1 Running, 512Mi memory
- **rabbitmq**: 1/1 Running, 512Mi memory
- **Resource Usage**: <40% memory

### **Phase 2 Success Criteria** ✅
- **9 business services**: All Running, 128Mi memory each
- **Resource Usage**: <60% memory
- **Dependencies**: All infrastructure services healthy

### **Phase 3 Success Criteria** ✅
- **6 operational services**: All Running, 128Mi memory each
- **Resource Usage**: <70% memory
- **Monitoring**: All services providing metrics

### **Phase 4 Success Criteria** ✅
- **3 UI services**: All Running, 128Mi memory each
- **Resource Usage**: <75% memory
- **Accessibility**: All services accessible via API

### **Phase 5 Success Criteria** ✅
- **4 utility services**: All Running, 128Mi memory each
- **Resource Usage**: <80% memory
- **Functionality**: All services operational

---

## 🚨 **TROUBLESHOOTING COMMANDS**

### **Check Service Status** 🔍
```bash
# Overall pod status
kubectl get pods -n openpolicy-platform

# Service-specific status
kubectl get pods -n openpolicy-platform -l app=postgresql
kubectl get pods -n openpolicy-platform -l app=scraper-service

# Detailed pod information
kubectl describe pod <pod-name> -n openpolicy-platform
```

### **Check Resource Usage** 📊
```bash
# Cluster resource allocation
kubectl describe nodes | grep -A 10 "Allocated resources"

# Pod resource requests
kubectl get pods -n openpolicy-platform -o custom-columns="NAME:.metadata.name,CPU_REQ:.spec.containers[0].resources.requests.cpu,MEMORY_REQ:.spec.containers[0].resources.requests.memory"
```

### **Check Service Logs** 📝
```bash
# Service logs
kubectl logs <pod-name> -n openpolicy-platform

# Follow logs in real-time
kubectl logs -f <pod-name> -n openpolicy-platform

# Previous container logs (if restarted)
kubectl logs <pod-name> -n openpolicy-platform --previous
```

### **Check Service Health** ❤️
```bash
# Port forward to service
kubectl port-forward <pod-name> -n openpolicy-platform <local-port>:<service-port>

# Test health endpoint
curl http://localhost:<local-port>/healthz
curl http://localhost:<local-port>/readyz
```

---

## 📋 **DEPLOYMENT CHECKLIST**

### **Pre-Deployment** ✅
- [ ] Device restarted and stable
- [ ] Kubernetes cluster running
- [ ] Namespace exists
- [ ] All service images built
- [ ] Deployment scripts executable
- [ ] Resource monitoring ready

### **Phase 1: Infrastructure** ✅
- [ ] postgresql deployed and healthy
- [ ] scraper-service deployed and healthy
- [ ] redis deployed and healthy
- [ ] rabbitmq deployed and healthy
- [ ] Resource usage <40%

### **Phase 2: Business Services** ✅
- [ ] Data services deployed and healthy
- [ ] Business logic services deployed and healthy
- [ ] Security services deployed and healthy
- [ ] Resource usage <60%

### **Phase 3: Operational Services** ✅
- [ ] Monitoring services deployed and healthy
- [ ] Intelligence services deployed and healthy
- [ ] Resource usage <70%

### **Phase 4: UI Services** ✅
- [ ] API gateway deployed and healthy
- [ ] Notification service deployed and healthy
- [ ] MCP service deployed and healthy
- [ ] Resource usage <75%

### **Phase 5: Utility Services** ✅
- [ ] Cache service deployed and healthy
- [ ] Web interface deployed and healthy
- [ ] Admin interface deployed and healthy
- [ ] Mobile API deployed and healthy
- [ ] Resource usage <80%

### **Final Validation** ✅
- [ ] All 26 services running
- [ ] Resource usage <80%
- [ ] All health checks passing
- [ ] Platform functionality verified

---

## 🎯 **EXPECTED OUTCOMES**

### **Immediate (After Phase 1)**
- **Platform Status**: STABLE infrastructure
- **Services Running**: 4/26 (15%)
- **Resource Usage**: <40% memory
- **Next Action**: Deploy Phase 2

### **Short-term (After Phase 2)**
- **Platform Status**: FUNCTIONAL business services
- **Services Running**: 13/26 (50%)
- **Resource Usage**: <60% memory
- **Next Action**: Deploy Phase 3

### **Medium-term (After Phase 3)**
- **Platform Status**: OPERATIONAL monitoring
- **Services Running**: 19/26 (73%)
- **Resource Usage**: <70% memory
- **Next Action**: Deploy Phase 4

### **Long-term (After Phase 5)**
- **Platform Status**: FULLY OPERATIONAL
- **Services Running**: 26/26 (100%)
- **Resource Usage**: <80% memory
- **Next Action**: Platform testing and optimization

---

## 🚀 **NEXT STEPS AFTER DEPLOYMENT**

### **1. Platform Testing** 🧪
- Test all service endpoints
- Validate data flow between services
- Check monitoring and alerting
- Verify user access and permissions

### **2. Performance Optimization** ⚡
- Monitor resource usage patterns
- Optimize service configurations
- Implement auto-scaling if needed
- Fine-tune performance parameters

### **3. Service Consolidation** 🔄
- Begin planning for service consolidation
- Design hub architectures
- Implement gradual consolidation
- Monitor resource efficiency improvements

---

## 📞 **SUPPORT & ESCALATION**

### **If Deployment Fails** 🚨
1. **Check logs**: Review deployment logs and service logs
2. **Resource issues**: Verify cluster has sufficient resources
3. **Service dependencies**: Ensure required services are running
4. **Configuration errors**: Validate YAML files and configurations

### **If Services Unhealthy** ❌
1. **Check pod status**: `kubectl get pods -n openpolicy-platform`
2. **Review logs**: `kubectl logs <pod-name> -n openpolicy-platform`
3. **Check events**: `kubectl get events -n openpolicy-platform`
4. **Validate health endpoints**: Test service health checks

### **If Resource Usage High** 📊
1. **Monitor resources**: Use monitoring script
2. **Check pod resources**: Verify resource requests/limits
3. **Scale services**: Adjust replica counts if needed
4. **Optimize configurations**: Review and update resource allocations

---

*This quick start guide provides everything needed to successfully deploy the OpenPolicy platform after the device restart. Follow the deployment options based on your preference and requirements.* 🚀

**Deployment Status**: Ready for execution  
**Expected Outcome**: 26 services operational with <80% resource usage  
**Platform Version**: 2.0 (Planned Deployment Ready)
