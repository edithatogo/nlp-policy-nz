"""Deterministic standards-based publication protocol for Track 34."""

from __future__ import annotations

import json
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Final

PUBLICATION_PROTOCOL_MANIFEST_FILENAME: Final[str] = "publication_protocol_manifest.json"
PUBLICATION_PROTOCOL_CLAIMS_FILENAME: Final[str] = "publication_protocol_claims.json"
PUBLICATION_PROTOCOL_INVENTORY_FILENAME: Final[str] = "publication_protocol_inventory.json"
PUBLICATION_PROTOCOL_OVERCLAIM_FILENAME: Final[str] = "publication_protocol_overclaim_review.json"
PUBLICATION_PROTOCOL_MARKDOWN_FILENAME: Final[str] = "publication_protocol.md"

TRACK_ID: Final[str] = "track34_publication_protocol_20260625"
DEFAULT_OUTPUT_DIR: Final[Path] = Path("data") / "publication"
DEFAULT_MARKDOWN_PATH: Final[Path] = Path("docs") / PUBLICATION_PROTOCOL_MARKDOWN_FILENAME


@dataclass(frozen=True, slots=True)
class PublicationProtocolBundle:
    """Track 34 protocol bundle ready for artifact export."""

    manifest: dict[str, Any]
    claims: tuple[dict[str, Any], ...]
    artifact_inventory: tuple[dict[str, Any], ...]
    reproducibility_commands: tuple[dict[str, str], ...]
    overclaim_review: tuple[dict[str, Any], ...]
    markdown: str


def build_publication_protocol(
    *,
    repo_root_path: Path | str | None = None,
) -> PublicationProtocolBundle:
    """Build the Track 34 publication protocol from checked-in repo evidence."""
    root = Path(repo_root_path) if repo_root_path is not None else _repo_root()
    claims = _claim_rows(root)
    inventory = _artifact_inventory(root)
    commands = _reproducibility_commands()
    overclaim = _overclaim_review(root)
    counts = Counter(claim["claim_status"] for claim in claims)
    manifest = {
        "schema_version": "1.0",
        "track_id": TRACK_ID,
        "producer": "nlp-policy-nz",
        "source_boundary": (
            "This protocol maps publication claims to checked-in repo evidence, "
            "external gates, planned work, or blockers. It does not claim full-corpus, "
            "live publication, authenticated API, or external-source completion unless "
            "those artifacts are explicitly present."
        ),
        "claim_counts": {
            "total": len(claims),
            "repo_evidence": counts["repo_evidence"],
            "external_gate": counts["external_gate"],
            "planned": counts["planned"],
            "blocker": counts["blocker"],
        },
        "artifact_counts": {
            "total": len(inventory),
            "present": sum(1 for item in inventory if item["exists"]),
            "missing": sum(1 for item in inventory if not item["exists"]),
        },
        "artifact_files": {
            "claims": PUBLICATION_PROTOCOL_CLAIMS_FILENAME,
            "inventory": PUBLICATION_PROTOCOL_INVENTORY_FILENAME,
            "overclaim_review": PUBLICATION_PROTOCOL_OVERCLAIM_FILENAME,
            "markdown": PUBLICATION_PROTOCOL_MARKDOWN_FILENAME,
        },
    }
    markdown = _markdown_protocol(manifest, claims, inventory, commands, overclaim)
    return PublicationProtocolBundle(
        manifest=manifest,
        claims=claims,
        artifact_inventory=inventory,
        reproducibility_commands=commands,
        overclaim_review=overclaim,
        markdown=markdown,
    )


