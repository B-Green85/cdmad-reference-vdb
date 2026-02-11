# Security

Security considerations for deploying the CDMAD VDB API on Kubernetes.

## Secrets Management

### Database Credentials

Never pass passwords via CLI flags in production. Use Kubernetes Secrets:

```bash
kubectl create secret generic cdmad-vdb-db-creds \
  --from-literal=POSTGRES_PASSWORD=your-password
```

Reference the existing secret in values:

```yaml
externalDatabase:
  existingSecret: cdmad-vdb-db-creds
  existingSecretKey: POSTGRES_PASSWORD
```

### API Keys

If using OpenAI for embeddings, store the key in a Secret:

```bash
kubectl create secret generic cdmad-vdb-openai \
  --from-literal=OPENAI_API_KEY=sk-...
```

Mount it as an environment variable in the deployment.

## RBAC

The chart creates minimal namespace-scoped RBAC:

- **ServiceAccount** — dedicated identity for the API pods
- **Role** — read-only access to ConfigMaps in the release namespace
- **RoleBinding** — binds the Role to the ServiceAccount

The API does not require any Kubernetes API access. The RBAC is intentionally
minimal. No cluster-level roles or permissions are created.

## Network Security

### No Default Ingress

Ingress is disabled by default. The API is only accessible within the cluster
via its ClusterIP Service. Enable ingress only when external access is needed.

### TLS

When enabling ingress, always configure TLS:

```yaml
ingress:
  enabled: true
  annotations:
    cert-manager.io/cluster-issuer: letsencrypt-prod
  tls:
    - secretName: cdmad-vdb-tls
      hosts:
        - cdmad-vdb.example.com
```

### Database Connections

For external databases, use SSL connections. Configure your Postgres DSN
to require SSL by setting the connection string appropriately in your
external database setup.

## Container Security

The API container runs as the default user in the Python slim image.
For hardened deployments, add a security context:

```yaml
# Add to deployment spec via values or template override
securityContext:
  runAsNonRoot: true
  readOnlyRootFilesystem: true
  allowPrivilegeEscalation: false
  capabilities:
    drop:
      - ALL
```

## What This Chart Does Not Do

Per the CDMAD contract, this chart intentionally avoids:

- **No admission controllers** — no OPA, Gatekeeper, or Kyverno
- **No custom operators** — no CRDs or controller loops
- **No cluster-admin requirements** — everything is namespace-scoped
- **No enforcement logic** — freeze is operational discipline, not automated
- **No multi-tenant features** — single-namespace, single-tenant deployment

## Seed Job Security

The seed job:
- Runs once as a Helm post-install hook
- Must be explicitly enabled (`seed.enabled=true`)
- Supports hash verification of `seed/chunks.json` before writing data
- Does not persist credentials beyond the job lifetime
- Uses the same ServiceAccount as the API

## Audit

Track what is deployed:

```bash
# Check deployed chart version
helm list

# Inspect the running configuration (non-secret values)
helm get values cdmad-vdb

# Review pod security context
kubectl get pods -o jsonpath='{.items[*].spec.securityContext}'
```
