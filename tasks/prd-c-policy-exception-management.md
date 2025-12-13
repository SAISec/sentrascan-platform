# Product Requirements Document: Policy & Exception Management

## Introduction/Overview

This PRD implements comprehensive policy configuration and exception handling systems with approval workflows for SentraScan. The current system uses file-based policies without approval workflows and has no exception handling capability. This PRD addresses these gaps by providing database-stored policies with approval workflows, policy templates, and a complete exception management system.

The goal is to enable tenant administrators to configure organization-specific policies with compliance oversight, and allow users to request exceptions for findings with proper approval workflows.

This PRD emphasizes code reuse, functional reuse, and comprehensive testing to ensure the policy and exception systems are robust and maintainable.

## Goals

1. **Implement Tenant-Level Policy Configuration**: Allow tenant administrators to configure custom policies with rulesets, severity mappings, and thresholds.

2. **Establish Policy Approval Workflow**: Create a structured approval process for policy changes with compliance manager oversight.

3. **Provide Policy Templates**: Offer system-provided policy templates as starting points for tenant administrators.

4. **Implement Exception Handling System**: Enable users to request exceptions for findings with approval workflows.

5. **Create Exception Management**: Allow compliance managers to approve, reject, and manage exceptions with expiration handling.

6. **Implement Scheduled Tasks**: Create background jobs for exception expiration notifications and processing.

## User Stories

### Policy Management
- **As a tenant admin**, I want to configure custom policies with rulesets and severity mappings, so that I can enforce organization-specific security requirements.
- **As a compliance manager**, I want to review and approve policy changes, so that I can ensure compliance with organizational standards.
- **As a tenant admin**, I want to see policy templates I can start from, so that I don't have to configure policies from scratch.
- **As a user**, I want to view current active policies for my tenant, so that I understand what security rules are in place.

### Exception Management
- **As a user**, I want to request exceptions for findings, so that I can handle false positives or accepted risks.
- **As a compliance manager**, I want to approve or reject exception requests, so that I can maintain security standards while allowing legitimate exceptions.
- **As a user**, I want to receive notifications before my exceptions expire, so that I can renew them if needed.
- **As a compliance manager**, I want to view all exceptions for my tenant, so that I can manage exception requests effectively.

## Functional Requirements

### 1. Policy Configuration

1.1. **Policy Configuration Capabilities**
   - The system must allow tenant admins to create custom rulesets using regex patterns.
   - The system must allow tenant admins to define custom issue types.
   - The system must allow tenant admins to configure file path exclusions.
   - The system must allow tenant admins to override default severity mappings.
   - The system must allow tenant admins to set organization-specific severity thresholds.
   - The system must allow tenant admins to map custom issue types to severity levels (critical, high, medium, low, info).

1.2. **Policy Storage**
   - The system must create new `Policy` table to store tenant-specific policies with approval workflow.
   - The system must store policies with fields: id, tenant_id, name, policy_type (mcp/model), content (JSONB), status (active/pending_approval/rejected), version, created_by, approved_by, approved_at, created_at, updated_at, policy_template_id.
   - The system must keep file-based policies (`.sentrascan.yaml`) as defaults/templates.
   - The system must make database policies override file-based policies when active.
   - The system must check for active database policy first, then fall back to file-based policy.

1.3. **Policy Versioning**
   - The system must maintain policy version history.
   - The system must track policy changes with version numbers.
   - The system must display policy version history showing approved changes over time.
   - The system must allow viewing previous policy versions.

1.4. **Policy Visibility**
   - The system must allow users to view current active policies for their tenant.
   - The system must allow users to view all configured rulesets for their tenant.
   - The system must display policy version history.
   - The system must show pending policy change requests with their status.

### 2. Policy Approval Workflow

2.1. **Policy Change Requests**
   - The system must require all policy changes (except those made by compliance managers) to go through an approval workflow.
   - The system must allow compliance managers to self-approve their own policy changes.
   - The system must require tenant admin policy changes to be approved by a compliance manager.
   - The system must create policy change requests with status `pending_approval`.
   - The system must store policy change requests in `policy_change_requests` table.

2.2. **Policy Change Display**
   - The system must display policy changes with diffs showing what was modified.
   - The system must show requester information (name, role, timestamp) for each policy change request.
   - The system must capture and display rationale for each policy change.
   - The system must optionally show impact analysis of policy changes, including:
     * Estimated number of affected scans (based on current scan history)
     * Estimated number of findings that would be affected by severity changes
     * List of issue types that would be newly blocked or allowed
     * Potential impact on gate pass/fail rates (if historical data available)
     * Warning if the change would make existing approved scans fail

