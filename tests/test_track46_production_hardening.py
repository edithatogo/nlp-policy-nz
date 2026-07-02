"""Track 46 production hardening contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from nlp_policy_nz.api import server
from nlp_policy_nz.config import (
    FeatureFlags,
    RuntimeSettings,
    load_feature_flags,
    load_runtime_settings,
)
from nlp_policy_nz.storage import PipelineRecord, load_from_parquet, serialize_to_parquet
from nlp_policy_nz.storage.migrations import (
    add_schema_version,
    current_schema_version,
    strip_schema_version,
)

ROOT = Path(__file__).resolve().parents[1]
TRACK46 = ROOT / "conductor" / "tracks" / "track46_production_hardening_20260626"


def test_track46_repo_artifacts_exist() -> None:
    """Track 46 should ship environment, workflow, migration, and runbook assets."""
    expected = [
        ROOT / ".env.dev",
        ROOT / ".env.staging",
        ROOT / ".env.prod",
        ROOT / "docs" / "ops" / "runbook.md",
        ROOT / "data" / "migrations" / "registry.json",
        ROOT / "data" / "migrations" / "0001_add_schema_version.py",
        ROOT / ".github" / "workflows" / "deploy-staging.yml",
        ROOT / ".github" / "workflows" / "load-test.yml",
        TRACK46 / "index.md",
        TRACK46 / "metadata.json",
        TRACK46 / "plan.md",
        TRACK46 / "spec.md",
    ]

    assert [path for path in expected if not path.is_file()] == []


def test_track46_registry_and_plan_are_in_sync() -> None:
    """Track 46 should be marked in progress with production-hardening scope."""
    registry = (ROOT / "conductor" / "tracks.md").read_text(encoding="utf-8")
    metadata = json.loads((TRACK46 / "metadata.json").read_text(encoding="utf-8"))
    plan = (TRACK46 / "plan.md").read_text(encoding="utf-8")
    spec = (TRACK46 / "spec.md").read_text(encoding="utf-8")

    assert "Track 46: Production Hardening & API Maturity" in registry
    assert "./conductor/tracks/track46_production_hardening_20260626/" in registry
    assert metadata["track_id"] == "track46_production_hardening_20260626"
    assert metadata["status"] == "in_progress"
    assert "VERSION.json" in plan
    assert "load-test.yml" in plan
    assert "slowapi" in plan.lower()
    assert "rate limiting" in spec.lower()
    assert "health check endpoint" in spec.lower()


def test_track46_runtime_settings_and_feature_flags_load_from_env(monkeypatch) -> None:
    """Runtime settings and feature flags should be driven by environment variables."""
    monkeypatch.setenv("NLP_POLICY_NZ_API_VERSIONS", "v1,v2")
    monkeypatch.setenv("NLP_POLICY_NZ_CORS_ORIGINS", "https://example.test,https://staging.example.test")
    monkeypatch.setenv("NLP_POLICY_NZ_DB_PATH", "./example-db")
    monkeypatch.setenv("NLP_POLICY_NZ_LAST_RUN_TIMESTAMP", "2026-07-02T00:00:00Z")
    monkeypatch.setenv("NLP_POLICY_NZ_RATE_LIMIT_PER_MINUTE", "42")
    monkeypatch.setenv("NLP_POLICY_NZ_UVICORN_WORKERS", "4")
    monkeypatch.setenv("NLP_POLICY_NZ_V1_SUNSET_DAYS", "90")
    monkeypatch.setenv("NLP_POLICY_NZ_ENABLE_EMBED", "false")
    monkeypatch.setenv("NLP_POLICY_NZ_ENABLE_SEARCH", "true")

    settings = load_runtime_settings()
    flags = load_feature_flags()

    assert settings.api_versions == ("v1", "v2")
    assert settings.cors_origins == ("https://example.test", "https://staging.example.test")
    assert settings.db_path == "./example-db"
    assert settings.last_run_timestamp == "2026-07-02T00:00:00Z"
    assert settings.rate_limit_per_minute == 42
    assert settings.uvicorn_workers == 4
    assert settings.sunset_days_v1 == 90
    assert flags.embed_enabled is False
    assert flags.search_enabled is True


def test_track46_versioned_routes_health_and_version_manifest(monkeypatch) -> None:
    """Versioned routes should serve v1 and v2 concurrently with deprecation headers."""
    monkeypatch.setattr(server, "_settings", RuntimeSettings(rate_limit_per_minute=120))
    monkeypatch.setattr(
        server,
        "_feature_flags",
        FeatureFlags(enable_v1=True, enable_v2=True, embed_enabled=True, search_enabled=True, process_enabled=True),
    )
    server._rate_limit_history.clear()

    client = TestClient(server.app)

    v1_health = client.get("/v1/health")
    v2_health = client.get("/v2/health")
    version = client.get("/v2/version")

    assert v1_health.status_code == 200
    assert v1_health.headers["deprecation"] == "true"
    assert "sunset" in v1_health.headers
    assert v2_health.status_code == 200
    assert "deprecation" not in v2_health.headers
    assert v1_health.json()["pipeline_status"] in {"ok", "degraded"}
    assert version.status_code == 200
    assert version.json()["version"] == server.app.version
    assert "build_timestamp" in version.json()


def test_track46_feature_flags_and_rate_limit(monkeypatch) -> None:
    """Feature flags should disable stages and the limiter should block abusive clients."""
    monkeypatch.setattr(server, "_settings", RuntimeSettings(rate_limit_per_minute=1))
    monkeypatch.setattr(
        server,
        "_feature_flags",
        FeatureFlags(embed_enabled=False, search_enabled=True, process_enabled=True),
    )
    server._rate_limit_history.clear()

    class DummyGenerator:
        model_name = "dummy-model"

        def embed_batch(self, texts):  # noqa: ANN001
            return []

    def make_generator() -> DummyGenerator:
        return DummyGenerator()

    monkeypatch.setattr(server, "_get_embedding_generator", make_generator)
    monkeypatch.setattr(server, "search_similar", lambda **kwargs: [{"doc_id": "d1", "text": "x"}])

    client = TestClient(server.app)

    disabled = client.post("/v2/embed", json={"texts": ["hello"]})
    assert disabled.status_code == 503

    first = client.post("/v2/search", json={"query": "health", "top_k": 1})
    second = client.post("/v2/search", json={"query": "health", "top_k": 1})
    assert first.status_code == 200
    assert second.status_code == 429


def test_track46_schema_version_and_migrations(tmp_path: Path) -> None:
    """Pipeline records should carry a schema version and survive migration helpers."""
    record = PipelineRecord(
        doc_id="doc-1",
        corpus_source="legislation",
        raw_text="Test text",
        cleaned_tokens=["Test", "text"],
        nz_act_citations=[],
        te_reo_terms=[],
    )
    assert record.schema_version == current_schema_version()

    upgraded = add_schema_version({"doc_id": "doc-1"})
    downgraded = strip_schema_version(upgraded)
    assert upgraded["schema_version"] == current_schema_version()
    assert "schema_version" not in downgraded

    parquet_path = serialize_to_parquet([record], tmp_path / "record.parquet")
    roundtrip = load_from_parquet(parquet_path)
    assert roundtrip[0].schema_version == current_schema_version()
