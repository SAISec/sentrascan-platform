# Glossary

Definitions of terms and concepts used in SentraScan Platform.

## A

### API Key
A unique identifier used for programmatic access to the SentraScan Platform API. API keys follow the format `ss-proj-h_` followed by a 147-character alphanumeric string with one hyphen. API keys are associated with users and tenants, and inherit permissions from the creating user.

### Analytics
The process of analyzing scan data to identify trends, patterns, and insights. Analytics includes trend analysis, severity distribution, scanner effectiveness metrics, remediation progress tracking, and risk scoring.

### Anomaly Detection
A machine learning feature that identifies unusual patterns in scan results. Anomalies may indicate security issues, configuration problems, or unexpected changes.

### Audit Log
A record of security-relevant events including authentication, authorization, data access, and configuration changes. Audit logs are stored in the database and used for compliance and security monitoring.

## B

### Baseline
A snapshot of an approved, secure configuration. Baselines are used to detect unauthorized changes (baseline drift) and ensure configurations remain compliant with security policies.

### Baseline Drift
When a current configuration differs from an approved baseline. Baseline drift may indicate unauthorized changes or security regressions.

## C

### CI/CD
Continuous Integration/Continuous Deployment. The practice of automatically building, testing, and deploying code changes. SentraScan can be integrated into CI/CD pipelines to scan configurations and models before deployment.

### Critical Finding
A security issue of the highest severity that requires immediate attention. Critical findings typically include hardcoded secrets, command injection vulnerabilities, or other issues that pose immediate security risks.

### CSRF (Cross-Site Request Forgery)
A security vulnerability where unauthorized commands are transmitted from a user that the website trusts. SentraScan implements CSRF protection using tokens and SameSite cookies.

## D

### Data Masking
The process of obscuring sensitive data in logs and telemetry. SentraScan masks API keys, passwords, email addresses, and IP addresses in log output to protect sensitive information.

### Database Sharding
A database architecture pattern where data is partitioned across multiple schemas or databases. SentraScan uses schema-based sharding to physically isolate tenant data.

## E

### Encryption at Rest
The practice of encrypting data stored in databases or on disk. SentraScan uses AES-256 encryption with tenant-specific keys to encrypt sensitive data at rest.

### Encryption in Transit
The practice of encrypting data during transmission over networks. SentraScan uses TLS 1.3 for all network communications.

## F

### Finding
A security issue detected by a scanner. Each finding includes severity, category, title, description, location, remediation guidance, and evidence.

### Finding Category
The type of security issue, such as:
- `hardcoded_secret`: Hardcoded API keys, passwords, or tokens
- `command_injection`: Unsafe command execution
- `excessive_permissions`: Overly permissive access controls
- `baseline_drift`: Configuration differs from baseline
- `tool_poisoning`: Malicious tool configurations

## G

### Gate Result
The overall result of a scan, indicating whether the scan passed or failed based on policy thresholds. A scan passes if it meets all policy requirements (e.g., no critical findings, within severity thresholds).

## H

### Hardcoded Secret
A security vulnerability where sensitive credentials (API keys, passwords, tokens) are stored directly in configuration files or code instead of using secure storage mechanisms like environment variables or secrets management systems.

## I

### Isolation Forest
A machine learning algorithm used for anomaly detection. SentraScan uses Isolation Forest to identify unusual scan patterns without training on customer data.

## K

### Key Management
The process of generating, storing, rotating, and securing encryption keys. SentraScan includes a local key management system that can be extended to integrate with external key management services (HashiCorp Vault, AWS KMS, Azure Key Vault).

### Key Rotation
The practice of periodically changing encryption keys to limit the impact of key compromise. SentraScan supports key rotation without downtime or data loss.

## M

### MCP (Model Context Protocol)
A protocol for configuring and managing AI model contexts. SentraScan scans MCP configuration files for security vulnerabilities.

