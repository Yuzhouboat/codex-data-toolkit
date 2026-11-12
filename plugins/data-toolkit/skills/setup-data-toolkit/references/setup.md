# Connector setup

Use a Codex client with plugin support and local execution. This package uses the
supported Codex compatibility manifest to retain `env_vars` and
`bearer_token_env_var` credential forwarding. It is intended for local Codex sessions.

| Service | Runtime | Credentials and defaults |
| --- | --- | --- |
| MySQL | Node.js 18+ and npx | MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD. Set MYSQL_HOST=localhost and MYSQL_PORT=3306 for a local server. |
| AWS / Redshift | uv with uvx | Existing AWS credential chain: profile, SSO, or environment. AWS_PROFILE is optional. Endpoint is us-east-1. |
| GitHub | Remote HTTP MCP; no extra local runtime | GITHUB_PERSONAL_ACCESS_TOKEN supplied to Codex through its launch environment. |

MySQL runs `@toolbox-sdk/server@1.16.0`; AWS runs `mcp-proxy-for-aws@1.6.3`.
First launch may download those packages. Codex starts each command directly;
there are no bundled launcher scripts. Supply MySQL host and port explicitly.
GitHub uses the hosted endpoint `https://api.githubcopilot.com/mcp/`.

Set credentials in the terminal or supported application launch environment, then restart
Codex. This package does not load .env files. Desktop launches may not inherit variables
from an unrelated terminal. Reuse a connected GitHub app if it already meets the user's
needs; disable the bundled GitHub server to avoid duplicate tools.

Use a database account and AWS/GitHub permissions appropriate for the requested work.
The servers can expose write tools according to those permissions. The connection-check
workflow uses read-only probes; the package does not enforce database read-only access.

## Unused connectors

In user or trusted-project Codex config, disable an unused bundled server:

```toml
[plugins."data-toolkit".mcp_servers.mysql]
enabled = false

[plugins."data-toolkit".mcp_servers."aws-mcp"]
enabled = false

[plugins."data-toolkit".mcp_servers.github]
enabled = false
```

Include only the entries the user wants disabled. This is the plugin-scoped MCP policy
namespace, distinct from the marketplace-qualified plugin enablement key.
Restart the session after configuration changes. A disabled connector is UNTESTED.

## AWS regions

The bundled endpoint is `https://aws-mcp.us-east-1.api.aws/mcp`. The environment's region
settings may influence tools, but they do not rewrite the proxy URL. To select a different
AWS MCP endpoint, configure a separate server using an endpoint verified against AWS's
current documentation, then disable the bundled aws-mcp entry. Avoid editing the installed
plugin cache, since a refresh replaces it.

## Verification

Ask: "Use check-connectors to check my Data Toolkit connections."
Configuration and executable presence do not establish remote access. AWS identity does
not establish Redshift SQL access.
