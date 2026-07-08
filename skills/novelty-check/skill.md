---
name: aris-novelty-check
description: >
  Verify whether a research idea, approach, or solution is genuinely novel against recent literature.
  Use before committing time to an idea, before client proposals, or before pitching an agentic solution.
  Trigger on: "novelty check [idea]", "has anyone done [X]", "is [idea] novel",
  "check if [approach] exists", "prior art for [idea]", "verify [solution] is new".
version: 1.0.0
source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/tree/main/skills/novelty-check
adapted: true
tags: [research, novelty, prior-art, validation, ideas]
---

# Novelty Check

Systematic literature sweep to verify an idea is genuinely new before investing in it.

---

## Trigger Patterns

| User says | What fires |
|---|---|
| `novelty check [idea]` | Full novelty verification |
| `has anyone done [X]` | Full verification |
| `is [approach] novel` | Full verification |
| `prior art for [idea]` | Full verification |
| `check if [solution] exists` | Full verification |

---

## Phase A: Extract Core Claims

Read the idea description. Identify 3-5 core technical claims that would need to be novel:
- What exactly is the method/approach?
- What problem does it solve?
- What is the mechanism?
- What makes it different from obvious alternatives?

Write these out explicitly before searching. Vague novelty checks produce false negatives.

---

## Phase B: Multi-Source Literature Search

For EACH core claim, search across multiple sources:

**Web sources:**
```
WebSearch: "[key concept] [mechanism] survey"
WebSearch: "[problem] [approach] prior work"
WebSearch: "[technique] existing work limitations"
```

**Academic sources:**
```
WebSearch site:arxiv.org "[claim]"
WebSearch site:semanticscholar.org "[claim]"
WebSearch site:paperswithcode.com "[method]"
```

**Adjacent domains:**
- Search for the same idea in adjacent fields (it may be novel in field A but old in field B)
- Check industry implementations (GitHub, technical blog posts, product docs)

Minimum 8 searches across at least 3 different query framings.

---

## Phase C: Evidence Evaluation

For each paper/work found, assess:
- Does it implement the same mechanism?
- Does it solve the same problem?
- Is it close enough to invalidate novelty?

Classify each finding:
- **Direct prior art** — essentially the same idea
- **Related work** — similar but meaningfully different
- **Tangentially related** — same domain, different approach
- **Not relevant** — false match

---

## Phase D: Novelty Assessment

Render a verdict:

```markdown
## Novelty Check: [Idea Name]

### Core Claims Checked
1. [claim 1]
2. [claim 2]
...

### Verdict: NOVEL / PARTIALLY NOVEL / NOT NOVEL

### Direct Prior Art
- [paper/work]: [how similar it is and what it does]

### Related Work (does not invalidate novelty)
- [paper/work]: [how it differs]

### Differentiation
[What specifically makes this idea different from the closest prior art]

### Recommended Next Steps
- [what to do: proceed / pivot / investigate further / abandon]

### Sources
[all URLs checked]
```

---

## Novelty Thresholds

- **NOVEL**: No direct prior art found. Related work exists but does not implement the same mechanism.
- **PARTIALLY NOVEL**: Core idea exists but proposed extension/application is new.
- **NOT NOVEL**: Direct prior art found that implements the same mechanism for the same purpose.

Be honest. The goal is to save time, not to confirm what the user hopes to hear.
