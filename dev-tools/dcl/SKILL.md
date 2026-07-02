---
name: dcl
description: >
  AD UI Design System Component Library (DCL). Use this skill when working on any frontend
  application that uses or should use the DCL — installing the library, importing components,
  setting up styles/themes, choosing the right component for a UI pattern, using Phosphor icons,
  writing tests for DCL components, or understanding accessibility requirements. Triggers on any
  request involving UI components, component library setup, design system integration, or
  references to @alterdomus-digital/ad-ui-components-react or @alterdomus-digital/ad-ui-components-angular.
  **ALWAYS** read this skill when working on frontend UI code in an Alter Domus project. If a DCL
  component exists for the job, you must use it — never reach for a 3rd-party UI library or raw
  HTML equivalent.
version: 1.0.0
---

# AD UI Design System Component Library (DCL)

The DCL is the official component library for all Alter Domus frontend applications. It ships as two first-class libraries — one for React and one for Angular — with largely the same component set. Each library may have slight API differences since they are native to their respective frameworks.

## References

| Resource | Link |
|----------|------|
| React repo | https://github.com/alterdomus-digital/ad-ui-components-react |
| Angular repo | https://github.com/alterdomus-digital/ad-ui-components-angular |
| React Storybook | https://alterdomus-digital.github.io/ad-ui-components-react/?path=/story/components-accordion--large-default |
| Angular Storybook | https://www.chromatic.com/library?appId=67eabedead5c395a5495db30 |
| Figma (V3 Components) | https://www.figma.com/design/dY40wuFMRYoHKcJuw29ygl/%F0%9F%A7%B1-V3-Components |
| Docs site | _Coming soon_ |

---

## Step 1: Detect the Framework

Before giving any DCL guidance, determine which framework the consuming project uses.

### Detection Logic

1. Check `package.json` for framework indicators:
   - `react` or `react-dom` in dependencies → **React**
   - `@angular/core` in dependencies → **Angular**
2. Check if DCL is already installed:
   - `@alterdomus-digital/ad-ui-components-react` → React DCL already present
   - `@alterdomus-digital/ad-ui-components-angular` → Angular DCL already present
3. If neither framework is detected → ask the user

**Always tell the user which framework you detected** before proceeding.

---

## Step 2: Installation

The DCL packages are published to **GitHub Packages** under the `@alterdomus-digital` scope.

### Prerequisites — `.npmrc` Configuration

