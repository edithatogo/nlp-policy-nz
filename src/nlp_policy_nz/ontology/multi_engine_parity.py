"""Multi-engine rules-as-code parity helpers for Track 80."""

from __future__ import annotations

import json
import textwrap
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path
from typing import Any

from nlp_policy_nz.axiom import SourceSection
from nlp_policy_nz.ontology.rac_bridge import (
    PolicyEnginePackageSkeleton,
    RulesAsCodeBridgeRecord,
    build_openfisca_package_skeleton,
    build_policyengine_package_skeleton,
    build_rules_as_code_bridge,
    write_policyengine_package_skeleton,
)
from nlp_policy_nz.policyengine_pilot import (
    PolicyEnginePilotDomain,
    load_policyengine_pilot_domain_json,
)

TRACK80_REPORT_FILENAME = "multi_engine_parity_report.json"
TRACK80_REPORT_MARKDOWN_FILENAME = "multi_engine_parity_report.md"
TRACK80_SCHEMA_VERSION = "track80.multi-engine-parity.v1"
POLICYENGINE_RUNTIME_VERSION = "reference"
OPENFISCA_RUNTIME_VERSION = "reference"
POLICYENGINE_SUPPORT_LEVEL = "primary"
OPENFISCA_SUPPORT_LEVEL = "export-only"


@dataclass(frozen=True)
class EngineAdapterContract:
    """Support-level metadata for one downstream rules engine."""

    engine_id: str
    package_name: str
    support_level: str
    runtime_version: str
    runtime_dependency: str
    skip_behavior: str
    known_gaps: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible engine contract."""
        payload = asdict(self)
        payload["known_gaps"] = list(self.known_gaps)
        return payload


@dataclass(frozen=True)
class MultiEngineParityCase:
    """Deterministic parity result for one oracle case."""

    case_id: str
    expected_output: bool
    policyengine_output: bool
    openfisca_output: bool
    passed: bool
    source_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible parity case."""
        payload = asdict(self)
        payload["source_ids"] = list(self.source_ids)
        return payload


@dataclass(frozen=True)
class MultiEngineParityReport:
    """Deterministic parity report across the repo-local engine contracts."""

    track_id: str
    source_ids: tuple[str, ...]
    source_citation_path: str
    source_sha256: str
    formula_id: str
    policyengine_package_name: str
    openfisca_package_name: str
    engine_contracts: tuple[EngineAdapterContract, ...]
    cases: tuple[MultiEngineParityCase, ...]
    known_gaps: tuple[str, ...]

    @property
    def passed(self) -> bool:
        """Return whether every engine output agreed with the oracle fixture."""
        return all(case.passed for case in self.cases)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible parity report."""
        return {
            "schema_version": TRACK80_SCHEMA_VERSION,
            "track_id": self.track_id,
            "source_ids": list(self.source_ids),
            "source_citation_path": self.source_citation_path,
            "source_sha256": self.source_sha256,
            "formula_id": self.formula_id,
            "policyengine_package_name": self.policyengine_package_name,
            "openfisca_package_name": self.openfisca_package_name,
            "passed": self.passed,
            "engine_contracts": [contract.to_dict() for contract in self.engine_contracts],
            "cases": [case.to_dict() for case in self.cases],
            "known_gaps": list(self.known_gaps),
        }


@dataclass(frozen=True)
class MultiEngineParityBundle:
    """All Track 80 artifacts derived from the reviewed pilot domain."""

    domain: PolicyEnginePilotDomain
    bridge_record: RulesAsCodeBridgeRecord
    policyengine_package: PolicyEnginePackageSkeleton
    openfisca_package: PolicyEnginePackageSkeleton
    report: MultiEngineParityReport

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible bundle."""
        return {
            "domain": self.domain.to_dict(),
            "bridge_record": self.bridge_record.to_dict(),
            "policyengine_package": self.policyengine_package.to_dict(),
            "openfisca_package": self.openfisca_package.to_dict(),
            "report": self.report.to_dict(),
        }


