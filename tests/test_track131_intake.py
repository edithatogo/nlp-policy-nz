import hashlib
import json
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_track131_intake.py"


def _write(root: Path, name: str, content: bytes) -> str:
    path = root / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    return hashlib.sha256(content).hexdigest()


def _manifest(root: Path) -> dict:
    image_hash = _write(root, "pages/p001.png", b"synthetic image fixture")
    annotation_hash = _write(root, "gold/p001.json", b'{"page_id":"p001","tokens":[]}')
    rights_hash = _write(root, "rights/clearance.txt", b"synthetic rights evidence")
    sbom_hash = _write(root, "runtime/sbom.json", b'{"bomFormat":"CycloneDX"}')
    license_hash = _write(root, "runtime/LICENSE.txt", b"synthetic license record")
    return {
        "schema_version": "track131-intake-v1",
        "dataset_id": "test-intake",
        "rights": {"status": "cleared", "basis": "test fixture", "evidence_path": "rights/clearance.txt", "evidence_sha256": rights_hash, "reviewer": "test", "reviewed_at": "2026-01-01"},
        "pages": [{"page_id": "p001", "source_id": "source-1", "sequence": 1, "image_path": "pages/p001.png", "image_sha256": image_hash, "mime_type": "image/png", "width": 100, "height": 200, "rights_evidence_ref": "rights/clearance.txt", "gold_annotation_path": "gold/p001.json", "gold_annotation_sha256": annotation_hash}],
        "runtime": {"engine": {"name": "fixture-engine", "version": "1.0.0", "source_commit": "a" * 40, "license_spdx": "MIT"}, "model": {"name": "fixture-model", "version": "1.0.0", "digest": "sha256:" + "b" * 64}, "container": {"image": "fixture/image", "digest": "sha256:" + "c" * 64}, "sbom": {"path": "runtime/sbom.json", "sha256": sbom_hash, "format": "cyclonedx-json"}, "licenses": [{"component": "fixture-engine", "version": "1.0.0", "spdx_id": "MIT", "source_path": "runtime/LICENSE.txt", "source_sha256": license_hash}]},
        "runner": {"provider": "test", "workflow_ref": "org/repo/.github/workflows/ocr.yml@" + "d" * 40, "no_cost": True, "quota_policy": "fixture quota", "paid_fallback": False},
    }


def _run(root: Path, manifest: dict):
    manifest_path = root / "intake.json"
    report_path = root / "report.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return subprocess.run([sys.executable, str(SCRIPT), "--manifest", str(manifest_path), "--root", str(root), "--report", str(report_path)], capture_output=True, text=True, check=False), report_path


def test_valid_intake_passes_and_writes_report(tmp_path: Path):
    result, report_path = _run(tmp_path, _manifest(tmp_path))
    assert result.returncode == 0
    assert json.loads(report_path.read_text(encoding="utf-8"))["passed"] is True


def test_hash_mismatch_fails_closed_and_reports(tmp_path: Path):
    manifest = _manifest(tmp_path)
    manifest["pages"][0]["image_sha256"] = "0" * 64
    result, report_path = _run(tmp_path, manifest)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert result.returncode == 1
    assert report["passed"] is False
    assert any("SHA-256 mismatch" in error for error in report["errors"])


def test_paid_runner_and_missing_pin_fail_closed(tmp_path: Path):
    manifest = _manifest(tmp_path)
    manifest["runner"]["no_cost"] = False
    del manifest["runtime"]["container"]["digest"]
    result, report_path = _run(tmp_path, manifest)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert result.returncode == 1
    assert report["passed"] is False
    assert any("no_cost" in error for error in report["errors"])
    assert any("container.digest" in error for error in report["errors"])


def test_path_escape_fails_closed(tmp_path: Path):
    manifest = _manifest(tmp_path)
    manifest["rights"]["evidence_path"] = "../outside.txt"
    result, report_path = _run(tmp_path, manifest)
    report = json.loads(report_path.read_text(encoding="utf-8"))
    assert result.returncode == 1
    assert report["passed"] is False
    assert any("escapes bundle root" in error for error in report["errors"])
