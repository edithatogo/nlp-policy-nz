"""Track 44 data-quality monitoring contract tests."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path


def _run_py311(script: str, cwd: Path) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    src_path = str(cwd / "src")
    env["PYTHONPATH"] = (
        f"{src_path}{os.pathsep}{env['PYTHONPATH']}" if env.get("PYTHONPATH") else src_path
    )
    return subprocess.run(
        ["pixi", "run", "-e", "py311", "python", "-c", script],
        cwd=cwd,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def test_track44_validation_and_quality_report(tmp_path: Path) -> None:
    """Validation should accept well-formed inputs and quality reports should persist."""
    script = f"""
from pathlib import Path
import json
from nlp_policy_nz.quality import (
    build_quality_report,
    load_quality_report,
    persist_quality_report,
    validate_ingestion_input,
)
from nlp_policy_nz.storage import PipelineRecord

base = Path({json.dumps(str(tmp_path))})
xml_path = base / "sample.xml"
xml_path.write_text("<root><item>hello</item></root>", encoding="utf-8")
jsonl_path = base / "sample.jsonl"
jsonl_path.write_text('{{"doc_id": "1", "text": "ok"}}\\n', encoding="utf-8")
invalid_path = base / "broken.jsonl"
invalid_path.write_text('{{"doc_id": "1"}}\\nnot-json\\n', encoding="utf-8")
html_path = base / "sample.html"
html_path.write_text("<html><body><article>ok</article></body></html>", encoding="utf-8")
plain_html_path = base / "plain.html"
plain_html_path.write_text("just some text", encoding="utf-8")

valid_xml = validate_ingestion_input(xml_path)
valid_jsonl = validate_ingestion_input(jsonl_path)
invalid = validate_ingestion_input(invalid_path)
valid_html = validate_ingestion_input(html_path)
invalid_html = validate_ingestion_input(plain_html_path)

record = PipelineRecord(
    doc_id="doc-1",
    corpus_source="hansard",
    raw_text="Kia ora māori policy",
    cleaned_tokens=["Kia", "ora", "māori", "policy"],
    nz_act_citations=["Example Act 2026"],
    te_reo_terms=["māori"],
    embeddings=None,
    resolved_entities=[{{"entity": "Māori", "confidence": 0.95}}],
    arguments=[],
    amendments=[],
)
report = build_quality_report(
    [record],
    source_paths=(xml_path,),
    validation_results=(valid_xml,),
)
report_path = persist_quality_report(report, base / "latest.quality.json")
persisted = load_quality_report(report_path)

print(json.dumps({{
    "valid_xml": valid_xml.valid,
    "valid_jsonl": valid_jsonl.valid,
    "valid_html": valid_html.valid,
    "jsonl_records": valid_jsonl.record_count,
    "invalid": invalid.valid,
    "invalid_issue_codes": [issue.code for issue in invalid.issues],
    "invalid_html": invalid_html.valid,
    "invalid_html_issue_codes": [issue.code for issue in invalid_html.issues],
    "record_count": report.summary["record_count"],
    "quality_score": report.summary["quality_score"],
    "persisted_run_id": persisted.run_id,
    "report_exists": report_path.is_file(),
}}))
"""

    result = _run_py311(script, _repo_root())
    assert result.returncode == 0, result.stderr

    payload = json.loads(result.stdout.strip())
    assert payload["valid_xml"] is True
    assert payload["valid_jsonl"] is True
    assert payload["valid_html"] is True
    assert payload["jsonl_records"] == 1
    assert payload["invalid"] is False
    assert "jsonl_parse_failure" in payload["invalid_issue_codes"]
    assert payload["invalid_html"] is False
    assert "html_parse_failure" in payload["invalid_html_issue_codes"]
    assert payload["record_count"] == 1
    assert payload["quality_score"] > 0
    assert payload["persisted_run_id"]
    assert payload["report_exists"] is True


def test_track44_pipeline_validation_runs_before_processing(tmp_path: Path) -> None:
    """Process invocation should stop when pre-ingestion validation fails."""
    script = f"""
