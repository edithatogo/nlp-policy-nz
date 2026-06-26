"""Track 25 ontology coverage audit helpers.

This module captures the repo's current ontology-facing implementation surface
and turns it into deterministic audit artifacts. The intent is not to claim
full coverage; it is to separate implemented surfaces from standards that are
still scaffolded or blocked on source data.
"""

from __future__ import annotations

from collections import OrderedDict
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any, Final, Iterable, Literal

CoverageStatus = Literal["implemented", "partial", "scaffolded", "missing"]
BlockerType = Literal["none", "data", "spec", "integration"]

STATUS_ORDER: Final[dict[str, int]] = {
    "implemented": 0,
    "partial": 1,
    "scaffolded": 2,
    "missing": 3,
}

OUTPUT_FILENAMES: Final[dict[str, str]] = {
    "matrix_json": "coverage_matrix.json",
    "matrix_md": "coverage_matrix.md",
    "blockers_json": "blocker_register.json",
    "backlog_json": "prioritized_backlog.json",
    "evidence_md": "evidence.md",
}


@dataclass(frozen=True)
class OntologySurface:
    """A single ontology family or standards surface in the repo."""

    standard: str
    repo_system: str
    local_files: tuple[str, ...]
    coverage_status: CoverageStatus
    implementation_summary: str
    gap_summary: str
    blocker_type: BlockerType
    blocker_source: str
    blocker_dataset: str
    next_action: str
    track_refs: tuple[str, ...]
    priority: int
    notes: str = ""

    def to_matrix_row(self, repo_root: Path) -> dict[str, Any]:
        """Render the surface as a JSON-ready audit row."""

        local_files = [
            {
                "path": local_file,
                "exists": (repo_root / local_file).exists(),
            }
            for local_file in self.local_files
        ]
        return {
            "standard": self.standard,
            "repo_system": self.repo_system,
            "local_files": list(self.local_files),
            "local_file_state": local_files,
            "coverage_status": self.coverage_status,
            "implementation_summary": self.implementation_summary,
            "gap_summary": self.gap_summary,
            "blocker_type": self.blocker_type,
            "blocker_source": self.blocker_source,
            "blocker_dataset": self.blocker_dataset,
            "next_action": self.next_action,
            "track_refs": list(self.track_refs),
            "priority": self.priority,
            "notes": self.notes,
        }


@dataclass(frozen=True)
class Track25OntologyCoverageAudit:
    """Container for the generated Track 25 audit artifacts."""

    matrix: tuple[dict[str, Any], ...]
    blockers: tuple[dict[str, Any], ...]
    backlog: tuple[dict[str, Any], ...]
    summary: dict[str, Any]


