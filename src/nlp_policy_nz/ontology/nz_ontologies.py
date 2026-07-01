"""Data-driven New Zealand ontology candidates for Track 31.

The module builds deterministic, reviewable NZ-specific ontology candidates
from the repository's ontology coverage audit and mapping graph evidence. It
does not claim full-corpus induction; concepts that are locally induced remain
marked as reviewable until corpus-scale evidence is available.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Literal

from rdflib import RDF, RDFS, Graph, Literal as RdfLiteral, Namespace, URIRef
from rdflib.namespace import DC, DCTERMS, OWL, PROV, SKOS, XSD

from nlp_policy_nz.ontology.mapping_graph import (
    SEED_MAPPINGS,
    MappingPredicate,
    OntologyMappingRecord,
)
from nlp_policy_nz.quality.track25_ontology_coverage import build_coverage_matrix, repo_root

ApplicationArea = Literal[
    "act_structure",
    "hansard_debate_topics",
    "court_hierarchy",
    "maori_legal_concepts",
    "government_agencies",
]
ConceptKind = Literal["class", "property", "controlled_vocabulary"]
ConceptAuthority = Literal["authoritative_external", "induced_nz"]
ReviewStatus = Literal["approved", "needs_review"]

NZ_ONTOLOGY_MANIFEST_FILENAME: Final[str] = "nz_ontology_candidates.json"
NZ_ONTOLOGY_TURTLE_FILENAME: Final[str] = "nz_ontology_candidates.ttl"
NZ_ONTOLOGY_JSONLD_FILENAME: Final[str] = "nz_ontology_candidates.jsonld"
NZ_ONTOLOGY_SKOS_FILENAME: Final[str] = "nz_controlled_vocabularies.json"

NZ = Namespace("https://legal-nz.example.org/ontology/nz/")
NZVOCAB = Namespace("https://legal-nz.example.org/ontology/nz/vocab/")
EVIDENCE = Namespace("https://legal-nz.example.org/ontology/evidence/")


@dataclass(frozen=True, slots=True)
class CorpusEvidence:
    """A local evidence pointer used to justify a concept candidate."""

    evidence_id: str
    source: str
    evidence_type: str
    value: str

    def __post_init__(self) -> None:
        """Validate required evidence fields."""
        for field_name in ("evidence_id", "source", "evidence_type", "value"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{field_name} is required")

    def to_dict(self) -> dict[str, str]:
        """Return JSON-ready evidence data."""
        return {
            "evidence_id": self.evidence_id,
            "source": self.source,
            "evidence_type": self.evidence_type,
            "value": self.value,
        }


@dataclass(frozen=True, slots=True)
class OntologyAnchor:
    """An upstream ontology anchor for a NZ concept candidate."""

    standard: str
    term: str
    mapping_id: str = ""
    predicate: str = "skos:relatedMatch"

    def __post_init__(self) -> None:
        """Validate required anchor identity."""
        for field_name in ("standard", "term", "predicate"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{field_name} is required")

    def to_dict(self) -> dict[str, str]:
        """Return JSON-ready anchor data."""
        return {
            "standard": self.standard,
            "term": self.term,
            "mapping_id": self.mapping_id,
            "predicate": self.predicate,
        }


@dataclass(frozen=True, slots=True)
class NZOntologyConcept:
    """A New Zealand-specific ontology class, property, or vocabulary concept."""

    concept_id: str
    label: str
    definition: str
    application_area: ApplicationArea
    kind: ConceptKind
    authority: ConceptAuthority
    confidence: float
    evidence: tuple[CorpusEvidence, ...]
    ontology_anchors: tuple[OntologyAnchor, ...]
    broader: tuple[str, ...] = ()
    related: tuple[str, ...] = ()
    review_status: ReviewStatus = "needs_review"

    def __post_init__(self) -> None:
        """Validate concept identity, review boundary, and traceability."""
        for field_name in ("concept_id", "label", "definition", "application_area", "kind"):
            if not str(getattr(self, field_name)).strip():
                raise ValueError(f"{field_name} is required")
        if not 0 < self.confidence <= 1:
            raise ValueError("confidence must be greater than 0 and no more than 1")
        if not self.evidence:
            raise ValueError("concept evidence is required")
        if not self.ontology_anchors:
            raise ValueError("ontology anchors are required")
        if self.authority == "induced_nz" and self.review_status != "needs_review":
            raise ValueError("induced NZ concepts must require review")
        if self.authority == "authoritative_external" and self.review_status != "approved":
            raise ValueError("authoritative external concepts must be approved")

    @property
    def uri(self) -> str:
        """Return a stable URI for this concept."""
        return str(NZ[self.concept_id])

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-ready concept data."""
        return {
            "concept_id": self.concept_id,
            "uri": self.uri,
            "label": self.label,
            "definition": self.definition,
            "application_area": self.application_area,
            "kind": self.kind,
            "authority": self.authority,
            "confidence": self.confidence,
            "review_status": self.review_status,
            "broader": list(self.broader),
            "related": list(self.related),
            "evidence": [item.to_dict() for item in self.evidence],
            "ontology_anchors": [item.to_dict() for item in self.ontology_anchors],
        }


