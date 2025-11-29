# Functional Testing Plan for Hardened Container

## Overview

This document outlines a comprehensive functional testing strategy for various model types and scanners in the hardened container environment.

## Testing Objectives

1. **Model Scanner Testing**: Verify scanning of 30+ ML model formats
2. **MCP Scanner Testing**: Verify MCP configuration scanning
3. **API Endpoint Testing**: Verify REST API functionality
4. **SBOM Generation**: Verify SBOM generation for model scans
5. **Error Handling**: Verify proper error handling for invalid inputs
6. **Multi-tenant Isolation**: Verify tenant-scoped scanning

## Test Categories

### 1. Model Scanner Tests

#### 1.1 Core Format Tests (Priority: P0)

| Format | Extension | Test File | Expected Behavior |
|--------|-----------|-----------|-------------------|
| **PyTorch Pickle** | `.pt`, `.pth` | `test_model.pt` | Scan for pickle vulnerabilities |
| **PyTorch Zip** | `.bin` | `test_model.bin` | Scan zip-based PyTorch models |
| **TensorFlow SavedModel** | Directory | `saved_model/` | Scan SavedModel format |
| **TensorFlow Lite** | `.tflite` | `test_model.tflite` | Scan TFLite models |
| **Keras H5** | `.h5` | `test_model.h5` | Scan Keras H5 format |
| **Keras V3** | `.keras` | `test_model.keras` | Scan Keras V3 format |
| **ONNX** | `.onnx` | `test_model.onnx` | Scan ONNX models |
| **SafeTensors** | `.safetensors` | `test_model.safetensors` | Scan Hugging Face SafeTensors |
| **Pickle** | `.pkl` | `test_model.pkl` | Scan standard pickle files |
| **Joblib** | `.joblib` | `test_model.joblib` | Scan scikit-learn joblib |
| **XGBoost** | `.xgb`, `.pkl` | `test_model.xgb` | Scan XGBoost models |
| **NumPy** | `.npy`, `.npz` | `test_model.npy` | Scan NumPy arrays |

#### 1.2 Advanced Format Tests (Priority: P1)

| Format | Extension | Test File | Expected Behavior |
|--------|-----------|-----------|-------------------|
| **GGUF** | `.gguf` | `test_model.gguf` | Scan LLM GGUF format |
| **TensorRT** | `.trt`, `.engine` | `test_model.trt` | Scan NVIDIA TensorRT |
| **OpenVINO** | `.xml`, `.bin` | `test_model.xml` | Scan Intel OpenVINO |
| **PaddlePaddle** | Various | `test_model.pdparams` | Scan PaddlePaddle models |
| **Flax/JAX** | `.msgpack` | `test_model.msgpack` | Scan Flax/JAX models |
| **ExecuTorch** | `.pte` | `test_model.pte` | Scan PyTorch mobile |
| **PMML** | `.pmml` | `test_model.pmml` | Scan Predictive Model Markup |
| **SKOps** | `.skops` | `test_model.skops` | Scan scikit-learn Ops |

#### 1.3 Archive Format Tests (Priority: P2)

| Format | Extension | Test File | Expected Behavior |
|--------|-----------|-----------|-------------------|
| **ZIP** | `.zip` | `test_model.zip` | Scan zip archives |
| **TAR** | `.tar` | `test_model.tar` | Scan tar archives |
| **7Z** | `.7z` | `test_model.7z` | Scan 7z archives |

### 2. MCP Scanner Tests

#### 2.1 Configuration File Tests

| Test Case | Config File | Expected Findings |
|-----------|-------------|-------------------|
| Valid MCP config | `valid_mcp.json` | No critical/high findings |
| Hardcoded secrets | `secrets_mcp.json` | Secret detection findings |
| Command injection | `injection_mcp.json` | Command injection findings |
| Excessive permissions | `permissions_mcp.json` | Permission violation findings |
| Baseline drift | `drift_mcp.json` | Baseline drift findings |

#### 2.2 Auto-Discovery Tests

- Test auto-discovery of MCP configs in default paths
- Test auto-discovery with custom paths
- Test auto-discovery with no configs found

### 3. API Endpoint Tests

#### 3.1 Model Scan API

- `POST /api/v1/models/scans` - Create model scan
- `GET /api/v1/scans/{scan_id}` - Get scan details
- `GET /api/v1/scans?type=model` - List model scans
- `GET /api/v1/findings?scanner=modelaudit` - List findings

#### 3.2 MCP Scan API

- `POST /api/v1/mcp/scans` - Create MCP scan
- `GET /api/v1/scans?type=mcp` - List MCP scans

#### 3.3 Error Handling

- Invalid model path (file not found)
- Invalid model format
- SSRF prevention (HTTP/HTTPS URLs rejected)
- Unauthorized access (missing/invalid API key)
- Permission denied (insufficient permissions)

### 4. SBOM Generation Tests

- Verify SBOM generation for model scans
- Verify SBOM format (CycloneDX 1.6)
- Verify SBOM content (components, dependencies, licenses)
- Verify SBOM storage in database

