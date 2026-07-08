# Excalidraw Diagram Skill

A coding agent skill that generates beautiful and practical Excalidraw diagrams from natural language descriptions. Not just boxes-and-arrows - diagrams that **argue visually**.

Compatible with any coding agent that supports skills. For agents that read from `.claude/skills/` (like [Claude Code](https://docs.anthropic.com/en/docs/claude-code) and [OpenCode](https://github.com/nicepkg/OpenCode)), just drop it in and go.

## What Makes This Different

- **Diagrams that argue, not display.** Every shape/group of shapes mirrors the concept it represents — fan-outs for one-to-many, timelines for sequences, convergence for aggregation. No uniform card grids.
- **Evidence artifacts.** As an example, technical diagrams include real code snippets and actual JSON payloads.
- **Built-in visual validation.** A Playwright-based render pipeline lets the agent see its own output, catch layout issues (overlapping text, misaligned arrows, unbalanced spacing), and fix them in a loop before delivering.
- **Brand-customizable.** All colors and brand styles live in a single file (`references/color-palette.md`). Swap it out and every diagram follows your palette.

## Installation

Clone or download this repo, then copy it into your project's `.claude/skills/` directory:

```bash
git clone https://github.com/coleam00/excalidraw-diagram-skill.git
cp -r excalidraw-diagram-skill .claude/skills/excalidraw-diagram
```

## Setup

The skill includes a render pipeline that lets the agent visually validate its diagrams. There are two ways to set it up:

**Option A: Ask your coding agent (easiest)**

Just tell your agent: *"Set up the Excalidraw diagram skill renderer by following the instructions in SKILL.md."* It will run the commands for you.

**Option B: Manual**

```bash
cd .claude/skills/excalidraw-diagram/references
uv sync
uv run playwright install chromium
```

## Usage

Ask your coding agent to create a diagram:

> "Create an Excalidraw diagram showing how the AG-UI protocol streams events from an AI agent to a frontend UI"

The skill handles the rest — concept mapping, layout, JSON generation, rendering, and visual validation.

## Customize Colors

Edit `references/color-palette.md` to match your brand. Everything else in the skill is universal design methodology.

## File Structure

```
excalidraw-diagram/
  SKILL.md                          # Design methodology + workflow
  references/
    color-palette.md                # Brand colors (edit this to customize)
    element-templates.md            # JSON templates for each element type
    json-schema.md                  # Excalidraw JSON format reference
    render_excalidraw.py            # Render .excalidraw to PNG
    render_template.html            # Browser template for rendering
    excalidraw.bundle.mjs           # Vendored offline Excalidraw bundle (no CDN)
    fonts/                          # Vendored Excalidraw fonts (served locally)
    pyproject.toml                  # Python dependencies (playwright)
```

## Offline Rendering

The render pipeline is fully offline. The Excalidraw library is vendored as a
single self-contained ESM bundle (`references/excalidraw.bundle.mjs`, built
from `@excalidraw/excalidraw@0.18.1`) and fonts are vendored in
`references/fonts/`. Both are served to headless Chromium over a loopback
`http.server` — no network egress is required at render time, so the pipeline
works in sandboxed agent runtimes and CI (e.g. GitHub Actions) without
special allowances.

One exception: the CJK font (Xiaolai, ~12MB) is not vendored to keep the
skill small. Diagrams containing CJK text will render with a fallback font.

To rebuild the bundle (e.g. to bump the Excalidraw version):

```bash
mkdir /tmp/excalibuild && cd /tmp/excalibuild
npm install @excalidraw/excalidraw@0.18.1 esbuild
echo 'export { exportToSvg } from "@excalidraw/excalidraw";' > entry.js
npx esbuild entry.js --bundle --format=esm --minify \
  --define:process.env.NODE_ENV='"production"' \
  --outfile=excalidraw.bundle.mjs
cp excalidraw.bundle.mjs <skill>/references/
# fonts (skip Xiaolai unless you need CJK):
cp -R node_modules/@excalidraw/excalidraw/dist/prod/fonts/{Assistant,Cascadia,ComicShanns,Excalifont,Liberation,Lilita,Nunito,Virgil} <skill>/references/fonts/
```
