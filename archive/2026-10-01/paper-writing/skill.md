---
name: feynman-paper-writing
description: >
  Turn research findings into a polished paper-style draft with sections, equations, and citations.
  Use when asked to write a paper, draft a report, write up findings, or produce a technical document from research.
  Trigger on: "write a paper on [topic]", "draft [report]", "write up findings on [topic]",
  "produce a technical document on [topic]", "paper draft for [topic]".
version: 1.0.0
source: https://github.com/getcompanion-ai/feynman/tree/main/skills/paper-writing
adapted: true
tags: [writing, paper, draft, academic, report]
---

# Paper Writing

Turns collected research into a structured, cited, submission-ready draft.

---

## Trigger Patterns

| User says | What fires |
|---|---|
| `write a paper on [topic]` | Full draft pipeline |
| `draft [report]` | Full pipeline |
| `write up findings on [topic]` | Full pipeline |
| `produce a technical document on [topic]` | Full pipeline |

---

## Step 1: Outline

Derive a short slug (lowercase, hyphens, ≤5 words).

Write `outputs/.plans/<slug>.md` with:
- Proposed title
- Sections (at minimum: Abstract, Introduction, Related Work, Method/Synthesis, Evidence/Results, Limitations, Conclusion)
- Key claims to make in each section
- Source material to draw from (files, URLs, research notes)
- Verification log for critical claims, figures, and calculations

Briefly summarize outline and continue immediately.

---

## Step 2: Draft

Write the full paper draft to `papers/<slug>.md`.

Structure:
```markdown
# [Title]

## Abstract
[150-250 words]

## 1. Introduction
[Problem, motivation, contributions]

## 2. Related Work
[Positioned against prior work with citations]

## 3. Method / Synthesis
[Core contribution — described precisely]

## 4. Evidence / Experiments / Analysis
[Results, benchmarks, examples — all source-backed]

## 5. Limitations
[Honest scope and failure modes]

## 6. Conclusion
[What was shown, what comes next]

## Sources
[All URLs and references]
```

Guidelines:
- Use clean Markdown with LaTeX for equations that add clarity
- Every number, benchmark, table, and figure needs a source URL or provenance note
- If evidence is missing: use a placeholder `[NEEDED: ...]` or `[Proposed experiment: ...]` — never fabricate
- Mark tentative results as tentative before delivery

---

## Step 3: Cite

Add inline citations `[N]` for every claim. Verify every URL. Build a numbered Sources appendix.

---

## Step 4: Review

Sweep for:
- Claims stronger than their evidence (downgrade or mark tentative)
- Unsupported numbers (remove or placeholder)
- Missing related work (flag as open)

---

## Step 5: Deliver

Final draft at `papers/<slug>.md`.

---

## Output Structure

```
outputs/
  .plans/<slug>.md
papers/
  <slug>.md              ← final draft
```
