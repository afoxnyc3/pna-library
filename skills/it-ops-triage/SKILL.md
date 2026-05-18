---
name: it-ops-triage
description: >
  Alert classification and routing loop for IT operations. Parses incoming alerts,
  classifies by domain and priority, routes to the correct specialist plugin, and
  generates a standardized triage record.
  WHEN: an alert, incident, or event arrives from any monitoring tool (GuardDuty, Defender,
  Meraki, NinjaOne, Mimecast, or manual report).
  WHEN: asked to triage, classify, or route an IT incident or security alert.
  WHEN: running an automated alert ingestion loop.
  WHEN: a new ticket needs domain classification before assignment.
version: 1.0.0
consumers: [it-ops-lead, azure-security, aws-security, meraki-network, mimecast-security, ninjaone-rmm]
tags: [it-ops, triage, routing, incident-response, chelsea-piers]
---

# IT Ops Triage

## Purpose

Every IT environment generates more alerts than humans can manually route. This skill
standardizes alert intake across all 6 Chelsea Piers monitoring surfaces — GuardDuty,
Microsoft Defender, Meraki, NinjaOne, Mimecast, and manual reports — and converts raw
alert payloads into classified, routed, and logged triage records.

One skill, one format, every agent.

---

## Step 1 — Parse the Alert

Extract the following fields from the alert payload (raw JSON, log line, or free-text
description). If a field is absent, mark it `unknown` — never infer from adjacent fields.

```
source        : GuardDuty | Defender | Meraki | NinjaOne | Mimecast | manual
alert_type    : (raw alert name or category from the source tool)
severity      : Critical | High | Medium | Low | Informational
affected      : (resource name, user, device, IP, or system)
timestamp     : ISO 8601
description   : (raw text, first 500 chars)
```

**For GuardDuty JSON payloads** — pull `type`, `severity` (0-10 scale), `resource`, and
`description` from the top-level fields.

**For Defender JSON payloads** — pull `title`, `severity`, `affectedAssets`, and
`detectionSource`.

**For Meraki alerts** — pull `alertType`, `deviceName`, `networkName`, and
`occurredAt`.

**For NinjaOne events** — pull `eventType`, `deviceId`, `severity`, and `message`.

**For Mimecast logs** — pull `action`, `senderAddress`, `recipientAddress`, and
`definition` (policy that triggered).

**For free-text / manual reports** — extract the closest equivalent fields. Flag
ambiguous fields for human review.

---

## Step 2 — Classify Priority

Apply the priority matrix. Use the **highest** applicable priority level.

| Priority | Condition | Response SLA |
|---|---|---|
| P0 | Admin/root account compromise, active exfiltration, complete WAN down, ransomware indicators | Immediate — phone CISO + IT Manager |
| P1 | Critical/High severity security alert, service down for multiple users, confirmed phishing campaign | 15 min response, 1 hour containment |
| P2 | Single system failure, Medium severity finding, patch non-compliance >30%, user account anomaly | 2 hour response, 4 hour resolution |
| P3 | Low/Informational finding, single-user impact, informational policy trigger | 4 hour response, 24 hour resolution |

**Severity-to-priority mappings by source:**

| Source | Raw Severity | Priority |
|---|---|---|
| GuardDuty | 7.0-10.0 (High/Critical) | P1 |
| GuardDuty | 4.0-6.9 (Medium) | P2 |
| GuardDuty | 0-3.9 (Low) | P3 |
| Defender | Critical | P1 |
| Defender | High | P1 or P2 depending on asset |
| Defender | Medium | P2 |
| Defender | Low/Informational | P3 |
| Meraki | uplink_down or MX_down | P0 or P1 depending on scope |
| Meraki | device_offline | P2 |
| Meraki | performance_degradation | P2 |
| NinjaOne | CRITICAL patch missing | P2 |
| NinjaOne | device_offline | P2 |
| Mimecast | impersonation_protect | P1 |
| Mimecast | url_protect block | P2 |
| Mimecast | attachment_protect | P2 |

**Override rule**: any alert touching admin credentials, root accounts, or indicating
lateral movement → escalate to P0 regardless of source severity score.

---

## Step 3 — Classify Domain and Route

Map the alert to the correct specialist plugin using the routing matrix.

