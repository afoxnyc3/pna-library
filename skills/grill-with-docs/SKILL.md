---
name: grill-with-docs
description: Relentless Socratic grilling session that stress-tests a plan or design, challenges it against the project's existing domain model, sharpens terminology, and updates documentation (CONTEXT.md and ADRs) inline as decisions crystallise. Use when the user wants to stress-test a plan, get grilled on their design, challenge their assumptions, or says "grill me" or "grill me with docs". If no CONTEXT.md or ADRs exist, run the grilling without the doc-update step.
---

# Grill With Docs

## Purpose

Same relentless interview as `grill-me`, but grounded in the project's living documentation. Every claim gets checked against the domain glossary. Every resolved decision that warrants it gets captured as an ADR. The session ends with the docs in better shape than it started.

## Instructions

Start immediately. No preamble.

### During codebase exploration

When the user names a project or path, locate its documentation before the first question:

**Standard single-context layout:**
```
~/dev/projects/<slug>/
├── CONTEXT.md           ← domain glossary, bounded context language
├── docs/
│   └── adr/             ← architectural decision records
│       └── 0001-*.md
└── src/
```

**Multi-context layout (CONTEXT-MAP.md exists at repo root):**
```
~/dev/projects/<slug>/
├── CONTEXT-MAP.md        ← points to each context's location
├── docs/
│   └── adr/             ← system-wide decisions
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/adr/
    └── billing/
        ├── CONTEXT.md
        └── docs/adr/
```

Create files lazily. Do not create `CONTEXT.md` or `docs/adr/` until you have something to write into them.

### Questioning discipline

1. Ask questions one at a time. Provide your recommended answer with each question.
2. Walk every branch of the decision tree in dependency order.
3. If a question can be answered by reading the codebase or docs, do that instead of asking.

### Challenge against the glossary

When the user uses a term that conflicts with `CONTEXT.md`, call it out immediately:

> "Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?"

When the user uses vague or overloaded terms, propose a precise canonical term:

> "You said 'account' — do you mean Customer or User? Those are different things in your model."

### Stress-test with concrete scenarios

When domain relationships are in play, invent edge-case scenarios to force precision. Do not accept "it depends" as a closed branch.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If there is a contradiction, surface it:

> "Your code cancels entire Orders, but you just said partial cancellation is possible. Which is right?"

### Update CONTEXT.md inline

When a term is resolved, update `CONTEXT.md` immediately. Do not batch. Format:

```markdown
## Glossary

### <Term>
<One sentence definition in plain language meaningful to a domain expert.>
Distinct from: <related term if confusion is likely>.
```

Do not couple `CONTEXT.md` to implementation details. Only terms meaningful to domain experts belong there.

### Offer ADRs sparingly

Create an ADR only when all three are true:

1. **Hard to reverse** — the cost of changing course later is real.
2. **Surprising without context** — a future reader will wonder "why did they do it this way?"
3. **The result of a real tradeoff** — there were genuine alternatives and you picked one for specific reasons.

If any condition is missing, skip the ADR.

ADR format (save to `docs/adr/<NNNN>-<slug>.md`):

```markdown
# <NNNN>. <Title>

Date: <YYYY-MM-DD>

## Status

Accepted

## Context

<What situation forced this decision? What constraints applied?>

## Decision

<What did we decide?>

## Consequences

<What becomes easier? What becomes harder? What is now locked in?>
```

## Workflow

1. User names the plan and project slug (or path).
2. Locate and read `CONTEXT.md` and any existing ADRs before the first question.
3. Identify the top-level decisions and dependencies in the plan.
4. Begin the interview: one question at a time, recommended answer included.
5. After each resolved term, update `CONTEXT.md` immediately.
6. After each resolved architectural decision that meets the ADR bar, write the ADR immediately.
7. When all branches are resolved or parked, produce the end-of-session report.

## Report

End of session output:

- Decisions made (what was resolved and how)
- Decisions parked (what was explicitly deferred and why)
- Risks accepted (tradeoffs the user acknowledged and moved past)
- Glossary terms added or updated in `CONTEXT.md`
- ADRs written (paths)
- Open questions remaining
