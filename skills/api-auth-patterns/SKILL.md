---
name: api-auth-patterns
description: |
  Implements authentication for external APIs. Use when integrating with any API that requires non-trivial auth.
  WHEN: implementing MCP server auth handlers for external services
  WHEN: connecting to NinjaOne, Mimecast, NetSuite, Meraki, AWS, or Microsoft Graph
  WHEN: asked to "add auth", "authenticate against", "get a token", "sign requests to"
  WHEN: encountering 401 Unauthorized or auth-related errors from an external API
  WHEN: building plugin integrations that need token refresh or credential rotation
  Supports: API Key, OAuth2 Client Credentials, HMAC-SHA1 signed requests, OAuth 1.0a TBA, AWS SigV4/STS, MSAL/Microsoft Graph OAuth2
version: 1.0.0
consumers: [principal_engineer, principal_architect]
---

# API Auth Patterns

## Purpose

Implement correct, secure authentication for external APIs without reinventing patterns or introducing credential leaks. Each auth type has a different handshake, token lifecycle, and failure mode. This skill provides the authoritative implementation pattern for each, grounded in the vendor's documented requirements.

Six patterns are in scope — chosen because they cover the Chelsea Piers IT ops plugin fleet (9 of 11 plugins) and are the most common non-standard auth types in enterprise integration work.

---

## Step 0 — Identify the pattern

Before writing a line of code, determine which pattern the target API uses. If unsure, read the vendor's authentication documentation. Do not guess from the API name.

| Service | Pattern |
|---|---|
| Cisco Meraki | API Key (header) |
| NinjaOne RMM | OAuth2 Client Credentials |
| Mimecast | HMAC-SHA1 signed requests |
| NetSuite ERP | OAuth 1.0a Token-Based Authentication (TBA) |
| AWS (any service) | AWS SigV4 + STS AssumeRole |
| Microsoft Graph (Azure, SharePoint, Teams, M365) | MSAL OAuth2 (app permissions or delegated) |

---

## Step 1 — Secrets management (all patterns)

Never hardcode credentials. Always read from environment variables. Document required env vars before implementing.

```python
# At module top — fail fast if secrets are missing
import os

def _require_env(key: str) -> str:
    val = os.getenv(key)
    if not val:
        raise EnvironmentError(f"Required env var {key!r} is not set")
    return val
```

Required env var naming convention: `{SERVICE}_{CREDENTIAL_TYPE}` — e.g. `MERAKI_API_KEY`, `NINJARMM_CLIENT_SECRET`, `MIMECAST_ACCESS_KEY`.

---

## Pattern A — API Key

**Target**: Cisco Meraki, any header-based or query-param-based key auth.

```python
import httpx

class ApiKeyAuth(httpx.Auth):
    """Header-based API key auth. Pass header_name per vendor spec."""

    def __init__(self, api_key: str, header_name: str = "X-Cisco-Meraki-API-Key"):
        self.api_key = api_key
        self.header_name = header_name

    def auth_flow(self, request):
        request.headers[self.header_name] = self.api_key
        yield request

# Usage
auth = ApiKeyAuth(api_key=_require_env("MERAKI_API_KEY"))
client = httpx.Client(auth=auth, base_url="https://api.meraki.com/api/v1")
```

**Probe request**: `GET /organizations` — expect 200 with list.

---

## Pattern B — OAuth2 Client Credentials

**Target**: NinjaOne RMM, any service using client_id + client_secret → access token flow.

```python
import time
import httpx
from threading import Lock

class OAuth2ClientCredentials:
    """Thread-safe token cache with auto-refresh."""

    def __init__(self, token_url: str, client_id: str, client_secret: str, scope: str = ""):
        self.token_url = token_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self._token: str | None = None
        self._expires_at: float = 0
        self._lock = Lock()

    def get_token(self) -> str:
        with self._lock:
            if self._token and time.time() < self._expires_at - 30:
                return self._token
            self._refresh()
            return self._token

    def _refresh(self):
        resp = httpx.post(self.token_url, data={
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            **({"scope": self.scope} if self.scope else {}),
        })
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        self._expires_at = time.time() + data.get("expires_in", 3600)

    def auth_header(self) -> dict:
        return {"Authorization": f"Bearer {self.get_token()}"}

# Usage — NinjaOne
auth = OAuth2ClientCredentials(
    token_url="https://app.ninjarmm.com/ws/oauth/token",
    client_id=_require_env("NINJARMM_CLIENT_ID"),
    client_secret=_require_env("NINJARMM_CLIENT_SECRET"),
    scope="monitoring management control",
)
```

