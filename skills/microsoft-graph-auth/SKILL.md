---
name: microsoft-graph-auth
description: |
  Implements Microsoft Graph API authentication for Azure, M365, SharePoint, and Teams integrations.
  WHEN: building or debugging any Microsoft Graph API client (email, calendar, files, teams, identity)
  WHEN: connecting to email-triage-m365, sharepoint, teams, or azure-security plugins
  WHEN: asked to "authenticate with Microsoft", "get a Graph token", "set up MSAL", "connect to M365"
  WHEN: encountering 401 from Microsoft Graph, token expiry issues, or consent errors
  WHEN: choosing between delegated and application permissions for a Graph workflow
  WHEN: building multi-tenant or cross-tenant Microsoft integrations
  Covers: MSAL confidential client, app vs delegated permissions, token caching, multi-tenant, admin consent, scope selection, common Graph endpoints for IT ops workflows.
version: 1.0.0
consumers: [principal_engineer, email-triage-m365, sharepoint, teams, azure-security]
---

# Microsoft Graph Auth

## Purpose

Microsoft 365 is one auth layer across four Chelsea Piers plugins: email triage (Exchange/Outlook), SharePoint, Teams, and Azure Security (Entra ID, Defender). Each plugin makes different Graph API calls but they all share the same MSAL confidential client setup, token caching pattern, and admin consent flow.

This skill pins the correct implementation so the pattern is consistent across the fleet — no plugin re-invents it, no plugin gets it slightly wrong.

Two flows in scope:

- **Application permissions** (no signed-in user): daemon services, background agents, automated IT workflows. Requires admin consent. This is the default for Chelsea Piers IT ops.
- **Delegated permissions** (on behalf of a signed-in user): interactive flows, approvals, actions that should be attributed to a specific user. Device code flow for CLI contexts.

---

## Step 0 — Permission selection

Before writing code, decide which permission model applies. Choosing wrong requires a re-deployment and a second admin consent grant.

| Scenario | Model | Reason |
|---|---|---|
| Email triage (reading shared helpdesk mailbox) | Application | Daemon reads a shared mailbox — no user sign-in |
| SharePoint content search and retrieval | Application | Background indexing — no user sign-in |
| Teams notification to a channel | Application | Bot sends to channel — no user sign-in |
| Azure Security sign-in log queries | Application | Security monitoring — no user sign-in |
| Acting on behalf of a user (approvals, delegated send) | Delegated | Action attributed to the user, not the app |
| Any interactive consent or user-specific data | Delegated | Must be tied to a real signed-in user |

**Chelsea Piers default: application permissions.** Switch to delegated only when the workflow requires user attribution.

---

## Step 1 — Required env vars

```bash
AZURE_TENANT_ID=         # Directory (tenant) ID from Azure portal App Registration Overview
AZURE_CLIENT_ID=         # Application (client) ID from Azure portal App Registration Overview
AZURE_CLIENT_SECRET=     # Client secret value (not the secret ID) — expires, set a reminder
```

Optional for delegated flows:
```bash
AZURE_CLIENT_CERT_PATH=  # Path to PEM cert (preferred over secret for production)
```

Never hardcode. Always `os.getenv()` with a fail-fast check.

---

## Step 2 — App registration checklist

Before auth code works, the Azure app registration must be configured correctly. Check these once:

1. **App registration exists** in the correct tenant — Azure portal → Entra ID → App registrations
2. **Client secret created and not expired** — Certificates & secrets. Note the expiry date in `.env.example`.
3. **API permissions granted** — verify with `az ad app permission list --id $AZURE_CLIENT_ID`
4. **Admin consent granted** for all application permissions — green checkmarks in the Permissions page, or `az ad app permission admin-consent --id $AZURE_CLIENT_ID`
5. **Token endpoint accessible** — `https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token` responds

---

## Step 3 — Core implementation

### Application permissions (daemon / service)

