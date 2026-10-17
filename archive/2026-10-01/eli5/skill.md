---
name: feynman-eli5
description: >
  Explain research papers or technical concepts in plain English with concrete analogies and clear takeaways.
  Use when asked to explain something complex simply, ELI5, break down a paper, or remove jargon.
  Trigger on: "ELI5 [paper/concept]", "explain [paper] simply", "what does [paper] actually mean",
  "break down [concept] for me", "explain [topic] without jargon", "summarize [paper] in plain English".
version: 1.0.0
source: https://github.com/getcompanion-ai/feynman/tree/main/skills/eli5
adapted: true
tags: [explanation, eli5, papers, plain-english, communication]
---

# ELI5

Complex ideas in plain English. Short sentences. One good analogy. No jargon without immediate definition.

---

## Trigger Patterns

| User says | What fires |
|---|---|
| `ELI5 [paper/concept]` | Plain-language explanation |
| `explain [paper] simply` | Plain-language explanation |
| `what does [paper] actually mean` | Plain-language explanation |
| `break down [concept] for me` | Plain-language explanation |
| `explain [topic] without jargon` | Plain-language explanation |

---

## Process

**If a specific paper is named (arXiv ID, DOI, URL, title):**
- Fetch the paper: use `alpha get <id>` if available, otherwise WebFetch on the abstract page
- Ground the explanation in the actual paper

**If only a topic is given:**
- Identify 1-3 representative papers
- Anchor the explanation around the clearest or most important one

---

## Output Structure

Always use this structure:

**One-Sentence Summary**
[What did this paper do / what is this concept, in one sentence]

**Big Idea**
[The core insight. Why it matters. What problem it solves.]

**How It Works**
[The mechanism. Step by step if needed. Use analogies heavily.]

**Why It Matters**
[Real-world implications. Who cares and why.]

**What To Be Skeptical Of**
[Limitations, assumptions, things the paper doesn't prove, common misreadings.]

**If You Remember 3 Things**
1. [Most important point]
2. [Second most important]
3. [Third most important]

---

## Guidelines

- Short sentences. Concrete words.
- Define jargon immediately after using it, or cut it entirely.
- One good analogy over several weak ones.
- Separate what the paper actually shows from speculation or interpretation.
- Keep inline unless user explicitly asks to save as a file.
- Never overstate confidence in the explanation — flag where you're simplifying away nuance.
