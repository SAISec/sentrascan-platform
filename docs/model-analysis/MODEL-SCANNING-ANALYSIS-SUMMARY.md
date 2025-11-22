# Model Security Scanning Tools - Analysis Summary
## For SentraScan-Model Product Development

**Analysis Date**: January 2025  
**Purpose**: Evaluate open-source model scanning tools for building SentraScan-Model

---

## Executive Summary

Analyzed **4 open-source tools** for ML model security scanning:
1. **picklescan** (Matthieu Maitre/Microsoft) - Lightweight pickle scanner
2. **modelscan** (Protect AI) - Multi-format enterprise scanner
3. **model-unpickler** (Goeckslab) - Safe model loading library
4. **watchtower** (Bosch AIShield) - Comprehensive AI/ML security platform

**Note**: `modelaudit` (PyPI) was inaccessible during analysis.

**Recommendation**: Build **SentraScan-Model** using **ModelScan** as primary engine + **picklescan** for enhanced pickle analysis + **Watchtower concepts** for notebook/secrets scanning.

---

## Tool Comparison Matrix

| Feature | picklescan | modelscan | model-unpickler | watchtower |
|---------|-----------|-----------|-----------------|------------|
| **License** | MIT | Apache 2.0 | MIT | Apache 2.0 |
| **Maturity** | Stable | Production | Research | Production |
| **Stars** | ~600 | ~600 | ~1 | ~200 |
| **Pickle Scanning** | ✅ Excellent | ✅ Excellent | ✅ Safe Loading | ✅ Good |
| **H5/Keras** | ❌ | ✅ | ❌ | ✅ |
| **TensorFlow (.pb)** | ❌ | ✅ | ❌ | ✅ |
| **Protocol Buffer** | ❌ | ✅ | ❌ | ✅ |
| **ONNX** | ❌ | ❌ | ❌ | Partial |
| **Notebook Scanning** | ❌ | ❌ | ❌ | ✅ |
| **Secrets Detection** | ❌ | ❌ | ❌ | ✅ |
| **PII Detection** | ❌ | ❌ | ❌ | ✅ |
| **Dependency Scanning** | ❌ | ❌ | ❌ | ✅ |
| **Hugging Face Direct** | ✅ | ❌ | ❌ | ✅ |
| **AWS S3 Support** | ❌ | ❌ | ❌ | ✅ |
| **CLI** | ✅ | ✅ | ❌ | ✅ |
| **Web UI** | ❌ | ❌ | ❌ | ✅ |
| **Python API** | ✅ | ✅ | ✅ | ❌ |
| **Severity Levels** | Binary | 4-level | Binary | 4-level |
| **Exit Codes** | 3 codes | 5 codes | N/A | N/A |
| **Report Formats** | Console | Console/JSON/Custom | N/A | JSON |

---

## Detailed Tool Analysis

### 1. picklescan (MIT License)

**Purpose**: Lightweight scanner for Python Pickle files

**Strengths:**
- ✅ Zero dependencies (pure Python)
- ✅ Extremely fast (2s for 100MB model)
- ✅ Direct Hugging Face integration
- ✅ Clean, simple API
- ✅ Well-documented with security research references
- ✅ MIT license (most permissive)

**Limitations:**
- ❌ Pickle-only (no H5, PB, ONNX)
- ❌ No notebook scanning
- ❌ No secrets/PII detection
- ❌ No baseline management

**Best For**: Pickle-specific scanning, Hugging Face models, lightweight deployments

---

### 2. modelscan (Apache 2.0 License) ⭐ **RECOMMENDED PRIMARY**

**Purpose**: Multi-format model serialization attack scanner

