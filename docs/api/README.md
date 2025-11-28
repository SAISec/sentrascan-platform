# API Documentation

Complete reference for the SentraScan Platform REST API.

## Table of Contents

1. [Authentication](#authentication)
2. [Base URL](#base-url)
3. [Endpoints](#endpoints)
4. [Request/Response Formats](#requestresponse-formats)
5. [Error Handling](#error-handling)
6. [Rate Limiting](#rate-limiting)

## Authentication

All API requests require authentication using API keys.

### API Key Format

API keys follow this format:
```
ss-proj-h_<147-character-alphanumeric-string-with-one-hyphen>
```

Example:
```
ss-proj-h_AbC123XyZ789-MnP456QrS012DeF345GhI678JkL901NoP234RsT567UvW890XyZ123AbC456DeF789GhI012JkL345MnP678QrS901RsT234UvW567XyZ890AbC123DeF456GhI789JkL012MnP345QrS678RsT901UvW234XyZ567AbC890
```

### Using API Keys

Include the API key in the `X-API-Key` header:

```bash
curl -H "X-API-Key: ss-proj-h_your-key-here" \
  http://localhost:8000/api/v1/scans
```

### Session Authentication (Web UI)

For web UI requests, use session cookies instead of API keys.

## Base URL

```
http://localhost:8000/api/v1
```

For production, replace `localhost:8000` with your server URL.

## Endpoints

### Health Check

**GET** `/health`

Check API health status.

**Response**:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### Scans

#### List Scans

**GET** `/scans`

List all scans for the current tenant.

**Query Parameters**:
- `type` (optional): Filter by scan type (`mcp` or `model`)
- `limit` (optional): Maximum number of results (default: 100)
- `offset` (optional): Pagination offset (default: 0)

**Response**:
```json
[
  {
    "id": "scan-id",
    "created_at": "2025-01-01T00:00:00Z",
    "scan_type": "mcp",
    "target_path": "/path/to/config",
    "passed": true,
    "total_findings": 5,
    "critical_count": 0,
    "high_count": 2,
    "medium_count": 3,
    "low_count": 0
  }
]
```

#### Get Scan Details

**GET** `/scans/{scan_id}`

Get detailed information about a specific scan.

**Response**:
```json
{
  "scan": {
    "id": "scan-id",
    "created_at": "2025-01-01T00:00:00Z",
    "type": "mcp",
    "target": "/path/to/config",
    "passed": true,
    "critical": 0,
    "high": 2,
    "medium": 3,
    "low": 0
  },
  "findings": [
    {
      "id": "finding-id",
      "severity": "high",
      "category": "hardcoded_secret",
      "title": "Hardcoded API Key Detected",
      "description": "An API key was found in the configuration...",
      "location": "config.json:42",
      "remediation": "Move API key to environment variable..."
    }
  ]
}
```

#### Create MCP Scan

**POST** `/mcp/scans`

Run a security scan on MCP configuration files.

**Request Body**:
```json
{
  "config_paths": ["/path/to/mcp.json"],
  "auto_discover": true,
  "policy": "/path/to/policy.yaml",
  "timeout": 60
}
```

**Response**:
```json
{
  "gate_result": {
    "passed": true,
    "total_findings": 5,
    "critical_count": 0,
    "high_count": 2,
    "medium_count": 3,
    "low_count": 0
  },
  "findings": [...],
  "scan_id": "scan-id"
}
```

#### Create Model Scan

**POST** `/models/scans`

Run a security scan on ML model files.

**Request Body**:
```json
{
  "paths": ["./models/model.pkl"],
  "model_path": "./models/model.pkl",
  "generate_sbom": true,
  "strict": false,
  "policy": "/path/to/policy.yaml",
  "timeout": 0
}
```

**Response**:
```json
{
  "gate_result": {
    "passed": true,
    "total_findings": 3,
    "critical_count": 1,
    "high_count": 1,
    "medium_count": 1,
    "low_count": 0
  },
  "findings": [...],
  "sbom": {...},
  "scan_id": "scan-id"
}
```

### Findings

#### List Findings

**GET** `/findings`

List all findings across scans.

**Query Parameters**:
- `severity` (optional): Filter by severity
- `category` (optional): Filter by category
- `scanner` (optional): Filter by scanner
- `scan_id` (optional): Filter by scan ID
- `limit` (optional): Maximum results (default: 100)
- `offset` (optional): Pagination offset
- `sort` (optional): Sort field (default: `created_at`)
- `order` (optional): Sort order (`asc` or `desc`, default: `desc`)

**Response**:
```json
{
  "findings": [...],
  "total": 150,
  "limit": 100,
  "offset": 0,
  "has_more": true
}
```

#### Export Findings

**GET** `/scans/{scan_id}/findings/export`

Export findings for a scan.

**Query Parameters**:
- `format`: Export format (`csv` or `json`)

**Response**: CSV or JSON file download

### Analytics

#### Trend Analysis

**GET** `/analytics/trends`

Get trend analysis over time.

**Query Parameters**:
- `days` (optional): Number of days to analyze (default: 30)
- `group_by` (optional): Grouping interval (`day`, `week`, `month`, default: `day`)

**Response**:
```json
{
  "period": {
    "start": "2025-01-01T00:00:00Z",
    "end": "2025-01-31T23:59:59Z"
  },
  "group_by": "day",
  "data": [
    {
      "period": "2025-01-01",
      "total_findings": 10,
      "critical_count": 1,
      "high_count": 3,
      "medium_count": 5,
      "low_count": 1,
      "scan_count": 5,
      "passed_count": 3
    }
  ],
  "summary": {
    "total_scans": 30,
    "total_findings": 150,
    "avg_findings_per_scan": 5.0,
    "pass_rate": 0.7
  }
}
```

#### Severity Distribution

**GET** `/analytics/severity-distribution`

Get severity distribution statistics.

**Query Parameters**:
- `days` (optional): Number of days (default: 30)

**Response**:
```json
{
  "period": {...},
  "distribution": {
    "critical": 5,
    "high": 20,
    "medium": 50,
    "low": 25,
    "info": 10
  },
  "total": 110,
  "percentages": {
    "critical": 4.5,
    "high": 18.2,
    "medium": 45.5,
    "low": 22.7,
    "info": 9.1
  }
}
```

#### Scanner Effectiveness

**GET** `/analytics/scanner-effectiveness`

Get scanner performance metrics.

**Query Parameters**:
- `days` (optional): Number of days (default: 30)

**Response**:
```json
{
  "period": {...},
  "scanners": {
    "mcp": {
      "scan_count": 20,
      "total_findings": 80,
      "critical_count": 5,
      "high_count": 15,
      "medium_count": 40,
      "low_count": 20,
      "avg_duration_ms": 45000,
      "pass_rate": 75.0,
      "avg_findings_per_scan": 4.0
    },
    "model": {
      "scan_count": 10,
      "total_findings": 30,
      "critical_count": 2,
      "high_count": 8,
      "medium_count": 15,
      "low_count": 5,
      "avg_duration_ms": 120000,
      "pass_rate": 80.0,
      "avg_findings_per_scan": 3.0
    }
  }
}
```

#### Remediation Progress

**GET** `/analytics/remediation-progress`

Track remediation progress.

**Query Parameters**:
- `days` (optional): Number of days (default: 90)

**Response**:
```json
{
  "period": {...},
  "total_findings": 200,
  "by_severity": {
    "critical": 10,
    "high": 40,
    "medium": 100,
    "low": 50
  },
  "by_age": {
    "new": 20,
    "recent": 80,
    "old": 100
  },
  "remediation_rate": 0.3
}
```

#### Risk Scores

**GET** `/analytics/risk-scores`

Get risk scoring and prioritization.

**Query Parameters**:
- `days` (optional): Number of days (default: 30)

**Response**:
```json
{
  "period": {...},
  "total_risk_score": 1250.5,
  "by_severity": {
    "critical": 500.0,
    "high": 400.0,
    "medium": 250.0,
    "low": 100.5
  },
  "top_risks": [
    {
      "category": "hardcoded_secret",
      "risk_score": 150.0
    },
    {
      "category": "command_injection",
      "risk_score": 120.0
    }
  ]
}
```

#### Export Analytics

**GET** `/analytics/export`

Export analytics data.

**Query Parameters**:
- `format`: Export format (`csv`, `json`, or `pdf`)
- `days` (optional): Number of days (default: 30)
- `include_trends` (optional): Include trend data (default: true)
- `include_severity` (optional): Include severity data (default: true)
- `include_scanner` (optional): Include scanner data (default: true)
- `include_remediation` (optional): Include remediation data (default: true)
- `include_risk` (optional): Include risk data (default: true)

**Response**: File download (CSV, JSON, or PDF)

### ML Insights

#### Get ML Insights Status

**GET** `/ml-insights/status`

Check if ML insights are enabled.

**Response**:
```json
{
  "enabled": true,
  "message": "ML insights are enabled"
}
```

#### Get All ML Insights

**GET** `/ml-insights`

Get all ML insights (anomaly detection, correlations, remediation prioritization).

**Query Parameters**:
- `days` (optional): Number of days (default: 30)

**Response**:
```json
{
  "enabled": true,
  "period": {...},
  "anomaly_detection": {...},
  "correlations": {...},
  "remediation_prioritization": {...}
}
```

#### Get Anomalies

**GET** `/ml-insights/anomalies`

Get anomaly detection results.

**Query Parameters**:
- `days` (optional): Number of days (default: 30)

**Response**:
```json
{
  "enabled": true,
  "anomalies": [
    {
      "scan_id": "scan-id",
      "created_at": "2025-01-01T00:00:00Z",
      "scan_type": "mcp",
      "anomaly_score": -0.5,
      "total_findings": 50,
      "critical_count": 10,
      "high_count": 20,
      "reason": "unusually high total findings; unusually high critical findings"
    }
  ],
  "total_scans": 100,
  "anomaly_count": 5,
  "anomaly_rate": 0.05
}
```

#### Get Correlations

**GET** `/ml-insights/correlations`

Get finding correlation analysis.

**Query Parameters**:
- `days` (optional): Number of days (default: 30)

**Response**:
```json
{
  "enabled": true,
  "correlations": {
    "severity_category": {
      "correlation": 0.75,
      "p_value": 0.001,
      "significant": true
    },
    "severity_scanner": {
      "correlation": 0.45,
      "p_value": 0.05,
      "significant": true
    }
  },
  "total_findings": 500
}
```

#### Get Remediation Recommendations

**GET** `/ml-insights/remediations`

Get prioritized remediation recommendations.

**Query Parameters**:
- `days` (optional): Number of days (default: 90)

**Response**:
```json
{
  "enabled": true,
  "recommendations": [
    {
      "category": "hardcoded_secret",
      "severity": "critical",
      "frequency": 15,
      "first_seen": "2025-01-01T00:00:00Z",
      "age_days": 30,
      "priority_score": 450.0,
      "recommendation": "Address 15 critical-severity finding(s) in category 'hardcoded_secret'"
    }
  ],
  "total_recommendations": 20
}
```

### Tenant Settings

#### Get All Settings

**GET** `/tenant-settings`

Get all tenant settings.

**Response**:
```json
{
  "policy": {...},
  "scanner": {...},
  "severity": {...},
  "notification": {...},
  "scan": {...},
  "integration": {...}
}
```

#### Get Specific Setting

**GET** `/tenant-settings/{setting_key}`

Get a specific setting category.

**Response**:
```json
{
  "key": "policy",
  "value": {
    "gate_thresholds": {
      "critical_max": 0,
      "high_max": 10,
      "medium_max": 50,
      "low_max": 100
    },
    "pass_criteria": {
      "require_all_scanners_pass": true,
      "allow_warnings": false
    }
  }
}
```

#### Update Setting

**PUT** `/tenant-settings/{setting_key}`

Update a specific setting.

**Request Body**:
```json
{
  "gate_thresholds": {
    "critical_max": 0,
    "high_max": 5,
    "medium_max": 30,
    "low_max": 100
  }
}
```

**Response**:
```json
{
  "key": "policy",
  "value": {...},
  "updated": true
}
```

#### Update Multiple Settings

**PUT** `/tenant-settings`

Update multiple settings at once.

**Request Body**:
```json
{
  "policy": {...},
  "scanner": {...}
}
```

**Response**:
```json
{
  "settings": {...},
  "updated": true
}
```

#### Reset to Defaults

**POST** `/tenant-settings/reset`

Reset all settings to default values.

**Response**:
```json
{
  "reset": true
}
```

### API Keys

#### List API Keys

**GET** `/api-keys`

List all API keys for the current user/tenant.

**Response**:
```json
[
  {
    "id": "key-id",
    "name": "My API Key",
    "created_at": "2025-01-01T00:00:00Z",
    "expires_at": null,
    "is_revoked": false
  }
]
```

#### Create API Key

**POST** `/api-keys`

Create a new API key.

**Request Body** (form data):
```
name=My API Key
```

**Response**:
```json
{
  "id": "key-id",
  "name": "My API Key",
  "key": "ss-proj-h_<full-key>",
  "created_at": "2025-01-01T00:00:00Z"
}
```

**Note**: The full key is only shown once. Store it securely.

#### Revoke API Key

**DELETE** `/api-keys/{key_id}`

Revoke an API key.

**Response**:
```json
{
  "revoked": true,
  "key_id": "key-id"
}
```

## Request/Response Formats

### Content Types

- **Request**: `application/json` for JSON, `application/x-www-form-urlencoded` for form data
- **Response**: `application/json` for JSON, `text/csv` for CSV exports, `application/pdf` for PDF exports

### Date Formats

All dates are in ISO 8601 format:
```
2025-01-01T00:00:00Z
```

### Pagination

List endpoints support pagination using `limit` and `offset`:

```
GET /api/v1/scans?limit=50&offset=100
```

## Error Handling

### Error Response Format

```json
{
  "detail": "Error message describing what went wrong"
}
```

### HTTP Status Codes

- `200 OK`: Request successful
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `422 Unprocessable Entity`: Validation error
- `500 Internal Server Error`: Server error
- `503 Service Unavailable`: Service temporarily unavailable (e.g., ML insights disabled)

### Common Errors

**401 Unauthorized**:
```json
{
  "detail": "Invalid API key"
}
```

**403 Forbidden**:
```json
{
  "detail": "Permission denied: scan.create required"
}
```

**404 Not Found**:
```json
{
  "detail": "Scan not found"
}
```

## Rate Limiting

API requests are rate-limited to prevent abuse:

- **Per API Key**: 100 requests per minute
- **Per IP Address**: 200 requests per minute
- **Per Tenant**: 500 requests per minute

Rate limit headers are included in responses:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

When rate limit is exceeded, a `429 Too Many Requests` response is returned.

## Examples

### Complete Workflow

```bash
# 1. Create API key (via web UI or API)
API_KEY="ss-proj-h_your-key-here"

# 2. Run MCP scan
SCAN_RESPONSE=$(curl -X POST http://localhost:8000/api/v1/mcp/scans \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"auto_discover": true}')

SCAN_ID=$(echo $SCAN_RESPONSE | jq -r '.scan_id')

# 3. Get scan details
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8000/api/v1/scans/$SCAN_ID"

# 4. List findings
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8000/api/v1/findings?severity=critical"

# 5. Export findings
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8000/api/v1/scans/$SCAN_ID/findings/export?format=csv" \
  -o findings.csv

# 6. Get analytics
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8000/api/v1/analytics/trends?days=30"
```

