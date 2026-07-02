# System Requirements

## Supported Platforms

- Windows 11 / Windows Server 2022
- macOS 13 or later
- Ubuntu 22.04 or later

## Python

- Minimum supported Python version: 3.11
- CI is exercised on Python 3.11 and 3.12

## Platform Notes

- Windows VC runtime (Microsoft Visual C++ runtime) is required for binary builds.
- macOS binary builds require Gatekeeper-compatible signing or local trust approval for ad hoc builds.
- Linux binary builds are validated against glibc-compatible runner images.

## Runtime Dependencies

- `pixi` for local development and test execution
- `torch`, `lancedb`, and `pyarrow` wheels that match the target platform
- Optional standalone binary builds are produced with PyInstaller
