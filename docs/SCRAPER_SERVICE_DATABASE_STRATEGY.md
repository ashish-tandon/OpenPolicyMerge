# 🗄️ SCRAPER SERVICE - DUAL DATABASE STRATEGY

## 📋 **EXECUTIVE SUMMARY**
This document outlines the comprehensive dual-database strategy for the OpenPolicy Scraper Service, ensuring data integrity, testing validation, and safe production deployment.

## 🎯 **STRATEGIC OBJECTIVES**
- **Data Safety**: Prevent production data corruption during testing
- **Quality Assurance**: Validate data structure before production deployment
- **Testing Isolation**: Separate test and production environments
- **Rollback Capability**: Enable safe rollback in case of issues
- **Schema Validation**: Ensure column and field compatibility

## 🏗️ **DUAL DATABASE ARCHITECTURE**

### **Database Separation Strategy**
```
┌─────────────────────────────────────────────────────────────┐
│                    SCRAPER SERVICE                          │
├─────────────────────────────────────────────────────────────┤
│  Test Mode: TEST_DATABASE_URL                              │
│  Production Mode: PRODUCTION_DATABASE_URL                  │
└─────────────────────────────────────────────────────────────┘
                    ↕️
┌─────────────────────────────────────────────────────────────┐
│  TEST DATABASE (test_openpolicy)                           │
│  • Schema validation                                        │
│  • Column mapping verification                              │
│  • Data transformation testing                              │
│  • Limited data volume                                      │
└─────────────────────────────────────────────────────────────┘
                    ↕️
┌─────────────────────────────────────────────────────────────┐
│  PRODUCTION DATABASE (openpolicy)                          │
│  • Live data storage                                        │
│  • Full data volume                                         │
│  • Production schemas                                       │
│  • Backup and rollback                                      │
└─────────────────────────────────────────────────────────────┘
```

### **Environment Configuration**
```bash
# Development/Testing Environment
ENVIRONMENT=development
TEST_MODE=true
TEST_DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_openpolicy
PRODUCTION_DATABASE_URL=postgresql://prod_user:prod_pass@localhost:5432/openpolicy

# Production Environment
ENVIRONMENT=production
TEST_MODE=false
TEST_DATABASE_URL=postgresql://test_user:test_pass@staging-db:5432/test_openpolicy
PRODUCTION_DATABASE_URL=postgresql://prod_user:prod_pass@prod-db:5432/openpolicy
```

## 🔄 **WORKFLOW: TEST → VALIDATION → PRODUCTION**

### **Phase 1: Test Mode Execution**
```python
# 1. Set test mode
os.environ["TEST_MODE"] = "true"
os.environ["ENVIRONMENT"] = "development"

# 2. Scraper runs against test database
test_db_url = config.TEST_DATABASE_URL  # test_openpolicy
test_db_name = config.TEST_DATABASE_NAME

# 3. Limited data collection for validation
if config.TEST_MODE:
    data_limit = config.TEST_DATA_LIMIT  # 1000 records
    enable_validation = config.TEST_SCHEMA_VERIFICATION
```

### **Phase 2: Schema Validation**
```python
# 1. Verify test database schema
def validate_test_schema():
    """Validate test database schema matches expected structure"""
    test_schema = get_database_schema(config.TEST_DATABASE_URL)
    expected_schema = load_expected_schema()
    
    validation_results = {
        "columns_match": compare_columns(test_schema, expected_schema),
        "data_types_match": compare_data_types(test_schema, expected_schema),
        "constraints_match": compare_constraints(test_schema, expected_schema)
    }
    
    return validation_results

# 2. Column mapping verification
def verify_column_mapping():
    """Verify test data columns map correctly to production schema"""
    test_columns = get_table_columns(config.TEST_DATABASE_URL, "scraped_data")
    prod_columns = get_table_columns(config.PRODUCTION_DATABASE_URL, "scraped_data")
    
    mapping_verification = {
        "test_columns": test_columns,
        "production_columns": prod_columns,
        "mapping_compatible": verify_column_compatibility(test_columns, prod_columns)
    }
    
    return mapping_verification
```

