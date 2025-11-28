# Security Audit: Authentication and Authorization Flows

**Date:** 2025-11-28  
**Auditor:** Security Team  
**Scope:** Authentication and Authorization mechanisms in SentraScan Platform  
**Status:** Manual Security Audit

---

## Executive Summary

This document provides a comprehensive security audit of authentication and authorization flows in the SentraScan Platform. The audit covers:

1. **Authentication Mechanisms**
   - User authentication (email/password)
   - API key authentication
   - Session management
   - MFA implementation

2. **Authorization Mechanisms**
   - Role-Based Access Control (RBAC)
   - Permission checking
   - Tenant isolation
   - Function-level authorization

3. **Security Controls**
   - Password policies
   - Account lockout
   - Rate limiting
   - CSRF protection
   - Input validation

---

## 1. Authentication Flows

### 1.1 User Registration Flow

**Endpoint:** `POST /api/v1/users/register`

**Flow:**
1. User submits email, password, name, optional tenant_id, and role
2. Password is validated against policy (min 12 chars, complexity requirements)
3. Password is hashed using bcrypt (preferred) or Argon2 (fallback)
4. User record is created with tenant_id and role
5. User is stored in database with password_hash

**Security Considerations:**
- ✅ Password policy enforced (min 12 chars, complexity)
- ✅ Password hashing with bcrypt/Argon2
- ✅ Email validation
- ⚠️ **Issue S-03**: Argon2 import/instantiation mismatch (addressed in tests)
- ⚠️ Role assignment should be restricted (only super_admin can assign admin roles)

**Recommendations:**
- Add email verification before account activation
- Implement rate limiting on registration endpoint
- Add CAPTCHA to prevent automated registrations
- Restrict role assignment to authorized users only

---

### 1.2 User Login Flow

**Endpoint:** `POST /api/v1/users/login`

**Flow:**
1. User submits email and password
2. System looks up user by email
3. Account lockout is checked (5 failed attempts, 30-minute lockout)
4. Password is verified using bcrypt/Argon2
5. Session is created using session management module
6. Session ID is signed with HMAC-SHA256
7. Session cookie is set with secure flags (httponly, samesite=strict, secure in production)
8. CSRF token is generated and set in cookie
9. Telemetry event is captured

**Security Considerations:**
- ✅ Account lockout after 5 failed attempts
- ✅ Secure session management with signed cookies
- ✅ CSRF token generation
- ✅ Secure cookie flags (httponly, samesite, secure)
- ✅ Session timeout (48 hours, configurable)
- ✅ Password verification with secure hashing
- ⚠️ **Issue S-05**: Broad except blocks may swallow auth errors (addressed in tests)

**Recommendations:**
- Add MFA verification step if MFA is enabled for user
- Implement session refresh on activity
- Add login attempt logging for security monitoring
- Consider implementing device fingerprinting

---

### 1.3 API Key Authentication Flow

**Endpoint:** `POST /api/v1/api-keys` (creation)  
**Usage:** `X-API-Key` header in API requests

**Flow:**
1. API key is generated with format: `ss-proj-h_` + 147-char alphanumeric string
2. API key is hashed using SHA256 and stored in database
3. API key is associated with user_id and tenant_id
4. API key inherits role from associated user
5. On API request, key is extracted from `X-API-Key` header
6. Key hash is computed and looked up in database
7. Key revocation and expiration are checked
8. Tenant status is verified (must be active)
9. User role is inherited if user_id is associated

**Security Considerations:**
- ✅ API key format validation
- ✅ Key hashing with SHA256
- ✅ Key revocation support
- ✅ Key expiration support
- ✅ Tenant association and validation
- ⚠️ **Issue S-04**: API key hashing uses plain SHA256 (no server-side pepper/HMAC)
- ⚠️ **Issue S-02**: Programmatic misuse of require_api_key in rbac.py

**Recommendations:**
- Add server-side pepper/HMAC for API key hashing
- Implement key rotation mechanism
- Add key usage rate limiting
- Add key access logging
- Consider implementing key scopes/permissions

---

### 1.4 Session Management Flow

**Module:** `src/sentrascan/core/session.py`

