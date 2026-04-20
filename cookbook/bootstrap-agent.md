# Cookbook: Bootstrap a headless agent with the library

For `research_a`, `research_b`, `principal_sandbox`, or any future worker that needs a consistent skill set across machines and fresh environments.

## When to use this

- A new agent is being provisioned for the first time.
- An agent runs in an ephemeral environment (E2B sandbox, CI container, remote VM) and needs its skill catalog reconstituted on every boot.
- You want a single source of truth for which skills an agent carries, versioned as a roster file.

## The script

`~/.claude/skills/library/bootstrap-agent.sh`

Pure bash, no dependencies beyond `git`. Optional `yq` only needed if using `--roster`.

## Three modes

### Mode 1: just sync the catalog (safest default)

```bash
~/.claude/skills/library/bootstrap-agent.sh
```

Ensures the library is cloned, up to date, and the SKILL.md typechange bug (if it recurs) is healed. Exits 0 on success. Idempotent.

### Mode 2: explicit skill list

```bash
~/.claude/skills/library/bootstrap-agent.sh \
    --skills deep-research,peer-review,source-comparison \
    --target ~/.claude/skills
```

Symlinks each skill's source directory into the target. Fast, keeps skills auto-updated with the source repo.

### Mode 3: roster file (recommended for long-lived agents)

Create a YAML roster at the agent's root:

```yaml
# ~/dev/projects/rnd/research-agent-sdk/skill_roster.yaml
skills:
  - deep-research
  - source-comparison
  - literature-review
  - novelty-check
  - peer-review
  - research-wiki
  - research-refine
  - alpha-research
  - eli5
  - paper-writing
  - feynman-bridge
```

Then bootstrap with:

```bash
~/.claude/skills/library/bootstrap-agent.sh \
    --roster ~/dev/projects/rnd/research-agent-sdk/skill_roster.yaml \
    --target ~/dev/projects/rnd/research-agent-sdk/.claude/skills
```

## Wiring into launchd / plists

Add to the `ProgramArguments` of an agent's plist so it runs before the main worker starts:

```xml
<key>ProgramArguments</key>
<array>
    <string>/bin/bash</string>
    <string>-c</string>
    <string>~/.claude/skills/library/bootstrap-agent.sh --roster ~/dev/projects/rnd/research-agent-sdk/skill_roster.yaml --target ~/dev/projects/rnd/research-agent-sdk/.claude/skills --quiet && exec /usr/local/bin/python3 ~/dev/projects/rnd/research-agent-sdk/daemon.py</string>
</array>
```

Or as a `RunAtLoad` pre-step invoked by the daemon itself on startup.

## For E2B / ephemeral sandboxes

Include this in your sandbox template `build_template.py` or startup hook:

```python
import subprocess
subprocess.run([
    "bash", "-c",
    "git clone --depth 1 https://github.com/afoxnyc3/pna-library.git /root/.claude/skills/library && "
    "/root/.claude/skills/library/bootstrap-agent.sh --roster /workspace/skill_roster.yaml --target /root/.claude/skills"
], check=True)
```

## Suggested rosters

### research_a / research_b (12 skills each)

```yaml
skills:
  - deep-research
  - source-comparison
  - literature-review
  - novelty-check
  - peer-review
  - research-wiki
  - research-refine
  - alpha-research
  - eli5
  - paper-writing
  - feynman-bridge
  - session-log
```

### principal_sandbox (10 skills)

```yaml
skills:
  - spec-driven-development
  - planning-and-task-breakdown
  - systematic-debugging
  - verification-before-completion
  - test-driven-development
  - webapp-testing
  - api-and-interface-design
  - documentation-and-adrs
  - git-workflow-and-versioning
  - claude-api
```

## Exit codes

| Code | Meaning                                    |
| ---- | ------------------------------------------ |
| 0    | Success (all skills installed, or no-op)   |
| 1    | Misuse (missing flags, bad roster)         |
| 2    | Network or git failure                     |
| 3    | Missing dependency (git, yq)               |

## Failure modes and recovery

- **Clone fails (exit 2)** — check network, `gh auth status`, and that the remote exists. Script will continue with local copy if one exists.
- **Skill not in catalog** — logged per-skill, does not abort other installs. Check spelling against `/library list`.
- **Source directory missing** — the referenced skill lives on a path that isn't present on this machine. For headless agents, this means the skill's source repo wasn't cloned first. Either clone it into the expected path, or update the catalog entry to a GitHub URL.