2.3. **Approval Process**
   - The system must send email notifications to compliance managers when policy changes require approval.
   - **Policy Change Approval Request Email**:
     * Subject: "Policy change approval required"
     * Include policy change details and diff
     * Include requester information and rationale
     * Include approval/rejection links
   - The system must allow compliance managers to approve policy changes with optional modifications.
   - The system must allow compliance managers to reject policy changes with comments explaining the rejection.
   - The system must allow requesters to modify and resubmit rejected policy changes.
   - The system must only apply approved policy changes; unapproved changes must remain in pending state.
   - The system must expire pending policy change requests after 7 days if not approved.

2.4. **Policy Application**
   - The system must apply approved policies immediately after approval.
   - The system must replace previous active policy with newly approved policy.
   - The system must maintain previous policy versions for history.
   - The system must update policy status to `active` after approval.

### 3. Policy Templates

3.1. **Template Storage**
   - The system must store templates in database (`PolicyTemplate` table).
   - The system must create template management API endpoints.
   - The system must implement template copying logic.
   - The system must make templates read-only (users copy templates to create their own policies).

3.2. **Template Content**
   - The system must include pre-configured severity mappings in templates:
     * Default severity levels: critical, high, medium, low, info
     * Common issue type to severity mappings (e.g., hardcoded_secrets → high, command_injection → critical)
   - The system must include common rules and patterns in templates:
     * Regex patterns for common security issues (e.g., API key patterns, password patterns)
     * File path exclusion patterns (e.g., exclude test files, vendor directories)
     * Common custom issue type definitions
   - The system must include default thresholds in templates:
     * Gate thresholds (critical_max: 0, high_max: 10, medium_max: 50, low_max: 100)
     * Severity action mappings (critical: block, high: warn, medium: notify, low: notify)

3.3. **Template Selection**
   - The system must provide 2-3 starter templates covering common use cases (e.g., "Strict Security", "Balanced", "Development").
   - The system must allow users to view and select from available policy templates when creating new policies.
   - Templates must be user-friendly with clear descriptions and not overwhelm users with too many options.
   - The system must allow users to preview template content before copying.

### 4. Severity Mapping

4.1. **Custom Severity Mappings**
   - The system must allow admins (tenant_admin, compliance_manager) to map custom issue types to severity levels.
   - The system must allow admins to override default severity assignments for standard issue types.
   - The system must validate that severity mappings use valid severity levels (critical, high, medium, low, info).
   - The system must apply severity mappings immediately after approval (for tenant_admin) or immediately (for compliance_manager).

4.2. **Severity Mapping Storage**
   - The system must store severity mappings in policy content (JSONB).
   - The system must validate severity mappings before saving.
   - The system must display severity mappings in policy configuration UI.

### 5. Exception Handling

5.1. **Exception Request Functionality**
   - The system must allow users to request exceptions for individual findings.
   - The system must allow users to create bulk exception rules (e.g., "ignore all X in path Y").
   - The system must allow users to create time-bound exceptions with configurable expiration (default: 30 days).
   - The system must require all exception requests to be approved by a compliance manager.
   - The system must allow users to provide rationale for exception requests.

5.2. **Exception Categories**
   - The system must provide standard exception categories: "False Positive", "Accepted Risk", "Under Review", "Temporary Exception", "Compliance Exception".
   - The system must allow users to create custom exception categories.
   - The system must store exception categories in `exception_categories` table.
   - The system must display exception categories in exception request UI.

5.3. **Exception Status**
   - The system must display exception status (pending, approved, rejected, expired, invalid) in the UI.
   - The system must track exception lifecycle from request to expiration.
   - The system must allow filtering exceptions by status, category, expiration date.

5.4. **Finding Deletion Handling**
   - The system must mark exception as `status='invalid'` with reason "finding_deleted" if finding is deleted.
   - The system must not cascade delete exceptions (preserve audit trail).
   - The system must allow compliance managers to view invalid exceptions for audit purposes.
   - The system must filter out invalid exceptions from active exception lists.

### 6. Exception Approval Workflow

