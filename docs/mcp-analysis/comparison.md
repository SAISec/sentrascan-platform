# MCP Security Scanners: Comprehensive Comparison

## Executive Summary

This document compares three MCP (Model Context Protocol) security scanning tools:
1. **mcp-checkpoint** (Aira Security) - Baseline-driven security scanner
2. **mcp-scan** (Invariant Labs) - Static + dynamic scanner with runtime proxy
3. **Proximity** (Thomas Roccia) - NOVA-powered rule-based threat hunter

All three tools scan MCP servers for security vulnerabilities but use different approaches and target different use cases.

---

## Common Features (Across All Three)

### ✅ Shared Capabilities

| Feature | Description |
|---------|-------------|
| **MCP Auto-Discovery** | Automatically find MCP configurations (Claude, Cursor, Windsurf, VS Code, etc.) |
| **Tool Enumeration** | Catalog MCP tools with names, descriptions, parameters |
| **Prompt Discovery** | List available prompts and their arguments |
| **Resource Discovery** | Enumerate resources and their URIs |
| **Prompt Injection Detection** | Identify malicious prompt patterns |
| **Tool Poisoning Detection** | Detect malicious tool descriptions |
| **JSON Output** | Export results in JSON format |
| **Markdown Reports** | Generate human-readable MD reports |
| **Python-Based** | All implemented in Python (3.10+) |
| **CLI Interface** | Command-line driven tools |
| **STDIO Support** | Connect to local STDIO MCP servers |
| **Rich Terminal UI** | Use `rich` library for colored output |
| **Apache 2.0 License** | mcp-checkpoint and mcp-scan (Proximity is GPLv3) |

---

## Unique Features by Tool

### 🔵 MCP Checkpoint (Aira Security)

#### Unique Capabilities
| Feature | Description |
|---------|-------------|
| **Baseline Drift Detection** | Creates approved snapshots and detects changes (rug pull attacks) |
| **Local ML Model** | Uses Aira-security/FT-Llama-Prompt-Guard-2 (runs locally, no API calls) |
| **Hash-Based Change Detection** | Tracks tool/prompt/resource modifications via hashing |
| **Inspect Mode** | Separate command to generate baseline files |
| **100% Offline** | No external API calls after initial model download |
| **Fuzzy Matching** | Detects tool name ambiguity via thefuzz library |
| **Cross-Server Tool Shadowing** | Identifies conflicting tool names across servers |
| **Command Injection Detection** | Regex-based OS command injection patterns |
| **Excessive Permissions Check** | Flags overly permissive tool configs |
| **Hardcoded Secrets Detection** | Finds secrets in configurations |
| **Timestamped Audit Trail** | Full traceability of baselines and reports |
| **Enterprise Edition** | Commercial offering with Active Insight Mode (runtime analysis) |

#### Security Checks Taxonomy
**Standard Checks:**
- Prompt Injection
- Indirect Prompt Injection
- Cross-Server Tool Shadowing
- Tool Poisoning (prompt + command injection in tool desc/name/args)
- Tool Name Ambiguity
- Command Injection
- Excessive Tool Permissions
- Hardcoded Secrets

**Baseline Checks (Rug Pull Detection):**
- Tool Modified
- Resource Modified
- Resource Template Modified
- Prompt Modified

#### Best For
- **Regulatory compliance** (audit trails)
- **Offline environments** (air-gapped networks)
- **Baseline management** (approved configurations)
- **Enterprise security** (with Active Insight Mode)

---

### 🟢 MCP-Scan (Invariant Labs)

#### Unique Capabilities
| Feature | Description |
|---------|-------------|
| **Runtime Proxy Mode** | Intercepts live MCP traffic in real-time |
| **Guardrails Framework** | Enforce security policies on tool calls/responses |
| **PII Detection** | Identify and block personal information |
| **Secrets Detection** | Detect API keys, passwords, tokens in traffic |
| **Tool Restrictions** | Allowlist/blocklist specific tools |
| **Custom Guardrail Policies** | DSL for defining security rules |
| **Invariant Gateway Integration** | Injects proxy layer into MCP configs |
| **Toxic Flow Detection** | Identifies dangerous tool call sequences |
| **Whitelist Management** | Track and approve known-good entities |
| **HTTP/SSE Support** | Scan remote MCP servers (not just STDIO) |
| **Activity Logging** | Real-time audit logs of MCP traffic |
| **Local + Cloud** | Static scan uses cloud API; proxy is local-only |
| **UVX Support** | Modern Python tooling (uv/uvx) |
| **Closed to Contributions** | Commercial focus (stabilization phase) |

