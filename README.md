# SentraScan Platform

Unified AI/ML security scanner for MCP configurations and ML models.

## Overview

SentraScan Platform provides comprehensive security scanning for:
- **MCP (Model Context Protocol) Servers**: Static analysis of MCP configurations
- **ML Models**: Security scanning with automatic CycloneDX SBOM generation

## Features

### SentraScan-MCP Module
- Static analysis of MCP server configurations
- Baseline drift detection (rug pull attack prevention)
- Secrets detection (TruffleHog, Gitleaks)
- Command injection detection
- SAST scanning (Semgrep)
- Runtime probing capabilities
- Auto-discovery of MCP configs (Claude Desktop, Cursor, Windsurf, VS Code)

### SentraScan-Model Module
- Scans 30+ ML model formats (Pickle, PyTorch, TensorFlow, ONNX, GGUF, etc.)
- Deserialization attack detection
- Automatic CycloneDX SBOM generation
- Policy-based pass/fail gates
- Multiple input sources (local, Hugging Face, MLflow, S3, GCS)

## Quick Start

### Installation

```bash
pip install -e .
```

### CLI Usage

```bash
# Scan MCP configurations
sentrascan scan mcp --auto-discover

# Scan ML model
sentrascan scan model model.pkl --sbom model.sbom.json

# Start REST API server
sentrascan server --host 0.0.0.0 --port 8200

# Initialize database
sentrascan db init
```

### Docker

```bash
docker-compose up -d
```

Access the API at `http://localhost:8200` and the web UI at `http://localhost:8200`.

## Documentation

### Getting Started
- [Quick Start Guide](docs/QUICK-START.md) - Get started in 5 minutes
- [User Guide](docs/USER-GUIDE.md) - Complete user guide with workflows

### Technical Reference
- [Technical Documentation](docs/TECHNICAL-DOCUMENTATION.md) - Complete technical reference
- [API Client Examples](docs/API-CLIENT-EXAMPLES.md) - Code examples in multiple languages

### Operations
- [Administrator Guide](docs/ADMIN-GUIDE.md) - Production deployment and administration
- [Runbooks](docs/RUNBOOKS.md) - Operational procedures and incident response
- [Monitoring Guide](docs/MONITORING.md) - Metrics, alerting, and observability
- [Backup & Recovery](docs/BACKUP-RECOVERY.md) - Backup and disaster recovery procedures

### Security & Integration
- [Security Best Practices](docs/SECURITY.md) - Security hardening and compliance
- [CI/CD Integration](docs/INTEGRATION-CICD.md) - Pipeline integration examples

### Analysis & Planning
- [Product Requirements Document](docs/PRODUCT-REQUIREMENTS-DOCUMENT.md)
- [MCP Analysis](docs/mcp-analysis/)
- [Model Analysis](docs/model-analysis/)
- [Documentation Improvement Plan](docs/DOCUMENTATION-IMPROVEMENT-PLAN.md) - Roadmap for enhancements

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.