# MCP Security Scanners: Executive Summary (Updated with Cisco Scanner)

## Overview
This analysis examines **four** MCP (Model Context Protocol) security scanning tools:

1. **mcp-checkpoint** v2.0.0 (Aira Security) - Apache 2.0
2. **mcp-scan** v0.3.30 (Invariant Labs) - Apache 2.0  
3. **Proximity** v1.0.0 (Thomas Roccia) - GPLv3
4. **cisco-ai-mcp-scanner** v3.2.1 (Cisco Systems) - Apache 2.0 ⭐ **NEW**

All are Python-based (≥3.10), CLI-driven tools that scan MCP servers for security vulnerabilities.

---

## Quick Comparison Matrix

| Feature | mcp-checkpoint | mcp-scan | Proximity | **Cisco Scanner** |
|---------|:--------------:|:--------:|:---------:|:----------------:|
| **License** | Apache 2.0 | Apache 2.0 | GPLv3 | Apache 2.0 |
| **Baseline Drift** | ✅ | ❌ | ❌ | ❌ |
| **Runtime Proxy** | ❌ | ✅ | ❌ | ❌ |
| **Multi-Engine** | ❌ | ❌ | ✅ (NOVA) | ✅✅✅ (3 engines) |
| **REST API Server** | ❌ | ❌ | ❌ | ✅ |
| **Offline Mode** | ✅ | Partial | Partial | Partial (YARA only) |
| **Enterprise Support** | ✅ (paid) | Future | ❌ | ✅ (Cisco) |
| **Pip Package** | ✅ | ✅ | ❌ | ✅ |
| **Cost** | Free | Free | Free + LLM | **Cisco subscription** |

---

## The Cisco MCP Scanner Difference

### 🎯 What Makes It Unique

**Cisco MCP Scanner** is the **only** enterprise-grade, multi-engine scanner with:

1. **Three Independent Engines:**
   - **Cisco AI Defense API** - Commercial threat intelligence
   - **YARA Pattern Matching** - Fast, local rule-based detection
   - **LLM-as-a-Judge** - AI-powered semantic analysis

2. **REST API Server Mode:**
   - Full FastAPI server for CI/CD integration
   - Interactive OpenAPI docs at `/docs`
   - Health check endpoints

3. **Maximum LLM Flexibility:**
   - OpenAI (GPT-4o, GPT-4.1)
   - AWS Bedrock (Claude, Titan)
   - Azure OpenAI
   - **Local LLMs** (Ollama, vLLM, LocalAI)

4. **Enterprise Backing:**
   - Cisco Systems commercial support
   - SLA and compliance guarantees
   - Regular threat intelligence updates

### 💰 Cost Structure

| Component | Cost |
|-----------|------|
| **YARA Engine** | Free (included) |
| **LLM Engine** | $0.01-0.03/tool (or free with local LLM) |
| **Cisco AI Defense API** | **Requires subscription** (contact Cisco) |

**Free Usage:** YARA-only mode + optional local LLM = $0

---

## Updated Recommendations

### Choose **mcp-checkpoint** if you need:
- ✅ Regulatory compliance (audit trails)
- ✅ Air-gapped/offline environments
- ✅ Baseline drift detection
- ✅ No external API dependencies
- ✅ Free, comprehensive static analysis

### Choose **mcp-scan** if you need:
- ✅ Runtime monitoring (live traffic)
- ✅ Guardrails & policy enforcement
- ✅ PII/secrets detection
- ✅ Development environment protection
- ✅ Free, with optional proxy mode

### Choose **Proximity** if you need:
- ✅ Custom threat hunting rules
- ✅ Semantic analysis
- ✅ Research & experimentation
- ✅ Lightweight, customizable tool
- ✅ Free, with pay-per-use LLM