6.1. **Exception Approval Process**
   - The system must show exception details including finding information, requested category, expiration date, and requester rationale.
   - The system must send email notifications to compliance managers when exceptions are requested.
   - **Exception Approval Request Email**:
     * Subject: "Exception approval required"
     * Include exception details
     * Include finding information
     * Include approval/rejection links
   - The system must allow compliance managers to approve exceptions with optional modifications (e.g., change expiration date, category).
   - The system must allow compliance managers to schedule exceptions for future activation or apply them immediately.
   - The system must allow compliance managers to reject exceptions with comments explaining the rejection.
   - The system must notify requesters via email when their exception requests are approved or rejected.

6.2. **Exception Application**
   - The system must apply approved exceptions immediately or on the scheduled date as specified by the compliance manager.
   - The system must check exception status at scan start and end.
   - The system must apply exceptions when evaluating findings.
   - The system must cancel scheduled exceptions if finding is resolved before activation.

6.3. **Exception Management Interface**
   - The system must allow compliance managers to view all exceptions (active, pending, expired) for their tenant.
   - The system must provide filtering by category, status, expiration date.
   - The system must show exception details in an expandable card format.
   - The system must provide bulk actions for compliance managers (approve/reject multiple exceptions).

### 7. Exception Expiration

7.1. **Expiration Notifications**
   - The system must send email notifications to users before their time-bound exceptions expire (default: 7 days before expiration, 1 day before expiration).
   - **Exception Expiration Notification Email**:
     * Subject: "Your exception will expire soon" (7 days before) / "Your exception expires tomorrow" (1 day before)
     * Include exception details (finding, category, expiration date)
     * Include link to request exception renewal
     * Include instructions for renewal process
     * Sent to exception requester
   - The system must track which notifications have been sent to avoid duplicate emails.
   - The system must include exception details (finding, category, expiration date) in notification emails.
   - The system must include link to request exception renewal in notification emails.

7.2. **Expiration Processing**
   - The system must automatically expire time-bound exceptions on their expiration date.
   - The system must update exception status to "expired" when expiration date is reached.
   - The system must log expiration events in audit logs.
   - The system must run expiration processing daily at configurable time (default: midnight UTC).

7.3. **Exception Renewal**
   - The system must allow users to request exception renewal before expiration.
   - The system must require re-approval for exception renewal requests.
   - The system must treat renewal as a new exception request.

### 8. Scheduled Tasks

8.1. **Exception Expiration Notifications**
   - The system must implement scheduled task (cron job or background worker) to check for expiring exceptions daily.
   - The system must send notification emails 7 days before expiration and 1 day before expiration.
   - The system must track which notifications have been sent to avoid duplicate emails.
   - The system must run daily at a configurable time (default: 9:00 AM UTC).

8.2. **Exception Expiration Processing**
   - The system must implement scheduled task to automatically expire time-bound exceptions on their expiration date.
   - The system must update exception status to "expired" when expiration date is reached.
   - The system must log expiration events in audit logs.
   - The system must run daily at a configurable time (default: midnight UTC).

8.3. **Policy Change Request Expiration**
   - The system must implement scheduled task to expire pending policy change requests after 7 days.
   - The system must update request status to "expired" and notify requester.
   - The system must run daily at a configurable time (default: midnight UTC).

## Non-Goals (Out of Scope)

1. **Policy Versioning and Rollback**: While policy history is viewable, advanced versioning with rollback capabilities is out of scope.

2. **Automated Policy Impact Analysis**: While impact analysis display is optional, automated calculation of policy impact is out of scope.

3. **Policy Template Marketplace**: Creating tenant-specific policy templates or template marketplace is out of scope. Only system-provided templates are included.

4. **Exception Auto-Approval**: Exceptions cannot be auto-approved. All exceptions require compliance manager approval.

5. **Policy Testing Environment**: Policy testing/sandbox environment is out of scope.

## Design Considerations

### UI/UX Requirements

1. **Policy Management Interface**
   - Create a dedicated policy management page with tabs for: Active Policies, Pending Changes, Templates, History.
   - Show policy diffs in a side-by-side or unified diff view.
   - Display approval workflow status clearly with visual indicators (pending, approved, rejected).
   - Provide inline editing capabilities for policy configuration.
   - Show policy impact analysis in a clear, readable format.

2. **Exception Management Interface**
   - Create an exception management page showing all exceptions (active, pending, expired).
   - Allow filtering by category, status, expiration date.
   - Show exception details in an expandable card format.
   - Provide bulk actions for compliance managers (approve/reject multiple exceptions).
   - Display exception timeline (requested, approved, expiration date).

