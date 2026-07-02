---
name: kubernetes
description: Kubernetes deployment patterns at Alter Domus. Use this skill when configuring Helm charts, understanding cluster topology, setting up secrets, autoscaling, health probes, or configuring environment-specific values for Kubernetes workloads.
---

# Kubernetes Deployment at Alter Domus

All workloads at Alter Domus run on AWS EKS (Elastic Kubernetes Service) and are deployed via Helm charts.

## Clusters

| Environment | Cluster | Region | Nodes taint (x86) | Nodes taint (ARM64) |
|-------------|---------|--------|-------------------|---------------------|
| dev | `eks-ceu-nonprd-shared-01` | `eu-central-1` | `env=dev:NoSchedule` | `env=dev-arm64:NoSchedule` |
| qa | `eks-ceu-nonprd-shared-01` | `eu-central-1` | `env=qa:NoSchedule` | `env=qa-arm64:NoSchedule` |
| sim | `eks-ceu-nonprd-shared-01` | `eu-central-1` | `env=sim:NoSchedule` | `env=sim-arm64:NoSchedule` |
| sbx | `eks-ceu-nonprd-shared-01` | `eu-central-1` | `env=sbx:NoSchedule` | `env=sbx-arm64:NoSchedule` |
| prd | `eks-ceu-prd-shared-01` | `eu-central-1` | `env=prd:NoSchedule` | `env=prd-arm64:NoSchedule` |

Non-production environments (dev, qa, sim, sbx) share the same cluster. Production has its own dedicated cluster.

**ARM64 nodes are preferred.** Build ARM64-compatible images and use the `-arm64` taint suffix to schedule on ARM64 nodes for better cost efficiency and performance.

### Namespaces

Workloads are deployed to namespaces following the pattern: `{app_name}-{environment}`

Example: `foundation-services-dev`, `foundation-services-prd`

## Helm Chart Structure

```
helm/
└── my-workload/
    ├── Chart.yaml
    ├── values-dev.yaml           # Development configuration
    ├── values-prd.yaml           # Production configuration
    └── templates/
        ├── _helpers.tpl          # Helm template helpers
        ├── deployment.yaml       # Kubernetes Deployment
        ├── service.yaml          # Kubernetes Service
        ├── configmap.yaml        # Environment variables
        ├── serviceaccount.yaml   # AWS IAM role binding (IRSA)
        ├── hpa.yaml              # Horizontal Pod Autoscaler
        └── aws-secretprovider.yaml  # AWS Secrets Manager integration
```

**Golden path templates** are included in this skill at `templates/helm/`. These are the recommended starting point — copy them to your project and adapt as needed:

```bash
cp -r .claude/skills/kubernetes/templates/helm helm/<your-workload-name>
```

Then update `Chart.yaml`, `values-dev.yaml`, and `values-prd.yaml` with your service-specific values (replace `{{ SERVICE_NAME }}`, `{{ AWS_ACCOUNT_ID }}`, etc.).

**These templates are a starting point, not a rigid contract.** They can be modified to accommodate the workload's needs — init containers, extra volumes, sidecars, custom probes, additional templates, etc. The golden path provides the baseline; the workload dictates the final shape.

**Only the `devops-engineer` agent should create or modify Helm charts and values files.** Other agents (e.g. `gsp-api-developer`) must not touch files under `helm/`.

## Values Configuration

Each environment has its own values file (`values-dev.yaml`, `values-prd.yaml`, etc.). Below are the key configuration sections.

### Environment Variables

Application environment variables are set via ConfigMap:

```yaml
environment:
  enabled: true
  values:
    APP_ENV: production
    DEPLOY_ENV: development  # "development" for dev, "production" for prd
    LOG_LEVEL: info
```

### Secrets (AWS Secrets Manager)

Secrets are stored in AWS Secrets Manager and mounted automatically via the CSI Secrets Store driver:

```yaml
secrets:
  enabled: true
  aws:
    prefix: my-service/dev  # Path prefix in Secrets Manager
  values:
    my_secrets:
      subkeys:
        - key: "DATABASE_PASSWORD"
        - key: "API_KEY"
```

At runtime, each `key` becomes an environment variable with the value from Secrets Manager.

### Resources

Always set CPU and memory requests/limits:

```yaml
resources:
  limits:
    cpu: 800m
    memory: 600Mi
  requests:
    cpu: 400m
    memory: 600Mi
```

### Autoscaling (HPA)

```yaml
autoscaling:
  enabled: true
  minReplicas: 2
  maxReplicas: 10
  targetCPUUtilizationPercentage: 80
```

### Service

```yaml
service:
  type: ClusterIP
  port: 8000
  containerPort: 8000
```

### Health Probes

Configure liveness and readiness probes:

```yaml
livenessProbe:
  httpGet:
    path: /healthz
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 30

readinessProbe:
  httpGet:
    path: /readyz
    port: 8000
  initialDelaySeconds: 15
  periodSeconds: 20
```

### Tolerations

Nodes are tainted per environment. **You must add tolerations** or pods will not be scheduled.

**ARM64 is preferred.** Use `-arm64` suffix for ARM64 nodes:

```yaml
# Dev environment (ARM64 — preferred)
tolerations:
  - key: "env"
    operator: "Equal"
    value: "dev-arm64"
    effect: "NoSchedule"

# Production environment (ARM64 — preferred)
tolerations:
  - key: "env"
    operator: "Equal"
    value: "prd-arm64"
    effect: "NoSchedule"
```

For x86 images (only if ARM64 is not possible):

```yaml
# Dev environment (x86)
tolerations:
  - key: "env"
    operator: "Equal"
    value: "dev"
    effect: "NoSchedule"
```

### AWS IAM Role (IRSA)

Service accounts are annotated with an IAM role ARN for AWS access (ECR, Secrets Manager, RDS, etc.):

```yaml
cloud:
  enabled: true
  type: aws
  aws:
    region: eu-central-1
    accountId: "123456789012"
    roleName: my-workload-dev-role
```

This creates a Kubernetes ServiceAccount with `eks.amazonaws.com/role-arn` annotation.

### Volumes

```yaml
volumes:
  enabled: true
  values:
    - name: my-volume
      mountPath: /data
```

## Environment Differences

| Setting | Dev | Production |
|---------|-----|------------|
| Values file | `values-dev.yaml` | `values-prd.yaml` |
| `DEPLOY_ENV` | `development` | `production` |
| Secrets prefix | `my-service/dev` | `my-service/prd` |
| IAM role | `*-dev-role` | `*-prd-role` |
| Tolerations value | `dev-arm64` (preferred) / `dev` | `prd-arm64` (preferred) / `prd` |
| Auth0 domain | `identity.alterdomus.dev` | `identity.alterdomus.com` |
| API base URL | `https://api.alterdomus.dev` | `https://api.alterdomus.com` |
| Cluster | `eks-ceu-nonprd-shared-01` | `eks-ceu-prd-shared-01` |

## Database Migrations as Init Containers

If the workload uses a database, run migrations as an init container so they complete before the app starts:

```yaml
# In deployment.yaml template
initContainers:
  - name: migrate
    image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
    command: ["alembic", "upgrade", "head"]        # Python (Alembic)
    # command: ["pnpm", "exec", "prisma", "migrate", "deploy"]  # TypeScript (Prisma)
    envFrom:
      - configMapRef:
          name: {{ include "my-workload.fullname" . }}
    # Same secret mounts as the main container
```

The init container uses the same image and has access to the same environment variables and secrets as the main container.

## Related Skills

| Skill | When to use |
|-------|-------------|
| [CI/CD](skill://ci-cd) | GitHub Actions pipelines that deploy to these clusters |
| [APIs](skill://apis) | API-specific patterns (GSP vs Flex, Kong control planes) |
