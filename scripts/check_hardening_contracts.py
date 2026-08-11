"""Validate the repository-side hardening manifest without network access."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/quality/repository_hardening_manifest.json"


def validate_manifest(path: Path = MANIFEST) -> None:
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["schema_version"] == "1.0"
    assert payload["default_branch"] == "master"
    assert payload["maintainer_model"] == "solo-maintainer"
    controls = payload["controls"]
    for key in ("metamorphic", "contract", "mutation", "codeql", "dependency_review", "workflow_lint", "secret_scan"):
        assert key in controls, key
        assert controls[key]["status"] in {"implemented", "available", "available-on-demand", "not-applicable"}
    assert payload["external_controls"]["ruleset"]


if __name__ == "__main__":
    validate_manifest()
    print("hardening manifest: OK")
