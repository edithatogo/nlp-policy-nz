"""Explicit ontology mapping knowledge graph for Track 29."""

from __future__ import annotations

import json
from collections import deque
from dataclasses import dataclass, replace
from pathlib import Path
from typing import Any, Final, Literal

from rdflib import RDF, RDFS, Graph, Literal as RdfLiteral, Namespace, URIRef
from rdflib.namespace import DC, DCTERMS, OWL, SKOS, XSD

MappingPredicate = Literal[
    "skos:exactMatch",
    "skos:closeMatch",
    "skos:broadMatch",
    "skos:narrowMatch",
    "skos:relatedMatch",
    "owl:equivalentClass",
    "owl:equivalentProperty",
    "rdfs:subClassOf",
    "rdfs:subPropertyOf",
    "source:crosswalk",
]
ReviewStatus = Literal["approved", "needs_review", "blocked"]

MAPPING_PREDICATES: Final[tuple[MappingPredicate, ...]] = (
    "skos:exactMatch",
    "skos:closeMatch",
    "skos:broadMatch",
    "skos:narrowMatch",
    "skos:relatedMatch",
    "owl:equivalentClass",
    "owl:equivalentProperty",
    "rdfs:subClassOf",
    "rdfs:subPropertyOf",
    "source:crosswalk",
)
REVIEW_STATUSES: Final[tuple[ReviewStatus, ...]] = ("approved", "needs_review", "blocked")
MAPPING_MANIFEST_FILENAME: Final[str] = "ontology_mappings.json"
MAPPING_SCHEMA_FILENAME: Final[str] = "ontology_mappings.schema.json"
MAPPING_TURTLE_FILENAME: Final[str] = "ontology_mappings.ttl"
MAPPING_JSONLD_FILENAME: Final[str] = "ontology_mappings.jsonld"
MAPPING_SUMMARY_FILENAME: Final[str] = "ontology_mapping_summary.json"
MAPPING_MERMAID_FILENAME: Final[str] = "ontology_mapping_graph.mmd"

BASE = Namespace("https://legal-nz.example.org/ontology/mapping/")
STANDARD = Namespace("https://legal-nz.example.org/ontology/standards/")
SOURCE = Namespace("https://legal-nz.example.org/ontology/source/")


