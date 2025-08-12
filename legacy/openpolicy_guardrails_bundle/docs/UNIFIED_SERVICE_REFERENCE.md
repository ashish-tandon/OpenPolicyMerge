# Unified Service Reference (Single Source of Truth)

## Service Discovery (authoritative)
- Backend: {{FILL: discovery backend e.g., "Kubernetes DNS"}} 
- Registration/Health: {{FILL: pattern, e.g., k8s readiness/liveness + DNS service names}}
- Resolution: NEVER hard-code ports; use `http://<svc>.<ns>.svc.cluster.local:<port-from-env>` or client-side discovery per backend.

## Standard Ports (from env only)
- API_GATEWAY_PORT: ${API_GATEWAY_PORT}
- ETL_PORT: ${ETL_PORT}
- WEB_PORT: ${WEB_PORT}
- ADMIN_PORT: ${ADMIN_PORT}

## Health/Readiness Contracts
- `GET /healthz` → { status: "ok" }
- `GET /readyz`  → 200 only when dependencies are healthy

## API Contract Source
- openapi.yaml — update before code (spec-first)

## Database
- PostgreSQL 15+ only. Changes via Alembic with downgrade.

## Testing & Coverage
- Thresholds from .cursorrules
- Contract tests against openapi.yaml
- ETL data tests: row counts, non-nullables, FK integrity

## Environments
- dev, staging, prod (fill details in DEPLOYMENT_PROCESS.md)
