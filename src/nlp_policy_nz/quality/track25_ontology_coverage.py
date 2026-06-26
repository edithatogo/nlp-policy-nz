from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import re
from typing import Any, Final, Literal

CoverageStatus = Literal["implemented", "partial", "prototype", "adjacent", "missing"]
BlockerType = Literal["none", "source_data", "specification", "validation", "integration"]
Priority = Literal["p0", "p1", "p2", "p3"]
LocalFileStatus = Literal["complete", "partial"]

_STATUS_RANK: Final[dict[str, int]] = {
    "implemented": 0,
    "partial": 1,
    "prototype": 2,
    "adjacent": 3,
    "missing": 4,
}

_PRIORITY_RANK: Final[dict[str, int]] = {
    "p0": 0,
    "p1": 1,
    "p2": 2,
    "p3": 3,
}

_BLOCKER_PRIORITY: Final[dict[tuple[str, str], Priority]] = {
    ("implemented", "none"): "p3",
    ("partial", "source_data"): "p1",
    ("partial", "specification"): "p1",
    ("partial", "validation"): "p2",
    ("partial", "integration"): "p2",
    ("prototype", "integration"): "p2",
    ("prototype", "specification"): "p1",
    ("adjacent", "source_data"): "p2",
    ("adjacent", "specification"): "p2",
    ("missing", "source_data"): "p0",
    ("missing", "specification"): "p1",
    ("missing", "integration"): "p1",
    ("missing", "validation"): "p1",
}


@dataclass(frozen=True, slots=True)
class StandardCoverage:
    upstream_standard: str
    coverage_status: CoverageStatus
    blocker_type: BlockerType = "none"
    blocker_data_source: str = ""
    missing_features: tuple[str, ...] = ()
    priority: Priority | None = None
    notes: str = ""
    follow_on_track: str = ""

    def with_derived_priority(self) -> StandardCoverage:
        if self.priority is not None:
            return self
        derived = _BLOCKER_PRIORITY.get((self.coverage_status, self.blocker_type), "p2")
        return StandardCoverage(
            upstream_standard=self.upstream_standard,
            coverage_status=self.coverage_status,
            blocker_type=self.blocker_type,
            blocker_data_source=self.blocker_data_source,
            missing_features=self.missing_features,
            priority=derived,
            notes=self.notes,
            follow_on_track=self.follow_on_track,
        )

    def to_dict(self) -> dict[str, Any]:
        value = self.with_derived_priority()
        return {
            "upstream_standard": value.upstream_standard,
            "coverage_status": value.coverage_status,
            "blocker_type": value.blocker_type,
            "blocker_data_source": value.blocker_data_source,
            "missing_features": list(value.missing_features),
            "priority": value.priority,
            "notes": value.notes,
            "follow_on_track": value.follow_on_track,
        }


@dataclass(frozen=True, slots=True)
class OntologySystem:
    system_key: str
    system_name: str
    description: str
    local_files: tuple[str, ...]
    standards: tuple[StandardCoverage, ...]

    def to_dict(self, repo_root: Path) -> dict[str, Any]:
        present_local_files = _existing_relative_paths(repo_root, self.local_files)
        missing_local_files = tuple(path for path in self.local_files if path not in present_local_files)
        local_file_status: LocalFileStatus = "complete" if not missing_local_files else "partial"
        return {
            "system_key": self.system_key,
            "system_name": self.system_name,
            "description": self.description,
            "local_files": list(self.local_files),
            "present_local_files": list(present_local_files),
            "missing_local_files": list(missing_local_files),
            "local_file_status": local_file_status,
            "standards": [standard.to_dict() for standard in self.standards],
        }


