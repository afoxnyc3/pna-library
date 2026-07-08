---
name: aris-idea-discovery
description: >
  Full idea discovery pipeline: survey the field, generate ideas, check novelty, get critical feedback,
  and refine the best idea into a concrete proposal. Works for research directions or client solution design.
  Trigger on: "idea discovery [direction]", "find ideas for [topic]", "discover approaches for [problem]",
  "full idea pipeline [direction]", "generate and validate ideas for [topic]".
version: 1.0.0
source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/tree/main/skills/idea-discovery
adapted: true
tags: [research, ideas, discovery, pipeline, brainstorming]
---

# Idea Discovery

Full pipeline from broad direction to validated, refined proposal. Chains survey → brainstorm → novelty check → critique → refine.

---

## Trigger Patterns

| User says | What fires |
|---|---|
| `idea discovery [direction]` | Full pipeline |
| `find ideas for [topic]` | Full pipeline |
| `discover approaches for [problem]` | Full pipeline |
| `generate and validate ideas for [topic]` | Full pipeline |

---

## Pipeline Overview

```
feynman-literature-review   →   brainstorm   →   aris-novelty-check   →   critique   →   aris-research-refine
     (survey field)            (generate ideas)    (filter non-novel)     (rank + stress)    (sharpen top idea)
```

Each phase builds on the previous. The output is a ranked idea list plus a refined proposal for the top idea.

---

## Phase 1: Survey the Field

Run a literature sweep on the direction. Use the `feynman-literature-review` skill or search directly:
- What approaches currently exist?
- Where do they fail?
- What gaps are consistently mentioned?
- What would be a meaningful advance?

Save findings to `idea-stage/LITERATURE_SURVEY.md`.

---

## Phase 2: Generate Ideas

From the survey, brainstorm 5-10 candidate ideas. For each idea:

```markdown
### Idea [N]: [Name]
- **Hypothesis**: [what we think will work]
- **Mechanism**: [how it would work]
- **Gap addressed**: [which gap from the survey it targets]
- **Why it might work**: [reasoning]
- **Why it might not**: [honest failure modes]
- **Effort estimate**: [rough scope — small/medium/large]
```

Save to `idea-stage/IDEA_CANDIDATES.md`.

Don't filter aggressively here — generate broadly, filter in Phase 3.

---

## Phase 3: Novelty Filter

For each idea, run a quick novelty check (use `aris-novelty-check` skill or search directly):
- Has this been done?
- Is the key mechanism novel?

Mark each idea: NOVEL / PARTIALLY NOVEL / NOT NOVEL.
Remove NOT NOVEL ideas. For PARTIALLY NOVEL, note what specifically remains new.

---

## Phase 4: Rank and Stress Test

For the remaining novel ideas, rank by:
1. **Impact** — if it works, how much does it matter?
2. **Feasibility** — how likely is it to work given current tools/knowledge?
3. **Differentiation** — how clearly distinct from prior work?
4. **Scope** — can it be validated without massive infrastructure?

Stress test the top 2-3:
- What's the single most likely failure mode?
- What would you need to believe for this to work?
- What's the smallest experiment that would tell you if it's worth pursuing?

Update `idea-stage/IDEA_CANDIDATES.md` with rankings and stress test results.

---

## Phase 5: Refine Top Idea

Take the top-ranked idea and run `aris-research-refine` on it:
- Freeze the Problem Anchor
- Write a concrete proposal
- Apply adversarial review

Output: `refine-logs/FINAL_PROPOSAL.md`

---

## Phase 6: Deliver

Final deliverables:
```
idea-stage/
  LITERATURE_SURVEY.md
  IDEA_CANDIDATES.md         ← all ideas, ranked, with novelty status
refine-logs/
  PROBLEM_ANCHOR.md
  FINAL_PROPOSAL.md          ← top idea, refined and concrete
```

Present summary to user: top-ranked idea, why it won, and what the refined proposal says.

---

## Configuration

- **AUTO_PROCEED**: If set, skip user confirmation at each phase gate and proceed with best option automatically
- **Max ideas to generate**: Default 10. Adjust if direction is narrow (use 5) or very broad (use 15)
- **Refine top N**: Default 1. Can refine top 2-3 if client needs options to choose from
