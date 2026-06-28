# Track 53 Recommendation

## Selected Roles

- Encoder baseline: isaacus/emubert
- Silver-label adjudicator: Equall/Saul-7B-Instruct-v1
- Retrieval candidate: Kanon 2 Embedder

## Tradeoffs

- EmuBERT is lighter and more local-friendly, while Legal-BERT is retained for comparison.
- Saul-7B gives a practical local/legal LLM option, but still needs privacy review.
- Kanon-style retrieval improves semantic search but may require proprietary or air-gapped access.

## Privacy Constraints

- Do not route sensitive NZ text to external services without explicit review.
- Silver-label outputs must remain separate from human-gold claims.

## Follow-Up

- Revisit after NZ-legislation fine-tuning to compare NZ-adapted encoders, legal LLM adjudicators, and frontier-model silver labelling.
