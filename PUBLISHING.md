# Distribution and public directory submission

This repository provides a Git-backed marketplace and a local-execution plugin.
The ZIP is an authoring artifact, not an approved public-directory release.

## GitHub marketplace

The public GitHub repository is the distribution source. Users add
`Yuzhouboat/codex-data-toolkit` as a custom marketplace, then install data-toolkit
from yuzhou-data-toolkit. This does not list the plugin in OpenAI's public Plugins
Directory. Share https://github.com/Yuzhouboat/codex-data-toolkit with users.
No license is asserted by this package; public visibility alone does not grant an
open-source license. Confirm licensing for reuse, including the source repository's
copied workflow.

For each release, change the version in `plugins/data-toolkit/.codex-plugin/plugin.json`,
run validation/tests, build the ZIP, and smoke-test a fresh install. Commit and tag
the version, then attach the built ZIP to a GitHub release if desired.

## OpenAI public Plugins Directory

Official documentation checked 2026-11-11:

- [Package a plugin](https://developers.openai.com/plugins/build/plugins)
- [Submit and publish](https://developers.openai.com/plugins/deploy/submission)
- [Desktop-only submission](https://developers.openai.com/plugins/deploy/desktop-only)

The current MySQL server and AWS proxy run locally. Public submissions with local
MCP servers require approved-partner status and an allowlisted submitting organization.
Confirm eligibility with OpenAI before trying to submit this package.

The public portal currently connects one MCP server per plugin, whereas this
marketplace package bundles three connectors. Confirm desktop-package acceptance
with OpenAI or split connectors into separate listings. A hosted redesign would
require a server, user authentication, database network access, and a separate
evaluation of the portal's supported authentication methods. The bundled GitHub
PAT connection is not a ready-to-submit OAuth integration.

This package ships no lifecycle hooks or registered app references. Hooks are not
currently accepted in public-directory ZIPs.

Before submitting, complete developer identity verification, licensing, public
listing assets and publisher URLs, privacy/terms documentation, a clean installation
test, and real service tests with dedicated sample accounts. Prepare five positive
and three negative test cases plus a video walkthrough for an MCP submission.
Do not mark unexecuted examples as passed or include reviewer secrets in the ZIP.

Recommended live test cases: MySQL SELECT 1 and schema discovery, AWS caller identity,
bounded Redshift workgroup listing, authenticated GitHub read, and missing-credential
handling. Also test that checks stay read-only and avoid disclosing credentials.
Verify permissions separately for each service.

After review approval, publishing is a separate action in the submission portal.
Marketplace installation alone does not create a public-directory listing.
