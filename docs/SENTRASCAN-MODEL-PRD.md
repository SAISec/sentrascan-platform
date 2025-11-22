# Product Requirements Document (PRD)
## SentraScan-Model: ML Model Security Scanner with SBOM Generation

---

## Document Control

| Field | Value |
|-------|-------|
| **Product Name** | SentraScan-Model |
| **Version** | 1.0 |
| **Date** | January 2025 |
| **Status** | Draft for Approval |
| **Owner** | Security Engineering Team |
| **Classification** | Internal Use |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Product Vision](#product-vision)
3. [Goals & Success Metrics](#goals--success-metrics)
4. [User Personas](#user-personas)
5. [Functional Requirements](#functional-requirements)
6. [Technical Requirements](#technical-requirements)
7. [User Interface Requirements](#user-interface-requirements)
8. [Security & Compliance](#security--compliance)
9. [Deployment Architecture](#deployment-architecture)
10. [Integration Points](#integration-points)
11. [Non-Functional Requirements](#non-functional-requirements)
12. [Roadmap & Milestones](#roadmap--milestones)
13. [Dependencies & Risks](#dependencies--risks)
14. [Appendix](#appendix)

---

## Executive Summary

### Problem Statement

Organizations deploying machine learning models face critical security risks:
- **Model Serialization Attacks**: Malicious code embedded in model files (Pickle, PyTorch, TensorFlow)
- **Supply Chain Vulnerabilities**: Untrusted models from Hugging Face, MLflow, cloud storage
- **Lack of SBOM**: No visibility into model components, dependencies, and licenses
- **Deserialization Exploits**: Arbitrary code execution when loading models
- **No Pre-Deployment Gates**: Models deployed without security validation

Currently, no unified solution exists for **comprehensive ML model security scanning with SBOM generation** before production deployment.

### Solution

**SentraScan-Model** is a self-hosted, containerized ML model security scanner that:
- Scans **30+ model formats** (Pickle, PyTorch, TensorFlow, ONNX, GGUF, SafeTensors, etc.)
- Detects **deserialization attacks** and malicious code patterns
- Generates **CycloneDX SBOM** (Software Bill of Materials) automatically
- Supports **multiple input sources** (local, Hugging Face, MLflow, S3, GCS, JFrog)
- Provides **CLI, REST API, and Web UI** interfaces
- Operates **100% locally** with no external dependencies
- Maintains **scan history and SBOM database**

### Value Proposition

| Stakeholder | Value |
|-------------|-------|
| **Security Teams** | Automated security gates, SBOM compliance, audit trails |
| **ML Engineers** | Fast feedback (<30s scans), clear remediation guidance |
| **DevOps Teams** | Easy CI/CD integration, Docker deployment |
| **Compliance Teams** | CycloneDX SBOM, supply chain transparency |

---

## Product Vision

### Vision Statement

"Enable every organization to deploy ML models with confidence through automated security scanning and SBOM generation, ensuring supply chain transparency and protection against model serialization attacks."

### Guiding Principles

1. **Security First**: Detect and prevent model serialization attacks
2. **SBOM Native**: CycloneDX generation built into every scan
3. **Comprehensive Coverage**: 30+ model formats from day one
4. **Developer Experience**: Sub-minute scans, clear output
5. **Enterprise Ready**: Docker-first, database-backed, RBAC-enabled
6. **License Clean**: MIT/Apache 2.0 only
7. **CI/CD Native**: Designed for automation

---

## Goals & Success Metrics

### Primary Goals

| Goal | Success Metric | Target |
|------|----------------|--------|
| **G1: Fast Scans** | P95 scan time for 100MB model | <30 seconds |
| **G2: Format Coverage** | Model formats supported | ≥30 formats |
| **G3: SBOM Generation** | SBOMs generated successfully | 100% |
| **G4: CI/CD Integration** | Pipelines using SentraScan-Model | 80% of ML deployments |
| **G5: Zero External Deps** | External API calls per scan | 0 |
| **G6: Threat Detection** | Deserialization attack detection rate | ≥95% |

### Key Performance Indicators (KPIs)

**Adoption Metrics:**
- Number of teams onboarded
- Scans per day (target: 100+)
- SBOM exports per day
- CI/CD integration rate

**Quality Metrics:**
- False positive rate (target: <5%)
- Critical findings detected (track trend)
- SBOM completeness (100%)

**Performance Metrics:**
- P50, P95, P99 scan latency
- SBOM generation time (<2s overhead)
- API response times (P95 <500ms)

---

## User Personas

### Persona 1: ML Engineer (Primary)

**Name:** Alex  
**Role:** Machine Learning Engineer  
**Goals:**
- Validate models before deployment
- Get fast security feedback during development
- Understand what's inside model files
- Ensure models are safe to load

**Pain Points:**
- Unsure if downloaded models are safe
- No visibility into model dependencies
- Manual security reviews slow down deployments
- Fear of loading malicious pickles

**How SentraScan-Model Helps:**
- Fast local scans during development
- SBOM shows exactly what's in the model
- Clear security findings with remediation
- Direct Hugging Face/MLflow integration

---

### Persona 2: Security Engineer (Secondary)

**Name:** Morgan  
**Role:** Application Security Engineer  
**Goals:**
- Enforce security policies for ML models
- Track model provenance and components
- Generate compliance reports (SBOM)
- Prevent supply chain attacks

**Pain Points:**
- No SBOM for ML models (unlike software packages)
- Lack of pre-deployment security gates
- Manual model inspection doesn't scale
- No audit trail for model changes

**How SentraScan-Model Helps:**
- Automated security scanning in CI/CD
- CycloneDX SBOM for every model
- Policy engine for pass/fail gates
- Complete audit trail in database

---

### Persona 3: MLOps/DevOps Engineer (Tertiary)

**Name:** Jordan  
**Role:** MLOps Engineer  
**Goals:**
- Integrate security into ML pipelines
- Automate model validation
- Maintain deployment velocity
- Support compliance requirements

**Pain Points:**
- Security checks slow down pipelines
- Integration complexity
- Need for model-specific scanning tools
- SBOM generation is manual

**How SentraScan-Model Helps:**
- Docker-first deployment
- REST API for pipeline integration
- Sub-minute scan times
- Automatic SBOM generation

---

## Functional Requirements

### FR-1: Multi-Format Model Scanning

#### FR-1.1: Core Format Support (via modelaudit)
**Priority:** P0 (Must Have)  
**Description:** Scan 30+ ML model formats for security issues

**Supported Formats:**

| Framework | Format | Extension | Scanner |
|-----------|--------|-----------|---------|
| **PyTorch** | Pickle/Zip | `.pt`, `.pth`, `.bin` | pytorch_binary, pytorch_zip, pickle |
| **TensorFlow** | SavedModel | `.pb` (directory) | tf_savedmodel |
| **TensorFlow** | TFLite | `.tflite` | tflite |
| **Keras** | H5 | `.h5` | keras_h5 |
| **Keras** | Keras V3 | `.keras` | keras_zip |
| **ONNX** | ONNX | `.onnx` | onnx |
| **Hugging Face** | SafeTensors | `.safetensors` | safetensors |
| **LLMs** | GGUF | `.gguf` | gguf |
| **Scikit-learn** | Pickle/Joblib | `.pkl`, `.joblib` | pickle, joblib |
| **XGBoost** | Binary/Pickle | `.xgb`, `.pkl` | xgboost, pickle |
| **Flax/JAX** | MsgPack/Checkpoint | `.msgpack` | flax_msgpack, jax_checkpoint |
| **PyTorch Mobile** | ExecuTorch | `.pte` | executorch |
| **NVIDIA** | TensorRT | `.trt`, `.engine` | tensorrt |
| **Intel** | OpenVINO | `.xml`, `.bin` | openvino |
| **PaddlePaddle** | Paddle | Various | paddle |
| **Classic ML** | PMML | `.pmml` | pmml |
| **SKOps** | SKOps | `.skops` | skops |
| **NumPy** | Array | `.npy`, `.npz` | numpy |
| **Archives** | Zip/Tar/7z | `.zip`, `.tar`, `.7z` | zip, tar, sevenzip |
| **Containers** | OCI Layers | Various | oci_layer |

**Additional Scanners:**
- `manifest` - Model manifest files
- `metadata` - Model metadata analysis
- `text` - Text file scanning
- `jinja2_template` - Template injection detection
- `weight_distribution` - Weight analysis

**Acceptance Criteria:**
- [x] Support all 30 modelaudit scanners
- [x] Auto-detect format from file extension/content
- [x] Scan multiple formats in single pass
- [x] Report format-specific issues
- [x] Handle nested/archived models

---

#### FR-1.2: Deserialization Attack Detection
**Priority:** P0 (Must Have)  
**Description:** Detect malicious code patterns in serialized models

**Detection Capabilities:**

| Threat Type | Description | Severity |
|-------------|-------------|----------|
| **Arbitrary Code Execution** | `eval`, `exec`, `compile`, `__import__` | CRITICAL |
| **OS Command Execution** | `os.system`, `subprocess.call`, `os.popen` | CRITICAL |
| **File System Access** | `open`, `read`, `write`, file I/O | HIGH |
| **Network Operations** | `socket`, `urllib`, `requests`, HTTP calls | HIGH |
| **Lambda/Reduce Abuse** | Lambda functions in pickle streams | HIGH |
| **Unsafe Imports** | Dangerous module imports | MEDIUM |
| **Code Injection** | Embedded code in model layers | HIGH |

**Fickling Integration:**
- Uses fickling 0.1.4 (Trail of Bits) for pickle analysis
- Static bytecode analysis (no execution)
- Pattern matching for dangerous opcodes

**Acceptance Criteria:**
- [x] Detect all OWASP Top 10 for ML risks
- [x] Scan pickle opcodes without execution
- [x] Report severity levels (CRITICAL, HIGH, MEDIUM, LOW)
- [x] Include code snippets in findings
- [x] Provide remediation guidance

---

### FR-2: SBOM Generation

#### FR-2.1: CycloneDX SBOM Creation
**Priority:** P0 (Must Have)  
**Description:** Generate CycloneDX SBOM for every scanned model

**SBOM Contents:**
```json
{
  "bomFormat": "CycloneDX",
  "specVersion": "1.6",
  "serialNumber": "urn:uuid:...",
  "version": 1,
  "metadata": {
    "timestamp": "2025-01-20T10:00:00Z",
    "component": {
      "type": "machine-learning-model",
      "name": "fraud_detector",
      "version": "2.1.0"
    }
  },
  "components": [
    {
      "type": "library",
      "name": "numpy",
      "version": "1.24.3",
      "licenses": [{"license": {"id": "BSD-3-Clause"}}],
      "hashes": [
        {"alg": "SHA-256", "content": "abc123..."}
      ]
    }
  ],
  "dependencies": [...],
  "vulnerabilities": [...]
}
```

**SBOM Fields:**
- **Components**: Libraries, frameworks, dependencies
- **Licenses**: Detected license information
- **Hashes**: SHA-256, SHA-1, MD5 checksums
- **Vulnerabilities**: CVE references (if detected)
- **Metadata**: Model name, version, framework
- **Dependencies**: Component dependency tree

**Acceptance Criteria:**
- [x] Generate CycloneDX 1.6 format
- [x] Include all model components
- [x] Extract dependency information
- [x] Detect licenses automatically
- [x] Calculate file hashes
- [x] Export as JSON file
- [x] Store SBOM in database

---

#### FR-2.2: SBOM Comparison & Drift Detection
**Priority:** P1 (Should Have)  
**Description:** Compare SBOMs to detect supply chain changes

**Use Cases:**
1. Compare baseline SBOM vs current scan
2. Detect new/removed/modified components
3. Track license changes
4. Monitor dependency updates

**Acceptance Criteria:**
- [x] Diff two SBOM files
- [x] Highlight component changes
- [x] Report license changes
- [x] Alert on new vulnerabilities
- [x] Generate comparison report

---

### FR-3: Input Sources

#### FR-3.1: Multi-Source Support
**Priority:** P0 (Must Have)  
**Description:** Scan models from various sources

**Supported Sources:**

```bash
# Local file
sentrascan-model scan model.pkl

# Local directory (recursive)
sentrascan-model scan /path/to/models/

# Hugging Face (hf:// protocol)
sentrascan-model scan hf://meta-llama/Llama-3.2-1B

# MLflow (models:// protocol)
sentrascan-model scan models:/production/fraud-detector/v3

# AWS S3
sentrascan-model scan s3://ml-models-bucket/production/

# Google Cloud Storage
sentrascan-model scan gs://models-bucket/latest/

# JFrog Artifactory
sentrascan-model scan https://artifactory.company.com/ml-models/latest.pkl

# Direct HTTPS URL
sentrascan-model scan https://example.com/models/resnet50.pt
```

**Acceptance Criteria:**
- [x] Auto-detect source type
- [x] Handle authentication (env vars)
- [x] Support recursive directory scans
- [x] Cache downloaded models
- [x] Streaming mode for large files
- [x] Progress indicators for downloads

---

#### FR-3.2: Smart Detection & Auto-Configuration
**Priority:** P1 (Should Have)  
**Description:** Automatically configure scan based on input

**Smart Detection Features:**
- **Input Type**: Local vs cloud vs registry
- **File Size**: Enable streaming for >1GB
- **Terminal Type**: Progress bars (TTY) vs quiet (CI)
- **Cloud Operations**: Auto-caching, size limits, timeouts

**Acceptance Criteria:**
- [x] Detect input source automatically
- [x] Optimize for file size
- [x] Adjust output for environment (TTY/CI)
- [x] Set appropriate timeouts
- [x] Enable caching when beneficial

---

### FR-4: Scanning Modes

#### FR-4.1: Standard Scan Mode
**Priority:** P0 (Must Have)  
**Description:** Default security + SBOM scan

```bash
sentrascan-model scan model.pkl \
  --format json \
  --output scan-report.json \
  --sbom model-sbom.json
```

**Outputs:**
1. Security scan report (JSON/Markdown/SARIF)
2. CycloneDX SBOM (JSON)
3. Exit code (0=pass, 1=fail, 2=error)

---

#### FR-4.2: Strict Mode
**Priority:** P1 (Should Have)  
**Description:** Fail on warnings, strict validation

```bash
sentrascan-model scan model.pkl --strict
```

**Strict Mode Behavior:**
- Fail on warnings (not just errors)
- Scan all file types (no skipping)
- Strict license validation
- Exit code 1 on ANY issues

---

#### FR-4.3: Streaming Mode
**Priority:** P1 (Should Have)  
**Description:** Download → Scan → Delete (saves disk space)

```bash
sentrascan-model scan s3://huge-models/ --stream
```

**Use Case:** Large model repositories where disk space is limited

---

### FR-5: Report Formats

#### FR-5.1: JSON Report
**Priority:** P0 (Must Have)

```json
{
  "scan_id": "uuid",
  "timestamp": "2025-01-20T10:00:00Z",
  "model_path": "model.pkl",
  "model_format": "pickle",
  "scan_result": {
    "passed": false,
    "total_issues": 12,
    "critical": 1,
    "high": 3,
    "medium": 5,
    "low": 3
  },
  "findings": [
    {
      "id": "finding-001",
      "scanner": "pickle",
      "severity": "CRITICAL",
      "category": "arbitrary_code_execution",
      "title": "Dangerous eval() detected",
      "description": "Model contains eval() call that executes arbitrary code",
      "location": "layer3.forward",
      "evidence": {
        "opcode": "GLOBAL",
        "import": "__builtin__ eval"
      },
      "remediation": "Remove eval() and use safe alternatives"
    }
  ],
  "sbom_generated": true,
  "sbom_path": "model_sbom.json",
  "metadata": {
    "scan_duration_ms": 2340,
    "scanners_used": ["pickle", "pytorch_zip"],
    "modelaudit_version": "0.2.17"
  }
}
```

---

#### FR-5.2: Markdown Report
**Priority:** P1 (Should Have)

```markdown
# Security Scan Report: model.pkl

**Scan ID**: abc-123-def  
**Date**: 2025-01-20 10:00:00  
**Result**: ❌ FAILED

## Summary
- **Critical Issues**: 1
- **High Issues**: 3  
- **Medium Issues**: 5
- **Low Issues**: 3

## Critical Findings

### 🔴 Arbitrary Code Execution
**Location**: layer3.forward  
**Scanner**: pickle  

Model contains `eval()` call that executes arbitrary code during deserialization.

**Evidence**:
```python
GLOBAL __builtin__ eval
```

**Remediation**: Remove eval() and use safe alternatives.

---

## SBOM
CycloneDX SBOM generated: `model_sbom.json`
```

---

#### FR-5.3: SARIF Report
**Priority:** P2 (Nice to Have)  
**Description:** GitHub Code Scanning compatible format

```json
{
  "$schema": "https://raw.githubusercontent.com/oasis-tcs/sarif-spec/master/Schemata/sarif-schema-2.1.0.json",
  "version": "2.1.0",
  "runs": [
    {
      "tool": {
        "driver": {
          "name": "SentraScan-Model",
          "version": "1.0.0"
        }
      },
      "results": [
        {
          "ruleId": "pickle/arbitrary-code-execution",
          "level": "error",
          "message": {"text": "Dangerous eval() detected"},
          "locations": [...]
        }
      ]
    }
  ]
}
```

---

### FR-6: Policy Engine

#### FR-6.1: Configurable Policies
**Priority:** P1 (Should Have)  
**Description:** Define security policies for pass/fail gates

**Policy Configuration** (`.sentrascan-model.yaml`):
```yaml
policy:
  name: "Production ML Models Policy"
  version: "1.0"
  
  severity_threshold: HIGH  # CRITICAL | HIGH | MEDIUM | LOW
  
  block_issues:
    - arbitrary_code_execution
    - os_command_execution
    - file_system_access
    - network_operations
  
  allow_issues:
    - unsafe_imports  # Allow with warning
  
  sbom_requirements:
    require_sbom: true
    require_licenses: true
    blocked_licenses:
      - GPL-3.0
      - AGPL-3.0
  
  format_rules:
    pickle:
      max_file_size: 2GB
      strict_mode: true
    onnx:
      allow_external_data: false
  
  allowlist:
    models:
      - "s3://trusted-models/approved/*"
    hashes:
      - "sha256:abc123..."
```

**Acceptance Criteria:**
- [x] Load policy from YAML file
- [x] Filter findings by severity threshold
- [x] Block specific issue types
- [x] SBOM policy enforcement
- [x] Format-specific rules
- [x] Model allowlist (path/hash)
- [x] Return pass/fail decision

---

### FR-7: Baseline Management

#### FR-7.1: Baseline Creation
**Priority:** P1 (Should Have)  
**Description:** Create approved model baseline

```bash
sentrascan-model baseline create model.pkl \
  --name "fraud_detector_v2" \
  --output baseline.json
```

**Baseline File**:
```json
{
  "version": "1.0",
  "created_at": "2025-01-20T10:00:00Z",
  "model": {
    "name": "fraud_detector",
    "version": "2.0.0",
    "path": "model.pkl",
    "format": "pickle",
    "hash": "sha256:abc123...",
    "size_bytes": 104857600
  },
  "sbom": {
    "components": [...],
    "dependencies": [...],
    "licenses": [...]
  },
  "scan_results": {
    "findings": [],
    "passed": true
  },
  "approved_by": "security@company.com",
  "approval_date": "2025-01-20T12:00:00Z"
}
```

---

#### FR-7.2: Baseline Comparison
**Priority:** P1 (Should Have)  
**Description:** Detect drift from approved baseline

```bash
sentrascan-model scan model.pkl \
  --baseline baseline.json \
  --detect-drift
```

**Drift Detection:**
- Hash changes (model modified)
- New components (SBOM diff)
- Removed components
- License changes
- New security findings
- Dependency updates

**Acceptance Criteria:**
- [x] Compare current scan vs baseline
- [x] Detect all drift types
- [x] Report drift with details
- [x] Fail scan if drift detected (configurable)

---

### FR-8: Database & Persistence

#### FR-8.1: Scan History Database
**Priority:** P1 (Should Have)  
**Description:** Store all scans and SBOMs in database

**Database Schema**:
```sql
-- Scans table
CREATE TABLE scans (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    model_path VARCHAR(1024) NOT NULL,
    model_format VARCHAR(50) NOT NULL,
    model_hash VARCHAR(255),
    scan_status VARCHAR(20) NOT NULL, -- completed, failed, pending
    passed BOOLEAN,
    duration_ms INTEGER,
    total_issues INTEGER,
    critical_count INTEGER,
    high_count INTEGER,
    medium_count INTEGER,
    low_count INTEGER,
    sbom_id UUID REFERENCES sboms(id),
    metadata JSONB,
    created_by VARCHAR(255)
);

-- Findings table
CREATE TABLE findings (
    id UUID PRIMARY KEY,
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
    scanner VARCHAR(50) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    category VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    evidence JSONB,
    remediation TEXT
);

-- SBOMs table
CREATE TABLE sboms (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    model_name VARCHAR(255),
    model_version VARCHAR(50),
    bom_format VARCHAR(20) NOT NULL, -- CycloneDX
    spec_version VARCHAR(10) NOT NULL, -- 1.6
    content JSONB NOT NULL,
    hash VARCHAR(255) NOT NULL
);

-- Baselines table
CREATE TABLE baselines (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    name VARCHAR(255) NOT NULL UNIQUE,
    model_name VARCHAR(255),
    model_version VARCHAR(50),
    model_hash VARCHAR(255) NOT NULL,
    scan_id UUID REFERENCES scans(id),
    sbom_id UUID REFERENCES sboms(id),
    approved_by VARCHAR(255),
    approval_date TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    notes TEXT
);

-- Audit log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    user VARCHAR(255),
    action VARCHAR(100) NOT NULL, -- scan, baseline_create, policy_update
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB
);
```

**Acceptance Criteria:**
- [x] SQLite for single-instance deployments
- [x] PostgreSQL support for enterprise
- [x] Store complete scan results
- [x] Store SBOMs as JSONB
- [x] Store baselines
- [x] Audit log for all operations
- [x] Indexed queries (fast lookups)

---

#### FR-8.2: Data Retention
**Priority:** P1 (Should Have)

**Retention Policy:**
- Scans: 90 days (configurable)
- SBOMs: 365 days (configurable)
- Baselines: Indefinite
- Audit logs: 365 days (configurable)

**Acceptance Criteria:**
- [x] Configurable retention periods
- [x] Automated cleanup job (daily)
- [x] Manual export before cleanup
- [x] Archival to S3/blob storage (optional)

---

## Technical Requirements

### TR-1: Technology Stack

**Core Components:**
- **Primary Scanner**: modelaudit 0.2.17+
- **Language**: Python 3.11+
- **Web Framework**: FastAPI 0.110+
- **Database**: SQLite (default) / PostgreSQL 15+ (optional)
- **ORM**: SQLAlchemy 2.0+
- **SBOM Library**: cyclonedx-python-lib (via modelaudit)
- **Pickle Analysis**: fickling 0.1.4 (via modelaudit)

**Optional Enhancements:**
- **modelscan**: 0.8+ (H5/SavedModel depth)
- **picklescan**: 0.0.32+ (Hugging Face direct)

**Frontend:**
- **Framework**: React 18+ or Vue 3+
- **UI Library**: Material-UI or Ant Design
- **State Management**: React Query or Pinia
- **Build Tool**: Vite

**DevOps:**
- **Containerization**: Docker 24+
- **Orchestration**: Docker Compose (MVP), Kubernetes (future)
- **CI/CD**: GitHub Actions / GitLab CI

---

### TR-2: Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Small Model (10MB)** | <5s | Pickle file |
| **Medium Model (100MB)** | <30s | PyTorch .bin |
| **Large Model (1GB)** | <3min | With streaming |
| **SBOM Generation** | <2s | Post-scan overhead |
| **API Response (P95)** | <500ms | Read endpoints |
| **Database Query (P95)** | <100ms | Single-table queries |
| **Memory Usage** | <2GB | Per scan worker |
| **Startup Time** | <10s | Container cold start |

---

### TR-3: Scalability Requirements

**MVP (Single Instance):**
- Concurrent scans: 10
- API throughput: 100 req/min
- Database: SQLite (up to 100K scans)

**Future (Distributed):**
- Concurrent scans: 50+ (queue-based)
- API throughput: 1000+ req/min (load balanced)
- Database: PostgreSQL cluster (millions of scans)

---

### TR-4: Deployment Architecture

```
┌─────────────────────────────────────────────┐
│          Docker Compose Stack               │
│                                             │
│  ┌─────────────┐  ┌──────────────┐        │
│  │  sentrascan │  │  Web UI      │        │
│  │  -model-api │  │  (Nginx)     │        │
│  │             │  │              │        │
│  │  • FastAPI  │◄─┤  React App   │        │
│  │  • modelaud │  │              │        │
│  │    it       │  │              │        │
│  └──────┬──────┘  └──────────────┘        │
│         │                                   │
│         ▼                                   │
│  ┌─────────────┐  ┌──────────────┐        │
│  │  PostgreSQL │  │  Cache       │        │
│  │  Database   │  │  (Redis)     │        │
│  │             │  │              │        │
│  │  • Scans    │  │  • Downloads │        │
│  │  • SBOMs    │  │  • Sessions  │        │
│  │  • Baseline │  │              │        │
│  └─────────────┘  └──────────────┘        │
│                                             │
│  Volumes:                                   │
│    - ./data:/data (database)               │
│    - ./sboms:/sboms (SBOM files)           │
│    - ./reports:/reports (scan outputs)     │
│    - ./cache:/cache (model downloads)      │
└─────────────────────────────────────────────┘
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    image: sentrascan-model:latest
    command: server --host 0.0.0.0 --port 8100
    ports:
      - "8100:8100"
    volumes:
      - ./data:/data
      - ./sboms:/sboms
      - ./reports:/reports
      - ./cache:/cache
    environment:
      - DATABASE_URL=postgresql://sentrascan:password@db/sentrascan_model
      - MODELAUDIT_CACHE_DIR=/cache
      - HUGGINGFACE_TOKEN=${HF_TOKEN}
      - MLFLOW_TRACKING_URI=${MLFLOW_URI}
      - AWS_ACCESS_KEY_ID=${AWS_KEY}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET}
      - GOOGLE_APPLICATION_CREDENTIALS=/secrets/gcs-key.json
    depends_on:
      - db
      - redis

  web:
    image: sentrascan-model-web:latest
    ports:
      - "3100:80"
    depends_on:
      - api

  db:
    image: postgres:15-alpine
    volumes:
      - pg-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=sentrascan_model
      - POSTGRES_USER=sentrascan
      - POSTGRES_PASSWORD=changeme

  redis:
    image: redis:7-alpine
    volumes:
      - redis-data:/data

volumes:
  pg-data:
  redis-data:
```

---

### TR-5: Security Requirements

#### TR-5.1: Secrets Management
- ❌ No hardcoded secrets in code/images
- ✅ Environment variables for sensitive config
- ✅ Support for secret managers (Vault, AWS Secrets Manager)
- ✅ Encrypted storage for API keys in database

#### TR-5.2: Network Security
- ✅ HTTPS/TLS for API (via reverse proxy)
- ✅ CORS whitelist for web UI
- ✅ Rate limiting per API key
- ✅ Input validation on all endpoints

#### TR-5.3: Data Security
- ✅ No sensitive data in logs
- ✅ Database encryption at rest (optional)
- ✅ Audit log for all operations
- ✅ RBAC for multi-user deployments

---

## User Interface Requirements

### UI-1: Design System

**Visual Identity:**
- **Color Palette:**
  - Primary: #1976D2 (blue)
  - Success: #4CAF50 (green)
  - Warning: #FF9800 (orange)
  - Error: #F44336 (red)
  - Critical: #9C27B0 (purple)

- **Typography:**
  - Font: Inter or Roboto
  - Headings: 24px/20px/16px
  - Body: 14px
  - Code: Fira Code or Monaco

- **Severity Colors:**
  - CRITICAL: #9C27B0 (purple)
  - HIGH: #F44336 (red)
  - MEDIUM: #FF9800 (orange)
  - LOW: #FFC107 (amber)
  - INFO: #2196F3 (blue)

---

### UI-2: Dashboard Views

**Pages:**

1. **Home Dashboard**
   - Recent scans (last 10)
   - Overall statistics
   - Quick scan trigger
   - SBOM stats

2. **Scans List**
   - Paginated table
   - Filters: date, status, format
   - Sort: timestamp, severity

3. **Scan Detail**
   - Scan metadata
   - Findings table
   - SBOM viewer
   - Export buttons

4. **SBOM Explorer**
   - Component list
   - Dependency tree
   - License summary
   - Hash verification

5. **Baselines Management**
   - List of baselines
   - Create/update workflow
   - Baseline diff viewer

6. **Policy Configuration**
   - YAML editor
   - Live validation
   - Policy testing

7. **Settings**
   - API key management
   - User preferences
   - System health

---

## Security & Compliance

### SEC-1: Threat Model

**Assets:**
- ML model files
- SBOM data
- Scan results
- Baseline configurations
- API keys
- Audit logs

**Threats:**
1. Malicious model files (handled by scanner)
2. Unauthorized access to scan results
3. SBOM tampering
4. API key leakage
5. Denial of service

**Mitigations:**
1. Sandboxed scanning (no model execution)
2. API key authentication + rate limiting
3. SBOM versioning + hash verification
4. Secrets management best practices
5. Resource limits + timeouts

---

### SEC-2: Compliance

**Requirements:**
- **SOC 2**: Audit logging, access controls, SBOM generation
- **ISO 27001**: Security controls documentation
- **NIST SSDF**: Secure software development framework (SBOM compliance)
- **Executive Order 14028**: Software supply chain security (SBOM requirement)

**Audit Trail:**
- All scans logged with timestamp, user, result
- SBOM changes tracked with versioning
- Baseline modifications logged with approver
- API key usage logged

---

## Deployment Architecture

### DEPLOY-1: Installation Steps

```bash
# 1. Download release
curl -L https://releases.example.com/sentrascan-model-latest.tar.gz | tar xz
cd sentrascan-model

# 2. Configure
cp .env.example .env
vi .env  # Edit database, API keys, etc.

# 3. Start services
docker-compose up -d

# 4. Initialize database
docker-compose exec api sentrascan-model db migrate

# 5. Create first API key
docker-compose exec api sentrascan-model auth create --name "admin"

# 6. Access UI
open http://localhost:3100
```

**Requirements:**
- Docker 24+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space (for cache)

---

## Integration Points

### INT-1: CI/CD Integration

**GitHub Actions:**
```yaml
- name: Scan ML Model
  uses: docker://sentrascan-model:latest
  with:
    command: scan model.pkl --strict --sbom model.sbom.json
    fail-on: HIGH
```

**GitLab CI:**
```yaml
model-scan:
  image: sentrascan-model:latest
  script:
    - sentrascan-model scan model.pkl --format json --output report.json
  artifacts:
    reports:
      - report.json
      - model.sbom.json
```

---

### INT-2: REST API

**Endpoints:**
```
POST   /api/v1/scans                 # Trigger scan
GET    /api/v1/scans                 # List scans
GET    /api/v1/scans/{id}            # Get scan details
GET    /api/v1/scans/{id}/findings   # Get findings
GET    /api/v1/scans/{id}/sbom       # Download SBOM

POST   /api/v1/baselines             # Create baseline
GET    /api/v1/baselines             # List baselines
GET    /api/v1/baselines/{id}        # Get baseline
PUT    /api/v1/baselines/{id}        # Update baseline

GET    /api/v1/sboms                 # List SBOMs
GET    /api/v1/sboms/{id}            # Get SBOM
POST   /api/v1/sboms/compare         # Compare SBOMs

GET    /api/v1/stats                 # Statistics
GET    /api/v1/health                # Health check
```

---

## Non-Functional Requirements

### NFR-1: Availability
- **Target:** 99.9% uptime
- **Health Checks:** HTTP `/health` endpoint
- **Monitoring:** Prometheus metrics

### NFR-2: Maintainability
- **Code Coverage:** ≥80%
- **Documentation:** OpenAPI spec
- **Logging:** Structured JSON logs

### NFR-3: Usability
- **Time to First Scan:** <15 minutes
- **Learning Curve:** <5 minutes for CLI
- **Error Messages:** Actionable with remediation

### NFR-4: Portability
- **Platforms:** Linux (x86_64, ARM64), macOS (x86_64, ARM64)
- **Databases:** SQLite, PostgreSQL
- **Containers:** Docker, Kubernetes

---

## Roadmap & Milestones

### Phase 1: MVP (Weeks 1-6)

**Week 1-2: Core Integration**
- Install and test modelaudit
- Create Python wrapper
- Test all 30 scanners
- SBOM generation validation

**Week 3-4: CLI & Orchestrator**
- Build CLI (wraps modelaudit)
- Policy engine
- Baseline management
- Report formats

**Week 5-6: Docker & Testing**
- Docker image
- Integration tests
- Documentation
- CI/CD examples

**Deliverables:**
- Docker image
- CLI tool
- SBOM generation
- Basic documentation

---

### Phase 2: Enterprise Features (Weeks 7-12)

**Week 7-9: REST API & Database**
- FastAPI server
- PostgreSQL integration
- SBOM storage
- Authentication

**Week 10-12: Web UI**
- React dashboard
- Scan viewer
- SBOM explorer
- Policy editor

**Deliverables:**
- REST API
- Web UI
- Database-backed storage
- Admin guide

---

### Phase 3: Production Hardening (Weeks 13-18)

**Week 13-15: Advanced Features**
- RBAC
- Advanced policies
- Kubernetes Helm chart
- Performance optimization

**Week 16-18: Launch**
- Security hardening
- Comprehensive testing
- Complete documentation
- Production deployment

**Deliverables:**
- Production-ready system
- Kubernetes support
- Complete documentation
- Compliance reports

---

## Dependencies & Risks

### External Dependencies

| Dependency | Version | Risk | Mitigation |
|------------|---------|------|------------|
| modelaudit | 0.2.17 | Version pinned, Promptfoo-backed | Monitor releases, test upgrades |
| cyclonedx-python-lib | 11.5.0+ | Stable, OWASP-backed | Pin version, test SBOM output |
| fickling | 0.1.4 | Stable, Trail of Bits | Handled by modelaudit |
| FastAPI | 0.110+ | Widely used, stable | Pin minor version |
| PostgreSQL | 15+ | LTS, stable | Use managed service |

---

### Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **modelaudit API Changes** | Low | Medium | Pin version 0.2.17, test upgrades |
| **SBOM Format Changes** | Low | Low | CycloneDX 1.6 is stable |
| **False Positives** | Medium | Medium | Tunable policies, user feedback |
| **Large Model Performance** | Medium | Medium | Streaming mode, caching |
| **Cloud Auth Complexity** | Low | High | Clear documentation, env vars |

---

## Appendix

### A. Glossary

- **SBOM**: Software Bill of Materials - inventory of components
- **CycloneDX**: Industry-standard SBOM format
- **Deserialization**: Converting serialized data back to objects
- **Model Serialization Attack**: Malicious code in serialized models
- **Baseline**: Approved snapshot of model + SBOM
- **Drift**: Deviation from approved baseline

---

### B. References

- **modelaudit**: https://pypi.org/project/modelaudit
- **modelscan**: https://github.com/protectai/modelscan
- **picklescan**: https://github.com/mmaitre314/picklescan
- **CycloneDX**: https://cyclonedx.org/
- **NIST SSDF**: https://csrc.nist.gov/Projects/ssdf
- **EO 14028**: https://www.whitehouse.gov/briefing-room/presidential-actions/2021/05/12/executive-order-on-improving-the-nations-cybersecurity/

---

### C. Success Criteria

**Must Have (MVP):**
- [x] Scan 30+ model formats
- [x] Generate CycloneDX SBOM
- [x] CLI tool with JSON/Markdown output
- [x] Docker deployment
- [x] P95 scan time <30s (100MB model)

**Should Have (Phase 2):**
- [x] REST API
- [x] Web UI
- [x] Database storage
- [x] Baseline management
- [x] Policy engine

**Nice to Have (Phase 3):**
- [x] RBAC
- [x] Kubernetes support
- [x] SARIF output
- [x] Advanced analytics

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Product Owner** | ________________ | ________ | ____ |
| **Engineering Lead** | ________________ | ________ | ____ |
| **Security Lead** | ________________ | ________ | ____ |
| **MLOps Lead** | ________________ | ________ | ____ |

---

**Version History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-20 | Team | Initial PRD |

---

**Document Status:** 🟡 Draft - Awaiting Approval  
**Primary Engine:** modelaudit (30 scanners + SBOM)  
**Key Differentiator:** Only ML model scanner with built-in CycloneDX SBOM generation
