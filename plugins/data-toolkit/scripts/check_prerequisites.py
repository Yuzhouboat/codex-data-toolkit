#!/usr/bin/env python3
"""Report local setup without network requests or disclosing environment values."""

import json
import os
import shutil

VARIABLES = (
    "MYSQL_HOST", "MYSQL_PORT", "MYSQL_DATABASE", "MYSQL_USER", "MYSQL_PASSWORD",
    "GITHUB_PERSONAL_ACCESS_TOKEN", "AWS_PROFILE", "AWS_REGION", "AWS_DEFAULT_REGION",
    "AWS_ACCESS_KEY_ID", "AWS_SECRET_ACCESS_KEY", "AWS_SESSION_TOKEN",
    "MLFLOW_TRACKING_URI", "MLFLOW_EXPERIMENT_ID", "MLFLOW_TRACKING_USERNAME",
    "MLFLOW_TRACKING_PASSWORD",
)


def report():
    return {
        "executables": {name: bool(shutil.which(name)) for name in ("python3", "node", "npx", "uvx")},
        "environment": {name: "set" if os.environ.get(name) else "unset" for name in VARIABLES},
        "notes": [
            "Presence checks only; service connectivity and runtime versions are untested.",
            "AWS can use profiles, SSO, or the default credential chain without exported keys.",
            "This terminal environment may differ from the running Codex process.",
            "MLflow tracing is optional and is not enabled by installing this plugin.",
        ],
    }


if __name__ == "__main__":
    print(json.dumps(report(), indent=2))
