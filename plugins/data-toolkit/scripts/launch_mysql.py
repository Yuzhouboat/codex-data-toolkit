#!/usr/bin/env python3
"""Apply MySQL defaults, then replace this process with the pinned MCP server."""

import os
import shutil
import sys

MYSQL_SERVER = "@toolbox-sdk/server@1.16.0"


def launch():
    required = ("MYSQL_DATABASE", "MYSQL_USER", "MYSQL_PASSWORD")
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        print("Data Toolkit: missing " + ", ".join(missing), file=sys.stderr)
        return 2
    executable = shutil.which("npx")
    if executable is None:
        print("Data Toolkit: npx is required for MySQL; install Node.js.", file=sys.stderr)
        return 2
    environment = os.environ.copy()
    environment["MYSQL_HOST"] = environment.get("MYSQL_HOST") or "localhost"
    environment["MYSQL_PORT"] = environment.get("MYSQL_PORT") or "3306"
    os.execve(executable, [executable, "-y", MYSQL_SERVER, "--prebuilt", "mysql", "--stdio"], environment)


if __name__ == "__main__":
    sys.exit(launch())
