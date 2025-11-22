# Product Requirements Document (PRD)
## SentraScan-MCP: Static Security Scanner for MCP Servers

---

## Document Control

| Field | Value |
|-------|-------|
| **Product Name** | SentraScan-MCP |
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

Organizations deploying MCP (Model Context Protocol) servers face security risks including:
- **Tool poisoning** - malicious MCP tool descriptions
- **Command injection** - embedded shell commands in tools
- **Hardcoded secrets** - API keys/passwords in configurations
- **Baseline drift** - unauthorized changes to approved MCP components (rug pull attacks)
- **Cross-server conflicts** - tool name collisions across servers

Currently, no unified solution exists for **pre-production static analysis** of MCP configurations before go-live.

### Solution

**SentraScan-MCP** is a self-hosted, containerized static security scanner that:
- Analyzes MCP server configurations before production deployment
- Detects security vulnerabilities using two complementary engines
- Enforces baseline policies with drift detection
- Provides CLI, REST API, and Web UI interfaces
- Operates **100% locally** with no external API dependencies
- Maintains scan history in a local database

### Value Proposition

| Stakeholder | Value |
|-------------|-------|
| **Security Teams** | Automated pre-prod security gates, audit trails, compliance |
| **Development Teams** | Fast feedback (<1 min scans), clear remediation guidance |
| **DevOps Teams** | Easy CI/CD integration, containerized deployment |
| **Compliance Teams** | Complete audit logs, baseline management, no data exfiltration |

---

## Product Vision

### Vision Statement

"Enable every organization to deploy MCP servers with confidence through automated, lightning-fast static security analysis that runs entirely on-premises."

### Guiding Principles

1. **Privacy First:** 100% local execution, zero external API calls
2. **Developer Experience:** Sub-minute scans, clear actionable output
3. **Enterprise Ready:** Docker-first, database-backed, RBAC-enabled
4. **License Clean:** Apache 2.0 only, no GPL contamination
5. **CI/CD Native:** Designed for automation, not manual testing

---

## Goals & Success Metrics

### Primary Goals

| Goal | Success Metric | Target |
|------|----------------|--------|
| **G1: Fast Scans** | P95 scan time for 10 servers | <60 seconds |
| **G2: High Coverage** | Static threat detection rate | ≥95% |
| **G3: Easy Adoption** | Time to first scan (new team) | <15 minutes |
| **G4: CI/CD Integration** | Pipelines using SentraScan-MCP | 80% of MCP deployments |
| **G5: Zero External Deps** | External API calls per scan | 0 |

### Key Performance Indicators (KPIs)

**Adoption Metrics:**
- Number of teams onboarded
- Scans per day (target: 100+)
- CI/CD integration rate

**Quality Metrics:**
- False positive rate (target: <5%)
- Critical findings detected (track trend)
- Baseline drift detection accuracy

**Performance Metrics:**
- P50, P95, P99 scan latency
- System resource usage (CPU, memory, disk)
- API response times (P95 <500ms)

---

## User Personas

### Persona 1: DevOps Engineer (Primary)

**Name:** Alex  
**Role:** DevOps/Platform Engineer  
**Goals:**
- Integrate security scanning into CI/CD pipelines
- Get fast, reliable scan results
- Minimize false positives
- Avoid manual security reviews for every deployment

**Pain Points:**
- Current manual security reviews slow down deployments
- External security tools require API keys and internet access
- Inconsistent security standards across teams

**How SentraScan-MCP Helps:**
- CLI tool with clear exit codes for CI/CD
- Docker container runs in isolated pipelines
- Consistent policy enforcement

---

### Persona 2: Security Engineer (Secondary)

**Name:** Morgan  
**Role:** Application Security Engineer  
**Goals:**
- Define and enforce security policies for MCP deployments
- Track security findings over time
- Generate audit reports for compliance
- Investigate security incidents

**Pain Points:**
- No visibility into MCP server configurations before prod
- Manual review doesn't scale
- Lack of audit trail for configuration changes

**How SentraScan-MCP Helps:**
- Web UI dashboard for findings review
- Database stores complete scan history
- Baseline management with drift alerts
- Exportable audit reports

---

### Persona 3: Software Developer (Tertiary)

**Name:** Jordan  
**Role:** Application Developer  
**Goals:**
- Get fast feedback on MCP configuration issues
- Understand and fix security findings quickly
- Avoid security surprises in prod

