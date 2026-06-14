"""Public API for the nlp-policy-nz pipeline.

Provides high-level functions that orchestrate the full NLP preprocessing
pipeline for New Zealand legislation and Hansard corpora.  Each function
coordinates across the guard, syntactic, semantic, and storage modules
to produce a complete workflow for a given corpus type.

Typical usage::

    from nlp_policy_nz import process_legislation, process_hansard, search_similar

    # Process a legislation XML file through the pipeline
    out = process_legislation("input.xml", "output.parquet")

    # Search the resulting vector index
    results = search_similar("climate change adaptation", top_k=5)
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

from nlp_policy_nz.guard import LanguageIdentifier, normalize_text
from nlp_policy_nz.legal import classify_legal_effect, detect_modality
from nlp_policy_nz.semantic import generate_embedding
from nlp_policy_nz.semantic.model_loader import load_model
from nlp_policy_nz.storage import PipelineRecord, VectorIndex, serialize_to_parquet
from nlp_policy_nz.syntactic import (
    chunk_hansard_speech,
    chunk_legislation_document,
    create_citation_ruler,
    create_nlp_pipeline,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _resolve_path(path: str | Path) -> Path:
    """Resolve a string or Path to an absolute Path.

    Parameters
    ----------
    path : str | Path
        Filesystem path to resolve.

    Returns
    -------
    Path
        Absolute, resolved :class:`~pathlib.Path`.

    """
    return Path(path).resolve()


def _collect_input_files(input_path: str | Path) -> list[Path]:
    """Collect all input files from a file path or directory.

    Parameters
    ----------
    input_path : str | Path
        Path to a single file or a directory of input files.

    Returns
    -------
    list[Path]
        List of resolved file paths.

    Raises
    ------
    FileNotFoundError
        If the input path does not exist.

    """
    path = _resolve_path(input_path)
    if path.is_file():
        return [path]
    if path.is_dir():
        files: list[Path] = sorted(
            p
            for p in path.iterdir()
            if p.is_file() and p.suffix.lower() in {".xml", ".txt", ".json"}
        )
        if not files:
            msg = f"No supported input files found in directory: {path}"
            raise FileNotFoundError(msg)
        return files
    msg = f"Input path does not exist: {path}"
    raise FileNotFoundError(msg)


def _extract_te_reo_terms(text: str) -> list[str]:
    """Extract Te Reo Māori terms from *text* using the language identifier.

    Parameters
    ----------
    text : str
        The text to scan for Māori-language segments.

    Returns
    -------
    list[str]
        A list of Te Reo Māori terms found in the text.

    """
    identifier = LanguageIdentifier()
    segments = identifier.detect_code_switching(text)
    return [seg for lang, seg in segments if lang == "mi"]


def _extract_citations(text: str, nlp: Any) -> list[str]:
    """Extract NZ act / section citations from *text*.

    Uses the spaCy pipeline's citation ruler (if registered) to identify
    legislative references.

    Parameters
    ----------
    text : str
        The text to scan for citations.
    nlp : spacy.language.Language
        A spaCy pipeline with citation-ruler component.

    Returns
    -------
    list[str]
        Detected citation strings.

    """
    doc = nlp(text)
    citations: list[str] = []
    for ent in doc.ents:
        if ent.label_ in {"NZ_ACT", "NZ_SECTION", "CITATION"}:
            citations.append(ent.text)
    for span_group_name in ("nz_cross_references",):
        for span in doc.spans.get(span_group_name, []):
            label = span.label_ if hasattr(span, "label_") else ""
            if label:
                citations.append(f"[{label}] {span.text}")
    return citations


# ---------------------------------------------------------------------------
# Public API: Processing
# ---------------------------------------------------------------------------


def process_legislation(
    input_path: str | Path,
    output_path: str | Path,
    generate_embeddings: bool = True,
) -> Path:
    """Process legislation documents through the full NLP pipeline.

    Reads one or more input files (XML or plain text), parses legislative
    structure, applies Māori-language normalisation, chunks into sentences,
    detects Te Reo terms and citations, optionally generates dense vector
    embeddings, and writes the results to a Parquet file.

    Parameters
    ----------
    input_path : str | Path
        Path to a single legislation file or a directory containing
        legislation files (``.xml``, ``.txt``, ``.json``).
    output_path : str | Path
        Destination path for the output Parquet file.
    generate_embeddings : bool
        If ``True`` (default), generate dense vector embeddings for each
        chunk using the Hugging Face transformer model.

    Returns
    -------
    Path
        The resolved absolute path of the written Parquet file.

    Raises
    ------
    FileNotFoundError
        If *input_path* does not exist.
    ValueError
        If no valid input files are found or no records are produced.

    Examples
    --------
    >>> out = process_legislation("data/acts/", "output/legislation.parquet")
    >>> print(out)
    ...\\\\output\\\\legislation.parquet

    """
    input_files = _collect_input_files(input_path)
    logger.info("Found %d legislation input file(s)", len(input_files))

    nlp = create_nlp_pipeline()
    if "citation_ruler" not in nlp.pipe_names:
        create_citation_ruler(nlp)
    if "deontic_modality" not in nlp.pipe_names:
        after = "parser" if "parser" in nlp.pipe_names else None
        nlp.add_pipe("deontic_modality", after=after)

    records: list[PipelineRecord] = []

    for file_path in input_files:
        raw_text = file_path.read_text(encoding="utf-8")
        clean_text = normalize_text(raw_text)

        chunks = chunk_legislation_document(clean_text, nlp, year=2024, number=1)

        for chunk in chunks:
            chunk_text: str = chunk["text"]
            te_reo_terms = _extract_te_reo_terms(chunk_text)
            citations = _extract_citations(chunk_text, nlp)
            deontic_modality = [
                annotation.to_dict() for annotation in detect_modality(chunk_text, nlp)
            ]
            legal_effect = classify_legal_effect(chunk_text, nlp)

            records.append(
                PipelineRecord(
                    doc_id=chunk["doc_id"],
                    corpus_source="legislation",
                    raw_text=chunk_text,
                    cleaned_tokens=[t.strip() for t in chunk_text.split() if t.strip()],
                    nz_act_citations=citations,
                    te_reo_terms=te_reo_terms,
                    embeddings=None,
                    deontic_modality=deontic_modality,
                    legal_effect=legal_effect,
                )
            )

    if not records:
        msg = "No pipeline records were produced from the input files."
        raise ValueError(msg)

    if generate_embeddings:
        logger.info("Generating embeddings for %d records \\u2026", len(records))
        model, tokenizer = load_model()
        for rec in records:
            embedding = generate_embedding(rec.raw_text, model, tokenizer)
            rec.embeddings = embedding

    output = _resolve_path(output_path)
    result = serialize_to_parquet(records, output)
    logger.info("Legislation pipeline output written to %s", result)
    return result


def process_hansard(
    input_path: str | Path,
    output_path: str | Path,
    generate_embeddings: bool = True,
) -> Path:
    """Process Hansard speech documents through the full NLP pipeline.

    Reads one or more input files (``.txt``, ``.json``, or ``.xml``),
    applies Maori-language normalisation, chunks into sentences with
    Hansard-specific document IDs, detects Te Reo terms and citations,
    optionally generates dense vector embeddings, and writes the results
    to a Parquet file.

    Parameters
    ----------
    input_path : str | Path
        Path to a single Hansard file or a directory containing Hansard
        files (``.txt``, ``.json``, ``.xml``).
    output_path : str | Path
        Destination path for the output Parquet file.
    generate_embeddings : bool
        If ``True`` (default), generate dense vector embeddings for each
        chunk using the Hugging Face transformer model.

    Returns
    -------
    Path
        The resolved absolute path of the written Parquet file.

    Raises
    ------
    FileNotFoundError
        If *input_path* does not exist.
    ValueError
        If no valid input files are found or no records are produced.

    Examples
    --------
    >>> out = process_hansard("data/hansard/2023-05-12.txt",
    ...                       "output/hansard.parquet")
    >>> print(out)
    ...\\\\output\\\\hansard.parquet

    """
    input_files = _collect_input_files(input_path)
    logger.info("Found %d Hansard input file(s)", len(input_files))

    nlp = create_nlp_pipeline()
    if "citation_ruler" not in nlp.pipe_names:
        create_citation_ruler(nlp)

    records: list[PipelineRecord] = []

    for idx, file_path in enumerate(input_files):
        raw_text = file_path.read_text(encoding="utf-8")
        clean_text = normalize_text(raw_text)

        date_str = file_path.stem[:10] if len(file_path.stem) >= 10 else "unknown-date"  # noqa: PLR2004
        chunks = chunk_hansard_speech(clean_text, nlp, date=date_str, speech_num=idx + 1)

        for chunk in chunks:
            chunk_text: str = chunk["text"]
            te_reo_terms = _extract_te_reo_terms(chunk_text)
            citations = _extract_citations(chunk_text, nlp)

            records.append(
                PipelineRecord(
                    doc_id=chunk["doc_id"],
                    corpus_source="hansard",
                    raw_text=chunk_text,
                    cleaned_tokens=[t.strip() for t in chunk_text.split() if t.strip()],
                    nz_act_citations=citations,
                    te_reo_terms=te_reo_terms,
                    embeddings=None,
                )
            )

    if not records:
        msg = "No pipeline records were produced from the input files."
        raise ValueError(msg)

    if generate_embeddings:
        logger.info("Generating embeddings for %d records ...", len(records))
        model, tokenizer = load_model()
        for rec in records:
            embedding = generate_embedding(rec.raw_text, model, tokenizer)
            rec.embeddings = embedding

    output = _resolve_path(output_path)
    result = serialize_to_parquet(records, output)
    logger.info("Hansard pipeline output written to %s", result)
    return result


# ---------------------------------------------------------------------------
# Public API: Search
# ---------------------------------------------------------------------------


def search_similar(
    query: str,
    db_path: str = "./lancedb_data",
    top_k: int = 10,
) -> list[dict[str, Any]]:
    """Search the vector index for documents similar to *query*.

    Loads the LanceDB vector index located at *db_path*, generates an
    embedding for the query text, and returns the top-*k* most similar
    documents with their metadata and similarity distances.

    Parameters
    ----------
    query : str
        The natural-language search query.
    db_path : str
        Filesystem path to the LanceDB database directory.
        Defaults to ``\"./lancedb_data\"``.
    top_k : int
        Number of nearest-neighbour results to return.
        Defaults to ``10``.

    Returns
    -------
    list[dict[str, Any]]
        A list of result dictionaries.  Each dict contains the record fields
        (``doc_id``, ``text``, ``corpus_source``, etc.) plus a ``_distance``
        key with the vector distance metric.

    Raises
    ------
    FileNotFoundError
        If the LanceDB database directory does not exist.
    RuntimeError
        If the vector index is empty or not found.

    Examples
    --------
    >>> results = search_similar("Treaty of Waitangi principles", top_k=5)
    >>> len(results)
    5
    >>> results[0][\"doc_id\"]
    'NZ-ACT-1961-043-SEC-4'

    """
    db = Path(db_path).resolve()
    if not db.is_dir():
        msg = f"LanceDB database directory not found: {db}"
        raise FileNotFoundError(msg)

    model, tokenizer = load_model()
    query_embedding = generate_embedding(query, model, tokenizer)

    index = VectorIndex(uri=str(db))
    if not index.table_exists():
        msg = (
            f"No table found in LanceDB database at {db}. "
            "Run pipeline processing with embeddings enabled first."
        )
        raise RuntimeError(msg)

    results = index.search(query_embedding, top_k=top_k)
    return results
