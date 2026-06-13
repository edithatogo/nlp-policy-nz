"""FastAPI inference server for nlp-policy-nz.

Provides a lightweight HTTP API for embedding generation, semantic search,
and full pipeline processing of New Zealand legislation and Hansard corpora.
All heavy dependencies (torch, transformers, lancedb) are imported lazily
so the server starts up quickly.
"""

from __future__ import annotations

import logging
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

# --- Models ---

class EmbedRequest(BaseModel):
    texts: list[str] = Field(..., min_length=1,
        description="One or more texts to generate embeddings for.")

class EmbedResponse(BaseModel):
    embeddings: list[list[float]]
    model_name: str
    dimension: int
    count: int
    elapsed_seconds: float

class SearchRequest(BaseModel):
    query: str = Field(..., min_length=1,
        description="Natural-language search query.")
    top_k: int = Field(default=5, ge=1, le=100,
        description="Number of results to return.")
    db_path: str = Field(default="./lancedb_data",
        description="Path to the LanceDB database directory.")

class SearchResponse(BaseModel):
    results: list[dict[str, Any]]
    query: str
    count: int
    elapsed_seconds: float

class ProcessRequest(BaseModel):
    input: str = Field(..., min_length=1,
        description="Input text or file path to process.")
    source: str = Field(default="legislation",
        pattern=r"^(legislation|hansard)$",
        description="Corpus source type.")
    generate_embeddings: bool = Field(default=False,
        description="Whether to generate embeddings.")

class ProcessResponse(BaseModel):
    records: list[dict[str, Any]]
    source: str
    count: int
    output_path: str | None = None
    elapsed_seconds: float

class HealthResponse(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    version: str = "0.1.0"

# --- FastAPI app ---

app = FastAPI(
    title="nlp-policy-nz Inference API",
    description=("HTTP API for the NLP Policy NZ pipeline. Provides embedding "
                 "generation, semantic search, and full pipeline processing."),
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# --- Lazy-loaded resources ---

_embedding_generator: Any = None

def _get_embedding_generator() -> Any:
    global _embedding_generator
    if _embedding_generator is None:
        logger.info("Lazy-loading EmbeddingGenerator (first request) ...")
        from nlp_policy_nz.semantic.embeddings import EmbeddingGenerator
        _embedding_generator = EmbeddingGenerator()
        _embedding_generator.load()
        logger.info("EmbeddingGenerator loaded (model=%s)",
                    _embedding_generator.model_name)
    return _embedding_generator

# --- Endpoints ---

@app.get("/health", response_model=HealthResponse, summary="Health check")
async def health() -> HealthResponse:
    model_loaded = _embedding_generator is not None
    model_name = _embedding_generator.model_name if model_loaded else ""
    return HealthResponse(status="ok", model_loaded=model_loaded,
                          model_name=model_name)

@app.post("/embed", response_model=EmbedResponse, summary="Generate embeddings")
async def embed(request: EmbedRequest) -> EmbedResponse:
    t0 = time.perf_counter()
    try:
        gen = _get_embedding_generator()
        results = gen.embed_batch(request.texts)
    except Exception as exc:
        logger.exception("Embedding request failed")
        raise HTTPException(status_code=500,
                            detail=f"Embedding failed: {exc}") from exc
    elapsed = time.perf_counter() - t0
    return EmbedResponse(
        embeddings=[r.embedding for r in results],
        model_name=gen.model_name,
        dimension=results[0].dimension if results else 0,
        count=len(results),
        elapsed_seconds=round(elapsed, 4),
    )

@app.post("/search", response_model=SearchResponse, summary="Semantic search")
async def search(request: SearchRequest) -> SearchResponse:
    t0 = time.perf_counter()
    try:
        from nlp_policy_nz.api import search_similar
    except Exception as exc:
        raise HTTPException(status_code=500,
            detail=f"Failed to import search module: {exc}") from exc
    try:
        results = search_similar(query=request.query,
            db_path=request.db_path, top_k=request.top_k)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404,
            detail=f"Vector database not found: {exc}") from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=404,
            detail=f"Vector index error: {exc}") from exc
    except Exception as exc:
        logger.exception("Search request failed")
        raise HTTPException(status_code=500,
            detail=f"Search failed: {exc}") from exc
    elapsed = time.perf_counter() - t0
    return SearchResponse(results=results, query=request.query,
        count=len(results), elapsed_seconds=round(elapsed, 4))