SYSTEM_CATALOG: Final[tuple[OntologySystem, ...]] = (
    OntologySystem(
        system_key="akn_legal_docml",
        system_name="Akoma Ntoso / LegalDocML emitter",
        description="AKN v3 legal document emission and validation with FRBR/TLC-aware metadata hooks.",
        local_files=(
            "src/nlp_policy_nz/schema/akn_v3.py",
            "src/nlp_policy_nz/universal_framework_v3.py",
        ),
        standards=(
            StandardCoverage(
                upstream_standard="Akoma Ntoso",
                coverage_status="implemented",
                notes="Document emitters support amendment, bill, debate, and judgment formats.",
                follow_on_track="Track 26",
            ),
            StandardCoverage(
                upstream_standard="LegalDocML",
                coverage_status="implemented",
                notes="AKN v3 emitter and validator are present.",
                follow_on_track="Track 26",
            ),
            StandardCoverage(
                upstream_standard="FRBR",
                coverage_status="partial",
                blocker_type="source_data",
                blocker_data_source="Versioned work/expression/version inventory for Acts, Bills, debates, and judgments.",
                missing_features=("complete work-expression-version lineage", "cross-document version graph"),
                notes="Metadata hooks exist, but the repository still needs a fuller source inventory.",
                follow_on_track="Track 26",
            ),
            StandardCoverage(
                upstream_standard="TLC",
                coverage_status="partial",
                blocker_type="source_data",
                blocker_data_source="Temporal concept inventory for commencement, repeal, versioning, and amendment chronology.",
                missing_features=("complete temporal concept catalog", "uniform TLC concept mapping"),
                notes="Temporal metadata is present in hooks, but not yet a full ontology layer.",
                follow_on_track="Track 27",
            ),
            StandardCoverage(
                upstream_standard="ELI",
                coverage_status="missing",
                blocker_type="source_data",
                blocker_data_source="Versioned legislation source texts with stable public URIs and section-level anchors.",
                missing_features=("ELI URI templates", "versioned legal resource identifiers", "section anchors"),
                notes="This is the primary legislative identifier layer missing from the repo.",
                follow_on_track="Track 26",
            ),
            StandardCoverage(
                upstream_standard="ELI-DL",
                coverage_status="missing",
                blocker_type="source_data",
                blocker_data_source="Document-level metadata for versioned legislation and reusable ELI descriptors.",
                missing_features=("ELI metadata descriptors", "publication metadata mapping", "distribution metadata"),
                notes="Needs the same source inventory as ELI plus document-level metadata alignment.",
                follow_on_track="Track 26",
            ),
            StandardCoverage(
                upstream_standard="ECLI",
                coverage_status="missing",
                blocker_type="source_data",
                blocker_data_source="Case law corpus with stable court/case citation identifiers and judgments metadata.",
                missing_features=("ECLI identifiers", "court/case metadata registry", "judgment citation mapping"),
                notes="Judgment support exists, but not the authoritative citation layer.",
                follow_on_track="Track 26",
            ),
        ),
    ),
    OntologySystem(
        system_key="provenance",
        system_name="PROV-O provenance sidecars",
        description="Bundle, entity, activity, and agent provenance serialisation for pipeline artefacts.",
        local_files=(
            "src/nlp_policy_nz/provenance/serializer.py",
            "src/nlp_policy_nz/provenance/recorder.py",
        ),
        standards=(
            StandardCoverage(
                upstream_standard="PROV-O",
                coverage_status="implemented",
                notes="The repo emits PROV-O aligned JSON-LD bundles and provenance sidecars.",
            ),
        ),
    ),
    OntologySystem(
        system_key="linked_data_graphs",
        system_name="FOAF / SIOC linked data",
        description="Parliamentary and speech-level linked data graphs for MPs, parties, electorates, and debates.",
        local_files=(
            "src/nlp_policy_nz/linked_data/rdf.py",
            "src/nlp_policy_nz/linked_data/foaf.py",
            "src/nlp_policy_nz/linked_data/sioc.py",
        ),
        standards=(
            StandardCoverage(
                upstream_standard="FOAF",
                coverage_status="implemented",
                notes="Person, party, and electorate graphs are materialised with FOAF-style links.",
            ),
            StandardCoverage(
                upstream_standard="SIOC",
                coverage_status="implemented",
                notes="Debate speech exports are SIOC-aligned.",
            ),
        ),
    ),
    OntologySystem(
        system_key="knowledge_graph_exports",
        system_name="Wikidata / schema.org knowledge graph",
        description="Knowledge graph export, federation helpers, and NZ entity ontology mapping.",
        local_files=(
            "src/nlp_policy_nz/kb/wikidata_kg.py",
            "data/ontologies/nz_wikidata_map.ttl",
        ),
        standards=(
            StandardCoverage(
                upstream_standard="Wikidata",
                coverage_status="partial",
                blocker_type="source_data",
                blocker_data_source="Authoritative entity-to-QID mapping for acts, members, parties, electorates, and courts.",
                missing_features=("complete QID coverage", "verified source-to-QID reconciliation"),
                notes="Local ontology mapping exists, but the entity inventory is not yet exhaustive.",
                follow_on_track="Track 29",
            ),
            StandardCoverage(
                upstream_standard="schema.org",
                coverage_status="partial",
                blocker_type="specification",
                blocker_data_source="Complete legislation publication metadata model with stable landing-page fields.",
                missing_features=("full legislation object mapping", "publication and distribution metadata"),
                notes="The repo exports JSON-LD, but the schema.org legislation profile is not complete.",
                follow_on_track="Track 26",
            ),
            StandardCoverage(
                upstream_standard="schema.org/Legislation",
                coverage_status="missing",
                blocker_type="specification",
                blocker_data_source="Field-level legislation profile and canonical section-level metadata mapping.",
                missing_features=("Legislation type profile", "section and version metadata", "public page discoverability"),
                notes="The Legislation subtype is not fully modelled yet.",
                follow_on_track="Track 26",
            ),
            StandardCoverage(
                upstream_standard="EuroVoc",
                coverage_status="missing",
                blocker_type="source_data",
                blocker_data_source="EuroVoc SKOS thesaurus and a NZ policy-domain crosswalk.",
                missing_features=("EuroVoc concept scheme", "NZ policy-domain mapping", "multilingual descriptors"),
                notes="No controlled policy-domain thesaurus is wired into the repo yet.",
                follow_on_track="Track 28",
            ),
            StandardCoverage(
                upstream_standard="SKOS",
                coverage_status="missing",
                blocker_type="specification",
                blocker_data_source="Local controlled vocabulary model for policy domains and provision classification.",
                missing_features=("concept scheme definitions", "broader/narrower relations", "preferred labels"),
                notes="SKOS is the missing substrate for controlled vocabularies here.",
                follow_on_track="Track 28",
            ),
            StandardCoverage(
                upstream_standard="Popolo",
                coverage_status="missing",
                blocker_type="specification",
                blocker_data_source="Actor, office, mandate, and organization graph model for parliamentary data.",
                missing_features=("office/mandate vocabulary", "person-organization relations", "membership history"),
                notes="Helpful for political actor graphs, but not yet implemented.",
                follow_on_track="Track 26",
            ),
            StandardCoverage(
                upstream_standard="W3C ORG",
                coverage_status="missing",
                blocker_type="specification",
                blocker_data_source="Organization hierarchy and role model for parliamentary and policy institutions.",
                missing_features=("organization classes", "role and membership relations", "hierarchy mapping"),
                notes="Would strengthen the actor and institution layer.",
                follow_on_track="Track 26",
            ),
            StandardCoverage(
                upstream_standard="DCAT",
                coverage_status="missing",
                blocker_type="specification",
                blocker_data_source="Dataset catalogue model for corpus, artefact, and package publication.",
                missing_features=("dataset metadata", "distribution metadata", "catalog records"),
                notes="Needed for publication-quality dataset discovery.",
                follow_on_track="Track 34",
            ),
            StandardCoverage(
                upstream_standard="DCAT-AP",
                coverage_status="missing",
                blocker_type="specification",
                blocker_data_source="Profiled catalogue metadata aligned with DCAT-AP publication practices.",
                missing_features=("AP-aligned properties", "profile validation", "distribution cataloguing"),
                notes="Would support a more standards-based publication layer.",
                follow_on_track="Track 34",
            ),
        ),
    ),
    OntologySystem(
        system_key="legal_semantics",
        system_name="LKIF-inspired legal effects",
        description="Legal effect classification and deontic modality detection for normative clauses.",
        local_files=(
            "src/nlp_policy_nz/legal/effects.py",
            "src/nlp_policy_nz/legal/modality.py",
        ),
        standards=(
            StandardCoverage(
                upstream_standard="LKIF",
                coverage_status="partial",
                blocker_type="source_data",
                blocker_data_source="Normalized deontic and legal-effect annotation corpus.",
                missing_features=("full norm taxonomy", "exception and defeasibility inventory", "applicability conditions"),
                notes="The repo captures legal effects, but the ontology is still only inspired by LKIF.",
                follow_on_track="Track 27",
            ),
            StandardCoverage(
                upstream_standard="full LKIF",
                coverage_status="missing",
                blocker_type="specification",
                blocker_data_source="Formal semantics for obligations, permissions, prohibitions, powers, exceptions, and defeasibility.",
                missing_features=("full semantic model", "rule exception handling", "defeasible inference layer"),
                notes="This is the complete normative semantics layer that remains open.",
                follow_on_track="Track 27",
            ),
        ),
    ),
    OntologySystem(
        system_key="temporal_semantics",
        system_name="TimeML / OWL-Time temporal extraction",
        description="Temporal extraction hooks for commencement, expiry, amendments, and assessment periods.",
        local_files=("src/nlp_policy_nz/universal_framework_v3.py",),
        standards=(
            StandardCoverage(
                upstream_standard="TimeML",
                coverage_status="partial",
                blocker_type="source_data",
                blocker_data_source="Temporal annotation corpus for commencement, repeal, and assessment periods.",
                missing_features=("event-time links", "temporal relation inventory", "annotation examples"),
                notes="Temporal extraction exists, but the annotation coverage is still partial.",
                follow_on_track="Track 27",
            ),
            StandardCoverage(
                upstream_standard="OWL-Time",
                coverage_status="partial",
                blocker_type="source_data",
                blocker_data_source="Time interval and effective-date inventory for legal sources and parameters.",
                missing_features=("interval normalization", "valid-time model", "historical parameter series"),
                notes="Time semantics are present as hooks, not as a complete model.",
                follow_on_track="Track 27",
            ),
        ),
    ),
    OntologySystem(
        system_key="normative_emission",
        system_name="LegalRuleML / Catala hooks",
        description="Prototype emitters for formal rule semantics and executable legal transformations.",
        local_files=("src/nlp_policy_nz/universal_framework_v3.py",),
        standards=(
            StandardCoverage(
                upstream_standard="LegalRuleML",
                coverage_status="prototype",
                blocker_type="integration",
                blocker_data_source="Rule serialization and validation pipeline for full formal norm semantics.",
                missing_features=("full LegalRuleML serialisation", "schema validation", "exception representation"),
                notes="The repo has LegalRuleML hooks, but not a full standards implementation.",
                follow_on_track="Track 27",
            ),
            StandardCoverage(
                upstream_standard="full LegalRuleML",
                coverage_status="missing",
                blocker_type="specification",
                blocker_data_source="Complete rule semantics model with obligations, permissions, prohibitions, powers, and exceptions.",
                missing_features=("complete rule ontology", "formal applicability conditions", "defeasible rule encoding"),
                notes="Needs the full semantics layer rather than only hook points.",
                follow_on_track="Track 27",
            ),
            StandardCoverage(
                upstream_standard="Catala",
                coverage_status="prototype",
                blocker_type="integration",
                blocker_data_source="Executable rule translation examples and validated clause-to-rule mappings.",
                missing_features=("translation coverage", "canonical rule examples", "validated compile targets"),
                notes="The repo exposes Catala hooks, but the translation path is not yet complete.",
                follow_on_track="Track 27",
            ),
        ),
    ),
    OntologySystem(
        system_key="rules_as_code_bridge",
        system_name="OpenFisca / PolicyEngine adjacent rules-as-code surfaces",
        description="Rules-as-code bridge surfaces for entities, variables, formulas, parameters, and periods.",
        local_files=("src/nlp_policy_nz/universal_framework_v3.py",),
        standards=(
            StandardCoverage(
                upstream_standard="OpenFisca",
                coverage_status="adjacent",
                blocker_type="source_data",
                blocker_data_source="Variable, parameter, and entity inventory with time-varying parameter histories.",
                missing_features=("entity ontology", "variable inventory", "parameter history tables"),
                notes="The repo is adjacent to OpenFisca concepts, but does not yet expose a formal ontology bridge.",
                follow_on_track="Track 27",
            ),
            StandardCoverage(
                upstream_standard="PolicyEngine",
                coverage_status="adjacent",
                blocker_type="source_data",
                blocker_data_source="Policy variable and parameter inventory plus entity-period semantics.",
                missing_features=("formula inventory", "parameter ontology", "entity-period model"),
                notes="The repo is adjacent to PolicyEngine concepts, but not yet formalised.",
                follow_on_track="Track 27",
            ),
            StandardCoverage(
                upstream_standard="formal OpenFisca/PolicyEngine variable/parameter/entity ontology",
                coverage_status="missing",
                blocker_type="specification",
                blocker_data_source="Crosswalk of entities, variables, parameters, formulas, and assessment periods.",
                missing_features=("formal entity model", "variable ontology", "parameter ontology", "period semantics"),
                notes="This is the explicit ontology bridge required for rules-as-code tooling.",
                follow_on_track="Track 31",
            ),
        ),
    ),
)


