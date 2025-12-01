## 1. Introduction / Overview

This PRD describes **static-analysis improvements** to the SentraScan MCP scanner to provide broader and deeper coverage of the MCP security threat model described in `docs/model-context-protocol-security.md`, **without adding any new dynamic/runtime testing**.

The current MCP scanner already integrates:
- `mcp-checkpoint` (config scanning),
- `mcp-scanner` with Yara (config scanning),
- `RuleScanner` (regex/code-pattern rules over MCP server repositories),
- `SASTRunner` (Semgrep SAST, currently Python-focused),
- MCP-specific probing of tool definitions (`MCPProbe`),
- a best-effort dynamic `RuntimeProbe` (which this PRD will not change),
- and secrets scanners (TruffleHog, Gitleaks).

However, coverage of several high-value MCP threat categories (especially identity/access, tool surface modelling, transport/network, supply chain, and logging/auditability) can be significantly strengthened by richer **static config/code analysis** and better mapping of findings back to the MCP threat taxonomy.

The goal of this feature is to define a set of static-only enhancements that:
- are understandable and implementable by a junior developer, and
- measurably improve MCP scanner coverage and fidelity, and
- provide clearer alignment between findings and the MCP threat categories (MCP‑T1…T12).

## 2. Goals

1. **Increase MCP threat coverage using static analysis only**  
   Expand MCP scanner rules so that more of the MCP threat categories (T1–T12) have one or more static detectors, with an emphasis on:
   - T1/T2: identity and access control misconfigurations,
   - T3/T4: input validation and dangerous tool surfaces,
   - T5/T7/T8: transport and network security misconfigurations,
   - T10: missing rate/resource controls,
   - T11: supply chain/dependency hygiene,
   - T12: logging and observability gaps.

2. **Improve actionable feedback for security engineers and developers**  
   Provide:
   - clear, high‑signal findings (titles, descriptions, remediation), and  
   - a high-level “MCP readiness” summary per scan that helps users quickly understand overall risk.

3. **Align findings with the MCP security white paper**  
   Tag static findings with explicit references to:
   - the MCP threat taxonomy (e.g. `MCP-T3`, `MCP-T7`), and  
   - whether the threat is MCP-specific, contextualized, or conventional.

4. **Use only static analyses – no new runtime instrumentation**  
   Reuse existing scanners, CLIs, and policy engine infrastructure, adding new rules, parsers, and reporting logic without introducing new dynamic probes or external scanning services.

## 3. User Stories

1. **Security engineer (CI/CD) – Config-level issues**
   - *As a* security engineer running SentraScan MCP checks in CI/CD,  
     *I want* the scanner to detect insecure authentication, authorization, and TLS settings in MCP configs,  
     *so that* I can block deployments that would expose MCP servers with weak identity and transport protections.

2. **MCP server developer – Tool surface risk**
   - *As a* developer building an MCP server,  
     *I want* the scanner to identify over‑powered tools (e.g. arbitrary SQL/file/HTTP capabilities with free‑form inputs),  
     *so that* I can refactor or gate those tools before they become a security liability.

3. **Security engineer – Code-level vulnerabilities in MCP context**
   - *As a* security engineer reviewing MCP server code,  
     *I want* Semgrep and regex rules specialized for MCP patterns (SQL injection, SSRF, path traversal, insecure TLS, etc.),  
     *so that* MCP-focused issues are detected consistently and mapped to relevant MCP threats.

4. **Platform/SRE – Supply chain and dependency hygiene**
   - *As a* platform/SRE engineer responsible for MCP infrastructure,  
     *I want* the MCP scanner to highlight unpinned or suspicious dependencies and insecure update channels in MCP server repos,  
     *so that* I can address supply-chain risk before deploying those servers.

5. **Security engineer – High-level readiness**
   - *As a* security engineer using SentraScan reports,  
     *I want* an “MCP readiness” summary that aggregates key static signals (auth, transport, tool surface, secrets, dependencies, logging),  
     *so that* I can quickly gauge whether a given MCP server is reasonably hardened, and where to focus remediation.

