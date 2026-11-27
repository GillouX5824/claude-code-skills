---
name: exec-slides
description: >
  Use this skill to create executive presentations, slide decks, pitch decks, or any multi-slide
  presentation when the output format has NOT been specified. This skill asks the user to choose
  between HTML (interactive, browser-navigable, exports to PDF) or PowerPoint (.pptx) before
  proceeding. When HTML is chosen, it produces a self-contained .html file using the AlterDomus
  brand design system (Brand Teal #1F6473, Accent Orange #E74314, DM Serif Display + Manrope
  fonts) and then exports a PDF via Puppeteer. Always use this skill when the user says "create a
  presentation", "make me a deck", "build slides", "executive presentation", "exec deck", "slide
  deck", "investor deck", or anything similar — unless they explicitly say ".pptx" or "PowerPoint",
  in which case use the pptx skill directly.
---

# Exec Slides — HTML Presentation Skill

## Before You Start: Load Supporting Skills

Before doing anything else, invoke these two skills and follow their guidance throughout:

1. **Invoke `scqa-framework`** — use it to structure the narrative (Situation → Complication → Question → Answer). The resulting SCQA spine determines slide order and story arc.
2. **Invoke `presentation-writing`** — apply its writing standards to every slide: titles as conclusions, concise bullets, executive language.

These skills shape the *content and structure*. This skill handles the *format and visual output*. Both are needed for a strong deck.

---

## Step 0: Format Selection

When the user asks for a presentation without specifying format, **always ask first**:

> "For this presentation, which format would you prefer?
> - **HTML** — interactive browser experience, arrow-key navigation, exports cleanly to PDF. Best for sharing and presenting.
> - **PowerPoint (.pptx)** — editable in PowerPoint, great when colleagues need to modify it."

- If they choose **HTML**: follow this skill.
- If they choose **PPTX**: switch to the `pptx` skill.

---

## Slide Architecture

Each presentation is a **single self-contained `.html` file**:

- CSS design tokens and component styles in `<style>` (no external CSS)
- Google Fonts via `<link>` (DM Serif Display + Manrope — requires internet connection)
- Slides as `<section class="slide …">` elements inside a fixed 1280×720 px deck
- JavaScript: scale-to-fit viewport + arrow-key / button / fullscreen navigation
- Print CSS: shows all slides as 16:9 pages for Puppeteer PDF export

### Deck wrapper structure
```html
<div id="scale-wrapper">
  <div class="slide-deck" id="deck">
    <section class="slide slide-title active"> … </section>
    <section class="slide slide-section"> … </section>
    <section class="slide slide-content"> … </section>
    <!-- … more slides … -->
    <section class="slide slide-conclusion"> … </section>
  </div>
</div>
<nav class="slide-nav" id="nav"> … </nav>
```

---

## Starting from the Base Template

**Read `assets/slide-base.html`** — it contains the full CSS design system, one example of every
slide type (clearly labelled), navigation JS, and print CSS. Use it as your starting point:

1. Copy the base template in full.
2. Replace all placeholder content with real presentation content.
3. Remove unused slide-type examples; duplicate slides as needed.
4. Update the `<title>` and presenter/date meta.
5. Export to PDF (see below).

> The base template already includes all CSS variables, component styles, and the navigation script.
> You should NOT need to add new CSS for standard slide types — just use the class names.

---

## Slide Types

| Type             | Outer class(es)                          | When to use |
|------------------|------------------------------------------|-------------|
| **Title**        | `slide-title`                            | First slide — presenter, date, topic |
| **Section break**| `slide-section`                          | Divider between major sections |
| **Standard**     | `slide-content`                          | Most slides: title bar + body area |
| **Stats / KPIs** | `slide-content` + `stats-grid` in body  | 3–4 large KPI numbers |
| **Feature cards**| `slide-content` + `cards-grid` in body  | 3–4 capability / feature cards |
| **Two-column**   | `slide-content` + `slide-body two-col`  | Side-by-side comparison, pros/cons |
| **Timeline**     | `slide-content` + `timeline` in body    | Process, roadmap, history |
| **Conclusion**   | `slide-conclusion`                       | Last slide — takeaway + next steps |

### Body layout modifiers (inside `.slide-content`)
- `.slide-body` — default flex row, `gap: 32px`
- `.slide-body.two-col` — equal two-column grid
- `.slide-body.two-col-wide` — 3:2 left-heavy grid

### Inner components (use inside any content slide body)
- `.bullet-list` — orange-dot bullets, `<li>` items
- `.stats-grid` → `.stat-card` with `.stat-value`, `.stat-label`, `.stat-change`
- `.cards-grid` → `.feature-card` with `.icon-box`, `h3`, `p`
- `.timeline` → `.timeline-item` with `.timeline-marker` and `.timeline-content`
- `.badge` / `.badge-orange` — pill-shaped label chips
- `.visual-placeholder` — grey box for images not yet available

