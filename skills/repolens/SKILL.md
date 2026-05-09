---
name: repolens
description: Wraps the Repolens CLI for repo intelligence tasks. Use when you need to orient on a codebase, analyze a large repo, audit for security or architecture issues, understand what a codebase does, or run focused code tasks without dumping the entire source into context. Triggers on "analyze this repo", "orient on codebase", "audit repo", "what does this codebase do", "code intelligence", "understand this codebase", "repo analysis", "refactor prep", "codebase audit".
---

# Repolens — Repo Intelligence

## Overview

Repolens v2 ingests git repos, scores and classifies every file by importance, builds token-budgeted context bundles, and runs Claude tasks against those bundles. It replaces the pattern of dumping entire codebases into context. Use it any time a task requires understanding a large codebase — analysis, audit, refactor prep, Q&A.

Installed at: `~/dev/projects/repolens_v2_repo/`

## When to Use

- "Analyze this repo" / "what does this codebase do"
- "Audit this repo for security issues" / "architecture review"
- "Orient on this codebase before I make a change"
- "Refactor prep" for a specific file or subsystem
- Any task where the codebase is too large to paste into context directly
- Running a targeted AI task against a repo without reading every file yourself

## Setup

Source the environment before every session. Always do this first:

```bash
cd ~/dev/projects/repolens_v2_repo
source .venv/bin/activate
source .env
export REPOLENS_TIMEOUT=300
```

After setup, `repolens` is available from anywhere. Commands take a repo argument that is the name or path registered at ingest time.

## Full Pipeline

### 1. Ingest — register a repo (first time only)

```bash
repolens ingest <path>
```

Registers the repo path and scans all text files into the DB. Run once per repo. Subsequent commands use the repo name returned at ingest.

Check registered repos at any time:

```bash
repolens list
```

### 2. Classify — score every file

```bash
repolens classify <repo>
```

Scores and classifies all files by importance. Run after ingest and after significant file additions. No API calls — fast, local-only.

Check results:

```bash
repolens status <repo>
```

### 3. Summarize — generate cached AI summaries (one-time cost)

```bash
repolens summarize <repo> --scope all --yes
```

Calls Claude once per file. Results are cached by content hash. Re-running after unchanged files is free — only new or modified files incur cost.

Scopes:
- `--scope all` — files, directories, and repo-level summary
- `--scope file` — file-level only (fastest, lowest cost)
- `--scope repo` — repo-level summary only

Pass `--yes` for non-interactive (agent) use to skip the cost confirmation prompt.

Summarize is optional but improves run quality. When to run it:
- First orient on a repo you have not used before
- After significant new files land
- Skip it for quick one-off analysis runs where cost matters more than depth

### 4. Preview — check the context bundle before committing

```bash
repolens context <repo> --task analyze --budget 20000
```

Prints the file list and token count that would be sent to the model. Use before a run to verify the bundle is the right size and scope.

Task types for `--task`: `analyze`, `summarize`, `refactor-prep`

### 5. Run — execute an AI task against the context bundle

```bash
repolens run <repo> --task analyze --description "..." --model claude-sonnet-4-5
```

Options:
- `--task` — required: `analyze` or `refactor-prep`
- `--description` — the specific question or instruction for this run
- `--budget` — token budget (default 32000); lower to control cost
- `--model` — override the model for this run
- `--dry-run` — print cost estimate without calling the API

Inspect recent runs and their costs:

```bash
repolens runs <repo> --limit 5
```

### Re-scan After File Changes

When the repo has changed since last ingest:

```bash
repolens scan <repo>
repolens classify <repo>
```

Summarize will automatically skip unchanged files on next run (content-hash cache).

## Model and Budget Tradeoffs

| Use case | Model | Budget |
|---|---|---|
| Day-to-day analysis, Q&A, refactor prep | `claude-sonnet-4-5` | 20k-32k |
| Deep architectural audit, one-shot deep review | `claude-opus-4-7` | 32k-50k |
| Quick orient, fast file-count check | `claude-sonnet-4-5` | 10k-15k |

Default model is `claude-opus-4-7`. Always pass `--model claude-sonnet-4-5` for day-to-day runs to keep costs in check. Reserve Opus for single high-value deep-dives where quality matters more than cost.

Example Opus deep-audit:

```bash
repolens run <repo> \
  --task analyze \
  --model claude-opus-4-7 \
  --budget 40000 \
  --description "Full architectural audit. Identify coupling, abstraction leaks, security risks, and any patterns that will hurt as the codebase scales."
```

## Refactor Prep Pattern

Before touching a specific file or subsystem, use `refactor-prep` to get a focused bundle covering only what you need:

```bash
repolens run <repo> \
  --task refactor-prep \
  --model claude-sonnet-4-5 \
  --description "Preparing to refactor FileClassifier in src/classifier.py. Map its dependencies, callers, shared state, and any side effects I need to understand before changing it."
```

Repolens builds a context bundle scoped to the relevant subsystem rather than the full repo. Engineers should use this before every non-trivial change rather than reading the whole codebase manually.

## Typical First-Orient Workflow

```bash
# 1. Source environment
cd ~/dev/projects/repolens_v2_repo && source .venv/bin/activate && source .env && export REPOLENS_TIMEOUT=300

# 2. Register the repo
repolens ingest /path/to/target-repo

# 3. Score files
repolens classify target-repo

# 4. Cache summaries (skip for quick runs)
repolens summarize target-repo --scope all --yes

# 5. Preview context bundle
repolens context target-repo --task analyze --budget 20000

# 6. Run the orient
repolens run target-repo \
  --task analyze \
  --model claude-sonnet-4-5 \
  --description "Give me a high-level map of this codebase: main modules, data flow, key abstractions, and anything that looks non-standard or risky."
```

## Quick Reference

```bash
repolens list                        # all tracked repos
repolens status <repo>               # file count, classification breakdown, summary coverage
repolens runs <repo> --limit 5       # recent runs with cost breakdown
repolens context <repo> --task analyze --budget 20000   # preview bundle
repolens run <repo> --task analyze --dry-run --description "..."  # cost estimate only
```

## Notes

- `REPOLENS_TIMEOUT=300` must be set every session. Large repo runs will hang without it.
- Repos are tracked by name after ingest. Pass the name (not path) to all subsequent commands.
- `--yes` on `summarize` is required for non-interactive agent use.
- Summarize cache is keyed by content hash. Re-running on unchanged files costs nothing.
- If a run hangs, verify `REPOLENS_TIMEOUT` is set before debugging further.
