# Product Requirements Document: SentraScan Platform Enhancements

## Introduction/Overview

This PRD outlines enhancements to the SentraScan Platform to improve UI/UX, add comprehensive logging and telemetry, optimize container size, enhance security, and improve API key management. The goal is to transform the platform into a modern, enterprise-ready security scanning solution with better observability and user experience.

**Problem Statement:** The current platform needs improvements in UI presentation, lacks comprehensive logging/telemetry, includes unnecessary dependencies (ZAP) that increase container size, and requires better security hardening for production deployments.

**Goal:** Enhance the platform's UI, add observability capabilities, reduce container footprint, improve security posture, and provide better API key management with session persistence.

## Goals

1. **UI Enhancement:** Modernize the user interface to be professional, clean, and enterprise-ready with improved layout and comprehensive findings display
2. **Observability:** Implement comprehensive logging and telemetry for all platform events
3. **Container Optimization:** Reduce container size by removing ZAP and test dependencies from production builds
4. **Security Hardening:** Implement container masking/protection for production deployments
5. **API Key Management:** Improve API key generation, naming, and session persistence
6. **Multi-Tenancy:** Support for multiple organizations or tenants with data isolation
7. **User Management & RBAC:** Implement basic user management and simple role-based access control with multi-tenancy support
8. **Advanced Analytics:** Provide complex analytics dashboards and machine learning-based insights

## User Stories

1. **As a security analyst**, I want to see all scan findings aggregated and displayed with clear details (severity, category, scanner, remediation) so that I can quickly identify and address security issues.

2. **As a platform administrator**, I want comprehensive logging and telemetry so that I can monitor system health, debug issues, and track usage patterns.

3. **As a DevOps engineer**, I want smaller container images without unnecessary dependencies so that I can deploy faster and reduce resource consumption.

4. **As a security-conscious user**, I want production containers to be protected from unauthorized access so that sensitive code and data cannot be easily inspected.

5. **As a developer**, I want API keys to have meaningful names and be preserved across sessions so that I can easily manage and use them.

6. **As a user**, I want a modern, professional UI with properly sized statistics cards and a complete footer so that the platform looks enterprise-ready.

7. **As an organization administrator**, I want to manage multiple tenants/organizations with complete data isolation so that each organization's data remains private and secure.

8. **As a platform administrator**, I want to manage users and assign roles (admin, viewer, etc.) within each tenant so that I can control access appropriately.

9. **As a security analyst**, I want advanced analytics dashboards with ML-based insights so that I can identify patterns, trends, and anomalies in security findings.

10. **As a tenant user**, I want to see only data from my organization so that I cannot accidentally access other organizations' sensitive information.

11. **As a tenant administrator**, I want to configure tenant-specific policies, scanner settings, and severity thresholds so that scans align with my organization's security requirements.

12. **As a security officer**, I want assurance that tenant data is encrypted at rest and stored in separate database shards so that data breaches are contained and data is protected.

13. **As a platform operator**, I want the platform to follow security best practices so that we can maintain compliance and protect customer data.

14. **As a new user**, I want comprehensive "How To" documentation and guides so that I can quickly learn how to use the platform effectively.

15. **As a user**, I want to access help documentation directly from the web application so that I don't need to search external resources.

## Functional Requirements

### UI Requirements

1. **Footer Copyright Update**
   - The footer must display "© 2025 SentraScan" (updated from 2024)
   - Copyright text must be visible in the footer section of all pages

2. **Statistics Cards Layout**
   - Statistics cards must be displayed in a single horizontal row
   - Cards must be smaller in size compared to current implementation
   - If more than 4 cards exist, additional cards must wrap to a second row
   - Cards must maintain responsive behavior on mobile devices

3. **API Key Naming and Generation**
   - The system must auto-generate API keys with format: `ss-proj-h_` + 147-character alphanumeric string (uppercase, lowercase, numbers) with exactly one random hyphen
   - Total length: 157 characters including prefix and hyphen
   - Example format: `ss-proj-h_AbC123xYz-456DeF789...`
   - Users must be able to optionally provide a custom name/label for API keys
   - API key generation must be secure and use cryptographically secure random generation
   - Generated keys must be displayed to the user immediately after creation

4. **Modern Enterprise UI**
   - The UI must follow the existing design system
   - The UI must include enhanced data tables for findings display
   - The UI must include charts/visualizations where appropriate
   - The UI must maintain a clean, professional, and enterprise-ready appearance
   - All UI components must be accessible (WCAG 2.1 AA compliant)

5. **Findings Display Enhancement**
   - The system must display findings from all scans in an aggregate view
   - The system must display findings per scan in detail view
   - Each finding must display:
     - Severity (Critical, High, Medium, Low)
     - Category
     - Scanner name
     - Remediation guidance
   - Findings must be filterable and sortable by all displayed attributes
   - Findings must support both aggregate and per-scan views with easy navigation between them

6. **How To / Documentation Page**
   - The web application must include a "How To" page accessible from the main navigation
   - The page must provide step-by-step guides for common tasks:
     - Getting started with SentraScan
     - Creating and managing API keys
     - Running scans (MCP and Model scans)
     - Understanding scan results and findings
     - Managing baselines
     - Configuring tenant settings
     - Using analytics dashboards
     - Troubleshooting common issues
   - The page must include:
     - Table of contents for easy navigation
     - Search functionality to find specific topics
     - Visual guides with screenshots or diagrams where helpful
     - Code examples for API usage
     - Links to related topics
     - Print-friendly format
   - The page must be accessible (WCAG 2.1 AA compliant)
   - The page must be responsive and work on mobile devices
   - Documentation must be kept up-to-date with platform features

### Functional Requirements

1. **Logging and Telemetry**
   - The system must implement structured logging (JSON format) to stdout/stderr
   - Telemetry must be OTEL (OpenTelemetry) compliant and stored locally (no external backend initially)
   - Logs must be stored in local log files within the container (`/app/logs` directory)
   - Log retention: 7 days active, then archived automatically
   - The system must log all events with appropriate log levels:
     - **INFO:** Scan start/end, API calls, successful operations
     - **DEBUG:** Detailed execution flow, intermediate states
     - **ERROR:** Exceptions, failures, validation errors
     - **WARNING:** Deprecation notices, configuration issues
   - Logs must include:
     - Timestamp
     - Log level
     - Event type
     - User/API key identifier (when applicable)
     - Request/response details (for API calls)
     - Error stack traces (for errors)
   - Telemetry must be configurable via environment variables (`TELEMETRY_ENABLED`, `OTEL_EXPORTER_TYPE`)
   - Logging must not expose sensitive information (API keys, passwords)

