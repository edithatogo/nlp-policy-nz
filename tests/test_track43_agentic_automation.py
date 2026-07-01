"""Track 43 agentic automation contract tests."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.automation import agentic

ROOT = Path(__file__).resolve().parents[1]
TRACK43 = ROOT / "conductor" / "tracks" / "track43_agentic_automation_20260626"


def test_track43_artifacts_exist() -> None:
    """Track 43 should ship the expected workflows, scripts, and docs."""
    expected = [
        ROOT / ".github" / "workflows" / "agent-review.yml",
        ROOT / ".github" / "workflows" / "auto-fix-ci.yml",
        ROOT / ".github" / "workflows" / "conductor-advance.yml",
        ROOT / ".github" / "workflows" / "self-healing-ci.yml",
        ROOT / "docs" / "agentic_automation.md",
        ROOT / "scripts" / "agent_review.py",
        ROOT / "scripts" / "conductor_advance_agent.py",
        ROOT / "scripts" / "llm_judge_eval.py",
        ROOT / "scripts" / "jules_integration.sh",
        TRACK43 / "index.md",
        TRACK43 / "metadata.json",
        TRACK43 / "plan.md",
        TRACK43 / "spec.md",
    ]

    assert [path for path in expected if not path.is_file()] == []


def test_track43_registry_and_plan_are_in_sync() -> None:
    """Track 43 should be marked in progress with the new agent workflows."""
    registry = (ROOT / "conductor" / "tracks.md").read_text(encoding="utf-8")
    metadata = json.loads((TRACK43 / "metadata.json").read_text(encoding="utf-8"))
    plan = (TRACK43 / "plan.md").read_text(encoding="utf-8")
    docs = (ROOT / "docs" / "agentic_automation.md").read_text(encoding="utf-8")

    assert "Track 43: Agentic Automation & Multi-Agent Orchestration" in registry
    assert "./conductor/tracks/track43_agentic_automation_20260626/" in registry
    assert metadata["track_id"] == "track43_agentic_automation_20260626"
    assert metadata["status"] == "complete"
    assert "Claude Code subagent" in plan
    assert "Google Jules" in plan
    assert "LLM-as-judge" in plan
    assert "self-healing CI" in plan
    assert "agent-review" in docs
    assert "self-healing" in docs


def test_track43_automation_helpers_cover_review_fix_and_judge(tmp_path, monkeypatch) -> None:
    """The reusable automation helpers should cover review, fix, advance, and judge flows."""
    review = agentic.build_review_summary(
        {
            "ruff": {"status": "pass", "detail": "ruff clean"},
            "basedpyright": {"status": "fail", "detail": "1 type error"},
        },
    )
    assert review["decision"] == "request_changes"
    assert review["failed_gates"] == ["basedpyright"]
    assert "ruff clean" in review["markdown"]

    recorded: list[list[str]] = []

    def fake_runner(cmd, **kwargs):  # noqa: ANN001
        recorded.append([str(part) for part in cmd])

        class Result:
            returncode = 0

        return Result()

    fix_result = agentic.run_auto_fix(Path.cwd(), runner=fake_runner)
    assert fix_result["ruff_fixed"] is True
    assert fix_result["basedpyright_passed"] is True
    assert any("ruff" in command for command in recorded)

    repo_root = tmp_path
    track_dir = repo_root / "conductor" / "tracks" / "track99_example_20260702"
    track_dir.mkdir(parents=True)
    (repo_root / "conductor" / "tracks.md").write_text(
        "\n".join(
            [
                "# Project Tracks",
                "",
                "---",
                "",
                "## [~] Track 99: Example",
                "*Link: [./conductor/tracks/track99_example_20260702/](./conductor/tracks/track99_example_20260702/)*",
                "",
            ],
        ),
        encoding="utf-8",
    )
    (track_dir / "plan.md").write_text(
        "\n".join(
            [
                "# Track 99: Example",
                "",
                "## Implementation Plan",
                "",
                "| # | Task | Status | Owner |",
                "|---|------|--------|-------|",
                "| 1 | Do thing | [x] | owner |",
            ],
        ),
        encoding="utf-8",
    )
    (track_dir / "metadata.json").write_text(
        json.dumps({"track_id": "track99_example_20260702", "status": "in_progress"}),
        encoding="utf-8",
    )

    advance = agentic.advance_completed_track(repo_root, "track99_example_20260702")
    assert advance["track_status"] == "complete"
    assert advance["registry_status"] == "complete"
    assert "next_track_id" in advance

    judge = agentic.evaluate_judge_run(
        [
            {
                "model_id": "model-a",
                "prompt": "Question",
                "prediction": "The answer is yes.",
                "reference": "The answer is yes.",
            },
            {
                "model_id": "model-b",
                "prompt": "Question",
                "prediction": "No.",
                "reference": "The answer is yes.",
            },
        ],
    )
    assert judge["best_model_id"] == "model-a"
    assert judge["ranked_models"][0]["model_id"] == "model-a"
    assert judge["ranked_models"][0]["judge_score"] >= judge["ranked_models"][1]["judge_score"]
