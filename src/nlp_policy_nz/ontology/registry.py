"""Track 26 ontology standards registry and manifest writer.

This module keeps the registry intentionally conservative: each entry states
what the repository currently represents, which upstream standard anchors it,
and what remains blocked. The output is deterministic JSON intended for
checked-in publication under ``data/ontologies/``.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Final, Literal

ImplementationStatus = Literal["implemented", "partial", "scaffolded", "adjacent", "missing"]
BlockerType = Literal["none", "data", "specification", "integration"]

IMPLEMENTATION_STATUSES: Final[tuple[ImplementationStatus, ...]] = (
    "implemented",
    "partial",
    "scaffolded",
    "adjacent",
    "missing",
)
BLOCKER_TYPES: Final[tuple[BlockerType, ...]] = (
    "none",
    "data",
    "specification",
    "integration",
)

TRACK26_MANIFEST_FILENAME: Final[str] = "track26_standards_registry.json"
TRACK26_MANIFEST_PATH: Final[Path] = Path("data") / "ontologies" / TRACK26_MANIFEST_FILENAME
UPSTREAM_LICENSE_UNVERIFIED: Final[str] = "upstream-verify: exact license not confirmed"
W3C_DOCUMENT_LICENSE: Final[str] = "W3C Document License"


@dataclass(frozen=True, slots=True)
class StandardsRegistryEntry:
    """One upstream ontology or standards surface in the Track 26 registry."""

    standard: str
    source_url: str
    source_license: str
    local_representation_paths: tuple[str, ...]
    implementation_status: ImplementationStatus
    blocker_type: BlockerType
    blocker_source: str
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert the registry entry to JSON-serializable data."""
        return {
            "standard": self.standard,
            "source_url": self.source_url,
            "source_license": self.source_license,
            "local_representation_paths": list(self.local_representation_paths),
            "implementation_status": self.implementation_status,
            "blocker_type": self.blocker_type,
            "blocker_source": self.blocker_source,
            "notes": self.notes,
        }