2. **ZAP Removal**
   - OWASP ZAP must be removed from the main Dockerfile
   - ZAP-related code in `src/sentrascan/modules/mcp/zap.py` must be removed or made optional
   - ZAP references in `src/sentrascan/modules/mcp/scanner.py` must be removed
   - Container size reduction must be documented

3. **Production Container Cleanup**
   - Test files (`tests/` directory) must not be included in production container builds
   - Test dependencies (pytest, pytest-playwright, requests for testing) must be removed from production builds
   - Playwright browsers must not be installed in production containers
   - A separate production Dockerfile must be created or the existing Dockerfile must be modified to exclude test artifacts
   - The production container must be clean and minimal

4. **API Key Session Persistence**
   - When a user logs in with an API key, the key must be preserved in the session
   - The session must persist across page navigations
   - The session must expire after a configurable timeout (default: 48 hours)
   - Users must be able to view their current API key in the UI
   - Session management must use secure, signed cookies

5. **Container Masking/Protection (Production Only)**
    - Production containers must require a specific key/password (`Sentrascan@25!`) to access the container shell
    - SSH/console access must be disabled or protected by the key
    - This protection must apply only to production containers (not development)
    - The protection mechanism must prevent unauthorized exploration of container contents
    - The key must be configurable at build time via build argument or environment variable

6. **Multi-Tenancy Support**
    - The system must support multiple organizations/tenants
    - Each tenant must have complete data isolation (scans, findings, baselines, API keys)
    - All database queries must be scoped to the current tenant
    - Tenant context must be determined from user/API key association
    - Users and API keys must be associated with a specific tenant
    - Cross-tenant data access must be prevented at the application layer

7. **User Management**
    - The system must support user accounts with email/password authentication
    - Users must be associated with a tenant/organization
    - Users must have a display name and email address
    - Users must be able to change their password
    - System administrators must be able to create, update, and deactivate users
    - User accounts must support soft deletion (deactivated, not deleted)

8. **Role-Based Access Control (RBAC)**
    - The system must support the following roles:
      - **Super Admin:** Full access across all tenants (platform-level)
      - **Tenant Admin:** Full access within a specific tenant
      - **Viewer:** Read-only access within a tenant
      - **Scanner:** Can trigger scans but limited read access
    - Roles must be assigned at the tenant level
    - API keys must inherit roles from their associated user
    - Role checks must be enforced at the API endpoint level
    - UI must display/hide features based on user role

9. **Advanced Analytics Dashboards**
    - The system must provide analytics dashboards with:
      - Trend analysis (findings over time)
      - Severity distribution charts
      - Scanner effectiveness metrics
      - Remediation progress tracking
      - Risk scoring and prioritization
    - Dashboards must support time range filtering
    - Dashboards must be tenant-scoped (show only current tenant data)
    - Analytics must support export functionality (CSV, JSON, PDF)

10. **Machine Learning-Based Insights**
    - The system must provide ML-based insights such as:
      - Anomaly detection in scan results
      - Predictive risk scoring
      - Finding correlation analysis
      - Remediation recommendation prioritization
    - ML models must NOT learn from customer data
    - ML models must use pre-trained models or synthetic data only
    - ML insights must be clearly labeled and explainable
    - ML features must be optional and can be disabled
    - No customer data must be used for model training or improvement

11. **Tenant-Specific Settings**
    - Each tenant must have configurable settings for:
      - **Policy Settings:** Custom policy rules, gate thresholds, pass/fail criteria
      - **Scanner Settings:** Enable/disable specific scanners, scanner timeouts, scanner configurations
      - **Severity Settings:** Custom severity mappings, severity thresholds, severity-based actions
      - **Notification Settings:** Alert thresholds, notification channels, notification preferences
      - **Scan Settings:** Default scan parameters, scan schedules, scan retention policies
      - **Integration Settings:** External tool integrations, webhook configurations
    - Settings must be tenant-scoped and isolated
    - Settings must have default values that can be overridden per tenant
    - Tenant admins must be able to manage their tenant's settings
    - Settings must be stored securely and validated on save
    - Settings changes must be logged for audit purposes

12. **Database Sharding for Tenant Isolation**
    - The database must implement sharding to physically separate tenant data
    - Each tenant must have data stored in separate database shards or schemas
    - Sharding strategy must prevent cross-tenant data access at the database level
    - Shard routing must be based on tenant_id
    - Database queries must automatically route to the correct shard
    - Sharding must support horizontal scaling (adding new shards)
    - Shard management must be transparent to the application layer
    - Sharding configuration must be stored securely and not exposed to tenants

13. **Encryption at Rest**
    - All tenant data must be encrypted at rest in the database
    - Encryption must use industry-standard encryption algorithms (AES-256)
    - Each tenant must have tenant-specific encryption keys
    - Encryption keys must be managed securely (key rotation, key storage)
    - Database backups must also be encrypted
    - Encryption must be transparent to the application (automatic encryption/decryption)
    - Encryption keys must never be stored in the database or application code
    - Key management must support key rotation without downtime

14. **Platform Security Best Practices**
    - The platform must implement comprehensive security measures:
      - **Authentication & Authorization:** Multi-factor authentication (MFA) support, secure password policies, session management
      - **Data Protection:** Encryption in transit (TLS 1.3), encryption at rest, data masking in logs
      - **API Security:** Rate limiting, API key rotation, request validation, input sanitization
      - **Network Security:** Network segmentation, firewall rules, DDoS protection
      - **Application Security:** Input validation, SQL injection prevention, XSS protection, CSRF protection
      - **Container Security:** Non-root user, minimal base images, security scanning, vulnerability management
      - **Secrets Management:** Secure storage of API keys, passwords, encryption keys (use secrets manager)
      - **Audit Logging:** Comprehensive audit trail of all security-relevant events
      - **Vulnerability Management:** Regular security updates, dependency scanning, patch management
      - **Compliance:** Support for SOC 2, ISO 27001, GDPR compliance requirements
    - Security controls must be documented and regularly reviewed
    - Security incidents must be logged and monitored
    - Regular security audits and penetration testing must be conducted

