---
name: setup-data-toolkit
description: Set up Data Toolkit credentials and runtimes, select its MySQL, AWS/Redshift, or GitHub integrations.
---

Configure the services the user intends to use. Installation makes connector definitions
available; it does not supply credentials or prove access.

Read [references/setup.md](references/setup.md) for runtimes, environment variables,
and disabling unused servers. Inspect available tools before proposing duplicate servers.
The plugin's `scripts/check_prerequisites.py` can report executable and variable presence
without network requests. Run it from the installed plugin root if local execution is
available. Report the difference between this shell and the running Codex environment.

Keep credentials in the user's existing environment or credential manager. Report variable
names and set/unset state; ask the user to enter secret values outside chat. Preserve
unrelated settings and existing connector registrations. When a requested configuration
change is authorized, make the smallest edit and validate the resulting TOML or JSON.

Explain that the bundled AWS proxy targets us-east-1. AWS_REGION alone does not change
that endpoint. Use the setup reference when a different endpoint is requested.

Finish by listing configured services, missing prerequisites, and any restart or project
trust step. When asked to verify connections, use the packaged check-connectors workflow
and report actual read-only probe evidence rather than treating configuration as success.
