"""Track 28 ontology discovery and intake artifacts.

The discovery set is curated from official standards pages, public vocabulary
registries, government metadata standards, and rules-as-code tool documentation.
It is intentionally deterministic: live discovery remains a research activity,
while checked-in artifacts record the reviewed intake decisions.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final, Literal

from nlp_policy_nz.ontology.registry import (
    BLOCKER_TYPES,
    TRACK26_STANDARDS_REGISTRY,
    BlockerType,
    ImplementationStatus,
    StandardsRegistryEntry,
)

DiscoveryCategory = Literal[
    "official_standard",
    "government_vocabulary",
    "legal_informatics",
    "rules_as_code",
    "graph_vector_publication",
]
TriageDecision = Literal["implement", "map-only", "monitor", "reject"]
RiskLevel = Literal["low", "medium", "high"]

DISCOVERY_LOG_FILENAME: Final[str] = "track28_discovery_log.json"
TRIAGE_FILENAME: Final[str] = "track28_triage.json"
REGISTRY_ADDENDUM_FILENAME: Final[str] = "track28_standards_registry_addendum.json"
BLOCKERS_FILENAME: Final[str] = "track28_blockers.json"

DISCOVERY_CATEGORIES: Final[tuple[DiscoveryCategory, ...]] = (
    "official_standard",
    "government_vocabulary",
    "legal_informatics",
    "rules_as_code",
    "graph_vector_publication",
)
TRIAGE_DECISIONS: Final[tuple[TriageDecision, ...]] = (
    "implement",
    "map-only",
    "monitor",
    "reject",
)


@dataclass(frozen=True, slots=True)
class OntologyDiscoveryCandidate:
    """One reviewed ontology, vocabulary, schema, or standards candidate."""

    candidate_id: str
    name: str
    category: DiscoveryCategory
    source_url: str
    authority: str
    source_license: str
    format: str
    version: str
    relevance: str
    risk: RiskLevel
    nz_relevance_score: int
    authority_score: int
    interoperability_score: int
    license_score: int
    maintenance_score: int
    implementation_effort: str
    decision: TriageDecision
    registry_standard: str | None = None
    blocker_type: BlockerType = "none"
    blocker_source: str = ""
    notes: str = ""

    @property
    def total_score(self) -> int:
        """Return the deterministic candidate score."""
        return (
            self.nz_relevance_score
            + self.authority_score
            + self.interoperability_score
            + self.license_score
            + self.maintenance_score
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the candidate to JSON-ready data."""
        return {
            "candidate_id": self.candidate_id,
            "name": self.name,
            "category": self.category,
            "source_url": self.source_url,
            "authority": self.authority,
            "source_license": self.source_license,
            "format": self.format,
            "version": self.version,
            "relevance": self.relevance,
            "risk": self.risk,
            "scores": {
                "authority": self.authority_score,
                "nz_relevance": self.nz_relevance_score,
                "interoperability": self.interoperability_score,
                "license": self.license_score,
                "maintenance": self.maintenance_score,
                "total": self.total_score,
            },
            "implementation_effort": self.implementation_effort,
            "decision": self.decision,
            "registry_standard": self.registry_standard,
            "blocker_type": self.blocker_type,
            "blocker_source": self.blocker_source,
            "notes": self.notes,
        }

    def to_registry_entry(self) -> StandardsRegistryEntry:
        """Convert an approved candidate into a Track 26-style registry entry."""
        if self.registry_standard is None:
            msg = f"{self.candidate_id} has no registry_standard"
            raise ValueError(msg)
        return StandardsRegistryEntry(
            standard=self.registry_standard,
            source_url=self.source_url,
            source_license=self.source_license,
            local_representation_paths=(
                "src/nlp_policy_nz/quality/track28_ontology_discovery.py",
                "data/ontologies/track28_discovery_log.json",
            ),
            implementation_status=_implementation_status_for_decision(self.decision),
            blocker_type=self.blocker_type,
            blocker_source=self.blocker_source,
            notes=self.notes,
        )


