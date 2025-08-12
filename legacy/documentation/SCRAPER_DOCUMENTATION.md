# 🕷️ **COMPREHENSIVE SCRAPER DOCUMENTATION - OPENPOLICY PLATFORM**

## 📋 **OVERVIEW**

This document provides comprehensive documentation of all scrapers in the OpenPolicy platform, including data sources, variables collected, and data flow architecture.

---

## 🏗️ **ARCHITECTURE OVERVIEW**

### **Data Flow Architecture**
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   SCRAPERS      │───▶│   MCP SERVICE   │───▶│   OPA SERVICE   │───▶│   DATABASE      │
│  (Port 8005)    │    │  (Port 8006)    │    │  (Port 8181)    │    │  (PostgreSQL)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │                       │
         ▼                       ▼                       ▼                       ▼
   Raw Data Collection    Data Processing        Policy Validation    Structured Storage
```

### **Database Architecture**
- **Scraper Data**: Single `openpolicy` database with schemas
- **Service Databases**: Separate databases for each service (safety)
- **Bills**: Separated by jurisdiction level (federal, provincial, municipal)

---

## 🏛️ **FEDERAL LEVEL SCRAPERS**

### **1. Parliament of Canada Scraper**
- **Source**: `https://www.parl.ca/`
- **Data Type**: Parliamentary data
- **Frequency**: Daily
- **Priority**: High

#### **Data Points Collected**
```yaml
bills:
  - bill_number: "C-123"
  - title_en: "English title"
  - title_fr: "French title"
  - summary_en: "English summary"
  - summary_fr: "French summary"
  - sponsor: "MP Name"
  - status: "introduced|second_reading|passed|defeated"
  - introduced_date: "2024-01-01"
  - passed_date: "2024-01-15"
  - royal_assent_date: "2024-01-20"
  - bill_type: "government|private_member|senate"
  - subject_matter: "Subject description"

representatives:
  - name: "Full Name"
  - name_given: "Given Name"
  - name_family: "Family Name"
  - party: "Party Name"
  - riding: "Electoral District"
  - province: "Province"
  - role: "MP|Senator"
  - start_date: "2024-01-01"
  - end_date: "2024-12-31"
  - website_url: "Personal website"
  - email: "email@parl.ca"
  - twitter_handle: "@handle"

votes:
  - bill_number: "C-123"
  - vote_date: "2024-01-15"
  - vote_type: "second_reading|third_reading|final"
  - result: "passed|defeated|tied"
  - yeas: 150
  - nays: 100
  - abstentions: 5
  - individual_votes: "List of MP votes"

committees:
  - name: "Committee Name"
  - type: "standing|special|joint"
  - members: "List of committee members"
  - meetings: "Meeting schedule and minutes"
```

#### **Storage Location**
- **Database**: `openpolicy.federal.bills`
- **Database**: `openpolicy.federal.votes`
- **Database**: `openpolicy.representatives.politicians`
- **Database**: `openpolicy.representatives.memberships`

---

## 🏛️ **PROVINCIAL LEVEL SCRAPERS**

### **2. Ontario Legislative Assembly Scraper**
- **Source**: `https://www.ola.org/`
- **Data Type**: Provincial legislative data
- **Frequency**: Daily
- **Priority**: High

#### **Data Points Collected**
```yaml
bills:
  - bill_number: "Bill 123"
  - title_en: "English title"
  - title_fr: "French title (if available)"
  - summary: "Bill summary"
  - sponsor: "MPP Name"
  - status: "introduced|second_reading|passed|defeated"
  - introduced_date: "2024-01-01"
  - passed_date: "2024-01-15"
  - royal_assent_date: "2024-01-20"
  - bill_type: "government|private_member|private"
  - subject_matter: "Subject description"

representatives:
  - name: "Full Name"
  - party: "Party Name"
  - riding: "Electoral District"
  - role: "MPP"
  - start_date: "2024-01-01"
  - end_date: "2024-12-31"
  - website_url: "Personal website"
  - email: "email@ola.org"
```

#### **Storage Location**
- **Database**: `openpolicy.provincial.bills`
- **Database**: `openpolicy.provincial.votes`
- **Database**: `openpolicy.representatives.politicians`
- **Database**: `openpolicy.representatives.memberships`

### **3. British Columbia Legislative Assembly Scraper**
- **Source**: `https://www.leg.bc.ca/`
- **Data Type**: Provincial legislative data
- **Frequency**: Daily
- **Priority**: High

### **4. Alberta Legislative Assembly Scraper**
- **Source**: `https://www.assembly.ab.ca/`
- **Data Type**: Provincial legislative data
- **Frequency**: Daily
- **Priority**: High

