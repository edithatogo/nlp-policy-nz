"""Ontology standards registry and round-trip helpers for Track 26."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Final, Literal
from urllib.parse import urlsplit

from nlp_policy_nz.kb.wikidata_kg import LOCAL_ONTOLOGY_URI

CoverageStatus = Literal["implemented", "partial", "prototype", "adjacent", "missing"]
BlockerType = Literal["none", "source_data", "specification", "validation", "integration"]

STANDARD_MANIFEST_PATH: Final[Path] = (
    Path(__file__).resolve().parents[3] / "data" / "ontologies" / "ontology_standards_manifest.json"
)
STANDARD_NAMESPACE_BASE: Final[str] = LOCAL_ONTOLOGY_URI.rstrip("/") + "/standards/"
ELI_URI_BASE: Final[str] = "https://legal-nz.example.org/ontology/eli/"
ELI_DL_URI_BASE: Final[str] = "https://legal-nz.example.org/ontology/eli-dl/"
ECLI_PREFIX: Final[str] = "ECLI"
EUROVOC_URI_BASE: Final[str] = "http://eurovoc.europa.eu/"
SKOS_NAMESPACE: Final[str] = "http://www.w3.org/2004/02/skos/core#"


@dataclass(frozen=True, slots=True)
class OntologyStandard:
    """Registry record for one external ontology standard."""

    standard_id: str
    label: str
    source_url: str
    license: str
    namespace: str
    local_representation: str
    coverage_status: CoverageStatus
    blocker_type: BlockerType = "none"
    blocker_reason: str = ""
    uri_template: str = ""
    aliases: tuple[str, ...] = ()
    notes: str = ""
    round_trip_supported: bool = False

    def with_aliases(self, *aliases: str) -> OntologyStandard:
        """Return a copy with a replacement alias set."""
        return replace(self, aliases=tuple(aliases))

    def to_dict(self) -> dict[str, Any]:
        """Convert the standard record to JSON-serialisable data."""
        return {
            "standard_id": self.standard_id,
            "label": self.label,
            "source_url": self.source_url,
            "license": self.license,
            "namespace": self.namespace,
            "local_representation": self.local_representation,
            "coverage_status": self.coverage_status,
            "blocker_type": self.blocker_type,
            "blocker_reason": self.blocker_reason,
            "uri_template": self.uri_template,
            "aliases": list(self.aliases),
            "notes": self.notes,
            "round_trip_supported": self.round_trip_supported,
        }


@dataclass(frozen=True, slots=True)
class LegislativeResource:
    """Local ELI/ELI-DL-compatible legislation identifier record."""

    jurisdiction: str
    authority: str
    year: int
    document_kind: str
    number: str
    version: str | None = None
    language: str | None = None
    draft_stage: str | None = None

    def with_draft_stage(self, draft_stage: str | None) -> LegislativeResource:
        """Return a copy with a different draft stage."""
        return replace(self, draft_stage=draft_stage)


@dataclass(frozen=True, slots=True)
class ECLIIdentifier:
    """Stable ECLI identifier with round-trip parsing support."""

    country_code: str
    court_code: str
    year: int
    sequence: str


@dataclass(frozen=True, slots=True)
class ControlledConcept:
    """SKOS-compatible concept record for EuroVoc and local taxonomies."""

    scheme_id: str
    concept_id: str
    pref_label: str
    language: str = "en"
    notation: str = ""
    broader: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class LegislationProfile:
    """schema.org/Legislation JSON-LD record."""

    identifier: str
    name: str
    jurisdiction: str
    legislation_type: str = "Act"
    date_published: str | None = None
    url: str | None = None
    same_as: tuple[str, ...] = ()


STANDARD_REGISTRY: Final[tuple[OntologyStandard, ...]] = (
    OntologyStandard(
        standard_id="eli",
        label="ELI",
        source_url="https://eur-lex.europa.eu/eli-register/what_is_eli.html",
        license="European Union reuse policy",
        namespace=f"{STANDARD_NAMESPACE_BASE}eli#",
        local_representation="LegislativeResource -> URI template",
        coverage_status="implemented",
        uri_template="{base}/eli/{jurisdiction}/{authority}/{year}/{document_kind}/{number}",
        aliases=("European Legislation Identifier",),
        notes="Supports stable legislative identifiers and metadata alignment.",
        round_trip_supported=True,
    ),
    OntologyStandard(
        standard_id="eli_dl",
        label="ELI-DL",
        source_url="https://eur-lex.europa.eu/eli-register/what_is_eli.html",
        license="European Union reuse policy",
        namespace=f"{STANDARD_NAMESPACE_BASE}eli-dl#",
        local_representation="LegislativeResource -> draft URI template",
        coverage_status="implemented",
        uri_template=(
            "{base}/eli-dl/{jurisdiction}/{authority}/{year}/{document_kind}/{draft_stage}/{number}"
        ),
        aliases=("ELI DL", "ELI Draft Legislation"),
        notes="Draft-stage metadata is represented as a first-class path segment.",
        round_trip_supported=True,
    ),
    OntologyStandard(
        standard_id="ecli",
        label="ECLI",
        source_url=(
            "https://e-justice.europa.eu/topics/legislation-and-case-law/"
            "european-case-law-identifier-ecli-search-engine_en"
        ),
        license="European Union reuse policy",
        namespace=f"{STANDARD_NAMESPACE_BASE}ecli#",
        local_representation="ECLIIdentifier -> canonical identifier string",
        coverage_status="implemented",
        uri_template="ECLI:{country}:{court}:{year}:{sequence}",
        aliases=("European Case Law Identifier",),
        notes="Provides stable case-law identifiers with a reversible code format.",
        round_trip_supported=True,
    ),
    OntologyStandard(
        standard_id="eurovoc",
        label="EuroVoc",
        source_url="https://op.europa.eu/en/web/eu-vocabularies/eurovoc",
        license="European Union reuse policy",
        namespace=f"{STANDARD_NAMESPACE_BASE}eurovoc#",
        local_representation="ControlledConcept -> SKOS JSON-LD",
        coverage_status="implemented",
        uri_template="{scheme}/{concept_id}",
        aliases=("EU Vocabularies EuroVoc",),
        notes="Useful for policy-domain tagging and crosswalks.",
        round_trip_supported=True,
    ),
    OntologyStandard(
        standard_id="skos",
        label="SKOS",
        source_url="https://www.w3.org/TR/skos-reference/",
        license="W3C Document License",
        namespace=f"{STANDARD_NAMESPACE_BASE}skos#",
        local_representation="ControlledConcept -> SKOS JSON-LD",
        coverage_status="implemented",
        uri_template="{scheme}/{concept_id}",
        aliases=("Simple Knowledge Organization System",),
        notes="Supports local controlled vocabularies and broader/narrower links.",
        round_trip_supported=True,
    ),
    OntologyStandard(
        standard_id="metalex",
        label="CEN MetaLex",
        source_url="https://www.metalex.eu/",
        license="official license not stated on the public homepage",
        namespace=f"{STANDARD_NAMESPACE_BASE}metalex#",
        local_representation="registry entry and namespace anchor",
        coverage_status="missing",
        blocker_type="source_data",
        blocker_reason="No source corpus or official schema bundle is checked into the repo.",
        notes="Track 26 records the standard as a blocker until source data is available.",
    ),
    OntologyStandard(
        standard_id="uslm",
        label="USLM",
        source_url="https://www.govinfo.gov/help/uslm",
        license="official license not stated on the public help page",
        namespace=f"{STANDARD_NAMESPACE_BASE}uslm#",
        local_representation="registry entry and namespace anchor",
        coverage_status="missing",
        blocker_type="source_data",
        blocker_reason="No source schema or legislative corpus has been imported for USLM.",
        notes="Useful for comparative legislative document modelling.",
    ),
    OntologyStandard(
        standard_id="lexml",
        label="LexML",
        source_url="https://www.lexml.gov.br/",
        license="official license not stated on the public portal",
        namespace=f"{STANDARD_NAMESPACE_BASE}lexml#",
        local_representation="registry entry and namespace anchor",
        coverage_status="missing",
        blocker_type="source_data",
        blocker_reason="The repository does not yet contain a LexML schema or sample corpus.",
        notes="Recorded as a blocked standard until source data is available.",
    ),
    OntologyStandard(
        standard_id="schema_org_legislation",
        label="schema.org/Legislation",
        source_url="https://schema.org/Legislation",
        license="Creative Commons Attribution-ShareAlike 3.0",
        namespace=f"{STANDARD_NAMESPACE_BASE}schema-org-legislation#",
        local_representation="LegislationProfile -> JSON-LD",
        coverage_status="partial",
        blocker_type="specification",
        blocker_reason="The repo has a local JSON-LD record shape but not a full field-level mapping.",
        uri_template="{base}/schema-org-legislation/{identifier}",
        aliases=("schema.org Legislation",),
        notes="Supports discoverable publication metadata and linked-data interoperability.",
        round_trip_supported=True,
    ),
    OntologyStandard(
        standard_id="lkif",
        label="LKIF",
        source_url="https://www.estrellaproject.org/lkif-core/",
        license="official license not stated on the public project site",
        namespace=f"{STANDARD_NAMESPACE_BASE}lkif#",
        local_representation="registry entry and normative-effect hook",
        coverage_status="prototype",
        blocker_type="integration",
        blocker_reason="The repo only has LKIF-inspired deontic hooks, not a full semantics layer.",
        notes="Useful as a bridge to full normative semantics work.",
    ),
    OntologyStandard(
        standard_id="full_lkif",
        label="full LKIF",
        source_url="https://www.estrellaproject.org/lkif-core/",
        license="official license not stated on the public project site",
        namespace=f"{STANDARD_NAMESPACE_BASE}full-lkif#",
        local_representation="registry entry only",
        coverage_status="missing",
        blocker_type="specification",
        blocker_reason="The full norm taxonomy, defeasibility model, and exception semantics are missing.",
        notes="Explicitly tracked as a standards blocker.",
    ),
    OntologyStandard(
        standard_id="legalruleml",
        label="LegalRuleML",
        source_url="https://docs.oasis-open.org/legalruleml/",
        license="OASIS specification license",
        namespace=f"{STANDARD_NAMESPACE_BASE}legalruleml#",
        local_representation="registry entry and prototype hook",
        coverage_status="prototype",
        blocker_type="integration",
        blocker_reason="Only hook-level support exists; no serialisable rule semantics are exposed yet.",
        notes="Provides a bridge point for later formal rule emission work.",
    ),
    OntologyStandard(
        standard_id="full_legalruleml",
        label="full LegalRuleML",
        source_url="https://docs.oasis-open.org/legalruleml/",
        license="OASIS specification license",
        namespace=f"{STANDARD_NAMESPACE_BASE}full-legalruleml#",
        local_representation="registry entry only",
        coverage_status="missing",
        blocker_type="specification",
        blocker_reason="No complete obligations/permissions/prohibitions model is checked in.",
        notes="Recorded as an explicit blocker for future semantic expansion.",
    ),
    OntologyStandard(
        standard_id="popolo",
        label="Popolo",
        source_url="https://www.popoloproject.com/",
        license="Creative Commons License",
        namespace=f"{STANDARD_NAMESPACE_BASE}popolo#",
        local_representation="registry entry and actor graph anchor",
        coverage_status="adjacent",
        blocker_type="source_data",
        blocker_reason="No Popolo actor/office/membership dataset has been imported yet.",
        notes="Useful for parliamentary actor modelling and office history.",
    ),
    OntologyStandard(
        standard_id="w3c_org",
        label="W3C ORG",
        source_url="https://www.w3.org/TR/vocab-org/",
        license="W3C Document License",
        namespace=f"{STANDARD_NAMESPACE_BASE}w3c-org#",
        local_representation="registry entry and organization graph anchor",
        coverage_status="adjacent",
        blocker_type="specification",
        blocker_reason="Only a local anchor is present; no full organization hierarchy model is exported.",
        notes="Useful for institutional roles and memberships.",
    ),
    OntologyStandard(
        standard_id="dcat",
        label="DCAT",
        source_url="https://www.w3.org/TR/vocab-dcat-3/",
        license="W3C Document License",
        namespace=f"{STANDARD_NAMESPACE_BASE}dcat#",
        local_representation="registry entry and dataset catalogue anchor",
        coverage_status="adjacent",
        blocker_type="specification",
        blocker_reason="Dataset catalogue records are not yet emitted from the repo pipelines.",
        notes="Supports publication discovery and catalogue interoperability.",
    ),
    OntologyStandard(
        standard_id="dcat_ap",
        label="DCAT-AP",
        source_url="https://semiceu.github.io/DCAT-AP/releases/2.2.0/",
        license="EU public-sector reuse policy",
        namespace=f"{STANDARD_NAMESPACE_BASE}dcat-ap#",
        local_representation="registry entry and profile anchor",
        coverage_status="adjacent",
        blocker_type="specification",
        blocker_reason="The repository does not yet validate against a profiled DCAT-AP catalogue.",
        notes="Record the profile now, even though catalogue emission remains pending.",
    ),
    OntologyStandard(
        standard_id="openfisca",
        label="OpenFisca",
        source_url="https://openfisca.org/doc/",
        license="OpenFisca documentation licence",
        namespace=f"{STANDARD_NAMESPACE_BASE}openfisca#",
        local_representation="registry entry and rules-as-code anchor",
        coverage_status="adjacent",
        blocker_type="source_data",
        blocker_reason="No country package variable, parameter, or entity inventory is imported.",
        notes="The repo is ready to map towards OpenFisca concepts later.",
    ),
    OntologyStandard(
        standard_id="policyengine",
        label="PolicyEngine",
        source_url="https://policyengine.org/",
        license="official license not stated on the public site",
        namespace=f"{STANDARD_NAMESPACE_BASE}policyengine#",
        local_representation="registry entry and rules-as-code anchor",
        coverage_status="adjacent",
        blocker_type="source_data",
        blocker_reason="No PolicyEngine variable, parameter, or formula model has been imported.",
        notes="Recorded for downstream rules-as-code bridging.",
    ),
    OntologyStandard(
        standard_id="openfisca_policyengine_bridge",
        label="OpenFisca/PolicyEngine bridge",
        source_url="https://legal-nz.example.org/ontology/standards/openfisca-policyengine-bridge",
        license="repo-local specification",
        namespace=f"{STANDARD_NAMESPACE_BASE}openfisca-policyengine-bridge#",
        local_representation="bridge registry only",
        coverage_status="missing",
        blocker_type="specification",
        blocker_reason="No formal entity-variable-parameter-period bridge has been authored yet.",
        notes="This is the explicit rules-as-code ontology bridge target.",
    ),
)

_STANDARD_INDEX: Final[dict[str, OntologyStandard]] = {
    standard.standard_id: standard for standard in STANDARD_REGISTRY
}


@dataclass(frozen=True, slots=True)
class ManifestSummary:
    """Compact manifest summary used in tests and archive notes."""

    total_standards: int
    coverage_counts: dict[str, int]
    blocker_counts: dict[str, int]
    round_trip_standard_ids: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Convert the summary to JSON-serialisable data."""
        return {
            "total_standards": self.total_standards,
            "coverage_counts": dict(self.coverage_counts),
            "blocker_counts": dict(self.blocker_counts),
            "round_trip_standard_ids": list(self.round_trip_standard_ids),
        }