def _implementation_status_for_decision(decision: TriageDecision) -> ImplementationStatus:
    if decision == "implement":
        return "missing"
    if decision == "map-only":
        return "adjacent"
    if decision == "monitor":
        return "adjacent"
    return "missing"


DISCOVERY_CANDIDATES: Final[tuple[OntologyDiscoveryCandidate, ...]] = (
    OntologyDiscoveryCandidate(
        candidate_id="w3c_owl2",
        name="OWL 2 Web Ontology Language",
        category="official_standard",
        source_url="https://www.w3.org/TR/owl2-overview/",
        authority="W3C",
        source_license="W3C Document License",
        format="OWL/RDF",
        version="OWL 2 Recommendation",
        relevance="Formal ontology modelling for standards alignment and inference tracks.",
        risk="low",
        nz_relevance_score=4,
        authority_score=5,
        interoperability_score=5,
        license_score=5,
        maintenance_score=5,
        implementation_effort="medium",
        decision="implement",
        registry_standard="OWL 2",
        blocker_type="specification",
        blocker_source="local OWL profile for extracted legislative concepts and ontology mappings",
        notes="Core substrate for Track 29 and Track 30 ontology mapping work.",
    ),
    OntologyDiscoveryCandidate(
        candidate_id="w3c_rdf12",
        name="RDF 1.2 Concepts and Abstract Syntax",
        category="official_standard",
        source_url="https://www.w3.org/TR/rdf12-concepts/",
        authority="W3C",
        source_license="W3C Document License",
        format="RDF",
        version="RDF 1.2",
        relevance="Graph interchange model for ontology mapping, provenance, and publication.",
        risk="low",
        nz_relevance_score=4,
        authority_score=5,
        interoperability_score=5,
        license_score=5,
        maintenance_score=5,
        implementation_effort="low",
        decision="implement",
        registry_standard="RDF 1.2",
        blocker_type="integration",
        blocker_source="RDF 1.2 serializer compatibility review across current rdflib outputs",
        notes="Use as graph baseline; keep existing RDF/Turtle exports compatible.",
    ),
    OntologyDiscoveryCandidate(
        candidate_id="w3c_shacl",
        name="SHACL",
        category="official_standard",
        source_url="https://www.w3.org/TR/shacl/",
        authority="W3C",
        source_license="W3C Document License",
        format="RDF shapes",
        version="W3C Recommendation",
        relevance="Validation layer for ontology manifests, graph exports, and extraction outputs.",
        risk="low",
        nz_relevance_score=4,
        authority_score=5,
        interoperability_score=5,
        license_score=5,
        maintenance_score=5,
        implementation_effort="medium",
        decision="implement",
        registry_standard="SHACL",
        blocker_type="integration",
        blocker_source="SHACL shape set for extraction manifests and ontology graph exports",
        notes="Useful before Track 29 graph publication and Track 44 data quality gates.",
    ),
    OntologyDiscoveryCandidate(
        candidate_id="w3c_odrl",
        name="ODRL Information Model",
        category="official_standard",
        source_url="https://www.w3.org/TR/odrl-model/",
        authority="W3C",
        source_license="W3C Document License",
        format="RDF vocabulary",
        version="W3C Recommendation",
        relevance="Rights, permissions, prohibitions, duties, and policy constraints vocabulary.",
        risk="medium",
        nz_relevance_score=4,
        authority_score=5,
        interoperability_score=4,
        license_score=5,
        maintenance_score=4,
        implementation_effort="medium",
        decision="map-only",
        registry_standard="ODRL",
        blocker_type="specification",
        blocker_source="crosswalk from deontic extraction families to ODRL duties/prohibitions",
        notes="Map deontic outputs cautiously; ODRL is not a full legal reasoning ontology.",
    ),
    OntologyDiscoveryCandidate(
        candidate_id="w3c_sosa_ssn",
        name="SOSA/SSN",
        category="graph_vector_publication",
        source_url="https://www.w3.org/TR/vocab-ssn/",
        authority="W3C",
        source_license="W3C Document License",
        format="OWL/RDF vocabulary",
        version="W3C Recommendation",
        relevance="Observation and measurement model for corpus analytics and quality metrics.",
        risk="medium",
        nz_relevance_score=2,
        authority_score=5,
        interoperability_score=4,
        license_score=5,
        maintenance_score=4,
        implementation_effort="medium",
        decision="monitor",
        registry_standard="SOSA/SSN",
        blocker_type="specification",
        blocker_source="analytics measurement model for Track 32 statistics and quality metrics",
        notes="Valuable later for analytics provenance; not core to legislation extraction.",
    ),
    OntologyDiscoveryCandidate(
        candidate_id="nzgls",
        name="New Zealand Government Locator Service",
        category="government_vocabulary",
        source_url="https://www.data.govt.nz/manage-data/policies/nzgls/",
        authority="New Zealand Government",
        source_license="New Zealand Government reuse terms",
        format="metadata element set",
        version="NZGLS",
        relevance="NZ public-sector metadata for discoverable datasets and government resources.",
        risk="low",
        nz_relevance_score=5,
        authority_score=5,
        interoperability_score=4,
        license_score=4,
        maintenance_score=3,
        implementation_effort="medium",
        decision="implement",
        registry_standard="NZGLS",
        blocker_type="specification",
        blocker_source="field-level crosswalk from NZGLS metadata to DCAT/DCAT-AP catalog records",
        notes="Highest-value NZ-specific metadata addition for dataset publication.",
    ),
    OntologyDiscoveryCandidate(
        candidate_id="agls",
        name="Australian Government Locator Service",
        category="government_vocabulary",
        source_url="https://www.agls.gov.au/",
        authority="Australian Government",
        source_license="Australian Government reuse terms",
        format="metadata element set",
        version="AGLS",
        relevance="Commonwealth metadata vocabulary adjacent to NZ public-sector cataloguing.",
        risk="low",
        nz_relevance_score=3,
        authority_score=4,
        interoperability_score=4,
        license_score=4,
        maintenance_score=3,
        implementation_effort="low",
        decision="map-only",
        registry_standard="AGLS",
        blocker_type="specification",
        blocker_source="AGLS to NZGLS/DCAT crosswalk for trans-Tasman metadata imports",
        notes="Useful for AU-to-NZ corpus transfer and Isaacus-adjacent datasets.",
    ),
    OntologyDiscoveryCandidate(
        candidate_id="data_govt_nz_metadata",
        name="data.govt.nz Dataset Metadata",
        category="government_vocabulary",
        source_url="https://www.data.govt.nz/manage-data/",
        authority="New Zealand Government",
        source_license="New Zealand Government reuse terms",
        format="dataset metadata guidance",
        version="current public guidance",
        relevance="Practical dataset publication fields for NZ legal data outputs.",
        risk="low",
        nz_relevance_score=5,
        authority_score=5,
        interoperability_score=4,
        license_score=4,
        maintenance_score=4,
        implementation_effort="medium",
        decision="implement",
        registry_standard="data.govt.nz Dataset Metadata",
        blocker_type="integration",
        blocker_source="publication manifest exporter mapping repo release metadata to data.govt.nz fields",
        notes="Complements DCAT and NZGLS for local publication readiness.",
    ),
    OntologyDiscoveryCandidate(
        candidate_id="lac_guidelines",
        name="Legislation Guidelines metadata concepts",
        category="government_vocabulary",
        source_url="https://www.legislation.govt.nz/guide/",
        authority="New Zealand Legislation Design and Advisory Committee",
        source_license="New Zealand Government reuse terms",
        format="legal drafting guidance",
        version="current online guide",
        relevance="NZ legislative design concepts for classification, commencement, amendment, and repeal.",
        risk="low",
        nz_relevance_score=5,
        authority_score=5,
        interoperability_score=3,
        license_score=4,
        maintenance_score=4,
        implementation_effort="medium",
        decision="implement",
        registry_standard="NZ Legislation Guidelines",
        blocker_type="data",
        blocker_source="controlled concept inventory from Legislation Guidelines headings and examples",
        notes="Use as NZ-specific extraction taxonomy seed, not as executable legal advice.",
    ),
    OntologyDiscoveryCandidate(
        candidate_id="figi",
        name="Financial Instrument Global Identifier",
        category="government_vocabulary",
        source_url="https://www.openfigi.com/about/figi",
        authority="Bloomberg / Object Management Group",
        source_license="OpenFIGI terms",
        format="identifier standard",
        version="current",
        relevance="Financial instrument identifiers for securities-related legislation only.",
        risk="medium",
        nz_relevance_score=1,
        authority_score=3,
        interoperability_score=3,
        license_score=3,
        maintenance_score=4,
        implementation_effort="high",
        decision="reject",
        blocker_type="data",
        blocker_source="not broadly relevant to legislative ontology intake",
        notes="Too domain-specific for core Track 28; revisit only for financial-market corpora.",
    ),
    OntologyDiscoveryCandidate(
        candidate_id="legal_knowledge_graph_literature",
        name="Legal knowledge graph ontology patterns",
        category="legal_informatics",
        source_url="https://dl.acm.org/conference/icail",
        authority="ICAIL / legal informatics literature",
        source_license="publisher-specific",
        format="research literature",
        version="ongoing",
        relevance="Design patterns for legal knowledge graph construction and ontology alignment.",
        risk="medium",
        nz_relevance_score=3,
        authority_score=3,
        interoperability_score=4,
        license_score=2,
        maintenance_score=3,
        implementation_effort="medium",
        decision="monitor",
        registry_standard="Legal knowledge graph literature patterns",
        blocker_type="specification",
        blocker_source="reviewed bibliography and extracted ontology pattern inventory",
        notes="Do not import publisher text; use as monitored design reference.",
    ),
    OntologyDiscoveryCandidate(
        candidate_id="jurix_ontology_patterns",
        name="JURIX legal ontology patterns",
        category="legal_informatics",
        source_url="https://jurix.nl/",
        authority="JURIX Foundation",
        source_license="publisher-specific",
        format="research literature",
        version="ongoing",
        relevance="European legal knowledge representation and reasoning patterns.",
        risk="medium",
        nz_relevance_score=3,
        authority_score=3,
        interoperability_score=4,
        license_score=2,
        maintenance_score=3,
        implementation_effort="medium",
        decision="monitor",
        registry_standard="JURIX ontology patterns",
        blocker_type="specification",
        blocker_source="curated bibliography with reusable ontology pattern summaries",
        notes="Monitor for Track 30 mapping inference and legal reasoning design.",
    ),
    OntologyDiscoveryCandidate(
        candidate_id="catala",
        name="Catala",
        category="rules_as_code",
        source_url="https://catala-lang.org/",
        authority="Catala project",
        source_license="project-specific open-source license",
        format="rules-as-code language",
        version="current project documentation",
        relevance="Legislative programming language with statute-oriented structure.",
        risk="medium",
        nz_relevance_score=4,
        authority_score=3,
        interoperability_score=4,
        license_score=3,
        maintenance_score=4,
        implementation_effort="medium",
        decision="map-only",
        registry_standard="Catala",
        blocker_type="integration",
        blocker_source="crosswalk from extraction manifests to Catala scopes and definitions",
        notes="Keep as downstream mapping target; do not add runtime dependency.",
    ),
    OntologyDiscoveryCandidate(
        candidate_id="docassemble",
        name="Docassemble",
        category="rules_as_code",
        source_url="https://docassemble.org/",
        authority="Docassemble project",
        source_license="project-specific open-source license",
        format="interview/rules platform",
        version="current project documentation",
        relevance="Eligibility/interview flow modelling for legal guidance applications.",
        risk="medium",
        nz_relevance_score=3,
        authority_score=3,
        interoperability_score=3,
        license_score=3,
        maintenance_score=4,
        implementation_effort="medium",
        decision="monitor",
        registry_standard="Docassemble",
        blocker_type="integration",
        blocker_source="reviewed downstream interview-flow use case and extraction-to-question mapping",
        notes="Useful later for guidance UI, not core ontology registry implementation.",
    ),
    OntologyDiscoveryCandidate(
        candidate_id="ergoai",
        name="ErgoAI / Flora-2 rule knowledge representation",
        category="rules_as_code",
        source_url="https://coherentknowledge.com/",
        authority="Coherent Knowledge",
        source_license="commercial/product-specific",
        format="rule language",
        version="current public product information",
        relevance="Rule reasoning design reference for legal/enterprise knowledge bases.",
        risk="high",
        nz_relevance_score=2,
        authority_score=2,
        interoperability_score=3,
        license_score=1,
        maintenance_score=3,
        implementation_effort="high",
        decision="reject",
        blocker_type="integration",
        blocker_source="commercial runtime and no immediate open ontology intake benefit",
        notes="Reject for now; avoid commercial runtime coupling.",
    ),
    OntologyDiscoveryCandidate(
        candidate_id="stoica",
        name="STOICA rules-as-code reference",
        category="rules_as_code",
        source_url="https://github.com/",
        authority="community / unverified",
        source_license="unverified",
        format="rules-as-code reference",
        version="unverified",
        relevance="Mentioned as possible rules-as-code tooling but not verified as an authoritative ontology.",
        risk="high",
        nz_relevance_score=1,
        authority_score=1,
        interoperability_score=1,
        license_score=1,
        maintenance_score=1,
        implementation_effort="high",
        decision="reject",
        blocker_type="specification",
        blocker_source="no authoritative source identified during Track 28 intake",
        notes="Do not add until a concrete, authoritative source is provided.",
    ),
)


