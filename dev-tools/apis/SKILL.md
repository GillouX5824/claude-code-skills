---
name: apis
description: Create production-grade APIs that follow Alter Domus engineering standards. Use this skill when the user asks to build, scaffold, or modify an API — whether it's a GSP (Global Servicing Platform) multi-tenant API or a lightweight Flex API. Handles project setup, routing, authentication patterns, and platform integration. **ALWAYS** Read this skill whenever you're working on a API. No exceptions. You will face issues if you dont. If you didn't read this skill but just realized you're working in a API, immediately stop and READ IT, this is VERY important.
---

# API Development at Alter Domus

## Step 1: Detect the Current Environment

Before doing anything, determine what kind of project you're working in.

### Detection Logic

1. **Detect the language/runtime**:
   - Look for `pyproject.toml` or `uv.lock` → **Python (FastAPI)**
   - Look for `package.json` or `tsconfig.json` → **TypeScript (Express)**
   - Neither found → **New project** (ask the user which stack to use)

2. **Check for GSP SDK references** in the source code:
   - **Python**: Search `pyproject.toml` (or `uv.lock`) for `gsp` dependency (e.g. `gsp-python-api`, `gsp[fastapi]`). Search source files for `from gsp` or `import gsp`.
   - **TypeScript**: Search `package.json` for `@alterdomus/gsp`. Search source files for `from '@alterdomus/gsp'` or `require('@alterdomus/gsp')`.

3. **Classify the environment**:

| Condition | Environment | What to do |
|-----------|-------------|------------|
| No `pyproject.toml`, `package.json`, or source files | **New project** | Ask the user for the stack (Python/TypeScript) and type (GSP/Flex) |
| GSP SDK found in dependencies or imports | **Existing GSP API** | Follow GSP patterns — multi-tenancy, standard errors, GSP SDK integration |
| Project exists but no GSP references | **Existing Flex API** | Follow Flex patterns — minimal platform integration, no default auth |

**Always tell the user which environment and language you detected** before proceeding.

---

## GSP API vs Flex API

There are two types of APIs at Alter Domus:

### GSP API (Recommended Default)

A **GSP (Global Servicing Platform) API** is the standardized, batteries-included API pattern. It integrates with the Alter Domus platform so that developers can **focus purely on their business logic** while the platform handles cross-cutting concerns:

- **Multi-tenancy** — Organization-based data isolation, managed automatically
- **Authentication** — Auth0 token validation handled by Kong + GSP SDK; user/org context injected via FastAPI dependencies
- **Authorization** — Role-based access through the GSP tenant model
- **Standard error format** — Consistent error responses across all platform APIs
- **Foundation API access** — Built-in clients for Tenant, Notification, Workspace, and Billing APIs via the GSP Python SDK
- **Fair usage rate limiting** — Applied automatically at the gateway level
- **CORS** — Configured at the platform level

**Use GSP when:** building any API that serves Alter Domus users or customers, needs multi-tenancy, or benefits from platform integration. This is the default choice.

### Flex API

A **Flex API** is the rawest form of API at Alter Domus. It gives you a blank canvas with only the most basic platform features:

- **Observability** — Sentry error tracking and Grafana dashboards are available
- **Kong gateway** — API is published through Kong for routing
- **Kubernetes hosting** — Deployed via the golden path Helm templates
- **No default authentication** — You must configure your own auth (or none) depending on your use case
- **No multi-tenancy** — No `X-Organization-Id`, no tenant isolation
- **No GSP SDK** — No built-in access to foundation APIs (unless you add it yourself)

**Use Flex when:** building internal tools, infrastructure services, public endpoints, or any API where the GSP multi-tenant model doesn't apply.

---

## Step 2: Apply the Right Pattern

### For New Projects

Ask the user:

> **Is this a GSP API or a Flex API?**
> - **GSP API** (recommended) — Multi-tenant, authenticated, integrated with the Alter Domus platform. Best for APIs serving users or customers.
> - **Flex API** — Minimal platform integration, no default authentication. Best for internal tools, infrastructure, or public endpoints.

Then **ask the user for all project configuration values** before delegating any work. These values are required by the Helm charts, CI/CD pipelines, and Kong configuration — do not guess them.

#### Required Project Configuration

