# Unified Service Reference (Single Source of Truth)

## Service Discovery (authoritative)
- Backend: Kubernetes DNS
- Registration/Health: Kubernetes readiness/liveness probes on each Deployment; Services expose stable DNS names.
- Resolution: NEVER hard-code ports; resolve via Service DNS:
  - http://<service>.<namespace>.svc.cluster.local:<PORT_FROM_ENV>
  - Clients read ports from environment variables; no literals in code.

## Standard Ports (from env only)
- API_GATEWAY_PORT: ${API_GATEWAY_PORT}
- ETL_PORT: ${ETL_PORT}
- WEB_PORT: ${WEB_PORT}
- ADMIN_PORT: ${ADMIN_PORT}

## Health/Readiness Contracts
- GET /healthz  -> { "status": "ok" }
- GET /readyz   -> 200 only when dependencies are healthy

## API Contract Source
- openapi.yaml — update before code (spec-first)

## Database
- PostgreSQL 15+ only. Changes via Alembic with downgrade.

## Testing & Coverage
- Thresholds from .cursorrules
- Contract tests against openapi.yaml
- ETL data tests: row counts, non-nullables, FK integrity

## Environments
- dev (smoke tests run here), staging, prod
