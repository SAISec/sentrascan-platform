# Functional Testing Guide for Hardened Container

## Quick Start

### Prerequisites

1. **Hardened container running**:
   ```bash
   docker compose -f docker-compose.protected.yml up -d
   ```

2. **API key created**:
   ```bash
   # Create via web UI or CLI
   docker compose -f docker-compose.protected.yml exec api \
     /usr/bin/python3 -m sentrascan.cli user create-super-admin
   ```

3. **Test models prepared** (optional, for format-specific tests):
   ```bash
   mkdir -p test-data/models
   # Copy or generate test model files here
   ```

### Method 1: API-Based Testing (Recommended)

**Best for:** End-to-end testing, verifying full stack functionality

```bash
# Set API key
export API_KEY="ss-proj-h_your-api-key-here"
export API_BASE_URL="http://localhost:8200/api/v1"

# Run functional tests
docker compose -f docker-compose.protected.yml exec api \
  /usr/bin/python3 -m pytest /app/tests/test_functional_models.py \
    -v \
    --api-key="$API_KEY" \
    --api-base-url="$API_BASE_URL"
```

### Method 2: Manual API Testing

**Best for:** Quick validation, debugging specific issues

```bash
# 1. Health check
curl http://localhost:8200/api/v1/health

# 2. Create model scan
curl -X POST http://localhost:8200/api/v1/models/scans \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "paths": ["/test-data/models/test_model.pkl"],
    "generate_sbom": true,
    "strict": false
  }'

# 3. Get scan details (use scan_id from previous response)
curl http://localhost:8200/api/v1/scans/{scan_id} \
  -H "X-API-Key: $API_KEY"

# 4. List scans
curl "http://localhost:8200/api/v1/scans?type=model&limit=10" \
  -H "X-API-Key: $API_KEY"
```

### Method 3: CLI-Based Testing

**Best for:** Direct scanner testing, faster execution

```bash
# Model scan
docker compose -f docker-compose.protected.yml exec api \
  /usr/bin/python3 -m sentrascan.cli model \
    --model-path /test-data/models/test_model.pkl \
    --generate-sbom

# MCP scan
docker compose -f docker-compose.protected.yml exec api \
  /usr/bin/python3 -m sentrascan.cli mcp \
    --config-paths /test-data/mcp/test_config.json \
    --auto-discover
```

## Test Scenarios

### Scenario 1: Basic Model Scan

**Objective:** Verify basic model scanning works

**Steps:**
1. Create a test pickle model
2. Trigger scan via API
3. Verify scan completes
4. Check findings are created

**Expected Result:**
- Scan completes successfully
- Scan ID is returned
- Findings are stored in database

### Scenario 2: Multiple Model Formats

**Objective:** Verify various model formats can be scanned

**Formats to Test:**
- `.pkl` (Pickle)
- `.joblib` (Joblib)
- `.pt`, `.pth` (PyTorch)
- `.h5` (Keras H5)
- `.onnx` (ONNX)
- `.safetensors` (SafeTensors)
- `.xgb` (XGBoost)
- `.npy`, `.npz` (NumPy)

**Expected Result:**
- Each format scans successfully (or returns appropriate error)
- Findings are correctly categorized

### Scenario 3: SBOM Generation

**Objective:** Verify SBOM generation works

**Steps:**
1. Trigger model scan with `generate_sbom: true`
2. Verify SBOM is generated
3. Check SBOM format (CycloneDX 1.6)
4. Verify SBOM is stored in database

**Expected Result:**
- SBOM is generated in CycloneDX format
- SBOM is linked to scan
- SBOM contains model components and dependencies

### Scenario 4: SSRF Prevention

**Objective:** Verify SSRF prevention works

**Steps:**
1. Attempt to scan HTTP/HTTPS URL
2. Verify request is rejected
3. Check error message

**Expected Result:**
- HTTP/HTTPS URLs are rejected
- Error message indicates SSRF prevention
- No network requests are made

### Scenario 5: Error Handling

**Objective:** Verify proper error handling

**Test Cases:**
- Invalid model path (file not found)
- Corrupted model file
- Missing API key
- Invalid API key
- Insufficient permissions

**Expected Result:**
- Appropriate error codes (400, 401, 403, 404, 500)
- Clear error messages
- No stack traces exposed

### Scenario 6: MCP Scanner

**Objective:** Verify MCP configuration scanning

**Steps:**
1. Create test MCP config file
2. Trigger MCP scan
3. Verify findings are created
4. Test auto-discovery

**Expected Result:**
- MCP configs are scanned
- Security issues are detected
- Findings are correctly categorized

## Test Data Preparation

### Creating Test Models

#### Pickle Model (Python)
```python
import pickle

# Simple test model
model_data = {
    "model_type": "test",
    "version": "1.0",
    "weights": [1.0, 2.0, 3.0]
}

with open("test_model.pkl", "wb") as f:
    pickle.dump(model_data, f)
```

#### NumPy Array
```python
import numpy as np

# Create test array
arr = np.array([1, 2, 3, 4, 5])
np.save("test_model.npy", arr)
```

#### Joblib Model
```python
from sklearn.linear_model import LinearRegression
import joblib

# Create simple model
model = LinearRegression()
model.fit([[1], [2], [3]], [1, 2, 3])

# Save as joblib
joblib.dump(model, "test_model.joblib")
```

### Creating Test MCP Configs

#### Valid Config
```json
{
  "mcpServers": {
    "test-server": {
      "command": "python",
      "args": ["server.py"],
      "env": {}
    }
  }
}
```

#### Config with Hardcoded Secret
```json
{
  "mcpServers": {
    "test-server": {
      "command": "python",
      "args": ["server.py"],
      "env": {
        "API_KEY": "sk-1234567890abcdef"
      }
    }
  }
}
```

## Troubleshooting

### Issue: API Key Not Working

**Solution:**
1. Verify API key format: `ss-proj-h_<147-char-string>`
2. Check API key is not revoked
3. Verify API key has `scan.create` permission
4. Check tenant context is correct

### Issue: Model Scan Fails

**Possible Causes:**
1. Model file not found (check path)
2. Model format not supported
3. modelaudit not installed
4. Insufficient permissions

**Solution:**
1. Verify model path is correct
2. Check model format is supported
3. Run `ModelScanner.doctor()` to check modelaudit
4. Verify API key permissions

### Issue: SSRF Test Fails

**Expected:** HTTP/HTTPS URLs should be rejected

**If test passes (URL accepted):**
- This is a security issue
- Check `ModelScanner._validate_paths()` implementation
- Verify SSRF prevention is working

### Issue: Tests Timeout

**Possible Causes:**
1. Large model files
2. Network issues
3. Container resource limits

**Solution:**
1. Use smaller test models
2. Increase timeout in test configuration
3. Check container resource limits
4. Verify database is accessible

## Best Practices

1. **Use API-Based Testing**: Tests the full stack
2. **Test Error Cases**: Don't just test happy paths
3. **Verify Findings**: Check that findings are correctly categorized
4. **Test Multi-Tenant**: Verify tenant isolation works
5. **Clean Up**: Remove test data after tests
6. **Document Results**: Keep track of what works and what doesn't

## Next Steps

1. **Expand Test Coverage**: Add more model formats
2. **Performance Testing**: Measure scan durations
3. **Load Testing**: Test with multiple concurrent scans
4. **Integration Testing**: Test with real-world models
5. **Security Testing**: Verify security controls work

## Related Documentation

- [Functional Test Plan](functional_test_plan.md)
- [API Documentation](../docs/api/README.md)
- [Getting Started Guide](../docs/getting-started/README.md)

