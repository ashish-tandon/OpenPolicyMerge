# COMPLETE OPENPOLICY PLATFORM PORT ASSIGNMENT PLAN

## 🎯 **PORT RANGES BY SERVICE TIER**

### **CORE INFRASTRUCTURE (9001-9012)**
- **9001**: API Gateway
- **9002**: Search Service  
- **9003**: Auth Service
- **9004**: Notification Service
- **9005**: Config Service
- **9006**: Health Service
- **9007**: Monitoring Service
- **9008**: Scraper Service
- **9009**: ETL Service
- **9010**: Analytics Service
- **9011**: Audit Service
- **9012**: OPA Service

### **NEW INFRASTRUCTURE (9013-9018)**
- **9013**: MCP Service
- **9014**: Plotly Service
- **9015**: Database Service (PostgreSQL)
- **9016**: Cache Service (Redis)
- **9017**: Queue Service (RabbitMQ)
- **9018**: Storage Service

### **FRONTEND & LEGACY (9019-9023)**
- **9019**: Web Frontend
- **9020**: Mobile API
- **9021**: Admin Dashboard
- **9022**: Legacy Django
- **9023**: OP Import

### **MONITORING & ERROR REPORTING (9024-9025)**
- **9024**: Error Reporting Service
- **9025**: Service Registry

### **SPECIAL PORTS (RESERVED)**
- **5432**: PostgreSQL (standard)
- **6379**: Redis (standard)
- **5672**: RabbitMQ (standard)
- **15672**: RabbitMQ Management
- **9090**: Prometheus
- **3000**: Grafana

## 🚀 **DEPLOYMENT STRATEGY**

### **PHASE 1: INFRASTRUCTURE (COMPLETED)**
- ✅ PostgreSQL (5432)
- ✅ Redis (6379)
- ✅ RabbitMQ (5672/15672)
- ✅ Prometheus (9090)
- ✅ Grafana (3000)

### **PHASE 2: CORE SERVICES (IN PROGRESS)**
- 🔄 API Gateway (9001)
- 🔄 Error Reporting (9024)
- 🔄 Policy Service (9001) - PORT CONFLICT!
- 🔄 Search Service (9002)
- 🔄 Notification Service (9004)

### **PHASE 3: ALL REMAINING SERVICES (NEXT)**
- ⏳ Auth Service (9003)
- ⏳ Config Service (9005)
- ⏳ Health Service (9006)
- ⏳ Monitoring Service (9007)
- ⏳ Scraper Service (9008)
- ⏳ ETL Service (9009)
- ⏳ Analytics Service (9010)
- ⏳ Audit Service (9011)
- ⏳ OPA Service (9012)
- ⏳ MCP Service (9013)
- ⏳ Plotly Service (9014)
- ⏳ Web Frontend (9019)
- ⏳ Mobile API (9020)
- ⏳ Admin Dashboard (9021)
- ⏳ Legacy Django (9022)
- ⏳ OP Import (9023)

## ⚠️ **CRITICAL ISSUES IDENTIFIED**

### **PORT CONFLICT ALERT**
- **Policy Service** is trying to use port 9001 (same as API Gateway)
- **All business services** are running on port 8000 instead of assigned ports

### **SOLUTION**
1. **API Gateway**: Keep port 9001
2. **Policy Service**: Move to port 9003 (was assigned to Auth Service)
3. **Auth Service**: Move to port 9013 (was assigned to MCP Service)
4. **MCP Service**: Move to port 9016 (was assigned to Cache Service)
5. **Cache Service**: Move to port 9017 (was assigned to Queue Service)
6. **Queue Service**: Move to port 9018 (was assigned to Storage Service)
7. **Storage Service**: Move to port 9025 (was assigned to Service Registry)

## 🔧 **IMMEDIATE ACTION PLAN**

1. **Fix port conflicts** in business services
2. **Deploy ALL 25 services** in one go
3. **Use local deployment approach** (like we did before)
4. **Maintain port consistency** across local and K8s
5. **Test everything** before moving to production

## 📊 **DEPLOYMENT STATUS**

- **Infrastructure**: 5/5 ✅
- **Core Services**: 3/5 🔄 (with port issues)
- **Business Services**: 0/15 ⏳
- **Frontend Services**: 0/5 ⏳
- **Total Deployed**: 8/25 (32%)
- **Target**: 25/25 (100%)
