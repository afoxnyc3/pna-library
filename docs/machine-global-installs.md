# Machine-global installs

A ledger of state installed **outside** any repo to make a catalogued skill work.

These are side effects no PR can revert. A `git revert` undoes the catalogue row
but leaves the package installed. If it is not written down here, the next person
to debug this machine has no way to know it was done deliberately.

Record every entry with: what, why, the exact command, and how to undo it.

---

## `networkx` — homebrew python 3.14

**For:** the `deeptutor` skill. `scripts/graph_builder.py` hard-fails without it
at the guard in `load_graph()`; `scripts/graph_retriever.py` fails transitively
through `from graph_builder import load_graph`. Same error either way:

```
ERROR: networkx not installed. Run: pip install networkx
```

**Installed:** 2026-09-07, `networkx 3.6.1`

```bash
python3 -m pip install --break-system-packages networkx
```

**Why `--break-system-packages`:** `/opt/homebrew/bin/python3` (3.14.3) is
PEP-668 externally-managed, so a plain `pip install` refuses. A venv was not
viable without patching upstream: the deeptutor scripts carry bare
`#!/usr/bin/env python3` shebangs and the agent at `~/.claude/agents/deeptutor.md`
invokes them as `python3 <script>` with no wrapper. The skill's own documented
setup step is `pip install networkx`.

`networkx` is pure-python and not a Homebrew formula dependency, so it does not
shadow or conflict with brew-managed packages.

**Undo:**

```bash
python3 -m pip uninstall --break-system-packages networkx
```

Safe to remove if `deeptutor` is ever retired. Nothing else in the library
declares `requires: [python:networkx]` — check with:

```bash
grep -n "python:networkx" library.yaml
```
