---
name: adi-new-mfe
description: >
  Agentic onboarding for a new ADI Portal micro-frontend. Use this skill when someone
  wants to create a new MFE for the ADI Portal. It replaces the 2-hour manual onboarding
  guide with an automated 20-minute flow. The skill gathers inputs (name, route, port,
  display label) then executes every step: creates the GitHub repo from the golden-path
  template, performs all placeholder substitutions, adds the submodule to adi-portal-meta,
  updates the registry, copies GitHub environment variables from adi-portal-reporting,
  and grants package access, reporting a live link at each step.
  Trigger phrases: "create a new MFE", "scaffold an MFE", "onboard a new MFE",
  "agentic way to create MFE", "new ADI micro-frontend".
version: 1.0.0
---

# ADI New MFE: Agentic Onboarding

This skill automates the [Full Onboarding Guide](https://alterdomus.atlassian.net/wiki/spaces/ADIP/pages/263847952/Adding+a+New+MFE+Full+Onboarding+Guide). It reduces approximately two hours of manual work to a guided twenty-minute flow.

---

## Invocation

```
/adi-new-mfe
```

The skill can also be triggered through natural language requests such as "create a new MFE for the investors module" or "scaffold adi-portal-kyc".

---

## Prerequisites

- GitHub access to the `alterdomus-intelligence` organisation (verify with `gh auth status`)
- Admin access to `adi-portal-meta` and `adi-portal-registry`
- The following information must be agreed before starting:
  - **MFE name**: kebab-case, becomes the repository suffix (e.g. `kyc`, `reporting-v2`)
  - **URL route**: the path users navigate to (e.g. `/kyc`, `/reporting-v2`)
  - **Port**: next available from the port table (currently 3019+)
  - **Display label**: human-readable sidebar name (e.g. `KYC Management`)

---

## Execution

Execute the following phases in sequence, running commands directly. Confirm each phase with the user before proceeding to the next. If a phase fails, report the error and stop.

---

### Phase 1: Gather inputs

Collect the following inputs from the user:

1. **MFE name** (kebab-case, without the `adi-portal-` prefix; for example: `kyc`)
2. **Route** (URL path without a leading slash; for example: `kyc`)
3. **Port** (consult the port table below and suggest the next available value)
4. **Display label** (sidebar text; for example: `KYC Management`)
5. **Squad name** (used in the initial commit message; for example: `Investors Squad`)

Confirm all inputs with the user before proceeding. Store as variables:
- `$NAME`: e.g. `kyc`
- `$ROUTE`: e.g. `kyc`
- `$PORT`: e.g. `3019`
- `$LABEL`: e.g. `KYC Management`
- `$SQUAD`: e.g. `Investors Squad`

### Port assignment table

| MFE | Port |
|-----|------|
| adi-portal-admin | 3004 |
| adi-portal-home | 3005 |
| adi-portal-auth | 3006 |
| adi-portal-ops-center | 3007 |
| adi-portal-portfolio | 3008 |
| adi-portal-funds | 3009 |
| adi-portal-registry | 3010 |
| adi-portal-investors | 3011 |
| adi-portal-documents | 3012 |
| adi-portal-compliance | 3013 |
| adi-portal-account | 3014 |
| adi-portal-reporting | 3015 |
| adi-portal-navigation | 3016 |
| adi-portal-notifications | 3017 |
| adi-portal-zustand | 3018 |
| **next available** | **3019+** |

---

### Phase 2: Create GitHub repository from template

```bash
gh api repos/alterdomus-intelligence/adi-portal-mfe-template/generate \
  --method POST \
  --field owner=alterdomus-intelligence \
  --field name=adi-portal-$NAME \
  --field private=true \
  --field include_all_branches=false
```

Report the new repository URL: `https://github.com/alterdomus-intelligence/adi-portal-$NAME`

---

### Phase 3: Substitute placeholders in the new repository

Clone the new repository into a temporary directory, perform all substitutions, commit, and push.

**Files and substitutions:**

| File | Find | Replace with |
|------|------|-------------|
| `package.json` | `adi-portal-MFENAME` | `adi-portal-$NAME` |
| `vite.config.ts` | `MFENAME` (x2) | `$NAME` |
| `vite.config.ts` | `30XX` (x2) | `$PORT` |
| `src/spa.tsx` | `MFENAME` (x3) | `$NAME` |
| `src/spa.tsx` | `MFEROUTE` | `$ROUTE` |
| `src/App.tsx` | `MFENAME` | `$NAME` |
| `index.html` | `MFENAME` | `$NAME` |
| `public/menu-manifest.json` | `TODO: MFE Display Name` | `$LABEL` |
| `public/menu-manifest.json` | `MFEROUTE` | `$ROUTE` |

After substituting, commit with the following message:
```
chore: initialise adi-portal-$NAME from golden-path template

Squad: $SQUAD

Co-Authored-By: Claude Sonnet 4 <noreply@anthropic.com>
```

Push to `main`, then create the `develop` branch and set it as the default:
```bash
gh api repos/alterdomus-intelligence/adi-portal-$NAME/branches \
  --method POST --field ref=develop --field sha=$(git rev-parse main)
gh api repos/alterdomus-intelligence/adi-portal-$NAME \
  --method PATCH --field default_branch=develop
```

---

### Phase 4: Add submodule to adi-portal-meta

Work inside the `adi-portal-meta` local checkout. Create a branch `feat/add-$NAME-mfe`.

```bash
git submodule add \
  https://github.com/alterdomus-intelligence/adi-portal-$NAME.git \
  adi-portal-$NAME
```

In `pnpm-workspace.yaml`, add:
```yaml
  - adi-portal-$NAME
```

In `scripts/dev.mjs`, add to the concurrently array in port order:
```javascript
{ command: 'pnpm --dir adi-portal-$NAME dev -- --port $PORT', name: '$NAME' },
```
Also add `tcp:$PORT` to the `wait-on` list.

Commit and open a PR to `main` on `adi-portal-meta`. Report the PR URL.

---

### Phase 5: Register in adi-portal-registry

Clone `adi-portal-registry` and create branch `feat/register-$NAME-mfe`.

**`app-registry.json`**: add to the `apps` array:
```json
{
  "name": "@alterdomus-intelligence/adi-portal-$NAME",
  "activeWhen": ["/$ROUTE"],
  "manifestUrl": "https://${SPA_CLOUDFRONT_DOMAIN_NAME}/$NAME/mfe-manifest.json"
}
```

**`app-registry.local.json`**: add:
```json
{
  "name": "@alterdomus-intelligence/adi-portal-$NAME",
  "activeWhen": ["/$ROUTE"],
  "manifestUrl": "http://localhost:$PORT/mfe-manifest.json"
}
```

**`importMap.local.json`**: add inside `imports`:
```json
"@alterdomus-intelligence/adi-portal-$NAME": "http://localhost:$PORT/src/spa.tsx"
```

Commit and open a PR to `develop` on `adi-portal-registry`. Report the PR URL.

---

### Phase 6: Create GitHub environments

Create four environments on the new repository. For each environment (`dev`, `qa`, `sim`, `prd`), copy the shared variables from `adi-portal-reporting`'s matching environment, then set `S3_PREFIX` and `URL_PATH` to the MFE-specific values.

Fetch source variables:
```bash
# Repeat for each of dev, qa, sim, prd
gh api repos/alterdomus-intelligence/adi-portal-reporting/environments/$ENV/variables \
  --jq '.variables[] | select(.name | test("AWS_ACCOUNT_ID|S3_BUCKET|CLOUDFRONT_DISTRIBUTION_ID|SPA_CLOUDFRONT_DOMAIN_NAME|VITE_AUTH0_DOMAIN|VITE_AUTH0_CLIENT_ID"))'
```

Create each environment and set variables:
```bash
# Create environment
gh api repos/alterdomus-intelligence/adi-portal-$NAME/environments/$ENV --method PUT

# Set MFE-specific variables
gh api repos/alterdomus-intelligence/adi-portal-$NAME/environments/$ENV/variables \
  --method POST --field name=S3_PREFIX --field value=$NAME

gh api repos/alterdomus-intelligence/adi-portal-$NAME/environments/$ENV/variables \
  --method POST --field name=URL_PATH --field value=/$ROUTE/
```

**Protection rules**: `qa` and `prd` require reviewers `remiminnebo` and `FranklinSolvasSolutions`.

```bash
gh api repos/alterdomus-intelligence/adi-portal-$NAME/environments/qa \
  --method PUT \
  --field 'reviewers=[{"type":"User","id":<remiminnebo_id>},{"type":"User","id":<FranklinSolvasSolutions_id>}]'
```

Resolve user IDs with `gh api search/users --query remiminnebo` before setting.

---

### Phase 7: Grant package registry access

For each shared package, add the new repository as an allowed consumer:

```bash
for PKG in adi-portal-vite-plugins adi-portal-auth adi-portal-navigation adi-portal-zustand; do
  gh api "orgs/alterdomus-intelligence/packages/npm/%40alterdomus-intelligence%2F$PKG/collaborators/adi-portal-$NAME" \
    --method PUT \
    --field permission=read
done
```

If the API does not support direct package-repository grants, instruct the user to navigate to each package's Settings, then Manage access, then Add repository, for:
`adi-portal-vite-plugins`, `adi-portal-auth`, `adi-portal-navigation`, `adi-portal-zustand`

---

### Phase 8: Final summary

Report a completion summary:

```
adi-portal-$NAME onboarding complete

Repo:        https://github.com/alterdomus-intelligence/adi-portal-$NAME
Meta PR:     <PR URL from Phase 4>
Registry PR: <PR URL from Phase 5>
Route:       /$ROUTE (port $PORT locally)

Pending actions:
- Merge meta PR to main
- Merge registry PR to develop
- Approve qa/prd environment deployments after first dev deploy
- Update public/menu-manifest.json with the correct nav icon if needed

Full guide: https://alterdomus.atlassian.net/wiki/spaces/ADIP/pages/263847952
```

Total estimated time: 15 to 20 minutes.

---

## Reference

- **Template repository**: https://github.com/alterdomus-intelligence/adi-portal-mfe-template
- **Full onboarding guide**: https://alterdomus.atlassian.net/wiki/spaces/ADIP/pages/263847952/Adding+a+New+MFE+Full+Onboarding+Guide
- **Naming schema**: https://alterdomus.atlassian.net/wiki/spaces/ADIP/pages/294649890/ADI+Repository+Naming+Schema
- **adi-portal-meta**: https://github.com/alterdomus-intelligence/adi-portal-meta
- **adi-portal-registry**: https://github.com/alterdomus-intelligence/adi-portal-registry
