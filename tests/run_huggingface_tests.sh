#!/bin/bash
# Test script for scanning Hugging Face models
# Usage: ./run_huggingface_tests.sh [API_KEY]

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
echo "Hugging Face Model Scanning Tests"
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

# Models to test
declare -a MODELS=(
    "Bingsu/yolo-world-mirror"
    "Adilbai/stock-trading-rl-agent"
    "lxyuan/distilbert-base-multilingual-cased-sentiments-student"
    "sentence-transformers/all-MiniLM-L6-v2"
    "deepseek-ai/DeepSeek-OCR"
)

# Test each model
for model in "${MODELS[@]}"; do
    echo "Testing: $model"
    echo "----------------------------------------"
    
    # Test with full URL
    docker compose -f docker-compose.protected.yml exec -T -e API_KEY="$API_KEY" -e API_BASE_URL="$API_BASE_URL" api \
        /usr/bin/python3 -c "
import requests
import os
import json
import sys

api_key = os.environ.get('API_KEY')
api_base = os.environ.get('API_BASE_URL', 'http://localhost:8200/api/v1')
model_url = f'https://huggingface.co/$model'

print(f'Scanning: {model_url}')

try:
    payload = {
        'paths': [model_url],
        'generate_sbom': True,
        'strict': False,
        'timeout': 300
    }
    
    response = requests.post(
        f'{api_base}/models/scans',
        headers={'X-API-Key': api_key, 'Content-Type': 'application/json'},
        json=payload,
        timeout=360
    )
    
    if response.status_code == 200:
        data = response.json()
        scan_id = data.get('scan_id') if isinstance(data, dict) else None
        if scan_id:
            print(f'  ✓ Scan created: {scan_id}')
            
            # Get scan details
            get_response = requests.get(
                f'{api_base}/scans/{scan_id}',
                headers={'X-API-Key': api_key},
                timeout=10
            )
            if get_response.status_code == 200:
                scan_data = get_response.json()
                scan_info = scan_data.get('scan', {})
                print(f'  Findings: {scan_info.get(\"critical\", 0)} critical, '
                      f'{scan_info.get(\"high\", 0)} high, '
                      f'{scan_info.get(\"medium\", 0)} medium, '
                      f'{scan_info.get(\"low\", 0)} low')
                print(f'  Status: {\"PASSED\" if scan_info.get(\"passed\") else \"FAILED\"}')
        else:
            print(f'  ✓ Scan completed (no scan_id in response)')
    elif response.status_code in [400, 422]:
        error_data = response.json()
        detail = error_data.get('detail', '')
        if 'not allowed' in detail.lower():
            print(f'  ✗ SSRF prevention blocked: {detail[:100]}')
        else:
            print(f'  ✗ Validation error: {detail[:100]}')
    else:
        print(f'  ✗ Failed: Status {response.status_code}')
        print(f'  Response: {response.text[:200]}')
except Exception as e:
    print(f'  ✗ Error: {e}')
    sys.exit(1)

print()
" 2>&1
    
    if [ $? -ne 0 ]; then
        echo "  ⚠ Test failed for $model"
    fi
    
    echo ""
done

echo "=========================================="
echo "Testing complete!"
echo "=========================================="

