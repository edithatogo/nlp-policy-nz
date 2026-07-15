from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

import scripts.cloud_ocr_worker as worker


def test_worker_emits_reviewed_publication_transitions(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = b"public pilot fixture"
    digest = hashlib.sha256(source).hexdigest()
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "plan": {
                    "work_manifest": {
                        "items": [
                            {
                                "item_id": "public-item-1",
                                "source_url": "https://example.test/public-item-1.pdf",
                                "content_address": f"sha256:{digest}",
                                "content_allowed": True,
                                "publication_decision": "public_full_text",
                            }
                        ]
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    def fake_download(_url: str, target: Path) -> str:
        target.write_bytes(source)
        return digest

    monkeypatch.setattr(worker, "_download", fake_download)
    monkeypatch.setattr(worker, "_ocr_source", lambda _source, _work: "Recognised public text.\n")
    results = tmp_path / "results.json"
    assert worker.run(plan, results, tmp_path / "output") == 0
    payload = json.loads(results.read_text(encoding="utf-8"))
    assert [row["state"] for row in payload["results"]] == ["processed", "reviewed", "published"]
    assert (tmp_path / "output" / "public-item-1.txt").is_file()


def test_worker_fails_closed_when_rights_gate_is_not_public(tmp_path: Path) -> None:
    plan = tmp_path / "plan.json"
    plan.write_text(
        json.dumps(
            {
                "plan": {
                    "work_manifest": {
                        "items": [
                            {
                                "item_id": "restricted-item",
                                "source_url": "https://example.test/restricted.pdf",
                                "content_address": "identity:restricted",
                                "content_allowed": False,
                                "publication_decision": "metadata_only",
                            }
                        ]
                    }
                }
            }
        ),
        encoding="utf-8",
    )
    results = tmp_path / "results.json"
    assert worker.run(plan, results, tmp_path / "output") == 0
    payload = json.loads(results.read_text(encoding="utf-8"))
    assert payload["results"][0]["state"] == "failed"
    assert "error_code" in payload["results"][0]
