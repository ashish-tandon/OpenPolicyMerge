# Deployment Process (Authoritative, Kubernetes-first)

## Environments
- dev: K8s context `dev` (namespace `openpolicy-dev`)
- staging: K8s context `staging` (namespace `openpolicy-stg`)
- prod: K8s context `prod` (namespace `openpolicy`)

## Service Discovery
- Backend: Kubernetes DNS
- Registration/health: Readiness/Liveness probes on all Deployments; Services expose DNS names.

## Artifact Types
- Kubernetes: Kustomize manifests under deploy/k8s/<env>
- Container images: Built per service; tagged with git SHA and env channel

## Secrets & Config
- Source of truth: GitHub Secrets and/or Vault → projected to K8s Secrets/ConfigMaps
- Mounting pattern: env vars for ports/URLs, volume mounts for credentials as needed

## Deploy Steps (Generic)
1) Build images -> tag git SHA
2) Push images -> registry
3) `kubectl apply -k deploy/k8s/dev` (or staging/prod)
4) Wait for readiness probes to pass
5) Run smoke tests (`scripts/smoke_dev.sh` for dev)
6) Tag release and notify

## Rollback
- `kubectl rollout undo deployment/<name> -n <ns>`
- Criteria to rollback: readiness failures > N minutes, elevated error rates, failing smoke tests
- Data migration rollback: `alembic downgrade -1` (confirm per release)

## Smoke Tests (dev)
- Base URL(s): set via service `ClusterIP` with port-forward OR via Ingress if present
- Example checks:
  - `GET /healthz` -> 200
  - `GET /version` -> 200 with semantic version
  - `GET /bills?page=1` -> 200 and JSON schema shape
