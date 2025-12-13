# Product Requirements Document: Tenant Management & Compliance Framework

## Introduction/Overview

This PRD focuses on improving tenant management transparency in the UI and implementing the compliance manager role with RBAC enhancements. The current system lacks clear tenant visibility for users and doesn't have a compliance manager role for policy and exception approvals. This PRD addresses these gaps by providing better tenant management UI and establishing the compliance framework needed for governance workflows.

The goal is to enhance tenant-to-user mapping transparency, implement the compliance manager role, and add RBAC-based documentation access control.

This PRD emphasizes code reuse, functional reuse, and comprehensive testing to ensure maintainability and security.

## Goals

1. **Improve Tenant-to-User Mapping Transparency**: Enable clear visibility and management of tenant assignments in the UI, with role-appropriate access controls.

2. **Implement Compliance Manager Role**: Create a new role for policy and exception approvals with proper RBAC integration.

3. **Enhance RBAC System**: Add new permissions and role validation logic to support compliance workflows.

4. **Implement Documentation Access Control**: Add RBAC-based access control for admin-only documentation.

5. **Improve Tenant Management UI**: Create searchable, filterable tenant selection and display tenant context throughout the application.

## User Stories

### Tenant Management
- **As a super admin**, I want to see all tenants and assign users to any tenant, so that I can manage the entire platform effectively.
- **As a tenant admin**, I want to see only my tenant and manage users within my tenant, so that I can maintain proper tenant isolation.
- **As a regular user**, I want to see which tenant I belong to in my profile, so that I understand my organizational context.

### Compliance Manager Role
- **As a tenant admin**, I want to assign compliance managers to my tenant, so that policy and exception approvals can be handled.
- **As a compliance manager**, I want to have appropriate permissions for approving policies and exceptions, so that I can fulfill my governance responsibilities.
- **As a system administrator**, I want compliance managers to be properly isolated to their tenant, so that security is maintained.

### Documentation Access
- **As an admin**, I want to access admin-only documentation, so that I can understand advanced configuration options.
- **As a regular user**, I want to be prevented from accessing admin documentation, so that I don't see information I shouldn't have access to.

## Functional Requirements

### 1. Tenant-to-User Mapping in UI

1.1. **Super Admin Tenant Management**
   - The system must allow super admins to view all tenants in a searchable, filterable list.
   - The system must allow super admins to assign users to any tenant via a dropdown or searchable tenant selector.
   - The system must display tenant information (name, ID, active status) for all tenants to super admins.
   - The system must show tenant count (number of users) for each tenant.
   - The system must allow super admins to filter tenants by name, active status.

1.2. **Tenant Admin Tenant Management**
   - The system must restrict tenant admins to view only their own tenant.
   - The system must allow tenant admins to assign users only to their own tenant.
   - The system must prevent tenant admins from viewing or accessing other tenants' data.
   - The system must display tenant information clearly for tenant admins.

1.3. **User Tenant Visibility**
   - The system must display the user's current tenant name and ID in their profile/settings page.
   - The system must show tenant information in a clear, non-technical format (e.g., "Organization: Acme Corp").
   - The system must prevent regular users from changing their tenant assignment.
   - The system must display tenant information in user profile header or sidebar.

1.4. **Tenant Selection UI**
   - The system must provide a searchable dropdown list for tenant selection when creating or editing users.
   - The system must support filtering tenants by name for super admins.
   - The system must show tenant status (active/inactive) in the selection UI.
   - The system must improve UI transparency by clearly showing which tenant a user belongs to in all relevant screens.
   - The system must use autocomplete/search functionality for better UX with many tenants.

1.5. **Tenant Management Transparency**
   - The system must fix any UI transparency issues where tenant context is unclear or hidden.
   - The system must display tenant information prominently in navigation or header where appropriate.
   - The system must show tenant context in user management, scan management, and settings pages.
   - The system must display tenant name in page headers or breadcrumbs.

### 2. Compliance Manager Role

2.1. **Role Definition**
   - The system must implement a new "compliance_manager" role at the tenant level.
   - The system must add `compliance_manager` to ROLES dictionary in `rbac.py`.
   - The system must define permissions for compliance_manager:
     * `policy.read` - View policies
     * `policy.approve` - Approve/reject policy changes
     * `exception.read` - View exceptions
     * `exception.approve` - Approve/reject exceptions
     * `policy.create` - Create policies (with self-approval)
     * `policy.update` - Update policies (with self-approval)
   - The system must set tenant scope to "own" (compliance managers can only access their own tenant).
   - The system must allow multiple compliance managers per tenant.

2.2. **Role Validation**
   - The system must prevent users from having both `tenant_admin` and `compliance_manager` roles simultaneously.
   - The system must enforce role exclusivity in user creation/update endpoints.
   - The system must validate role assignments before saving to database.
   - The system must return clear error messages when role conflicts occur.

