# Product Requirements Document: SentraScan-RAG

## Introduction/Overview

This PRD describes the **SentraScan-RAG** module, a new security scanner for RAG (Retrieval-Augmented Generation) applications. RAG-based applications introduce new, non-traditional security risks that are not reliably detected by conventional SAST, secret scanners, or IaC tools.

**Problem Statement:** RAG applications face unique security challenges including unsafe prompt and context construction, weak retrieval isolation and tenant boundary violations, poisoned or malicious instructions inside vector databases, sensitive data embedded into vector stores without governance, excessive agent autonomy and unsafe tool invocation, and missing AI-specific governance evidence required by NIST AI RMF and regulated environments.

**Goal:** Provide a deterministic, offline scanner that can statistically analyze RAG code and configuration, optionally inspect actual vector database contents, and produce explainable, policy-mapped findings before deployment.

---

## Goals

1. **Detect RAG-Specific Security Issues:** Statically analyze RAG code and configuration to identify security vulnerabilities, misconfigurations, and governance gaps
2. **Provide Optional Data-Plane Scanning:** Support future read-only inspection of vector database contents (structure prepared in v1, implementation in future versions)
3. **Framework Alignment:** Map every finding to OWASP Top 10 for LLM Applications (2025), NIST AI Risk Management Framework, and MITRE ATLAS
4. **CI/CD Integration:** Support gating with low false positives for High and Critical findings
5. **Offline Operation:** Operate fully offline with no data exfiltration
6. **Platform Integration:** Seamlessly integrate with existing SentraScan Platform UI, API, and database infrastructure

---

## User Stories

1. **As an AI Engineer**, I want to scan my RAG application code before deployment so that I can identify and fix security issues early in development.

2. **As an AppSec Engineer**, I want RAG scans to detect prompt injection risks, tenant isolation violations, and unsafe tool invocations so that I can enforce security controls before production.

3. **As a Platform Engineer**, I want to validate RAG configurations and vector store security so that I can confidently deploy RAG services to production.

4. **As a Risk/GRC Lead**, I want findings mapped to OWASP LLM Top 10, NIST AI RMF, and MITRE ATLAS so that I can provide evidence for compliance and risk assessments.

5. **As a DevOps Engineer**, I want RAG scans to run in CI/CD pipelines with configurable gates so that insecure RAG applications are blocked from deployment.

6. **As a Security Analyst**, I want to see RAG findings in the same dashboard as MCP and Model scan findings so that I have a unified view of AI security risks.

7. **As a Developer**, I want the scanner to auto-detect RAG frameworks (LangChain, LlamaIndex, Haystack) so that I don't need to manually configure scan targets.

8. **As a Tenant Administrator**, I want RAG scan configurations to be tenant-scoped so that each organization can customize security policies for their RAG applications.

---

## Functional Requirements

### 1. Module Architecture and Integration

1. **Module Structure**
   - The system must implement SentraScan-RAG as a new module following the same architecture pattern as SentraScan-MCP and SentraScan-Model
   - The module must be located at `src/sentrascan/modules/rag/`
   - The module must include a `RAGScanner` class that follows the same interface pattern as `MCPScanner` and `ModelScanner`
   - **Interface Contract:** RAGScanner must implement:
     ```python
     class RAGScanner:
         def __init__(self, policy: PolicyEngine):
             """Initialize RAG scanner with policy engine"""
             
         def scan(
             self,
             target: str | List[str],  # Directory path or repo URL, or list of paths
             timeout: int = 300,
             db: Session,
             tenant_id: Optional[str] = None
         ) -> Scan:
             """
             Execute RAG scan and return Scan object.
             Must create Scan record with scan_type="rag"
             Must create Finding records with module="rag"
             """
             
         def to_report(self, scan: Scan) -> dict:
             """
             Generate scan report in standardized format.
             Must return dict with: scan_id, gate_result, findings, summary
             """
     ```

2. **Database Integration**
   - RAG scans must use the same `Scan` and `Finding` models as existing scanners
   - Scan records must have `scan_type="rag"` to distinguish from MCP and Model scans
   - **Database Schema Update Required:** The `Scan` model comment must be updated from `# 'mcp' or 'model'` to `# 'mcp', 'model', or 'rag'` in `src/sentrascan/core/models.py`
   - The `Baseline` model `baseline_type` comment must similarly be updated to include 'rag'
   - **Finding Module Field:** RAG findings must set `module="rag"` in Finding records (consistent with MCP using "mcp" and Model using "model")
   - Findings must be stored in the same `findings` table with appropriate categorization
   - All scans must be tenant-scoped using the existing `tenant_id` mechanism
   - No new database tables are required; existing schema supports RAG scans

3. **API Integration**
   - The system must add a new endpoint `/api/v1/rag/scans` for triggering RAG scans
   - The endpoint must accept both directory paths and repository URLs as scan targets
   - The endpoint must support the same authentication and authorization mechanisms as existing scan endpoints
   - The endpoint must return scan results in the same format as MCP and Model scans
   - **Request Format:**
     ```json
     POST /api/v1/rag/scans
     {
         "target": "path/to/rag/app" | "https://github.com/org/repo",
         "targets": ["path1", "path2"],  // Optional: multiple targets
         "policy": ".sentrascan.yaml",  // Optional
         "timeout": 300,                 // Optional, default 300
         "strict": false                 // Optional, default false
     }
     ```
   - **Response Format:**
     ```json
     {
         "scan_id": "uuid",
         "scan_type": "rag",
         "status": "completed",
         "gate_result": {
             "passed": true,
             "total_findings": 5,
             "critical_count": 0,
             "high_count": 2,
             "medium_count": 2,
             "low_count": 1
         },
         "findings": [...],
         "summary": {
             "frameworks_detected": ["langchain"],
             "analyzers_run": ["rag-rule", "rag-sast", "rag-langchain"],
             "analyzers_failed": [],
             "duration_ms": 45000,
             "partial_scan": false
         }
     }
     ```
   - **Error Responses:**
     - `400 Bad Request` - Invalid target path, invalid policy file, validation errors
     - `403 Forbidden` - RAG scanner disabled for tenant, insufficient permissions
     - `500 Internal Server Error` - Scanner failures, database errors
   - **Partial Results:** When analyzers fail, response must include `"partial_scan": true` flag

4. **UI Integration**
   - RAG scan findings must appear in the same findings dashboard as MCP and Model scans
   - The UI must support filtering findings by scanner type (including "rag")
   - The UI must display RAG-specific finding categories and metadata
   - The scan list view must show RAG scans alongside MCP and Model scans
   - **UI Template Updates Required:**
     - `src/sentrascan/web/templates/index.html` - Add "rag" option to scan type filter dropdown (line ~33-37)
     - `src/sentrascan/web/templates/scan_detail.html` - Update conditional checks to include `scan.scan_type == 'rag'` (line ~152)
       - Change: `{% if (scan.scan_type == 'model' or scan.scan_type == 'mcp') ... %}` 
       - To: `{% if (scan.scan_type == 'model' or scan.scan_type == 'mcp' or scan.scan_type == 'rag') ... %}`
     - `src/sentrascan/web/templates/findings_aggregate.html` - Ensure RAG scans display correctly in scan filter dropdown
     - `src/sentrascan/web/templates/dashboard.html` - Update scan type display to show "RAG" badge correctly
   - **UI Filter Update:**
     ```html
     <select id="filter_type" name="type" class="form-select">
       <option value="">All Types</option>
       <option value="model" {% if filters.type == 'model' %}selected{% endif %}>Model</option>
       <option value="mcp" {% if filters.type == 'mcp' %}selected{% endif %}>MCP</option>
       <option value="rag" {% if filters.type == 'rag' %}selected{% endif %}>RAG</option>
     </select>
     ```
   - **UI Verification:** All UI templates must be tested to ensure RAG scans display correctly in all views

5. **CLI Integration**
   - The system must add a new CLI command `sentrascan scan rag <target>` for triggering RAG scans
   - The command must support both local directory paths and repository URLs
   - The command must support the same flags as other scan commands (e.g., `--policy`, `--strict`, `--timeout`)

### 2. Scan Input and Target Discovery

6. **Input Types**
   - The system must support scanning local directories containing RAG code
   - The system must support scanning remote repositories via URL (GitHub, GitLab, etc.)
   - **SSRF Prevention:** The system must validate repository URLs to prevent SSRF attacks using shared utility functions
   - **Repository Cloning:** The system must clone repositories to cache directory `/cache/rag_repos/` (following MCP scanner pattern)
   - **Code Reuse:** Repository cloning and SSRF prevention logic must be extracted to shared `src/sentrascan/core/repo_utils.py`:
     - `is_allowed_repo_url(url: str) -> bool` - Validates URLs (allows only GitHub, HuggingFace)
     - `ensure_repo(url: str, cache_dir: str = "/cache/rag_repos", timeout: int = 180) -> Optional[str]` - Clones repos with depth=1
   - **Timeout:** Default repository cloning timeout is 180 seconds (configurable via tenant settings)
   - **Git Submodules:** Git submodules are not cloned (depth=1 prevents submodule inclusion)

