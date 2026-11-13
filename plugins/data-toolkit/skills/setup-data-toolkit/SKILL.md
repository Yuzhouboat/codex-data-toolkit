---
name: setup-data-toolkit
description: Check Data Toolkit credential readiness and guide manual or wizard setup for MySQL, AWS/Redshift, and GitHub.
---

Follow this order: inspect existing settings, report readiness, establish service scope,
ask for the setup method, then configure only the selected missing settings. Existing
credentials are preserved unless the user explicitly requests changes.

Read [references/setup.md](references/setup.md) for runtimes, credential handling,
and disabling unused servers. Inspect available tools before proposing duplicate servers.

1. Resolve this plugin's installed root and run
   `node <installed-plugin-root>/scripts/runtime.mjs status` through local execution.
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
   explicitly wants to change/reset credentials. For GitHub with appLaunchRequired,
   explain the app launcher below instead of requesting the token again.

3. For services still needing setup, ask the user to choose exactly one method:
   "Set environment variables myself" or "Use the interactive wizard". Honor an already
   stated method without asking again. Wait for the answer before opening Terminal,
   editing settings, or issuing method-specific instructions.

4. For manual setup, list required/missing variable names for the selected services
   and give placeholder-only examples to run outside chat. MySQL uses MYSQL_HOST,
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
   through an agent-recorded terminal. If opening is unavailable/blocked, give the user
   `bash <installed-plugin-root>/scripts/setup.sh <services>` with the same selection and
   optional --reconfigure flag to run in their own terminal. Wait for completion and do
   not open another wizard while the user is working.

6. Once the user reports completion, rerun status for the selected services and report
   which credentials are present and which settings still need attention. Offer the
   packaged check-connectors workflow for read-only connection verification. Saving
   credentials or opening the wizard is not evidence of successful authentication.

The MySQL and AWS launchers automatically load saved settings. GitHub keeps its direct
HTTP connection and reads the app environment. If its token is saved but absent from
that environment, tell the user to fully quit the desktop app and run
`node <installed-plugin-root>/scripts/runtime.mjs app` in their own terminal each time
needed. Ordinary Dock launches do not load the saved token. This launcher is macOS-only.

When checking prerequisites, report executable availability or variable presence only.
The absence of exported variables is normal with the private credential store. Never
dump that file. Preserve unrelated settings and connector registrations; validate any
authorized config edit. Explain that the bundled AWS endpoint is us-east-1 and that
AWS_REGION alone does not change it. Finish with configured services, missing
prerequisites, and any restart or trust step.