## 4. Functional Requirements

### 4.1 Config-Level Identity and Access Control Analysis (Static)

1. **Config parsing and normalization**
   - The system must parse MCP config files (e.g. `mcp.json` and equivalent) used by `MCPScanner` into a structured internal model that captures for each MCP server:
     1.1. Command, args, and env vars.  
     1.2. Any auth-related fields (e.g. `auth`, `token`, `client_id`, `client_secret`, `scope`, `audience`).  
     1.3. Whether the server is local vs remote (based on URL/host).
   - Config/env analysis is limited to:
     - configuration files explicitly provided to the MCP scanner (e.g. `mcp.json` and similar), and  
     - any checked-in environment/config files within the scanned repositories (if included by design),  
     and will **not** introspect the host OS environment at runtime.

2. **Auth mechanism classification**
   - The system must, from config/env alone, classify the apparent authentication mechanism for each remote MCP server where possible, e.g.:
     2.1. No authentication (anonymous).  
     2.2. Basic auth / static API key.  
     2.3. OAuth/OIDC (by presence of token endpoints, client IDs, scopes, etc.).

3. **Static rules for risky auth patterns**
   - The system must implement static rules that create findings when it detects:
     3.1. Remote MCP servers with no evident authentication.  
     3.2. Use of basic auth or long‑lived static API keys in config/env (e.g. `API_KEY`, `AUTH_TOKEN`, `Authorization: Bearer ...` hardcoded).  
     3.3. Comments or flags indicating token passthrough (e.g. env names like `USER_TOKEN`, `PASSTHROUGH_TOKEN`) without evidence of token exchange.  
     3.4. OAuth/OIDC scopes that are obviously over‑broad (e.g. `*`, `admin`, `full_access`, `repo`, or other high‑privilege strings).

4. **RBAC and policy hints**
   - The system should look for RBAC/policy hints in config (fields like `role`, `roles`, `permissions`, `policy`, `policy_file`) and:
     4.1. Record their presence as positive evidence.  
     4.2. Emit an informational finding if a repo exposes many tools but no RBAC/policy references are found anywhere in config or code.

5. **Threat mapping**
   - Findings from these rules must be tagged in evidence with:
     5.1. `mcp_threat` values such as `MCP-T1` and/or `MCP-T2`.  
     5.2. A short note indicating whether the threat is **MCP-contextualized** or **conventional** as per the white paper.

### 4.2 Enhanced MCP Tool Surface Modelling (Static)

6. **Structured tool profile output (extending existing MCPProbe)**
   - `MCPProbe` already performs heuristic risk assessment on tools based on names and `inputSchema`.  
   - It must be extended to produce a structured profile for each discovered tool, including:
     6.1. Tool name and description.  
     6.2. Input parameters with types and whether they are free‑form text vs enumerated/structured.  
     6.3. A set of “capability tags” describing what the tool can do (e.g. `filesystem.read`, `filesystem.write`, `sql.execute`, `shell.exec`, `http.request`, `llm.invoke`), inferred from existing MCPProbe heuristics and schema fields.

7. **Static risk policies on tool profiles**
   - The system must add or refine static rules that flag tool definitions with:
     7.1. Both **unconstrained free‑form text input** and **high‑risk capabilities** (e.g. `sql.execute`, `shell.exec`, `filesystem.write`, unrestricted `http.request`).  
     7.2. Multiple unrelated high‑risk capability tags, indicating “Swiss‑army” tools (e.g. combined HTTP, filesystem, and database operations in one tool).  
     7.3. Parameters representing file paths or URLs with no explicit allowlists, roots, or constrained enums.

