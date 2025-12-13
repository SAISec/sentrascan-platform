# Product Requirements Document: Foundation & User Management

## Introduction/Overview

This PRD establishes the foundational infrastructure for email services, rate limiting, and token management, and implements a complete self-service user onboarding system for SentraScan. The current system lacks email capabilities, rate limiting, and self-service user signup with approval workflows. This PRD addresses these gaps by providing a robust foundation that enables secure user authentication and onboarding.

The goal is to create reusable infrastructure components (email service, rate limiting, token management) and implement a complete user signup and authentication flow with email verification, password reset, and admin approval workflows.

This PRD emphasizes code reuse, functional reuse, and comprehensive testing to ensure the foundation is robust and maintainable.

## Goals

1. **Establish Email Infrastructure**: Implement a reliable email service with queue management, retry logic, and template support for all system emails.

2. **Implement Rate Limiting**: Create a rate limiting system to prevent abuse of signup and password reset endpoints.

3. **Create Token Management System**: Build a secure, reusable token management system for email verification, password reset, and invitations.

4. **Enable Self-Service User Signup**: Allow users to sign up with email and password, with email verification and admin approval workflows.

5. **Implement Password Reset**: Enable users to reset their passwords via email with secure token-based verification.

6. **Support Email Domain Mapping**: Map users to tenants based on email domain with fallback to default tenant.

7. **Provide Super Admin Fallback**: Enable super admins to manually verify users and reset passwords when email service is unavailable (critical for enterprise deployments).

8. **Configure Default Tenant**: Implement system-wide default tenant configuration for user assignment.

## User Stories

### Email Infrastructure
- **As a system administrator**, I want email service to be reliable with retry logic, so that important notifications are never lost.
- **As a developer**, I want reusable email templates, so that I can easily add new email types in the future.
- **As a super admin**, I want to manually verify users and reset passwords, so that the system works even when email service is unavailable.

### User Signup & Authentication
- **As a new user**, I want to sign up with my email and password, so that I can access SentraScan without waiting for manual account creation.
- **As a tenant admin**, I want to invite users via email, so that I can onboard team members quickly.
- **As a user**, I want to reset my password via email, so that I can regain access if I forget my password.
- **As a tenant admin**, I want to approve or reject new user signups, so that I can control who has access to my tenant.
- **As a user**, I want my email to be verified, so that I know my account is secure.

### Email Domain Mapping
- **As a system administrator**, I want users to be automatically assigned to tenants based on email domain, so that onboarding is seamless.
- **As a super admin**, I want to configure email domain to tenant mappings, so that users are assigned to the correct organization.

## Functional Requirements

### 1. Email Service Infrastructure

1.1. **Email Service Module**
   - The system must create `src/sentrascan/core/email.py` module for centralized email sending.
   - The system must use `aiosmtplib` for async email sending.
   - The system must use Jinja2 for email template rendering.
   - The system must support Gmail SMTP configuration (smtp.gmail.com, port 587 for TLS or 465 for SSL).
   - The system must use environment variables for SMTP configuration (SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD, SMTP_USE_TLS).
   - The system must store Gmail password in environment variable `SMTP_PASSWORD` (never hardcoded).
   - The system must use Gmail App Password (not regular password).
   - All system emails must be sent from manoj@sovereignaisecurity.com.
   - The system must implement email sending abstraction layer for potential future provider switching.

1.2. **Email Queue System**
   - The system must implement email queue using database table (`email_queue`).
   - The system must store email queue in database (can migrate to Redis later if needed).
   - The system must retry failed email sends with exponential backoff (max 3 retries).
   - The system must log all email sending attempts and failures with detailed error messages.
   - The system must handle Gmail-specific rate limits and quota restrictions.
   - The system must implement background worker process to process email queue.
   - The system must queue emails and notify super admins if email service is unavailable.

