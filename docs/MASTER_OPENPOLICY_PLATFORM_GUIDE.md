# 🚀 **MASTER OPENPOLICY PLATFORM GUIDE** 🚀

> **SINGLE SOURCE OF TRUTH** - All platform status, architecture, and next steps
> **COPY + ADAPT + INTEGRATE** strategy for scrapers and legacy code

## 📊 **CURRENT STATUS OVERVIEW**

### **✅ COMPLETED SERVICES**
- **Scraper Service**: Core infrastructure complete, database setup done
- **Database Architecture**: Consolidated PostgreSQL with schema-based separation

### **🎯 IMMEDIATE NEXT STEPS: CLEAR DIRECTION**

#### **🎯 PRIORITY 1: COMPLETE SCRAPER SERVICE (Week 1-2) ✅ COMPLETED**
1. **Complete Missing Core Modules** ✅
   - [x] Complete all missing core modules
   - [x] Complete all missing middleware components
   - [x] Complete all missing route handlers
   - [x] Complete all missing service implementations
   - [x] Complete all missing data models

2. **Database Setup** ✅ COMPLETED
   - [x] Run `scripts/setup-databases.sh`
   - [x] Test database connectivity
   - [x] Verify schema creation

3. **Service Testing** ✅ COMPLETED
   - [x] Test Scraper Service endpoints
   - [x] Test health checks
   - [x] Test monitoring

#### **🎯 PRIORITY 2: LEGACY SCRAPER ANALYSIS & TEST INTEGRATION (Week 2-3) 🎯 NEXT**
1. **Code Review & Test Discovery**
   - [ ] Analyze each scraper's implementation
   - [ ] Document data structures and dependencies
   - [ ] **CRITICAL**: Identify and catalog existing test infrastructure
   - [ ] **CRITICAL**: Document test coverage gaps

2. **Test Infrastructure Migration**
   - [ ] **COPY OVER** existing tests from legacy scrapers
   - [ ] **COPY OVER** OpenParliament test suite (Django-based)
   - [ ] **COPY OVER** Civic-Scraper test suite (pytest-based)
   - [ ] Adapt tests to new service architecture
   - [ ] Ensure test coverage meets thresholds (85% statements, 95% branch)

#### **🎯 PRIORITY 3: SCRAPER MIGRATION (Week 3-8)**
1. **High Priority Scrapers**: Parliament of Canada, Ontario, BC, AB, QC, Toronto, Vancouver, Montreal, Calgary, Edmonton
2. **Medium Priority Scrapers**: NS, NB, MB, SK, Remaining municipal scrapers
3. **Low Priority Scrapers**: PE, NL, NT, NU, YT
4. **Data Pipeline Integration**: Connect scrapers to MCP service and OPA

## 🔄 **DATA FLOW ARCHITECTURE (CRITICAL)**

### **✅ CORRECT FLOW: Scrapers → Services (NOT the other way around)**
```
Web Sources → Scrapers → ETL Service → Database → Other Services
     ↓           ↓         ↓           ↓         ↓
   Raw Data → Structured → Processed → Stored → Consumed
```

### **❌ WRONG APPROACH: Services → Database → Scrapers**
- **Database schemas are defined by the data collected**, not by service requirements
- **Services adapt to the data structure**, not force the data to fit service schemas
- **Scrapers determine the data model**, services consume it

### **Database Schema Strategy**
- **Scraper Data Schemas**: `federal`, `provincial`, `municipal` (defined by scrapers)
- **Service Schemas**: `auth`, `etl`, `plotly`, `go`, `scrapers`, `health`, `monitoring`, `notifications`, `config`, `search`, `policy`
- **Single PostgreSQL instance** with logical separation via schemas

## 🧪 **TEST INTEGRATION STRATEGY**

### **Existing Test Infrastructure (COPY OVER)**
1. **OpenParliament Tests** (Django-based)
   - Location: `legacy/openparliament/parliament/politicians/tests.py`
   - Coverage: Politician models, API endpoints, data validation
   - **MIGRATION**: Adapt to new service architecture

2. **Civic-Scraper Tests** (pytest-based)
   - Location: `legacy/civic-scraper/tests/`
   - Coverage: Asset management, CLI operations, data processing
   - **MIGRATION**: Integrate with new Scraper Service

3. **Legacy Scraper Tests**
   - **SEARCH REQUIRED**: Look for test files in `src/scrapers/` subdirectories
   - **COVERAGE**: Individual scraper functionality, data validation

### **Test Migration Plan**
1. **Phase 1**: Copy existing tests to `services/scraper-service/tests/`
2. **Phase 2**: Adapt test infrastructure (pytest, test databases, fixtures)
3. **Phase 3**: Ensure test coverage meets thresholds
4. **Phase 4**: Integrate with CI/CD pipeline

### **Test Coverage Requirements**
- **Scraper Service**: ≥85% statements, ≥95% branch coverage
- **Data Processing**: ≥95% branch coverage (critical for data integrity)
- **API Endpoints**: 100% endpoint coverage
- **Integration Tests**: All scraper → ETL → Database flows

## 🏗️ **ARCHITECTURE IMPLEMENTATION**

### **Service Discovery & Communication**
- **No hard-coded ports**: All services resolve via service discovery
- **Health checks**: `/healthz`, `/readyz`, `/livez` endpoints
- **Metrics**: Prometheus integration for monitoring

### **Database Strategy**
- **Single PostgreSQL instance** with multiple schemas
- **Alembic migrations** for all schema changes
- **Schema separation** for logical organization
- **No service-specific databases** (consolidated approach)

## 📁 **FILE STRUCTURE**

### **Root Directory**
- `.cursorrules` - Cursor global rules
- `docs/instructions.md` - RUN_PLAYBOOK procedures
- `docs/architecture.md` - Current architecture diagram
- `docs/MASTER_OPENPOLICY_PLATFORM_GUIDE.md` - This file (SINGLE SOURCE OF TRUTH)

### **Legacy Directory** (Read-only, for reference)
- `legacy/documentation/` - Old documentation files
- `legacy/architecture_docs/` - Old architecture documents
- `legacy/migration_plans/` - Old migration plans
- `legacy/status_reports/` - Old status reports
- `legacy/openparliament/` - OpenParliament code and tests
- `legacy/civic-scraper/` - Civic-scraper code and tests

## 🚨 **CRITICAL CONSTRAINTS**

1. **NO DELETION**: All legacy code and tests must be preserved
2. **COPY + ADAPT**: Don't reinvent, copy and adapt existing code
3. **TEST PRESERVATION**: All existing tests must be migrated and maintained
4. **DATA FLOW**: Scrapers → Services, never Services → Scrapers
5. **SINGLE SOURCE**: This document is the ONLY source of truth

## 🔄 **NEXT IMMEDIATE ACTIONS**

1. **Complete Scraper Service Testing** (Priority 1.3)
2. **Begin Legacy Test Discovery** (Priority 2.1)
3. **Plan Test Migration Strategy** (Priority 2.2)
4. **Validate Data Flow Architecture** (Priority 2.3)

---

> **Remember**: This is the SINGLE SOURCE OF TRUTH. All decisions, status updates, and next steps are documented here.
> **COPY + ADAPT + INTEGRATE** - Don't reinvent the wheel!
