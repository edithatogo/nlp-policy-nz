"""Data quality monitoring helpers for pipeline validation and drift detection."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from statistics import fmean
from typing import Any, Final, Literal, cast

from bs4 import BeautifulSoup

from nlp_policy_nz.storage import PipelineRecord
from nlp_policy_nz.telemetry import set_span_attribute

ValidationSeverity = Literal["info", "warning", "error"]

SUPPORTED_INGESTION_SUFFIXES: Final[dict[str, str]] = {
    ".xml": "xml",
    ".html": "html",
    ".htm": "html",
    ".jsonl": "jsonl",
    ".txt": "text",
}
DEFAULT_DRIFT_THRESHOLDS: Final[dict[str, float]] = {
    "average_token_count": 0.25,
    "average_entity_density": 0.35,
    "average_macron_integrity": 0.15,
    "average_completeness": 0.15,
    "quality_score": 0.15,
    "parse_success_rate": 0.10,
}


def _utc_now() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if hasattr(value, "to_dict"):
        return value.to_dict()
    return value


def _macron_ratio(texts: list[str]) -> float:
    if not texts:
        return 1.0
    accent_words = sum(1 for text in texts if any(char in text for char in "āēīōūĀĒĪŌŪ"))
    return accent_words / len(texts)


def _is_present(value: object) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    return True


@dataclass(frozen=True, slots=True)
class IngestionIssue:
    """Structured issue raised by input validation."""

    code: str
    message: str
    severity: ValidationSeverity = "error"

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
        }


@dataclass(frozen=True, slots=True)
class IngestionValidationResult:
    """Result of validating a single input file."""

    path: str
    file_format: str
    valid: bool
    issue_count: int
    issues: tuple[IngestionIssue, ...] = ()
    record_count: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "path": self.path,
            "file_format": self.file_format,
            "valid": self.valid,
            "issue_count": self.issue_count,
            "issues": [issue.to_dict() for issue in self.issues],
            "record_count": self.record_count,
        }


@dataclass(frozen=True, slots=True)
class RecordQualityMetrics:
    """Quality metrics for one PipelineRecord."""

    doc_id: str
    corpus_source: str
    token_count: int
    completeness: float
    parse_success: float
    entity_density: float
    macron_integrity: float
    quality_score: float

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.doc_id,
            "corpus_source": self.corpus_source,
            "token_count": self.token_count,
            "completeness": self.completeness,
            "parse_success": self.parse_success,
            "entity_density": self.entity_density,
            "macron_integrity": self.macron_integrity,
            "quality_score": self.quality_score,
        }


@dataclass(frozen=True, slots=True)
class DriftSignal:
    """A single drift comparison between a baseline and the current run."""

    metric: str
    baseline: float
    current: float
    delta: float
    relative_change: float | None
    threshold: float
    drifted: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "metric": self.metric,
            "baseline": self.baseline,
            "current": self.current,
            "delta": self.delta,
            "relative_change": self.relative_change,
            "threshold": self.threshold,
            "drifted": self.drifted,
        }


@dataclass(frozen=True, slots=True)
class QualityReport:
    """Batch quality report for a pipeline invocation."""

    run_id: str
    timestamp: str
    source_paths: tuple[str, ...]
    validation: tuple[IngestionValidationResult, ...]
    record_metrics: tuple[RecordQualityMetrics, ...]
    summary: dict[str, Any]
    drift: tuple[DriftSignal, ...]
    alerts: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "source_paths": list(self.source_paths),
            "validation": [item.to_dict() for item in self.validation],
            "record_metrics": [item.to_dict() for item in self.record_metrics],
            "summary": _json_safe(self.summary),
            "drift": [item.to_dict() for item in self.drift],
            "alerts": list(self.alerts),
        }


def validate_ingestion_input(path: str | Path) -> IngestionValidationResult:
    """Validate a single ingestion input file before processing."""
    input_path = Path(path)
    file_format = SUPPORTED_INGESTION_SUFFIXES.get(input_path.suffix.lower(), "unknown")
    issues: list[IngestionIssue] = []
    record_count: int | None = None

    if not input_path.exists():
        issues.append(
            IngestionIssue(
                code="input_missing",
                message=f"Input file does not exist: {input_path}",
            )
        )
        return IngestionValidationResult(
            path=str(input_path),
            file_format=file_format,
            valid=False,
            issue_count=len(issues),
            issues=tuple(issues),
            record_count=record_count,
        )

    if file_format == "unknown":
        issues.append(
            IngestionIssue(
                code="unsupported_format",
                message=f"Unsupported ingestion file type: {input_path.suffix or '<none>'}",
            )
        )
        return IngestionValidationResult(
            path=str(input_path),
            file_format=file_format,
            valid=False,
            issue_count=len(issues),
            issues=tuple(issues),
            record_count=record_count,
        )

    text = input_path.read_text(encoding="utf-8")
    if not text.strip():
        issues.append(
            IngestionIssue(
                code="empty_input",
                message="Input file is empty.",
            )
        )

    if file_format == "xml":
        soup = BeautifulSoup(text, "xml")
        if soup.find() is None:
            issues.append(
                IngestionIssue(
                    code="xml_parse_failure",
                    message="XML input could not be parsed.",
                )
            )
    elif file_format == "html":
        soup = BeautifulSoup(text, "html.parser")
        tags = [tag.name for tag in soup.find_all(True)]
        if not tags or not any(tag not in {"html", "head", "body"} for tag in tags):
            issues.append(
                IngestionIssue(
                    code="html_parse_failure",
                    message="HTML input does not contain a meaningful document structure.",
                )
            )
    elif file_format == "jsonl":
        parsed_records = 0
        for lineno, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                issues.append(
                    IngestionIssue(
                        code="jsonl_parse_failure",
                        message=f"Invalid JSON on line {lineno}: {exc.msg}",
                    )
                )
                continue
            if not isinstance(payload, dict):
                issues.append(
                    IngestionIssue(
                        code="jsonl_invalid_record",
                        message=f"JSONL record on line {lineno} must be an object.",
                    )
                )
            parsed_records += 1
        record_count = parsed_records

    return IngestionValidationResult(
        path=str(input_path),
        file_format=file_format,
        valid=not issues,
        issue_count=len(issues),
        issues=tuple(issues),
        record_count=record_count,
    )


def validate_ingestion_inputs(paths: list[Path] | tuple[Path, ...]) -> tuple[IngestionValidationResult, ...]:
    """Validate a batch of ingestion inputs."""
    return tuple(validate_ingestion_input(path) for path in paths)


def record_quality_metrics(record: PipelineRecord) -> RecordQualityMetrics:
    """Compute per-record quality metrics for a PipelineRecord."""
    token_count = len(record.cleaned_tokens)
    resolved_entities = len(record.resolved_entities)
    te_reo_terms = list(record.te_reo_terms)
    completeness_fields = (
        record.doc_id,
        record.corpus_source,
        record.raw_text,
        record.cleaned_tokens,
        record.nz_act_citations,
        record.te_reo_terms,
    )
    completeness = sum(1 for field in completeness_fields if _is_present(field)) / len(completeness_fields)
    parse_success = 1.0 if _is_present(record.raw_text) and _is_present(record.cleaned_tokens) else 0.0
    entity_density = resolved_entities / max(token_count, 1)
    macron_integrity = _macron_ratio(te_reo_terms)
    quality_score = round(
        (0.35 * completeness)
        + (0.2 * parse_success)
        + (0.25 * min(entity_density * 10.0, 1.0))
        + (0.2 * macron_integrity),
        4,
    )
    return RecordQualityMetrics(
        doc_id=record.doc_id,
        corpus_source=record.corpus_source,
        token_count=token_count,
        completeness=round(completeness, 4),
        parse_success=round(parse_success, 4),
        entity_density=round(entity_density, 4),
        macron_integrity=round(macron_integrity, 4),
        quality_score=quality_score,
    )


def _distribution_shift(current: Counter[str], baseline: Counter[str]) -> float:
    total_current = sum(current.values()) or 1
    total_baseline = sum(baseline.values()) or 1
    keys = set(current) | set(baseline)
    return 0.5 * sum(
        abs((current.get(key, 0) / total_current) - (baseline.get(key, 0) / total_baseline))
        for key in keys
    )


def _numeric_drift(
    metric: str,
    current: float,
    baseline: float,
    threshold: float,
) -> DriftSignal:
    delta = current - baseline
    relative_change = None if baseline == 0 else delta / baseline
    drifted = abs(relative_change) >= threshold if relative_change is not None else abs(delta) >= threshold
    return DriftSignal(
        metric=metric,
        baseline=round(baseline, 4),
        current=round(current, 4),
        delta=round(delta, 4),
        relative_change=None if relative_change is None else round(relative_change, 4),
        threshold=threshold,
        drifted=drifted,
    )


def build_quality_report(
    records: list[PipelineRecord] | tuple[PipelineRecord, ...],
    *,
    source_paths: list[Path] | tuple[Path, ...] = (),
    run_id: str | None = None,
    baseline_summary: dict[str, Any] | None = None,
    validation_results: tuple[IngestionValidationResult, ...] | None = None,
    validate_sources: bool = True,
) -> QualityReport:
    """Build a quality report for a processed batch."""
    if not records:
        raise ValueError("Cannot build a quality report without pipeline records.")

    record_metrics = tuple(record_quality_metrics(record) for record in records)
    if validation_results is not None:
        validation = validation_results
    elif validate_sources and source_paths:
        validation = validate_ingestion_inputs(tuple(source_paths))
    else:
        validation = ()
    timestamp = _utc_now()
    run_id = run_id or timestamp.replace(":", "").replace("-", "")

    token_counts = [item.token_count for item in record_metrics]
    quality_scores = [item.quality_score for item in record_metrics]
    completeness = [item.completeness for item in record_metrics]
    parse_success = [item.parse_success for item in record_metrics]
    entity_density = [item.entity_density for item in record_metrics]
    macron_integrity = [item.macron_integrity for item in record_metrics]
    source_counts = Counter(record.corpus_source for record in records)
    validation_failed = sum(1 for item in validation if not item.valid)

    summary = {
        "record_count": len(records),
        "source_paths": [str(path) for path in source_paths],
        "validation_count": len(validation),
        "validation_failed": validation_failed,
        "average_token_count": round(fmean(token_counts), 4),
        "average_completeness": round(fmean(completeness), 4),
        "parse_success_rate": round(fmean(parse_success), 4),
        "average_entity_density": round(fmean(entity_density), 4),
        "average_macron_integrity": round(fmean(macron_integrity), 4),
        "quality_score": round(fmean(quality_scores), 4),
        "source_distribution": dict(sorted(source_counts.items())),
        "quality_gate_pass": validation_failed == 0 and fmean(quality_scores) >= 0.75,
    }

    drift: list[DriftSignal] = []
    if baseline_summary:
        baseline_sources = Counter(baseline_summary.get("source_distribution", {}))
        current_sources = Counter(summary["source_distribution"])
        drift.append(
            DriftSignal(
                metric="source_distribution",
                baseline=1.0,
                current=round(_distribution_shift(current_sources, baseline_sources), 4),
                delta=round(_distribution_shift(current_sources, baseline_sources), 4),
                relative_change=None,
                threshold=0.2,
                drifted=_distribution_shift(current_sources, baseline_sources) >= 0.2,
            )
        )
        for metric_name, threshold in DEFAULT_DRIFT_THRESHOLDS.items():
            if metric_name not in baseline_summary:
                continue
            drift.append(
                _numeric_drift(
                    metric_name,
                    float(summary[metric_name]),
                    float(baseline_summary[metric_name]),
                    threshold,
                )
            )

    alerts = tuple(
        message
        for message in (
            "validation_failed" if validation_failed else "",
            "quality_score_below_threshold" if summary["quality_score"] < 0.75 else "",
            "data_drift_detected" if any(signal.drifted for signal in drift) else "",
        )
        if message
    )
    return QualityReport(
        run_id=run_id,
        timestamp=timestamp,
        source_paths=tuple(str(path) for path in source_paths),
        validation=validation,
        record_metrics=record_metrics,
        summary=summary,
        drift=tuple(drift),
        alerts=alerts,
    )


def report_to_json(report: QualityReport) -> str:
    """Render a quality report as JSON."""
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def load_quality_report(path: str | Path) -> QualityReport:
    """Load a persisted quality report from JSON."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    return QualityReport(
        run_id=str(payload["run_id"]),
        timestamp=str(payload["timestamp"]),
        source_paths=tuple(str(item) for item in payload.get("source_paths", [])),
        validation=tuple(
            IngestionValidationResult(
                path=str(item["path"]),
                file_format=str(item["file_format"]),
                valid=bool(item["valid"]),
                issue_count=int(item["issue_count"]),
                issues=tuple(
                    IngestionIssue(
                        code=str(issue["code"]),
                        message=str(issue["message"]),
                        severity=cast(ValidationSeverity, str(issue.get("severity", "error"))),
                    )
                    for issue in item.get("issues", [])
                ),
                record_count=item.get("record_count"),
            )
            for item in payload.get("validation", [])
        ),
        record_metrics=tuple(
            RecordQualityMetrics(
                doc_id=str(item["doc_id"]),
                corpus_source=str(item["corpus_source"]),
                token_count=int(item["token_count"]),
                completeness=float(item["completeness"]),
                parse_success=float(item["parse_success"]),
                entity_density=float(item["entity_density"]),
                macron_integrity=float(item["macron_integrity"]),
                quality_score=float(item["quality_score"]),
            )
            for item in payload.get("record_metrics", [])
        ),
        summary=dict(payload.get("summary", {})),
        drift=tuple(
            DriftSignal(
                metric=str(item["metric"]),
                baseline=float(item["baseline"]),
                current=float(item["current"]),
                delta=float(item["delta"]),
                relative_change=item.get("relative_change"),
                threshold=float(item["threshold"]),
                drifted=bool(item["drifted"]),
            )
            for item in payload.get("drift", [])
        ),
        alerts=tuple(str(item) for item in payload.get("alerts", [])),
    )


