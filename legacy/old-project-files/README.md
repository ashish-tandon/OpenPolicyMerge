# Old Project Files - Legacy Documentation

This directory contains files from the previous monolithic project structure that have been moved to legacy as part of the microservices architecture migration.

## Files Moved

### Old Project Structure Files
- `PROJECT_COMPLETION_REPORT.md` - Old project completion report
- `PROJECT_COMPLETION_SUMMARY.md` - Old project summary
- `test_system.sh` - Old system testing script
- `README_COMPLETE.md` - Old comprehensive README
- `deploy.sh` - Old deployment script
- `nginx.conf` - Old nginx configuration
- `prometheus.yml` - Old Prometheus configuration
- `main.go` - Old Go main file
- `Dockerfile.api` - Old API Dockerfile
- `FINAL_STATUS_REPORT.md` - Old final status report
- `MERGE_PLAN.md` - Old merge plan document
- `docker-compose.yml` - Old Docker Compose configuration
- `docker-compose.simple.yml` - Old simple Docker Compose
- `go.mod` - Old Go module file
- `go.sum` - Old Go dependencies
- `.dockerignore` - Old Docker ignore file
- `src/` - Old source code directory

## Why These Files Were Moved

1. **Architecture Change**: The project has moved from a monolithic structure to a microservices architecture
2. **Technology Stack**: Some files were specific to the old technology stack (Go, old Docker setup)
3. **Project Structure**: The new structure uses different organization and naming conventions
4. **Preservation**: Files are kept for reference and potential future use

## Current Project Structure

The new microservices architecture is organized as follows:

```
OpenPolicyMerge/
├── services/           # Backend microservices
│   ├── api-gateway/   # FastAPI API Gateway
│   ├── etl/          # Prefect-based ETL service
│   └── legacy-django/ # Django bridge service
├── apps/              # Frontend applications
│   ├── web/          # Next.js web frontend
│   ├── admin/        # Next.js admin dashboard
│   └── mobile/       # React Native mobile app
├── db/                # Database schema and migrations
├── policies/          # Open Policy Agent policies
├── docs/              # Project documentation
└── legacy/            # Legacy code and old files
```

## When to Reference These Files

- **Historical Context**: Understanding previous project decisions
- **Data Migration**: Extracting data structures from old implementations
- **Feature Reference**: Understanding how features were previously implemented
- **Troubleshooting**: Debugging issues that may have existed in the old system

## Migration Status

- ✅ **Completed**: Project structure setup, legacy code import
- 🚧 **In Progress**: Core services development
- 📋 **Planned**: Data integration, frontend development, production readiness

## Notes

- These files are preserved for reference only
- Do not modify these files directly
- If you need to implement something similar, check the new architecture first
- Always follow the current microservices architecture patterns
