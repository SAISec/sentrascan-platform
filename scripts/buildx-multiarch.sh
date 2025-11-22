#!/usr/bin/env bash
set -euo pipefail

# Build and optionally push a multi-architecture Docker image for SentraScan.
# Usage:
#   scripts/buildx-multiarch.sh <image_tag> [--push]
# Examples:
#   scripts/buildx-multiarch.sh sentrascan/platform:dev
#   scripts/buildx-multiarch.sh ghcr.io/yourorg/sentrascan:latest --push

TAG=${1:-sentrascan/platform:dev}
PUSH=${2:-}

# Ensure buildx is available
if ! docker buildx version >/dev/null 2>&1; then
  echo "docker buildx not available. Install Docker Desktop or enable buildx." >&2
  exit 1
fi

# Create and use a builder if one is not set up
if ! docker buildx inspect multiarch-builder >/dev/null 2>&1; then
  docker buildx create --name multiarch-builder --use
else
  docker buildx use multiarch-builder
fi

ARGS=(--platform linux/amd64,linux/arm64 -t "$TAG" .)
if [[ "$PUSH" == "--push" ]]; then
  docker buildx build "${ARGS[@]}" --push
else
  docker buildx build "${ARGS[@]}"
fi

echo "Built multi-arch image: $TAG"
