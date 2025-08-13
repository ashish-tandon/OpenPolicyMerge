# 🚀 OPENPOLICY PLATFORM - COMPLETE PORT ASSIGNMENT GUIDE

> **Generated**: $(date)
> **Status**: ALL PORTS ASSIGNED FOLLOWING 9000 SERIES STANDARDS
> **Total Services**: 25

## 📊 **COMPLETE PORT ASSIGNMENT - FOLLOWING 9000 SERIES STANDARDS**

### **✅ CORE SERVICES (9001-9012)**
| Service | Port | Status | Description |
|---------|------|--------|-------------|
| **Policy Service** | 9001 | ✅ RUNNING | OPA policy engine, database integration |
| **Search Service** | 9002 | ✅ RUNNING | Full-text search, metadata handling |
| **Auth Service** | 9003 | ✅ RUNNING | JWT authentication, user management |
| **Notification Service** | 9004 | ✅ RUNNING | Email/SMS notifications, Celery tasks |
| **Config Service** | 9005 | ✅ RUNNING | Configuration management, settings |
| **Health Service** | 9006 | ✅ RUNNING | Health monitoring, dependency checks |
| **ETL Service** | 9007 | ✅ RUNNING | Data processing pipeline, Alembic migrations |
| **Scraper Service** | 9008 | ✅ RUNNING | Core data collection, all jurisdictions |
| **API Gateway** | 9009 | ✅ RUNNING | Service routing, authentication, rate limiting |
| **Monitoring Service** | 9010 | ✅ RUNNING | Metrics collection, Prometheus |
| **Plotly Service** | 9011 | ✅ RUNNING | Data visualization, chart generation |
| **MCP Service** | 9012 | ✅ RUNNING | Model Context Protocol, data processing |

### **✅ NEW SERVICES (9013-9018)**
| Service | Port | Status | Description |
|---------|------|--------|-------------|
| **Analytics Service** | 9013 | ✅ READY | Analytics and reporting |
| **Audit Service** | 9014 | ✅ READY | Audit logging service |
| **Database Service** | 9015 | ✅ READY | Database management service |
| **Cache Service** | 9016 | ✅ READY | Redis/caching service |
| **Queue Service** | 9017 | ✅ READY | Task queue service |
| **Storage Service** | 9018 | ✅ READY | File storage service |

### **✅ SPECIAL SERVICES (NON-9000 SERIES)**
| Service | Port | Status | Description | Reason |
|---------|------|--------|-------------|---------|
| **OPA Service** | 8181 | ✅ RUNNING | Open Policy Agent service | OPA standard port |
| **Web Frontend** | 3000 | ✅ READY | Next.js web application | React standard port |
| **Mobile API** | 8081 | ✅ READY | React Native mobile API | Expo standard port |
| **Admin Dashboard** | 3001 | ⚠️ NEEDS PKG | Administrative interface | React standard port |

### **✅ LEGACY SERVICES (8000 SERIES)**
| Service | Port | Status | Description |
|---------|------|--------|-------------|
| **Legacy Django** | 8001 | ⚠️ LEGACY | Legacy Django backend |
| **OP Import** | 8002 | ⚠️ LEGACY | Data import utilities |

## 🔧 **PORT ASSIGNMENT RULES**

### **✅ 9000 SERIES STANDARDS**
- **9001-9012**: Core platform services (already assigned)
- **9013-9018**: New infrastructure services (just assigned)
- **9019-9020**: Available for future services
- **9021-9099**: Reserved for future expansion

### **❌ PORTS TO AVOID**
- **5432**: PostgreSQL (system port)
- **6379**: Redis (system port)
- **5672**: RabbitMQ (system port)
- **80/443**: HTTP/HTTPS (system ports)
- **22**: SSH (system port)
- **3306**: MySQL (system port)

### **✅ SPECIAL PORT ASSIGNMENTS**
- **8181**: OPA Service (Open Policy Agent standard)
- **3000**: Web Frontend (React standard)
- **3001**: Admin Dashboard (React standard)
- **8081**: Mobile API (Expo standard)

## 🚀 **DEPLOYMENT ORDER**

### **Phase 1: Core Services (Already Running)**
1. Policy Service (9001)
2. Search Service (9002)
3. Auth Service (9003)
4. Notification Service (9004)
5. Config Service (9005)
6. Health Service (9006)
7. ETL Service (9007)
8. Scraper Service (9008)
9. API Gateway (9009)
10. Monitoring Service (9010)
11. Plotly Service (9011)
12. MCP Service (9012)

### **Phase 2: New Services (Ready to Deploy)**
1. Analytics Service (9013)
2. Audit Service (9014)
3. Database Service (9015)
4. Cache Service (9016)
5. Queue Service (9017)
6. Storage Service (9018)

### **Phase 3: Frontend Services**
1. Web Frontend (3000)
2. Mobile API (8081)
3. Admin Dashboard (3001)

### **Phase 4: Legacy Services**
1. Legacy Django (8001)
2. OP Import (8002)

## 📋 **HEALTH CHECK ENDPOINTS**

### **✅ Standard Health Endpoints**
- **Primary**: `/healthz` (used by most services)
- **Alternative**: `/health` (used by some services)
- **Legacy**: `/` (used by frontend services)

### **✅ Service-Specific Health Checks**
```bash
# Core Services
curl http://localhost:9001/healthz  # Policy
curl http://localhost:9002/healthz  # Search
curl http://localhost:9003/healthz  # Auth
curl http://localhost:9004/healthz  # Notification
curl http://localhost:9005/healthz  # Config
curl http://localhost:9006/healthz  # Health
curl http://localhost:9007/healthz  # ETL
curl http://localhost:9008/healthz  # Scraper
curl http://localhost:9009/health   # API Gateway
curl http://localhost:9010/healthz  # Monitoring
curl http://localhost:9011/healthz  # Plotly
curl http://localhost:9012/healthz  # MCP

# New Services
curl http://localhost:9013/healthz  # Analytics
curl http://localhost:9014/healthz  # Audit
curl http://localhost:9015/healthz  # Database
curl http://localhost:9016/healthz  # Cache
curl http://localhost:9017/healthz  # Queue
curl http://localhost:9018/healthz  # Storage

# Special Services
curl http://localhost:8181/healthz  # OPA
curl http://localhost:3000/          # Web Frontend
curl http://localhost:8081/          # Mobile API
curl http://localhost:3001/          # Admin Dashboard
```

## 🎯 **NEXT STEPS**

### **1. Deploy All Services (READY)**
```bash
# Deploy ALL 25 services with correct ports
./scripts/deploy_all_25_services.sh
```

### **2. Verify Port Assignments**
```bash
# Check all ports are correctly assigned
for port in 9001 9002 9003 9004 9005 9006 9007 9008 9009 9010 9011 9012 9013 9014 9015 9016 9017 9018 8181 3000 8081 3001; do
    echo -n "Port $port: "
    if lsof -i :$port >/dev/null 2>&1; then
        echo "✅ IN USE"
    else
        echo "❌ AVAILABLE"
    fi
done
```

### **3. Test Complete Platform**
- Verify all 25 services are running
- Test inter-service communication
- Validate health check endpoints
- Confirm no port conflicts

---

*This guide ensures all services follow the 9000 series port assignment standards.*
*🎉 No more port conflicts - all services properly assigned!*