```python
import os
import time
from msal import ConfidentialClientApplication

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

def _require_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(f"Required env var {key!r} is not set. Check .env or environment.")
    return val

class GraphClient:
    """
    MSAL confidential client for Microsoft Graph — application permissions.
    Thread-safe token cache with auto-refresh.
    """

    def __init__(
        self,
        tenant_id: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        scopes: list[str] | None = None,
    ):
        self._tenant_id = tenant_id or _require_env("AZURE_TENANT_ID")
        self._client_id = client_id or _require_env("AZURE_CLIENT_ID")
        self._client_secret = client_secret or _require_env("AZURE_CLIENT_SECRET")
        self._scopes = scopes or ["https://graph.microsoft.com/.default"]

        self._app = ConfidentialClientApplication(
            client_id=self._client_id,
            client_credential=self._client_secret,
            authority=f"https://login.microsoftonline.com/{self._tenant_id}",
        )
        self._token: str | None = None
        self._expires_at: float = 0

    def token(self) -> str:
        """Return a valid access token, refreshing silently if needed."""
        if self._token and time.time() < self._expires_at - 30:
            return self._token
        return self._refresh()

    def _refresh(self) -> str:
        # Try silent (cache) first, then acquire fresh
        result = self._app.acquire_token_silent(self._scopes, account=None)
        if not result:
            result = self._app.acquire_token_for_client(scopes=self._scopes)

        if "access_token" not in result:
            err = result.get("error_description", result.get("error", "unknown error"))
            raise RuntimeError(f"MSAL token acquisition failed: {err}")

        self._token = result["access_token"]
        self._expires_at = time.time() + result.get("expires_in", 3600)
        return self._token

    def headers(self) -> dict:
        return {
            "Authorization": f"Bearer {self.token()}",
            "Content-Type": "application/json",
        }

    def get(self, path: str, params: dict | None = None) -> dict:
        import httpx
        resp = httpx.get(
            f"{GRAPH_BASE}{path}",
            headers=self.headers(),
            params=params,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def post(self, path: str, body: dict) -> dict:
        import httpx
        resp = httpx.post(
            f"{GRAPH_BASE}{path}",
            headers=self.headers(),
            json=body,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()

    def patch(self, path: str, body: dict) -> dict:
        import httpx
        resp = httpx.patch(
            f"{GRAPH_BASE}{path}",
            headers=self.headers(),
            json=body,
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()
```

### Delegated permissions (device code flow for CLI/agent)

```python
from msal import PublicClientApplication

class GraphDelegatedClient:
    """
    MSAL public client — delegated permissions via device code flow.
    Use when the action must be attributed to a specific signed-in user.
    """

    def __init__(
        self,
        tenant_id: str | None = None,
        client_id: str | None = None,
        scopes: list[str] | None = None,
    ):
        self._scopes = scopes or ["https://graph.microsoft.com/.default"]
        self._app = PublicClientApplication(
            client_id=client_id or _require_env("AZURE_CLIENT_ID"),
            authority=f"https://login.microsoftonline.com/{tenant_id or _require_env('AZURE_TENANT_ID')}",
        )
        self._token: str | None = None

    def authenticate(self) -> str:
        """Initiate device code flow. Print the user code and URL, wait for sign-in."""
        flow = self._app.initiate_device_flow(scopes=self._scopes)
        if "user_code" not in flow:
            raise RuntimeError(f"Device flow failed: {flow.get('error_description')}")

        print(f"\nOpen: {flow['verification_uri']}")
        print(f"Enter code: {flow['user_code']}\n")

        result = self._app.acquire_token_by_device_flow(flow)
        if "access_token" not in result:
            raise RuntimeError(f"Auth failed: {result.get('error_description')}")

        self._token = result["access_token"]
        return self._token

    def headers(self) -> dict:
        if not self._token:
            self.authenticate()
        return {"Authorization": f"Bearer {self._token}"}
```

---

## Step 4 — Probe requests by plugin

Run one probe per plugin to confirm auth and permissions before building further.

### email-triage-m365
```python
graph = GraphClient()
# Confirm mailbox access
result = graph.get("/users", params={"$filter": "mail eq 'it-helpdesk@chelseapiers.com'", "$select": "id,mail,displayName"})
print(result)
# Required permission: User.Read.All (application)
```

### sharepoint
```python
graph = GraphClient()
# Confirm site access
result = graph.get("/sites/root", params={"$select": "id,displayName,webUrl"})
print(result)
# Required permission: Sites.Read.All (application)
```

### teams
```python
graph = GraphClient()
# Confirm team access
result = graph.get("/teams", params={"$select": "id,displayName"})
print(result)
# Required permission: Team.ReadBasic.All (application)
```