def repo_root() -> Path:
    """Return the repository root for this package."""
    return Path(__file__).resolve().parents[3]


def ontology_standard_ids() -> tuple[str, ...]:
    """Return the registry identifiers in stable sorted order."""
    return tuple(sorted(_STANDARD_INDEX))


def ontology_standard_mappings() -> dict[str, str]:
    """Return stable ontology identifiers mapped to local namespaces."""
    return {
        standard_id: _STANDARD_INDEX[standard_id].namespace
        for standard_id in ontology_standard_ids()
    }


def get_ontology_standard(standard_id: str) -> OntologyStandard:
    """Return one ontology standard by its stable identifier."""
    try:
        return _STANDARD_INDEX[standard_id]
    except KeyError as exc:
        msg = f"Unknown ontology standard: {standard_id}"
        raise KeyError(msg) from exc


def _coverage_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for standard in STANDARD_REGISTRY:
        counts[standard.coverage_status] = counts.get(standard.coverage_status, 0) + 1
    return dict(sorted(counts.items()))


def _blocker_counts() -> dict[str, int]:
    counts: dict[str, int] = {}
    for standard in STANDARD_REGISTRY:
        if standard.blocker_type == "none":
            continue
        counts[standard.blocker_type] = counts.get(standard.blocker_type, 0) + 1
    return dict(sorted(counts.items()))