**Pain Points:**
- Security issues discovered late in deployment cycle
- Unclear remediation guidance
- Blocked deployments without context

**How SentraScan-MCP Helps:**
- Clear, actionable error messages
- Remediation guidance in reports
- Fast local scans during development

---

## Functional Requirements

### FR-1: Core Scanning Engine

#### FR-1.1: Auto-Discovery
**Priority:** P0 (Must Have)  
**Description:** Automatically discover MCP configurations from well-known locations

**Acceptance Criteria:**
- [x] Discover Claude Desktop configs (`~/Library/Application Support/Claude/`)
- [x] Discover Cursor configs (`~/.cursor/mcp.json`)
- [x] Discover Windsurf configs (`~/.codeium/windsurf/mcp_config.json`)
- [x] Discover VS Code configs (`~/.vscode/mcp.json`)
- [x] Support custom config paths via CLI flag
- [x] Handle multiple config files in single scan

**Technical Notes:**
- Use mcp-checkpoint and Cisco Scanner discovery capabilities
- Merge discovered configs, deduplicate servers

---

#### FR-1.2: Dual-Engine Scanning
**Priority:** P0 (Must Have)  
**Description:** Run two complementary security engines

**Engines:**

1. **mcp-checkpoint Engine:**
   - Baseline drift detection
   - Hardcoded secrets
   - Command injection patterns
   - Cross-server shadowing
   - Excessive permissions
   - Tool name ambiguity

2. **Cisco Scanner (YARA) Engine:**
   - Tool poisoning patterns
   - Security violations
   - Suspicious code execution
   - Command injection patterns (secondary coverage)

**Acceptance Criteria:**
- [x] Run both engines in parallel with timeouts
- [x] Normalize findings to common schema
- [x] Deduplicate findings from both engines
- [x] Aggregate severity (max severity wins)
- [x] Handle engine failures gracefully (continue with available engines)

---

#### FR-1.3: Baseline Management
**Priority:** P0 (Must Have)  
**Description:** Manage approved MCP configuration baselines

**User Stories:**
1. As a security engineer, I can create a baseline from current configs
2. As a DevOps engineer, I can detect when configs deviate from baseline
3. As a compliance officer, I can audit baseline changes over time

**Acceptance Criteria:**
- [x] Create baseline via `inspect` mode
- [x] Store baseline as JSON (version-controllable)
- [x] Detect tool/prompt/resource additions, modifications, deletions
- [x] Calculate hash-based fingerprints for integrity
- [x] Report baseline drift with specific changes
- [x] Allow baseline updates with approval workflow

**Baseline Schema:**
```json
{
  "version": "1.0",
  "created_at": "2025-01-20T10:00:00Z",
  "servers": [
    {
      "server_id": "claude-desktop",
      "config_path": "~/Library/Application Support/Claude/...",
      "tools": [
        {"name": "tool1", "hash": "abc123...", "approved_by": "user@org"}
      ],
      "prompts": [...],
      "resources": [...]
    }
  ]
}
```

---

#### FR-1.4: Policy Engine
**Priority:** P0 (Must Have)  
**Description:** Enforce security policies with configurable thresholds

**Policy Configuration:**
```yaml
policy:
  severity_threshold: HIGH  # CRITICAL | HIGH | MEDIUM | LOW
  block_issue_types:
    - prompt_injection
    - tool_poisoning
    - command_injection
    - hardcoded_secrets
    - baseline_drift
    - excessive_permissions
  require_baseline: true
  allowlist:
    tools: ["approved_tool_1"]
    servers: ["trusted_server"]
```

**Acceptance Criteria:**
- [x] Load policy from YAML config
- [x] Filter findings by severity threshold
- [x] Filter findings by issue type
- [x] Apply allowlist (bypass policy for approved items)
- [x] Return binary pass/fail decision
- [x] Include policy violations in report

---

### FR-2: Command-Line Interface (CLI)

#### FR-2.1: CLI Commands
**Priority:** P0 (Must Have)

**Commands:**

```bash
# Scan mode (default)
sentrascan-mcp scan [OPTIONS]

# Inspect mode (create baseline)
sentrascan-mcp inspect [OPTIONS]

# Server mode (start REST API)
sentrascan-mcp server [OPTIONS]

# Version/help
sentrascan-mcp version
sentrascan-mcp help
```