def discovery_candidates() -> tuple[OntologyDiscoveryCandidate, ...]:
    """Return candidates in deterministic ID order."""
    return tuple(sorted(DISCOVERY_CANDIDATES, key=lambda candidate: candidate.candidate_id))


def build_discovery_log() -> dict[str, Any]:
    """Build the Track 28 discovery log artifact."""
    candidates = [candidate.to_dict() for candidate in discovery_candidates()]
    return {
        "schema_version": "1.0",
        "track_id": "track28_ontology_discovery_intake_20260625",
        "discovery_scope": list(DISCOVERY_CATEGORIES),
        "candidate_count": len(candidates),
        "candidates": candidates,
    }


def build_triage() -> dict[str, Any]:
    """Build the triage summary and candidate ranking artifact."""
    candidates = discovery_candidates()
    decision_counts = dict.fromkeys(TRIAGE_DECISIONS, 0)
    for candidate in candidates:
        decision_counts[candidate.decision] += 1
    ranked = sorted(candidates, key=lambda candidate: (-candidate.total_score, candidate.candidate_id))
    return {
        "schema_version": "1.0",
        "track_id": "track28_ontology_discovery_intake_20260625",
        "decision_counts": decision_counts,
        "ranked_candidates": [
            {
                "candidate_id": candidate.candidate_id,
                "name": candidate.name,
                "decision": candidate.decision,
                "total_score": candidate.total_score,
                "risk": candidate.risk,
            }
            for candidate in ranked
        ],
        "scoring_notes": (
            "Each score is 1-5. Total score sums authority, NZ relevance, "
            "interoperability, license/access, and maintenance status."
        ),
    }