**Strengths:**
- ✅ **Multi-format support** (Pickle, H5, SavedModel, Keras V3)
- ✅ **Enterprise-grade** (Protect AI backed, active development)
- ✅ **Python 3.10-3.12** support
- ✅ **Pluggable architecture** (scanners, middlewares, reporters)
- ✅ **Severity ranking** (CRITICAL, HIGH, MEDIUM, LOW)
- ✅ **Configurable** (settings via TOML)
- ✅ **Multiple report formats** (console, JSON, custom)
- ✅ **Exit codes** for CI/CD integration
- ✅ **Python API** for programmatic use
- ✅ **Extensive documentation** + Jupyter notebooks with attack examples
- ✅ **Apache 2.0** license (enterprise-friendly)

**Limitations:**
- ❌ No notebook scanning
- ❌ No secrets/PII detection
- ❌ No direct Hugging Face/S3 support (file-based only)
- ❌ No Web UI

**Architecture:**
```
modelscan/
├── scanners/          # Format-specific scanners
│   ├── pickle/
│   ├── h5/
│   └── saved_model/
├── middlewares/       # Pre/post-processing
├── reporting/         # Output formatters
├── issues.py          # Issue management
└── modelscan.py       # Orchestrator
```

**Best For**: Production ML pipelines, multi-framework environments, CI/CD integration

---

### 3. model-unpickler (MIT License)

**Purpose**: Safe model loading library with whitelist-based approach

**Strengths:**
- ✅ Whitelist-based security (only approved globals)
- ✅ Scikit-learn/Galaxy-ML integration
- ✅ PyTorch compatible
- ✅ Prevents execution during load
- ✅ Customizable whitelist

