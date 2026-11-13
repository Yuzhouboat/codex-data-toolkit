---
name: setup-data-toolkit
description: Set up Data Toolkit credentials and runtimes, select its MySQL, AWS/Redshift, or GitHub integrations.
---

Configure the services the user intends to use. Installation makes connector definitions
available; it does not supply credentials or prove access.

Read [references/setup.md](references/setup.md) for runtimes, environment variables,
and disabling unused servers. Inspect available tools before proposing duplicate servers.
For interactive setup on macOS, resolve this plugin's installed root, then run
`node <installed-plugin-root>/scripts/runtime.mjs setup` through the local execution
tool, passing the path as a properly quoted argument. This opens the wizard in a
separate visible Terminal window. Tell the user to enter credentials in that window
and return when finished. Launching this opener is safe for tool logs: it passes only
the script path, and no credential values or interactive input pass through the agent.

The wizard collects MySQL, AWS profile/access-key, and GitHub settings with hidden
secret entry and saves a private local credential file. Never run `setup.sh` interactively
through an agent-recorded terminal or ask for secrets in chat. If automatic opening is
unavailable or blocked, give the user the installed `bash scripts/setup.sh` command to
run in their own terminal. Wait for completion; opening the window or saving a file
does not prove access. Do not launch another wizard while waiting for the user.

The MySQL and AWS launchers automatically load saved settings. GitHub keeps its direct
HTTP connection and reads the app environment. For a saved GitHub token, tell the user
to fully quit the desktop app and run `node scripts/runtime.mjs app` from the installed
plugin root in their own terminal each time they need to reopen the app. Ordinary Dock
launches do not load the saved token. This launcher supports macOS only.

When checking prerequisites, report executable availability or variable presence only.
The absence of exported variables is normal when using the saved credential file.
Keep its contents out of tool output and chat.

Keep credentials in the private wizard store or the user's existing environment. Report
variable names and set/unset state only; secrets are entered outside chat. Preserve
unrelated settings and existing connector registrations. When a requested configuration
change is authorized, make the smallest edit and validate the resulting TOML or JSON.

Explain that the bundled AWS proxy targets us-east-1. AWS_REGION alone does not change
that endpoint. Use the setup reference when a different endpoint is requested.

Finish by listing configured services, missing prerequisites, and any restart or project
trust step. When asked to verify connections, use the packaged check-connectors workflow
and report actual read-only probe evidence rather than treating configuration as success.
