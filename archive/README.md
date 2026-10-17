# Archive

Policy is **deactivate, not delete**. A retired skill is never removed from the
machine; it is moved out of the active skills tree and its `library.yaml` row is
annotated with a retirement date, a reason, and a restore command.

## Two archives, on purpose

These are different things. Both should exist.

| | what it holds | location |
|---|---|---|
| **Runtime archive** | deactivated skills still on the machine, restorable in place | `~/.claude/skills/.archive/` |
| **Repo archive** (this dir) | the git-preserved record, survives machine loss | `pna-library/archive/` |

The runtime archive is a single root. There is exactly one, at
`~/.claude/skills/.archive/`, with one subdirectory per retirement **event**
(`2026-04/`, `2026-07-08/`, `2026-07-17/`) — dated to the groom, not the month,
because two separate grooms both landed in July 2026.

`2026-04/` stays a bare month by exception: it predates the convention and its
exact groom date is not recorded anywhere, so dating it would mean inventing a
day. New cohorts use a full `YYYY-MM-DD`.

See `~/.claude/skills/.archive/README.md` for the runtime-side procedure.

## Retiring a skill

1. `mv ~/.claude/skills/<name> ~/.claude/skills/.archive/<YYYY-MM-DD>/`
2. Annotate the `library.yaml` row:
   `# retired <YYYY-MM-DD> (<reason>): <rationale>. Restore with /library use <name>`
3. Copy the SKILL.md here under `archive/<YYYY-MM-DD>/` so the record survives
   the machine.
4. Run `python3 scripts/reconcile.py` — it must report clean.

Do not create a new archive root. That is what broke.

## History

Until 2026-09-07 the runtime archive was split across two roots:
`~/.claude/skills/.archive/` and `~/.claude/skills-archive/`. A retirement
landed in whichever one the author knew about, and a restore looked in only one.

Issue #143 Finding 1 reported five catalogued skills as deleted against policy
— "Gone. no copy elsewhere on disk". All five were on disk the entire time, in
archive directories the audit did not search:

| skill | actual location |
|---|---|
| `systematic-debugging` | `.archive/2026-07-08/` |
| `vertex-ai-api-dev` | `.archive/2026-07-08/` |
| `gemini-api-dev` | `.archive/2026-04/` |
| `gemini-interactions-api` | `.archive/2026-07-17/` (was `skills-archive/`) |
| `gemini-live-api-dev` | `.archive/2026-07-17/` (was `skills-archive/`) |

Consolidated onto one root, content verified byte-identical across the move
(36 files before, 36 after, matching checksum manifest). `~/.claude/skills-archive/`
retains a `MOVED.md` signpost rather than being deleted.

## Known gap

This repo archive holds 1 of the 14 skills present in the runtime archive.
Step 3 above was not being followed. Backfilling is not done and is tracked
separately — it is a content-migration task, not a policy fix.
