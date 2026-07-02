---
name: gsp
description: Global Servicing Platform (GSP) at Alter Domus. Covers both the GSP Developer Platform SDK (users, organizations, notifications, workspaces, billing) and the GSP Fund Administration API (funds, NAV, distributions, investors, capital calls). Use this skill for any GSP integration work.
---

# Global Servicing Platform (GSP)

GSP is Alter Domus's central operational hub. It provides two distinct sets of APIs:

| Area | Purpose | Base URL |
|------|---------|----------|
| **Developer Platform** | Internal platform APIs for building Alter Domus apps — users, orgs, notifications, workspaces, billing | `api.alterdomus.dev/v1` / `api.alterdomus.com/v1` |
| **Fund Administration** | External-facing fund admin workflows — funds, NAV, distributions, investors, capital calls | `api.gsp.alterdomus.com/v2/` |

---

## Part 1 — Developer Platform APIs

The GSP Developer Platform is a suite of foundational APIs that provide common platform capabilities out of the box. Use this when:

- Getting the current user or organization
- Listing users, teams, or service accounts
- Sending notifications (UI alerts or silent data refresh signals)
- Managing workspaces and permissions
- Tracking billing and usage
- Authenticating as a backend service account

### READ THE SDK DOCUMENTATION FIRST

Before writing any GSP Developer Platform integration code, **read the bundled SDK documentation** for the project's language. The SDK docs are the source of truth for available methods, models, and usage patterns.

#### Python

```bash
uv add "gsp[fastapi]" --git https://github.com/AlterDomus/gsp-python-api.git
```

Read the SDK README from the installed package:

```bash
cat $(uv run python -c "import gsp; import os; print(os.path.dirname(gsp.__file__))")/README.md
```

#### TypeScript

```bash
pnpm add @alterdomus/gsp --registry=https://npm.pkg.github.com
```

Ensure `.npmrc` is configured:
```
@alterdomus:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```

Read the SDK README from the installed package:

```bash
cat node_modules/@alterdomus/gsp/README.md
```

---

### Tenant Model

GSP Developer Platform is multi-tenant with two types of tenants:

- **Alter Domus Tenant** — The internal organization for AD applications and services
- **Customer Tenants** — Customer organizations managed separately

#### Admin Portal

| Environment | URL |
|-------------|-----|
| Development | `https://admin.alterdomus.dev` |
| Production | `https://admin.alterdomus.com` |

#### Cross-Tenant Access

| Method | How it works |
|--------|--------------|
| Account Manager role | AD users with `account_manager` role on a customer tenant can manage it |
| Global Access | Service accounts from the AD tenant with "Global Access" enabled can access all customer tenants |

### Environments

| Environment | API Base URL | Auth0 Domain | Audience |
|-------------|--------------|--------------|----------|
| Development | `https://api.alterdomus.dev/v1` | `identity.alterdomus.dev` | `https://api.alterdomus.dev` |
| Production | `https://api.alterdomus.com/v1` | `identity.alterdomus.com` | `https://api.alterdomus.com` |

---

### SDK Quick Reference

**For the full API surface, read the bundled SDK documentation.**

#### Python — FastAPI Dependencies

| Dependency | Returns | Description |
|------------|---------|-------------|
| `get_gsp_client` | `GSPClient` | OBO client — forwards the user's token + `X-Organization-Id` header. Use for actions **as the user**. |
| `get_gsp_backend_client` | `GSPClient` | Backend client — uses service account credentials (client credentials flow). Use for actions **as the API itself** (e.g. sending notifications). Requires `GSP_CLIENT_ID` and `GSP_CLIENT_SECRET` env vars. |

**Important:** Always use the GSP client's `.tenant` accessor to get user/org info. Do **not** use `get_current_user` or `get_current_organization` as standalone FastAPI dependencies.

```python
from fastapi import FastAPI, Depends
from gsp.fastapi import get_gsp_client
from gsp import GSPClient

app = FastAPI()

@app.get("/me")
async def get_me(gsp: GSPClient = Depends(get_gsp_client)):
    user = await gsp.tenant.get_current_user()
    return {"id": user.id, "email": user.email, "name": user.full_name}
```

