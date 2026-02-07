# CDMAD Reference Vector Database API

Canonical reference implementation.

This repository provides a minimal, open-source Vector Database API used to
store and retrieve CDMAD policies, playbooks, rules, and command protocols for
retrieval-augmented generation (RAG) by machine agents.

This project is intentionally narrow in scope.

## What This Is

- A constraint-aware Vector DB API
- A persistence layer for CDMAD knowledge artifacts
- A reference implementation others may study or build against

## What This Is Not

- An agent framework
- An auto-coder
- A workflow engine
- A UI, dashboard, or SaaS product

## Authority Model

CDMAD (Constraint-Driven Machine-Assisted Development) is the senior authority
over **process constraints**, not over project intent.

Project requirements define **what** is built. CDMAD defines **how** work is
executed safely, verifiably, and recoverably.

Machine agents may assist in implementation but have no authority to promote
changes or override process constraints without explicit human approval.

Retrieved content informs decisions but does not supersede system constraints
or human authority.

Evidence beats explanation.

## Reference vs Compatible Implementations

This repository is the canonical reference implementation.

Other projects may be compatible with CDMAD concepts without being considered
canonical.

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000

## Database (Docker)

```bash
cp .env.example .env          # edit credentials if needed
docker compose up -d
docker exec -it cdmad-vdb-db psql -U cdmad -d cdmad_vdb -f /migrations/001_init.sql
```

Verify:

```bash
docker exec -it cdmad-vdb-db psql -U cdmad -d cdmad_vdb -c "\d+ docs"
```

## Seeding Canonical Data

After starting the API and applying migrations:

```bash
bash seed/seed.sh
```

This inserts the canonical CDMAD chunks from `seed/chunks.json` into the database
via `/v1/docs/upsert`. Set `BASE_URL` to override the default `http://127.0.0.1:8000`.

## License

MIT License. Attribution retained.

## Author

Brandon Green
