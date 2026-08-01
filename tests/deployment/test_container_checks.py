"""Tests for container smoke checks."""

from unittest.mock import patch, MagicMock

import pytest
import requests

from nlp_policy_nz.deployment.container_checks import (
    SmokeCheckResult,
    probe_http_endpoint,
    probe_tcp_endpoint,
    _probe_target,
    run_container_smoke_checks,
)


def test_probe_http_endpoint_success():
    with patch("nlp_policy_nz.deployment.container_checks.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_get.return_value = mock_response
        assert probe_http_endpoint("http://example.com") is True
        mock_get.assert_called_once_with("http://example.com", timeout=5.0)
        mock_response.raise_for_status.assert_called_once()

def test_probe_http_endpoint_failure():
    with patch("nlp_policy_nz.deployment.container_checks.requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.HTTPError()
        mock_get.return_value = mock_response
        with pytest.raises(requests.HTTPError):
            probe_http_endpoint("http://example.com")

def test_probe_tcp_endpoint_success():
    with patch("nlp_policy_nz.deployment.container_checks.socket.create_connection") as mock_conn:
        assert probe_tcp_endpoint("localhost", 8080) is True
        mock_conn.assert_called_once_with(("localhost", 8080), timeout=5.0)

def test_probe_tcp_endpoint_failure():
    with patch("nlp_policy_nz.deployment.container_checks.socket.create_connection") as mock_conn:
        mock_conn.side_effect = OSError()
        with pytest.raises(OSError):
            probe_tcp_endpoint("localhost", 8080)

def test_probe_target_dispatch_http():
    with patch("nlp_policy_nz.deployment.container_checks.probe_http_endpoint") as mock_http:
        mock_http.return_value = True
        assert _probe_target("http://example.com", 2.0) is True
        mock_http.assert_called_once_with("http://example.com", timeout=2.0)

def test_probe_target_dispatch_tcp():
    with patch("nlp_policy_nz.deployment.container_checks.probe_tcp_endpoint") as mock_tcp:
        mock_tcp.return_value = True
        assert _probe_target("tcp://localhost:5432", 3.0) is True
        mock_tcp.assert_called_once_with("localhost", 5432, timeout=3.0)

def test_probe_target_invalid_tcp():
    with pytest.raises(ValueError, match="Invalid TCP target"):
        _probe_target("tcp://invalid", 3.0)  # No port

def test_run_container_smoke_checks():
    targets = {
        "web": "http://web:8000",
        "db": "tcp://db:5432",
        "cache": "tcp://invalid",
        "api": "http://api.invalid",
        "storage": "tcp://storage:9000"
    }

    def mock_probe(target, timeout):
        if target == "http://web:8000":
            return True
        elif target == "tcp://db:5432":
            return True
        elif target == "tcp://invalid":
            raise ValueError("Invalid TCP target")
        elif target == "http://api.invalid":
            raise requests.RequestException()
        elif target == "tcp://storage:9000":
            raise OSError()
        return False

    with patch("nlp_policy_nz.deployment.container_checks._probe_target", side_effect=mock_probe):
        results = run_container_smoke_checks(targets, timeout=1.0)

        assert len(results) == 5
        assert results[0] == SmokeCheckResult(name="web", target="http://web:8000", reachable=True)
        assert results[1] == SmokeCheckResult(name="db", target="tcp://db:5432", reachable=True)
        assert results[2] == SmokeCheckResult(name="cache", target="tcp://invalid", reachable=False)
        assert results[3] == SmokeCheckResult(name="api", target="http://api.invalid", reachable=False)
        assert results[4] == SmokeCheckResult(name="storage", target="tcp://storage:9000", reachable=False)
