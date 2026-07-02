"""FastAPI inference server for nlp-policy-nz.

Provides a lightweight HTTP API for embedding generation, semantic search,
and full pipeline processing of New Zealand legislation and Hansard corpora.
All heavy dependencies (torch, transformers, lancedb) are imported lazily
so the server starts up quickly.
"""

from __future__ import annotations

import asyncio
import json
import time
from collections import defaultdict, deque
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel, Field
from starlette.middleware.base import RequestResponseEndpoint

from nlp_policy_nz.api.auth import (
    APIKeyStore,
    AuthContext,
    build_audit_logger,
    emit_audit_event,
    extract_api_key,
    load_security_settings,
    required_scope_for_path,
    verify_api_key,
)
from nlp_policy_nz.api.errors import (
    ProblemCode,
    ProblemDetail,
    ProblemError,
    problem_response,
    register_problem_handlers,
)
from nlp_policy_nz.api.metrics import (
    decrement_active_requests,
    increment_active_requests,
    record_request,
    render_metrics,
    reset_metrics,
    set_model_loaded,
)
from nlp_policy_nz.api.observability import (
    config_hash,
    current_request_id,
    generate_request_id,
    get_structured_logger,
    reset_request_id,
    set_request_id,
)
from nlp_policy_nz.config import load_feature_flags, load_runtime_settings

logger = get_structured_logger(__name__)

_settings = load_runtime_settings()
_feature_flags = load_feature_flags()
_security_settings = load_security_settings()
_api_key_store = APIKeyStore.load(_security_settings.api_keys_path)
_audit_logger = build_audit_logger(_security_settings.audit_log_path)
_version_manifest_path = Path(__file__).resolve().parents[3] / "VERSION.json"
_embedding_load_failed = False


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
_PUBLIC_PATHS = {
    "/health",
    "/version",
    "/v1/health",
    "/v2/health",
    "/v1/version",
    "/v2/version",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/startup",
    "/ready",
    "/live",
    "/metrics",
}

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


class ProbeResponse(BaseModel):
    """Health probe response body."""

    status: str
    request_id: str | None = None
    model_loaded: bool | None = None
    db_connected: bool | None = None
    degraded_embeddings: bool | None = None


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
register_problem_handlers(app)

cors_origins = ["*"] if "*" in _settings.cors_origins else list(_settings.cors_origins)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
reset_metrics()
set_model_loaded(False)
app.state.model_loaded = False
app.state.degraded_embeddings = False
app.state.startup_complete = False


def _custom_openapi() -> dict[str, Any]:
    """Inject RFC 7807 schemas and default problem responses into OpenAPI."""
    if app.openapi_schema:
        return app.openapi_schema
    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    components = schema.setdefault("components", {})
    schemas = components.setdefault("schemas", {})
    schemas["ProblemError"] = ProblemError.model_json_schema(ref_template="#/components/schemas/{model}")
    schemas["ProblemDetail"] = ProblemDetail.model_json_schema(ref_template="#/components/schemas/{model}")
    for path_item in schema.get("paths", {}).values():
        for operation in path_item.values():
            if not isinstance(operation, dict):
                continue
            responses = operation.setdefault("responses", {})
            for status_code in ("400", "401", "403", "404", "413", "422", "429", "500", "503"):
                responses.setdefault(
                    status_code,
                    {
                        "description": "RFC 7807 problem detail response",
                        "content": {
                            "application/problem+json": {
                                "schema": {"$ref": "#/components/schemas/ProblemDetail"}
                            }
                        },
                    },
                )
    app.openapi_schema = schema
    return schema


app.openapi = _custom_openapi

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
    model_loaded = _embedding_generator is not None and not _embedding_load_failed
    db_connected = Path(_settings.db_path).exists()
    pipeline_status = "ok" if db_connected and model_loaded else "degraded"
    model_name = _embedding_generator.model_name if model_loaded else ""
    app.state.model_loaded = model_loaded
    app.state.degraded_embeddings = _feature_flags.degraded_embeddings or not model_loaded
    set_model_loaded(model_loaded)
    return HealthResponse(
        status="ok",
        pipeline_status=pipeline_status,
        db_connected=db_connected,
        model_loaded=model_loaded,
        model_name=model_name,
        version=_version_manifest["version"],
        last_run_timestamp=app.state.last_run_timestamp,
    )


