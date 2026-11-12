# Codex Data Toolkit

A Codex plugin for **MySQL, AWS / Redshift, and GitHub**, with guided setup and
read-only connection checks. Derived from
[ai-agent-data-toolkit](https://github.com/Yuzhouboat/ai-agent-data-toolkit), with
independent source control and plugin installation instead of a shell installer.

Version **0.1.1** is a GitHub-marketplace package for local Codex sessions. It has
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
| MySQL | Python 3.8+, Node.js 18+ with npx; MYSQL_DATABASE, MYSQL_USER, MYSQL_PASSWORD |
| AWS / Redshift | uv with uvx; an existing AWS profile, SSO session, or credential environment |
| GitHub | GITHUB_PERSONAL_ACCESS_TOKEN available to the Codex process |

MySQL defaults to localhost:3306; set MYSQL_HOST and MYSQL_PORT to override.
The AWS proxy targets **us-east-1**. AWS_REGION does not rewrite that proxy URL.
MySQL's server package is pinned to **1.16.0** and the AWS proxy to **1.6.3**.
They may download dependencies on first start. GitHub uses its hosted MCP service.

Export credentials outside chat in the environment used to launch Codex, or use
your supported application launch environment. Restart Codex after changing them.
This plugin does not load .env files, request secrets in chat, or provide credentials.
Desktop sessions may not inherit exports made in an unrelated terminal.

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
Uninstalling does not revoke service credentials.

## Develop and package

Build tooling requires Python **3.11+**, with no third-party Python packages:

```bash
python3 scripts/package_plugin.py --check
python3 -m unittest discover -s tests -v
python3 scripts/package_plugin.py
```

Output: `dist/data-toolkit-0.1.1.zip`. Its root contains `.codex-plugin/plugin.json`,
`.mcp.json`, scripts, and skills. The packager validates references, rejects
symlinks and unlisted plugin files, and uses an explicit release-file allowlist.
The `.agents/plugins/marketplace.json` catalog remains in the repository, outside
the plugin ZIP. CI runs validation, unit tests, and builds an artifact.

With Codex CLI installed, run `python3 scripts/smoke_codex.py` to register the
marketplace, install the plugin, inspect parsed MCP definitions, and uninstall in
a disposable CODEX_HOME. It does not modify your active profile or contact services.

The supported Codex compatibility format retains environment-based authentication
from the original toolkit. No global config merger or credential installer is bundled.
See [PUBLISHING.md](PUBLISHING.md) for public-directory eligibility and the remaining
release requirements. Local package checks do not verify live service connectivity.