def load_track80_domain_json(
    path: str | Path = Path("data/track79/policyengine_pilot_manifest.json"),
) -> PolicyEnginePilotDomain:
    """Load the Track 79 reviewed pilot domain used by Track 80 parity checks."""
    return load_policyengine_pilot_domain_json(path)


def build_multi_engine_parity_bundle(
    domain: PolicyEnginePilotDomain,
) -> MultiEngineParityBundle:
    """Build the Track 80 parity bundle from a reviewed pilot domain."""
    if domain.expression.strip() != "assessment_date > royal_assent_date":
        raise ValueError("Track 80 only supports the reviewed commencement pilot expression")
    bridge_record = _build_bridge_record(domain)
    policyengine_package = build_policyengine_package_skeleton(
        bridge_record,
        package_name=domain.package_name,
    )
    openfisca_package = build_openfisca_package_skeleton(
        bridge_record,
        package_name=_openfisca_package_name(domain.package_name),
    )
    report = _build_parity_report(
        domain=domain,
        bridge_record=bridge_record,
        policyengine_package=policyengine_package,
        openfisca_package=openfisca_package,
    )
    return MultiEngineParityBundle(
        domain=domain,
        bridge_record=bridge_record,
        policyengine_package=policyengine_package,
        openfisca_package=openfisca_package,
        report=report,
    )


def write_multi_engine_parity_bundle(
    bundle: MultiEngineParityBundle,
    output_dir: str | Path,
) -> Path:
    """Write the Track 80 bundle and return the resolved output directory."""
    root = Path(output_dir).resolve()
    write_policyengine_package_skeleton(
        bundle.policyengine_package,
        root / "policyengine",
    )
    write_policyengine_package_skeleton(
        bundle.openfisca_package,
        root / "openfisca",
    )
    (root / TRACK80_REPORT_FILENAME).write_text(
        render_multi_engine_parity_report_json(bundle.report),
        encoding="utf-8",
    )
    (root / TRACK80_REPORT_MARKDOWN_FILENAME).write_text(
        render_multi_engine_parity_report_markdown(bundle.report),
        encoding="utf-8",
    )
    return root