@dataclass(frozen=True, slots=True)
class SKOSConcept:
    """A concept in a Track 31 controlled vocabulary scheme."""

    concept_id: str
    pref_label: str
    definition: str
    broader: tuple[str, ...] = ()

    @property
    def uri(self) -> str:
        """Return a stable SKOS concept URI."""
        return str(NZVOCAB[self.concept_id])

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-ready SKOS concept data."""
        return {
            "concept_id": self.concept_id,
            "uri": self.uri,
            "pref_label": self.pref_label,
            "definition": self.definition,
            "broader": list(self.broader),
        }


@dataclass(frozen=True, slots=True)
class SKOSConceptScheme:
    """A deterministic NZ controlled vocabulary scheme."""

    scheme_id: str
    pref_label: str
    definition: str
    concepts: tuple[SKOSConcept, ...]

    @property
    def uri(self) -> str:
        """Return a stable SKOS scheme URI."""
        return str(NZVOCAB[self.scheme_id])

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-ready SKOS scheme data."""
        return {
            "scheme_id": self.scheme_id,
            "uri": self.uri,
            "pref_label": self.pref_label,
            "definition": self.definition,
            "concepts": [concept.to_dict() for concept in self.concepts],
        }


@dataclass(frozen=True, slots=True)
class NZOntologyBundle:
    """The Track 31 ontology induction output bundle."""

    concepts: tuple[NZOntologyConcept, ...]
    controlled_vocabularies: tuple[SKOSConceptScheme, ...]
    source_summary: dict[str, Any]

    @property
    def summary(self) -> dict[str, Any]:
        """Return deterministic summary metrics for the bundle."""
        authority_counts: dict[str, int] = {}
        area_counts: dict[str, int] = {}
        for concept in self.concepts:
            authority_counts[concept.authority] = authority_counts.get(concept.authority, 0) + 1
            area_counts[concept.application_area] = area_counts.get(concept.application_area, 0) + 1
        return {
            "concept_count": len(self.concepts),
            "controlled_vocabulary_count": len(self.controlled_vocabularies),
            "authority_counts": dict(sorted(authority_counts.items())),
            "application_area_counts": dict(sorted(area_counts.items())),
            "validation_errors": validate_nz_ontology_bundle(self),
        }

    def to_dict(self) -> dict[str, Any]:
        """Return JSON-ready bundle data."""
        return {
            "schema_version": "1.0",
            "track_id": "track31_nz_data_driven_ontologies_20260625",
            "source_summary": self.source_summary,
            "summary": self.summary,
            "concepts": [concept.to_dict() for concept in self.concepts],
            "controlled_vocabularies": [
                scheme.to_dict() for scheme in self.controlled_vocabularies
            ],
        }


