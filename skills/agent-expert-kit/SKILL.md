---
name: agent-expert-kit
description: Scaffold the Disler domain triad (expertise.yaml + question.md + self-improve.md) for persistent agent memory. Use when seeding a new expertise domain from source code, adding durable domain knowledge for an agent, or after /agent-expert-kit. Triggers on "scaffold expertise", "create domain expert", "seed expertise for <domain>", or explicit domain= scope= arguments.
argument-hint: [domain=<slug> scope=<glob> description="<optional one-liner>"]
allowed-tools: Bash, Read, Write, Glob, Edit, TodoWrite
---

# agent-expert-kit

Scaffolds a three-file Disler domain triad at `~/.pna/experts/<domain>/`:

| File | Role |
|---|---|
| `expertise.yaml` | Machine-readable mental model. Seeded from real code. Line-capped. |
| `question.md` | Read-only Q&A slash command that reads + validates expertise first. |
| `self-improve.md` | 7-step workflow to re-sync expertise against current codebase. |

Agents read the triad at session start for instant domain context. Symlink into any agent's skill path as needed.

---

## Variables

```
DOMAIN          the domain slug, e.g. claudeclaw-missions
SCOPE_GLOB      glob for source files to seed from, e.g. src/missions/**
DESCRIPTION     one-line domain description (optional; derived from scope if absent)
TARGET_BASE     ~/.pna/experts
TARGET_DIR      ~/.pna/experts/$DOMAIN
MAX_LINES       1000
TEMPLATES_DIR   <directory of this SKILL.md>/templates
```

---

## Workflow

### Step 1 — Parse and validate

Extract `DOMAIN` and `SCOPE_GLOB` from the invocation arguments. Both are required.

If `DOMAIN` is missing: fail with `"agent-expert-kit: domain= is required. Example: domain=claudeclaw-missions"`

If `SCOPE_GLOB` is missing: fail with `"agent-expert-kit: scope= is required. Example: scope=src/missions/**"`

Validate that `DOMAIN` is a valid slug: lowercase letters, numbers, hyphens only.

### Step 2 — Check for existing triad

```bash
ls ~/.pna/experts/$DOMAIN/ 2>/dev/null
```

If `expertise.yaml` already exists, ask the user: `"Triad exists at ~/.pna/experts/$DOMAIN/. Overwrite? (y/n)"`

On confirm: save a timestamped backup:
```bash
cp ~/.pna/experts/$DOMAIN/expertise.yaml \
   ~/.pna/experts/$DOMAIN/expertise.yaml.bak.$(date +%s)
```

On decline: exit cleanly.

### Step 3 — Collect scope files

Use the Glob tool with `SCOPE_GLOB` to find matching files. Collect all paths.

If zero files match:
```
agent-expert-kit: no files matched scope=$SCOPE_GLOB
Check the glob pattern and working directory.
```

If more than 20 files match, read the most structurally important 20 (prefer non-test, non-generated, non-minified files). Note the total count.

List the files being seeded:
```
Seeding from N files:
  src/foo.ts
  src/bar.ts
  ...
```

### Step 4 — Seed expertise.yaml

Read the template at `$TEMPLATES_DIR/expertise.yaml.tmpl`.

Read all collected scope files using the Read tool.

Apply the seeder prompt below to produce the expertise.yaml body. Perform plain text substitution:

- `$DOMAIN` → the domain slug
- `$DESCRIPTION` → provided description or one derived from the scope files
- `$SCOPE_FILES` → comma-separated list of seeded file paths
- `$GENERATED_DATE` → today's date (ISO 8601, e.g. 2026-04-21)

**Seeder prompt (T1.5):**

```
You are seeding a domain expertise YAML for an agent memory system.

Domain: $DOMAIN
Description: $DESCRIPTION
Source files seeded from: $SCOPE_FILES
Generated: $GENERATED_DATE

Your job: produce a valid YAML document that becomes a persistent mental model
for this domain. An agent will read it at session start before answering questions.

Rules — follow exactly:

1. GROUND ONLY IN THE SOURCE FILES. Do not fabricate architecture, patterns, or
   behaviours not present in the provided files. If you are uncertain, omit.

2. CITE EVERY NON-TRIVIAL CLAIM. Every function, interface, table, schema item,
   or pattern you document must include a source citation in one of these forms:
     - Inline: "(file: src/foo.ts, line: 42)"
     - Under a "source:" key: "source: src/foo.ts"
   Claims without a file citation will fail the post-seed validation pass.

3. STRUCTURE. Use these top-level YAML keys in order:
     overview:           # domain purpose, tech stack, key entry points
     core_implementation: # one entry per key file: purpose, patterns, key_functions
     $CONDITIONAL_SECTION: # pick the ONE most relevant from the list below

   Conditional section options (pick one based on what dominates the scope):
     key_operations    — for systems whose primary surface is function calls
     schema_structure  — for systems whose primary surface is data models/tables
     api_surface       — for HTTP/RPC APIs
     event_flow        — for event-driven or queue-based systems
     command_surface   — for CLI tools

4. CONCISION. Target 300-600 lines. Never exceed MAX_LINES lines. Every line must
   earn its place. Specific beats generic. Omit boilerplate.

5. OUTPUT. Raw YAML only. No markdown fences. No preamble. No commentary after.
```