def _is_public_path(path: str) -> bool:
    normalized = path.rstrip("/") or "/"
    return normalized in _PUBLIC_PATHS


def _client_ip(request: Request) -> str:
    if request.client and request.client.host:
        return request.client.host
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return "unknown"


def _rate_limit_key(request: Request, auth_context: AuthContext | None) -> str:
    client_host = _client_ip(request)
    if auth_context is not None:
        return f"{auth_context.key_hash}:{request.url.path}"
    return f"{client_host}:{request.url.path}"


def _check_rate_limit(request: Request, auth_context: AuthContext | None) -> Response | None:
    if _settings.rate_limit_per_minute <= 0:
        return None
    if _is_public_path(request.url.path):
        return None
    key = _rate_limit_key(request, auth_context)
    history = _rate_limit_history[key]
    now = time.monotonic()
    window = 60.0
    while history and now - history[0] > window:
        history.popleft()
    if len(history) >= _settings.rate_limit_per_minute:
        retry_after = max(1, int(window - (now - history[0]))) if history else 60
        response = problem_response(
            status_code=429,
            code=ProblemCode.RATE_LIMITED,
            detail="Rate limit exceeded.",
            instance=request.url.path,
        )
        response.headers["X-RateLimit-Limit"] = str(_settings.rate_limit_per_minute)
        response.headers["X-RateLimit-Remaining"] = "0"
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + retry_after)
        response.headers["Retry-After"] = str(retry_after)
        return response
    history.append(now)
    return None


@app.middleware("http")
async def observability_middleware(
    request: Request,
    call_next: RequestResponseEndpoint,
) -> Response:
    """Apply request IDs, auth, rate limiting, metrics, and audit logging."""
    request_id = generate_request_id()
    token = set_request_id(request_id)
    increment_active_requests()
    started = time.perf_counter()
    path = request.url.path
    api_version = _request_api_version(path)
    auth_context: AuthContext | None = None
    response: Response | None = None
    scope = required_scope_for_path(path)
    body_limit = _security_settings.max_body_bytes
    content_length = request.headers.get("content-length")
    degraded = False
    status_code = 500

    try:
        if request.method in {"POST", "PUT", "PATCH"} and content_length:
            try:
                if int(content_length) > body_limit:
                    response = problem_response(
                        status_code=413,
                        code=ProblemCode.PIPELINE_FAILURE,
                        detail="Request body too large.",
                        instance=path,
                    )
            except ValueError:
                response = problem_response(
                    status_code=400,
                    code=ProblemCode.PIPELINE_FAILURE,
                    detail="Invalid Content-Length header.",
                    instance=path,
                )

        if response is None and _security_settings.auth_required and not _is_public_path(path):
            secret = extract_api_key(dict(request.headers))
            if secret is None:
                response = problem_response(
                    status_code=401,
                    code=ProblemCode.AUTH_INVALID_KEY,
                    detail="API key required.",
                    instance=path,
                )
            else:
                required_scope = scope or "read"
                try:
                    auth_context = verify_api_key(_api_key_store, secret, required_scope)
                except PermissionError as exc:
                    message = str(exc).lower()
                    response = problem_response(
                        status_code=403 if "scope" in message else 401,
                        code=ProblemCode.AUTH_INSUFFICIENT_SCOPE if "scope" in message else ProblemCode.AUTH_INVALID_KEY,
                        detail=str(exc),
                        instance=path,
                    )

        if response is None:
            limited = _check_rate_limit(request, auth_context)
            if limited is not None:
                response = limited

        if response is None:
            try:
                response = await call_next(request)
            except Exception as exc:
                logger.exception(
                    "Request processing failed",
                    extra={
                        "request_id": request_id,
                        "endpoint": path,
                        "method": request.method,
                    },
                )
                response = problem_response(
                    status_code=500,
                    code=ProblemCode.PIPELINE_FAILURE,
                    detail=str(exc) or "Internal server error.",
                    instance=path,
                )

        status_code = response.status_code
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers.setdefault("Permissions-Policy", "geolocation=(), microphone=(), camera=()")
        if request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        _apply_version_headers(response, api_version)
        if auth_context is not None:
            remaining = max(
                0,
                _settings.rate_limit_per_minute
                - len(_rate_limit_history[_rate_limit_key(request, auth_context)]),
            )
            response.headers["X-RateLimit-Limit"] = str(_settings.rate_limit_per_minute)
            response.headers["X-RateLimit-Remaining"] = str(remaining)
            response.headers["X-RateLimit-Reset"] = str(int(time.time()) + 60)
        if _feature_flags.degraded_embeddings or _embedding_load_failed:
            degraded = True
            response.headers.setdefault("X-Degraded", "true")
        duration = time.perf_counter() - started
        record_request(
            method=request.method,
            endpoint=path,
            status=status_code,
            scope=(scope or "public"),
            duration_seconds=duration,
        )
        emit_audit_event(
            _audit_logger,
            {
                "timestamp": datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "key_hash": auth_context.key_hash if auth_context else None,
                "key_id": auth_context.key_id if auth_context else None,
                "endpoint": path,
                "method": request.method,
                "status": status_code,
                "duration_seconds": round(duration, 4),
                "client_ip": _client_ip(request),
                "authorized": auth_context is not None,
                "request_id": request_id,
                "degraded": degraded,
            },
        )
        logger.info(
            "request complete",
            extra={
                "request_id": request_id,
                "endpoint": path,
                "method": request.method,
                "status": status_code,
                "duration_ms": round(duration * 1000, 2),
                "scope": scope or "public",
                "degraded": degraded,
            },
        )
        return response
    finally:
        decrement_active_requests()
        reset_request_id(token)