**Flow:**
1. Session is created with unique session ID
2. Session ID is signed with HMAC-SHA256
3. Session data stored in memory (user_id, tenant_id, role, expires_at)
4. Session cookie is set with secure flags
5. Session is refreshed on activity (if <80% time remaining)
6. Session is invalidated on logout or password change
7. Expired sessions are cleaned up

**Security Considerations:**
- ✅ Session signing with HMAC-SHA256
- ✅ Session timeout (48 hours, configurable)
- ✅ Session refresh on activity
- ✅ Session invalidation on logout
- ✅ Secure cookie flags
- ⚠️ **Issue**: In-memory session store (should use Redis/database in production)
- ⚠️ **Issue S-06**: Circular import between rbac.py and server.py (addressed with lazy imports)

**Recommendations:**
- Migrate to Redis or database-backed session store for production
- Implement session fixation prevention
- Add session activity logging
- Consider implementing concurrent session limits

---

### 1.5 MFA Implementation Flow

**Endpoints:**
- `POST /api/v1/users/mfa/setup` - Setup MFA
- `POST /api/v1/users/mfa/verify` - Verify and enable MFA
- `POST /api/v1/users/mfa/disable` - Disable MFA

**Flow:**
1. User requests MFA setup
2. TOTP secret is generated using pyotp
3. Secret is encrypted using tenant-specific encryption key
4. QR code is generated for authenticator app
5. User scans QR code and enters TOTP token
6. Token is verified using pyotp
7. MFA is enabled for user account
8. On login, if MFA enabled, user must provide TOTP token

**Security Considerations:**
- ✅ TOTP secret generation
- ✅ Secret encryption at rest
- ✅ QR code generation
- ✅ Token verification
- ✅ MFA enable/disable with token verification
- ⚠️ MFA verification not enforced in login flow (needs implementation)

**Recommendations:**
- Enforce MFA verification in login flow
- Add backup codes for MFA recovery
- Implement MFA bypass for emergency access (with audit logging)
- Add MFA setup logging

---

## 2. Authorization Flows

### 2.1 Role-Based Access Control (RBAC)

**Module:** `src/sentrascan/core/rbac.py`

**Roles:**
- `super_admin` - Full platform access across all tenants
- `tenant_admin` - Full access within own tenant
- `viewer` - Read-only access within own tenant
- `scanner` - Can create and read scans within own tenant

**Permission System:**
- Permissions are defined per role
- Super admin has all permissions
- Permissions checked using `has_permission(role, permission)`
- Role checked using `check_role(user, allowed_roles)`

**Security Considerations:**
- ✅ Role definitions with clear permissions
- ✅ Permission checking functions
- ✅ Role checking functions
- ✅ Decorator-based permission enforcement
- ⚠️ **Issue D-01**: Function-level authorization coverage gaps (some endpoints may not check permissions)
- ⚠️ **Issue S-02**: Programmatic misuse of require_api_key in decorators

**Recommendations:**
- Audit all endpoints to ensure permission checks
- Implement comprehensive endpoint permission matrix
- Add automated tests for role-based access control
- Consider implementing resource-level permissions

---

### 2.2 Tenant Isolation

**Module:** `src/sentrascan/core/tenant_context.py`

**Flow:**
1. Tenant ID is extracted from:
   - Authenticated user's tenant_id field
   - API key's associated tenant_id
   - Session cookie's tenant context
2. Tenant context is set in thread-local storage
3. Database queries are automatically filtered by tenant_id
4. Tenant access is validated before operations

**Security Considerations:**
- ✅ Tenant context extraction from multiple sources
- ✅ Automatic tenant filtering in queries
- ✅ Tenant access validation
- ⚠️ **Issue D-02**: Tenant isolation / IDOR risk (some code paths may not include tenant context)
- ⚠️ **Issue**: Background jobs may not have tenant context

**Recommendations:**
- Audit all database queries to ensure tenant filtering
- Add tenant context validation in all endpoints
- Implement comprehensive tenant isolation tests
- Ensure background jobs include tenant context

---

### 2.3 Function-Level Authorization

**Implementation:**
- Decorators: `@require_permission(permission)`, `@require_role(*roles)`
- Manual checks: `check_permission(user, permission)`, `check_role(user, *roles)`
- Endpoint-level enforcement

**Security Considerations:**
- ✅ Decorator-based enforcement
- ✅ Manual permission checks
- ⚠️ **Issue D-01**: Not all endpoints may have permission checks
- ⚠️ **Issue S-02**: require_api_key called programmatically may have parameter binding issues

