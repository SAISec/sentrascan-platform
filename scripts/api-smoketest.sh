#!/usr/bin/env bash
set -euo pipefail

# Wait for API health
echo "Waiting for API health..."
until curl -sf http://localhost:8200/api/v1/health >/dev/null; do sleep 1; done
echo "API healthy."

# Create admin API key securely and insert hashed into DB (without printing secret)
ADMIN_API_KEY=$(python3 - <<'PY'
import secrets; print(secrets.token_urlsafe(32))
PY
)

KEY_HASH=$(python3 -c 'import sys,hashlib; print(hashlib.sha256(sys.argv[1].encode()).hexdigest())' "$ADMIN_API_KEY")

UUID=$(python3 - <<'PY'
import uuid; print(uuid.uuid4())
PY
)

docker compose exec -T db sh -lc "psql -U sentrascan -d sentrascan -qAt -c \"INSERT INTO api_keys (id,name,role,key_hash,is_revoked,created_at) VALUES ('$UUID','smoketest-admin','admin','$KEY_HASH', false, NOW());\""

# Smoke tests
printf "Health: "
curl -s http://localhost:8200/api/v1/health

echo
echo "List scans (0 expected initially):"
curl -s -H "x-api-key: $ADMIN_API_KEY" "http://localhost:8200/api/v1/scans?limit=5"

echo
echo "Trigger MCP scan (auto_discover):"
curl -s -H "x-api-key: $ADMIN_API_KEY" -H "content-type: application/json" -d '{"auto_discover": true}' http://localhost:8200/api/v1/mcp/scans

echo
echo "List scans (after):"
curl -s -H "x-api-key: $ADMIN_API_KEY" "http://localhost:8200/api/v1/scans?limit=5"

# Extract last scan id
LAST_ID=$(curl -s -H "x-api-key: $ADMIN_API_KEY" "http://localhost:8200/api/v1/scans?limit=1" | python3 - <<'PY'
import sys, json
data=json.load(sys.stdin)
print(data[0]['id'] if data else '')
PY
)

if [ -n "${LAST_ID:-}" ]; then
  echo
  echo "Scan detail (${LAST_ID}):"
  curl -s -H "x-api-key: $ADMIN_API_KEY" "http://localhost:8200/api/v1/scans/${LAST_ID}"
  echo
  echo "UI page check for /scan/${LAST_ID} (first lines):"
  curl -s "http://localhost:8200/scan/${LAST_ID}" | head -n 5
fi
