---
name: embeddable
description: >
  Use this skill when integrating an Alter Domus Embeddable Dashboards and Analytics (EDA)
  dashboard into a consuming application. Triggers on any request involving: embedding the
  <em-beddable> web component, calling the Token Service to mint a security token, wiring the
  React frontend package (the <Dashboard> component or the useEmbeddableToken hook), pinning a
  dashboard version (vN / savedVersion), supplying clientId for row-level tenant isolation,
  setting theme via client-context, handling 24-hour token refresh, or debugging a blank or
  unauthorized embed. This is the reference for the CONSUMER side of EDA: the team dropping a
  published dashboard into their own app. It does not cover building dashboards, Cube models, or
  the ad-ui-embeddable repo itself.
license: Apache-2.0
---

# Integrating an Embeddable Dashboard (EDA)

Alter Domus builds reusable analytics dashboards on the [Embeddable.com](https://embeddable.com) platform (React components plus Cube.js data models, in the `ad-ui-embeddable` repo). Those dashboards are published to a hosted Embeddable workspace and **consumed** by other applications. This skill is for the consuming side: how a product team drops a published dashboard into its own app, authenticates it, and pins a version.

If you are building the dashboards themselves (components, Cube models, presets, the publish workflow), this is the wrong reference. Go to the [ad-ui-embeddable repo](https://github.com/alterdomus-digital/ad-ui-embeddable) and the [EDA Confluence space](https://alterdomus.atlassian.net/wiki/spaces/EDA/overview).

## Key facts

| Fact | Value |
|------|-------|
| Render mechanism | A web component, `<em-beddable>`. Not an iframe, not a hosted MFE bundle. |
| Embeddable region | **US** |
| Embed script | `https://embed.embeddable.com/js/v1/?region=us` |
| Preconnect host | `https://static-data.us.embeddable.com` |
| Token source (consumer) | Alter Domus **Token Service** (`POST /embeddable/token`). Never call Embeddable's Tokens API directly. |
| Tenant isolation key | `clientId` (UUID), required on every token request |
| Version selector | `savedVersion`, a `vN` string (e.g. `v12`). Consumer pins it explicitly. |
| Token lifetime | 24 hours, refreshed without a page reload |
| Dashboards repo | [`alterdomus-digital/ad-ui-embeddable`](https://github.com/alterdomus-digital/ad-ui-embeddable) |

> **Status note.** The Token Service and the React frontend package are the agreed MVP design and may still be in build at the time you read this (frontend package: DCL-157; publish workflow: DCL-158). Confirm availability and the exact Token Service base URL with the Embeddable dev team (Tech Owner: Nic Ford). The web component contract below is stable and matches Embeddable's platform.

## How embedding works

```
Consuming app (browser)
  └─ Loads embed script + preconnect in <head>  (region=us)
  └─ Asks ITS OWN backend / the Token Service for a token   ← server-side mint
       └─ Token Service holds the Embeddable API key, builds securityContext,
          calls Embeddable's Tokens API, returns a JWT
  └─ Renders <em-beddable token="<JWT>"> and the dashboard mounts
  └─ Refreshes the token before its 24h exp and updates the attribute
```

The single hard rule: **the security token must be minted server-side.** Minting requires the Embeddable API key, which cannot ship to the browser. The Token Service is that server-side layer, shared across all consumers so no app ever holds the API key. There is no path where a user's own auth token reaches Cube directly.

## Integration path A: the frontend package (recommended)

Consumers should not hand-roll the script injection, token fetch, refresh loop, and `<em-beddable>` wiring. The Embeddable team ships a small React package that wraps all of it. Two entry points:

```tsx
// Drop-in component: handles preconnect + script injection, token fetch,
// refresh on exp, and renders <em-beddable>. Use this unless you need more control.
import { Dashboard } from '<embeddable-frontend-package>';

<Dashboard embeddableId="dash_cortrade_client" version="v12" clientId={orgId} />
```

```tsx
// Lower-level hook: returns the token and lets you render <em-beddable> yourself.
import { useEmbeddableToken } from '<embeddable-frontend-package>';

const { token, expiresAt, refresh } = useEmbeddableToken({
  embeddableId: 'dash_cortrade_client',
  version: 'v12',
});
```

`version` is required and is typed to the `vN` format, so passing anything else is a TypeScript error. The package also exposes `useEmbeddableVersions(embeddableId)` (DCL-161) to discover which `vN` exist without leaving the IDE.

Confirm the published package name and import paths with the Embeddable dev team before wiring it in; the package is tracked under DCL-157 and the name above is a placeholder.

## Integration path B: manual integration

This is what path A does under the hood. Use it only if the frontend package is not yet available to you, or you are on a non-React stack.

### 1. Load the script and preconnect

In the page `<head>`:

```html
<link rel="preconnect" href="https://static-data.us.embeddable.com" crossorigin>
<script type="module" src="https://embed.embeddable.com/js/v1/?region=us"></script>
```

In React, inject these via `react-helmet`; in Next.js via `next/head`.

### 2. Mint a token (server-side, via the Token Service)

Call the Alter Domus Token Service from your backend. Your app's normal app-to-app auth protects this call; the Token Service resolves the caller and builds the `securityContext`.

```
POST /embeddable/token
Authorization: <your app-to-app auth>
Content-Type: application/json

{
  "embeddableId":  "dash_cortrade_client",
  "savedVersion":  "v12",                  // required, vN format only (^v\d+$); env tags rejected with 400
  "clientId":      "0c3b...-uuid",         // required, UUID; forwarded into securityContext for row-level security
  "clientContext": { "theme": "light" },   // optional non-security context, validated against a per-embeddableId allow-list
  "canvas":        { "readOnly": true }    // optional
}
```

Response:

```json
{
  "token": "eyJhbGciOiJIUzI1NiJ9...",
  "expiresAt": "2026-05-07T16:14:22Z"
}
```

Return the `token` to your frontend. Never expose the Embeddable API key or call `https://api.us.embeddable.com/api/v1/security-token` from a consuming app: that endpoint is the Token Service's job.

### 3. Render the web component

```html
<em-beddable
  token="eyJhbGciOiJIUzI1NiJ9..."
  client-context='{"theme":"light"}'
></em-beddable>
```

Supported attributes: `token` (required), `client-context` (JSON), `variables` (JSON dashboard variables).

In React, treat it as a custom element via JSX or `React.createElement('em-beddable', { token })`. For TypeScript, declare the element to avoid `Property 'em-beddable' does not exist on type 'JSX.IntrinsicElements'`:

```ts
declare namespace JSX {
  interface IntrinsicElements {
    'em-beddable': {
      token: string;
      'client-context'?: string;
      variables?: string;
    };
  }
}
```

### 4. Refresh before expiry

Tokens last 24 hours and can be refreshed without reloading the page. Re-mint via the Token Service before `expiresAt` and update the `token` attribute on the element. (Path A does this for you.)

## Authentication and the security model

Authorization is enforced in two layers:

1. **The token**, which carries `clientId` in its `securityContext`.
2. **Cube.js models**, which inject that context as a `WHERE` predicate so the SQL only returns rows the caller may see (`WHERE client_id = SECURITY_CONTEXT.clientId`).

What the consumer supplies on each token request:

- `embeddableId` and `savedVersion` (`vN`): which dashboard and which version.
- `clientId` (UUID, **required**): the tenant identifier. The canonical key every model filters on. If your app calls this `orgId`, `tenantId`, or similar internally, map it to `clientId` at the Token Service boundary.
- Optional non-security context (e.g. `clientContext.theme`, `canvas.readOnly`): display and behaviour flags, validated against a per-`embeddableId` allow-list.

What the consumer does **not** supply: the Embeddable API key, the `user` field (resolved from the authenticated request), or future security-relevant fields like roles (these will be server-resolved in v2).

> **MVP trust assumption.** In the initial release, the Token Service trusts the `clientId` your backend sends and does not independently verify it. Your backend is responsible for authenticating its own user and sending the correct `clientId` for that user. Sending the wrong `clientId` shows the wrong tenant's data. This is bounded by your own auth boundary plus audit logging, and the long-term direction is server-resolved `clientId` (DCL-167). Treat sending the right `clientId` as a hard security requirement on the consumer side.

Row-based access only in v1: every user of a tenant sees the same data. Role-based differentiation (Analyst vs Client Manager, entitled regions, and so on) is v2 on the roadmap.

## Versioning and rollback

- Pin an explicit `vN` per request. The version lives in **your** code (or your own per-environment config). Promoting dev to staging to prod is a deliberate code change in your app, which keeps QA deterministic: the artifact signed off in staging is the same one that reaches prod.
- The Token Service rejects any `savedVersion` not matching `^v\d+$` with a `400`. Env tags (`production`, `staging`, `development`) are not accepted in MVP.
- Only the **most recent 30** saved versions per `embeddableId` remain addressable. Keep your pinned `vN` reasonably current, or it can eventually fall out of range and stop loading.
- **Rollback is a code change on your side:** pin to any prior `vN` still in the 30-version window and redeploy through your normal pipeline. There is no server-side denylist for broken versions in MVP (DCL-162 is the future option).
- Per-tenant pinning or gradual rollouts are a consumer-side concern: read your own feature flag (LaunchDarkly, and so on), map the flag value to a `vN`, and pass it to the package or the Token Service. The Token Service stays a simple mint-and-validate surface and has no awareness of your flag system.

Watch the [ad-ui-embeddable](https://github.com/alterdomus-digital/ad-ui-embeddable) GitHub releases (Watch, Custom, Releases) to learn when a new `vN` is available and whether it requires a consumer-side change.

## Theming and client-context

Theme and other display preferences ride on `client-context` (web component attribute) or `clientContext` (Token Service request). For example `{ "theme": "light" }` or `{ "theme": "dark" }`. These are non-security flags and must be on the per-`embeddableId` allow-list; if a flag is silently ignored, check the allow-list with the dashboard's SME.

## Framework gotchas

- **Angular and Vue** sanitise unknown attributes by default and can strip values like `client-context`. In Angular, bind via a directive or `DomSanitizer`; in Vue, use explicit attribute binding.
- **Multiple dashboards on one page:** set `position: relative` and explicit `z-index` values on the elements so overlays stack correctly.
- **TypeScript** needs the `em-beddable` JSX declaration shown above.

## Common failure modes

| Symptom | Likely cause |
|---------|--------------|
| Blank embed, nothing renders | Embed script or preconnect missing from `<head>`, or wrong region (must be `us`) |
| `400` from the Token Service | `savedVersion` is not `vN` format (e.g. you sent `production`), or `clientId` is missing or not a UUID |
| `502` from the Token Service | Embeddable's Tokens API failed upstream; the service does not fall back to a stale token |
| Wrong tenant's data shown | Backend sent the wrong `clientId` (MVP trust assumption: nothing else catches this) |
| Dashboard version stopped loading | The pinned `vN` fell out of the most-recent-30 window; bump to a current `vN` |
| `client-context` value ignored | Key is not on the per-`embeddableId` allow-list, or the framework stripped the attribute |
| Embed shows an old dashboard after you bumped `vN` | In-flight 24h token still pinned to the old version; it refreshes on the next mint cycle |

## Reference

- EDA Confluence space: https://alterdomus.atlassian.net/wiki/spaces/EDA/overview
- Token Service design: https://alterdomus.atlassian.net/wiki/spaces/EDA/pages/271712276
- Authorization (clientId / row-level security): https://alterdomus.atlassian.net/wiki/spaces/EDA/pages/266534979
- Deployment / release cycle (versioning, rollback): https://alterdomus.atlassian.net/wiki/spaces/EDA/pages/266534960
- Embeddable embedding docs: https://docs.embeddable.com/deployment/embedding
- Embeddable Tokens API: https://docs.embeddable.com/deployment/tokens-api
- Dashboards repo: https://github.com/alterdomus-digital/ad-ui-embeddable