### Choose **Cisco MCP Scanner** if you need: ⭐
- ✅ **Enterprise-grade support**
- ✅ **Multi-engine validation** (3 independent engines)
- ✅ **REST API for CI/CD integration**
- ✅ **Commercial threat intelligence**
- ✅ **Maximum LLM flexibility** (AWS Bedrock, Azure, local)
- ✅ **Defense-in-depth** (combine all engines)

---

## Cost Comparison

| Tool | Initial Cost | Ongoing Cost | Enterprise |
|------|--------------|--------------|------------|
| mcp-checkpoint | Free | $0 | Paid tier available |
| mcp-scan | Free | $0 | Future commercial |
| Proximity | Free | LLM API (~$0.03/tool) | None |
| **Cisco Scanner** | **Cisco subscription** | LLM API (optional) | Included |

**Budget Ranking (lowest to highest):**
1. mcp-checkpoint (100% free, local)
2. mcp-scan (free, optional paid features future)
3. Proximity (free + LLM costs)
4. **Cisco Scanner (requires enterprise subscription)**

---

## Feature Presence Matrix

| Feature | checkpoint | scan | Proximity | **Cisco** |
|---------|:----------:|:----:|:---------:|:---------:|
| Auto-Discovery | ✅ | ✅ | ❌ | ✅ |
| STDIO Support | ✅ | ✅ | ✅ | ✅ |
| HTTP/SSE Support | ❌ | ✅ | ✅ | ✅ |
| Prompt Injection | ✅ | ✅ | ✅ | ✅✅✅ |
| Tool Poisoning | ✅ | ✅ | ✅ | ✅✅✅ |
| Baseline Drift | ✅ | ❌ | ❌ | ❌ |
| Runtime Proxy | ❌ | ✅ | ❌ | ❌ |
| Guardrails | ❌ | ✅ | ❌ | ❌ |
| PII Detection | ❌ | ✅ | ❌ | ❌ |
| YARA Rules | ❌ | ❌ | ❌ | ✅ |
| REST API Server | ❌ | ❌ | ❌ | ✅ |
| Local LLM Support | ❌ | ❌ | ❌ | ✅ |
| AWS Bedrock | ❌ | ❌ | ❌ | ✅ |
| Commercial Support | Paid | Future | ❌ | ✅ |

✅✅✅ = Three engines (API + YARA + LLM)

---

## Architecture Comparison

### Detection Methods

**mcp-checkpoint:**
```
Local ML Model (Llama) → Static Analysis → Report
```

**mcp-scan:**
```
Cloud API → Static Scan → Report
        ↓
Invariant Gateway → Runtime Proxy → Guardrails
```

**Proximity:**
```
NOVA Rule Engine → (Keywords + Semantics + LLM) → Report
```

**Cisco MCP Scanner:**
```
                    ┌→ Cisco AI Defense API
Tool/Prompt/Resource ─→ YARA Pattern Matcher  → Aggregate → Report
                    └→ LLM-as-a-Judge (multi-provider)
```

---

## Recommended Integration Strategy (Updated)

### Layered Defense with Cisco

**Layer 1: CI/CD Pipeline**
```
mcp-checkpoint (baseline) → Block on HIGH/CRITICAL
```

**Layer 2: Pre-Deployment Validation**
```
Cisco MCP Scanner (all 3 engines) → Multi-engine consensus
```

**Layer 3: Development Environment**
```
mcp-scan proxy (guardrails + PII detection)
```

**Layer 4: Threat Hunting**
```
Proximity (custom NOVA rules) OR Cisco Scanner (targeted analysis)
```

### Enterprise Deployment (Cisco-Centric)

**Primary:** Cisco MCP Scanner with Cisco AI Defense subscription
- YARA for fast initial triage
- Cisco API for enterprise threat intelligence
- LLM (AWS Bedrock) for semantic analysis

**Secondary:** mcp-scan proxy for development
**Tertiary:** mcp-checkpoint for baseline compliance

---

## Privacy Considerations (Updated)

