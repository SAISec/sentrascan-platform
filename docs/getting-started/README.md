# Getting Started with SentraScan Platform

Welcome to SentraScan Platform! This guide will help you get started with security scanning for MCP configurations and ML models.

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Installation](#installation)
4. [First Scan](#first-scan)
5. [Next Steps](#next-steps)

## Overview

SentraScan Platform is a unified security scanning solution that helps you:

- **Scan MCP Configurations**: Detect security issues in Model Context Protocol configurations
- **Scan ML Models**: Identify vulnerabilities in machine learning model files
- **Generate SBOMs**: Create Software Bill of Materials for your models
- **Manage Baselines**: Track and detect unauthorized changes
- **Multi-Tenant Support**: Isolated environments for different organizations

## Quick Start

### Prerequisites

- Python 3.11 or higher
- Docker and Docker Compose (for containerized deployment)
- PostgreSQL database (for production)

### Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd sentrascan-platform
   ```

2. **Install dependencies**:
   ```bash
   pip install -e .
   ```

3. **Set up environment variables**:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/sentrascan"
   export SESSION_SECRET="your-secret-key-here"
   ```

4. **Initialize the database**:
   ```bash
   python -m sentrascan.cli db init
   ```

5. **Start the server**:
   ```bash
   uvicorn sentrascan.server:app --host 0.0.0.0 --port 8000
   ```

### Using Docker

1. **Start services**:
   ```bash
   docker compose up -d
   ```

2. **Access the web interface**:
   Open your browser to `http://localhost:8000`

## First Scan

### Web Interface

1. **Log in** to the platform using your credentials
2. **Navigate** to "Run Scan" in the main menu
3. **Choose scan type**:
   - **MCP Scan**: For scanning MCP configuration files
   - **Model Scan**: For scanning ML model files
4. **Configure scan parameters**:
   - Select target paths or enable auto-discovery
   - Choose policy file (optional)
   - Set timeout and other options
5. **Run scan** and view results

### Command Line Interface

#### MCP Scan

```bash
sentrascan mcp \
  --config-paths ~/.cursor/mcp.json \
  --auto-discover \
  --policy ./policy.yaml
```

#### Model Scan

```bash
sentrascan model \
  --model-path ./models/my_model.pkl \
  --generate-sbom \
  --strict
```

### API

```bash
# Create an API key first (via web interface or API)
export API_KEY="ss-proj-h_your-api-key-here"

# Run MCP scan
curl -X POST http://localhost:8000/api/v1/mcp/scans \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"auto_discover": true}'

# Run Model scan
curl -X POST http://localhost:8000/api/v1/models/scans \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"paths": ["./models/model.pkl"]}'
```

## Next Steps

- Read the [User Guide](../user-guide/README.md) for detailed usage instructions
- Check out [How-To Guides](../how-to/README.md) for common tasks
- Review [Best Practices](../best-practices/README.md) for security recommendations
- Explore the [API Documentation](../api/README.md) for programmatic access

## Getting Help

- **FAQ**: See [Frequently Asked Questions](../faq/README.md)
- **Troubleshooting**: Check [Troubleshooting Guide](../troubleshooting/README.md)
- **Glossary**: Refer to [Terminology Glossary](../glossary/README.md)

