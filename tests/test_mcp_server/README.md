# Test MCP Server - Comprehensive Vulnerability Test Suite

This test MCP server is designed to trigger all detectors and sensors across most vulnerability categories to validate the scanning system.

## Purpose

This server contains intentionally vulnerable code patterns to test:
- **SAST Scanners** (Semgrep, Code Rules)
- **Secrets Detection** (Gitleaks, TruffleHog)
- **MCP-Specific Scanners** (MCP Check, MCP Yara, MCP Probe)

## Vulnerability Categories Included

1. **SQL Injection** - Multiple patterns
2. **Command Injection** - Shell command execution
3. **Remote Code Execution (RCE)** - eval(), exec(), pickle
4. **SSRF (Server-Side Request Forgery)** - Unsafe URL fetching
5. **Local File Inclusion (LFI)** - Path traversal
6. **Zip Slip** - Archive extraction vulnerabilities
7. **Hardcoded Secrets** - API keys, passwords, tokens
8. **Insecure Deserialization** - Pickle, JSON with eval
9. **XSS (Cross-Site Scripting)** - Reflected XSS patterns
10. **Path Traversal** - Directory traversal
11. **Insecure Random** - Weak random number generation
12. **Weak Cryptography** - MD5, DES usage
13. **Insecure HTTP** - HTTP without TLS
14. **Hardcoded Credentials** - Passwords in code
15. **Sensitive Data Exposure** - Logging sensitive info

## Structure

```
test_mcp_server/
├── README.md
├── pyproject.toml
├── src/
│   └── test_mcp_server/
│       ├── __init__.py
│       ├── server.py          # Main MCP server with vulnerabilities
│       ├── utils.py           # Utility functions with issues
│       ├── database.py        # Database operations with SQL injection
│       ├── file_ops.py        # File operations with LFI/Zip Slip
│       └── api_client.py      # API client with SSRF
└── tests/
    └── test_server.py
```

## Usage

This server is intended for testing purposes only. Do not deploy in production.

To scan this server:
```bash
# From SentraScan platform
Scan Type: MCP
Target: tests/test_mcp_server (or GitHub URL if pushed)
```

## Expected Findings

The scanner should detect:
- Multiple SQL injection vulnerabilities
- Command injection patterns
- RCE vulnerabilities (eval, exec, pickle)
- SSRF vulnerabilities
- LFI/Zip Slip vulnerabilities
- Hardcoded secrets (API keys, passwords)
- Insecure deserialization
- Weak cryptography
- And more...

