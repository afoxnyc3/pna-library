# P&A Design Tokens

Source of truth for all Principal & Agent visual output. Read this before every visual decision. Do not invent values outside this file.

---

## Palette

### Named colours

| Token | Hex | Role |
|---|---|---|
| Ink | `#080c09` | Dark theme background (canonical) |
| Bone | `#e8e3d5` | Light theme background, body text on dark |
| Forest | `#1f6b3a` | Primary brand colour — buttons, live indicators, CTAs |
| Forest Mid | `#267d46` | Button hover, elevated forest |
| Forest Bright | `#2e9453` | Active indicators, terminal prompts |
| Gold | `#c8a96e` | Accent — headings emphasis, nav CTA, eyebrows, ampersand |
| Gold Bright | `#d4b87e` | Gold hover states |
| Gold Dim | `#7a6540` | Borders with gold, muted gold text |

### CSS variables — dark (Ink) theme

```css
--bg:           #080c09;
--bg-surface:   #0e1410;
--bg-card:      #131a14;
--bg-card-hover:#18211a;
--border:       #1e2b20;
--border-mid:   #253228;
--border-bright:#2e3f31;
--text:         #e8e3d5;   /* Bone */
--text-muted:   #7a7669;
--text-dim:     #404638;
--green:        #1f6b3a;   /* Forest */
--green-mid:    #267d46;
--green-bright: #2e9453;
--gold:         #c8a96e;
--gold-bright:  #d4b87e;
--gold-dim:     #7a6540;
```

### CSS variables — light (Bone) theme

```css
--bg:           #e8e3d5;   /* Bone */
--bg-surface:   #ddd8ca;
--bg-card:      #f0ebe0;
--bg-card-hover:#e8e1d2;
--border:       rgba(31,107,58,0.14);
--border-mid:   rgba(31,107,58,0.22);
--border-bright:rgba(31,107,58,0.38);
--text:         #0e1a10;   /* near-Ink */
--text-muted:   #4a4238;
--text-dim:     #8a7e6a;
--green:        #1f6b3a;   /* Forest — same */
--green-mid:    #267d46;
--green-bright: #2e9453;
--gold:         #b89050;   /* slightly deeper on bone */
--gold-bright:  #c8a96e;
--gold-dim:     #7a6540;
```

### Status colours (for risk matrices, callouts)

```css
--status-danger:  #8a1f1f;   /* Critical — dark red */
--status-warning: #7a5a18;   /* High — dark amber */
--status-caution: #1f6b3a;   /* Medium — Forest */
--status-success: #1a4a28;   /* Low — deep Forest */
```

Light theme status bg (use at 0.08 opacity):
- Critical bg: `rgba(138,31,31,0.08)`, border: `rgba(138,31,31,0.3)`
- High bg: `rgba(122,90,24,0.08)`, border: `rgba(122,90,24,0.3)`
- Medium bg: `rgba(31,107,58,0.08)`, border: `rgba(31,107,58,0.3)`
- Low bg: `rgba(26,74,40,0.05)`, border: `rgba(26,74,40,0.2)`

---

## Typography

```css
--font-display: 'Playfair Display', Georgia, serif;
--font-body:    'Plus Jakarta Sans', system-ui, sans-serif;
--font-mono:    'JetBrains Mono', monospace;
```

Google Fonts CDN (only external dependency):
```html
<link href="https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,400;0,500;0,700;1,400;1,500&family=Plus+Jakarta+Sans:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
```

### Usage rules

| Font | Use for |
|---|---|
| Playfair Display | Section h1/h2, hero headline, pull quotes, stat values |
| Playfair italic + gold | Emphasis within headings — the key word gets italic gold |
| Plus Jakarta Sans | Body copy, descriptions, paragraphs, nav links |
| JetBrains Mono | Eyebrow labels, stat labels, section numbers, mono metadata |

---

## Geometry

```css
--radius:    2px;    /* Sharp — all cards, buttons, inputs */
--radius-sm: 2px;    /* Same — no rounded pills anywhere */
--max-w:     1200px;
```

**No rounded buttons. No pill shapes. 2px across the board.**

---

## Texture

Dot-grid background — the P&A signature:

```css
body::before {
  content: '';
  position: fixed; inset: 0;
  background-image: radial-gradient(circle, #1a2e1c 1px, transparent 1px); /* dark */
  /* light: radial-gradient(circle, #b8aa8a 1px, transparent 1px) */
  background-size: 26px 26px;
  opacity: 0.5;
  pointer-events: none;
  z-index: 0;
}
```

Vertical grid lines (desktop only):
```css
.grid-lines {
  position: fixed; inset: 0; pointer-events: none; z-index: 0;
  display: flex; justify-content: space-between; padding: 0 var(--pad-x);
}
.grid-lines span {
  display: block; width: 1px; height: 100%;
  background: linear-gradient(to bottom, transparent, var(--border) 15%, var(--border) 85%, transparent);
  opacity: 0.45;
}
```

