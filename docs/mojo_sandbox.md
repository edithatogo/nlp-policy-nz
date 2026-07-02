# Mojo Sandbox

Track 71 keeps Mojo optional and Linux-only. The sandbox exists to prove two things:

1. the repo can install and run Mojo in a temporary Linux CI project, and
2. the Python reference payload stays byte-for-byte comparable with the Mojo output fixture.

## Usage

Run the reference helper locally:

```bash
pixi run python -m experiments.mojo.sandbox --json
```

In GitHub Actions, the sandbox job creates a temporary Pixi project, installs `mojo`,
runs `experiments/mojo/kernel.mojo`, and compares the output with the Python reference.

## Skip behavior

- Non-Linux runners report the sandbox as skipped.
- Linux runners without a `mojo` executable report the sandbox as skipped.
- The sandbox never blocks the default CI matrix.

## Removal criteria

Remove or archive the sandbox when any of these become true:

- it does not produce a measurable gain over Python or a Rust-backed alternative,
- it breaks parity with the Python reference payload,
- it starts blocking ordinary validation, or
- a simpler runtime option proves better for the same kernel.