### **5. National Assembly of Quebec Scraper**
- **Source**: `https://www.assnat.qc.ca/`
- **Data Type**: Provincial legislative data
- **Frequency**: Daily
- **Priority**: High

### **6. Nova Scotia House of Assembly Scraper**
- **Source**: `https://nslegislature.ca/`
- **Data Type**: Provincial legislative data
- **Frequency**: Daily
- **Priority**: Medium

### **7. New Brunswick Legislative Assembly Scraper**
- **Source**: `https://www.legnb.ca/`
- **Data Type**: Provincial legislative data
- **Frequency**: Daily
- **Priority**: Medium

### **8. Manitoba Legislative Assembly Scraper**
- **Source**: `https://www.gov.mb.ca/legislature/`
- **Data Type**: Provincial legislative data
- **Frequency**: Daily
- **Priority**: Medium

### **9. Saskatchewan Legislative Assembly Scraper**
- **Source**: `https://www.legassembly.sk.ca/`
- **Data Type**: Provincial legislative data
- **Frequency**: Daily
- **Priority**: Medium

### **10. Prince Edward Island Legislative Assembly Scraper**
- **Source**: `https://www.assembly.pe.ca/`
- **Data Type**: Provincial legislative data
- **Frequency**: Daily
- **Priority**: Low

### **11. Newfoundland and Labrador House of Assembly Scraper**
- **Source**: `https://www.assembly.nl.ca/`
- **Data Type**: Provincial legislative data
- **Frequency**: Daily
- **Priority**: Low

### **12. Northwest Territories Legislative Assembly Scraper**
- **Source**: `https://www.assembly.gov.nt.ca/`
- **Data Type**: Territorial legislative data
- **Frequency**: Weekly
- **Priority**: Low

### **13. Nunavut Legislative Assembly Scraper**
- **Source**: `https://www.assembly.nu.ca/`
- **Data Type**: Territorial legislative data
- **Frequency**: Weekly
- **Priority**: Low

### **14. Yukon Legislative Assembly Scraper**
- **Source**: `https://yukonassembly.ca/`
- **Data Type**: Territorial legislative data
- **Frequency**: Weekly
- **Priority**: Low

---

## 🏙️ **MUNICIPAL LEVEL SCRAPERS**

### **15. Toronto City Council Scraper**
- **Source**: `https://www.toronto.ca/`
- **Data Type**: Municipal council data
- **Frequency**: Daily
- **Priority**: High

#### **Data Points Collected**
```yaml
bills:
  - bill_number: "By-law 2024-001"
  - title: "By-law title"
  - summary: "By-law summary"
  - sponsor: "Councillor Name"
  - status: "introduced|first_reading|passed|defeated"
  - introduced_date: "2024-01-01"
  - passed_date: "2024-01-15"
  - effective_date: "2024-01-20"
  - bill_type: "by-law|resolution|motion"
  - subject_matter: "Subject description"

representatives:
  - name: "Full Name"
  - ward: "Ward Number/Name"
  - role: "Councillor|Mayor|Deputy Mayor"
  - start_date: "2024-01-01"
  - end_date: "2024-12-31"
  - website_url: "Personal website"
  - email: "email@toronto.ca"
```

#### **Storage Location**
- **Database**: `openpolicy.municipal.bills`
- **Database**: `openpolicy.municipal.votes`
- **Database**: `openpolicy.representatives.politicians`
- **Database**: `openpolicy.representatives.memberships`

### **16. Vancouver City Council Scraper**
- **Source**: `https://vancouver.ca/`
- **Data Type**: Municipal council data
- **Frequency**: Daily
- **Priority**: High

### **17. Montreal City Council Scraper**
- **Source**: `https://montreal.ca/`
- **Data Type**: Municipal council data
- **Frequency**: Daily
- **Priority**: High

### **18. Calgary City Council Scraper**
- **Source**: `https://www.calgary.ca/`
- **Data Type**: Municipal council data
- **Frequency**: Daily
- **Priority**: High

### **19. Edmonton City Council Scraper**
- **Source**: `https://www.edmonton.ca/`
- **Data Type**: Municipal council data
- **Frequency**: Daily
- **Priority**: High

### **20. Ottawa City Council Scraper**
- **Source**: `https://ottawa.ca/`
- **Data Type**: Municipal council data
- **Frequency**: Daily
- **Priority**: Medium

### **21. Mississauga City Council Scraper**
- **Source**: `https://www.mississauga.ca/`
- **Data Type**: Municipal council data
- **Frequency**: Daily
- **Priority**: Medium

