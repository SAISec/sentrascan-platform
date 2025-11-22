#!/usr/bin/env bash
set -euo pipefail
API_BASE=${SENTRASCAN_API_BASE:-http://localhost:8200}
echo "Waiting for API at $API_BASE ..."
for i in {1..60}; do
  if curl -sf "$API_BASE/api/v1/health" >/dev/null; then
    break
  fi
  sleep 1
  if [ "$i" -eq 60 ]; then
    echo "API not ready" >&2
    exit 1
  fi
done
pytest -q -m integration
