---
name: check-connectors
description: Check Data Toolkit's MySQL, AWS/Redshift, and GitHub integrations when asked to verify connector tools, credentials, or connectivity.
---

Verify the toolkit's configured integrations with small, read-only probes. Report what
actually worked in this agent session, rather than inferring success from installed files.

## Checks

Discover the tools available in this session, including deferred tools if the agent offers
tool discovery. Inspect plugin or project configuration only as needed to identify the configured
servers. Use the actual tool schemas; names vary by agent and plugin.

| Integration | Probe and evidence |
| --- | --- |
| MySQL | Through the configured MySQL MCP tool, execute `SELECT 1 AS connection_ok` if arbitrary read-only SQL is supported. Otherwise use its smallest metadata/list operation. Report which operation succeeded; metadata access alone does not verify SQL execution. |
| AWS | Through the configured AWS MCP tools, request STS caller identity, or another supported minimal identity operation. Report successful authentication without reproducing account identifiers. A successful local AWS CLI call alone does not verify the MCP server. |
| Redshift | If available through the AWS tools, make a bounded read-only cluster or serverless workgroup listing. If a specific warehouse and database are configured and an SQL tool is available, use `SELECT 1`; otherwise mark SQL access untested. AWS identity alone does not prove Redshift permissions or database access. |
| GitHub | Use the GitHub MCP tool's authenticated current-user operation when available. Otherwise use a small authenticated read against a repository already identified by the project. A public anonymous read does not prove the configured token works. |

For every integration, distinguish tool availability, remote connectivity/authentication,
and the permissions exercised by the probe. If the tool is unavailable, report that and the
next setup step; a direct CLI/API fallback may supply extra diagnostic evidence but must
not count as an MCP success. Continue checking the other integrations after a failure.

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

Return one compact table with rows for MySQL, AWS, Redshift, and GitHub and columns
for status, evidence, and next step. Use `PASS` only for the precise operation actually
verified, `FAIL` for an attempted operation that failed, and `UNTESTED` when a necessary
tool, target, or permission to run the probe was unavailable. Never claim that every
connector tool works from one probe per service.
