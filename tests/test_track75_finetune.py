"""Tests for Track 75 NZ legislation/Hansard fine-tuning closeout helpers."""

from __future__ import annotations

import json
from pathlib import Path

from nlp_policy_nz.training.track75_finetune import (
    build_track75_run_record,
    default_track75_config,
    render_track75_model_card_markdown,
    render_track75_run_record_json,
)

ROOT = Path(__file__).resolve().parents[1]
TRACK75_DIR = (
    ROOT
    / "conductor"
    / "tracks"
    / "archive"
    / "track75_nz_legislation_hansard_finetuned_model_20260704"
)


def test_track75_run_record_is_deterministic_and_defer_first() -> None:
    """The Track 75 record should pin tracked inputs and defer promotion without live scores."""
    record = build_track75_run_record(default_track75_config())

    assert record.track_id == "track75_nz_legislation_hansard_finetuned_model_20260704"
    assert record.training_seed == 20260704
    assert record.training_data_manifest_id == "track74_nz_legal_hansard_evaluation_set_20260704"
    assert record.training_job_spec["task"] == "mlm"
    assert record.training_job_spec["model"]["model_name"] == "nlpaueb/legal-bert-base-uncased"
    assert record.training_job_spec["training"]["num_epochs"] == 3
    assert record.comparison.track74_overall_score == 0.7143
    assert record.comparison.track74_promotion_threshold == 0.75
    assert record.comparison.promotion_ready is False
    assert record.comparison.decision == "defer"
    assert "live fine-tuned run" in record.comparison.decision_reason.lower()
    assert record.artifact_layout.fallback_path == "nlp_policy_nz.semantic.model_loader:load_model"


def test_track75_residual_gates_are_explicit() -> None:
    """The closeout record should keep the remaining external gates visible."""
    record = build_track75_run_record(default_track75_config())

    assert "Live fine-tuning run on the selected model" in record.residual_external_gates
    assert "Measured evaluation on the Track 74 held-out set" in record.residual_external_gates
    assert "Optional Hugging Face Hub publication after promotion approval" in record.residual_external_gates


def test_track75_committed_artifacts_match_rendered_outputs() -> None:
    """Committed Track 75 artifacts should match the deterministic renderers."""
    run_record_path = TRACK75_DIR / "run_record.json"
    model_card_path = TRACK75_DIR / "model_card.md"

    assert run_record_path.read_text(encoding="utf-8") == render_track75_run_record_json()
    assert model_card_path.read_text(encoding="utf-8") == render_track75_model_card_markdown()

    payload = json.loads(run_record_path.read_text(encoding="utf-8"))
    assert payload["track_id"] == "track75_nz_legislation_hansard_finetuned_model_20260704"
    assert payload["comparison"]["decision"] == "defer"