1.3. **Email Templates**
   - The system must support 7 email template types with detailed specifications:
     * **User Signup Verification Email**
       - Subject: "Verify your SentraScan account"
       - Include verification link with token
       - Include expiration time (24 hours)
       - Branded with SentraScan styling
     * **Password Reset Email**
       - Subject: "Reset your SentraScan password"
       - Include reset link with token
       - Include expiration time (4 hours)
       - Security warning about not sharing the link
     * **User Invitation Email**
       - Subject: "You've been invited to join SentraScan"
       - Include invitation link with token
       - Include inviter name and tenant name
       - Include expiration time
     * **User Approval Notification Email**
       - Subject: "Your SentraScan account has been approved"
       - Welcome message
       - Login instructions
     * **User Rejection Notification Email**
       - Subject: "Your SentraScan account request"
       - Clear rejection message
       - Contact information for questions
   - The system must use Jinja2 template engine for email rendering.
   - The system must support HTML and plain text email formats.
   - The system must store email templates in configuration files or database.
   - All email templates must be in English only (no multi-language support initially).
   - Templates must include SentraScan branding and consistent styling.

1.4. **Super Admin Fallback**
   - The system must allow super admins to manually verify user emails when email service is unavailable.
   - The system must provide endpoint: `POST /api/v1/admin/users/{user_id}/verify-email` (super admin only).
   - The system must allow super admins to manually reset user passwords when email service is unavailable.
   - The system must provide endpoint: `POST /api/v1/admin/users/{user_id}/reset-password` (super admin only).
   - The system must log all super admin manual actions in audit logs with full details.
   - The system must require super admin authentication for fallback endpoints.
   - Super admin fallback is critical for enterprise deployments where email may not be immediately available.

### 2. Rate Limiting Service

2.1. **Rate Limiting Implementation**
   - The system must create `src/sentrascan/core/rate_limit.py` module for centralized rate limiting.
   - The system must use in-memory cache for rate limiting (single-instance deployment).
   - The system must implement sliding window algorithm for accurate rate limiting.
   - The system must track requests by IP address and email address.
   - The system must enforce stricter limit (most restrictive of IP or email limits).
   - The system must return 429 Too Many Requests with Retry-After header when limit exceeded.
   - The system must use thread-safe data structures for concurrent access.

2.2. **Rate Limit Configuration**
   - The system must limit signup requests to 5 requests per hour per IP address.
   - The system must limit password reset requests to 5 requests per hour per IP address.
   - The system must make rate limits configurable via environment variables.
   - The system must track rate limits separately for signup and password reset endpoints.

### 3. Token Management Service

3.1. **Token Service Module**
   - The system must create `src/sentrascan/core/token.py` module for centralized token management.
   - The system must generate tokens using `secrets.token_urlsafe()` (cryptographically secure).
   - The system must support three token types:
     * Email verification tokens
     * Password reset tokens
     * Invitation tokens
   - The system must implement token expiration handling.
   - The system must implement single-use token validation.
   - The system must implement token invalidation.

3.2. **Email Verification Tokens**
   - The system must generate secure tokens for email verification.
   - The system must expire verification tokens after 24 hours (configurable).
   - The system must make verification tokens single-use only.
   - The system must store tokens in `email_verification_tokens` table.
   - The system must track token usage (used/unused).

3.3. **Password Reset Tokens**
   - The system must generate secure tokens for password reset.
   - The system must expire password reset tokens after 4 hours.
   - The system must make password reset tokens single-use only.
   - The system must store tokens in `password_reset_tokens` table.
   - The system must track token usage (used/unused).

3.4. **Invitation Tokens**
   - The system must generate secure tokens for user invitations.
   - The system must expire invitation tokens after a configurable time period (default: 7 days).
   - The system must make invitation tokens single-use only.
   - The system must store tokens in `user_invitations` table.

### 4. Default Tenant Configuration

