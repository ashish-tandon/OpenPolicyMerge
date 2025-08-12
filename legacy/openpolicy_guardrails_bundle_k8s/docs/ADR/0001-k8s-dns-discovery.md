# ADR-0001: Kubernetes DNS as Service Discovery

- Status: Accepted
- Context: Multi-service architecture requires stable discovery; static ports/hosts are brittle.
- Decision: Use Kubernetes DNS with readiness/liveness probes; no hard-coded ports in code.
- Consequences: Requires K8s manifests and environment config discipline.
- Alternatives: Consul, etcd + sidecar; rejected for operational overhead.
- Date: 2025-08-12
