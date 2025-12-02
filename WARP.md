# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## 1. Core workflows & commands

### 1.1 Local Python development (no Docker)

- Create a virtualenv and install the package in editable mode:
  - `make venv` to create `venv/` (if it does not exist).
  - `make install` or `make dev-install` to install `sentrascan` and its dependencies.
  - Equivalent manual setup:
    - `python3.11 -m venv venv && source venv/bin/activate`
    - `pip install -e . && pip install pytest pytest-asyncio`

- Run the API server against a local database:
  - Ensure `DATABASE_URL` is set, for example:
    - `export DATABASE_URL=postgresql+psycopg2://sentrascan:changeme@localhost:5432/sentrascan`
  - Initialize the database once:
    - `make db-init`  (or `sentrascan db init`)
  - Start the server:
    - `make server`  (runs `sentrascan server --host 0.0.0.0 --port 8200`)

- Create API keys and bootstrap a tenant/admin user:
  - Create API keys (admin or viewer):
    - `make auth-create NAME=admin ROLE=admin`
    - `make auth-create NAME=viewer ROLE=viewer`
  - First deployment bootstrap (tenant + super admin user):
    - `make create-super-admin EMAIL=admin@example.com PASSWORD=... NAME="Admin User" TENANT_NAME="Default Tenant"`

### 1.2 Docker-based workflow

- Start full stack locally (API + Postgres + UI):
  - `make docker-up`  (equivalent to `docker compose up -d`)
  - After first start, initialize DB:
    - `make db-init`  or `docker compose exec api sentrascan db init`

- Development mode with live code reloading:
  - `make docker-up-dev` (uses `docker-compose.dev.yml` to mount `src/` and `tests/` into the API container).

- Stop and clean:
  - `make docker-down` to stop services.
  - `make docker-clean` or `make clean-all` for deep Docker/system cleanup.

### 1.3 Testing

- Run the full pytest suite:
  - `make test`  (runs `pytest tests`)

- Unit-only vs integration tests:
  - Unit tests (exclude `@pytest.mark.integration`):
    - `make test-unit`  (`pytest tests -m "not integration"`)
  - Integration tests (require Docker services + API container):
    - `make docker-up`
    - `make test-integration`  (uses `scripts/test.sh` with `SENTRASCAN_API_BASE`, default `http://localhost:8200`)

- Smoke & UI tests:
  - API smoke tests:
    - `make test-smoke`  (requires Docker services; runs `scripts/api-smoketest.sh`)
  - UI smoke tests:
    - `make test-ui`  (`pytest tests/test_ui_smoke.py -v`)

- Run a single test file or test:
  - `pytest tests/path/to/test_file.py -v`
  - `pytest tests/path/to/test_file.py::test_name -v`

- Cloud/remote testing helpers:
  - `make test-cloud-remote API_BASE=https://your-env`  (runs full suite against remote API).
  - `make test-cloud-smoke API_BASE=https://your-env`  (smoke tests via `scripts/api-smoketest.sh`).
  - `make test-cloud-ci`  (CI-like local run; uses `SENTRASCAN_API_BASE=${API_BASE:-http://localhost:8200}`).

### 1.4 Linting, formatting, type checking

- Lint:
  - `make lint`  (prefers `ruff check src/ tests/`, falls back to `flake8`).

- Format:
  - `make format`  (prefers `ruff format src/ tests/`, falls back to `black src/ tests/`).

- Type-check:
  - `make type-check`  (runs `mypy src/`).

### 1.5 Docker images & multi-arch builds

- Build dev image:
  - `make docker-build IMAGE_TAG=sentrascan/platform:dev`

- Faster incremental builds (BuildKit):
  - `make docker-build-fast IMAGE_TAG=sentrascan/platform:dev`

- Multi-architecture image (uses `scripts/buildx-multiarch.sh`):
  - `make docker-build-multiarch IMAGE_TAG=sentrascan/platform:dev`
  - Add `PUSH=1` to push the built image: `make docker-build-multiarch IMAGE_TAG=... PUSH=1`

### 1.6 CLI entrypoints (direct usage)

The `sentrascan` CLI (defined in `src/sentrascan/cli.py`) exposes the main operations:

- Model scan:
  - `sentrascan scan model path/to/model --sbom path/to/model.sbom.json [--strict] [--policy .sentrascan.yaml] [--timeout N]`

