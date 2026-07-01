"""Track 38 containerization contract tests."""

from __future__ import annotations

import json
import tomllib
from pathlib import Path

from nlp_policy_nz.deployment.container_checks import (
    probe_http_endpoint,
    probe_tcp_endpoint,
)

ROOT = Path(__file__).resolve().parents[1]
TRACK38 = ROOT / "conductor" / "tracks" / "track38_containerization_20260626"


def test_track38_repo_artifacts_exist() -> None:
    """The containerization track must ship the repo-side container assets."""
    expected = [
        ROOT / ".dockerignore",
        ROOT / "Dockerfile",
        ROOT / "docker-compose.yml",
        ROOT / ".devcontainer" / "devcontainer.json",
        ROOT / ".github" / "workflows" / "containerized-ci.yml",
        ROOT / ".github" / "workflows" / "docker-publish.yml",
        TRACK38 / "index.md",
        TRACK38 / "metadata.json",
        TRACK38 / "plan.md",
        TRACK38 / "spec.md",
    ]

    assert [path for path in expected if not path.is_file()] == []


def test_track38_registry_and_metadata_are_linked() -> None:
    """Track 38 should be declared in the registry with planned metadata."""
    registry = (ROOT / "conductor" / "tracks.md").read_text(encoding="utf-8")
    metadata = json.loads((TRACK38 / "metadata.json").read_text(encoding="utf-8"))
    plan = (TRACK38 / "plan.md").read_text(encoding="utf-8")

    assert "Track 38: Containerization & Reproducible Execution" in registry
    assert "./conductor/tracks/track38_containerization_20260626/" in registry
    assert metadata["track_id"] == "track38_containerization_20260626"
    assert metadata["status"] in {"planned", "in_progress", "complete"}
    assert "docker build" in plan
    assert "docker run" in plan


def test_track38_docker_artifacts_are_structured() -> None:
    """The Dockerfile, compose file, and devcontainer should carry the right wiring."""
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")
    devcontainer = json.loads((ROOT / ".devcontainer" / "devcontainer.json").read_text(encoding="utf-8"))
    ci_workflow = (ROOT / ".github" / "workflows" / "containerized-ci.yml").read_text(encoding="utf-8")
    publish_workflow = (ROOT / ".github" / "workflows" / "docker-publish.yml").read_text(encoding="utf-8")
    ci_workflow_base = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))

    assert "FROM python:3.13-slim-bookworm" in dockerfile
    assert "pixi install --locked" in dockerfile
    assert "HEALTHCHECK" in dockerfile
    assert "USER appuser" in dockerfile
    assert "appuser" in dockerfile
    assert "lancedb_data" in compose
    assert "qdrant" in compose
    assert "pre-commit" in json.dumps(devcontainer)
    assert "ruff" in json.dumps(devcontainer).lower()
    assert "python" in json.dumps(devcontainer).lower()
    assert "docker build" in ci_workflow
    assert "docker run" in ci_workflow
    assert "--user 10001:10001" in ci_workflow
    assert "mkdir(parents=True, exist_ok=True)" in ci_workflow
    assert 'write_text("ok"' in ci_workflow or "write_text('ok'" in ci_workflow
    assert "hadolint" in ci_workflow_base.lower()
    assert "linux/amd64" in publish_workflow
    assert "linux/arm64" in publish_workflow
    assert "ghcr.io" in publish_workflow.lower()
    assert pyproject["project"]["scripts"]["nlp-policy-nz"] == "nlp_policy_nz.cli.main:main"


def test_track38_smoke_helpers_probe_http_and_tcp(monkeypatch) -> None:
    """Container smoke helpers should report success and failure deterministically."""
    class DummyResponse:
        status_code = 200

        def raise_for_status(self) -> None:
            return None

    def fake_get(url: str, timeout: float):  # noqa: ANN001
        assert url == "https://example.test/health"
        assert timeout == 3.0
        return DummyResponse()

    class DummySocket:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr("nlp_policy_nz.deployment.container_checks.requests.get", fake_get)
    monkeypatch.setattr("nlp_policy_nz.deployment.container_checks.socket.create_connection", lambda *args, **kwargs: DummySocket())

    assert probe_http_endpoint("https://example.test/health", timeout=3.0) is True
    assert probe_tcp_endpoint("example.test", 1234, timeout=3.0) is True
