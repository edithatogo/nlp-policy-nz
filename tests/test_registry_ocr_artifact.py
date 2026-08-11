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


def test_ocr_artifact_requires_payload_sha256(tmp_path: Path, monkeypatch) -> None:
    import scripts.check_ocr_artifact_registry as module

    payload = json.loads(OCR_PATH.read_text(encoding="utf-8"))
    payload["status"] = "payload_complete_doi_pending"
    target = tmp_path / "ocr_artifact.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    manifest = tmp_path / "payload.json"
    manifest.write_text(
        json.dumps(
            {
                "artifact_version": payload["version"],
                "benchmark_id": payload["benchmark_id"],
                "hf_source": payload["hf_evidence"],
                "archive": {"sha256": "not-a-checksum"},
                "files": [{"path": "README.md"}],
                "scope": {"payload_policy": "metadata_only"},
            }
        ),
        encoding="utf-8",
    )
    monkeypatch.setattr(module, "REGISTRY_PATH", target)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    payload["payload_manifest_path"] = "payload.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    errors = module.check()
    assert any("SHA-256 checksum" in error for error in errors)


def test_ocr_artifact_requires_checksum_to_match_payload(tmp_path: Path, monkeypatch) -> None:
    import scripts.check_ocr_artifact_registry as module

    payload = json.loads(OCR_PATH.read_text(encoding="utf-8"))
    payload["status"] = "payload_complete_doi_pending"
    payload["checksums"] = {"sha256": "a" * 64}
    payload["payload_manifest_path"] = "payload.json"
    payload["zenodo_metadata_path"] = "metadata.json"
    (tmp_path / "payload.json").write_text(
        json.dumps(
            {
                "artifact_version": payload["version"],
                "benchmark_id": payload["benchmark_id"],
                "hf_source": payload["hf_evidence"],
                "archive": {"sha256": "b" * 64},
                "files": [{"path": "README.md"}],
                "scope": {"payload_policy": "metadata_only"},
            }
        ),
        encoding="utf-8",
    )
    (tmp_path / "metadata.json").write_text(
        json.dumps({"upload_type": "dataset", "version": payload["version"]}),
        encoding="utf-8",
    )
    target = tmp_path / "ocr_artifact.json"
    target.write_text(json.dumps(payload), encoding="utf-8")
    monkeypatch.setattr(module, "REGISTRY_PATH", target)
    monkeypatch.setattr(module, "ROOT", tmp_path)
    errors = module.check()
    assert any("checksum must match" in error for error in errors)
