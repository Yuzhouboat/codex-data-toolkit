#!/usr/bin/env python3
"""Validate and package an explicit set of plugin files, with no external dependencies."""

import argparse
import json
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins/data-toolkit"
PACKAGE_FILES = (
    ".codex-plugin/plugin.json",
    ".mcp.json",
    "scripts/launch_mysql.py",
    "scripts/check_prerequisites.py",
    "skills/check-connectors/SKILL.md",
    "skills/setup-data-toolkit/SKILL.md",
    "skills/setup-data-toolkit/references/setup.md",
    "skills/setup-data-toolkit/references/mlflow.md",
)


def validate(plugin=PLUGIN, catalog_path=None):
    plugin = Path(plugin)
    if plugin.is_symlink():
        raise ValueError("Plugin root must not be a symlink")
    for path in plugin.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Symlink is not allowed: {path.relative_to(plugin)}")
        if path.is_file() and "__pycache__" not in path.parts:
            if path.relative_to(plugin).as_posix() not in PACKAGE_FILES:
                raise ValueError(f"Unlisted plugin file: {path.relative_to(plugin)}")
    for rel in PACKAGE_FILES:
        path = plugin / rel
        if not path.is_file():
            raise ValueError(f"Missing package file: {rel}")
        path.read_text(encoding="utf-8")
    manifest = json.loads((plugin / ".codex-plugin/plugin.json").read_text())
    if manifest["name"] != "data-toolkit" or not re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]):
        raise ValueError("Invalid package identity or version")
    if manifest.get("skills") != "./skills/" or manifest.get("mcpServers") != "./.mcp.json":
        raise ValueError("Component paths must reference the packaged skills and MCP config")
    if "hooks" in manifest or "apps" in manifest:
        raise ValueError("This distribution must not include hooks or registered app references")
    servers = json.loads((plugin / ".mcp.json").read_text())["mcpServers"]
    if set(servers) != {"mysql", "aws-mcp", "github"}:
        raise ValueError("Expected MySQL, AWS, and GitHub connectors")
    for name, server in servers.items():
        if server.get("env") or server.get("headers") or server.get("http_headers"):
            raise ValueError(f"Inline credential values are not allowed: {name}")
        if name == "github":
            if server.get("bearer_token_env_var") != "GITHUB_PERSONAL_ACCESS_TOKEN":
                raise ValueError("GitHub must obtain its token from the environment")
        elif not isinstance(server.get("env_vars"), list):
            raise ValueError(f"Missing credential forwarding list: {name}")
    for skill in (plugin / "skills").iterdir():
        text = (skill / "SKILL.md").read_text()
        if not text.startswith("---\n"):
            raise ValueError(f"Missing skill frontmatter: {skill.name}")
        header = text.split("---", 2)[1]
        if f"name: {skill.name}\n" not in header or "\ndescription: " not in header:
            raise ValueError(f"Invalid skill discovery metadata: {skill.name}")
        for reference in re.findall(r"\]\((references/[^)]+)\)", text):
            target = (skill / reference).resolve()
            if not target.is_relative_to(plugin.resolve()) or not target.is_file():
                raise ValueError(f"Broken skill reference: {reference}")
    if catalog_path is not None:
        catalog_path = Path(catalog_path)
        catalog = json.loads(catalog_path.read_text())
        entry, = catalog["plugins"]
        source_path = entry["source"]["path"]
        root = catalog_path.parents[2].resolve()
        target = (root / source_path).resolve()
        if not source_path.startswith("./") or not target.is_relative_to(root) or target != plugin.resolve():
            raise ValueError("Marketplace path must resolve to this plugin within the repo")
        if entry["name"] != manifest["name"]:
            raise ValueError("Marketplace and plugin names disagree")
        if entry["policy"] != {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}:
            raise ValueError("Unexpected marketplace policy")
    return manifest


def build(destination, plugin=PLUGIN):
    manifest = validate(plugin)
    destination = Path(destination)
    if destination.resolve().is_relative_to(Path(plugin).resolve()):
        raise ValueError("Build output must be outside the plugin source")
    destination.parent.mkdir(parents=True, exist_ok=True)
    with ZipFile(destination, "w", compression=ZIP_DEFLATED) as archive:
        for rel in sorted(PACKAGE_FILES):
            info = ZipInfo(rel, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            archive.writestr(info, (Path(plugin) / rel).read_bytes())
    return manifest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Validate without creating a ZIP")
    args = parser.parse_args()
    try:
        manifest = validate(catalog_path=ROOT / ".agents/plugins/marketplace.json")
        if args.check:
            print(f"Validated {manifest['name']} {manifest['version']} ({len(PACKAGE_FILES)} files)")
        else:
            output = ROOT / "dist" / f"{manifest['name']}-{manifest['version']}.zip"
            build(output)
            print(output)
    except (ValueError, KeyError, OSError) as error:
        parser.exit(1, f"Package error: {error}\n")


if __name__ == "__main__":
    main()
