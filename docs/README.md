# SentraScan Platform Documentation

Complete documentation for SentraScan Platform - unified security scanning for MCP configurations and ML models.

## 📚 Documentation Structure

### 🚀 Getting Started
**Start here if you're new to SentraScan Platform**

- **[Quick Start Guide](QUICK-START.md)** - Get up and running in 5 minutes
  - Installation (Docker & Local)
  - First scan examples
  - Basic troubleshooting

- **[User Guide](USER-GUIDE.md)** - Complete user manual
  - Scanning workflows (MCP & Models)
  - Understanding results
  - Baseline management
  - Policy configuration
  - Remediation strategies
  - Best practices

### 🔧 Technical Reference
**For developers and system integrators**

- **[Technical Documentation](TECHNICAL-DOCUMENTATION.md)** - Complete technical reference
  - Architecture overview
  - System components
  - API documentation
  - Database schema
  - Module details
  - Development guide

- **[API Client Examples](API-CLIENT-EXAMPLES.md)** - Integration code examples
  - Python (sync & async)
  - JavaScript/TypeScript
  - Node.js
  - cURL
  - Go
  - Ruby
  - Error handling patterns

### 🔗 Integration Guides
**Connect SentraScan to your workflow**

- **[CI/CD Integration](INTEGRATION-CICD.md)** - Pipeline integration
  - GitHub Actions
  - GitLab CI
  - Jenkins
  - Azure DevOps
  - CircleCI
  - Best practices

### 🛠️ Operations & Administration
**For system administrators and DevOps**

- **[Administrator Guide](ADMIN-GUIDE.md)** - Production deployment
  - Production setup
  - Security hardening
  - Performance tuning
  - High availability
  - Upgrade procedures

- **[Runbooks](RUNBOOKS.md)** - Day-to-day operations
  - Daily operations checklist
  - Health checks
  - Incident response
  - Maintenance procedures
  - Emergency procedures

- **[Monitoring Guide](MONITORING.md)** - Observability
  - Metrics to monitor
  - Prometheus setup
  - Grafana dashboards
  - Alerting configuration
  - Log management

- **[Backup & Recovery](BACKUP-RECOVERY.md)** - Data protection
  - Backup strategies
  - Database backup
  - File system backup
  - Recovery procedures
  - Disaster recovery

### 🔒 Security
**Security best practices and compliance**

- **[Security Best Practices](SECURITY.md)** - Security hardening
  - Security checklist
  - Network security
  - Application security
  - Data security
  - Compliance (SOC 2, GDPR, ISO 27001)
  - Vulnerability management
  - Incident response

### 📋 Requirements & Analysis
**Product requirements and analysis documents**

- **[Product Requirements Document](PRODUCT-REQUIREMENTS-DOCUMENT.md)** - MCP Scanner PRD
- **[SentraScan Platform PRD](SENTRASCAN-PLATFORM-PRD.md)** - Platform-level requirements
- **[SentraScan Model PRD](SENTRASCAN-MODEL-PRD.md)** - Model Scanner requirements

- **[MCP Analysis](mcp-analysis/)** - MCP scanner analysis
  - [Comparison](mcp-analysis/comparison.md) - Tool comparison
  - [Summary](mcp-analysis/summary.md) - Executive summary
  - [Updated Summary](mcp-analysis/UPDATED-SUMMARY.md) - Latest analysis
  - [Final Analysis](mcp-analysis/FINAL-ANALYSIS-SUMMARY.md) - Final recommendations

- **[Model Analysis](model-analysis/)** - Model scanner analysis
  - [Model Scanning Summary](model-analysis/MODEL-SCANNING-ANALYSIS-SUMMARY.md)
  - [Updated Model Analysis](model-analysis/UPDATED-MODEL-ONLY-ANALYSIS.md)
  - [PickleScan Factsheet](model-analysis/01-picklescan-factsheet.md)

### 📝 Planning & Improvement
**Documentation planning and improvement**

- **[Documentation Improvement Plan](DOCUMENTATION-IMPROVEMENT-PLAN.md)** - Roadmap for enhancements
- **[Documentation Structure](DOCUMENTATION-STRUCTURE.md)** - Organization and standards

---

## 🗺️ Documentation Map

### By User Role

**👤 End Users (Developers, Security Engineers)**
1. Start with [Quick Start Guide](QUICK-START.md)
2. Read [User Guide](USER-GUIDE.md) for workflows
3. Reference [API Client Examples](API-CLIENT-EXAMPLES.md) for integration
4. Check [CI/CD Integration](INTEGRATION-CICD.md) for pipelines

**🔧 System Administrators**
1. Read [Administrator Guide](ADMIN-GUIDE.md) for production setup
2. Follow [Security Best Practices](SECURITY.md) for hardening
3. Use [Runbooks](RUNBOOKS.md) for daily operations
4. Set up [Monitoring Guide](MONITORING.md) for observability
5. Configure [Backup & Recovery](BACKUP-RECOVERY.md) procedures

