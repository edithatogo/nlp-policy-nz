# Track 47: Cross-Platform CI Matrix & Binary Distribution

**Dependencies**: Tracks 1, 23, 38
**Parallelization Node**: CI/CD Automation
**Status**: Planned

## Goal

Extend CI from ubuntu-only to a full platform matrix (ubuntu, windows, macOS), resolve platform-specific issues, and provide binary distribution for end users who cannot run pixi or Docker.

## Scope

### 1. Cross-Platform CI Matrix
- `.github/workflows/ci.yml`: add `strategy.matrix.os` with `[ubuntu-latest, windows-latest, macos-latest]`
- Platform-specific steps for pixi setup, caching, and dependency installation
- Platform-specific test exclusions/skips for known incompatibilities
- Conditional job outputs: report per-platform pass/fail

### 2. Platform-Specific Fixes
- Windows: path separator (`\` vs `/`), file locking, long-path support
- macOS: SIP (System Integrity Protection) interactions, temp directory
- Linux: glibc version compatibility for binary wheels
- Cross-platform CI environment variables (`CI`, `PYTHONUTF8`, `SYSTEMROOT`)

### 3. Binary Distribution
- `.github/workflows/build-binaries.yml`: PyInstaller or briefcase standalone executable per platform
- Upload platform-specific artifacts to GitHub Release
- Document system requirements (glibc, macOS min version, Windows VC redist)

### 4. Version Matrix Testing
- Test against Python 3.11 and 3.12 (and 3.13 when pixi/pytorch support it)
- Document minimum Python version requirements

## Acceptance Criteria

- [ ] CI matrix runs ubuntu, windows, macOS in parallel on every PR and master push
- [ ] All platform-specific test exclusions are documented with links to upstream issues
- [ ] Platform-specific binary builds produce standalone executables
- [ ] Binary executables uploaded to GitHub Release pass smoke tests
- [ ] Minimum Python version documented in `pyproject.toml` `python_requires`
- [ ] CI matrix report shows all platform statuses in a single view
