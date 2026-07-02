---
name: adi-mfe
description: >
  Use this skill when working on the ADI Portal microfrontend platform. Triggers on any
  request involving ADI MFE development: setting up or running a local dev environment,
  configuring vite.config.ts, using the MFE override panel against the deployed CloudFront
  shell, fixing CI build failures (lockfile, TypeScript errors), wiring up Auth0 via
  adi-portal-auth, handling cross-MFE navigation, configuring HTTPS for local dev,
  understanding the single-spa architecture, branching and deployment workflow, or applying
  the Alter Domus brand system. Provides authoritative knowledge of the platform
  architecture, port assignments, standard patterns, and known failure modes.
version: 1.0.0
---

# ADI Portal: Microfrontend Development

The ADI Portal is a **single-spa** micro-frontend platform. Each squad owns their MFE end-to-end, from local development to independent deployment on AWS CloudFront and S3, with no dependency on another squad's code.

Official documentation: https://alterdomus.atlassian.net/wiki/spaces/ADIP/pages/213024773/ADI+-+Developing+Micro+Frontends

---

## Architecture

```
Browser
  └─ Loads shell/index.html from CloudFront
       └─ Shell fetches registry/app-registry.json
            └─ For each MFE: fetches /mfe-manifest.json to get entry JS URL
                 └─ single-spa registers the MFE
                      └─ On route match: loads MFE JS bundle
                           └─ MFE mounts into #single-spa-application:main
```

All `@alterdomus-intelligence/*` packages (auth, vite-plugins) are **external**; they are resolved at runtime via the import map and are never bundled into an MFE.

---

## Repo Map and Port Assignments

| Submodule | Package name | Dev port | Route / purpose |
|-----------|-------------|----------|-----------------|
| `adi-portal-shell` | `@alterdomus-intelligence/adi-portal-shell` | 3000 | Root app: layout, auth, routing |
| `adi-portal-auth` | `@alterdomus-intelligence/adi-portal-auth` | 3001 | Shared Auth0 library (runtime only) |
| `adi-portal-registry` | `@alterdomus-intelligence/adi-portal-registry` | 3010 | Import map and app registry |
| `adi-portal-home` | `@alterdomus-intelligence/adi-portal-home` | 3005 | `/home`: dashboard |
| `adi-portal-admin` | `@alterdomus-intelligence/adi-portal-admin` | 3004 | `/admin`: admin console |
| `adi-portal-account` | `@alterdomus-intelligence/adi-portal-account` | 3014 | `/account`: profile and settings |
| `adi-portal-ops-center` | `@alterdomus-intelligence/adi-portal-ops-center` | 3007 | `/ops-center` |
| `adi-portal-portfolio` | `@alterdomus-intelligence/adi-portal-portfolio` | 3008 | `/portfolio` |
| `adi-portal-funds` | `@alterdomus-intelligence/adi-portal-funds` | 3009 | `/funds` |
| `adi-portal-investors` | `@alterdomus-intelligence/adi-portal-investors` | 3011 | `/investors` |
| `adi-portal-documents` | `@alterdomus-intelligence/adi-portal-documents` | 3012 | `/documents` |
| `adi-portal-compliance` | `@alterdomus-intelligence/adi-portal-compliance` | 3013 | `/compliance` |
| `adi-portal-reporting` | `@alterdomus-intelligence/adi-portal-reporting` | 3015 | `/reporting` |
| `adi-portal-vite-plugins` | `@alterdomus-intelligence/adi-portal-vite-plugins` | n/a | Shared Vite plugins (GitHub Packages) |
| `adi-aws-infrastructure` | n/a | n/a | Terraform: CloudFront and S3 |

### Getting started

```bash
git clone --recurse-submodules https://github.com/alterdomus-intelligence/adi-portal-meta.git
cd adi-portal-meta
cp adi-portal-shell/.env.local.example adi-portal-shell/.env.local
# Set VITE_AUTH0_DOMAIN and VITE_AUTH0_CLIENT_ID
pnpm install && pnpm dev   # http://localhost:3000
```

To run a single MFE standalone:
```bash
cd adi-portal-funds && pnpm install && pnpm dev   # https://localhost:3009
```

---

## MFE Override Panel

The override panel allows any deployed MFE to be pointed at a local dev server, without running the full local stack.

**Dev CloudFront URL:** `https://dww1y1fc4a3sj.cloudfront.net`

The `DEV` tab appears at the bottom-right of the dev environment (auto-hides, green badge when active). It is available on **dev** only; it is compiled out on QA, sim, and prd.

### Instructions

1. Open `https://dww1y1fc4a3sj.cloudfront.net`
2. Click `DEV` and find the target MFE, enter the local port, then click **Apply**
3. Start the local dev server: `pnpm dev` in the MFE repository
4. On first use: open `https://localhost:PORT` in a new tab and accept the self-signed certificate

Overrides persist in `localStorage['mfe-manifest-overrides']`. Click **Clear** or **Reset all** to remove them.

### Why HTTPS on localhost