7. **Auto-Detection of RAG Frameworks**
   - The system must implement a staged framework detection algorithm in `src/sentrascan/modules/rag/detection.py`:
     - **Stage 1 - Dependency File Detection:** Check `requirements.txt`, `pyproject.toml`, `package.json` for framework packages (HIGH confidence)
     - **Stage 2 - Import Statement Detection:** Parse Python files for import statements (MEDIUM confidence)
     - **Stage 3 - Pattern Detection:** Look for framework-specific patterns (e.g., `from langchain.retrievers import`) (MEDIUM confidence)
     - **Stage 4 - Configuration Detection:** Check configuration files for framework references (LOW confidence)
   - **Framework Detection Results:** Must return structured data:
     ```python
     {
         "langchain": {
             "detected": True,
             "confidence": "HIGH",
             "version": "0.1.0",  # if detectable
             "methods": ["dependency_file", "import_statement"]
         },
         "llama_index": {...},
         "haystack": {...}
     }
     ```
   - **Multiple Frameworks:** When multiple frameworks are detected, the system must run all applicable analyzers and tag findings with the framework that detected them
   - **Confidence Levels:** Confidence must be based on detection method (dependency file = HIGH, import = MEDIUM, pattern = LOW)
   - **Custom RAG Implementations:** The system must handle cases where no standard framework is detected (pattern-based detection only)

8. **Language Support**
   - The system must primarily scan Python code (primary target for v1)
   - The system must support scanning JavaScript/TypeScript RAG implementations using Semgrep JS/TS rulesets
   - The system must detect the programming language of scanned files and apply appropriate analysis rules

9. **File Type Scanning**
   - The system must scan Python source files (`.py`)
   - The system must scan prompt template files (`.txt`, `.md`, `.jinja`, `.yaml`, `.yml`)
   - The system must scan configuration files (`.yaml`, `.yml`, `.json`, `.toml`, `.env`)
   - The system must scan deployment files (`Dockerfile`, `docker-compose.yml`, Helm values, Terraform snippets)
   - The system must scan JavaScript/TypeScript files (`.js`, `.ts`, `.jsx`, `.tsx`) when RAG frameworks are detected

### 3. Static Analysis Requirements

#### 3.1 Prompt and Context Construction Analysis

10. **User Input in System Prompts**
    - The system must detect when user input is concatenated directly into system or developer prompts without proper delimiters
    - The system must flag patterns where user-controlled variables are inserted into prompt strings using string concatenation, f-strings, or `.format()`
    - The system must identify missing instruction vs data separation markers
    - Findings must be categorized as `RAG.PromptInjection.UserInputInSystemPrompt` with severity HIGH or CRITICAL

11. **Context Delimiter Detection**
    - The system must detect when retrieved context is appended to prompts without delimiters or quoting
    - The system must identify missing context delimiters (e.g., XML tags, special markers, clear boundaries)
    - The system must flag patterns where context and instructions are not clearly separated
    - Findings must be categorized as `RAG.PromptInjection.MissingContextDelimiters` with severity MEDIUM or HIGH

12. **Context Overflow Detection**
    - The system must detect absence of truncation or limits on context length
    - The system must flag patterns where context size is unbounded or exceeds reasonable limits (configurable threshold, default 8000 tokens)
    - The system must identify missing token counting or truncation logic
    - Findings must be categorized as `RAG.PromptInjection.ContextOverflow` with severity MEDIUM

13. **Secrets in Prompt Templates**
    - The system must detect hardcoded secrets or credentials in prompt template files
    - The system must flag API keys, passwords, tokens, or other sensitive data embedded in prompts
    - The system must integrate with existing secrets scanners (TruffleHog, Gitleaks) for comprehensive detection
    - Findings must be categorized as `RAG.Secrets.HardcodedInPrompts` with severity HIGH or CRITICAL

14. **Prompt Template Analysis**
    - The system must parse and analyze Jinja2, YAML, and Markdown prompt templates
    - The system must detect unsafe template patterns (e.g., direct user input interpolation)
    - The system must identify missing input validation or sanitization in templates
    - Findings must be categorized as `RAG.PromptInjection.UnsafeTemplate` with severity MEDIUM or HIGH

#### 3.2 Retriever and Tenant Isolation Analysis

15. **Metadata Filter Detection**
    - The system must detect similarity search operations without metadata or namespace filters using multi-level detection:
      - **Positive Patterns:** Detect good isolation (metadata filters present) → HIGH confidence, MEDIUM severity
      - **Negative Patterns:** Detect missing isolation (no filters) → MEDIUM/LOW confidence, MEDIUM severity (not CRITICAL)
      - **Context Analysis:** Consider framework, patterns, and code structure to adjust confidence
    - The system must identify vector database queries that lack tenant isolation mechanisms
    - The system must flag patterns where tenant identifiers are present in code but not enforced in queries
    - **Severity Assignment:** Findings must be categorized as `RAG.TenantIsolation.MissingMetadataFilters` with severity MEDIUM (not CRITICAL) unless explicit evidence of cross-tenant data access exists
    - **Confidence-Based Severity:** CRITICAL severity requires explicit evidence (e.g., shared index configuration, cross-tenant query patterns)
    - **False Positive Mitigation:** Use confidence levels to reduce false positives; missing isolation alone is not sufficient for CRITICAL severity

16. **Shared Vector Index Detection**
    - The system must detect when shared vector indexes are used across multiple tenants
    - The system must identify missing namespace or collection isolation mechanisms
    - The system must flag configurations where tenant data could be accessed across boundaries
    - Findings must be categorized as `RAG.TenantIsolation.SharedIndex` with severity CRITICAL

17. **Tenant Identifier Enforcement**
    - The system must detect when tenant identifiers are defined but not consistently used in retrieval operations
    - The system must identify missing tenant context propagation through the RAG pipeline
    - The system must flag patterns where tenant isolation is incomplete or bypassed
    - Findings must be categorized as `RAG.TenantIsolation.WeakEnforcement` with severity HIGH

18. **Cross-Source Retrieval Analysis**
    - The system must detect cross-source retrieval without trust tier enforcement
    - The system must identify missing source validation or trust boundaries
    - The system must flag patterns where untrusted sources are mixed with trusted sources
    - Findings must be categorized as `RAG.TenantIsolation.UnsafeCrossSource` with severity MEDIUM or HIGH

#### 3.3 Tool Invocation and Agent Control Analysis

19. **Direct LLM Output to Tool Calls**
    - The system must detect when LLM output is routed directly to tool calls without validation
    - The system must identify patterns where model responses are used as tool parameters without sanitization
    - The system must flag missing allow-lists or validation for tool invocations
    - Findings must be categorized as `RAG.AgentControl.UnvalidatedToolCall` with severity HIGH or CRITICAL

20. **Missing Tool Allow-Lists**
    - The system must detect absence of allow-lists for tools that can be invoked
    - The system must identify configurations where all available tools are accessible without restrictions
    - The system must flag missing tool permission or access control mechanisms
    - Findings must be categorized as `RAG.AgentControl.MissingAllowlist` with severity HIGH

21. **Dangerous Sink Detection**
    - The system must detect dangerous sinks reachable from model output:
      - `exec`, `eval`, `subprocess`, OS commands
      - File system write operations
      - Network requests (HTTP, database connections)
      - System configuration changes
    - The system must identify patterns where LLM output flows to these sinks without proper validation
    - Findings must be categorized as `RAG.AgentControl.DangerousSink` with severity CRITICAL

22. **Unbounded Agent Loops**
    - The system must detect unbounded agent loops without termination conditions
    - The system must identify missing iteration limits or timeout mechanisms
    - The system must flag patterns where agents could run indefinitely
    - Findings must be categorized as `RAG.AgentControl.UnboundedLoop` with severity MEDIUM or HIGH

23. **Output Handling Analysis**
    - The system must detect missing HTML escaping or sanitization for LLM output
    - The system must identify patterns where model responses are directly rendered without validation
    - The system must flag missing output encoding or filtering mechanisms
    - Findings must be categorized as `RAG.OutputHandling.UnsafeRendering` with severity MEDIUM

#### 3.4 Configuration and Secrets Analysis

24. **Hardcoded Secrets Detection**
    - The system must detect hardcoded API keys and vector database tokens in configuration files
    - The system must integrate with existing secrets scanners (TruffleHog, Gitleaks) for comprehensive detection
    - The system must flag secrets in code, config files, and environment variable defaults
    - Findings must be categorized as `RAG.Secrets.Hardcoded` with severity HIGH or CRITICAL