15. **User Documentation (Markdown)**
    - The platform must include comprehensive markdown documentation for users
    - Documentation must be stored in `/docs` directory (or similar) and accessible via web
    - Documentation must cover:
      - **Getting Started Guide:** Installation, first login, initial setup
      - **User Guide:** Complete platform usage instructions
      - **API Documentation:** API endpoints, authentication, request/response formats, examples
      - **How To Guides:** Step-by-step instructions for common tasks
      - **Troubleshooting Guide:** Common issues and solutions
      - **FAQ:** Frequently asked questions
      - **Best Practices:** Recommended workflows and security practices
      - **Glossary:** Definitions of key terms and concepts
    - Documentation must be:
      - Written in clear, concise language suitable for junior developers
      - Include code examples and screenshots where appropriate
      - Organized with clear headings and table of contents
      - Searchable and indexed
      - Version-controlled alongside the codebase
      - Available in both web UI and as downloadable markdown files
    - Documentation must be rendered in the web application with:
      - Syntax highlighting for code blocks
      - Proper markdown rendering (headers, lists, tables, links)
      - Navigation sidebar for easy browsing
      - Search functionality
      - Print-friendly CSS
    - Documentation must be kept synchronized with platform features
    - Documentation updates must be part of the release process

## Implementation Phases

To manage complexity and ensure successful delivery, the implementation will be divided into phases:

### Phase 1: Foundation & Critical Updates (Must Have)
**Goal:** Establish foundation and address critical improvements
**Duration:** 4-6 weeks

**Requirements:**
- UI-1: Footer Copyright Update
- UI-2: Statistics Cards Layout
- UI-3: API Key Naming and Generation
- FR-1: Logging and Telemetry (local storage)
- FR-2: ZAP Removal
- FR-3: Production Container Cleanup
- FR-4: API Key Session Persistence
- FR-5: Container Masking/Protection

**Deliverables:**
- Updated UI with improved layout
- Comprehensive logging system
- Optimized production containers
- Enhanced API key management

### Phase 2: Multi-Tenancy & User Management (Must Have)
**Goal:** Enable multi-tenant architecture and user management
**Duration:** 6-8 weeks

**Requirements:**
- FR-6: Multi-Tenancy Support
- FR-7: User Management
- FR-8: Role-Based Access Control (RBAC)
- UI-5: Multi-Tenancy UI
- UI-6: User Management UI

**Dependencies:** Phase 1 complete

**Deliverables:**
- Multi-tenant data isolation
- User authentication and management
- Role-based access control
- Tenant management UI

### Phase 3: Security & Data Protection (Must Have)
**Goal:** Implement enterprise-grade security
**Duration:** 4-6 weeks

**Requirements:**
- FR-12: Database Sharding
- FR-13: Encryption at Rest
- FR-14: Platform Security Best Practices

**Dependencies:** Phase 2 complete

**Deliverables:**
- Database sharding implementation
- Encryption at rest
- Comprehensive security controls

### Phase 4: Analytics & Advanced Features (Should Have)
**Goal:** Add analytics and ML capabilities
**Duration:** 4-6 weeks

**Requirements:**
- FR-9: Advanced Analytics Dashboards
- FR-10: Machine Learning-Based Insights
- FR-11: Tenant-Specific Settings
- UI-7: Analytics Dashboard UI

**Dependencies:** Phase 2 complete

**Deliverables:**
- Analytics dashboards
- ML-based insights
- Tenant-specific configuration

### Phase 5: Documentation & Polish (Nice to Have)
**Goal:** Complete documentation and final polish
**Duration:** 2-4 weeks

**Requirements:**
- UI-6: How To / Documentation Page
- FR-15: User Documentation (Markdown)
- UI-5: Findings Display Enhancement (if not completed earlier)

**Dependencies:** All previous phases

**Deliverables:**
- Complete user documentation
- How-to guides
- Platform polish

## Testing Requirements

### Unit Testing

1. **Coverage Requirements:**
   - Minimum 80% code coverage for new code
   - 100% coverage for critical security functions
   - All API endpoints must have unit tests
   - All database operations must have unit tests

2. **Test Categories:**
   - **Unit Tests:** Individual functions and methods
   - **Service Tests:** Business logic and services
   - **Model Tests:** Database models and relationships
   - **Utility Tests:** Helper functions and utilities

3. **Test Framework:**
   - Use pytest for Python tests
   - Use Jest or similar for JavaScript tests
   - Mock external dependencies
   - Use fixtures for test data

### Integration Testing

1. **API Integration Tests:**
   - Test all API endpoints with valid/invalid inputs
   - Test authentication and authorization
   - Test tenant isolation
   - Test error handling and error responses
   - Test rate limiting

2. **Database Integration Tests:**
   - Test database schema initialization
   - Test shard routing
   - Test encryption/decryption
   - Test data isolation between tenants
   - Test transaction handling

3. **External Service Integration Tests:**
   - Test key management system integration
   - Test logging system integration
   - Mock external services for testing

### End-to-End (E2E) Testing

1. **User Flows:**
   - User registration and login
   - API key creation and usage
   - Scan creation and execution
   - Findings viewing and filtering
   - Tenant settings configuration
   - User management workflows

2. **Multi-Tenant Scenarios:**
   - Tenant isolation verification
   - Cross-tenant access prevention
   - Tenant-specific settings
   - Tenant data encryption

3. **E2E Test Framework:**
   - Use Playwright or Selenium for browser automation
   - Test critical user journeys
   - Test on multiple browsers (Chrome, Firefox, Safari)
   - Test responsive design on mobile devices

### Security Testing

1. **Authentication & Authorization Tests:**
   - Test password policies
   - Test MFA implementation
   - Test session management
   - Test role-based access control
   - Test API key validation

2. **Security Vulnerability Tests:**
   - SQL injection prevention
   - XSS prevention
   - CSRF protection
   - Input validation
   - Output encoding

3. **Penetration Testing:**
   - External penetration testing (quarterly)
   - Internal security audits
   - Dependency vulnerability scanning
   - Container security scanning

4. **Data Protection Tests:**
   - Encryption at rest verification
   - Encryption in transit verification
   - Data masking in logs
   - Secure data deletion

### Performance Testing

1. **Load Testing:**
   - Test API endpoints under load (1000+ concurrent requests)
   - Test database queries under load
   - Test shard routing performance
   - Test encryption/decryption performance impact

2. **Stress Testing:**
   - Test system limits (max tenants, max users, max scans)
   - Test memory usage under stress
   - Test CPU usage under stress
   - Test database connection pooling

