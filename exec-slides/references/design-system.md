# AlterDomus Design System — Quick Reference

Full specification for the exec-slides HTML template.

---

## Color Palette

### Brand Colors
| Token | Hex | RGB | Usage |
|-------|-----|-----|-------|
| Brand Teal | `#1F6473` | 31, 100, 115 | Nav, headers, slide backgrounds |
| Accent Orange | `#E74314` | 231, 67, 20 | CTAs, bullets, accents, hover |
| Accent Orange Hover | `#B83712` | — | Darker hover variant |
| Highlight Yellow | `#FFD166` | — | Sparingly, special emphasis only |

### Gradients
| Name | CSS | Usage |
|------|-----|-------|
| Primary | `linear-gradient(135deg, #3d6d7a 0%, #2a5563 100%)` | Slide headers, title/section/conclusion slides |
| CTA | `linear-gradient(135deg, #E74314 0%, #ff6b3d 100%)` | Orange buttons, icon boxes |
| Subtle bg | `linear-gradient(180deg, #f8f9fa 0%, white 100%)` | Content slide backgrounds |
| Card bg | `linear-gradient(135deg, #f8fafb 0%, #ffffff 100%)` | Card surfaces |
| Success tag | `linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%)` | Green badges, text `#00695c` |

### Neutrals
| Token | Value |
|-------|-------|
| Background white | `#ffffff` |
| Light gray | `#f8f9fa` / `#f8fafb` |
| Text primary | `#073540` / `#2a5563` / `#2d3748` |
| Text secondary | `#4a5568` |
| Text muted | `#6b7280` |
| Border | `#e5e7eb` / `#e9ecef` |

---

## Typography

### Font Families
- **DM Serif Display** — `h1` only, weight 700, `font-family: 'DM Serif Display', serif`
- **Manrope** — all other text (h2–h6, body, UI), weights 400 / 500 / 600

Both loaded from Google Fonts:
```html
<link href="https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet">
```

### Type Scale (fixed px for 1280×720 slides)
| Element | Size | Weight | Line-height |
|---------|------|--------|-------------|
| h1 (title slides) | 52–64px | 700 | 1.1 |
| h2 (slide titles in header bar) | 28–34px | 600 | 1.2 |
| h3 (card/section headers) | 20–24px | 600 | 1.3 |
| Body text | 17–19px | 400 | 1.6 |
| Bullet text | 17–19px | 400 | 1.5 |
| Stat value (large callout) | 52–68px | 700 | 1.0 |
| Small labels / badges | 11–13px | 600 | — |
| Slide number | 12px | 500 | — |

---

## Shadows & Elevation

| Level | CSS | Use |
|-------|-----|-----|
| Subtle | `0 2px 8px rgba(0,0,0,0.05)` | Resting state |
| Standard | `0 4px 12px rgba(0,0,0,0.08)` | Cards, stat boxes |
| Elevated | `0 8px 24px rgba(0,0,0,0.1)` | Feature card hover |
| Strong hover | `0 12px 32px rgba(0,0,0,0.12)` | Interactive hover |

---

## Spacing Scale (8px base)
`4 · 8 · 12 · 16 · 24 · 32 · 48 · 64 · 80px`

In 1280×720 slides:
- Slide padding: `40–48px` horizontal, `28–36px` vertical
- Gap between cards: `20–24px`
- Gap between sections: `32–48px`
- Header bar height: ~80px

---

## Border Radius
| Scale | Value | Use |
|-------|-------|-----|
| Small | 4–6px | Tags |
| Medium | 8–10px | Buttons, inputs |
| Large | 12–16px | Cards, containers |
| Full / pill | 999px | Badges |

---

## Animations

### Entrance (applied on `.active` slide)
```css
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(20px); }
  to   { opacity: 1; transform: translateY(0); }
}
/* Stagger: 0.1s, 0.2s, 0.3s delays for list items */
```

### Hover effects
- Cards: `translateY(-4px)` + stronger shadow
- Buttons: `translateY(-2px)` + shadow `0 4px 8px rgba(231,67,20,0.3)`

---

## Design Rules (do / don't)

| Do | Don't |
|----|-------|
| Use DM Serif Display for `h1` only | Use serif for any other heading |
| Orange for primary actions and accent dots | Overuse orange — it's an accent |
| One key message per slide | Cram bullets beyond 5 items |
| Use teal slides at open/close | Use teal for every slide |
| Slide titles as conclusions | Slide titles as topics |
| Leave breathing room around elements | Fill every pixel |
| Use `border-radius: 999px` for badges | Use sharp corners on tags |
| Use shadows to create depth hierarchy | Use flat equal-weight everything |
| **Never** underline headings | Never use an accent line under a title |