25. **Insecure Endpoints Detection**
    - The system must detect insecure endpoints (no TLS) in configuration
    - The system must identify HTTP endpoints where HTTPS should be used
    - The system must flag missing TLS verification or insecure SSL configurations
    - Findings must be categorized as `RAG.Configuration.InsecureEndpoint` with severity HIGH

26. **Debug Flags Detection**
    - The system must detect debug or unsafe flags enabled in production configurations
    - The system must identify development-only settings that should not be enabled in production
    - The system must flag verbose logging or debug modes that could expose sensitive information
    - Findings must be categorized as `RAG.Configuration.UnsafeFlags` with severity MEDIUM

27. **Missing Rate Limits**
    - The system must detect absence of rate limits and max token caps in configuration
    - The system must identify missing resource controls for API calls, token usage, or request throttling
    - The system must flag configurations without consumption limits
    - Findings must be categorized as `RAG.Configuration.MissingRateLimits` with severity MEDIUM

28. **Environment Variable Analysis**
    - The system must prefer environment variables over hardcoded values for sensitive configuration
    - The system must detect when environment variables are used correctly vs hardcoded values
    - The system must flag missing environment variable usage for API keys, tokens, and credentials
    - Findings must be categorized as `RAG.Configuration.EnvVarUsage` with severity LOW or MEDIUM

### 4. Rule Implementation

29. **Regex Pattern Rules**
    - The system must implement `RAGRuleScanner` class in `src/sentrascan/modules/rag/rules.py` following the MCP `RuleScanner` pattern
    - **Code Reuse:** The RAG RuleScanner must reuse file walking and exclusion logic from MCP RuleScanner pattern
    - Rules must be defined as Python code (similar to MCP `RISK_PATTERNS` list) for v1, with YAML support planned for future
    - Rules must support pattern matching across multiple file types (`.py`, `.js`, `.ts`, `.yaml`, `.yml`, `.json`, `.txt`, `.md`, `.jinja`)
    - **Pattern Format:** Each rule must include: `id`, `regex`, `severity`, `title`, `description`, `category`
    - **Scanner Name:** RAG RuleScanner findings must use scanner name `"sentrascan-rag-rule"` to distinguish from MCP rule scanner findings

30. **Semgrep Rules**
    - The system must implement `RAGSASTRunner` class in `src/sentrascan/modules/rag/sast.py` that extends or reuses `SASTRunner` logic
    - **Code Reuse:** RAGSASTRunner must extend `SASTRunner` from `src/sentrascan/modules/mcp/sast.py` to reuse Semgrep execution pattern
    - RAG-specific Semgrep rules must be located in `src/sentrascan/modules/rag/semgrep/` directory
    - Rules must cover Python and JavaScript/TypeScript code
    - Rules must be organized into rule packs (e.g., `rag-prompt-injection`, `rag-tenant-isolation`, `rag-agent-control`)
    - **Default Configs:** Must use standard Semgrep configs: `p/python`, `p/security-audit`, `p/injection` plus RAG-specific rules

31. **Custom Python Analyzers**
    - The system must implement custom Python analyzers in `src/sentrascan/modules/rag/analyzers/` directory
    - **AST Parsing:** Analyzers must use Python's built-in `ast` module (no new dependencies) to parse Abstract Syntax Trees
    - The system must create AST visitor classes for specific patterns:
      - `LangChainPromptAnalyzer` - Detects LangChain prompt construction issues
      - `LlamaIndexRetrieverAnalyzer` - Detects LlamaIndex retriever security issues
      - `HaystackAnalyzer` - Detects Haystack-specific patterns
    - **Data Flow Tracking:** Analyzers must trace data flow (user input → prompt → LLM) to detect injection risks
    - **Framework-Specific API Calls:** Analyzers must identify framework-specific API calls and their security implications
    - **Performance:** AST parsing is slower than regex; analyzers must skip files that don't match framework patterns to optimize performance
    - **Error Handling:** AST parsing errors must be handled gracefully; continue scanning with other analyzers if AST parsing fails
    - **Scanner Names:** AST analyzer findings must use framework-specific scanner names:
      - `"sentrascan-rag-langchain"` - LangChain AST analyzer findings
      - `"sentrascan-rag-llamaindex"` - LlamaIndex AST analyzer findings
      - `"sentrascan-rag-haystack"` - Haystack analyzer findings

32. **Rule Organization**
    - Rules must be organized into clearly named rule packs:
      - `rag-prompt-injection` - Prompt injection and context construction issues
      - `rag-tenant-isolation` - Tenant boundary and isolation violations
      - `rag-agent-control` - Agent autonomy and tool invocation issues
      - `rag-configuration` - Configuration and secrets issues
      - `rag-vector-db` - Vector database security patterns (for future data-plane scanning)
    - Rules must be versioned and shipped as part of a rule bundle
    - Rules must support enable/disable configuration per tenant

### 5. Finding Categories and Threat Mapping

33. **Finding Categories**
    - The system must use the following category structure for findings:
      - `RAG.PromptInjection.*` - Prompt injection and context construction issues
      - `RAG.TenantIsolation.*` - Tenant boundary violations
      - `RAG.AgentControl.*` - Agent autonomy and tool invocation issues
      - `RAG.OutputHandling.*` - Unsafe output handling
      - `RAG.Secrets.*` - Hardcoded secrets and credentials
      - `RAG.Configuration.*` - Configuration and security settings
      - `RAG.VectorDB.*` - Vector database security (for future data-plane scanning)
      - `RAG.SupplyChain.*` - Supply chain and dependency issues
      - `RAG.Governance.*` - Governance and compliance gaps

34. **OWASP LLM Top 10 Mapping**
    - Every finding must include OWASP LLM Top 10 (2025) mapping in evidence
    - The system must map findings to the following OWASP categories:
      - LLM01: Prompt Injection
      - LLM02: Insecure Output Handling
      - LLM03: Training Data Poisoning
      - LLM04: Model Denial of Service
      - LLM05: Supply Chain Vulnerabilities
      - LLM06: Sensitive Information Disclosure
      - LLM07: Insecure Plugin Design
      - LLM08: Excessive Agency
      - LLM09: Overreliance
      - LLM10: Model Theft
    - Evidence must include `owasp_llm_category` field with the appropriate category ID

35. **NIST AI RMF Mapping**
    - Every finding must include NIST AI Risk Management Framework mapping in evidence
    - The system must map findings to NIST AI RMF functions:
      - Govern (GOV) - Governance, policies, culture
      - Map (MAP) - Context and risk identification
      - Measure (MEA) - Testing, evaluation, validation
      - Manage (MAN) - Risk mitigation and controls
    - Evidence must include `nist_rmf_function` field with the appropriate function
    - Evidence must include `nist_rmf_category` field with specific category (e.g., "Security", "Reliability", "Privacy")

36. **MITRE ATLAS Mapping**
    - Every finding must include MITRE ATLAS (Adversarial Threat Landscape for AI Systems) mapping where applicable
    - The system must map findings to relevant MITRE ATLAS techniques and tactics
    - Evidence must include `mitre_atlas_technique` field with technique ID (e.g., "T1574", "T1059")
    - Evidence must include `mitre_atlas_tactic` field with tactic name (e.g., "Initial Access", "Execution")

37. **Severity Assignment**
    - Findings must be assigned severity levels: CRITICAL, HIGH, MEDIUM, LOW, INFO
    - Severity must be based on:
      - Potential impact (data breach, unauthorized access, system compromise)
      - Exploitability (ease of exploitation, prerequisites)
      - Scope (single tenant vs multi-tenant, isolated vs widespread)
    - Default severity mappings must be defined for each rule category

38. **Confidence Levels**
    - Findings must include confidence levels: HIGH, MEDIUM, LOW
    - Confidence must be based on:
      - Pattern match quality (exact match vs heuristic)
      - Context analysis (sufficient context vs limited context)
      - Framework detection (known framework vs pattern-based)
    - Evidence must include `confidence` field

### 6. Error Handling and Resilience

39. **Framework Parsing Errors**
    - The system must handle errors when parsing RAG frameworks gracefully
    - If a framework cannot be parsed (e.g., unknown LangChain version), the system must:
      - Continue scanning with available analyzers
      - Emit a warning in the scan report indicating partial analysis
      - Provide clear error messages to users about what was skipped
    - The system must not fail the entire scan due to framework parsing errors

40. **Partial Scan Results**
    - The system must support partial scan results when some analyzers fail
    - The system must clearly indicate in the scan report which analyzers completed successfully
    - The system must provide a confidence indicator based on which tools ran
    - The system must allow users to understand what was analyzed and what was skipped

41. **Large Codebase Handling**
    - The system must handle large codebases incrementally to avoid timeouts
    - The system must support configurable timeouts for individual analyzers
    - The system must process files in batches to manage memory usage
    - The system must provide progress indicators for long-running scans
    - The system must support resumable scans for very large repositories

42. **Error Reporting**
    - The system must log all errors with appropriate log levels (ERROR, WARNING)
    - The system must include error details in scan reports when analyzers fail
    - The system must provide actionable error messages to users
    - The system must not expose sensitive information in error messages

