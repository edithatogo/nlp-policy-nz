"""Contract tests for the isolated spaCy compatibility probe."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from scripts.spacy4_compatibility_spike import build_report, main


def test_probe_report_is_deterministic_for_the_same_runtime() -> None:
    first = build_report()
    second = build_report()

    assert first["experiment"] == "spacy4_compatibility_spike"
    assert first["experiment"] == second["experiment"]
    assert first["tokenization"] == second["tokenization"]
    assert first["entities"] == second["entities"]
    assert first["serialization"] == second["serialization"]
    assert first["benchmark"]["deterministic"] is True
    assert "runtime" in first
    assert "compatibility" in first


def test_probe_cli_writes_json_without_optional_transformers(tmp_path: Path) -> None:
    output = tmp_path / "spacy4.json"
    assert main(["--output", str(output)]) == 0
    payload = json.loads(output.read_text(encoding="utf-8"))

    assert payload["experiment"] == "spacy4_compatibility_spike"
    assert payload["runtime"]["python"] == ".".join(map(str, sys.version_info[:3]))
    assert payload["compatibility"]["transformers"]["status"] in {
        "available",
        "missing_dependency",
        "import_error",
    }
