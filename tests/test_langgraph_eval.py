"""Tests for langgraph_eval.py."""

import pytest

from nlp_policy_nz.automation.langgraph_eval import (
    CandidateTransition,
    CandidateWorkflow,
    build_candidate_workflow,
    build_decision_record,
    cleanup_checkpoints,
    evaluation_fingerprint,
    render_evaluation_report,
    run_deterministic_prototype,
)


def test_build_candidate_workflow():
    workflow = build_candidate_workflow()
    assert isinstance(workflow, CandidateWorkflow)
    assert "intake" in workflow.states
    assert len(workflow.transitions) > 0


def test_build_decision_record():
    record = build_decision_record()
    assert "track_id" in record
    assert "allowed" in record
    assert "banned" in record
    assert isinstance(record["allowed"], list)


def test_cleanup_checkpoints(tmp_path):
    checkpoint_dir = tmp_path / "checkpoints"
    checkpoint_dir.mkdir()
    (checkpoint_dir / "test.checkpoint").write_text("test")
    (checkpoint_dir / "test.stale").write_text("test")
    (checkpoint_dir / "keep.txt").write_text("test")

    result = cleanup_checkpoints(checkpoint_dir)
    assert "test.checkpoint" in result["removed"]
    assert "test.stale" in result["removed"]
    assert "keep.txt" in result["remaining"]
    assert not (checkpoint_dir / "test.checkpoint").exists()
    assert (checkpoint_dir / "keep.txt").exists()


def test_run_deterministic_prototype(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = run_deterministic_prototype()
    assert "track_id" in result
    assert "workflow" in result
    assert "benchmark" in result
    assert "runs" in result
    assert "langgraph_available" in result


def test_render_evaluation_report(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = run_deterministic_prototype()
    report = render_evaluation_report(result)
    assert "# Track 58 LangGraph Evaluation" in report
    assert "Allowed" in report
    assert "Banned" in report


def test_evaluation_fingerprint(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = run_deterministic_prototype()
    fingerprint = evaluation_fingerprint(result)
    assert isinstance(fingerprint, str)
    assert len(fingerprint) == 64


def test_run_item_unexpected_state():
    from nlp_policy_nz.automation.langgraph_eval import _run_item

    # Create a custom workflow that forces an invalid state transition
    workflow = CandidateWorkflow(
        name="test",
        states=("intake", "complete"),
        transitions=(
            CandidateTransition(state="intake", next_state="invalid_state", rationale=""),
        ),
        human_in_loop_states=(),
        telemetry_events=(),
        allowed_contexts=(),
        banned_contexts=(),
    )

    item = {"item_id": "test_item"}
    with pytest.raises(ValueError, match="Unexpected state in prototype trace"):
        _run_item(item, workflow)
