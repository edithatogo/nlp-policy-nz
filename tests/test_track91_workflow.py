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
    assert "worker_image:" in workflow
    assert "docker run --rm" in workflow
    assert "--results .tmp/cloud-ocr/worker-results.json" in workflow
    assert "secrets.CLOUD_OCR_SIGNING_KEY" in workflow
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


def test_orchestrator_pilot_passes_completed_unquarantined_plan(tmp_path: Path) -> None:
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
    plan = tmp_path / "plan.json"
    assert subprocess.run(
        [
            sys.executable,
            "scripts/cloud_ocr_orchestrator.py",
            "validate",
            "--input",
            str(manifest),
            "--output",
            str(plan),
            "--run-id",
            "pilot-1",
        ],
        cwd=ROOT,
        check=False,
    ).returncode == 0
    payload = json.loads(plan.read_text(encoding="utf-8"))
    payload["plan"]["ledger"][0]["state"] = "published"
    plan.write_text(json.dumps(payload), encoding="utf-8")
    output = tmp_path / "pilot.json"
    result = subprocess.run(
        [
            sys.executable,
            "scripts/cloud_ocr_orchestrator.py",
            "pilot",
            "--input",
            str(plan),
            "--output",
            str(output),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert json.loads(output.read_text(encoding="utf-8"))["status"] == "passed"


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


def test_orchestrator_enforces_volume_limit(tmp_path: Path) -> None:
    import json
    import subprocess
    import sys

    items = []
    for index in range(4):
        items.append(
            {
                "collection_id": "hathi-nz",
                "dataset_id": "dataset-a",
                "source_id": f"source-{index}",
                "item_id": f"item-{index}",
                "htid": f"htid-{index}",
                "access_class": "public_full_text",
                "acquisition_mode": "github_actions",
                "source_url": f"https://example.test/item-{index}",
                "source_dataset_name": "seed",
                "rights_code": "public",
                "digitization_profile": "standard",
                "publish_eligibility": "public_full_text",
                "source_sha256": "a" * 64,
            }
        )
    manifest = tmp_path / "items.json"
    manifest.write_text(json.dumps({"items": items}), encoding="utf-8")
    result = subprocess.run(
        [
            sys.executable,
            "scripts/cloud_ocr_orchestrator.py",
            "validate",
            "--input",
            str(manifest),
            "--output",
            str(tmp_path / "plan.json"),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "volume limit" in result.stderr


def test_orchestrator_collects_worker_states_and_signs_published_report(tmp_path: Path) -> None:
    import json
    import os
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
    collected = tmp_path / "collected.json"
    report = tmp_path / "run-report.json"
    results = tmp_path / "results.json"
    results.write_text(
        json.dumps(
            {
                "results": [
                    {"item_id": "item-a", "state": "processed", "output_digest": "sha256:" + "b" * 64},
                    {"item_id": "item-a", "state": "reviewed"},
                    {"item_id": "item-a", "state": "published"},
                ]
            }
        ),
        encoding="utf-8",
    )
    base = [
        sys.executable,
        "scripts/cloud_ocr_orchestrator.py",
        "validate",
        "--input",
        str(manifest),
        "--output",
        str(validated),
        "--run-id",
        "run-1",
    ]
    assert subprocess.run(base, cwd=ROOT, check=False).returncode == 0
    collect = subprocess.run(
        [
            sys.executable,
            "scripts/cloud_ocr_orchestrator.py",
            "collect",
            "--input",
            str(validated),
            "--results",
            str(results),
            "--output",
            str(collected),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert collect.returncode == 0, collect.stderr
    env = os.environ.copy()
    env["CLOUD_OCR_SIGNING_KEY"] = "test-key"
    publish = subprocess.run(
        [
            sys.executable,
            "scripts/cloud_ocr_orchestrator.py",
            "publish",
            "--input",
            str(collected),
            "--output",
            str(report),
        ],
        cwd=ROOT,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    assert publish.returncode == 0, publish.stderr
    assert json.loads(report.read_text(encoding="utf-8"))["status"] == "complete"
