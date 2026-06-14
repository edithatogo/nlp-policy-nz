"""Tests for the FastAPI inference server."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

from nlp_policy_nz.api.server import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"
        assert data["version"] == "0.1.0"
        assert data["model_loaded"] is False
        assert data["model_name"] == ""
    def test_health_json(self, client: TestClient) -> None:
        resp = client.get("/health")
        assert resp.headers["content-type"].startswith("application/json")


class TestEmbedEndpoint:
    @patch("nlp_policy_nz.api.server._get_embedding_generator")
    def test_single(self, mock_gen: MagicMock, client: TestClient) -> None:
        gen = MagicMock()
        gen.model_name = "test"
        gen.embed_batch.return_value = [MagicMock(embedding=[0.1], dimension=1, model_name="test", doc_id="", text="h")]
        mock_gen.return_value = gen
        resp = client.post("/embed", json={"texts": ["hello"]})
        assert resp.status_code == 200
        assert resp.json()["count"] == 1
    def test_empty(self, client: TestClient) -> None:
        resp = client.post("/embed", json={"texts": []})
        assert resp.status_code == 422
    def test_missing(self, client: TestClient) -> None:
        resp = client.post("/embed", json={})
        assert resp.status_code == 422


class TestSearchEndpoint:
    @patch("nlp_policy_nz.api.server.search_similar")
    def test_returns_results(self, mock_s: MagicMock, client: TestClient) -> None:
        mock_s.return_value = [{"doc_id": "d1", "text": "t", "corpus_source": "leg"}]
        resp = client.post("/search", json={"query": "climate", "top_k": 1})
        assert resp.status_code == 200
        assert resp.json()["count"] == 1
    @patch("nlp_policy_nz.api.server.search_similar")
    def test_default_top_k(self, mock_s: MagicMock, client: TestClient) -> None:
        mock_s.return_value = [{"doc_id": f"d{i}", "text": "t", "corpus_source": "leg"} for i in range(5)]
        resp = client.post("/search", json={"query": "test"})
        assert resp.status_code == 200
        assert resp.json()["count"] == 5
    def test_empty_query(self, client: TestClient) -> None:
        resp = client.post("/search", json={"query": ""})
        assert resp.status_code == 422
    @patch("nlp_policy_nz.api.server.search_similar")
    def test_db_not_found(self, mock_s: MagicMock, client: TestClient) -> None:
        mock_s.side_effect = FileNotFoundError()
        resp = client.post("/search", json={"query": "test"})
        assert resp.status_code == 404
    @patch("nlp_policy_nz.api.server.search_similar")
    def test_runtime_error(self, mock_s: MagicMock, client: TestClient) -> None:
        mock_s.side_effect = RuntimeError()
        resp = client.post("/search", json={"query": "test"})
        assert resp.status_code == 404
    def test_invalid_top_k(self, client: TestClient) -> None:
        resp = client.post("/search", json={"query": "test", "top_k": 0})
        assert resp.status_code == 422
    def test_top_k_large(self, client: TestClient) -> None:
        resp = client.post("/search", json={"query": "test", "top_k": 101})
        assert resp.status_code == 422


class TestProcessEndpoint:
    @patch('nlp_policy_nz.api.server.create_nlp_pipeline')
    @patch('nlp_policy_nz.api.server.normalize_text')
    @patch('nlp_policy_nz.api.server.LanguageIdentifier')
    def test_inline_legislation(self, mock_id, mock_norm, mock_nlp, client):
        mock_norm.return_value = 'Test text.'
        pipe = MagicMock()
        pipe.pipe_names = []
        pipe.ents = []
        pipe.spans = {}
        mock_nlp.return_value = pipe
        id_inst = MagicMock()
        id_inst.detect_code_switching.return_value = []
        mock_id.return_value = id_inst
        resp = client.post('/process', json={'input': 'Test text.', 'source': 'legislation'})
        assert resp.status_code == 200
        data = resp.json()
        assert data['count'] == 1
        assert data['source'] == 'legislation'

    @patch('nlp_policy_nz.api.server.create_nlp_pipeline')
    @patch('nlp_policy_nz.api.server.normalize_text')
    @patch('nlp_policy_nz.api.server.LanguageIdentifier')
    def test_inline_hansard(self, mock_id, mock_norm, mock_nlp, client):
        mock_norm.return_value = 'Kia ora.'
        pipe = MagicMock()
        pipe.pipe_names = []
        pipe.ents = []
        pipe.spans = {}
        mock_nlp.return_value = pipe
        id_inst = MagicMock()
        id_inst.detect_code_switching.return_value = [('mi', 'Kia ora')]
        mock_id.return_value = id_inst
        resp = client.post('/process', json={'input': 'Kia ora.', 'source': 'hansard'})
        assert resp.status_code == 200
        assert resp.json()['source'] == 'hansard'

    def test_invalid_source(self, client):
        resp = client.post('/process', json={'input': 'test', 'source': 'invalid'})
        assert resp.status_code == 422

    def test_empty_input(self, client):
        resp = client.post('/process', json={'input': '', 'source': 'legislation'})
        assert resp.status_code == 422


class TestOpenAPI:
    def test_openapi_json(self, client):
        resp = client.get('/openapi.json')
        assert resp.status_code == 200
        schema = resp.json()
        assert schema['info']['title'] == 'nlp-policy-nz Inference API'
        for p in ('/health', '/embed', '/search', '/process'):
            assert p in schema['paths']
    def test_docs(self, client):
        resp = client.get('/docs')
        assert resp.status_code == 200
        assert 'swagger' in resp.text.lower()
    def test_redoc(self, client):
        resp = client.get('/redoc')
        assert resp.status_code == 200
        assert 'redoc' in resp.text.lower()


class TestValidation:
    def test_bad_json(self, client):
        resp = client.post('/embed', content=b'bad', headers={'content-type': 'application/json'})
        assert resp.status_code == 422
    def test_missing_query(self, client):
        resp = client.post('/search', json={'top_k': 5})
        assert resp.status_code == 422
    def test_missing_process_input(self, client):
        resp = client.post('/process', json={'source': 'legislation'})
        assert resp.status_code == 422
    def test_unknown_route(self, client):
        resp = client.get('/nonexistent')
        assert resp.status_code == 404


class TestAppAttributes:
    def test_title(self):
        assert app.title == 'nlp-policy-nz Inference API'
    def test_version(self):
        assert app.version == '0.1.0'
    def test_routes(self):
        routes = {r.path for r in app.routes}
        for p in ('/health', '/embed', '/search', '/process'):
            assert p in routes