3. **Performance Benchmarks:**
   - API response time: <200ms for 95th percentile
   - Database query time: <100ms for 95th percentile
   - Page load time: <2 seconds
   - Scan execution time: within configured timeout

### Regression Testing

1. **Automated Regression Suite:**
   - Run full test suite before each release
   - Test all critical user flows
   - Test all API endpoints
   - Test database schema initialization

2. **Manual Regression Testing:**
   - Test new features manually
   - Test UI changes across browsers
   - Test accessibility features
   - Test documentation accuracy

### Test Data Management

1. **Test Data Requirements:**
   - Use realistic test data
   - Include edge cases and boundary conditions
   - Include invalid data for negative testing
   - Maintain test data separate from production

2. **Test Environment:**
   - Separate test environment matching production
   - Test database with representative data
   - Test containers with production-like configuration
   - Test key management system (staging)

## Quality Aspects

### Code Quality

1. **Code Standards:**
   - Follow PEP 8 for Python code
   - Follow ESLint/Prettier for JavaScript code
   - Use type hints in Python
   - Use TypeScript for JavaScript where possible
   - Consistent naming conventions

2. **Code Review Requirements:**
   - All code must be reviewed before merge
   - Minimum 2 reviewers for security-related changes
   - Automated code quality checks (linting, formatting)
   - Code coverage checks in CI/CD

3. **Documentation Quality:**
   - All functions must have docstrings
   - Complex logic must have inline comments
   - API endpoints must have OpenAPI documentation
   - Architecture decisions must be documented (ADRs)

### Performance Quality

1. **Performance Targets:**
   - API response time: <200ms (95th percentile)
   - Page load time: <2 seconds
   - Database query time: <100ms (95th percentile)
   - Scan execution: within configured timeout

2. **Resource Usage:**
   - Memory usage: monitor and optimize
   - CPU usage: efficient algorithms
   - Database connections: connection pooling
   - Container size: minimize image size

3. **Scalability:**
   - Support horizontal scaling
   - Database sharding for scale
   - Caching for frequently accessed data
   - Background jobs for heavy operations

### Reliability Quality

1. **Availability:**
   - Target uptime: 99.9% (SLA)
   - Health check endpoints
   - Graceful degradation on errors
   - Automatic failover where applicable

2. **Error Handling:**
   - Comprehensive error handling
   - User-friendly error messages
   - Error logging and monitoring
   - Error recovery mechanisms

3. **Data Integrity:**
   - Database transactions for critical operations
   - Data validation at all layers
   - Backup and recovery procedures
   - Data consistency checks

### Security Quality

1. **Security Standards:**
   - OWASP Top 10 compliance
   - Regular security audits
   - Dependency vulnerability scanning
   - Security code reviews

2. **Compliance:**
   - SOC 2 Type II compliance
   - ISO 27001 compliance
   - GDPR compliance
   - Regular compliance audits

3. **Security Monitoring:**
   - Real-time security monitoring
   - Anomaly detection
   - Security incident response
   - Security metrics dashboard

### Usability Quality

1. **User Experience:**
   - Intuitive user interface
   - Clear error messages
   - Helpful tooltips and guidance
   - Consistent design patterns

2. **Accessibility:**
   - WCAG 2.1 AA compliance
   - Keyboard navigation support
   - Screen reader compatibility
   - Color contrast compliance

3. **Documentation Quality:**
   - Clear, concise documentation
   - Step-by-step guides
   - Code examples
   - Troubleshooting guides

### Maintainability Quality

1. **Code Maintainability:**
   - Modular code structure
   - Clear separation of concerns
   - Reusable components
   - Well-organized codebase

2. **Technical Debt:**
   - Regular technical debt reviews
   - Refactoring as needed
   - Deprecation of old code
   - Documentation updates

3. **Monitoring & Observability:**
   - Comprehensive logging
   - Application metrics
   - Performance monitoring
   - Error tracking

## Non-Goals (Out of Scope)

1. **UI Redesign:** Complete redesign of the UI - we are enhancing the existing design system, not replacing it
2. **New Scanning Capabilities:** Adding new scanner types or scanning features beyond what exists
3. **Real-time Collaboration:** Real-time updates or collaborative features
4. **Mobile Applications:** Native mobile apps (responsive web UI is sufficient)
5. **ZAP Alternative:** Implementing a replacement for ZAP functionality
6. **Development Container Changes:** Container protection applies only to production, not development containers
7. **External Log Storage:** Sending logs to external storage services (logs stored locally only)
8. **Complex RBAC:** Advanced permission models with fine-grained permissions (simple role-based model is sufficient)

## Design Considerations

### UI Components

1. **Statistics Cards:**
   - Use CSS Grid with `grid-template-columns: repeat(4, 1fr)` for 4 cards per row
   - Reduce card padding and font sizes to make cards more compact
   - Maintain card hover states and accessibility features
   - Ensure responsive breakpoints for mobile (stack cards vertically on small screens)

2. **Findings Display:**
   - Use enhanced data tables with sorting, filtering, and pagination
   - Implement severity badges with color coding
   - Add expandable rows for finding details
   - Include charts for severity distribution
   - Provide export functionality (CSV, JSON)

3. **Footer:**
   - Update copyright year to 2025
   - Maintain existing footer structure and styling
   - Ensure footer is visible on all pages

4. **API Key Management UI:**
   - Add API key creation form with optional name field
   - Display generated keys in a secure manner (masked with reveal option)
   - Show API key list with names, creation dates, and status
   - Include copy-to-clipboard functionality
   - API key names must follow validation: alphanumeric, uppercase, lowercase, one hyphen allowed
   - Display tenant context in API key management UI

5. **Multi-Tenancy UI:**
   - Add tenant selector/switcher in header (for users with multiple tenant access)
   - Display current tenant name in navigation
   - Show tenant-scoped statistics and data
   - Tenant creation/management UI (for super admins)

6. **User Management UI:**
   - User list view (tenant-scoped)
   - User creation form (email, name, role, password)
   - User edit form (update name, role, password reset)
   - User deactivation (soft delete)
   - Role assignment interface

7. **Analytics Dashboard UI:**
   - Interactive charts using Chart.js or similar
   - Time range selector (last 7 days, 30 days, 90 days, custom)
   - Severity trend charts
   - Scanner effectiveness metrics
   - Risk score visualization
   - Export buttons (CSV, JSON, PDF)
   - ML insights panel (if ML features enabled)