ONTOLOGY_SURFACES: Final[tuple[OntologySurface, ...]] = (
    OntologySurface(
        standard="Akoma Ntoso / LegalDocML",
        repo_system="AKN v3 emitter and validator",
        local_files=("src/nlp_policy_nz/schema/akn_v3.py",),
        coverage_status="partial",
        implementation_summary=(
            "AKN v3 emission and validation exist for core document types."
        ),
        gap_summary=(
            "Source anchoring is still incomplete because ELI/ELI-DL-style URI "
            "templates and a full legislative source inventory are missing."
        ),
        blocker_type="data",
        blocker_source="NZ legislation URI template and source inventory",
        blocker_dataset="official NZ legislation metadata export",
        next_action=(
            "Bind AKN sections and versions to stable NZ legislation identifiers "
            "and source metadata."
        ),
        track_refs=("track26", "track27", "track28"),
        priority=1,
        notes="Covers amendment, bill, debate, and judgment document types.",
    ),
    OntologySurface(
        standard="PROV-O",
        repo_system="Provenance serializer and recorder",
        local_files=(
            "src/nlp_policy_nz/provenance/serializer.py",
            "src/nlp_policy_nz/provenance/recorder.py",
        ),
        coverage_status="implemented",
        implementation_summary=(
            "PROV-O JSON-LD bundles, entities, activities, and agents are emitted."
        ),
        gap_summary="No blocking ontology gap found in the current repo surface.",
        blocker_type="none",
        blocker_source="",
        blocker_dataset="",
        next_action="Keep provenance bundled with downstream exports.",
        track_refs=("track25", "track35"),
        priority=0,
        notes="This is the cleanest standards-aligned surface in the repo.",
    ),
    OntologySurface(
        standard="FOAF / SIOC",
        repo_system="Parliamentary actor and speech graph exporters",
        local_files=(
            "src/nlp_policy_nz/linked_data/foaf.py",
            "src/nlp_policy_nz/linked_data/sioc.py",
            "src/nlp_policy_nz/linked_data/rdf.py",
        ),
        coverage_status="implemented",
        implementation_summary=(
            "FOAF actor profiles and SIOC speech graphs are already generated."
        ),
        gap_summary="No blocking ontology gap found in the current repo surface.",
        blocker_type="none",
        blocker_source="",
        blocker_dataset="",
        next_action="Keep RDF vocabularies aligned when new parliamentary fields land.",
        track_refs=("track25", "track29"),
        priority=0,
        notes="Useful for parliamentary identity and speech graphs.",
    ),
    OntologySurface(
        standard="Wikidata / schema.org",
        repo_system="NZ knowledge graph bridge and JSON-LD export",
        local_files=(
            "src/nlp_policy_nz/kb/wikidata_kg.py",
            "data/ontologies/nz_wikidata_map.ttl",
        ),
        coverage_status="partial",
        implementation_summary=(
            "There is a local ontology map plus schema.org JSON-LD and SPARQL bridge."
        ),
        gap_summary=(
            "Coverage is still partial because the schema.org Legislation model and "
            "stable identifier coverage are not complete."
        ),
        blocker_type="spec",
        blocker_source="Curated NZ entity authority and schema.org Legislation crosswalk",
        blocker_dataset="Wikidata QID and legislative entity map",
        next_action=(
            "Expand the NZ entity crosswalk and publish a fuller schema.org/Legislation model."
        ),
        track_refs=("track26", "track29", "track30"),
        priority=2,
        notes="The current map includes acts, MPs, parties, electorates, and courts.",
    ),
    OntologySurface(
        standard="LKIF-inspired legal effects",
        repo_system="Deontic effect and modality helpers",
        local_files=(
            "src/nlp_policy_nz/legal/effects.py",
            "src/nlp_policy_nz/legal/modality.py",
        ),
        coverage_status="partial",
        implementation_summary=(
            "The repo already models obligations, prohibitions, permissions, powers, "
            "liabilities, immunities, and disabilities."
        ),
        gap_summary=(
            "This is still LKIF-inspired rather than a full LKIF semantic model with "
            "defeasibility and richer applicability conditions."
        ),
        blocker_type="spec",
        blocker_source="LKIF alignment and normative rule inventory",
        blocker_dataset="normative rule catalogue and exception set",
        next_action=(
            "Align the effect taxonomy with a fuller LKIF/LegalRuleML semantics layer."
        ),
        track_refs=("track27", "track30", "track31"),
        priority=2,
        notes="Useful for rules-as-code semantics but not yet a full ontology bridge.",
    ),
    OntologySurface(
        standard="TimeML / OWL-Time",
        repo_system="Temporal extraction and pipeline timeline hooks",
        local_files=("src/nlp_policy_nz/universal_framework_v3.py",),
        coverage_status="partial",
        implementation_summary=(
            "The framework already carries temporal and pipeline-related XML/DSL hooks."
        ),
        gap_summary=(
            "Effective dates, commencement, expiry, assessment periods, and parameter "
            "histories are not fully normalised into a temporal ontology."
        ),
        blocker_type="data",
        blocker_source="Authority-date and amendment chronology corpus",
        blocker_dataset="commencement, expiry, and amendment timeline tables",
        next_action=(
            "Extract and normalise legal time spans for direct OWL-Time / TimeML mapping."
        ),
        track_refs=("track27", "track31"),
        priority=1,
        notes="This maps directly to time-varying policy parameters later on.",
    ),
    OntologySurface(
        standard="LegalRuleML / Catala",
        repo_system="Prototype rule emitters in the universal framework",
        local_files=("src/nlp_policy_nz/universal_framework_v3.py",),
        coverage_status="scaffolded",
        implementation_summary=(
            "There are prototype emit paths and embedded markers for LegalRuleML and Catala."
        ),
        gap_summary=(
            "The repo does not yet emit a full LegalRuleML semantics layer or a "
            "production Catala translation."
        ),
        blocker_type="integration",
        blocker_source="Rule semantics extraction and emitter integration",
        blocker_dataset="normative rule translation set",
        next_action=(
            "Convert the prototype hooks into real LegalRuleML and Catala emitters."
        ),
        track_refs=("track26", "track27", "track30"),
        priority=2,
        notes="Currently a scaffold rather than a validated downstream target.",
    ),
    OntologySurface(
        standard="OpenFisca / PolicyEngine ontology",
        repo_system="Rules-as-code model bridge",
        local_files=("src/nlp_policy_nz/universal_framework_v3.py",),
        coverage_status="scaffolded",
        implementation_summary=(
            "There is a bridge concept, but not a formal variables/parameters/entities ontology."
        ),
        gap_summary=(
            "The repo does not yet expose a native OpenFisca/PolicyEngine model with "
            "variable, parameter, entity, and period semantics."
        ),
        blocker_type="data",
        blocker_source="NZ policy variable and parameter catalogue",
        blocker_dataset="policy variable, parameter, and entity definitions",
        next_action=(
            "Model the legislation-to-variable bridge as a first-class ontology."
        ),
        track_refs=("track26", "track27", "track31"),
        priority=1,
        notes="This is the main rules-as-code target for later tracks.",
    ),
    OntologySurface(
        standard="Parliamentary voting / amendment analytics",
        repo_system="Track 22 evidence and MLEB fixture slice",
        local_files=("src/nlp_policy_nz/training/track22_evidence.py",),
        coverage_status="partial",
        implementation_summary=(
            "The repo has an evidence helper for a local NZ-MLEB fixture slice."
        ),
        gap_summary=(
            "A broader parliamentary vote and amendment corpus is still needed to "
            "support more complete ontology mapping."
        ),
        blocker_type="data",
        blocker_source="NZ MLEB / Isaacus fixture slice",
        blocker_dataset="local NZ-MLEB parliamentary fixture corpus",
        next_action=(
            "Expand the fixture slice so amendment, vote, and provenance links can be audited."
        ),
        track_refs=("track22", "track25", "track35"),
        priority=2,
        notes="Useful as a source-grounded input to future legislative mappings.",
    ),
    OntologySurface(
        standard="ELI / ELI-DL",
        repo_system="Missing source anchoring layer",
        local_files=(),
        coverage_status="missing",
        implementation_summary="No dedicated ELI/ELI-DL implementation surface is present yet.",
        gap_summary=(
            "Stable legislative URIs, FRBR work/expression/version metadata, and "
            "section-level source anchoring are missing."
        ),
        blocker_type="data",
        blocker_source="NZ legislation metadata dump and URI template inventory",
        blocker_dataset="official NZ legislation metadata export",
        next_action="Add ELI URI templates and FRBR-aware source anchors.",
        track_refs=("track26", "track27", "track28"),
        priority=1,
    ),
    OntologySurface(
        standard="ECLI",
        repo_system="Missing case-law identifier layer",
        local_files=(),
        coverage_status="missing",
        implementation_summary="No ECLI identifier layer is implemented yet.",
        gap_summary="Court decision identifiers are not normalised in an ECLI-compatible form.",
        blocker_type="data",
        blocker_source="NZ case law identifier corpus",
        blocker_dataset="judgment corpus with stable case identifiers",
        next_action="Normalise judgments into a case-law identifier scheme.",
        track_refs=("track26", "track28"),
        priority=2,
    ),
    OntologySurface(
        standard="EuroVoc / SKOS",
        repo_system="Policy-domain taxonomy layer",
        local_files=(),
        coverage_status="missing",
        implementation_summary="No controlled vocabulary mapping is implemented yet.",
        gap_summary=(
            "There is no SKOS-backed policy-domain taxonomy for classifying provisions."
        ),
        blocker_type="spec",
        blocker_source="Policy-domain taxonomy mapping set",
        blocker_dataset="provision-to-domain mapping corpus",
        next_action="Attach policy-domain labels to provisions and sections.",
        track_refs=("track26", "track27", "track31"),
        priority=1,
    ),
    OntologySurface(
        standard="CEN MetaLex",
        repo_system="Missing legislative XML crosswalk",
        local_files=(),
        coverage_status="missing",
        implementation_summary="No MetaLex emitter or importer is present yet.",
        gap_summary="A CEN MetaLex schema crosswalk has not been built.",
        blocker_type="integration",
        blocker_source="Legislative XML corpus and schema mapping",
        blocker_dataset="machine-readable legislation corpus",
        next_action="Map legislative XML into a MetaLex-aligned representation.",
        track_refs=("track26", "track28", "track29"),
        priority=2,
    ),
    OntologySurface(
        standard="USLM",
        repo_system="Missing comparative legislative XML bridge",
        local_files=(),
        coverage_status="missing",
        implementation_summary="No USLM mapper or comparator is present yet.",
        gap_summary="The repo has no cross-jurisdiction USLM model or crosswalk.",
        blocker_type="spec",
        blocker_source="USLM mapping corpus",
        blocker_dataset="US legislative XML benchmark set",
        next_action="Build a USLM comparison layer for legislative structure.",
        track_refs=("track26", "track29", "track30"),
        priority=3,
    ),
    OntologySurface(
        standard="LexML",
        repo_system="Missing legislative identifier and structure bridge",
        local_files=(),
        coverage_status="missing",
        implementation_summary="No LexML URI or structure layer is present yet.",
        gap_summary="LexML-style stable references and metadata are not modelled.",
        blocker_type="data",
        blocker_source="LexML URI template and legislation corpus",
        blocker_dataset="LexML crosswalk and legislation reference set",
        next_action="Add LexML-style identifiers and structural crosswalks.",
        track_refs=("track26", "track28", "track29"),
        priority=2,
    ),
    OntologySurface(
        standard="Popolo",
        repo_system="Missing parliamentary actor graph",
        local_files=(),
        coverage_status="missing",
        implementation_summary="No Popolo-compatible people/offices graph is present yet.",
        gap_summary="The repo does not yet expose a parliamentary role and office ontology.",
        blocker_type="data",
        blocker_source="Parliamentary actor and office roster",
        blocker_dataset="people, offices, roles, and memberships",
        next_action="Publish the parliamentary actor graph in Popolo-compatible form.",
        track_refs=("track26", "track29"),
        priority=3,
    ),
    OntologySurface(
        standard="W3C ORG",
        repo_system="Missing organization hierarchy graph",
        local_files=(),
        coverage_status="missing",
        implementation_summary="No W3C ORG hierarchy is currently modelled.",
        gap_summary="Government, parliamentary, and committee organization structures are absent.",
        blocker_type="data",
        blocker_source="Official organization chart export",
        blocker_dataset="institutional hierarchy and role roster",
        next_action="Map parliamentary and government bodies into W3C ORG.",
        track_refs=("track26", "track29"),
        priority=3,
    ),
    OntologySurface(
        standard="DCAT / DCAT-AP",
        repo_system="Missing dataset catalog layer",
        local_files=(),
        coverage_status="missing",
        implementation_summary="No dataset catalog metadata model is present yet.",
        gap_summary="Dataset-level discovery and catalog metadata are not published as DCAT.",
        blocker_type="data",
        blocker_source="Dataset catalog and provenance inventory",
        blocker_dataset="catalog of repo datasets and derived resources",
        next_action="Publish the repo datasets and derived artifacts as DCAT records.",
        track_refs=("track26", "track34", "track35"),
        priority=2,
    ),
)


