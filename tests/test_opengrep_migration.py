"""Offline OpenGrep migration and scanner integrity contracts."""
from __future__ import annotations

import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import install_opengrep

ROOT = Path(__file__).resolve().parents[1]


class OpenGrepMigrationTests(unittest.TestCase):
    def test_reject_unexpected_binary_bytes(self):
        with tempfile.TemporaryDirectory() as folder, \
             patch.object(install_opengrep.platform, "system", return_value="Linux"), \
             patch.object(install_opengrep.platform, "machine", return_value="x86_64"), \
             patch.object(install_opengrep, "urlopen", return_value=io.BytesIO(b"untrusted")):
            with self.assertRaisesRegex(RuntimeError, "SHA-256"):
                install_opengrep.install(Path(folder))
            self.assertFalse((Path(folder) / "opengrep").exists())

    def test_pr_and_default_branch_run_qualified_scanner(self):
        workflow = (ROOT / ".github/workflows/opengrep.yml").read_text()
        self.assertIn("pull_request:", workflow)
        self.assertIn("push:", workflow)
        self.assertIn("branches: [master]", workflow)
        self.assertIn("install_opengrep.py", workflow)
        self.assertIn("--strict --error", workflow)
        self.assertIn("--config p/python --severity WARNING src/nlp_policy_nz/", workflow)
        self.assertIn('test "$observed" -eq 1', workflow)

    def test_legacy_active_semgrep_removed_but_bandit_preserved(self):
        main = (ROOT / ".github/workflows/ci.yml").read_text()
        make = (ROOT / "Makefile").read_text()
        project = (ROOT / "pyproject.toml").read_text()
        self.assertNotIn("semgrep scan", main + make)
        self.assertNotIn("pip install --user semgrep", main)
        self.assertNotIn("semgrep>=", project)
        self.assertIn("Bandit source security", main)
        self.assertIn("opengrep scan --strict --error --config p/python", make)


if __name__ == "__main__":
    unittest.main()