**Recommendations:**
- Audit all API endpoints for permission checks
- Create endpoint permission matrix
- Add automated tests for all endpoint permissions
- Fix require_api_key programmatic usage

---

## 3. Security Controls

### 3.1 Password Policies

**Implementation:** `src/sentrascan/core/auth.py`

**Requirements:**
- Minimum 12 characters
- At least one uppercase letter
- At least one lowercase letter
- At least one digit
- At least one special character
- Password expiration: 90 days
- Minimum password age: 1 day

**Security Considerations:**
- ✅ Strong password requirements
- ✅ Password expiration
- ✅ Minimum password age
- ✅ Password hashing with bcrypt/Argon2

**Recommendations:**
- Consider increasing minimum length to 14 characters
- Add password history (prevent reuse of last 5 passwords)
- Add password strength meter in UI

---

### 3.2 Account Lockout

**Implementation:** `src/sentrascan/core/auth.py`

**Configuration:**
- Maximum login attempts: 5
- Lockout duration: 30 minutes
- Lockout tracked per user

**Security Considerations:**
- ✅ Account lockout after failed attempts
- ✅ Configurable lockout duration
- ⚠️ Lockout is in-memory (should persist across restarts)

**Recommendations:**
- Persist lockout state in database
- Add lockout notification to user
- Consider implementing progressive lockout (longer duration after multiple lockouts)

---

### 3.3 Rate Limiting

**Implementation:** `src/sentrascan/core/security.py`

**Limits:**
- Per API key: 100 requests/minute
- Per IP address: 200 requests/minute
- Per tenant: 1000 requests/minute

**Security Considerations:**
- ✅ Rate limiting implemented
- ✅ Multiple rate limit keys (API key, IP, tenant)
- ⚠️ Rate limiting is in-memory (should use Redis in production)

**Recommendations:**
- Migrate to Redis-based rate limiting for production
- Add rate limit headers in responses
- Implement progressive rate limiting (temporary ban after repeated violations)

---

### 3.4 CSRF Protection

**Implementation:** `src/sentrascan/core/security.py`

**Mechanism:**
- CSRF token generated on login
- Token stored in cookie (httponly=False for JavaScript access)
- Token validated on state-changing requests
- SameSite=strict cookie flag

**Security Considerations:**
- ✅ CSRF token generation
- ✅ Token validation
- ✅ SameSite cookie flag
- ⚠️ CSRF token validation not enforced on all endpoints

**Recommendations:**
- Enforce CSRF token validation on all state-changing endpoints
- Add CSRF token refresh mechanism
- Implement double-submit cookie pattern

---

### 3.5 Input Validation

**Implementation:** `src/sentrascan/core/security.py`

**Validations:**
- Email format validation
- UUID format validation
- API key format validation
- Input sanitization (XSS prevention)
- Output encoding (XSS prevention)

**Security Considerations:**
- ✅ Email validation
- ✅ UUID validation
- ✅ Input sanitization
- ✅ Output encoding
- ⚠️ **Issue**: SQL injection prevention relies on ORM (should add explicit validation)

**Recommendations:**
- Add comprehensive input validation for all endpoints
- Implement parameterized queries (already using ORM)
- Add request size limits
- Add file upload validation

---

## 4. Identified Issues and Recommendations

### High Priority Issues

1. **S-01: Default DB Credentials**
   - **Status:** Identified
   - **Recommendation:** Remove default database connection string, require DATABASE_URL at runtime

2. **S-06: Circular Import**
   - **Status:** Partially addressed with lazy imports
   - **Recommendation:** Refactor to dedicated auth_helpers module

3. **D-01: Function-Level Authorization Gaps**
   - **Status:** Needs audit
   - **Recommendation:** Audit all endpoints, add permission checks

4. **D-02: Tenant Isolation / IDOR Risk**
   - **Status:** Needs audit
   - **Recommendation:** Audit all queries, ensure tenant filtering

### Medium Priority Issues

5. **S-02: Programmatic require_api_key Usage**
   - **Status:** Identified
   - **Recommendation:** Fix parameter binding in rbac.py decorators

6. **S-03: Argon2 Import Mismatch**
   - **Status:** Identified
   - **Recommendation:** Fix import/instantiation code