@dataclass(frozen=True, slots=True)
class OntologyMappingRecord:
    """One explicit reviewed mapping between ontology terms."""

    mapping_id: str
    source_standard: str
    target_standard: str
    source_term: str
    target_term: str
    mapping_predicate: MappingPredicate
    confidence: float
    method: str
    provenance: str
    review_status: ReviewStatus = "approved"
    notes: str = ""

    def __post_init__(self) -> None:
        """Validate mapping contract fields."""
        if not self.mapping_id.strip():
            raise ValueError("mapping_id is required")
        if self.mapping_predicate not in MAPPING_PREDICATES:
            raise ValueError(f"unsupported mapping predicate: {self.mapping_predicate}")
        if self.review_status not in REVIEW_STATUSES:
            raise ValueError(f"unsupported review status: {self.review_status}")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")
        for field_name in (
            "source_standard",
            "target_standard",
            "source_term",
            "target_term",
            "method",
            "provenance",
        ):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{field_name} is required")

    @property
    def source_key(self) -> str:
        """Return the normalized source node key."""
        return concept_key(self.source_standard, self.source_term)

    @property
    def target_key(self) -> str:
        """Return the normalized target node key."""
        return concept_key(self.target_standard, self.target_term)

    def reversed(self) -> OntologyMappingRecord:
        """Return a reversed mapping for graph traversal."""
        return replace(
            self,
            mapping_id=f"{self.mapping_id}__reverse",
            source_standard=self.target_standard,
            target_standard=self.source_standard,
            source_term=self.target_term,
            target_term=self.source_term,
            mapping_predicate=_reverse_predicate(self.mapping_predicate),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the record to JSON-ready data."""
        return {
            "mapping_id": self.mapping_id,
            "source_standard": self.source_standard,
            "target_standard": self.target_standard,
            "source_term": self.source_term,
            "target_term": self.target_term,
            "mapping_predicate": self.mapping_predicate,
            "confidence": self.confidence,
            "method": self.method,
            "provenance": self.provenance,
            "review_status": self.review_status,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> OntologyMappingRecord:
        """Build a mapping record from JSON data."""
        return cls(
            mapping_id=str(payload["mapping_id"]),
            source_standard=str(payload["source_standard"]),
            target_standard=str(payload["target_standard"]),
            source_term=str(payload["source_term"]),
            target_term=str(payload["target_term"]),
            mapping_predicate=payload["mapping_predicate"],
            confidence=float(payload["confidence"]),
            method=str(payload["method"]),
            provenance=str(payload["provenance"]),
            review_status=payload.get("review_status", "approved"),
            notes=str(payload.get("notes", "")),
        )


def concept_key(standard: str, term: str) -> str:
    """Return a stable concept key used by query helpers."""
    return f"{standard.strip()}::{term.strip()}"


def build_mapping_manifest(
    mappings: tuple[OntologyMappingRecord, ...] | None = None,
) -> dict[str, Any]:
    """Build a deterministic JSON mapping manifest."""
    records = mappings or SEED_MAPPINGS
    sorted_records = tuple(sorted(records, key=lambda record: record.mapping_id))
    return {
        "schema_version": "1.0",
        "track_id": "track29_ontology_mapping_kg_20260625",
        "mapping_predicates": list(MAPPING_PREDICATES),
        "review_statuses": list(REVIEW_STATUSES),
        "mappings": [record.to_dict() for record in sorted_records],
        "summary": mapping_summary(sorted_records),
    }


def mapping_summary(
    mappings: tuple[OntologyMappingRecord, ...] | None = None,
) -> dict[str, Any]:
    """Return summary statistics for a mapping set."""
    records = mappings or SEED_MAPPINGS
    standards = sorted(
        {
            standard
            for record in records
            for standard in (record.source_standard, record.target_standard)
        },
        key=str.casefold,
    )
    predicate_counts: dict[str, int] = dict.fromkeys(MAPPING_PREDICATES, 0)
    review_counts: dict[str, int] = dict.fromkeys(REVIEW_STATUSES, 0)
    for record in records:
        predicate_counts[record.mapping_predicate] += 1
        review_counts[record.review_status] += 1
    return {
        "mapping_count": len(records),
        "standard_count": len(standards),
        "standards": standards,
        "predicate_counts": {key: value for key, value in predicate_counts.items() if value},
        "review_status_counts": {key: value for key, value in review_counts.items() if value},
    }


def validate_mapping_manifest(manifest: dict[str, Any]) -> tuple[OntologyMappingRecord, ...]:
    """Validate a mapping manifest and return records."""
    if manifest.get("schema_version") != "1.0":
        raise ValueError("schema_version must be 1.0")
    records = tuple(
        OntologyMappingRecord.from_dict(payload) for payload in manifest.get("mappings", [])
    )
    ids = [record.mapping_id for record in records]
    if len(ids) != len(set(ids)):
        raise ValueError("mapping_id values must be unique")
    return tuple(sorted(records, key=lambda record: record.mapping_id))


def load_mapping_manifest(path: Path | str) -> tuple[OntologyMappingRecord, ...]:
    """Load and validate mapping records from a JSON manifest."""
    return validate_mapping_manifest(json.loads(Path(path).read_text(encoding="utf-8")))


def add_mapping_record(
    mappings: tuple[OntologyMappingRecord, ...],
    record: OntologyMappingRecord,
) -> tuple[OntologyMappingRecord, ...]:
    """Return mappings with a new record appended after duplicate-id checks."""
    if any(existing.mapping_id == record.mapping_id for existing in mappings):
        raise ValueError(f"mapping_id already exists: {record.mapping_id}")
    return tuple(sorted((*mappings, record), key=lambda item: item.mapping_id))


def replace_mapping_record(
    mappings: tuple[OntologyMappingRecord, ...],
    record: OntologyMappingRecord,
) -> tuple[OntologyMappingRecord, ...]:
    """Return mappings with one existing record replaced by ``record``."""
    if not any(existing.mapping_id == record.mapping_id for existing in mappings):
        raise ValueError(f"mapping_id does not exist: {record.mapping_id}")
    return tuple(
        sorted(
            (
                record if existing.mapping_id == record.mapping_id else existing
                for existing in mappings
            ),
            key=lambda item: item.mapping_id,
        )
    )


def remove_mapping_record(
    mappings: tuple[OntologyMappingRecord, ...],
    mapping_id: str,
) -> tuple[OntologyMappingRecord, ...]:
    """Return mappings with ``mapping_id`` removed."""
    filtered = tuple(record for record in mappings if record.mapping_id != mapping_id)
    if len(filtered) == len(mappings):
        raise ValueError(f"mapping_id does not exist: {mapping_id}")
    return filtered


def update_mapping_review_status(
    mappings: tuple[OntologyMappingRecord, ...],
    mapping_id: str,
    review_status: ReviewStatus,
) -> tuple[OntologyMappingRecord, ...]:
    """Return mappings with one record's review status changed."""
    target = next((record for record in mappings if record.mapping_id == mapping_id), None)
    if target is None:
        raise ValueError(f"mapping_id does not exist: {mapping_id}")
    return replace_mapping_record(mappings, replace(target, review_status=review_status))


def write_mapping_artifacts(output_dir: Path | str | None = None) -> dict[str, Path]:
    """Write JSON, RDF, JSON-LD, summary, schema, and Mermaid artifacts."""
    target_dir = Path(output_dir) if output_dir is not None else repo_root() / "data" / "ontologies"
    target_dir.mkdir(parents=True, exist_ok=True)
    manifest = build_mapping_manifest()
    graph = build_mapping_graph(SEED_MAPPINGS)
    payloads = {
        MAPPING_MANIFEST_FILENAME: json.dumps(
            manifest, indent=2, ensure_ascii=False, sort_keys=True
        )
        + "\n",
        MAPPING_SCHEMA_FILENAME: json.dumps(mapping_json_schema(), indent=2, sort_keys=True) + "\n",
        MAPPING_TURTLE_FILENAME: graph.serialize(format="turtle"),
        MAPPING_JSONLD_FILENAME: graph.serialize(format="json-ld", indent=2),
        MAPPING_SUMMARY_FILENAME: json.dumps(
            mapping_summary(SEED_MAPPINGS), indent=2, ensure_ascii=False, sort_keys=True
        )
        + "\n",
        MAPPING_MERMAID_FILENAME: render_mermaid_graph(SEED_MAPPINGS),
    }
    written: dict[str, Path] = {}
    for filename, content in payloads.items():
        path = target_dir / filename
        path.write_text(str(content), encoding="utf-8")
        written[filename] = path
    return written


def build_mapping_graph(
    mappings: tuple[OntologyMappingRecord, ...] | None = None,
) -> Graph:
    """Build an RDF graph for explicit ontology mappings."""
    records = mappings or SEED_MAPPINGS
    graph = Graph()
    graph.bind("map", BASE)
    graph.bind("std", STANDARD)
    graph.bind("source", SOURCE)
    graph.bind("skos", SKOS)
    graph.bind("owl", OWL)
    graph.bind("rdfs", RDFS)
    graph.bind("dcterms", DCTERMS)
    for record in records:
        mapping_uri = BASE[record.mapping_id]
        source_uri = _term_uri(record.source_standard, record.source_term)
        target_uri = _term_uri(record.target_standard, record.target_term)
        graph.add((mapping_uri, RDF.type, BASE.MappingRecord))
        graph.add((mapping_uri, DC.identifier, RdfLiteral(record.mapping_id)))
        graph.add((mapping_uri, BASE.sourceStandard, RdfLiteral(record.source_standard)))
        graph.add((mapping_uri, BASE.targetStandard, RdfLiteral(record.target_standard)))
        graph.add((mapping_uri, BASE.sourceTerm, RdfLiteral(record.source_term)))
        graph.add((mapping_uri, BASE.targetTerm, RdfLiteral(record.target_term)))
        graph.add((mapping_uri, BASE.mappingPredicate, RdfLiteral(record.mapping_predicate)))
        graph.add(
            (mapping_uri, BASE.confidence, RdfLiteral(record.confidence, datatype=XSD.decimal))
        )
        graph.add((mapping_uri, BASE.method, RdfLiteral(record.method)))
        graph.add((mapping_uri, DCTERMS.source, RdfLiteral(record.provenance)))
        graph.add((mapping_uri, BASE.reviewStatus, RdfLiteral(record.review_status)))
        if record.notes:
            graph.add((mapping_uri, RDFS.comment, RdfLiteral(record.notes)))
        graph.add((mapping_uri, BASE.sourceNode, source_uri))
        graph.add((mapping_uri, BASE.targetNode, target_uri))
        graph.add((source_uri, _predicate_uri(record.mapping_predicate), target_uri))
    return graph


def mappings_by_standard_pair(
    source_standard: str,
    target_standard: str,
    *,
    mappings: tuple[OntologyMappingRecord, ...] | None = None,
) -> tuple[OntologyMappingRecord, ...]:
    """Return mappings from one standard to another."""
    records = mappings or SEED_MAPPINGS
    return tuple(
        record
        for record in records
        if record.source_standard == source_standard and record.target_standard == target_standard
    )


def get_equivalent(
    concept: str,
    from_std: str,
    to_std: str,
    *,
    mappings: tuple[OntologyMappingRecord, ...] | None = None,
) -> tuple[str, ...]:
    """Return explicit equivalent or close target terms for a standard pair."""
    allowed = {
        "skos:exactMatch",
        "skos:closeMatch",
        "owl:equivalentClass",
        "owl:equivalentProperty",
    }
    return tuple(
        record.target_term
        for record in mappings_by_standard_pair(from_std, to_std, mappings=mappings)
        if record.source_term == concept
        and record.mapping_predicate in allowed
        and record.review_status == "approved"
    )


def traverse_mappings(
    concept: str,
    from_std: str,
    *,
    max_hops: int = 2,
    mappings: tuple[OntologyMappingRecord, ...] | None = None,
) -> tuple[dict[str, Any], ...]:
    """Traverse explicit mappings from a concept up to ``max_hops``."""
    records = mappings or SEED_MAPPINGS
    adjacency: dict[str, list[OntologyMappingRecord]] = {}
    for record in records:
        if record.review_status != "approved":
            continue
        adjacency.setdefault(record.source_key, []).append(record)
        if record.mapping_predicate in _REVERSIBLE_PREDICATES:
            reverse = record.reversed()
            adjacency.setdefault(reverse.source_key, []).append(reverse)

    start = concept_key(from_std, concept)
    queue: deque[tuple[str, int, tuple[str, ...]]] = deque([(start, 0, ())])
    visited = {start}
    paths: list[dict[str, Any]] = []
    while queue:
        key, hops, trail = queue.popleft()
        if hops >= max_hops:
            continue
        for edge in adjacency.get(key, []):
            next_key = edge.target_key
            path = (*trail, edge.mapping_id)
            paths.append(
                {
                    "source": key,
                    "target": next_key,
                    "hops": hops + 1,
                    "path": list(path),
                    "predicate": edge.mapping_predicate,
                    "confidence": edge.confidence,
                }
            )
            if next_key not in visited:
                visited.add(next_key)
                queue.append((next_key, hops + 1, path))
    return tuple(paths)


def render_mermaid_graph(
    mappings: tuple[OntologyMappingRecord, ...] | None = None,
) -> str:
    """Render a Mermaid graph for standards-level ontology relationships."""
    records = mappings or SEED_MAPPINGS
    lines = ["graph LR"]
    for record in sorted(records, key=lambda item: item.mapping_id):
        source = _node_id(record.source_standard)
        target = _node_id(record.target_standard)
        label = record.mapping_predicate.replace(":", "_")
        lines.append(
            f'  {source}["{record.source_standard}"] -- "{label}" --> {target}["{record.target_standard}"]'
        )
    return "\n".join(lines) + "\n"


def mapping_json_schema() -> dict[str, Any]:
    """Return the JSON Schema for mapping manifests."""
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "Track 29 Ontology Mapping Manifest",
        "type": "object",
        "required": [
            "schema_version",
            "track_id",
            "mapping_predicates",
            "review_statuses",
            "mappings",
            "summary",
        ],
        "properties": {
            "schema_version": {"const": "1.0"},
            "track_id": {"const": "track29_ontology_mapping_kg_20260625"},
            "mapping_predicates": {"type": "array", "items": {"enum": list(MAPPING_PREDICATES)}},
            "review_statuses": {"type": "array", "items": {"enum": list(REVIEW_STATUSES)}},
            "mappings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": [
                        "mapping_id",
                        "source_standard",
                        "target_standard",
                        "source_term",
                        "target_term",
                        "mapping_predicate",
                        "confidence",
                        "method",
                        "provenance",
                        "review_status",
                        "notes",
                    ],
                    "properties": {
                        "mapping_id": {"type": "string", "minLength": 1},
                        "source_standard": {"type": "string", "minLength": 1},
                        "target_standard": {"type": "string", "minLength": 1},
                        "source_term": {"type": "string", "minLength": 1},
                        "target_term": {"type": "string", "minLength": 1},
                        "mapping_predicate": {"enum": list(MAPPING_PREDICATES)},
                        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
                        "method": {"type": "string", "minLength": 1},
                        "provenance": {"type": "string", "minLength": 1},
                        "review_status": {"enum": list(REVIEW_STATUSES)},
                        "notes": {"type": "string"},
                    },
                    "additionalProperties": False,
                },
            },
            "summary": {"type": "object"},
        },
        "additionalProperties": False,
    }