**Probe request**: `GET /v2/devices` with `auth.auth_header()` — expect 200 or empty list.

---

## Pattern C — HMAC-SHA1 Signed Requests

**Target**: Mimecast. Each request requires a per-request signature built from timestamp, request ID, URI, and access key.

```python
import base64
import hashlib
import hmac
import uuid
import datetime
import httpx

class MimecastAuth:
    """
    Mimecast per-request HMAC-SHA1 signing.
    Docs: https://developer.services.mimecast.com/api-overview/authentication-guide
    """

    def __init__(self, access_key: str, secret_key: str, app_id: str, app_key: str):
        self.access_key = access_key
        self.secret_key = base64.b64decode(secret_key)
        self.app_id = app_id
        self.app_key = app_key

    def signed_headers(self, uri: str) -> dict:
        request_id = str(uuid.uuid4())
        date_str = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S UTC")

        # HMAC-SHA1 over: date + \n + request_id + \n + uri + \n + app_key
        data_to_sign = ":".join([date_str, request_id, uri, self.app_key])
        sig = base64.b64encode(
            hmac.new(self.secret_key, data_to_sign.encode(), hashlib.sha1).digest()
        ).decode()

        return {
            "Authorization": f"MC {self.access_key}:{self.app_id}:{sig}",
            "x-mc-date": date_str,
            "x-mc-req-id": request_id,
            "x-mc-app-id": self.app_id,
            "Content-Type": "application/json",
        }

# Usage
auth = MimecastAuth(
    access_key=_require_env("MIMECAST_ACCESS_KEY"),
    secret_key=_require_env("MIMECAST_SECRET_KEY"),
    app_id=_require_env("MIMECAST_APP_ID"),
    app_key=_require_env("MIMECAST_APP_KEY"),
)
uri = "/api/account/get-account"
headers = auth.signed_headers(uri)
resp = httpx.post(f"https://us-api.mimecast.com{uri}", headers=headers, json={"data": [{}]})
```

**Probe request**: `POST /api/account/get-account` — expect 200 with account data.

**Critical gotchas**: Clock skew >5 minutes causes 401. The `date_str` must be UTC. The URI in the signature is the path only (no host). `secret_key` is base64-encoded in the Mimecast console — decode before use.

---

## Pattern D — OAuth 1.0a Token-Based Authentication (TBA)

**Target**: NetSuite ERP. Non-standard OAuth 1.0a with HMAC-SHA256 (not SHA1). Requires account-specific domain.

```python
import hashlib
import hmac
import base64
import time
import uuid
import urllib.parse
import httpx

class NetSuiteTBA:
    """
    NetSuite OAuth 1.0a TBA with HMAC-SHA256.
    Docs: https://docs.oracle.com/en/cloud/saas/netsuite/ns-online-help/section_4393545816.html
    """

    def __init__(self, account_id: str, consumer_key: str, consumer_secret: str,
                 token: str, token_secret: str):
        self.account_id = account_id.upper().replace("-", "_")
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.token = token
        self.token_secret = token_secret

    def auth_header(self, method: str, url: str, params: dict | None = None) -> dict:
        nonce = uuid.uuid4().hex
        timestamp = str(int(time.time()))

        oauth_params = {
            "oauth_consumer_key": self.consumer_key,
            "oauth_nonce": nonce,
            "oauth_signature_method": "HMAC-SHA256",
            "oauth_timestamp": timestamp,
            "oauth_token": self.token,
            "oauth_version": "1.0",
        }

        # Combine oauth params + query params for signature base
        all_params = {**oauth_params, **(params or {})}
        sorted_params = "&".join(
            f"{urllib.parse.quote(k, safe='')}={urllib.parse.quote(v, safe='')}"
            for k, v in sorted(all_params.items())
        )
        base_string = "&".join([
            method.upper(),
            urllib.parse.quote(url, safe=""),
            urllib.parse.quote(sorted_params, safe=""),
        ])

        signing_key = f"{urllib.parse.quote(self.consumer_secret, safe='')}&{urllib.parse.quote(self.token_secret, safe='')}"
        sig = base64.b64encode(
            hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha256).digest()
        ).decode()

        oauth_params["oauth_signature"] = sig
        auth_str = "OAuth " + ", ".join(
            f'{k}="{urllib.parse.quote(v, safe="")}"'
            for k, v in sorted(oauth_params.items())
        )
        return {"Authorization": auth_str}

    @property
    def base_url(self) -> str:
        return f"https://{self.account_id}.suitetalk.api.netsuite.com/services/rest/record/v1"

# Usage
ns = NetSuiteTBA(
    account_id=_require_env("NETSUITE_ACCOUNT_ID"),
    consumer_key=_require_env("NETSUITE_CONSUMER_KEY"),
    consumer_secret=_require_env("NETSUITE_CONSUMER_SECRET"),
    token=_require_env("NETSUITE_TOKEN"),
    token_secret=_require_env("NETSUITE_TOKEN_SECRET"),
)
url = f"{ns.base_url}/customer"
headers = ns.auth_header("GET", url)
resp = httpx.get(url, headers=headers, params={"limit": 1})
```

