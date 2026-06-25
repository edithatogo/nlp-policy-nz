"""Tests for Track 14 benchmark script contracts."""

from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pytest

ROOT = Path(__file__).resolve().parents[1]
WORKDIR = ROOT / ".tmp" / "track14-tests"
sys.path.insert(0, str(ROOT / "scripts"))

benchmark_msgspec = importlib.import_module("benchmark_msgspec_orjson")
benchmark_tokenizers = importlib.import_module("benchmark_tokenizers_chunking")


def _patch_find_spec(monkeypatch: pytest.MonkeyPatch, missing: set[str]) -> None:
    """Force specific optional dependencies to appear unavailable."""
    original_find_spec = importlib.util.find_spec

    def _find_spec(name: str, package: str | None = None):
        if name in missing:
            return None
        return original_find_spec(name, package)

    monkeypatch.setattr(importlib.util, "find_spec", _find_spec)


def _evidence_path(filename: str) -> Path:
    WORKDIR.mkdir(parents=True, exist_ok=True)
    return WORKDIR / filename


def test_msgspec_orjson_benchmark_records_dependency_statuses(monkeypatch: pytest.MonkeyPatch) -> None:
    """Serializer benchmark should mark optional dependencies with explicit statuses."""
    _patch_find_spec(monkeypatch, {"orjson"})
    evidence_path = _evidence_path("track14_msgspec_orjson_benchmark.json")

    exit_code = benchmark_msgspec.main(["--records", "10", "--iterations", "2", "--evidence", str(evidence_path)])
    assert exit_code == 0

    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    results = {entry["name"]: entry["status"] for entry in payload["results"]}

    assert payload["experiment"] == "msgspec_orjson_serializer"
    assert results["stdlib_json"] == "measured"
    assert results["msgspec_json"] == "measured"
    assert results["orjson"] == "missing_dependency"


def test_tokenizers_chunking_benchmark_handles_missing_spacy_and_tokenizers(
    monkeypatch: pytest.MonkeyPatch
) -> None:
    """Tokenizers benchmark should keep writing evidence when both optional libs are missing."""
    _patch_find_spec(monkeypatch, {"spacy", "tokenizers"})
    evidence_path = _evidence_path("track14_tokenizers_chunking_benchmark.json")

    exit_code = benchmark_tokenizers.main(
        ["--records", "12", "--repeat", "2", "--iterations", "2", "--evidence", str(evidence_path)]
    )
    assert exit_code == 0

    payload = json.loads(evidence_path.read_text(encoding="utf-8"))
    results = payload["results"]

    assert results["tokenizers"]["status"] == "missing_dependency"
    assert results["spacy_sentence"]["status"] == "missing_dependency"
