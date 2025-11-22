# SentraScan Platform - Quick Start Guide

Get up and running with SentraScan Platform in 5 minutes.

## Prerequisites

- Docker 24+ and Docker Compose 2.0+ (for Docker deployment)
- OR Python 3.11+ (for local installation)
- 2GB RAM minimum
- 10GB disk space

---

## Option 1: Docker Deployment (Recommended)

### Step 1: Start Services

```bash
# Clone the repository (if you haven't already)
git clone <repository-url>
cd sentrascan-platform

# Start all services
docker-compose up -d
```

This starts:
- API server on port 8200
- PostgreSQL database
- Web UI (accessible via API server)

### Step 2: Initialize Database

```bash
docker-compose exec api sentrascan db init
```

Expected output:
```
Database initialized
```

### Step 3: Create API Key

```bash
docker-compose exec api sentrascan auth create --name admin --role admin
```

**Important:** Save the API key shown - you won't be able to retrieve it later!

Example output:
```
API key created. Save it now; you won't be able to retrieve it later:
abc123xyz789...
```

### Step 4: Access the Platform

- **Web UI:** http://localhost:8200
- **API:** http://localhost:8200/api/v1
- **API Docs:** http://localhost:8200/docs

---

## Option 2: Local Installation

### Step 1: Install Dependencies

```bash
# Create virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install SentraScan
pip install -e .
```

### Step 2: Initialize Database

```bash
sentrascan db init
```

### Step 3: Create API Key

```bash
sentrascan auth create --name admin --role admin
```

Save the API key!

### Step 4: Start Server

```bash
sentrascan server --host 0.0.0.0 --port 8200
```

---

## Your First Scan

### Scan MCP Configurations

**Using CLI:**
```bash
# Auto-discover MCP configs
sentrascan scan mcp --auto-discover

# Or specify config file
sentrascan scan mcp --config ~/.cursor/mcp.json
```

**Using API:**
```bash
curl -X POST http://localhost:8200/api/v1/mcp/scans \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "auto_discover": true
  }'
```

**Using Web UI:**
1. Navigate to http://localhost:8200
2. Log in with your API key
3. Click "New Scan" → "MCP Scan"
4. Enable "Auto-discover" and click "Scan"

### Scan ML Model

**Using CLI:**
```bash
sentrascan scan model model.pkl --sbom model.sbom.json
```

**Using API:**
```bash
curl -X POST http://localhost:8200/api/v1/models/scans \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json" \
  -d '{
    "paths": ["model.pkl"],
    "generate_sbom": true
  }'
```

---

## Understanding Results

### Scan Status

- ✅ **PASSED** - No blocking findings detected
- ❌ **FAILED** - Blocking findings detected (policy violation)

### Finding Severity Levels

- 🔴 **CRITICAL** - Immediate security risk
- 🟠 **HIGH** - Significant security risk
- 🟡 **MEDIUM** - Moderate security risk
- 🔵 **LOW** - Minor security risk
- ℹ️ **INFO** - Informational finding

### Example Output

```json
{
  "scan_id": "550e8400-e29b-41d4-a716-446655440000",
  "gate_result": {
    "passed": false,
    "total_findings": 3,
    "blocking_findings": 2,
    "high_count": 2,
    "medium_count": 1
  },
  "findings": [
    {
      "severity": "HIGH",
      "category": "command_injection",
      "title": "Command injection detected",
      "description": "Tool contains shell command patterns",
      "remediation": "Review tool implementation..."
    }
  ]
}
```

---

## Next Steps

1. **Read User Guide** - Learn complete workflows in the [User Guide](USER-GUIDE.md)
2. **Configure Policies** - Customize security policies (see [User Guide - Configuring Policies](USER-GUIDE.md#configuring-policies))
3. **Create Baselines** - Set up baseline snapshots (see [User Guide - Managing Baselines](USER-GUIDE.md#managing-baselines))
4. **Integrate CI/CD** - Add scans to your pipeline (see [CI/CD Integration Guide](INTEGRATION-CICD.md))
5. **Explore API** - Check [API Client Examples](API-CLIENT-EXAMPLES.md) for integration code

**For Administrators:**
- [Administrator Guide](ADMIN-GUIDE.md) - Production deployment
- [Security Best Practices](SECURITY.md) - Security hardening
- [Runbooks](RUNBOOKS.md) - Operational procedures

---

## Troubleshooting

**Quick Fixes:**
```bash
# Service not starting
docker-compose ps && docker-compose restart

# Database connection
docker-compose exec db psql -U sentrascan -d sentrascan -c "SELECT 1;"

# Scanner issues
docker-compose exec api sentrascan doctor
```

For comprehensive troubleshooting, see **[Runbooks](RUNBOOKS.md#incident-response)**.

---

## Getting Help

- 📖 [Documentation Index](README.md) - Complete documentation overview
- 📘 [User Guide](USER-GUIDE.md) - Complete user manual
- 🔧 [Technical Documentation](TECHNICAL-DOCUMENTATION.md) - Technical reference
- 🐛 [Report Issues](https://github.com/your-repo/issues)
- 💬 [Community Discussions](https://github.com/your-repo/discussions)

---

**Ready to go?** Start scanning and secure your MCP configurations and ML models! 🚀