@app.on_event("shutdown")
async def _shutdown_event() -> None:
    """Record shutdown state for production diagnostics."""
    app.state.shutdown_completed = True
    logger.info(
        "shutdown complete",
        extra={
            "version": _version_manifest["version"],
            "config_hash": config_hash(
                {
                    "runtime": _settings.__dict__,
                    "feature_flags": _feature_flags.__dict__,
                    "security": {
                        "auth_required": _security_settings.auth_required,
                        "api_keys_path": str(_security_settings.api_keys_path),
                        "audit_log_path": str(_security_settings.audit_log_path),
                        "max_body_bytes": _security_settings.max_body_bytes,
                    },
                }
            ),
        },
    )


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
    global _embedding_generator, _embedding_load_failed
    if _embedding_generator is None:
        logger.info("Lazy-loading EmbeddingGenerator (first request) ...")
        from nlp_policy_nz.semantic.embeddings import EmbeddingGenerator

        try:
            _embedding_generator = EmbeddingGenerator()
            _embedding_generator.load()
            _embedding_load_failed = False
            app.state.model_loaded = True
            set_model_loaded(True)
            logger.info(
                "EmbeddingGenerator loaded (model=%s)",
                _embedding_generator.model_name,
            )
        except Exception as exc:  # noqa: BLE001
            _embedding_generator = None
            _embedding_load_failed = True
            app.state.model_loaded = False
            app.state.degraded_embeddings = True
            set_model_loaded(False)
            logger.exception(
                "Embedding generator failed to load",
                extra={"error_code": ProblemCode.MODEL_NOT_LOADED.value},
            )
            raise RuntimeError("MODEL_NOT_LOADED") from exc
    return _embedding_generator


# --- Endpoints ---


@app.get("/health", response_model=HealthResponse, summary="Health check")
@app.get("/v1/health", response_model=HealthResponse, summary="Health check")
@app.get("/v2/health", response_model=HealthResponse, summary="Health check")
async def health(request: Request, response: Response) -> HealthResponse:
    """Return API health and lazy model-load state."""
    _apply_version_headers(response, _request_api_version(request.url.path))
    return _build_health_response()


@app.get("/startup", response_model=ProbeResponse, summary="Startup probe")
async def startup_probe(response: Response) -> ProbeResponse:
    """Report whether the model has finished startup initialization."""
    response.headers["X-Request-ID"] = current_request_id() or generate_request_id()
    return ProbeResponse(
        status="ok" if _embedding_generator is not None or _embedding_load_failed else "starting",
        model_loaded=_embedding_generator is not None and not _embedding_load_failed,
        degraded_embeddings=_feature_flags.degraded_embeddings or _embedding_load_failed,
    )


@app.get("/ready", response_model=ProbeResponse, summary="Readiness probe")
async def readiness_probe(response: Response) -> ProbeResponse:
    """Report whether the pipeline and database are ready to serve."""
    db_connected = Path(_settings.db_path).exists()
    ready = db_connected and not _feature_flags.kill_switch
    response.headers["X-Request-ID"] = current_request_id() or generate_request_id()
    return ProbeResponse(
        status="ready" if ready else "degraded",
        db_connected=db_connected,
        model_loaded=_embedding_generator is not None and not _embedding_load_failed,
        degraded_embeddings=_feature_flags.degraded_embeddings or _embedding_load_failed,
    )