#### Backend Client (Service Account)

```python
from fastapi import Depends
from gsp.fastapi import get_gsp_backend_client
from gsp import GSPClient
from gsp.models import NotificationTarget

@app.post("/process")
async def process_item(gsp: GSPClient = Depends(get_gsp_backend_client)):
    await gsp.notifications.send_ui(
        domain="my-api",
        target=NotificationTarget(user_id="user-id"),
        title="Action completed",
        content="Your request has been processed.",
        type="success",
    )
```

#### Available API Clients

| Client | Access via | What it does |
|--------|-----------|--------------|
| Tenant | `client.tenant` | Users, organizations, teams, service accounts, branding |
| Notifications | `client.notifications` | Send/list/read/delete notifications |

#### Configuration

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `GSP_BASE_URL` | GSP API base URL | `https://api.alterdomus.dev/v1` |
| `GSP_CLIENT_ID` | Service account client ID (for backend client) | - |
| `GSP_CLIENT_SECRET` | Service account client secret (for backend client) | - |
| `GSP_AUTH_DOMAIN` | Auth0 domain (auto-detected from `GSP_BASE_URL`) | - |
| `GSP_AUDIENCE` | API audience (auto-detected from `GSP_BASE_URL`) | - |

---

### Authentication Flow (Developer Platform)

1. Client obtains token from Auth0
2. Client sends request to Kong with `Authorization: Bearer <token>`
3. Kong validates token and extracts identity
4. Service uses GSP SDK to get user/org details

#### Tenant Switching

Use `X-Organization-Id` header to operate on a different tenant. Requires `account_manager` role or Global Access.

#### Backend Service Account Configuration

```yaml
environment:
  values:
    GSP_CLIENT_ID: <service-account-client-id>

secrets:
  values:
    app_secrets:
      subkeys:
        - key: "GSP_CLIENT_SECRET"
```

---

### Error Handling

```python
import httpx

try:
    user = await gsp.tenant.get_user("invalid-id")
except httpx.HTTPStatusError as e:
    if e.response.status_code == 404:
        print("User not found")
    elif e.response.status_code == 403:
        print("Access denied")
```

Standard error format:

```json
{
  "error": {
    "code": "FORBIDDEN",
    "message": "Insufficient permissions"
  }
}
```

---

### Roles

| Role | Description |
|------|-------------|
| `enterprise_administrator` | Full admin access |
| `account_manager` | Manage accounts and service accounts |
| `ad_service_account` | Alter Domus internal service account with global access |

### Pagination (Developer Platform)

| Parameter | Description |
|-----------|-------------|
| `limit` | Number of items per page |
| `offset` | Number of items to skip |
| `sort` | Field to sort by |
| `order` | Sort order (asc/desc) |

---

### GSP Developer Platform APIs Overview

#### Tenant API (`client.tenant`)

Manage users, organizations, teams, service accounts, and branding — current user and organization, user listing and lookup, organization profiles and roles, team management and membership, service account creation and credentials, branding configuration.

#### Notification API (`client.notifications`)

Send real-time notifications to users. Two types:

| Type | Purpose |
|------|---------|
| `ui` | Visible alert in the notification center |
| `silent` | Data refresh signal to frontends — not displayed to users |

Notification targets (exactly one must be specified): `organization_id`, `user_id`, `team_id`, `workspace_id`.

#### Workspaces API

Manage workspaces, permissions, and enabled services within organizations. Workspace roles: `user`, `contributor`, `admin`. Available services: `DataHub`, `DomusDocs`.

#### Billing API

Track costs and usage across services. Any service can integrate by posting transactions with a `source_application` identifier. Supports aggregated summaries and flexible analytics reports.

---

## Part 2 — Fund Administration API

The GSP Fund Administration API is AlterDomus's external-facing API for fund admin workflows. It consolidates fund administration, investor services, and reporting across all platforms and client-facing applications.

### Core Domain Concepts

