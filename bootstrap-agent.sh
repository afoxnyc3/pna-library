#!/usr/bin/env bash
# bootstrap-agent.sh
#
# One-shot library bootstrap for a headless agent (research_a, research_b,
# principal_sandbox, or any future worker). Safe to run on every startup.
#
# What it does:
#   1. Ensures ~/.claude/skills/library/ exists and is current (git pull).
#      Clones afoxnyc3/pna-library if the directory is missing.
#   2. Heals the SKILL.md typechange bug if it recurs.
#   3. Optionally pulls a specified skill set into a target directory.
#
# Usage:
#   bootstrap-agent.sh                     # just sync the catalog
#   bootstrap-agent.sh --roster /path/to/roster.yaml
#   bootstrap-agent.sh --skills deep-research,peer-review --target ~/agent/.claude/skills
#
# Exit codes:
#   0 success, 1 misuse, 2 network/git failure, 3 missing dependency

set -euo pipefail

LIBRARY_REPO_URL="${LIBRARY_REPO_URL:-https://github.com/afoxnyc3/pna-library.git}"
LIBRARY_DIR="${LIBRARY_DIR:-$HOME/.claude/skills/library}"
TARGET_DIR=""
SKILLS=""
ROSTER=""
QUIET="${QUIET:-0}"

log() { [ "$QUIET" = "1" ] || printf '[library-bootstrap] %s\n' "$*" >&2; }
die() { printf '[library-bootstrap] ERROR: %s\n' "$*" >&2; exit "${2:-1}"; }

# --- parse args ---
while [ $# -gt 0 ]; do
  case "$1" in
    --skills) SKILLS="$2"; shift 2 ;;
    --roster) ROSTER="$2"; shift 2 ;;
    --target) TARGET_DIR="$2"; shift 2 ;;
    --quiet)  QUIET=1; shift ;;
    -h|--help)
      sed -n '2,20p' "$0"; exit 0 ;;
    *) die "unknown flag: $1" 1 ;;
  esac
done

# --- preflight ---
command -v git >/dev/null 2>&1 || die "git not installed" 3
command -v yq  >/dev/null 2>&1 || YQ_MISSING=1  # yq only required if --roster used

# --- step 1: ensure library is present ---
if [ ! -d "$LIBRARY_DIR/.git" ]; then
  log "library missing — cloning from $LIBRARY_REPO_URL"
  mkdir -p "$(dirname "$LIBRARY_DIR")"
  git clone --depth 1 "$LIBRARY_REPO_URL" "$LIBRARY_DIR" >/dev/null 2>&1 || die "clone failed" 2
else
  log "library present — fetching latest"
  (cd "$LIBRARY_DIR" && git pull --ff-only --quiet) || log "pull failed (continuing with local copy)"
fi

# --- step 2: heal the SKILL.md typechange bug if it recurs ---
if [ ! -f "$LIBRARY_DIR/SKILL.md" ] || [ ! -s "$LIBRARY_DIR/SKILL.md" ]; then
  log "SKILL.md missing or empty — restoring from git"
  (cd "$LIBRARY_DIR" && git restore SKILL.md) || die "git restore SKILL.md failed" 2
fi

# --- step 3: resolve which skills to install ---
if [ -n "$ROSTER" ]; then
  [ -f "$ROSTER" ] || die "roster file not found: $ROSTER" 1
  [ -z "${YQ_MISSING:-}" ] || die "yq is required to parse --roster (brew install yq)" 3
  SKILLS=$(yq -r '.skills[]' "$ROSTER" 2>/dev/null | tr '\n' ',' | sed 's/,$//')
  log "resolved ${SKILLS//,/ , } from roster"
fi

# --- step 4: install skills if requested ---
if [ -n "$SKILLS" ]; then
  [ -n "$TARGET_DIR" ] || die "--target required when --skills or --roster is used" 1
  mkdir -p "$TARGET_DIR"

  IFS=',' read -ra SKILL_LIST <<< "$SKILLS"
  INSTALLED=0
  FAILED=0
  for skill in "${SKILL_LIST[@]}"; do
    skill=$(echo "$skill" | xargs)  # trim
    [ -z "$skill" ] && continue

    # Look up the source path from library.yaml
    SRC=$(awk -v name="$skill" '
      $0 ~ "name: " name "$" { found=1; next }
      found && /source:/ { sub(/^ *source: */, ""); print; exit }
    ' "$LIBRARY_DIR/library.yaml")

    if [ -z "$SRC" ]; then
      log "skill not in catalog: $skill"
      FAILED=$((FAILED + 1))
      continue
    fi

    # Expand ~ in source path
    SRC="${SRC/#\~/$HOME}"
    SRC_DIR=$(dirname "$SRC")

    if [ ! -d "$SRC_DIR" ]; then
      log "source directory missing for $skill: $SRC_DIR"
      FAILED=$((FAILED + 1))
      continue
    fi

    # Symlink preferred (keeps skills in sync); fallback to copy if source is a GitHub URL
    if [ -L "$TARGET_DIR/$skill" ] || [ -d "$TARGET_DIR/$skill" ]; then
      rm -rf "$TARGET_DIR/$skill"
    fi
    ln -s "$SRC_DIR" "$TARGET_DIR/$skill"
    log "linked $skill -> $SRC_DIR"
    INSTALLED=$((INSTALLED + 1))
  done

  log "installed: $INSTALLED | failed: $FAILED | target: $TARGET_DIR"
  [ "$FAILED" -eq 0 ] || exit 1
fi

log "done"
exit 0
