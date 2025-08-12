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
- Helm charts: Available under helm/openpolicy/ for advanced deployments

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

## Helm Deployment (Alternative)
1) Update values.yaml with new image tags
2) `helm upgrade --install openpolicy helm/openpolicy -f values.yaml`
3) Verify deployment with `helm status openpolicy`
4) Run smoke tests

## Rollback
- `kubectl rollout undo deployment/<name> -n <ns>`
- Criteria to rollback: readiness failures > N minutes, elevated error rates, failing smoke tests
- Data migration rollback: `alembic downgrade -1` (confirm per release)

## Smoke Tests
- **Dev**: `scripts/smoke_dev.sh` (port-forward based)
- **Staging**: `scripts/smoke_staging.sh` (exec-based)
- **Production**: `scripts/smoke_prod.sh` (exec-based)

## Pre-Deployment Validation
- `kubectl apply -k deploy/k8s/dev --dry-run=server`
- `helm template helm/openpolicy --dry-run`
- Image security scans
- Manifest validation