- MCP scan:
  - `sentrascan scan mcp --auto-discover [--policy .sentrascan.yaml] [--timeout 60]`
  - Or specify explicit config files:
    - `sentrascan scan mcp --config path/to/mcp.json --config other.json`

- Server:
  - `sentrascan server --host 0.0.0.0 --port 8200`

- Database and auth management (usually via Makefile wrappers):
  - `sentrascan db init`
  - `sentrascan auth create --name NAME --role admin|viewer`
  - `sentrascan user create-super-admin --email ... --password ... --name ... --tenant-name ...`

When using Docker, prefer running these via `docker compose exec api ...` so they operate inside the container environment.

### 1.7 Security scanning CI

GitHub Actions workflows under `.github/workflows`:

- `security-scan.yml` (active):
  - Runs on pushes/PRs to `main` and `develop`, and on a weekly cron.
  - Performs Python dependency scanning with `safety` and `pip-audit`.
  - Builds `Dockerfile.production` and scans the image with Trivy (CRITICAL/HIGH severities), uploading SARIF results.

- `ci.yml` (currently disabled):
  - Contains a placeholder CI job; enabling it requires adding an `on:` trigger and real jobs.

## 2. High-level architecture

### 2.1 Top-level structure

- `src/sentrascan/` is the main application package. It contains:
  - `cli.py` – Click-based CLI entrypoint (`sentrascan` console script).
  - `server.py` – FastAPI app that serves both REST API and Jinja2 web UI.
  - `core/` – Domain and infrastructure services (DB models, auth, RBAC, security, logging, telemetry, tenancy, encryption, etc.).
  - `modules/` – Scanner implementations for MCP (`modules/mcp`) and models (`modules/model`).
  - `web/` – HTML templates and static assets (CSS/JS) for the UI.

Scans and SBOMs are persisted via SQLAlchemy into a relational database (SQLite or PostgreSQL; production typically uses Postgres via `DATABASE_URL`).

### 2.2 CLI orchestration (`src/sentrascan/cli.py`)

- Exposes a `click.group()` `main` with subcommands:
  - `scan model`:
    - Builds a `PolicyEngine` (from a policy file or `PolicyEngine.default_model()`), instantiates `ModelScanner`, opens a `SessionLocal()` DB session, and calls `ModelScanner.scan`.
    - Emits a JSON report (either to `--output` or stdout) including `gate_result`, and exits with code `0` on pass, `1` on policy failure.
  - `scan mcp`:
    - Similar pattern using `MCPScanner` and `PolicyEngine.default_mcp()` unless a policy file is provided.
    - Supports `--config` (one or more MCP config files) and `--auto-discover` to search common MCP locations.
  - `server`:
    - Calls `core.container_protection.check_container_access()` and then `run_server(host, port)` from `server.py`.
  - `db init`:
    - Calls `core.storage.init_db()` and prints a confirmation.
  - `auth create`:
    - Generates a cryptographically strong API key, hashes it with SHA-256, stores it as a `core.models.APIKey`, and prints the plaintext key once.
  - `user create-super-admin`:
    - Bootstraps a tenant (`core.models.Tenant`) and a `super_admin` user via `core.auth.create_user`, or attaches the user to an existing active tenant.
  - `doctor`:
    - Runs `ModelScanner.doctor()` (a wrapper around `python -m modelaudit doctor`) to verify scanner health.

Whenever possible, use these CLI commands (directly or via Makefile targets) rather than calling scanner classes manually, so that DB state, policy evaluation, and logging remain consistent.

### 2.3 FastAPI server & Web UI (`src/sentrascan/server.py`, `src/sentrascan/web/`)

**Lifecycle & middleware:**

- On import, the server module:
  - Enforces container hardening by calling `check_container_access()`.
  - Configures structured logging via `core.logging.configure_logging()` and logs startup with the package version.
  - Initializes telemetry with `core.telemetry.initialize_telemetry()` and pre-emptively archives old logs/telemetry (`core.log_retention`).
- Wraps the FastAPI app with:
  - `LoggingMiddleware` for request/response logging and per-request telemetry events.
  - `TenantContextMiddleware` to bind tenant information into request context.
  - Security middleware from `core.security` (rate limiting, security headers, request size limits).
  - Optional CORS middleware based on `CORS_ALLOWED_ORIGINS` / `CORS_ALLOW_CREDENTIALS`.