### **Phase 3: Production Deployment**
```python
# 1. Pre-production verification
def pre_production_verification():
    """Verify all tests passed before production deployment"""
    if not config.PRODUCTION_VERIFICATION_REQUIRED:
        return True
    
    verification_checks = {
        "test_data_validated": validate_test_data_quality(),
        "schema_compatible": validate_schema_compatibility(),
        "column_mapping_verified": verify_column_mapping(),
        "data_transformation_tested": test_data_transformations()
    }
    
    all_passed = all(verification_checks.values())
    
    if not all_passed:
        raise ValidationError(f"Production verification failed: {verification_checks}")
    
    return True

# 2. Production database backup
def backup_production_database():
    """Create backup before production update"""
    if not config.PRODUCTION_BACKUP_BEFORE_UPDATE:
        return
    
    backup_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"openpolicy_backup_{backup_timestamp}"
    
    create_database_backup(
        config.PRODUCTION_DATABASE_URL,
        backup_name,
        backup_retention_days=7
    )

# 3. Production deployment
def deploy_to_production():
    """Deploy validated data to production database"""
    # Verify all checks passed
    pre_production_verification()
    
    # Create backup
    backup_production_database()
    
    # Deploy to production
    production_db_url = config.PRODUCTION_DATABASE_URL
    production_db_name = config.PRODUCTION_DATABASE_NAME
    
    # Execute production deployment
    deploy_validated_data(production_db_url, production_db_name)
    
    # Verify deployment success
    verify_production_deployment()
```

## 🧪 **TESTING & VALIDATION FRAMEWORK**

### **Test Data Quality Checks**
```python
def validate_test_data_quality():
    """Validate quality of test data before production deployment"""
    quality_checks = {
        "data_completeness": check_data_completeness(),
        "data_accuracy": check_data_accuracy(),
        "data_consistency": check_data_consistency(),
        "data_integrity": check_data_integrity()
    }
    
    return quality_checks

def check_data_completeness():
    """Check if all required fields are populated"""
    test_data = query_test_database("SELECT * FROM scraped_data LIMIT 100")
    
    required_fields = ["id", "title", "content", "source", "timestamp"]
    completeness_score = 0
    
    for record in test_data:
        field_count = sum(1 for field in required_fields if record.get(field))
        completeness_score += field_count / len(required_fields)
    
    return completeness_score / len(test_data) > 0.95  # 95% completeness required
```

### **Schema Compatibility Validation**
```python
def validate_schema_compatibility():
    """Validate test and production schemas are compatible"""
    test_schema = get_database_schema(config.TEST_DATABASE_URL)
    prod_schema = get_database_schema(config.PRODUCTION_DATABASE_URL)
    
    compatibility_checks = {
        "table_structure": compare_table_structures(test_schema, prod_schema),
        "column_types": compare_column_types(test_schema, prod_schema),
        "indexes": compare_indexes(test_schema, prod_schema),
        "constraints": compare_constraints(test_schema, prod_schema)
    }
    
    return all(compatibility_checks.values())
```

## 🚨 **ERROR HANDLING & ROLLBACK**

### **Error Detection & Reporting**
```python
def monitor_deployment_errors():
    """Monitor for errors during production deployment"""
    error_threshold = 5  # Maximum allowed errors
    error_count = 0
    
    try:
        # Monitor deployment process
        deployment_status = monitor_deployment_process()
        
        if deployment_status.has_errors():
            error_count += 1
            report_error_to_monitoring_service(
                service="scraper-service",
                error_type="deployment_error",
                error_count=error_count,
                threshold=error_threshold
            )
            
            if error_count >= error_threshold:
                trigger_automatic_rollback()
                
    except Exception as e:
        log_error(f"Deployment monitoring failed: {e}")
        trigger_manual_rollback()
```

### **Automatic Rollback Strategy**
```python
def trigger_automatic_rollback():
    """Automatically rollback to previous production state"""
    if not config.PRODUCTION_ROLLBACK_ENABLED:
        log_warning("Automatic rollback disabled, manual intervention required")
        return
    
    try:
        # Stop current deployment
        stop_deployment_process()
        
        # Restore from backup
        latest_backup = get_latest_backup()
        restore_database_from_backup(
            config.PRODUCTION_DATABASE_URL,
            latest_backup
        )
        
        # Verify rollback success
        verify_rollback_success()
        
        # Notify stakeholders
        notify_rollback_completion()
        
    except Exception as e:
        log_error(f"Automatic rollback failed: {e}")
        escalate_to_manual_intervention()
```

## 📊 **MONITORING & METRICS**

