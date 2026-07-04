"""Track 75 NZ legislation/Hansard fine-tuning closeout helpers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any, Literal

from nlp_policy_nz.semantic.finetune import FineTuneConfig, build_mlm_job_spec
from nlp_policy_nz.semantic.model_loader import DEFAULT_MODEL, FALLBACK_MODEL
from nlp_policy_nz.training.track74_evaluation import (
    default_track74_manifest,
    evaluate_track74_manifest,
)

ROOT = Path(__file__).resolve().parents[3]
TRACK75_TRACK_ID = "track75_nz_legislation_hansard_finetuned_model_20260704"
DEFAULT_TRACK75_OUTPUT_DIR = "models/nz-legislation-hansard-finetuned"
DEFAULT_TRACK75_SEED = 20260704
DEFAULT_TRACK75_TRACK74_MANIFEST_PATH = "data/track74/held_out_evaluation_set.json"
DEFAULT_TRACK75_RUN_RECORD_PATH = (
    "conductor/tracks/archive/track75_nz_legislation_hansard_finetuned_model_20260704/run_record.json"
)
DEFAULT_TRACK75_MODEL_CARD_PATH = (
    "conductor/tracks/archive/track75_nz_legislation_hansard_finetuned_model_20260704/model_card.md"
)

Track75Decision = Literal["promote", "defer"]


@dataclass(frozen=True, slots=True)
class Track75ArtifactLayout:
    """Repo-side artifact layout for the Track 75 closeout."""

    model_output_dir: str
    model_card_path: str
    run_record_path: str
    track74_manifest_path: str
    fallback_path: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready artifact layout."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Track75ComparisonSummary:
    """Repo-side comparison summary against the Track 74 baseline."""

    track74_manifest_id: str
    track74_overall_score: float
    track74_promotion_threshold: float
    promotion_margin: float
    promotion_ready: bool
    fine_tuned_model_score: float | None
    decision: Track75Decision
    decision_reason: str

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready comparison summary."""
        return asdict(self)