TRACK26_STANDARDS_REGISTRY: Final[tuple[StandardsRegistryEntry, ...]] = (
    StandardsRegistryEntry(
        standard="ELI",
        source_url="https://eur-lex.europa.eu/eli-register/resources.html",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/schema/akn_v3.py",
            "src/nlp_policy_nz/quality/track25_ontology_coverage.py",
        ),
        implementation_status="missing",
        blocker_type="data",
        blocker_source="official NZ legislation metadata export and URI template inventory",
        notes="ELI source anchoring is not yet implemented in the repo.",
    ),
    StandardsRegistryEntry(
        standard="ELI-DL",
        source_url="https://eur-lex.europa.eu/eli-register/resources.html",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/schema/akn_v3.py",
            "src/nlp_policy_nz/quality/track25_ontology_coverage.py",
        ),
        implementation_status="missing",
        blocker_type="data",
        blocker_source="official NZ legislation metadata export and draft-legislation descriptors",
        notes="Draft-legislation metadata is still absent.",
    ),
    StandardsRegistryEntry(
        standard="ECLI",
        source_url="https://e-justice.europa.eu/ecli/",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/schema/akn_v3.py",
            "src/nlp_policy_nz/quality/track25_ontology_coverage.py",
        ),
        implementation_status="missing",
        blocker_type="data",
        blocker_source="NZ judgment corpus with stable case-law identifiers",
        notes="Court decisions are not yet normalised into ECLI-compatible identifiers.",
    ),
    StandardsRegistryEntry(
        standard="EuroVoc",
        source_url="https://op.europa.eu/en/web/eu-vocabularies/eurovoc",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/kb/wikidata_kg.py",
            "src/nlp_policy_nz/quality/track25_ontology_coverage.py",
        ),
        implementation_status="missing",
        blocker_type="data",
        blocker_source="EuroVoc concept scheme and NZ policy-domain crosswalk",
        notes="No controlled policy-domain thesaurus is wired into the repo yet.",
    ),
    StandardsRegistryEntry(
        standard="SKOS",
        source_url="https://www.w3.org/TR/skos-reference/",
        source_license=W3C_DOCUMENT_LICENSE,
        local_representation_paths=(
            "src/nlp_policy_nz/kb/wikidata_kg.py",
            "data/ontologies/nz_wikidata_map.ttl",
        ),
        implementation_status="missing",
        blocker_type="specification",
        blocker_source="local controlled vocabulary model for policy domains and provision classification",
        notes="SKOS is the missing substrate for a policy taxonomy layer.",
    ),
    StandardsRegistryEntry(
        standard="CEN MetaLex",
        source_url="https://www.metalex.eu/",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/schema/akn_v3.py",
            "src/nlp_policy_nz/universal_framework_v3.py",
        ),
        implementation_status="missing",
        blocker_type="integration",
        blocker_source="machine-readable legislation corpus and schema crosswalk",
        notes="No MetaLex emitter or importer exists yet.",
    ),
    StandardsRegistryEntry(
        standard="USLM",
        source_url="https://uscode.house.gov/download/download.shtml",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/schema/akn_v3.py",
            "src/nlp_policy_nz/universal_framework_v3.py",
        ),
        implementation_status="missing",
        blocker_type="specification",
        blocker_source="US legislative XML benchmark set and crosswalk",
        notes="The repo has no USLM mapper or comparator yet.",
    ),
    StandardsRegistryEntry(
        standard="LexML",
        source_url="https://projeto.lexml.gov.br/",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/schema/akn_v3.py",
            "src/nlp_policy_nz/quality/track25_ontology_coverage.py",
        ),
        implementation_status="missing",
        blocker_type="data",
        blocker_source="LexML URI template inventory and legislation reference set",
        notes="Stable LexML-style references and metadata are not modelled yet.",
    ),
    StandardsRegistryEntry(
        standard="schema.org/Legislation",
        source_url="https://schema.org/Legislation",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/kb/wikidata_kg.py",
            "data/ontologies/nz_wikidata_map.ttl",
        ),
        implementation_status="partial",
        blocker_type="specification",
        blocker_source="complete legislation publication metadata model with stable landing-page fields",
        notes="The repo exports JSON-LD, but the Legislation profile is incomplete.",
    ),
    StandardsRegistryEntry(
        standard="LKIF",
        source_url="https://github.com/RinkeHoekstra/lkif-core",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/legal/effects.py",
            "src/nlp_policy_nz/legal/modality.py",
        ),
        implementation_status="partial",
        blocker_type="data",
        blocker_source="normalized deontic and legal-effect annotation corpus",
        notes="The repo captures legal effects, but only as an LKIF-inspired layer.",
    ),
    StandardsRegistryEntry(
        standard="full LKIF",
        source_url="https://github.com/RinkeHoekstra/lkif-core",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/legal/effects.py",
            "src/nlp_policy_nz/legal/modality.py",
            "src/nlp_policy_nz/quality/track25_ontology_coverage.py",
        ),
        implementation_status="missing",
        blocker_type="specification",
        blocker_source="formal semantics for obligations, permissions, prohibitions, powers, and exceptions",
        notes="The complete normative semantics layer is still open.",
    ),
    StandardsRegistryEntry(
        standard="LegalRuleML",
        source_url="https://www.oasis-open.org/committees/legalruleml/",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/universal_framework_v3.py",
            "tests/test_framework_rac.py",
        ),
        implementation_status="scaffolded",
        blocker_type="integration",
        blocker_source="rule serialization and validation pipeline for formal norm semantics",
        notes="Prototype emit hooks exist, but not a validated emitter.",
    ),
    StandardsRegistryEntry(
        standard="full LegalRuleML",
        source_url="https://www.oasis-open.org/committees/legalruleml/",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/universal_framework_v3.py",
            "tests/test_framework_rac.py",
        ),
        implementation_status="missing",
        blocker_type="specification",
        blocker_source="complete rule semantics model with applicability and defeasibility",
        notes="No standards-complete emitter exists yet.",
    ),
    StandardsRegistryEntry(
        standard="Popolo",
        source_url="https://www.popoloproject.com/",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/linked_data/foaf.py",
            "src/nlp_policy_nz/linked_data/rdf.py",
        ),
        implementation_status="missing",
        blocker_type="data",
        blocker_source="parliamentary actor, office, and membership roster",
        notes="No Popolo-compatible people/offices graph exists yet.",
    ),
    StandardsRegistryEntry(
        standard="W3C ORG",
        source_url="https://www.w3.org/TR/vocab-org/",
        source_license=W3C_DOCUMENT_LICENSE,
        local_representation_paths=(
            "src/nlp_policy_nz/linked_data/foaf.py",
            "src/nlp_policy_nz/linked_data/rdf.py",
        ),
        implementation_status="missing",
        blocker_type="data",
        blocker_source="official organization chart export and role roster",
        notes="Government and parliamentary organization structures are still absent.",
    ),
    StandardsRegistryEntry(
        standard="DCAT",
        source_url="https://www.w3.org/TR/vocab-dcat-3/",
        source_license=W3C_DOCUMENT_LICENSE,
        local_representation_paths=(
            "src/nlp_policy_nz/provenance/serializer.py",
            "src/nlp_policy_nz/quality/track25_ontology_coverage.py",
        ),
        implementation_status="missing",
        blocker_type="data",
        blocker_source="dataset catalog and provenance inventory",
        notes="Dataset-level catalog metadata is not published as DCAT yet.",
    ),
    StandardsRegistryEntry(
        standard="DCAT-AP",
        source_url="https://semiceu.github.io/DCAT-AP/releases/",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/provenance/serializer.py",
            "src/nlp_policy_nz/quality/track25_ontology_coverage.py",
        ),
        implementation_status="missing",
        blocker_type="specification",
        blocker_source="profiled catalogue metadata aligned with DCAT-AP publication practices",
        notes="A profile-valid catalog layer is not present yet.",
    ),
    StandardsRegistryEntry(
        standard="OpenFisca",
        source_url="https://openfisca.org/doc/",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/universal_framework_v3.py",
            "src/nlp_policy_nz/quality/track25_ontology_coverage.py",
        ),
        implementation_status="adjacent",
        blocker_type="specification",
        blocker_source="variable, parameter, and entity inventory with time-varying parameter histories",
        notes="The repo is adjacent to OpenFisca concepts, but lacks a formal ontology bridge.",
    ),
    StandardsRegistryEntry(
        standard="PolicyEngine",
        source_url="https://policyengine.org/",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/universal_framework_v3.py",
            "src/nlp_policy_nz/quality/track25_ontology_coverage.py",
        ),
        implementation_status="adjacent",
        blocker_type="specification",
        blocker_source="policy variable and parameter inventory plus entity-period semantics",
        notes="The repo is adjacent to PolicyEngine concepts, but not yet formalised.",
    ),
    StandardsRegistryEntry(
        standard="formal OpenFisca/PolicyEngine variable/parameter/entity ontology",
        source_url="https://openfisca.org/doc/",
        source_license=UPSTREAM_LICENSE_UNVERIFIED,
        local_representation_paths=(
            "src/nlp_policy_nz/universal_framework_v3.py",
            "src/nlp_policy_nz/legal/effects.py",
            "src/nlp_policy_nz/quality/track25_ontology_coverage.py",
        ),
        implementation_status="missing",
        blocker_type="specification",
        blocker_source="crosswalk of entities, variables, parameters, formulas, and periods",
        notes="This bridge remains the explicit ontology layer for rules-as-code tooling.",
    ),
)