### azure-security
```python
graph = GraphClient()
# Confirm sign-in log access (requires Azure AD P1/P2)
result = graph.get("/auditLogs/signIns", params={"$top": "1"})
print(result)
# Required permission: AuditLog.Read.All (application)
```

---

## Step 5 — Permission manifest

Minimum required permissions per plugin. Request no more than needed. Get admin consent before testing.

| Plugin | Permission | Type | Justification |
|---|---|---|---|
| email-triage-m365 | `Mail.Read` | Application | Read helpdesk mailbox |
| email-triage-m365 | `Mail.Send` | Application | Auto-reply to requesters |
| email-triage-m365 | `User.Read.All` | Application | Look up user details from email |
| sharepoint | `Sites.Read.All` | Application | Search and retrieve SP content |
| sharepoint | `Sites.ReadWrite.All` | Application | Update permissions (if needed) |
| teams | `ChannelMessage.Send` | Application | Send IT notifications to channels |
| teams | `Team.ReadBasic.All` | Application | List teams and channels |
| teams | `User.Read.All` | Application | Check user presence |
| azure-security | `AuditLog.Read.All` | Application | Read sign-in logs |
| azure-security | `SecurityEvents.Read.All` | Application | Read Defender alerts |
| azure-security | `Policy.Read.All` | Application | Read conditional access policies |
| azure-security | `IdentityRiskyUser.Read.All` | Application | Read Entra Identity Protection data |

---

## Step 6 — Common error table

| Error code | Error message | Root cause | Fix |
|---|---|---|---|
| `AADSTS700016` | Application not found | Client ID wrong or in wrong tenant | Verify `AZURE_CLIENT_ID` + `AZURE_TENANT_ID` match the app registration |
| `AADSTS7000215` | Invalid client secret | Secret expired or wrong value | Rotate secret in Azure portal, update env var |
| `AADSTS65001` | Admin consent required | Permission not consented | Grant admin consent via portal or `az ad app permission admin-consent` |
| `401 Unauthorized` | Access token missing scope | Wrong permission requested | Add the missing permission scope and re-consent |
| `403 Forbidden` | Insufficient privileges | Permission granted but not correct type (delegated vs application) | Check whether delegated or application type matches the scenario |
| `429 Too Many Requests` | Throttled | Too many calls to same endpoint | Implement exponential backoff, use `$select` to reduce payload |
| `MsalServiceException` | Service unavailable | Transient Microsoft outage | Retry with backoff, check https://status.office365.com |

---

## Step 7 — Multi-tenant considerations

If Chelsea Piers expands to additional Entra tenants (e.g., subsidiary or partner tenant):

```python
# Each tenant needs its own ConfidentialClientApplication instance
# Do NOT share a single MSAL app across tenants — token caches are tenant-scoped

clients = {
    "chelseapiers": GraphClient(tenant_id=os.getenv("AZURE_TENANT_ID_PRIMARY")),
    "chelseapiersfitness": GraphClient(tenant_id=os.getenv("AZURE_TENANT_ID_FITNESS")),
}
```

Each tenant requires its own app registration and admin consent grant.

---

## MCP server integration pattern

When wiring this into an MCP server (the standard pattern for all Chelsea Piers plugins):

```python
from mcp.server.fastmcp import FastMCP
from .auth import GraphClient  # shared module

mcp = FastMCP("email-triage-m365")
_graph: GraphClient | None = None

def get_graph() -> GraphClient:
    global _graph
    if _graph is None:
        _graph = GraphClient()  # reads from env, lazy init
    return _graph

@mcp.tool()
def list_helpdesk_emails(top: int = 20) -> dict:
    """List unread emails in the IT helpdesk mailbox."""
    graph = get_graph()
    return graph.get(
        "/users/it-helpdesk@chelseapiers.com/messages",
        params={"$filter": "isRead eq false", "$top": top, "$orderby": "receivedDateTime desc"},
    )
```

Instantiate `GraphClient` once at module level (lazy, via `get_graph()`), not on every tool call. MSAL handles token refresh — callers do not need to manage token lifecycle.

---

## Report

After implementing auth for a Graph-connected plugin, output:

- Permissions granted (list with types — application vs delegated)
- Admin consent status (confirmed via portal screenshot or `az` output)
- Probe result for each endpoint the plugin uses
- Secret expiry date (set a calendar reminder)
- Any permission gaps found during probe (403s with specific scope names)
