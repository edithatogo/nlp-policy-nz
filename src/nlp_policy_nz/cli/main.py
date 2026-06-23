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
"""

import argparse
import json
import logging
import sys
from pathlib import Path

from nlp_policy_nz.api import process_hansard, process_legislation, search_similar
from nlp_policy_nz.integrations.hf_uploader import deploy_space, push_dataset_to_hub
from nlp_policy_nz.integrations.release import ReleaseManager
from nlp_policy_nz.integrations.zenodo_archive import ZenodoArchiver
from nlp_policy_nz.parliament.amendments import amendments_to_dicts, parse_amendments
from nlp_policy_nz.parliament.voting import parse_division
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

    return parser


def main(argv: list[str] | None = None) -> int:
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
        "provenance",
        "export-rdf",
        "sparql",
        "knowledge-graph",
        "voting-summary",
        "amendment-history",
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
                load_provenance_sidecar(provenance_path)
                if provenance_path.is_file()
                else None
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
            text = Path(args.input).read_text(encoding="utf-8")
            division = parse_division(text)
            payload = None if division is None else {
                "motion": division.motion,
                "ayes_count": division.ayes_count,
                "nays_count": division.nays_count,
                "abstains_count": division.abstains_count,
                "outcome": division.outcome,
                "votes": [vote.__dict__ for vote in division.votes],
                "party_votes": division.party_votes,
            }
            sys.stdout.write(f"{json.dumps(payload, indent=2, ensure_ascii=False)}\n")

        elif args.command == "amendment-history":
            text = Path(args.input).read_text(encoding="utf-8")
            payload = amendments_to_dicts(parse_amendments(text))
            sys.stdout.write(f"{json.dumps(payload, indent=2, ensure_ascii=False)}\n")

        else:
            parser.print_help()
            return 1

    except Exception:
        logger.exception("Command failed")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
