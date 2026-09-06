#!/usr/bin/env python3
"""reconcile.py — does the catalogue describe the system, or a different system?

    scripts/reconcile.py            # report
    scripts/reconcile.py --strict   # exit 1 if anything is uncatalogued or broken

WHY THIS EXISTS. On 2026-09-06 a hand audit found 16 skills installed and
routable in ~/.claude/skills/ that this catalogue had never heard of, including
fleet-ops, wrangler and the whole Cloudflare and Sandbox families. `/library`
could not see a sixth of the working set, which makes the catalogue useless for
the one question it exists to answer: what can this fleet do.

Nothing detected that, because nothing was looking.

A SECOND finding from the same audit is the reason this script prints the
resolved catalogue path in its header. There are two checkouts of the
pna-library repo on this machine:

    ~/dev/projects/pna-library   main, current           <- CANONICAL
    ~/dev/pna-library            a stale April feature
                                 branch, 2 commits ahead

The first pass of that audit read the stale one and produced entirely wrong
numbers: it reported 5 skills as deleted-in-violation-of-policy when they were
archived exactly as policy requires, and 60 uncatalogued when the real figure
was 16. Reading the wrong file is not a rare failure mode, so this script says
which file it read, every time, rather than leaving that to be assumed.

WHAT COUNTS AS A PROBLEM, and what deliberately does not:

  UNCATALOGUED  installed and loadable, absent from the catalogue. A real gap:
                the fleet can invoke something the library cannot describe.

  BROKEN        a source path that resolves nowhere AND has no retirement note.
                A retired entry keeping its original path is CORRECT and is the
                documented convention, so a `# retired` comment suppresses this.
                Flagging those was the other error in the first audit.

  DEAD          catalogued, not installed. NOT reported as a failure. Retired
                skills are deactivated rather than deleted on purpose, and
                upstream sources that were never symlinked are a choice, not a
                defect. Counted and listed under --verbose, never exit 1.
"""
import argparse
import os
import glob
import re
import sys

CANONICAL = "~/dev/projects/pna-library/library.yaml"
INSTALL_DIR = "~/.claude/skills"


def load(path):
    """Parse without importing yaml: this must run anywhere, including a bare
    launchd env where site-packages is not what you think it is."""
    entries, kind, name, src, retired = [], None, None, None, False
    for line in open(path, encoding="utf-8"):
        m = re.match(r"^  (skills|agents|prompts):\s*$", line)
        if m:
            kind = m.group(1)
            continue
        m = re.match(r"^\s*-\s*name:\s*(\S+)", line)
        if m:
            if name:
                entries.append((name, kind, src, retired))
            name, src, retired = m.group(1), None, False
            continue
        m = re.match(r"^\s*source:\s*(\S+)", line)
        if m and name and src is None:
            src = m.group(1)
        if name and re.search(r"#\s*retired", line, re.I):
            retired = True
    if name:
        entries.append((name, kind, src, retired))
    return entries


def installed(root):
    out = set()
    for p in glob.glob(os.path.join(root, "*")):
        b = os.path.basename(p)
        if b.startswith("."):
            continue
        if any(os.path.isfile(os.path.join(p, f)) for f in ("SKILL.md", "skill.md")):
            out.add(b)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--catalogue", default=CANONICAL)
    ap.add_argument("--install-dir", default=INSTALL_DIR)
    ap.add_argument("--strict", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    a = ap.parse_args()

    cat_path = os.path.expanduser(a.catalogue)
    inst_dir = os.path.expanduser(a.install_dir)
    if not os.path.exists(cat_path):
        print(f"reconcile: no catalogue at {cat_path}", file=sys.stderr)
        sys.exit(2)

    entries = load(cat_path)
    cat = {n: (k, s, r) for n, k, s, r in entries}
    inst = installed(inst_dir)

    # Read paths out loud. See the module docstring for why.
    print(f"catalogue:   {cat_path}")
    print(f"install dir: {inst_dir}")
    print(f"catalogued {len(cat)}   installed {len(inst)}   both {len(set(cat) & inst)}")

    uncatalogued = sorted(inst - set(cat))
    broken = sorted(
        (n, s) for n, (k, s, r) in cat.items()
        if s and not s.startswith("http") and not r
        and not os.path.exists(os.path.expanduser(s))
    )
    dead = sorted(n for n, (k, s, r) in cat.items() if k == "skills" and n not in inst)

    print()
    if uncatalogued:
        print(f"UNCATALOGUED ({len(uncatalogued)}) — installed, invisible to /library:")
        for n in uncatalogued:
            print(f"  {n}")
    if broken:
        print(f"BROKEN ({len(broken)}) — source resolves nowhere and no retirement note:")
        for n, s in broken:
            print(f"  {n}: {s}")
    if not uncatalogued and not broken:
        print("clean: every installed skill is catalogued, every source resolves or is retired")

    print(f"\nnot installed: {len(dead)} (retired or upstream-only, not a failure)")
    if a.verbose and dead:
        for n in dead:
            print(f"  {n}")

    if a.strict and (uncatalogued or broken):
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