### **22. Brampton City Council Scraper**
- **Source**: `https://www.brampton.ca/`
- **Data Type**: Municipal council data
- **Frequency**: Daily
- **Priority**: Medium

### **23. Hamilton City Council Scraper**
- **Source**: `https://www.hamilton.ca/`
- **Data Type**: Municipal council data
- **Frequency**: Daily
- **Priority**: Medium

### **24. Winnipeg City Council Scraper**
- **Source**: `https://www.winnipeg.ca/`
- **Data Type**: Municipal council data
- **Frequency**: Daily
- **Priority**: Medium

### **25. Quebec City Council Scraper**
- **Source**: `https://www.ville.quebec.qc.ca/`
- **Data Type**: Municipal council data
- **Frequency**: Daily
- **Priority**: Medium

### **26. Surrey City Council Scraper**
- **Source**: `https://www.surrey.ca/`
- **Data Type**: Municipal council data
- **Frequency**: Daily
- **Priority**: Medium

---

## 🔗 **EXTERNAL DATA SOURCES**

### **27. OpenParliament Scraper**
- **Source**: `https://openparliament.ca/`
- **Data Type**: Parliamentary data (comprehensive)
- **Frequency**: Daily
- **Priority**: High

#### **Data Points Collected**
```yaml
bills:
  - bill_number: "C-123"
  - title: "Bill title"
  - summary: "Bill summary"
  - sponsor: "MP Name"
  - status: "Bill status"
  - introduced_date: "Introduction date"
  - debates: "Debate transcripts"
  - votes: "Voting records"

representatives:
  - name: "MP Name"
  - party: "Party affiliation"
  - riding: "Electoral district"
  - speeches: "Speech transcripts"
  - voting_record: "Voting history"
  - expenses: "Expense reports"
```

#### **Storage Location**
- **Database**: `openpolicy.federal.bills` (merged with Parliament data)
- **Database**: `openpolicy.representatives.politicians`
- **Database**: `openpolicy.representatives.memberships`

### **28. OpenNorth Scraper**
- **Source**: `https://opennorth.ca/`
- **Data Type**: Representative and boundary data
- **Frequency**: Weekly
- **Priority**: High

#### **Data Points Collected**
```yaml
representatives:
  - name: "Representative name"
  - jurisdiction: "Federal|Provincial|Municipal"
  - district: "District/riding name"
  - party: "Party affiliation"
  - contact_info: "Contact information"
  - boundaries: "Geographic boundaries"

boundaries:
  - jurisdiction: "Jurisdiction level"
  - district_name: "District name"
  - geometry: "Geographic coordinates"
  - population: "Population data"
  - area: "Geographic area"
```

#### **Storage Location**
- **Database**: `openpolicy.representatives.politicians`
- **Database**: `openpolicy.representatives.memberships`

---

## 📊 **DATA VARIABLES & SCHEMAS**

### **Common Data Variables Across All Levels**

#### **Bills/Legislation Variables**
```yaml
# Common fields
- id: "UUID primary key"
- jurisdiction_level: "federal|provincial|municipal"
- jurisdiction_id: "Reference to jurisdiction table"
- session_id: "Reference to session table"
- number: "Bill number/identifier"
- title_en: "English title"
- title_fr: "French title (if applicable)"
- summary: "Bill summary"
- sponsor_id: "Reference to politician"
- status: "Current status"
- introduced_date: "Introduction date"
- passed_date: "Passage date"
- bill_type: "Type of bill"
- subject_matter: "Subject description"
- created_at: "Record creation timestamp"
- updated_at: "Record update timestamp"

# Level-specific fields
federal:
  - royal_assent_date: "Royal assent date"
  - edid: "Elections Canada ID"

provincial:
  - royal_assent_date: "Royal assent date"

municipal:
  - effective_date: "Effective date"
  - bylaw_number: "By-law number"
```

#### **Representatives Variables**
```yaml
# Common fields
- id: "UUID primary key"
- name: "Full name"
- name_given: "Given name"
- name_family: "Family name"
- slug: "URL slug"
- gender: "M|F"
- birth_date: "Birth date"
- website_url: "Personal website"
- twitter_handle: "Twitter handle"
- email: "Email address"
- phone: "Phone number"
- created_at: "Record creation timestamp"
- updated_at: "Record update timestamp"

# Membership fields
- politician_id: "Reference to politician"
- jurisdiction_level: "federal|provincial|municipal"
- jurisdiction_id: "Reference to jurisdiction"
- district_id: "Reference to district"
- party_id: "Reference to party"
- session_id: "Reference to session"
- start_date: "Start date"
- end_date: "End date"
- role: "Role description"
- status: "active|inactive|resigned|defeated"
```