### MFA (Multi-Factor Authentication)
An authentication method that requires multiple verification factors. SentraScan supports TOTP (Time-based One-Time Password) MFA using authenticator apps.

### ML Insights
Machine learning-based analysis features including anomaly detection, correlation analysis, and remediation prioritization. ML insights do not learn from customer data.

### Model Scan
A security scan of machine learning model files. Model scans detect vulnerabilities like unsafe deserialization, pickle exploits, and other model-specific security issues.

## O

### OTEL (OpenTelemetry)
An open standard for observability. SentraScan implements OTEL-compliant telemetry for logging and monitoring.

## P

### Policy
A set of rules that define security requirements and scan pass/fail criteria. Policies can specify maximum allowed findings per severity level, required scanners, and other security thresholds.

### Permission
A specific action that can be performed, such as `scan.create`, `user.read`, or `tenant.update`. Permissions are assigned to roles, and roles are assigned to users.

## R

### RBAC (Role-Based Access Control)
An access control method that restricts system access based on user roles. SentraScan defines roles (Super Admin, Tenant Admin, Viewer, Scanner) with specific permissions.

### Remediation
The process of fixing security issues identified by scans. Remediation includes addressing findings, verifying fixes, and updating baselines.

### Risk Score
A numerical value that quantifies the security risk of findings or scans. Risk scores are calculated using severity weights, frequency, age, and other factors.

### Role
A collection of permissions that define what actions a user can perform. SentraScan roles include:
- **Super Admin**: Full platform access across all tenants
- **Tenant Admin**: Full access within own tenant
- **Viewer**: Read-only access
- **Scanner**: Can create scans, limited read access

## S

### SBOM (Software Bill of Materials)
A list of components, libraries, and dependencies in a software artifact. SentraScan can generate SBOMs for ML models.

### Scanner
A tool or engine that analyzes code, configurations, or models for security issues. SentraScan includes scanners for MCP configurations and ML models.

### Scanner Effectiveness
A metric that measures how well a scanner performs, including the number of findings detected, average scan duration, and pass rate.

### Scan
An execution of one or more scanners against a target (MCP configuration or ML model). Each scan produces findings and a gate result.

### Schema
A database schema is a namespace that contains database objects (tables, indexes, etc.). SentraScan uses schema-based sharding where each tenant has its own schema.

### Session
A user's authenticated session that persists across requests. Sessions use secure, signed cookies and have a configurable timeout (default 48 hours).

### Severity
The level of risk associated with a finding. Severity levels include:
- **Critical**: Immediate action required
- **High**: Address soon (within 24 hours)
- **Medium**: Should be addressed
- **Low**: Consider addressing
- **Info**: Informational only

### Shard
A partition of data in a sharded database. In SentraScan, each tenant's data is stored in a separate shard (schema).

## T

### Tenant
An isolated organization or team within the SentraScan Platform. Each tenant has separate data storage, settings, users, and API keys. Data is physically isolated through database sharding.

### Tenant Settings
Configurable settings specific to each tenant, including policy rules, scanner configurations, severity mappings, notification preferences, and integration settings.

### TOTP (Time-based One-Time Password)
A type of MFA that generates time-based authentication codes. TOTP codes are typically generated by authenticator apps and expire every 30 seconds.

### Trend Analysis
Analysis of scan data over time to identify patterns, improvements, or regressions. Trend analysis helps track security posture over time.

## U

### User
An individual account that can access the SentraScan Platform. Users belong to a tenant and have a role that determines their permissions.

## V

### Vulnerability
A security weakness or flaw that could be exploited. SentraScan scans for vulnerabilities in MCP configurations and ML models.

## Additional Resources

- [User Guide](../user-guide/README.md) - Detailed usage instructions
- [API Documentation](../api/README.md) - API reference
- [Best Practices](../best-practices/README.md) - Security recommendations
- [FAQ](../faq/README.md) - Frequently asked questions

