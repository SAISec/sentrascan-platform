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

# Install OWASP ZAP (stable) into /opt/zap
ARG ZAP_VERSION_UNDERSCORE=2_15_0
ARG ZAP_VERSION_DOTTED=2.15.0
RUN set -eux; \
    curl -fsSL -o /tmp/ZAP_${ZAP_VERSION_UNDERSCORE}_unix.sh "https://github.com/zaproxy/zaproxy/releases/download/v${ZAP_VERSION_DOTTED}/ZAP_${ZAP_VERSION_UNDERSCORE}_unix.sh" && \
    chmod +x /tmp/ZAP_${ZAP_VERSION_UNDERSCORE}_unix.sh && \
    /tmp/ZAP_${ZAP_VERSION_UNDERSCORE}_unix.sh -q -dir /opt/zap && \
    ln -sf /opt/zap/zap-baseline.py /usr/local/bin/zap-baseline.py && \
    ln -sf /opt/zap/zap.sh /usr/local/bin/zap.sh && \
    rm -f /tmp/ZAP_${ZAP_VERSION_UNDERSCORE}_unix.sh

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

# Copy source and wheels
COPY . /app/
COPY --from=wheels /wheels /wheels

# Install app, semgrep, MCP tools, and optional mcp client
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
 && pip install --no-cache-dir -e . \
 && pip install --no-cache-dir semgrep \
 && pip install --no-cache-dir /wheels/* \
 && (pip install --no-cache-dir 'mcp>=1.0.0' || true)

# Create runtime dirs
RUN mkdir -p /data /reports /sboms /cache
ENV DATABASE_URL=postgresql+psycopg2://sentrascan:changeme@db:5432/sentrascan

# Expose API
EXPOSE 8200
CMD ["sentrascan", "server", "--host", "0.0.0.0", "--port", "8200"]