2.3. **Role Assignment**
   - The system must allow both `tenant_admin` and `super_admin` to assign `compliance_manager` role.
   - The system must allow super admin to assign compliance_manager to any user in any tenant.
   - The system must allow tenant admin to assign compliance_manager only to users in their own tenant.
   - The system must provide API endpoint: `PUT /api/v1/users/{user_id}/role` for role assignment.
   - The system must provide UI for role assignment in user management interface.

2.4. **Role Permissions Enforcement**
   - The system must enforce compliance_manager permissions on all relevant endpoints.
   - The system must allow compliance managers to self-approve their own policy changes.
   - The system must require compliance manager approval for tenant admin policy changes.
   - The system must require compliance manager approval for exception requests.

2.5. **Edge Case Handling**
   - The system must require at least one compliance manager per tenant before allowing policy changes (validation).
   - The system must prevent removal of last compliance manager in a tenant (require assigning replacement first).
   - The system must handle compliance manager deactivation gracefully (notify if last one).

### 3. RBAC Enhancements

3.1. **Permission Updates**
   - The system must add `policy.approve` permission to permission system.
   - The system must add `exception.approve` permission to permission system.
   - The system must add `user.approve` permission for user signup approval.
   - The system must update permission checking logic to support new permissions.

3.2. **Role Hierarchy**
   - The system must maintain role hierarchy: super_admin > tenant_admin > compliance_manager > viewer/scanner.
   - The system must ensure super_admin has all permissions (including new ones).
   - The system must ensure tenant_admin has appropriate permissions for tenant management.

3.3. **Permission Checking**
   - The system must update all relevant endpoints to check new permissions.
   - The system must provide clear error messages when permissions are denied.
   - The system must log permission denial attempts for security auditing.

### 4. Documentation Access Control

4.1. **Documentation Structure**
   - The system must create `/docs/admin/` directory for admin-only documentation.
   - The system must keep public documentation in `/docs/` directory.
   - The system must update documentation navigation to filter based on user role.

4.2. **RBAC Middleware for Documentation**
   - The system must implement RBAC checks when rendering documentation pages.
   - The system must return 403 Forbidden for non-admin users attempting to access admin documentation via direct URL.
   - The system must log unauthorized documentation access attempts with full details (user_id, role, requested path, timestamp, IP address).

4.3. **UI Access Control**
   - The system must hide admin documentation links from non-admin users in navigation.
   - The system must show admin documentation links only to users with admin roles (super_admin, tenant_admin).
   - The system must hide admin documentation from viewers, scanners, and compliance managers in the UI.
   - The system must show clear access denied messages if non-admin users attempt to access admin docs.

4.4. **Documentation Filtering**
   - The system must filter documentation navigation based on user role.
   - The system must show only accessible documentation in documentation index.
   - The system must provide clear indication of admin-only vs. public documentation.

## Non-Goals (Out of Scope)

1. **Policy Management**: Policy configuration and approval workflows are out of scope (covered in PRD C).

2. **Exception Management**: Exception handling and approval workflows are out of scope (covered in PRD C).

3. **User Signup**: User signup and authentication are out of scope (covered in PRD A).

4. **Email Service**: Email infrastructure is out of scope (covered in PRD A).

5. **Multi-Tenant User Assignment**: Users will remain assigned to a single tenant. Multi-tenant user membership is out of scope.

## Design Considerations

### UI/UX Requirements

1. **Tenant Selection Dropdown**
   - Implement a searchable, filterable dropdown component for tenant selection.
   - Show tenant name, ID, and active status in the dropdown.
   - For super admins, display all tenants; for tenant admins, show only their tenant.
   - Use autocomplete/search functionality for better UX with many tenants.
   - Show tenant user count in dropdown.

2. **User Profile Display**
   - Add a clear "Organization" or "Tenant" section in user profile/settings.
   - Display tenant name in a user-friendly format (not just UUID).
   - Consider adding tenant logo/branding if available.
   - Show tenant information in user profile header.

3. **Tenant Context Display**
   - Display tenant name in navigation bar or header.
   - Show tenant context in page titles or breadcrumbs.
   - Display tenant information in user management, scan management, and settings pages.
   - Use consistent tenant display format throughout application.

4. **Compliance Manager UI**
   - Add role assignment interface in user management.
   - Show compliance manager role in user list and profile.
   - Display compliance manager permissions clearly.
   - Provide UI for viewing compliance managers per tenant.

5. **Documentation Access Control UI**
   - Hide admin documentation links from non-admin users in navigation.
   - Show clear access denied messages if non-admin users attempt to access admin docs.
   - Consider adding a "Documentation" section in user settings showing available docs based on role.
   - Display role-based documentation filtering in documentation index.

## Technical Considerations

### Database Schema Changes

