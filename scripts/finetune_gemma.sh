#!/usr/bin/env bash
set -euo pipefail

# Dry-run entrypoint: emits an auditable QLoRA job spec only.
python -m nlp_policy_nz.training.run_qlora \
  --print-spec \
  --model-name google/gemma-3-9b \
  --task citation \
  --output-dir models/gemma-3-9b-citation \
  --hub-model-id nlp-policy-nz/gemma-3-9b-citation \
  "$@"