### 5. Multi-Tenant Isolation Tests

- Verify scans are tenant-scoped
- Verify findings are tenant-scoped
- Verify cross-tenant access prevention

## Test Execution Methods

### Method 1: API-Based Testing (Recommended)

Use REST API endpoints to trigger scans and verify results.

**Advantages:**
- Tests the full stack (API → Scanner → Database)
- Verifies authentication and authorization
- Tests error handling and validation
- Can be automated easily

**Example:**
```bash
# Create model scan via API
curl -X POST http://localhost:8200/api/v1/models/scans \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"paths": ["/test/models/test_model.pkl"]}'
```

### Method 2: CLI-Based Testing

Use the CLI directly inside the container.

**Advantages:**
- Tests scanner functionality directly
- Faster execution (no API overhead)
- Good for debugging scanner issues

**Example:**
```bash
docker compose -f docker-compose.protected.yml exec api \
  /usr/bin/python3 -m sentrascan.cli model \
    --model-path /test/models/test_model.pkl \
    --generate-sbom
```

### Method 3: Direct Scanner Testing

Import and test scanner classes directly.

**Advantages:**
- Unit-level testing
- Fast execution
- Good for testing specific scanner features

**Example:**
```python
from sentrascan.modules.model.scanner import ModelScanner
from sentrascan.core.policy import PolicyEngine

scanner = ModelScanner(policy=PolicyEngine.default_model())
scan = scanner.scan(paths=["/test/models/test_model.pkl"], ...)
```

## Test Data Preparation

### Model Files

For testing, you'll need sample model files. Options:

1. **Create Minimal Test Models** (Recommended for hardened container)
   - Small pickle files with known vulnerabilities
   - Minimal ONNX models
   - Simple TensorFlow SavedModel directories

2. **Download Public Models** (If network access available)
   - Hugging Face models (via allowlisted URLs)
   - Public model repositories

3. **Generate Test Models** (Before container deployment)
   - Use test fixtures in `/tests/fixtures/models/`
   - Pre-generate models and mount as volume

### MCP Config Files

Create test MCP configuration files with:
- Valid configurations
- Hardcoded secrets
- Command injection patterns
- Permission violations

## Test Environment Setup

### Hardened Container Constraints

1. **Read-Only Filesystem**: Test files must be in mounted volumes
2. **No Shell**: Use Python/CLI commands, not shell scripts
3. **Limited Tools**: Only tools included in distroless image
4. **Network Restrictions**: SSRF prevention limits remote URLs

### Recommended Setup

1. **Create Test Volume**:
   ```yaml
   volumes:
     - ./test-data:/test-data:ro  # Read-only test data
   ```

2. **Mount Test Models**:
   ```bash
   mkdir -p test-data/models
   # Copy or generate test models here
   ```

3. **Use API Keys**: Create API keys for testing
   ```bash
   # Create test API key via CLI or web UI
   ```

## Test Execution Strategy

### Phase 1: Smoke Tests (Quick Validation)

1. Health check: `GET /api/v1/health`
2. Model scanner doctor: Verify `modelaudit` is available
3. Single model scan: Test one common format (e.g., `.pkl`)
4. Single MCP scan: Test one config file

### Phase 2: Core Format Tests

1. Test all P0 formats (12 formats)
2. Verify findings are created
3. Verify SBOM generation
4. Verify scan results are stored

### Phase 3: Advanced Format Tests

1. Test P1 formats (8 formats)
2. Test P2 archive formats (3 formats)
3. Verify error handling for unsupported formats

### Phase 4: Integration Tests

1. Test API endpoints end-to-end
2. Test multi-tenant isolation
3. Test error handling and validation
4. Test rate limiting (if applicable)

### Phase 5: Edge Cases

1. Large model files
2. Corrupted model files
3. Missing dependencies
4. Timeout scenarios
5. SSRF prevention verification

## Success Criteria

### Model Scanner

- ✅ All P0 formats scan successfully
- ✅ Findings are correctly categorized by severity
- ✅ SBOM is generated for model scans
- ✅ Scan results are persisted to database
- ✅ SSRF prevention blocks HTTP/HTTPS URLs
- ✅ Error handling works for invalid inputs

### MCP Scanner

- ✅ Valid configs scan without false positives
- ✅ Security issues are detected correctly
- ✅ Auto-discovery works for default paths
- ✅ Findings are correctly categorized
- ✅ Repository URL allowlisting works

### API Endpoints

- ✅ All endpoints respond correctly
- ✅ Authentication and authorization work
- ✅ Error responses are properly formatted
- ✅ Rate limiting works (if enabled)

## Test Reporting

After test execution, generate reports:

1. **Test Summary**: Pass/fail counts per category
2. **Format Coverage**: Which formats were tested
3. **Findings Summary**: Types of findings detected
4. **Performance Metrics**: Scan durations
5. **Error Logs**: Any errors or warnings encountered

## Next Steps

1. Create test data fixtures (models and MCP configs)
2. Implement test scripts (API-based or CLI-based)
3. Set up test execution environment
4. Run tests and collect results
5. Document findings and recommendations

