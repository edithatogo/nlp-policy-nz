"""PolicyEngine pilot package generation for Track 79.

This module turns a reviewed rules-as-code handoff into a deterministic,
offline package layout with one executable pilot formula and checked-in oracle
fixtures. The generated package is PolicyEngine-compatible in shape, while the
repo-local execution path remains standard-library only so GitHub Actions can
run it without external runtime dependencies.
"""

from __future__ import annotations

import json
import textwrap
from dataclasses import asdict, dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import yaml

from nlp_policy_nz.axiom import SourceSection
from nlp_policy_nz.extraction.schemas import ExtractedSpan, SourceTrace
from nlp_policy_nz.ontology.rac_bridge import build_rules_as_code_bridge
from nlp_policy_nz.rulespec_promotion import (
    PromotionState,
    RuleSpecFormula,
    RuleSpecOracleFixtureRef,
    RuleSpecPromotionHandoff,
    RuleSpecReviewerEvidence,
    build_rulespec_promotion_handoff,
    validate_rulespec_promotion_handoff,
    write_rulespec_promotion_handoff,
)

TRACK79_SELECTION_PATH = Path("data/track79/policyengine_pilot_manifest.json")
TRACK79_ORACLE_FIXTURE_PATH = Path("data/track79/oracles/policyengine_oracles.json")
TRACK79_REVIEW_NOTE_PATH = Path("data/track79/reviews/policyengine_pilot_review.md")
PACKAGE_NAME_DEFAULT = "policyengine_nz_commencement_pilot"


@dataclass(frozen=True)
class PolicyEngineOracleCase:
    """One deterministic oracle case for the pilot formula."""

    case_id: str
    assessment_date: str
    royal_assent_date: str
    expected_output: bool
    notes: str | None = None

    def __post_init__(self) -> None:
        """Validate oracle case fields."""
        _require_nonempty("case_id", self.case_id)
        _validate_iso_date("assessment_date", self.assessment_date)
        _validate_iso_date("royal_assent_date", self.royal_assent_date)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible oracle case."""
        return asdict(self)


@dataclass(frozen=True)
class PolicyEnginePilotDomain:
    """A narrow reviewed pilot domain selected for executable PolicyEngine output."""

    track_id: str
    package_name: str
    domain_id: str
    domain_title: str
    source_path: str
    source_citation_path: str
    source_url: str
    retrieved_at: str
    source_title: str
    source_excerpt: str
    source_sha256: str
    concept: str
    entity: str
    period: str
    parameter_name: str
    parameter_value: str
    formula_id: str
    variable_name: str
    expression: str
    review_state: PromotionState = PromotionState.PROMOTED
    reviewer_evidence: tuple[RuleSpecReviewerEvidence, ...] = field(default_factory=tuple)
    oracle_cases: tuple[PolicyEngineOracleCase, ...] = field(default_factory=tuple)
    oracle_fixture_path: str = str(TRACK79_ORACLE_FIXTURE_PATH)
    review_note_path: str = str(TRACK79_REVIEW_NOTE_PATH)
    downstream_targets: tuple[str, ...] = ("policyengine",)

    def __post_init__(self) -> None:
        """Validate the pilot domain and normalize review state."""
        _require_nonempty("track_id", self.track_id)
        _require_nonempty("package_name", self.package_name)
        _require_nonempty("domain_id", self.domain_id)
        _require_nonempty("domain_title", self.domain_title)
        _require_nonempty("source_path", self.source_path)
        _require_nonempty("source_citation_path", self.source_citation_path)
        _require_nonempty("source_url", self.source_url)
        _require_nonempty("retrieved_at", self.retrieved_at)
        _require_nonempty("source_title", self.source_title)
        _require_nonempty("source_excerpt", self.source_excerpt)
        _require_nonempty("source_sha256", self.source_sha256)
        _require_nonempty("concept", self.concept)
        _require_nonempty("entity", self.entity)
        _require_nonempty("period", self.period)
        _require_nonempty("parameter_name", self.parameter_name)
        _validate_iso_date("parameter_value", self.parameter_value)
        _require_nonempty("formula_id", self.formula_id)
        _require_nonempty("variable_name", self.variable_name)
        _require_nonempty("expression", self.expression)
        object.__setattr__(self, "review_state", _normalize_state(self.review_state))
        object.__setattr__(self, "reviewer_evidence", tuple(self.reviewer_evidence))
        object.__setattr__(self, "oracle_cases", tuple(self.oracle_cases))
        object.__setattr__(self, "downstream_targets", tuple(_require_nonempty("target", target) for target in self.downstream_targets))

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible pilot domain payload."""
        return {
            "track_id": self.track_id,
            "package_name": self.package_name,
            "domain_id": self.domain_id,
            "domain_title": self.domain_title,
            "source_path": self.source_path,
            "source_citation_path": self.source_citation_path,
            "source_url": self.source_url,
            "retrieved_at": self.retrieved_at,
            "source_title": self.source_title,
            "source_excerpt": self.source_excerpt,
            "source_sha256": self.source_sha256,
            "concept": self.concept,
            "entity": self.entity,
            "period": self.period,
            "parameter_name": self.parameter_name,
            "parameter_value": self.parameter_value,
            "formula_id": self.formula_id,
            "variable_name": self.variable_name,
            "expression": self.expression,
            "review_state": self.review_state.value,
            "reviewer_evidence": [item.to_dict() for item in self.reviewer_evidence],
            "oracle_cases": [item.to_dict() for item in self.oracle_cases],
            "oracle_fixture_path": self.oracle_fixture_path,
            "review_note_path": self.review_note_path,
            "downstream_targets": list(self.downstream_targets),
        }