43. **Specific Error Handling Scenarios**
    - **Semgrep Not Available:** If Semgrep is not available, the system must skip SAST scanning, log a warning, and continue with other analyzers
    - **Secrets Scanners Fail:** If TruffleHog or Gitleaks fail, the system must log the error, skip that scanner, and continue with remaining analyzers
    - **Corrupted Repository Clones:** If repository cloning fails or produces corrupted files, the system must log the error, skip that repository, and continue with other targets
    - **Unsupported File Encodings:** If a file cannot be read due to encoding issues, the system must skip that file, log a warning, and continue scanning
    - **AST Parsing Errors:** If AST parsing fails for a file, the system must skip AST analysis for that file, log a warning, and continue with regex/pattern matching
    - **Framework Detection Failures:** If framework detection fails, the system must use pattern-based detection with LOW confidence and continue scanning
    - **Timeout Handling:** If an analyzer times out, the system must log the timeout, mark that analyzer as failed, and continue with other analyzers
    - **Memory Exhaustion:** If memory limits are reached, the system must skip remaining files, log the issue, and return partial results

### 7. Performance and Scalability

44. **Scan Performance**
    - The system must optimize scan performance to complete as quickly as possible
    - **Performance Targets:**
      - Small codebase (<100 files): <30 seconds
      - Medium codebase (<1000 files): <2 minutes
      - Large codebase (<10,000 files): <10 minutes
    - The system must use parallel processing with `ThreadPoolExecutor` (max_workers=4) for file analysis
    - The system must cache framework detection results to avoid redundant analysis
    - **File Size Limits:** Files larger than 1MB must be skipped for AST parsing (log warning, continue with regex only)

45. **Incremental Scanning**
    - The system must support incremental scanning for large codebases
    - The system must process files in batches (100 files per batch) to avoid memory exhaustion
    - The system must support checkpoint/resume functionality for very large scans (future enhancement)
    - The system must provide progress updates during long-running scans (log every 100 files processed)
    - **File Filtering:** The system must skip files that don't match framework patterns before AST parsing to improve performance

46. **Resource Management**
    - The system must manage memory usage efficiently (target: <2GB for typical scans)
    - The system must avoid loading entire codebases into memory at once
    - The system must clean up temporary files and caches after scans complete
    - The system must respect system resource limits
    - **AST Result Caching:** AST parsing results must be cached per file to avoid re-parsing during multiple analyzer passes

### 8. Integration with Existing Scanners and Code Reuse

**Shared Utilities:** The following utilities must be extracted to shared locations for reuse across all scanners:

- **Repository Utilities:** `src/sentrascan/core/repo_utils.py`
  - `is_allowed_repo_url(url: str) -> bool` - SSRF prevention
  - `ensure_repo(url: str, cache_dir: str, timeout: int) -> Optional[str]` - Repository cloning
  
- **Path Utilities:** `src/sentrascan/core/path_utils.py`
  - `clean_file_path(file_path: str) -> str` - Remove cache directory prefixes
  - `normalize_file_key(file_path: str) -> str` - Normalize paths for grouping
  
- **Secrets Scanners:** `src/sentrascan/core/secrets.py` (moved from `modules/mcp/secrets.py`)
  - `TruffleHogRunner` class
  - `GitleaksRunner` class
  
- **Reporting Utilities:** `src/sentrascan/core/reporting.py` (optional, for standardization)
  - `generate_scan_report(scan, findings, gate_result, summary) -> dict` - Standardized report format

46. **Secrets Scanner Integration**
    - **Code Reuse:** The system must reuse existing `TruffleHogRunner` and `GitleaksRunner` classes from `src/sentrascan/core/secrets.py` (moved from MCP module)
    - The system must run existing secrets scanners (TruffleHog, Gitleaks) on RAG codebases
    - The system must integrate secrets scanner findings into RAG scan reports
    - The system must deduplicate findings when the same secret is detected by multiple scanners
    - The system must categorize secrets findings appropriately (e.g., `RAG.Secrets.*`) while using the same detection engines as MCP scanner
    - **No Duplication:** RAG scanner must import and use the same secrets scanner classes; no code duplication allowed
    - **Scanner Names:** Secrets scanner findings must use existing scanner names:
      - `"sentrascan-trufflehog"` - TruffleHog findings (same as MCP)
      - `"sentrascan-gitleaks"` - Gitleaks findings (same as MCP)

47. **SAST Integration**
    - The system must leverage existing SAST capabilities (Semgrep) for general code security issues
    - The system must combine SAST findings with RAG-specific findings in unified reports
    - The system must avoid duplicate findings when the same issue is detected by multiple analyzers
    - The system must clearly distinguish RAG-specific findings from general SAST findings
    - **Scanner Names:** SAST findings must use scanner name `"sentrascan-rag-sast"` to distinguish from MCP SAST findings

### 9. Configuration Management and Tenant Settings

47. **Tenant Settings Integration**
    - The system must integrate with existing tenant settings system (`TenantSettings` model and `get_tenant_setting()` helper)
    - **Tenant Settings Schema Update Required:** The `scan_type` enum in `src/sentrascan/core/tenant_settings.py` must be updated from `["mcp", "model"]` to `["mcp", "model", "rag"]` to support RAG scan schedules
    - **Tenant Settings Structure:**
      ```python
      {
          "scanner": {
              "enabled_scanners": ["mcp", "model", "rag"],  # Enable/disable RAG scanner per tenant
              "scanner_timeouts": {
                  "rag_timeout": 300  # RAG-specific timeout (default: 300 seconds)
              }
          },
          "rag": {
              "enabled_rule_packs": ["rag-prompt-injection", "rag-tenant-isolation"],  # Per-tenant rule pack control
              "scan_mode": "static",  # static | dataplane | hybrid (dataplane for future)
              "severity_threshold": "HIGH",  # Per-tenant severity threshold
              "confidence_threshold": "MEDIUM"  # Minimum confidence level to report
          }
      }
      ```
    - The RAG scanner must check `scanner.enabled_scanners` to determine if RAG scanning is enabled for the tenant
    - The RAG scanner must use `scanner.scanner_timeouts.rag_timeout` for scan timeouts (fallback to default 300 seconds)
    - The RAG scanner must respect `rag.enabled_rule_packs` to enable/disable specific rule packs per tenant
    - Tenant settings must be validated on save to ensure correct structure

48. **Configuration File Support**
    - **Primary Configuration:** The system must use `.sentrascan.yaml` with `rag:` section (consistent with existing `model:` and `mcp:` sections)
    - **No Alternative Configuration:** The system does NOT support `ragscan.yml` in v1 to maintain consistency with existing configuration pattern
    - **Configuration Structure:** The `rag:` section must use a **flat structure** (no nested `scan:` section) to match the pattern used by `model:` and `mcp:` sections:
      ```yaml
      rag:
        severity_threshold: HIGH
        block_issues:
          - RAG.PromptInjection.UserInputInSystemPrompt
          - RAG.TenantIsolation.SharedIndex
          - RAG.AgentControl.DangerousSink
        # RAG-specific configuration options (flat structure, no nested 'scan:')
        # Detailed settings (prompt_analysis, retriever, etc.) are in tenant settings
      ```
    - **PolicyEngine Integration:** The system must extend `PolicyEngine.from_file()` to parse `rag:` section (flat structure only):
      ```python
      if "rag" in data:
          pol = data["rag"]
          return PolicyEngine("rag", Policy(
              pol.get("severity_threshold", "HIGH"),
              pol.get("block_issues", []),
              pol.get("rag_requirements")  # RAG-specific requirements (optional)
          ), tenant_id=tenant_id, db=db)
      ```
    - **Default Policy:** The system must add `PolicyEngine.default_rag()` static method:
      ```python
      @staticmethod
      def default_rag(tenant_id: Optional[str] = None, db: Optional[Session] = None):
          return PolicyEngine("rag", Policy("HIGH", ["RAG.PromptInjection.*", "RAG.TenantIsolation.*", "RAG.AgentControl.DangerousSink"]), tenant_id=tenant_id, db=db)
      ```
    - Configuration must be tenant-scoped and support per-tenant customization
    - Configuration must support enabling/disabling specific rule packs (via tenant settings)
    - Configuration must support severity threshold customization

49. **Policy Integration**
    - The system must integrate with the existing PolicyEngine for scan gating
    - The system must support policy-based pass/fail criteria for RAG scans
    - The system must support severity-based blocking (e.g., fail on HIGH or CRITICAL findings)
    - The system must support category-based blocking (e.g., fail on specific RAG categories)

50. **Data-Plane Configuration (Future Support)**
    - Data-plane scanning configuration is NOT included in `.sentrascan.yaml` in v1 (out of scope)
    - Data-plane configuration will be added in future PRD when data-plane scanning is implemented
    - The code structure must be designed to support future data-plane scanning implementation
    - Configuration structure for data-plane scanning will be defined in future PRD