**Scan Options:**
| Option | Description | Default |
|--------|-------------|---------|
| `--config PATH` | Custom MCP config file(s) | Auto-discover |
| `--baseline PATH` | Baseline file for drift detection | `baseline.json` |
| `--policy PATH` | Policy configuration file | `.sentrascan-mcp.yaml` |
| `--output PATH` | Output report path | `./reports/` |
| `--format FORMAT` | Report format (json\|md\|sarif) | `json,md` |
| `--verbose` | Verbose logging | `false` |
| `--timeout SECONDS` | Per-server timeout | `60` |

**Acceptance Criteria:**
- [x] Exit code 0 for pass, non-zero for fail
- [x] Colorized terminal output (success=green, fail=red)
- [x] Progress indicators during scan
- [x] Clear error messages with remediation hints
- [x] Support `--help` for all commands
- [x] Support `--version` flag

---

#### FR-2.2: Output Formats
**Priority:** P0 (Must Have)

**JSON Report:**
```json
{
  "scan_id": "uuid",
  "timestamp": "2025-01-20T10:00:00Z",
  "gate_result": {
    "passed": false,
    "total_findings": 15,
    "blocking_findings": 3,
    "critical_count": 1,
    "high_count": 2
  },
  "findings": [
    {
      "id": "finding-001",
      "source_engine": "mcp-checkpoint",
      "entity_type": "tool",
      "entity_name": "execute_command",
      "server": "claude-desktop",
      "issue_type": "command_injection",
      "severity": "HIGH",
      "description": "Tool contains shell command patterns",
      "evidence": {...},
      "remediation": "Review tool implementation..."
    }
  ],
  "metadata": {
    "scan_duration_ms": 2340,
    "servers_scanned": 3,
    "engines_used": ["mcp-checkpoint", "cisco-yara"]
  }
}
```

**Markdown Report:**
- Executive summary (pass/fail, counts)
- Summary by issue type
- Blocking issues detail (with remediation)
- Server coverage summary

**SARIF (Optional):**
- For integration with GitHub Code Scanning
- Standard format for security findings

---

### FR-3: REST API

#### FR-3.1: API Endpoints
**Priority:** P1 (Should Have)

**Core Endpoints:**

```
POST   /api/v1/scans              # Trigger new scan
GET    /api/v1/scans               # List scans (paginated)
GET    /api/v1/scans/{id}          # Get scan details
GET    /api/v1/scans/{id}/report   # Download report (JSON/MD)
DELETE /api/v1/scans/{id}          # Delete scan

POST   /api/v1/baselines           # Create baseline
GET    /api/v1/baselines           # List baselines
GET    /api/v1/baselines/{id}      # Get baseline details
PUT    /api/v1/baselines/{id}      # Update baseline

GET    /api/v1/policies            # Get current policy
PUT    /api/v1/policies            # Update policy

GET    /api/v1/stats               # Overall statistics
GET    /api/v1/health              # Health check
GET    /api/v1/version             # Version info
```

**Acceptance Criteria:**
- [x] OpenAPI 3.0 spec available at `/api/v1/docs`
- [x] All endpoints return JSON
- [x] Standard HTTP status codes (200, 201, 400, 404, 500)
- [x] Request validation with detailed error messages
- [x] Response includes request_id for tracing
- [x] CORS support for web UI

---

#### FR-3.2: API Authentication
**Priority:** P1 (Should Have)

**Auth Methods:**
1. API Key (header: `X-API-Key`)
2. Basic Auth (for internal use)
3. No auth (for localhost/dev mode)

**Acceptance Criteria:**
- [x] Generate API keys via CLI (`sentrascan-mcp auth create`)
- [x] Rotate API keys
- [x] Revoke API keys
- [x] API key tied to user identity
- [x] Rate limiting (100 requests/minute per key)

---

### FR-4: Web UI Dashboard

#### FR-4.1: Dashboard Views
**Priority:** P1 (Should Have)

**Pages:**

1. **Home Dashboard**
   - Recent scans summary (last 10)
   - Overall statistics (total scans, findings trend)
   - Quick scan trigger button

2. **Scans List**
   - Paginated table of all scans
   - Filters: date range, status (pass/fail), server
   - Sort by: timestamp, severity, server count

