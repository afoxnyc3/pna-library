---
name: grill-me
description: Relentless Socratic interview that stress-tests a plan, design, or decision by walking every branch of the decision tree. Use when the user wants to stress-test a plan, get grilled on their design, challenge their assumptions, or says "grill me".
---

# Grill Me

## Purpose

Force rigorous thinking on a plan or design before committing to it. The model acts as a tough but fair interviewer — not a yes-and partner. Every branch of the decision tree gets walked. Every assumption gets challenged. The session ends only when there is genuine shared understanding of the design, including its tradeoffs.

## Instructions

Start immediately. No preamble.

1. Ask questions one at a time. Wait for the answer before moving to the next question.
2. For each question, provide your recommended answer alongside it. The user may agree, disagree, or refine — the goal is to surface the reasoning, not to lecture.
3. Walk every branch of the decision tree: when a question is answered, identify the next open question it creates. Do not skip branches because they seem obvious.
4. Resolve dependencies between decisions before branching deeper. If decision B depends on decision A, close A first.
5. If a question can be answered by exploring the codebase, explore the codebase instead of asking. Only ask when the codebase does not contain the answer.
6. Challenge vague answers. "We'll figure it out later" closes no branch. Push for specificity or explicitly park the decision with a note that it is unresolved.
7. Keep going until every branch is resolved or explicitly parked. Do not stop early because the plan feels solid on the surface.

## Workflow

1. Ask the user to describe the plan or design being grilled.
2. Identify the top-level decisions and dependencies.
3. Start with the decision that blocks the most others.
4. For each question: state the question, give your recommended answer, wait for input.
5. When a branch resolves, confirm closure and move to the next open branch.
6. When all branches are resolved or parked, produce a brief summary of what was decided, what was parked, and any risks you surfaced but the user chose to accept.

## Report

End of session output:

- Decisions made (what was resolved and how)
- Decisions parked (what was explicitly deferred and why)
- Risks accepted (tradeoffs the user acknowledged and moved past)
- Open questions remaining (if any branch was never resolved)