8. **Prompt‑injection sensitive flows (static patterns)**
   - The system must provide static patterns (regex/Semgrep) to flag where:
     8.1. Tool or resource output is concatenated directly into prompts that are later passed to other tools or LLMs without filtering.  
     8.2. Untrusted text from tools/resources is included in control‑like fields (e.g. shell/SQL/URL arguments).

9. **Categorization**
   - Tool-surface-related findings must use consistent categories such as:
     9.1. `MCP.ToolSurface.Overprivileged`.  
     9.2. `MCP.ToolSurface.PromptInjectionRisk`.  
     9.3. `MCP.ToolSurface.WeakInputConstraints`.

### 4.3 MCP-Focused SAST and Regex Rules (Static Code)

10. **MCP ruleset for SQL/command/file/HTTP**
    - The system must **extend existing RuleScanner patterns and Semgrep rules** to detect, in MCP server repos:
      10.1. SQL built from string concatenation, f‑strings, or formatting using untrusted values (SQL injection).  
      10.2. Shell/command execution APIs (e.g. `subprocess`, `os.system`, `Popen`, `eval`, `exec`) passed user/tool inputs.  
      10.3. Path traversal / arbitrary file access using unvalidated path components.  
      10.4. HTTP/SSRF patterns where arbitrary URLs are fetched without hostname or scheme allowlists.  
      10.5. Disabling TLS verification (e.g. `verify=False`, custom SSL contexts that turn off checks).

    - For Node/TypeScript MCP servers, the system must:
      10.6. Add or enable appropriate Semgrep JS/TS rulesets (e.g. `p/javascript` or equivalent) and/or custom JS/TS rules to cover analogous patterns (SQLi, command exec, SSRF, path traversal, insecure TLS) in JavaScript/TypeScript code.

11. **Transport and binding checks in code**
    - The system must add static rules that flag:
      11.1. Servers binding to `0.0.0.0` without any evidence of TLS or auth.  
      11.2. Explicit disablement of TLS or comments indicating “temporary” insecure HTTP usage for production‑like code paths.

12. **MCP threat mapping in SAST findings**
    - New SAST findings must be tagged with relevant MCP threat IDs, for example:
      12.1. SQL/command/file injections → `MCP-T3` (and conventional injection threats).  
      12.2. Insecure HTTP / TLS settings → `MCP-T5`, `MCP-T7`, `MCP-T8`.  
      12.3. SSRF patterns → `MCP-T5`, `MCP-T8`.

### 4.4 Static Resource/Rate-Limiting Heuristics (T10)

13. **Unbounded tool logic detection**
    - The system must add static rules that warn when MCP server code:
      13.1. Iterates over unbounded data sets (e.g. all rows, all files) **and** calls known high-cost or external operations (e.g. HTTP clients, LLM APIs, MCP tools) inside the loop with no throttling.  
      13.2. Performs recursive or nested invocations involving such high-cost operations that could explode in complexity or cost.

14. **Config-based quota presence checks**
    - The system should scan config/env for hints of resource controls (keys like `RATE_LIMIT`, `MAX_REQUESTS`, `MAX_TOKENS`, `MAX_RETRIES`) and:
      14.1. Note their presence as positive evidence.  
      14.2. Create a warning if high‑risk tools are present but no resource/limit settings are detected anywhere in the repo/config (e.g. category `MCP.Resource.RateLimitMissing`).

### 4.5 Supply Chain & Dependency Hygiene (Static)

15. **Dependency file inspection**
    - The system must parse common dependency files in MCP server repos (e.g. `pyproject.toml`, `requirements.txt`, `package.json`) and:
      15.1. Identify unpinned or loosely pinned versions for security‑sensitive dependencies (e.g. version ranges `>=`, `^`, `*`).  
      15.2. Flag use of obvious MCP‑server libraries with no pinned versions (if known set is available).  
      15.3. Group findings under categories such as `MCP.SupplyChain.UnpinnedDependency`.

16. **Insecure package source patterns**
    - The system must add rules to flag:
      16.1. `pip install`/`npm install` from raw git URLs or non‑TLS package indexes (`http://`).  
      16.2. Custom package indexes defined in config/env that use `http://` or untrusted hosts.

