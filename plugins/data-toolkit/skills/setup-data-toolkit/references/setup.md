# Connector setup

Use a Codex client with plugin support and local execution. This package uses the
supported Codex compatibility manifest to retain `env_vars` and
`bearer_token_env_var` credential forwarding. It is intended for local Codex sessions.

| Service | Runtime | Credentials and defaults |
| --- | --- | --- |
| MySQL | Node.js 18+ and npx | MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD. Set MYSQL_HOST=localhost and MYSQL_PORT=3306 for a local server. |
| AWS / Redshift | Node.js 18+, uv with uvx | Existing AWS credential chain, or wizard-saved profile/access keys. Endpoint is us-east-1. |
| GitHub | Remote HTTP MCP; Node.js 18+ for the app launcher | GITHUB_PERSONAL_ACCESS_TOKEN supplied through the app launcher or existing launch environment. |

MySQL runs `@toolbox-sdk/server@1.16.0`; AWS runs `mcp-proxy-for-aws@1.6.3`.
First launch may download those packages. The Node runtime helper loads saved MySQL
or AWS settings and starts the pinned command. MySQL host and port are supplied by
the wizard, or must be set explicitly for environment-only setups.
GitHub uses the hosted endpoint `https://api.githubcopilot.com/mcp/`.

## Platform compatibility

Run `node scripts/runtime.mjs compatibility` when Node is available. The automatic
wizard requires macOS, Bash, AppleScript, and Terminal.app. On Windows or other unsupported
systems, or if these tools/local execution are unavailable, guide the user through manual
setup in their native shell instead. Do not offer the wizard or require Bash/WSL solely
for setup. An automation permission failure also falls back to manual setup.

On Windows, use `node scripts/runtime.mjs status --environment-only` for presence checks;
it skips the Unix private credential store. If Node is missing, report that prerequisite
and use native presence-only checks without printing values. Use PowerShell examples on
Windows and export syntax on Bash/Zsh. Environment variables set only in a terminal do
not automatically reach an already-running desktop app. Explain persistence and restart
requirements for the user's platform. Credential entry does not install MCP runtimes.

## Check existing setup first

Run `node scripts/runtime.mjs status` from the installed plugin root before launching
setup. An optional `mysql`, `aws`, or `github` argument scopes the report. Output includes
only configured state, credential source, missing/invalid variable names, and whether
the GitHub token is saved or present in the current process environment. It never returns credential values or tests remote access.

Show a readiness table for all services, listing only credential state and missing/invalid
variable names. Ask which service to set up first (or all), then ask whether the user
prefers manual environment-variable setup or the wizard. Reuse choices already stated
by the user and wait for each missing choice before proceeding.

Skip setup for already-configured requested services. A saved GitHub token that is absent
from the current process does not need to be entered again; ensure it reaches the app
through manual environment setup or the optional macOS launcher. Missing tools alone
do not prove the token is missing from the app. AWS's
default credential chain may already work even when status finds no explicit credentials;
verify existing AWS tools before recommending setup. Change existing credentials only
when the user asks. A malformed or inaccessible store is an error, not an empty setup.

## Interactive setup

On macOS, the setup skill can run this opener from the installed plugin root:

```bash
node scripts/runtime.mjs setup mysql
```

It opens a separate visible Terminal window; credentials are entered only in that window.
The agent may launch the opener, but must not capture the wizard's interactive input.
macOS may require permission to control Terminal. If opening fails or the platform is
unsupported, use manual environment-variable setup. Compatible macOS users can also
run the script themselves in their own terminal:

```bash
bash scripts/setup.sh mysql
```

Pass mysql, aws, github, all (the default), or multiple individual names to select stages.
The wizard skips services whose credentials are complete and keeps existing fields.
Append --reconfigure only when changing/resetting existing credentials is intended.
Each selected stage can also be skipped. It hides passwords,
access keys, session tokens, and GitHub tokens. Re-running keeps skipped settings.
Press Enter to retain an existing value. For the optional AWS session token, `-` clears it.
Completed stages are saved atomically; cancelling a stage preserves its previous settings.

Credentials are stored as plaintext in `~/.config/codex-data-toolkit/credentials.env`.
The directory has mode 700 and the file mode 600. The helper parses literal values;
this is not a shell script and must never be sourced. Arbitrary project .env files are
not loaded. Saved settings take precedence for configured services. If a service has
no saved settings, its existing environment/credential-chain setup continues working.
For AWS, selecting a profile clears inherited access keys; selecting keys clears
inherited profile settings. Profile/SSO sign-in remains managed by AWS tooling.

MySQL and AWS load their saved settings on MCP startup. GitHub remains a direct HTTP
connection and requires the token in the desktop app's environment. If the PAT is already
available there, no special launcher is required. If it is saved only in the wizard file,
configure the app environment manually or fully quit the macOS app and use this helper:

```bash
node scripts/runtime.mjs app
```

This detects the app by bundle ID `com.openai.codex`. If detection fails, supply its path:

```bash
node scripts/runtime.mjs app --app /Applications/ChatGPT.app
```

Use the launcher each time you reopen the app and need the saved GitHub token. Launching
from the Dock does not load it. The helper refuses to launch an already-running app;
it never force-quits it. Without a saved GitHub token, open the app normally for MySQL/AWS.
Existing environment-based credentials are still supported. Reuse a connected GitHub
app if it meets the user's needs and disable the bundled GitHub server to avoid duplicates.

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