from pathlib import Path
from nlp_policy_nz.pipeline_api import process_legislation
import nlp_policy_nz.pipeline_api as pipeline_api
from nlp_policy_nz.quality import IngestionIssue, IngestionValidationResult

input_path = Path({json.dumps(str(tmp_path / "broken.xml"))})
output_path = Path({json.dumps(str(tmp_path / "output.parquet"))})
input_path.write_text("<root></root>", encoding="utf-8")

validation = (
    IngestionValidationResult(
        path=str(input_path),
        file_format="xml",
        valid=False,
        issue_count=1,
        issues=(IngestionIssue(code="xml_parse_failure", message="broken"),),
    ),
)

pipeline_api.validate_ingestion_inputs = lambda _paths: validation
pipeline_api.create_nlp_pipeline = lambda: (_ for _ in ()).throw(
    AssertionError("processing should not run when validation fails")
)

try:
    process_legislation(input_path, output_path)
except ValueError:
    raise SystemExit(0)
raise SystemExit(1)
"""

    result = _run_py311(script, _repo_root())
    assert result.returncode == 0, result.stderr


def test_track44_span_attributes_and_cli_report(tmp_path: Path) -> None:
    """Batch reports should be serialisable, traceable, and available via the CLI."""
    parquet_path = tmp_path / "sample.parquet"
    dashboard_path = tmp_path / "dashboard.html"
    report_path = tmp_path / "latest.quality.json"
    history_dir = tmp_path / "runs"

    script = f"""
import json
from pathlib import Path
from nlp_policy_nz.quality import build_quality_report, register_quality_span_attributes
from nlp_policy_nz.quality import monitoring
from nlp_policy_nz.storage import PipelineRecord, serialize_to_parquet

parquet_path = Path({json.dumps(str(parquet_path))})
record = PipelineRecord(
    doc_id="doc-1",
    corpus_source="hansard",
    raw_text="Kia ora māori policy",
    cleaned_tokens=["Kia", "ora", "māori", "policy"],
    nz_act_citations=["Example Act 2026"],
    te_reo_terms=["māori"],
    embeddings=None,
    resolved_entities=[{{"entity": "Māori", "confidence": 0.95}}],
    arguments=[],
    amendments=[],
)
serialize_to_parquet([record], parquet_path)

captured = {{}}

def _capture_attr(key: str, value: object) -> None:
    captured[key] = value

monitoring.set_span_attribute = _capture_attr
report = build_quality_report([record], source_paths=(parquet_path,))
register_quality_span_attributes(report)

print(json.dumps({{
    "parquet_exists": parquet_path.is_file(),
    "record_count": report.summary["record_count"],
    "quality_score": report.summary["quality_score"],
    "captured": captured,
}}))
"""

    result = _run_py311(script, _repo_root())
    assert result.returncode == 0, result.stderr
    payload = json.loads(result.stdout.strip())
    assert payload["parquet_exists"] is True
    assert payload["record_count"] == 1
    assert payload["quality_score"] > 0
    assert payload["captured"]["quality.record_count"] == 1
    assert payload["captured"]["quality.quality_score"] > 0

    report_run = _run_py311(
        f"""
from pathlib import Path
from nlp_policy_nz.cli.main import main

raise SystemExit(main([
    "quality",
    "report",
    "--parquet",
    {json.dumps(str(parquet_path))},
    "--output",
    {json.dumps(str(report_path))},
    "--history-dir",
    {json.dumps(str(history_dir))},
]))
""",
        _repo_root(),
    )
    assert report_run.returncode == 0, report_run.stderr
    assert report_path.is_file()
    assert list(history_dir.glob("*.json"))

    dashboard_run = _run_py311(
        f"""
from nlp_policy_nz.cli.main import main

raise SystemExit(main([
    "quality",
    "dashboard",
    "--history-dir",
    {json.dumps(str(history_dir))},
    "--output",
    {json.dumps(str(dashboard_path))},
]))
""",
        _repo_root(),
    )
    assert dashboard_run.returncode == 0, dashboard_run.stderr
    assert "Data Quality Dashboard" in dashboard_path.read_text(encoding="utf-8")
