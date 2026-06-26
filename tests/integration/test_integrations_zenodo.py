"""Integration-style tests for Zenodo API request construction."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from nlp_policy_nz.integrations import zenodo

if TYPE_CHECKING:
    import pytest


class _Response:
    """Small requests.Response stand-in for mocked Zenodo calls."""

    ok = True
    status_code = 201
    reason = "Created"
    text = "{}"

    def json(self) -> dict[str, Any]:
        """Return a minimal deposit payload."""
        return {"id": 123, "links": {"bucket": "https://example.test/bucket"}}


def test_create_sandbox_deposit_builds_expected_payload(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Zenodo deposit creation sends metadata without requiring live network access."""
    captured: dict[str, Any] = {}

    def fake_post(
        url: str,
        *,
        json: dict[str, Any],
        headers: dict[str, str],
        timeout: int,
    ) -> _Response:
        captured.update({"url": url, "json": json, "headers": headers, "timeout": timeout})
        return _Response()

    monkeypatch.setattr(zenodo.requests, "post", fake_post)

    result = zenodo.create_sandbox_deposit(
        title="Track 23 test deposit",
        description="Mocked deposit",
        creators=[{"name": "Tester, Example"}],
        token="test-token",
    )

    assert result["id"] == 123
    assert captured["url"].endswith("/deposit/depositions")
    assert captured["json"]["metadata"]["upload_type"] == "dataset"
    assert captured["headers"]["Authorization"] == "Bearer test-token"