| Variable | Description | Example | Used in |
|----------|-------------|---------|---------|
| **API name** | The service/image name | `todo-api` | Helm `Chart.yaml`, Kong patches, CI/CD `container_image_name` / `chart_name` |
| **App name** | The application group / namespace prefix. Multiple APIs can share the same app name. | `foundation-services` | CI/CD `app_name` / `namespace_prefix`, Kong `DECK_TARGET_NAMESPACE` |
| **Team name** | GitHub team slug for CODEOWNERS and Backstage `owner` | `platform-engineering-team` | `.github/CODEOWNERS`, `catalog-info.yaml` |
| **Backstage system** | The system this API belongs to in Backstage | `foundation-services` | `catalog-info.yaml` |
| **AWS ECR account ID** | AWS account for container registry | `211125459373` | CI/CD pipelines |
| **AWS Secrets account ID** | AWS account for Secrets Manager | `145023093167` | CI/CD pipelines |
| **AWS non-prod account ID** | AWS account for non-prod EKS cluster | `851725580540` | CI/CD pipelines |
| **AWS prod account ID** | AWS account for prod EKS cluster | `881490100256` | CI/CD pipelines |
| **IAM role name** | IAM role for the service account (without `-dev`/`-prd` suffix) | `todo-api` | Helm values (`roleName: <name>-dev-role`) |

The **Kubernetes namespace** is derived automatically: `<app-name>-<env>` (e.g. `foundation-services-dev`, `foundation-services-prd`). This is used in `kong/env/*.sh` as `DECK_TARGET_NAMESPACE` and in the CI/CD deploy pipeline as the `namespace` parameter.

**Pass these values to the agents** when delegating work so they can replace all template placeholders correctly.

### For GSP APIs — Delegate to the `gsp-api-developer` agent

**All GSP API development work must be delegated to the `gsp-api-developer` agent.** This agent has deep knowledge of the GSP platform, SDK patterns, multi-tenancy, authentication, database conventions, and Alter Domus engineering standards.

Use the Task tool to launch the `gsp-api-developer` agent for any GSP work:
- Creating new endpoints
- Modifying existing routes, models, or services
- Adding business logic
- Database models and migrations
- SDK integration

### For Flex APIs

