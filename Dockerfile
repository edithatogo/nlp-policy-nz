# syntax=docker/dockerfile:1.7

FROM python:3.13-slim-bookworm AS builder

ENV DEBIAN_FRONTEND=noninteractive \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIXI_HOME=/opt/pixi \
    PIXI_CACHE_DIR=/opt/pixi-cache \
    PATH=/opt/pixi/bin:/root/.local/bin:$PATH

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential ca-certificates curl git \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://pixi.sh/install.sh -o /tmp/pixi-install.sh \
    && sh /tmp/pixi-install.sh -b /opt/pixi/bin \
    && rm /tmp/pixi-install.sh

WORKDIR /app

COPY pyproject.toml pixi.toml pixi.lock README.md Dockerfile .dockerignore .tach.toml docker-compose.yml ./
COPY .devcontainer ./.devcontainer
COPY .github ./.github
COPY src ./src
COPY scripts ./scripts
COPY spaces ./spaces
COPY tests ./tests
COPY docs ./docs
COPY config ./config
COPY conductor ./conductor

RUN pixi install -e py312 --frozen --skip-with-deps semgrep --skip-with-deps scalene


FROM python:3.13-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH=/opt/pixi/bin:/app/.pixi/envs/default/bin:/usr/local/bin:/usr/local/sbin:/usr/sbin:/usr/bin:/bin

RUN useradd --create-home --uid 10001 --shell /usr/sbin/nologin appuser

WORKDIR /app

COPY --from=builder /opt/pixi /opt/pixi
COPY --from=builder /app /app

RUN chown -R appuser:appuser /app

USER appuser

HEALTHCHECK --interval=30s --timeout=5s --start-period=30s --retries=3 \
    CMD python -c "import nlp_policy_nz; print(nlp_policy_nz.__version__)" || exit 1

CMD ["nlp-policy-nz", "--help"]
