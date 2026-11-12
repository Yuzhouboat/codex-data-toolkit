import contextlib
import importlib.util
import io
import json
import os
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


package = module("package_plugin", ROOT / "scripts/package_plugin.py")
launcher = module("launch_mysql", package.PLUGIN / "scripts/launch_mysql.py")
prerequisites = module("check_prerequisites", package.PLUGIN / "scripts/check_prerequisites.py")


class PackagingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.plugin = self.root / "plugins/data-toolkit"
        shutil.copytree(package.PLUGIN, self.plugin, ignore=shutil.ignore_patterns("__pycache__"))
        self.catalog = self.root / ".agents/plugins/marketplace.json"
        self.catalog.parent.mkdir(parents=True)
        shutil.copyfile(ROOT / ".agents/plugins/marketplace.json", self.catalog)

    def test_marketplace_resolves_and_zip_is_reproducible(self):
        package.validate(self.plugin, self.catalog)
        first, second = self.root / "first.zip", self.root / "second.zip"
        package.build(first, self.plugin)
        package.build(second, self.plugin)
        self.assertEqual(first.read_bytes(), second.read_bytes())
        with ZipFile(first) as archive:
            self.assertEqual(set(archive.namelist()), set(package.PACKAGE_FILES))
            self.assertEqual(json.loads(archive.read(".codex-plugin/plugin.json"))["name"], "data-toolkit")

    def test_unlisted_secrets_cannot_be_packaged(self):
        (self.plugin / ".env").write_text("PASSWORD=secret")
        with self.assertRaisesRegex(ValueError, "Unlisted"):
            package.build(self.root / "release.zip", self.plugin)
        self.assertFalse((self.root / "release.zip").exists())

    def test_branding_reference_must_be_packaged(self):
        path = self.plugin / ".codex-plugin/plugin.json"
        data = json.loads(path.read_text())
        data["interface"]["logo"] = "./assets/missing.svg"
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "Unpackaged presentation reference: logo"):
            package.validate(self.plugin)

    def test_symlink_cannot_exfiltrate_an_external_file(self):
        secret = self.root / "secret"
        secret.write_text("secret")
        target = self.plugin / "scripts/launch_mysql.py"
        target.unlink()
        target.symlink_to(secret)
        with self.assertRaisesRegex(ValueError, "Symlink"):
            package.build(self.root / "release.zip", self.plugin)

    def test_marketplace_cannot_escape_repo(self):
        data = json.loads(self.catalog.read_text())
        data["plugins"][0]["source"]["path"] = "../external-plugin"
        self.catalog.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "Marketplace path"):
            package.validate(self.plugin, self.catalog)

    def test_inline_authentication_is_rejected(self):
        path = self.plugin / ".mcp.json"
        data = json.loads(path.read_text())
        data["mcpServers"]["github"]["http_headers"] = {"Authorization": "Bearer secret"}
        path.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, "Inline credential"):
            package.validate(self.plugin)


class LauncherTests(unittest.TestCase):
    def test_missing_credentials_do_not_start_a_server_or_print_secrets(self):
        error = io.StringIO()
        with patch.dict(os.environ, {"MYSQL_PASSWORD": "secret-value"}, clear=True), patch.object(launcher.os, "execve") as execute, contextlib.redirect_stderr(error):
            self.assertEqual(launcher.launch(), 2)
            execute.assert_not_called()
        self.assertIn("MYSQL_DATABASE", error.getvalue())
        self.assertNotIn("secret-value", error.getvalue())

    def test_defaults_and_credentials_are_forwarded_without_shell_interpolation(self):
        environment = {"MYSQL_DATABASE": "example", "MYSQL_USER": "example", "MYSQL_PASSWORD": "$(not-a-shell-command)"}
        with patch.dict(os.environ, environment, clear=True), patch.object(launcher.shutil, "which", return_value="/usr/bin/npx"), patch.object(launcher.os, "execve") as execute:
            launcher.launch()
        executable, args, forwarded = execute.call_args.args
        self.assertEqual(executable, "/usr/bin/npx")
        self.assertEqual(args, [executable, "-y", "@toolbox-sdk/server@1.16.0", "--prebuilt", "mysql", "--stdio"])
        self.assertEqual(forwarded["MYSQL_HOST"], "localhost")
        self.assertEqual(forwarded["MYSQL_PORT"], "3306")
        self.assertEqual(forwarded["MYSQL_PASSWORD"], environment["MYSQL_PASSWORD"])
        self.assertNotIn(environment["MYSQL_PASSWORD"], args)

    def test_custom_connection_is_preserved(self):
        environment = {"MYSQL_DATABASE": "example", "MYSQL_USER": "example", "MYSQL_PASSWORD": "secret", "MYSQL_HOST": "db.internal", "MYSQL_PORT": "3307"}
        with patch.dict(os.environ, environment, clear=True), patch.object(launcher.shutil, "which", return_value="/usr/bin/npx"), patch.object(launcher.os, "execve") as execute:
            launcher.launch()
        self.assertEqual(execute.call_args.args[2]["MYSQL_HOST"], "db.internal")
        self.assertEqual(execute.call_args.args[2]["MYSQL_PORT"], "3307")

    def test_prerequisite_report_contains_no_environment_values(self):
        with patch.dict(os.environ, {"MYSQL_PASSWORD": "sentinel-secret", "GITHUB_PERSONAL_ACCESS_TOKEN": "sentinel-token"}, clear=True):
            result = prerequisites.report()
        self.assertEqual(result["environment"]["MYSQL_PASSWORD"], "set")
        self.assertEqual(result["environment"]["MYSQL_DATABASE"], "unset")
        self.assertNotIn("sentinel-", json.dumps(result))


if __name__ == "__main__":
    unittest.main()
