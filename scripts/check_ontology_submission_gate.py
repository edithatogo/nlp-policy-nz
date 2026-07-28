"""Check the ontology submission gate contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GATE_PATH = ROOT / "data" / "registry" / "ontology_submission_gate.json"
ACCEPTANCE_LIKE_MARKERS = ("accepted", "registered", "submitted", "approved", "published")


def check() -> list[str]:
    """Return ontology submission gate violations."""
    errors: list[str] = []
    if not GATE_PATH.exists():
        errors.append(f"missing {GATE_PATH}")
        return errors

    gate = json.loads(GATE_PATH.read_text(encoding="utf-8"))
    if gate.get("schema_version") != "registry-ontology-submission-gate-v1":
        errors.append("ontology_submission_gate.json schema_version mismatch")

    submission_status = str(gate.get("submission_status", ""))
    registry_response = gate.get("registry_response")
    if submission_status == "no_submission" and registry_response is not None:
        errors.append("ontology submission_status no_submission requires registry_response null")

    status_lower = submission_status.lower()
    if any(marker in status_lower for marker in ACCEPTANCE_LIKE_MARKERS) and registry_response is None:
        errors.append("ontology submission_status implies acceptance but registry_response is null")

    for rel_path in gate.get("candidate_artifacts", []):
        if not (ROOT / rel_path).exists():
            errors.append(f"ontology candidate artifact missing: {rel_path}")

    namespace = gate.get("namespace")
    candidates_path = ROOT / "data" / "ontologies" / "nz_ontology_candidates.json"
    if namespace and candidates_path.exists():
        candidates = json.loads(candidates_path.read_text(encoding="utf-8"))
        concepts = candidates.get("concepts", [])
        if not concepts:
            errors.append("nz_ontology_candidates.json has no concepts for namespace spot-check")
        else:
            first_uri = concepts[0].get("uri")
            if not first_uri or not str(first_uri).startswith(namespace):
                errors.append("ontology namespace does not match first concept uri prefix")

    return errors


if __name__ == "__main__":
    problems = check()
    if problems:
        raise SystemExit("\n".join(problems))
    sys.stdout.write("ontology submission gate: OK\n")
