from __future__ import annotations

import json
from pathlib import Path

from scripts.check_ocr_artifact_registry import check

ROOT = Path(__file__).resolve().parents[1]
OCR_PATH = ROOT / "data" / "registry" / "ocr_artifact.json"


def test_ocr_artifact_registry_contract() -> None:
    assert check() == []


def test_ocr_artifact_rejects_published_doi_pending_bypass(tmp_path: Path, monkeypatch) -> None:
    """published_* with doi_pending must not bypass the DOI/deposit requirement."""
    import scripts.check_ocr_artifact_registry as module

    payload = json.loads(OCR_PATH.read_text(encoding="utf-8"))
    payload["status"] = "published_doi_pending"
    target = tmp_path / "ocr_artifact.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(module, "REGISTRY_PATH", target)
    errors = module.check()
    assert any("published-like status requires both doi and deposit_url" in error for error in errors)


def test_ocr_artifact_requires_blockers_while_doi_pending(tmp_path: Path, monkeypatch) -> None:
    import scripts.check_ocr_artifact_registry as module

    payload = json.loads(OCR_PATH.read_text(encoding="utf-8"))
    payload["blockers"] = []
    target = tmp_path / "ocr_artifact.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(module, "REGISTRY_PATH", target)
    errors = module.check()
    assert any("blockers must be non-empty" in error for error in errors)
