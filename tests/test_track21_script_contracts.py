from __future__ import annotations

from pathlib import Path

SCRIPT_NAMES = (
    "evaluate_mor.sh",
    "evaluate_mamba.sh",
    "evaluate_ttt.sh",
    "evaluate_diffusion_gemma.sh",
)


def test_track21_evaluation_scripts_are_audit_only_by_default() -> None:
    root = Path(__file__).resolve().parents[1]

    for script_name in SCRIPT_NAMES:
        script = (root / "scripts" / script_name).read_text(encoding="utf-8")

        assert "--live" in script
        assert "exit 64" in script
        assert "no clone, download, training, or Hub push" in script
        assert "HF_HUB_OFFLINE" in script
        assert "TRANSFORMERS_OFFLINE" in script
        assert "WANDB_DISABLED" in script
        assert "from nlp_policy_nz.training.eval_arch import main" in script
