# MCP Security Scanners: Executive Summary

## Overview
This analysis examines three open-source MCP (Model Context Protocol) security scanning tools for integration into your security infrastructure.

**Analyzed Tools:**
1. **mcp-checkpoint** v2.0.0 (Aira Security) - Apache 2.0
2. **mcp-scan** v0.3.30 (Invariant Labs) - Apache 2.0
3. **Proximity** v1.0.0 (Thomas Roccia) - GPLv3

All three are Python-based (≥3.10), CLI-driven tools that scan MCP servers for security vulnerabilities.

---

## Key Prerequisites Summary

### mcp-checkpoint
- **Runtime:** Python 3.10-3.15
- **Installation:** `pip install mcp-checkpoint`
- **Dependencies:** torch, transformers (~100s MB model download on first run)
- **External Services:** None (100% offline after initial model download)
- **Environment Variables:** None required
- **OS:** Linux, macOS, Windows

### mcp-scan
- **Runtime:** Python 3.10+
- **Installation:** `uvx mcp-scan@latest` (instant) or `pip install mcp-scan`
- **Dependencies:** Standard Python libs, optional `[proxy]` extra
- **External Services:** Snyk/Invariant API for scan mode (opt-out available)
- **Environment Variables:** None required (optional: `INVARIANT_API_KEY` for advanced guardrails)
- **OS:** Linux, macOS, Windows

### Proximity
- **Runtime:** Python 3.10+
- **Installation:** Clone repo + `pip install -r requirements.txt`
- **Dependencies:** nova-hunting
- **External Services:** OpenAI or Groq API (for NOVA security mode only)
- **Environment Variables:** `OPENAI_API_KEY` or `GROQ_API_KEY` (for NOVA mode)
- **OS:** Linux, macOS, Windows

---

## Common Features (All Three)

**What ALL three tools provide:**
- ✅ MCP tool/prompt/resource enumeration
- ✅ Prompt injection detection
- ✅ Tool poisoning detection
- ✅ JSON output format
- ✅ Markdown reports
- ✅ Python 3.10+ runtime
- ✅ CLI interface
- ✅ STDIO MCP server support
- ✅ Rich terminal UI

---

## Unique Differentiators

### 🔵 mcp-checkpoint (Aira Security)
**What ONLY mcp-checkpoint has:**
- **Baseline drift detection** - Hash-based snapshots to detect rug pull attacks
- **Local ML model** - 100% offline prompt injection detection
- **Inspect mode** - Separate command to create/manage baselines
- **Cross-server tool shadowing** - Detect conflicting tool names across servers
- **Command injection detection** - Regex-based OS command pattern matching
- **Hardcoded secrets detection** - Find secrets in configurations
- **Timestamped audit trails** - Full compliance-grade traceability
- **Enterprise edition** - Commercial runtime monitoring (Active Insight Mode)

**Best for:** Regulatory compliance, offline/air-gapped environments, baseline management

---

### 🟢 mcp-scan (Invariant Labs)
**What ONLY mcp-scan has:**
- **Runtime proxy mode** - Intercepts live MCP traffic in real-time
- **Guardrails framework** - Enforce security policies on tool calls/responses
- **PII detection** - Identify and block personal information
- **Runtime secrets detection** - Detect API keys/tokens in live traffic
- **Tool restrictions** - Allowlist/blocklist specific tools
- **Toxic flow detection** - Identify dangerous tool call sequences
- **Whitelist management** - Track approved entities
- **HTTP/SSE support** - Scan remote MCP servers (not just STDIO)
- **Invariant Gateway integration** - Automatic proxy injection

**Best for:** Runtime monitoring, development environments, policy enforcement, DLP (data loss prevention)

---

### 🟡 Proximity (Thomas Roccia)
**What ONLY Proximity has:**
- **NOVA rule engine** - Custom DSL for threat hunting
- **Semantic analysis** - Contextual meaning evaluation (not just keywords)
- **LLM-powered evaluation** - AI-based threat assessment (OpenAI/Groq)
- **Custom rule creation** - Write `.nov` files with detection logic
- **Jailbreak detection** - Specialized rules for prompt bypass attempts
- **Multi-provider LLM** - OpenAI or Groq support
- **Function signature analysis** - Detailed parameter type display
- **Complexity ratings** - Simple/Moderate/Complex tool classifications
- **Example usage generation** - Auto-generate tool call examples
- **Lightweight & focused** - Small codebase, easy to customize