**Limitations:**
- ❌ Not a scanner (prevents, doesn't detect)
- ❌ Requires code changes (not drop-in)
- ❌ Research-level (1 star, inactive since 2021)
- ❌ No CLI tool
- ❌ No multi-format support

**Best For**: Safe model loading in controlled environments (not scanning)

**Note**: Interesting whitelist concept but not suitable as primary scanner

---

### 4. watchtower (Apache 2.0 License) ⭐ **COMPREHENSIVE FEATURES**

**Purpose**: Comprehensive AI/ML model and notebook security platform

**Strengths:**
- ✅ **Broadest coverage** (models + notebooks + dependencies)
- ✅ **Multi-format models** (Pickle, H5, PB, Keras, PyTorch, ONNX, GGUF)
- ✅ **Jupyter notebook scanning** (hardcoded secrets, PII, tokens)
- ✅ **Python file scanning** (.py files)
- ✅ **requirements.txt scanning** (outdated/vulnerable libraries)
- ✅ **Secrets detection** (API keys, passwords, tokens)
- ✅ **PII detection** (personal information)
- ✅ **Multiple repo sources** (GitHub, Hugging Face, AWS S3, local)
- ✅ **Web UI** + CLI + Docker deployment
- ✅ **Three report types** (summary, severity mapping, detailed)
- ✅ **4-level severity** (Critical, High, Medium, Low)
- ✅ **OWASP/MITRE/CWE/NIST AI RMF alignment**
- ✅ **Enterprise backing** (Bosch)

**Limitations:**
- ❌ Complex codebase (PyArmor obfuscated modules)
- ❌ No Python API (CLI/UI only)
- ❌ Heavier dependencies
- ❌ Linux-only for some features (.pb scanning)
- ❌ Known issues: false positives, manual cleanup required

**Architecture:**
```
watchtower/
├── src/
│   ├── modules/              # Scanner modules
│   ├── utils/                # Utility functions
│   ├── watchtower.py         # CLI
│   └── watchtower_webapp.py  # Web UI
├── external_files/           # Detection rules
└── pyarmor_runtime*/         # Obfuscated code
```

**Best For**: Comprehensive security audits, notebook environments, enterprise deployments

---

## Feature Coverage Analysis

### Deserialization Attack Detection

| Tool | Pickle | H5 | SavedModel | Keras V3 | ONNX |
|------|--------|----|-----------|---------| -----|
| picklescan | ✅✅✅ | ❌ | ❌ | ❌ | ❌ |
| modelscan | ✅✅✅ | ✅✅ | ✅✅ | ✅✅ | ❌ |
| model-unpickler | ✅ (prevent) | ❌ | ❌ | ❌ | ❌ |
| watchtower | ✅✅ | ✅ | ✅ | ✅ | ✅ (partial) |

✅✅✅ = Excellent, ✅✅ = Good, ✅ = Basic

---

### Threat Coverage

| Threat Type | picklescan | modelscan | model-unpickler | watchtower |
|-------------|-----------|-----------|-----------------|------------|
| **Arbitrary Code Execution** | ✅ | ✅ | ✅ | ✅ |
| **Credential Theft** | ✅ | ✅ | ✅ | ✅ |
| **Data Exfiltration** | ✅ | ✅ | ✅ | ✅ |
| **Model Poisoning** | ❌ | ❌ | ❌ | ❌ |
| **Backdoor Triggers** | ❌ | ❌ | ❌ | ✅ (TF) |
| **Hardcoded Secrets** | ❌ | ❌ | ❌ | ✅ |
| **PII Leakage** | ❌ | ❌ | ❌ | ✅ |
| **Vulnerable Dependencies** | ❌ | ❌ | ❌ | ✅ |

---

## Licensing Analysis

| Tool | License | Commercial Use | Modification | Distribution | Enterprise-Friendly |
|------|---------|---------------|--------------|--------------|---------------------|
| picklescan | MIT | ✅ | ✅ | ✅ | ✅✅✅ |
| modelscan | Apache 2.0 | ✅ | ✅ | ✅ | ✅✅ |
| model-unpickler | MIT | ✅ | ✅ | ✅ | ✅✅✅ |
| watchtower | Apache 2.0 | ✅ | ✅ | ✅ | ✅✅ |

**License Compatibility:**
- MIT + Apache 2.0 = ✅ Fully compatible
- Can combine all tools in SentraScan-Model
- Recommend Apache 2.0 for final product (stronger patent protection)

---

## Architecture Recommendation for SentraScan-Model

### Hybrid Multi-Engine Approach

```
┌─────────────────────────────────────────────┐
│         SentraScan-Model Platform           │
│                                             │
│  ┌──────────────────────────────────────┐  │
│  │  Orchestrator & Policy Engine        │  │
│  └──────────────┬───────────────────────┘  │
│                 │                           │
│    ┌────────────┴────────────┐             │
│    │                         │             │
│    ▼                         ▼             │
│  ┌─────────────┐      ┌─────────────┐     │
│  │ Model       │      │ Notebook &  │     │
│  │ Scanner     │      │ Code Scanner│     │
│  │ Engine      │      │ Engine      │     │
│  │             │      │             │     │
│  │ • modelscan │      │ • detect-   │     │
│  │   (primary) │      │   secrets   │     │
│  │ • picklescan│      │ • whispers  │     │
│  │   (enhanced)│      │ • presidio  │     │
│  └─────────────┘      └─────────────┘     │
│         │                     │            │
│         └──────────┬──────────┘            │
│                    ▼                       │
│         ┌─────────────────────┐           │
│         │ Report Generator    │           │
│         │ • JSON              │           │
│         │ • Markdown          │           │
│         │ • SARIF             │           │
│         └─────────────────────┘           │
└─────────────────────────────────────────────┘
```

---

## Recommended Technology Stack

### Core Engines

**1. ModelScan (Primary Multi-Format Scanner)**
- Version: 0.8+ (latest)
- License: Apache 2.0
- Role: Primary orchestrator + H5/SavedModel/Pickle scanning
- Reasoning: Production-ready, extensible, well-maintained

**2. Picklescan (Enhanced Pickle Analysis)**
- Version: 0.0.32+
- License: MIT
- Role: Specialized pickle deep analysis + Hugging Face integration
- Reasoning: Lightweight, excellent pickle coverage, HF direct access

**3. Watchtower Components (Notebook & Secrets)**
- Version: Latest
- License: Apache 2.0
- Role: Notebook scanning, secrets detection, PII detection
- Extract specific modules:
  - `detect-secrets` integration
  - `whispers` for secrets
  - `presidio` for PII
  - Notebook vulnerability patterns

---

## What to Build

### SentraScan-Model Feature Set

#### Phase 1: Core Model Scanning (Weeks 1-6)

**FR-1: Multi-Format Model Scanning**
- ✅ Pickle/Joblib/Dill (.pkl, .pth, .bin, .pt)
- ✅ H5/Keras (.h5, .keras)
- ✅ TensorFlow SavedModel (.pb)
- ✅ Protocol Buffer parsing
- ✅ Numpy arrays (.npy)

**FR-2: Deserialization Attack Detection**
- ✅ Arbitrary code execution patterns
- ✅ Dangerous global imports
- ✅ Filesystem operations
- ✅ Network operations
- ✅ Subprocess execution

**FR-3: Severity Classification**
- CRITICAL: Immediate code execution
- HIGH: Credential theft potential
- MEDIUM: Suspicious patterns
- LOW: Informational findings

**FR-4: Report Formats**
- JSON (machine-readable)
- Markdown (human-readable)
- SARIF (GitHub Code Scanning)

**FR-5: Input Sources**
- Local files/directories
- Hugging Face models
- URLs (direct HTTP/HTTPS)
- AWS S3 buckets
- GitHub repositories

---

#### Phase 2: Notebook & Code Scanning (Weeks 7-12)

**FR-6: Jupyter Notebook Scanning**
- ✅ Hardcoded secrets (API keys, passwords)
- ✅ PII detection (emails, SSNs, phone numbers)
- ✅ Unsafe operations (os.system, eval, exec)
- ✅ Credential exposure

**FR-7: Python File Scanning**
- ✅ .py files in repositories
- ✅ requirements.txt vulnerability scanning
- ✅ Deprecated/unsafe library detection

**FR-8: Secrets Detection**
- API keys (AWS, Azure, GCP, OpenAI, etc.)
- Passwords and tokens
- Private keys and certificates
- Database connection strings

**FR-9: PII Detection**
- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers
- IP addresses

---

#### Phase 3: Enterprise Features (Weeks 13-18)

**FR-10: Baseline Management**
- Create approved model baselines
- Detect drift from baselines
- Version control integration

**FR-11: Policy Engine**
- Configurable severity thresholds
- Issue type filtering
- Allow/block lists
- Custom rules

**FR-12: Provenance Tracking**
- Model source tracking
- Author attribution
- Download timestamps
- Scan history

**FR-13: Integration Points**
- REST API
- Python SDK
- CLI tool
- GitHub Actions
- GitLab CI
- Pre-commit hooks

**FR-14: Reporting & Audit**
- SQLite/PostgreSQL database
- Historical scan tracking
- Compliance reports
- Executive dashboards

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
      - MODELSCAN_CONFIG=/config/modelscan.toml
      - PICKLESCAN_ENABLED=true
      - NOTEBOOK_SCAN_ENABLED=true
    volumes:
      - ./models:/scan
      - ./reports:/reports
      - ./baselines:/baselines
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
```

---

## Key Differentiators from Existing Tools

### Why Build SentraScan-Model?

| Feature | Existing Tools | SentraScan-Model |
|---------|---------------|------------------|
| **Multi-Engine** | Single engine | Hybrid (modelscan + picklescan + watchtower concepts) |
| **Notebook + Model** | Separate tools | Unified platform |
| **Baseline Management** | None | Full drift detection |
| **Provenance Tracking** | Basic | Complete audit trail |
| **Policy Engine** | Limited | Advanced with custom rules |
| **Web UI + API** | CLI-only (mostly) | Full-stack platform |
| **Database-Backed** | File-based | PostgreSQL/SQLite with history |
| **Enterprise Features** | Open-source only | RBAC, multi-tenancy, compliance |
| **Local Execution** | Varies | 100% on-premises, no external APIs |

---

## Non-Functional Requirements

### Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Model Scan (P95)** | <30s | 100MB pickle file |
| **Notebook Scan (P95)** | <10s | 1000-line .ipynb file |
| **Memory Usage** | <2GB | Per scan worker |
| **Concurrent Scans** | 10+ | Parallel execution |
| **Startup Time** | <10s | Container cold start |

### Scalability

- **MVP**: 50 scans/day, single instance
- **Production**: 1000+ scans/day, distributed workers

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **ModelScan API Changes** | Medium | High | Pin version, test upgrades |
| **Picklescan Maintenance** | Low | Medium | Fork if needed, simple codebase |
| **False Positives** | Medium | Medium | Tunable policies, user feedback loop |
| **License Compliance** | Low | High | Apache 2.0 for entire product |
| **Performance Issues** | Low | Medium | Async scanning, worker pools |

---

## Implementation Roadmap

### Phase 1: MVP (6 weeks)

**Deliverables:**
- CLI tool with model scanning
- ModelScan + Picklescan integration
- JSON/Markdown reporting
- Docker image
- Basic documentation

**Stack:**
- Python 3.11+
- ModelScan 0.8+
- Picklescan 0.0.32+
- Click (CLI)
- FastAPI (future API)

---

### Phase 2: Enterprise Features (6 weeks)

**Deliverables:**
- Notebook & secrets scanning
- REST API
- SQLite database
- Baseline management
- Web UI (React)

**Stack:**
- FastAPI 0.110+
- SQLAlchemy 2.0+
- SQLite/PostgreSQL
- React 18+
- Material-UI

---

### Phase 3: Production Hardening (6 weeks)

**Deliverables:**
- Policy engine
- RBAC & multi-tenancy
- Kubernetes Helm chart
- Comprehensive testing
- Complete documentation

**Stack:**
- Docker Compose
- Kubernetes
- Prometheus metrics
- OpenTelemetry

---

## Success Metrics

### Adoption Metrics
- ✅ 10+ teams onboarded (first 3 months)
- ✅ 100+ scans/day (steady state)
- ✅ 80% CI/CD integration rate

### Quality Metrics
- ✅ <5% false positive rate
- ✅ 95%+ threat detection rate
- ✅ 99.9% uptime (production)

### Performance Metrics
- ✅ P95 scan time <30s
- ✅ API response time <500ms
- ✅ Zero external API dependencies

---

## Conclusion

**Primary Recommendation: Build SentraScan-Model on ModelScan + Picklescan foundation**

**Reasoning:**
1. **ModelScan** provides production-ready multi-format scanning
2. **Picklescan** adds enhanced pickle analysis + Hugging Face integration
3. **Watchtower concepts** (secrets/PII/notebooks) fill critical gaps
4. **All Apache 2.0/MIT** licenses enable commercial product
5. **Extensible architecture** allows future enhancements
6. **Enterprise-grade** foundations from established vendors

**Next Steps:**
1. Clone ModelScan and Picklescan repositories
2. Create PoC integrating both engines
3. Add notebook scanning module (borrow from Watchtower concepts)
4. Build orchestrator with policy engine
5. Develop REST API and CLI
6. Create Docker deployment
7. Build Web UI
8. Comprehensive testing and documentation

---

## Appendix: Tool Repositories

| Tool | Repository | Documentation |
|------|-----------|---------------|
| picklescan | https://github.com/mmaitre314/picklescan | README.md |
| modelscan | https://github.com/protectai/modelscan | docs/ folder |
| model-unpickler | https://github.com/goeckslab/model-unpickler | README.md |
| watchtower | https://github.com/bosch-aisecurity-aishield/watchtower | README.md |

---

**Document Status:** ✅ Complete - Ready for PRD Development