### 10. Reporting and Output

51. **Report Formats**
    - The system must support JSON output format (same as existing scanners)
    - The system must support SARIF output format for CI/CD integration
    - The system must support Markdown and HTML report formats
    - The system must integrate reports into the existing web UI

52. **Finding Evidence**
    - **Standardized Evidence Schema:** Each finding must use a standardized evidence schema defined in `src/sentrascan/core/evidence.py`:
      ```python
      {
          # Required fields
          "owasp_llm_category": "LLM01",      # Required: OWASP LLM Top 10 category
          "nist_rmf_function": "MAN",          # Required: NIST AI RMF function (GOV, MAP, MEA, MAN)
          "nist_rmf_category": "Security",     # Required: NIST category (Security, Reliability, Privacy, etc.)
          "confidence": "HIGH",                # Required: Confidence level (HIGH, MEDIUM, LOW)
          "rule_id": "RAG-PI-001",            # Required: Unique rule identifier
          
          # Optional fields
          "mitre_atlas_technique": "T1574",   # Optional: MITRE ATLAS technique ID
          "mitre_atlas_tactic": "Execution",  # Optional: MITRE ATLAS tactic name
          "framework": "langchain",           # Optional: Framework that detected the issue
          "detection_method": "ast_analysis", # Optional: Detection method used
          
          # Additional evidence fields (rule-specific)
          "pattern_match": "...",             # Optional: Matched pattern
          "code_snippet": "...",              # Optional: Code snippet showing issue
          "file_path": "...",                 # Optional: File path
          "line_number": 42,                  # Optional: Line number
      }
      ```
    - **Evidence Builder:** The system must provide an `EvidenceBuilder` utility class to construct evidence objects with validation
    - Each finding must include:
      - Rule ID (unique identifier for the rule)
      - Title (human-readable finding title)
      - Description (detailed explanation of the issue)
      - Severity (CRITICAL, HIGH, MEDIUM, LOW, INFO)
      - Confidence (HIGH, MEDIUM, LOW)
      - Location (file path, line number, code snippet)
      - Evidence (detailed evidence following standardized schema)
      - OWASP LLM Top 10 mapping (in evidence)
      - NIST AI RMF mapping (in evidence)
      - MITRE ATLAS mapping (in evidence, where applicable)
      - Remediation guidance (actionable steps to fix the issue)

53. **Scan Summary**
    - The system must provide a scan summary including:
      - Total findings count by severity
      - Findings count by category
      - Framework detection results (which frameworks detected, confidence levels)
      - Analyzers that ran successfully (list of analyzers executed)
      - Analyzers that failed (list of analyzers that encountered errors)
      - Scan duration and performance metrics
      - Confidence indicator based on analyzers executed (LOW/MEDIUM/HIGH based on number of analyzers that ran)
      - Partial scan indicator (if any analyzers failed)

54. **Logging and Observability**
    - The system must use `structlog` for structured logging (consistent with MCP scanner pattern)
    - **Log Levels:**
      - **INFO:** Scan start/end, framework detection results, analyzer execution, findings count
      - **DEBUG:** Detailed execution flow, intermediate states, pattern matches
      - **WARNING:** Framework detection failures, analyzer timeouts, partial scan results
      - **ERROR:** Analyzer failures, repository cloning errors, critical errors
    - **Structured Log Fields:**
      - `scan_id` - Scan identifier
      - `scan_type` - Always "rag"
      - `tenant_id` - Tenant identifier
      - `framework_detected` - List of detected frameworks
      - `analyzers_run` - List of analyzers that executed
      - `analyzers_failed` - List of analyzers that failed
      - `findings_count` - Total findings count
      - `duration_ms` - Scan duration in milliseconds
    - **Performance Logging:** The system must log performance metrics:
      - Framework detection time
      - Per-analyzer execution time
      - Total scan duration
      - Memory usage (if available)

### 11. Testing Requirements

55. **Unit Testing Requirements**
    - **Framework Detection Tests** (`tests/test_rag_detection.py`):
      - Test LangChain detection from requirements.txt
      - Test LlamaIndex detection from import statements
      - Test detection when multiple frameworks present
      - Test detection of custom RAG implementations
      - Test confidence level assignment
    - **Rule Scanner Tests** (`tests/test_rag_rules.py`):
      - Test prompt injection detection
      - Test missing context delimiters detection
      - Test tenant isolation detection
      - Test agent control detection
    - **AST Analyzer Tests** (`tests/test_rag_analyzers.py`):
      - Test LangChain-specific prompt analysis
      - Test LlamaIndex retriever analysis
      - Test data flow tracking
      - Test AST parsing error handling
    - **Integration Tests** (`tests/test_rag_integration.py`):
      - Test secrets scanner integration (TruffleHog, Gitleaks)
      - Test SAST integration (Semgrep)
      - Test policy engine integration
      - Test tenant settings integration

56. **Integration Testing Requirements**
    - **End-to-End Scan Tests** (`tests/integration/test_rag_scan_e2e.py`):
      - Test full scan of LangChain RAG application
      - Test full scan of LlamaIndex RAG application
      - Test scan when multiple frameworks present
      - Test scan of custom RAG implementation
    - **API Integration Tests** (`tests/integration/test_rag_api.py`):
      - Test POST `/api/v1/rag/scans` endpoint
      - Test RAG scan with policy enforcement
      - Test tenant-scoped RAG scans
      - Test error handling in API
      - Test request/response format validation
      - Test partial scan results when analyzers fail
    - **CLI Integration Tests** (`tests/integration/test_rag_cli.py`):
      - Test `sentrascan scan rag` CLI command
      - Test CLI with `--policy`, `--timeout` options
      - Test CLI error handling
    - **UI Integration Tests** (`tests/integration/test_rag_ui.py`):
      - Test RAG scan type appears in filter dropdown
      - Test RAG scans display in scan list
      - Test RAG scan detail page renders correctly
      - Test RAG findings appear in findings dashboard
      - Test filtering findings by RAG scanner type
      - Test scan type badges display "RAG" correctly
    - **Tenant Settings Integration Tests** (`tests/integration/test_rag_tenant_settings.py`):
      - Test enabling/disabling RAG scanner per tenant
      - Test RAG-specific tenant settings configuration
      - Test tenant settings validation accepts "rag" scan_type
      - Test RAG scan schedules with tenant settings
    - **Analytics Integration Tests** (`tests/integration/test_rag_analytics.py`):
      - Test analytics grouping by scan_type="rag"
      - Test dashboard statistics include RAG scan counts
      - Test reports include RAG scan data correctly

57. **Test Data Requirements**
    - **LangChain RAG Application (Vulnerable)** - `tests/fixtures/rag_apps/langchain_vulnerable/`
      - Contains: User input in system prompt, missing context delimiters, missing tenant isolation, hardcoded secrets
      - Expected findings: 5+ CRITICAL, 10+ HIGH
    - **LlamaIndex RAG Application (Vulnerable)** - `tests/fixtures/rag_apps/llamaindex_vulnerable/`
      - Similar structure to LangChain fixture
    - **Secure RAG Application (Baseline)** - `tests/fixtures/rag_apps/secure/`
      - Contains best practices
      - Expected findings: 0 CRITICAL, 0 HIGH, <5 MEDIUM/LOW
    - **Multi-Framework RAG Application** - `tests/fixtures/rag_apps/mixed/`
      - Contains both LangChain and LlamaIndex
      - Tests framework detection with multiple frameworks
    - **Large Codebase (Performance Testing)** - `tests/fixtures/rag_apps/large/`
      - 10,000+ files
      - Tests incremental scanning and performance

58. **Performance Testing Requirements**
    - **Performance Tests** (`tests/performance/test_rag_performance.py`):
      - Test scan time for <100 files (<30 seconds)
      - Test scan time for <1000 files (<2 minutes)
      - Test scan time for <10,000 files (<10 minutes)
      - Test memory usage doesn't exceed 2GB
      - Test parallel processing improves performance

59. **False Positive Validation**
    - **Validation Tests** (`tests/validation/test_rag_false_positives.py`):
      - Test secure RAG app produces no false positives
      - Test HIGH confidence findings are accurate
      - Manually validate all CRITICAL findings are real issues
      - Test false positive rate <10% for HIGH and CRITICAL findings

### 12. Supported Technologies (v1)

60. **RAG Frameworks**
    - The system must support scanning LangChain-based RAG applications
    - The system must support scanning LlamaIndex-based RAG applications
    - The system must support pattern-based detection for Haystack RAG applications
    - The system must be extensible to support additional frameworks in future versions

61. **Vector Databases (Detection Only in v1)**
    - The system must detect usage of the following vector databases in code/config:
      - Chroma
      - Weaviate
      - Pinecone
      - Milvus
      - pgvector (Postgres)
    - The system must identify vector database connection patterns and configurations
    - The system must prepare code structure for future data-plane scanning of these databases