def repo_root(anchor: Path | None = None) -> Path:
    """Return the repository root for local-file existence checks."""

    path = (anchor or Path(__file__)).resolve()
    for candidate in path.parents:
        if (candidate / "conductor").exists() and (candidate / "src").exists():
            return candidate
    return path.parent


def build_coverage_matrix(root: Path | None = None) -> list[dict[str, Any]]:
    """Build the deterministic coverage matrix."""

    repo_root_path = root or repo_root()
    rows = [surface.to_matrix_row(repo_root_path) for surface in ONTOLOGY_SURFACES]
    return sorted(
        rows,
        key=lambda row: (
            row["priority"],
            STATUS_ORDER[row["coverage_status"]],
            row["standard"].lower(),
        ),
    )


def build_blocker_register(
    matrix: Iterable[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Group the matrix into distinct blocker records."""

    rows = list(matrix or build_coverage_matrix())
    grouped: dict[tuple[str, str, str, str], dict[str, Any]] = {}

    for row in rows:
        blocker_type = row["blocker_type"]
        if blocker_type == "none":
            continue
        key = (
            blocker_type,
            row["blocker_source"],
            row["blocker_dataset"],
            row["next_action"],
        )
        bucket = grouped.get(key)
        if bucket is None:
            bucket = {
                "blocker_type": blocker_type,
                "blocker_source": row["blocker_source"],
                "blocker_dataset": row["blocker_dataset"],
                "affected_standards": [],
                "track_refs": [],
                "next_action": row["next_action"],
                "priority": row["priority"],
                "gap_summary": row["gap_summary"],
            }
            grouped[key] = bucket
        bucket["affected_standards"].append(row["standard"])
        bucket["track_refs"].extend(row["track_refs"])
        bucket["priority"] = min(bucket["priority"], row["priority"])

    register: list[dict[str, Any]] = []
    for bucket in grouped.values():
        register.append(
            {
                **bucket,
                "affected_standards": sorted(set(bucket["affected_standards"])),
                "track_refs": sorted(set(bucket["track_refs"])),
            }
        )

    return sorted(
        register,
        key=lambda row: (
            row["priority"],
            row["blocker_type"],
            row["blocker_source"].lower(),
        ),
    )


def build_prioritized_backlog(
    matrix: Iterable[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Convert the audit into a work backlog."""

    rows = [
        row
        for row in (matrix or build_coverage_matrix())
        if row["blocker_type"] != "none"
    ]
    rows = sorted(
        rows,
        key=lambda row: (
            row["priority"],
            STATUS_ORDER[row["coverage_status"]],
            row["standard"].lower(),
        ),
    )
    backlog: list[dict[str, Any]] = []
    for index, row in enumerate(rows, start=1):
        backlog.append(
            {
                "rank": index,
                "standard": row["standard"],
                "repo_system": row["repo_system"],
                "next_action": row["next_action"],
                "blocker_type": row["blocker_type"],
                "blocker_source": row["blocker_source"],
                "blocker_dataset": row["blocker_dataset"],
                "track_refs": list(row["track_refs"]),
                "priority": row["priority"],
                "gap_summary": row["gap_summary"],
                "coverage_status": row["coverage_status"],
                "notes": row["notes"],
            }
        )
    return backlog


def build_audit_summary(matrix: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Summarize the matrix at a glance."""

    rows = list(matrix)
    status_counts = {status: 0 for status in STATUS_ORDER}
    blocker_counts = {"none": 0, "data": 0, "spec": 0, "integration": 0}
    for row in rows:
        status_counts[row["coverage_status"]] += 1
        blocker_counts[row["blocker_type"]] += 1

    return {
        "total_surfaces": len(rows),
        "status_counts": status_counts,
        "blocker_counts": blocker_counts,
        "implemented_surfaces": [
            row["standard"] for row in rows if row["coverage_status"] == "implemented"
        ],
        "partial_surfaces": [
            row["standard"] for row in rows if row["coverage_status"] == "partial"
        ],
        "scaffolded_surfaces": [
            row["standard"] for row in rows if row["coverage_status"] == "scaffolded"
        ],
        "missing_surfaces": [
            row["standard"] for row in rows if row["coverage_status"] == "missing"
        ],
    }


def build_audit_bundle(root: Path | None = None) -> Track25OntologyCoverageAudit:
    """Build the full audit bundle as plain Python structures."""

    matrix = build_coverage_matrix(root=root)
    blockers = build_blocker_register(matrix)
    backlog = build_prioritized_backlog(matrix)
    summary = build_audit_summary(matrix)
    return Track25OntologyCoverageAudit(
        matrix=tuple(matrix),
        blockers=tuple(blockers),
        backlog=tuple(backlog),
        summary=summary,
    )


def matrix_to_markdown(matrix: Iterable[dict[str, Any]]) -> str:
    """Render the matrix as a compact markdown table."""

    rows = list(matrix)
    header = "| Standard | Status | Files | Blocker | Next action |"
    separator = "| --- | --- | --- | --- | --- |"
    lines = [header, separator]
    for row in rows:
        files = "<br>".join(row["local_files"]) if row["local_files"] else "none"
        blocker = (
            f'{row["blocker_type"]}: {row["blocker_source"]}'
            if row["blocker_type"] != "none"
            else "none"
        )
        next_action = row["next_action"]
        lines.append(
            "| {standard} | {status} | {files} | {blocker} | {action} |".format(
                standard=row["standard"],
                status=row["coverage_status"],
                files=files,
                blocker=blocker,
                action=next_action,
            )
        )
    return "\n".join(lines)


def build_evidence_markdown(bundle: Track25OntologyCoverageAudit) -> str:
    """Build the human-readable evidence summary."""

    summary = bundle.summary
    implemented = ", ".join(summary["implemented_surfaces"]) or "none"
    partial = ", ".join(summary["partial_surfaces"]) or "none"
    scaffolded = ", ".join(summary["scaffolded_surfaces"]) or "none"
    missing = ", ".join(summary["missing_surfaces"]) or "none"

    lines = [
        "# Track 25 Ontology Coverage Audit",
        "",
        "This audit separates implemented repo surfaces from standards that are",
        "still partial, scaffolded, or missing.",
        "",
        "## Summary",
        f"- Total ontology surfaces: {summary['total_surfaces']}",
        f"- Implemented: {summary['status_counts']['implemented']}",
        f"- Partial: {summary['status_counts']['partial']}",
        f"- Scaffolded: {summary['status_counts']['scaffolded']}",
        f"- Missing: {summary['status_counts']['missing']}",
        "",
        "## Implemented surfaces",
        implemented,
        "",
        "## Partial surfaces",
        partial,
        "",
        "## Scaffolded surfaces",
        scaffolded,
        "",
        "## Missing surfaces",
        missing,
        "",
        "## Blockers",
    ]
    for blocker in bundle.blockers:
        standards = ", ".join(blocker["affected_standards"])
        lines.append(
            f"- {blocker['blocker_type']}: {standards} -> {blocker['next_action']}"
        )
    lines.extend(
        [
            "",
            "## Priority backlog",
        ]
    )
    for item in bundle.backlog:
        lines.append(
            f"{item['rank']}. {item['standard']} - {item['next_action']}"
        )
    lines.extend(["", "## Matrix", "", matrix_to_markdown(bundle.matrix)])
    return "\n".join(lines)


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_track25_artifacts(output_dir: Path, root: Path | None = None) -> dict[str, Path]:
    """Write the standard Track 25 artifact set to disk."""

    bundle = build_audit_bundle(root=root)
    output_dir.mkdir(parents=True, exist_ok=True)
    outputs = {
        OUTPUT_FILENAMES["matrix_json"]: bundle.matrix,
        OUTPUT_FILENAMES["matrix_md"]: matrix_to_markdown(bundle.matrix),
        OUTPUT_FILENAMES["blockers_json"]: bundle.blockers,
        OUTPUT_FILENAMES["backlog_json"]: bundle.backlog,
        OUTPUT_FILENAMES["evidence_md"]: build_evidence_markdown(bundle),
    }
    written: dict[str, Path] = {}
    for filename, payload in outputs.items():
        path = output_dir / filename
        if filename.endswith(".json"):
            _write_json(path, payload)
        else:
            path.write_text(str(payload), encoding="utf-8")
        written[filename] = path
    return written


__all__ = [
    "BlockerType",
    "CoverageStatus",
    "ONTOLOGY_SURFACES",
    "OntologySurface",
    "OUTPUT_FILENAMES",
    "Track25OntologyCoverageAudit",
    "build_audit_bundle",
    "build_audit_summary",
    "build_blocker_register",
    "build_coverage_matrix",
    "build_evidence_markdown",
    "build_prioritized_backlog",
    "matrix_to_markdown",
    "repo_root",
    "write_track25_artifacts",
]
