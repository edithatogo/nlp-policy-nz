"""Dependency audit and SBOM helpers for supply-chain security."""

from __future__ import annotations

import json
import subprocess
import sys
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import requests
from cvss import CVSS3, CVSS4

HIGH_SEVERITY_THRESHOLD = 7.0
OSV_VULN_URL = "https://api.osv.dev/v1/vulns/{vuln_id}"


@dataclass(frozen=True, slots=True)
class DependencyFinding:
    """A dependency vulnerability classified by severity."""

    package: str
    version: str
    vuln_id: str
    severity_score: float | None
    fix_versions: tuple[str, ...]

    @property
    def severity_label(self) -> str:
        """Return the human severity bucket for the finding."""
        if self.severity_score is None:
            return "unknown"
        if self.severity_score >= 9.0:
            return "critical"
        if self.severity_score >= 7.0:
            return "high"
        if self.severity_score >= 4.0:
            return "medium"
        if self.severity_score > 0.0:
            return "low"
        return "none"


def run_dependency_audit(project_root: Path | None = None) -> dict[str, Any]:
    """Run pip-audit against the project and return the parsed JSON report."""
    root = Path.cwd() if project_root is None else project_root
    result = subprocess.run(  # noqa: S603
        [sys.executable, "-m", "pip_audit", "--format=json", "--local"],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )
    if not result.stdout.strip():
        stderr = result.stderr.strip()
        msg = stderr or "pip-audit did not produce JSON output"
        raise RuntimeError(msg)
    return json.loads(result.stdout)


def audit_dependency_report(report: Mapping[str, Any]) -> list[DependencyFinding]:
    """Convert a pip-audit JSON report into vulnerability findings."""
    findings: list[DependencyFinding] = []
    for dependency in report.get("dependencies", []):
        package = str(dependency.get("name", "unknown"))
        version = str(dependency.get("version", "unknown"))
        for vulnerability in dependency.get("vulns", []):
            vuln_id = str(vulnerability.get("id", "unknown"))
            aliases = tuple(
                str(alias)
                for alias in vulnerability.get("aliases", [])
                if str(alias).strip()
            )
            score = classify_osv_severity(vuln_id, aliases)
            fix_versions = tuple(str(version) for version in vulnerability.get("fix_versions", []))
            findings.append(
                DependencyFinding(
                    package=package,
                    version=version,
                    vuln_id=vuln_id,
                    severity_score=score,
                    fix_versions=fix_versions,
                ),
            )
    return findings


def collect_high_severity_findings(
    report: Mapping[str, Any],
    *,
    threshold: float = HIGH_SEVERITY_THRESHOLD,
) -> list[DependencyFinding]:
    """Return only the vulnerability findings at or above the severity threshold."""
    return [
        finding
        for finding in audit_dependency_report(report)
        if finding.severity_score is not None and finding.severity_score >= threshold
    ]


def generate_cyclonedx_sbom(output_path: Path, project_root: Path | None = None) -> Path:
    """Generate a CycloneDX JSON SBOM for the current Pixi environment."""
    root = Path.cwd() if project_root is None else project_root
    output_path.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(  # noqa: S603
        [
            sys.executable,
            "-m",
            "cyclonedx_py",
            "environment",
            "--of",
            "JSON",
            "-o",
            str(output_path),
            str(sys.executable),
        ],
        cwd=root,
        check=True,
    )
    return output_path


@lru_cache(maxsize=256)
def classify_osv_severity(vuln_id: str, aliases: Sequence[str] = ()) -> float | None:
    """Return the highest CVSS score reported by OSV for a vulnerability ID."""
    candidate_ids = [vuln_id, *[alias for alias in aliases if alias != vuln_id]]
    for candidate in candidate_ids:
        details = _fetch_osv_vulnerability(candidate)
        if details is None:
            continue
        score = _highest_score_from_osv_details(details)
        if score is not None:
            return score
    return None


def _highest_score_from_osv_details(details: Mapping[str, Any]) -> float | None:
    scores: list[float] = []
    for severity in details.get("severity", []):
        score = _score_from_cvss_vector(str(severity.get("score", "")))
        if score is not None:
            scores.append(score)
    if scores:
        return max(scores)
    return None


def _score_from_cvss_vector(vector: str) -> float | None:
    if not vector:
        return None
    if vector.startswith("CVSS:4."):
        return CVSS4(vector).scores()[0]
    if vector.startswith("CVSS:3."):
        return CVSS3(vector).scores()[0]
    return None


@lru_cache(maxsize=512)
def _fetch_osv_vulnerability(vuln_id: str) -> Mapping[str, Any] | None:
    response = requests.get(OSV_VULN_URL.format(vuln_id=vuln_id), timeout=20)
    if response.status_code == 404:
        return None
    response.raise_for_status()
    return response.json()