**Probe request**: `GET /customer?limit=1` — expect 200 with items list.

**Critical gotchas**: NetSuite uses HMAC-SHA256, NOT SHA1 despite being OAuth 1.0a. Account ID must be uppercase with underscores (not hyphens). The base URL uses `suitetalk.api.netsuite.com`, not `rest.netsuite.com`. 2026.1 API: `oauth_version` must be `"1.0"` (string, not number).

---

## Pattern E — AWS SigV4 + STS AssumeRole

**Target**: Any AWS service (CloudTrail, GuardDuty, EC2, S3, IAM). Use `boto3` — do not implement SigV4 manually.

```python
import boto3
from botocore.exceptions import ClientError

class AWSAuthManager:
    """
    STS AssumeRole + boto3 session management.
    Handles cross-account access and temporary credential refresh.
    """

    def __init__(self, role_arn: str, session_name: str = "pna-agent",
                 region: str = "us-east-1", duration_seconds: int = 3600):
        self.role_arn = role_arn
        self.session_name = session_name
        self.region = region
        self.duration = duration_seconds
        self._session: boto3.Session | None = None
        self._expires_at: float = 0

    def session(self) -> boto3.Session:
        import time
        if self._session and time.time() < self._expires_at - 60:
            return self._session

        sts = boto3.client("sts", region_name=self.region)
        creds = sts.assume_role(
            RoleArn=self.role_arn,
            RoleSessionName=self.session_name,
            DurationSeconds=self.duration,
        )["Credentials"]

        self._session = boto3.Session(
            aws_access_key_id=creds["AccessKeyId"],
            aws_secret_access_key=creds["SecretAccessKey"],
            aws_session_token=creds["SessionToken"],
            region_name=self.region,
        )
        self._expires_at = creds["Expiration"].timestamp()
        return self._session

    def client(self, service: str) -> boto3.client:
        return self.session().client(service)

# Usage — requires AWS_DEFAULT_REGION and valid IAM creds in environment
aws = AWSAuthManager(
    role_arn=_require_env("AWS_ROLE_ARN"),
    region=_require_env("AWS_REGION"),
)

# Probe
iam = aws.client("iam")
try:
    iam.get_account_summary()
    print("AWS auth OK")
except ClientError as e:
    print(f"AWS auth failed: {e}")
```

**Probe request**: `iam.get_account_summary()` — expect success or explicit permission denied (either confirms auth works, permission denied is an IAM issue not auth).

**Critical gotchas**: If running inside an EC2 instance or Lambda, do not use STS AssumeRole for the same account — use the instance profile directly. STS session duration max is 12 hours. If the target account requires MFA, add `SerialNumber` and `TokenCode` to `assume_role` call. `boto3` handles SigV4 signing automatically — never implement it manually.

---

## Pattern F — MSAL / Microsoft Graph OAuth2

**Target**: Microsoft Graph API used by Azure Security, SharePoint, Teams, Exchange/M365 Email Triage.

