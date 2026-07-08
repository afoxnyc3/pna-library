---
name: wrap
description: >
  End-of-session summary and publish. Runs agent-session-summary to save a local handoff file,
  then publishes the session to pna-sessions.vercel.app and optionally notifies via Telegram.
  Invoke with /wrap at the end of any session.
version: 1.1.0
source: ~/.claude/commands/wrap.md
tags: [session, summary, publish, handoff]
requires: [skill:agent-session-summary]
---

# Wrap

End-of-session routine. Saves a local summary and publishes it to the P&A sessions archive.

---

## Step 1 — Save local session summary

Run the agent-session-summary skill:

1. Identify which agent you are: clarke, architect, engineer, pipeline, strategy, or main.
2. Fill in the template at `~/.claude/skills/agent-session-summary/template.md` with session content.
3. Save to:
   ```
   ~/dev/projects/rnd/deepagents/sessions/YYYY-MM-DD-<agent-id>-summary.md
   ```
4. Confirm the file path.

---

## Step 2 — Publish to pna-sessions

1. Confirm the local summary file path from Step 1.

2. Determine the agent ID:
   ```bash
   echo $CLAUDECLAW_AGENT_ID
   ```
   If empty, use `main`.

3. Build the session title:
   - Format: `<agent-id> session — YYYY-MM-DD`
   - Example: `principal_architect session — 2026-04-19`

4. Run the publish script:
   ```bash
   bash ~/dev/projects/pna-sessions/scripts/publish_session.sh \
     --title "<session title>" \
     --agent "<agent-id>" \
     --body-md "<path to local summary .md file>" \
     --type session \
     --tags "<agent-id>,$(date +%Y-%m-%d)"
   ```

5. Capture the URL from stdout — it is the last line, formatted as:
   ```
   URL: https://pna-sessions.vercel.app/sessions/<slug>
   ```

6. If `CLAUDECLAW_AGENT_ID` is set (non-empty), send a Telegram notification:
   ```bash
   ~/dev/claudeclaw/scripts/notify.sh "Session archived: <URL>"
   ```

7. Report the final URL to the user.
