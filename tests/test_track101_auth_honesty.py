"""Regression tests for Track 101 authentication configuration honesty."""

from pathlib import Path

from nlp_policy_nz.api.auth import load_security_settings


ROOT = Path(__file__).resolve().parents[1]


def test_compose_enables_api_auth():
    compose = (ROOT / "docker-compose.yml").read_text(encoding="utf-8")

    assert 'NLP_POLICY_NZ_REQUIRE_API_AUTH: "true"' in compose


def test_local_default_remains_optional(monkeypatch):
    monkeypatch.delenv("NLP_POLICY_NZ_REQUIRE_API_AUTH", raising=False)

    assert load_security_settings().auth_required is False


def test_environment_can_enable_auth(monkeypatch):
    monkeypatch.setenv("NLP_POLICY_NZ_REQUIRE_API_AUTH", "true")

    assert load_security_settings().auth_required is True