3. **Scan Detail**
   - Scan metadata (ID, timestamp, duration, status)
   - Findings table with filtering
   - Severity breakdown chart (pie/bar)
   - Export report buttons (JSON, MD)

4. **Baselines Management**
   - List of baselines
   - Create/update baseline workflow
   - Baseline diff viewer

5. **Policy Configuration**
   - YAML editor for policy
   - Live validation
   - Policy test against historical scan

6. **Settings**
   - API key management
   - User preferences
   - System health

**Acceptance Criteria:**
- [x] Responsive design (mobile-friendly)
- [x] Clean, modern UI (Material Design or similar)
- [x] Color-coded severity (red=critical, orange=high, etc.)
- [x] Search and filter on all list views
- [x] Export functionality on all data tables
- [x] Dark mode support (optional)

---

#### FR-4.2: Real-Time Updates
**Priority:** P2 (Nice to Have)

**Features:**
- Live scan progress (WebSocket or SSE)
- Auto-refresh dashboard stats every 30s
- Notifications for completed scans

---

### FR-5: Database & Persistence

#### FR-5.1: Database Schema
**Priority:** P0 (Must Have)

**Tables:**

```sql
-- Scans table
CREATE TABLE scans (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    status VARCHAR(20) NOT NULL, -- pending, running, completed, failed
    gate_passed BOOLEAN,
    duration_ms INTEGER,
    servers_scanned INTEGER,
    total_findings INTEGER,
    blocking_findings INTEGER,
    metadata JSONB,
    created_by VARCHAR(255)
);

-- Findings table
CREATE TABLE findings (
    id UUID PRIMARY KEY,
    scan_id UUID REFERENCES scans(id) ON DELETE CASCADE,
    source_engine VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_name VARCHAR(255) NOT NULL,
    server VARCHAR(255) NOT NULL,
    issue_type VARCHAR(100) NOT NULL,
    severity VARCHAR(20) NOT NULL,
    description TEXT,
    evidence JSONB,
    remediation TEXT
);

-- Baselines table
CREATE TABLE baselines (
    id UUID PRIMARY KEY,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    content JSONB NOT NULL, -- baseline JSON
    approved_by VARCHAR(255),
    is_active BOOLEAN DEFAULT true
);

-- API Keys table
CREATE TABLE api_keys (
    id UUID PRIMARY KEY,
    key_hash VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    created_at TIMESTAMP NOT NULL,
    expires_at TIMESTAMP,
    last_used_at TIMESTAMP,
    created_by VARCHAR(255),
    is_revoked BOOLEAN DEFAULT false
);

-- Audit log table
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
- [x] PostgreSQL support for enterprise deployments
- [x] Database migrations managed via Alembic or similar
- [x] Indexes on frequently queried columns
- [x] Foreign key constraints enforced
- [x] Automatic cleanup of old scans (configurable retention period)

---

#### FR-5.2: Data Retention
**Priority:** P1 (Should Have)

**Retention Policy:**
- Scans: 90 days (configurable)
- Baselines: Indefinite
- Audit logs: 365 days (configurable)

**Acceptance Criteria:**
- [x] Configurable retention periods
- [x] Automated cleanup job (daily cron)
- [x] Manual export before cleanup
- [x] Archival to S3/blob storage (optional)

---

## Technical Requirements

### TR-1: Technology Stack

**Backend:**
- **Language:** Python 3.11+
- **Web Framework:** FastAPI 0.110+
- **Database:** SQLite (default) / PostgreSQL 15+ (optional)
- **ORM:** SQLAlchemy 2.0+
- **Task Queue:** None (synchronous for MVP)
- **Testing:** pytest, pytest-asyncio

**Scanning Engines:**
- **mcp-checkpoint:** 2.0.0 (pinned)
- **cisco-ai-mcp-scanner:** 3.2.1 (pinned)

**Frontend:**
- **Framework:** React 18+ or Vue 3+
- **UI Library:** Material-UI or Ant Design
- **State Management:** React Query or Pinia
- **Build Tool:** Vite

**DevOps:**
- **Containerization:** Docker 24+
- **Orchestration:** Docker Compose (MVP), Kubernetes (future)
- **CI/CD:** GitHub Actions / GitLab CI

---

### TR-2: Performance Requirements

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Scan Latency (P95)** | <60s | 10 servers, typical config |
| **API Response (P95)** | <500ms | Read endpoints |
| **Database Query (P95)** | <100ms | Single-table queries |
| **Memory Usage** | <1GB | Per container instance |
| **Startup Time** | <5s | Container cold start |

---

### TR-3: Scalability Requirements

**MVP (Single Instance):**
- Concurrent scans: 5
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
│  │  -mcp       │  │  (Nginx)     │        │
│  │  API        │  │              │        │
│  │             │◄─┤  React App   │        │
│  │  FastAPI    │  │              │        │
│  └──────┬──────┘  └──────────────┘        │
│         │                                   │
│         ▼                                   │
│  ┌─────────────┐  ┌──────────────┐        │
│  │  SQLite /   │  │  Scan        │        │
│  │  PostgreSQL │  │  Worker      │        │
│  │  Database   │  │              │        │
│  └─────────────┘  │  mcp-        │        │
│                   │  checkpoint  │        │
│                   │  +           │        │
│                   │  Cisco       │        │
│                   │  Scanner     │        │
│                   └──────────────┘        │
│                                             │
│  Volumes:                                   │
│    - ./data:/data (database)               │
│    - ./reports:/reports (scan outputs)     │
│    - ./baselines:/baselines (configs)      │
└─────────────────────────────────────────────┘
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  api:
    image: sentrascan-mcp:latest
    command: server --host 0.0.0.0 --port 8000
    ports:
      - "8000:8000"
    volumes:
      - ./data:/data
      - ./reports:/reports
      - ./baselines:/baselines
    environment:
      - DATABASE_URL=sqlite:////data/sentrascan-mcp.db
      - LOG_LEVEL=info
    depends_on:
      - db

  web:
    image: sentrascan-mcp-web:latest
    ports:
      - "3000:80"
    depends_on:
      - api

  db:
    image: postgres:15-alpine
    volumes:
      - pg-data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=sentrascan_mc      - POSTGRES_USER=sentrascan
      - POSTGRES_PASSWORD=changeme

volumes:
  pg-data:
```

