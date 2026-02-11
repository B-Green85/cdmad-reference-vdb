# Claude Build Contract — Kubernetes Scaffolding for CDMAD VDB API

Goal
- Add Kubernetes deployment scaffolding (Helm chart + docs) for the CDMAD VDB API.
- This is packaging, not a rewrite.

Non-goals (forbidden)
- No admission controllers, OPA/Gatekeeper/Kyverno
- No custom operators/controllers
- No multi-tenant SaaS features
- No new business logic inside the API
- No “autoseed on startup” behavior
- No changing API endpoints unless required for readiness/liveness

Deliverables
1) Helm chart at: helm/cdmad-vdb/
   - Deployment (API)
   - Service
   - Optional Ingress (off by default)
   - RBAC (minimal, namespace-scoped)
   - Seed Job (one-time initializer)
   - Optional Postgres (Mode A) behind postgres.enabled

2) Docs under docs/
   - QUICKSTART.md
   - PRODUCTION.md
   - SEED_AND_FREEZE.md
   - SECURITY.md

Seed + Freeze rules
- Seed is a Kubernetes Job, run manually (helm hook or explicit manifest)
- Seed must be safe to re-run (no-op OR fail loudly without mutation)
- Runtime API must NOT perform seeding
- Freeze is operational discipline + optional DB user read-only permissions

Acceptance checks
- helm template renders with defaults
- installs into fresh namespace
- seed job completes once
- API returns constraints after seed
- scale API replicas to 3 without behavior drift
- DB persists across pod restart (Mode A)
- Mode B works with external DB values

Output format
- Keep changes small and reviewable
- Prefer explicit files over clever templates
- Document every value in values.yaml with comments