def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def slugify_identifier(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "_", value.lower()).strip("_")
    return slug or "item"


def _existing_relative_paths(repo_root_path: Path, relative_paths: tuple[str, ...]) -> tuple[str, ...]:
    present = [path for path in relative_paths if (repo_root_path / path).exists()]
    return tuple(sorted(present))


def _system_rows(repo_root_path: Path) -> list[dict[str, Any]]:
    return [system.to_dict(repo_root_path) for system in SYSTEM_CATALOG]


def enumerate_ontology_facing_systems(repo_root_path: Path | str | None = None) -> list[dict[str, Any]]:
    root = Path(repo_root_path) if repo_root_path is not None else repo_root()
    return _system_rows(root)


def _flatten_coverage_rows(repo_root_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for system in SYSTEM_CATALOG:
        system_dict = system.to_dict(repo_root_path)
        for standard in system_dict["standards"]:
            rows.append(
                {
                    "system_key": system_dict["system_key"],
                    "system_name": system_dict["system_name"],
                    "description": system_dict["description"],
                    "upstream_standard": standard["upstream_standard"],
                    "coverage_status": standard["coverage_status"],
                    "local_files": system_dict["local_files"],
                    "present_local_files": system_dict["present_local_files"],
                    "missing_local_files": system_dict["missing_local_files"],
                    "local_file_status": system_dict["local_file_status"],
                    "blocker_type": standard["blocker_type"],
                    "blocker_data_source": standard["blocker_data_source"],
                    "missing_features": standard["missing_features"],
                    "priority": standard["priority"],
                    "notes": standard["notes"],
                    "follow_on_track": standard["follow_on_track"],
                    "blocker_id": f"{system_dict['system_key']}::{slugify_identifier(standard['upstream_standard'])}",
                }
            )
    rows.sort(
        key=lambda row: (
            row["system_key"],
            _STATUS_RANK[row["coverage_status"]],
            _PRIORITY_RANK[row["priority"]],
            row["upstream_standard"],
        )
    )
    return rows


def build_coverage_matrix(repo_root_path: Path | str | None = None) -> list[dict[str, Any]]:
    root = Path(repo_root_path) if repo_root_path is not None else repo_root()
    return _flatten_coverage_rows(root)


def build_blocker_register(repo_root_path: Path | str | None = None) -> list[dict[str, Any]]:
    rows = build_coverage_matrix(repo_root_path)
    blockers = [
        {
            "blocker_id": row["blocker_id"],
            "system_key": row["system_key"],
            "system_name": row["system_name"],
            "upstream_standard": row["upstream_standard"],
            "coverage_status": row["coverage_status"],
            "blocker_type": row["blocker_type"],
            "blocker_data_source": row["blocker_data_source"],
            "missing_features": row["missing_features"],
            "priority": row["priority"],
            "follow_on_track": row["follow_on_track"],
            "local_files": row["local_files"],
            "present_local_files": row["present_local_files"],
            "missing_local_files": row["missing_local_files"],
            "notes": row["notes"],
        }
        for row in rows
        if row["blocker_type"] != "none"
    ]
    blockers.sort(
        key=lambda row: (
            _PRIORITY_RANK[row["priority"]],
            _STATUS_RANK[row["coverage_status"]],
            row["system_key"],
            row["upstream_standard"],
        )
    )
    return blockers


def build_prioritized_backlog(repo_root_path: Path | str | None = None) -> list[dict[str, Any]]:
    rows = build_blocker_register(repo_root_path)
    backlog = [
        {
            "priority": row["priority"],
            "system_key": row["system_key"],
            "system_name": row["system_name"],
            "upstream_standard": row["upstream_standard"],
            "coverage_status": row["coverage_status"],
            "action": _backlog_action(row["upstream_standard"], row["coverage_status"]),
            "inputs_needed": list(row["missing_features"]) if row["missing_features"] else [row["blocker_data_source"]],
            "expected_output": _expected_output(row["upstream_standard"]),
            "blocker_type": row["blocker_type"],
            "blocker_data_source": row["blocker_data_source"],
            "follow_on_track": row["follow_on_track"],
            "local_files": row["local_files"],
            "present_local_files": row["present_local_files"],
            "missing_local_files": row["missing_local_files"],
            "notes": row["notes"],
        }
        for row in rows
    ]
    backlog.sort(
        key=lambda row: (
            _PRIORITY_RANK[row["priority"]],
            _STATUS_RANK[row["coverage_status"]],
            row["system_key"],
            row["upstream_standard"],
        )
    )
    return backlog


def _backlog_action(standard: str, status: str) -> str:
    if status == "implemented":
        return f"Maintain and validate {standard} coverage"
    if standard == "ELI":
        return "Add ELI URI templates and stable legislative identifiers"
    if standard == "ELI-DL":
        return "Add ELI-DL document metadata and publication descriptors"
    if standard == "ECLI":
        return "Add ECLI-compliant case law identifiers"
    if standard == "schema.org/Legislation":
        return "Complete schema.org/Legislation mapping"
    if standard == "EuroVoc":
        return "Add EuroVoc controlled vocabulary mappings"
    if standard == "SKOS":
        return "Model the local policy taxonomy in SKOS"
    if standard == "Popolo":
        return "Add Popolo actor, office, and mandate modelling"
    if standard == "W3C ORG":
        return "Add W3C ORG institution and role modelling"
    if standard == "DCAT":
        return "Publish datasets through DCAT metadata"
    if standard == "DCAT-AP":
        return "Add DCAT-AP catalogue profiles"
    if standard == "full LKIF":
        return "Implement the full LKIF normative semantics model"
    if standard == "full LegalRuleML":
        return "Implement the full LegalRuleML semantics layer"
    if standard == "formal OpenFisca/PolicyEngine variable/parameter/entity ontology":
        return "Define the formal OpenFisca/PolicyEngine ontology bridge"
    if standard == "OpenFisca":
        return "Formalise the OpenFisca-adjacent bridge"
    if standard == "PolicyEngine":
        return "Formalise the PolicyEngine-adjacent bridge"
    if standard == "TimeML":
        return "Expand temporal extraction into TimeML-aligned annotations"
    if standard == "OWL-Time":
        return "Model legal time intervals with OWL-Time"
    if standard == "LegalRuleML":
        return "Complete the LegalRuleML hook into a serialisable emitter"
    if standard == "Catala":
        return "Add executable Catala translation coverage"
    if standard == "Wikidata":
        return "Expand and verify the Wikidata entity crosswalk"
    if standard == "schema.org":
        return "Expand the schema.org knowledge graph export"
    if standard == "FRBR":
        return "Complete work-expression-version lineage metadata"
    if standard == "TLC":
        return "Complete temporal concept metadata"
    if standard == "LKIF":
        return "Expand deontic and legal-effect classification coverage"
    return f"Address {standard} coverage"


def _expected_output(standard: str) -> list[str]:
    if standard in {"ELI", "ELI-DL"}:
        return ["stable URI templates", "versioned legislative metadata"]
    if standard == "ECLI":
        return ["case law identifier registry", "citation-mapped judgments"]
    if standard in {"EuroVoc", "SKOS"}:
        return ["controlled vocabulary scheme", "domain concept crosswalk"]
    if standard in {"Popolo", "W3C ORG"}:
        return ["actor and institution graph", "membership and role relations"]
    if standard in {"DCAT", "DCAT-AP"}:
        return ["dataset catalogue records", "distribution metadata"]
    if standard in {"full LKIF", "LKIF"}:
        return ["norm semantics model", "exception and defeasibility rules"]
    if standard in {"full LegalRuleML", "LegalRuleML"}:
        return ["formal rule serialization", "validated norm semantics"]
    if standard in {"OpenFisca", "PolicyEngine", "formal OpenFisca/PolicyEngine variable/parameter/entity ontology"}:
        return ["entity-variable-parameter ontology", "period-aware rule model"]
    if standard in {"TimeML", "OWL-Time"}:
        return ["temporal annotations", "effective-date model"]
    if standard in {"Wikidata", "schema.org", "schema.org/Legislation"}:
        return ["linked-data export", "discoverable legal metadata"]
    return ["coverage update"]


def _coverage_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    blocker_counts: dict[str, int] = {}
    for row in rows:
        status_counts[row["coverage_status"]] = status_counts.get(row["coverage_status"], 0) + 1
        blocker_type = row["blocker_type"]
        if blocker_type != "none":
            blocker_counts[blocker_type] = blocker_counts.get(blocker_type, 0) + 1
    return {
        "row_count": len(rows),
        "status_counts": dict(sorted(status_counts.items(), key=lambda item: _STATUS_RANK[item[0]])),
        "blocker_type_counts": dict(sorted(blocker_counts.items())),
    }


def build_track25_ontology_coverage_audit(repo_root_path: Path | str | None = None) -> dict[str, Any]:
    root = Path(repo_root_path) if repo_root_path is not None else repo_root()
    systems = enumerate_ontology_facing_systems(root)
    coverage_matrix = build_coverage_matrix(root)
    blocker_register = build_blocker_register(root)
    prioritized_backlog = build_prioritized_backlog(root)
    return {
        "audit_name": "track25_ontology_coverage_audit",
        "repo_root": str(root),
        "systems": systems,
        "coverage_matrix": coverage_matrix,
        "blocker_register": blocker_register,
        "prioritized_backlog": prioritized_backlog,
        "summary": _coverage_summary(coverage_matrix),
    }


def dump_track25_ontology_coverage_audit(repo_root_path: Path | str | None = None) -> str:
    return json.dumps(build_track25_ontology_coverage_audit(repo_root_path), indent=2, sort_keys=True)


if __name__ == "__main__":
    print(dump_track25_ontology_coverage_audit())
