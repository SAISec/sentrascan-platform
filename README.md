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

- [Product Requirements Document](docs/PRODUCT-REQUIREMENTS-DOCUMENT.md)
- [MCP Analysis](docs/mcp-analysis/)
- [Model Analysis](docs/model-analysis/)

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.