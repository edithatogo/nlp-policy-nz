# Track 36: Hugging Face Exploration Site

## Key Files

- `spaces/app.py`
- `spaces/README.md`
- `spaces/requirements.txt`
- `tests/test_gradio_space.py`
- `conductor/tracks/track36_huggingface_exploration_site_20260625/spec.md`
- `conductor/tracks/track36_huggingface_exploration_site_20260625/plan.md`
- `conductor/tracks/track36_huggingface_exploration_site_20260625/evidence.md`

## Implementation Decision

The repo-standard Hugging Face Space root is `spaces/`, and existing deployment tooling uploads that directory. Track 36 extends the existing Space rather than introducing a parallel `scripts/hf_space/` scaffold.