4.1. **Default Tenant Field**
   - The system must add `default_tenant` boolean field to `Tenant` model.
   - The system must add database constraint: Only one tenant can have `default_tenant=True` at a time.
   - The system must automatically mark first tenant created (by `created_at`) as `default_tenant=True`.
   - The system must allow super admins to change default tenant via API.
   - The system must prevent deletion of default tenant (require setting new default first).
   - The system must prevent deactivation of default tenant.

4.2. **Default Tenant Logic**
   - The system must use system-wide default tenant configuration (not per-deployment).
   - The system must assign users to default tenant if their email domain doesn't match any configured tenant domain.
   - The system must store default tenant configuration in database (via `default_tenant` field).

### 5. User Signup and Authentication

5.1. **Open User Signup**
   - The system must allow users to sign up with email and password without requiring an invite.
   - The system must require email verification before account activation.
   - The system must map users to tenants based on email domain (e.g., @company.com → Company Tenant).
   - The system must assign users to default tenant if their email domain doesn't match any configured tenant domain.
   - The system must require admin approval (tenant admin or super admin) for all new user signups before account activation.
   - The system must send email notifications to approvers when a new user signs up.
   - The system must implement rate limiting: maximum 5 signup requests per hour per IP address.
   - The system must enforce stricter rate limiting (most restrictive of IP-based or email-based limits).
   - The system must update existing `/api/v1/users/register` endpoint to require approval workflow (breaking change).

5.2. **Invite-Only User Signup**
   - The system must allow tenant admins to send invitation emails to users.
   - The system must generate unique, time-limited invitation tokens for each invite.
   - The system must require invited users to complete signup within the invitation validity period.
   - The system must allow tenant admins to resend or revoke invitations.
   - The system must track invitation status (pending, accepted, expired, revoked).

5.3. **Email Verification**
   - The system must send verification emails with secure tokens when users sign up.
   - The system must require email verification before allowing password reset.
   - The system must make verification tokens single-use only.
   - The system must expire verification tokens after 24 hours (configurable).
   - The system must provide a "Resend verification email" option.
   - The system must update user `email_verified` field to `True` after successful verification.

5.4. **Password Reset**
   - The system must allow users to request password reset via email.
   - The system must send password reset emails with secure, time-limited tokens.
   - The system must expire password reset tokens after 4 hours.
   - The system must make password reset tokens single-use only.
   - The system must require email verification before processing password reset requests.
   - The system must implement rate limiting: maximum 5 password reset requests per hour per IP address.
   - The system must enforce stricter rate limiting (most restrictive of IP-based or email-based limits).
   - The system must invalidate all existing sessions after a successful password reset.

5.5. **User Approval Workflow**
   - The system must maintain a pending approval state for new user signups.
   - The system must allow tenant admins and super admins to approve or reject user signups.
   - The system must send notification emails to users when their signup is approved or rejected.
   - The system must allow admins to assign users to different tenants during approval if email domain doesn't match.
   - The system must provide an admin interface to view and manage pending user approvals.
   - The system must update user `signup_approved` field to `True` after approval.
   - The system must set `approved_by` and `approved_at` fields after approval.

### 6. Email Domain Mapping

6.1. **Email Domain Model**
   - The system must create `TenantEmailDomain` model in `models.py`.
   - The system must store email domain to tenant mappings (domain, tenant_id).
   - The system must enforce UNIQUE constraint on domain field (one-to-one mapping).
   - The system must prevent duplicate domain mappings.
   - The system must use case-insensitive domain matching.

6.2. **Domain Matching Logic**
   - The system must create reusable domain matching utility for email domain to tenant mapping.
   - The system must implement domain validation (must be valid domain format).
   - The system must handle subdomain matching (most specific domain wins).
   - The system must implement domain matching logic in signup flow.
   - The system must assign users to tenant based on email domain match.
   - The system must fall back to default tenant if no domain match found.

