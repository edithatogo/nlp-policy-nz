#!/usr/bin/env bash
set -euo pipefail

# Dry-run entrypoint: emits an auditable QLoRA job spec only.
python -m nlp_policy_nz.training.run_qlora \
  --print-spec \
  --model-name mistralai/Mistral-Nemo-Base-2407 \
  --task entity \
  --output-dir models/mistral-nemo-entity \
  --hub-model-id nlp-policy-nz/mistral-nemo-entity \
  "$@"
