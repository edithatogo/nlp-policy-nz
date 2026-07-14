from pathlib import Path

ROOT = Path(__file__).parents[1]


def test_cloud_ocr_workflow_has_secure_dispatch_controls() -> None:
    workflow = (ROOT / ".github/workflows/cloud-ocr-operations.yml").read_text(encoding="utf-8")
    assert "workflow_dispatch:" in workflow
    assert "id-token: write" in workflow
    assert "contents: write" not in workflow
    assert "secrets.HF_TOKEN" not in workflow
    assert "corpus" not in workflow.lower()
    assert "validate:" in workflow
    assert "plan:" in workflow
    assert "dispatch:" in workflow
    assert "collect:" in workflow
    assert "retry-and-quarantine:" in workflow
    assert "publish:" in workflow
    assert "pilot-gate:" in workflow
    assert "actions/checkout@" in workflow
    assert all(
        len(part.split("@")[1]) == 40
        for part in workflow.split()
        if part.startswith(("actions/", "astral-sh/")) and "@" in part
    )


def test_orchestrator_rejects_oversized_public_pilot(tmp_path: Path) -> None:
    import subprocess
    import sys

    result = subprocess.run(
        [
            sys.executable,
            "scripts/cloud_ocr_orchestrator.py",
            "validate",
            "--volume-limit",
            "4",
            "--output",
            str(tmp_path / "plan.json"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0


def test_orchestrator_pilot_is_explicitly_external_gate(tmp_path: Path) -> None:
    import json
    import subprocess
    import sys

    output = tmp_path / "pilot.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/cloud_ocr_orchestrator.py",
            "pilot",
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "external_gate_required"


def test_orchestrator_validate_builds_and_plan_preserves_cloud_plan(tmp_path: Path) -> None:
    import json
    import subprocess
    import sys

    item = {
        "collection_id": "hathi-nz",
        "dataset_id": "dataset-a",
        "source_id": "source-a",
        "item_id": "item-a",
        "htid": "htid-a",
        "access_class": "public_full_text",
        "acquisition_mode": "github_actions",
        "source_url": "https://example.test/item-a",
        "source_dataset_name": "seed",
        "rights_code": "public",
        "digitization_profile": "standard",
        "publish_eligibility": "public_full_text",
        "source_sha256": "a" * 64,
    }
    manifest = tmp_path / "items.json"
    manifest.write_text(json.dumps({"items": [item]}), encoding="utf-8")
    validated = tmp_path / "validated.json"
    planned = tmp_path / "planned.json"

    validate = subprocess.run(
        [
            sys.executable,
            "scripts/cloud_ocr_orchestrator.py",
            "validate",
            "--input",
            str(manifest),
            "--output",
            str(validated),
            "--run-id",
            "run-1",
            "--pipeline-version",
            "1.0.0",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert validate.returncode == 0, validate.stderr
    validated_payload = json.loads(validated.read_text(encoding="utf-8"))
    assert validated_payload["plan"]["ledger"][0]["item_id"] == "item-a"

    plan = subprocess.run(
        [
            sys.executable,
            "scripts/cloud_ocr_orchestrator.py",
            "plan",
            "--input",
            str(validated),
            "--output",
            str(planned),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert plan.returncode == 0, plan.stderr
    assert json.loads(planned.read_text(encoding="utf-8"))["plan"]["run_id"] == "run-1"


def test_orchestrator_publish_fails_closed_for_incomplete_plan(tmp_path: Path) -> None:
    import json
    import subprocess
    import sys

    source = tmp_path / "source.json"
    source.write_text(json.dumps({"plan": {"ledger": [{"state": "pending"}]}}), encoding="utf-8")
    output = tmp_path / "publish.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/cloud_ocr_orchestrator.py",
            "publish",
            "--input",
            str(source),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
