"""Track 40 dependency automation and supply-chain security contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.security import dependency_security

ROOT = Path(__file__).resolve().parents[1]
TRACK40 = ROOT / "conductor" / "tracks" / "track40_dependency_supplychain_20260626"


def test_track40_repo_supply_chain_artifacts_exist() -> None:
    """Track 40 should ship dependency automation, audit, and SBOM files."""
    expected = [
        ROOT / ".github" / "dependabot.yml",
        ROOT / "scripts" / "check_dependency_security.py",
        ROOT / "src" / "nlp_policy_nz" / "security" / "__init__.py",
        ROOT / "src" / "nlp_policy_nz" / "security" / "dependency_security.py",
        ROOT / "conductor" / "tracks" / "track40_dependency_supplychain_20260626" / "index.md",
        TRACK40 / "metadata.json",
        TRACK40 / "plan.md",
        TRACK40 / "spec.md",
    ]

    assert [path for path in expected if not path.is_file()] == []


def test_track40_registry_metadata_and_plan_are_linked() -> None:
    """Track 40 should be registered as in progress with a complete track package."""
    registry = (ROOT / "conductor" / "tracks.md").read_text(encoding="utf-8")
    metadata = json.loads((TRACK40 / "metadata.json").read_text(encoding="utf-8"))
    plan = (TRACK40 / "plan.md").read_text(encoding="utf-8")
    spec = (TRACK40 / "spec.md").read_text(encoding="utf-8")

    assert "Track 40: Dependency Automation & Supply Chain Security" in registry
    assert "./conductor/tracks/track40_dependency_supplychain_20260626/" in registry
    assert metadata["track_id"] == "track40_dependency_supplychain_20260626"
    assert metadata["status"] == "complete"
    assert "SBOM" in spec
    assert "Dependabot" in spec
    assert "pip-audit" in plan
    assert "cyclonedx-bom" in plan
    assert "CONTRIBUTING.md" in plan


def test_track40_dependabot_and_workflows_reference_grouped_updates() -> None:
    """Dependabot and CI should encode grouped updates plus SBOM publication."""
    dependabot = (ROOT / ".github" / "dependabot.yml").read_text(encoding="utf-8")
    ci_workflow = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    release_workflow = (ROOT / ".github" / "workflows" / "release.yml").read_text(
        encoding="utf-8",
    )
    contributing = (ROOT / "CONTRIBUTING.md").read_text(encoding="utf-8")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    pixi = (ROOT / "pixi.toml").read_text(encoding="utf-8")

    assert 'package-ecosystem: "pip"' in dependabot
    assert 'package-ecosystem: "github-actions"' in dependabot
    assert "production-dependencies" in dependabot
    assert "development-dependencies" in dependabot
    assert "actions" in dependabot
    assert "Supply-chain dependency audit" in ci_workflow
    assert "Generate CycloneDX SBOM" in ci_workflow
    assert "nlp-policy-nz-sbom" in ci_workflow
    assert "Generate CycloneDX SBOM" in release_workflow
    assert "nlp-policy-nz.cdx.json" in release_workflow
    assert "make security-deps" in contributing
    assert "Pixi lockfile refreshes" in contributing
    assert "pixi run python scripts/check_dependency_security.py" in makefile
    assert "pip-audit>=2.10.0" in pyproject
    assert "cyclonedx-bom>=1.5.0" in pyproject
    assert "cvss>=3.6" in pyproject
    assert 'pip-audit = ">=2.10.0"' in pixi
    assert 'cyclonedx-bom = ">=1.5.0"' in pixi
    assert 'cvss = ">=3.6"' in pixi


def test_track40_dependency_severity_gate_flags_high_and_critical(monkeypatch) -> None:
    """The severity gate should only fail on high/critical OSV findings."""
    report = {
        "dependencies": [
            {
                "name": "flask",
                "version": "0.5",
                "vulns": [
                    {
                        "id": "PYSEC-2019-179",
                        "aliases": ["CVE-2019-1010083"],
                        "fix_versions": ["1.0"],
                    }
                ],
            },
            {
                "name": "jinja2",
                "version": "3.1.0",
                "vulns": [
                    {
                        "id": "PYSEC-2020-123",
                        "aliases": ["CVE-2020-12345"],
                        "fix_versions": ["3.1.3"],
                    }
                ],
            },
        ]
    }

    def fake_fetch(vuln_id: str, aliases=()):  # noqa: ANN001, ARG001
        if vuln_id in {"PYSEC-2019-179", "CVE-2019-1010083"}:
            return 9.8
        if vuln_id in {"PYSEC-2020-123", "CVE-2020-12345"}:
            return 4.7
        return None

    monkeypatch.setattr(dependency_security, "classify_osv_severity", fake_fetch)
    findings = dependency_security.collect_high_severity_findings(report)
    assert len(findings) == 1
    assert findings[0].package == "flask"
    assert findings[0].severity_label == "critical"

    audited = dependency_security.audit_dependency_report(report)
    assert len(audited) == 2
    assert audited[0].severity_score == 9.8
    assert audited[1].severity_score == 4.7
    assert audited[1].severity_label == "medium"
