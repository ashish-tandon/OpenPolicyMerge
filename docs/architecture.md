# Architecture (Current)

> This is the authoritative architecture document and diagram for the platform.
> The deprecated services doc lives in docs/LEGACY/ and must not be used.

## Diagram
![OpenPolicy Architecture](./images/architecture.png)

## Overview
- API Gateway → services via service discovery (no static ports).
- ETL → canonical Postgres schema (Alembic migrations).
- Search → Postgres FTS initially; can upgrade later.
- UIs (Web/Mobile/Admin) → API Gateway only.
- Observability → healthz/readyz + metrics; centralized logging.

## Sources of Truth
- UNIFIED_SERVICE_REFERENCE.md (patterns, discovery, ports-from-env)
- openapi.yaml (API contract)
- ADRs (decisions)
- DEPLOYMENT_PROCESS.md (environments, rollout/rollback)

## Change Protocol
1) Update diagram if a boundary changes.
2) Add an ADR for any architectural decision.
3) Update UNIFIED_SERVICE_REFERENCE.md patterns if discovery/config changes.

## Current Service Architecture

### Core Services
- **API Gateway**: Service discovery, routing, authentication
- **ETL Service**: Data transformation and loading
- **Scraper Service**: Web scraping orchestration
- **Policy Service**: Policy evaluation and management
- **Search Service**: Full-text search capabilities
- **Authentication Service**: User management and auth
- **Notification Service**: Event notifications
- **Configuration Service**: Centralized configuration
- **Health Service**: Service health monitoring
- **Monitoring Service**: Metrics and observability

### Data Flow
1. **Scrapers** collect data from various sources
2. **ETL Service** processes and transforms the data
3. **Policy Service** applies business rules and policies
4. **Search Service** indexes data for fast retrieval
5. **API Gateway** provides unified access to all services

### Database Strategy
- **Single PostgreSQL instance** with multiple schemas
- **Scraper data**: federal, provincial, municipal schemas
- **Service data**: auth, etl, plotly, go, scrapers, health, monitoring, notifications, config, search, policy schemas
- **Alembic migrations** for all schema changes