### **Key Performance Indicators**
```python
def collect_deployment_metrics():
    """Collect metrics during deployment process"""
    metrics = {
        "test_data_quality_score": calculate_data_quality_score(),
        "schema_validation_time": measure_schema_validation_time(),
        "deployment_duration": measure_deployment_duration(),
        "error_rate": calculate_error_rate(),
        "rollback_frequency": track_rollback_frequency()
    }
    
    return metrics

def calculate_data_quality_score():
    """Calculate overall data quality score"""
    quality_factors = {
        "completeness": 0.3,
        "accuracy": 0.3,
        "consistency": 0.2,
        "integrity": 0.2
    }
    
    scores = {
        "completeness": check_data_completeness(),
        "accuracy": check_data_accuracy(),
        "consistency": check_data_consistency(),
        "integrity": check_data_integrity()
    }
    
    weighted_score = sum(
        scores[factor] * weight 
        for factor, weight in quality_factors.items()
    )
    
    return weighted_score
```

## 🔧 **CONFIGURATION & ENVIRONMENT SETUP**

### **Environment Variables**
```bash
# Database Configuration
TEST_DATABASE_URL=postgresql://test_user:test_pass@localhost:5432/test_openpolicy
PRODUCTION_DATABASE_URL=postgresql://prod_user:prod_pass@localhost:5432/openpolicy
TEST_DATABASE_NAME=test_openpolicy
PRODUCTION_DATABASE_NAME=openpolicy

# Test Mode Settings
TEST_MODE=true
TEST_DATA_LIMIT=1000
TEST_SCHEMA_VERIFICATION=true
TEST_COLUMN_MATCHING=true

# Production Settings
PRODUCTION_VERIFICATION_REQUIRED=true
PRODUCTION_BACKUP_BEFORE_UPDATE=true
PRODUCTION_ROLLBACK_ENABLED=true

# Validation Settings
ENABLE_SCHEMA_VALIDATION=true
ENABLE_COLUMN_MAPPING=true
ENABLE_DATA_TRANSFORMATION=true
```

### **Database Setup Scripts**
```sql
-- Test Database Setup
CREATE DATABASE test_openpolicy;
CREATE USER test_user WITH PASSWORD 'test_pass';
GRANT ALL PRIVILEGES ON DATABASE test_openpolicy TO test_user;

-- Production Database Setup
CREATE DATABASE openpolicy;
CREATE USER prod_user WITH PASSWORD 'prod_pass';
GRANT ALL PRIVILEGES ON DATABASE openpolicy TO prod_user;

-- Backup User (for automated backups)
CREATE USER backup_user WITH PASSWORD 'backup_pass';
GRANT CONNECT ON DATABASE openpolicy TO backup_user;
GRANT USAGE ON SCHEMA public TO backup_user;
```

## 📋 **DEPLOYMENT CHECKLIST**

### **Pre-Deployment (Test Mode)**
- [ ] Test mode enabled
- [ ] Test database accessible
- [ ] Test data collection completed
- [ ] Schema validation passed
- [ ] Column mapping verified
- [ ] Data quality checks passed
- [ ] Error rate below threshold

### **Production Deployment**
- [ ] All test validations passed
- [ ] Production database accessible
- [ ] Backup created successfully
- [ ] Rollback plan ready
- [ ] Monitoring active
- [ ] Error reporting configured
- [ ] Stakeholders notified

### **Post-Deployment**
- [ ] Deployment verification completed
- [ ] Data integrity confirmed
- [ ] Performance metrics collected
- [ ] Error monitoring active
- [ ] Rollback capability maintained
- [ ] Documentation updated

---

## 🔮 **FUTURE ENHANCEMENTS**

### **Phase 2: Advanced Features**
- **Automated Schema Migration**: Version-controlled schema changes
- **Data Lineage Tracking**: Track data transformations and sources
- **Advanced Validation Rules**: Custom validation logic per data type
- **Performance Optimization**: Optimize database queries and indexing

### **Phase 3: Enterprise Features**
- **Multi-Environment Support**: Dev, staging, production, disaster recovery
- **Advanced Backup Strategies**: Point-in-time recovery, cross-region backup
- **Compliance Automation**: Automated compliance reporting and auditing
- **Cost Optimization**: Database resource optimization and monitoring

---

## 📞 **SUPPORT & CONTACTS**

### **Database Team**
- **Primary**: [Name/Team]
- **Secondary**: [Name/Team]

### **Emergency Contacts**
- **Database Issues**: [Contact Information]
- **Rollback Support**: [Contact Information]

### **Documentation**
- **Database Schema**: [Link]
- **Backup Procedures**: [Link]
- **Rollback Procedures**: [Link]
