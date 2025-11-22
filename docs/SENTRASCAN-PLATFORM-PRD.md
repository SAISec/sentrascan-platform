# Product Requirements Document (PRD)
## SentraScan Platform: Unified AI/ML Security Scanner

**Unified Security Scanning for MCP Servers and ML Models**

---

## Document Control

| Field | Value |
|-------|-------|
| **Product Name** | SentraScan Platform |
| **Modules** | SentraScan-MCP, SentraScan-Model |
| **Version** | 1.0 |
| **Date** | August 2025 |
| **Status** | Draft for Approval |
| **Owner** | Security Engineering Team |
| **Classification** | Internal Use |

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Product Vision](#product-vision)
3. [Platform Architecture](#platform-architecture)
4. [Module 1: SentraScan-MCP](#module-1-sentrascan-mcp)
5. [Module 2: SentraScan-Model](#module-2-sentrascan-model)
6. [Shared Components](#shared-components)
7. [User Interfaces](#user-interfaces)
8. [Technical Requirements](#technical-requirements)
9. [Deployment Architecture](#deployment-architecture)
10. [Integration Points](#integration-points)
11. [Roadmap & Implementation](#roadmap--implementation)
12. [Appendix](#appendix)

---

## Executive Summary

### Problem Statement

Organizations deploying AI/ML systems face two critical security gaps:

**1. MCP Server Security (Agentic AI)**
- **Tool Poisoning**: Malicious MCP tool descriptions
- **Baseline Drift**: Unauthorized changes to approved MCP configurations (rug pull attacks)
- **Command Injection**: Embedded shell commands in tools
- **No Pre-Production Gates**: MCP servers deployed without validation

**2. ML Model Security (Model Files)**
- **Model Serialization Attacks**: Malicious code in model files (Pickle, PyTorch, TensorFlow)
- **Lack of SBOM**: No visibility into model components and dependencies
- **Supply Chain Vulnerabilities**: Untrusted models from Hugging Face, MLflow, cloud storage
- **Deserialization Exploits**: Arbitrary code execution when loading models

Currently, **no unified platform exists** to scan both MCP configurations and ML model files before production deployment.

---

### Solution

**SentraScan Platform** is a self-hosted, containerized security scanner that provides:

**Unified Capabilities:**
- **Dual-Module System**: MCP scanning + Model scanning in one platform
- **Shared Infrastructure**: Single CLI, API, UI, and database
- **100% Local Execution**: No external API dependencies
- **Docker-First**: Easy installation and deployment
- **Lightweight Database**: SQLite (default) or PostgreSQL for enterprise

**Module 1: SentraScan-MCP**
- Scans MCP server configurations (Claude Desktop, Cursor, Windsurf, VS Code)
- Detects tool poisoning, command injection, baseline drift
- Static analysis only (no runtime/prompt scanning)
- Uses mcp-checkpoint + Cisco Scanner (YARA-only mode)

**Module 2: SentraScan-Model**
- Scans 30+ ML model formats (Pickle, PyTorch, TensorFlow, ONNX, GGUF, etc.)
- Detects deserialization attacks and malicious code patterns
- Generates CycloneDX SBOM automatically
- Supports multiple sources (local, Hugging Face, MLflow, S3, GCS)
- Uses modelaudit (30 scanners) + optional modelscan/picklescan

---

### Value Proposition

| Stakeholder | Value |
|-------------|-------|
| **Security Teams** | Single platform for MCP + Model security, unified audit trails |
| **ML Engineers** | Fast feedback (<30s scans), model SBOM generation |
| **DevOps Teams** | One-click Docker deployment, easy CI/CD integration |
| **Compliance Teams** | Complete SBOM, baseline management, audit logs |

---

## Product Vision

### Vision Statement

"Enable every organization to deploy AI/ML systems with confidence through unified security scanning of MCP configurations and ML models, ensuring supply chain transparency and protection against serialization attacks."

### Guiding Principles

1. **Unified Platform**: One tool for MCP + Model security
2. **Security First**: Static analysis, no execution of untrusted code
3. **SBOM Native**: CycloneDX generation for models
4. **Developer Experience**: Sub-minute scans, clear output
5. **Enterprise Ready**: Docker-first, database-backed, RBAC-enabled
6. **Privacy First**: 100% local, zero external API calls
7. **License Clean**: Apache 2.0 / MIT only

---

## Platform Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────┐
│                  SentraScan Platform                    │
│                                                         │
│  ┌───────────────────────────────────────────────────┐ │
│  │            Unified Interface Layer                 │ │
│  │  • CLI (sentrascan)                               │ │
│  │  • REST API (FastAPI)                             │ │
│  │  • Web UI (React)                                 │ │
│  └─────────────┬───────────────────────────────────┬─┘ │
│                │                                   │   │
│                ▼                                   ▼   │
│  ┌─────────────────────────┐  ┌──────────────────────┐ │
│  │  Module 1:              │  │  Module 2:           │ │
│  │  SentraScan-MCP         │  │  SentraScan-Model    │ │
│  │                         │  │                      │ │
│  │  • mcp-checkpoint       │  │  • modelaudit (30)   │ │
│  │  • Cisco Scanner (YARA) │  │  • modelscan (opt)   │ │
│  │  • Baseline drift       │  │  • picklescan (opt)  │ │
│  │  • Static analysis      │  │  • SBOM (CycloneDX)  │ │
│  └─────────────┬───────────┘  └──────────┬───────────┘ │
│                │                         │             │
│                └──────────┬──────────────┘             │
│                           ▼                             │
│         ┌────────────────────────────────────────┐     │
│         │      Shared Components                 │     │
│         │  • Policy Engine                       │     │
│         │  • Baseline Management                 │     │
│         │  • Report Generator (JSON/MD/SARIF)    │     │
│         │  • Database (SQLite/PostgreSQL)        │     │
│         │  • Audit Logger                        │     │
│         └────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## Module 1: SentraScan-MCP

### Purpose

Scan MCP (Model Context Protocol) server configurations for security vulnerabilities before production deployment.

### Scope

**Included:**
- ✅ MCP server configuration scanning
- ✅ Tool poisoning detection
- ✅ Command injection patterns
- ✅ Baseline drift detection
- ✅ Cross-server tool shadowing
- ✅ Excessive permissions
- ✅ Hardcoded secrets in configs

**Excluded:**
- ❌ Runtime prompt injection scanning
- ❌ Jailbreak detection
- ❌ LLM-based analysis

### Core Features

#### 1. Auto-Discovery
Automatically discover MCP configurations from:
- Claude Desktop: `~/Library/Application Support/Claude/`
- Cursor: `~/.cursor/mcp.json`
- Windsurf: `~/.codeium/windsurf/mcp_config.json`
- VS Code: `~/.vscode/mcp.json`
- Custom paths via CLI flag

#### 2. Dual-Engine Scanning

**Engine 1: mcp-checkpoint (Primary)**
- Baseline drift detection
- Hardcoded secrets
- Command injection patterns
- Cross-server shadowing
- Excessive permissions
- Tool name ambiguity

**Engine 2: Cisco Scanner - YARA Only**
- Tool poisoning patterns
- Security violations
- Suspicious code execution
- No API, no LLM (YARA rules only)

#### 3. Baseline Management
- Create approved MCP configuration baselines
- Detect unauthorized changes (rug pull attacks)
- Version-controllable baseline files (JSON)
- Hash-based integrity verification

#### 4. Policy Enforcement
```yaml
mcp_policy:
  severity_threshold: HIGH
  block_issue_types:
    - tool_poisoning
    - command_injection
    - baseline_drift
    - hardcoded_secrets
  require_baseline: true
  allowlist:
    servers: ["trusted_server_1"]
```

---

## Module 2: SentraScan-Model

### Purpose

Scan ML model files for security vulnerabilities and generate SBOM before production deployment.

### Scope

**Included:**
- ✅ 30+ model format scanning
- ✅ Deserialization attack detection
- ✅ SBOM generation (CycloneDX 1.6)
- ✅ Multi-source support (local, HF, MLflow, S3, GCS)
- ✅ Baseline management for models

**Excluded:**
- ❌ Jupyter notebook scanning
- ❌ Secrets detection in code files
- ❌ PII detection

### Core Features

#### 1. Multi-Format Scanning (30+ Formats)

**Primary Scanner: modelaudit**
- 30 built-in scanners
- Formats: Pickle, PyTorch, TensorFlow, ONNX, GGUF, SafeTensors, H5, Keras, XGBoost, Flax/JAX, TensorRT, TFLite, OpenVINO, PMML, NumPy, and more
- Fickling integration for pickle analysis
- Smart detection and auto-configuration

**Optional Enhancements:**
- modelscan (H5/SavedModel depth)
- picklescan (Hugging Face direct access)

#### 2. SBOM Generation

**CycloneDX 1.6 Format:**
- Automatic component extraction
- License detection
- Hash verification (SHA-256, SHA-1, MD5)
- Dependency tree
- Vulnerability references (CVE-compatible)

#### 3. Multi-Source Support
```bash
# Local
sentrascan scan model model.pkl

# Hugging Face
sentrascan scan model hf://meta-llama/Llama-3.2-1B

# MLflow
sentrascan scan model models:/production/fraud-detector/v3

# S3/GCS
sentrascan scan model s3://ml-models/production/
sentrascan scan model gs://models-bucket/latest/
```

#### 4. Deserialization Attack Detection
- Arbitrary code execution (eval, exec, compile)
- OS command execution (os.system, subprocess)
- File system access
- Network operations
- Lambda/reduce abuse
- Unsafe imports

---

## Shared Components

### 1. Unified CLI

```bash
# Platform-wide commands
sentrascan version
sentrascan health
sentrascan doctor

# MCP module commands
sentrascan scan mcp [OPTIONS]
sentrascan baseline create mcp [OPTIONS]

# Model module commands
sentrascan scan model [OPTIONS]
sentrascan baseline create model [OPTIONS]

# Database commands
sentrascan db migrate
sentrascan db backup

# Server mode (REST API)
sentrascan server
```

**CLI Features:**
- Single binary for both modules
- Module selection via subcommands
- Consistent flags across modules
- Color-coded output
- Progress indicators
- Exit codes: 0 (pass), 1 (fail), 2 (error)

---

### 2. REST API

**Unified Endpoints:**

```
# Health & Info
GET    /api/v1/health
GET    /api/v1/version
GET    /api/v1/stats

# MCP Scanning
POST   /api/v1/mcp/scans
GET    /api/v1/mcp/scans
GET    /api/v1/mcp/scans/{id}
GET    /api/v1/mcp/scans/{id}/findings

# Model Scanning
POST   /api/v1/models/scans
GET    /api/v1/models/scans
GET    /api/v1/models/scans/{id}
GET    /api/v1/models/scans/{id}/findings
GET    /api/v1/models/scans/{id}/sbom

# Baselines (shared)
POST   /api/v1/baselines
GET    /api/v1/baselines
GET    /api/v1/baselines/{id}
PUT    /api/v1/baselines/{id}
DELETE /api/v1/baselines/{id}

# SBOMs (model-specific)
GET    /api/v1/sboms
GET    /api/v1/sboms/{id}
POST   /api/v1/sboms/compare

# Policies (shared)
GET    /api/v1/policies
PUT    /api/v1/policies

# Authentication
POST   /api/v1/auth/keys
GET    /api/v1/auth/keys
DELETE /api/v1/auth/keys/{id}
```

**API Features:**
- OpenAPI 3.0 specification
- API key authentication
- Rate limiting (100 req/min per key)
- JSON responses
- CORS support
- Request tracing (request_id)

---

### 3. Web UI

**Unified Dashboard:**

```
┌─────────────────────────────────────────────┐
│  SentraScan Platform         [Profile] [⚙️] │
├─────────────────────────────────────────────┤
│  📊 Dashboard                               │
│  ├─ MCP Scans       [42 total] [3 failed]  │
│  └─ Model Scans     [127 total] [5 failed] │
│                                             │
│  🔍 Recent Activity                         │
│  ┌─────────────────────────────────────┐   │
│  │ MCP: claude-desktop  ❌ 5m ago      │   │
│  │ Model: model.pkl     ✅ 12m ago     │   │
│  │ MCP: cursor          ✅ 1h ago      │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  📈 Statistics (Last 30 Days)               │
│  ┌──────────┬──────────┬──────────┐        │
│  │ 169      │ 94.1%    │ 67       │        │
│  │ Scans    │ Pass Rate│ Findings │        │
│  └──────────┴──────────┴──────────┘        │
└─────────────────────────────────────────────┘
```

**Pages:**

1. **Home Dashboard**
   - Unified view of MCP + Model scans
   - Recent activity (combined)
   - Overall statistics
   - Quick scan triggers

2. **MCP Scans**
   - List of MCP scans
   - Scan details with findings
   - Baseline management
   - Config viewer

3. **Model Scans**
   - List of model scans
   - Scan details with findings
   - SBOM viewer
   - Baseline management

4. **Baselines** (Unified)
   - MCP baselines
   - Model baselines
   - Comparison tool
   - Drift reports

5. **SBOMs** (Model-specific)
   - SBOM list
   - Component explorer
   - License summary
   - Dependency tree

6. **Policies**
   - MCP policies
   - Model policies
   - YAML editor
   - Policy testing

7. **Settings**
   - API keys
   - User preferences
   - System health
   - Module configuration

---

### 4. Database Schema

**Unified Database (SQLite/PostgreSQL):**

```sql
-- Scans table (unified)
CREATE TABLE scans (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    scan_type VARCHAR(20) NOT NULL,  -- 'mcp' or 'model'
    target_path VARCHAR(1024) NOT NULL,
    target_format VARCHAR(50),       -- 'mcp_config', 'pickle', 'pytorch', etc.
    target_hash VARCHAR(255),
    scan_status VARCHAR(20) NOT NULL,  -- 'completed', 'failed', 'pending'
    passed BOOLEAN,
    duration_ms INTEGER,
    total_findings INTEGER,
    critical_count INTEGER,
    high_count INTEGER,
    medium_count INTEGER,
    low_count INTEGER,
    baseline_id UUID REFERENCES baselines(id),
    sbom_id UUID REFERENCES sboms(id),  -- NULL for MCP scans
    metadata JSONB,
    created_by VARCHAR(255)
);

-- Findings table (unified)
CREATE TABLE findings (
    id UUID PRIMARY KEY,
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
    module VARCHAR(20) NOT NULL,     -- 'mcp' or 'model'
    scanner VARCHAR(50) NOT NULL,    -- 'mcp-checkpoint', 'cisco-yara', 'modelaudit', etc.
    severity VARCHAR(20) NOT NULL,
    category VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    location VARCHAR(255),
    evidence JSONB,
    remediation TEXT
);

-- Baselines table (unified)
CREATE TABLE baselines (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    baseline_type VARCHAR(20) NOT NULL,  -- 'mcp' or 'model'
    name VARCHAR(255) NOT NULL,
    description TEXT,
    target_hash VARCHAR(255) NOT NULL,
    content JSONB NOT NULL,
    scan_id UUID REFERENCES scans(id),
    sbom_id UUID REFERENCES sboms(id),   -- NULL for MCP baselines
    approved_by VARCHAR(255),
    approval_date TIMESTAMP,
    is_active BOOLEAN DEFAULT true
);

-- SBOMs table (model-specific)
CREATE TABLE sboms (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    model_name VARCHAR(255),
    model_version VARCHAR(50),
    bom_format VARCHAR(20) NOT NULL,     -- 'CycloneDX'
    spec_version VARCHAR(10) NOT NULL,   -- '1.6'
    content JSONB NOT NULL,
    hash VARCHAR(255) NOT NULL
);

-- API Keys table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP,
    is_revoked BOOLEAN DEFAULT false
);

-- Policies table (unified)
CREATE TABLE policies (
    id UUID PRIMARY KEY,
    policy_type VARCHAR(20) NOT NULL,    -- 'mcp' or 'model'
    name VARCHAR(255) NOT NULL,
    version VARCHAR(50),
    content JSONB NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

-- Audit log
CREATE TABLE audit_log (
    id UUID PRIMARY KEY,
    timestamp TIMESTAMP NOT NULL,
    user VARCHAR(255),
    module VARCHAR(20),              -- 'mcp', 'model', 'platform'
    action VARCHAR(100) NOT NULL,
    resource_type VARCHAR(50),
    resource_id UUID,
    details JSONB
);

-- Indexes
CREATE INDEX idx_scans_type_created ON scans(scan_type, created_at DESC);
CREATE INDEX idx_scans_status ON scans(scan_status);
CREATE INDEX idx_findings_scan ON findings(scan_id);
CREATE INDEX idx_baselines_type_active ON baselines(baseline_type, is_active);
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC);
```

---

### 5. Policy Engine (Unified)

**Configuration File:** `.sentrascan.yaml`

```yaml
# Platform-wide settings
platform:
  name: "Production AI/ML Policy"
  version: "1.0"
  
# MCP-specific policies
mcp:
  enabled: true
  severity_threshold: HIGH
  block_issues:
    - tool_poisoning
    - command_injection
    - baseline_drift
    - hardcoded_secrets
  require_baseline: true
  engines:
    mcp_checkpoint:
      enabled: true
      skip_ml_model: true  # Skip 500MB model
    cisco_yara:
      enabled: true
      analyzers: ["yara"]  # YARA only, no API/LLM

# Model-specific policies
model:
  enabled: true
  severity_threshold: HIGH
  block_issues:
    - arbitrary_code_execution
    - os_command_execution
    - file_system_access
  sbom_requirements:
    require_sbom: true
    require_licenses: true
    blocked_licenses:
      - GPL-3.0
      - AGPL-3.0
  engines:
    modelaudit:
      enabled: true
      strict_mode: true
    modelscan:
      enabled: false  # Optional
    picklescan:
      enabled: false  # Optional

# Shared settings
baseline:
  require_approval: true
  auto_update: false
  
reporting:
  formats: ["json", "markdown"]
  output_dir: "./reports"
  
notifications:
  enabled: false
  webhooks: []
```

---

## User Interfaces

### CLI Interface

```bash
# Installation
docker pull sentrascan/platform:latest

# Quick scan
sentrascan scan mcp --auto-discover
sentrascan scan model model.pkl

# With baseline
sentrascan scan mcp --baseline mcp-baseline.json
sentrascan scan model model.pkl --baseline model-baseline.json

# Create baseline
sentrascan baseline create mcp --name "production-mcp" -o mcp-baseline.json
sentrascan baseline create model model.pkl --name "fraud-v2" -o model-baseline.json

# Generate reports
sentrascan scan model model.pkl \
  --format json,markdown \
  --output report.json \
  --sbom model.sbom.json

# Server mode
sentrascan server --host 0.0.0.0 --port 8200

# Health check
sentrascan doctor
sentrascan health

# Version info
sentrascan version
```

---

### REST API Interface

**Trigger MCP Scan:**
```bash
curl -X POST http://localhost:8200/api/v1/mcp/scans \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "config_paths": ["~/.config/Claude/mcp.json"],
    "baseline_id": "uuid-baseline",
    "policy": "production"
  }'
```

**Trigger Model Scan:**
```bash
curl -X POST http://localhost:8200/api/v1/models/scans \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "model_path": "s3://models/fraud-detector.pkl",
    "generate_sbom": true,
    "baseline_id": "uuid-baseline",
    "policy": "production"
  }'
```

**Get Scan Results:**
```bash
curl http://localhost:8200/api/v1/models/scans/{scan_id} \
  -H "X-API-Key: your-api-key"
```

---

### Web UI Interface

**Tech Stack:**
- Framework: React 18+ or Vue 3+
- UI Library: Material-UI or Ant Design
- State Management: React Query or Pinia
- Build Tool: Vite
- Charts: Recharts or Chart.js

**Color Scheme:**
- Primary: #1976D2 (blue)
- Success: #4CAF50 (green)
- Warning: #FF9800 (orange)
- Error: #F44336 (red)
- Critical: #9C27B0 (purple)

**Features:**
- Real-time scan progress
- Unified dashboard (MCP + Model)
- Drill-down into findings
- SBOM explorer (models only)
- Baseline comparison
- Policy editor
- Export functionality (PDF, CSV, JSON)

---

## Technical Requirements

### TR-1: Technology Stack

**Backend:**
- Language: Python 3.11+
- Web Framework: FastAPI 0.110+
- Database: SQLite (default) / PostgreSQL 15+ (optional)
- ORM: SQLAlchemy 2.0+
- Task Queue: None (synchronous for MVP)
- Testing: pytest, pytest-asyncio

**MCP Module:**
- mcp-checkpoint 2.0.0
- cisco-ai-mcp-scanner 3.2.1 (YARA only)

**Model Module:**
- modelaudit 0.2.17+
- cyclonedx-python-lib 11.5.0+
- fickling 0.1.4 (via modelaudit)
- modelscan 0.8+ (optional)
- picklescan 0.0.32+ (optional)

**Frontend:**
- Framework: React 18+ or Vue 3+
- UI Library: Material-UI or Ant Design
- Build Tool: Vite

**DevOps:**
- Containerization: Docker 24+
- Orchestration: Docker Compose (MVP), Kubernetes (future)
- CI/CD: GitHub Actions / GitLab CI

---

### TR-2: Performance Requirements

| Metric | Target | Module |
|--------|--------|--------|
| **MCP Scan (10 servers)** | <60s | MCP |
| **Model Scan (10MB)** | <5s | Model |
| **Model Scan (100MB)** | <30s | Model |
| **Model Scan (1GB)** | <3min | Model (streaming) |
| **SBOM Generation** | <2s | Model |
| **API Response (P95)** | <500ms | Platform |
| **Database Query (P95)** | <100ms | Platform |
| **Memory Usage** | <2GB | Platform |
| **Startup Time** | <10s | Platform |

---

### TR-3: Scalability Requirements

**MVP (Single Instance):**
- Concurrent MCP scans: 5
- Concurrent Model scans: 5
- API throughput: 100 req/min
- Database: SQLite (up to 100K scans)

**Future (Distributed):**
- Concurrent scans: 50+ (queue-based)
- API throughput: 1000+ req/min
- Database: PostgreSQL cluster

---

## Deployment Architecture

### Docker Compose Stack

```yaml
version: '3.8'

services:
  sentrascan-api:
    image: sentrascan/platform:latest
    command: server --host 0.0.0.0 --port 8200
    ports:
      - "8200:8200"
    volumes:
      - ./data:/data
      - ./reports:/reports
      - ./sboms:/sboms
      - ./baselines:/baselines
      - ./cache:/cache
    environment:
      - DATABASE_URL=postgresql://sentrascan:password@db/sentrascan
      - SENTRASCAN_CONFIG=/config/sentrascan.yaml
      # MCP module
      - MCP_MODULE_ENABLED=true
      # Model module
      - MODEL_MODULE_ENABLED=true
      - MODELAUDIT_CACHE_DIR=/cache
      - HUGGINGFACE_TOKEN=${HF_TOKEN}
      - MLFLOW_TRACKING_URI=${MLFLOW_URI}
      - AWS_ACCESS_KEY_ID=${AWS_KEY}
      - AWS_SECRET_ACCESS_KEY=${AWS_SECRET}
    depends_on:
      - db
      - redis

  sentrascan-web:
    image: sentrascan/platform-web:latest
    ports:
      - "3200:80"
    environment:
      - API_URL=http://sentrascan-api:8200
    depends_on:
      - sentrascan-api

  db:
    image: postgres:15-alpine
    volumes:
      - pg-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=sentrascan
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

### Installation Steps

```bash
# 1. Download and extract
curl -L https://releases.example.com/sentrascan-latest.tar.gz | tar xz
cd sentrascan

# 2. Configure
cp .env.example .env
vi .env  # Edit configuration

# 3. Start platform
docker-compose up -d

# 4. Initialize database
docker-compose exec sentrascan-api sentrascan db migrate

# 5. Create API key
docker-compose exec sentrascan-api sentrascan auth create --name "admin"

# 6. Access UI
open http://localhost:3200

# 7. Verify modules
docker-compose exec sentrascan-api sentrascan doctor
```

**System Requirements:**
- Docker 24+
- Docker Compose 2.0+
- 4GB RAM minimum
- 20GB disk space
- Linux (x86_64, ARM64) or macOS (x86_64, ARM64)

---

## Integration Points

### CI/CD Integration

**GitHub Actions:**
```yaml
name: AI/ML Security Scan

on: [pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      # Scan MCP configs
      - name: Scan MCP Configuration
        uses: docker://sentrascan/platform:latest
        with:
          args: scan mcp --config .mcp/config.json --strict
      
      # Scan ML models
      - name: Scan ML Models
        uses: docker://sentrascan/platform:latest
        with:
          args: scan model models/*.pkl --strict --sbom sboms/
      
      # Upload artifacts
      - uses: actions/upload-artifact@v3
        with:
          name: scan-reports
          path: |
            reports/
            sboms/
```

**GitLab CI:**
```yaml
sentrascan:
  image: sentrascan/platform:latest
  script:
    # Scan MCP
    - sentrascan scan mcp --config .mcp/config.json --format json -o mcp-report.json
    # Scan models
    - sentrascan scan model models/ --format json -o model-report.json --sbom sboms/
  artifacts:
    reports:
      - mcp-report.json
      - model-report.json
      - sboms/
```

---

### Python SDK (Future)

```python
from sentrascan import SentraScan

# Initialize
scanner = SentraScan(
    api_url="http://localhost:8200",
    api_key="your-api-key"
)

# Scan MCP config
mcp_result = scanner.mcp.scan(
    config_path="~/.config/Claude/mcp.json",
    baseline="mcp-baseline.json"
)

# Scan model
model_result = scanner.model.scan(
    model_path="model.pkl",
    generate_sbom=True,
    baseline="model-baseline.json"
)

# Check results
if not mcp_result.passed or not model_result.passed:
    print("Security scan failed!")
    exit(1)
```

---

## Roadmap & Implementation

### Phase 1: MVP (Weeks 1-8)

**Week 1-2: Core Infrastructure**
- Unified CLI framework
- Database schema
- Docker setup
- Basic API structure

**Week 3-4: MCP Module**
- mcp-checkpoint integration
- Cisco Scanner (YARA) integration
- MCP baseline management
- MCP policy engine

**Week 5-6: Model Module**
- modelaudit integration
- SBOM generation
- Model baseline management
- Model policy engine

**Week 7-8: Integration & Testing**
- Unified reporting
- CLI refinement
- Integration tests
- Documentation

**Deliverables:**
- Docker image (CLI mode)
- SQLite database
- Unified policy engine
- Basic documentation

---

### Phase 2: Enterprise Features (Weeks 9-16)

**Week 9-11: REST API**
- FastAPI implementation
- API authentication
- PostgreSQL support
- API documentation (OpenAPI)

**Week 12-14: Web UI**
- React dashboard
- Unified scan viewer
- SBOM explorer
- Policy editor

**Week 15-16: Advanced Features**
- RBAC
- Audit logging
- Baseline comparison UI
- Webhook notifications

**Deliverables:**
- REST API server
- Web UI
- PostgreSQL support
- Admin guide

---

### Phase 3: Production Hardening (Weeks 17-24)

**Week 17-19: Optimization**
- Performance tuning
- Parallel scanning
- Caching strategy
- Resource optimization

**Week 20-22: Enterprise Features**
- Kubernetes Helm chart
- Multi-tenancy
- Advanced RBAC
- SSO integration (SAML/OIDC)

**Week 23-24: Launch**
- Security hardening
- Comprehensive testing
- Complete documentation
- Production deployment

**Deliverables:**
- Production-ready platform
- Kubernetes support
- Enterprise features
- Compliance reports

---

## Success Metrics

### Adoption Metrics
- ✅ 20+ teams onboarded (first 6 months)
- ✅ 200+ scans/day (steady state)
- ✅ 80% CI/CD integration rate

### Quality Metrics
- ✅ <5% false positive rate (both modules)
- ✅ 95%+ threat detection rate
- ✅ 100% SBOM generation success (models)

### Performance Metrics
- ✅ P95 MCP scan time <60s (10 servers)
- ✅ P95 Model scan time <30s (100MB)
- ✅ API P95 response time <500ms
- ✅ 99.9% uptime

---

## Appendix

### A. Glossary

- **MCP**: Model Context Protocol for AI agent tool execution
- **SBOM**: Software Bill of Materials - inventory of components
- **CycloneDX**: Industry-standard SBOM format
- **Baseline**: Approved snapshot of MCP config or model
- **Drift**: Deviation from approved baseline
- **Rug Pull**: Malicious modification of trusted components
- **Tool Poisoning**: Injection of malicious code in MCP tools

---

### B. Module Comparison

| Feature | SentraScan-MCP | SentraScan-Model |
|---------|---------------|------------------|
| **Purpose** | MCP config security | Model file security |
| **Scan Target** | JSON configs | Binary model files |
| **Primary Engine** | mcp-checkpoint | modelaudit |
| **Formats** | 1 (MCP JSON) | 30+ (Pickle, PT, TF, etc.) |
| **SBOM** | ❌ | ✅ CycloneDX |
| **Baseline** | ✅ | ✅ |
| **Policy** | ✅ | ✅ |
| **Sources** | Local configs | Local, HF, MLflow, S3, GCS |
| **Avg Scan Time** | 30-60s (10 servers) | 5-30s (typical model) |

---

### C. References

**MCP Module:**
- mcp-checkpoint: https://github.com/aira-security/mcp-checkpoint
- cisco-ai-mcp-scanner: https://github.com/cisco-ai-defense/mcp-scanner
- MCP Protocol: https://modelcontextprotocol.io/

**Model Module:**
- modelaudit: https://pypi.org/project/modelaudit
- modelscan: https://github.com/protectai/modelscan
- picklescan: https://github.com/mmaitre314/picklescan
- CycloneDX: https://cyclonedx.org/

**Standards:**
- NIST SSDF: https://csrc.nist.gov/Projects/ssdf
- Executive Order 14028: Software supply chain security
- OWASP Top 10 for LLMs: https://owasp.org/www-project-top-10-for-large-language-model-applications/

---

### D. Document Approval

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
| 1.0 | 2025-01-20 | Team | Initial unified PRD |

---

**Document Status:** 🟡 Draft - Awaiting Approval  
**Scope:** Unified platform with MCP + Model scanning modules  
**Key Differentiator:** Only platform scanning both MCP configs and ML models with shared infrastructure
