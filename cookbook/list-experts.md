# List Registered Domain Experts

## Context

Show the agent-expert-kit triads registered in `library.yaml` under the
top-level `experts:` key. These are persistent domain mental models
(expertise.yaml + question.md + self-improve.md) that
`agent-expert-kit` scaffolds and registers on disk.

Triggered by `/library list experts`.

## Steps

### 1. Sync the Library Repo

Pull the latest catalog before reading:

```bash
cd <LIBRARY_SKILL_DIR>
git pull
```

### 2. Read the `experts:` Section

- Read `library.yaml`.
- Parse the top-level `experts:` key.
- If the key is absent or the list is empty, print:

  ```
  No experts registered.
  ```

  and stop. This is a normal state, not an error.

### 3. Check On-Disk Presence

For each registered entry:

- Read the `path` field (absolute path to the triad directory).
- Check that `<path>/expertise.yaml` exists on disk.
- Mark as `present` or `missing (path not found)`.

Missing entries usually mean the triad was scaffolded on another device
or removed manually. Surface but do not auto-repair.

### 4. Display Results

Format the output as a single table:

```
## Experts

| Name                 | Domain                | Path                                          | Last Sync   | Status  |
|----------------------|-----------------------|-----------------------------------------------|-------------|---------|
| Claudeclaw Missions  | claudeclaw-missions   | ~/.pna/experts/claudeclaw-missions            | 2026-04-22  | present |
| Creator Stack        | creator-stack         | ~/.pna/experts/creator-stack                  | -           | missing |
```

Rules:

- Show `last_sync` when present; otherwise `-`.
- Abbreviate the home directory (`~/`) in the path column for readability.
- Sort alphabetically by `domain`.

### 5. Summary

At the bottom, show:

- Total experts registered.
- Total present on disk.
- Total missing (path not found).

If any are missing, suggest the operator either rescaffold via
`agent-expert-kit` or remove the stale entry by hand (registrar does
not yet support removal).