8. **How To / Documentation Page UI:**
   - Add "How To" or "Documentation" link in main navigation (header)
   - Create dedicated documentation page route (`/docs` or `/how-to`)
   - Implement documentation viewer with:
     - Left sidebar navigation (table of contents)
     - Main content area with markdown rendering
     - Search bar at the top
     - Breadcrumb navigation
     - "Edit on GitHub" or "Report Issue" links (if applicable)
     - Print button
     - Mobile-responsive layout (collapsible sidebar on mobile)
   - Use markdown rendering library (e.g., marked.js, markdown-it)
   - Implement syntax highlighting for code blocks (e.g., Prism.js, highlight.js)
   - Style documentation with readable typography and spacing
   - Include anchor links for headings (for deep linking)
   - Support for embedded images, videos, or diagrams
   - Dark mode support (if platform has dark mode)

### Design System Compliance

- Follow existing CSS variables and design tokens
- Maintain color scheme and typography
- Use existing component patterns where possible
- Ensure accessibility standards are met

## Technical Considerations

### Logging Implementation

1. **Structured Logging:**
   - Use Python's `structlog` or `python-json-logger` for JSON formatting
   - Configure log levels via environment variable (`LOG_LEVEL`)
   - Implement log rotation and size limits
   - Logs must be stored in local log files within the container
   - Log retention: 7 days active, then archived
   - Log archiving must be automatic (compress old logs)
   - Log files must be stored in `/app/logs` directory

2. **Telemetry Integration:**
   - Telemetry must be OTEL (OpenTelemetry) compliant
   - Telemetry data must be stored locally (no external backend initially)
   - Telemetry must support OTEL standard formats (traces, metrics, logs)
   - Configuration via environment variables:
     - `TELEMETRY_ENABLED=true/false`
     - `OTEL_EXPORTER_TYPE=file|console` (file for local storage)
   - Telemetry data must be stored in structured format alongside logs

3. **Log Events to Capture:**
   - Authentication events (login, logout, API key validation)
   - Scan lifecycle (start, progress, completion, failure)
   - API requests (endpoint, method, status code, duration)
   - Database operations (queries, errors)
   - System events (startup, shutdown, health checks)

### Container Optimization

1. **ZAP Removal:**
   - Remove ZAP installation steps from Dockerfile
   - Remove ZAP-related environment variables
   - Update `docker-compose.yml` to remove ZAP service (or make it optional)
   - Keep ZAP code as optional/disabled rather than deleting (for future use if needed)

2. **Production Dockerfile:**
   - Create multi-stage build with separate test stage
   - Remove `tests/` directory copy in production stage
   - Remove test dependencies from production requirements
   - Remove Playwright browser installation
   - Use `.dockerignore` to exclude test files

3. **Container Protection:**
   - Use industry best practices for container security:
     - Use distroless or minimal base images (already using distroless in Dockerfile.protected)
     - Remove shell and unnecessary tools from production images
     - Use read-only filesystem where possible
     - Run as non-root user (already implemented)
     - Use build-time secrets for access keys (not runtime environment variables)
   - Container access key must be set at build time via build argument
   - Access key default: `Sentrascan@25!` (configurable at build time)
   - Document the protection mechanism and access procedures
   - Consider using Docker secrets or build-time arguments for key management

### API Key Management

1. **Key Generation:**
   - Use `secrets.token_urlsafe()` or similar for secure generation
   - Format: `ss-proj-h_` + 147-character alphanumeric string (uppercase, lowercase, numbers)
   - The 147-character string must include exactly one random hyphen (-) character
   - Example format: `ss-proj-h_AbC123xYz-456DeF789...` (total 157 characters including prefix and hyphen)
   - Store hashed version in database (existing `hash_key` method)
   - Display full key only once during creation

2. **Session Management:**
   - Use signed cookies (existing `sign`/`unsign` functions)
   - Store API key hash in session cookie
   - Implement session timeout (configurable, default 48 hours)
   - Add session refresh on activity

3. **Database Schema:**
   - Ensure `APIKey.name` field is used for custom names
   - Add validation for name length and format
   - Consider adding `last_used_at` timestamp for tracking

### Findings Display

1. **Aggregate View:**
   - Query all findings across all scans (tenant-scoped)
   - Perform aggregation in application layer (not database)
   - Group by severity, category, or scanner
   - Provide summary statistics
   - Support filtering and sorting
   - Implement pagination for large datasets

2. **Per-Scan View:**
   - Maintain existing scan detail page
   - Enhance with better table features
   - Add navigation between aggregate and detail views

3. **Data Model:**
   - Existing `Finding` model has all required fields
   - Ensure `remediation` field is populated by scanners
   - Add indexes for performance on large datasets
   - Add `tenant_id` foreign key to all tenant-scoped tables:
     - `scans` table: add `tenant_id` column
     - `findings` table: add `tenant_id` column (or inherit from scan)
     - `api_keys` table: add `tenant_id` column
     - `baselines` table: add `tenant_id` column
     - `sboms` table: add `tenant_id` column
   - Create new `tenants` table with: `id`, `name`, `created_at`, `is_active`
   - Create new `users` table with: `id`, `email`, `password_hash`, `name`, `tenant_id`, `role`, `created_at`, `is_active`
   - Add foreign key constraints to enforce referential integrity

## Success Metrics

1. **UI Metrics:**
   - Footer displays "© 2025 SentraScan" on all pages
   - Statistics cards display in single row (4 cards) on desktop
   - All findings display with required details (severity, category, scanner, remediation)
   - UI accessibility score maintains WCAG 2.1 AA compliance

2. **Logging Metrics:**
   - 100% of critical events (scan start/end, errors) are logged
   - Logs are structured (JSON format) and parseable
   - Logs are stored locally in log files
   - Log retention: 7 days active, then archived
   - Telemetry is OTEL compliant
   - Zero sensitive data exposure in logs

3. **Container Metrics:**
   - Container size reduction of at least 200MB (ZAP removal)
   - Production container excludes all test files and dependencies
   - Production container protection is active and requires key for access

4. **API Key Metrics:**
   - API keys follow format: `ss-proj-h_` + 147-character alphanumeric string with one hyphen
   - API keys can be generated with auto-generated and custom names
   - Sessions persist API keys across page navigations
   - Session timeout works as configured (default 48 hours)

5. **Multi-Tenancy Metrics:**
   - Complete data isolation between tenants (zero cross-tenant data leakage)
   - All queries are tenant-scoped
   - Users can only access their assigned tenant(s)
   - API keys are tenant-scoped

