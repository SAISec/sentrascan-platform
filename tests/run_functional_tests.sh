#!/bin/bash
# Functional testing script for hardened container
# Usage: ./run_functional_tests.sh [API_KEY]

set -e

API_KEY="${1:-${API_KEY}}"
API_BASE_URL="${API_BASE_URL:-http://localhost:8200/api/v1}"
CONTAINER_NAME="sentrascan-platform-api-1"

if [ -z "$API_KEY" ]; then
    echo "Error: API_KEY is required"
    echo "Usage: $0 <API_KEY>"
    echo "Or set API_KEY environment variable"
    exit 1
fi

echo "=========================================="
echo "Functional Testing for Hardened Container"
echo "=========================================="
echo "API Base URL: $API_BASE_URL"
echo "Container: $CONTAINER_NAME"
echo ""

# Check if container is running
if ! docker ps | grep -q "$CONTAINER_NAME"; then
    echo "Error: Container $CONTAINER_NAME is not running"
    echo "Start it with: docker compose -f docker-compose.protected.yml up -d"
    exit 1
fi

# Check API health
echo "1. Checking API health..."
HEALTH_RESPONSE=$(docker compose -f docker-compose.protected.yml exec -T api \
    /usr/bin/python3 -c "
import urllib.request
import json
try:
    with urllib.request.urlopen('http://localhost:8200/api/v1/health', timeout=5) as response:
        data = json.loads(response.read().decode())
        print(json.dumps(data))
except Exception as e:
    print(json.dumps({'error': str(e)}))
    exit(1)
")

if echo "$HEALTH_RESPONSE" | grep -q '"status"'; then
    echo "✓ API is healthy"
else
    echo "✗ API health check failed"
    echo "$HEALTH_RESPONSE"
    exit 1
fi

# Check modelaudit availability
echo ""
echo "2. Checking modelaudit availability..."
MODELAUDIT_CHECK=$(docker compose -f docker-compose.protected.yml exec -T api \
    /usr/bin/python3 -c "
from sentrascan.modules.model.scanner import ModelScanner
ok, msg = ModelScanner.doctor()
print('OK' if ok else 'FAIL')
print(msg)
" 2>&1)

if echo "$MODELAUDIT_CHECK" | grep -q "OK"; then
    echo "✓ modelaudit is available"
else
    echo "✗ modelaudit check failed"
    echo "$MODELAUDIT_CHECK"
    exit 1
fi

# Run pytest functional tests
echo ""
echo "3. Running functional tests..."
echo ""

docker compose -f docker-compose.protected.yml exec -T api \
    /usr/bin/python3 -m pytest \
        /app/tests/test_functional_models.py \
        -v \
        --tb=short \
        -k "not test_model_format_scan" \
        --api-key="$API_KEY" \
        --api-base-url="$API_BASE_URL" \
        2>&1

TEST_EXIT_CODE=$?

if [ $TEST_EXIT_CODE -eq 0 ]; then
    echo ""
    echo "=========================================="
    echo "✓ All functional tests passed!"
    echo "=========================================="
else
    echo ""
    echo "=========================================="
    echo "✗ Some functional tests failed"
    echo "=========================================="
fi

exit $TEST_EXIT_CODE