**Best for:** Custom threat hunting, research, semantic threat detection, flexible rule systems

---

## Feature Comparison (Quick Reference)

| Feature | mcp-checkpoint | mcp-scan | Proximity |
|---------|:--------------:|:--------:|:---------:|
| **Baseline drift** | ✅ | ❌ | ❌ |
| **Runtime proxy** | ❌ | ✅ | ❌ |
| **Guardrails** | ❌ | ✅ | ❌ |
| **PII detection** | ❌ | ✅ | ❌ |
| **Custom rules** | ❌ | ✅ | ✅ |
| **Offline** | ✅ | ⚠️ | ⚠️ |
| **HTTP/SSE** | ❌ | ✅ | ✅ |
| **LLM-based** | ✅ (local) | ❌ | ✅ (cloud) |
| **Pip package** | ✅ | ✅ | ❌ |

✅ = Fully supported | ❌ = Not available | ⚠️ = Partial (mode-dependent)

---

## Privacy & Data Sharing

### mcp-checkpoint
- **Data shared:** None (after initial model download)
- **Processing:** 100% local
- **Risk:** Minimal

### mcp-scan
- **Scan mode:** Tool names/descriptions shared with Snyk/Invariant API
- **Proxy mode:** 100% local (no external calls)
- **Opt-out:** `--opt-out` flag available
- **Risk:** Low (metadata only, opt-out available)

### Proximity
- **Discovery mode:** 100% local
- **NOVA mode:** Tool descriptions sent to OpenAI/Groq
- **Risk:** Medium (user controls LLM provider, API costs)

**Privacy ranking:** mcp-checkpoint > mcp-scan (proxy) > mcp-scan (scan) > Proximity (NOVA)

---

## Cost Considerations

| Tool | Base Cost | Ongoing Costs | Commercial |
|------|-----------|---------------|------------|
| **mcp-checkpoint** | Free (OSS) | None | Enterprise edition (paid) |
| **mcp-scan** | Free (OSS) | None (for now) | Future commercial features |
| **Proximity** | Free (OSS) | LLM API usage (~$0.03/tool w/ GPT-4) | None |

**For budget-conscious orgs:** mcp-checkpoint (free + local compute only)

---

## Integration Considerations

### Deployment Models
1. **CI/CD Integration:** mcp-checkpoint (baseline checks before deployment)
2. **Development Proxy:** mcp-scan (runtime guardrails during development)
3. **Ad-hoc Threat Hunting:** Proximity (custom NOVA rules for research)

### Recommended Architecture (Layered Defense)
```
┌───────────────────────────────────────┐
│     CI/CD Pipeline                    │
│  ┌─────────────────────────────────┐  │
│  │ mcp-checkpoint scan             │  │ ← Baseline checks
│  │ (blocks on HIGH/CRITICAL)       │  │
│  └─────────────────────────────────┘  │
└───────────────────────────────────────┘
                  ↓
┌───────────────────────────────────────┐
│     Development Environment           │
│  ┌─────────────────────────────────┐  │
│  │ mcp-scan proxy                  │  │ ← Runtime guardrails
│  │ (PII/secrets detection)         │  │
│  └─────────────────────────────────┘  │
└───────────────────────────────────────┘
                  ↓
┌───────────────────────────────────────┐
│     Production Monitoring             │
│  ┌─────────────────────────────────┐  │
│  │ mcp-checkpoint Enterprise       │  │ ← Active Insight Mode
│  │ (optional commercial tier)      │  │
│  └─────────────────────────────────┘  │
└───────────────────────────────────────┘

       (Ad-hoc Threat Hunting)
┌───────────────────────────────────────┐
│  Proximity + NOVA rules               │ ← Custom investigations
└───────────────────────────────────────┘
```

