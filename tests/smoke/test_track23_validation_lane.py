"""Bounded Track 23 smoke validation lane.

These tests keep the Track 23 repo-side validation contract fast and local.
They deliberately avoid live services, large model downloads, full-repo linting,
full type checking, coverage thresholds, and mutation execution.
"""

from __future__ import annotations

import configparser
import tomllib
from pathlib import Path

import spacy

from nlp_policy_nz.guard import normalize_text
from nlp_policy_nz.quality.track23_evidence import (
    Track23EvidenceReport,
    evaluate_track23_acceptance,
    track23_residual_external_gates,
)
from nlp_policy_nz.storage import PipelineRecord
from nlp_policy_nz.syntactic import chunk_legislation_document

ROOT = Path(__file__).resolve().parents[2]


def test_track23_smoke_lane_artifacts_are_present() -> None:
    """Track 23 has the local artifacts needed for bounded validation."""
    expected_files = [
        ROOT / ".coveragerc",
        ROOT / "docs" / "build_backend.md",
        ROOT / "docs" / "profiling.md",
        ROOT / "docs" / "pydantic_vs_msgspec.md",
        ROOT / "scripts" / "profile_with_scalene.py",
        ROOT / "tests" / ".mutatest.toml",
        ROOT / "tests" / "smoke" / "__init__.py",
        ROOT / "tests" / "integration" / "__init__.py",
        ROOT / "tests" / "e2e" / "__init__.py",
    ]

    assert [path for path in expected_files if not path.is_file()] == []


def test_track23_smoke_lane_config_is_parseable() -> None:
    """Quality configuration parses without invoking heavyweight tools."""
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    pixi = tomllib.loads((ROOT / "pixi.toml").read_text(encoding="utf-8"))
    coverage = configparser.ConfigParser()
    coverage.read(ROOT / ".coveragerc", encoding="utf-8")

    assert {"ANN", "D", "TCH", "YTT", "RET"} <= set(
        pyproject["tool"]["ruff"]["lint"]["select"]
    )
    assert pyproject["tool"]["pyright"]["typeCheckingMode"] == "strict"
    assert {"coverage", "mutation", "profile", "typecheck"} <= set(pixi["tasks"])
    assert coverage.getboolean("run", "branch") is True


def test_track23_smoke_lane_docs_record_bounded_decisions() -> None:
    """Docs distinguish repo-side scaffolding from measured external gates."""
    build_backend = (ROOT / "docs" / "build_backend.md").read_text(encoding="utf-8")
    profiling = (ROOT / "docs" / "profiling.md").read_text(encoding="utf-8")
    validation = (ROOT / "docs" / "pydantic_vs_msgspec.md").read_text(
        encoding="utf-8"
    )

    assert "hatchling" in build_backend
    assert "uv_build" in build_backend
    assert "external gate" in profiling
    assert "msgspec" in validation
    assert "pydantic" in validation.lower()


def test_track23_smoke_lane_core_path_runs_without_external_services() -> None:
    """A tiny local text path can normalize, chunk, and enter the record schema."""
    nlp = spacy.blank("en")
    nlp.add_pipe("sentencizer")

    text = normalize_text("Maaori Act 2024 applies. The Minister may consult iwi.")
    chunks = chunk_legislation_document(text, nlp, year=2024, number=1)
    record = PipelineRecord(
        doc_id=chunks[0]["doc_id"],
        corpus_source="legislation",
        raw_text=chunks[0]["text"],
        cleaned_tokens=chunks[0]["text"].split(),
        nz_act_citations=[],
        te_reo_terms=["M\u0101ori"],
    )

    assert len(chunks) == 2
    assert record.doc_id == "NZ-ACT-2024-001-SEC-0"
    assert record.raw_text == "M\u0101ori Act 2024 applies."


def test_track23_smoke_lane_evidence_keeps_measured_gates_pending() -> None:
    """Repo-side validation does not overclaim strict measured gates."""
    report = Track23EvidenceReport(
        ruff_strict_configured=True,
        pyright_strict_configured=True,
        coverage_configured=True,
        ci_quality_steps=5,
        smoke_tests_present=True,
        integration_tests_present=True,
        e2e_tests_present=True,
        property_tests_present=True,
        mutation_config_present=True,
        profiling_script_present=True,
        build_backend_documented=True,
        pydantic_eval_documented=True,
        focused_tests_passing=True,
        full_ruff_strict_passing=False,
        full_typecheck_passing=False,
        coverage_gate_passing=False,
        mutation_ci_gate_enabled=False,
    )

    status = evaluate_track23_acceptance(report)
    residual = track23_residual_external_gates(report)

    assert status["repo_side_contracts"] is True
    assert status["full_ruff_strict"] is False
    assert status["full_typecheck"] is False
    assert status["coverage_gate"] is False
    assert status["mutation_ci_gate"] is False
    assert len(residual) == 4