**Auth, sessions, and tenancy:**

- Cookie-based sessions are implemented in `core.session`; `SESSION_COOKIE_NAME` is used and cookies are signed/verified through helper functions.
- `get_session_user` resolves the effective principal from the session cookie, supporting both `User` and `APIKey` subjects and handling legacy cookie formats.
- Multi-tenancy is enforced by:
  - Extracting tenant from the request (`core.tenant_context` helpers and middleware).
  - Scoping queries via `core.query_helpers.filter_by_tenant` / `require_tenant_for_query`.
  - Ensuring all major models (`Tenant`, `User`, `APIKey`, `Scan`, `Finding`, `Baseline`, `SBOM`, etc.) carry a `tenant_id` with appropriate indexes.
- Role- and permission-based access control is centralised in `core.rbac`, which exposes helpers like `require_role`, `require_permission`, `can_access_tenant`, and `has_permission` used across endpoints.

**Scanning endpoints and job execution:**

- The server exposes REST endpoints (documented in `docs/TECHNICAL-DOCUMENTATION.md`) for:
  - Health checks (`/api/v1/health`).
  - Triggering model and MCP scans (`/api/v1/models/scans`, `/api/v1/mcp/scans`).
  - Listing and inspecting scans and findings (`/api/v1/scans`, `/api/v1/scans/{id}`).
  - Managing baselines and policies.
- Scan execution uses a simple in-process job runner that coordinates `ModelScanner` and `MCPScanner` instances with a shared `PolicyEngine` and DB session.

**Web UI:**

- Templates under `src/sentrascan/web/templates` provide:
  - Login, dashboard, scan detail, scan forms, baselines and baseline comparison, analytics, tenant and API key management, and error pages.
- Static assets under `src/sentrascan/web/static/{css,js}` handle client-side behavior (filters, charts, realtime updates, tenant settings, etc.).
- When changing UI behavior, update both the Jinja2 templates and the corresponding JS modules rather than embedding UI logic into the API layer.

### 2.4 Core domain & infrastructure (`src/sentrascan/core/`)

**Persistence & models (`models.py`, `storage.py`):**

- `storage.py` (not reproduced here) defines SQLAlchemy `Base`, engine configuration, `SessionLocal`, and `init_db()`. Use these instead of constructing new engines/sessions ad-hoc.
- `models.py` defines the main relational entities, all scoped by tenant:
  - `Tenant`, `TenantSettings`, `AuditLog` – tenant metadata, key-value settings, and audit trail with indexes on tenant, user, and timestamp.
  - `User` – user accounts (email, password hash, MFA fields, role, active flag) with indexes on `tenant_id` and `email`.
  - `APIKey` – API keys and their metadata (role, hashed key, revoked/expiry/rotation fields). Includes helpers:
    - `hash_key(key: str) -> str` (SHA-256) for secure storage.
    - `validate_key_format(...)` enforcing an `ss-proj-h_...` key format with additional constraints.
  - `Scan`, `Finding`, `Baseline`, `SBOM` – core scanning artifacts:
    - `Scan` tracks scan type (`mcp` / `model`), status, pass/fail, severity counts, baseline/SBOM associations, and metadata.
    - `Finding` captures module/scanner, severity, category, description, location/evidence/remediation.
    - `SBOM` stores CycloneDX SBOM content for model scans.
    - `Baseline` stores approved snapshot content and metadata (including links back to scans/SBOMs).

**Policy & gating (`policy.py`):**

- `Policy` dataclass:
  - `severity_threshold`, `block_issues`, and optional `sbom_requirements`.
  - Tenant-specific configuration fields: `gate_thresholds`, `policy_rules`, `pass_criteria`.
- `PolicyEngine`:
  - `from_file(path, tenant_id, db)` reads YAML (typically `.sentrascan.yaml`), supporting unified `model`/`mcp` keys and falling back to defaults when `.sentrascan.yaml` is missing.
  - `default_model(...)` and `default_mcp(...)` define conservative defaults for model and MCP scans.
  - `gate(severity_counts, issue_types)` evaluates whether a scan passes:
    - Uses numeric `gate_thresholds` (per severity) if set in tenant settings.
    - Otherwise falls back to severity-threshold semantics (BLOCK on any finding at or above `severity_threshold`).
    - Also blocks on configured `block_issues` and any failing custom rules in `policy_rules`.

**Security, observability, and platform services:**