def approved_registry_addendum() -> tuple[StandardsRegistryEntry, ...]:
    """Return implement/map-only candidates converted to registry entries."""
    approved = [
        candidate.to_registry_entry()
        for candidate in discovery_candidates()
        if candidate.decision in {"implement", "map-only"}
    ]
    return tuple(sorted(approved, key=lambda entry: entry.standard.casefold()))


def build_registry_addendum() -> dict[str, Any]:
    """Build Track 26-style registry addendum entries from approved candidates."""
    existing = {entry.standard.casefold() for entry in TRACK26_STANDARDS_REGISTRY}
    entries = [entry.to_dict() for entry in approved_registry_addendum()]
    return {
        "schema_version": "1.0",
        "registry_name": "track28_standards_registry_addendum",
        "extends_registry": "track26_standards_registry",
        "entries": entries,
        "summary": {
            "entry_count": len(entries),
            "new_standard_count": sum(
                1 for entry in entries if str(entry["standard"]).casefold() not in existing
            ),
            "existing_overlap_count": sum(
                1 for entry in entries if str(entry["standard"]).casefold() in existing
            ),
        },
        "registry_notes": (
            "These entries are approved intake addenda. Track 29/30 decide exact "
            "mapping and implementation order."
        ),
    }


def build_blockers() -> dict[str, Any]:
    """Build implementation blocker records for non-rejected candidates."""
    blockers = []
    for candidate in discovery_candidates():
        if candidate.decision == "reject":
            continue
        if candidate.blocker_type == "none":
            continue
        blockers.append(
            {
                "blocker_id": f"track28::{candidate.candidate_id}::{candidate.blocker_type}",
                "candidate_id": candidate.candidate_id,
                "standard": candidate.registry_standard or candidate.name,
                "blocker_type": candidate.blocker_type,
                "blocker_source": candidate.blocker_source,
                "decision": candidate.decision,
                "risk": candidate.risk,
            }
        )
    return {
        "schema_version": "1.0",
        "track_id": "track28_ontology_discovery_intake_20260625",
        "blocker_count": len(blockers),
        "valid_blocker_types": list(BLOCKER_TYPES),
        "blockers": sorted(blockers, key=lambda row: row["blocker_id"]),
    }


