"""Rules-as-code semantic bridge records for Track 27."""

from __future__ import annotations

import json
import keyword
import re
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from nlp_policy_nz.axiom import (
    DOCUMENT_TYPES,
    SourceSection,
    source_section_to_pipeline_record,
    source_verification_metadata,
)
from nlp_policy_nz.legal.effects import classify_legal_effect
from nlp_policy_nz.ontology.standards import LegislationProfile, build_schema_legislation

RAC_CONTEXT: dict[str, str] = {
    "schema": "https://schema.org/",
    "prov": "http://www.w3.org/ns/prov#",
    "lkif": "https://legal-nz.example.org/ontology/standards/lkif#",
    "legalruleml": "https://legal-nz.example.org/ontology/standards/legalruleml#",
    "rulespec": "https://github.com/TheAxiomFoundation/rulespec-nz#",
}


@dataclass(frozen=True)
class SourceAnchor:
    """Stable source text anchor for a rules-as-code bridge record."""

    citation_path: str
    source_url: str
    source_sha256: str
    jurisdiction: str = "NZ"
    document_type: str = "act"
    title: str | None = None

    def __post_init__(self) -> None:
        """Validate source anchor fields used by bridge exports."""
        _require_nonempty("citation_path", self.citation_path)
        _require_nonempty("source_url", self.source_url)
        _validate_sha256(self.source_sha256)
        _require_nonempty("jurisdiction", self.jurisdiction)
        _validate_document_type(self.document_type)

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-compatible source anchor."""
        return asdict(self)


@dataclass(frozen=True)
class NormSemantics:
    """Normative semantics inferred from one legal source section."""

    legal_effect: str | None
    deontic_modality: str | None = None
    trigger: str | None = None
    scope: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-compatible norm semantics record."""
        return asdict(self)


@dataclass(frozen=True)
class TemporalValidity:
    """Temporal validity bounds for a source-grounded rule candidate."""

    start: str | None = None
    end: str | None = None
    expression: str | None = None

    def to_dict(self) -> dict[str, str | None]:
        """Return a JSON-compatible temporal validity record."""
        return asdict(self)


@dataclass(frozen=True)
class PolicyTaxonomy:
    """Policy-domain classification hook for later SKOS/EuroVoc alignment."""

    scheme_id: str
    concept_id: str
    label: str

    def __post_init__(self) -> None:
        """Validate taxonomy identifiers used in bridge exports."""
        _require_nonempty("scheme_id", self.scheme_id)
        _require_nonempty("concept_id", self.concept_id)
        _require_nonempty("label", self.label)

    def to_dict(self) -> dict[str, str]:
        """Return a JSON-compatible taxonomy record."""
        return asdict(self)


@dataclass(frozen=True)
class RulesAsCodeBridgeRecord:
    """Deterministic bridge from source law to executable-rule metadata."""

    record_id: str
    source_anchor: SourceAnchor
    norm_semantics: NormSemantics
    temporal_validity: TemporalValidity
    taxonomy: PolicyTaxonomy
    rulespec: dict[str, Any]
    schema_legislation: dict[str, Any]
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate bridge record identity."""
        _require_nonempty("record_id", self.record_id)
        _rulespec_durable_id(self.rulespec)

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible bridge record."""
        return {
            "record_id": self.record_id,
            "source_anchor": self.source_anchor.to_dict(),
            "norm_semantics": self.norm_semantics.to_dict(),
            "temporal_validity": self.temporal_validity.to_dict(),
            "taxonomy": self.taxonomy.to_dict(),
            "rulespec": self.rulespec,
            "schema_legislation": self.schema_legislation,
            "provenance": dict(self.provenance),
        }

    def to_jsonld(self) -> dict[str, Any]:
        """Return a JSON-LD-style bridge payload."""
        payload = self.to_dict()
        payload["@context"] = RAC_CONTEXT
        payload["@type"] = "legalruleml:RuleStatement"
        payload["@id"] = _rulespec_durable_id(self.rulespec)
        return payload


