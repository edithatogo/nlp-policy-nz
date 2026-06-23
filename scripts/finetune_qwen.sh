#!/usr/bin/env bash
set -euo pipefail

# Dry-run entrypoint: emits an auditable QLoRA job spec only.
python -m nlp_policy_nz.training.run_qlora \
  --print-spec \
  --model-name Qwen/Qwen2.5-7B \
  --task qa \
  --output-dir models/qwen2.5-7b-nz-qa \
  --hub-model-id nlp-policy-nz/qwen2.5-7b-nz-qa \
  "$@"