def repo_root() -> Path:
    """Return repository root."""
    return Path(__file__).resolve().parents[3]


def _reverse_predicate(predicate: MappingPredicate) -> MappingPredicate:
    reverse = {
        "skos:broadMatch": "skos:narrowMatch",
        "skos:narrowMatch": "skos:broadMatch",
        "rdfs:subClassOf": "skos:broadMatch",
        "rdfs:subPropertyOf": "skos:broadMatch",
    }
    return reverse.get(predicate, predicate)  # type: ignore[return-value]


def _term_uri(standard: str, term: str) -> URIRef:
    return STANDARD[f"{_slug(standard)}/{_slug(term)}"]


def _predicate_uri(predicate: MappingPredicate) -> URIRef:
    namespace, name = predicate.split(":", 1)
    if namespace == "skos":
        return SKOS[name]
    if namespace == "owl":
        return OWL[name]
    if namespace == "rdfs":
        return RDFS[name]
    return SOURCE[name]


def _slug(value: str) -> str:
    return "".join(character.lower() if character.isalnum() else "-" for character in value).strip(
        "-"
    )


def _node_id(value: str) -> str:
    return "n_" + "".join(character.lower() if character.isalnum() else "_" for character in value)


_REVERSIBLE_PREDICATES: Final[set[MappingPredicate]] = {
    "skos:exactMatch",
    "skos:closeMatch",
    "skos:broadMatch",
    "skos:narrowMatch",
    "skos:relatedMatch",
    "owl:equivalentClass",
    "owl:equivalentProperty",
}

