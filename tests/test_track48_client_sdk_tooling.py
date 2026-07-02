"""Track 48 API client SDK and developer tooling contract tests."""

from __future__ import annotations

import asyncio
import json
import tomllib
from pathlib import Path

import httpx

from nlp_policy_nz.cli.main import main
from nlp_policy_nz.client import AsyncNLPPolicyNZClient, NLPPolicyNZClient

ROOT = Path(__file__).resolve().parents[1]
TRACK48 = ROOT / "conductor" / "tracks" / "track48_client_sdk_tooling_20260626"


def test_track48_repo_artifacts_exist() -> None:
    """Track 48 should ship the SDK, tooling, and developer experience assets."""
    expected = [
        ROOT / "src" / "nlp_policy_nz" / "client" / "__init__.py",
        ROOT / "src" / "nlp_policy_nz" / "client" / "async_client.py",
        ROOT / "src" / "nlp_policy_nz" / "client" / "models.py",
        ROOT / "src" / "nlp_policy_nz" / "client" / "sync.py",
        ROOT / "src" / "nlp_policy_nz" / "cli" / "completion.py",
        ROOT / "docker-compose.yml",
        ROOT / ".env.example",
        ROOT / "QUICKSTART.md",
        ROOT / "examples" / "client_health.py",
        ROOT / "examples" / "client_search.py",
        ROOT / "examples" / "client_process.py",
        TRACK48 / "index.md",
        TRACK48 / "metadata.json",
        TRACK48 / "plan.md",
        TRACK48 / "spec.md",
    ]

    assert [path for path in expected if not path.is_file()] == []


def test_track48_registry_and_plan_are_linked() -> None:
    """Track 48 should be registered and marked complete."""
    registry = (ROOT / "conductor" / "tracks.md").read_text(encoding="utf-8")
    metadata = json.loads((TRACK48 / "metadata.json").read_text(encoding="utf-8"))
    plan = (TRACK48 / "plan.md").read_text(encoding="utf-8")
    spec = (TRACK48 / "spec.md").read_text(encoding="utf-8")

    assert "Track 48: API Client SDK & Developer Tooling" in registry
    assert "./conductor/tracks/track48_client_sdk_tooling_20260626/" in registry
    assert metadata["track_id"] == "track48_client_sdk_tooling_20260626"
    assert metadata["status"] == "complete"
    assert "`[client]` extra" in plan
    assert "completion install" in plan
    assert "docker-compose.yml" in plan
    assert "quickstart" in spec.lower()
    assert "5-minute" in spec.lower()


def test_track48_client_sdk_parses_responses_and_retries(monkeypatch) -> None:
    """The sync client should build versioned requests, parse models, and retry once."""
    calls: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.path)
        if len(calls) == 1:
            return httpx.Response(503, json={"detail": "retry me"})
        assert request.headers["x-api-key"] == "secret"
        return httpx.Response(
            200,
            json={
                "status": "ok",
                "pipeline_status": "degraded",
                "db_connected": True,
                "model_loaded": False,
                "model_name": "",
                "version": "0.1.0",
                "last_run_timestamp": None,
            },
        )

    monkeypatch.setattr("nlp_policy_nz.client.sync.time.sleep", lambda *_args, **_kwargs: None)
    client = NLPPolicyNZClient(
        base_url="https://example.test",
        api_key="secret",
        transport=httpx.MockTransport(handler),
        retry_attempts=2,
        retry_backoff_seconds=0.0,
    )

    health = client.health()

    assert health.pipeline_status == "degraded"
    assert calls == ["/v1/health", "/v1/health"]
    assert health.model_dump()["status"] == "ok"


def test_track48_async_client_parses_search_results() -> None:
    """The async client should parse typed search responses."""

    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == "/v1/search"
        return httpx.Response(
            200,
            json={
                "results": [{"doc_id": "doc-1", "text": "matched", "corpus_source": "legislation"}],
                "query": "climate",
                "count": 1,
                "elapsed_seconds": 0.01,
            },
        )

    async def run() -> None:
        client = AsyncNLPPolicyNZClient(
            base_url="https://example.test",
            transport=httpx.MockTransport(handler),
            retry_attempts=1,
        )
        try:
            result = await client.search("climate", top_k=1)
        finally:
            await client.aclose()
        assert result.count == 1
        assert result.results[0]["doc_id"] == "doc-1"

    asyncio.run(run())


def test_track48_completion_and_manpage_generation(tmp_path: Path) -> None:
    """The CLI should generate installable completions and a man page."""
    bash_output = tmp_path / "nlp-policy-nz.bash"
    man_output = tmp_path / "nlp-policy-nz.1"

    assert main(["completion", "install", "--shell", "bash", "--output", str(bash_output)]) == 0
    assert main(["completion", "manpage", "--output", str(man_output)]) == 0

    bash_script = bash_output.read_text(encoding="utf-8")
    manpage = man_output.read_text(encoding="utf-8")

    assert "complete -F _nlp_policy_nz_complete nlp-policy-nz" in bash_script
    assert "completion" in bash_script
    assert ".TH NLP-POLICY-NZ 1" in manpage
    assert "nlp-policy-nz \\- NLP preprocessing pipeline CLI" in manpage


def test_track48_compose_and_quickstart_are_reusable() -> None:
    """The compose stack and quickstart should reflect the developer workflow."""
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    env_example = (ROOT / ".env.example").read_text(encoding="utf-8")
    quickstart = (ROOT / "QUICKSTART.md").read_text(encoding="utf-8")

    assert "api:" in compose
    assert "lancedb:" in compose
    assert "model-cache:" in compose
    assert "qdrant:" in compose
    assert "NLP_POLICY_NZ_DB_PATH" in env_example
    assert "NLP_POLICY_NZ_ENABLE_SEARCH" in env_example
    assert "docker compose up --build api lancedb model-cache qdrant" in quickstart
    assert "client_search.py" in quickstart


def test_track48_pyproject_client_extra() -> None:
    """The optional client extra should expose the HTTP dependency."""
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert pyproject["project"]["requires-python"] == ">=3.11"
    assert "httpx>=0.27.0" in pyproject["project"]["optional-dependencies"]["client"]