#### Scan Modes
1. **scan (default)** - Static analysis of MCP configurations
2. **proxy** - Runtime monitoring with guardrails
3. **inspect** - View without verification
4. **whitelist** - Manage approved entities

#### Guardrails Capabilities
- PII detection and blocking
- Secrets detection (API keys, tokens)
- Tool call restrictions
- Custom DSL policies
- Data flow constraints

#### Best For
- **Runtime monitoring** (live traffic analysis)
- **Policy enforcement** (guardrails)
- **Development environments** (with proxy)
- **Cloud-based MCP servers** (HTTP/SSE support)
- **Data loss prevention** (PII/secrets detection)

---

### 🟡 Proximity (Thomas Roccia @fr0gger_)

#### Unique Capabilities
| Feature | Description |
|---------|-------------|
| **NOVA Rule Engine** | Custom rule DSL for threat hunting |
| **Keyword + Semantic + LLM** | Three-layer threat detection |
| **Semantic Analysis** | Contextual meaning evaluation (similarity thresholds) |
| **LLM-Powered Evaluation** | AI-based threat assessment (OpenAI/Groq) |
| **Custom Rule Creation** | Users write `.nov` files with detection logic |
| **Jailbreak Detection** | Specialized rules for prompt bypass attempts |
| **Multi-Provider LLM** | OpenAI or Groq support |
| **Function Signature Analysis** | Detailed parameter type display |
| **Complexity Ratings** | Simple/Moderate/Complex tool classifications |
| **Example Usage Generation** | Auto-generates tool call examples |
| **Lightweight & Focused** | Small codebase, easy to understand |
| **Research-Oriented** | Individual project, not commercial |
| **GPLv3 License** | Open source copyleft |
| **No Pip Package** | Source-only distribution |

#### NOVA Rule System Components
1. **meta** - Metadata (description, author, severity)
2. **keywords** - Exact string pattern matching
3. **semantics** - Contextual meaning with similarity threshold
4. **llm** - LLM evaluation queries
5. **condition** - Boolean logic combining above

#### Best For
- **Custom threat hunting** (define your own patterns)
- **Research & experimentation** (flexible rule system)
- **Semantic threat detection** (meaning-based, not just keywords)
- **Budget-flexible scanning** (pay-per-use LLM APIs)
- **Rapid prototyping** (small, focused tool)

---

## Feature Comparison Matrix

| Feature | mcp-checkpoint | mcp-scan | Proximity |
|---------|----------------|----------|-----------|
| **Auto-Discovery** | ✅ | ✅ | ❌ (manual target) |
| **STDIO Support** | ✅ | ✅ | ✅ |
| **HTTP/SSE Support** | ❌ | ✅ | ✅ |
| **Prompt Injection** | ✅ (local ML) | ✅ (cloud API) | ✅ (NOVA rules) |
| **Tool Poisoning** | ✅ | ✅ | ✅ |
| **Baseline Drift** | ✅ | ❌ | ❌ |
| **Rug Pull Detection** | ✅ (hash-based) | ✅ (hash-based) | ❌ |
| **Runtime Proxy** | ❌ (enterprise only) | ✅ | ❌ |
| **Guardrails** | ❌ | ✅ | ❌ |
| **PII Detection** | ❌ | ✅ | ❌ |
| **Secrets Detection** | ✅ (static only) | ✅ (runtime) | ❌ |
| **Toxic Flow Detection** | ❌ | ✅ | ❌ |
| **Whitelist Management** | ❌ | ✅ | ❌ |
| **Custom Rules** | ❌ | ✅ (guardrail DSL) | ✅ (NOVA DSL) |
| **Offline Operation** | ✅ | ❌ (scan mode) / ✅ (proxy mode) | ✅ (discovery) / ❌ (NOVA) |
| **LLM-Based Detection** | ✅ (local) | ❌ | ✅ (cloud) |
| **JSON Output** | ✅ | ✅ | ✅ |
| **Markdown Output** | ✅ | ❌ | ✅ |
| **Pip Package** | ✅ | ✅ | ❌ |
| **Commercial Support** | ✅ (enterprise) | ✅ (closed source focus) | ❌ |
| **License** | Apache 2.0 | Apache 2.0 | GPLv3 |

---

## Technology Stack Comparison

| Aspect | mcp-checkpoint | mcp-scan | Proximity |
|--------|----------------|----------|-----------|
| **Python Version** | 3.10-3.15 | 3.10+ | 3.10+ |
| **MCP Library** | fastmcp~=2.13.0 | mcp[cli]==1.16.0 | mcp>=0.9.0 |
| **ML/AI** | transformers + torch | (cloud API) | nova-hunting |
| **UI Library** | rich | rich | rich (minimal) |
| **Fuzzy Matching** | thefuzz | rapidfuzz | ❌ |
| **Guardrails** | ❌ | invariant-sdk + invariant-ai | ❌ |
| **HTTP Client** | (via fastmcp) | aiohttp | requests |
| **Packaging** | setuptools | hatchling | ❌ (source only) |
| **Package Manager** | pip | pip/uv/uvx | pip |
| **Model Size** | ~100s MB (torch) | N/A | N/A |
| **External APIs** | None (local) | Snyk verification | OpenAI/Groq |