SEED_MAPPINGS: Final[tuple[OntologyMappingRecord, ...]] = (
    OntologyMappingRecord(
        mapping_id="lkif-obligation-to-akn-obligation",
        source_standard="LKIF",
        target_standard="Akoma Ntoso",
        source_term="Obligation",
        target_term="obligation",
        mapping_predicate="skos:closeMatch",
        confidence=0.82,
        method="manual crosswalk from Track 25/26 normative effect inventory",
        provenance="conductor/tracks/track26_ontology_standards_expansion_20260625/spec.md",
        notes="LKIF normative effect is represented as an AKN-oriented semantic annotation, not native AKN markup.",
    ),
    OntologyMappingRecord(
        mapping_id="lkif-permission-to-odrl-permission",
        source_standard="LKIF",
        target_standard="ODRL",
        source_term="Permission",
        target_term="Permission",
        mapping_predicate="skos:closeMatch",
        confidence=0.78,
        method="manual Track 28 ODRL map-only decision",
        provenance="data/ontologies/track28_discovery_log.json",
        notes="ODRL policy permission is adjacent to legal permission but should not be treated as full legal reasoning parity.",
    ),
    OntologyMappingRecord(
        mapping_id="lkif-prohibition-to-odrl-prohibition",
        source_standard="LKIF",
        target_standard="ODRL",
        source_term="Prohibition",
        target_term="Prohibition",
        mapping_predicate="skos:closeMatch",
        confidence=0.78,
        method="manual Track 28 ODRL map-only decision",
        provenance="data/ontologies/track28_discovery_log.json",
        notes="Use for deontic extraction inspection and not as executable ODRL policy output.",
    ),
    OntologyMappingRecord(
        mapping_id="foaf-person-to-schema-person",
        source_standard="FOAF",
        target_standard="schema.org",
        source_term="Person",
        target_term="Person",
        mapping_predicate="owl:equivalentClass",
        confidence=0.95,
        method="manual class identity crosswalk for public person metadata",
        provenance="src/nlp_policy_nz/linked_data/foaf.py",
        notes="Used for parliamentary people and speaker profile interoperability.",
    ),
    OntologyMappingRecord(
        mapping_id="sioc-post-to-akn-debate",
        source_standard="SIOC",
        target_standard="Akoma Ntoso",
        source_term="Post",
        target_term="debateSpeech",
        mapping_predicate="skos:closeMatch",
        confidence=0.74,
        method="manual discourse-to-legislative-document crosswalk",
        provenance="src/nlp_policy_nz/linked_data/sioc.py",
        notes="SIOC post models discourse item; AKN debateSpeech models parliamentary speech structure.",
    ),
    OntologyMappingRecord(
        mapping_id="prov-entity-to-dcat-dataset",
        source_standard="PROV-O",
        target_standard="DCAT",
        source_term="Entity",
        target_term="Dataset",
        mapping_predicate="skos:relatedMatch",
        confidence=0.72,
        method="manual provenance-to-catalog publication crosswalk",
        provenance="data/ontologies/track26_standards_registry.json",
        notes="A pipeline output entity can be catalogued as a DCAT dataset when published.",
    ),
    OntologyMappingRecord(
        mapping_id="dcat-dataset-to-data-govt-nz-dataset",
        source_standard="DCAT",
        target_standard="data.govt.nz Dataset Metadata",
        source_term="Dataset",
        target_term="dataset",
        mapping_predicate="source:crosswalk",
        confidence=0.86,
        method="manual Track 28 dataset publication crosswalk",
        provenance="data/ontologies/track28_standards_registry_addendum.json",
        notes="Maps generic dataset catalogue semantics to NZ publication metadata intake.",
    ),
    OntologyMappingRecord(
        mapping_id="dcat-dataset-to-nzgls-resource",
        source_standard="DCAT",
        target_standard="NZGLS",
        source_term="Dataset",
        target_term="Resource",
        mapping_predicate="source:crosswalk",
        confidence=0.84,
        method="manual Track 28 NZGLS addendum crosswalk",
        provenance="data/ontologies/track28_standards_registry_addendum.json",
        notes="NZGLS resource metadata is used as a local publication crosswalk target.",
    ),
    OntologyMappingRecord(
        mapping_id="agls-resource-to-nzgls-resource",
        source_standard="AGLS",
        target_standard="NZGLS",
        source_term="Resource",
        target_term="Resource",
        mapping_predicate="skos:closeMatch",
        confidence=0.8,
        method="manual trans-Tasman metadata crosswalk",
        provenance="data/ontologies/track28_standards_registry_addendum.json",
        notes="Supports AU-to-NZ corpus metadata transfer without adopting AGLS as core.",
    ),
    OntologyMappingRecord(
        mapping_id="extraction-rules-as-code-to-catala-scope",
        source_standard="nlp-policy-nz extraction",
        target_standard="Catala",
        source_term="rules_as_code",
        target_term="scope",
        mapping_predicate="source:crosswalk",
        confidence=0.68,
        method="manual Track 55 to Track 28 rules-as-code bridge",
        provenance="docs/extraction-framework.md",
        review_status="needs_review",
        notes="Requires downstream review before generating Catala code or scopes.",
    ),
    OntologyMappingRecord(
        mapping_id="extraction-date-to-time-instant",
        source_standard="nlp-policy-nz extraction",
        target_standard="OWL-Time",
        source_term="date",
        target_term="time:Instant",
        mapping_predicate="skos:closeMatch",
        confidence=0.76,
        method="manual extraction-family to W3C Time crosswalk",
        provenance="src/nlp_policy_nz/extraction/schemas.py",
        notes="Only normalized dates with source spans should be mapped to Time entities.",
    ),
    OntologyMappingRecord(
        mapping_id="extraction-definition-to-skos-concept",
        source_standard="nlp-policy-nz extraction",
        target_standard="SKOS",
        source_term="definition",
        target_term="Concept",
        mapping_predicate="skos:relatedMatch",
        confidence=0.7,
        method="manual extraction-family to controlled vocabulary crosswalk",
        provenance="src/nlp_policy_nz/extraction/schemas.py",
        notes="Definitions can seed concepts but require curation before becoming a controlled vocabulary.",
    ),
)


__all__ = [
    "MAPPING_JSONLD_FILENAME",
    "MAPPING_MANIFEST_FILENAME",
    "MAPPING_MERMAID_FILENAME",
    "MAPPING_PREDICATES",
    "MAPPING_SCHEMA_FILENAME",
    "MAPPING_SUMMARY_FILENAME",
    "MAPPING_TURTLE_FILENAME",
    "REVIEW_STATUSES",
    "SEED_MAPPINGS",
    "MappingPredicate",
    "OntologyMappingRecord",
    "ReviewStatus",
    "add_mapping_record",
    "build_mapping_graph",
    "build_mapping_manifest",
    "concept_key",
    "get_equivalent",
    "load_mapping_manifest",
    "mapping_json_schema",
    "mapping_summary",
    "mappings_by_standard_pair",
    "remove_mapping_record",
    "render_mermaid_graph",
    "replace_mapping_record",
    "repo_root",
    "traverse_mappings",
    "update_mapping_review_status",
    "validate_mapping_manifest",
    "write_mapping_artifacts",
]