def build_nz_ontology_bundle(
    *,
    coverage_rows: tuple[dict[str, Any], ...] | None = None,
    mappings: tuple[OntologyMappingRecord, ...] | None = None,
) -> NZOntologyBundle:
    """Build the deterministic Track 31 NZ ontology candidate bundle."""
    rows = coverage_rows or tuple(build_coverage_matrix(repo_root()))
    mapping_records = mappings or SEED_MAPPINGS
    concepts = tuple(sorted(_seed_concepts(rows, mapping_records), key=lambda item: item.uri))
    vocabularies = build_skos_concept_schemes()
    return NZOntologyBundle(
        concepts=concepts,
        controlled_vocabularies=vocabularies,
        source_summary={
            "coverage_row_count": len(rows),
            "mapping_record_count": len(mapping_records),
            "inputs": [
                "Track 25 ontology coverage matrix",
                "Track 29 explicit ontology mappings",
                "Track 30 inferred mapping contract",
                "Track 32 whole-corpus statistics placeholder",
            ],
            "evidence_boundary": (
                "Repo-side candidates are deterministic and reviewable. Full-corpus "
                "induction remains blocked until Track 32 dataset statistics exist."
            ),
        },
    )


def build_skos_concept_schemes() -> tuple[SKOSConceptScheme, ...]:
    """Build controlled vocabularies for NZ ontology publication surfaces."""
    schemes = (
        SKOSConceptScheme(
            scheme_id="nz-act-types",
            pref_label="NZ Act types",
            definition="Controlled vocabulary for New Zealand legislative document types.",
            concepts=_concepts(
                (
                    ("act", "Act", "An enacted New Zealand statute."),
                    ("bill", "Bill", "A proposed legislative instrument before enactment."),
                    ("regulation", "Regulation", "A delegated legislative instrument."),
                    ("amendment-act", "Amendment Act", "An Act that modifies earlier legislation."),
                )
            ),
        ),
        SKOSConceptScheme(
            scheme_id="hansard-topics",
            pref_label="Hansard topics",
            definition="Controlled vocabulary for high-level parliamentary debate topics.",
            concepts=_concepts(
                (
                    ("budget", "Budget", "Debate about fiscal appropriations or spending."),
                    ("health", "Health", "Debate about health policy and services."),
                    ("justice", "Justice", "Debate about courts, policing, or legal policy."),
                    ("treaty", "Treaty", "Debate about Te Tiriti o Waitangi obligations."),
                )
            ),
        ),
        SKOSConceptScheme(
            scheme_id="court-levels",
            pref_label="NZ court levels",
            definition="Controlled vocabulary for New Zealand court hierarchy levels.",
            concepts=_concepts(
                (
                    ("district-court", "District Court", "First-instance court level."),
                    ("high-court", "High Court", "Superior first-instance court level."),
                    ("court-of-appeal", "Court of Appeal", "Intermediate appellate court level."),
                    ("supreme-court", "Supreme Court", "Final appellate court level."),
                )
            ),
        ),
        SKOSConceptScheme(
            scheme_id="government-agencies",
            pref_label="NZ government agencies",
            definition="Controlled vocabulary for public sector actor classes.",
            concepts=_concepts(
                (
                    ("department", "Department", "Central government department."),
                    ("crown-entity", "Crown entity", "Statutory public body."),
                    ("ministerial-portfolio", "Ministerial portfolio", "Ministerial area of responsibility."),
                    ("office", "Office", "Public office or statutory role."),
                )
            ),
        ),
        SKOSConceptScheme(
            scheme_id="maori-legal-concepts",
            pref_label="Māori legal concepts",
            definition="Controlled vocabulary for Māori legal and policy concepts.",
            concepts=_concepts(
                (
                    ("iwi", "Iwi", "Tribal group or people."),
                    ("taonga", "Taonga", "Treasured resource or thing."),
                    ("te-tiriti", "Te Tiriti", "Te Tiriti o Waitangi reference."),
                    ("tikanga", "Tikanga", "Māori law, values, and customary practice."),
                )
            ),
        ),
    )
    return tuple(sorted(schemes, key=lambda scheme: scheme.scheme_id))