@dataclass(frozen=True, slots=True)
class Track75RunRecord:
    """Repo-side run record for the Track 75 fine-tuning closeout."""

    track_id: str
    training_seed: int
    training_job_spec: dict[str, Any]
    training_data_manifest_path: str
    training_data_manifest_id: str
    training_data_manifest_hash: str
    artifact_layout: Track75ArtifactLayout
    comparison: Track75ComparisonSummary
    residual_external_gates: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-ready run record."""
        return {
            "track_id": self.track_id,
            "training_seed": self.training_seed,
            "training_job_spec": self.training_job_spec,
            "training_data_manifest_path": self.training_data_manifest_path,
            "training_data_manifest_id": self.training_data_manifest_id,
            "training_data_manifest_hash": self.training_data_manifest_hash,
            "artifact_layout": self.artifact_layout.to_dict(),
            "comparison": self.comparison.to_dict(),
            "residual_external_gates": list(self.residual_external_gates),
        }


def default_track75_config() -> FineTuneConfig:
    """Return the default Track 75 fine-tuning configuration."""
    return FineTuneConfig(
        model_name=DEFAULT_MODEL,
        output_dir=DEFAULT_TRACK75_OUTPUT_DIR,
        max_length=128,
        batch_size=16,
        learning_rate=2e-5,
        num_epochs=3,
        warmup_ratio=0.1,
        push_to_hub=False,
        hub_model_id="",
    )


def default_track75_artifact_layout(
    config: FineTuneConfig | None = None,
) -> Track75ArtifactLayout:
    """Return the default Track 75 artifact layout."""
    resolved = config or default_track75_config()
    return Track75ArtifactLayout(
        model_output_dir=resolved.output_dir,
        model_card_path=DEFAULT_TRACK75_MODEL_CARD_PATH,
        run_record_path=DEFAULT_TRACK75_RUN_RECORD_PATH,
        track74_manifest_path=DEFAULT_TRACK75_TRACK74_MANIFEST_PATH,
        fallback_path="nlp_policy_nz.semantic.model_loader:load_model",
    )


def default_track75_comparison_summary() -> Track75ComparisonSummary:
    """Return the default Track 75 comparison summary."""
    manifest = default_track74_manifest()
    report = evaluate_track74_manifest(manifest)
    decision = "promote" if report.promotion_ready else "defer"
    reason = (
        "Track 74 baseline clears the promotion threshold"
        if report.promotion_ready
        else (
            "Track 74 baseline remains below the promotion threshold; defer live model "
            "promotion until a measured live fine-tuned run improves the held-out score"
        )
    )
    return Track75ComparisonSummary(
        track74_manifest_id=manifest.track_id,
        track74_overall_score=report.overall_score,
        track74_promotion_threshold=report.promotion_threshold,
        promotion_margin=round(report.overall_score - report.promotion_threshold, 4),
        promotion_ready=report.promotion_ready,
        fine_tuned_model_score=None,
        decision=decision,
        decision_reason=reason,
    )


def build_track75_run_record(config: FineTuneConfig | None = None) -> Track75RunRecord:
    """Build the deterministic Track 75 run record."""
    resolved = config or default_track75_config()
    manifest = default_track74_manifest()
    comparison = default_track75_comparison_summary()
    job_spec = build_mlm_job_spec(resolved).to_dict()
    manifest_hash = sha256(
        json.dumps(manifest.to_dict(), sort_keys=True, ensure_ascii=False).encode("utf-8")
    ).hexdigest()
    return Track75RunRecord(
        track_id=TRACK75_TRACK_ID,
        training_seed=DEFAULT_TRACK75_SEED,
        training_job_spec=job_spec,
        training_data_manifest_path=DEFAULT_TRACK75_TRACK74_MANIFEST_PATH,
        training_data_manifest_id=manifest.track_id,
        training_data_manifest_hash=manifest_hash,
        artifact_layout=default_track75_artifact_layout(resolved),
        comparison=comparison,
        residual_external_gates=(
            "Live fine-tuning run on the selected model",
            "Measured evaluation on the Track 74 held-out set",
            "Model card publication with artifact hashes",
            "Optional Hugging Face Hub publication after promotion approval",
        ),
    )


def render_track75_run_record_json(config: FineTuneConfig | None = None) -> str:
    """Return the Track 75 run record as formatted JSON."""
    return json.dumps(build_track75_run_record(config).to_dict(), indent=2, ensure_ascii=False) + "\n"


def render_track75_model_card_markdown(config: FineTuneConfig | None = None) -> str:
    """Return the Track 75 model card as Markdown."""
    resolved = config or default_track75_config()
    record = build_track75_run_record(resolved)
    comparison = record.comparison
    layout = record.artifact_layout
    lines = [
        "# Track 75: NZ Legislation/Hansard Fine-Tuned Model",
        "",
        "## Summary",
        "",
        (
            "This track records the reproducible fine-tuning recipe, artifact layout, "
            "and promotion decision for the NZ legislation/Hansard model follow-up to Track 74."
        ),
        "",
        "## Tracked Inputs",
        "",
        f"- Baseline model: `{resolved.model_name}`",
        f"- Fallback model: `{FALLBACK_MODEL}`",
        f"- Training seed: `{record.training_seed}`",
        f"- Track 74 manifest: `{layout.track74_manifest_path}`",
        f"- Track 74 manifest id: `{record.training_data_manifest_id}`",
        f"- Promotion threshold: `{comparison.track74_promotion_threshold:.4f}`",
        f"- Track 74 baseline score: `{comparison.track74_overall_score:.4f}`",
        f"- Promotion margin: `{comparison.promotion_margin:.4f}`",
        "",
        "## Artifact Layout",
        "",
        f"- Model output dir: `{layout.model_output_dir}`",
        f"- Model card: `{layout.model_card_path}`",
        f"- Run record: `{layout.run_record_path}`",
        f"- Fallback reference: `{layout.fallback_path}`",
        "",
        "## Decision",
        "",
        f"- Promotion ready: `{comparison.promotion_ready}`",
        f"- Decision: `{comparison.decision}`",
        f"- Reason: {comparison.decision_reason}",
        "",
        "## Residual External Gates",
        "",
    ]
    lines.extend(f"- {gate}" for gate in record.residual_external_gates)
    return "\n".join(lines) + "\n"


def render_track75_closeout_markdown(config: FineTuneConfig | None = None) -> str:
    """Return a concise Track 75 closeout summary."""
    record = build_track75_run_record(config)
    comparison = record.comparison
    lines = [
        "# Track 75 Closeout",
        "",
        f"- Track id: `{record.track_id}`",
        f"- Training seed: `{record.training_seed}`",
        f"- Decision: `{comparison.decision}`",
        f"- Promotion ready: `{comparison.promotion_ready}`",
        f"- Promotion margin: `{comparison.promotion_margin:.4f}`",
        "",
        "## Residual External Gates",
        "",
    ]
    lines.extend(f"- {gate}" for gate in record.residual_external_gates)
    return "\n".join(lines) + "\n"