| Tool | Data Shared | Processing | Privacy Score |
|------|-------------|------------|---------------|
| mcp-checkpoint | None | 100% local | ⭐⭐⭐⭐⭐ |
| mcp-scan (proxy) | None | 100% local | ⭐⭐⭐⭐⭐ |
| mcp-scan (scan) | Tool names/desc | Cloud API | ⭐⭐⭐⭐ |
| Proximity (discovery) | None | 100% local | ⭐⭐⭐⭐⭐ |
| Proximity (NOVA) | Tool desc → LLM | OpenAI/Groq | ⭐⭐⭐ |
| **Cisco (YARA)** | **None** | **100% local** | ⭐⭐⭐⭐⭐ |
| **Cisco (API)** | **Tool desc** | **Cisco cloud** | ⭐⭐⭐⭐ |
| **Cisco (LLM)** | **Tool desc** | **Chosen provider** | ⭐⭐⭐-⭐⭐⭐⭐⭐ |

**Privacy Ranking (best to worst):**
1. mcp-checkpoint (always local)
2. **Cisco Scanner with YARA-only + local LLM** (no cloud calls)
3. mcp-scan proxy mode (local)
4. mcp-scan scan mode (metadata only)
5. **Cisco Scanner with Cisco API** (enterprise data handling)
6. Proximity NOVA mode (public LLM providers)

---

## Key Decision Factors

### Budget: < $1000/year
**Choose:** mcp-checkpoint + mcp-scan proxy (both free)

### Budget: $1000-10,000/year
**Choose:** Add Proximity with OpenAI for custom rules

### Budget: Enterprise ($10K+/year)
**Choose:** **Cisco MCP Scanner** + Cisco AI Defense subscription

### Compliance: Air-gapped environment
**Choose:** mcp-checkpoint (only fully offline option)

### Compliance: Enterprise SLA required
**Choose:** **Cisco MCP Scanner** (Cisco backing + support)

### Use Case: CI/CD Integration
**Choose:** **Cisco MCP Scanner** (REST API server)

### Use Case: Development Protection
**Choose:** mcp-scan (proxy mode with guardrails)

### Use Case: Custom Threat Hunting
**Choose:** Proximity (NOVA rules) or **Cisco Scanner** (multi-engine)

---

## Installation Quick Reference

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

## Summary Recommendation

**For Most Organizations:**
1. Start with **mcp-checkpoint** (free, comprehensive, local)
2. Add **mcp-scan proxy** for development environments
3. Evaluate **Cisco MCP Scanner** if:
   - Enterprise support required
   - CI/CD REST API integration needed
   - Multi-engine validation desired
   - Budget allows for Cisco subscription

**For Enterprises with Budget:**
- **Primary:** Cisco MCP Scanner (3 engines + REST API + support)
- **Secondary:** mcp-scan proxy (development guardrails)
- **Tertiary:** mcp-checkpoint (compliance baselines)

**For Budget-Constrained:**
- **Primary:** mcp-checkpoint (free, local, comprehensive)
- **Secondary:** Cisco Scanner YARA-only mode (free tier)
- **Optional:** Proximity for custom rules (pay-per-use LLM)

---

## Contact Information

- **mcp-checkpoint:** https://github.com/aira-security/mcp-checkpoint
- **mcp-scan:** https://github.com/invariantlabs-ai/mcp-scan
- **Proximity:** https://github.com/fr0gger/proximity
- **Cisco MCP Scanner:** https://github.com/cisco-ai-defense/mcp-scanner
  - **Sales:** https://www.cisco.com/site/us/en/products/security/ai-defense/index.html

---

**Analysis Date:** January 2025  
**Versions Analyzed:**
- mcp-checkpoint 2.0.0
- mcp-scan 0.3.30
- Proximity 1.0.0
- **cisco-ai-mcp-scanner 3.2.1** ⭐ NEW

**Key Insight:** With the addition of Cisco MCP Scanner, enterprises now have a commercial-grade option with three independent engines, REST API integration, and Cisco backing—filling the gap between open-source tools and enterprise requirements.