62. **Programming Languages**
    - The system must primarily support Python (primary target for v1)
    - The system must support JavaScript/TypeScript RAG implementations using Semgrep
    - The system must be extensible to support additional languages in future versions

---

## Non-Goals (Out of Scope)

1. **No Data-Plane Scanning in v1**
   - This PRD explicitly excludes actual data-plane scanning of vector database contents in v1
   - Code structure and configuration must support future data-plane scanning, but implementation is deferred
   - Vector database content analysis (PII detection, injection artifacts, etc.) is out of scope for v1

2. **No Runtime Red Teaming**
   - The scanner will not perform runtime red teaming or live LLM exploitation
   - The scanner will not execute prompts or interact with live RAG systems
   - All analysis must be static (code and configuration only)

3. **No Automated Remediation**
   - The scanner will not automatically fix or remediate findings
   - The scanner will not delete or modify vector database records
   - The scanner provides findings and guidance only

4. **No Semantic Truthfulness Analysis**
   - The scanner will not evaluate semantic truthfulness or hallucination in RAG outputs
   - The scanner will not score retrieval quality or accuracy
   - The scanner focuses on security and governance, not content quality

5. **No Full Regulatory Certification**
   - The scanner provides evidence mapping to frameworks but does not claim full regulatory certification
   - The scanner supports compliance efforts but does not guarantee compliance
   - Users are responsible for interpreting findings in the context of their regulatory requirements

6. **No LLM-Based Analysis**
   - The scanner will not use LLMs to analyze code or generate findings
   - All analysis must be deterministic and rule-based
   - The scanner must operate fully offline without external API dependencies

---

## Design Considerations

1. **Rule Pack Organization**
   - Rules must be organized into clearly named rule packs for maintainability
   - Rule packs must be versioned and shipped as part of a rule bundle
   - Rule packs must support enable/disable configuration per tenant

2. **False Positive Control**
   - Rules must be tuned to minimize false positives, especially for HIGH and CRITICAL findings
   - Rules with higher false positive risk should default to MEDIUM or LOW severity
   - The system must support rule tuning and customization per tenant

3. **Extensibility**
   - The code structure must support adding new RAG frameworks easily
   - The code structure must support adding new rule packs without major refactoring
   - The code structure must prepare for future data-plane scanning implementation

4. **Finding Deduplication**
   - The system must deduplicate findings when the same issue is detected by multiple analyzers
   - Deduplication must be based on `(engine, rule_id, file:line)` or equivalent
   - The system must clearly indicate when findings are merged from multiple sources

5. **Backward Compatibility**
   - New RAG-specific categories must be additive to existing categories
   - Evidence fields (OWASP, NIST, MITRE mappings) must be additive and safe for existing consumers
   - API changes must maintain backward compatibility with existing scan consumers

---

## Technical Considerations

1. **Integration Points**
   - Most work will occur in `src/sentrascan/modules/rag/scanner.py` (new file)
   - Framework detection in `src/sentrascan/modules/rag/detection.py` (new file)
   - Rules will be organized in `src/sentrascan/modules/rag/rules.py` (new file)
   - Custom analyzers will be in `src/sentrascan/modules/rag/analyzers/` directory (new directory)
   - Semgrep rules will be in `src/sentrascan/modules/rag/semgrep/` directory (new directory)
   - SAST runner in `src/sentrascan/modules/rag/sast.py` (new file, extends MCP SASTRunner)

2. **Shared Utilities (Code Reuse)**
   - **Repository Utilities:** Extract to `src/sentrascan/core/repo_utils.py` (new file)
     - `is_allowed_repo_url()` - SSRF prevention
     - `ensure_repo()` - Repository cloning
   - **Path Utilities:** Extract to `src/sentrascan/core/path_utils.py` (new file)
     - `clean_file_path()` - Remove cache prefixes
     - `normalize_file_key()` - Normalize paths
   - **Secrets Scanners:** Move to `src/sentrascan/core/secrets.py` (move from `modules/mcp/secrets.py`)
     - `TruffleHogRunner` class
     - `GitleaksRunner` class
   - **Evidence Builder:** Create `src/sentrascan/core/evidence.py` (new file)
     - `EvidenceBuilder` class for standardized evidence construction

3. **Dependencies**
   - The module must reuse existing platform dependencies (no new major dependencies for v1)
   - The module must use Python's built-in `ast` module for AST parsing (no external dependencies)
   - The module must use existing Semgrep integration for SAST scanning
   - The module must use existing secrets scanner integrations (TruffleHog, Gitleaks)
   - **No tree-sitter:** Use `ast` module only for v1; tree-sitter for multi-language support is future enhancement

4. **Database Schema Updates Required**
   - Update `Scan.scan_type` comment in `src/sentrascan/core/models.py`: `# 'mcp', 'model', or 'rag'`
   - Update `Baseline.baseline_type` comment similarly: `# 'mcp', 'model', or 'rag'`
   - No new database tables required (uses existing `scans` and `findings` tables)
   - Scan records must use `scan_type="rag"` to distinguish from other scan types
   - Findings must use appropriate category prefixes (`RAG.*`)

5. **PolicyEngine Updates Required**
   - Add `PolicyEngine.default_rag()` static method in `src/sentrascan/core/policy.py`
   - Extend `PolicyEngine.from_file()` to parse `rag:` section in `.sentrascan.yaml` (flat structure, no nested sections)
   - Only `.sentrascan.yaml` is supported (no `ragscan.yml` alternative in v1)

6. **Tenant Settings Updates Required**
   - Update `scan_type` enum in `src/sentrascan/core/tenant_settings.py` from `["mcp", "model"]` to `["mcp", "model", "rag"]`
   - This enables RAG scan schedules and tenant settings validation

7. **Telemetry Updates Required**
   - Update `capture_scan_event()` function documentation in `src/sentrascan/core/telemetry.py` (line ~131-144) to include "rag" scan type
   - Update type hints and comments to reflect all three scan types: "model", "mcp", "rag"
   - Change: `scan_type: str,  # "model", "mcp"` to `scan_type: str,  # "model", "mcp", or "rag"`
   - Update docstring: `scan_type: Type of scan (model, mcp).` to `scan_type: Type of scan (model, mcp, or rag).`

8. **Analytics Updates Required**
   - Review `src/sentrascan/core/analytics.py` for hardcoded scan_type assumptions
   - Ensure analytics handle "rag" scan type correctly in all grouping and aggregation operations
   - Verify `group_by_scan_type()` includes RAG scans
   - Update dashboard statistics to include RAG scan counts
   - Review `src/sentrascan/web/templates/dashboard.html` to ensure RAG stats display
   - Review `src/sentrascan/web/static/js/analytics.js` for scan type assumptions
   - Analytics must treat "rag" scan type the same as "mcp" and "model" (no special handling needed if using generic grouping)

9. **API Endpoints**
   - New endpoint: `POST /api/v1/rag/scans` - Trigger RAG scan
     - Request body: `{"target": "path", "policy": "...", "timeout": 300, "strict": false}`
     - Response: Standard scan report format with `scan_type="rag"`
     - Error codes: 400 (validation), 403 (disabled/unauthorized), 500 (server error)
   - New endpoint: `GET /api/v1/rag/scans/{id}` - Get RAG scan results (reuses existing scan endpoint)
   - Endpoints must follow the same authentication and authorization patterns as existing scan endpoints
   - Endpoints must check `scanner.enabled_scanners` tenant setting to verify RAG scanner is enabled
   - Endpoints must return partial scan results with `partial_scan: true` flag when analyzers fail

10. **CLI Commands**
   - New command: `sentrascan scan rag <target> [options]`
   - Command must support same options as other scan commands (`--policy`, `--strict`, `--timeout`, etc.)
   - Command must support both directory paths and repository URLs
   - Command must use `PolicyEngine.default_rag()` if no policy file specified

11. **Performance Optimization and Resource Allocation**
   - Use parallel processing with `ThreadPoolExecutor` (max_workers=4) for file analysis
   - Cache framework detection results to avoid redundant analysis
   - Cache AST parsing results per file to avoid re-parsing
   - Implement incremental scanning for large codebases (100 files per batch)
   - Skip files larger than 1MB for AST parsing
   - Skip files that don't match framework patterns before AST parsing
   - **CPU Usage:** AST parsing is CPU-intensive; parallel processing limited to 4 workers to prevent CPU exhaustion
   - **Memory Target:** <2GB per scan (as specified in performance metrics)
   - **CPU Throttling:** Consider throttling AST parsing for large codebases to prevent system resource exhaustion
   - **Resource Limits:** RAG scans must respect system resource limits and not monopolize CPU/memory

12. **Concurrent Scan Limits**
   - RAG scans use the same job queue as MCP/Model scans (no separate queue)
   - RAG scans count toward concurrent scan limits (same as other scan types)
   - No special priority for RAG scans (first-come-first-served processing)
   - RAG scans compete for resources with MCP and Model scans fairly