def write_publication_protocol_artifacts(
    output_dir: Path | str | None = None,
    *,
    repo_root_path: Path | str | None = None,
    markdown_path: Path | str | None = None,
) -> dict[str, Path]:
    """Write Track 34 publication protocol artifacts and return output paths."""
    root = Path(repo_root_path) if repo_root_path is not None else _repo_root()
    target_dir = Path(output_dir) if output_dir is not None else root / DEFAULT_OUTPUT_DIR
    target_dir.mkdir(parents=True, exist_ok=True)
    if markdown_path is not None:
        target_markdown = Path(markdown_path)
    elif output_dir is None:
        target_markdown = root / DEFAULT_MARKDOWN_PATH
    else:
        target_markdown = target_dir / PUBLICATION_PROTOCOL_MARKDOWN_FILENAME
    target_markdown.parent.mkdir(parents=True, exist_ok=True)
    bundle = build_publication_protocol(repo_root_path=root)
    paths = {
        PUBLICATION_PROTOCOL_MANIFEST_FILENAME: target_dir
        / PUBLICATION_PROTOCOL_MANIFEST_FILENAME,
        PUBLICATION_PROTOCOL_CLAIMS_FILENAME: target_dir / PUBLICATION_PROTOCOL_CLAIMS_FILENAME,
        PUBLICATION_PROTOCOL_INVENTORY_FILENAME: target_dir
        / PUBLICATION_PROTOCOL_INVENTORY_FILENAME,
        PUBLICATION_PROTOCOL_OVERCLAIM_FILENAME: target_dir
        / PUBLICATION_PROTOCOL_OVERCLAIM_FILENAME,
        PUBLICATION_PROTOCOL_MARKDOWN_FILENAME: target_markdown,
    }
    _write_json(paths[PUBLICATION_PROTOCOL_MANIFEST_FILENAME], bundle.manifest)
    _write_json(paths[PUBLICATION_PROTOCOL_CLAIMS_FILENAME], {"claims": list(bundle.claims)})
    _write_json(
        paths[PUBLICATION_PROTOCOL_INVENTORY_FILENAME],
        {
            "artifacts": list(bundle.artifact_inventory),
            "reproducibility_commands": list(bundle.reproducibility_commands),
        },
    )
    _write_json(paths[PUBLICATION_PROTOCOL_OVERCLAIM_FILENAME], list(bundle.overclaim_review))
    paths[PUBLICATION_PROTOCOL_MARKDOWN_FILENAME].write_text(bundle.markdown, encoding="utf-8")
    return paths


def _claim_rows(root: Path) -> tuple[dict[str, Any], ...]:
    rows = (
        _claim("protocol-repo-boundary", "The protocol is repo-side and evidence-mapped; it does not claim full-corpus or live external completion.", "limitations", "repo_evidence", ("conductor/tracks/track34_publication_protocol_20260625/spec.md",), root),
        _claim("pipeline-architecture", "The repository defines a unified NLP pipeline for legislation and Hansard preprocessing.", "methods", "repo_evidence", ("README.md", "conductor/product.md", "src/nlp_policy_nz/cli/main.py"), root),
        _claim("standards-registry", "Standards coverage is inventoried through checked-in ontology and standards manifests.", "standards", "repo_evidence", ("data/ontologies/track26_standards_registry.json", "data/ontologies/coverage_manifest.json", "data/ontologies/data_blocker_register.json"), root),
        _claim("ontology-strategy", "The protocol references deterministic NZ ontology candidates and controlled vocabularies.", "ontology", "repo_evidence", ("data/ontologies/nz_ontology_candidates.json", "data/ontologies/nz_controlled_vocabularies.json", "docs/nz_ontologies.md"), root),
        _claim("mapping-graph", "Ontology mapping and inference artifacts are available as deterministic repo evidence.", "ontology", "repo_evidence", ("data/ontologies/ontology_mappings.json", "data/ontologies/inferred_mapping_candidates.json", "docs/ontology_mapping.md"), root),
        _claim("corpus-statistics", "Corpus statistics are reproducible from PipelineRecord inputs or deterministic fixtures.", "analysis", "repo_evidence", ("data/statistics/corpus_statistics_manifest.json", "data/statistics/corpus_statistics_per_corpus.csv", "docs/corpus_statistics.md"), root),
        _claim("graph-vector-analysis", "Graph/vector/network analysis is reproducible from checked-in ontology/statistics inputs and deterministic vectors.", "analysis", "repo_evidence", ("data/analysis/graph_vector_manifest.json", "data/analysis/graph_vector_graph_metrics.json", "docs/graph_vector_network_analysis.md"), root),
        _claim("rules-as-code-bridge", "The repository contains an offline rules-as-code bridge and Axiom relevance documentation.", "methods", "repo_evidence", ("docs/axiom-foundation-relevance.md", "src/nlp_policy_nz/axiom/rulespec.py", "src/nlp_policy_nz/cli/main.py"), root),
        _claim("quality-gates", "Track 34 is validated by focused tests, CLI smoke coverage, and Ruff linting.", "quality", "repo_evidence", ("tests/test_track34_publication_protocol.py", "tests/test_track34_conductor.py"), root),
        _claim("full-corpus-statistics", "Canonical whole-corpus counts and longitudinal completeness remain blocked until full PipelineRecord Parquet inputs are supplied.", "limitations", "blocker", ("data/statistics/corpus_statistics_blockers.json",), root),
        _claim("full-graph-vector", "Full citation, co-vote, co-speech, Wikidata, and vector-index analyses remain blocked until canonical exports are supplied.", "limitations", "blocker", ("data/analysis/graph_vector_blockers.json",), root),
        _claim("publication-metadata-standards", "Dataset catalogue publication standards such as DCAT, DCAT-AP, NZGLS, and data.govt.nz remain partial or planned.", "standards", "blocker", ("data/ontologies/data_blocker_register.json", "data/ontologies/coverage_manifest.json"), root),
        _claim("live-zenodo-hf-publication", "Live Zenodo, Hugging Face Hub, or authenticated external publication evidence requires credentials and external service runs.", "publication", "external_gate", ("README.md", ".github/workflows/release.yml", "src/nlp_policy_nz/integrations/release.py"), root),
        _claim("figure-production", "Final publication figures and executable analysis notebooks are assigned to Track 35.", "planned", "planned", ("conductor/tracks/track35_analysis_artifact_execution_20260625/spec.md",), root),
    )
    return tuple(sorted(rows, key=lambda row: row["claim_id"]))