Handle directly using the patterns below and the [API Development skill](skill://api-development:api-development) for full details on project structure, Kong configuration, and Helm setup.

### Infrastructure — Delegate to the `devops-engineer` agent

**All infrastructure and deployment configuration must be delegated to the `devops-engineer` agent.** This includes:
- GitHub Actions workflows (`.github/workflows/`)
- Helm charts and values files (`helm/`)
- Kong gateway configuration (`kong/`)
- Dockerfiles

The API developer agents (`gsp-api-developer` or direct handling for Flex) only touch source code under `src/` and `openapi.yaml`. Everything else is the devops-engineer's responsibility.

### For Existing Projects

Continue with the detected pattern (GSP or Flex). Do not mix patterns unless the user explicitly asks to migrate.

### After bootstrapping or creating a new API

**ALWAYS run the Deployment Readiness Checklist (Step 3) after creating or bootstrapping a new API.** Do not consider the work done until every checklist item passes. This ensures the API has source code, infrastructure, observability, and CI/CD fully configured and ready to deploy from day one.

---

## Common Requirements (Both GSP and Flex)

All Alter Domus APIs must:

- Be written in **Python** (FastAPI + uv) or **TypeScript** (Express + pnpm)
- Be hosted on **Kubernetes** using the golden path Helm templates
- Be published through **Kong** gateway
- Have an **`openapi.yaml`** at the project root
- Have a **`catalog-info.yaml`** at the repository root for Backstage registration

Refer to the [API Development skill](skill://api-development:api-development) for full project structure, Kong configuration, Helm setup, and Backstage catalog details.

### Kong Control Planes

GSP and Flex APIs are published to **different Kong control planes**. The API type determines which control plane to use:

#### GSP APIs

| Environment | Control Plane |
|-------------|---------------|
| dev | `cp-dev-pub-01` |
| qa | `cp-qa-pub-01` |
| sim | `cp-sim-pub-01` |
| sbx | `cp-sbx-pub-01` |
| prd | `cp-prd-pub-01` |

#### Flex APIs

| Environment | Control Plane |
|-------------|---------------|
| dev | `cp-dev-pub-01-flex` |
| qa | `cp-qa-pub-01-flex` |
| sim | `cp-sim-pub-01-flex` |
| prd | `cp-prd-pub-01-flex` |

The control plane name follows the pattern:
- **GSP**: `cp-{env}-pub-01`
- **Flex**: `cp-{env}-pub-01-flex`

This distinction matters when configuring the `deploy-kong` action in CI/CD pipelines. Make sure to use the correct control plane for the API type.

### Kong Directory Structure

All APIs must have a `kong/` directory at the project root with the following structure:

```
kong/
├── env/
│   ├── dev.sh          # Dev namespace targeting
│   └── prd.sh          # Prod namespace targeting
├── patches/
│   └── patches.yaml    # Service routing to Kubernetes
└── plugins/            # Optional — additional Kong plugins
```

#### `kong/env/*.sh` (Required)

`DECK_TARGET_NAMESPACE` is the **Kubernetes namespace** where your service is deployed for that environment. Kong uses this to route traffic to the correct namespace. It follows the pattern `<app-name>-<env>` (e.g. `foundation-services-dev`, `foundation-services-prd`).

**`kong/env/dev.sh`:**
```bash
export DECK_TARGET_NAMESPACE=<app-name>-dev
```

**`kong/env/prd.sh`:**
```bash
export DECK_TARGET_NAMESPACE=<app-name>-prd
```

Create additional env files for other environments as needed (`qa.sh`, `sim.sh`, `sbx.sh`).

#### `kong/patches/patches.yaml` (Required)

Routes Kong traffic to the Kubernetes service. The `host` uses the `DECK_TARGET_NAMESPACE` environment variable to target the correct namespace:

```yaml
_format_version: "1.0"

patches:
  - selectors:
    - $.services[?(@.name=="<api-name>")]
    values:
      host: <api-name>.${{ env "DECK_TARGET_NAMESPACE" }}
      port: 8000
      protocol: http
      path: /
```

Replace `<api-name>` with the service name (must match the service name in `openapi.yaml` and the Helm chart).

#### `kong/plugins/` (Optional)

GSP APIs automatically get these plugins from the shared gateway:
- **OIDC authentication** (Auth0)
- **Rate limiting**
- **CORS**

Flex APIs do **not** get these automatically — you must add your own auth plugins if needed.

You can add additional plugins for either type. Example — request size limiting:

```yaml
# kong/plugins/request-size-limiting.yaml
_format_version: '3.0'
add-plugins:
- selectors:
  - "$..services[0]"
  plugins:
    - name: request-size-limiting
      config:
        allowed_payload_size: 10
        size_unit: megabytes
```

---

## Step 3: Deployment Readiness Checklist

Before an API can be deployed, **all** of the following must be in place. Run this checklist when the user asks to deploy, asks if the project is ready, or after completing a round of development work.

### How to run the checklist

Check each item below. If anything is missing or incomplete, delegate to the appropriate agent to fix it. **Do not proceed with deployment until all items pass.**

### Checklist

| # | Check | How to verify | If missing → delegate to |
|---|-------|---------------|--------------------------|
| 1 | **Source code exists** | `src/` directory contains application code (`.py` or `.ts` files) | `gsp-api-developer` agent (GSP) or handle directly (Flex) |
| 2 | **`openapi.yaml` exists** | File exists at project root and documents all API endpoints | `gsp-api-developer` agent (GSP) or handle directly (Flex) |
| 3 | **`catalog-info.yaml` exists** | File exists at project root with valid Backstage metadata (`name`, `owner`, `system`, `definition.$text`) | `devops-engineer` agent |
| 4 | **`Dockerfile` exists** | File exists at project root, uses multi-stage build, runs as non-root user | `devops-engineer` agent |
| 5 | **Helm charts exist** | `helm/<chart-name>/` contains `Chart.yaml`, `values-dev.yaml`, `values-prd.yaml`, and `templates/` | `devops-engineer` agent |
| 6 | **No template placeholders remain** | Search `helm/` and `.github/workflows/` for `{{ ` — there should be **zero** unresolved `{{ PLACEHOLDER }}` values | `devops-engineer` agent |
| 7 | **Health probes configured** | Helm values include `livenessProbe` (`/healthz`) and `readinessProbe` (`/readyz`) | `devops-engineer` agent |
| 8 | **Init containers (if database)** | If the project uses a database (check for `DB_CONNECTION_STRING`, `AWS_RDS_SECRET`, SQLAlchemy, Prisma), the Helm deployment must have an init container running migrations (`alembic upgrade head` or `prisma migrate deploy`) | `devops-engineer` agent |
| 9 | **Kong configuration exists** | `kong/` directory exists with proper deck configuration | `devops-engineer` agent |
| 10 | **GitHub Actions — validation pipeline** | `.github/workflows/` contains a validation pipeline with `validate-helm-eks` and `deploy-kong` (dry_run) actions | `devops-engineer` agent |
| 11 | **GitHub Actions — deploy pipeline** | `.github/workflows/` contains a deploy pipeline with `deploy-helm-eks` and `deploy-kong` actions, targeting correct environments (`develop` → dev, `release/*` → prd) | `devops-engineer` agent |
| 12 | **Kong control plane is correct** | Deploy pipeline uses the right control plane: `cp-{env}-pub-01` for GSP, `cp-{env}-pub-01-flex` for Flex | `devops-engineer` agent |
| 13 | **CODEOWNERS exists** | `.github/CODEOWNERS` exists with the team slug | `devops-engineer` agent |
| 14 | **Observability configured** | Source code initializes both **Sentry** (error tracking) and **OpenTelemetry** (tracing/metrics). Check for `sentry_sdk.init()`/`Sentry.init()` and `TracerProvider`/`OTLPSpanExporter`/`opentelemetry` imports. Helm values must include `SENTRY_DSN` and `OTEL_EXPORTER_OTLP_ENDPOINT` environment variables. | `gsp-api-developer` agent (source code) + `devops-engineer` agent (Helm env vars) |

### Verification commands

Run these to quickly check the project state:

```bash
# 1. Source code
ls src/

# 2. OpenAPI spec
ls openapi.yaml

# 3. Backstage catalog
ls catalog-info.yaml

# 4. Dockerfile
ls Dockerfile

# 5. Helm charts
ls helm/*/Chart.yaml

# 6. Unresolved template placeholders (should return nothing)
grep -r '{{ ' helm/ .github/workflows/ 2>/dev/null

# 7-8. Helm deployment config (check probes and init containers)
cat helm/*/templates/deployment.yaml

# 9. Kong config
ls kong/

# 10-12. GitHub Actions
ls .github/workflows/

# 13. CODEOWNERS
ls .github/CODEOWNERS

# 14. Observability (Sentry + OpenTelemetry)
grep -r 'sentry_sdk\|Sentry.init\|sentry' src/ 2>/dev/null
grep -r 'opentelemetry\|TracerProvider\|OTLPSpanExporter' src/ 2>/dev/null
grep -r 'SENTRY_DSN\|OTEL_EXPORTER_OTLP_ENDPOINT' helm/ 2>/dev/null
```

### Remediation workflow

When items are missing:

1. **Source code or OpenAPI issues (items 1-2)** → Launch the `gsp-api-developer` agent (for GSP APIs) or fix directly (for Flex APIs)
2. **All infrastructure issues (items 3-13)** → Launch the `devops-engineer` agent with a clear description of what's missing. The devops-engineer will copy golden path templates, create the Dockerfile, set up Kong config, and configure GitHub Actions.
3. **Observability (item 14)** → This spans both agents. Launch `gsp-api-developer` to add Sentry + OpenTelemetry initialization in source code, and `devops-engineer` to add `SENTRY_DSN` and `OTEL_EXPORTER_OTLP_ENDPOINT` to Helm values. See the [Observability skill](skill://observability) for details.

You can run both agents in parallel if both source code and infrastructure items are missing.

---

## Flex API Specifics

Flex APIs have fewer requirements:

1. **Set up observability** — Integrate Sentry for error tracking. See the [Observability skill](skill://observability).

2. **Configure Kong without GSP auth** — No default Auth0 audience; you manage authentication yourself (or omit it).

3. **No GSP SDK required** — Unless you choose to call GSP foundation APIs.

4. **No standard error format required** — Though consistency with the GSP format is encouraged.

---

## Related Skills & Agents

| Resource | When to use |
|----------|-------------|
| **`gsp-api-developer` agent** | **All GSP API development work** — endpoints, models, services, migrations, SDK integration |
| **`devops-engineer` agent** | **All infrastructure work** — GitHub Actions, Helm charts, Kong config, Dockerfiles |
| [GSP](skill://gsp) | Integrating with GSP — getting users, organizations, permissions, sending notifications, managing workspaces, tracking billing, SDK reference |
| [CI/CD](skill://ci-cd) | GitHub Actions pipeline templates, branch strategy, deployment |
| [Kubernetes](skill://kubernetes) | Helm chart templates, cluster topology, values configuration |
| [Observability](skill://observability) | Sentry, OpenTelemetry, Grafana |