#### **Voting Variables**
```yaml
# Common fields
- id: "UUID primary key"
- bill_id: "Reference to bill"
- vote_date: "Vote date"
- vote_type: "Type of vote"
- result: "passed|defeated|tied"
- yeas: "Number of yes votes"
- nays: "Number of no votes"
- abstentions: "Number of abstentions"
- created_at: "Record creation timestamp"
- updated_at: "Record update timestamp"
```

---

## 🗄️ **DATABASE SCHEMA MAPPING**

### **Federal Level Data**
```sql
-- Bills
openpolicy.federal.bills
openpolicy.federal.votes

-- Representatives
openpolicy.representatives.politicians
openpolicy.representatives.memberships

-- Jurisdictions
openpolicy.federal.jurisdictions
openpolicy.federal.sessions
openpolicy.federal.parties
openpolicy.federal.districts
```

### **Provincial Level Data**
```sql
-- Bills
openpolicy.provincial.bills
openpolicy.provincial.votes

-- Representatives
openpolicy.representatives.politicians
openpolicy.representatives.memberships

-- Jurisdictions
openpolicy.provincial.jurisdictions
openpolicy.provincial.sessions
openpolicy.provincial.parties
openpolicy.provincial.districts
```

### **Municipal Level Data**
```sql
-- Bills
openpolicy.municipal.bills
openpolicy.municipal.votes

-- Representatives
openpolicy.representatives.politicians
openpolicy.representatives.memberships

-- Jurisdictions
openpolicy.municipal.jurisdictions
openpolicy.municipal.sessions
openpolicy.municipal.wards
```

### **Cross-Level Data**
```sql
-- Representatives (all levels)
openpolicy.representatives.politicians
openpolicy.representatives.memberships

-- ETL Operations
openpolicy.etl.jobs
openpolicy.etl.data_sources

-- Monitoring
openpolicy.monitoring.health_checks
openpolicy.monitoring.data_quality
```

---

## 🔄 **DATA FLOW & PROCESSING**

### **1. Data Collection Phase**
```yaml
scrapers:
  - Collect raw data from government websites
  - Store in temporary storage (Redis/File system)
  - Validate basic data structure
  - Log collection metrics
```

### **2. Data Processing Phase (MCP Service)**
```yaml
mcp_service:
  - Receive raw data from scrapers
  - Transform data to standard format
  - Validate data quality
  - Apply business rules
  - Prepare for OPA validation
```

### **3. Policy Validation Phase (OPA Service)**
```yaml
opa_service:
  - Validate data against policies
  - Check data integrity
  - Apply business rules
  - Flag violations
  - Approve/reject data
```

### **4. Database Storage Phase**
```yaml
database:
  - Store validated data in appropriate schemas
  - Maintain referential integrity
  - Update indexes
  - Log storage metrics
  - Trigger notifications
```

---

## 📈 **MONITORING & QUALITY ASSURANCE**

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

### **Health Monitoring**
```yaml
scraper_health:
  - Success rate
  - Error rate
  - Response time
  - Data volume

data_quality:
  - Validation success rate
  - Error count
  - Quality score
  - Trend analysis

system_performance:
  - Database performance
  - API response times
  - Resource utilization
  - Error rates
```

---

## 🚨 **ERROR HANDLING & RECOVERY**

### **Common Error Scenarios**
```yaml
scraper_errors:
  - Website structure changes
  - Network timeouts
  - Rate limiting
  - Authentication failures
  - Data format changes

processing_errors:
  - Invalid data format
  - Missing required fields
  - Data type mismatches
  - Business rule violations
  - Database constraints

system_errors:
  - Database connection failures
  - Service unavailability
  - Resource exhaustion
  - Configuration errors
```

### **Recovery Strategies**
```yaml
automatic_recovery:
  - Retry mechanisms
  - Circuit breaker patterns
  - Fallback data sources
  - Graceful degradation

manual_recovery:
  - Data re-processing
  - Manual data correction
  - System restart
  - Configuration updates

monitoring_alerts:
  - Error rate thresholds
  - Data quality alerts
  - System health notifications
  - Performance warnings
```

---

## 🔧 **CONFIGURATION & DEPLOYMENT**

