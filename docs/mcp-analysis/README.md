# MCP Security Scanner Analysis

This directory contains a comprehensive analysis of **four** MCP (Model Context Protocol) security scanning tools, including three open-source and one enterprise-grade commercial solution.

## 📑 Documentation Structure

### Executive Summary
📄 **[summary.md](./summary.md)** - Original analysis (3 tools)  
📄 **[UPDATED-SUMMARY.md](./UPDATED-SUMMARY.md)** - ⭐ **START HERE** - Updated with Cisco Scanner (4 tools)  
High-level overview with key findings, prerequisites, recommendations, and decision criteria.

### Individual Tool Fact Sheets
- 📄 **[mcp-checkpoint/fact-sheet.md](./mcp-checkpoint/fact-sheet.md)**  
  Aira Security's baseline-driven security scanner with local ML model

- 📄 **[mcp-scan/fact-sheet.md](./mcp-scan/fact-sheet.md)**  
  Invariant Labs' static + dynamic scanner with runtime proxy and guardrails

- 📄 **[proximity/fact-sheet.md](./proximity/fact-sheet.md)**  
  Thomas Roccia's NOVA-powered rule-based threat hunter

- 📄 **[mcp-scanner/fact-sheet.md](./mcp-scanner/fact-sheet.md)** ⭐ **NEW**  
  Cisco's enterprise-grade multi-engine scanner (API + YARA + LLM)

### Cross-Tool Comparison
📄 **[comparison.md](./comparison.md)**  
Detailed side-by-side comparison: common features, unique capabilities, technology stacks, use cases

---

## 🚀 Quick Reference

### Tools at a Glance

| Tool | Version | License | Best For |
|------|---------|---------|----------|
| **mcp-checkpoint** | 2.0.0 | Apache 2.0 | Compliance, offline, baseline drift |
| **mcp-scan** | 0.3.30 | Apache 2.0 | Runtime monitoring, guardrails, proxy |
| **Proximity** | 1.0.0 | GPLv3 | Custom threat hunting, semantic analysis |
| **cisco-ai-mcp-scanner** ⭐ | 3.2.1 | Apache 2.0 | Enterprise, multi-engine, REST API, CI/CD |

### Installation Quick Start

```bash
# mcp-checkpoint
pip install mcp-checkpoint

# mcp-scan
uvx mcp-scan@latest

# Proximity
git clone https://github.com/fr0gger/proximity.git
cd proximity && pip install -r requirements.txt

# Cisco MCP Scanner ⭐
uv pip install cisco-ai-mcp-scanner
```

---

## 🎯 Decision Matrix

### Choose **mcp-checkpoint** if you need:
- ✅ Regulatory compliance (audit trails)
- ✅ Air-gapped/offline environments
- ✅ Baseline management & drift detection
- ✅ No external API dependencies
- ✅ Comprehensive static analysis

### Choose **mcp-scan** if you need:
- ✅ Runtime monitoring (live traffic)
- ✅ Guardrails & policy enforcement
- ✅ PII/secrets detection
- ✅ HTTP/SSE remote server scanning
- ✅ Development environment protection

### Choose **Proximity** if you need:
- ✅ Custom threat hunting rules
- ✅ Semantic analysis (meaning-based)
- ✅ Flexible LLM providers
- ✅ Research & experimentation
- ✅ Lightweight, customizable tool

### Choose **Cisco MCP Scanner** if you need: ⭐
- ✅ Enterprise-grade support (Cisco backing)
- ✅ Multi-engine validation (3 independent engines)
- ✅ REST API for CI/CD integration
- ✅ Commercial threat intelligence
- ✅ Maximum LLM flexibility (AWS Bedrock, Azure, local)
- ✅ Defense-in-depth scanning

---

## 📊 Common Features (All Three)

- MCP tool/prompt/resource enumeration
- Prompt injection detection
- Tool poisoning detection
- JSON & Markdown output
- Python 3.10+ runtime
- CLI interface
- STDIO support

---

## 🔒 Privacy Considerations

| Tool | Data Shared Externally | Processing |
|------|------------------------|------------|
| **mcp-checkpoint** | None (after model download) | 100% local |
| **mcp-scan** (scan) | Tool names/descriptions | Cloud API (opt-out available) |
| **mcp-scan** (proxy) | None | 100% local |
| **Proximity** (discovery) | None | 100% local |
| **Proximity** (NOVA) | Tool descriptions → LLM | OpenAI/Groq |

---

## 📈 Recommended Integration Strategy

**Layered Defense:**
1. **CI/CD:** mcp-checkpoint (baseline checks)
2. **Development:** mcp-scan proxy (runtime guardrails)
3. **Threat Hunting:** Proximity (custom NOVA rules)

**Minimum Viable Security:**
- Start with **mcp-checkpoint** (free, comprehensive, offline)
- Add **mcp-scan proxy** for sensitive dev work
- Use **Proximity** for incident response

---

## 📚 Repository Information

**Analyzed Repositories:**
1. https://github.com/aira-security/mcp-checkpoint
2. https://github.com/invariantlabs-ai/mcp-scan
3. https://github.com/fr0gger/proximity
4. https://github.com/cisco-ai-defense/mcp-scanner ⭐ **NEW**

**Analysis Date:** January 2025  
**Versions:**
- mcp-checkpoint 2.0.0
- mcp-scan 0.3.30
- Proximity 1.0.0
- cisco-ai-mcp-scanner 3.2.1 ⭐ **NEW**

---

## 🔄 Update Policy

This analysis is based on the tool versions and features available as of January 2025. For the latest capabilities:
- Consult official documentation
- Check GitHub releases
- Review CHANGELOG files

---

## 📖 How to Use This Documentation

1. **New to MCP security?** → Start with [summary.md](./summary.md)
2. **Evaluating a specific tool?** → Read its fact sheet
3. **Comparing tools?** → See [comparison.md](./comparison.md)
4. **Need integration guidance?** → Check summary.md recommendations

---

## 🛠️ Analysis Methodology

This analysis includes:
- ✅ Repository structure review
- ✅ Dependency analysis (pyproject.toml, requirements.txt)
- ✅ Feature extraction from README and source code
- ✅ License verification
- ✅ Technology stack identification
- ✅ Security model assessment
- ✅ Privacy & data flow analysis
- ✅ Use case mapping
- ✅ Integration considerations

---

## 📞 Support & Questions

For questions about this analysis:
- **Internal:** Contact your security team
- **External:** File an issue in the respective tool's GitHub repository

For tool-specific support:
- **mcp-checkpoint:** Slack community or Enterprise support
- **mcp-scan:** GitHub issues
- **Proximity:** GitHub issues or Twitter (@fr0gger_)

---

**Disclaimer:** This analysis is provided for informational purposes. Always conduct your own security review and testing before deploying tools in production environments.