### 4.6 Logging, Monitoring, and Auditability (Static)

17. **Logging presence heuristics**
    - The system should inspect MCP server repos for:
      17.1. Use of logging frameworks (`logging`, `structlog`, or equivalents) around tool invocations and sensitive operations.  
      17.2. If many tools are present but there is almost no logging in the repo, emit a low‑severity informational finding like `MCP.Observability.LowLogging`.

18. **Audit/telemetry config hints**
    - The system should check config/env for audit/telemetry settings (e.g. keys starting with `OTEL_`, `OPENTELEMETRY`, `AUDIT_LOG`) and:
      18.1. Record their presence positively in evidence.  
      18.2. Optionally emit an informational “missing audit integration” note when absent in larger MCP repos.

### 4.7 Reporting & Readiness Summary

19. **MCP threat metadata on findings**
    - For new MCP-related rules, the system must:
      19.1. Attach in the finding’s evidence fields: `mcp_threat` (e.g. `"MCP-T3"`), `mcp_tier` (e.g. `"MCP-Contextualized"` or `"Conventional"`).  
      19.2. Ensure these tags are available in the existing export/report APIs (no breaking changes to existing fields).
    - The mapping from rules to MCP threats must be keyed by at least `(engine, rule_id)` (or an equivalent stable identifier), so that multiple engines (RuleScanner, Semgrep, MCPProbe, secrets) can be mapped consistently.

20. **MCP readiness summary**
    - The MCP scanner’s `to_report` output should be extended (or supplemented) to include a non-blocking, high‑level MCP readiness summary that aggregates:
      20.1. Presence/absence of critical config protections (auth, TLS, host allowlists).  
      20.2. Count of high‑risk tool-surface findings.  
      20.3. Secrets/severity counts from existing scanners.  
      20.4. Dependency hygiene warnings.  
      20.5. Observability/logging hints.
    - The readiness summary must:
      20.6. Be emitted whenever at least one MCP-relevant tool (e.g. mcp-checkpoint, mcp-scanner Yara, RuleScanner, Semgrep, secrets scanners, MCPProbe) has run successfully in the scan, as determined from the scanners invoked in `MCPScanner.scan` (e.g. `issue_types` and/or per-scanner execution flags).  
      20.7. Include an explicit **confidence indicator** based on how many of the available tools actually ran (e.g. low/medium/high, plus a count of executed tools vs total supported), using the agreed thresholds.  
      20.8. Be clearly labeled as informational and must **not** change gating behavior in the policy engine in this iteration.

## 5. Non-Goals (Out of Scope)

1. **No dynamic or runtime testing changes**  
   - This PRD explicitly excludes any new dynamic probing, runtime instrumentation, or changes to existing runtime probes. All enhancements must be static (config + code + repo structure).

2. **No changes to policy engine gating logic**  
   - The feature will not introduce new gating rules or change pass/fail criteria in the policy engine.  
   - Any “readiness score” or enriched metadata is for visibility and triage only.

3. **No new external tools/CLIs**  
   - The MCP scanner must reuse existing infrastructure (Semgrep, mcp-checkpoint, mcp-scanner, secrets scanners) and not introduce new third‑party binaries or services.

4. **No full protocol or spec validation**  
   - The scanner will not attempt to fully validate MCP protocol correctness; it only performs heuristic/static security checks aligned with the white paper.

## 6. Design Considerations (Optional)

- **Rule organization**  
  - Group new rules into clearly named rule packs (e.g. `mcp-config-auth`, `mcp-tool-surface`, `mcp-transport`, `mcp-supplychain`) to keep configuration manageable.

- **False positive control**  
  - Start new rules at medium/low severity by default where there is higher FP risk (e.g. logging presence, unbounded loops) so security teams can tune policy without disruption.

