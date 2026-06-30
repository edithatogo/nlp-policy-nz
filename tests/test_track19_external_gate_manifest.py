"""Track 19 external profiling and full-suite gate manifest checks."""

from __future__ import annotations

import json
from pathlib import Path

MANIFEST = Path(
    "conductor/tracks/track19_observability_benchmarks_20260613/external_gate_manifest.json"
)


def test_track19_external_gate_manifest_is_explicit() -> None:
    """Track 19 records full-suite and profiling gates as external evidence."""
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    assert manifest["track"] == 19
    assert manifest["status"] == "externally_blocked"
    assert manifest["repo_side_status"] == "benchmark_harness_complete"
    assert manifest["local_runtime_observations"]["benchmark_status"] == "unskipped_passed"
    assert (
        manifest["local_runtime_observations"]["one_gib_hansard_corpus_available_in_repo"] is False
    )

    gates = {gate["id"]: gate for gate in manifest["external_gates"]}
    assert gates["full_suite_validation"]["status"] == "satisfied"
    assert gates["scalene_one_gib_profile"]["minimum_input_bytes"] >= 1_073_741_824
    assert gates["memray_one_gib_flamegraph"]["minimum_input_bytes"] >= 1_073_741_824
    assert "input_bytes" in gates["scalene_one_gib_profile"]["required_fields"]
    assert "flamegraph_exists" in gates["memray_one_gib_flamegraph"]["required_fields"]


def test_track19_external_gate_manifest_rejects_micro_run_surrogates() -> None:
    """Bundled fixtures and benchmark JSON must not satisfy corpus profile gates."""
    manifest_text = MANIFEST.read_text(encoding="utf-8").lower()

    for rejected in ("sample fixtures", "synthetic micro-runs", "benchmark json"):
        assert rejected in manifest_text
    assert "1 gib" in manifest_text
    assert "canonical full corpus" in manifest_text