| Concept | Description |
|---------|-------------|
| **Fund** | A legal investment vehicle administered through GSP. Identified by a `fundId` (UUID). |
| **Share Class** | A sub-division of a fund with distinct fee structures and investor rights. |
| **Investor** | A legal entity or individual holding shares in one or more funds. |
| **NAV** | Net Asset Value — the per-share value of a fund, published on a defined frequency. |
| **Distribution** | A cash payment (dividend, return of capital, etc.) made from a fund to investors. |
| **Reporting Period** | A fixed calendar window (monthly, quarterly, annual) used for NAV and statements. |
| **Commitment** | An investor's contractual pledge to contribute capital to a fund over time. |
| **Capital Call** | A draw-down request issued against an investor's unfunded commitment. |

### Environments

| Environment | Base URL |
|-------------|----------|
| Production | `https://api.gsp.alterdomus.com/v2/` |
| Sandbox | `https://api-sandbox.gsp.alterdomus.com/v2/` |

Sandbox credentials are issued separately. Seed data is refreshed nightly. Use sandbox for all automated tests and CI pipelines.

### Authentication (Fund Admin API)

OAuth 2.0 Client Credentials flow for service-to-service calls:

```
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id={CLIENT_ID}
&client_secret={CLIENT_SECRET}
&scope=gsp:read gsp:write
```

Tokens expire after 3600 s. Refresh proactively before expiry.

#### Common Headers

```
Authorization: Bearer {access_token}
x-api-version: 2024-01
x-correlation-id: {uuid}        # propagate from upstream request
Content-Type: application/json
```

### Pagination (Fund Admin API)

Cursor-based pagination on all list endpoints:

```json
{
  "data": [...],
  "pagination": {
    "nextCursor": "eyJpZCI6...",
    "hasMore": true,
    "totalCount": 1042
  }
}
```

Pass `?cursor={nextCursor}&pageSize=100` on subsequent requests. Always iterate until `hasMore` is `false`.

### Error Envelope (Fund Admin API)

```json
{
  "error": {
    "code": "FUND_NOT_FOUND",
    "message": "No fund exists with id 'abc-123'.",
    "requestId": "7f3a2c...",
    "details": {}
  }
}
```

Map `error.code` to domain exceptions in your service layer — never expose raw GSP error messages directly to end users.

### Key Endpoint Groups

| Group | Base Path | Notes |
|-------|-----------|-------|
| Funds | `/v2/funds` | CRUD + share-class sub-resources |
| Investors | `/v2/investors` | Linked to funds via `/v2/funds/{id}/investors` |
| NAV | `/v2/funds/{id}/nav` | Published NAV per reporting period |
| Distributions | `/v2/funds/{id}/distributions` | Paginated; filterable by date range |
| Capital Calls | `/v2/funds/{id}/capital-calls` | Includes commitment linkage |
| Documents | `/v2/documents` | Signed URL generation for investor statements |
| Webhooks | `/v2/webhooks` | Event subscriptions (NAV published, distribution paid, etc.) |

### Integration Patterns

#### Fetching all NAV entries for a fund

```python
cursor = None
nav_records = []

while True:
    params = {"pageSize": 200}
    if cursor:
        params["cursor"] = cursor

    resp = gsp_client.get(f"/v2/funds/{fund_id}/nav", params=params)
    resp.raise_for_status()
    body = resp.json()

    nav_records.extend(body["data"])

    if not body["pagination"]["hasMore"]:
        break
    cursor = body["pagination"]["nextCursor"]
```

#### Webhook event handling

Subscribe to relevant events at `/v2/webhooks`. GSP sends a signed `POST` to your endpoint:

```
x-gsp-signature: sha256={hmac}
x-gsp-event-type: nav.published
```

Verify the HMAC with your webhook secret before processing. Respond `200 OK` within 5 s; enqueue heavy processing asynchronously.

### Environment Variables (Fund Admin API)

| Variable | Purpose |
|----------|---------|
| `GSP_CLIENT_ID` | OAuth client ID |
| `GSP_CLIENT_SECRET` | OAuth client secret |
| `GSP_API_BASE_URL` | Base URL (override for sandbox) |
| `GSP_WEBHOOK_SECRET` | HMAC key for webhook signature verification |
| `GSP_API_VERSION` | Default: `2024-01` |