- Notable modules (high level):
  - `auth.py` – user lifecycle and password policies.
  - `security.py` – rate limiting, security headers, request size limits, sanitization, and CORS defaults.
  - `session.py` – session and cookie management, including rotation and cleanup.
  - `rbac.py` – roles/permissions and checking helpers.
  - `logging.py`, `telemetry.py`, `analytics*.py`, `log_retention.py` – structured logging, telemetry capture, analytics, and archival.
  - `container_protection.py` – host/container checks used at CLI/server startup.
  - `encryption.py`, `transparent_encryption.py`, `key_management.py`, `masking.py`, `backup.py`, `sharding.py`, `tenant_context.py`, `tenant_settings.py` – data protection, key rotation, masking, backup/sharding, and tenant context/settings.

Where possible, reuse these utilities (e.g., `filter_by_tenant`, RBAC helpers, key management, masking) instead of re-implementing security, logging, or tenancy logic.

### 2.5 Scanner modules

#### Model scanner (`src/sentrascan/modules/model/scanner.py`)

- Responsible for ML model security and SBOM generation, built on top of the external `modelaudit` tool.
- `_validate_paths(paths)` defends against SSRF by:
  - Allowing only local filesystem paths, `hf://...` shorthand, and well-formed `https://huggingface.co/...` URLs.
  - Rejecting arbitrary HTTP(S) URLs with a clear error, instructing callers to pre-download artifacts.
- `scan(paths, sbom_path, strict, timeout, db, tenant_id)`:
  - Validates paths and creates a `Scan` row with status `in_progress` before invoking `modelaudit`.
  - Executes `python -m modelaudit scan ... -f json` via `subprocess.run`, directing cache and home directories to writable locations (`MODELAUDIT_CACHE_DIR`, `HOME`, `XDG_CACHE_HOME`) suitable for read-only containers.
  - Parses JSON from stdout, logs anomalies, and fails the scan if no usable report is produced.
  - Optionally persists a generated SBOM into `core.models.SBOM` and links it via `scan.sbom_id`.
  - Normalizes severity levels, aggregates `sev_counts` and `issue_types`, and uses `PolicyEngine.gate(...)` to set `scan.passed`.
  - Materializes each reported issue as a `Finding`, tracking file/line info and aggregating issues per file for reporting.
- `doctor()` provides a health check around `modelaudit doctor` and is exposed via the `sentrascan doctor` CLI.

#### MCP scanner (`src/sentrascan/modules/mcp/scanner.py`)

- Performs static and dynamic security analysis of MCP configurations and associated code repositories.
- Configuration discovery:
  - `DEFAULT_DISCOVERY_PATHS` includes common MCP config locations (Claude Desktop, Cursor, Windsurf, VS Code, etc.).
  - `auto_discover()` walks these paths to find MCP JSON files.
- Repository handling:
  - `_is_allowed_repo_url(url)` restricts repositories to an allowlist (GitHub, Hugging Face, and `hf://` URIs) and safe schemes (`https`, `http`, or git+ssh for GitHub), rejecting arbitrary hosts/schemes.
  - `_ensure_repo(url, cache_dir)` clones with `git clone --depth 1`, using `GIT_LFS_SKIP_SMUDGE=1` for Hugging Face to avoid large LFS blobs, and logs failures/timeouts.
  - On git failure and when possible, falls back to downloading a GitHub repo zip via `requests` and extracting it into a cache directory under `/cache/mcp_repos`.
- `scan(config_paths, auto_discover, timeout, db, tenant_id, existing_scan)`:
  - Merges discovered config paths when `auto_discover` is enabled.
  - Creates or updates a `Scan` row (`scan_type="mcp"`, status `in_progress`, `tenant_id` set) and flushes it.
  - Initializes severity counts and per-file tracking structures:
    - Uses `clean_file_path` to strip cache prefixes and internal paths.
    - Uses `normalize_file_key` to group issues by filename, independent of full path or line-number suffixes.
  - Orchestrates multiple analysis steps via:
    - `RuleScanner` (regex/rule-based analysis).
    - `SASTRunner` (Semgrep-based SAST).
    - `RuntimeProbe` (safe-run MCP probing via `uv`).
    - `TruffleHogRunner` and `GitleaksRunner` (secrets detection).
  - Aggregates severities and issue types across all sub-scanners, then uses `PolicyEngine.gate(...)` to produce the gate result (`scan.passed`).