6.3. **Domain Management**
   - The system must allow super admins and tenant admins to create email domain mappings.
   - The system must allow admins to list email domain mappings.
   - The system must prevent deletion of domain mappings if users exist with that domain.
   - The system must return clear error messages for duplicate domain mappings.

## Non-Goals (Out of Scope)

1. **SSO Integration**: Single Sign-On (SSO) integration is not included in this PRD. Email/password authentication is the focus.

2. **Multi-Provider Email Support**: While the email service has abstraction for future providers, only Gmail SMTP is implemented initially.

3. **Distributed Rate Limiting**: Redis-based distributed rate limiting is out of scope. In-memory rate limiting is sufficient for single-instance deployment.

4. **Email Template Customization**: Users cannot customize email templates. Only system-provided templates are supported.

5. **Multi-Language Email Support**: Email templates are English only. No multi-language support.

6. **Advanced Token Features**: Token rotation, refresh tokens, and OAuth-style tokens are out of scope.

## Design Considerations

### Email Service Design

1. **Email Service Abstraction**
   - Create `EmailService` class with methods: `send_email()`, `send_verification_email()`, `send_password_reset_email()`, etc.
   - Use dependency injection for SMTP configuration.
   - Support both sync and async email sending.
   - Implement email queue as separate service.

2. **Email Template Structure**
   - Store templates in `src/sentrascan/core/templates/email/` directory.
   - Use Jinja2 template inheritance for consistent styling.
   - Create base template with SentraScan branding.
   - Each email type has its own template file.

3. **Email Queue Processing**
   - Background worker polls `email_queue` table.
   - Process emails in batches.
   - Retry failed emails with exponential backoff.
   - Log all email processing events.

### Rate Limiting Design

1. **Rate Limiting Middleware**
   - Create FastAPI middleware for rate limiting.
   - Use decorator `@rate_limit(requests_per_hour=5)` for endpoints.
   - Store rate limit data in thread-safe dictionary.
   - Implement sliding window algorithm.

2. **Rate Limit Storage**
   - Use in-memory dictionary with structure: `{key: [(timestamp1, count1), (timestamp2, count2), ...]}`
   - Key format: `ip:{ip_address}` or `email:{email_address}`
   - Clean up old entries periodically.

### Token Management Design

1. **Token Service Class**
   - Create `TokenService` class with methods: `generate_token()`, `validate_token()`, `invalidate_token()`.
   - Support different token types via enum or string parameter.
   - Store tokens in appropriate database tables.
   - Implement token expiration checking.

2. **Token Storage**
   - Each token type has its own table for clarity.
   - Tokens include: token string, user_id, expires_at, used boolean, created_at.
   - Index on token string for fast lookups.
   - Index on expires_at for cleanup jobs.

### User Signup Flow Design

1. **Signup Process**
   - User submits signup form → Create user with `email_verified=False`, `signup_approved=False`
   - Send verification email → User clicks link → Set `email_verified=True`
   - Admin approves → Set `signup_approved=True`, `approved_by`, `approved_at`
   - User can now log in

2. **Invitation Process**
   - Tenant admin sends invitation → Create invitation record with token
   - Send invitation email → User clicks link → Pre-fill signup form
   - User completes signup → Link invitation to user → Set `email_verified=True` (invitation implies verification)
   - Admin approves → User can log in

## Technical Considerations

### Database Schema Changes

1. **New Tables**
   - `email_verification_tokens`: id, user_id, token, type, expires_at, used, created_at
   - `password_reset_tokens`: id, user_id, token, expires_at, used, created_at
   - `user_invitations`: id, email, tenant_id, inviter_id, token, status, expires_at, created_at
   - `email_queue`: id, recipient_email, subject, template_name, template_data JSONB, status, attempts, next_retry_at, created_at, sent_at
   - `tenant_email_domains`: id, domain (UNIQUE), tenant_id, created_at