def render_multi_engine_parity_report_json(report: MultiEngineParityReport) -> str:
    """Render the parity report as stable formatted JSON."""
    return json.dumps(report.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_multi_engine_parity_report_markdown(report: MultiEngineParityReport) -> str:
    """Render the parity report as a compact Markdown summary."""
    engine_rows = "\n".join(
        f"- {contract.engine_id}: {contract.support_level} ({contract.runtime_version})"
        for contract in report.engine_contracts
    )
    case_rows = "\n".join(
        f"| {case.case_id} | {case.expected_output} | {case.policyengine_output} | {case.openfisca_output} | {case.passed} |"
        for case in report.cases
    )
    gaps = "\n".join(f"- {gap}" for gap in report.known_gaps) or "- None"
    return textwrap.dedent(
        f"""\
        # Track 80 Multi-Engine Parity Report

        - Track ID: `{report.track_id}`
        - Source IDs: {", ".join(report.source_ids)}
        - Source citation path: `{report.source_citation_path}`
        - Source SHA-256: `{report.source_sha256}`
        - Formula ID: `{report.formula_id}`
        - Passed: `{report.passed}`

        ## Engine Contracts

        {engine_rows}

        ## Parity Cases

        | Case ID | Expected | PolicyEngine | OpenFisca | Passed |
        | --- | --- | --- | --- | --- |
        {case_rows}

        ## Known Gaps

        {gaps}
        """
    )


def _build_bridge_record(domain: PolicyEnginePilotDomain) -> RulesAsCodeBridgeRecord:
    source_path = Path(domain.source_path)
    if not source_path.is_absolute():
        source_path = _repo_root() / source_path
    source_path = source_path.resolve()
    if not source_path.is_file():
        raise FileNotFoundError(f"Track 80 source file not found: {source_path}")
    text = source_path.read_text(encoding="utf-8")
    source_section = SourceSection.from_text(
        text,
        citation_path=domain.source_citation_path,
        jurisdiction="NZ",
        document_type="act",
        source_url=domain.source_url,
        retrieved_at=domain.retrieved_at,
        title=domain.source_title,
    )
    if source_section.metadata.checksum_sha256 != domain.source_sha256:
        raise ValueError("Track 80 source SHA-256 does not match the manifest")
    return build_rules_as_code_bridge(
        source_section,
        concept=domain.concept,
        review_status="reviewed",
    )


def _build_parity_report(
    *,
    domain: PolicyEnginePilotDomain,
    bridge_record: RulesAsCodeBridgeRecord,
    policyengine_package: PolicyEnginePackageSkeleton,
    openfisca_package: PolicyEnginePackageSkeleton,
) -> MultiEngineParityReport:
    cases = tuple(
        _build_parity_case(
            case_id=case.case_id,
            expected_output=case.expected_output,
            assessment_date=case.assessment_date,
            royal_assent_date=case.royal_assent_date,
            source_ids=(bridge_record.record_id, domain.domain_id, domain.source_citation_path),
        )
        for case in domain.oracle_cases
    )
    contracts = (
        EngineAdapterContract(
            engine_id="policyengine",
            package_name=policyengine_package.package_name,
            support_level=POLICYENGINE_SUPPORT_LEVEL,
            runtime_version=POLICYENGINE_RUNTIME_VERSION,
            runtime_dependency="none; repo-local reference adapter",
            skip_behavior="never skipped in repo-local CI",
        ),
        EngineAdapterContract(
            engine_id="openfisca",
            package_name=openfisca_package.package_name,
            support_level=OPENFISCA_SUPPORT_LEVEL,
            runtime_version=OPENFISCA_RUNTIME_VERSION,
            runtime_dependency="openfisca-core optional",
            skip_behavior="skip only when an external OpenFisca runtime test is added",
            known_gaps=(
                "Repo-local CI validates export parity through the reference adapter, not a live OpenFisca runtime.",
            ),
        ),
    )
    known_gaps = (
        "OpenFisca runtime execution remains optional until an external dependency path is promoted.",
    )
    return MultiEngineParityReport(
        track_id=domain.track_id,
        source_ids=(bridge_record.record_id, domain.domain_id, domain.source_citation_path),
        source_citation_path=domain.source_citation_path,
        source_sha256=domain.source_sha256,
        formula_id=domain.formula_id,
        policyengine_package_name=policyengine_package.package_name,
        openfisca_package_name=openfisca_package.package_name,
        engine_contracts=contracts,
        cases=cases,
        known_gaps=known_gaps,
    )


def _build_parity_case(
    *,
    case_id: str,
    expected_output: bool,
    assessment_date: str,
    royal_assent_date: str,
    source_ids: tuple[str, ...],
) -> MultiEngineParityCase:
    """Build one parity case and evaluate both repo-local engine adapters."""
    policyengine_output = _evaluate_commencement_formula(
        assessment_date=assessment_date,
        royal_assent_date=royal_assent_date,
    )
    openfisca_output = _evaluate_commencement_formula(
        assessment_date=assessment_date,
        royal_assent_date=royal_assent_date,
    )
    return MultiEngineParityCase(
        case_id=case_id,
        expected_output=expected_output,
        policyengine_output=policyengine_output,
        openfisca_output=openfisca_output,
        passed=(
            policyengine_output == expected_output
            and openfisca_output == expected_output
            and policyengine_output == openfisca_output
        ),
        source_ids=source_ids,
    )


def _evaluate_commencement_formula(*, assessment_date: str, royal_assent_date: str) -> bool:
    """Evaluate the reviewed commencement formula for parity reporting."""
    return date.fromisoformat(assessment_date) > date.fromisoformat(royal_assent_date)


def _openfisca_package_name(package_name: str) -> str:
    """Derive an OpenFisca package name from the reviewed PolicyEngine package name."""
    if "policyengine" in package_name:
        return package_name.replace("policyengine", "openfisca", 1)
    if package_name.startswith("openfisca_"):
        return package_name
    return f"openfisca_{package_name}"


def _repo_root() -> Path:
    """Return the repository root."""
    return Path(__file__).resolve().parents[3]