The consuming project (or the user's global config) must have an `.npmrc` that points `@alterdomus-digital` to GitHub Packages:

```ini
@alterdomus-digital:registry=https://npm.pkg.github.com
//npm.pkg.github.com/:_authToken=${GITHUB_TOKEN}
```

The `GITHUB_TOKEN` must have `read:packages` scope on the `alterdomus-digital` GitHub org.

### React

```bash
npm install @alterdomus-digital/ad-ui-components-react
```

Current version: **1.4.0**

### Angular

```bash
npm install @alterdomus-digital/ad-ui-components-angular
```

Current version: **1.0.0-alpha.8.25**

> **Version policy:** Only the latest major versions of React and Angular are supported. Keep your framework up to date.

---

## Step 3: Style Setup

DCL components depend on global styles and CSS custom properties. Setup differs by framework.

### React

Add a single CSS import at the top of your application entry point (e.g., `main.tsx`, `index.tsx`, or `App.tsx`):

```tsx
import "@alterdomus-digital/ad-ui-components-react/style.css";
```

That's it — this loads all design tokens, base styles, and component styles.

### Angular

Angular requires a **two-step** setup because it needs both plain CSS custom properties and SCSS compilation:

#### 1. Add CSS variables to `angular.json`

Add the auto-generated CSS custom properties file to the `styles` array in your project's `angular.json`:

```json
"styles": [
  "node_modules/@alterdomus-digital/ad-ui-components-angular/src/styles/theme/variables.css",
  "src/styles.scss"
]
```

This loads the `--dns-*` CSS custom properties (colors, border-radius, typography tokens, etc.) that every DCL component depends on.

#### 2. Import the global stylesheet in `styles.scss`

Import the library's main stylesheet in your app's `src/styles.scss`:

```scss
@import '@alterdomus-digital/ad-ui-components-angular/styles.scss';
```

This brings in global styles: scrollbar classes, tooltip styles, flex utilities, AG Grid overrides, Angular Material setup, Phosphor icons, and more.

**Selective imports** are also supported if you only need specific pieces:

```scss
@import '@alterdomus-digital/ad-ui-components-angular/styles/tokens';
@import '@alterdomus-digital/ad-ui-components-angular/styles/mixins';
```

#### Why both are needed

- **`variables.css`** is a plain CSS file with `:root` custom properties — it must be loaded as a standalone style asset via `angular.json` so it's available globally before any component renders.
- **`styles.scss`** contains SCSS that uses `@use`/`@include` for Angular Material theming plus all global utility classes — this needs SCSS compilation, so it's imported from another SCSS file.

---

## Strict Rules

These rules are **mandatory** for all Alter Domus frontend projects. Claude must enforce them.

### Rule 1: DCL-First

If a DCL component exists for a UI pattern, **you must use it**. Never build a custom implementation or use a native HTML element when a DCL equivalent is available.

- Use DCL `Button`, not `<button>`
- Use DCL `Input`, not `<input>`
- Use DCL `Select`, not `<select>`
- Use DCL `Modal`/`Dialog`, not a custom overlay
- Use DCL `Table`/`DataGrid`, not a hand-rolled table
- Use DCL `Toast`/`Alert`, not `window.alert()` or a custom notification

### Rule 2: No Third-Party UI Libraries

**Never install a competing component library** alongside the DCL. This includes but is not limited to:

- Material UI (MUI)
- PrimeNG / PrimeReact
- Ant Design
- Bootstrap / React-Bootstrap
- Chakra UI
- Radix UI / shadcn/ui
- Angular Material _(except as a peer dependency of the Angular DCL itself)_

If you encounter an existing project with a 3rd-party library, flag it to the user and recommend a migration path to DCL components.

### Rule 3: Check Before You Build

Before writing any custom UI component:

1. **Search the Storybook** for an existing DCL component
2. **Search the DCL repo source code** for relevant component types/props
3. **Check the installed `node_modules`** package for exported components

If no DCL component exists, see the [Contributing](#contributing) section.

---

## Component Categories

The DCL covers these major categories:

### Layout & Navigation
Sidebar, Header, AppShell, Breadcrumbs, Tabs, Navigation menus, Page layouts

### Forms & Inputs
Input, TextArea, Select, Datepicker, Checkbox, Radio, Switch, FileUpload, Form validation components

### Data Display
Table, DataGrid, Cards, Lists, Stats, Charts, Badges, Tags, Avatars

### Feedback & Overlays
Modal, Dialog, Toast, Alert, Tooltip, Drawer, Popover, Loading/Spinner, Progress indicators

---

## Looking Up Component APIs

When you need to understand a DCL component's API (props, events, slots), use **both** of these approaches:

### 1. Read the source code / types

Check the installed package for type definitions:

**React:**
```bash
# Find component exports
grep -r "export" node_modules/@alterdomus-digital/ad-ui-components-react/dist/ --include="*.d.ts" | head -50

# Read a specific component's types
cat node_modules/@alterdomus-digital/ad-ui-components-react/dist/components/Button/Button.d.ts
```

**Angular:**
```bash
# Find component exports
grep -r "export" node_modules/@alterdomus-digital/ad-ui-components-angular/ --include="*.d.ts" | head -50
```

### 2. Reference Storybook for usage patterns

- **React Storybook:** https://alterdomus-digital.github.io/ad-ui-components-react/
- **Angular Storybook:** https://www.chromatic.com/library?appId=67eabedead5c395a5495db30

Storybook stories show real usage examples, variant combinations, and interactive props.

---

## Icons — Phosphor Icons

The DCL uses **Phosphor Icons** as its icon system. Icons are imported and used directly as components within DCL components and in consuming applications.

### React

```tsx
import { MagnifyingGlass, CaretDown, X } from "@phosphor-icons/react";

<MagnifyingGlass size={24} weight="regular" />
<CaretDown size={16} weight="bold" />
```

### Angular

```typescript
// Import the Phosphor icon module/component as needed
// Check the Angular DCL Storybook for the exact import pattern
```

### Guidelines

- Always use Phosphor icons — do not mix icon libraries (no FontAwesome, Heroicons, Lucide, etc.)
- Use the `weight` prop to match the design: `"thin"`, `"light"`, `"regular"`, `"bold"`, `"fill"`, `"duotone"`
- Refer to the [Phosphor Icons catalog](https://phosphoricons.com/) for available icons
- The Angular DCL global stylesheet already includes Phosphor icon setup

---

## Accessibility

The DCL components are built with accessibility in mind. Engineers must uphold these standards:

### What the DCL handles

- Correct ARIA roles and attributes on interactive components
- Keyboard navigation within complex components (menus, selects, modals)
- Focus management (trapping focus in modals, restoring focus on close)
- Screen reader announcements for dynamic content (toasts, alerts)

### What engineers must do

- **Always provide labels**: Use `aria-label`, `aria-labelledby`, or visible `<label>` elements for form inputs
- **Don't override focus styles**: DCL components ship with visible focus indicators — never remove them with `outline: none`
- **Use semantic props**: Use the `role`, `aria-*`, and `disabled` props that DCL components expose
- **Test with keyboard**: Every interactive flow must be completable via keyboard alone
- **Provide alt text**: For images, icons used as standalone actions, or any visual-only content
- **Color contrast**: The built-in theme meets WCAG 2.1 AA — do not override token colors with lower-contrast values
- **Heading hierarchy**: Use proper heading levels (`h1` → `h2` → `h3`), never skip levels for styling purposes

---

## Testing with DCL Components

### React — Testing Library

```tsx
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button } from "@alterdomus-digital/ad-ui-components-react";

test("calls onClick when button is clicked", async () => {
  const handleClick = vi.fn();
  render(<Button onClick={handleClick}>Submit</Button>);

  await userEvent.click(screen.getByRole("button", { name: /submit/i }));
  expect(handleClick).toHaveBeenCalledOnce();
});
```

### Angular — Testing Library or ComponentFixture

```typescript
import { ComponentFixture, TestBed } from "@angular/core/testing";
// Import the DCL module for the component you're testing
// Check the Angular DCL exports for the correct module name

describe("MyComponent", () => {
  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [
        // Add relevant DCL modules here
      ],
      declarations: [MyComponent],
    }).compileComponents();
  });
});
```

### Best practices

- **Query by role, not class**: Use `getByRole`, `getByLabelText`, `getByText` — never query by DCL internal CSS class names, as they may change between versions
- **Don't test DCL internals**: Test your application's behavior, not whether a DCL component renders its internal structure correctly
- **Mock sparingly**: Avoid mocking DCL components unless absolutely necessary — render the real component so you test actual behavior
- **Import styles in test setup**: If your tests use a DOM environment (jsdom/happy-dom), you may need to import the DCL stylesheet in your test setup file to avoid style-dependent rendering issues

---

## Contributing

When a component you need doesn't exist in the DCL, **contribute it directly** by opening a PR to the appropriate repo:

- **React:** https://github.com/alterdomus-digital/ad-ui-components-react
- **Angular:** https://github.com/alterdomus-digital/ad-ui-components-angular

### Process

1. Check the Figma designs at https://www.figma.com/design/dY40wuFMRYoHKcJuw29ygl/%F0%9F%A7%B1-V3-Components to see if the component is already designed
2. Open an issue or discuss with the DCL maintainers before starting work on large components
3. Follow the existing coding patterns in the repo (component structure, naming, testing, Storybook stories)
4. Reference the repo's `CONTRIBUTING.md` for detailed contribution guidelines

---

## Quick Reference

| Task | React | Angular |
|------|-------|---------|
| Install | `npm i @alterdomus-digital/ad-ui-components-react` | `npm i @alterdomus-digital/ad-ui-components-angular` |
| Import styles | `import "@alterdomus-digital/ad-ui-components-react/style.css"` | `angular.json` styles array + `@import` in `styles.scss` |
| Use a component | `import { Button } from "@alterdomus-digital/ad-ui-components-react"` | Import the component/module from the Angular package |
| Use an icon | `import { Icon } from "@phosphor-icons/react"` | Phosphor icons via Angular DCL |
| Browse components | [React Storybook](https://alterdomus-digital.github.io/ad-ui-components-react/) | [Angular Storybook](https://www.chromatic.com/library?appId=67eabedead5c395a5495db30) |
| View designs | [Figma V3 Components](https://www.figma.com/design/dY40wuFMRYoHKcJuw29ygl/%F0%9F%A7%B1-V3-Components) | Same Figma |
| Missing component? | PR to [React repo](https://github.com/alterdomus-digital/ad-ui-components-react) | PR to [Angular repo](https://github.com/alterdomus-digital/ad-ui-components-angular) |
| npm scope config | `@alterdomus-digital:registry=https://npm.pkg.github.com` | Same `.npmrc` |