def validate_nz_ontology_bundle(bundle: NZOntologyBundle) -> list[str]:
    """Validate Track 31 candidate consistency."""
    errors: list[str] = []
    ids = [concept.concept_id for concept in bundle.concepts]
    labels = [concept.label.casefold() for concept in bundle.concepts]
    if len(ids) != len(set(ids)):
        errors.append("concept IDs must be unique")
    if len(labels) != len(set(labels)):
        errors.append("concept labels must be unique")
    known_ids = set(ids)
    for concept in bundle.concepts:
        if not concept.evidence:
            errors.append(f"{concept.concept_id} is missing evidence")
        if not concept.ontology_anchors:
            errors.append(f"{concept.concept_id} is missing ontology anchors")
        for broader in concept.broader:
            if broader not in known_ids:
                errors.append(f"{concept.concept_id} has unknown broader concept {broader}")
    errors.extend(_hierarchy_cycle_errors(bundle.concepts))
    return errors


def build_nz_ontology_graph(bundle: NZOntologyBundle | None = None) -> Graph:
    """Build an RDF graph for NZ ontology candidates and SKOS schemes."""
    resolved = bundle or build_nz_ontology_bundle()
    graph = Graph()
    graph.bind("nz", NZ)
    graph.bind("nzvocab", NZVOCAB)
    graph.bind("evidence", EVIDENCE)
    graph.bind("skos", SKOS)
    graph.bind("owl", OWL)
    graph.bind("prov", PROV)
    graph.bind("dcterms", DCTERMS)
    for concept in resolved.concepts:
        subject = URIRef(concept.uri)
        graph.add((subject, RDF.type, _rdf_type(concept)))
        graph.add((subject, RDFS.label, RdfLiteral(concept.label)))
        graph.add((subject, SKOS.definition, RdfLiteral(concept.definition)))
        graph.add((subject, NZ.applicationArea, RdfLiteral(concept.application_area)))
        graph.add((subject, NZ.authority, RdfLiteral(concept.authority)))
        graph.add((subject, NZ.reviewStatus, RdfLiteral(concept.review_status)))
        graph.add((subject, NZ.confidence, RdfLiteral(concept.confidence, datatype=XSD.decimal)))
        for broader in concept.broader:
            graph.add((subject, RDFS.subClassOf, NZ[broader]))
        for related in concept.related:
            graph.add((subject, SKOS.related, NZ[related]))
        for anchor in concept.ontology_anchors:
            anchor_node = _anchor_uri(anchor)
            graph.add((subject, _mapping_predicate_uri(anchor.predicate), anchor_node))
            graph.add((anchor_node, RDFS.label, RdfLiteral(anchor.term)))
            graph.add((anchor_node, DC.source, RdfLiteral(anchor.standard)))
            if anchor.mapping_id:
                graph.add((subject, NZ.mappingId, RdfLiteral(anchor.mapping_id)))
        for evidence in concept.evidence:
            evidence_node = EVIDENCE[evidence.evidence_id]
            graph.add((evidence_node, RDF.type, PROV.Entity))
            graph.add((evidence_node, DCTERMS.source, RdfLiteral(evidence.source)))
            graph.add((evidence_node, NZ.evidenceType, RdfLiteral(evidence.evidence_type)))
            graph.add((evidence_node, RDF.value, RdfLiteral(evidence.value)))
            graph.add((subject, PROV.wasDerivedFrom, evidence_node))
    _add_skos_schemes(graph, resolved.controlled_vocabularies)
    return graph


