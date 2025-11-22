# Model Security Scanning Tools - Updated Analysis
## Focus: Model Scanning Only (No Notebooks/Secrets/PII) + SBOM Generation

**Analysis Date**: January 2025  
**Scope**: ML Model scanning + SBOM generation + Dependency analysis  
**Excluded**: Jupyter notebooks, secrets detection, PII scanning

---

## Executive Summary

Analyzed **5 tools** for ML model security scanning with SBOM capabilities:
1. **modelscan** (Protect AI) - Multi-format enterprise scanner
2. **picklescan** (Microsoft) - Lightweight pickle scanner
3. **modelaudit** (Promptfoo) - ⭐ **NEW DISCOVERY** - Comprehensive with 30 scanners + SBOM
4. **model-unpickler** (Goeckslab) - Safe loading library
5. **watchtower** (Bosch) - Comprehensive platform (excluded per requirements)

**🎯 FINAL RECOMMENDATION**: Build **SentraScan-Model** using:
- **Primary**: **modelaudit** (30 scanners, SBOM built-in, smart detection)
- **Secondary**: **modelscan** (H5/SavedModel depth)
- **Optional**: **picklescan** (Hugging Face direct integration)

---

## Tool Comparison Matrix (Model Scanning Focus)

| Feature | modelaudit ⭐ | modelscan | picklescan | model-unpickler |
|---------|-------------|-----------|-----------|-----------------|
| **License** | MIT | Apache 2.0 | MIT | MIT |
| **Version** | 0.2.17 | 0.8.x | 0.0.32 | 0.1 |
| **Maturity** | Production | Production | Stable | Research |
| **Scanners Count** | **30** | 5 | 1 | 1 |
| **SBOM Generation** | ✅ **CycloneDX** | ❌ | ❌ | ❌ |
| **Dependency Analysis** | ✅ Implicit | ❌ | ❌ | ❌ |
| **Pickle/Joblib** | ✅ | ✅ | ✅✅✅ | ✅ |
| **PyTorch (.pt, .pth, .bin)** | ✅✅ | ✅ | ✅ | ❌ |
| **H5/Keras** | ✅ | ✅✅ | ❌ | ❌ |
| **TensorFlow SavedModel** | ✅ | ✅✅ | ❌ | ❌ |
| **ONNX** | ✅ | ❌ | ❌ | ❌ |
| **GGUF (LLMs)** | ✅ | ❌ | ❌ | ❌ |
| **SafeTensors** | ✅ | ❌ | ❌ | ❌ |
| **TensorRT** | ✅ | ❌ | ❌ | ❌ |
| **XGBoost** | ✅ | ✅ | ❌ | ❌ |
| **Flax/JAX** | ✅ | ❌ | ❌ | ❌ |
| **PaddlePaddle** | ✅ | ❌ | ❌ | ❌ |
| **TFLite** | ✅ | ❌ | ❌ | ❌ |
| **OpenVINO** | ✅ | ❌ | ❌ | ❌ |
| **PMML** | ✅ | ❌ | ❌ | ❌ |
| **Hugging Face Direct** | ✅ (`hf://`) | ❌ | ✅✅ | ❌ |
| **MLflow Integration** | ✅ (`models://`) | ❌ | ❌ | ❌ |
| **S3/GCS Support** | ✅ | ❌ | ❌ | ❌ |
| **JFrog Artifactory** | ✅ | ❌ | ❌ | ❌ |
| **Smart Detection** | ✅ Auto-config | ❌ | ❌ | ❌ |
| **Progress Bars** | ✅ Auto (large files) | ❌ | ❌ | ❌ |
| **Streaming Scan** | ✅ Save disk | ❌ | ❌ | ❌ |
| **Caching** | ✅ Built-in | ❌ | ❌ | ❌ |
| **Report Formats** | JSON, SARIF, Text | JSON, Console | Console | N/A |
| **Exit Codes** | 3 codes | 5 codes | 3 codes | N/A |
| **Python API** | ✅ | ✅ | ✅ | ✅ |
| **CLI** | ✅ Advanced | ✅ | ✅ | ❌ |
| **Strict Mode** | ✅ | ❌ | ❌ | ❌ |
| **Fickling Integration** | ✅ v0.1.4 | ✅ Similar | ❌ | ❌ |

