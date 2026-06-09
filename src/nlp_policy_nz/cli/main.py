"""Command-line entry point for the nlp-policy-nz pipeline.

Provides ``process`` and ``search`` subcommands for interacting with the
NLP preprocessing pipeline via the terminal.

Typical usage::

    nlp-policy-nz process -i data/acts/ -o output/legislation.parquet -s legislation
    nlp-policy-nz process -i data/hansard/ -o output/hansard.parquet -s hansard --no-embeddings
    nlp-policy-nz search -q "climate change adaptation" -k 5 -d ./lancedb_data
"""

from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from nlp_policy_nz.api import process_hansard, process_legislation, search_similar

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

        else:
            parser.print_help()
            return 1

    except Exception as exc:
        logger.exception("Command failed: %s", exc)
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