2. **User Model Updates**
   - Add `email_verified` boolean field (default: False)
   - Add `signup_approved` boolean field (default: False)
   - Add `approved_by` foreign key to users table (nullable)
   - Add `approved_at` timestamp field (nullable)

3. **Tenant Model Updates**
   - Add `default_tenant` boolean field (default: False)
   - Add database constraint: Only one tenant can have `default_tenant=True`
   - Add `signup_enabled` boolean field (default: True) - for future use

### API Endpoints

1. **User Signup & Authentication**
   - `POST /api/v1/users/signup` - Open user signup (updated to require approval)
   - `POST /api/v1/users/verify-email` - Verify email with token
   - `POST /api/v1/users/resend-verification` - Resend verification email
   - `POST /api/v1/users/forgot-password` - Request password reset
   - `POST /api/v1/users/reset-password` - Reset password with token
   - `POST /api/v1/users/invite` - Send user invitation (tenant_admin only)
   - `GET /api/v1/users/invitations/{token}` - Get invitation details
   - `POST /api/v1/users/accept-invitation` - Accept invitation and complete signup
   - `GET /api/v1/users/pending-approvals` - List pending user approvals (admin only)
   - `POST /api/v1/users/{user_id}/approve` - Approve user signup (admin only)
   - `POST /api/v1/users/{user_id}/reject` - Reject user signup (admin only)

2. **Super Admin Fallback**
   - `POST /api/v1/admin/users/{user_id}/verify-email` - Manually verify user email (super admin only)
   - `POST /api/v1/admin/users/{user_id}/reset-password` - Manually reset user password (super admin only)

3. **Email Domain Management**
   - `GET /api/v1/tenant-email-domains` - List email domain mappings (admin only)
   - `POST /api/v1/tenant-email-domains` - Create email domain mapping (admin only)
   - `DELETE /api/v1/tenant-email-domains/{domain_id}` - Delete email domain mapping (admin only)

4. **Default Tenant Management**
   - `PUT /api/v1/tenants/{tenant_id}/set-default` - Set default tenant (super admin only)
   - `GET /api/v1/tenants/default` - Get current default tenant

### Code Reuse Requirements

1. **Shared Utilities**
   - Create `src/sentrascan/core/utils/token.py` for token generation and validation
   - Create `src/sentrascan/core/utils/domain.py` for domain matching logic
   - All utilities must be well-documented with docstrings and type hints

2. **Reusable Service Classes**
   - `EmailService` - Centralized email sending with queue management
   - `RateLimitService` - Centralized rate limiting logic
   - `TokenService` - Centralized token generation and validation
   - All services must be easily testable with dependency injection

3. **Reusable API Decorators**
   - `@rate_limit(requests_per_hour=5)` - For endpoints requiring rate limiting
   - `@require_email_verified` - For endpoints requiring email verification
   - `@audit_log` - For endpoints requiring audit logging

### Testing Requirements

1. **Unit Testing**
   - Email service tests (mock SMTP)
   - Rate limiting tests (sliding window algorithm)
   - Token service tests (generation, validation, expiration)
   - Domain matching tests (various edge cases)
   - Minimum 80% code coverage, 100% for utilities

2. **Integration Testing**
   - Complete user signup flow (signup → verification → approval → login)
   - Password reset flow (request → email → reset → login)
   - Invitation flow (invite → accept → signup)
   - Email domain mapping and tenant assignment
   - Super admin fallback (manual verification, password reset)

3. **Security Testing**
   - Rate limiting effectiveness (prevent brute force)
   - Token security (prevent reuse, expiration)
   - Email token security (prevent token guessing)
   - Super admin fallback authorization
   - Input validation and sanitization
   - SQL injection prevention

4. **Performance Testing**
   - Rate limiting performance (should not significantly impact response times)
   - Email queue processing performance
   - Database query performance (with indexes)
   - Concurrent user signup handling
   - Token generation and validation performance