---

### TR-5: Security Requirements

#### TR-5.1: Secrets Management
- ❌ No hardcoded secrets in code/images
- ✅ Environment variables for sensitive config
- ✅ Secrets rotation support
- ✅ API key hashing (bcrypt or similar)

#### TR-5.2: Network Security
- ✅ HTTPS/TLS for API (optional, reverse proxy)
- ✅ CORS whitelist for web UI
- ✅ Rate limiting per API key
- ✅ Input validation on all endpoints

#### TR-5.3: Data Security
- ✅ No sensitive data in logs
- ✅ Database encryption at rest (optional)
- ✅ Audit log for all sensitive operations
- ✅ RBAC for multi-user deployments (future)

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

### UI-2: Page Wireframes

**Home Dashboard:**
```
┌─────────────────────────────────────────────┐
│  SentraScan-MCP           [Scan] [Settings] │
├─────────────────────────────────────────────┤
│  Recent Scans                               │
│  ┌─────────────────────────────────────┐   │
│  │ Scan #123  | FAILED | 2m ago | ❌  │   │
│  │ 3 blocking findings                 │   │
│  ├─────────────────────────────────────┤   │
│  │ Scan #122  | PASSED | 1h ago | ✅  │   │
│  │ 0 blocking findings                 │   │
│  └─────────────────────────────────────┘   │
│                                             │
│  Statistics (Last 30 Days)                  │
│  ┌──────────┬──────────┬──────────┐        │
│  │ 127      │ 95.3%    │ 42       │        │
│  │ Scans    │ Pass Rate│ Findings │        │
│  └──────────┴──────────┴──────────┘        │
└─────────────────────────────────────────────┘
```

**Scan Detail:**
```
┌─────────────────────────────────────────────┐
│  ← Back to Scans                            │
├─────────────────────────────────────────────┤
│  Scan #123 - FAILED ❌                      │
│  2025-01-20 10:30:45 • Duration: 42s        │
│  Servers: 3 • Findings: 15 (3 blocking)    │
│                                             │
│  [Export JSON] [Export MD]                  │
├─────────────────────────────────────────────┤
│  Findings (15)                              │
│  [Filter: All ▼] [Search...]               │
│  ┌─────────────────────────────────────┐   │
│  │ ❌ HIGH | command_injection          │   │
│  │ Tool: exec_command (server-1)       │   │
│  │ Shell command patterns detected     │   │
│  │ [View Details]                      │   │
│  ├─────────────────────────────────────┤   │
│  │ ⚠️  MEDIUM | hardcoded_secret       │   │
│  │ ...                                 │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
```