| Alert Domain | Indicators | Route to Plugin |
|---|---|---|
| AWS IAM / GuardDuty / CloudTrail | GuardDuty finding, IAM event, S3/EC2 alert, root activity | `aws-security` |
| Azure AD / Defender / Entra | Defender alert, impossible travel, CA policy, PIM event | `azure-security` |
| Meraki / Network | Uplink down, switch offline, AP offline, firewall rule trigger | `meraki-network` |
| NinjaOne / Endpoint | Device offline, patch missing, disk/CPU/RAM alert | `ninjaone-rmm` |
| Mimecast / Email Security | URL blocked, phishing detected, impersonation, DLP trigger | `mimecast-security` |
| Manual / Cross-system | Spans 2+ domains, source unclear, user-reported anomaly | `it-ops-lead` (route manually) |

**Cross-system escalation**: if an alert touches 2+ domains (e.g., compromised user
accessing both AWS and Azure), route to `it-ops-lead` with all domain context. Do not
split-route without it-ops-lead coordination.

---

## Step 4 — Generate the Triage Record

Output a standardized triage record for every processed alert.

```
TRIAGE RECORD
═════════════════════════════════════════════════════════
Triage ID    : TRIAGE-YYYYMMDD-NNNN   (auto-increment per session)
Timestamp    : <ISO 8601 when triage was run>
Source       : <GuardDuty | Defender | Meraki | NinjaOne | Mimecast | manual>
Alert Type   : <raw alert type>
Affected     : <resource / user / device>
Priority     : <P0 | P1 | P2 | P3>
Domain       : <aws | azure | network | endpoint | email | cross-system>
Route to     : <plugin name>
SLA Target   : <response / resolution window>
Action Taken : <routed | escalated | held-for-review | auto-closed>
Jira Ticket  : <ticket key or PENDING>
Notes        : <any ambiguities, override reasons, or escalation context>
═════════════════════════════════════════════════════════
```

If running batch triage (multiple alerts), output one record per alert, then a summary
table:

```
BATCH TRIAGE SUMMARY
--------------------
Total alerts   : N
P0             : N
P1             : N
P2             : N
P3             : N
Routed         : N (breakdown by plugin)
Escalated      : N
Held           : N
```

---

## Step 5 — Escalation Triggers

Execute these automatically — do not wait for confirmation:

| Trigger | Action |
|---|---|
| Priority = P0 | Immediately notify IT Manager + CISO via Teams `#it-security` + phone. Do not proceed with routing until escalation is acknowledged. |
| GuardDuty finding with `root` in resource | Escalate P0 regardless of severity score |
| Defender alert with `AccountCompromised` or `LateralMovement` in type | Escalate P0 |
| Meraki: all uplinks down at any venue | Escalate P0 to Network Engineer + IT Manager |
| 5+ P1 alerts in a single triage batch | Flag as potential incident wave — notify IT Manager before routing individual alerts |

For P1 escalation, notify `#it-security` on Teams and create a Jira ticket in the
SEC project before routing to the specialist plugin.

---

## Step 6 — Jira Ticket (P0/P1 only)

For P0 and P1 alerts, create a Jira ticket before routing:

```
Project      : SEC (security events) or ITINFRA (infrastructure)
Issue Type   : Incident
Summary      : [P0|P1][SOURCE] Brief description of alert
Priority     : Critical or High
Labels       : [source-tool, domain, priority-level]
Description  : Full triage record pasted verbatim
Assignee     : Per routing matrix:
               - aws: Security Analyst
               - azure: Security Analyst / Miguel
               - network: Stuart
               - endpoint: Brittney (user-facing) / Miguel (admin)
               - email: Security Analyst
```

Return the Jira ticket key in the triage record.

---

## Automated Loop Mode

When used in an automated alert ingestion pipeline, process alerts in batches of up to
50. For each batch:

1. Parse all alerts (Step 1)
2. Classify all priorities (Step 2)
3. Sort by priority descending (P0 first)
4. Process P0/P1 alerts immediately with escalation
5. Route P2/P3 alerts to specialist plugins
6. Output batch summary

If any P0 alert is encountered mid-batch, halt the loop and escalate before continuing.

---

## Report

After completing a triage run, output:

- Number of alerts processed
- Priority distribution (P0/P1/P2/P3 counts)
- Routing breakdown by plugin
- Any escalations triggered (with Jira ticket keys)
- Any alerts held for human review with reason
- Triage duration (wall clock)
