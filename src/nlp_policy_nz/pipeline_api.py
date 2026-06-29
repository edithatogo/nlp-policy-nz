"""Public API for the nlp-policy-nz pipeline.

Provides high-level functions that orchestrate the full NLP preprocessing
pipeline for New Zealand legislation and Hansard corpora. Each function
coordinates across the guard, syntactic, semantic, and storage modules
to produce a complete workflow for a given corpus type.
"""

from __future__ import annotations

import logging
import re
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING, Any

from nlp_policy_nz.discourse import ArgumentDetector, StanceClassifier
from nlp_policy_nz.guard import LanguageIdentifier, normalize_text
from nlp_policy_nz.kb import (
    EntityContext,
    EntityRecord,
    NzEntityResolverComponent,
    default_nz_entities,
)
from nlp_policy_nz.legal import classify_legal_effect, detect_modality, detect_temporal_expressions
from nlp_policy_nz.parliament.amendments import amendments_to_dicts, parse_amendments
from nlp_policy_nz.parliament.voting import parse_division
from nlp_policy_nz.provenance import ProvenanceRecorder
from nlp_policy_nz.semantic import generate_embedding
from nlp_policy_nz.semantic.model_loader import DEFAULT_MODEL, load_model
from nlp_policy_nz.storage import LanceDBAdapter, PipelineRecord, serialize_to_parquet
from nlp_policy_nz.syntactic import (
    chunk_hansard_speech,
    chunk_legislation_document,
    create_citation_ruler,
    create_nlp_pipeline,
)
from nlp_policy_nz.telemetry import configure_tracing, pipeline_span, set_span_attribute

if TYPE_CHECKING:
    from spacy.language import Language

logger = logging.getLogger(__name__)


def _model_version_from_loaded(model: object, tokenizer: object) -> str:
    """Return the best available model identifier for provenance."""
    model_config = getattr(model, "config", None)
    tokenizer_kwargs = getattr(tokenizer, "init_kwargs", {})
    candidates = (
        getattr(model_config, "_name_or_path", None),
        tokenizer_kwargs.get("name_or_path") if isinstance(tokenizer_kwargs, dict) else None,
        getattr(tokenizer, "name_or_path", None),
    )
    for candidate in candidates:
        if candidate:
            return str(candidate)
    return DEFAULT_MODEL


def _resolve_path(path: str | Path) -> Path:
    """Resolve a string or Path to an absolute Path."""
    return Path(path).resolve()


def _collect_input_files(input_path: str | Path) -> list[Path]:
    """Collect all input files from a file path or directory."""
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
    """Extract Te Reo Maori terms from *text* using the language identifier."""
    identifier = LanguageIdentifier()
    segments = identifier.detect_code_switching(text)
    return [seg for lang, seg in segments if lang == "mi"]


def _extract_citations(text: str, nlp: Language) -> list[str]:
    """Extract NZ act / section citations from *text*."""
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


def _extract_voting_record(text: str) -> dict[str, Any] | None:
    """Extract a Hansard division record summary from text, if present."""
    division = parse_division(text)
    if division is None or (
        division.ayes_count == 0
        and division.nays_count == 0
        and division.abstains_count == 0
        and not division.votes
        and not division.party_votes
    ):
        return None
    payload = asdict(division)
    if not payload["votes"]:
        payload["votes"] = None
    if not payload["party_votes"]:
        payload["party_votes"] = None
    return payload


def _extract_amendment_records(text: str) -> list[dict[str, str | None]]:
    """Extract amendment records from text."""
    return amendments_to_dicts(parse_amendments(text))


def _ensure_nz_entity_resolver(nlp: Language) -> NzEntityResolverComponent:
    """Return the registered NZ entity resolver component."""
    if not hasattr(nlp, "get_pipe"):
        return NzEntityResolverComponent()
    if "nz_entity_resolver" not in nlp.pipe_names:
        nlp.add_pipe("nz_entity_resolver", last=True)
    component = nlp.get_pipe("nz_entity_resolver")
    if not isinstance(component, NzEntityResolverComponent):
        msg = "spaCy component 'nz_entity_resolver' has an unexpected type."
        raise TypeError(msg)
    return component


def _resolve_named_entities(
    text: str,
    nlp: Language,
    *,
    context: EntityContext | None = None,
) -> list[dict[str, Any]]:
    """Resolve known NZ legal and parliamentary entities in text."""
    if not hasattr(nlp, "get_pipe"):
        return []
    component = _ensure_nz_entity_resolver(nlp)
    doc = nlp(text)
    return [entity.to_dict() for entity in component.resolve_doc(doc, context=context)]


def _infer_entity_context(text: str, *, date: str | None = None) -> EntityContext:
    """Infer party/electorate context from exact KB mentions in text."""
    party: str | None = None
    electorate: str | None = None
    for entity in default_nz_entities():
        if entity.entity_type not in {"party", "electorate"}:
            continue
        if not _text_mentions_entity(text, entity):
            continue
        if entity.entity_type == "party" and party is None:
            party = entity.name
        if entity.entity_type == "electorate" and electorate is None:
            electorate = entity.name
        if party and electorate:
            break
    return EntityContext(party=party, electorate=electorate, date=date)