@dataclass(frozen=True)
class PolicyEnginePackageSkeleton:
    """Deterministic package files for a future OpenFisca/PolicyEngine model."""

    package_name: str
    files: dict[str, str]
    source_citation_path: str
    rulespec_id: str

    def __post_init__(self) -> None:
        """Validate generated package manifest identity."""
        object.__setattr__(self, "package_name", _python_identifier(self.package_name))
        _require_nonempty("source_citation_path", self.source_citation_path)
        _require_nonempty("rulespec_id", self.rulespec_id)
        if not self.files:
            raise ValueError("files must contain at least one package artifact")
        for relative_path, content in self.files.items():
            _require_nonempty("file path", relative_path)
            if not isinstance(content, str):
                raise TypeError("file content must be text")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible skeleton manifest."""
        return {
            "package_name": self.package_name,
            "files": dict(sorted(self.files.items())),
            "source_citation_path": self.source_citation_path,
            "rulespec_id": self.rulespec_id,
        }


def build_rules_as_code_bridge(
    section: SourceSection,
    *,
    concept: str | None = None,
    taxonomy: PolicyTaxonomy | None = None,
    temporal_validity: TemporalValidity | None = None,
    provenance: dict[str, Any] | None = None,
) -> RulesAsCodeBridgeRecord:
    """Build one source-grounded rules-as-code bridge record."""
    pipeline_record = source_section_to_pipeline_record(section)
    legal_effect = classify_legal_effect(section.text)
    concept_id = concept or legal_effect or "source_text"
    norm = _norm_semantics(section.text, legal_effect)
    verification = source_verification_metadata(section.metadata, concept=concept_id)
    profile = LegislationProfile(
        identifier=section.metadata.citation_path,
        name=section.metadata.title or section.metadata.citation_path,
        jurisdiction=section.metadata.jurisdiction,
        legislation_type=section.metadata.document_type,
        date_published=section.metadata.effective_date,
        url=section.metadata.source_url,
        same_as=(verification["rulespec_reference"]["durable_id"],),
    )
    return RulesAsCodeBridgeRecord(
        record_id=pipeline_record.doc_id,
        source_anchor=SourceAnchor(
            citation_path=section.metadata.citation_path,
            source_url=section.metadata.source_url,
            source_sha256=section.metadata.checksum_sha256,
            jurisdiction=section.metadata.jurisdiction,
            document_type=section.metadata.document_type,
            title=section.metadata.title,
        ),
        norm_semantics=norm,
        temporal_validity=temporal_validity
        or TemporalValidity(start=section.metadata.effective_date),
        taxonomy=taxonomy
        or PolicyTaxonomy(
            scheme_id="nz-local-policy-domain",
            concept_id="unspecified",
            label="Unspecified policy domain",
        ),
        rulespec=verification,
        schema_legislation=build_schema_legislation(profile),
        provenance=provenance
        or {
            "prov:wasGeneratedBy": "nlp-policy-nz.rules-as-code-bridge",
            "prov:wasDerivedFrom": section.metadata.source_url,
        },
    )


def build_policyengine_package_skeleton(
    record: RulesAsCodeBridgeRecord,
    *,
    package_name: str = "policyengine_nz_generated",
) -> PolicyEnginePackageSkeleton:
    """Build an offline OpenFisca/PolicyEngine-style package skeleton.

    The generated files are intentionally placeholders. They make source,
    entity, variable, period, and parameter decisions explicit without claiming
    executable parity with an external OpenFisca or PolicyEngine package.
    """
    safe_package = _python_identifier(package_name)
    variable_name = _python_identifier(
        record.rulespec["rulespec_reference"]["concept"] or "generated_rule"
    )
    citation = record.source_anchor.citation_path
    rulespec_id = record.rulespec["rulespec_reference"]["durable_id"]
    legal_effect = record.norm_semantics.legal_effect or "unknown"
    source_sha = record.source_anchor.source_sha256
    files = {
        "pyproject.toml": _package_pyproject(safe_package),
        f"{safe_package}/__init__.py": '"""Generated NZ rules package skeleton."""\n',
        f"{safe_package}/variables/__init__.py": "",
        f"{safe_package}/variables/generated.py": _variable_module(
            variable_name=variable_name,
            citation=citation,
            rulespec_id=rulespec_id,
            legal_effect=legal_effect,
            source_sha=source_sha,
        ),
        f"{safe_package}/parameters/generated.yaml": _parameter_yaml(
            citation=citation,
            source_sha=source_sha,
        ),
        "README.md": _package_readme(
            package_name=safe_package,
            citation=citation,
            rulespec_id=rulespec_id,
        ),
    }
    return PolicyEnginePackageSkeleton(
        package_name=safe_package,
        files=files,
        source_citation_path=citation,
        rulespec_id=rulespec_id,
    )


def write_policyengine_package_skeleton(
    skeleton: PolicyEnginePackageSkeleton,
    output_dir: str | Path,
) -> Path:
    """Write a package skeleton to *output_dir* and return the directory path."""
    root = Path(output_dir).resolve()
    for relative_path, content in skeleton.files.items():
        target = _safe_output_path(root, relative_path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    return root


def render_rules_as_code_bridge_json(record: RulesAsCodeBridgeRecord) -> str:
    """Render a bridge record as stable formatted JSON."""
    return json.dumps(record.to_jsonld(), indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def write_rules_as_code_bridge_json(
    record: RulesAsCodeBridgeRecord,
    path: str | Path,
) -> Path:
    """Write a bridge record to disk and return the output path."""
    target = Path(path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_rules_as_code_bridge_json(record), encoding="utf-8")
    return target


def _safe_output_path(root: Path, relative_path: str) -> Path:
    """Resolve a generated file path and reject writes outside *root*."""
    candidate = Path(relative_path)
    if candidate.is_absolute():
        raise ValueError("skeleton file paths must be relative")
    target = (root / candidate).resolve()
    if target != root and root not in target.parents:
        raise ValueError("skeleton file paths must stay within output_dir")
    return target


def _rulespec_durable_id(rulespec: dict[str, Any]) -> str:
    """Return a required RuleSpec durable ID from a bridge rulespec payload."""
    reference = rulespec.get("rulespec_reference")
    if not isinstance(reference, dict):
        raise ValueError("rulespec.rulespec_reference is required")
    durable_id = reference.get("durable_id")
    if not isinstance(durable_id, str):
        raise ValueError("rulespec.rulespec_reference.durable_id is required")
    return _require_nonempty("rulespec.rulespec_reference.durable_id", durable_id)


def _norm_semantics(text: str, legal_effect: str | None) -> NormSemantics:
    """Infer a compact norm-semantics record from source text."""
    trigger = _first_deontic_trigger(text)
    return NormSemantics(
        legal_effect=legal_effect,
        deontic_modality=(
            legal_effect if legal_effect in {"obligation", "prohibition", "permission"} else None
        ),
        trigger=trigger,
        scope=_scope_after_trigger(text, trigger) if trigger else None,
    )


def _first_deontic_trigger(text: str) -> str | None:
    """Return the first simple deontic trigger in source order."""
    matches = [
        (match.start(), match.group(0).lower())
        for match in re.finditer(
            r"\b(?:must not|shall not|need not|must|shall|may)\b",
            text,
            re.IGNORECASE,
        )
    ]
    return min(matches)[1] if matches else None


def _scope_after_trigger(text: str, trigger: str) -> str | None:
    """Return text after a trigger up to common clause punctuation."""
    match = re.search(re.escape(trigger), text, re.IGNORECASE)
    if match is None:
        return None
    suffix = text[match.end() :].strip()
    scope = re.split(r"[.;]\s*", suffix, maxsplit=1)[0].strip()
    return scope or None


def _python_identifier(value: str) -> str:
    """Return a safe lowercase Python identifier."""
    identifier = re.sub(r"\W+", "_", value.strip().lower()).strip("_")
    if not identifier:
        return "generated_rule"
    if identifier[0].isdigit():
        identifier = f"rule_{identifier}"
    if keyword.iskeyword(identifier):
        identifier = f"{identifier}_rule"
    return identifier


def _require_nonempty(name: str, value: str) -> str:
    """Return a stripped required value or raise a contract error."""
    stripped = value.strip()
    if not stripped:
        raise ValueError(f"{name} is required")
    return stripped


def _validate_document_type(value: str) -> str:
    """Return a supported source document type or raise a contract error."""
    stripped = value.strip()
    if stripped not in DOCUMENT_TYPES:
        allowed = ", ".join(DOCUMENT_TYPES)
        raise ValueError(f"document_type must be one of: {allowed}")
    return stripped


def _validate_sha256(value: str) -> str:
    """Return a valid lowercase SHA-256 hex digest or raise a contract error."""
    stripped = value.strip()
    if not re.fullmatch(r"[0-9a-f]{64}", stripped):
        raise ValueError("source_sha256 must be a lowercase 64-character SHA-256 hex digest")
    return stripped


def _package_pyproject(package_name: str) -> str:
    """Return pyproject metadata for the generated skeleton."""
    return (
        "[project]\n"
        f'name = "{package_name}"\n'
        'version = "0.0.0"\n'
        'description = "Generated NZ rules-as-code package skeleton"\n'
        'requires-python = ">=3.11"\n'
        "dependencies = []\n"
    )


def _variable_module(
    *,
    variable_name: str,
    citation: str,
    rulespec_id: str,
    legal_effect: str,
    source_sha: str,
) -> str:
    """Return a placeholder variable module with source provenance."""
    return (
        '"""Generated variable placeholders from nlp-policy-nz."""\n\n'
        f"SOURCE_CITATION_PATH = {citation!r}\n"
        f"RULESPEC_ID = {rulespec_id!r}\n"
        f"SOURCE_SHA256 = {source_sha!r}\n\n"
        f"class {variable_name}:\n"
        f'    """Placeholder for {legal_effect} derived from {citation}."""\n\n'
        '    value_type = "bool"\n'
        '    entity = "Person"\n'
        '    definition_period = "day"\n\n'
        "    def formula(self, person, period, parameters):\n"
        '        """Raise until legal facts and oracle fixtures are supplied."""\n'
        "        raise NotImplementedError(\n"
        '            "Generated skeleton requires reviewed formula semantics and oracle fixtures."\n'
        "        )\n"
    )


def _parameter_yaml(*, citation: str, source_sha: str) -> str:
    """Return a placeholder parameter YAML file."""
    return (
        "metadata:\n"
        f"  source_citation_path: {citation}\n"
        f"  source_sha256: {source_sha}\n"
        "  status: placeholder\n"
        "values: {}\n"
    )


def _package_readme(*, package_name: str, citation: str, rulespec_id: str) -> str:
    """Return README text for the generated skeleton."""
    return (
        f"# {package_name}\n\n"
        "Generated by `nlp-policy-nz` as a rules-as-code package skeleton.\n\n"
        f"- Source citation path: `{citation}`\n"
        f"- RuleSpec ID: `{rulespec_id}`\n"
        "- Status: non-executable placeholder until reviewed formulas, target "
        "entities, parameters, periods, and oracle fixtures are supplied.\n"
    )