def _artifact_inventory(root: Path) -> tuple[dict[str, Any], ...]:
    artifacts = (
        ("README.md", "overview", "Human-readable repo overview and CLI entrypoints."),
        ("docs/ontology_mapping.md", "documentation", "Ontology mapping method summary."),
        ("docs/nz_ontologies.md", "documentation", "NZ ontology candidate summary."),
        ("docs/corpus_statistics.md", "documentation", "Corpus statistics protocol summary."),
        ("docs/graph_vector_network_analysis.md", "documentation", "Graph/vector analysis summary."),
        ("data/ontologies/coverage_manifest.json", "standards", "Ontology coverage matrix."),
        ("data/ontologies/data_blocker_register.json", "standards", "Standards blocker register."),
        ("data/ontologies/track26_standards_registry.json", "standards", "Standards registry."),
        ("data/ontologies/nz_ontology_candidates.json", "ontology", "NZ ontology candidates."),
        ("data/statistics/corpus_statistics_manifest.json", "analysis", "Corpus statistics manifest."),
        ("data/statistics/corpus_statistics_blockers.json", "analysis", "Corpus blockers."),
        ("data/analysis/graph_vector_manifest.json", "analysis", "Graph/vector manifest."),
        ("data/analysis/graph_vector_blockers.json", "analysis", "Graph/vector blockers."),
        ("tests/test_track34_publication_protocol.py", "quality", "Track 34 protocol tests."),
    )
    return tuple(
        {
            "path": path,
            "artifact_type": artifact_type,
            "description": description,
            "exists": (root / path).is_file(),
        }
        for path, artifact_type, description in artifacts
    )


def _reproducibility_commands() -> tuple[dict[str, str], ...]:
    return (
        {"command": "nlp-policy-nz export-nz-ontologies --output-dir data/ontologies", "purpose": "Regenerate deterministic Track 31 ontology artifacts."},
        {"command": "nlp-policy-nz corpus-stats --output-dir data/statistics", "purpose": "Regenerate deterministic Track 32 fixture-bounded statistics."},
        {"command": "nlp-policy-nz graph-vector-analysis --output-dir data/analysis", "purpose": "Regenerate deterministic Track 33 graph/vector artifacts."},
        {"command": "nlp-policy-nz publication-protocol --output-dir data/publication", "purpose": "Regenerate Track 34 publication protocol JSON and Markdown."},
        {"command": "pixi run python -m pytest -q tests\\test_track34_publication_protocol.py tests\\test_track34_conductor.py tests\\test_cli.py", "purpose": "Validate Track 34 protocol, conductor, and CLI coverage."},
    )


def _overclaim_review(root: Path) -> tuple[dict[str, Any], ...]:
    risks = (
        ("full-corpus-overclaim", "high", "The repository contains complete NZ legislation and Hansard corpus statistics.", "The repository contains deterministic fixture-bounded statistics and can process supplied PipelineRecord Parquet inputs; full-corpus counts remain gated.", ("data/statistics/corpus_statistics_blockers.json",)),
        ("live-publication-overclaim", "high", "The corpus has been published to Zenodo or Hugging Face.", "The repository includes release tooling; live publication requires credentials and an executed external publication run.", ("README.md", ".github/workflows/release.yml")),
        ("standards-compliance-overclaim", "medium", "All ontology and publication standards are fully implemented.", "The protocol lists implemented, partial, planned, and blocked standards coverage with evidence paths.", ("data/ontologies/coverage_manifest.json",)),
        ("graph-vector-overclaim", "medium", "Graph and vector metrics cover the full production corpus.", "Checked-in graph/vector metrics are deterministic and fixture-bounded; full graph/vector publication requires canonical exports.", ("data/analysis/graph_vector_blockers.json",)),
    )
    return tuple(
        {
            "risk_id": risk_id,
            "risk_level": level,
            "unsafe_claim": unsafe,
            "safe_wording": safe,
            "evidence_paths": list(paths),
            "evidence_state": [{"path": path, "exists": (root / path).is_file()} for path in paths],
        }
        for risk_id, level, unsafe, safe, paths in risks
    )