def write_track28_discovery_artifacts(output_dir: Path | str | None = None) -> dict[str, Path]:
    """Write all deterministic Track 28 discovery artifacts."""
    target_dir = Path(output_dir) if output_dir is not None else repo_root() / "data" / "ontologies"
    target_dir.mkdir(parents=True, exist_ok=True)
    artifacts = {
        DISCOVERY_LOG_FILENAME: build_discovery_log(),
        TRIAGE_FILENAME: build_triage(),
        REGISTRY_ADDENDUM_FILENAME: build_registry_addendum(),
        BLOCKERS_FILENAME: build_blockers(),
    }
    written: dict[str, Path] = {}
    for filename, payload in artifacts.items():
        path = target_dir / filename
        path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        written[filename] = path
    return written


def repo_root() -> Path:
    """Return the repository root."""
    return Path(__file__).resolve().parents[3]


__all__ = [
    "BLOCKERS_FILENAME",
    "DISCOVERY_CANDIDATES",
    "DISCOVERY_CATEGORIES",
    "DISCOVERY_LOG_FILENAME",
    "REGISTRY_ADDENDUM_FILENAME",
    "TRIAGE_DECISIONS",
    "TRIAGE_FILENAME",
    "DiscoveryCategory",
    "OntologyDiscoveryCandidate",
    "RiskLevel",
    "TriageDecision",
    "approved_registry_addendum",
    "build_blockers",
    "build_discovery_log",
    "build_registry_addendum",
    "build_triage",
    "discovery_candidates",
    "repo_root",
    "write_track28_discovery_artifacts",
]
