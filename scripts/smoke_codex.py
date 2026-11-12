#!/usr/bin/env python3
"""Exercise Codex marketplace install/config/remove in a disposable CODEX_HOME."""

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def main():
    if not shutil.which("codex"):
        raise SystemExit("Install a Codex CLI with plugin support before running this check.")
    with tempfile.TemporaryDirectory(prefix="data-toolkit-smoke-") as folder:
        environment = dict(os.environ, CODEX_HOME=folder)

        def run(*args, decode=True):
            command = ["codex", *args]
            result = subprocess.run(command, cwd=folder, env=environment, capture_output=True, text=True, timeout=30)
            if result.returncode:
                # Normal plugin commands contain no secrets; do not print process environment.
                raise RuntimeError(f"{' '.join(command[:4])} failed: {result.stderr.strip()}")
            return json.loads(result.stdout) if decode else result.stdout

        added = run("plugin", "marketplace", "add", str(ROOT), "--json")
        assert added["marketplaceName"] == "yuzhou-data-toolkit"
        available = run("plugin", "list", "--available", "--json", "--marketplace", "yuzhou-data-toolkit")
        assert any(item["pluginId"] == "data-toolkit@yuzhou-data-toolkit" for item in available["available"])
        installed = run("plugin", "add", "data-toolkit@yuzhou-data-toolkit", "--json")
        installed_path = Path(installed["installedPath"]).resolve()
        assert installed_path.is_relative_to(Path(folder).resolve())
        assert (installed_path / "skills/check-connectors/SKILL.md").is_file()
        servers = {item["name"]: item for item in run("mcp", "list", "--json")}
        assert set(servers) == {"mysql", "aws-mcp", "github"}
        assert servers["github"]["transport"]["bearer_token_env_var"] == "GITHUB_PERSONAL_ACCESS_TOKEN"
        assert "MYSQL_PASSWORD" in servers["mysql"]["transport"]["env_vars"]
        assert "AWS_PROFILE" in servers["aws-mcp"]["transport"]["env_vars"]
        run("plugin", "remove", "data-toolkit@yuzhou-data-toolkit", decode=False)
        remaining = run("plugin", "list", "--json", "--marketplace", "yuzhou-data-toolkit")
        assert not remaining["installed"]
    print("PASS: isolated marketplace registration, discovery, install, MCP config loading, and uninstall")
    print("Live service connectivity and MCP process startup were not exercised.")


if __name__ == "__main__":
    main()
