# How-To Guides

Step-by-step guides for common tasks and workflows.

## Table of Contents

1. [How to Set Up Your First Tenant](#how-to-set-up-your-first-tenant)
2. [How to Run Your First Scan](#how-to-run-your-first-scan)
3. [How to Create and Use Baselines](#how-to-create-and-use-baselines)
4. [How to Configure Tenant Settings](#how-to-configure-tenant-settings)
5. [How to Set Up MFA](#how-to-set-up-mfa)
6. [How to Create API Keys](#how-to-create-api-keys)
7. [How to Integrate with CI/CD](#how-to-integrate-with-cicd)
8. [How to Export and Share Results](#how-to-export-and-share-results)
9. [How to Interpret Scan Results](#how-to-interpret-scan-results)
10. [How to Remediate Common Issues](#how-to-remediate-common-issues)

## How to Set Up Your First Tenant

### Prerequisites

- Super Admin access or ability to create a tenant

### Steps

1. **Log in** as Super Admin
2. Navigate to **"Tenant Management"** (in user menu)
3. Click **"Create Tenant"**
4. Fill in tenant details:
   - **Name**: Your organization name
   - **Description** (optional): Brief description
5. Click **"Create"**
6. **Create a user** for the tenant:
   - Go to **"User Management"**
   - Click **"Create User"**
   - Assign **Tenant Admin** role
   - Set email and password
7. **Log in** with the new user account
8. Configure tenant settings (see [How to Configure Tenant Settings](#how-to-configure-tenant-settings))

## How to Run Your First Scan

### MCP Scan

1. **Prepare your MCP configuration**:
   - Locate your MCP config file (e.g., `~/.cursor/mcp.json`)
   - Or use auto-discovery to find configs automatically

2. **Run the scan**:
   - Navigate to **"Run Scan"** → **"MCP Scan"**
   - Enable **"Auto Discover"** OR enter config paths manually
   - Click **"Run Scan"**

3. **Review results**:
   - View findings by severity
   - Check gate result (pass/fail)
   - Review remediation recommendations

### Model Scan

1. **Locate your model file**:
   - Supported formats: `.pkl`, `.pt`, `.pth`, `.h5`, `.onnx`, etc.

2. **Run the scan**:
   - Navigate to **"Run Scan"** → **"Model Scan"**
   - Enter model file path
   - Enable **"Generate SBOM"** if needed
   - Click **"Run Scan"**

3. **Review results**:
   - Check for deserialization vulnerabilities
   - Review SBOM if generated
   - Address critical findings first

## How to Create and Use Baselines

### Creating a Baseline

1. **Run a scan** that passes all security checks
2. Navigate to **"Baselines"**
3. Click **"Create Baseline"**
4. Select the scan that passed
5. Enter baseline name and description
6. Click **"Create"**

### Using Baselines for Comparison

1. **Run a new scan**
2. From the scan detail page, click **"Compare with Baseline"**
3. Select the baseline to compare against
4. Review differences:
   - **New Findings**: Issues introduced since baseline
   - **Resolved Findings**: Issues fixed since baseline
   - **Unchanged**: Issues still present

### Baseline Drift Detection

The platform automatically detects when current configurations differ from approved baselines. This helps identify:
- Unauthorized changes
- Security regressions
- Configuration drift

## How to Configure Tenant Settings

1. Navigate to **"Tenant Settings"** (in user menu)
2. **Configure each category**:

   **Policy Settings**:
   - Set gate thresholds (max findings per severity)
   - Configure pass criteria

   **Scanner Settings**:
   - Enable/disable specific scanners
   - Set scanner timeouts

   **Severity Settings**:
   - Customize severity mappings
   - Set alert thresholds
   - Configure severity actions

   **Notification Settings**:
   - Set alert thresholds
   - Configure notification channels
   - Set up webhook URLs

   **Scan Settings**:
   - Set default scan parameters
   - Configure retention policies

   **Integration Settings**:
   - Add webhook URLs
   - Configure external tool integrations

3. Click **"Save Settings"** after each category

## How to Set Up MFA

### Prerequisites

- Authenticator app installed (Google Authenticator, Authy, etc.)

### Steps

1. **Log in** to your account
2. Navigate to **"Security Settings"** (in user profile)
3. Click **"Enable MFA"**
4. **Scan the QR code** with your authenticator app
5. **Enter the verification code** from your app
6. Click **"Verify and Enable"**

### Using MFA

After enabling MFA:
1. Enter your email and password
2. Enter the 6-digit code from your authenticator app
3. Click **"Login"**

### Disabling MFA

1. Go to **"Security Settings"**
2. Click **"Disable MFA"**
3. Enter your MFA code to confirm
4. MFA will be disabled

## How to Create API Keys

1. Navigate to **"API Keys"** (in user menu)
2. Click **"Create API Key"**
3. Enter a descriptive name (e.g., "CI/CD Pipeline", "Development Key")
4. Click **"Create"**
5. **Copy the API key immediately** - it won't be shown again
6. Store the key securely (password manager, secrets management system)

### Best Practices

- Use descriptive names for easy identification
- Create separate keys for different purposes
- Rotate keys periodically (every 90 days)
- Revoke unused keys immediately
- Never commit keys to version control

## How to Integrate with CI/CD

### GitHub Actions Example

```yaml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run SentraScan
        run: |
          curl -X POST ${{ secrets.SENTRASCAN_API_URL }}/api/v1/mcp/scans \
            -H "X-API-Key: ${{ secrets.SENTRASCAN_API_KEY }}" \
            -H "Content-Type: application/json" \
            -d '{"auto_discover": true}'
      
      - name: Check Results
        # Add logic to fail build if critical findings detected
```

### GitLab CI Example

```yaml
security_scan:
  stage: test
  script:
    - |
      RESPONSE=$(curl -X POST $SENTRASCAN_API_URL/api/v1/mcp/scans \
        -H "X-API-Key: $SENTRASCAN_API_KEY" \
        -H "Content-Type: application/json" \
        -d '{"auto_discover": true}')
      
      CRITICAL_COUNT=$(echo $RESPONSE | jq -r '.gate_result.critical_count')
      
      if [ "$CRITICAL_COUNT" -gt 0 ]; then
        echo "Critical findings detected. Build failed."
        exit 1
      fi
```

### Jenkins Pipeline Example

```groovy
pipeline {
    agent any
    stages {
        stage('Security Scan') {
            steps {
                script {
                    def response = sh(
                        script: """
                            curl -X POST ${env.SENTRASCAN_API_URL}/api/v1/mcp/scans \
                              -H "X-API-Key: ${env.SENTRASCAN_API_KEY}" \
                              -H "Content-Type: application/json" \
                              -d '{"auto_discover": true}'
                        """,
                        returnStdout: true
                    )
                    
                    def json = readJSON text: response
                    if (json.gate_result.critical_count > 0) {
                        error("Critical security findings detected")
                    }
                }
            }
        }
    }
}
```

## How to Export and Share Results

### Exporting from Web UI

1. **From Dashboard**:
   - Click **"Export"** dropdown
   - Choose format (CSV or JSON)

2. **From Scan Detail**:
   - Click **"Export Findings"**
   - Choose format (CSV or JSON)

3. **From Analytics**:
   - Click export button (CSV, JSON, or PDF)
   - Select time range
   - Download file

### Exporting via API

```bash
# Export scan findings
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8000/api/v1/scans/{scan_id}/findings/export?format=csv" \
  -o findings.csv

# Export analytics
curl -H "X-API-Key: $API_KEY" \
  "http://localhost:8000/api/v1/analytics/export?format=pdf&days=30" \
  -o analytics.pdf
```

### Sharing Results

- **Email**: Attach exported files
- **Slack/Teams**: Upload to channels
- **JIRA**: Attach to tickets
- **Documentation**: Include in security reports

## How to Interpret Scan Results

### Understanding Severity Levels

- **Critical**: Immediate action required (e.g., hardcoded secrets, command injection)
- **High**: Address soon (e.g., excessive permissions, baseline drift)
- **Medium**: Should be addressed (e.g., weak configurations)
- **Low**: Consider addressing (e.g., informational findings)
- **Info**: Informational only (e.g., best practice suggestions)

### Gate Result

- **Passed**: Scan meets policy requirements (no critical findings, within thresholds)
- **Failed**: Scan violates policy (critical findings or exceeds thresholds)

### Finding Details

Each finding includes:
- **Title**: Brief description
- **Description**: Detailed explanation
- **Location**: Where the issue was found
- **Remediation**: Steps to fix
- **Evidence**: Supporting data

### Prioritization

1. **Address Critical findings first**
2. **Review High findings within 24 hours**
3. **Plan remediation for Medium findings**
4. **Document Low findings for future review**

## How to Remediate Common Issues

### Hardcoded Secrets

**Issue**: API keys, passwords, or tokens found in configuration files.

**Remediation**:
1. Remove hardcoded secrets from files
2. Move to environment variables
3. Use secrets management system
4. Rotate compromised credentials
5. Re-scan to verify fix

**Example**:
```yaml
# Before (BAD)
api_key: "sk-1234567890abcdef"

# After (GOOD)
api_key: "${API_KEY}"  # Use environment variable
```

### Command Injection

**Issue**: Unsanitized user input in command execution.

**Remediation**:
1. Validate and sanitize all inputs
2. Use parameterized commands
3. Avoid shell execution when possible
4. Implement input validation

### Excessive Permissions

**Issue**: Overly permissive access controls.

**Remediation**:
1. Apply principle of least privilege
2. Review and restrict permissions
3. Use role-based access control
4. Audit permission usage

### Baseline Drift

**Issue**: Configuration differs from approved baseline.

**Remediation**:
1. Review changes against baseline
2. Determine if changes are authorized
3. If authorized: Update baseline
4. If unauthorized: Revert to baseline
5. Investigate cause of drift

### Model Security Issues

**Issue**: Vulnerable model files (pickle exploits, unsafe deserialization).

**Remediation**:
1. Use SafeTensors format when possible
2. Avoid pickle for untrusted models
3. Validate model sources
4. Scan models before deployment
5. Use model signing/verification

## Additional Resources

- [User Guide](../user-guide/README.md) - Comprehensive usage documentation
- [API Documentation](../api/README.md) - API reference
- [Best Practices](../best-practices/README.md) - Security recommendations
- [Troubleshooting](../troubleshooting/README.md) - Common issues and solutions
- [FAQ](../faq/README.md) - Frequently asked questions

