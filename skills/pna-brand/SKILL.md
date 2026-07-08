# pna-brand

Source-of-truth design system for all Principal & Agent client deliverables.

## Trigger

Load this skill when:
- Starting any client-facing HTML report, dossier, or deck
- Building any P&A-branded document
- Checking brand compliance before generating visual output
- Using `report-template-light.html` or `slides-template-light.html`

## On load

1. Read `DESIGN_TOKENS.md` — do not make any colour, font, radius, or layout decision before reading it
2. Identify the correct template: `report-template-light.html` (dossiers, client docs) or `report-template.html` (dark, internal/web)
3. Copy the template as the scaffold. Replace `{{PLACEHOLDERS}}`. Do not modify the skill files in place.

## Files

| File | Purpose |
|---|---|
| `DESIGN_TOKENS.md` | Complete colour palette, typography, component patterns, aesthetic brief |
| `report-template-light.html` | Bone/light scaffold for property dossiers and client deliverables |
| `report-template.html` | Ink/dark scaffold for internal briefs and web (same structure, dark tokens) |
| `slides-template-light.html` | 16:9 slide deck scaffold, bone theme |

## Brand model

Deliverables are **from Principal & Agent**, **prepared for [Client Name]**. P&A brand is on the artifact. Client identity appears only in cover metadata.

## Non-negotiables

- Read DESIGN_TOKENS.md before every session. Every visual decision flows from it.
- Never invent colours, fonts, border-radii, or component patterns outside the tokens.
- Never deploy automatically. Local-first — Alex deploys explicitly.
- Never use the ALPA slide-deck-generator skill — use `slides-template-light.html`.
