from __future__ import annotations

import json
from pathlib import Path


def test_track88_gold_annotations_are_metadata_only_and_stratified() -> None:
    path = Path("data/track88/golden_annotations.json")
    payload = json.loads(path.read_text(encoding="utf-8"))

    assert payload["leakage_policy"] == "metadata-only"
    assert len(payload["strata"]) >= 4
    assert {item["layout"] for item in payload["strata"]} >= {
        "single-column",
        "multi-column",
        "table",
        "marginalia",
    }
