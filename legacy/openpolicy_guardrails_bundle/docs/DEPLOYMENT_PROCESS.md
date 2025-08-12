# Deployment Process (Authoritative)

## Environments
- dev: {{FILL: cluster/context}}
- staging: {{FILL}}
- prod: {{FILL}}

## Service Discovery
- Backend: {{FILL}}
- Registration/health: {{FILL exact readiness/liveness/DNS patterns}}

## Artifact Types
- Kubernetes: {{FILL manifests/Helm}} 
- Docker Compose overrides: {{FILL}}
- Versioning & rollout strategy: {{FILL canary/blue-green}}

## Secrets & Config
- Source of truth: {{Vault/GitHub Secrets/.env}} 
- Mounting pattern: {{FILL}}

## Deploy Steps (Generic)
1) Build images → tag `git sha`
2) Push images → registry
3) Apply manifests / Helm upgrade with version pin
4) Wait for readiness gates
5) Run smoke tests
6) Notify + tag release

## Rollback
- Command(s): {{FILL}} 
- Criteria to rollback: {{FILL}}
- Data migration rollback: `alembic downgrade -1` (confirm per release)

## Smoke Tests
- URLs/curl/Playwright: {{FILL}}

## Post-Deploy Validation
- Logs clear, error rates normal, health green
