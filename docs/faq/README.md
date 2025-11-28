# Frequently Asked Questions (FAQ)

Common questions and answers about SentraScan Platform.

## General

### What is SentraScan Platform?

SentraScan Platform is a unified security scanning solution for MCP (Model Context Protocol) configurations and ML model files. It helps identify security vulnerabilities, generate SBOMs, and manage security baselines.

### What file formats are supported?

**MCP Scans**: JSON configuration files (`.json`, `.yaml`, `.yml`)

**Model Scans**: 30+ formats including:
- Pickle (`.pkl`, `.pickle`)
- PyTorch (`.pt`, `.pth`, `.bin`)
- TensorFlow (`.h5`, SavedModel, `.pb`)
- ONNX (`.onnx`)
- GGUF (LLM formats)
- SafeTensors
- And many more

### Is there a free tier?

Contact your administrator or sales team for pricing and licensing information.

### How do I get started?

See the [Getting Started Guide](../getting-started/README.md) for step-by-step instructions.

## Scans

### How long do scans take?

Scan duration depends on:
- File size and complexity
- Number of files scanned
- Scanner type and configuration
- Server resources

Typical scan times:
- **MCP scans**: 10-60 seconds
- **Model scans**: 30 seconds - 5 minutes (depending on model size)

### Can I cancel a running scan?

Currently, scans cannot be cancelled once started. They will complete or timeout based on configured timeout settings.

### What happens if a scan fails?

Failed scans are logged with error details. Check the scan detail page or logs for specific error messages. Common causes include file access issues, timeouts, or invalid file formats.

### Can I schedule scans?

Scheduled scans are planned for future releases. Currently, scans must be triggered manually via UI or API.

### What's the difference between MCP and Model scans?

- **MCP scans**: Analyze Model Context Protocol configuration files for security issues (secrets, injection, permissions)
- **Model scans**: Analyze ML model files for vulnerabilities (deserialization attacks, unsafe formats)

## Findings

### How are findings prioritized?

Findings are prioritized by:
1. **Severity**: Critical > High > Medium > Low > Info
2. **Risk Score**: Calculated using severity weight, frequency, and age
3. **ML Recommendations**: If ML insights enabled, prioritized recommendations provided

### What should I fix first?

1. **Critical findings** - Address immediately
2. **High findings** - Address within 24 hours
3. **Medium findings** - Plan remediation
4. **Low findings** - Document for future review

### Can I ignore certain findings?

Yes, but not recommended. Instead:
- Fix the underlying issue
- Update policy to reflect acceptable risk
- Document exceptions with justification

### How do I know if a finding is a false positive?

- Review finding details and evidence
- Verify the detection is accurate
- Check scanner documentation
- Contact support if unsure

## Baselines

### What is a baseline?

A baseline is a snapshot of an approved, secure configuration. It's used to detect unauthorized changes (baseline drift).

### When should I create a baseline?

Create a baseline after:
- Security review and approval
- All critical/high findings are remediated
- Configuration is verified secure

### How often should I update baselines?

Update baselines when:
- Authorized changes are made
- Security improvements are implemented
- After major configuration updates

### Can I have multiple baselines?

Yes, you can create multiple baselines for different configurations or time periods.

## Authentication & Security

### How do I reset my password?

1. Go to login page
2. Click "Forgot Password"
3. Enter your email
4. Follow instructions in email
5. Set new password

### What are the password requirements?

- Minimum 12 characters
- Must include uppercase letters
- Must include lowercase letters
- Must include numbers
- Must include special characters

### Is MFA required?

MFA is optional but highly recommended, especially for admin accounts. It can be enabled in user security settings.

### How do API keys work?

API keys provide programmatic access to the platform. They:
- Inherit permissions from the creating user
- Can be revoked at any time
- Have expiration dates (optional)
- Are tenant-scoped

### Are API keys secure?

Yes. API keys are:
- Hashed before storage
- Transmitted over HTTPS only
- Tenant-isolated
- Can be rotated regularly

## Multi-Tenancy

### What is a tenant?

A tenant is an isolated organization or team within the platform. Each tenant has:
- Separate data storage
- Independent settings
- Isolated user accounts
- Own API keys

