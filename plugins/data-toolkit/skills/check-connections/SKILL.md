---
name: check-connections
description: Check connectivity and authentication for the Data Toolkit's GitHub, Redshift, S3, and MySQL connections. Use for connection health checks, verifying setup, or diagnosing service access failures.
---

# Check Connections

Run small, read-only probes through the Data Toolkit's configured MCP connections.
Check all four services unless the user requests a subset. Continue checking the
other services when one fails or lacks configuration.

## Prepare

Discover the available GitHub, AWS, and MySQL tools and read their current schemas.
Use MCP connections rather than local CLI credentials: a successful local CLI call
does not verify the plugin's connection. If a required tool is absent, report that
service as unavailable instead of silently substituting a different connection.

Reuse targets and AWS regions supplied by the user or established in the session.
Read `../../.mcp.json` and the repository README if configuration guidance is
needed. They describe variable names and runtimes, not credential values. Keep
passwords, tokens, connection strings, and credential files out of tool output and
the report. Never request secret values in chat.

For AWS, use the configured region when it is known. Otherwise use `us-east-1` for
an initial API probe and disclose that choice. The AWS MCP endpoint's region does
not establish the location of the user's resources. Avoid an all-region inventory
for a connection check. Ask for missing targets only after completing probes that
can run without them.

## Probes

### GitHub

Call the authenticated-user tool (`get_me`). A successful response verifies the
MCP connection and authentication; report the login. A public repository search
alone is insufficient evidence of authentication. If a repository was specified,
also make one small read against it and report repository access separately.

### MySQL

Use `execute_sql` to run:

```sql
SELECT 1 AS connection_ok, DATABASE() AS database_name;
```

Expect `connection_ok = 1`. Report the selected database; a null database means the
server answered without a selected database. This probe verifies SQL execution,
not permissions on application tables. It needs no schema scan or table reads.

### AWS and S3

Through the AWS script tool, call STS `GetCallerIdentity` once to establish AWS
authentication. Then run an S3 probe independently, even if STS fails.

- With a specified bucket, use S3 `HeadBucket`. Success verifies bucket access;
  it does not prove object-read permissions. Preserve the supplied region or use
  a region returned by AWS to correct a region mismatch once.
- Without a bucket, use S3 `ListBuckets`. A successful empty response still
  verifies this API permission. Return only a count or a small summary, not an
  account-wide resource inventory. If listing is denied, ask for a bucket to test
  directly; the denial does not establish that all bucket access is broken.

Report AWS identity and S3 access as separate evidence. A successful STS response
alone cannot make S3 pass. Do not upload, download, or create objects for this test.

### Redshift

Check the API and query paths separately:

1. For a known provisioned cluster, call Redshift `DescribeClusters` for that
   identifier. For a known serverless workgroup, call Redshift Serverless
   `GetWorkgroup`. Otherwise probe `DescribeClusters` and `ListWorkgroups` in the
   chosen region, recording each result independently. An empty successful list
   verifies that API access, but establishes no usable database connection.
2. When a target database and supported authentication configuration are already
   known, use Redshift Data API `ExecuteStatement` with `SELECT 1 AS connection_ok`
   and the appropriate cluster identifier or workgroup name. Supply the known
   database and applicable authentication parameters; do not invent a database,
   database user, secret ARN, or authentication method. If a direct Redshift SQL
   tool is available for the intended target, the same query can verify that path.
3. With Data API, poll `DescribeStatement` until `FINISHED`, `FAILED`, or `ABORTED`,
   for at most 60 seconds with short waits, then use `GetStatementResult` to verify
   the returned value is 1. A statement ID alone is not query success. On timeout,
   report pending with its statement ID rather than claiming success or failure.

Without sufficient query configuration, report SQL as not tested and name the
missing non-secret target information. API discovery failure need not block a
query against an already known target. Control-plane success alone must be
reported as partial Redshift verification.

For AWS scripts, follow the current tool's `call_boto3` signature and response
contract. Use PascalCase operation names, isolate errors per probe, and verify
the response's API-call evidence rather than trusting a generated summary.

## Report

Return a compact table with one row per requested service: service, status,
evidence (including region or target where relevant), and next action if needed.
Use these statuses consistently:

- **PASS**: The service-specific probe returned the expected successful result.
  State the scope verified, such as S3 listing or access to a particular bucket.
- **PARTIAL**: Some access was verified, but a requested target or operation was
  denied or untested; use this for Redshift API success without SQL verification.
- **FAIL**: An attempted connection or authentication probe failed. Include a
  short, sanitized error and a targeted fix supported by the error.
- **NOT TESTED**: Missing tools, target configuration, or a pending query prevented
  a conclusive probe. Name what is needed to finish.

Distinguish missing MCP startup/runtime, invalid or expired credentials,
permission denial, network/DNS/TLS failure, and incorrect region or target when
the evidence supports it. Permission denial means the API responded but the
operation is restricted; do not describe it as a network outage. Avoid automatic
retries except the single S3 region correction and bounded query polling above.

For each failed or incomplete check, give the user concrete setup instructions
from [Setup and troubleshooting](references/troubleshooting.md). Read that reference
for any failed or incomplete check. Name the variables relevant to that failure, explain
where to make them available, and give the next check to run. Show placeholders
instead of actual secret values. Apply credential, IAM, database, or plugin
configuration changes only when separately requested.