3. **Policy Template Selection**
   - Create template selection UI with preview capability.
   - Show template descriptions and use cases.
   - Allow users to compare templates side-by-side.
   - Provide "Create from Template" action.

## Technical Considerations

### Database Schema Changes

1. **New Tables**
   - `policies`: id, tenant_id, name, policy_type (mcp/model), content JSONB, status (active/pending_approval/rejected), version, created_by, approved_by, approved_at, created_at, updated_at, policy_template_id
   - `policy_templates`: id, name, description, policy_type, content JSONB, is_system_template, created_at
   - `policy_change_requests`: id, policy_id (foreign key), requester_id, approver_id, status, rationale, policy_diff JSONB, expires_at, created_at, updated_at
   - `exceptions`: id, finding_id (foreign key), category, status (pending/approved/rejected/expired/invalid), requester_id, approver_id, expires_at, scheduled_activation, rationale, created_at, updated_at
   - `exception_categories`: id, name, description, is_standard, tenant_id, created_at

2. **No Model Updates**
   - All new functionality uses new tables.
   - Existing models remain unchanged.

### API Endpoints

1. **Policy Management**
   - `GET /api/v1/policies` - Get current active policies for tenant
   - `POST /api/v1/policies` - Create policy change request
   - `PUT /api/v1/policies/{policy_id}` - Update policy (creates change request)
   - `GET /api/v1/policies/pending` - List pending policy change requests
   - `POST /api/v1/policies/{request_id}/approve` - Approve policy change (compliance_manager only)
   - `POST /api/v1/policies/{request_id}/reject` - Reject policy change (compliance_manager only)
   - `GET /api/v1/policies/templates` - List available policy templates
   - `POST /api/v1/policies/from-template` - Create policy from template
   - `GET /api/v1/policies/{policy_id}/diff` - Get policy diff for change request
   - `GET /api/v1/policies/{policy_id}/history` - Get policy version history

2. **Exception Management**
   - `POST /api/v1/exceptions` - Request exception
   - `GET /api/v1/exceptions` - List exceptions (filtered by status, category, etc.)
   - `GET /api/v1/exceptions/{exception_id}` - Get exception details
   - `POST /api/v1/exceptions/{exception_id}/approve` - Approve exception (compliance_manager only)
   - `POST /api/v1/exceptions/{exception_id}/reject` - Reject exception (compliance_manager only)
   - `GET /api/v1/exception-categories` - List exception categories (standard + custom)
   - `POST /api/v1/exception-categories` - Create custom exception category
   - `POST /api/v1/exceptions/{exception_id}/renew` - Request exception renewal

3. **Compliance Manager**
   - `GET /api/v1/compliance/pending-approvals` - List all pending approvals for compliance manager (policies + exceptions)

### Code Reuse Requirements

1. **Approval Workflow Engine**
   - Create generic approval workflow engine that can be reused for:
     * Policy change approvals
     * Exception approvals
   - The approval workflow engine must support:
     * Request creation with rationale
     * Approval/rejection with comments
     * Expiration handling
     * Notification sending
     * Audit logging
   - Approval workflow must be configurable per use case (approver role, expiration time, etc.)

2. **Shared Utilities**
   - Create reusable policy diff calculation utility
   - Create reusable impact analysis calculation utility (optional)
   - Create reusable exception expiration checking utility

### Testing Requirements

1. **Unit Testing**
   - Policy model tests (validation, relationships)
   - Exception model tests (validation, relationships)
   - Policy approval workflow tests
   - Exception approval workflow tests
   - Policy template copying tests
   - Exception expiration logic tests
   - Minimum 80% code coverage, 100% for utilities

2. **Integration Testing**
   - Policy change approval workflow (request → approval → activation)
   - Exception approval workflow (request → approval → application)
   - Policy template copying and customization
   - Exception expiration and renewal
   - Scheduled task execution