---

## Security & Compliance

### SEC-1: Threat Model

**Assets:**
- MCP server configurations
- Baseline files
- Scan results (findings)
- API keys
- Audit logs

**Threats:**
1. Unauthorized access to scan results
2. Tampering with baselines
3. API key leakage
4. Denial of service (excessive scans)
5. Data exfiltration

**Mitigations:**
1. API key authentication + rate limiting
2. Baseline version control + approval workflow
3. Secrets management best practices
4. Resource limits + timeouts
5. Local-only deployment (no external network)

---

### SEC-2: Compliance

**Requirements:**
- **SOC 2:** Audit logging, access controls
- **ISO 27001:** Security controls documentation
- **GDPR:** No PII in logs/database (or anonymization)

**Audit Trail:**
- All scans logged with timestamp, user, result
- Baseline changes logged with approver
- Policy changes logged with diff
- API key usage logged

---

## Deployment Architecture

### DEPLOY-1: Deployment Modes

#### Mode 1: Standalone (Docker Compose)
**Use Case:** Small teams, single organization  
**Components:** All-in-one container (API + UI + DB)  
**Scaling:** Vertical (single instance)

#### Mode 2: Distributed (Kubernetes - Future)
**Use Case:** Large enterprises, multi-tenant  
**Components:** Separate pods (API, worker, DB, UI)  
**Scaling:** Horizontal (multiple replicas)

---

### DEPLOY-2: Installation Steps

```bash
# 1. Download release
curl -L https://releases.example.com/sentrascan-mcp-latest.tar.gz | tar xz
cd sentrascan-mcp

# 2. Configure
cp .env.example .env
vi .env  # Edit database, API keys, etc.

# 3. Start services
docker-compose up -d

# 4. Initialize database
docker-compose exec api sentrascan-mcp db migrate

# 5. Create first API key
docker-compose exec api sentrascan-mcp auth create --name "admin"

# 6. Access UI
open http://localhost:3000
```

**Requirements:**
- Docker 24+
- Docker Compose 2.0+
- 2GB RAM minimum
- 10GB disk space

---

## Integration Points

### INT-1: CI/CD Integration

**GitHub Actions Example:**
```yaml
- name: Run MCP Security Scan
  uses: docker://sentrascan-mcp:latest
  with:
    command: scan --config mcp.json --baseline baseline.json
    fail-on: HIGH
```

**GitLab CI Example:**
```yaml
mcp-scan:
  image: sentrascan-mcp:latest
  script:
    - sentrascan-mcp scan --config mcp.json
  artifacts:
    reports:
      - reports/scan.json
```

---

### INT-2: Webhook Notifications

**Configuration:**
```yaml
webhooks:
  - url: https://slack.com/webhook/abc123
    events: [scan_failed, baseline_drift]
    headers:
      Authorization: Bearer token
```

**Payload:**
```json
{
  "event": "scan_failed",
  "scan_id": "uuid",
  "timestamp": "2025-01-20T10:00:00Z",
  "details": {
    "blocking_findings": 3,
    "critical_count": 1
  }
}
```

---

## Non-Functional Requirements

### NFR-1: Availability
- **Target:** 99.9% uptime (excluding maintenance)
- **Downtime Budget:** ~8 hours/year
- **Health Checks:** HTTP `/health` endpoint
- **Monitoring:** Prometheus metrics export

---

### NFR-2: Maintainability
- **Code Coverage:** ≥80% for core logic
- **Documentation:** All APIs documented (OpenAPI)
- **Logging:** Structured JSON logs (ELK-compatible)
- **Dependency Updates:** Automated Dependabot PRs

---

### NFR-3: Usability
- **Time to First Scan:** <15 minutes (from Docker pull to scan result)
- **Learning Curve:** Developers can use CLI in <5 minutes
- **Error Messages:** Actionable with remediation links
- **Documentation:** Complete user guide + API reference

---

### NFR-4: Portability
- **Platforms:** Linux (x86_64, ARM64), macOS (x86_64, ARM64)
- **Databases:** SQLite (default), PostgreSQL (optional)
- **Container Registries:** Docker Hub, GitHub Container Registry, Private

---

## Roadmap & Milestones

