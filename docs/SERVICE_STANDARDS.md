# OpenPolicy Platform Service Standards

## Overview
This document defines the mandatory standards that all services in the OpenPolicy platform must comply with to ensure consistency, reliability, and maintainability.

## Mandatory Service Components

### 1. File Structure
```
service-name/
├── src/
│   ├── __init__.py          # Package initialization with version and port
│   ├── main.py              # Service entry point
│   ├── config.py            # Configuration management
│   └── api.py               # API endpoints
├── tests/                   # Test directory
├── logs/                    # Log directory
├── venv/                    # Python virtual environment
├── Dockerfile               # Container definition
├── start.sh                 # Startup script (executable)
├── requirements.txt         # Python dependencies
└── .env.example            # Environment template
```

### 2. Startup Script (`start.sh`)
- Must be executable (`chmod +x`)
- Check dependencies and environment
- Create virtual environment if missing
- Install dependencies
- Start service with proper error handling
- Include service identification and port

### 3. Configuration (`src/config.py`)
- Service identification (name, version, port)
- Environment-based configuration
- External service dependencies
- Logging configuration
- Health check settings
- Performance and security settings
- **MANDATORY: Error reporting service integration**

### 4. API Endpoints
- Root endpoint (`/`)
- Health check (`/healthz`, `/health`)
- Service-specific endpoints (`/api/service-name/*`)
- **MANDATORY: Error reporting endpoints for monitoring**

### 5. Health Checks
- `/healthz` endpoint returning service status
- Health check interval configuration
- Dependency health verification
- **MANDATORY: Error reporting service health integration**

### 6. Dependency Management
- `requirements.txt` for Python services
- `package.json` for Node.js services
- Virtual environment management
- **MANDATORY: Error reporting service as dependency**

### 7. Logging and Metrics
- Structured logging with service identification
- Log level configuration
- Performance metrics collection
- **MANDATORY: Error reporting integration for centralized logging**

### 8. Error Handling
- Comprehensive exception handling
- Error logging with context
- **MANDATORY: Error reporting service integration for all errors**

### 9. Service Discovery
- Port assignment (9000 series)
- Health check endpoints
- Service registration
- **MANDATORY: Error reporting service discovery**

## Error Reporting Integration Requirements

### **CRITICAL: All services MUST integrate with Error Reporting Service (Port 9024)**

#### 1. Configuration Integration
```python
# In src/config.py
ERROR_REPORTING_URL = os.getenv("ERROR_REPORTING_URL", "http://localhost:9024")
ENABLE_ERROR_REPORTING = os.getenv("ENABLE_ERROR_REPORTING", "true").lower() == "true"
```

#### 2. Error Reporting Endpoints
```python
# In src/api.py
@router.post("/api/{service_name}/errors/report")
async def report_error(error_data: dict):
    """Report error to centralized error reporting service"""
    # Implementation required
```

#### 3. Logging Integration
```python
# In main.py and other files
import logging
from .error_reporter import ErrorReporter

# Initialize error reporter
error_reporter = ErrorReporter(Config.ERROR_REPORTING_URL)

# Log errors with service context
logger.error(f"Service error: {error}", extra={
    "service": Config.SERVICE_NAME,
    "port": Config.SERVICE_PORT,
    "error_type": "service_error"
})
```

#### 4. Health Check Integration
```python
# In health check endpoints
@router.get("/healthz")
async def health_check():
    try:
        # Check error reporting service health
        error_service_health = await check_error_service_health()
        return {
            "status": "healthy",
            "error_reporting": error_service_health
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error_reporting": "disconnected"
        }
```

## Service Integration Requirements

### 1. Monitoring Integration
- Health check endpoints
- Metrics collection
- Performance monitoring
- **Error reporting service monitoring**

### 2. API Gateway Integration
- Service registration
- Route configuration
- Authentication integration
- **Error reporting service routing**

### 3. Database Integration
- Connection pooling
- Migration support
- Backup procedures
- **Error logging to database**

### 4. Cache Integration
- Redis connection
- Cache invalidation
- Performance optimization
- **Error cache management**

## Compliance Checklist

### Phase 1: Basic Structure ✅
- [x] File structure compliance
- [x] Startup script creation
- [x] Configuration files
- [x] API endpoints
- [x] Health checks

### Phase 2: Error Reporting Integration 🔄
- [ ] Error reporting service configuration
- [ ] Error reporting endpoints
- [ ] Logging integration
- [ ] Health check integration
- [ ] Service discovery integration

### Phase 3: Advanced Features
- [ ] Metrics collection
- [ ] Performance monitoring
- [ ] Security implementation
- [ ] Testing framework
- [ ] Documentation

## Implementation Priorities

### Week 1: Core Compliance
1. Complete all missing files
2. Achieve 100% basic compliance
3. Implement error reporting integration

### Week 2: Error Reporting
1. Deploy error reporting service
2. Integrate all services with error reporting
3. Test error collection and reporting

### Week 3: Advanced Features
1. Implement metrics collection
2. Add performance monitoring
3. Enhance security features

## Reporting and Monitoring

### Daily Compliance Checks
- Run comprehensive audit script
- Check error reporting service health
- Monitor service status
- Track compliance percentage

### Weekly Reviews
- Compliance report generation
- Error pattern analysis
- Performance metrics review
- Service health assessment

## Success Metrics

### Compliance Targets
- **Week 1**: 100% basic compliance
- **Week 2**: 100% error reporting integration
- **Week 3**: 100% advanced features

### Quality Metrics
- Zero critical compliance gaps
- 100% error reporting coverage
- <2 second health check response
- 99.9% service uptime

---

**Note**: This document is continuously updated. All services must maintain compliance with these standards. Non-compliance will block deployment and require immediate remediation.
