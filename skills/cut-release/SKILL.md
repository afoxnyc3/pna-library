---
name: cut-release
description: >-
  Cut a dated/named release snapshot of a git repo into a bare "remote" repo
  under ~/dev/github-dated, so deployments can be cloned from a frozen,
  self-identifying version. Use this whenever the user wants to snapshot, freeze,
  tag, or version a repo for later deployment — trigger phrases include "cut a
  release", "snapshot claudeclaw", "new dated release", "freeze this version",
  "make a release copy", or "tag today's build". Prefer this skill over ad-hoc
  git commands whenever the goal is a reusable, labeled deployment source.
---

# Cut Release

Snapshot a working git repo into a **bare release remote** under
`~/dev/github-dated/`. Each release is frozen and self-identifying, so any copy
cloned from it can always report which version it came from.

## The convention (why it works this way)

The whole point is that a deployment should never be a mystery — you should be
able to look at any cloned copy and know exactly which release it is. Version
identity is therefore baked in three places, and they must stay in sync:

1. **Repo name** — `<project>-<label>.git` (e.g. `claudeclaw-os-july-1-26-release.git`)
2. **Annotated git tag** — `<label>` on the exact snapshot commit
3. **Self-reporting** — `git describe --tags` on any clone returns `<label>`

One bare repo per release. Don't push new work into an existing release repo —
that would silently change what "july-1-26-release" means, breaking the guarantee.
Cut a new dated repo instead.

**Labels always include the 2-digit year:** `month-day-YY-release`, e.g.
`july-1-26-release`, `aug-15-26-release`. Without the year, `july-1-release`
collides the moment July comes around again next year. If the user gives a label
without a year, add it (derive the year from today's date) and confirm.

## How to cut a release

The mechanism lives in `~/dev/github-dated/cut-release.sh` (already tested). It
bare-clones the source, creates the annotated tag, strips any embedded token
from the upstream URL, and appends a row to the release log in
`~/dev/github-dated/README.md`.

Run it from the `github-dated` directory:

```bash
cd ~/dev/github-dated
./cut-release.sh <label> [source-repo] [git-ref]      # local-only
PUBLISH=1 ./cut-release.sh <label> [source-repo] [git-ref]   # + push to GitHub
```

- `<label>` — human release name **with the 2-digit year**, e.g.
  `aug-15-26-release` (this becomes the repo suffix AND the tag; keep it
  filesystem- and git-tag-safe: lowercase, hyphens)
- `[source-repo]` — working repo to snapshot (default: `~/dev/claudeclaw-os`)
- `[git-ref]` — commit/branch/tag to freeze (default: `HEAD` of the source)
- `PUBLISH=1` — also create a private GitHub repo under `principal-and-agent`
  and mirror-push to it. This is what makes a release pullable **from another
  laptop**. Needs the `gh` CLI, authenticated.

**Examples:**

Snapshot the current HEAD of the default repo (local only):
Input: "cut an aug 15 release"
Output: `cd ~/dev/github-dated && ./cut-release.sh aug-15-26-release`

Cut a release and publish it so both laptops can pull it:
Input: "cut today's release and push it to github so I can pull it on my other laptop"
Output: `cd ~/dev/github-dated && PUBLISH=1 ./cut-release.sh aug-15-26-release`

Freeze a specific tagged build of a different repo:
Input: "freeze v1.3.3 of claudeclaw as a hotfix release"
Output: `cd ~/dev/github-dated && ./cut-release.sh hotfix-26-release ~/dev/claudeclaw-os v1.3.3`

## After cutting

Confirm the label and report the deploy command back to the user so they can
clone a fresh copy off the new remote:

```bash
# same machine
git clone ~/dev/github-dated/<project>-<label>.git my-new-deploy

# another laptop (only if PUBLISH=1 was used)
git clone https://github.com/principal-and-agent/<project>-<label>.git my-new-deploy

cd my-new-deploy && git describe --tags   # -> <label>
```

Before deriving the label from a date, check today's actual date (the script
stamps the log with `date +%Y-%m-%d` itself, so the log date is always correct —
but a human label like "july-1-release" is your responsibility to get right).

## If something looks off

- **Label already exists** — the script refuses to overwrite an existing bare
  repo. Pick a new label; don't force it, since reusing a label destroys the
  version guarantee.
- **Source isn't a git repo** — the script checks for `.git` and errors early.
- **Verifying a release** — clone it to a temp dir and run `git describe --tags`;
  it should print the label. That's the same check the deploy step relies on.
