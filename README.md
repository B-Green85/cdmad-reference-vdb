# CDMAD Reference Vector Database API

CDMAD (Constraint-Driven Machine-Assisted Development) is a methodology in which
process constraints are treated as first-class artifacts and enforced externally
from the agents that execute work.

This repository provides the canonical, minimal reference implementation of a
deterministic, vendor-neutral Vector Database API used to store and retrieve
CDMAD policies, playbooks, rules, and command protocols for
retrieval-augmented generation (RAG) by machine agents.

The project includes production-ready Kubernetes scaffolding and a strict
external HTTPS embeddings contract.

The scope is intentionally narrow.

## What This Is

- A deterministic Vector Database API
- A persistence layer for CDMAD knowledge artifacts
- A Kubernetes-ready reference deployment
- A vendor-neutral external embeddings integration
- A fail-fast, constraint-enforcing runtime

## What This Is Not

- An agent framework
- A workflow engine
- A model host or GPU runtime
- An auto-coder
- A UI, dashboard, or SaaS product
- A multi-vendor SDK abstraction layer

Embeddings are treated strictly as an external dependency.

## Kubernetes-Ready Infrastructure

The repository includes a complete Helm chart located at:
`helm/cdmad-vdb/`

The chart provisions:

- API Deployment
- Service
- RBAC
- PostgreSQL (pgvector) StatefulSet
- ConfigMap and Secret wiring
- Seed job
- Deterministic migration configuration

The chart supports both in-cluster and external PostgreSQL modes. Enable in-cluster Postgres via `postgres.enabled=true` for reference deployments.

Embedding settings are injected via Helm values. The chart does not provision model infrastructure.

---

## Architecture
```
External HTTPS Embeddings
            │
            ▼
Client ───▶ API
            │
            │  Validates:
            │  • response shape
            │  • numeric values
            │  • embedding dimension
            ▼
PostgreSQL (pgvector)
```
                                    


Flow:

1. `/v1/docs/upsert` accepts documents
2. API calls configured HTTPS embedding endpoint
3. Embedding response is validated
4. Vector stored in PostgreSQL
5. `/v1/query` performs semantic retrieval

No model hosting occurs in this repository.

---

## External Embeddings Contract

Embeddings are retrieved via a vendor-neutral HTTPS contract.

Required environment variables:

- `EMBEDDING_ENDPOINT_URL`
- `EMBEDDING_MODEL`
- `EMBEDDING_DIMENSION`

Optional:

- `EMBEDDING_RESPONSE_PATH` (default: `data[0].embedding`)
- `EMBEDDING_HEADERS_JSON`
- `EMBEDDING_TIMEOUT_SECONDS`

Validation enforces:

- Response path resolves
- Extracted value is a list
- Elements are numeric
- Length matches configured dimension

Failures are explicit.

---

## Database

PostgreSQL with pgvector is used for persistence.

Vector dimension is configured once and applied in migrations.
No hardcoded embedding sizes exist.

Docker support is provided:

```bash
cp .env.example .env
docker compose up -d
```

Manual migration (local Docker only):
```bash
docker exec -it cdmad-vdb-db psql -U cdmad -d cdmad_vdb -f /migrations/001_init.sql
```
## Local Development

Copy `.env.example` to `.env` and configure your embedding endpoint.

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```
## Seeding Canonical Data
```bash
bash seed/seed.sh
```
The canonical seed provided in this repository represents the reference CDMAD corpus.
Operators may extend or replace this corpus to meet their own governance requirements.

## Proof Pack
```bash
bash scripts/proof_pack.sh
```
Collects a read-only snapshot of current project state for verification.



---
