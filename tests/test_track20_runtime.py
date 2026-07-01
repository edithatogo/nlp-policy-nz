"""Tests for Track 20 environment-adaptive runtime planning."""

from __future__ import annotations

import json

from nlp_policy_nz.training.runtime import (
    TrainingRuntimeProfile,
    choose_training_execution_plan,
    render_runtime_plan_json,
)
from nlp_policy_nz.training.smoke import (
    render_smoke_training_json,
    run_cpu_mlm_smoke_training,
)


def _profile(**overrides: object) -> TrainingRuntimeProfile:
    """Return a synthetic runtime profile for deterministic backend tests."""
    base: dict[str, object] = {
        "platform": "Linux",
        "machine": "x86_64",
        "cpu_count": 2,
        "ci": False,
        "torch_installed": True,
        "torch_version": "2.12.1+cpu",
        "cuda_available": False,
        "mps_available": False,
        "rocm_available": False,
        "directml_available": False,
        "onnxruntime_installed": False,
        "transformers_installed": True,
        "datasets_installed": True,
        "peft_installed": True,
        "trl_installed": True,
        "bitsandbytes_installed": True,
        "wandb_installed": True,
        "hf_cli_available": True,
        "nvidia_smi_available": False,
    }
    base.update(overrides)
    return TrainingRuntimeProfile(**base)


def test_github_actions_profile_uses_ci_cpu_smoke_plan() -> None:
    """GitHub Actions should use a tiny CPU plan, not require CUDA."""
    plan = choose_training_execution_plan(_profile(ci=True, cpu_count=2))

    assert plan.backend == "ci_cpu"
    assert plan.device == "cpu"
    assert plan.ci_safe is True
    assert plan.smoke_test is True
    assert plan.max_steps == 2
    assert plan.allow_model_download is False
    assert plan.allow_hub_push is False
    assert plan.blockers == ()


def test_local_cpu_profile_uses_bounded_cpu_plan() -> None:
    """A no-GPU workstation should still get an executable bounded local plan."""
    plan = choose_training_execution_plan(_profile(platform="Windows", cpu_count=22))

    assert plan.backend == "local_cpu"
    assert plan.device == "cpu"
    assert plan.smoke_test is True
    assert plan.max_steps == 5
    assert "mlm_smoke" in plan.suitable_tasks
    assert plan.blockers == ()


def test_cuda_profile_uses_accelerated_plan_without_hub_push_by_default() -> None:
    """CUDA should be used when available, while publication remains opt-in."""
    plan = choose_training_execution_plan(
        _profile(cuda_available=True, nvidia_smi_available=True, torch_version="2.12.1+cu128")
    )

    assert plan.backend == "cuda"
    assert plan.device == "cuda"
    assert plan.smoke_test is False
    assert plan.allow_model_download is True
    assert plan.allow_hub_push is False
    assert "citation" in plan.suitable_tasks


def test_requested_unavailable_directml_reports_blocker() -> None:
    """Explicit backend requests should report blockers instead of silently falling back."""
    plan = choose_training_execution_plan(_profile(platform="Windows"), prefer_backend="directml")

    assert plan.backend == "directml"
    assert "torch-directml is not installed" in plan.blockers


def test_runtime_plan_json_is_stable() -> None:
    """Runtime plans should be renderable as JSON for CI logs."""
    payload = json.loads(render_runtime_plan_json(_profile(ci=True)))

    assert payload["selected_plan"]["backend"] == "ci_cpu"
    assert payload["profile"]["ci"] is True


def test_ci_cpu_plan_runs_bounded_smoke_training() -> None:
    """The GitHub Actions plan should execute a tiny CPU training loop."""
    plan = choose_training_execution_plan(_profile(ci=True))

    result = run_cpu_mlm_smoke_training(plan=plan)

    assert result.backend == "ci_cpu"
    assert result.device == "cpu"
    assert result.ci_safe is True
    assert result.steps_run == 2
    assert result.records_seen == 4
    assert result.final_loss > 0
    assert result.loss_decreased is True


def test_local_cpu_plan_runs_bounded_smoke_training() -> None:
    """The local CPU plan should execute a bounded CPU training loop."""
    plan = choose_training_execution_plan(_profile(platform="Windows", cpu_count=22))

    result = run_cpu_mlm_smoke_training(plan=plan)

    assert result.backend == "local_cpu"
    assert result.device == "cpu"
    assert result.steps_run == 5
    assert result.records_seen == 4
    assert result.final_loss > 0
    assert result.loss_decreased is True


def test_smoke_training_json_is_stable() -> None:
    """Smoke training results should be JSON-renderable for CI logs."""
    plan = choose_training_execution_plan(_profile(ci=True))
    payload = json.loads(render_smoke_training_json(plan=plan))

    assert payload["backend"] == "ci_cpu"
    assert payload["steps_run"] == 2
