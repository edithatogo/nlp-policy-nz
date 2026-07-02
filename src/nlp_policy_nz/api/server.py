"""FastAPI inference server for nlp-policy-nz.

Provides a lightweight HTTP API for embedding generation, semantic search,
and full pipeline processing of New Zealand legislation and Hansard corpora.
All heavy dependencies (torch, transformers, lancedb) are imported lazily
so the server starts up quickly.
"""

from __future__ import annotations

import asyncio
import json
import logging
import time
from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from starlette.middleware.base import RequestResponseEndpoint

from nlp_policy_nz.config import load_feature_flags, load_runtime_settings

logger = logging.getLogger(__name__)

_settings = load_runtime_settings()
_feature_flags = load_feature_flags()
_version_manifest_path = Path(__file__).resolve().parents[3] / "VERSION.json"


def _load_version_manifest() -> dict[str, str]:
    if _version_manifest_path.is_file():
        try:
            return json.loads(_version_manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logger.warning("VERSION.json is invalid; falling back to default version")
    return {
        "version": "0.1.0",
        "build_timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "commit_sha": "unknown",
        "dataset_revision": "0",
    }


_version_manifest = _load_version_manifest()
_rate_limit_history: dict[str, deque[float]] = defaultdict(deque)

# --- Models ---


class EmbedRequest(BaseModel):
    """Request body for embedding generation."""

    texts: list[str] = Field(
        ...,
        min_length=1,
        description="One or more texts to generate embeddings for.",
    )


class EmbedResponse(BaseModel):
    """Embedding generation response body."""

    embeddings: list[list[float]]
    model_name: str
    dimension: int
    count: int
    elapsed_seconds: float


class SearchRequest(BaseModel):
    """Request body for semantic search."""

    query: str = Field(..., min_length=1, description="Natural-language search query.")
    top_k: int = Field(default=5, ge=1, le=100, description="Number of results to return.")
    db_path: str = Field(
        default="./lancedb_data", description="Path to the LanceDB database directory."
    )


class SearchResponse(BaseModel):
    """Semantic search response body."""

    results: list[dict[str, Any]]
    query: str
    count: int
    elapsed_seconds: float


class ProcessRequest(BaseModel):
    """Request body for inline or file pipeline processing."""

    input: str = Field(..., min_length=1, description="Input text or file path to process.")
    source: str = Field(
        default="legislation",
        pattern=r"^(legislation|hansard)$",
        description="Corpus source type.",
    )
    generate_embeddings: bool = Field(default=False, description="Whether to generate embeddings.")


class ProcessResponse(BaseModel):
    """Pipeline processing response body."""

    records: list[dict[str, Any]]
    source: str
    count: int
    output_path: str | None = None
    elapsed_seconds: float


class HealthResponse(BaseModel):
    """Health check response body."""

    status: str
    pipeline_status: str
    db_connected: bool
    model_loaded: bool
    model_name: str
    version: str
    last_run_timestamp: str | None = None


class VersionResponse(BaseModel):
    """Version metadata response body."""

    version: str
    build_timestamp: str
    commit_sha: str
    dataset_revision: str


# --- FastAPI app ---

app = FastAPI(
    title="nlp-policy-nz Inference API",
    description=(
        "HTTP API for the NLP Policy NZ pipeline. Provides embedding "
        "generation, semantic search, and full pipeline processing."
    ),
    version=_version_manifest["version"],
    docs_url="/docs",
    redoc_url="/redoc",
)

cors_origins = ["*"] if "*" in _settings.cors_origins else list(_settings.cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Lazy-loaded resources ---

_embedding_generator: object | None = None


app.state.last_run_timestamp = _settings.last_run_timestamp


def _request_api_version(path: str) -> str:
    if path.startswith("/v1/"):
        return "v1"
    if path.startswith("/v2/"):
        return "v2"
    return "root"


def _apply_version_headers(response: Response, api_version: str) -> None:
    response.headers["X-API-Version"] = _version_manifest["version"]
    if api_version == "v1":
        response.headers["Deprecation"] = "true"
        sunset = datetime.now(UTC) + timedelta(days=_settings.sunset_days_v1)
        response.headers["Sunset"] = sunset.strftime("%a, %d %b %Y %H:%M:%S GMT")


def _build_health_response() -> HealthResponse:
    model_loaded = _embedding_generator is not None
    db_connected = Path(_settings.db_path).exists()
    pipeline_status = "ok" if db_connected and model_loaded else "degraded"
    model_name = _embedding_generator.model_name if model_loaded else ""
    return HealthResponse(
        status="ok",
        pipeline_status=pipeline_status,
        db_connected=db_connected,
        model_loaded=model_loaded,
        model_name=model_name,
        version=_version_manifest["version"],
        last_run_timestamp=app.state.last_run_timestamp,
    )


def _rate_limit_key(request: Request) -> str:
    client_host = request.client.host if request.client else "unknown"
    return f"{client_host}:{request.url.path}"


def _check_rate_limit(request: Request) -> Response | None:
    if _settings.rate_limit_per_minute <= 0:
        return None
    if request.url.path in {"/health", "/v1/health", "/v2/health", "/version", "/v1/version", "/v2/version", "/openapi.json", "/docs", "/redoc"}:
        return None
    key = _rate_limit_key(request)
    history = _rate_limit_history[key]
    now = time.monotonic()
    window = 60.0
    while history and now - history[0] > window:
        history.popleft()
    if len(history) >= _settings.rate_limit_per_minute:
        retry_after = max(1, int(window - (now - history[0]))) if history else 60
        response = JSONResponse(
            status_code=429,
            content={"detail": "Rate limit exceeded."},
        )
        response.headers["X-RateLimit-Limit"] = str(_settings.rate_limit_per_minute)
        response.headers["X-RateLimit-Remaining"] = "0"
        response.headers["Retry-After"] = str(retry_after)
        return response
    history.append(now)
    return None


@app.middleware("http")
async def rate_limit_middleware(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    """Apply a light token-bucket limiter to production endpoints."""
    limited = _check_rate_limit(request)
    if limited is not None:
        return limited
    return await call_next(request)


@app.on_event("shutdown")
async def _shutdown_event() -> None:
    """Record shutdown state for production diagnostics."""
    app.state.shutdown_completed = True


def search_similar(
    query: str,
    db_path: str = "./lancedb_data",
    top_k: int = 10,
) -> list[dict[str, Any]]:
    """Lazy proxy for vector search.

    Kept as a module attribute so tests and callers can patch the endpoint
    boundary without importing semantic dependencies at server import time.
    """
    from nlp_policy_nz.pipeline_api import search_similar as _search_similar

    return _search_similar(query=query, db_path=db_path, top_k=top_k)


def normalize_text(text: str) -> str:
    """Lazy proxy for guard text normalization."""
    from nlp_policy_nz.guard import normalize_text as _normalize_text

    return _normalize_text(text)


def LanguageIdentifier() -> object:  # noqa: N802
    """Lazy proxy for the language identifier constructor."""
    from nlp_policy_nz.guard import LanguageIdentifier as _LanguageIdentifier

    return _LanguageIdentifier()


def create_nlp_pipeline() -> object:
    """Lazy proxy for the syntactic pipeline factory."""
    from nlp_policy_nz.syntactic import create_nlp_pipeline as _create_nlp_pipeline

    return _create_nlp_pipeline()


def create_citation_ruler(nlp: object) -> object:
    """Lazy proxy for the syntactic citation ruler factory."""
    from nlp_policy_nz.syntactic import create_citation_ruler as _create_citation_ruler

    return _create_citation_ruler(nlp)


def _get_embedding_generator() -> object:
    """Return the lazy singleton embedding generator."""
    global _embedding_generator
    if _embedding_generator is None:
        logger.info("Lazy-loading EmbeddingGenerator (first request) ...")
        from nlp_policy_nz.semantic.embeddings import EmbeddingGenerator

        _embedding_generator = EmbeddingGenerator()
        _embedding_generator.load()
        logger.info(
            "EmbeddingGenerator loaded (model=%s)",
            _embedding_generator.model_name,
        )
    return _embedding_generator


# --- Endpoints ---


@app.get("/health", response_model=HealthResponse, summary="Health check")
@app.get("/v1/health", response_model=HealthResponse, summary="Health check")
@app.get("/v2/health", response_model=HealthResponse, summary="Health check")
async def health(request: Request, response: Response) -> HealthResponse:
    """Return API health and lazy model-load state."""
    _apply_version_headers(response, _request_api_version(request.url.path))
    return _build_health_response()


@app.get("/version", response_model=VersionResponse, summary="Version metadata")
@app.get("/v1/version", response_model=VersionResponse, summary="Version metadata")
@app.get("/v2/version", response_model=VersionResponse, summary="Version metadata")
async def version(request: Request, response: Response) -> VersionResponse:
    """Return the canonical release version metadata."""
    _apply_version_headers(response, _request_api_version(request.url.path))
    return VersionResponse(**_version_manifest)


@app.post("/embed", response_model=EmbedResponse, summary="Generate embeddings")
@app.post("/v1/embed", response_model=EmbedResponse, summary="Generate embeddings")
@app.post("/v2/embed", response_model=EmbedResponse, summary="Generate embeddings")
async def embed(request: Request, payload: EmbedRequest, response: Response) -> EmbedResponse:
    """Generate embeddings for one or more input texts."""
    api_version = _request_api_version(request.url.path)
    _apply_version_headers(response, api_version)
    if not _feature_flags.embed_enabled or _feature_flags.kill_switch:
        raise HTTPException(status_code=503, detail="Embedding generation is disabled by feature flag.")
    t0 = time.perf_counter()
    try:
        gen = await asyncio.to_thread(_get_embedding_generator)
        results = await asyncio.to_thread(gen.embed_batch, payload.texts)
    except Exception as exc:
        logger.exception("Embedding request failed")
        raise HTTPException(status_code=500, detail=f"Embedding failed: {exc}") from exc
    elapsed = time.perf_counter() - t0
    return EmbedResponse(
        embeddings=[result.embedding for result in results],
        model_name=gen.model_name,
        dimension=results[0].dimension if results else 0,
        count=len(results),
        elapsed_seconds=round(elapsed, 4),
    )


@app.post("/search", response_model=SearchResponse, summary="Semantic search")
@app.post("/v1/search", response_model=SearchResponse, summary="Semantic search")
@app.post("/v2/search", response_model=SearchResponse, summary="Semantic search")
async def search(request: Request, payload: SearchRequest, response: Response) -> SearchResponse:
    """Run semantic vector search over the configured index."""
    _apply_version_headers(response, _request_api_version(request.url.path))
    if not _feature_flags.search_enabled or _feature_flags.kill_switch:
        raise HTTPException(status_code=503, detail="Search is disabled by feature flag.")
    t0 = time.perf_counter()
    try:
        results = await asyncio.to_thread(
            search_similar,
            query=payload.query,
            db_path=payload.db_path,
            top_k=payload.top_k,
        )
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=f"Vector database not found: {exc}") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=404, detail=f"Vector index error: {exc}") from exc
    except Exception as exc:
        logger.exception("Search request failed")
        raise HTTPException(status_code=500, detail=f"Search failed: {exc}") from exc
    elapsed = time.perf_counter() - t0
    return SearchResponse(
        results=results,
        query=payload.query,
        count=len(results),
        elapsed_seconds=round(elapsed, 4),
    )


@app.post("/process", response_model=ProcessResponse, summary="Run full pipeline")
@app.post("/v1/process", response_model=ProcessResponse, summary="Run full pipeline")
@app.post("/v2/process", response_model=ProcessResponse, summary="Run full pipeline")
async def process(request: Request, payload: ProcessRequest, response: Response) -> ProcessResponse:
    """Run pipeline processing against a path or inline text."""
    _apply_version_headers(response, _request_api_version(request.url.path))
    if not _feature_flags.process_enabled or _feature_flags.kill_switch:
        raise HTTPException(status_code=503, detail="Processing is disabled by feature flag.")
    t0 = time.perf_counter()
    effective_payload = payload
    if _feature_flags.degraded_embeddings or not _feature_flags.embed_enabled:
        effective_payload = payload.model_copy(update={"generate_embeddings": False})
    input_path_candidate = Path(effective_payload.input)
    if input_path_candidate.is_file():
        return await _run_file_pipeline(effective_payload, input_path_candidate, t0)
    return await _run_inline_pipeline(effective_payload, t0)


async def _run_file_pipeline(
    request: ProcessRequest,
    input_path: Path,
    t0: float,
) -> ProcessResponse:
    """Run the full file-backed pipeline and return serialized records."""
    from nlp_policy_nz.pipeline_api import process_hansard, process_legislation
    from nlp_policy_nz.storage.serialization import load_from_parquet

    runner = process_legislation if request.source == "legislation" else process_hansard
    output_dir = Path.cwd() / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{input_path.stem}_{request.source}.parquet"
    try:
        result_path = await asyncio.to_thread(
            runner,
            input_path=str(input_path),
            output_path=str(output_path),
            generate_embeddings=request.generate_embeddings,
        )
    except Exception as exc:
        logger.exception("Pipeline processing failed")
        raise HTTPException(status_code=500, detail=f"Pipeline processing failed: {exc}") from exc
    elapsed = time.perf_counter() - t0
    try:
        records = await asyncio.to_thread(load_from_parquet, result_path)
    except Exception:
        records = []
    return ProcessResponse(
        records=[_record_to_dict(record) for record in records],
        source=request.source,
        count=len(records),
        output_path=str(result_path),
        elapsed_seconds=round(elapsed, 4),
    )


async def _run_inline_pipeline(request: ProcessRequest, t0: float) -> ProcessResponse:
    """Run the lightweight inline pipeline for a single request body."""
    from dataclasses import asdict

    from nlp_policy_nz.discourse import ArgumentDetector, StanceClassifier
    from nlp_policy_nz.legal import detect_temporal_expressions
    from nlp_policy_nz.parliament.amendments import amendments_to_dicts, parse_amendments
    from nlp_policy_nz.parliament.voting import parse_division
    from nlp_policy_nz.semantic import generate_embedding
    from nlp_policy_nz.semantic.model_loader import load_model
    from nlp_policy_nz.storage.serialization import PipelineRecord

    nlp = create_nlp_pipeline()
    if "citation_ruler" not in nlp.pipe_names and "maori_guard" in nlp.pipe_names:
        create_citation_ruler(nlp)
    clean_text = normalize_text(request.input)
    doc = nlp(clean_text)
    identifier = LanguageIdentifier()
    te_reo_segments = identifier.detect_code_switching(clean_text)
    te_reo_terms = [seg for lang, seg in te_reo_segments if lang == "mi"]
    citations = [ent.text for ent in doc.ents if ent.label_ in {"NZ_ACT", "NZ_SECTION", "CITATION"}]
    temporal_expressions = [
        annotation.to_dict() for annotation in detect_temporal_expressions(clean_text, nlp)
    ]
    division = parse_division(clean_text) if request.source == "hansard" else None
    voting_record = asdict(division) if division is not None else None
    if voting_record is not None:
        if not voting_record["votes"]:
            voting_record["votes"] = None
        if not voting_record["party_votes"]:
            voting_record["party_votes"] = None
    amendments = amendments_to_dicts(parse_amendments(clean_text))
    arguments = []
    stance = None
    argument_label_source = None
    stance_label_source = None
    if request.source == "hansard":
        arguments = [argument.to_dict() for argument in ArgumentDetector().detect(clean_text)]
        stance = StanceClassifier().classify(clean_text).stance
        argument_label_source = "predicted"
        stance_label_source = "predicted"
    record = PipelineRecord(
        doc_id="inline-001",
        corpus_source=request.source,
        raw_text=clean_text,
        cleaned_tokens=[token.strip() for token in clean_text.split() if token.strip()],
        nz_act_citations=citations,
        te_reo_terms=te_reo_terms,
        embeddings=None,
        temporal_expressions=temporal_expressions,
        voting_record=voting_record,
        amendments=amendments,
        arguments=arguments,
        argument_label_source=argument_label_source,
        stance=stance,
        stance_label_source=stance_label_source,
    )
    if request.generate_embeddings:
        model, tokenizer = load_model()
        record.embeddings = generate_embedding(record.raw_text, model, tokenizer)
    elapsed = time.perf_counter() - t0
    return ProcessResponse(
        records=[_record_to_dict(record)],
        source=request.source,
        count=1,
        output_path=None,
        elapsed_seconds=round(elapsed, 4),
    )


# --- Helpers ---


def _record_to_dict(record: object) -> dict[str, object]:
    """Convert a PipelineRecord-like object to an API response dictionary."""
    return {
        "doc_id": record.doc_id,
        "corpus_source": record.corpus_source,
        "raw_text": record.raw_text,
        "cleaned_tokens": record.cleaned_tokens,
        "nz_act_citations": record.nz_act_citations,
        "te_reo_terms": record.te_reo_terms,
        "temporal_expressions": getattr(record, "temporal_expressions", []),
        "voting_record": getattr(record, "voting_record", None),
        "amendments": getattr(record, "amendments", []),
        "arguments": getattr(record, "arguments", []),
        "argument_label_source": getattr(record, "argument_label_source", None),
        "stance": getattr(record, "stance", None),
        "stance_label_source": getattr(record, "stance_label_source", None),
        "embeddings": record.embeddings,
    }


# --- CLI entry point ---

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        workers=_settings.uvicorn_workers,
    )