**👨‍💻 Developers**
1. Review [Technical Documentation](TECHNICAL-DOCUMENTATION.md) for architecture
2. Check [API Client Examples](API-CLIENT-EXAMPLES.md) for code samples
3. Follow [Development Guide](TECHNICAL-DOCUMENTATION.md#development-guide) section

**📊 Product Managers**
1. Review [Product Requirements Documents](PRODUCT-REQUIREMENTS-DOCUMENT.md)
2. Check [MCP Analysis](mcp-analysis/) and [Model Analysis](model-analysis/)
3. Reference [Documentation Improvement Plan](DOCUMENTATION-IMPROVEMENT-PLAN.md)

### By Task

**Getting Started**
- [Quick Start Guide](QUICK-START.md) → [User Guide](USER-GUIDE.md)

**Integration**
- [CI/CD Integration](INTEGRATION-CICD.md) → [API Client Examples](API-CLIENT-EXAMPLES.md)

**Production Deployment**
- [Administrator Guide](ADMIN-GUIDE.md) → [Security Best Practices](SECURITY.md) → [Monitoring Guide](MONITORING.md) → [Backup & Recovery](BACKUP-RECOVERY.md)

**Operations**
- [Runbooks](RUNBOOKS.md) → [Monitoring Guide](MONITORING.md) → [Backup & Recovery](BACKUP-RECOVERY.md)

**Development**
- [Technical Documentation](TECHNICAL-DOCUMENTATION.md) → [API Client Examples](API-CLIENT-EXAMPLES.md)

---

## 📖 Documentation Standards

### Formatting
- All documents use Markdown
- Code blocks include language tags
- Diagrams use Mermaid syntax
- Cross-references use relative paths

### Structure
- Table of Contents for documents > 500 lines
- Clear section headings (##, ###)
- Consistent terminology
- Code examples are tested and working

### Navigation
- "Next Steps" section at end of each guide
- Cross-references to related documents
- Back to top links for long documents

---

## 🔍 Quick Reference

### Common Tasks

**Installation:**
- [Quick Start Guide](QUICK-START.md#option-1-docker-deployment-recommended)

**First Scan:**
- [Quick Start Guide](QUICK-START.md#your-first-scan)

**API Integration:**
- [API Client Examples](API-CLIENT-EXAMPLES.md)

**CI/CD Setup:**
- [CI/CD Integration](INTEGRATION-CICD.md)

**Production Deployment:**
- [Administrator Guide](ADMIN-GUIDE.md#production-deployment)

**Security Hardening:**
- [Security Best Practices](SECURITY.md)

**Troubleshooting:**
- [User Guide - Troubleshooting](USER-GUIDE.md#troubleshooting)
- [Technical Documentation - Troubleshooting](TECHNICAL-DOCUMENTATION.md#troubleshooting)
- [Runbooks - Incident Response](RUNBOOKS.md#incident-response)

---

## 📊 Documentation Status

| Document | Status | Last Updated | Completeness |
|----------|--------|--------------|--------------|
| Quick Start Guide | ✅ Complete | 2025-01 | 100% |
| User Guide | ✅ Complete | 2025-01 | 100% |
| Technical Documentation | ✅ Complete | 2025-01 | 100% |
| API Client Examples | ✅ Complete | 2025-01 | 100% |
| CI/CD Integration | ✅ Complete | 2025-01 | 100% |
| Administrator Guide | ✅ Complete | 2025-01 | 100% |
| Runbooks | ✅ Complete | 2025-01 | 100% |
| Monitoring Guide | ✅ Complete | 2025-01 | 100% |
| Backup & Recovery | ✅ Complete | 2025-01 | 100% |
| Security Best Practices | ✅ Complete | 2025-01 | 100% |

---

## 🤝 Contributing to Documentation

**Documentation Standards:**
- [Documentation Structure](DOCUMENTATION-STRUCTURE.md) - Organization and formatting standards
- [Documentation Improvement Plan](DOCUMENTATION-IMPROVEMENT-PLAN.md) - Planned enhancements and roadmap

**Guidelines:**
- Follow formatting standards in [Documentation Structure](DOCUMENTATION-STRUCTURE.md)
- Use consistent terminology across all documents
- Include cross-references to related documents
- Test all code examples before committing
- Update Table of Contents when adding sections

---

## 📞 Getting Help

- **Documentation Issues:** Open an issue or PR
- **Questions:** Check the relevant guide above
- **Feature Requests:** See [Documentation Improvement Plan](DOCUMENTATION-IMPROVEMENT-PLAN.md)

---

**Last Updated:** January 2025  
**Documentation Version:** 1.0

