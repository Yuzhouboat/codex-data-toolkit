# Optional MLflow CLI tracing

MLflow tracing is a separate opt-in Codex CLI configuration. This package ships no
lifecycle hooks and never selects a tracking service automatically. Conversation content
may be uploaded to the selected tracking server after completed CLI turns. Confirm the
user's chosen tracking URI and experiment ID before applying the requested setup.

This follows the original toolkit's `@mlflow/codex` notify integration. Compatibility
must be checked with the installed Codex CLI and MLflow package. It is not a guarantee
of desktop or web conversation tracing.

When configuring, inspect the project's `.codex/config.toml` for an existing root-level
`notify` key. Preserve it and explain the conflict instead of replacing another handler.
Otherwise add the following at the root, before any table headings:

```toml
notify = ["npx", "-y", "@mlflow/codex@latest", "notify-hook"]
```

Create `.codex/mlflow-tracing.json` with the user's chosen values:

```json
{
  "trackingUri": "https://YOUR-MLFLOW-HOST",
  "experimentId": "YOUR-EXPERIMENT-ID"
}
```

The example values are placeholders. Preserve an existing tracing file and resolve
differences with the user. The original integration uses @latest; resolve and pin a tested
package version when preparing production tracing. Keep authentication in the launch
environment, for example MLFLOW_TRACKING_USERNAME and MLFLOW_TRACKING_PASSWORD when
supported by the tracking server. Restart Codex from that environment and trust the project.

To disable tracing, remove only the notify entry installed for this integration. Remove
the tracing JSON only if it belongs to this setup and the user wants it removed. Uninstalling
the plugin does not remove separately configured tracing.

Validate edited TOML/JSON and report configuration separately from remote experiment
access and observed trace uploads. A connection check must not create a trace for testing.