---

## Detection Method Comparison

### Prompt Injection Detection

| Tool | Method | Privacy | Latency | Cost |
|------|--------|---------|---------|------|
| **mcp-checkpoint** | Local ML (Llama-based) | 100% private | Medium (local inference) | Free (after download) |
| **mcp-scan** | Cloud API (Snyk/Invariant) | Tool descriptions shared | Low (API call) | Free (for now) |
| **Proximity** | NOVA rules + LLM | Tool descriptions → LLM | High (LLM API) | Pay-per-use |

### Tool Poisoning Detection

| Tool | Method | Granularity |
|------|--------|-------------|
| **mcp-checkpoint** | Regex + ML on desc/name/args | High (multiple injection types) |
| **mcp-scan** | Cloud API + pattern matching | Medium (tool descriptions) |
| **Proximity** | NOVA rules (keywords/semantics/LLM) | Custom (user-defined) |

### Change Detection (Rug Pull)

| Tool | Method | Storage |
|------|--------|---------|
| **mcp-checkpoint** | Hash-based baseline files | Local JSON |
| **mcp-scan** | Hash-based whitelist | Local storage file (~/.mcp-scan) |
| **Proximity** | ❌ (no baseline support) | N/A |

---

## Use Case Decision Matrix

### Choose **mcp-checkpoint** if you need:
- ✅ **Regulatory compliance** (audit trails, timestamped baselines)
- ✅ **Offline/air-gapped** environments
- ✅ **Data privacy** (no external API calls)
- ✅ **Baseline management** (approved configurations)
- ✅ **Enterprise security** (Active Insight Mode)
- ✅ **Comprehensive static analysis** (12+ check types)

### Choose **mcp-scan** if you need:
- ✅ **Runtime monitoring** (live MCP traffic)
- ✅ **Guardrails** (policy enforcement on tool calls)
- ✅ **PII/Secrets detection** (data loss prevention)
- ✅ **HTTP/SSE server scanning** (remote MCP servers)
- ✅ **Development/staging protection** (proxy mode)
- ✅ **Toxic flow detection** (dangerous tool sequences)

### Choose **Proximity** if you need:
- ✅ **Custom threat hunting** (write your own detection rules)
- ✅ **Semantic analysis** (meaning-based detection)
- ✅ **Flexible LLM providers** (OpenAI, Groq)
- ✅ **Research & experimentation** (lightweight tool)
- ✅ **Jailbreak detection** (specialized NOVA rules)
- ✅ **Quick prototyping** (small codebase, easy to modify)

---

## Integration & Deployment Comparison

### Installation Complexity
| Tool | Complexity | Time | Notes |
|------|------------|------|-------|
| **mcp-checkpoint** | Medium | ~5 min + model download | Torch/transformers = large deps |
| **mcp-scan** | Low | <1 min | UVX makes it instant |
| **Proximity** | Low | <1 min | Lightweight deps, but NOVA needs API key |

### Configuration Complexity
| Tool | Complexity | Notes |
|------|------------|-------|
| **mcp-checkpoint** | Low | Auto-discovery works out-of-box |
| **mcp-scan** | Medium | Guardrails config requires YAML setup |
| **Proximity** | Medium-High | Must write NOVA `.nov` rule files |

### Operational Model
| Tool | Model | Notes |
|------|-------|-------|
| **mcp-checkpoint** | Scan-on-demand | Run periodically (CI/CD, cron, manual) |
| **mcp-scan** | Scan + continuous proxy | Proxy runs in background for dev |
| **Proximity** | Scan-on-demand | Research/ad-hoc scanning |

---

## Privacy & Data Sharing Comparison

| Tool | Data Shared Externally | Processing Location | Opt-Out |
|------|------------------------|---------------------|---------|
| **mcp-checkpoint** | None (after model download) | 100% local | N/A (no external calls) |
| **mcp-scan** (scan mode) | Tool names/descriptions | Cloud API (Snyk/Invariant) | `--opt-out` flag |
| **mcp-scan** (proxy mode) | None | 100% local | N/A (local-only) |
| **Proximity** (discovery) | None | 100% local | N/A |
| **Proximity** (NOVA mode) | Tool descriptions → LLM | OpenAI/Groq | Disable NOVA (`-n` flag) |

