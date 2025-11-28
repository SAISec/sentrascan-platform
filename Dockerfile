# Multi-stage build for SentraScan Platform with MCP tools always on
FROM python:3.11-slim AS wheels
WORKDIR /wheels
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ make && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir wheel
# Build wheels for MCP tools
RUN pip wheel --no-cache-dir mcp-checkpoint cisco-ai-mcp-scanner -w /wheels

FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl ca-certificates tar gzip git git-lfs \
    default-jre-headless libharfbuzz0b libfontconfig1 libfreetype6 \
  && rm -rf /var/lib/apt/lists/* \
  && git lfs install

# ZAP removed to reduce container size

# Install uv (for safe-run probe)
ENV PATH="/root/.local/bin:${PATH}"
RUN curl -fsSL https://astral.sh/uv/install.sh | sh

# Install pinned gitleaks and trufflehog binaries (multi-arch)
ARG GITLEAKS_VERSION=8.18.1
ARG TRUFFLEHOG_VERSION=3.78.0
RUN set -eux; \
    arch="$(uname -m)"; \
    if [ "$arch" = "x86_64" ] || [ "$arch" = "amd64" ]; then gl_arch="linux_x64"; th_arch="linux_amd64"; \
    elif [ "$arch" = "aarch64" ] || [ "$arch" = "arm64" ]; then gl_arch="linux_arm64"; th_arch="linux_arm64"; \
    else gl_arch="linux_x64"; th_arch="linux_amd64"; fi; \
    curl -fsSL -o /tmp/gitleaks.tgz "https://github.com/gitleaks/gitleaks/releases/download/v${GITLEAKS_VERSION}/gitleaks_${GITLEAKS_VERSION}_${gl_arch}.tar.gz" && \
    tar -C /usr/local/bin -xzf /tmp/gitleaks.tgz gitleaks && chmod +x /usr/local/bin/gitleaks && rm -f /tmp/gitleaks.tgz; \
    curl -fsSL -o /tmp/trufflehog.tgz "https://github.com/trufflesecurity/trufflehog/releases/download/v${TRUFFLEHOG_VERSION}/trufflehog_${TRUFFLEHOG_VERSION}_${th_arch}.tar.gz" && \
    tar -C /usr/local/bin -xzf /tmp/trufflehog.tgz trufflehog && chmod +x /usr/local/bin/trufflehog && rm -f /tmp/trufflehog.tgz

# Copy dependency files first (for better layer caching)
COPY pyproject.toml README.md /app/
COPY --from=wheels /wheels /wheels

# Install base Python dependencies (without the package itself)
# This layer will be cached unless dependencies change
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir semgrep \
 && pip install --no-cache-dir /wheels/* \
 && (pip install --no-cache-dir 'mcp>=1.0.0' || true) \
 && pip install --no-cache-dir pytest pytest-playwright requests

# Install Playwright browsers (required for UI tests)
# This is separate so browser installs are cached
RUN playwright install chromium \
 && playwright install-deps chromium

# Copy source code (needed for editable install)
# This layer rebuilds when code changes, but dependencies above are cached
COPY src/ /app/src/
# Copy tests (for running tests in container)
COPY tests/ /app/tests/
# Copy documentation (for docs viewer)
COPY docs/ /app/docs/

# Install the package in editable mode (fast since dependencies are already installed)
RUN pip install --no-cache-dir -e .

# Create runtime dirs
RUN mkdir -p /data /reports /sboms /cache
ENV DATABASE_URL=postgresql+psycopg2://sentrascan:changeme@db:5432/sentrascan

# Expose API
EXPOSE 8200
CMD ["sentrascan", "server", "--host", "0.0.0.0", "--port", "8200"]
