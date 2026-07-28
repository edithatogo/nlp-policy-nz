"""Track 99 Haystack governance orchestration contract tests."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from nlp_policy_nz.orchestration.haystack import decision
from nlp_policy_nz.orchestration.haystack.components import (
    DocumentWriter,
    InMemoryDocumentStore,
    LanceDBDocumentWriter,
    LegalStructureSplitter,
    ProvenanceStepRecorder,
    RightsGateComponent,
    SpaCyEnricher,
)
from nlp_policy_nz.orchestration.haystack.evaluation import (
    emit_scorecard,
    exact_match_score,
    sas_proxy_score,
)
from nlp_policy_nz.orchestration.haystack.pipelines import (
    GENERATIVE_COMPONENTS_FORBIDDEN,
    build_indexing_pipeline,
    build_restricted_query_pipeline,
    extractive_qa,
    run_indexing_pipeline,
)
from nlp_policy_nz.orchestration.haystack.types import (
    ExtractedSpanAnswer,
    GovernanceDocument,
)

ROOT = Path(__file__).resolve().parents[1]


def test_track99_decision_constants() -> None:
    """Decision record constants should reflect governance boundaries."""
    assert decision.TRACK_ID == "track99_haystack_governance_orchestration_20260728"
    assert "typed dag" in " ".join(decision.ALLOWED_CONTEXTS).lower()
    assert any("required runtime dependency" in item.lower() for item in decision.BANNED_CONTEXTS)
    assert decision.FAITHFULNESS_EVALUATOR_AUTHORITATIVE is False
    assert decision.GENERATIVE_DEFAULT_ALLOWED is False


def test_track99_importing_package_does_not_load_haystack() -> None:
    """Default package import must not eagerly import haystack."""
    decision.assert_haystack_not_default_runtime()
    assert isinstance(decision.haystack_available(), bool)


def test_track99_rights_gate_fail_closed() -> None:
    """Rights gate should block restricted documents without clearance."""
    gate = RightsGateComponent()
    blocked = gate.run(
        documents=[
            GovernanceDocument(
                id="restricted-1",
                content="secret clause",
                meta={"access_class": "restricted"},
            )
        ]
    )
    assert blocked["documents"] == []
    assert "error" in blocked

    missing_class = gate.run(
        documents=[GovernanceDocument(id="x", content="text", meta={})]
    )
    assert missing_class["documents"] == []
    assert "error" in missing_class

    cleared = gate.run(
        documents=[
            GovernanceDocument(
                id="public-1",
                content="open clause",
                meta={"access_class": "public"},
            )
        ]
    )
    assert len(cleared["documents"]) == 1


def test_track99_legal_structure_splitter_preserves_clauses() -> None:
    """Splitter should preserve multiple legal clauses instead of naive word split."""
    splitter = LegalStructureSplitter()
    doc = GovernanceDocument(
        id="act-1",
        content="Section 1\nFirst clause body.\n\nSection 2\nSecond clause body.",
        meta={"access_class": "public"},
    )
    result = splitter.run(documents=[doc])
    chunks = result["documents"]
    assert len(chunks) >= 2
    clause_indices = {chunk.meta.get("clause_index") for chunk in chunks}
    assert len(clause_indices) >= 2
    assert all(chunk.meta.get("parent_id") == "act-1" for chunk in chunks)


def test_track99_spacy_enricher_meta_tags() -> None:
    """SpaCy enricher should tag pipeline component and ents."""
    noop = SpaCyEnricher()
    result = noop.run(
        documents=[
            GovernanceDocument(id="d1", content="Parliament met.", meta={"access_class": "public"})
        ]
    )
    enriched = result["documents"][0]
    assert enriched.meta["pipeline_component"] == "SpaCyEnricher"
    assert enriched.meta["spacy_model"] == "noop"
    assert enriched.meta["ents"] == []


def test_track99_indexing_pipeline_offline(tmp_path: Path) -> None:
    """Indexing pipeline should run offline through in-memory writer."""
    store = InMemoryDocumentStore()
    writer = DocumentWriter(store=store)
    pipeline = build_indexing_pipeline(writer=writer)
    docs = [
        GovernanceDocument(
            id="doc-a",
            content="Section 1\nAlpha text.\n\nSection 2\nBeta text.",
            meta={"access_class": "public"},
        )
    ]
    result = run_indexing_pipeline(docs, pipeline=pipeline)
    assert result["written_count"] >= 2
    assert len(store.documents) >= 2


def test_track99_extractive_answer_is_substring_with_offsets() -> None:
    """Extractive QA must return a verbatim substring with offsets."""
    documents = [
        GovernanceDocument(
            id="d1",
            content="The Privacy Act 2020 governs personal information.",
            meta={"access_class": "public"},
        ),
        GovernanceDocument(
            id="d2",
            content="Unrelated fisheries regulation text.",
            meta={"access_class": "public"},
        ),
    ]
    answer = extractive_qa("Privacy Act personal information", documents)
    source = documents[0].content
    assert isinstance(answer, ExtractedSpanAnswer)
    assert answer.document_id == "d1"
    assert source[answer.start : answer.end] == answer.answer
    assert answer.is_verbatim_of(source)


def test_track99_restricted_pipeline_forbids_generative() -> None:
    """Restricted query pipeline must not include generative components."""
    pipeline = build_restricted_query_pipeline()
    assert GENERATIVE_COMPONENTS_FORBIDDEN is True
    assert "generator" not in pipeline
    assert pipeline.get("generative_forbidden") is True


def test_track99_scorecard_marks_faithfulness_non_authoritative() -> None:
    """Scorecard should mark faithfulness non-authoritative and block promotion."""
    predictions = ["Privacy Act", "fisheries"]
    ground_truths = ["Privacy Act", "Privacy Act"]
    card = emit_scorecard(predictions, ground_truths)
    assert card["faithfulness_evaluator_authoritative"] is False
    assert card["promotion_allowed"] is False
    assert card["exact_match"] == pytest.approx(0.5)
    assert 0.0 <= card["sas_proxy"] <= 1.0
    assert len(card["individual_scores"]) == 2


def test_track99_evaluation_helpers() -> None:
    """Exact match and SAS proxy helpers should be deterministic."""
    assert exact_match_score("A", "A") == 1.0
    assert exact_match_score("A", "B") == 0.0
    assert sas_proxy_score("hello world", "hello there") == pytest.approx(1 / 3)


def test_track99_docs_exist() -> None:
    """Track 99 decision and sovereign deploy docs should exist."""
    expected = [
        ROOT / "docs" / "haystack-governance-decision.md",
        ROOT / "docs" / "haystack-sovereign-deploy.md",
    ]
    assert [path for path in expected if not path.is_file()] == []
    decision_doc = expected[0].read_text(encoding="utf-8")
    assert "#189" in decision_doc
    assert "no-promotion" in decision_doc.lower() or "no promotion" in decision_doc.lower()


def test_track99_lance_writer_zero_vectors() -> None:
    """Lance writer should accept documents without vectors using zero padding."""

    class _FakeBackend:
        def __init__(self) -> None:
            self.records: list[dict[str, Any]] = []
            self.created = False

        def create_index(self, records: list[dict[str, Any]], overwrite: bool = False) -> None:
            self.records = list(records)
            self.created = True

        def add_records(self, records: list[dict[str, Any]]) -> None:
            self.records.extend(records)

        def search(self, query_vector: list[float], top_k: int = 10) -> list[dict[str, Any]]:
            return []

        def delete_index(self) -> None:
            self.records = []

        def index_exists(self) -> bool:
            return self.created

        def close(self) -> None:
            return None

    backend = _FakeBackend()
    writer = LanceDBDocumentWriter(backend=backend, vector_dim=4)
    writer.run(
        documents=[
            GovernanceDocument(id="d1", content="text", meta={"access_class": "public"})
        ]
    )
    assert len(backend.records) == 1
    assert backend.records[0]["vector"] == [0.0, 0.0, 0.0, 0.0]


def test_track99_provenance_step_recorder() -> None:
    """Provenance recorder should capture step metadata."""
    steps: list[dict[str, Any]] = []
    recorder = ProvenanceStepRecorder(steps=steps)
    recorder.run(step_name="rights_gate", started_at="2026-07-28T00:00:00Z")
    assert steps[0]["step_name"] == "rights_gate"
    assert "ended_at" in steps[0]