### **Environment Variables**
```yaml
# Scraper Configuration
SCRAPER_ENVIRONMENT: "development|staging|production"
SCRAPER_LOG_LEVEL: "debug|info|warn|error"
SCRAPER_MAX_CONCURRENT: "5"
SCRAPER_REQUEST_DELAY: "1.0"
SCRAPER_TIMEOUT: "30"

# Database Configuration
DATABASE_URL: "postgresql://user:pass@host:port/db"
REDIS_URL: "redis://host:port/db"

# OPA Configuration
OPA_URL: "http://localhost:8181"
OPA_ENABLED: "true"
OPA_TIMEOUT: "30"

# Monitoring Configuration
MONITORING_ENABLED: "true"
PROMETHEUS_ENABLED: "true"
METRICS_PATH: "/metrics"
```

### **Deployment Configuration**
```yaml
# Docker Configuration
scraper_service:
  ports: "8005:8005"
  environment:
    - DATABASE_URL=postgresql://postgres:password@postgres:5432/openpolicy
    - REDIS_URL=redis://redis:6379/1
    - ENVIRONMENT=development
    - LOG_LEVEL=info

# Health Checks
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8005/healthz"]
  interval: "30s"
  timeout: "10s"
  retries: "3"
  start_period: "40s"
```

---

## 📚 **LEGACY CODE MIGRATION**

### **Migration Strategy**
```yaml
phase_1:
  - Document existing scrapers
  - Identify data sources
  - Map data structures
  - Validate data quality

phase_2:
  - Create new schema
  - Migrate data
  - Update scrapers
  - Test functionality

phase_3:
  - Deploy new system
  - Monitor performance
  - Validate results
  - Optimize processes
```

### **Legacy Scraper Inventory**
```yaml
federal:
  - parliament_ca_scraper.py
  - openparliament_scraper.py

provincial:
  - ca_on_scraper.py
  - ca_bc_scraper.py
  - ca_ab_scraper.py
  - ca_qc_scraper.py
  - ca_ns_scraper.py
  - ca_nb_scraper.py
  - ca_mb_scraper.py
  - ca_sk_scraper.py
  - ca_pe_scraper.py
  - ca_nl_scraper.py
  - ca_nt_scraper.py
  - ca_nu_scraper.py
  - ca_yt_scraper.py

municipal:
  - ca_on_toronto_scraper.py
  - ca_bc_vancouver_scraper.py
  - ca_qc_montreal_scraper.py
  - ca_ab_calgary_scraper.py
  - ca_ab_edmonton_scraper.py
  - ca_on_ottawa_scraper.py
  - ca_on_mississauga_scraper.py
  - ca_on_brampton_scraper.py
  - ca_on_hamilton_scraper.py
  - ca_mb_winnipeg_scraper.py
  - ca_qc_quebec_city_scraper.py
  - ca_bc_surrey_scraper.py

external:
  - opennorth_scraper.py
```

---

## 🎯 **SUCCESS METRICS & KPIs**

### **Data Collection Metrics**
```yaml
volume:
  - Records collected per day
  - Data size per day
  - Coverage percentage
  - Update frequency

quality:
  - Validation success rate
  - Error rate
  - Completeness score
  - Accuracy score

performance:
  - Collection time
  - Processing time
  - Storage time
  - Response time
```

### **System Health Metrics**
```yaml
availability:
  - Uptime percentage
  - Service availability
  - Error rate
  - Response time

efficiency:
  - Resource utilization
  - Throughput
  - Latency
  - Queue depth

reliability:
  - Success rate
  - Failure rate
  - Recovery time
  - Data consistency
```

---

## 📞 **SUPPORT & MAINTENANCE**

### **Regular Maintenance Tasks**
```yaml
daily:
  - Monitor scraper health
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

## 🔮 **FUTURE ENHANCEMENTS**

### **Planned Improvements**
```yaml
short_term:
  - Enhanced error handling
  - Improved monitoring
  - Better data validation
  - Performance optimization

medium_term:
  - Machine learning integration
  - Advanced analytics
  - Real-time processing
  - API enhancements

long_term:
  - AI-powered data extraction
  - Predictive analytics
  - Advanced reporting
  - Integration expansion
```

### **Technology Roadmap**
```yaml
phase_1:
  - Current system stabilization
  - Performance optimization
  - Error handling improvement

phase_2:
  - Advanced monitoring
  - Machine learning integration
  - API enhancement

phase_3:
  - AI-powered features
  - Advanced analytics
  - Platform expansion
```

---

## 📋 **APPENDIX**

### **A. Data Dictionary**
Complete list of all data fields, types, and descriptions.

### **B. API Documentation**
API endpoints for data access and management.

### **C. Troubleshooting Guide**
Common issues and solutions.

### **D. Change Log**
History of system changes and updates.

---

**This documentation provides a comprehensive overview of the OpenPolicy platform's scraping infrastructure. For specific implementation details, refer to the individual scraper files and configuration documentation.**