def _text_mentions_entity(text: str, entity: EntityRecord) -> bool:
    """Return whether text contains an exact entity name or alias."""
    return any(
        re.search(rf"\b{re.escape(name)}\b", text, flags=re.IGNORECASE)
        for name in entity.names()
    )


def _valid_context_date(value: str) -> str | None:
    """Return an ISO date suitable for entity context scoring."""
    return value if re.fullmatch(r"\d{4}-\d{2}-\d{2}", value) else None


def process_legislation(
    input_path: str | Path,
    output_path: str | Path,
    generate_embeddings: bool = True,
) -> Path:
    """Process legislation documents through the full NLP pipeline."""
    output = _resolve_path(output_path)
    configure_tracing(
        service_name="nlp-policy-nz",
        trace_file=output.with_suffix(".traces.jsonl"),
    )
    with pipeline_span(
        "pipeline.process_legislation",
        {
            "pipeline.source": "legislation",
            "pipeline.generate_embeddings": generate_embeddings,
            "pipeline.output_path": str(output),
        },
    ):
        input_files = _collect_input_files(input_path)
        set_span_attribute("pipeline.input_file_count", len(input_files))
        result = _process_legislation_records(input_files, output, generate_embeddings)
        set_span_attribute("pipeline.output_path", str(result))
        return result


def _process_legislation_records(
    input_files: list[Path],
    output: Path,
    generate_embeddings: bool,
) -> Path:
    """Run the legislation processing implementation for resolved inputs."""
    recorder = ProvenanceRecorder(
        pipeline_name="process_legislation",
        parameters={"generate_embeddings": generate_embeddings, "source": "legislation"},
    )
    logger.info("Found %d legislation input file(s)", len(input_files))

    nlp = create_nlp_pipeline()
    if "citation_ruler" not in nlp.pipe_names:
        create_citation_ruler(nlp)
    if "deontic_modality" not in nlp.pipe_names:
        after = "parser" if "parser" in nlp.pipe_names else None
        nlp.add_pipe("deontic_modality", after=after)
    _ensure_nz_entity_resolver(nlp)

    records: list[PipelineRecord] = []
    for file_path in input_files:
        with pipeline_span(
            "pipeline.legislation.file",
            {"file.path": str(file_path), "file.name": file_path.name},
        ):
            raw_text = file_path.read_text(encoding="utf-8")
            clean_text = normalize_text(raw_text)
            chunks = chunk_legislation_document(clean_text, nlp, year=2024, number=1)
            set_span_attribute("pipeline.chunk_count", len(chunks))

            for chunk in chunks:
                chunk_text: str = chunk["text"]
                with pipeline_span(
                    "pipeline.legislation.chunk",
                    {"chunk.doc_id": chunk["doc_id"], "chunk.length": len(chunk_text)},
                ):
                    te_reo_terms = _extract_te_reo_terms(chunk_text)
                    citations = _extract_citations(chunk_text, nlp)
                    deontic_modality = [
                        annotation.to_dict() for annotation in detect_modality(chunk_text, nlp)
                    ]
                    temporal_expressions = [
                        annotation.to_dict()
                        for annotation in detect_temporal_expressions(chunk_text, nlp)
                    ]
                    context = _infer_entity_context(chunk_text)
                    resolved_entities = _resolve_named_entities(chunk_text, nlp, context=context)
                    legal_effect = classify_legal_effect(chunk_text, nlp)
                    amendments = _extract_amendment_records(chunk_text)

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
                            temporal_expressions=temporal_expressions,
                            resolved_entities=resolved_entities,
                            legal_effect=legal_effect,
                            amendments=amendments,
                        )
                    )

    if not records:
        msg = "No pipeline records were produced from the input files."
        raise ValueError(msg)

    if generate_embeddings:
        with pipeline_span("pipeline.embeddings", {"pipeline.record_count": len(records)}):
            logger.info("Generating embeddings for %d records ...", len(records))
            model, tokenizer = load_model()
            recorder.model_versions["embedding_model"] = _model_version_from_loaded(
                model,
                tokenizer,
            )
            for rec in records:
                rec.embeddings = generate_embedding(rec.raw_text, model, tokenizer)

    with pipeline_span("pipeline.storage.serialize", {"pipeline.record_count": len(records)}):
        result = serialize_to_parquet(records, output)
    recorder.finish(input_paths=input_files, output_path=result, record_count=len(records)).write_sidecar(result)
    logger.info("Legislation pipeline output written to %s", result)
    return result