13. **Error Handling**
   - Implement graceful degradation when analyzers fail
   - Provide clear error messages and partial results
   - Log errors appropriately using structlog
   - Support resumable scans for large repositories (future enhancement)
   - Handle specific error scenarios (see requirement 43)

10. **Input Validation and Security**
    - **Path Validation:** Validate local paths to prevent directory traversal attacks
      - Use `os.path.abspath()` and `os.path.commonpath()` to prevent path traversal
      - Validate paths are within allowed directories
    - **File Size Limits:** Limit individual file size (1MB for AST parsing, larger for regex-only analysis)
      - Files >1MB must be skipped for AST parsing (log warning, continue with regex only)
      - Files >10MB must be skipped entirely (log warning)
    - **Repository Size Limits:** Limit total repository size (configurable via tenant settings, default 1GB)
      - Reject repositories larger than limit before cloning
      - Log warning if repository exceeds limit after cloning
    - **File Count Limits:** Limit number of files per scan (configurable via tenant settings, default 10,000 files)
      - Stop scanning after reaching file count limit
      - Log warning indicating partial scan due to file count limit
    - **Secrets Redaction:** Redact actual secret values from findings evidence (keep type/location, not value)
      - Redact `pattern_match` field if it contains secret values
      - Redact `code_snippet` field if it contains secret values
      - Keep secret type (e.g., "API_KEY", "PASSWORD") and location
    - **Report Redaction:** Apply redaction to JSON, SARIF, and HTML report formats
      - Use consistent redaction marker: `"[REDACTED]"` or `"***REDACTED***"`
      - Redaction must be applied before report generation
    - **Redaction Marking:** Clearly mark redacted fields in output
      - Add `redacted: true` flag to evidence when content is redacted
      - Include redaction reason in evidence (e.g., `redaction_reason: "contains_secret"`)

11. **Baseline and SBOM Support**
    - **Baseline Support:** RAG scans do NOT support baseline creation/drift detection in v1 (out of scope)
    - Baseline support may be added in future versions if needed
    - Code structure should support future baseline support (Baseline model already supports baseline_type="rag")
    - **SBOM Generation:** RAG scans do NOT generate SBOMs in v1 (SBOM generation is model-specific)
    - SBOM generation for RAG may be considered in future if dependency tracking is needed
    - RAG scans do not set `sbom_id` field in Scan records (leave as NULL)

---

## Success Metrics

1. **Coverage Metrics**
   - The scanner must detect at least 80% of known RAG security patterns from the reference document
   - The scanner must successfully auto-detect RAG frameworks in 90% of test cases
   - The scanner must map 100% of findings to OWASP LLM Top 10 categories
   - The scanner must map 100% of findings to NIST AI RMF functions

2. **Accuracy Metrics**
   - False positive rate for HIGH and CRITICAL findings must be less than 10%
   - False negative rate for known RAG security issues must be less than 20%
   - Confidence levels must accurately reflect detection quality

3. **Performance Metrics**
   - Typical scan time for medium codebase (< 1000 files) must be under 2 minutes
   - Large codebase scans (< 10,000 files) must complete within 10 minutes
   - Memory usage must not exceed 2GB for typical scans

4. **Integration Metrics**
   - RAG scans must integrate seamlessly with existing UI, API, and database
   - Findings must appear correctly in the unified findings dashboard
   - Policy-based gating must work correctly for RAG scans
   - CLI and API must provide consistent results

5. **User Experience Metrics**
   - Users must be able to trigger RAG scans via CLI, API, and UI
   - Scan reports must be clear and actionable
   - Remediation guidance must be helpful and specific
   - Error messages must be informative and actionable

---

## Open Questions (Resolved)

1. **Rule Bundle Versioning** ✅ RESOLVED
   - **Decision:** Use the same rule bundle versioning mechanism as existing scanners, with rule bundles shipped as part of platform releases initially.

2. **Framework Detection Confidence** ✅ RESOLVED
   - **Decision:** Run all applicable analyzers when multiple frameworks are detected, with findings tagged with the framework that detected them. Use staged detection algorithm with confidence levels.

3. **Data-Plane Scanning Timeline** ✅ RESOLVED
   - **Decision:** Defer to future PRD, but ensure code structure supports it clearly. Configuration structure is defined in PRD.

4. **MITRE ATLAS Coverage** ✅ RESOLVED
   - **Decision:** Include MITRE ATLAS mappings where applicable, but don't force mappings for all findings. Focus on techniques relevant to RAG security. MITRE fields are optional in evidence schema.

5. **Tenant Isolation Detection Precision** ✅ RESOLVED
   - **Decision:** Use multi-level detection with confidence-based severity. Missing isolation defaults to MEDIUM severity (not CRITICAL). Require explicit evidence for CRITICAL findings.

6. **Performance vs. Coverage Trade-offs** ✅ RESOLVED
   - **Decision:** Optimize for both, with incremental scanning for large codebases and parallel processing where possible. Provide progress indicators for long-running scans. Performance targets defined.

7. **Configuration File Format** ✅ RESOLVED
   - **Decision:** Use `.sentrascan.yaml` with `rag:` section for consistency. No `ragscan.yml` alternative in v1 to maintain consistency with existing pattern.

8. **Evidence Field Structure** ✅ RESOLVED
   - **Decision:** Use standardized evidence schema with required fields (OWASP, NIST) and optional fields (MITRE). Create EvidenceBuilder utility class.

---

## Appendix

### A. Reference Configuration Example

**Primary Configuration (`.sentrascan.yaml` - Flat Structure):**

```yaml
version: 1

rag:
  severity_threshold: HIGH
  block_issues:
    - RAG.PromptInjection.UserInputInSystemPrompt
    - RAG.TenantIsolation.SharedIndex
    - RAG.AgentControl.DangerousSink
  
  # RAG-specific configuration (flat structure, consistent with model: and mcp: sections)
  # Note: Detailed scan configuration (prompt_analysis, retriever, etc.) is handled via
  # rule packs and tenant settings, not in policy file
  # This structure matches the pattern used by model: and mcp: sections
```

**Note on Configuration Structure:**
- The primary configuration uses `.sentrascan.yaml` with flat `rag:` section (consistent with `model:` and `mcp:` sections)
- Alternative `ragscan.yml` file format is NOT supported in v1 to maintain consistency
- All RAG configuration must use `.sentrascan.yaml` with `rag:` section
- Detailed scan settings (prompt_analysis, retriever, etc.) are configured via tenant settings, not policy files

### B. Finding Category Reference

| Category | Description | Default Severity |
|----------|-------------|------------------|
| `RAG.PromptInjection.UserInputInSystemPrompt` | User input concatenated into system prompts | CRITICAL |
| `RAG.PromptInjection.MissingContextDelimiters` | Missing delimiters between context and instructions | HIGH |
| `RAG.PromptInjection.ContextOverflow` | Unbounded context size | MEDIUM |
| `RAG.PromptInjection.UnsafeTemplate` | Unsafe prompt template patterns | MEDIUM |
| `RAG.TenantIsolation.MissingMetadataFilters` | Missing metadata filters in retrieval | MEDIUM (CRITICAL only with explicit evidence) |
| `RAG.TenantIsolation.SharedIndex` | Shared vector index across tenants | CRITICAL |
| `RAG.TenantIsolation.WeakEnforcement` | Weak tenant identifier enforcement | HIGH |
| `RAG.TenantIsolation.UnsafeCrossSource` | Unsafe cross-source retrieval | HIGH |
| `RAG.AgentControl.UnvalidatedToolCall` | LLM output used directly in tool calls | CRITICAL |
| `RAG.AgentControl.MissingAllowlist` | Missing tool allow-list | HIGH |
| `RAG.AgentControl.DangerousSink` | Dangerous sinks reachable from LLM output | CRITICAL |
| `RAG.AgentControl.UnboundedLoop` | Unbounded agent loops | HIGH |
| `RAG.OutputHandling.UnsafeRendering` | Unsafe output rendering | MEDIUM |
| `RAG.Secrets.Hardcoded` | Hardcoded secrets in code/config | CRITICAL |
| `RAG.Secrets.HardcodedInPrompts` | Secrets in prompt templates | CRITICAL |
| `RAG.Configuration.InsecureEndpoint` | Insecure endpoints (no TLS) | HIGH |
| `RAG.Configuration.UnsafeFlags` | Debug/unsafe flags enabled | MEDIUM |
| `RAG.Configuration.MissingRateLimits` | Missing rate limits | MEDIUM |
| `RAG.Configuration.EnvVarUsage` | Missing environment variable usage | LOW |

### C. OWASP LLM Top 10 Mapping Reference