---

## 🎖️ modelaudit - THE GAME CHANGER

### Overview

| Attribute | Value |
|-----------|-------|
| **Project** | modelaudit |
| **Author** | Promptfoo (Ian Webster, Michael D'Angelo) |
| **Version** | 0.2.17 (Active development) |
| **License** | MIT |
| **PyPI** | https://pypi.org/project/modelaudit |
| **Python** | ≥3.8 |
| **Dependencies** | 18 packages (including cyclonedx-python-lib, fickling) |

### Why modelaudit is SUPERIOR

**1. Comprehensive Scanner Coverage (30 Scanners)**

```
Available Scanners:
  ✅ executorch           # PyTorch mobile
  ✅ flax_msgpack         # JAX/Flax models
  ✅ gguf                 # LLM format (llama.cpp)
  ✅ jax_checkpoint       # JAX checkpoints
  ✅ jinja2_template      # Template injection
  ✅ joblib               # Scikit-learn
  ✅ keras_h5             # Keras H5
  ✅ keras_zip            # Keras V3
  ✅ manifest             # Model manifests
  ✅ metadata             # Model metadata
  ✅ numpy                # NumPy arrays
  ✅ oci_layer            # Container layers
  ✅ onnx                 # ONNX models
  ✅ openvino             # Intel OpenVINO
  ✅ paddle               # PaddlePaddle
  ✅ pickle               # Standard pickle
  ✅ pmml                 # Predictive Model Markup
  ✅ pytorch_binary       # PyTorch .pt/.pth
  ✅ pytorch_zip          # PyTorch .bin (zip)
  ✅ safetensors          # Hugging Face SafeTensors
  ✅ sevenzip             # 7z archives
  ✅ skops                # Scikit-learn Ops
  ✅ tar                  # Tar archives
  ✅ tensorrt             # NVIDIA TensorRT
  ✅ text                 # Text file analysis
  ✅ tf_savedmodel        # TensorFlow SavedModel
  ✅ tflite               # TensorFlow Lite
  ✅ weight_distribution  # Weight analysis
  ✅ xgboost              # XGBoost models
  ✅ zip                  # Zip archives
```

**2. Built-in SBOM Generation (CycloneDX)**

```bash
# Generate SBOM during scan
modelaudit scan model.pkl --sbom model_sbom.json

# SBOM format: CycloneDX 1.6 (industry standard)
# Includes:
# - Model components
# - Dependencies
# - Licenses
# - Vulnerabilities
# - Hashes (SHA-256, SHA-1, MD5)
```

**3. Smart Detection & Auto-Configuration**

- **Input Type Detection**: Local, cloud (S3/GCS), HuggingFace, MLflow, JFrog
- **File Size Optimization**: Automatic for large models (>1GB)
- **Terminal Awareness**: Progress bars for TTY, quiet for CI/CD
- **Cloud Operations**: Automatic caching, size limits, timeouts

**4. Advanced Input Sources**

```bash
# Local
modelaudit scan model.pkl

# Hugging Face (hf:// protocol)
modelaudit scan hf://meta-llama/Llama-3.2-1B

# MLflow (models:// protocol)
modelaudit scan models:/production/fraud-detector/v3

# S3
modelaudit scan s3://ml-models/production/

# GCS
modelaudit scan gs://models-bucket/latest/

# JFrog Artifactory
modelaudit scan https://artifacts.company.com/ml-models/

# URL
modelaudit scan https://pytorch.org/hub/pytorch_vision_resnet/
```

**5. Streaming Scan (Disk Space Saver)**

```bash
# Download → Scan → Delete (one file at a time)
modelaudit scan s3://huge-models/ --stream

# Saves disk space for large model repositories
```

**6. Strict Mode for Security Gates**

```bash
# Fail on warnings, strict validation
modelaudit scan model.pkl --strict --format json -o report.json

# Exit code 1 on ANY issues (not just critical)
```

**7. Fickling Integration**

- Uses **fickling 0.1.4** (Trail of Bits) for pickle analysis
- Same engine as used by security researchers
- Detects:
  - Arbitrary code execution
  - Import abuse
  - Lambda functions
  - Reduce exploits

---

## Feature Coverage Comparison

### Deserialization Attack Detection

| Format | modelaudit | modelscan | picklescan |
|--------|-----------|-----------|-----------|
| **Pickle (.pkl)** | ✅✅ | ✅✅ | ✅✅✅ |
| **PyTorch (.pt, .pth, .bin)** | ✅✅ | ✅✅ | ✅✅ |
| **Joblib** | ✅✅ | ✅ | ❌ |
| **H5/Keras** | ✅ | ✅✅ | ❌ |
| **TensorFlow SavedModel** | ✅ | ✅✅ | ❌ |
| **ONNX** | ✅ | ❌ | ❌ |
| **GGUF** | ✅ | ❌ | ❌ |
| **SafeTensors** | ✅ | ❌ | ❌ |
| **TensorRT** | ✅ | ❌ | ❌ |
| **XGBoost** | ✅ | ✅ | ❌ |
| **Flax/JAX** | ✅ | ❌ | ❌ |

✅✅✅ = Excellent, ✅✅ = Good, ✅ = Basic

---

### SBOM & Dependency Analysis

| Feature | modelaudit | modelscan | picklescan |
|---------|-----------|-----------|-----------|
| **SBOM Generation** | ✅ CycloneDX 1.6 | ❌ | ❌ |
| **Component List** | ✅ Auto-extracted | ❌ | ❌ |
| **License Detection** | ✅ | ❌ | ❌ |
| **Dependency Tree** | ✅ Implicit | ❌ | ❌ |
| **Hash Verification** | ✅ SHA-256/SHA-1/MD5 | ❌ | ❌ |
| **Vulnerability Mapping** | ✅ CVE-compatible | ❌ | ❌ |
| **SARIF Output** | ✅ | ❌ | ❌ |

---

## Licensing Analysis

| Tool | License | Commercial | Modification | Distribution | Patent Protection |
|------|---------|-----------|--------------|--------------|-------------------|
| **modelaudit** | MIT | ✅ | ✅ | ✅ | ❌ |
| **modelscan** | Apache 2.0 | ✅ | ✅ | ✅ | ✅ |
| **picklescan** | MIT | ✅ | ✅ | ✅ | ❌ |

**All licenses are compatible** - can combine in SentraScan-Model.

**Recommendation**: Apache 2.0 for final product (stronger patent protection from modelscan).

---

## Architecture Recommendation for SentraScan-Model

### Simplified Two-Engine Approach

```
┌─────────────────────────────────────────────┐
│         SentraScan-Model Platform           │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Orchestrator & Policy Engine        │  │
│  └──────────────┬───────────────────────┘  │
│                 │                           │
│                 ▼                           │
│  ┌──────────────────────────────────────┐  │
│  │  Primary Engine: modelaudit          │  │
│  │  • 30 scanners                       │  │
│  │  • SBOM generation (CycloneDX)       │  │
│  │  • Smart detection                   │  │
│  │  • HuggingFace/MLflow/S3/GCS        │  │
│  │  • Fickling for pickle              │  │
│  └──────────────┬───────────────────────┘  │
│                 │                           │
│                 ▼                           │
│  ┌──────────────────────────────────────┐  │
│  │  Enhancement Engines (Optional)      │  │
│  │  • modelscan (H5/SavedModel depth)   │  │
│  │  • picklescan (HF direct access)     │  │
│  └──────────────┬───────────────────────┘  │
│                 │                           │
│                 ▼                           │
│  ┌──────────────────────────────────────┐  │
│  │  Report Generator                    │  │
│  │  • JSON (machine-readable)           │  │
│  │  • SARIF (GitHub Code Scanning)      │  │
│  │  • CycloneDX SBOM                    │  │
│  │  • Markdown (human-readable)         │  │
│  └──────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

---

## Recommended Technology Stack

### Core Components

**1. Primary Engine: modelaudit**
- Version: 0.2.17+
- License: MIT
- Role: Primary model scanner (30 formats) + SBOM generation
- Dependencies: cyclonedx-python-lib, fickling, huggingface-hub, s3fs, gcsfs
- Reasoning:
  - Most comprehensive format coverage
  - Built-in SBOM (no additional tooling needed)
  - Smart detection reduces configuration
  - Production-ready with active development
  - Promptfoo-backed (enterprise ML security focus)

**2. Enhancement: modelscan (Optional)**
- Version: 0.8+
- License: Apache 2.0
- Role: Deep analysis for H5/SavedModel formats
- Use When: Need deeper TensorFlow/Keras inspection
- Integration: Run after modelaudit for additional checks

**3. Enhancement: picklescan (Optional)**
- Version: 0.0.32+
- License: MIT
- Role: Hugging Face model hub direct scanning
- Use When: Need quick HF model checks before download
- Integration: Pre-scan filter before modelaudit

---

## What to Build - SentraScan-Model

### Phase 1: Core Model Scanning (Weeks 1-6)

**FR-1: Multi-Format Model Scanning**
- ✅ Leverage modelaudit's 30 scanners
- ✅ Pickle/Joblib/Dill (.pkl, .pth, .bin, .pt)
- ✅ H5/Keras (.h5, .keras)
- ✅ TensorFlow SavedModel (.pb)
- ✅ ONNX (.onnx)
- ✅ GGUF (LLM models)
- ✅ SafeTensors (.safetensors)
- ✅ TensorRT (.trt)
- ✅ XGBoost (.xgb, .pkl)
- ✅ Flax/JAX checkpoints
- ✅ NumPy arrays (.npy)

**FR-2: SBOM Generation**
- ✅ CycloneDX 1.6 format (industry standard)
- ✅ Component inventory
- ✅ Dependency tree
- ✅ License detection
- ✅ Hash verification (SHA-256, SHA-1, MD5)
- ✅ Vulnerability references (CVE-compatible)

**FR-3: Deserialization Attack Detection**
- ✅ Arbitrary code execution patterns
- ✅ Dangerous global imports (eval, exec, os.system)
- ✅ Filesystem operations
- ✅ Network operations
- ✅ Subprocess execution
- ✅ Lambda function abuse
- ✅ Reduce exploits

**FR-4: Input Sources**
- ✅ Local files/directories
- ✅ Hugging Face (`hf://user/model`)
- ✅ MLflow (`models:/name/version`)
- ✅ AWS S3 (`s3://bucket/path`)
- ✅ Google Cloud Storage (`gs://bucket/path`)
- ✅ JFrog Artifactory (via URL)
- ✅ Direct URLs (HTTPS)

**FR-5: Report Formats**
- ✅ JSON (machine-readable)
- ✅ SARIF (GitHub Code Scanning compatible)
- ✅ CycloneDX SBOM (separate file)
- ✅ Markdown (human-readable)
- ✅ Text/Console (terminal output)

---

### Phase 2: Enterprise Features (Weeks 7-12)

**FR-6: Baseline Management**
- Create approved model baselines
- Detect drift from baselines
- SBOM comparison (baseline vs current)
- Version control integration

**FR-7: Policy Engine**
- Configurable severity thresholds
- Issue type filtering
- Format-specific rules
- Custom scanner configuration
- Allowlist/blocklist

**FR-8: Enhanced Scanning**
- Optional modelscan integration for H5/SavedModel depth
- Optional picklescan for HF pre-scan filtering
- Parallel scanning for large repositories
- Streaming scan for cloud sources

**FR-9: Integration Points**
- REST API (FastAPI)
- Python SDK
- CLI tool (wraps modelaudit)
- GitHub Actions
- GitLab CI
- Pre-commit hooks

**FR-10: Database & Audit**
- SQLite/PostgreSQL for scan history
- SBOM storage and comparison
- Provenance tracking
- Compliance reports

---

### Phase 3: Production Hardening (Weeks 13-18)

**FR-11: Advanced Features**
- RBAC & multi-tenancy
- Web UI (React)
- Historical trend analysis
- Vulnerability database integration
- Custom scanner plugins

**FR-12: Observability**
- Prometheus metrics
- Structured logging (JSON)
- OpenTelemetry tracing
- Health checks

**FR-13: Deployment**
- Docker Compose stack
- Kubernetes Helm chart
- Cloud-native (AWS/GCP/Azure)
- Air-gapped deployment support

---

## Deployment Architecture

```yaml
# Docker Compose Stack
services:
  sentrascan-model-api:
    image: sentrascan-model:latest
    command: server
    environment:
      - DATABASE_URL=postgresql://...
      - MODELAUDIT_CACHE_DIR=/cache
      - HUGGINGFACE_TOKEN=${HF_TOKEN}
      - MLFLOW_TRACKING_URI=${MLFLOW_URI}
      - AWS_ACCESS_KEY_ID=${AWS_KEY}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET}
    volumes:
      - ./models:/scan
      - ./reports:/reports
      - ./sboms:/sboms
      - ./cache:/cache
    ports:
      - "8100:8100"
  
  sentrascan-model-web:
    image: sentrascan-model-web:latest
    ports:
      - "3100:80"
    depends_on:
      - sentrascan-model-api
  
  db:
    image: postgres:15-alpine
    volumes:
      - pg-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=sentrascan_model
      - POSTGRES_USER=sentrascan
      - POSTGRES_PASSWORD=changeme

volumes:
  pg-data:
```

---

## Key Differentiators

| Feature | modelaudit (standalone) | SentraScan-Model |
|---------|------------------------|------------------|
| **Scanner Count** | 30 | 30 (via modelaudit) |
| **SBOM** | CycloneDX only | CycloneDX + custom extensions |
| **Baseline Management** | ❌ | ✅ Full drift detection |
| **Policy Engine** | Basic (--strict) | ✅ Advanced rules |
| **Web UI** | ❌ | ✅ React dashboard |
| **Database** | File cache only | ✅ PostgreSQL/SQLite with history |
| **API** | CLI only | ✅ REST API + Python SDK |
| **Multi-Engine** | Single | ✅ modelaudit + optional enhancements |
| **RBAC** | ❌ | ✅ Enterprise multi-tenancy |
| **Compliance Reports** | Basic | ✅ SOC2/ISO27001 templates |

---

## Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Small Model (10MB)** | <5s | Pickle file |
| **Medium Model (100MB)** | <30s | PyTorch .bin |
| **Large Model (1GB)** | <3min | With streaming |
| **SBOM Generation** | <2s | Post-scan overhead |
| **Concurrent Scans** | 10+ | Parallel workers |
| **Memory Usage** | <2GB | Per scan worker |

---

## Implementation Roadmap

### Week 1-2: PoC & Integration
- Install modelaudit and test all 30 scanners
- Create Python wrapper around modelaudit CLI
- Test SBOM generation with sample models
- Validate all input sources (local, HF, MLflow, S3, GCS)

### Week 3-4: CLI & Orchestrator
- Build SentraScan-Model CLI (wraps modelaudit)
- Add policy engine (threshold filtering)
- Implement report format conversions
- Add baseline management (JSON storage)

### Week 5-6: Docker & Documentation
- Create Docker image with all dependencies
- Test against diverse model formats
- Write user documentation
- Create CI/CD integration examples

### Week 7-9: REST API
- FastAPI server with scan endpoints
- SQLite database for scan history
- SBOM storage and retrieval
- Authentication (API keys)

### Week 10-12: Web UI
- React dashboard
- Scan history viewer
- SBOM explorer
- Policy configuration UI

### Week 13-15: Enterprise Features
- PostgreSQL support
- RBAC implementation
- Advanced policy rules
- Kubernetes Helm chart

### Week 16-18: Production Hardening
- Comprehensive testing
- Performance optimization
- Security hardening
- Complete documentation

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **modelaudit API Changes** | Low | Medium | Pin version 0.2.17, monitor releases |
| **Fickling Version Lock** | Low | Low | modelaudit handles internally |
| **False Positives** | Medium | Medium | Tunable policies, allowlists |
| **Large Model Performance** | Medium | Medium | Use streaming mode, caching |
| **Cloud Authentication** | Low | High | Environment variable management |

---

## Success Metrics

### Adoption
- ✅ 10+ teams onboarded (first 3 months)
- ✅ 100+ scans/day (steady state)
- ✅ 80% CI/CD integration rate

### Quality
- ✅ <5% false positive rate
- ✅ 95%+ threat detection rate (via modelaudit)
- ✅ 100% SBOM generation success

### Performance
- ✅ P95 scan time <30s (small models)
- ✅ P95 scan time <3min (large models with streaming)
- ✅ 99.9% uptime

---

## Conclusion

**PRIMARY RECOMMENDATION: Build SentraScan-Model on modelaudit foundation**

### Why modelaudit is the Winner

1. **30 Scanners**: Broadest format coverage (5x more than modelscan)
2. **SBOM Built-in**: CycloneDX generation included (no extra tooling)
3. **Smart Detection**: Auto-configures based on input (reduces complexity)
4. **Production-Ready**: Promptfoo-backed, active development, v0.2.17
5. **MIT License**: Most permissive (compatible with all other tools)
6. **Modern Features**: Streaming, caching, MLflow/HF/S3/GCS support
7. **Fickling Integration**: Industry-standard pickle analysis

### Integration Strategy

1. **Core**: modelaudit (handles 95% of use cases)
2. **Enhancement**: modelscan (optional, for H5/SavedModel depth)
3. **Pre-filter**: picklescan (optional, for HF quick checks)
4. **Orchestration**: SentraScan wrapper (policy, baseline, reporting)

### Next Steps

1. ✅ **Approve** modelaudit as primary engine
2. ⏳ **Install** modelaudit and run test scans
3. ⏳ **Create** PoC Python wrapper
4. ⏳ **Test** SBOM generation with diverse models
5. ⏳ **Build** orchestrator with policy engine
6. ⏳ **Proceed** with PRD development

---

## Appendix: Tool Details

| Tool | PyPI | Repository | Version |
|------|------|------------|---------|
| **modelaudit** | ✅ https://pypi.org/project/modelaudit | N/A (closed source) | 0.2.17 |
| **modelscan** | ✅ https://pypi.org/project/modelscan | https://github.com/protectai/modelscan | 0.8.x |
| **picklescan** | ✅ https://pypi.org/project/picklescan | https://github.com/mmaitre314/picklescan | 0.0.32 |
| **model-unpickler** | ❌ | https://github.com/goeckslab/model-unpickler | 0.1 |

---

**Document Status:** ✅ Complete - Ready for PRD Development  
**Primary Engine:** modelaudit (30 scanners + SBOM)  
**License:** MIT (can upgrade to Apache 2.0 for final product)  
**SBOM:** CycloneDX 1.6 built-in
