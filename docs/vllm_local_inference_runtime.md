# vLLM Local Inference Runtime Evaluation

Track 62 keeps vLLM optional. The repository uses it only when a local Linux
deployment can prove a useful throughput win without breaking the existing
Python fallback.

## Supported runtime modes

- Offline generation through the vLLM `LLM` API on a local machine with the
  optional `vllm` extra installed.
- OpenAI-compatible endpoint mode against a local vLLM server.
- Deterministic fixture-backed tests in CI, including a fake completion server.

## Unsupported runtime modes

- Required import-time dependency on vLLM.
- Windows-only development that expects vLLM to be present.
- Replacing deterministic extraction, schema projection, or publication
  assembly with a generation runtime.
- Unbounded production GPU reliance without a later review gate.

## Integration points

- DSPy can target the OpenAI-compatible endpoint when a prompt/program
  optimizer needs a local generation backend.
- spaCy-llm can also point at the same endpoint for optional annotation or
  extraction experiments.
- The repository keeps those integrations optional; the Python fallback remains
  the default path.

## Decision record

Track 62 records vLLM as optional, not default. A later track can promote it
only if benchmark evidence and deployment evidence justify that change.
