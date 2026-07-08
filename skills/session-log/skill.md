---
name: feynman-session-log
description: >
  Write a durable session log capturing completed work, findings, open questions, and next steps.
  Use when asked to log progress, save session notes, write up what was done, or create a research diary entry.
  Trigger on: "log this session", "save session notes", "write up what we did", "create a session log",
  "document this session", "research diary entry".
version: 1.0.0
source: https://github.com/getcompanion-ai/feynman/tree/main/skills/session-log
adapted: true
tags: [session, logging, notes, documentation, continuity]
---

# Session Log

Durable record of what was done, what was found, what's still open, and what comes next.

---

## Trigger Patterns

| User says | What fires |
|---|---|
| `log this session` | Write session log |
| `save session notes` | Write session log |
| `write up what we did` | Write session log |
| `create a session log` | Write session log |
| `document this session` | Write session log |

---

## Process

Summarize the current session:

1. **What was done** — concrete actions taken, decisions made, code written, research run
2. **Strongest findings or decisions** — the 2-3 things that actually matter from this session
3. **Open questions** — unresolved questions, ambiguities, things to revisit
4. **Unresolved risks** — anything that could break or needs validation
5. **Concrete next steps** — specific tasks, not vague intentions
6. **Artifact references** — link to any files written to `notes/`, `outputs/`, `papers/`, or other dirs

If any external claims matter, include direct source URLs.

---

## Output

Save to `notes/session-logs/` as Markdown with a date-oriented filename:
```
notes/session-logs/YYYY-MM-DD-<slug>.md
```

Format:
```markdown
# Session Log: [date] — [short topic]

## Done
- [concrete action 1]
- [concrete action 2]

## Key Findings
- [finding 1]
- [finding 2]

## Open Questions
- [question 1]
- [question 2]

## Next Steps
- [ ] [specific next action]
- [ ] [specific next action]

## Artifacts
- [file path or URL]

## Sources
- [URL if relevant]
```

---

## Note

This saves to `notes/session-logs/` in the current working directory. For Obsidian vault integration, use the `tldr` skill instead — it saves to the vault and updates memory.