5. **Test Data Management**
   - Create test fixtures for common entities (users, tenants, tokens, invitations)
   - Use factory pattern for test data generation
   - Create test database with sample data
   - Implement test data cleanup between tests
   - Mock email service for unit tests (don't send real emails)
   - Mock SMTP server for integration tests
   - Use test doubles for rate limiting in unit tests

6. **Test Documentation**
   - Document all test scenarios and test cases
   - Document test setup and teardown procedures
   - Document how to run tests (unit, integration, security, performance)
   - Document test coverage reports and how to interpret them
   - Document test data requirements and fixtures

## Success Metrics

1. **Email Delivery**
   - Email delivery success rate: > 99%
   - Email queue processing time: < 5 minutes average
   - Email retry success rate: > 80% on first retry

2. **User Onboarding**
   - 80% of new users complete signup and email verification within 24 hours
   - Average time from signup to approval: < 2 business days
   - Invitation acceptance rate: > 70%

3. **Rate Limiting**
   - Rate limiting effectiveness: < 0.1% false positives
   - Rate limit check performance: < 10ms overhead per request

4. **Token Security**
   - Zero successful token reuse attempts
   - 100% expired token rejection rate

5. **Super Admin Fallback Usage**
   - Track usage of super admin fallback endpoints
   - Monitor when email service is unavailable

## Audit Logging Requirements

### User Approval Audit Logging
- The system must log all user signup approvals/rejections with maximum detail:
  * User details (user_id, email, name, requested tenant)
  * Signup method (open signup, invitation)
  * Email domain and tenant mapping result
  * Approver user_id, email, role
  * Approval/rejection decision and timestamp
  * Any tenant reassignment during approval
  * IP address of user and approver
  * Email verification status and timestamps
- The system must log all super admin manual actions (email verification, password reset) with full details:
  * Action type (verify_email, reset_password)
  * Target user details
  * Super admin user_id, email
  * Action timestamp
  * IP address of super admin
  * Reason for manual action (if provided)

### Audit Log Storage
- Store all audit logs in the audit_logs table with JSON details field for maximum flexibility
- Ensure audit logs are immutable (no updates or deletes)
- Include all relevant context in the details JSON field
- Maintain audit log retention policy (recommended: 7 years for compliance)

## Dependency Management

### Required Dependencies
- `aiosmtplib` - Async SMTP email sending
- `Jinja2` - Email template engine
- `cryptography` - Secure token generation
- Handle missing dependencies gracefully with clear error messages
- Provide installation instructions in documentation

### Optional Dependencies
- Background job scheduler (can use APScheduler or similar) - for email queue processing
- Make system functional without optional dependencies

## Data Migration Strategy

### Migration Approach
- Data migration is not challenging as there are not many existing users
- Existing users can be recreated if needed
- Focus on schema migrations rather than data migration
- Provide migration scripts for database schema changes
- Test migrations on staging environment before production

### Migration Scripts
- Create Alembic migrations for all database schema changes
- Include rollback scripts for each migration
- Document migration steps and dependencies
- Test migrations on sample data

### Breaking Changes Documentation
- Document all breaking changes in `BREAKING_CHANGES.md`
- Update API documentation to reflect new behavior
- Provide clear migration guide for API clients

## Resolved Decisions

1. **Email Service Provider**: Gmail SMTP with manoj@sovereignaisecurity.com as sender email.

2. **Rate Limiting**: In-memory implementation using sliding window algorithm.

3. **Token Expiration**: Email verification: 24 hours, Password reset: 4 hours, Invitations: 7 days.

4. **Default Tenant**: System-wide configuration, first tenant automatically marked as default.

5. **Super Admin Fallback**: Critical feature for enterprise deployments, fully audited.

6. **Breaking Changes**: User registration endpoint updated to require approval (no versioning needed). Document in `BREAKING_CHANGES.md`.

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-27  
**Status**: Ready for Implementation  
**Part of**: 4-PRD Breakdown for RBAC, User, and Tenant Management Improvements
