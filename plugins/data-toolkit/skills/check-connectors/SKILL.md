---
name: check-connectors
description: Verify Data Toolkit's MySQL, AWS/Redshift, and GitHub connections, distinguishing current-session tools, fresh MCP discovery, and authenticated operations.
---

Verify the toolkit's configured integrations with small, read-only probes. Account for
which connection and environment produced each result. Credential presence, MCP tool
discovery, and a successful authenticated operation are different kinds of evidence.

## Checks

1. Discover tools available in the current conversation, including deferred tool discovery
   when supported. Record each server as available, unavailable, or disabled. Use the
   actual schemas; names vary by agent and plugin. Configuration alone is not tool access.
2. Run the integration probes below through the current conversation's MCP tools when
   available. If a probe succeeds, record its exact operation and scope. No extra fresh
   connection is necessary for an already-working server unless the user requests one.
3. When current tools are unavailable or fail, attempt one fresh initialization/tool-list
   check using an existing supported read-only MCP diagnostic or app-server interface,
   if available. Scope it to the affected server. Use the installed configuration and
   existing credentials without printing secrets, editing config, creating an agent task,
   or installing diagnostic packages. If no supported diagnostic is available, mark fresh
   discovery UNTESTED and say why; never invent a successful check.
4. Label fresh-connection results separately. A fresh handshake and tool list establish
   discovery only, not authenticated operation success or access in the original thread.
   If a supported fresh diagnostic also executes an authenticated probe, label that read
   as belonging to the fresh connection. CLI/API fallbacks are additional diagnostics,
   not evidence of MCP access in the current conversation.
5. For unavailable tools, inspect current startup evidence before prescribing a fix.
   Prefer errors from the current attempt. Label older log entries with their timestamp
   and treat them as historical; do not present them as the current cause without a fresh
   failure confirming it. If recency or process identity cannot be established, say the
   cause remains unknown. Continue checking other integrations after a failure.

| Integration | Probe and evidence |
| --- | --- |
| MySQL | Through the configured MySQL MCP tool, execute `SELECT 1 AS connection_ok` if arbitrary read-only SQL is supported. Otherwise use its smallest metadata/list operation. Report which operation succeeded; metadata access alone does not verify SQL execution. |
| AWS | Through the configured AWS MCP tools, request STS caller identity, or another supported minimal identity operation. Report successful authentication without reproducing account identifiers. A successful local AWS CLI call alone does not verify the MCP server. |
| Redshift | If available through the AWS tools, make a bounded read-only cluster or serverless workgroup listing. If a specific warehouse and database are configured and an SQL tool is available, use `SELECT 1`; otherwise mark SQL access untested. AWS identity alone does not prove Redshift permissions or database access. |
| GitHub | Use the GitHub MCP tool's authenticated current-user operation when available. Otherwise use a small authenticated read against a repository already identified by the project. A public anonymous read does not prove the configured token works. |

For every probe, identify whether it used the current conversation, a fresh MCP
connection, or a direct CLI/API client. Report only permissions exercised by that probe.
When fresh discovery succeeds while current tools are unavailable, say exactly that;
this is consistent with a session/environment difference, not proof of stale caching.
Recommend a new conversation/reconnect as a bounded next step, then verify it rather
than claiming the original conversation has been repaired.

GitHub's direct MCP connection requires GITHUB_PERSONAL_ACCESS_TOKEN in the Codex
process environment; a special app launcher is not inherently required. Unavailable
tools alone do not establish that the token is missing. Check available startup errors
or presence-only environment diagnostics first, and distinguish the diagnostic shell's
environment from the running app. If the cause is unknown, report UNTESTED with
"Check GitHub MCP startup/configuration" as the next step. Recommend supplying the
token to the app only when current missing-environment evidence supports it. For a token saved
only in the wizard file, the macOS app launcher is one optional way to supply it;
manual launch-environment configuration is equally valid. Do not append a machine-specific
app-launch command to every report or require relaunch when GitHub tools already work.

## Credential handling and boundaries

When diagnosing missing configuration, inspect only whether named variables are present
and nonempty. The kit uses `MYSQL_HOST`, `MYSQL_PORT`,
`MYSQL_DATABASE`, `MYSQL_USER`, `MYSQL_PASSWORD`, and `GITHUB_PERSONAL_ACCESS_TOKEN`.
MySQL and AWS may load saved credentials through the bundled runtime helper.
GitHub may inherit its saved token through the desktop app launcher. Never read or dump
the private credential file during a check.
AWS may authenticate through profiles, SSO, or the default credential chain. Missing
environment variables alone do not prove authentication is broken. The running agent may also have a different environment
from the terminal where credentials were set.

Keep secrets out of tool arguments and chat output: never dump environment variables,
credential files, authorization headers, or raw config containing credentials. Pass existing
credentials through the client's normal environment/credential mechanism. Summarize errors
with secret values and connection strings removed; report missing variable names only.

Use existing tools and installed clients. Keep the check read-only: no credential setup,
package installation, config edits, resource creation, or test writes. For a failed probe,
give a concrete next step without retry loops or automatic fixes.

## Result

Return a compact table with rows for MySQL, AWS, Redshift, and GitHub and columns for:

- Current-session MCP tools
- Fresh MCP discovery
- Authenticated operation
- Evidence / next step

Use PASS, FAIL, or UNTESTED independently in each column. Current-session PASS means
its tools were discovered, not that authentication was tested. Fresh-discovery PASS means
an observed handshake/tool-list succeeded. Operation PASS requires an observed successful
probe and must name its connection scope and operation. For Redshift, distinguish resource
listing from database SQL access. Use FAIL only for an attempted check that failed;
unavailable/disabled tools or checks not performed are UNTESTED with an explanation.

If only discovery succeeded, explicitly leave authenticated access UNTESTED. If a current
probe succeeded and no fresh connection was needed, mark fresh discovery UNTESTED (not
needed). Do not summarize an entire integration as fully working from discovery alone,
and do not claim every connector tool works from one operation.

For example: GitHub current tools UNTESTED (unavailable), fresh discovery PASS (tools listed),
authenticated operation UNTESTED (not run). This calls for verifying the current session,
not declaring the PAT invalid or requiring another credential-entry step. Tool counts and
example outcomes must always come from actual observations, not this illustrative example.