### Phase 1: MVP (Weeks 1-6)

**Week 1-2: Core Scanner**
- ✅ Orchestrator with mcp-checkpoint + Cisco YARA
- ✅ Discovery and normalization
- ✅ Policy engine
- ✅ JSON/MD reporting

**Week 3-4: CLI & Docker**
- ✅ CLI commands (scan, inspect)
- ✅ Docker image with pinned dependencies
- ✅ Basic documentation

**Week 5-6: Database & API**
- ✅ SQLite database schema
- ✅ REST API (scans, baselines, policies)
- ✅ OpenAPI documentation

**Deliverables:**
- Docker image (CLI mode)
- REST API server
- User documentation
- CI/CD template

---

### Phase 2: Enterprise Features (Weeks 7-12)

**Week 7-9: Web UI**
- Dashboard
- Scans list & detail
- Baselines management

**Week 10-11: Authentication & RBAC**
- API key management
- Basic RBAC (admin, viewer roles)
- Audit logging

**Week 12: Observability**
- Prometheus metrics
- Structured logging
- Health checks

**Deliverables:**
- Docker Compose stack (all services)
- Web UI
- Admin guide

---

### Phase 3: Advanced Features (Weeks 13-18)

**Future Enhancements:**
- Kubernetes Helm chart
- Multi-tenancy
- Advanced RBAC (teams, projects)
- Webhook notifications
- Scan scheduling
- PostgreSQL support
- Historical trend charts
- Custom YARA rule management

---

## Dependencies & Risks

### External Dependencies

| Dependency | Version | Risk | Mitigation |
|------------|---------|------|------------|
| mcp-checkpoint | 2.0.0 | Version pinned, active maintenance | Monitor releases, test upgrades |
| cisco-ai-mcp-scanner | 3.2.1 | Version pinned, Cisco-backed | Monitor releases, Cisco support |
| FastAPI | 0.110+ | Widely used, stable API | Pin minor version |
| SQLAlchemy | 2.0+ | Breaking changes in 2.x | Pin minor version, test upgrades |
| React | 18+ | Frequent updates | Use long-term support release |

---

### Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| **Engine API changes** | Medium | High | Pin versions, test before upgrading |
| **False positives** | Medium | Medium | Tune policies, user feedback loop |
| **Performance degradation** | Low | Medium | Load testing, resource monitoring |
| **Security vulnerability** | Low | High | Regular dependency scans, security patches |
| **Adoption resistance** | Medium | High | Clear documentation, easy onboarding |

---

## Appendix

### A. Glossary

- **MCP:** Model Context Protocol - protocol for AI agent tool execution
- **Baseline:** Approved snapshot of MCP configurations
- **Drift:** Deviation from approved baseline
- **Rug Pull:** Malicious modification of previously trusted MCP tools
- **Tool Poisoning:** Injection of malicious code/prompts into MCP tool descriptions
- **Static Analysis:** Code analysis without execution
- **YARA:** Pattern matching engine for security rules

---

### B. References

- [MCP Checkpoint Documentation](https://github.com/aira-security/mcp-checkpoint)
- [Cisco MCP Scanner Documentation](https://github.com/cisco-ai-defense/mcp-scanner)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)
- [OWASP Top 10 for LLMs](https://owasp.org/www-project-top-10-for-large-language-model-applications/)

---

### C. Open Questions

1. **Q:** Should we support SARIF output format for GitHub Code Scanning integration?  
   **A:** P2 (future enhancement, not MVP)

2. **Q:** What is the baseline approval workflow?  
   **A:** Manual review + Git commit for MVP; future: built-in approval UI

3. **Q:** Should we support scanning of remote MCP servers (HTTP/SSE)?  
   **A:** Yes, via custom config paths; auto-discovery focuses on local

4. **Q:** Do we need multi-tenancy (multiple orgs in single deployment)?  
   **A:** Not for MVP; Phase 3 feature

---

## Document Approval

| Role | Name | Signature | Date |
|------|------|-----------|------|
| **Product Owner** | ________________ | ________ | ____ |
| **Engineering Lead** | ________________ | ________ | ____ |
| **Security Lead** | ________________ | ________ | ____ |
| **DevOps Lead** | ________________ | ________ | ____ |

---

**Version History:**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-01-20 | Team | Initial PRD |

---

**Document Status:** 🟡 Draft - Awaiting Approval