1. **User Model Updates**
   - No new fields needed (uses existing `role` field).
   - Role validation enforced at application level.

2. **No New Tables**
   - All functionality uses existing `users` and `tenants` tables.
   - Role information stored in `users.role` field.

### API Endpoints

1. **Tenant Management**
   - `GET /api/v1/tenants` - List tenants (filtered by role, enhanced with search/filter)
   - `GET /api/v1/tenants/{tenant_id}/users` - List users in tenant
   - `PUT /api/v1/users/{user_id}/tenant` - Update user tenant assignment (admin only)

2. **Role Management**
   - `PUT /api/v1/users/{user_id}/role` - Assign compliance_manager role (tenant_admin or super_admin only)
   - `GET /api/v1/users/{user_id}/role` - Get user role information

3. **Compliance Manager**
   - `GET /api/v1/compliance/pending-approvals` - List all pending approvals for compliance manager (placeholder for PRD C)

4. **Documentation**
   - `GET /docs/admin/*` - Admin-only documentation (with RBAC check)
   - `GET /docs/*` - Public documentation

### RBAC Updates

1. **New Role: compliance_manager**
   - Add to ROLES dictionary in `rbac.py`
   - Permissions: `policy.read`, `policy.approve`, `exception.read`, `exception.approve`, `policy.create`, `policy.update` (self-approve)
   - Tenant scope: own tenant only

2. **Role Validation Functions**
   - Create `validate_role_exclusivity()` function
   - Create `can_assign_role()` function
   - Add role validation in user creation/update endpoints

3. **Permission Updates**
   - Add `policy.approve` permission
   - Add `exception.approve` permission
   - Add `user.approve` permission (for user signup approval)

### Code Reuse Requirements

1. **Shared Utilities**
   - Create reusable role validation utilities
   - Create reusable permission checking helpers
   - All utilities must be well-documented with docstrings and type hints

2. **Reusable Components**
   - Create reusable tenant selection component for UI
   - Create reusable role assignment component
   - Create reusable documentation access control middleware

### Testing Requirements

1. **Unit Testing**
   - RBAC role definition tests
   - Permission checking tests
   - Role validation tests
   - Tenant filtering tests
   - Minimum 80% code coverage, 100% for RBAC utilities

2. **Integration Testing**
   - Tenant management UI tests
   - Compliance manager role assignment tests
   - Documentation access control tests
   - Role exclusivity enforcement tests

3. **Security Testing**
   - RBAC enforcement tests (prevent unauthorized access)
   - Tenant isolation tests (compliance manager can't access other tenants)
   - Documentation access control tests
   - Role assignment authorization tests

## Success Metrics

1. **Tenant Management**
   - 100% of users can see their tenant in profile
   - Super admins can assign users to any tenant successfully
   - Tenant admins restricted to own tenant only

2. **Compliance Manager Role**
   - Compliance manager role assigned successfully
   - Role exclusivity enforced (zero users with both tenant_admin and compliance_manager)
   - Permissions correctly enforced on all endpoints

3. **Documentation Access**
   - Zero unauthorized access to admin documentation (measured via audit logs)
   - 100% of admin users can access admin documentation
   - 100% of non-admin users blocked from admin documentation

4. **RBAC System**
   - All permission checks working correctly
   - Role validation preventing invalid assignments
   - Clear error messages for permission denials

## Audit Logging Requirements

### Compliance Manager Role Assignment Audit Logging
- The system must log all compliance_manager role assignments with maximum detail:
  * User being assigned role (user_id, email, previous role)
  * Assigner user_id, email, role (tenant_admin or super_admin)
  * Assignment timestamp
  * Tenant context
  * IP address of assigner
- The system must log all compliance_manager role removals with full details
- The system must log all role validation failures (e.g., attempting to assign both tenant_admin and compliance_manager)

### Documentation Access Audit Logging
- The system must log all unauthorized documentation access attempts with full details:
  * User_id, email, role
  * Requested path
  * Timestamp
  * IP address
  * Reason for denial

### Audit Log Storage
- Store all audit logs in the audit_logs table with JSON details field for maximum flexibility
- Ensure audit logs are immutable (no updates or deletes)
- Include all relevant context in the details JSON field
- Maintain audit log retention policy (recommended: 7 years for compliance)

## Resolved Decisions

1. **Compliance Manager Role**: New role with specific permissions for policy and exception approvals.

2. **Role Exclusivity**: Users cannot have both tenant_admin and compliance_manager roles.

3. **Role Assignment**: Both tenant_admin and super_admin can assign compliance_manager role.

4. **Documentation Access**: RBAC-based access control with clear separation of admin and public docs.

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-27  
**Status**: Ready for Implementation  
**Part of**: 4-PRD Breakdown for RBAC, User, and Tenant Management Improvements  
**Dependencies**: PRD A (for default tenant configuration - but tenant UI can start in parallel)