---

## Cost Comparison

| Tool | Base Cost | Additional Costs | Commercial Offering |
|------|-----------|------------------|---------------------|
| **mcp-checkpoint** | Free (OSS) | None (local compute) | Enterprise Edition (paid) |
| **mcp-scan** | Free (OSS) | None (for now) | Future commercial features |
| **Proximity** | Free (OSS) | LLM API usage (NOVA mode) | None |

### Proximity NOVA Cost Estimate
- **OpenAI GPT-4:** ~$0.03 per tool analyzed (varies)
- **Groq:** Lower cost, faster inference
- **Discovery mode:** $0 (no LLM calls)

---

## Maturity & Support Comparison

| Tool | Version | Maturity | Support | Community |
|------|---------|----------|---------|-----------|
| **mcp-checkpoint** | 2.0.0 | Production-ready | Slack community + enterprise | Active |
| **mcp-scan** | 0.3.30 | Stabilizing (closed to contributions) | GitHub issues | Active (commercial focus) |
| **Proximity** | 1.0.0 | Stable | GitHub issues, Twitter | Individual project |

---

## Architecture Comparison

### mcp-checkpoint Architecture
```
┌─────────────┐
│   CLI       │
├─────────────┤
│ Scanner     │ ← Auto-discovery
├─────────────┤
│ Connector   │ ← MCP STDIO client
├─────────────┤
│ Run Checks  │ ← 12+ security checks
├─────────────┤
│ Security    │
│ Utils       │ ← ML model (local)
│ (Prompt     │
│  Injection) │
├─────────────┤
│ Baseline    │ ← Hash-based drift
└─────────────┘
```

### mcp-scan Architecture
```
┌──────────────┐
│   CLI        │
├──────────────┤
│ MCPScanner   │ ← Auto-discovery
├──────────────┤
│ MCP Client   │ ← STDIO/HTTP/SSE
├──────────────┤
│ Verification │ ← Cloud API
│ API          │
├──────────────┤
│ Storage      │ ← Whitelist
└──────────────┘

Proxy Mode (separate):
┌───────────────┐
│ MCP Client    │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Invariant     │ ← Guardrails
│ Gateway       │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ MCP Server    │
└───────────────┘
```

### Proximity Architecture
```
┌─────────────┐
│   CLI       │
├─────────────┤
│ MCP Scanner │ ← HTTP/SSE/STDIO
│ Lib         │
├─────────────┤
│ NOVA        │ ← Rule engine
│ Evaluator   │
│ Lib         │
├─────────────┤
│ LLM API     │ ← OpenAI/Groq
└─────────────┘
```

---

## Limitations Summary

### mcp-checkpoint Limitations
- ❌ STDIO only (no HTTP/SSE in OSS)
- ❌ Large dependency footprint (torch/transformers)
- ❌ First run requires model download (~100s MB)
- ❌ No runtime monitoring (enterprise only)
- ❌ No custom rule DSL

### mcp-scan Limitations
- ❌ Scan mode requires internet (cloud API)
- ❌ Closed to external contributions
- ❌ Data sharing in scan mode (opt-out available)
- ❌ Proxy mode requires extra dependencies

### Proximity Limitations
- ❌ No baseline management
- ❌ NOVA requires LLM API keys (costs $$$)
- ❌ Manual rule creation (learning curve)
- ❌ No pip package (source-only)
- ❌ No auto-discovery
- ❌ Data sent to LLM providers (NOVA mode)

---

## Recommended Combinations

### Layered Security Approach
1. **CI/CD Pipeline:** mcp-checkpoint (baseline checks)
2. **Dev Environment:** mcp-scan proxy (runtime guardrails)
3. **Threat Hunting:** Proximity (custom NOVA rules)

### Minimum Viable Setup
- **Small team:** mcp-checkpoint (free, local, comprehensive)
- **Enterprise:** mcp-checkpoint Enterprise + mcp-scan proxy
- **Research:** Proximity (flexible, customizable)

---

## Conclusion

| Question | Answer |
|----------|--------|
| **Most comprehensive static scanner?** | mcp-checkpoint |
| **Best runtime protection?** | mcp-scan (proxy mode) |
| **Most customizable?** | Proximity (NOVA rules) |
| **Best for privacy?** | mcp-checkpoint (100% local) |
| **Best for remote servers?** | mcp-scan (HTTP/SSE support) |
| **Best for research?** | Proximity (lightweight, flexible) |
| **Best for enterprise?** | mcp-checkpoint Enterprise |
| **Best for development?** | mcp-scan (proxy + guardrails) |

**All three tools are complementary** - consider using multiple tools for defense-in-depth.
