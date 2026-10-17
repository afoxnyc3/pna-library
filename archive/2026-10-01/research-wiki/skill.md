---
name: aris-research-wiki
description: >
  Persistent research knowledge base that accumulates papers, ideas, experiments, and claims
  across sessions. Karpathy LLM Wiki pattern — compile once, keep current, don't re-derive.
  Use when asked to build or query a research knowledge base, add papers to a project wiki,
  track ideas and their status, or maintain a persistent field map.
  Trigger on: "research wiki [topic]", "add to wiki", "query wiki", "build knowledge base for [topic]",
  "what do we know about [topic]", "update the wiki with [paper/idea/result]".
version: 1.0.0
source: https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/tree/main/skills/research-wiki
adapted: true
tags: [research, wiki, knowledge-base, karpathy, persistent-memory]
---

# Research Wiki

Persistent, compounding knowledge base. Every paper read, idea tested, and result obtained makes the wiki smarter. Inspired by [Karpathy's LLM Wiki pattern](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f).

Unlike one-off surveys that are used and forgotten, the wiki accumulates across sessions.

---

## Trigger Patterns

| User says | What fires |
|---|---|
| `research wiki init [topic]` | Initialize new project wiki |
| `add to wiki [paper/idea/result]` | Ingest new entity |
| `query wiki [question]` | Search and synthesize from wiki |
| `update wiki [entity-id]` | Update existing entity |
| `wiki stats` | Show what's in the wiki |
| `wiki lint` | Check for broken relationships or stale entries |

---

## Wiki Structure

```
wiki/
  papers/         ← research papers with metadata and annotations
  ideas/          ← research ideas (proposed, tested, failed)
  experiments/    ← experiment runs with results
  claims/         ← testable claims with evidence status
  graph/
    edges.jsonl   ← typed relationships between entities
  WIKI_INDEX.md   ← master index, human-readable summary
```

Each entity has a node ID:
- Papers: `paper:<slug>` (e.g. `paper:attention-is-all-you-need`)
- Ideas: `idea:<id>` (e.g. `idea:001`)
- Experiments: `exp:<id>` (e.g. `exp:001`)
- Claims: `claim:<id>` (e.g. `claim:001`)

---

## Subcommands

### `init`
Create the wiki directory structure and `WIKI_INDEX.md`. Run once per project.

```bash
mkdir -p wiki/{papers,ideas,experiments,claims,graph}
touch wiki/graph/edges.jsonl
```

Create `wiki/WIKI_INDEX.md` with project name, domain, and empty sections.

### `ingest` (add paper/idea/result)
For each entity being added:
1. Determine entity type (paper / idea / experiment / claim)
2. Create entity file in the appropriate directory
3. Extract: title, key claims, methods, evidence, status
4. Identify relationships to existing entities and append to `graph/edges.jsonl`
5. Update `WIKI_INDEX.md`

Paper entity format:
```markdown
# [Paper Title]
- **ID**: paper:<slug>
- **Source**: [URL/arXiv ID]
- **Date**: [year]
- **Key Claims**: [list]
- **Methods**: [brief]
- **Evidence**: [what it shows]
- **Relevance**: [why it matters to this project]
- **Status**: read | skimmed | to-read
- **Annotations**: [your notes]
```

Idea entity format:
```markdown
# [Idea Name]
- **ID**: idea:<id>
- **Status**: proposed | in-progress | tested | failed | succeeded
- **Hypothesis**: [what we think will work]
- **Based on**: [paper IDs that inspired this]
- **Contradicts**: [ideas this conflicts with]
- **Result**: [outcome if tested]
- **Notes**: [learnings]
```

Experiment entity format:
```markdown
# [Experiment Name]
- **ID**: exp:<id>
- **Date**: [date]
- **Tests**: [idea ID or claim ID]
- **Setup**: [brief description]
- **Metric**: [what was measured]
- **Result**: [numerical result]
- **Status**: success | failure | inconclusive | blocked
- **Notes**: [what we learned]
```

### `query`
Given a question:
1. Read `WIKI_INDEX.md` to identify relevant entity types
2. Search entity files using Grep for relevant keywords
3. Read matching entity files
4. Traverse `graph/edges.jsonl` for related entities
5. Synthesize a response from wiki content only — clearly distinguish wiki knowledge from model knowledge
6. Note gaps: what the wiki doesn't cover yet

### `update`
Update an existing entity's status, add annotations, or link new relationships:
1. Read existing entity file
2. Apply update
3. Append new edges to `graph/edges.jsonl` if relationships changed
4. Update `WIKI_INDEX.md` if status changed

### `stats`
Report:
- Total entities by type (papers / ideas / experiments / claims)
- Ideas by status
- Experiments by status
- Most-linked entities (hub nodes in the graph)
- Last updated

### `lint`
Check for:
- Entity files referenced in edges but not present
- Ideas with no linked papers
- Claims with no linked experiments
- Stale "in-progress" experiments (> 30 days)

---

## Edge Schema

Each line in `graph/edges.jsonl`:
```json
{
  "from": "paper:slug",
  "to": "idea:001",
  "type": "inspired",
  "note": "optional context"
}
```

Relationship types: `inspired`, `contradicts`, `supports`, `tests`, `depends-on`, `extends`, `failed-by`, `succeeded-by`

---

## Integration with Other Skills

- After `feynman-deep-research`: ingest papers found into wiki
- After `feynman-literature-review`: bulk ingest all surveyed papers
- Before `feynman-source-comparison`: query wiki for existing knowledge on the items being compared
- After any experiment: update the relevant experiment entity