def repo_root() -> Path:
    """Return the repository root for manifest output paths."""
    return Path(__file__).resolve().parents[3]


def build_track26_standards_registry() -> list[dict[str, Any]]:
    """Build the registry rows as deterministic JSON-ready data."""
    rows = [entry.to_dict() for entry in TRACK26_STANDARDS_REGISTRY]
    return sorted(rows, key=lambda row: row["standard"].casefold())


def _count_by(values: list[dict[str, Any]], field: str, choices: tuple[str, ...]) -> dict[str, int]:
    counts = {choice: 0 for choice in choices}
    for row in values:
        key = str(row[field])
        counts[key] = counts.get(key, 0) + 1
    return counts


def _license_assumptions(entries: list[dict[str, Any]]) -> list[dict[str, str]]:
    assumptions: list[dict[str, str]] = []
    for row in entries:
        license_value = str(row["source_license"])
        if license_value.startswith("upstream-verify:"):
            assumptions.append(
                {
                    "standard": str(row["standard"]),
                    "source_url": str(row["source_url"]),
                    "source_license": license_value,
                }
            )
    return assumptions


def build_track26_standards_manifest() -> dict[str, Any]:
    """Build the full Track 26 standards manifest."""
    entries = build_track26_standards_registry()
    return {
        "schema_version": "1.0",
        "registry_name": "track26_standards_registry",
        "entries": entries,
        "summary": {
            "entry_count": len(entries),
            "implementation_status_counts": _count_by(entries, "implementation_status", IMPLEMENTATION_STATUSES),
            "blocker_type_counts": _count_by(entries, "blocker_type", BLOCKER_TYPES),
            "license_assumption_count": len(_license_assumptions(entries)),
        },
        "license_assumptions": _license_assumptions(entries),
        "registry_notes": (
            "Implementation status reflects the current repo surface, not upstream "
            "standard maturity."
        ),
    }


def write_track26_standards_manifest(output_path: Path | None = None) -> Path:
    """Write the Track 26 manifest to disk and return its path."""
    target = output_path or (repo_root() / TRACK26_MANIFEST_PATH)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = build_track26_standards_manifest()
    target.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return target


__all__ = [
    "BLOCKER_TYPES",
    "BlockerType",
    "IMPLEMENTATION_STATUSES",
    "ImplementationStatus",
    "StandardsRegistryEntry",
    "TRACK26_MANIFEST_FILENAME",
    "TRACK26_MANIFEST_PATH",
    "TRACK26_STANDARDS_REGISTRY",
    "UPSTREAM_LICENSE_UNVERIFIED",
    "W3C_DOCUMENT_LICENSE",
    "build_track26_standards_manifest",
    "build_track26_standards_registry",
    "repo_root",
    "write_track26_standards_manifest",
]
