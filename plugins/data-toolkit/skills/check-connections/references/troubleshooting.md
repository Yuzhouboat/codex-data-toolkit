# Connection Setup and Troubleshooting

### Make configuration available to Codex

The plugin inherits credentials from the environment of the Codex process. It
does not load `.env` files. Exporting variables in an unrelated terminal does not
configure an already running desktop app. For CLI use, export them in the shell
that launches Codex, then start a new session. For desktop use, configure the
environment used to launch the app, fully quit and reopen it, then start a new
session. Tailor launch instructions to the user's platform when known; do not
claim shell profile edits automatically configure a GUI-launched app.

Only name variables as missing when evidence establishes that. Otherwise say
"verify these variables are available to Codex". If checking local presence is
useful, print only variable names and set/unset status, never their values; the
local shell's environment does not prove what a remote MCP server received.

### GitHub

- Authentication missing, invalid, or expired: make
  `GITHUB_PERSONAL_ACCESS_TOKEN` available to Codex. Use a valid PAT with access
  to the intended repositories, then restart as described above and rerun
  `get_me`. Do not suggest `GH_TOKEN` or `GITHUB_TOKEN` as substitutes: this plugin
  is configured to read `GITHUB_PERSONAL_ACCESS_TOKEN`.
- Authentication succeeds but repository access fails: verify the repository
  owner/name, the PAT's repository selection and required read permissions, and
  organization authorization if required. Adding environment variables alone
  will not grant access. Rerun the specific repository read after fixing access.

### MySQL

Verify all five variables are available to Codex:

| Variable | What the user supplies |
| --- | --- |
| `MYSQL_HOST` | Reachable database hostname; `localhost` for a local server |
| `MYSQL_PORT` | Explicit server port, normally `3306` |
| `MYSQL_DATABASE` | Existing database name |
| `MYSQL_USER` | Database login with permission to connect to that database |
| `MYSQL_PASSWORD` | That login's password, configured outside chat |

For access-denied errors, verify the username/password and MySQL host-based
grants. For an unknown database, correct `MYSQL_DATABASE` or have the database
administrator provide an existing accessible database. For DNS, refusal, or
timeout errors, verify host/port, that the server is running, and any required
VPN, firewall, or network access. For MCP startup failures, verify Node.js 18+
and `npx` are available to the Codex process. Restart and rerun the SQL probe.

### AWS credentials shared by S3 and Redshift

Choose the user's existing authentication method; do not require both:

- **Profile or SSO:** Make `AWS_PROFILE` available to Codex for a named profile.
  Use the existing AWS configuration and credential files. If SSO has expired,
  run `aws sso login --profile <profile>` in the user's environment, then retry.
  For nondefault file locations, make `AWS_CONFIG_FILE` and/or
  `AWS_SHARED_CREDENTIALS_FILE` available as applicable.
- **Environment credentials:** Make `AWS_ACCESS_KEY_ID` and
  `AWS_SECRET_ACCESS_KEY` available to Codex. Temporary credentials also require
  the matching `AWS_SESSION_TOKEN`; replace the complete set when expired.
  Stale environment credentials can override a valid profile, so resolve
  conflicting sources when the error indicates the wrong credentials are used.

Make `AWS_REGION` or `AWS_DEFAULT_REGION` available with the intended resource
region. The configured AWS MCP URL stays in `us-east-1` regardless of these
variables; each probe must still use the correct resource region. For AWS MCP
startup failures, verify `uv`/`uvx` are available to the Codex process. Restart
after changing launch configuration and rerun STS and the affected service probe.

### S3 access

If AWS authentication works but S3 is denied, explain the permission needed by
the attempted probe: `s3:ListAllMyBuckets` for listing, or `s3:ListBucket` on the
specified general purpose bucket for `HeadBucket`. For a directory bucket,
consult the [HeadBucket documentation](https://docs.aws.amazon.com/AmazonS3/latest/API/API_HeadBucket.html)
for its distinct permissions and endpoint requirements. A generic HeadBucket
400/403/404 response cannot reliably distinguish a missing bucket from denied
access; report that ambiguity instead of inventing a cause. The user may supply a known bucket to avoid
requiring account-wide listing. Check bucket spelling, region, and relevant
identity/bucket policies when supported by the error. These are access settings,
not additional environment variables. This plugin requires no separate S3 key
or bucket environment variable; reuse AWS credentials and accept the bucket as
a task parameter. Rerun the affected bucket or listing probe.

### Redshift access and SQL configuration

Reuse the AWS variables above. For missing targets, request the region, cluster
identifier or serverless workgroup name, database name, and intended supported
authentication method. A secret ARN or database user may be needed for that
method; secret values belong outside chat. This plugin does not define
`REDSHIFT_*` environment variables, and setting invented ones will not configure
the MCP connection. Pass known target details to the AWS API calls.

For access-denied errors, name the actual denied operation and corresponding
permission when known, such as `redshift:DescribeClusters`,
`redshift-serverless:ListWorkgroups`, `redshift-serverless:GetWorkgroup`, or
`redshift-data:ExecuteStatement`, `redshift-data:DescribeStatement`, or
`redshift-data:GetStatementResult`.
Data API authentication may additionally require access to the chosen Secrets
Manager secret or Redshift temporary database credentials, depending on the
method. Use the [ExecuteStatement authentication documentation](https://docs.aws.amazon.com/redshift-data/latest/APIReference/API_ExecuteStatement.html)
when resolving method-specific parameters and permissions. Suggest only the permissions implicated by the chosen method and error;
avoid blanket administrator access. Verify the database login's access when SQL
authentication fails. Rerun the API probe and `SELECT 1` after the relevant fix.