6. **User Management & RBAC Metrics:**
   - Users can be created, updated, and deactivated
   - Roles are enforced at API and UI level
   - Role-based access control prevents unauthorized actions
   - User authentication works with email/password

7. **Analytics Metrics:**
   - Analytics dashboards load within 3 seconds
   - Charts render correctly with tenant-scoped data
   - ML insights are generated (if enabled) without using customer data
   - Export functionality works for all formats

8. **Tenant Settings Metrics:**
   - Tenant-specific settings are isolated and cannot affect other tenants
   - Settings changes are applied correctly
   - Settings are persisted securely
   - Audit logs capture all settings changes

9. **Database Security Metrics:**
   - Zero cross-tenant data access incidents
   - All tenant data is encrypted at rest
   - Database sharding prevents physical data access between tenants
   - Encryption keys are rotated regularly
   - Database backups are encrypted

10. **Platform Security Metrics:**
    - Zero critical security vulnerabilities in production
    - All security controls are active and monitored
    - Security incidents are logged and responded to within SLA
    - Compliance requirements are met
    - Regular security audits pass

11. **Documentation Metrics:**
    - "How To" page is accessible from main navigation
    - Documentation page loads within 2 seconds
    - All documentation topics are covered (getting started, user guide, API, how-to, troubleshooting, FAQ)
    - Documentation search returns results within 500ms
    - Documentation is kept up-to-date (reviewed quarterly)
    - User feedback indicates documentation is helpful (survey or feedback mechanism)
    - Documentation is accessible (WCAG 2.1 AA compliant)
    - Markdown files are properly formatted and render correctly

12. **Performance Metrics:**
   - No performance degradation from logging overhead (<5% impact)
   - Findings display loads within 2 seconds for up to 1000 findings
   - Container build time does not increase significantly
   - Documentation page renders within 2 seconds

## Open Questions - Resolved

1. **Telemetry Backend Priority:** ✅ **RESOLVED** - Telemetry backend will not be available initially. Logs should be stored locally in log files. Telemetry must be OTEL compliant for future integration.

2. **Session Timeout Default:** ✅ **RESOLVED** - Session timeout default should be 48 hours (updated from 24 hours).

3. **API Key Naming Validation:** ✅ **RESOLVED** - API key format: `ss-proj-h_` followed by 147-character alphanumeric string (uppercase, lowercase, numbers) with exactly one random hyphen. Total length: 157 characters including prefix and hyphen.

4. **Container Protection Method:** ✅ **RESOLVED** - Use industry best practices: distroless images, read-only filesystem where possible, non-root user, build-time secrets. Container access key must be set at build time (not runtime).

5. **Findings Aggregation Performance:** ✅ **RESOLVED** - Aggregation should be done in the application layer (not database). Pagination should be implemented for large datasets.

6. **ZAP Removal Impact:** ✅ **RESOLVED** - No impact. ZAP removal can proceed without notifying existing users.

7. **Log Retention:** ✅ **RESOLVED** - Logs should be retained for 7 days in container and should be archived. Sending externally is not in scope.

8. **Container Access Key Management:** ✅ **RESOLVED** - Container access key should be set at build time (not changeable at runtime).

---

## Additional Technical Considerations

### Multi-Tenancy Implementation

1. **Database Schema Changes:**
   - Add `tenants` table: `id` (UUID), `name` (string), `created_at` (timestamp), `is_active` (boolean), `settings` (JSON)
   - Add `tenant_settings` table: `id` (UUID), `tenant_id` (FK), `setting_key` (string), `setting_value` (JSON), `updated_at` (timestamp), `updated_by` (FK to users)
   - Add `users` table: `id` (UUID), `email` (string, unique per tenant), `password_hash` (string), `name` (string), `tenant_id` (FK), `role` (enum), `created_at` (timestamp), `is_active` (boolean), `mfa_enabled` (boolean), `mfa_secret` (encrypted)
   - Add `tenant_id` column to: `scans`, `findings`, `api_keys`, `baselines`, `sboms`
   - Add database indexes on `tenant_id` columns for performance
   - Add `audit_logs` table: `id` (UUID), `tenant_id` (FK), `user_id` (FK), `action` (string), `resource_type` (string), `resource_id` (string), `details` (JSON), `ip_address` (string), `timestamp` (timestamp)

2. **Database Sharding:**
   - Implement database sharding strategy (schema-based or table-based)
   - Each tenant's data must be stored in separate database schemas or shards
   - Shard routing must be based on `tenant_id` hash or direct mapping
   - Use connection pooling with shard-aware routing
   - Implement shard management API for adding/removing shards
   - Shard metadata must be stored securely (not in tenant-accessible tables)
   - Database queries must automatically route to correct shard based on tenant context
   - Support for shard management (adding/removing shards for new tenants)

3. **Encryption at Rest:**
   - Implement Transparent Data Encryption (TDE) or application-level encryption
   - Use AES-256 encryption for all tenant data
   - Each tenant must have tenant-specific encryption keys
   - Encryption keys must be stored in a secure key management system (e.g., HashiCorp Vault, AWS KMS, Azure Key Vault)
   - Implement key rotation mechanism (rotate keys periodically without downtime)
   - Database backups must be encrypted
   - Encryption must be transparent to application code (automatic encryption/decryption)
   - Key access must be logged and audited

4. **Application Layer:**
   - Implement tenant context middleware that extracts tenant from user/API key
   - All database queries must include tenant filter AND route to correct shard
   - API endpoints must validate tenant access before processing
   - UI must scope all data queries to current tenant
   - Implement tenant settings service for managing tenant-specific configurations
   - Settings must be cached for performance (with invalidation on update)

5. **Authentication:**
   - Support email/password authentication for users
   - Support Multi-Factor Authentication (MFA) - TOTP-based
   - API keys must be associated with a user (which has a tenant)
   - Session must store tenant context
   - Super admins can access multiple tenants (special handling)
   - Implement secure password policies (minimum length, complexity, expiration)
   - Implement account lockout after failed login attempts

6. **Tenant Settings Management:**
   - Create `TenantSettings` service for managing tenant configurations
   - Settings categories:
     - Policy: `policy_rules`, `gate_thresholds`, `pass_criteria`
     - Scanner: `enabled_scanners`, `scanner_timeouts`, `scanner_configs`
     - Severity: `severity_mappings`, `severity_thresholds`, `severity_actions`
     - Notifications: `alert_thresholds`, `notification_channels`, `notification_preferences`
     - Scan: `default_scan_params`, `scan_schedules`, `retention_policies`
     - Integration: `webhook_urls`, `external_tool_configs`
   - Settings must be validated before saving
   - Settings changes must trigger audit log entries
   - Settings must have JSON schema validation
   - Default settings must be provided for new tenants