@app.post("/process", response_model=ProcessResponse, summary="Run full pipeline")
async def process(request: ProcessRequest) -> ProcessResponse:
    t0 = time.perf_counter()
    input_path_candidate = Path(request.input)
    if input_path_candidate.is_file():
        return await _run_file_pipeline(request, input_path_candidate, t0)
    return await _run_inline_pipeline(request, t0)

async def _run_file_pipeline(request, input_path, t0):
    try:
        from nlp_policy_nz.api import process_hansard, process_legislation
    except Exception as exc:
        raise HTTPException(status_code=500,
            detail=f"Failed to import pipeline functions: {exc}") from exc
    runner = process_legislation if request.source == "legislation" else process_hansard
    output_dir = Path.cwd() / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{input_path.stem}_{request.source}.parquet"
    try:
        result_path = runner(input_path=str(input_path),
            output_path=str(output_path),
            generate_embeddings=request.generate_embeddings)
    except Exception as exc:
        logger.exception("Pipeline processing failed")
        raise HTTPException(status_code=500,
            detail=f"Pipeline processing failed: {exc}") from exc
    elapsed = time.perf_counter() - t0
    try:
        from nlp_policy_nz.storage.serialization import load_from_parquet
        records = load_from_parquet(result_path)
    except Exception:
        records = []
    return ProcessResponse(records=[_record_to_dict(r) for r in records],
        source=request.source, count=len(records),
        output_path=str(result_path), elapsed_seconds=round(elapsed, 4))

async def _run_inline_pipeline(request, t0):
    try:
        from nlp_policy_nz.guard import LanguageIdentifier, normalize_text
        from nlp_policy_nz.semantic import generate_embedding
        from nlp_policy_nz.semantic.model_loader import load_model
        from nlp_policy_nz.storage.serialization import PipelineRecord
        from nlp_policy_nz.syntactic import (create_citation_ruler,
                                               create_nlp_pipeline)
    except Exception as exc:
        raise HTTPException(status_code=500,
            detail=f"Failed to import pipeline modules: {exc}") from exc
    nlp = create_nlp_pipeline()
    if "citation_ruler" not in nlp.pipe_names:
        create_citation_ruler(nlp)
    clean_text = normalize_text(request.input)
    doc = nlp(clean_text)
    identifier = LanguageIdentifier()
    te_reo_segments = identifier.detect_code_switching(clean_text)
    te_reo_terms = [seg for lang, seg in te_reo_segments if lang == "mi"]
    citations = []
    for ent in doc.ents:
        if ent.label_ in {"NZ_ACT", "NZ_SECTION", "CITATION"}:
            citations.append(ent.text)
    record = PipelineRecord(doc_id="inline-001",
        corpus_source=request.source, raw_text=clean_text,
        cleaned_tokens=[t.strip() for t in clean_text.split() if t.strip()],
        nz_act_citations=citations, te_reo_terms=te_reo_terms,
        embeddings=None)
    if request.generate_embeddings:
        model, tokenizer = load_model()
        embedding = generate_embedding(record.raw_text, model, tokenizer)
        record.embeddings = embedding
    elapsed = time.perf_counter() - t0
    return ProcessResponse(records=[_record_to_dict(record)],
        source=request.source, count=1, output_path=None,
        elapsed_seconds=round(elapsed, 4))

# --- Helpers ---

def _record_to_dict(record: Any) -> dict[str, Any]:
    return {"doc_id": record.doc_id, "corpus_source": record.corpus_source,
            "raw_text": record.raw_text,
            "cleaned_tokens": record.cleaned_tokens,
            "nz_act_citations": record.nz_act_citations,
            "te_reo_terms": record.te_reo_terms,
            "embeddings": record.embeddings}

# --- CLI entry point ---

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
