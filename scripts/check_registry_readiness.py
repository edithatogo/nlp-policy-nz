"""Check the repository-side research registry readiness contract."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.audit_huggingface_targets import check_audit_json  # noqa: E402
from scripts.check_ocr_artifact_registry import check as check_ocr_artifact  # noqa: E402
from scripts.check_ontology_submission_gate import check as check_ontology_gate  # noqa: E402


def check() -> list[str]:
    """Return registry readiness contract violations."""
    errors: list[str] = []
    doc = ROOT / "docs" / "registry-readiness.md"
    registry = ROOT / "data_registry.json"
    if not doc.exists():
        errors.append(f"missing {doc}")
    if not registry.exists():
        errors.append(f"missing {registry}")
    else:
        records = json.loads(registry.read_text(encoding="utf-8"))
        if not records or not all(record.get("dataset_id") and record.get("version") for record in records):
            errors.append("data_registry.json must contain dataset_id and version")
    if doc.exists():
        text = doc.read_text(encoding="utf-8")
        if not any(
            marker in text
            for marker in (
                "repository_ready_external_gates_pending",
                "rights_approved_external_acceptance_pending",
                "rights_approved_huggingface_metadata_verified_doi_pending",
            )
        ):
            errors.append("registry-readiness.md missing a recognized readiness status")
        for marker in ("External boundary", "#166", "#167", "#168"):
            if marker not in text:
                errors.append(f"registry-readiness.md missing {marker}")
        for artifact in (
            "data/registry/ocr_artifact.json",
            "data/registry/huggingface_audit.json",
            "data/registry/ontology_submission_gate.json",
        ):
            if artifact not in text:
                errors.append(f"registry-readiness.md missing {artifact}")

    errors.extend(check_ocr_artifact())
    errors.extend(check_audit_json())
    errors.extend(check_ontology_gate())
    return errors


if __name__ == "__main__":
    problems = check()
    if problems:
        raise SystemExit("\n".join(problems))
    sys.stdout.write("registry readiness contract: OK\n")
