"""Command-line entry point for the nlp-policy-nz pipeline.

Provides ``process``, ``search``, ``upload-dataset``, ``deploy-space``,
``archive-to-zenodo``, and ``release`` subcommands for interacting with
the NLP preprocessing pipeline via the terminal.

Typical usage::

    nlp-policy-nz process -i data/acts/ -o output/legislation.parquet -s legislation
    nlp-policy-nz process -i data/hansard/ -o output/hansard.parquet -s hansard --no-embeddings
    nlp-policy-nz search -q "climate change adaptation" -k 5 -d ./lancedb_data
    nlp-policy-nz upload-dataset --parquet output/legislation.parquet --repo-id user/nz-legislation
    nlp-policy-nz deploy-space --repo-id user/nz-policy-explorer
    nlp-policy-nz archive-to-zenodo --parquet output/legislation.parquet --title "NZ Legislation"
    nlp-policy-nz release --parquet output/legislation.parquet --version 1.0.0 --title "v1.0"
    nlp-policy-nz export-nz-ontologies --output-dir data/ontologies
    nlp-policy-nz corpus-stats --parquet output/legislation.parquet --output-dir data/statistics
    nlp-policy-nz graph-vector-analysis --output-dir data/analysis
    nlp-policy-nz publication-protocol --output-dir data/publication
    nlp-policy-nz generate-analysis-artifacts --output-dir artifacts
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from nlp_policy_nz.api import process_hansard, process_legislation, search_similar
from nlp_policy_nz.axiom import DOCUMENT_TYPES
from nlp_policy_nz.cli.auth import create_api_key, list_api_keys, revoke_api_key, rotate_api_key
from nlp_policy_nz.cli.completion import (
    SUPPORTED_SHELLS,
    build_completion_script,
    build_manpage,
    write_text_output,
)
from nlp_policy_nz.integrations.hf_uploader import deploy_space, push_dataset_to_hub
from nlp_policy_nz.integrations.release import ReleaseManager
from nlp_policy_nz.integrations.zenodo_archive import ZenodoArchiver
from nlp_policy_nz.provenance import load_provenance_sidecar, provenance_sidecar_path
from nlp_policy_nz.storage import load_from_parquet

logger = logging.getLogger(__name__)


def _setup_logging(verbose: bool = False) -> None:
    """Configure logging for the CLI.

    Parameters
    ----------
    verbose : bool
        If ``True``, set log level to ``DEBUG``; otherwise ``INFO``.

    """
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(levelname)-8s | %(name)s | %(message)s",
        stream=sys.stderr,
    )


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the CLI.

    Returns
    -------
    argparse.ArgumentParser
        Configured parser with ``process`` and ``search`` subcommands.

    """
    parser = argparse.ArgumentParser(
        prog="nlp-policy-nz",
        description="NLP preprocessing pipeline for NZ legislation and Hansard corpora.",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        default=False,
        help="Enable verbose (DEBUG) logging.",
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
        help="Available sub-commands.",
    )

    # --- process subcommand --------------------------------------------------
    process_parser = subparsers.add_parser(
        "process",
        help="Process documents through the NLP pipeline.",
        description=(
            "Read input files, apply Maori-language normalisation, chunk into "
            "sentences, extract citations and Te Reo terms, optionally generate "
            "embeddings, and write the results to a Parquet file."
        ),
    )
    process_parser.add_argument(
        "--input",
        "-i",
        type=str,
        required=True,
        help="Path to input file or directory containing input files.",
    )
    process_parser.add_argument(
        "--output",
        "-o",
        type=str,
        required=True,
        help="Destination path for the output Parquet file.",
    )
    process_parser.add_argument(
        "--source",
        "-s",
        type=str,
        required=True,
        choices=["legislation", "hansard"],
        help="Corpus source type (legislation or hansard).",
    )
    process_parser.add_argument(
        "--no-embeddings",
        action="store_true",
        default=False,
        help="Skip embedding generation (faster, but search will not work).",
    )

    # --- search subcommand ---------------------------------------------------
    search_parser = subparsers.add_parser(
        "search",
        help="Search the vector index for similar documents.",
        description=(
            "Generate an embedding for the query text and search the LanceDB "
            "vector index for the nearest neighbours."
        ),
    )
    search_parser.add_argument(
        "--query",
        "-q",
        type=str,
        required=True,
        help="Natural-language search query.",
    )
    search_parser.add_argument(
        "--top-k",
        "-k",
        type=int,
        default=10,
        help="Number of nearest-neighbour results to return (default: 10).",
    )
    search_parser.add_argument(
        "--db",
        "-d",
        type=str,
        default="./lancedb_data",
        help="Path to the LanceDB database directory (default: ./lancedb_data).",
    )

    # --- upload-dataset subcommand --------------------------------------------
    upload_parser = subparsers.add_parser(
        "upload-dataset",
        help="Upload a Parquet dataset to the Hugging Face Hub.",
        description=(
            "Convert a pipeline Parquet output to a Hugging Face Dataset "
            "and push it to the specified Hub repository."
        ),
    )
    upload_parser.add_argument(
        "--parquet",
        "-p",
        type=str,
        required=True,
        help="Path to the Parquet file to upload.",
    )
    upload_parser.add_argument(
        "--repo-id",
        "-r",
        type=str,
        required=True,
        help='Hugging Face dataset repo ID (e.g. "user/my-dataset").',
    )
    upload_parser.add_argument(
        "--split",
        type=str,
        default="train",
        help="Dataset split name (default: train).",
    )
    upload_parser.add_argument(
        "--private",
        action="store_true",
        default=False,
        help="Create a private repository.",
    )
    upload_parser.add_argument(
        "--message",
        type=str,
        default=None,
        help="Custom commit message for the upload.",
    )

    # --- auth subcommand ----------------------------------------------------
    auth_parser = subparsers.add_parser(
        "auth",
        help="Manage API keys for secured API access.",
        description="Create, list, revoke, and rotate hashed API keys.",
    )
    auth_subparsers = auth_parser.add_subparsers(
        dest="auth_command",
        required=True,
        help="Auth lifecycle commands.",
    )

    auth_create_parser = auth_subparsers.add_parser(
        "create-key",
        help="Create a new API key.",
        description="Generate a new secret key and persist the hashed record.",
    )
    auth_create_parser.add_argument("--name", required=True, help="Human-friendly key name.")
    auth_create_parser.add_argument(
        "--scopes",
        nargs="+",
        required=True,
        help="One or more scopes to grant, such as read write admin.",
    )
    auth_create_parser.add_argument(
        "--expires-at",
        default=None,
        help="Optional ISO 8601 expiration timestamp.",
    )

    auth_subparsers.add_parser(
        "list-keys",
        help="List API keys.",
        description="Show stored API key metadata without revealing secrets.",
    )

    auth_revoke_parser = auth_subparsers.add_parser(
        "revoke-key",
        help="Revoke an API key.",
        description="Mark an API key revoked by key ID.",
    )
    auth_revoke_parser.add_argument("--key-id", required=True, help="Key identifier to revoke.")

    auth_rotate_parser = auth_subparsers.add_parser(
        "rotate-key",
        help="Rotate an API key.",
        description="Revoke the old key and mint a replacement with the same scopes.",
    )
    auth_rotate_parser.add_argument("--key-id", required=True, help="Key identifier to rotate.")

    # --- deploy-space subcommand ---------------------------------------------
    deploy_parser = subparsers.add_parser(
        "deploy-space",
        help="Deploy the Gradio visualization Space to Hugging Face Hub.",
        description=(
            "Push the spaces/ directory (Gradio app) to a Hugging Face Space "
            "repository for interactive exploration of pipeline outputs."
        ),
    )
    deploy_parser.add_argument(
        "--repo-id",
        "-r",
        type=str,
        required=True,
        help='Hugging Face Space repo ID (e.g. "user/my-space").',
    )
    deploy_parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="Hugging Face access token. Falls back to HF_TOKEN env var.",
    )
    deploy_parser.add_argument(
        "--spaces-dir",
        type=str,
        default=None,
        help="Path to the spaces/ directory (default: auto-detect from package root).",
    )
    deploy_parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        help="Validate inputs without uploading.",
    )
    deploy_parser.add_argument(
        "--message",
        type=str,
        default=None,
        help="Custom commit message for the deployment.",
    )

    # --- archive-to-zenodo subcommand ---------------------------------------
    archive_parser = subparsers.add_parser(
        "archive-to-zenodo",
        help="Archive a Parquet file to the Zenodo Sandbox.",
        description=(
            "Upload a Parquet file to Zenodo Sandbox, creating a new "
            "deposit, uploading the file, and publishing it."
        ),
    )
    archive_parser.add_argument(
        "--parquet",
        "-p",
        type=str,
        required=True,
        help="Path to the Parquet file to archive.",
    )
    archive_parser.add_argument(
        "--title",
        type=str,
        required=True,
        help="Title for the Zenodo deposit.",
    )
    archive_parser.add_argument(
        "--description",
        type=str,
        required=True,
        help="Description for the Zenodo deposit.",
    )
    archive_parser.add_argument(
        "--creators",
        type=str,
        required=True,
        help='JSON list of creator dicts, e.g. \'[{"name": "Doe, Jane"}]\'.',
    )
    archive_parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="Zenodo access token. Falls back to ZENODO_SANDBOX_TOKEN env var.",
    )
    archive_parser.add_argument(
        "--license",
        type=str,
        default="MIT",
        help="SPDX license identifier (default: MIT).",
    )

    # --- release subcommand -------------------------------------------------
    release_parser = subparsers.add_parser(
        "release",
        help="Create a versioned release archive and publish to Zenodo.",
        description=(
            "Bundle a Parquet file with metadata into a .tar.gz archive "
            "and publish it to Zenodo Sandbox."
        ),
    )
    release_parser.add_argument(
        "--parquet",
        "-p",
        type=str,
        required=True,
        help="Path to the Parquet file to release.",
    )
    release_parser.add_argument(
        "--version",
        type=str,
        required=True,
        help='Semantic version string (e.g. "1.0.0").',
    )
    release_parser.add_argument(
        "--title",
        type=str,
        required=True,
        help="Title for the Zenodo deposit.",
    )
    release_parser.add_argument(
        "--description",
        type=str,
        required=True,
        help="Description for the Zenodo deposit.",
    )
    release_parser.add_argument(
        "--creators",
        type=str,
        required=True,
        help='JSON list of creator dicts, e.g. \'[{"name": "Doe, Jane"}]\'.',
    )
    release_parser.add_argument(
        "--token",
        type=str,
        default=None,
        help="Zenodo access token. Falls back to ZENODO_SANDBOX_TOKEN env var.",
    )
    release_parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Directory for the local archive (default: temp dir).",
    )

    # --- provenance subcommand ---------------------------------------------
    provenance_parser = subparsers.add_parser(
        "provenance",
        help="Display PROV-O provenance for a Parquet output.",
        description="Read and print the .prov.json sidecar for a Parquet file.",
    )
    provenance_parser.add_argument(
        "parquet",
        type=str,
        help="Path to a Parquet file or an explicit .prov.json sidecar.",
    )

    # --- export-rdf subcommand ---------------------------------------------
    export_rdf_parser = subparsers.add_parser(
        "export-rdf",
        help="Export Hansard Parquet records as SIOC/FOAF Turtle RDF.",
        description="Write a .ttl sidecar containing linked-data discourse RDF.",
    )
    export_rdf_parser.add_argument(
        "--parquet",
        "-p",
        type=str,
        required=True,
        help="Path to the Hansard Parquet file to export.",
    )
    export_rdf_parser.add_argument(
        "--output",
        "-o",
        type=str,
        default=None,
        help="Destination Turtle file (default: <parquet>.ttl).",
    )
    export_rdf_parser.add_argument(
        "--base-uri",
        type=str,
        default="https://data.parliament.nz/",
        help="Base URI for generated RDF resources.",
    )

    # --- sparql subcommand --------------------------------------------------
    sparql_parser = subparsers.add_parser(
        "sparql",
        help="Run a SPARQL SELECT query over a Turtle RDF file.",
        description="Query a local RDF graph generated by export-rdf.",
    )
    sparql_parser.add_argument(
        "--rdf",
        "-r",
        type=str,
        required=True,
        help="Path to a Turtle RDF file.",
    )
    sparql_parser.add_argument(
        "--query",
        "-q",
        type=str,
        required=True,
        help="SPARQL SELECT query to run.",
    )

    # --- knowledge-graph subcommand ----------------------------------------
    kg_parser = subparsers.add_parser(
        "knowledge-graph",
        help="Export Wikidata-annotated entities as JSON-LD.",
        description="Write a schema.org JSON-LD knowledge graph from resolved entities.",
    )
    kg_parser.add_argument(
        "--entities",
        type=str,
        required=True,
        help="Path to a JSON list of resolved Wikidata entities.",
    )
    kg_parser.add_argument(
        "--output",
        "-o",
        type=str,
        required=True,
        help="Destination JSON-LD file.",
    )
    kg_parser.add_argument(
        "--base-uri",
        type=str,
        default="https://legal-nz.example.org/kg/",
        help="Base URI for local JSON-LD entity identifiers.",
    )

    # --- voting-summary subcommand -----------------------------------------
    voting_parser = subparsers.add_parser(
        "voting-summary",
        help="Parse a Hansard division text file into a voting summary.",
        description="Extract motion, vote counts, outcome, party votes, and MP votes.",
    )
    voting_parser.add_argument(
        "--input",
        "-i",
        type=str,
        required=True,
        help="Path to a Hansard division text file.",
    )

    # --- amendment-history subcommand --------------------------------------
    amendment_parser = subparsers.add_parser(
        "amendment-history",
        help="Parse amendment records from a Hansard or committee text file.",
        description="Extract proposer, target clause, type, SOP number, and text.",
    )
    amendment_parser.add_argument(
        "--input",
        "-i",
        type=str,
        required=True,
        help="Path to an amendment debate or committee report text file.",
    )

    # --- rac-export subcommand ---------------------------------------------
    rac_parser = subparsers.add_parser(
        "rac-export",
        help="Export one source section as a rules-as-code bridge JSON-LD record.",
        description=(
            "Create an offline source-grounded bridge record with Axiom-style "
            "source verification, RuleSpec identity, norm semantics, and "
            "schema.org/Legislation metadata."
        ),
    )
    rac_parser.add_argument("--input", "-i", type=str, required=True)
    rac_parser.add_argument("--output", "-o", type=str, required=True)
    rac_parser.add_argument("--citation-path", type=str, required=True)
    rac_parser.add_argument("--source-url", type=str, required=True)
    rac_parser.add_argument("--retrieved-at", type=str, required=True)
    rac_parser.add_argument(
        "--document-type",
        type=str,
        default="act",
        choices=DOCUMENT_TYPES,
    )
    rac_parser.add_argument("--jurisdiction", type=str, default="NZ")
    rac_parser.add_argument("--title", type=str, default=None)
    rac_parser.add_argument("--concept", type=str, default=None)
    rac_parser.add_argument("--effective-date", type=str, default=None)
    rac_parser.add_argument(
        "--package-output-dir",
        type=str,
        default=None,
        help="Optional directory for an OpenFisca/PolicyEngine package skeleton.",
    )
    rac_parser.add_argument(
        "--package-name",
        type=str,
        default="policyengine_nz_generated",
        help="Package name to use with --package-output-dir.",
    )

    # --- export-extractions subcommand -------------------------------------
    export_extractions_parser = subparsers.add_parser(
        "export-extractions",
        help="Export pipeline Parquet records as a broad extraction manifest.",
        description=(
            "Convert existing PipelineRecord Parquet output into deterministic "
            "source-grounded extraction JSON for downstream consumers."
        ),
    )
    export_extractions_parser.add_argument(
        "--parquet",
        "-p",
        type=str,
        required=True,
        help="Path to pipeline Parquet output.",
    )
    export_extractions_parser.add_argument(
        "--output",
        "-o",
        type=str,
        required=True,
        help="Destination extraction manifest JSON file.",
    )
    export_extractions_parser.add_argument(
        "--retrieved-at",
        type=str,
        required=True,
        help="Retrieval timestamp to place in source trace provenance.",
    )
    export_extractions_parser.add_argument(
        "--source-url-base",
        type=str,
        default="pipeline://records",
        help="Base URL used to build per-record source trace URLs.",
    )

    # --- export-nz-ontologies subcommand -----------------------------------
    nz_ontology_parser = subparsers.add_parser(
        "export-nz-ontologies",
        help="Export Track 31 NZ ontology candidates and controlled vocabularies.",
        description=(
            "Write deterministic Track 31 New Zealand ontology candidate JSON, "
            "Turtle, JSON-LD, and SKOS controlled vocabulary artifacts."
        ),
    )
    nz_ontology_parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="data/ontologies",
        help="Directory for NZ ontology artifacts (default: data/ontologies).",
    )

    # --- corpus-stats subcommand -------------------------------------------
    corpus_stats_parser = subparsers.add_parser(
        "corpus-stats",
        help="Export Track 32 corpus descriptive statistics.",
        description=(
            "Compute deterministic Track 32 statistics from PipelineRecord Parquet "
            "inputs and checked-in ontology/blocker manifests."
        ),
    )
    corpus_stats_parser.add_argument(
        "--parquet",
        "-p",
        action="append",
        default=[],
        help=(
            "PipelineRecord Parquet file to include. May be supplied more than once; "
            "if omitted, deterministic repo fixtures are used."
        ),
    )
    corpus_stats_parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="data/statistics",
        help="Directory for JSON and CSV statistics artifacts (default: data/statistics).",
    )
    corpus_stats_parser.add_argument(
        "--markdown",
        type=str,
        default=None,
        help="Path for the Markdown summary.",
    )

    # --- graph-vector-analysis subcommand ---------------------------------
    graph_vector_parser = subparsers.add_parser(
        "graph-vector-analysis",
        help="Export Track 33 graph, vector, and network analysis.",
        description=(
            "Compute deterministic Track 33 graph topology, vector clustering, "
            "and graph/vector alignment metrics from checked-in artifacts."
        ),
    )
    graph_vector_parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="data/analysis",
        help="Directory for JSON, CSV, and Mermaid analysis artifacts.",
    )
    graph_vector_parser.add_argument(
        "--markdown",
        type=str,
        default=None,
        help="Path for the Markdown summary.",
    )

    publication_parser = subparsers.add_parser(
        "publication-protocol",
        help="Export Track 34 standards-based publication protocol.",
        description=(
            "Write deterministic Track 34 publication protocol artifacts, including "
            "claim evidence mapping, artifact inventory, reproducibility commands, "
            "and overclaim-risk review."
        ),
    )
    publication_parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="data/publication",
        help="Directory for publication protocol JSON artifacts.",
    )
    publication_parser.add_argument(
        "--markdown",
        type=str,
        default=None,
        help="Path for the Markdown protocol document.",
    )

    artifact_parser = subparsers.add_parser(
        "generate-analysis-artifacts",
        help="Generate Track 35 tables, figures, diagrams, and blockers.",
        description=(
            "Execute deterministic Track 35 artifact production from checked-in "
            "Track 32-34 analysis outputs, writing machine-readable tables, SVG "
            "figures, Mermaid diagrams, blockers, and a visual inspection checklist."
        ),
    )
    artifact_parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="artifacts",
        help="Directory for generated analysis artifacts (default: artifacts).",
    )

    manuscript_parser = subparsers.add_parser(
        "generate-manuscript-package",
        help="Generate Track 37 manuscript and review-agent artifacts.",
        description=(
            "Write deterministic Track 37 manuscript, supplement, arXiv requirements, "
            "LaTeX source scaffold, 100-point review rubrics, and offline review logs."
        ),
    )
    manuscript_parser.add_argument(
        "--output-dir",
        "-o",
        type=str,
        default="artifacts/manuscript",
        help="Directory for manuscript artifacts (default: artifacts/manuscript).",
    )

    # --- completion subcommand ---------------------------------------------
    completion_parser = subparsers.add_parser(
        "completion",
        help="Generate shell completions and a man page.",
        description="Render installable shell completion snippets and a manual page.",
    )
    completion_subparsers = completion_parser.add_subparsers(
        dest="completion_command",
        required=True,
        help="Completion artifacts.",
    )

    install_parser = completion_subparsers.add_parser(
        "install",
        help="Generate shell completion output.",
        description="Write a completion script for bash, zsh, or PowerShell.",
    )
    install_parser.add_argument(
        "--shell",
        required=True,
        choices=SUPPORTED_SHELLS,
        help="Target shell for the completion script.",
    )
    install_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional destination file. Prints to stdout when omitted.",
    )

    manpage_parser = completion_subparsers.add_parser(
        "manpage",
        help="Generate a man page from the parser.",
        description="Write a roff man page derived from the argparse parser.",
    )
    manpage_parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Optional destination file. Prints to stdout when omitted.",
    )

    return parser


