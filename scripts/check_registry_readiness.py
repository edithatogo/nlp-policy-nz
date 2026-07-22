"""Check the repository-side research registry readiness contract."""

from pathlib import Path
import json


ROOT = Path(__file__).resolve().parents[1]


def check() -> list[str]:
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
    return errors


if __name__ == "__main__":
    problems = check()
    if problems:
        raise SystemExit("\n".join(problems))
    print("registry readiness contract: OK")