Supports two flows:
- **App permissions** (no user): daemon/service use cases, requires admin consent
- **Delegated permissions** (on behalf of user): interactive or device code flow

```python
from msal import ConfidentialClientApplication
import httpx
import time

GRAPH_BASE = "https://graph.microsoft.com/v1.0"

class MSALAuth:
    """
    MSAL confidential client — app permissions (client credentials flow).
    For delegated flows, switch to PublicClientApplication with device_flow.
    """

    def __init__(self, tenant_id: str, client_id: str, client_secret: str,
                 scopes: list[str] | None = None):
        self.scopes = scopes or ["https://graph.microsoft.com/.default"]
        self._app = ConfidentialClientApplication(
            client_id=client_id,
            client_credential=client_secret,
            authority=f"https://login.microsoftonline.com/{tenant_id}",
        )
        self._token: str | None = None
        self._expires_at: float = 0

    def get_token(self) -> str:
        if self._token and time.time() < self._expires_at - 30:
            return self._token

        result = self._app.acquire_token_silent(self.scopes, account=None)
        if not result:
            result = self._app.acquire_token_for_client(scopes=self.scopes)

        if "access_token" not in result:
            raise RuntimeError(f"MSAL token acquisition failed: {result.get('error_description')}")

        self._token = result["access_token"]
        self._expires_at = time.time() + result.get("expires_in", 3600)
        return self._token

    def auth_header(self) -> dict:
        return {"Authorization": f"Bearer {self.get_token()}"}

    def graph_client(self) -> httpx.Client:
        return httpx.Client(
            base_url=GRAPH_BASE,
            headers=self.auth_header(),
            timeout=30,
        )

# Usage
msal_auth = MSALAuth(
    tenant_id=_require_env("AZURE_TENANT_ID"),
    client_id=_require_env("AZURE_CLIENT_ID"),
    client_secret=_require_env("AZURE_CLIENT_SECRET"),
)

# Probe — GET /organization
client = msal_auth.graph_client()
resp = client.get("/organization")
resp.raise_for_status()
```

**Probe request**: `GET /organization` — expect 200 with tenant details.

**Critical gotchas**: App permissions require admin consent for each permission scope — document required scopes before requesting. Delegated permissions require a signed-in user — not usable for daemon services. MSAL caches tokens in memory by default — for multi-process or serverless use, configure a distributed token cache. Token is valid 1 hour; MSAL `acquire_token_silent` handles refresh automatically. For SharePoint calls, the Graph base URL is correct (`/sites/{site-id}/...`); do not use the legacy SharePoint REST API unless explicitly required.

---

## Workflow

1. **Identify the pattern** using Step 0. Confirm with the vendor docs link if unsure.
2. **List required env vars** before writing any code. Document them in the MCP server README.
3. **Copy the pattern implementation** from the matching section above. Do not modify the core auth logic without a documented reason.
4. **Run the probe request**. Auth is not done until the probe succeeds.
5. **Wire into the MCP server** — instantiate auth at module load, pass the client or headers to each tool function. Do not re-authenticate per-request unless the pattern requires it (HMAC-SHA1 does — it is per-request by design).
6. **Add to .env.example** — all required env vars with placeholder values and a comment linking to the vendor console where credentials are obtained.

---

## Error handling

| Error | Likely cause | Fix |
|---|---|---|
| 401 Unauthorized | Wrong credentials or malformed signature | Re-check env vars, verify HMAC/signing steps match vendor docs exactly |
| 401 on Mimecast | Clock skew >5 min | Sync system clock, verify UTC timestamp format |
| 403 Forbidden | Auth works, missing permission scope | Expand scope, request admin consent (Graph), add IAM permission (AWS) |
| 400 on NetSuite | Wrong account ID format | Uppercase + underscores, not hyphens |
| Token expired mid-session | Missing refresh logic | All token-based patterns above include auto-refresh — check the `_expires_at` gate |
| MSAL error `AADSTS700016` | Client ID not found in tenant | Verify `AZURE_TENANT_ID` matches the app registration tenant |

---

## Report

After implementing auth for a service, output:

- Pattern used and why
- Required env vars (with vendor console link for each)
- Probe result (success / error and resolution)
- Any permission scopes or IAM policies required
- One-liner for `.env.example`
