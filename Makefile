.PHONY: install test lint format typecheck check clean coverage benchmark docker devcontainer security audit ci-all conductor-status track-implement track-new

# === Environment ===
install:
	pixi install

# === Quality ===
test:
	pixi run test

lint:
	pixi run lint

format:
	pixi run format

typecheck:
	pixi run typecheck

check: lint format typecheck test

coverage:
	pixi run coverage

clean:
	rm -rf .tmp/ artifacts/ build/ dist/ *.egg-info __pycache__/ .pytest_cache/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true

# === Security ===
security-sast:
	pixi run bandit -c .bandit -r src/nlp_policy_nz/ -lll -iii
	pixi run semgrep scan --config p/python --severity WARNING --error --metrics=off src/nlp_policy_nz/

security-deps:
	pixi run python scripts/check_dependency_security.py

security-secrets:
	pixi run detect-secrets scan --baseline .secrets.baseline

security-secrets:
	pre-commit run detect-secrets --all-files

security: security-sast security-secrets security-deps

# === Performance ===
benchmark:
	pixi run benchmark

profile:
	pixi run profile

# === Container ===
docker-build:
	docker build -t nlp-policy-nz .

docker-test:
	docker run --rm nlp-policy-nz pixi run check

# === Conductor ===
conductor-status:
	@echo "=== nlp-policy-nz Track Audit ==="
	@for d in conductor/tracks/track*/; do \
		f=$$(basename $$d); \
		s=$$([ -f "$$d/spec.md" ] && echo "Y" || echo "N"); \
		p=$$([ -f "$$d/plan.md" ] && echo "Y" || echo "N"); \
		m=$$([ -f "$$d/metadata.json" ] && echo "Y" || echo "N"); \
		echo "  $$f  [spec:$$s plan:$$p meta:$$m]"; \
	done
	@echo "  Total: $$(ls -d conductor/tracks/track*/ | wc -l) tracks"

track-implement:
	@@echo "Use: conductor-implement (via Claude Code /conductor-implement)"

track-new:
	@@echo "Use: conductor-newtrack (via Claude Code /conductor-newtrack)"

# === CI ===
ci-all: lint-ci format-ci typecheck-ci coverage-ci

lint-ci:
	pixi run lint-ci

format-ci:
	pixi run format-ci

typecheck-ci:
	pixi run typecheck-ci

coverage-ci:
	pixi run coverage-ci

# === Pre-commit ===
hooks-install:
	pixi run install-git-hooks

hooks-run:
	pre-commit run --all-files

# === Help ===
help:
	@@echo "nlp-policy-nz Makefile"
	@@echo ""
	@@echo "Environment:"
	@@echo "  install          Install pixi environment"
	@@echo "Quality:"
	@@echo "  test             Run pytest"
	@@echo "  lint             Run ruff + vale"
	@@echo "  format           Run ruff format"
	@@echo "  typecheck        Run basedpyright"
	@@echo "  check            Run all quality gates (lint + format + typecheck + test)"
	@@echo "  coverage         Run tests with coverage"
	@@echo "  clean            Clean build artifacts"
	@@echo "Security:"
	@@echo "  security-sast    Run Bandit and Semgrep scans"
	@@echo "  security-deps    Run pip-audit vulnerability scan"
	@@echo "  security-secrets  Run detect-secrets scan"
	@@echo "  security         Run all security scans"
	@@echo "Performance:"
	@@echo "  benchmark        Run pytest-benchmark"
	@@echo "  profile          Run Scalene profiler"
	@@echo "Container:"
	@@echo "  docker-build     Build Docker image"
	@@echo "  docker-test      Test Docker image"
	@@echo "Conductor:"
	@@echo "  conductor-status  Show all track files status"
	@@echo "  track-implement  Continue active track"
	@@echo "  track-new        Create new track"
	@@echo "Pre-commit:"
	@@echo "  hooks-install    Install git hooks"
	@@echo "  hooks-run        Run pre-commit on all files"
