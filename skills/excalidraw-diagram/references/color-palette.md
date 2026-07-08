# Color Palette & Brand Style — Principal & Agent

**This is the single source of truth for all colors and brand-specific styles.** Tuned to the Principal & Agent identity: Forest green + Gold on Bone, restrained, law-firm-meets-research-lab. Everything else in the skill is universal.

**Brand rules for every diagram:**
- Use `roughness: 0` on all elements — clean lines, not sketchy. P&A is precise, not hand-drawn.
- Use `fontFamily: 2` (normal) for titles and labels, `fontFamily: 3` (code) for mono metadata, evidence, and section numbers.
- No pure black or pure white. No blue/purple/teal. Every element earns its place.

---

## Shape Colors (Semantic)

Colors encode meaning, not decoration. Each semantic purpose has a fill/stroke pair. Fills are light (bone/forest/gold tints); strokes are the deep brand hue.

| Semantic Purpose | Fill | Stroke |
|------------------|------|--------|
| Primary/Neutral | `#d9e5dc` | `#1f6b3a` |
| Secondary | `#e8e3d5` | `#267d46` |
| Tertiary | `#f0ebe0` | `#2e9453` |
| Start/Trigger | `#efe3c9` | `#7a6540` |
| End/Success | `#cfe4d5` | `#1a4a28` |
| Warning/Reset | `#ece0c2` | `#7a5a18` |
| Decision | `#f2e6c8` | `#b89050` |
| AI/LLM | `#e0dcae` | `#1f6b3a` |
| Inactive/Disabled | `#ddd8ca` | `#7a6540` (use dashed stroke) |
| Error | `#eccccc` | `#8a1f1f` |

**Rule**: Always pair a darker stroke with a lighter fill for contrast.

---

## Text Colors (Hierarchy)

Use color on free-floating text to create visual hierarchy without containers.

| Level | Color | Use For |
|-------|-------|---------|
| Title | `#1f6b3a` | Section headings, major labels (Forest) |
| Subtitle | `#267d46` | Subheadings, secondary labels |
| Body/Detail | `#4a4238` | Descriptions, annotations, metadata (muted) |
| Accent/Emphasis | `#b89050` | The one word that matters — the P&A gold |
| On light fills | `#0e1a10` | Text inside light-colored shapes (near-Ink) |
| On dark fills | `#e8e3d5` | Text inside dark-colored shapes (Bone) |

---

## Evidence Artifact Colors

Used for code snippets, data examples, and other concrete evidence inside technical diagrams.

| Artifact | Background | Text Color |
|----------|-----------|------------|
| Code snippet | `#080c09` | `#e8e3d5` (Bone) |
| JSON/data example | `#080c09` | `#2e9453` (Forest Bright) |
| Terminal/CLI | `#080c09` | `#c8a96e` (Gold) |
| Inline label / eyebrow | `transparent` | `#7a6540` (Gold Dim) |

---

## Default Stroke & Line Colors

| Element | Color |
|---------|-------|
| Arrows | Use the stroke color of the source element's semantic purpose |
| Structural lines (dividers, trees, timelines) | Gold Dim (`#7a6540`) or Forest (`#1f6b3a`) |
| Marker dots (fill + stroke) | Gold (`#c8a96e`) |

---

## Background

| Property | Value |
|----------|-------|
| Canvas background | `#faf9f5` (near-Bone; never pure white) |
| Dark-theme canvas (investor/web) | `#080c09` (Ink) |

---

## Reference — Named Brand Colors

| Token | Hex | Role |
|---|---|---|
| Ink | `#080c09` | Dark background |
| Bone | `#e8e3d5` | Light background / text on dark |
| Forest | `#1f6b3a` | Primary — strokes, CTAs |
| Forest Bright | `#2e9453` | Active / positive |
| Gold | `#c8a96e` | Accent, emphasis, the ampersand |
| Gold Dim | `#7a6540` | Muted gold, borders |
| Danger | `#8a1f1f` | Critical / error |
| Warning | `#7a5a18` | High / caution |