MCP and model scanning share the same persistence model (`Scan`/`Finding`/`SBOM`/`Baseline`) and policy engine; cross-cutting features such as baselines, reporting, or gating should therefore be implemented in a module-agnostic way whenever feasible.

## 3. Documentation to consult

Key documentation files (do not duplicate them here; use them as primary references):

- `README.md` – high-level overview, core features, CLI examples, and links to all documentation.
- `docs/QUICK-START.md` – concrete setup steps for Docker vs local installation and first scans via CLI/API/UI.
- `docs/TECHNICAL-DOCUMENTATION.md` – detailed architecture description (mermaid diagram, component breakdown, API and DB references).
- `docs/SECURITY.md` – repository-specific security practices, example configs, and code snippets for hardening.

Before making architectural or security-impacting changes in `src/sentrascan/server.py` or `src/sentrascan/core/`, review these documents.

## 4. AI-assistant workflows from existing .cursor rules

This repo contains Cursor rules under `.cursor/rules/*.mdc`. When operating as Warp in this repository, mirror the intent of these workflows so behavior is consistent across tools.

### 4.1 PRDs and task lists (`/tasks` directory)

- **Creating a PRD (`create-prd.mdc`)**:
  - When asked to define a new feature, first ask focused clarifying questions (problem/goal, target user, core functionality, user stories, acceptance criteria, scope/non-goals, data requirements, design hints, edge cases).
  - Generate a Markdown PRD with sections such as: Introduction/Overview, Goals, User Stories, Functional Requirements, Non-Goals, Design Considerations, Technical Considerations, Success Metrics, Open Questions.
  - Save the PRD as `tasks/prd-<feature-name>.md`.

- **Generating an implementation task list from a PRD (`generate-tasks.mdc`)**:
  - Phase 1 – High-level tasks:
    - Read the referenced PRD, derive a small set of numbered parent tasks, and present ONLY those high-level tasks.
    - Pause and wait for explicit user confirmation (e.g., reply "Go") before proceeding.
  - Phase 2 – Detailed subtasks:
    - Expand each parent into checkbox subtasks and maintain a `## Relevant Files` section listing code/test files that will likely be involved, with one-line descriptions.
    - Save as `tasks/tasks-<prd-file-name>.md` (e.g., `tasks-prd-user-profile-editing.md`).

- **Managing task lists (`process-task-list.mdc`)**:
  - Work on **one subtask at a time**; after completing a subtask, immediately update the Markdown checklist to `[x]` and pause for user approval before starting the next.
  - Keep the `Relevant Files` section synchronized with actual files created or modified.
  - When all subtasks for a parent task are complete and tests pass, prepare a conventional commit message that summarizes the parent task and references the PRD/task number, but only run `git` commands after explicit user approval in this Warp environment.

### 4.2 Debugging flows

- **DebugFast (`debug-fast.mdc`) – localized issues**:
  - Use when the bug is clearly tied to a specific component/endpoint and impact is moderate or low.
  - Restate the problem succinctly (problem, expected behavior, scope).
  - Identify the primary file/function, perform a targeted code review, and generate 2–3 concrete hypotheses with supporting evidence and quick verification steps.
  - Select the most likely hypothesis, propose 1–2 simple fix options (with trade-offs), and outline a minimal test plan (reproduction, verification, and one or two regression checks).

- **DeepDebug (`debug-deep.mdc`) – cross-module or high-impact issues**:
  - Use for multi-module, intermittent, or high-severity problems (including security and data integrity).
  - Classify severity (S0–S3) and restate the problem and scope (affected components, environments, and users).
  - Map domains involved (UI, backend, DB, networking, security, integrations, infra, observability) and describe request, data, and configuration flows across them.
  - Run "quick passes" for each relevant domain module to generate domain-specific hypotheses, then synthesize them into a ranked global hypothesis list.
  - Deep-dive on the top hypotheses, confirm/refute them with code, logs, traces, and data checks, converge on a likely root cause, and produce:
    - A preferred solution (plus alternatives with risk/trade-off analysis).
    - An implementation outline across modules.
    - A validation and regression plan, and a brief RCA-style summary with prevention steps (tests, alerts, guidelines, docs updates).

Use DebugFast by default; escalate to DeepDebug when evidence indicates cross-cutting behavior, high impact, or security/compliance implications.