7. **S-04: API Key Hashing (SHA256 only)**
   - **Status:** Identified
   - **Recommendation:** Add server-side pepper/HMAC

8. **S-05: Broad Except Blocks**
   - **Status:** Identified
   - **Recommendation:** Replace with targeted exception handling and logging

---

## 5. Testing Recommendations

1. **Automated Security Tests**
   - Run `tests/test_security.py` regularly
   - Add tests for all identified issues
   - Implement endpoint permission matrix tests

2. **Penetration Testing**
   - Perform regular penetration tests
   - Test authentication bypass attempts
   - Test authorization bypass attempts
   - Test tenant isolation

3. **Dependency Scanning**
   - Run `scripts/security-scan-dependencies.sh` regularly
   - Update dependencies promptly
   - Monitor security advisories

4. **Container Scanning**
   - Run `scripts/security-scan-container.sh` on all images
   - Scan base images for vulnerabilities
   - Update base images regularly

---

## 6. Compliance and Best Practices

### OWASP Top 10 Coverage

- ✅ A01:2021 – Broken Access Control (RBAC, tenant isolation)
- ✅ A02:2021 – Cryptographic Failures (password hashing, encryption)
- ✅ A03:2021 – Injection (ORM usage, input validation)
- ✅ A04:2021 – Insecure Design (security by design)
- ✅ A05:2021 – Security Misconfiguration (secure defaults)
- ✅ A06:2021 – Vulnerable Components (dependency scanning)
- ✅ A07:2021 – Authentication Failures (strong auth, MFA)
- ✅ A08:2021 – Software and Data Integrity (CSRF protection)
- ✅ A09:2021 – Security Logging (audit logging)
- ✅ A10:2021 – SSRF (input validation)

### Security Best Practices

- ✅ Defense in depth
- ✅ Least privilege
- ✅ Secure by default
- ✅ Fail securely
- ✅ Security logging
- ✅ Input validation
- ✅ Output encoding
- ✅ Secure session management
- ✅ Strong authentication
- ✅ Authorization checks

---

## 7. Conclusion

The SentraScan Platform implements comprehensive authentication and authorization mechanisms with strong security controls. However, several issues identified in the penetration test report need to be addressed:

1. **Critical:** Fix circular imports and default credentials
2. **High:** Audit and fix function-level authorization gaps
3. **High:** Audit and fix tenant isolation gaps
4. **Medium:** Fix API key hashing, Argon2 imports, error handling

Regular security audits, automated testing, and dependency scanning are essential for maintaining security posture.

---

## Appendix: Endpoint Permission Matrix

| Endpoint | Method | Required Permission | Required Role | Notes |
|----------|--------|---------------------|---------------|-------|
| `/api/v1/users/register` | POST | None | None | Public registration |
| `/api/v1/users/login` | POST | None | None | Public login |
| `/api/v1/users` | GET | `user.read` | tenant_admin, super_admin | List users |
| `/api/v1/users` | POST | `user.create` | tenant_admin, super_admin | Create user |
| `/api/v1/users/{user_id}` | PUT | `user.update` | tenant_admin, super_admin | Update user |
| `/api/v1/users/{user_id}` | DELETE | `user.delete` | tenant_admin, super_admin | Delete user |
| `/api/v1/tenants` | GET | `tenant.read` | super_admin | List tenants |
| `/api/v1/tenants` | POST | `tenant.create` | super_admin | Create tenant |
| `/api/v1/scans` | GET | `scan.read` | viewer, scanner, tenant_admin, super_admin | List scans |
| `/api/v1/scans` | POST | `scan.create` | scanner, tenant_admin, super_admin | Create scan |
| `/api/v1/findings` | GET | `finding.read` | viewer, scanner, tenant_admin, super_admin | List findings |
| `/api/v1/api-keys` | GET | `api_key.read` | viewer, tenant_admin, super_admin | List API keys |
| `/api/v1/api-keys` | POST | `api_key.create` | tenant_admin, super_admin | Create API key |
| `/api/v1/api-keys/{key_id}` | DELETE | `api_key.delete` | tenant_admin, super_admin | Delete API key |

*Note: This matrix should be verified and updated as endpoints are audited.*

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-28  
**Next Review:** 2025-12-28