| OWASP Category | RAG Finding Categories |
|----------------|----------------------|
| LLM01: Prompt Injection | `RAG.PromptInjection.*` |
| LLM02: Insecure Output Handling | `RAG.OutputHandling.*` |
| LLM03: Training Data Poisoning | `RAG.VectorDB.*` (future data-plane) |
| LLM04: Model Denial of Service | `RAG.Configuration.MissingRateLimits` |
| LLM05: Supply Chain Vulnerabilities | `RAG.SupplyChain.*` |
| LLM06: Sensitive Information Disclosure | `RAG.Secrets.*` |
| LLM07: Insecure Plugin Design | `RAG.AgentControl.*` |
| LLM08: Excessive Agency | `RAG.AgentControl.*` |
| LLM09: Overreliance | N/A (out of scope) |
| LLM10: Model Theft | N/A (out of scope) |

### D. NIST AI RMF Mapping Reference

| NIST Function | RAG Finding Categories |
|---------------|----------------------|
| Govern (GOV) | `RAG.Governance.*`, `RAG.Configuration.*` |
| Map (MAP) | All categories (risk identification) |
| Measure (MEA) | All categories (testing and validation) |
| Manage (MAN) | All categories (risk mitigation) |

### E. MITRE ATLAS Mapping Reference (Selected Techniques)

| MITRE Technique | RAG Finding Categories |
|----------------|----------------------|
| T1574: Hijack Execution Flow | `RAG.AgentControl.*` |
| T1059: Command and Scripting Interpreter | `RAG.AgentControl.DangerousSink` |
| T1071: Application Layer Protocol | `RAG.Configuration.InsecureEndpoint` |
| T1552: Unsecured Credentials | `RAG.Secrets.*` |
| T1190: Exploit Public-Facing Application | `RAG.PromptInjection.*` |

### F. Evidence Schema Reference

**Required Evidence Fields:**
- `owasp_llm_category` (string, required) - OWASP LLM Top 10 category ID (e.g., "LLM01")
- `nist_rmf_function` (string, required) - NIST AI RMF function (GOV, MAP, MEA, MAN)
- `nist_rmf_category` (string, required) - NIST category (Security, Reliability, Privacy, etc.)
- `confidence` (string, required) - Confidence level (HIGH, MEDIUM, LOW)
- `rule_id` (string, required) - Unique rule identifier (e.g., "RAG-PI-001")

**Optional Evidence Fields:**
- `mitre_atlas_technique` (string, optional) - MITRE ATLAS technique ID (e.g., "T1574")
- `mitre_atlas_tactic` (string, optional) - MITRE ATLAS tactic name (e.g., "Execution")
- `framework` (string, optional) - Framework that detected the issue (e.g., "langchain")
- `detection_method` (string, optional) - Detection method (e.g., "ast_analysis", "regex_pattern", "semgrep")
- `pattern_match` (string, optional) - Matched pattern or code snippet
- `code_snippet` (string, optional) - Code snippet showing the issue
- `file_path` (string, optional) - File path where issue was found
- `line_number` (integer, optional) - Line number where issue was found

### G. Scanner Naming Convention

**RAG Scanner Names:**
- `"sentrascan-rag-rule"` - RAG RuleScanner findings (regex patterns)
- `"sentrascan-rag-sast"` - RAG SAST (Semgrep) findings
- `"sentrascan-rag-langchain"` - LangChain AST analyzer findings
- `"sentrascan-rag-llamaindex"` - LlamaIndex AST analyzer findings
- `"sentrascan-rag-haystack"` - Haystack analyzer findings
- `"sentrascan-trufflehog"` - TruffleHog secrets scanner (reused from MCP)
- `"sentrascan-gitleaks"` - Gitleaks secrets scanner (reused from MCP)

**Finding Module Field:**
- All RAG findings must set `module="rag"` in Finding records

### H. Implementation Checklist

**Pre-Implementation Requirements:**
- [ ] Update `Scan.scan_type` comment in `src/sentrascan/core/models.py`
- [ ] Update `Baseline.baseline_type` comment in `src/sentrascan/core/models.py`
- [ ] Add `PolicyEngine.default_rag()` method in `src/sentrascan/core/policy.py`
- [ ] Extend `PolicyEngine.from_file()` to parse `rag:` section
- [ ] Update `scan_type` enum in `src/sentrascan/core/tenant_settings.py` to include "rag"
- [ ] Update telemetry documentation in `src/sentrascan/core/telemetry.py`
- [ ] Review and verify analytics code handles "rag" scan type
- [ ] Update UI template `src/sentrascan/web/templates/index.html` (add "rag" filter option)
- [ ] Update UI template `src/sentrascan/web/templates/scan_detail.html` (update conditionals)
- [ ] Update UI template `src/sentrascan/web/templates/findings_aggregate.html` (verify RAG display)
- [ ] Update UI template `src/sentrascan/web/templates/dashboard.html` (verify RAG stats)
- [ ] Extract repository utilities to `src/sentrascan/core/repo_utils.py`
- [ ] Extract path utilities to `src/sentrascan/core/path_utils.py`
- [ ] Move secrets scanners to `src/sentrascan/core/secrets.py`
- [ ] Create evidence builder in `src/sentrascan/core/evidence.py`

**Implementation Tasks:**
- [ ] Create `src/sentrascan/modules/rag/scanner.py` (RAGScanner class)
- [ ] Create `src/sentrascan/modules/rag/detection.py` (FrameworkDetector class)
- [ ] Create `src/sentrascan/modules/rag/rules.py` (RAGRuleScanner class)
- [ ] Create `src/sentrascan/modules/rag/sast.py` (RAGSASTRunner class)
- [ ] Create `src/sentrascan/modules/rag/analyzers/` directory and analyzer classes
- [ ] Create `src/sentrascan/modules/rag/semgrep/` directory and Semgrep rules
- [ ] Add API endpoint `POST /api/v1/rag/scans` in `src/sentrascan/server.py`
- [ ] Add CLI command `sentrascan scan rag` in `src/sentrascan/cli.py`
- [ ] Create test fixtures in `tests/fixtures/rag_apps/`
- [ ] Write unit tests for all components
- [ ] Write integration tests for API, CLI, UI
- [ ] Write performance tests
- [ ] Write false positive validation tests

### I. Documentation Requirements

1. **User Guide:**
   - How to run RAG scans (CLI, API, UI)
   - How to interpret findings
   - How to configure `.sentrascan.yaml` with `rag:` section (flat structure)
   - Remediation guidance for each finding category
   - Examples of secure vs vulnerable RAG code patterns

2. **Developer Guide:**
   - How to add new RAG rules (regex patterns)
   - How to add new framework analyzers (AST-based)
   - How to extend AST analyzers
   - How to add new Semgrep rules
   - Code structure and architecture
   - Scanner naming conventions

3. **API Documentation:**
   - RAG scan endpoint documentation (`POST /api/v1/rag/scans`)
   - **OpenAPI 3.0 Schema:** Complete OpenAPI schema definition for the endpoint
   - Request/response examples with all fields documented
   - Error codes and meanings (400, 403, 500)
   - Authentication and authorization requirements
   - Partial scan result handling
   - Request body schema with validation rules
   - Response schema with all fields and types
   - Error response schemas for all error codes

4. **Configuration Documentation:**
   - `.sentrascan.yaml` structure with `rag:` section (flat structure, no nested sections)
   - Tenant settings configuration
   - Rule pack enable/disable configuration
   - Severity threshold configuration

5. **Migration Guide:**
   - **Database Migration:** Update scan_type comment in `Scan` model (no schema change, comment only)
   - **No Data Migration:** No existing data needs migration (RAG is new scan type)
   - **Backward Compatibility:** Existing scans and findings are unaffected
   - **Deployment Steps:**
     1. Update database model comments (scan_type, baseline_type)
     2. Update PolicyEngine to support `rag:` section
     3. Update tenant settings schema to include "rag" in enum
     4. Update UI templates to include "rag" option
     5. Update telemetry documentation
     6. Deploy RAG scanner module
   - **Rollback Plan:** If issues occur, RAG scanner can be disabled via tenant settings without affecting other scanners

6. **OpenAPI/Swagger Documentation:**
   - **OpenAPI 3.0 Schema:** Must provide complete OpenAPI schema for `/api/v1/rag/scans` endpoint
   - **Request Schema:** Document all request body fields with types, required/optional status, and validation rules
   - **Response Schema:** Document all response fields with types and descriptions
   - **Error Schemas:** Document error response formats for all HTTP status codes (400, 403, 500)
   - **Examples:** Provide request/response examples for common scenarios
   - **Authentication:** Document authentication requirements (API key, session)
   - **Authorization:** Document authorization requirements (scan.create permission)

5. **Migration Guide:**
   - Database migration requirements (comment updates only, no schema changes)
   - No data migration needed (new scan type)
   - Backward compatibility notes

---

**Document Version:** 2.2  
**Last Updated:** January 2025  
**Status:** Updated with All Critical Review Resolutions - Ready for Implementation