Write the produced YAML to a temp location: `~/.pna/experts/$DOMAIN/_expertise_draft.yaml`

### Step 5 — Compile-check and trim loop (T1.6)

Run the following Python snippet. If it exits non-zero, follow the recovery instructions.

```bash
python3 << 'PYEOF'
import yaml, sys, os

draft = os.path.expanduser("~/.pna/experts/$DOMAIN/_expertise_draft.yaml")
max_lines = $MAX_LINES
max_attempts = int(os.environ.get("EXPERT_MAX_ATTEMPTS", "3"))

with open(draft) as f:
    text = f.read()

# Compile check
try:
    yaml.safe_load(text)
except yaml.YAMLError as e:
    print(f"YAML_ERROR: {e}", file=sys.stderr)
    sys.exit(2)

# Line cap check
line_count = text.count("\n")
print(f"Lines: {line_count}/{max_lines}")

if line_count > max_lines:
    print(f"TRIM_NEEDED: {line_count} lines exceeds cap of {max_lines}", file=sys.stderr)
    sys.exit(3)

print("PASS")
sys.exit(0)
PYEOF
```

Exit code handling (loop up to 3 total attempts across the seeding + validation cycle):

- **Exit 0 (PASS)**: proceed to Step 6.
- **Exit 2 (YAML_ERROR)**: re-run the seeder prompt from Step 4, appending:
  `"The previous output had a YAML syntax error: <error from stderr>. Fix it and output raw YAML only."`
- **Exit 3 (TRIM_NEEDED)**: re-run the seeder prompt from Step 4, appending:
  `"The previous output was <N> lines, exceeding the cap of $MAX_LINES. Trim to under $MAX_LINES lines. Remove least-important claims first. Keep all file citations for key functions. Output raw YAML only."`
- **3rd failure**: report the failure verbatim and stop. Do not write partial files.

On success, move the draft to its final location:
```bash
mkdir -p ~/.pna/experts/$DOMAIN
mv ~/.pna/experts/$DOMAIN/_expertise_draft.yaml \
   ~/.pna/experts/$DOMAIN/expertise.yaml
```

### Step 6 — Write question.md and self-improve.md

Read `$TEMPLATES_DIR/question.md.tmpl`. Substitute:
- `$DOMAIN` → the domain slug
- `$EXPERTISE_PATH` → `~/.pna/experts/$DOMAIN/expertise.yaml`

Write to `~/.pna/experts/$DOMAIN/question.md`.

Read `$TEMPLATES_DIR/self-improve.md.tmpl`. Substitute:
- `$DOMAIN` → the domain slug
- `$EXPERTISE_FILE` → `~/.pna/experts/$DOMAIN/expertise.yaml`
- `$SCOPE_GLOB` → the original scope glob
- `$MAX_LINES` → `1000`

Write to `~/.pna/experts/$DOMAIN/self-improve.md`.

### Step 7 — Final validation

```bash
python3 -c "
import yaml, sys
p = '$HOME/.pna/experts/$DOMAIN/expertise.yaml'
try:
    yaml.safe_load(open(p))
    n = open(p).read().count('\n')
    print(f'expertise.yaml: valid YAML, {n} lines')
except Exception as e:
    print(f'FAILED: {e}'); sys.exit(1)
"
ls -la ~/.pna/experts/$DOMAIN/
```

### Step 8 — Report

```
agent-expert-kit: done

Domain:    $DOMAIN
Location:  ~/.pna/experts/$DOMAIN/
Files:
  expertise.yaml    (<N> lines, YAML valid)
  question.md       (read-only Q&A slash command)
  self-improve.md   (7-step rewrite + validation workflow)

Seeded from: <N> source files
  <list>

Next steps:
  Ask domain questions:    run question.md "<your question>"
  Keep expertise current:  run self-improve.md after code changes
  Wire to an agent:        ln -s ~/.pna/experts/$DOMAIN \
                             ~/.claudeclaw/agents/<id>/experts/$DOMAIN
```

---

## Notes

- Re-running against an existing triad triggers an overwrite prompt (Step 2). A `.bak` is saved automatically.
- `MAX_LINES=1000` is the default. Override per-domain by editing expertise.yaml's first comment line.
- Phase 2 (registrar + slug collision check) is not included in v1. Triad registration via `library add` is manual.
- Self-improve (Phase 3) lives in a separate `self-improve-expertise` skill. The generated `self-improve.md` is the per-domain instance of that workflow.