def _round_trip_standard_ids() -> tuple[str, ...]:
    return tuple(
        standard.standard_id for standard in STANDARD_REGISTRY if standard.round_trip_supported
    )


def build_ontology_standards_manifest(
    repo_root_path: Path | str | None = None,
) -> dict[str, Any]:
    """Build the Track 26 standards manifest as a JSON-compatible mapping."""
    root = Path(repo_root_path) if repo_root_path is not None else repo_root()
    standards = [standard.to_dict() for standard in STANDARD_REGISTRY]
    summary = ManifestSummary(
        total_standards=len(standards),
        coverage_counts=_coverage_counts(),
        blocker_counts=_blocker_counts(),
        round_trip_standard_ids=_round_trip_standard_ids(),
    )
    return {
        "track_id": "track26_ontology_standards_expansion_20260625",
        "repository_root": str(root),
        "standard_ids": list(ontology_standard_ids()),
        "stable_id_map": ontology_standard_mappings(),
        "standards": standards,
        "summary": summary.to_dict(),
    }


def dump_ontology_standards_manifest(repo_root_path: Path | str | None = None) -> str:
    """Serialise the Track 26 standards manifest to formatted JSON."""
    return json.dumps(
        build_ontology_standards_manifest(repo_root_path),
        indent=2,
        ensure_ascii=False,
        sort_keys=True,
    )


