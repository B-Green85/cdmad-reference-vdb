# Production Deployment

Guidelines for running CDMAD VDB API in production Kubernetes environments.

## Mode B (External Database) is Recommended

Production deployments should use Mode B with a managed PostgreSQL service
(e.g., AWS RDS, GCP Cloud SQL, Azure Database for PostgreSQL). This provides:

- Automated backups and point-in-time recovery
- High availability and failover
- Connection pooling at the infrastructure level
- Separation of compute and storage lifecycle

## Image Registry

Push the image to a private registry accessible from your cluster:

```bash
docker build -t your-registry/cdmad-vdb:0.1.0 .
docker push your-registry/cdmad-vdb:0.1.0
```

If your registry requires authentication:

```yaml
imagePullSecrets:
  - name: my-registry-secret
```

## Resource Limits

Set explicit resource requests and limits:

```yaml
resources:
  requests:
    cpu: 100m
    memory: 256Mi
  limits:
    cpu: 500m
    memory: 512Mi
```

## Replicas and Scaling

The API is stateless and safe to scale horizontally:

```yaml
replicaCount: 3
```

All replicas connect to the same database. No coordination is needed between
replicas. Scaling does not cause behavior drift.

## Using Existing Secrets

Do not pass passwords via `--set`. Use an existing Kubernetes Secret:

```bash
kubectl create secret generic cdmad-vdb-db-creds \
  --from-literal=POSTGRES_PASSWORD=your-secure-password
```

```yaml
externalDatabase:
  existingSecret: cdmad-vdb-db-creds
  existingSecretKey: POSTGRES_PASSWORD
```

## Ingress

Enable and configure ingress for external access:

```yaml
ingress:
  enabled: true
  className: nginx
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  hosts:
    - host: cdmad-vdb.example.com
      paths:
        - path: /
          pathType: Prefix
  tls:
    - secretName: cdmad-vdb-tls
      hosts:
        - cdmad-vdb.example.com
```

## Health Probes

The chart configures liveness and readiness probes against `/health`.
The `/health` endpoint returns `{"status": "ok"}` and verifies the API
process is running. Adjust timing if your container takes longer to start:

```yaml
# In deployment.yaml overrides (via values if customized)
livenessProbe:
  initialDelaySeconds: 10
  periodSeconds: 15
readinessProbe:
  initialDelaySeconds: 5
  periodSeconds: 10
```

## Namespace Isolation

Deploy into a dedicated namespace:

```bash
kubectl create namespace cdmad
helm install cdmad-vdb ./helm/cdmad-vdb -n cdmad \
  --set externalDatabase.host=... \
  --set externalDatabase.password=...
```

## Embedding Provider

For production, use OpenAI embeddings:

```yaml
api:
  embeddingProvider: openai
  embeddingModel: text-embedding-3-small
openaiApiKey: "sk-..."
```

Or mount the API key from an existing secret and set the `OPENAI_API_KEY`
env var via additional environment configuration.

## Monitoring

The API exposes:
- `GET /health` — basic liveness check
- `GET /` — service status

Integrate with your existing monitoring by probing these endpoints.
