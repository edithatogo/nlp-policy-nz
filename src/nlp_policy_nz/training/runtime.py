"""Environment-adaptive execution planning for Track 20 training."""

from __future__ import annotations

import importlib.util
import json
import os
import platform
import shutil
import sys
from dataclasses import asdict, dataclass, field
from typing import Literal

TrainingBackend = Literal[
    "ci_cpu",
    "local_cpu",
    "cuda",
    "rocm",
    "mps",
    "directml",
    "onnx_cpu",
]


@dataclass(frozen=True)
class TrainingRuntimeProfile:
    """Detected local capabilities relevant to Track 20 execution."""

    platform: str
    machine: str
    cpu_count: int
    ci: bool
    torch_installed: bool
    torch_version: str | None
    cuda_available: bool
    mps_available: bool
    rocm_available: bool
    directml_available: bool
    onnxruntime_installed: bool
    transformers_installed: bool
    datasets_installed: bool
    peft_installed: bool
    trl_installed: bool
    bitsandbytes_installed: bool
    wandb_installed: bool
    hf_cli_available: bool
    nvidia_smi_available: bool

    @property
    def python_training_stack_ready(self) -> bool:
        """Return whether the core Python training stack is importable."""
        return all(
            (
                self.torch_installed,
                self.transformers_installed,
                self.datasets_installed,
            )
        )

    @property
    def qlora_stack_ready(self) -> bool:
        """Return whether optional QLoRA planning dependencies are importable."""
        return all(
            (
                self.python_training_stack_ready,
                self.peft_installed,
                self.trl_installed,
                self.bitsandbytes_installed,
            )
        )