---

## The Ampersand

The brand mark. Always italic Playfair, always gold:

```html
<span class="amp">&amp;</span>
```

```css
.amp { color: var(--gold); font-style: italic; }
```

Use in: "Principal **&** Agent" in nav, footer, and cover blocks. Never plain `&`.

---

## Component patterns

### Eyebrow
```html
<div class="s-eyebrow">
  <span class="s-bar"></span>
  <span class="s-tag">Section Label</span>
  <span class="s-num">01 / 04</span>
</div>
```
```css
.s-bar { width: 22px; height: 1px; background: var(--gold-dim); }
.s-tag { font-family: var(--font-mono); font-size: 0.67rem; letter-spacing: 0.12em; text-transform: uppercase; color: var(--gold); }
.s-num { font-family: var(--font-mono); font-size: 0.62rem; color: var(--text-dim); letter-spacing: 0.06em; margin-left: auto; }
```

### Section heading
```html
<h2 class="s-title">Built by someone who runs<br>systems <em>like yours</em></h2>
```
```css
.s-title { font-family: var(--font-display); font-size: clamp(1.9rem, 3.5vw, 2.85rem); font-weight: 500; line-height: 1.15; letter-spacing: -0.01em; }
.s-title em { font-style: italic; color: var(--gold); }
```

### Pull quote
```html
<div class="about-quote">
  <p>"Quote text here."</p>
  <cite>— Name, Title</cite>
</div>
```
```css
.about-quote { padding: 1.75rem; border-left: 2px solid var(--gold-dim); background: rgba(200,169,110,0.04); border-radius: 0 2px 2px 0; }
.about-quote p { font-family: var(--font-display); font-style: italic; font-size: 1rem; color: var(--text-muted); line-height: 1.7; margin-bottom: 0.75rem; }
.about-quote cite { font-family: var(--font-mono); font-size: 0.67rem; color: var(--text-dim); letter-spacing: 0.06em; text-transform: uppercase; font-style: normal; }
```

### Risk callout (left-border)
```html
<div class="risk-block risk-critical">
  <div class="risk-level">Critical</div>
  <div class="risk-headline">Headline finding in one line</div>
  <div class="risk-detail">Supporting evidence or citation.</div>
</div>
```
```css
.risk-block { padding: 1rem 1.25rem; border-left: 3px solid; border-radius: 0 2px 2px 0; margin-bottom: 0.75rem; }
.risk-critical { background: rgba(138,31,31,0.08); border-color: rgba(138,31,31,0.4); }
.risk-high     { background: rgba(122,90,24,0.08);  border-color: rgba(122,90,24,0.4); }
.risk-medium   { background: rgba(31,107,58,0.08);  border-color: rgba(31,107,58,0.4); }
.risk-low      { background: rgba(26,74,40,0.05);   border-color: rgba(26,74,40,0.25); }
.risk-level { font-family: var(--font-mono); font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-dim); margin-bottom: 0.3rem; }
.risk-headline { font-weight: 600; font-size: 0.9rem; color: var(--text); margin-bottom: 0.25rem; }
.risk-detail { font-size: 0.84rem; color: var(--text-muted); line-height: 1.65; }
```

### Metric grid
```html
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-label">Walk Score</div>
    <div class="metric-val">92</div>
    <div class="metric-sub">Walker's Paradise</div>
  </div>
  <!-- repeat -->
</div>
```
```css
.metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 1px; background: var(--border); border: 1px solid var(--border); border-radius: 2px; overflow: hidden; margin-bottom: 4rem; }
.metric-card { background: var(--bg-card); padding: 1.75rem 1.5rem; }
.metric-label { font-family: var(--font-mono); font-size: 0.62rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-dim); margin-bottom: 0.5rem; }
.metric-val { font-family: var(--font-display); font-size: 2rem; font-weight: 500; color: var(--gold); line-height: 1; }
.metric-sub { font-size: 0.76rem; color: var(--text-muted); margin-top: 0.3rem; }
```

---

## Aesthetic brief

**"After Close"** — the feeling of a signed document that arrives on a partner's desk.

- Law-firm gravitas × AI research-lab precision
- NOT friendly SaaS, NOT crypto, NOT YC demo day
- Restrained. Every element earns its presence.

**Banned:**
- Pure `#000000` or `#ffffff`
- Blue, purple, teal in any form
- Hue-rotating gradients
- Rounded buttons (border-radius > 2px)
- Drop shadows on text
- Decorative icons that don't carry information

---

## Theme selection guide

| Use case | Theme |
|---|---|
| Property dossier for client review | Light (bone) — default |
| Anything for print or PDF circulation | Light (bone) |
| Internal P&A brief | Dark (ink) |
| Investor deck | Dark (ink) |
| pna.agency website | Dark (ink) — canonical |
| Uncertainty | Dark (ink) |