---

## Risk Assessment

### Technical Risks
| Risk | mcp-checkpoint | mcp-scan | Proximity |
|------|:--------------:|:--------:|:---------:|
| **Data leakage** | Low | Low-Medium | Medium |
| **Dependency bloat** | High (torch) | Low | Low |
| **Vendor lock-in** | Low | Medium | Low |
| **False positives** | Medium | Low | Medium-High |
| **API cost overruns** | None | None | High (NOVA) |
| **Offline operability** | High | Partial | Partial |

### Security Risks
- **mcp-checkpoint:** Minimal (local-only, no external APIs)
- **mcp-scan:** Low (metadata shared, opt-out available, proxy is local)
- **Proximity:** Medium (tool descriptions sent to LLM, user controls provider)

---

## Recommendations by Use Case

### ✅ Choose mcp-checkpoint if you need:
- Regulatory compliance (SOC2, ISO 27001, GDPR)
- Air-gapped/offline environments
- Baseline management and drift detection
- Audit trails with timestamps
- No external API dependencies

### ✅ Choose mcp-scan if you need:
- Runtime monitoring and guardrails
- PII/secrets detection in live traffic
- Development environment protection
- HTTP/SSE remote server scanning
- Toxic flow detection

### ✅ Choose Proximity if you need:
- Custom threat hunting rules
- Semantic/contextual threat detection
- Research and experimentation
- Flexible LLM provider choice
- Lightweight, customizable tool

---

## Quick Start Guidance

### For Immediate Value
**Fastest ROI:** `uvx mcp-scan@latest` (instant scan of all discovered MCP configs)

### For Compliance
**Best fit:** `pip install mcp-checkpoint` → `mcp-checkpoint inspect` → `mcp-checkpoint scan`

### For Development Protection
**Best fit:** `uvx --with "mcp-scan[proxy]" mcp-scan@latest proxy` (add guardrails config)

### For Threat Hunting
**Best fit:** Clone Proximity → write NOVA rules → scan with custom patterns

---

## Limitations to Note

### mcp-checkpoint
- ❌ STDIO only (no HTTP/SSE in open-source version)
- ❌ Large dependency footprint (~100s MB model)
- ❌ No runtime monitoring (enterprise edition only)

### mcp-scan
- ❌ Scan mode requires internet (cloud API)
- ❌ Closed to external contributions
- ❌ Proxy mode requires extra dependencies

### Proximity
- ❌ No baseline management
- ❌ NOVA requires LLM API keys (ongoing costs)
- ❌ No pip package (source-only)
- ❌ No auto-discovery (manual target specification)

---

## Conclusion & Next Steps

**Key Findings:**
1. All three tools are **complementary**, not competing
2. **mcp-checkpoint** = best for compliance and offline use
3. **mcp-scan** = best for runtime monitoring and guardrails
4. **Proximity** = best for custom threat hunting

**Recommended Next Steps:**
1. **Immediate:** Deploy mcp-checkpoint for baseline security
2. **Short-term:** Add mcp-scan proxy for development environments
3. **Long-term:** Integrate Proximity for threat hunting and research

**Minimum Viable Security:**
- Start with **mcp-checkpoint** (free, comprehensive, no external deps)
- Add **mcp-scan proxy** for sensitive development work
- Use **Proximity** for incident response and custom threat investigation

---

## Contact & Further Information

### Documentation Links
- **mcp-checkpoint:** https://github.com/aira-security/mcp-checkpoint
- **mcp-scan:** https://github.com/invariantlabs-ai/mcp-scan
- **Proximity:** https://github.com/fr0gger/proximity

### Community & Support
- **mcp-checkpoint:** Slack community, Enterprise support available
- **mcp-scan:** GitHub issues, Invariant Labs blog
- **Proximity:** GitHub issues, Twitter (@fr0gger_)

---

**Analysis Date:** January 2025  
**Versions Analyzed:**  
- mcp-checkpoint 2.0.0  
- mcp-scan 0.3.30  
- Proximity 1.0.0  

**Note:** Feature sets and capabilities may evolve. Consult official documentation for latest updates.