def persist_quality_report(
    report: QualityReport,
    report_path: str | Path,
    *,
    history_dir: str | Path | None = None,
) -> Path:
    """Persist a quality report and optionally append it to the run history."""
    output_path = Path(report_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report_to_json(report), encoding="utf-8")
    if history_dir is not None:
        history_path = Path(history_dir).resolve()
        history_path.mkdir(parents=True, exist_ok=True)
        history_file = history_path / f"{report.timestamp.replace(':', '').replace('-', '')}_{report.run_id}.json"
        history_file.write_text(report_to_json(report), encoding="utf-8")
    return output_path


def history_reports(history_dir: str | Path) -> list[QualityReport]:
    """Load every JSON quality report in a history directory."""
    directory = Path(history_dir)
    if not directory.exists():
        return []
    reports = [load_quality_report(path) for path in sorted(directory.glob("*.json"))]
    return sorted(reports, key=lambda report: report.timestamp)


def dashboard_rows(reports: list[QualityReport]) -> list[dict[str, Any]]:
    """Return compact dashboard rows for HTML or CLI rendering."""
    rows: list[dict[str, Any]] = []
    for report in reports:
        rows.append(
            {
                "run_id": report.run_id,
                "timestamp": report.timestamp,
                "record_count": report.summary.get("record_count", 0),
                "quality_score": report.summary.get("quality_score", 0.0),
                "validation_failed": report.summary.get("validation_failed", 0),
                "quality_gate_pass": report.summary.get("quality_gate_pass", False),
                "alerts": list(report.alerts),
            }
        )
    return rows


