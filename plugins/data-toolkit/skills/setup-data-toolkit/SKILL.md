---
name: setup-data-toolkit
description: Check Data Toolkit credential readiness and guide manual or wizard setup for MySQL, AWS/Redshift, and GitHub.
---

Follow this order: inspect existing settings, report readiness, establish service scope,
ask for the setup method, then configure only the selected missing settings. Existing
credentials are preserved unless the user explicitly requests changes.

Read [references/setup.md](references/setup.md) for runtimes, credential handling,
and disabling unused servers. Inspect available tools before proposing duplicate servers.

1. Identify the user's native operating system from environment context (a Bash shell
   on Windows does not make the native desktop app macOS-compatible). Resolve this
   plugin's installed root. If Node is available, run
   `node <installed-plugin-root>/scripts/runtime.mjs compatibility` to check the launcher.
   Then run `node <installed-plugin-root>/scripts/runtime.mjs status` through local execution.
   On Windows, use `status --environment-only` to avoid the Unix private-store checks.
   If Node/local execution is unavailable, use existing tools and OS-native presence-only
   checks where possible; label unavailable checks UNTESTED rather than requesting secrets.
   Always show a compact table for MySQL, AWS/Redshift, and GitHub with credential state,
   missing/invalid variable names, and next step. Describe complete settings as
   "Credentials present; connection not yet verified", never as a successful connection.
   Show AWS's default credential chain as "Needs verification", not definitely missing.
   Use existing AWS tools when available to determine whether it already authenticates.
   If status fails, report and resolve that storage/runtime error; do not treat it as an
   empty store or overwrite it. Keep credential values out of tools and chat.

2. Ask which service the user wants to set up first: MySQL, AWS/Redshift, GitHub, or all
   services. If the user already specified scope, use it rather than asking again.
   A text-input question tool may be used when available; otherwise ask in conversation.
   Wait for the answer before configuring anything. Skip already-configured selected
   services and explain that no credential entry is needed for them. If all selected
   services are configured, offer check-connectors and stop setup unless the user
   explicitly wants to change/reset credentials. For GitHub, distinguish savedTokenPresent
   from environmentTokenPresent. A saved token need not be entered again, and an existing
   environment token does not require a special launcher even if it differs from the saved
   token. Presence diagnostics describe their current process, not necessarily the app.

3. Offer the wizard only when compatibility reports wizardSupported: true and local
   execution is available. On Windows, other unsupported systems, missing Bash/AppleScript/
   Terminal, or unavailable Node/local execution, explain the limitation and guide the user
   through manual environment-variable setup for their selected services. Never ask them
   to install Bash/WSL solely to run this wizard or offer a wizard known to be incompatible.
   If the wizard was requested but unsupported, explain the fallback before proceeding.
   On compatible systems, ask the user to choose exactly one method:
   "Set environment variables myself" or "Use the interactive wizard". Honor an already
   stated method without asking again. Wait for the answer before opening Terminal,
   editing settings, or issuing method-specific instructions.

4. For manual setup, list required/missing variable names for the selected services
   and give placeholder-only examples for their native shell (PowerShell on Windows,
   export syntax for Bash/Zsh) to run outside chat. State whether settings affect only
   the current terminal or persist for future app launches; explain any required restart.
   Do not run Unix chmod/private-store or macOS app-launch commands on Windows. Missing
   Node/npx/uvx prerequisites are separate from credential setup and must also be reported.
   MySQL uses MYSQL_HOST,
   MYSQL_PORT, MYSQL_DATABASE, MYSQL_USER, and MYSQL_PASSWORD. AWS can use an existing
   profile/SSO session or access keys with an optional session token; establish the
   authentication method before prescribing variables. GitHub uses
   GITHUB_PERSONAL_ACCESS_TOKEN in the app's launch environment. Explain that an unrelated
   terminal's exports may not reach the desktop app. Saved settings take precedence;
   if an invalid saved value conflicts, explain how the user can update/remove that entry
   outside chat rather than suggesting exports will override it. Never request secret
   values in chat or write them on the user's behalf.

5. For wizard setup on macOS, run
   `node <installed-plugin-root>/scripts/runtime.mjs setup <services>` through local
   execution, quoting the installed path correctly. Replace <services> with mysql, aws,
   github, all, or a space-separated list of the selected services still missing settings.
   Append --reconfigure only when the user explicitly wants to change/reset credentials.
   This opens a separate visible Terminal window. The opener passes only script paths
   and service names; credentials stay in that window. Never run setup.sh interactively
   through an agent-recorded terminal. If opening is unavailable/blocked, explain the
   failure and fall back to manual environment-variable instructions. Do not retry the
   opener in a loop or suggest incompatible shell commands. Wait for completion and do
   not open another wizard while the user is working.

6. Once the user reports completion, rerun status (with --environment-only on Windows)
   for the selected services, or repeat available OS-native presence checks, and report
   which credentials are present and which settings still need attention. Offer the
   packaged check-connectors workflow for read-only connection verification. Saving
   credentials or opening the wizard is not evidence of successful authentication.

The MySQL and AWS launchers automatically load saved settings. GitHub keeps its direct
HTTP connection and only needs GITHUB_PERSONAL_ACCESS_TOKEN in the app environment.
When it is already available, no special launcher or relaunch is required. If a saved
token is not reaching the app, offer manual environment configuration or, on compatible
macOS systems, the optional `node <installed-plugin-root>/scripts/runtime.mjs app` helper
after fully quitting the app. Ordinary Dock launches do not read the wizard file. Never
infer a missing token solely from missing tools; inspect startup evidence first.

When checking prerequisites, report executable availability or variable presence only.
The absence of exported variables is normal with the private credential store. Never
dump that file. Preserve unrelated settings and connector registrations; validate any
authorized config edit. Explain that the bundled AWS endpoint is us-east-1 and that
AWS_REGION alone does not change it. Finish with configured services, missing
prerequisites, and any restart or trust step.