The CloudFront shell is served over HTTPS. A plain `http://localhost` dev server triggers a browser mixed-content block. `@vitejs/plugin-basic-ssl` (included in every MFE's `devDependencies`) adds a self-signed certificate so Vite serves on `https://localhost:PORT`.

---

## Standard `vite.config.ts` Pattern

```ts
import path from 'node:path'
import { defineConfig, type Plugin, type UserConfig } from 'vite'
import react from '@vitejs/plugin-react'
import vitePluginSingleSpa from 'vite-plugin-single-spa'
import basicSsl from '@vitejs/plugin-basic-ssl'
// import tailwindcss from '@tailwindcss/vite'  // home, admin, account, reporting only

const LOCAL_IMPORT_MAP = path.resolve(__dirname, '../adi-portal-registry/importMap.local.json')

const singleSpaPreambleBypass: Plugin = {
  name: 'single-spa-preamble-bypass',
  enforce: 'post',
  apply: 'serve',
  transform(code, id) {
    if (!id.includes('node_modules') && (id.endsWith('.tsx') || id.endsWith('.jsx'))) {
      return code.replace(
        /if\s*\(!window\.\$RefreshReg\$\)\s*\{[^}]*throw[^}]*\}/,
        '/* single-spa: preamble bypass */',
      )
    }
  },
}

const hashMfeEntry: Plugin = {
  name: 'hash-mfe-entry',
  outputOptions(opts) { opts.entryFileNames = 'assets/[name]-[hash].js'; return opts },
}

export default defineConfig(async (): Promise<UserConfig> => {
  let mfePlugins: Plugin[] = []
  try {
    const pkg = '@alterdomus-intelligence/adi-portal-vite-plugins'
    const vp = await import(pkg)
    mfePlugins = [
      vp.mfeResolverPlugin({ localImportMapPath: LOCAL_IMPORT_MAP }),
      vp.mfeManifestPlugin({ spaEntryPoint: 'src/spa.tsx' }),
    ]
  } catch (err) {
    if ((err as NodeJS.ErrnoException).code !== 'ERR_MODULE_NOT_FOUND') throw err
  }

  return {
    plugins: [
      basicSsl(),
      // tailwindcss(),
      react(),
      singleSpaPreambleBypass,
      ...mfePlugins,
      vitePluginSingleSpa({ serverPort: PORT, spaEntryPoints: 'src/spa.tsx' }),
      hashMfeEntry,
    ],
    server: { port: PORT, cors: true },
    build: {
      rollupOptions: {
        external: ['single-spa', /^@alterdomus-intelligence\/.+/],
      },
    },
  }
})
```

### Vite 7 known issues

| Issue | Root cause | Fix |
|-------|-----------|-----|
| `TS2769: No overload matches this call` | Return type not inferred from async function | Add `: Promise<UserConfig>` to the function signature |
| `TS2559: Type 'true' has no properties in common` | `server.https` type changed in Vite 7 | Remove `https: true`; `basicSsl()` sets it automatically |
| Manifest returns `http://` instead of `https://` | `mfeManifestPlugin` races `basicSsl` in `configResolved` | Use `adi-portal-vite-plugins@^0.1.0-pre.7` or later |

---

## React Fast Refresh Preamble Shim

When loading via the override panel, Vite's `index.html` does not run, so the React Fast Refresh preamble globals are not set. The following two-part fix is required.

### `src/setup.ts`

```ts
/// <reference types="vite/client" />
if (import.meta.env.DEV) {
  // @ts-expect-error
  window.$RefreshReg$ = () => {}
  // @ts-expect-error
  window.$RefreshSig$ = () => (type: unknown) => type
  // @ts-expect-error
  window.__vite_plugin_react_preamble_installed__ = true
}
```

### `src/spa.tsx`: setup must be the first import

```ts
import './setup'  // must be the first import

import React from 'react'
import ReactDOM from 'react-dom/client'
import singleSpaReact from 'single-spa-react'
import App from './App'

const lifecycles = singleSpaReact({ React, ReactDOM, rootComponent: App,
  errorBoundary(err) { return <div>Error: {err.message}</div> } })

export const { bootstrap, mount, unmount } = lifecycles
```

---

## Authentication

Do not call Auth0 directly. Use the shared auth library, which is resolved at runtime via the import map:

```ts
import {
  getCachedToken,  // 5-minute cache; preferred for repeated calls
  getToken,        // always fetches a fresh token
  clearToken,      // clears the cache on 401, then retry
  getUser,         // Promise<{ name, email, sub, ... } | null>
  getOrgId,        // string | null
  authHeaders,     // (token) => { Authorization, Content-Type, x-organization-id }
} from '@alterdomus-intelligence/adi-portal-auth'
```

### GraphQL

```ts
const token = await getCachedToken()
const res = await fetch('https://api.alterdomus.dev/v1/graphql', {
  method: 'POST',
  headers: authHeaders(token),
  body: JSON.stringify({ query, variables }),
})
if (res.status === 401) { clearToken(); /* retry once */ }
```

### REST

```ts
const res = await fetch('https://api.alterdomus.dev/v1/organizations', {
  headers: authHeaders(token),
})
```

`authHeaders(token)` automatically includes `x-organization-id` from sessionStorage.

**Rules:**
- Do not add `adi-portal-auth` to `devDependencies`; it will be bundled and break the singleton.
- Do not read `sessionStorage.getItem('gsp-org-id')` directly; use `getOrgId()`.

---

## Cross-MFE Navigation

```ts
import { navigateToUrl } from 'single-spa'

navigateToUrl('/funds')
navigateToUrl('/ops-center?workflowId=x')
```

- Do not use `window.location.href = '/funds'`; this causes a full page reload and loses auth state.
- Within the same MFE, use React Router `<Link>` and `useNavigate` as normal.

---

## `package.json` Checklist

```json
{
  "dependencies": {
    "react": "^19.x", "react-dom": "^19.x",
    "single-spa": "^6.x", "single-spa-react": "^6.x"
  },
  "devDependencies": {
    "@types/react": "^19.x", "@types/react-dom": "^19.x", "@types/node": "^24.x",
    "@vitejs/plugin-basic-ssl": "^2.2.0",
    "@vitejs/plugin-react": "^5.x",
    "typescript": "~5.9.x",
    "vite": "^7.x",
    "vite-plugin-single-spa": "^1.x"
  },
  "optionalDependencies": {
    "@alterdomus-intelligence/adi-portal-vite-plugins": "^0.2.0-pre.2"
  }
}
```

`adi-portal-vite-plugins` is **optional**. CI pipelines do not always have access to GitHub Packages for private organisation packages. The vite config handles `ERR_MODULE_NOT_FOUND` gracefully.

---

## Branching and Deployment

```
feature/*  --+
fix/*      --+--> develop --> dev (auto) --> qa (manual approval)
chore/*    --+
                                                 |
                                                 | cut release branch
                                                 v
                                        release/x.y --> sim (auto) --> prd (manual approval)
```

- Do not push directly to `develop` or `release/*`.
- `develop` must always be in a deployable state; CI (validate, SAST, Amazon Q) must pass before merging.
- To release: `git checkout -b release/1.2 && git push origin release/1.2`, then approve in GitHub Actions.

---

## Common Issues and Fixes

| Symptom | Cause | Fix |
|---------|-------|-----|
| `ERR_PNPM_OUTDATED_LOCKFILE` in CI | `pnpm install` inside meta workspace updates the workspace lockfile, not the submodule lockfile | Run `pnpm install --no-frozen-lockfile` in a standalone copy outside the workspace |
| Manifest returns `http://` | `mfeManifestPlugin` races `basicSsl` in Vite 7 concurrent `configResolved` | Upgrade to `adi-portal-vite-plugins@^0.2.0-pre.2` |
| `Cannot find module '@vitejs/plugin-basic-ssl'` in CI | Missing from `devDependencies` (was only workspace-hoisted) | Add `"@vitejs/plugin-basic-ssl": "^2.2.0"` to `devDependencies` |
| `TS2769: No overload matches this call` | Missing `Promise<UserConfig>` return type | Add `: Promise<UserConfig>` to the async function signature |
| `TS2339: Property 'env' does not exist on ImportMeta` | Missing Vite client types | Add `/// <reference types="vite/client" />` to `setup.ts` |
| `$RefreshReg$ is not defined` via override panel | React Fast Refresh preamble never ran | Add `src/setup.ts` and `singleSpaPreambleBypass` plugin; ensure `setup` is the first import in `spa.tsx` |
| MFE not activating / blank page | `activeWhen` mismatch or incorrect port | Check `app-registry.json` and `serverPort` in `vite.config.ts` |
| `adi-portal-auth` bundled into output | Missing from `rollupOptions.external` | Add `/^@alterdomus-intelligence\/.+/` to the external list |

---

## Brand and Design Tokens

```css
--ad-teal:       #D95A32;  /* primary interactive: buttons, links, CTAs */
--ad-teal-dark:  #b84829;  /* hover and pressed state */
--ad-orange:     #D95A32;  /* accent */
--ad-dark:       #2E3A3D;  /* body text */
--ad-grey:       #e0e0e0;  /* borders */
--ad-royal-blue: #303030;  /* secondary text and icons */
```

Typography: **DM Serif Display** for `h1` through `h3`, **Manrope** for all other elements. Square corners (`border-radius: 0`) throughout. Background: `#ffffff`.

---

## Quick Reference

| Task | How |
|------|-----|
| Run full portal locally | `pnpm dev` in meta repo |
| Run MFE standalone | `pnpm dev` in the MFE repository |
| Test against deployed shell | Override panel at `https://dww1y1fc4a3sj.cloudfront.net` |
| Navigate to another MFE | `navigateToUrl('/route')` from `single-spa` |
| Get auth token | `getCachedToken()` from `adi-portal-auth` |
| Read active organisation | `getOrgId()` from `adi-portal-auth` |
| GraphQL endpoint | `https://api.alterdomus.dev/v1/graphql` |
| REST base URL | `https://api.alterdomus.dev/v1` |
| Deploy to dev | Merge PR to `develop` |
| Deploy to prd | Cut `release/*` branch and approve in GitHub Actions |