def load_ontology_standards_manifest(path: Path | str = STANDARD_MANIFEST_PATH) -> dict[str, Any]:
    """Load the checked-in standards manifest."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_ontology_standards_manifest(
    path: Path | str = STANDARD_MANIFEST_PATH,
    *,
    repo_root_path: Path | str | None = None,
) -> Path:
    """Write the deterministic Track 26 manifest to disk."""
    target = Path(path).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(dump_ontology_standards_manifest(repo_root_path), encoding="utf-8")
    return target


def _clean_segments(uri: str) -> list[str]:
    """Return the path segments from *uri* without empty entries."""
    parsed = urlsplit(uri)
    return [segment for segment in parsed.path.split("/") if segment]


def _join_uri(base_uri: str, *parts: str) -> str:
    """Join URI segments with a stable single-slash separator."""
    return base_uri.rstrip("/") + "/" + "/".join(part.strip("/") for part in parts)


def _slug(value: str) -> str:
    """Return a stable URI slug for ontology identifiers."""
    slug = re.sub(r"[^A-Za-z0-9]+", "-", value.strip()).strip("-")
    return slug.lower()


def _strip_template_prefix(segments: list[str], expected: tuple[str, ...]) -> list[str]:
    """Drop a fixed prefix from *segments* and raise when it is missing."""
    if segments[: len(expected)] != list(expected):
        msg = f"URI does not match expected prefix: {'/'.join(expected)}"
        raise ValueError(msg)
    return segments[len(expected) :]


def build_eli_uri(
    resource: LegislativeResource,
    *,
    base_uri: str = ELI_URI_BASE,
) -> str:
    """Build a deterministic local ELI URI."""
    if resource.draft_stage is not None:
        return build_eli_dl_uri(resource, base_uri=base_uri)
    parts = [
        "eli",
        resource.jurisdiction,
        resource.authority,
        str(resource.year),
        resource.document_kind,
        resource.number,
    ]
    if resource.version is not None:
        parts.extend(("version", resource.version))
    if resource.language is not None:
        parts.extend(("language", resource.language))
    return _join_uri(base_uri, *parts)


def build_eli_dl_uri(
    resource: LegislativeResource,
    *,
    base_uri: str = ELI_DL_URI_BASE,
) -> str:
    """Build a deterministic local ELI-DL URI."""
    if resource.draft_stage is None:
        msg = "ELI-DL resources require a draft_stage value."
        raise ValueError(msg)
    parts = [
        "eli-dl",
        resource.jurisdiction,
        resource.authority,
        str(resource.year),
        resource.document_kind,
        resource.draft_stage,
        resource.number,
    ]
    if resource.version is not None:
        parts.extend(("version", resource.version))
    if resource.language is not None:
        parts.extend(("language", resource.language))
    return _join_uri(base_uri, *parts)


def parse_eli_uri(uri: str, *, base_uri: str = ELI_URI_BASE) -> LegislativeResource:
    """Parse an ELI or ELI-DL URI back to a local legislation record."""
    segments = _clean_segments(uri)
    relative = _strip_template_prefix(segments, tuple(_clean_segments(base_uri)))
    is_draft = relative[0] == "eli-dl"
    if relative[0] not in {"eli", "eli-dl"}:
        msg = "Expected an ELI or ELI-DL URI."
        raise ValueError(msg)
    offset = 1
    jurisdiction = relative[offset]
    authority = relative[offset + 1]
    year = int(relative[offset + 2])
    document_kind = relative[offset + 3]
    index = offset + 4
    draft_stage: str | None = None
    if is_draft:
        draft_stage = relative[index]
        index += 1
    number = relative[index]
    index += 1
    version: str | None = None
    language: str | None = None
    while index < len(relative):
        key = relative[index]
        value = relative[index + 1]
        if key == "version":
            version = value
        elif key == "language":
            language = value
        index += 2
    return LegislativeResource(
        jurisdiction=jurisdiction,
        authority=authority,
        year=year,
        document_kind=document_kind,
        number=number,
        version=version,
        language=language,
        draft_stage=draft_stage,
    )


def build_ecli_identifier(identifier: ECLIIdentifier) -> str:
    """Build an ECLI identifier string."""
    return ":".join(
        (
            ECLI_PREFIX,
            identifier.country_code.upper(),
            identifier.court_code.upper(),
            str(identifier.year),
            identifier.sequence,
        )
    )


def parse_ecli_identifier(identifier: str) -> ECLIIdentifier:
    """Parse an ECLI identifier string back to structured data."""
    parts = identifier.split(":")
    if len(parts) != 5 or parts[0] != ECLI_PREFIX:
        msg = "Expected an ECLI identifier in the form ECLI:CC:COURT:YEAR:SEQUENCE."
        raise ValueError(msg)
    return ECLIIdentifier(
        country_code=parts[1],
        court_code=parts[2],
        year=int(parts[3]),
        sequence=parts[4],
    )


def build_controlled_concept(
    concept: ControlledConcept, *, scheme_uri: str | None = None
) -> dict[str, Any]:
    """Build a SKOS-compatible JSON-LD concept record."""
    scheme = scheme_uri or (
        EUROVOC_URI_BASE
        if concept.scheme_id.casefold() == "eurovoc"
        else _scheme_anchor(concept.scheme_id)
    )
    concept_uri = _join_uri(scheme, _slug(concept.concept_id))
    payload: dict[str, Any] = {
        "@context": {
            "skos": SKOS_NAMESPACE,
        },
        "@id": concept_uri,
        "@type": "skos:Concept",
        "skos:prefLabel": {
            "@value": concept.pref_label,
            "@language": concept.language,
        },
        "skos:inScheme": scheme,
    }
    if concept.notation:
        payload["skos:notation"] = concept.notation
    if concept.broader:
        payload["skos:broader"] = [_join_uri(scheme, _slug(broader)) for broader in concept.broader]
    return payload


def parse_controlled_concept(data: dict[str, Any]) -> ControlledConcept:
    """Parse a SKOS-compatible JSON-LD concept record."""
    concept_uri = str(data["@id"])
    scheme = str(data["skos:inScheme"])
    concept_id = concept_uri.rstrip("/").rsplit("/", 1)[-1]
    label_value = data["skos:prefLabel"]
    if not isinstance(label_value, dict):
        msg = "Concept prefLabel must be an object."
        raise ValueError(msg)
    broader = data.get("skos:broader", [])
    if isinstance(broader, str):
        broader_values = (broader.rsplit("/", 1)[-1],)
    else:
        broader_values = tuple(str(item).rstrip("/").rsplit("/", 1)[-1] for item in broader)
    scheme_id = _scheme_identifier(scheme)
    return ControlledConcept(
        scheme_id=scheme_id,
        concept_id=concept_id,
        pref_label=str(label_value["@value"]),
        language=str(label_value.get("@language", "en")),
        notation=str(data.get("skos:notation", "")),
        broader=broader_values,
    )


def load_controlled_concept(path: Path | str) -> ControlledConcept:
    """Load a SKOS-compatible concept record from JSON."""
    return parse_controlled_concept(json.loads(Path(path).read_text(encoding="utf-8")))


def build_eurovoc_concept(concept: ControlledConcept) -> dict[str, Any]:
    """Build a EuroVoc concept record."""
    return build_controlled_concept(concept, scheme_uri=EUROVOC_URI_BASE)


def build_skos_concept(concept: ControlledConcept) -> dict[str, Any]:
    """Build a local SKOS concept record."""
    return build_controlled_concept(concept)


def build_schema_legislation(profile: LegislationProfile) -> dict[str, Any]:
    """Build a schema.org/Legislation JSON-LD record."""
    payload: dict[str, Any] = {
        "@context": {
            "schema": "https://schema.org/",
        },
        "@id": _join_uri(
            STANDARD_NAMESPACE_BASE, "schema-org-legislation", _slug(profile.identifier)
        ),
        "@type": "schema:Legislation",
        "schema:identifier": profile.identifier,
        "schema:name": profile.name,
        "schema:legislationJurisdiction": profile.jurisdiction,
        "schema:legislationType": profile.legislation_type,
    }
    if profile.date_published is not None:
        payload["schema:datePublished"] = profile.date_published
    if profile.url is not None:
        payload["schema:url"] = profile.url
    if profile.same_as:
        payload["schema:sameAs"] = list(profile.same_as)
    return payload


def parse_schema_legislation(data: dict[str, Any]) -> LegislationProfile:
    """Parse a schema.org/Legislation JSON-LD record."""
    identifier = str(data["schema:identifier"])
    name = str(data["schema:name"])
    jurisdiction = str(data["schema:legislationJurisdiction"])
    legislation_type = str(data.get("schema:legislationType", "Act"))
    date_published = data.get("schema:datePublished")
    url = data.get("schema:url")
    same_as = data.get("schema:sameAs", [])
    if isinstance(same_as, str):
        same_as_values = (same_as,)
    else:
        same_as_values = tuple(str(item) for item in same_as)
    return LegislationProfile(
        identifier=identifier,
        name=name,
        jurisdiction=jurisdiction,
        legislation_type=legislation_type,
        date_published=str(date_published) if date_published is not None else None,
        url=str(url) if url is not None else None,
        same_as=same_as_values,
    )


def load_schema_legislation(path: Path | str) -> LegislationProfile:
    """Load a schema.org/Legislation JSON-LD record from JSON."""
    return parse_schema_legislation(json.loads(Path(path).read_text(encoding="utf-8")))


def _scheme_anchor(scheme_id: str) -> str:
    """Return a stable local namespace for a SKOS concept scheme."""
    return _join_uri(STANDARD_NAMESPACE_BASE, "skos", _slug(scheme_id))


def _scheme_identifier(scheme: str) -> str:
    """Derive a stable scheme identifier from a scheme URI."""
    if scheme.rstrip("/") == EUROVOC_URI_BASE.rstrip("/"):
        return "eurovoc"
    return scheme.rstrip("/").rsplit("/", 1)[-1].replace("-", "_")