@dataclass(frozen=True)
class TrainingExecutionPlan:
    """Backend-specific Track 20 execution plan."""

    backend: TrainingBackend
    device: str
    ci_safe: bool
    smoke_test: bool
    max_records: int
    max_steps: int
    per_device_batch_size: int
    gradient_accumulation_steps: int
    mixed_precision: str | None
    allow_model_download: bool
    allow_hub_push: bool
    suitable_tasks: tuple[str, ...]
    blockers: tuple[str, ...] = field(default_factory=tuple)
    notes: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-compatible plan."""
        return asdict(self)


def detect_training_runtime() -> TrainingRuntimeProfile:
    """Detect local Track 20 training capabilities without downloading models."""
    torch_version: str | None = None
    cuda_available = False
    mps_available = False
    rocm_available = False
    if _has_module("torch"):
        try:
            import torch

            torch_version = str(torch.__version__)
            cuda_available = bool(torch.cuda.is_available())
            mps_available = bool(
                hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
            )
            rocm_available = bool(getattr(torch.version, "hip", None))
        except (ImportError, RuntimeError, OSError):
            torch_version = None

    return TrainingRuntimeProfile(
        platform=platform.system(),
        machine=platform.machine(),
        cpu_count=os.cpu_count() or 1,
        ci=_env_flag("CI") or _env_flag("GITHUB_ACTIONS"),
        torch_installed=_has_module("torch"),
        torch_version=torch_version,
        cuda_available=cuda_available,
        mps_available=mps_available,
        rocm_available=rocm_available,
        directml_available=_has_module("torch_directml"),
        onnxruntime_installed=_has_module("onnxruntime"),
        transformers_installed=_has_module("transformers"),
        datasets_installed=_has_module("datasets"),
        peft_installed=_has_module("peft"),
        trl_installed=_has_module("trl"),
        bitsandbytes_installed=_has_module("bitsandbytes"),
        wandb_installed=_has_module("wandb"),
        hf_cli_available=shutil.which("hf") is not None,
        nvidia_smi_available=shutil.which("nvidia-smi") is not None,
    )


def choose_training_execution_plan(
    profile: TrainingRuntimeProfile | None = None,
    *,
    prefer_backend: TrainingBackend | None = None,
) -> TrainingExecutionPlan:
    """Choose a Track 20 execution plan for the detected environment."""
    resolved = profile or detect_training_runtime()
    backend = prefer_backend or _default_backend(resolved)
    blockers = _backend_blockers(resolved, backend)
    if backend == "ci_cpu":
        return TrainingExecutionPlan(
            backend=backend,
            device="cpu",
            ci_safe=True,
            smoke_test=True,
            max_records=8,
            max_steps=2,
            per_device_batch_size=1,
            gradient_accumulation_steps=1,
            mixed_precision=None,
            allow_model_download=False,
            allow_hub_push=False,
            suitable_tasks=("mlm_smoke", "metrics", "job_spec", "data_split"),
            blockers=tuple(blockers),
            notes=(
                "Designed for GitHub Actions and other no-GPU runners.",
                "Uses tiny fixtures and no Hub writes.",
            ),
        )
    if backend in {"local_cpu", "onnx_cpu"}:
        return TrainingExecutionPlan(
            backend=backend,
            device="cpu",
            ci_safe=backend == "onnx_cpu",
            smoke_test=True,
            max_records=32,
            max_steps=5,
            per_device_batch_size=1,
            gradient_accumulation_steps=1,
            mixed_precision=None,
            allow_model_download=False,
            allow_hub_push=False,
            suitable_tasks=("mlm_smoke", "metrics", "job_spec", "data_split"),
            blockers=tuple(blockers),
            notes=("Suitable for bounded local proof runs, not publication-quality training.",),
        )
    if backend == "directml":
        device = "privateuseone"
        precision = None
    elif backend == "mps":
        device = "mps"
        precision = "fp16"
    elif backend == "rocm":
        device = "cuda"
        precision = "bf16"
    else:
        device = "cuda"
        precision = "bf16"
    return TrainingExecutionPlan(
        backend=backend,
        device=device,
        ci_safe=False,
        smoke_test=False,
        max_records=0,
        max_steps=100_000,
        per_device_batch_size=1 if backend in {"cuda", "rocm"} else 2,
        gradient_accumulation_steps=16 if backend in {"cuda", "rocm"} else 4,
        mixed_precision=precision,
        allow_model_download=True,
        allow_hub_push=False,
        suitable_tasks=("mlm", "citation", "deontic", "entity", "qa", "maori"),
        blockers=tuple(blockers),
        notes=("Hub publication remains an explicit opt-in even on accelerated backends.",),
    )


def render_runtime_plan_json(
    profile: TrainingRuntimeProfile | None = None,
    *,
    prefer_backend: TrainingBackend | None = None,
) -> str:
    """Render detected runtime and selected plan as stable JSON."""
    resolved = profile or detect_training_runtime()
    plan = choose_training_execution_plan(resolved, prefer_backend=prefer_backend)
    return json.dumps(
        {"profile": asdict(resolved), "selected_plan": plan.to_dict()},
        indent=2,
        sort_keys=True,
    )


def main() -> int:
    """Print the detected Track 20 runtime plan."""
    sys.stdout.write(f"{render_runtime_plan_json()}\n")
    return 0


def _default_backend(profile: TrainingRuntimeProfile) -> TrainingBackend:
    """Return the best backend for the detected environment."""
    candidates: tuple[tuple[bool, TrainingBackend], ...] = (
        (profile.ci, "ci_cpu"),
        (profile.cuda_available, "cuda"),
        (profile.rocm_available, "rocm"),
        (profile.mps_available, "mps"),
        (profile.directml_available, "directml"),
        (profile.onnxruntime_installed, "onnx_cpu"),
    )
    for available, backend in candidates:
        if available:
            return backend
    return "local_cpu"


def _backend_blockers(profile: TrainingRuntimeProfile, backend: TrainingBackend) -> list[str]:
    """Return blockers for a requested backend."""
    blockers: list[str] = []
    if not profile.python_training_stack_ready:
        blockers.append("Core Python training stack is not importable")
    if backend in {"cuda", "rocm"} and not profile.qlora_stack_ready:
        blockers.append("QLoRA stack is not fully importable")
    if backend == "cuda" and not profile.cuda_available:
        blockers.append("CUDA is not available to PyTorch")
    if backend == "rocm" and not profile.rocm_available:
        blockers.append("ROCm/HIP PyTorch runtime is not available")
    if backend == "mps" and not profile.mps_available:
        blockers.append("Apple MPS runtime is not available")
    if backend == "directml" and not profile.directml_available:
        blockers.append("torch-directml is not installed")
    if backend == "onnx_cpu" and not profile.onnxruntime_installed:
        blockers.append("onnxruntime is not installed")
    return blockers


def _has_module(name: str) -> bool:
    """Return whether a module can be imported."""
    return importlib.util.find_spec(name) is not None


def _env_flag(name: str) -> bool:
    """Return whether an environment flag is truthy."""
    return os.getenv(name, "").casefold() in {"1", "true", "yes"}


if __name__ == "__main__":
    raise SystemExit(main())
