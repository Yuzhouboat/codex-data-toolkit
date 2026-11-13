# Codex Data Toolkit

A Codex plugin for **MySQL, AWS / Redshift, and GitHub**, with guided setup and
read-only connection checks. Derived from
[ai-agent-data-toolkit](https://github.com/Yuzhouboat/ai-agent-data-toolkit), with
independent source control and plugin installation instead of a shell installer.

Version **0.1.6** is a GitHub-marketplace package for local Codex sessions. It has
not been approved or published in OpenAI's public Plugins Directory.

## Install

Use a Codex client with plugin marketplace support. Register this public GitHub
repository as a custom marketplace:

```bash
codex plugin marketplace add Yuzhouboat/codex-data-toolkit
```

Open the Plugins Directory in the desktop client, choose **Yuzhou Data Toolkit**,
and install **Data Toolkit**. Restart or start a new session after installation.
Share this repository link with other users:
[Yuzhouboat/codex-data-toolkit](https://github.com/Yuzhouboat/codex-data-toolkit).
Users must add this custom marketplace before browsing its plugins; the plugin
is not listed in OpenAI's public Plugins Directory.

On CLI versions exposing `codex plugin add`, you can also install with:

```bash
codex plugin add data-toolkit@yuzhou-data-toolkit
```

For local development:

```bash
git clone https://github.com/Yuzhouboat/codex-data-toolkit.git
cd codex-data-toolkit
codex plugin marketplace add "$PWD"
```

Install from that source, then launch a fresh session. Codex loads a cached copy;
after editing source, refresh the marketplace and reinstall/refresh the plugin
using your client's controls. Do not edit the installed cache.

## Credentials and runtimes

| Integration | Requirements |
| --- | --- |
| MySQL | Node.js 18+ with npx; MYSQL_HOST, MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD |
| AWS / Redshift | Node.js 18+, uv with uvx; an existing AWS profile, SSO session, or access keys |
| GitHub | GITHUB_PERSONAL_ACCESS_TOKEN available to Codex; Node.js 18+ for the saved-token app launcher |

Set MYSQL_HOST and MYSQL_PORT explicitly; use localhost and 3306 for a local MySQL server.
The AWS proxy targets **us-east-1**. AWS_REGION does not rewrite that proxy URL.
MySQL's server package is pinned to **1.16.0** and the AWS proxy to **1.6.3**.
They may download dependencies on first start. GitHub uses its hosted MCP service.

Ask **"Use setup-data-toolkit to help me configure my connections."** The skill:

1. Shows credential readiness and missing/invalid variable names for all three services.
2. Asks which service to set up first, or whether to set up all services.
3. Skips services whose credentials are already present.
4. On compatible macOS systems, asks whether you prefer manual environment setup or
   the wizard. On Windows or incompatible systems, guides manual setup in your native shell.
5. For the wizard choice on macOS, opens a separate Terminal window for your selection.

Credential presence is separate from verified connection access. No secret values are
shown in the readiness report. For manual setup, follow the selected service's variable
instructions outside chat; exports in another terminal may not reach the desktop app.
For wizard setup, macOS may ask you to allow control of Terminal. The agent does not capture your input.
You can also open the wizard from this repository:

```bash
node plugins/data-toolkit/scripts/runtime.mjs setup mysql
```

If automatic opening fails, use manual environment-variable setup. On a compatible
macOS system, you may also run the wizard yourself in your own terminal:

```bash
bash plugins/data-toolkit/scripts/setup.sh mysql
```

For an installed copy, the setup skill resolves the installed plugin path. It checks
compatibility before offering the wizard; missing Bash, AppleScript, Terminal, or Node
results in manual setup guidance. It does not require Windows users to install WSL/Bash.
Use PowerShell environment instructions on Windows and restart the desktop app after
changing its launch environment. Runtime prerequisites still need to be installed.
`node plugins/data-toolkit/scripts/runtime.mjs status --environment-only` checks variable
presence without loading the Unix credential store.
Use mysql, aws, github, or all (the default) to select services. Multiple service names
are also accepted. Complete services and existing fields are kept automatically. Add
--reconfigure only to change existing credentials. Each service can also be skipped.
Passwords, tokens, and AWS access keys use
hidden input. AWS supports either an existing profile/SSO session or access keys with
an optional session token. The wizard does not create accounts, tokens, or AWS profiles.

Settings are stored as **plaintext** in `~/.config/codex-data-toolkit/credentials.env`,
with directory permission 700 and file permission 600. The helper parses this file as
literal data, never as shell commands. Do not source it or paste its contents into chat.
Project `.env` files are not loaded. Re-running preserves skipped services and offers
to keep existing values; completed service stages are saved atomically.

MySQL and AWS load saved settings automatically when their MCP servers start. Saved
settings take precedence; environment-only configurations continue working when a
service has no saved settings. The wizard defaults MySQL host/port to localhost/3306.

GitHub keeps its direct HTTP connection, so its token must reach the desktop app's
environment. If the PAT is already available there, no special launcher is required.
If it is saved only in the wizard file, configure the app's environment manually or use
this optional macOS helper after fully quitting the app:

```bash
node plugins/data-toolkit/scripts/runtime.mjs app
```

The helper detects the app by bundle ID `com.openai.codex`, refuses to launch it if
already running, and never force-quits it. If detection fails, append
`--app /Applications/ChatGPT.app` or your actual app path. Use this helper each time
you reopen the app and need the saved GitHub token; opening from the Dock does not
load it. From an installed copy, use its runtime script path instead.

Without a saved GitHub token, open the app normally for MySQL/AWS. Existing credentials
supplied through the app's launch environment remain supported. Saving credentials
does not test live access; use Check Connectors afterward.

Ask **"Use setup-data-toolkit to help me configure my connections."** to select
services and disable unused connectors. The setup skill includes configuration
examples for plugin-scoped server policy. Prefer reusing an existing connected app
over adding duplicate tools.

These connectors may expose write capabilities according to your service
permissions. Use appropriate database, AWS, and GitHub credentials. The bundled
connection checks are read-only; this package is not a read-only enforcement layer.

## Use

Start with **"Use check-connectors to check my Data Toolkit connections."**

Checks report PASS, FAIL, or UNTESTED with actual evidence. They distinguish AWS
identity from Redshift SQL access and tool configuration from successful calls.
Then ask for the work you need, for example:

- "List the tables in my MySQL database and describe their columns."
- "List Redshift serverless workgroups in us-east-1."
- "Summarize open issues in owner/repository."

The available tools and permissions determine which requests can run.

## Update or remove

Refresh this marketplace, then update the installed plugin using the client:

```bash
codex plugin marketplace upgrade yuzhou-data-toolkit
```

Use the Plugins Directory to uninstall. On CLI versions exposing these commands:

```bash
codex plugin remove data-toolkit@yuzhou-data-toolkit
codex plugin marketplace remove yuzhou-data-toolkit
```

Check `codex plugin remove --help` for your installed client's selector format.
Uninstalling does not revoke service credentials or remove the private credential file.
Delete `~/.config/codex-data-toolkit/credentials.env` yourself to remove saved settings.

## Repository structure

```text
.agents/plugins/marketplace.json      # Lists the plugin
plugins/data-toolkit/
  .codex-plugin/plugin.json           # Identity, presentation, and onboarding
  .mcp.json                          # MySQL, AWS, and GitHub connections
  assets/icon.svg                    # Plugin icon
  scripts/setup.sh                    # Interactive terminal wizard
  scripts/runtime.mjs                 # Credential loading and app/server launch
  skills/
    setup-data-toolkit/SKILL.md       # Guided setup
    setup-data-toolkit/references/setup.md
    check-connectors/SKILL.md         # Read-only connection checks
```

Edit these files directly. This repository has no automated test folder, GitHub
workflow, or ZIP build. The two scripts support interactive setup and runtime startup. Local MCP entries use
`cwd: "."` and relative script arguments so Codex resolves them from the installed
plugin directory without relying on placeholder expansion.

To try changes locally, register the repository directory:

```bash
codex plugin marketplace add "$PWD"
```

Refresh the marketplace, update/reinstall the plugin, and start a new session.
Use check-connectors to verify live service access after configuring credentials.