def process_hansard(
    input_path: str | Path,
    output_path: str | Path,
    generate_embeddings: bool = True,
) -> Path:
    """Process Hansard speech documents through the full NLP pipeline."""
    output = _resolve_path(output_path)
    configure_tracing(
        service_name="nlp-policy-nz",
        trace_file=output.with_suffix(".traces.jsonl"),
    )
    with pipeline_span(
        "pipeline.process_hansard",
        {
            "pipeline.source": "hansard",
            "pipeline.generate_embeddings": generate_embeddings,
            "pipeline.output_path": str(output),
        },
    ):
        input_files = _collect_input_files(input_path)
        set_span_attribute("pipeline.input_file_count", len(input_files))
        result = _process_hansard_records(input_files, output, generate_embeddings)
        set_span_attribute("pipeline.output_path", str(result))
        return result


def _process_hansard_records(
    input_files: list[Path],
    output: Path,
    generate_embeddings: bool,
) -> Path:
    """Run the Hansard processing implementation for resolved inputs."""
    recorder = ProvenanceRecorder(
        pipeline_name="process_hansard",
        parameters={"generate_embeddings": generate_embeddings, "source": "hansard"},
    )
    logger.info("Found %d Hansard input file(s)", len(input_files))

    nlp = create_nlp_pipeline()
    if "citation_ruler" not in nlp.pipe_names:
        create_citation_ruler(nlp)
    _ensure_nz_entity_resolver(nlp)
    argument_detector = ArgumentDetector()
    stance_classifier = StanceClassifier()

    records: list[PipelineRecord] = []
    for idx, file_path in enumerate(input_files):
        with pipeline_span(
            "pipeline.hansard.file",
            {"file.path": str(file_path), "file.name": file_path.name},
        ):
            raw_text = file_path.read_text(encoding="utf-8")
            clean_text = normalize_text(raw_text)
            date_str = file_path.stem[:10] if len(file_path.stem) >= 10 else "unknown-date"
            chunks = chunk_hansard_speech(clean_text, nlp, date=date_str, speech_num=idx + 1)
            set_span_attribute("pipeline.chunk_count", len(chunks))

            for chunk in chunks:
                chunk_text: str = chunk["text"]
                with pipeline_span(
                    "pipeline.hansard.chunk",
                    {"chunk.doc_id": chunk["doc_id"], "chunk.length": len(chunk_text)},
                ):
                    te_reo_terms = _extract_te_reo_terms(chunk_text)
                    citations = _extract_citations(chunk_text, nlp)
                    temporal_expressions = [
                        annotation.to_dict()
                        for annotation in detect_temporal_expressions(chunk_text, nlp)
                    ]
                    context = _infer_entity_context(
                        chunk_text,
                        date=_valid_context_date(date_str),
                    )
                    resolved_entities = _resolve_named_entities(chunk_text, nlp, context=context)
                    voting_record = _extract_voting_record(chunk_text)
                    amendments = _extract_amendment_records(chunk_text)
                    arguments = [
                        argument.to_dict()
                        for argument in argument_detector.detect(chunk_text)
                    ]
                    stance = stance_classifier.classify(chunk_text).stance


                    records.append(
                        PipelineRecord(
                            doc_id=chunk["doc_id"],
                            corpus_source="hansard",
                            raw_text=chunk_text,
                            cleaned_tokens=[t.strip() for t in chunk_text.split() if t.strip()],
                            nz_act_citations=citations,
                            te_reo_terms=te_reo_terms,
                            embeddings=None,
                            temporal_expressions=temporal_expressions,
                            resolved_entities=resolved_entities,
                            voting_record=voting_record,
                            amendments=amendments,
                            arguments=arguments,
                            stance=stance,
                        )
                    )

    if not records:
        msg = "No pipeline records were produced from the input files."
        raise ValueError(msg)

    if generate_embeddings:
        with pipeline_span("pipeline.embeddings", {"pipeline.record_count": len(records)}):
            logger.info("Generating embeddings for %d records ...", len(records))
            model, tokenizer = load_model()
            recorder.model_versions["embedding_model"] = _model_version_from_loaded(
                model,
                tokenizer,
            )
            for rec in records:
                rec.embeddings = generate_embedding(rec.raw_text, model, tokenizer)

    with pipeline_span("pipeline.storage.serialize", {"pipeline.record_count": len(records)}):
        result = serialize_to_parquet(records, output)
    recorder.finish(input_paths=input_files, output_path=result, record_count=len(records)).write_sidecar(result)
    logger.info("Hansard pipeline output written to %s", result)
    return result


def search_similar(
    query: str,
    db_path: str = "./lancedb_data",
    top_k: int = 10,
) -> list[dict[str, Any]]:
    """Search the vector index for documents similar to *query*."""
    db = Path(db_path).resolve()
    if not db.is_dir():
        msg = f"LanceDB database directory not found: {db}"
        raise FileNotFoundError(msg)

    model, tokenizer = load_model()
    query_embedding = generate_embedding(query, model, tokenizer)

    index = LanceDBAdapter(uri=str(db))
    if not index.index_exists():
        msg = (
            f"No table found in LanceDB database at {db}. "
            "Run pipeline processing with embeddings enabled first."
        )
        raise RuntimeError(msg)

    return index.search(query_embedding, top_k=top_k)
