#!/usr/bin/env bash
set -euo pipefail

# Dry-run entrypoint: emits an auditable QLoRA job spec only.
python -m nlp_policy_nz.training.run_qlora \
  --print-spec \
  --model-name microsoft/phi-4 \
  --task deontic \
  --output-dir models/phi-4-deontic \
  --hub-model-id nlp-policy-nz/phi-4-deontic \
  "$@"