def main(argv: list[str] | None = None) -> int:  # noqa: PLR0911
    """CLI entry point for the nlp-policy-nz pipeline.

    Parses command-line arguments and dispatches to the appropriate
    subcommand handler.

    Parameters
    ----------
    argv : list[str] | None
        Command-line argument list.  If ``None``, :data:`sys.argv` is used.

    Returns
    -------
    int
        Exit code (``0`` on success, ``1`` on failure).

    """
    parser = _build_parser()
    commands = {
        "process",
        "search",
        "upload-dataset",
        "deploy-space",
        "archive-to-zenodo",
        "release",
        "auth",
        "provenance",
        "export-rdf",
        "sparql",
        "knowledge-graph",
        "voting-summary",
        "amendment-history",
        "rac-export",
        "export-extractions",
        "export-nz-ontologies",
        "corpus-stats",
        "graph-vector-analysis",
        "completion",
        "publication-protocol",
        "generate-analysis-artifacts",
        "generate-manuscript-package",
    }
    if argv and argv[0] not in commands and not argv[0].startswith("-"):
        parser.print_help()
        return 1

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if argv and argv[0] in {"--help", "-h"}:
            return exc.code if isinstance(exc.code, int) else 1
        code = exc.code if isinstance(exc.code, int) else 1
        if code == 0:
            return 0
        raise

    _setup_logging(verbose=args.verbose)

    try:
        if args.command == "process":
            generate_emb = not args.no_embeddings
            input_path = Path(args.input)
            output_path = Path(args.output)

            if args.source == "legislation":
                process_legislation(
                    input_path,
                    output_path,
                    generate_embeddings=generate_emb,
                )
            else:
                process_hansard(
                    input_path,
                    output_path,
                    generate_embeddings=generate_emb,
                )

            logger.info("Processing complete.")

        elif args.command == "search":
            results = search_similar(
                query=args.query,
                db_path=args.db,
                top_k=args.top_k,
            )

            if not results:
                pass
            else:
                for _i, res in enumerate(results, start=1):
                    res.get("doc_id", "?")
                    text = res.get("text", "")
                    res.get("_distance", "?")
                    text[:120] + "..." if len(text) > 120 else text  # noqa: PLR2004

        elif args.command == "upload-dataset":
            url = push_dataset_to_hub(
                parquet_path=args.parquet,
                repo_id=args.repo_id,
                split=args.split,
                private=args.private,
                commit_message=args.message,
            )
            logger.info("Dataset uploaded: %s", url)

        elif args.command == "deploy-space":
            url = deploy_space(
                repo_id=args.repo_id,
                spaces_dir=args.spaces_dir,
                token=args.token,
                commit_message=args.message,
                dry_run=args.dry_run,
            )
            logger.info("Space deployed: %s", url)

        elif args.command == "archive-to-zenodo":
            import json as _json  # noqa: PLC0415

            creators = _json.loads(args.creators)
            provenance_path = provenance_sidecar_path(args.parquet)
            provenance_metadata = (
                load_provenance_sidecar(provenance_path) if provenance_path.is_file() else None
            )
            archiver = ZenodoArchiver(token=args.token)
            result = archiver.create_archive(
                title=args.title,
                description=args.description,
                creators=creators,
                file_path=args.parquet,
                license_id=args.license,
                provenance_metadata=provenance_metadata,
            )
            logger.info("Archived to Zenodo - DOI: %s", result.get("doi", "N/A"))

        elif args.command == "release":
            import json as _json  # noqa: PLC0415

            creators = _json.loads(args.creators)
            manager = ReleaseManager(token=args.token)
            result = manager.full_release(
                args.parquet,
                version=args.version,
                title=args.title,
                description=args.description,
                creators=creators,
            )
            logger.info("Release published - DOI: %s", result.get("doi", "N/A"))

        elif args.command == "auth":
            import json as _json  # noqa: PLC0415

            if args.auth_command == "create-key":
                payload = create_api_key(name=args.name, scopes=args.scopes, expires_at=args.expires_at)
                sys.stdout.write(f"{_json.dumps(payload, indent=2, ensure_ascii=False)}\n")
            elif args.auth_command == "list-keys":
                payload = list_api_keys()
                sys.stdout.write(f"{_json.dumps(payload, indent=2, ensure_ascii=False)}\n")
            elif args.auth_command == "revoke-key":
                payload = revoke_api_key(key_id=args.key_id)
                sys.stdout.write(f"{_json.dumps(payload, indent=2, ensure_ascii=False)}\n")
            elif args.auth_command == "rotate-key":
                payload = rotate_api_key(key_id=args.key_id)
                sys.stdout.write(f"{_json.dumps(payload, indent=2, ensure_ascii=False)}\n")
            else:
                parser.print_help()
                return 1

        elif args.command == "provenance":
            import json as _json  # noqa: PLC0415

            data = load_provenance_sidecar(args.parquet)
            sys.stdout.write(f"{_json.dumps(data, indent=2, ensure_ascii=False)}\n")

        elif args.command == "export-rdf":
            from nlp_policy_nz.linked_data import (  # noqa: PLC0415
                export_hansard_sioc,
                rdf_sidecar_path,
            )

            records = load_from_parquet(args.parquet)
            output = Path(args.output) if args.output else rdf_sidecar_path(args.parquet)
            result = export_hansard_sioc(
                records,
                output,
                base_uri=args.base_uri,
            )
            logger.info("RDF export written: %s", result)

        elif args.command == "sparql":
            import json as _json  # noqa: PLC0415

            from nlp_policy_nz.linked_data import query_graph  # noqa: PLC0415

            rows = query_graph(args.rdf, args.query)
            sys.stdout.write(f"{_json.dumps(rows, indent=2, ensure_ascii=False)}\n")

        elif args.command == "knowledge-graph":
            from nlp_policy_nz.kb import (  # noqa: PLC0415
                export_knowledge_graph_jsonld,
                load_wikidata_entities,
            )

            entities = load_wikidata_entities(args.entities)
            result = export_knowledge_graph_jsonld(
                entities,
                args.output,
                base_uri=args.base_uri,
            )
            logger.info("Knowledge graph written: %s", result)

        elif args.command == "voting-summary":
            from nlp_policy_nz.parliament.voting import parse_division  # noqa: PLC0415

            text = Path(args.input).read_text(encoding="utf-8")
            division = parse_division(text)
            payload = (
                None
                if division is None
                else {
                    "motion": division.motion,
                    "ayes_count": division.ayes_count,
                    "nays_count": division.nays_count,
                    "abstains_count": division.abstains_count,
                    "outcome": division.outcome,
                    "votes": [vote.__dict__ for vote in division.votes],
                    "party_votes": division.party_votes,
                }
            )
            sys.stdout.write(f"{json.dumps(payload, indent=2, ensure_ascii=False)}\n")

        elif args.command == "amendment-history":
            from nlp_policy_nz.parliament.amendments import (  # noqa: PLC0415
                amendments_to_dicts,
                parse_amendments,
            )

            text = Path(args.input).read_text(encoding="utf-8")
            payload = amendments_to_dicts(parse_amendments(text))
            sys.stdout.write(f"{json.dumps(payload, indent=2, ensure_ascii=False)}\n")

        elif args.command == "rac-export":
            from nlp_policy_nz.axiom import SourceSection  # noqa: PLC0415
            from nlp_policy_nz.ontology import (  # noqa: PLC0415
                build_policyengine_package_skeleton,
                build_rules_as_code_bridge,
                write_policyengine_package_skeleton,
                write_rules_as_code_bridge_json,
            )

            text = Path(args.input).read_text(encoding="utf-8")
            section = SourceSection.from_text(
                text,
                citation_path=args.citation_path,
                jurisdiction=args.jurisdiction,
                document_type=args.document_type,
                source_url=args.source_url,
                retrieved_at=args.retrieved_at,
                title=args.title,
                effective_date=args.effective_date,
            )
            record = build_rules_as_code_bridge(section, concept=args.concept)
            result = write_rules_as_code_bridge_json(record, args.output)
            logger.info("Rules-as-code bridge written: %s", result)
            if args.package_output_dir:
                skeleton = build_policyengine_package_skeleton(
                    record,
                    package_name=args.package_name,
                )
                package_dir = write_policyengine_package_skeleton(
                    skeleton,
                    args.package_output_dir,
                )
                logger.info("Package skeleton written: %s", package_dir)

        elif args.command == "export-extractions":
            from nlp_policy_nz.extraction import (  # noqa: PLC0415
                export_extraction_manifest_from_parquet,
            )

            result = export_extraction_manifest_from_parquet(
                args.parquet,
                args.output,
                retrieved_at=args.retrieved_at,
                source_url_base=args.source_url_base,
            )
            logger.info("Extraction manifest written: %s", result)

        elif args.command == "export-nz-ontologies":
            from nlp_policy_nz.ontology import write_nz_ontology_artifacts  # noqa: PLC0415

            written = write_nz_ontology_artifacts(args.output_dir)
            logger.info(
                "NZ ontology artifacts written: %s", sorted(str(path) for path in written.values())
            )

        elif args.command == "corpus-stats":
            from nlp_policy_nz.analysis import (  # noqa: PLC0415
                build_fixture_records,
                load_pipeline_records,
                write_corpus_statistics_artifacts,
            )

            records = (
                load_pipeline_records(tuple(args.parquet))
                if args.parquet
                else build_fixture_records()
            )
            written = write_corpus_statistics_artifacts(
                args.output_dir,
                records=records,
                markdown_path=args.markdown,
            )
            logger.info(
                "Corpus statistics artifacts written: %s",
                sorted(str(path) for path in written.values()),
            )

        elif args.command == "graph-vector-analysis":
            from nlp_policy_nz.analysis import (  # noqa: PLC0415
                write_graph_vector_network_artifacts,
            )

            written = write_graph_vector_network_artifacts(
                args.output_dir,
                markdown_path=args.markdown,
            )
            logger.info(
                "Graph/vector analysis artifacts written: %s",
                sorted(str(path) for path in written.values()),
            )

        elif args.command == "publication-protocol":
            from nlp_policy_nz.publication.protocol import (  # noqa: PLC0415
                write_publication_protocol_artifacts,
            )

            written = write_publication_protocol_artifacts(
                args.output_dir,
                markdown_path=args.markdown,
            )
            logger.info(
                "Publication protocol artifacts written: %s",
                sorted(str(path) for path in written.values()),
            )

        elif args.command == "generate-analysis-artifacts":
            from nlp_policy_nz.analysis import write_analysis_artifacts  # noqa: PLC0415

            written = write_analysis_artifacts(args.output_dir)
            logger.info(
                "Analysis artifacts written: %s",
                sorted(str(path) for path in written.values()),
            )

        elif args.command == "generate-manuscript-package":
            from nlp_policy_nz.publication import write_manuscript_package  # noqa: PLC0415

            written = write_manuscript_package(args.output_dir)
            logger.info(
                "Manuscript package artifacts written: %s",
                sorted(str(path) for path in written.values()),
            )

        elif args.command == "completion":
            if args.completion_command == "install":
                write_text_output(
                    build_completion_script(parser, args.shell),
                    args.output,
                )
            elif args.completion_command == "manpage":
                write_text_output(build_manpage(parser), args.output)
            else:
                parser.print_help()
                return 1

        else:
            parser.print_help()
            return 1

    except Exception:
        logger.exception("Command failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