def render_dashboard_html(reports: list[QualityReport]) -> str:
    """Render a static HTML dashboard for quality monitoring history."""
    rows = dashboard_rows(reports)
    latest = rows[-1] if rows else None
    trend_items = []
    for row in rows:
        width = max(4, min(100, int(round(float(row["quality_score"]) * 100))))
        trend_items.append(
            "<li>"
            f"<span>{row['timestamp']}</span>"
            f"<span class=\"bar\"><span style=\"width:{width}%\"></span></span>"
            f"<strong>{float(row['quality_score']):.2f}</strong>"
            f"<em>{row['record_count']} records</em>"
            "</li>"
        )
    table_rows = []
    for row in rows:
        alerts = ", ".join(row["alerts"]) if row["alerts"] else "none"
        table_rows.append(
            "<tr>"
            f"<td>{row['timestamp']}</td>"
            f"<td>{row['run_id']}</td>"
            f"<td>{row['record_count']}</td>"
            f"<td>{float(row['quality_score']):.2f}</td>"
            f"<td>{'pass' if row['quality_gate_pass'] else 'review'}</td>"
            f"<td>{alerts}</td>"
            "</tr>"
        )
    latest_block = ""
    if latest is not None:
        latest_block = (
            "<section class=\"card summary\">"
            "<h2>Latest Run</h2>"
            f"<p><strong>Run:</strong> {latest['run_id']}</p>"
            f"<p><strong>Quality score:</strong> {float(latest['quality_score']):.2f}</p>"
            f"<p><strong>Records:</strong> {latest['record_count']}</p>"
            f"<p><strong>Status:</strong> {'pass' if latest['quality_gate_pass'] else 'review'}</p>"
            "</section>"
        )
    return (
        "<!doctype html><html><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">"
        "<title>nlp-policy-nz Quality Dashboard</title>"
        "<style>"
        "body{font-family:system-ui,Segoe UI,Arial,sans-serif;margin:0;background:#0f172a;color:#e2e8f0;}"
        "main{max-width:1100px;margin:0 auto;padding:32px 20px 60px;}"
        ".hero{display:grid;gap:16px;grid-template-columns:2fr 1fr;align-items:start;}"
        ".card{background:#111827;border:1px solid #334155;border-radius:18px;padding:20px;box-shadow:0 18px 50px rgba(15,23,42,.35);}"
        "h1,h2{margin-top:0;}"
        "table{width:100%;border-collapse:collapse;}"
        "th,td{padding:10px 12px;border-bottom:1px solid #243244;text-align:left;}"
        ".bar{display:inline-block;width:160px;height:10px;background:#1f2937;border-radius:999px;overflow:hidden;vertical-align:middle;margin:0 10px;}"
        ".bar span{display:block;height:100%;background:linear-gradient(90deg,#22c55e,#eab308);}"
        "ul{list-style:none;padding:0;margin:0;display:grid;gap:10px;}"
        "li{display:grid;grid-template-columns:1.4fr 1fr .5fr .8fr;gap:10px;align-items:center;}"
        ".summary p{margin:.35rem 0;}"
        "@media (max-width: 900px){.hero{grid-template-columns:1fr;}li{grid-template-columns:1fr;}.bar{width:100%;}}"
        "</style></head><body><main>"
        "<section class=\"hero\">"
        "<div class=\"card\"><h1>Data Quality Dashboard</h1>"
        "<p>Static snapshot of pipeline validation, drift, and quality scores.</p>"
        "</div>"
        f"{latest_block}"
        "</section>"
        "<section class=\"card\"><h2>Trend</h2><ul>"
        + "".join(trend_items)
        + "</ul></section>"
        "<section class=\"card\"><h2>Run History</h2><table><thead><tr><th>Timestamp</th><th>Run</th><th>Records</th><th>Score</th><th>Status</th><th>Alerts</th></tr></thead><tbody>"
        + ("".join(table_rows) if table_rows else "<tr><td colspan=\"6\">No reports yet.</td></tr>")
        + "</tbody></table></section>"
        "</main></body></html>"
    )


def write_dashboard_html(reports: list[QualityReport], output_path: str | Path) -> Path:
    """Write the static HTML dashboard to disk."""
    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(render_dashboard_html(reports), encoding="utf-8")
    return destination


def register_quality_span_attributes(report: QualityReport) -> None:
    """Attach quality summary metrics to the current trace span."""
    summary = report.summary
    set_span_attribute("quality.record_count", int(summary.get("record_count", 0)))
    set_span_attribute("quality.average_token_count", float(summary.get("average_token_count", 0.0)))
    set_span_attribute("quality.average_entity_density", float(summary.get("average_entity_density", 0.0)))
    set_span_attribute("quality.average_macron_integrity", float(summary.get("average_macron_integrity", 0.0)))
    set_span_attribute("quality.quality_score", float(summary.get("quality_score", 0.0)))
    set_span_attribute("quality.validation_failed", int(summary.get("validation_failed", 0)))
    set_span_attribute("quality.drift_count", len(report.drift))
    set_span_attribute("quality.alert_count", len(report.alerts))
