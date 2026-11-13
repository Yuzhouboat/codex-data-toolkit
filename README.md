# Codex Data Toolkit

A Codex plugin containing MCP connections for **MySQL, AWS / Redshift / S3, and GitHub**.
It uses existing server packages directly and includes a connection-check skill.

Version **0.1.9** is distributed through this public GitHub marketplace. It is not
listed in OpenAI's public Plugins Directory.

## Install

Register the marketplace:

```bash
codex plugin marketplace add Yuzhouboat/codex-data-toolkit
```

In the desktop Plugins Directory, choose **Yuzhou Data Toolkit** and install
**Data Toolkit**. Start a new session after installation.

On CLI versions supporting plugin installation:

```bash
codex plugin add data-toolkit@yuzhou-data-toolkit
```

## Credentials and runtimes

Configure credentials outside chat, in the environment available to Codex.

| Integration | Runtime | Credentials |
| --- | --- | --- |
| MySQL | Node.js 18+ and npx | MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD |
| AWS / Redshift | uv with uvx | Existing AWS profile, SSO session, or AWS credential environment |
| GitHub | Hosted HTTP MCP | GITHUB_PERSONAL_ACCESS_TOKEN |

Set MySQL host and port explicitly; use localhost and 3306 for a local server.
MySQL starts `@toolbox-sdk/server@1.16.0`. AWS starts `mcp-proxy-for-aws@1.6.3`
against `https://aws-mcp.us-east-1.api.aws/mcp`. AWS_REGION does not change that URL.
These packages may download dependencies on first start.

GitHub connects directly to `https://api.githubcopilot.com/mcp/`, using the PAT from
Codex's environment. No custom app launcher is needed.

This plugin does not collect credentials or load .env files. Exporting variables in
an unrelated terminal may not make them available to the desktop app. Restart the
app after changing its launch environment. Service permissions determine available
operations; the plugin does not enforce read-only access.

Versions before 0.1.8 included a wizard and private credential file. That file is no
longer read. Supply the required credentials through your environment or existing AWS
credential chain. Existing private files are left untouched; remove them yourself if
no longer needed.

## Use

Ask for the work you need, for example:

- "List the tables in my MySQL database and describe their columns."
- "List Redshift serverless workgroups in us-east-1."
- "Summarize open issues in owner/repository."

Available tools and service permissions determine which requests can run.

Use `$check-connections` or ask "Check all my service connections" to run
read-only checks for GitHub, Redshift, S3, and MySQL. The skill reports each
service separately, including missing configuration or permission errors, and
gives setup instructions with the relevant environment variable names and
steps to make them available to Codex.
Redshift API access and SQL execution are checked separately; SQL verification
requires a known target database and authentication configuration.

## Update or remove

Refresh the marketplace, then update the plugin using your client:

```bash
codex plugin marketplace upgrade yuzhou-data-toolkit
```

Use the Plugins Directory to uninstall. Uninstalling does not revoke credentials.

## Repository structure

```text
.agents/plugins/marketplace.json       # Plugin catalog
plugins/data-toolkit/
  .codex-plugin/plugin.json            # Identity and presentation
  .mcp.json                           # Direct MCP connections
  assets/icon.svg                     # Plugin icon
  skills/check-connections/            # Read-only service connection checks
README.md
NOTICE
```

To test local changes, register the repository directory with
`codex plugin marketplace add "$PWD"`, refresh/reinstall the plugin, and start a
new session. Edit the source files rather than the installed cache.

Derived from [ai-agent-data-toolkit](https://github.com/Yuzhouboat/ai-agent-data-toolkit).
See NOTICE for attribution.
