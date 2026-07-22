from __future__ import annotations

import json
from pathlib import Path

AUDIT = Path("data/registry/huggingface_audit.json")


def test_huggingface_audit_is_immutable_and_external_gated() -> None:
    value = json.loads(AUDIT.read_text(encoding="utf-8"))

    assert value["status"] == "rights-approved-external-acceptance-pending"
    assert value["rights_approval"]["status"] == "approved"
    assert value["rights_approval"]["scope"]
    assert len(value["targets"]) == 3
    assert all(len(target["revision"]) == 40 for target in value["targets"])
    assert all(target["private"] is False for target in value["targets"])
    assert len(value["blockers"]) >= 3


def test_huggingface_audit_preserves_card_metadata_distinctions() -> None:
    targets = {
        target["repo_id"]: target
        for target in json.loads(AUDIT.read_text(encoding="utf-8"))["targets"]
    }

    assert targets["edithatogo/corpus-legislation-nz"]["card_license"] == "other"
    assert targets["edithatogo/nz-hansard-corpus"]["card_license"] == "mit"
    assert targets["edithatogo/nlp-policy-nz-cloud-ocr-pilots"]["card_license"] is None
