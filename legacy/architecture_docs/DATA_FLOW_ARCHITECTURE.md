# 🔄 **DATA FLOW ARCHITECTURE - OPENPOLICY PLATFORM**

## 📋 **OVERVIEW**

This document provides a comprehensive overview of the data flow architecture in the OpenPolicy platform, including how data moves from scrapers through the MCP service to the database, and how it's organized and stored.

---

## 🏗️ **HIGH-LEVEL ARCHITECTURE**

### **System Architecture Overview**
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              USER INTERFACE LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   MAIN      │  │    ADMIN    │  │   MOBILE    │  │   PLOTLY    │              │
│  │   WEB APP   │  │  DASHBOARD  │  │     API     │  │   SERVICE   │              │
│  │ Port: 3000  │  │ Port: 8002  │  │ Port: 8002  │  │ Port: 8004  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              API GATEWAY LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────────────────────────────────────────┐    │
│  │                        API GATEWAY SERVICE                                  │    │
│  │                           Port: 8000                                        │    │
│  │                                                                             │    │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │    │
│  │  │   ROUTING   │  │AUTHENTICATION│  │RATE LIMITING│  │   MONITORING│        │    │
│  │  │             │  │             │  │             │  │             │        │    │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘        │    │
│  └─────────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              MICROSERVICES LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │     ETL     │  │     GO      │  │   HEALTH    │  │     OPA     │              │
│  │   SERVICE   │  │    API      │  │   SERVICE   │  │   SERVICE   │              │
│  │ Port: 8003  │  │ Port: 8080  │  │ Port: 8007  │  │ Port: 8181  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘              │
│                                                                                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │   SCRAPER   │  │     MCP     │  │   MONITOR   │  │   AUTH      │              │
│  │   SERVICE   │  │   SERVICE   │  │   SERVICE   │  │   SERVICE   │              │
│  │ Port: 8005  │  │ Port: 8006  │  │ Port: 8008  │  │ Port: 8009  │              │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              DATA LAYER                                            │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │  SCRAPER    │  │   SERVICE   │  │   CACHE     │  │   MONITOR   │              │
│  │   DATA      │  │   DATABASES │  │   (REDIS)   │  │   DATA      │              │
│  │(PostgreSQL) │  │(PostgreSQL) │  │             │  │(PostgreSQL) │              │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘              │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 **DATA FLOW ARCHITECTURE**