def write_nz_ontology_artifacts(output_dir: Path | str | None = None) -> dict[str, Path]:
    """Write Track 31 JSON, Turtle, JSON-LD, and SKOS artifacts."""
    target_dir = Path(output_dir) if output_dir is not None else repo_root() / "data" / "ontologies"
    target_dir.mkdir(parents=True, exist_ok=True)
    bundle = build_nz_ontology_bundle()
    graph = build_nz_ontology_graph(bundle)
    paths = {
        NZ_ONTOLOGY_MANIFEST_FILENAME: target_dir / NZ_ONTOLOGY_MANIFEST_FILENAME,
        NZ_ONTOLOGY_TURTLE_FILENAME: target_dir / NZ_ONTOLOGY_TURTLE_FILENAME,
        NZ_ONTOLOGY_JSONLD_FILENAME: target_dir / NZ_ONTOLOGY_JSONLD_FILENAME,
        NZ_ONTOLOGY_SKOS_FILENAME: target_dir / NZ_ONTOLOGY_SKOS_FILENAME,
    }
    paths[NZ_ONTOLOGY_MANIFEST_FILENAME].write_text(
        json.dumps(bundle.to_dict(), indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    paths[NZ_ONTOLOGY_TURTLE_FILENAME].write_text(
        graph.serialize(format="turtle"),
        encoding="utf-8",
    )
    paths[NZ_ONTOLOGY_JSONLD_FILENAME].write_text(
        graph.serialize(format="json-ld", indent=2),
        encoding="utf-8",
    )
    paths[NZ_ONTOLOGY_SKOS_FILENAME].write_text(
        json.dumps(_skos_manifest(bundle.controlled_vocabularies), indent=2, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    return paths


def _seed_concepts(
    rows: tuple[dict[str, Any], ...],
    mappings: tuple[OntologyMappingRecord, ...],
) -> tuple[NZOntologyConcept, ...]:
    row_index = {
        (str(row["system_key"]), str(row["upstream_standard"])): row for row in rows
    }
    mapping_index = {record.mapping_id: record for record in mappings}

    return (
        _concept(
            "NZActOntology",
            "NZ Act ontology",
            "NZ-specific ontology for Acts, Bills, provisions, amendments, and commencement.",
            "act_structure",
            "class",
            "induced_nz",
            0.86,
            _coverage_evidence(row_index, "akn_legal_docml", "Akoma Ntoso"),
            (
                _anchor("Akoma Ntoso", "act", mapping_index),
                _anchor("ELI", "LegalResource", mapping_index),
            ),
        ),
        _concept(
            "NZProvision",
            "NZ provision",
            "A section, clause, schedule item, or regulation provision with stable anchors.",
            "act_structure",
            "class",
            "induced_nz",
            0.82,
            _coverage_evidence(row_index, "akn_legal_docml", "ELI"),
            (_anchor("schema.org/Legislation", "legislationSection", mapping_index),),
            broader=("NZActOntology",),
        ),
        _concept(
            "NZHansardOntology",
            "NZ Hansard ontology",
            "NZ-specific ontology for debate speeches, topics, questions, and votes.",
            "hansard_debate_topics",
            "class",
            "induced_nz",
            0.84,
            _mapping_evidence("sioc-post-to-akn-debate"),
            (_anchor("SIOC", "Post", mapping_index, "sioc-post-to-akn-debate"),),
        ),
        _concept(
            "NZDebateTopic",
            "NZ debate topic",
            "A reviewable topic label induced from debate text and publication metadata.",
            "hansard_debate_topics",
            "controlled_vocabulary",
            "induced_nz",
            0.78,
            _coverage_evidence(row_index, "knowledge_graph_exports", "SKOS"),
            (_anchor("SKOS", "Concept", mapping_index),),
            broader=("NZHansardOntology",),
        ),
        _concept(
            "NZCourtOntology",
            "NZ court ontology",
            "NZ-specific ontology for courts, court levels, judgments, and case citations.",
            "court_hierarchy",
            "class",
            "induced_nz",
            0.74,
            _coverage_evidence(row_index, "akn_legal_docml", "ECLI"),
            (_anchor("ECLI", "court", mapping_index), _anchor("schema.org", "Court", mapping_index)),
        ),
        _concept(
            "NZCourtLevel",
            "NZ court level",
            "A controlled court hierarchy level used for judgment and citation metadata.",
            "court_hierarchy",
            "controlled_vocabulary",
            "induced_nz",
            0.72,
            _coverage_evidence(row_index, "akn_legal_docml", "ECLI"),
            (_anchor("SKOS", "Concept", mapping_index),),
            broader=("NZCourtOntology",),
        ),
        _concept(
            "Tikanga",
            "Tikanga",
            "Māori law, values, and customary practice as a reviewable NZ legal concept.",
            "maori_legal_concepts",
            "controlled_vocabulary",
            "induced_nz",
            0.8,
            (CorpusEvidence("maori-guard-tikanga", "src/nlp_policy_nz/guard.py", "term", "tikanga"),),
            (_anchor("SKOS", "Concept", mapping_index), _anchor("LKIF", "Legal concept", mapping_index)),
        ),
        _concept(
            "TeTiriti",
            "Te Tiriti",
            "Te Tiriti o Waitangi references in legal and parliamentary sources.",
            "maori_legal_concepts",
            "controlled_vocabulary",
            "induced_nz",
            0.79,
            (CorpusEvidence("maori-guard-te-tiriti", "docs/nz_ontologies.md", "term", "Te Tiriti"),),
            (_anchor("SKOS", "Concept", mapping_index),),
        ),
        _concept(
            "NZGovernmentAgencyOntology",
            "NZ government agency ontology",
            "NZ-specific ontology for agencies, offices, portfolios, and public organizations.",
            "government_agencies",
            "class",
            "induced_nz",
            0.78,
            _coverage_evidence(row_index, "knowledge_graph_exports", "W3C ORG"),
            (_anchor("W3C ORG", "Organization", mapping_index), _anchor("Popolo", "Organization", mapping_index)),
        ),
        _concept(
            "NZPublicOrganization",
            "NZ public organization",
            "A government department, Crown entity, office, or agency in NZ public sector data.",
            "government_agencies",
            "class",
            "authoritative_external",
            0.88,
            _coverage_evidence(row_index, "knowledge_graph_exports", "W3C ORG"),
            (_anchor("W3C ORG", "Organization", mapping_index),),
            broader=("NZGovernmentAgencyOntology",),
            review_status="approved",
        ),
    )


def _concept(
    concept_id: str,
    label: str,
    definition: str,
    application_area: ApplicationArea,
    kind: ConceptKind,
    authority: ConceptAuthority,
    confidence: float,
    evidence: tuple[CorpusEvidence, ...],
    anchors: tuple[OntologyAnchor, ...],
    *,
    broader: tuple[str, ...] = (),
    related: tuple[str, ...] = (),
    review_status: ReviewStatus | None = None,
) -> NZOntologyConcept:
    resolved_status: ReviewStatus = (
        review_status
        if review_status is not None
        else "approved"
        if authority == "authoritative_external"
        else "needs_review"
    )
    return NZOntologyConcept(
        concept_id=concept_id,
        label=label,
        definition=definition,
        application_area=application_area,
        kind=kind,
        authority=authority,
        confidence=confidence,
        evidence=evidence,
        ontology_anchors=anchors,
        broader=broader,
        related=related,
        review_status=resolved_status,
    )


def _coverage_evidence(
    row_index: dict[tuple[str, str], dict[str, Any]],
    system_key: str,
    standard: str,
) -> tuple[CorpusEvidence, ...]:
    row = row_index[(system_key, standard)]
    source = ", ".join(row["present_local_files"] or row["local_files"])
    value = f"{row['coverage_status']} coverage for {standard}: {row['notes']}"
    return (
        CorpusEvidence(
            evidence_id=f"coverage-{_slug(system_key)}-{_slug(standard)}",
            source=source,
            evidence_type="track25_coverage_row",
            value=value,
        ),
    )


def _mapping_evidence(mapping_id: str) -> tuple[CorpusEvidence, ...]:
    return (
        CorpusEvidence(
            evidence_id=f"mapping-{_slug(mapping_id)}",
            source="src/nlp_policy_nz/ontology/mapping_graph.py",
            evidence_type="track29_mapping_record",
            value=mapping_id,
        ),
    )


def _anchor(
    standard: str,
    term: str,
    mapping_index: dict[str, OntologyMappingRecord],
    mapping_id: str = "",
) -> OntologyAnchor:
    record = mapping_index.get(mapping_id) if mapping_id else None
    return OntologyAnchor(
        standard=standard,
        term=term,
        mapping_id=mapping_id,
        predicate=record.mapping_predicate if record else "skos:relatedMatch",
    )


def _concepts(raw: tuple[tuple[str, str, str], ...]) -> tuple[SKOSConcept, ...]:
    return tuple(
        sorted(
            (SKOSConcept(concept_id=concept_id, pref_label=label, definition=definition)
             for concept_id, label, definition in raw),
            key=lambda concept: concept.pref_label.casefold(),
        )
    )


def _hierarchy_cycle_errors(concepts: tuple[NZOntologyConcept, ...]) -> list[str]:
    broader = {concept.concept_id: set(concept.broader) for concept in concepts}
    errors: list[str] = []

    def visit(node: str, path: tuple[str, ...]) -> None:
        if node in path:
            errors.append(f"cycle detected: {' -> '.join((*path, node))}")
            return
        for parent in broader.get(node, set()):
            visit(parent, (*path, node))

    for concept in concepts:
        visit(concept.concept_id, ())
    return sorted(set(errors))


def _rdf_type(concept: NZOntologyConcept) -> URIRef:
    if concept.kind == "class":
        return OWL.Class
    if concept.kind == "property":
        return RDF.Property
    return SKOS.Concept


def _anchor_uri(anchor: OntologyAnchor) -> URIRef:
    return URIRef(f"{NZ}anchor/{_slug(anchor.standard)}/{_slug(anchor.term)}")


def _mapping_predicate_uri(predicate: MappingPredicate | str) -> URIRef:
    namespace, name = predicate.split(":", 1)
    if namespace == "skos":
        return SKOS[name]
    if namespace == "owl":
        return OWL[name]
    if namespace == "rdfs":
        return RDFS[name]
    return NZ[f"source/{name}"]


def _add_skos_schemes(graph: Graph, schemes: tuple[SKOSConceptScheme, ...]) -> None:
    for scheme in schemes:
        scheme_uri = URIRef(scheme.uri)
        graph.add((scheme_uri, RDF.type, SKOS.ConceptScheme))
        graph.add((scheme_uri, SKOS.prefLabel, RdfLiteral(scheme.pref_label)))
        graph.add((scheme_uri, SKOS.definition, RdfLiteral(scheme.definition)))
        for concept in scheme.concepts:
            concept_uri = URIRef(concept.uri)
            graph.add((concept_uri, RDF.type, SKOS.Concept))
            graph.add((concept_uri, SKOS.inScheme, scheme_uri))
            graph.add((concept_uri, SKOS.prefLabel, RdfLiteral(concept.pref_label)))
            graph.add((concept_uri, SKOS.definition, RdfLiteral(concept.definition)))
            for broader in concept.broader:
                graph.add((concept_uri, SKOS.broader, NZVOCAB[broader]))


def _skos_manifest(schemes: tuple[SKOSConceptScheme, ...]) -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "track_id": "track31_nz_data_driven_ontologies_20260625",
        "scheme_count": len(schemes),
        "schemes": [scheme.to_dict() for scheme in schemes],
    }


def _slug(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.casefold()).strip("-")
    return normalized or "item"


__all__ = [
    "NZ_ONTOLOGY_JSONLD_FILENAME",
    "NZ_ONTOLOGY_MANIFEST_FILENAME",
    "NZ_ONTOLOGY_SKOS_FILENAME",
    "NZ_ONTOLOGY_TURTLE_FILENAME",
    "ApplicationArea",
    "ConceptAuthority",
    "ConceptKind",
    "CorpusEvidence",
    "NZOntologyBundle",
    "NZOntologyConcept",
    "OntologyAnchor",
    "SKOSConcept",
    "SKOSConceptScheme",
    "build_nz_ontology_bundle",
    "build_nz_ontology_graph",
    "build_skos_concept_schemes",
    "validate_nz_ontology_bundle",
    "write_nz_ontology_artifacts",
]
