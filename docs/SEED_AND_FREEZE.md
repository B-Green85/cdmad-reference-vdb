# Seed and Freeze

How canonical CDMAD data is seeded into the database and how the dataset
is frozen for operational integrity.

## Seed Overview

Seeding loads the canonical CDMAD chunks from `seed/chunks.json` into the
database via the API's `/v1/docs/upsert` endpoint. The seed process:

1. Reads each chunk from `seed/chunks.json`
2. POSTs it to the running API
3. The API generates embeddings and stores the document

Seeding is **not** part of the runtime application. It runs as a separate
Kubernetes Job.

## Running the Seed Job

The seed job is disabled by default. Enable it during install or upgrade:

```bash
helm install cdmad-vdb ./helm/cdmad-vdb \
  --set seed.enabled=true \
  --set externalDatabase.host=... \
  --set externalDatabase.password=...
```

Or trigger on an existing deployment:

```bash
helm upgrade cdmad-vdb ./helm/cdmad-vdb --reuse-values --set seed.enabled=true
```

The job runs as a Helm `post-install` hook. It waits for the API to pass
health checks before sending data.

## Re-Run Safety

The seed job uses the `/v1/docs/upsert` endpoint, which performs an
INSERT ... ON CONFLICT UPDATE. Re-running the seed:

- Overwrites existing documents with the same content
- Does not create duplicates
- Updates the `updated_at` timestamp
- Re-generates embeddings (which may vary slightly across runs)

This is functionally idempotent: the data content remains the same.

## Hash Verification

To verify the integrity of `seed/chunks.json` before seeding, set the
expected SHA-256 hash:

```bash
# Compute the hash locally
sha256sum seed/chunks.json

# Deploy with verification
helm install cdmad-vdb ./helm/cdmad-vdb \
  --set seed.enabled=true \
  --set seed.expectedHash=abc123...
```

If the hash does not match, the seed job exits with an error without
sending any data to the API.

## Checking Seed Status

```bash
# Job status
kubectl get jobs -l app.kubernetes.io/component=seed

# Job logs
kubectl logs job/cdmad-vdb-seed

# Verify data was seeded
kubectl port-forward svc/cdmad-vdb 8000:8000
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "constraint", "k": 1}'
```

## Freeze

Freezing is an operational discipline, not an automated enforcement
mechanism. A frozen dataset means:

1. **No further writes** — the seed job is not re-run
2. **API remains read-queryable** — queries continue to work
3. **No upsert calls** — production clients should not call `/v1/docs/upsert`

### Implementing Freeze

Freeze is enforced through operational controls:

- **Remove seed.enabled** — ensure seed is not triggered on upgrades
- **Database user permissions** — grant the API user SELECT-only access:

```sql
-- Create a read-only role
CREATE ROLE cdmad_readonly;
GRANT CONNECT ON DATABASE cdmad_vdb TO cdmad_readonly;
GRANT USAGE ON SCHEMA public TO cdmad_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO cdmad_readonly;

-- Assign to the API user
GRANT cdmad_readonly TO cdmad;
REVOKE INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public FROM cdmad;
```

- **Document the freeze** — record the freeze tag and invariants in `FREEZE.md`

### Verifying Freeze

After freezing, verify the API cannot write:

```bash
# This should fail with a database error
curl -X POST http://localhost:8000/v1/docs/upsert \
  -H "Content-Type: application/json" \
  -d '{"id":"test","type":"test","text":"test"}'
```

The API will return a 500 error if the database user lacks write permissions.