3. **Security Testing**
   - Approval workflow authorization (prevent unauthorized approvals)
   - Tenant isolation (compliance manager can't approve other tenants)
   - Policy validation before approval (prevent malicious changes)
   - Input validation and sanitization
   - SQL injection prevention

4. **Performance Testing**
   - Policy change request processing performance
   - Exception request processing performance
   - Scheduled task execution performance
   - Database query performance (with indexes)
   - Policy diff calculation performance
   - Impact analysis calculation performance (if implemented)

5. **Test Data Management**
   - Create test fixtures for common entities (policies, exceptions, policy templates, exception categories)
   - Use factory pattern for test data generation
   - Create test database with sample data
   - Implement test data cleanup between tests
   - Mock email service for unit tests (don't send real emails)
   - Mock scheduled task execution for unit tests

## Success Metrics

1. **Policy Management**
   - 90% of policy change requests are approved/rejected within 7 days
   - Average policy change approval time: < 3 business days
   - Policy template usage: > 50% of new policies start from templates

2. **Exception Management**
   - 85% of exception requests are approved/rejected within 5 business days
   - Exception expiration compliance: 100% of time-bound exceptions expire on schedule
   - Exception renewal rate: Track percentage of exceptions renewed before expiration

3. **System Performance**
   - Policy change request processing: < 100ms API response time
   - Exception request processing: < 100ms API response time
   - Scheduled task execution: Complete within 5 minutes

## Resolved Decisions

1. **Policy Storage**: Database policies with file-based fallback. Database policies override file-based when active.

2. **Policy Templates**: System-provided templates stored in database, read-only, users copy to create their own.

3. **Exception Expiration**: 30 days default, notifications at 7 days and 1 day before expiration.

4. **Finding Deletion**: Mark exception as invalid, don't cascade delete (preserve audit trail).

5. **Approval Workflow**: Compliance managers can self-approve, tenant admins require compliance manager approval.

## Audit Logging Requirements

### Policy Change Audit Logging
- The system must log all policy change requests with maximum detail:
  * Requester user_id, email, role, tenant_id
  * Policy change details (before/after state, diff)
  * Rationale provided by requester
  * Timestamp of request
  * Approval/rejection status, approver details, timestamp
  * Any modifications made during approval
  * IP address of requester and approver
- The system must store policy change history with full version tracking

### Exception Approval Audit Logging
- The system must log all exception requests and approvals with maximum detail:
  * Exception requester user_id, email, role, tenant_id
  * Finding details (finding_id, issue_type, severity, scan_id)
  * Exception category, expiration date, scheduled activation
  * Rationale for exception
  * Approval/rejection status, approver details, timestamp
  * Any modifications made during approval (expiration date, category changes)
  * IP address of requester and approver
  * Exception expiration notifications sent

### Audit Log Storage
- Store all audit logs in the audit_logs table with JSON details field for maximum flexibility
- Ensure audit logs are immutable (no updates or deletes)
- Include all relevant context in the details JSON field
- Maintain audit log retention policy (recommended: 7 years for compliance)

## Edge Case Handling

### Policy Approval Edge Cases
- **Expired policy change requests**: Mark as expired, notify requester, allow resubmission
- **Rejected policy changes**: Store rejection reason, allow requester to modify and resubmit
- **Policy version conflicts**: Detect conflicts, require resolution before approval
- **No compliance managers**: Require at least one compliance manager before allowing policy changes (validation)

### Exception Expiration Edge Cases
- **Exception expires during scan**: Check exception status at scan start and end
- **Finding deleted with active exception**: Mark exception as invalid, preserve for audit
- **Exception renewal**: Require re-approval for renewal requests
- **Scheduled exception activation**: Cancel scheduled exceptions if finding is resolved before activation

## Security Implementation

### Approval Workflow Security
- Policy change requests are immutable after creation (read-only)
- All approval/rejection actions are logged in audit logs
- Compliance manager actions are fully audited
- Policy validation before approval (prevent malicious changes)
- Require rationale for all policy changes
- Exception requests must include rationale
- All exception approvals/rejections must be logged with full details

### Tenant Isolation Security
- Compliance managers can only approve policies and exceptions for their own tenant
- Policy change requests are scoped to tenant
- Exception requests are scoped to tenant
- All tenant isolation checks must be enforced at API and database levels

## Data Migration Strategy

### Migration Approach
- Focus on schema migrations for new policy and exception tables
- Provide migration scripts for database schema changes
- Test migrations on staging environment before production
- Policy templates can be seeded via migration scripts

### Migration Scripts
- Create Alembic migrations for all database schema changes
- Include rollback scripts for each migration
- Document migration steps and dependencies
- Test migrations on sample data
- Seed initial policy templates via migration

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-27  
**Status**: Ready for Implementation  
**Part of**: 4-PRD Breakdown for RBAC, User, and Tenant Management Improvements  
**Dependencies**: PRD A (email service for notifications, scheduled tasks), PRD B (compliance manager role)