def _claim(
    claim_id: str,
    text: str,
    section: str,
    status: str,
    evidence_paths: tuple[str, ...],
    root: Path,
) -> dict[str, Any]:
    return {
        "claim_id": claim_id,
        "claim": text,
        "protocol_section": section,
        "claim_status": status,
        "evidence_paths": list(evidence_paths),
        "evidence_state": [
            {"path": path, "exists": (root / path).exists()} for path in evidence_paths
        ],
    }


def _markdown_protocol(
    manifest: dict[str, Any],
    claims: tuple[dict[str, Any], ...],
    artifact_inventory: tuple[dict[str, Any], ...],
    reproducibility_commands: tuple[dict[str, str], ...],
    overclaim_review: tuple[dict[str, Any], ...],
) -> str:
    lines = [
        "# Standards-Based Publication Protocol",
        "",
        "Track 34 defines a publication-ready protocol for the current repo-side evidence. It does not claim full-corpus, live publication, authenticated API, or external-source completion unless the cited evidence exists.",
        "",
        "## Scope and evidence boundary",
        "",
        manifest["source_boundary"],
        "",
        "## Repository overview and methods",
        "",
        "- Pipeline architecture is grounded in `README.md`, `conductor/product.md`, and the CLI entrypoints in `src/nlp_policy_nz/cli/main.py`.",
        "- Ontology and standards claims are grounded in checked-in manifests under `data/ontologies/`.",
        "- Analysis claims are grounded in deterministic Track 32 and Track 33 artifacts under `data/statistics/` and `data/analysis/`.",
        "",
        "## Standards compliance matrix",
        "",
        "| Claim | Status | Evidence |",
        "| --- | --- | --- |",
    ]
    for claim in claims:
        evidence = ", ".join(f"`{path}`" for path in claim["evidence_paths"])
        lines.append(f"| {claim['claim_id']} | {claim['claim_status']} | {evidence} |")
    lines.extend(["", "## Ontology mapping and reasoning", "", "The protocol references Track 29-31 ontology mapping, inference, and NZ ontology candidates as repo evidence. These artifacts are deterministic and review-bounded; authoritative external crosswalks remain explicit gates.", "", "## Corpus statistics and analysis methodology", "", "Track 32 corpus statistics and Track 33 graph/vector analysis are fixture-bounded by default. They can be regenerated locally and extended with supplied full-corpus PipelineRecord, graph, or vector exports.", "", "## Artifact inventory", "", "| Artifact | Type | Present |", "| --- | --- | --- |"])
    for item in artifact_inventory:
        lines.append(f"| `{item['path']}` | {item['artifact_type']} | {item['exists']} |")
    lines.extend(["", "## Reproducibility instructions", ""])
    for index, command in enumerate(reproducibility_commands, start=1):
        lines.append(f"{index}. `{command['command']}`")
        lines.append(f"   - {command['purpose']}")
    lines.extend(["", "## Overclaim review", "", "| Risk | Level | Safe wording |", "| --- | --- | --- |"])
    for risk in overclaim_review:
        lines.append(f"| {risk['risk_id']} | {risk['risk_level']} | {risk['safe_wording']} |")
    lines.extend(["", "## Limitations", "", "- The protocol does not claim full-corpus coverage without supplied full corpus inputs.", "- The protocol does not claim live publication without external service execution evidence.", "- The protocol does not claim fully implemented DCAT, DCAT-AP, NZGLS, ELI, ELI-DL, ECLI, or LegalRuleML coverage where blocker manifests record partial or missing coverage."])
    return "\n".join(lines) + "\n"


def _write_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


__all__ = [
    "PUBLICATION_PROTOCOL_CLAIMS_FILENAME",
    "PUBLICATION_PROTOCOL_INVENTORY_FILENAME",
    "PUBLICATION_PROTOCOL_MANIFEST_FILENAME",
    "PUBLICATION_PROTOCOL_MARKDOWN_FILENAME",
    "PUBLICATION_PROTOCOL_OVERCLAIM_FILENAME",
    "PublicationProtocolBundle",
    "build_publication_protocol",
    "write_publication_protocol_artifacts",
]