@dataclass(frozen=True)
class PolicyEnginePilotExecutionResult:
    """One oracle evaluation result from the generated package."""

    case_id: str
    expected_output: bool
    actual_output: bool
    passed: bool
    assessment_date: str
    royal_assent_date: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible oracle execution result."""
        return asdict(self)


@dataclass(frozen=True)
class PolicyEnginePilotExecutionReport:
    """Summary of the generated pilot package execution results."""

    package_name: str
    rulespec_id: str
    source_citation_path: str
    source_sha256: str
    formula_id: str
    results: tuple[PolicyEnginePilotExecutionResult, ...]

    @property
    def passed(self) -> bool:
        """Return whether all oracle cases passed."""
        return all(result.passed for result in self.results)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible execution report."""
        return {
            "package_name": self.package_name,
            "rulespec_id": self.rulespec_id,
            "source_citation_path": self.source_citation_path,
            "source_sha256": self.source_sha256,
            "formula_id": self.formula_id,
            "passed": self.passed,
            "results": [result.to_dict() for result in self.results],
        }


@dataclass(frozen=True)
class PolicyEnginePilotPackage:
    """Deterministic generated package and its execution report."""

    domain: PolicyEnginePilotDomain
    handoff: RuleSpecPromotionHandoff
    files: dict[str, str]
    execution_report: PolicyEnginePilotExecutionReport

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible generated package."""
        return {
            "domain": self.domain.to_dict(),
            "handoff": self.handoff.to_dict(),
            "files": dict(sorted(self.files.items())),
            "execution_report": self.execution_report.to_dict(),
        }


def load_policyengine_pilot_domain_json(path: str | Path = TRACK79_SELECTION_PATH) -> PolicyEnginePilotDomain:
    """Load the Track 79 pilot domain from deterministic JSON."""
    source = Path(path)
    if not source.is_absolute():
        source = _repo_root() / source
    source = source.resolve()
    if not source.is_file():
        raise FileNotFoundError(f"PolicyEngine pilot manifest not found: {source}")
    payload = json.loads(source.read_text(encoding="utf-8"))
    return _pilot_domain_from_mapping(payload)


def build_policyengine_pilot_package(
    domain: PolicyEnginePilotDomain,
) -> PolicyEnginePilotPackage:
    """Build a reviewed, executable PolicyEngine pilot package."""
    source_path = Path(domain.source_path)
    if not source_path.is_absolute():
        source_path = _repo_root() / source_path
    source_path = source_path.resolve()
    if not source_path.is_file():
        raise FileNotFoundError(f"Pilot source file not found: {source_path}")
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
        raise ValueError("pilot source SHA-256 does not match the manifest")
    if domain.review_state != PromotionState.PROMOTED:
        raise ValueError("pilot domain must be promoted before package generation")
    span = _find_excerpt_span(text, domain.source_excerpt)
    source_trace = SourceTrace(
        citation_path=domain.source_citation_path,
        source_sha256=domain.source_sha256,
        source_url=domain.source_url,
        retrieved_at=domain.retrieved_at,
        spans=(span,),
    )
    bridge = build_rules_as_code_bridge(
        source_section,
        concept=domain.concept,
        review_status="reviewed",
    )
    formula = RuleSpecFormula(
        formula_id=domain.formula_id,
        status=PromotionState.REVIEWED,
        expression=domain.expression,
        entity=domain.entity,
        period=domain.period,
        parameters=(domain.parameter_name,),
        source_spans=(span,),
    )
    oracle_ref = RuleSpecOracleFixtureRef(
        fixture_id="track79-policyengine-oracles",
        path=domain.oracle_fixture_path,
        description="Track 79 PolicyEngine oracle fixtures",
    )
    handoff = build_rulespec_promotion_handoff(
        bridge,
        source_trace=source_trace,
        review_state=domain.review_state,
        entities=({"entity_id": domain.entity, "label": domain.entity.title()},),
        periods=({"period_id": domain.period, "label": domain.period},),
        parameters={domain.parameter_name: domain.parameter_value},
        formulas=(formula,),
        oracle_fixture_refs=(oracle_ref,),
        reviewer_evidence=domain.reviewer_evidence,
        review_notes=f"Reviewed pilot domain: {domain.domain_title}",
    )
    validate_rulespec_promotion_handoff(handoff)
    results = _evaluate_oracle_cases(domain, formula)
    report = PolicyEnginePilotExecutionReport(
        package_name=domain.package_name,
        rulespec_id=handoff.rulespec_id,
        source_citation_path=domain.source_citation_path,
        source_sha256=domain.source_sha256,
        formula_id=domain.formula_id,
        results=results,
    )
    files = _render_policyengine_pilot_files(domain, handoff, report)
    return PolicyEnginePilotPackage(
        domain=domain,
        handoff=handoff,
        files=files,
        execution_report=report,
    )


def write_policyengine_pilot_package(
    package: PolicyEnginePilotPackage,
    output_dir: str | Path,
) -> Path:
    """Write the generated pilot package to *output_dir* and return the path."""
    root = Path(output_dir).resolve()
    for relative_path, content in package.files.items():
        target = _safe_output_path(root, relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    write_rulespec_promotion_handoff(package.handoff, root)
    return root


def render_policyengine_pilot_package_metadata_json(package: PolicyEnginePilotPackage) -> str:
    """Render package metadata as stable JSON."""
    return json.dumps(package.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_policyengine_pilot_oracles_json(domain: PolicyEnginePilotDomain) -> str:
    """Render pilot oracle fixtures as stable JSON."""
    payload = {
        "schema_version": "track79.policyengine-pilot.oracles.v1",
        "track_id": domain.track_id,
        "package_name": domain.package_name,
        "formula_id": domain.formula_id,
        "source_citation_path": domain.source_citation_path,
        "source_sha256": domain.source_sha256,
        "source_excerpt": domain.source_excerpt,
        "cases": [case.to_dict() for case in domain.oracle_cases],
    }
    return json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def render_policyengine_pilot_domain_yaml(domain: PolicyEnginePilotDomain) -> str:
    """Render the selected pilot domain as YAML for review."""
    return yaml.safe_dump(domain.to_dict(), sort_keys=True, allow_unicode=True)


def _evaluate_oracle_cases(
    domain: PolicyEnginePilotDomain,
    formula: RuleSpecFormula,
) -> tuple[PolicyEnginePilotExecutionResult, ...]:
    """Evaluate the pilot formula against each oracle case."""
    results: list[PolicyEnginePilotExecutionResult] = []
    for case in domain.oracle_cases:
        actual = _evaluate_commencement_formula(
            assessment_date=case.assessment_date,
            royal_assent_date=case.royal_assent_date,
            expression=formula.expression,
        )
        results.append(
            PolicyEnginePilotExecutionResult(
                case_id=case.case_id,
                expected_output=case.expected_output,
                actual_output=actual,
                passed=actual == case.expected_output,
                assessment_date=case.assessment_date,
                royal_assent_date=case.royal_assent_date,
            )
        )
    return tuple(results)


def _render_policyengine_pilot_files(
    domain: PolicyEnginePilotDomain,
    handoff: RuleSpecPromotionHandoff,
    report: PolicyEnginePilotExecutionReport,
) -> dict[str, str]:
    """Render the deterministic package files for the pilot."""
    package_name = _python_identifier(domain.package_name)
    class_name = _to_class_name(domain.variable_name)
    variable_module = _render_variable_module(domain, handoff, class_name)
    evaluation_module = _render_evaluation_module(class_name)
    return {
        "pyproject.toml": _render_pyproject(package_name),
        f"{package_name}/__init__.py": _render_init_file(domain, handoff),
        f"{package_name}/variables/__init__.py": 'from .commencement import ActCommenced\n\n__all__ = ["ActCommenced"]\n',
        f"{package_name}/variables/commencement.py": variable_module,
        f"{package_name}/parameters/commencement.yaml": _render_parameters_yaml(domain, handoff.rulespec_id),
        f"{package_name}/evaluate_oracles.py": evaluation_module,
        f"{package_name}/oracle_fixtures.json": render_policyengine_pilot_oracles_json(domain),
        "README.md": _render_readme(domain, handoff),
        "metadata.json": render_policyengine_pilot_package_metadata_json(
            PolicyEnginePilotPackage(domain=domain, handoff=handoff, files={}, execution_report=report)
        ),
        "pilot_domain.yaml": render_policyengine_pilot_domain_yaml(domain),
    }


def _render_init_file(
    domain: PolicyEnginePilotDomain,
    handoff: RuleSpecPromotionHandoff,
) -> str:
    return (
        '"""PolicyEngine pilot package generated by nlp-policy-nz."""\n\n'
        f'PACKAGE_NAME = {domain.package_name!r}\n'
        f'RULESPEC_ID = {handoff.rulespec_id!r}\n'
        f'SOURCE_CITATION_PATH = {domain.source_citation_path!r}\n'
        f'SOURCE_SHA256 = {domain.source_sha256!r}\n'
        f'REVIEW_STATE = {handoff.review_state.value!r}\n'
        "\n"
        "from .variables.commencement import ActCommenced\n\n"
        '__all__ = ["ActCommenced", "PACKAGE_NAME", "RULESPEC_ID"]\n'
    )


def _render_variable_module(
    domain: PolicyEnginePilotDomain,
    handoff: RuleSpecPromotionHandoff,
    class_name: str,
) -> str:
    return textwrap.dedent(
        f'''\
        """Executable commencement pilot formula generated from reviewed source."""

        from __future__ import annotations

        from datetime import date
        from typing import Any

        PACKAGE_NAME = {domain.package_name!r}
        RULESPEC_ID = {handoff.rulespec_id!r}
        SOURCE_CITATION_PATH = {domain.source_citation_path!r}
        SOURCE_EXCERPT = {domain.source_excerpt!r}
        SOURCE_SHA256 = {domain.source_sha256!r}
        REVIEW_STATE = {handoff.review_state.value!r}
        PARAMETER_NAME = {domain.parameter_name!r}
        DEFAULT_ROYAL_ASSENT_DATE = {domain.parameter_value!r}


        class {class_name}:
            """PolicyEngine-style variable for commencement after Royal assent."""

            value_type = "bool"
            entity = {domain.entity!r}
            definition_period = {domain.period!r}
            formula_id = {domain.formula_id!r}
            source_citation_path = SOURCE_CITATION_PATH
            source_excerpt = SOURCE_EXCERPT
            rulespec_id = RULESPEC_ID
            review_state = REVIEW_STATE

            @staticmethod
            def evaluate(*, assessment_date: str, royal_assent_date: str | None = None) -> bool:
                """Return whether the Act has commenced by *assessment_date*."""
                assent = _coerce_date(royal_assent_date or DEFAULT_ROYAL_ASSENT_DATE)
                assessment = _coerce_date(assessment_date)
                return assessment > assent

            def formula(self, person: object, period: object, parameters: dict[str, Any]) -> bool:
                """PolicyEngine-compatible formula hook for the pilot package."""
                assessment_date = _coerce_period_start(period)
                royal_assent_date = parameters.get(PARAMETER_NAME, DEFAULT_ROYAL_ASSENT_DATE)
                return self.evaluate(
                    assessment_date=assessment_date,
                    royal_assent_date=royal_assent_date,
                )


        def _coerce_date(value: object) -> date:
            if isinstance(value, date):
                return value
            if isinstance(value, str):
                return date.fromisoformat(value)
            raise TypeError("dates must be ISO strings or datetime.date values")


        def _coerce_period_start(period: object) -> str:
            if isinstance(period, str):
                return period
            start = getattr(period, "start", None)
            if isinstance(start, date):
                return start.isoformat()
            if isinstance(start, str):
                return start
            raise TypeError("period must expose a start date or ISO string")


        __all__ = ["{class_name}", "PACKAGE_NAME", "RULESPEC_ID"]
        '''
    )


def _render_evaluation_module(class_name: str) -> str:
    template = '''
        """Deterministic oracle execution helper for the generated pilot package."""

        from __future__ import annotations

        import json
        from pathlib import Path
        from typing import Any

        from .variables.commencement import {class_name} as PilotFormula


        def run_oracles(oracle_path: str | Path, *, output_path: str | Path | None = None) -> dict[str, Any]:
            payload = json.loads(Path(oracle_path).read_text(encoding="utf-8"))
            formula = PilotFormula()
            results = []
            for case in payload["cases"]:
                actual = formula.evaluate(
                    assessment_date=case["assessment_date"],
                    royal_assent_date=case.get("royal_assent_date"),
                )
                results.append(
                    {{
                        "case_id": case["case_id"],
                        "expected_output": case["expected_output"],
                        "actual_output": actual,
                        "passed": actual == case["expected_output"],
                    }}
                )
            report = {{
                "package_name": payload["package_name"],
                "formula_id": payload["formula_id"],
                "passed": all(item["passed"] for item in results),
                "results": results,
            }}
            if output_path is not None:
                Path(output_path).write_text(json.dumps(report, indent=2, sort_keys=True) + "\\n", encoding="utf-8")
            return report


        def main(argv: list[str] | None = None) -> int:
            import argparse

            parser = argparse.ArgumentParser(description="Run Track 79 oracle fixtures.")
            parser.add_argument("--oracle-path", required=True)
            parser.add_argument("--output", default=None)
            args = parser.parse_args(argv)
            report = run_oracles(args.oracle_path, output_path=args.output)
            print(json.dumps(report, indent=2, sort_keys=True))
            return 0 if report["passed"] else 1


        if __name__ == "__main__":
            raise SystemExit(main())
    '''
    return textwrap.dedent(template.format(class_name=class_name))


def _render_parameters_yaml(domain: PolicyEnginePilotDomain, rulespec_id: str) -> str:
    payload = {
        "metadata": {
            "package_name": domain.package_name,
            "rulespec_id": rulespec_id,
            "source_citation_path": domain.source_citation_path,
            "source_sha256": domain.source_sha256,
            "review_state": domain.review_state.value,
        },
        domain.parameter_name: {"value": domain.parameter_value},
    }
    return yaml.safe_dump(payload, sort_keys=True, allow_unicode=True)


def _render_pyproject(package_name: str) -> str:
    return textwrap.dedent(
        f"""\
        [project]
        name = "{package_name}"
        version = "0.0.0"
        description = "Generated PolicyEngine pilot package for Track 79"
        requires-python = ">=3.11"
        dependencies = []
        """
    )


def _render_readme(
    domain: PolicyEnginePilotDomain,
    handoff: RuleSpecPromotionHandoff,
) -> str:
    return textwrap.dedent(
        f"""\
        # {domain.package_name}

        Generated PolicyEngine pilot package for Track 79.

        - Domain: {domain.domain_title}
        - Source citation path: `{domain.source_citation_path}`
        - Source SHA-256: `{domain.source_sha256}`
        - RuleSpec ID: `{handoff.rulespec_id}`
        - Review state: `{handoff.review_state.value}`
        - Source excerpt: `{domain.source_excerpt}`

        The package ships one executable commencement formula and deterministic
        oracle fixtures. It is intentionally narrow and offline-friendly so the
        first PolicyEngine-style pilot can run in GitHub Actions.
        """
    )


def _evaluate_commencement_formula(
    *,
    assessment_date: str,
    royal_assent_date: str,
    expression: str,
) -> bool:
    if expression.strip() != "assessment_date > royal_assent_date":
        raise ValueError("unsupported pilot expression")
    return date.fromisoformat(assessment_date) > date.fromisoformat(royal_assent_date)


def _find_excerpt_span(text: str, excerpt: str) -> ExtractedSpan:
    start = text.find(excerpt)
    if start < 0:
        raise ValueError("source excerpt must appear in the pilot source text")
    end = start + len(excerpt)
    return ExtractedSpan(start=start, end=end, text=excerpt)


def _normalize_state(value: PromotionState | str) -> PromotionState:
    if isinstance(value, PromotionState):
        return value
    normalized = value.replace("-", "_").lower()
    try:
        return PromotionState(normalized)
    except ValueError as exc:
        raise ValueError("invalid pilot review state") from exc


def _require_nonempty(name: str, value: str) -> str:
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{name} is required")
    return stripped


def _validate_iso_date(name: str, value: str) -> str:
    text = _require_nonempty(name, value)
    try:
        date.fromisoformat(text)
    except ValueError as exc:
        raise ValueError(f"{name} must be an ISO date string") from exc
    return text


def _safe_output_path(root: Path, relative_path: str) -> Path:
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise ValueError("pilot package file paths must be relative")
    target = (root / candidate).resolve()
    if target != root and root not in target.parents:
        raise ValueError("pilot package file paths must stay within output_dir")
    return target


def _python_identifier(value: str) -> str:
    identifier = "".join(ch if ch.isalnum() or ch == "_" else "_" for ch in value.strip().lower()).strip("_")
    if not identifier:
        return "generated_rule"
    if identifier[0].isdigit():
        identifier = f"rule_{identifier}"
    return identifier


def _to_class_name(value: str) -> str:
    identifier = _python_identifier(value)
    return "".join(part.title() for part in identifier.split("_") if part)


def _pilot_domain_from_mapping(payload: dict[str, Any]) -> PolicyEnginePilotDomain:
    reviewer_evidence = tuple(
        RuleSpecReviewerEvidence(
            reviewer=item["reviewer"],
            reviewed_at=item["reviewed_at"],
            evidence_uri=item["evidence_uri"],
            notes=item.get("notes"),
        )
        for item in payload.get("reviewer_evidence", [])
    )
    oracle_cases_data = payload.get("oracle_cases")
    if oracle_cases_data is None:
        oracle_fixture_path = Path(payload.get("oracle_fixture_path", TRACK79_ORACLE_FIXTURE_PATH))
        if not oracle_fixture_path.is_absolute():
            oracle_fixture_path = _repo_root() / oracle_fixture_path
        oracle_payload = json.loads(oracle_fixture_path.read_text(encoding="utf-8"))
        if oracle_payload.get("source_sha256") != payload.get("source_sha256"):
            raise ValueError("oracle fixture checksum must match the pilot source checksum")
        oracle_cases_data = oracle_payload.get("cases", [])
    oracle_cases = tuple(PolicyEngineOracleCase(**item) for item in oracle_cases_data)
    review_state = _normalize_state(payload.get("review_state", PromotionState.PROMOTED))
    return PolicyEnginePilotDomain(
        track_id=payload["track_id"],
        package_name=payload.get("package_name", PACKAGE_NAME_DEFAULT),
        domain_id=payload["domain_id"],
        domain_title=payload["domain_title"],
        source_path=payload["source_path"],
        source_citation_path=payload["source_citation_path"],
        source_url=payload["source_url"],
        retrieved_at=payload["retrieved_at"],
        source_title=payload["source_title"],
        source_excerpt=payload["source_excerpt"],
        source_sha256=payload["source_sha256"],
        concept=payload["concept"],
        entity=payload["entity"],
        period=payload["period"],
        parameter_name=payload["parameter_name"],
        parameter_value=payload["parameter_value"],
        formula_id=payload["formula_id"],
        variable_name=payload["variable_name"],
        expression=payload["expression"],
        review_state=review_state,
        reviewer_evidence=reviewer_evidence,
        oracle_cases=oracle_cases,
        oracle_fixture_path=payload.get("oracle_fixture_path", str(TRACK79_ORACLE_FIXTURE_PATH)),
        review_note_path=payload.get("review_note_path", str(TRACK79_REVIEW_NOTE_PATH)),
        downstream_targets=tuple(payload.get("downstream_targets", ("policyengine",))),
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]
