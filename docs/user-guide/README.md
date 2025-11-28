# User Guide

Comprehensive guide to using SentraScan Platform features and capabilities.

## Table of Contents

1. [Authentication](#authentication)
2. [Dashboard](#dashboard)
3. [Running Scans](#running-scans)
4. [Viewing Results](#viewing-results)
5. [Baseline Management](#baseline-management)
6. [Analytics](#analytics)
7. [Tenant Settings](#tenant-settings)
8. [API Keys](#api-keys)
9. [User Management](#user-management)

## Authentication

### Creating an Account

1. Navigate to the login page
2. Click "Register" or "Sign Up"
3. Fill in your details:
   - Email address
   - Name
   - Password (minimum 12 characters, must include uppercase, lowercase, numbers, and special characters)
4. Complete registration

### Logging In

1. Enter your email and password
2. If MFA is enabled, enter the code from your authenticator app
3. Click "Login"

### Multi-Factor Authentication (MFA)

**Setting up MFA**:

1. Go to your user profile
2. Navigate to "Security Settings"
3. Click "Enable MFA"
4. Scan the QR code with your authenticator app (Google Authenticator, Authy, etc.)
5. Enter the verification code to complete setup

**Using MFA**:
- After entering your password, you'll be prompted for the MFA code
- Enter the 6-digit code from your authenticator app

## Dashboard

The dashboard provides an overview of your security scans and findings.

### Key Metrics

- **Total Scans**: Number of scans executed
- **Total Findings**: Total security issues detected
- **Pass Rate**: Percentage of scans that passed policy checks
- **Risk Score**: Overall risk assessment

### Charts

- **Trend Analysis**: Findings over time
- **Severity Distribution**: Breakdown by severity level
- **Scanner Effectiveness**: Performance metrics per scanner type

### Filters

- **Time Range**: Filter by date (7 days, 30 days, 90 days, custom)
- **Scan Type**: Filter by MCP or Model scans
- **Status**: Filter by passed/failed scans

## Running Scans

### MCP Scans

**Purpose**: Scan Model Context Protocol configuration files for security issues.

**Steps**:

1. Navigate to "Run Scan" → "MCP Scan"
2. **Option A - Auto Discovery**:
   - Enable "Auto Discover"
   - Platform will automatically find MCP configs in common locations
3. **Option B - Manual Paths**:
   - Enter configuration file paths (one per line)
   - Common locations:
     - `~/.cursor/mcp.json`
     - `~/Library/Application Support/Claude/`
     - `~/.vscode/mcp.json`
4. **Configure Options**:
   - **Policy**: Select custom policy file (optional)
   - **Timeout**: Maximum scan duration in seconds
5. Click "Run Scan"

**What Gets Scanned**:
- Hardcoded secrets
- Command injection vulnerabilities
- Excessive permissions
- Baseline drift detection
- Tool poisoning patterns

### Model Scans

**Purpose**: Scan ML model files for security vulnerabilities.

**Steps**:

1. Navigate to "Run Scan" → "Model Scan"
2. Enter model file path(s)
3. **Options**:
   - **Generate SBOM**: Create Software Bill of Materials
   - **Strict Mode**: Enable stricter security checks
   - **Policy**: Select custom policy file
   - **Timeout**: Maximum scan duration
4. Click "Run Scan"

**Supported Formats**:
- Pickle (.pkl, .pickle)
- PyTorch (.pt, .pth, .bin)
- TensorFlow (SavedModel, .h5, .pb)
- ONNX (.onnx)
- GGUF (LLM formats)
- SafeTensors
- And 20+ more formats

## Viewing Results

### Scan Details

1. Click on a scan from the dashboard or scan list
2. View:
   - **Scan Information**: Type, target, timestamp, duration
   - **Gate Result**: Pass/fail status, finding counts
   - **Findings List**: All detected security issues
   - **SBOM**: Software Bill of Materials (if generated)

### Findings

Each finding includes:

- **Severity**: Critical, High, Medium, Low, Info
- **Category**: Type of security issue
- **Title**: Brief description
- **Description**: Detailed explanation
- **Location**: Where the issue was found
- **Remediation**: Steps to fix the issue
- **Evidence**: Supporting data or code snippets

### Filtering Findings

- **By Severity**: Filter by criticality level
- **By Category**: Filter by issue type
- **By Scanner**: Filter by detection tool
- **By Scan**: Filter by specific scan

### Exporting Results

- **CSV**: Export findings as CSV file
- **JSON**: Export full scan data as JSON
- **PDF**: Generate PDF report (coming soon)

## Baseline Management

Baselines help you track approved configurations and detect unauthorized changes.

### Creating a Baseline

1. Navigate to "Baselines"
2. Click "Create Baseline"
3. Select a scan that passed all checks
4. Enter baseline name and description
5. Click "Create"

### Comparing Scans to Baseline

1. Select a scan
2. Click "Compare with Baseline"
3. Choose baseline to compare against
4. View differences:
   - **New Findings**: Issues not in baseline
   - **Resolved Findings**: Issues fixed since baseline
   - **Unchanged Findings**: Issues still present

### Baseline Drift Detection

The platform automatically detects when current configurations differ from approved baselines, helping identify potential security regressions.

## Analytics

Access comprehensive analytics and insights about your security posture.

### Analytics Dashboard

Navigate to "Analytics" to view:

- **Trend Analysis**: How findings change over time
- **Severity Distribution**: Breakdown of issue severity
- **Scanner Effectiveness**: Which scanners find the most issues
- **Remediation Progress**: Tracking of issue resolution
- **Risk Scores**: Prioritized risk assessment

### ML Insights (Optional)

If ML features are enabled:

- **Anomaly Detection**: Identify unusual scan patterns
- **Correlation Analysis**: Find relationships between finding types
- **Remediation Recommendations**: Prioritized action items

### Exporting Analytics

- Export analytics data as CSV, JSON, or PDF
- Filter by time range before exporting

## Tenant Settings

Configure tenant-specific settings for your organization.

### Policy Settings

- **Gate Thresholds**: Maximum allowed findings per severity level
- **Pass Criteria**: Requirements for scan to pass

### Scanner Settings

- **Enabled Scanners**: Enable/disable specific scanners
- **Timeouts**: Configure scanner timeouts
- **Custom Configurations**: Advanced scanner settings

### Severity Settings

- **Severity Mappings**: Custom severity classifications
- **Severity Thresholds**: Alert thresholds per severity
- **Severity Actions**: Actions to take (block, warn, notify)

### Notification Settings

- **Alert Thresholds**: When to send notifications
- **Notification Channels**: Email, webhook, Slack, Teams
- **Preferences**: Channel-specific settings

### Scan Settings

- **Default Parameters**: Default scan configuration
- **Retention Policies**: How long to keep scan data

### Integration Settings

- **Webhook URLs**: External system integrations
- **Tool Configurations**: Third-party tool settings

## API Keys

API keys allow programmatic access to the platform.

### Creating an API Key

1. Navigate to "API Keys" (in user menu)
2. Click "Create API Key"
3. Enter a descriptive name
4. Click "Create"
5. **Important**: Copy the key immediately - it won't be shown again

### Using API Keys

Include the API key in requests:

```bash
curl -H "X-API-Key: ss-proj-h_your-key-here" \
  http://localhost:8000/api/v1/scans
```

### API Key Permissions

API keys inherit permissions from the user who created them:
- **Admin**: Full access to create scans, manage users, etc.
- **Scanner**: Can create scans, limited read access
- **Viewer**: Read-only access

### Revoking API Keys

1. Go to "API Keys"
2. Find the key to revoke
3. Click "Revoke"
4. Confirm revocation

## User Management

### Creating Users (Tenant Admin)

1. Navigate to "User Management"
2. Click "Create User"
3. Fill in:
   - Email address
   - Name
   - Password
   - Role (Tenant Admin, Viewer, Scanner)
4. Click "Create"

### Managing Users

- **Edit User**: Update name, email, role
- **Activate/Deactivate**: Enable or disable user accounts
- **Reset Password**: Force password reset on next login

### Roles

- **Super Admin**: Full platform access across all tenants
- **Tenant Admin**: Full access within own tenant
- **Viewer**: Read-only access
- **Scanner**: Can create scans, limited read access

## Best Practices

- Run scans regularly (daily or weekly)
- Create baselines after security reviews
- Review and remediate critical findings immediately
- Use MFA for all admin accounts
- Rotate API keys periodically
- Monitor analytics for trends

For more detailed best practices, see the [Best Practices Guide](../best-practices/README.md).