---

## Design System Quick Reference

Full details in `references/design-system.md`. Key values for slides:

```css
/* Colors */
--teal:           #1F6473;
--teal-gradient:  linear-gradient(135deg, #3d6d7a 0%, #2a5563 100%);
--orange:         #E74314;
--orange-gradient:linear-gradient(135deg, #E74314 0%, #ff6b3d 100%);
--yellow:         #FFD166;   /* use sparingly for highlights */
--text-dark:      #2a5563;
--text-body:      #2d3748;
--text-muted:     #6b7280;

/* Fonts */
h1 only → DM Serif Display (serif), 700
All else → Manrope (sans-serif), 400/500/600
```

### Visual rules for slides
- Dark teal background slides (`slide-title`, `slide-section`, `slide-conclusion`) open and close the deck.
- White/light content slides (`slide-content`) fill the middle.
- Orange (`#E74314`) for accent dots, highlights, active states — never overused.
- **Never put an underline accent line below a heading** — use whitespace or background colour instead.
- Every slide must have at least one visual element (stat, icon, chart, image, or structured layout).
- Slide titles should be **conclusions** ("Revenue grew 23% in Q3") not topics ("Q3 Revenue").

---

## PDF Export

### One-time setup
```bash
npm install puppeteer          # local project
# OR
npm install -g puppeteer       # global
```

### Export command
```bash
node "<this skill's directory>/scripts/export-pdf.js" presentation.html
# → produces presentation.pdf in the same directory
```

Pass an optional second argument to control output path:
```bash
node export-pdf.js deck.html "C:\Reports\Q4-exec-deck.pdf"
```

The script opens the file in headless Chromium, triggers print layout (all slides visible, one per
page), and exports at **1280×720 px per page** (16:9 widescreen, matching PowerPoint standard).

### Offline / no internet
If fonts cannot load from Google Fonts, substitute:
- `DM Serif Display` → `Georgia, serif`
- `Manrope` → `system-ui, -apple-system, sans-serif`

---

## PPTX Export (embedded images)

After the HTML deck is finalised, **always ask the user**:

> "Would you also like a PowerPoint (.pptx) version? Each slide will be embedded as a high-resolution image — layout is identical to the HTML, but the file is editable in PowerPoint (slides are read-only images, not editable text)."

If yes, run:

```bash
node "<this skill's directory>/scripts/export-pptx.js" presentation.html
# → produces presentation.pptx in the same directory
```

Pass an optional second argument for a custom output path:
```bash
node export-pptx.js deck.html "C:\Reports\Q4-exec-deck.pptx"
```

### How it works
- Uses Puppeteer with a 1280×5000 px viewport (tall enough to render all slides in the scrollable page at once, no lazy-loading issues).
- Screenshots each `.slide` element directly via `elementHandle.screenshot()` — this captures the element's bounding box regardless of body padding or scroll position, producing pixel-accurate 1280×720 captures at 2× device scale.
- Hides the nav bar before capturing.
- Embeds each screenshot as a full-bleed 13.33"×7.5" image in a 16:9 pptxgenjs slide.
- **Do not use the old clip-based approach** (clipping at x:0, y:0 produces empty slides because the body has 48px top padding).

### Dependencies
`puppeteer` and `pptxgenjs` are both installed in `scripts/node_modules/` — no additional setup needed.

---

## Slide Count & Density

- **Title + Conclusion**: always present.
- **Section breaks**: one per major section (optional).
- **Content density**: one key message per slide. If you need more than 5 bullets, split the slide.
- **Typical exec deck**: 8–15 slides.

---

## QA Checklist

After generating, open the HTML in Chrome/Edge and verify:

- [ ] All slides render correctly at 16:9 in the browser.
- [ ] No text overflows slide boundaries.
- [ ] `DM Serif Display` renders on `h1` elements; `Manrope` everywhere else.
- [ ] Arrow keys and Prev/Next buttons navigate correctly.
- [ ] Slide counter (e.g. "3 / 10") updates correctly.
- [ ] Fullscreen button (⛶) in the nav bar toggles fullscreen; icon changes to ✕ when active. **F** key also toggles.
- [ ] After PDF export: open the PDF and check all slides appear, no content truncated.

---

## Delivery

Always deliver **both files**:
1. `[name].html` — the interactive presentation (open in Chrome/Edge for best experience).
2. `[name].pdf` — the PDF export (run the Puppeteer script immediately after finalising the HTML).

Then ask about PPTX (see **PPTX Export** section above).

The nav bar includes a fullscreen button (⛶) — clicking it or pressing **F** toggles fullscreen mode.
