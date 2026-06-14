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

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from nlp_policy_nz.api import process_hansard, process_legislation, search_similar
from nlp_policy_nz.integrations.hf_uploader import deploy_space, push_dataset_to_hub
from nlp_policy_nz.integrations.release import ReleaseManager
from nlp_policy_nz.integrations.zenodo_archive import ZenodoArchiver

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
    args = parser.parse_args(argv)

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
            archiver = ZenodoArchiver(token=args.token)
            result = archiver.create_archive(
                title=args.title,
                description=args.description,
                creators=creators,
                file_path=args.parquet,
                license_id=args.license,
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

        else:
            parser.print_help()
            return 1

    except Exception as exc:
        logger.exception("Command failed: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
