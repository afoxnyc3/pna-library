---
name: feynman-source-comparison
description: >
  Compare multiple sources, papers, tools, frameworks, or approaches and produce a grounded comparison matrix.
  Use when asked to compare options, contrast approaches, evaluate alternatives, or build a decision matrix.
  Trigger on: "compare [A] vs [B]", "comparison of [options]", "which is better [A] or [B]",
  "evaluate [options]", "contrast [approaches]", "decision matrix for [topic]".
version: 1.0.0
source: https://github.com/getcompanion-ai/feynman/tree/main/skills/source-comparison
adapted: true
tags: [research, comparison, decision-matrix, vendor-selection, analysis]
---

# Source Comparison

Grounded comparison matrix with agreements, disagreements, and confidence levels. No unsourced opinions.

---

## Trigger Patterns

| User says | What fires |
|---|---|
| `compare [A] vs [B]` | Full comparison pipeline |
| `comparison of [options]` | Full comparison pipeline |
| `which is better [A] or [B]` | Full pipeline with recommendation |
| `evaluate [options]` | Full pipeline |
| `decision matrix for [topic]` | Full pipeline with scoring |
| `contrast [approaches]` | Full pipeline |

---

## Step 1: Plan

Derive a short slug from the comparison topic (lowercase, hyphens, ≤5 words).

Write `outputs/.plans/<slug>.md` with:
- What is being compared (items, dimensions)
- Which sources to consult per item
- Matrix dimensions (e.g. performance, cost, maturity, API quality, community)
- Expected output structure

Briefly summarize the plan and continue immediately. Do not wait for confirmation unless the user asked for plan review.

---

## Step 2: Gather

For each item being compared:
- Search using WebSearch and fetch key pages with defuddle or WebFetch
- For papers/academic claims: use WebSearch targeting arxiv, semantic scholar, or official sites
- Record source URL, key claim, evidence type, and caveats for each data point
- Save notes to `outputs/.drafts/<slug>-research.md`

For broad comparisons (3+ items, many dimensions): launch parallel Task agents, one per item, each writing to `outputs/.drafts/<slug>-[item].md`.

---

## Step 3: Build Matrix

Produce a comparison matrix in Markdown table format with columns:
- **Source/Item**
- **Key Claims**
- **Evidence Type** (benchmark, paper, docs, user report)
- **Caveats**
- **Confidence** (High / Medium / Low)

For quantitative metrics: include a summary table with numbers.
Clearly distinguish: agreement across sources, disagreement, and uncertainty.

---

## Step 4: Verify

Check every URL cited in the matrix. Mark unverifiable sources as `[unverified]`.

---

## Step 5: Deliver

Save to `outputs/<slug>-comparison.md`.

End with a `Sources` section listing every URL used.

If the user needs a recommendation: add a `Recommendation` section with explicit reasoning anchored to the matrix, not opinion.

---

## Output Structure

```
outputs/
  .plans/<slug>.md
  .drafts/<slug>-research.md
  <slug>-comparison.md          ← final
```
