# Quickstart

Deploy CDMAD VDB API to Kubernetes using Helm.

## Prerequisites

- Kubernetes cluster (1.24+)
- Helm 3.x
- `kubectl` configured for your cluster
- Container image built and accessible (see [Building the Image](#building-the-image))

## Building the Image

```bash
docker build -t cdmad-vdb:0.1.0 .
```

If using a remote registry:

```bash
docker tag cdmad-vdb:0.1.0 your-registry/cdmad-vdb:0.1.0
docker push your-registry/cdmad-vdb:0.1.0
```

## Mode B: External Database (Recommended First Deploy)

Use an existing PostgreSQL instance with pgvector installed.

### 1. Prepare Your Database

Ensure your external Postgres has pgvector enabled and migrations applied:

```bash
psql -h <host> -U <user> -d <db> -f db/migrations/001_init.sql
psql -h <host> -U <user> -d <db> -f db/migrations/002_embedding_dim_768.sql
```

### 2. Install the Chart

```bash
helm install cdmad-vdb ./helm/cdmad-vdb \
  --set externalDatabase.host=your-pg-host \
  --set externalDatabase.password=your-pg-password \
  --set image.repository=your-registry/cdmad-vdb
```

### 3. Verify

```bash
kubectl get pods
kubectl port-forward svc/cdmad-vdb 8000:8000
curl http://localhost:8000/health
```

### 4. Seed Data

```bash
helm upgrade cdmad-vdb ./helm/cdmad-vdb \
  --set externalDatabase.host=your-pg-host \
  --set externalDatabase.password=your-pg-password \
  --set image.repository=your-registry/cdmad-vdb \
  --set seed.enabled=true
```

Check seed job status:

```bash
kubectl get jobs -l app.kubernetes.io/component=seed
kubectl logs job/cdmad-vdb-seed
```

## Mode A: In-Cluster Postgres

Deploy Postgres alongside the API. Good for development and testing.

```bash
helm install cdmad-vdb ./helm/cdmad-vdb \
  --set postgres.enabled=true \
  --set seed.enabled=true \
  --set image.repository=your-registry/cdmad-vdb
```

This will:
1. Start a Postgres StatefulSet with persistent storage
2. Run schema migrations automatically via init containers
3. Start the API
4. Run the seed job after install

## Verify the Full Stack

```bash
kubectl port-forward svc/cdmad-vdb 8000:8000

# Health check
curl http://localhost:8000/health

# Query seeded data
curl -X POST http://localhost:8000/v1/query \
  -H "Content-Type: application/json" \
  -d '{"query": "constraint", "k": 3}'
```

## Uninstall

```bash
helm uninstall cdmad-vdb
```

Note: In Mode A, PVCs are retained after uninstall. Delete manually if needed:

```bash
kubectl delete pvc -l app.kubernetes.io/instance=cdmad-vdb
```
