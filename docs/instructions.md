# RUN_PLAYBOOK

SCOPE OF TRUTH (MUST READ)
- Primary: docs/UNIFIED_SERVICE_REFERENCE.md
- This file: docs/instructions.md (procedures)
- Architecture: docs/architecture.md (diagram + overview)
- Deployment: docs/DEPLOYMENT_PROCESS.md
- Legacy: docs/LEGACY/** (read-only)

HARD RULES
- Kubernetes-first: no docker-compose in core flow.
- No manual board/port checks; all service resolution via Kubernetes DNS.
- No breaking API changes; spec-first.
- PostgreSQL only; all schema via Alembic with downgrade.
- Tests required: unit + contract; ETL data checks.

USAGE
- RUN_PLAYBOOK: continue
- RUN_PLAYBOOK: micro <target>
- RUN_PLAYBOOK: recovery
- RUN_PLAYBOOK: pre-pr

-------------------------------------------------------------------------------
MODE: CONTINUE  (RUN_PLAYBOOK: continue)
1) NEXT STEP: docs/PROJECT_PLAN.md or Kanban → pick the single next increment.
2) DISCOVERY COMPLIANCE: remove/replace any hard-coded host:port in scope; verify health/registration via K8s readiness/liveness and DNS svc names.
3) SPEC-FIRST (if API): update openapi.yaml before code.
4) IMPLEMENT:
   - API: pydantic models, router, service layer (no SQL in handlers).
   - ETL: idempotent upsert; retries; metrics.
   - UI: typed client; behind feature flag when replacing old calls.
5) TESTS:
   - Unit tests for new modules.
   - Contract tests vs openapi.yaml.
   - ETL data tests (row counts, nulls, FKs).
6) DB: create Alembic migration; ensure downgrade works.
7) LINT/TYPE: ruff, black --check, eslint, tsc --noEmit (and go vet/staticcheck if Go).
8) LOCAL DEV/DEV CLUSTER:
   - Build images and push to registry (dev tag).
   - kubectl apply -k deploy/k8s/dev --dry-run=server (validate manifests).
   - OPTIONAL: kubectl apply -k deploy/k8s/dev && scripts/smoke_dev.sh
9) DOCS: update docs/ARCHITECTURE_IMPLEMENTATION_STATUS.md & docs/REFERENCE/omitted.md.
10) OUTPUT: code diff summary, test summary, migration paths, ADR (if any), CHANGELOG (Unreleased), confirmation of discovery-compliant endpoints.

-------------------------------------------------------------------------------
MODE: MICRO  (RUN_PLAYBOOK: micro <target>)
- Minimal slice only; spec-first if API.
- Unit + contract tests.
- K8s dev dry-run apply (if manifests changed).
- 5-line Summary, Risks, Next step.
- Reject scope creep.

-------------------------------------------------------------------------------
MODE: RECOVERY  (RUN_PLAYBOOK: recovery)
1) STATUS REPORT: files changed last run; failing tests; Alembic heads.
2) RECONCILE with openapi.yaml, .cursorrules, UNIFIED_SERVICE_REFERENCE.md.
3) BRANCH if needed: recover/<timestamp>.
4) FIX TESTS FIRST; no new features.
5) Resume CONTINUE when green.

-------------------------------------------------------------------------------
MODE: PRE-PR  (RUN_PLAYBOOK: pre-pr)
Artifacts required:
- Updated openapi.yaml (if API touched)
- Alembic migrations + downgrades (if DB touched)
- Unit + contract tests; ETL data checks (if ETL touched)
- ADR for any decision change
- CHANGELOG Unreleased entry
Static gates: ruff, black --check, eslint, tsc --noEmit, go vet/staticcheck (if Go)
Coverage thresholds met
K8s checks: build images; kubectl apply -k deploy/k8s/dev --dry-run=server
PRE-PR SUMMARY must include: Changes, Risks & rollback, Manual checks, Endpoints touched, DB objects

-------------------------------------------------------------------------------
TEMPLATES

BLOCKER REPORT
- Step failed:
- Action/command:
- Error/output (trim):
- Suspected cause:
- Options A/B/C:
- Recommendation:
- Inputs needed:

PRE-PR SUMMARY
- Changes:
- Risks:
- Rollback:
- Manual checks:
- Endpoints touched:
- DB objects:

RELEASE NOTES (CHANGELOG fragment)
- feat/fix/chore: <one-liner>
- Impact: <api/db/ui/etl>
- Migrations: <file(s)>
- Notes: <breaking? flags?>