### RBAC Implementation

1. **Role Definitions:**
   - **Super Admin:** Can access all tenants, manage tenants, manage all users
   - **Tenant Admin:** Can manage users within tenant, create API keys, trigger scans, view all data
   - **Viewer:** Can view scans, findings, baselines (read-only)
   - **Scanner:** Can trigger scans, view limited data

2. **Permission Enforcement:**
   - Decorator-based role checking on API endpoints
   - UI component visibility based on role
   - Database query filtering based on role (e.g., viewers can't see certain fields)

### Analytics & ML Implementation

1. **Analytics Engine:**
   - Use Python libraries: pandas for data processing, Chart.js for visualization
   - Implement time-series analysis for trends
   - Calculate metrics: pass rate, finding velocity, remediation rate
   - Support real-time and historical data analysis

2. **ML Integration:**
   - Use scikit-learn or similar for ML models
   - Implement anomaly detection using statistical methods
   - Risk scoring based on finding patterns
   - **CRITICAL:** ML models must NOT learn from customer data
   - ML models must use pre-trained models, synthetic data, or public datasets only
   - No customer scan data, findings, or configurations must be used for training
   - ML features must be clearly marked and explainable
   - ML inference must be tenant-scoped (results per tenant, but no training on tenant data)

3. **Performance:**
   - Cache analytics results for frequently accessed dashboards
   - Use background jobs for heavy ML computations
   - Limit ML processing to prevent resource exhaustion

### Security Best Practices Implementation

1. **Authentication & Authorization:**
   - Implement MFA support using TOTP (Time-based One-Time Password)
   - Enforce strong password policies (min 12 chars, complexity requirements)
   - Implement password expiration and rotation policies
   - Use secure session management (HTTP-only, secure cookies, SameSite)
   - Implement account lockout after 5 failed login attempts
   - Use bcrypt or Argon2 for password hashing (never plain text)
   - Implement OAuth 2.0 / SAML support for enterprise SSO (future)

2. **Data Protection:**
   - **Encryption in Transit:** TLS 1.3 for all communications, certificate pinning
   - **Encryption at Rest:** AES-256 encryption for all tenant data (see Encryption at Rest section)
   - **Data Masking:** Mask sensitive data in logs (API keys, passwords, PII)
   - **Data Retention:** Implement data retention policies per tenant
   - **Data Deletion:** Secure data deletion (crypto-shredding for encrypted data)

3. **API Security:**
   - Implement rate limiting (per API key, per IP, per tenant)
   - API key rotation and expiration policies
   - Request size limits and timeout limits
   - Input validation and sanitization (prevent injection attacks)
   - Output encoding (prevent XSS)
   - CORS configuration (restrict origins)
   - API versioning and deprecation policies

4. **Network Security:**
   - Network segmentation (separate networks for different tiers)
   - Firewall rules (whitelist approach)
   - DDoS protection (rate limiting, IP blocking)
   - VPN/Private network support for database access
   - Network monitoring and intrusion detection

5. **Application Security:**
   - **Input Validation:** Validate and sanitize all inputs
   - **SQL Injection Prevention:** Use parameterized queries, ORM with proper escaping
   - **XSS Prevention:** Output encoding, Content Security Policy (CSP)
   - **CSRF Protection:** CSRF tokens, SameSite cookies
   - **Security Headers:** HSTS, X-Frame-Options, X-Content-Type-Options, CSP
   - **Dependency Management:** Regular dependency updates, vulnerability scanning
   - **Code Security:** Static code analysis, security code reviews

6. **Container Security:**
   - Use distroless or minimal base images
   - Run as non-root user (already implemented)
   - Read-only filesystem where possible
   - Container image scanning (vulnerability scanning)
   - Minimal attack surface (remove unnecessary tools)
   - Security scanning in CI/CD pipeline
   - Container runtime security (seccomp, AppArmor/SELinux profiles)

7. **Secrets Management:**
   - Use secrets management service (HashiCorp Vault, AWS Secrets Manager, Azure Key Vault)
   - Never store secrets in code, environment variables, or config files
   - Rotate secrets regularly
   - Use different secrets for different environments
   - Audit secret access
   - Encrypt secrets at rest

8. **Audit Logging:**
   - Log all security-relevant events:
     - Authentication (login, logout, failed attempts)
     - Authorization (permission denied events)
     - Data access (who accessed what data)
     - Configuration changes (settings, user management)
     - Administrative actions
   - Logs must include: timestamp, user, tenant, action, resource, IP address, result
   - Logs must be tamper-proof (append-only, cryptographic signatures)
   - Log retention: 90 days minimum, 1 year for compliance

9. **Vulnerability Management:**
   - Regular dependency scanning (weekly)
   - Container image scanning (on build)
   - Regular security updates (patch management)
   - Vulnerability disclosure process
   - Security bug bounty program (optional)
   - Regular penetration testing (quarterly)

10. **Compliance:**
    - SOC 2 Type II compliance support
    - ISO 27001 compliance support
    - GDPR compliance (data protection, right to deletion, data portability)
    - HIPAA compliance (if handling healthcare data)
    - Regular compliance audits
    - Compliance documentation and reporting

11. **Incident Response:**
    - Security incident response plan
    - Incident detection and alerting
    - Incident logging and tracking
    - Communication plan for security incidents
    - Post-incident review and improvement

12. **Security Monitoring:**
    - Real-time security monitoring
    - Anomaly detection (unusual access patterns)
    - Security alerting (SIEM integration)
    - Regular security reports
    - Security metrics dashboard

### Documentation Implementation

1. **Documentation Structure:**
   - Store markdown files in `/docs` directory in the repository
   - Organize documentation by topic:
     - `/docs/getting-started/` - Getting started guides
     - `/docs/user-guide/` - Complete user guide
     - `/docs/api/` - API documentation
     - `/docs/how-to/` - Step-by-step how-to guides
     - `/docs/troubleshooting/` - Troubleshooting guides
     - `/docs/faq/` - Frequently asked questions
     - `/docs/best-practices/` - Best practices and recommendations
     - `/docs/glossary/` - Glossary of terms
   - Use consistent markdown file naming (kebab-case, descriptive names)
   - Include `README.md` in each directory with overview

2. **Markdown Documentation Standards:**
   - Use standard markdown syntax (CommonMark specification)
   - Include frontmatter (YAML) for metadata (title, description, last updated)
   - Use consistent heading hierarchy (H1 for page title, H2 for main sections)
   - Include code blocks with language tags for syntax highlighting
   - Use tables for structured data
   - Include links to related documentation
   - Add "Last Updated" date to each document
   - Include version information if applicable

3. **Documentation Rendering:**
   - Use markdown rendering library (e.g., `marked`, `markdown-it`, `mistune` for Python)
   - Implement server-side rendering or client-side rendering (pre-render for performance)
   - Use syntax highlighting library (e.g., `Prism.js`, `highlight.js`, `pygments`)
   - Generate table of contents automatically from headings
   - Implement anchor links for all headings (for deep linking)
   - Support for markdown extensions:
     - Tables
     - Code blocks with syntax highlighting
     - Task lists (checkboxes)
     - Strikethrough
     - Autolinks

4. **Documentation API/Endpoint:**
   - Create API endpoint to serve documentation: `/api/v1/docs` or `/docs/api`
   - Create web UI endpoint: `/docs` or `/how-to`
   - Support for serving raw markdown files: `/docs/raw/{path}`
   - Support for downloading documentation as PDF (optional, future)
   - Implement caching for rendered documentation (performance)

5. **Documentation Search:**
   - Implement full-text search across all documentation
   - Index documentation content (use Elasticsearch, SQLite FTS, or similar)
   - Search must be fast (<500ms response time)
   - Highlight search terms in results
   - Support for search filters (by section, by type)

6. **Documentation Maintenance:**
   - Documentation must be version-controlled (in Git)
   - Documentation updates must be reviewed (code review process)
   - Link documentation updates to code changes (when features change)
   - Regular documentation audits (quarterly review)
   - User feedback mechanism for documentation improvements
   - Documentation versioning (if API changes, document version)

7. **Documentation Content Guidelines:**
   - Write for junior developers (clear, simple language)
   - Include practical examples (code snippets, screenshots)
   - Use step-by-step instructions for complex tasks
   - Include "What's Next" or "Related Topics" sections
   - Include troubleshooting tips where relevant
   - Keep documentation up-to-date with platform features
   - Include screenshots or diagrams for visual learners

8. **Documentation UI Components:**
   - Sidebar navigation (table of contents, hierarchical)
   - Search bar (prominent, accessible)
   - Breadcrumb navigation
   - Previous/Next navigation buttons
   - Print-friendly CSS (hide navigation, optimize layout)
   - Mobile-responsive layout (collapsible sidebar)
   - Dark mode support (if platform has dark mode)
   - Copy code button for code blocks
   - "Edit on GitHub" link (if repository is public)

---

## Dependencies & Prerequisites

### External Dependencies

1. **Key Management System:**
   - HashiCorp Vault, AWS KMS, or Azure Key Vault
   - Required for encryption key management
   - Must support key rotation
   - Must support audit logging

2. **Database:**
   - PostgreSQL 15+ (current)
   - Must support sharding (schema-based or table-based)
   - Must support encryption at rest (TDE or application-level)

3. **Container Registry:**
   - Docker Hub or private registry
   - For storing container images
   - Must support image scanning

### Infrastructure Prerequisites

1. **Compute Resources:**
   - Sufficient CPU and memory for multi-tenant workloads
   - Horizontal scaling capability
   - Load balancing for high availability

2. **Storage:**
   - Database storage with encryption support
   - Log storage (7 days active, archived)
   - Backup storage (encrypted)

3. **Network:**
   - TLS 1.3 support
   - Firewall rules
   - DDoS protection

### Development Prerequisites

1. **Development Tools:**
   - Python 3.11+
   - Node.js (for frontend)
   - Docker and Docker Compose
   - Git for version control

2. **Testing Tools:**
   - pytest for Python testing
   - Playwright for E2E testing
   - Security scanning tools
   - Performance testing tools

## Performance & SLA Requirements

### Service Level Agreements (SLAs)

1. **Availability:**
   - Target: 99.9% uptime
   - Planned maintenance windows: <4 hours/month
   - Unplanned downtime: <8.76 hours/year

2. **Response Times:**
   - API endpoints: <200ms (95th percentile)
   - Page load: <2 seconds
   - Database queries: <100ms (95th percentile)

3. **Throughput:**
   - API requests: 1000+ requests/second
   - Concurrent users: 500+ users
   - Scans: 100+ concurrent scans

### Performance Requirements

1. **Scalability:**
   - Support 100+ tenants
   - Support 1000+ users per tenant
   - Support 10,000+ scans per tenant
   - Horizontal scaling capability

2. **Resource Limits:**
   - Memory: Monitor and optimize
   - CPU: Efficient algorithms
   - Storage: Data retention policies
   - Network: Bandwidth optimization

## Error Handling & Monitoring

### Error Handling Strategy

1. **Error Categories:**
   - **Client Errors (4xx):** Validation errors, authentication failures
   - **Server Errors (5xx):** Internal errors, database errors
   - **Business Logic Errors:** Custom error codes for business rules

2. **Error Response Format:**
   ```json
   {
     "error": {
       "code": "ERROR_CODE",
       "message": "User-friendly error message",
       "details": {},
       "timestamp": "2025-01-XXT00:00:00Z"
     }
   }
   ```

3. **Error Logging:**
   - Log all errors with stack traces
   - Include context (user, tenant, request details)
   - Alert on critical errors
   - Track error rates and trends

### Monitoring & Alerting

1. **Health Checks:**
   - `/health` endpoint: Basic health check
   - `/health/ready` endpoint: Readiness check
   - `/health/live` endpoint: Liveness check
   - Database connectivity check
   - Key management system connectivity check

2. **Metrics:**
   - Request rate and latency
   - Error rates by endpoint
   - Database query performance
   - Resource usage (CPU, memory, disk)
   - Tenant-specific metrics

3. **Alerting:**
   - Critical errors: Immediate alert
   - High error rate: Alert if >5% errors
   - Performance degradation: Alert if >20% slower
   - Resource exhaustion: Alert at 80% capacity
   - Security incidents: Immediate alert

---

**Document Version:** 4.1  
**Last Updated:** 2025-01-XX  
**Status:** First Version - Includes Implementation Phases, Testing Requirements, Quality Aspects, Dependencies, Performance SLAs, Error Handling, and Monitoring. No backward compatibility or migration required.