@app.get("/live", response_model=ProbeResponse, summary="Liveness probe")
async def liveness_probe(response: Response) -> ProbeResponse:
    """Report basic process liveness."""
    response.headers["X-Request-ID"] = current_request_id() or generate_request_id()
    return ProbeResponse(status="alive")


@app.get("/version", response_model=VersionResponse, summary="Version metadata")
@app.get("/v1/version", response_model=VersionResponse, summary="Version metadata")
@app.get("/v2/version", response_model=VersionResponse, summary="Version metadata")
async def version(request: Request, response: Response) -> VersionResponse:
    """Return the canonical release version metadata."""
    _apply_version_headers(response, _request_api_version(request.url.path))
    return VersionResponse(**_version_manifest)


@app.get("/metrics", summary="Prometheus metrics", include_in_schema=False)
async def metrics() -> Response:
    """Expose Prometheus-compatible metrics."""
    return Response(content=render_metrics(), media_type="text/plain; version=0.0.4; charset=utf-8")


@app.on_event("startup")
async def _startup_event() -> None:
    """Record startup state and log structured startup diagnostics."""
    app.state.startup_complete = True
    diagnostics = {
        "version": _version_manifest["version"],
        "config_hash": config_hash(
            {
                "runtime": _settings.__dict__,
                "feature_flags": _feature_flags.__dict__,
                "security": {
                    "auth_required": _security_settings.auth_required,
                    "api_keys_path": str(_security_settings.api_keys_path),
                    "audit_log_path": str(_security_settings.audit_log_path),
                    "max_body_bytes": _security_settings.max_body_bytes,
                },
            }
        ),
    }
    logger.info("startup complete", extra=diagnostics)


@app.post("/embed", response_model=EmbedResponse, summary="Generate embeddings")
@app.post("/v1/embed", response_model=EmbedResponse, summary="Generate embeddings")
@app.post("/v2/embed", response_model=EmbedResponse, summary="Generate embeddings")
async def embed(request: Request, payload: EmbedRequest, response: Response) -> EmbedResponse:
    """Generate embeddings for one or more input texts."""
    api_version = _request_api_version(request.url.path)
    _apply_version_headers(response, api_version)
    if (
        not _feature_flags.embed_enabled
        or _feature_flags.kill_switch
        or _feature_flags.degraded_embeddings
        or _embedding_load_failed
    ):
        raise HTTPException(status_code=503, detail="MODEL_NOT_LOADED")
    t0 = time.perf_counter()
    try:
        gen = await asyncio.to_thread(_get_embedding_generator)
        results = await asyncio.to_thread(gen.embed_batch, payload.texts)
    except Exception as exc:
        if "MODEL_NOT_LOADED" in str(exc):
            raise HTTPException(status_code=503, detail="MODEL_NOT_LOADED") from exc
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
    degraded = _feature_flags.degraded_embeddings or _embedding_load_failed
    if degraded:
        response.headers["X-Degraded"] = "true"
        results = _keyword_only_search(payload.query, payload.top_k, payload.db_path)
        elapsed = time.perf_counter() - t0
        return SearchResponse(
            results=results,
            query=payload.query,
            count=len(results),
            elapsed_seconds=round(elapsed, 4),
        )
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
    if _feature_flags.degraded_embeddings or not _feature_flags.embed_enabled or _embedding_load_failed:
        effective_payload = payload.model_copy(update={"generate_embeddings": False})
    input_path_candidate = Path(effective_payload.input)
    if input_path_candidate.is_file():
        return await _run_file_pipeline(effective_payload, input_path_candidate, t0)
    return await _run_inline_pipeline(effective_payload, t0)


def _keyword_only_search(query: str, top_k: int, db_path: str) -> list[dict[str, Any]]:
    """Return a deterministic keyword-only degraded search result set."""
    keywords = [term for term in query.split() if term]
    return [
        {
            "doc_id": "degraded-keyword-fallback",
            "text": query,
            "corpus_source": "keyword-only",
            "keywords": keywords[:top_k],
            "db_path": db_path,
            "score": 1.0,
        }
    ]


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