- **Extensibility to Node/TypeScript**  
  - Some Semgrep rules should be written in a language-agnostic way where possible, then extended to **Python as the primary target** and to **basic Node/TypeScript rules in the same iteration**, so that JavaScript/TypeScript MCP servers receive at least baseline coverage.

- **Finding categories and deduplication**
  - New MCP-specific categories (e.g. `MCP.ToolSurface.Overprivileged`, `MCP.Resource.RateLimitMissing`, `MCP.Observability.LowLogging`) should be **additive** to existing categories (`Code.Pattern`, `MCP.ToolSurface`, `Secrets`, `MCP.ToolSurface.Dynamic`) to avoid breaking existing filters.  
  - Where multiple scanners report essentially the same issue for the same file/line (e.g. Semgrep and RuleScanner on the same SQL injection), the implementation should either de-duplicate based on `(engine, rule_id, file:line)` or clearly indicate merged evidence to avoid double-counting in summaries.

## 7. Technical Considerations (Optional)

- **Integration points**
  - Most work will occur in and around `src/sentrascan/modules/mcp/scanner.py`, the MCP rules engine, and Semgrep rule packs.
  - Config parsing should be careful not to break existing `mcp.json` handling and should tolerate partial or invalid configs.

- **Performance**
  - New static rules should be designed to avoid excessive overhead on large repos (e.g. limit deep dependency tree analysis, avoid expensive regexes).

- **Backward compatibility**
  - New evidence fields (`mcp_threat`, `mcp_tier`) must be additive and safe for existing consumers that ignore unknown keys.

- **Rule bundle versioning and ownership**
  - MCP-related rule packs should be versioned and shipped as part of an explicit **rule bundle**, or via the existing `policy_file`/rules configuration mechanism (whichever is more consistent with the current product design).  
  - Ownership of these MCP rules (authoring, tuning, updating) will reside with the **product teams**, who will publish updates alongside rule bundle or policy configuration version bumps.

## 8. Success Metrics

1. **Improved coverage in existing test MCP server**
   - New static rules find additional, meaningful findings when scanning `tests/test_mcp_server` (or an extended version of it), especially for:
     - config/auth/TLS issues,  
     - tool-surface risks,  
     - dependency hygiene,  
     - and logging/observability hints.
   - The test MCP server should be extended (if needed) to include representative auth/TLS config examples, rate-limit configuration, and logging/audit patterns so each new rule has a corresponding test case.

2. **Threat-mapped findings visible in output**
   - MCP scan results show findings tagged with specific `MCP-T*` identifiers and tiers, making it clear which parts of the white paper are covered.

3. **User feedback (qualitative)**
   - Early users (security engineers and MCP developers) report that:
     - findings are understandable and actionable, and  
     - the readiness summary helps them prioritize remediation across multiple MCP servers.

## 9. Open Questions
1. **Published rule-to-threat mapping format and location**  
   - We will maintain a published mapping table of **each rule → MCP threat(s)** in addition to embedding tags in evidence.  
   - Decision: use a **canonical JSON/YAML source** under a configuration/rules directory, and generate a human-friendly Markdown table under `docs/` from that source so both tooling and humans can consume it consistently.

2. **Confidence scoring formula for readiness summary**  
   - The readiness summary will include a confidence indicator based on the number of tools run vs total supported.  
   - Decision (initial thresholds):  
     - 0–1 tools run → `low` confidence,  
     - 2–3 tools run → `medium` confidence,  
     - ≥ 4 tools run → `high` confidence.  
   - Open: in future iterations, we may refine this to weight some tools more heavily than others based on their coverage.

3. **Policy/pipeline integration for rule bundles**  
   - Product teams will own rules and ship them as versioned bundles or via existing `policy_file` formats.  
   - Decision: expose the **rule bundle or policy version identifier** in exported reports (JSON/CSV/API) rather than changing the core scan metadata shape, so that downstream systems can track which rule bundle produced a given scan without impacting existing scan consumers.



