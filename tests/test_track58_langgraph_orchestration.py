"""Track 58 LangGraph orchestration evaluation contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.automation import langgraph_eval

ROOT = Path(__file__).resolve().parents[1]
TRACK58 = ROOT / "conductor" / "tracks" / "track58_langgraph_orchestration_eval_20260701"


def test_track58_artifacts_exist() -> None:
    """Track 58 should ship the evaluation scaffold, doc, and helper module."""
    expected = [
        ROOT / "docs" / "langgraph_orchestration_evaluation.md",
        TRACK58 / "index.md",
        TRACK58 / "metadata.json",
        TRACK58 / "plan.md",
        TRACK58 / "spec.md",
        ROOT / "src" / "nlp_policy_nz" / "automation" / "langgraph_eval.py",
    ]
    assert [path for path in expected if not path.is_file()] == []


def test_track58_registry_metadata_and_doc_are_in_sync() -> None:
    """The registry, metadata, and docs should reflect the new evaluation track."""
    registry = (ROOT / "conductor" / "tracks.md").read_text(encoding="utf-8")
    metadata = json.loads((TRACK58 / "metadata.json").read_text(encoding="utf-8"))
    docs = (ROOT / "docs" / "langgraph_orchestration_evaluation.md").read_text(encoding="utf-8")

    assert "Track 58: LangGraph Agent Workflow Orchestration Evaluation" in registry
    assert "./conductor/tracks/track58_langgraph_orchestration_eval_20260701/" in registry
    assert metadata["track_id"] == "track58_langgraph_orchestration_eval_20260701"
    assert metadata["status"] == "complete"
    assert "intake -> triage -> draft -> review -> recover -> complete" in docs
    assert "core deterministic extraction pipelines" in docs.lower()


def test_track58_prototype_scoring_and_cleanup(tmp_path) -> None:
    """The prototype should be deterministic and cleanup stale checkpoints."""
    workflow = langgraph_eval.build_candidate_workflow()
    assert workflow.states == (
        "intake",
        "triage",
        "draft",
        "review",
        "recover",
        "complete",
    )
    assert any(step.state == "review" and step.next_state == "recover" for step in workflow.transitions)

    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir()
    stale = checkpoint_dir / "review.checkpoint"
    fresh = checkpoint_dir / "keep.txt"
    stale.write_text("stale", encoding="utf-8")
    fresh.write_text("fresh", encoding="utf-8")

    cleanup = langgraph_eval.cleanup_checkpoints(checkpoint_dir)
    assert cleanup["removed"] == ["review.checkpoint"]
    assert cleanup["remaining"] == ["keep.txt"]
    assert not stale.exists()
    assert fresh.exists()

    result = langgraph_eval.run_deterministic_prototype()
    assert result["benchmark"]["candidate_score"] >= result["benchmark"]["baseline_score"]
    assert "review" in result["runs"][0]["trace"]
    assert "recover" in result["runs"][0]["trace"]
    assert result["decision_record"]["checkpoint_cleanup_required"] is True
    assert result["decision_record"]["python_fallback_required"] is True


def test_track58_report_and_fingerprint_are_stable() -> None:
    """The rendered report and fingerprint should be deterministic."""
    result = langgraph_eval.run_deterministic_prototype()
    report = langgraph_eval.render_evaluation_report(result)
    fingerprint = langgraph_eval.evaluation_fingerprint(result)

    assert "# Track 58 LangGraph Evaluation" in report
    assert "Allowed" in report
    assert "Banned" in report
    assert len(fingerprint) == 64
    assert fingerprint == langgraph_eval.evaluation_fingerprint(result)
