"""Tests for the semantic fine-tuning dry-run contract."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any, cast

from nlp_policy_nz.semantic.finetune import FineTuneConfig, _main, build_dry_run_payload

if TYPE_CHECKING:
    from pathlib import Path


def test_dry_run_payload_preserves_cli_training_parameters() -> None:
    """Dry-run job specs should reflect requested CLI hyperparameters."""
    payload = build_dry_run_payload(
        FineTuneConfig(
            model_name="nlpaueb/legal-bert-base-uncased",
            output_dir="models/legal-bert-test",
            max_length=256,
            batch_size=24,
            learning_rate=3e-5,
            num_epochs=7,
            warmup_ratio=0.2,
            hub_model_id="nlp-policy-nz/legal-bert-test",
        ),
        parquet_paths=["data/train.parquet"],
    )

    job_spec = cast(dict[str, Any], payload["job_spec"])
    training = cast(dict[str, Any], job_spec["training"])

    assert payload["training_started"] is False
    assert payload["model_download_started"] is False
    assert payload["hub_push_started"] is False
    assert training["num_epochs"] == 7
    assert training["per_device_batch_size"] == 24
    assert training["learning_rate"] == 3e-5
    assert training["max_length"] == 256


def test_cli_spec_output_creates_parent_directory(tmp_path: Path) -> None:
    """Nested dry-run evidence paths should be created without live training."""
    spec_output = tmp_path / "nested" / "track20" / "dry-run.json"

    _main(["--spec-output", str(spec_output)])

    payload = json.loads(spec_output.read_text(encoding="utf-8"))
    assert payload["mode"] == "dry_run"
    assert payload["training_started"] is False
    assert payload["model_download_started"] is False
    assert payload["hub_push_started"] is False