### Can users access multiple tenants?

- **Super Admins**: Can access all tenants
- **Other users**: Can only access their assigned tenant

### How is data isolated between tenants?

Data isolation is enforced through:
- Database sharding (physical separation)
- Tenant-scoped queries
- Encryption at rest (tenant-specific keys)
- RBAC enforcement

## Analytics

### What analytics are available?

- Trend analysis (findings over time)
- Severity distribution
- Scanner effectiveness metrics
- Remediation progress tracking
- Risk scoring and prioritization

### Can I export analytics?

Yes, analytics can be exported as:
- CSV (spreadsheet format)
- JSON (programmatic access)
- PDF (reports)

### How far back does analytics go?

Analytics can analyze data from any time range. Default is 30 days, but you can select:
- Last 7 days
- Last 30 days
- Last 90 days
- Custom date range

## ML Insights

### What are ML Insights?

ML Insights provide machine learning-based analysis:
- **Anomaly Detection**: Identify unusual scan patterns
- **Correlation Analysis**: Find relationships between finding types
- **Remediation Recommendations**: Prioritized action items

### Do ML models learn from my data?

**No.** ML models are trained on synthetic data only. Your customer data is never used for training. Models only perform inference (prediction) on your data.

### How do I enable ML Insights?

1. Set environment variable: `ML_INSIGHTS_ENABLED=true`
2. Install scikit-learn: `pip install scikit-learn`
3. Restart the server
4. ML insights will be available in Analytics dashboard

### Are ML Insights required?

No, ML Insights are optional. The platform works fully without them.

## API

### What's the API rate limit?

Rate limits:
- **Per API Key**: 100 requests/minute
- **Per IP**: 200 requests/minute
- **Per Tenant**: 500 requests/minute

### Can I increase rate limits?

Contact your administrator to discuss custom rate limits.

### How do I handle pagination?

Use `limit` and `offset` query parameters:

```
GET /api/v1/scans?limit=50&offset=100
```

### What's the API version?

Current API version is `v1`. All endpoints are under `/api/v1/`.

## Troubleshooting

### Scan returns no findings - is that normal?

Yes, if your files are secure! However, verify:
- Scanners are enabled
- File paths are correct
- Policy isn't too permissive

### I can't log in - what should I do?

1. Verify email and password
2. Check for account lockout
3. Try password reset
4. Contact administrator

### Export file is empty - why?

- Check time range has data
- Verify filters aren't too restrictive
- Try different format
- Check export permissions

### For more troubleshooting help:

See the [Troubleshooting Guide](../troubleshooting/README.md).

## Best Practices

### How often should I run scans?

- **Development**: Before each commit
- **CI/CD**: On every build
- **Production**: Daily or weekly
- **After changes**: Immediately after configuration changes

### Should I scan in production?

Yes, but consider:
- Use read-only scans when possible
- Schedule during low-traffic periods
- Monitor resource usage
- Use appropriate timeouts

### How do I integrate with CI/CD?

See [How to Integrate with CI/CD](../how-to/README.md#how-to-integrate-with-cicd) for examples.

### What's the best way to remediate findings?

1. **Prioritize**: Address critical findings first
2. **Document**: Track remediation progress
3. **Verify**: Re-scan after fixes
4. **Baseline**: Create baseline after remediation

## Support

### Where can I get help?

- **Documentation**: This documentation site
- **FAQ**: This page
- **Troubleshooting**: [Troubleshooting Guide](../troubleshooting/README.md)
- **Support**: Contact your administrator or support team

### How do I report a bug?

Contact support with:
- Description of the issue
- Steps to reproduce
- Error messages
- System information
- Log excerpts (if available)

### Can I request a feature?

Yes! Contact your administrator or submit feature requests through your support channel.

## Additional Resources

- [Getting Started Guide](../getting-started/README.md)
- [User Guide](../user-guide/README.md)
- [API Documentation](../api/README.md)
- [How-To Guides](../how-to/README.md)
- [Best Practices Guide](../best-practices/README.md)
- [Troubleshooting Guide](../troubleshooting/README.md)
- [Glossary](../glossary/README.md)