### **Primary Data Flow: Scrapers → MCP → OPA → Database**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SCRAPERS      │───▶│   MCP SERVICE   │───▶│   OPA SERVICE   │───▶│   DATABASE      │
│  (Port 8005)    │    │  (Port 8006)    │    │  (Port 8181)    │    │  (PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
   Raw Data Collection    Data Processing        Policy Validation    Structured Storage
         │                       │                       │                       │
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
   Government Websites    Transform & Validate    Apply Business Rules    Schema-based Storage
```

### **Detailed Data Flow Steps**

#### **Step 1: Data Collection (Scrapers)**
```yaml
scrapers:
  - Collect raw data from government websites
  - Store in temporary storage (Redis/File system)
  - Validate basic data structure
  - Log collection metrics
  - Send data to MCP Service
```

#### **Step 2: Data Processing (MCP Service)**
```yaml
mcp_service:
  - Receive raw data from scrapers
  - Transform data to standard format
  - Validate data quality
  - Apply business rules
  - Prepare for OPA validation
  - Send processed data to OPA Service
```

#### **Step 3: Policy Validation (OPA Service)**
```yaml
opa_service:
  - Validate data against policies
  - Check data integrity
  - Apply business rules
  - Flag violations
  - Approve/reject data
  - Send validated data to Database
```

#### **Step 4: Database Storage**
```yaml
database:
  - Store validated data in appropriate schemas
  - Maintain referential integrity
  - Update indexes
  - Log storage metrics
  - Trigger notifications
```

---

## 🗄️ **DATABASE ARCHITECTURE**

### **Database Organization Strategy**

#### **1. Scraper Data Database (openpolicy)**
```
openpolicy (single database for all scraped data)
├── federal (federal parliamentary data)
│   ├── jurisdictions
│   ├── sessions
│   ├── parties
│   ├── districts
│   ├── bills (separate from other levels)
│   └── votes
├── provincial (provincial legislative data)
│   ├── jurisdictions
│   ├── sessions
│   ├── parties
│   ├── districts
│   ├── bills (separate from other levels)
│   └── votes
├── municipal (municipal council data)
│   ├── jurisdictions
│   ├── sessions
│   ├── wards
│   ├── bills (separate from other levels)
│   └── votes
├── representatives (all levels)
│   ├── politicians
│   └── memberships
├── etl (data processing operations)
│   ├── jobs
│   └── data_sources
└── monitoring (health & metrics)
    ├── health_checks
    └── data_quality
```

#### **2. Service Databases (Separate for Safety)**
```
openpolicy_etl (ETL service database)
openpolicy_plotly (Plotly service database)
openpolicy_go (Go API service database)
openpolicy_scrapers (Scraper service database)
openpolicy_health (Health service database)
openpolicy_auth (Authentication service database)
openpolicy_monitoring (Monitoring service database)
openpolicy_notifications (Notification service database)
openpolicy_config (Configuration service database)
openpolicy_search (Search service database)
openpolicy_policy (Policy service database)
```

### **Why This Architecture?**

#### **Benefits of Separate Service Databases**
- **Safety**: Services can't interfere with each other's data
- **Isolation**: Service failures don't affect other services
- **Scalability**: Each service can scale independently
- **Maintenance**: Easier to backup and maintain individual services

#### **Benefits of Consolidated Scraper Data**
- **Easy Joins**: Cross-jurisdiction queries are simple
- **Data Consistency**: Single source of truth for scraped data
- **Performance**: Better query performance for complex joins
- **Simplified Backup**: One database to backup for all scraped data

---

## 📊 **DATA SCHEMA ORGANIZATION**

### **Federal Level Schema**
```sql
-- Federal parliamentary data
federal.jurisdictions      -- Federal jurisdiction info
federal.sessions          -- Parliamentary sessions
federal.parties           -- Political parties
federal.districts         -- Electoral districts/ridings
federal.bills             -- Federal bills (separate table)
federal.votes             -- Federal voting records
```

### **Provincial Level Schema**
```sql
-- Provincial legislative data
provincial.jurisdictions  -- Provincial jurisdiction info
provincial.sessions       -- Legislative sessions
provincial.parties        -- Political parties
provincial.districts      -- Electoral districts
provincial.bills          -- Provincial bills (separate table)
provincial.votes          -- Provincial voting records
```

### **Municipal Level Schema**
```sql
-- Municipal council data
municipal.jurisdictions   -- Municipal jurisdiction info
municipal.sessions        -- Council sessions
municipal.wards           -- Municipal wards/districts
municipal.bills           -- Municipal bylaws (separate table)
municipal.votes           -- Municipal voting records
```

### **Cross-Level Schema**
```sql
-- Representatives (all levels)
representatives.politicians    -- All politicians
representatives.memberships    -- Political memberships

-- ETL Operations
etl.jobs                      -- ETL job tracking
etl.data_sources              -- Data source management

-- Monitoring
monitoring.health_checks      -- Service health
monitoring.data_quality       -- Data quality metrics
```

---

## 🔗 **DATA RELATIONSHIPS**

### **Cross-Jurisdiction Relationships**
```sql
-- Representatives can serve at multiple levels
representatives.politicians
    ↓
representatives.memberships
    ↓
[federal|provincial|municipal].jurisdictions

-- Bills reference jurisdictions and sessions
[federal|provincial|municipal].bills
    ↓
[federal|provincial|municipal].jurisdictions
[federal|provincial|municipal].sessions

-- Votes reference bills
[federal|provincial|municipal].votes
    ↓
[federal|provincial|municipal].bills
```

### **Data Integrity Constraints**
```sql
-- Foreign key relationships
federal.bills.jurisdiction_id → federal.jurisdictions.id
federal.bills.session_id → federal.sessions.id
federal.bills.sponsor_id → representatives.politicians.id

provincial.bills.jurisdiction_id → provincial.jurisdictions.id
provincial.bills.session_id → provincial.sessions.id
provincial.bills.sponsor_id → representatives.politicians.id

municipal.bills.jurisdiction_id → municipal.jurisdictions.id
municipal.bills.session_id → municipal.sessions.id
municipal.bills.sponsor_id → representatives.politicians.id

-- Cross-level relationships
representatives.memberships.politician_id → representatives.politicians.id
representatives.memberships.jurisdiction_id → [federal|provincial|municipal].jurisdictions.id
```

---

## 🔄 **DATA PROCESSING PIPELINE**

### **1. Data Ingestion Pipeline**
```yaml
ingestion:
  - Scrapers collect data from government websites
  - Data is stored in temporary storage (Redis)
  - Basic validation is performed
  - Data is queued for processing
```

### **2. Data Transformation Pipeline**
```yaml
transformation:
  - MCP Service receives raw data
  - Data is parsed and cleaned
  - Standard format is applied
  - Business rules are validated
  - Data is prepared for storage
```

### **3. Data Validation Pipeline**
```yaml
validation:
  - OPA Service receives processed data
  - Policies are applied
  - Data integrity is checked
  - Business rules are enforced
  - Data is approved or rejected
```

### **4. Data Storage Pipeline**
```yaml
storage:
  - Validated data is stored in appropriate schemas
  - Referential integrity is maintained
  - Indexes are updated
  - Metrics are logged
  - Notifications are triggered
```

---

## 📈 **DATA QUALITY & MONITORING**

### **Data Quality Metrics**
```yaml
completeness:
  - Required fields present
  - Data coverage percentage
  - Missing data identification

accuracy:
  - Data validation rules
  - Cross-reference validation
  - Error rate tracking

timeliness:
  - Data freshness
  - Update frequency
  - Lag time monitoring

consistency:
  - Format standardization
  - Naming conventions
  - Data type consistency
```

### **Monitoring Points**
```yaml
scraper_monitoring:
  - Success rate
  - Error rate
  - Response time
  - Data volume

processing_monitoring:
  - Transformation success rate
  - Validation success rate
  - Processing time
  - Queue depth

storage_monitoring:
  - Database performance
  - Storage success rate
  - Index performance
  - Data integrity
```

---

## 🚨 **ERROR HANDLING & RECOVERY**

### **Error Handling Strategy**
```yaml
scraper_errors:
  - Retry mechanism with exponential backoff
  - Circuit breaker pattern
  - Fallback data sources
  - Graceful degradation

processing_errors:
  - Data validation failures
  - Business rule violations
  - Transformation errors
  - OPA validation failures

storage_errors:
  - Database connection failures
  - Constraint violations
  - Index update failures
  - Referential integrity violations
```

### **Recovery Mechanisms**
```yaml
automatic_recovery:
  - Retry mechanisms
  - Circuit breaker patterns
  - Fallback strategies
  - Graceful degradation

manual_recovery:
  - Data re-processing
  - Manual data correction
  - System restart
  - Configuration updates
```

---

## 🔧 **CONFIGURATION & DEPLOYMENT**

### **Environment Configuration**
```yaml
# Database Configuration
DATABASE_URL: "postgresql://postgres:password@postgres:5432/openpolicy"
REDIS_URL: "redis://redis:6379/1"

# Service Configuration
SCRAPER_SERVICE_PORT: "8005"
MCP_SERVICE_PORT: "8006"
OPA_SERVICE_PORT: "8181"

# Monitoring Configuration
MONITORING_ENABLED: "true"
PROMETHEUS_ENABLED: "true"
METRICS_PATH: "/metrics"
```

### **Deployment Strategy**
```yaml
# Phase 1: Core Infrastructure
- Deploy database infrastructure
- Deploy Redis cache
- Deploy monitoring services

# Phase 2: Core Services
- Deploy Scraper Service
- Deploy MCP Service
- Deploy OPA Service

# Phase 3: Data Pipeline
- Test data flow
- Validate data quality
- Monitor performance

# Phase 4: Integration
- Deploy remaining services
- Test full integration
- Performance optimization
```

---

## 📊 **PERFORMANCE & SCALABILITY**

### **Performance Optimization**
```yaml
database_optimization:
  - Proper indexing strategy
  - Query optimization
  - Connection pooling
  - Read replicas

caching_strategy:
  - Redis caching for frequently accessed data
  - Query result caching
  - Session caching
  - API response caching

scaling_strategy:
  - Horizontal scaling of services
  - Database sharding
  - Load balancing
  - Auto-scaling
```

### **Scalability Considerations**
```yaml
horizontal_scaling:
  - Multiple scraper instances
  - Multiple MCP service instances
  - Multiple OPA service instances
  - Load balancer configuration

vertical_scaling:
  - Database resource allocation
  - Service resource allocation
  - Cache resource allocation
  - Monitoring resource allocation
```

---

## 🔮 **FUTURE ENHANCEMENTS**

### **Short-term Improvements**
```yaml
performance:
  - Query optimization
  - Index optimization
  - Caching improvements
  - Connection pooling

monitoring:
  - Enhanced metrics
  - Better alerting
  - Performance dashboards
  - Error tracking
```

### **Long-term Enhancements**
```yaml
advanced_features:
  - Machine learning integration
  - Real-time processing
  - Advanced analytics
  - Predictive modeling

infrastructure:
  - Cloud-native deployment
  - Kubernetes orchestration
  - Service mesh
  - Advanced monitoring
```

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **Phase 1: Infrastructure Setup**
- [ ] Deploy PostgreSQL database
- [ ] Deploy Redis cache
- [ ] Create database schemas
- [ ] Setup monitoring infrastructure

### **Phase 2: Core Services**
- [ ] Deploy Scraper Service
- [ ] Deploy MCP Service
- [ ] Deploy OPA Service
- [ ] Test service communication

### **Phase 3: Data Pipeline**
- [ ] Test data collection
- [ ] Test data processing
- [ ] Test data validation
- [ ] Test data storage

### **Phase 4: Integration**
- [ ] Deploy remaining services
- [ ] Test full integration
- [ ] Performance optimization
- [ ] Documentation completion

---

## 📞 **SUPPORT & MAINTENANCE**

### **Regular Maintenance Tasks**
```yaml
daily:
  - Monitor system health
  - Check data quality
  - Review error logs
  - Validate data integrity

weekly:
  - Performance analysis
  - Data quality review
  - Error pattern analysis
  - System optimization

monthly:
  - Comprehensive health check
  - Performance review
  - Capacity planning
  - Documentation updates
```

### **Support Contacts**
```yaml
technical_support:
  - System administrators
  - Database administrators
  - DevOps engineers
  - Data engineers

business_support:
  - Data analysts
  - Business analysts
  - Product managers
  - Stakeholders
```

---

**This document provides a comprehensive overview of the OpenPolicy platform's data flow architecture. For specific implementation details, refer to the individual service documentation and configuration files.**
