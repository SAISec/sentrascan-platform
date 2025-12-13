# Product Requirements Document: Documentation & Branding

## Introduction/Overview

This PRD focuses on cleaning up documentation by removing outdated baseline references and implementing proper access controls for admin-only documentation. Additionally, it updates all branding from "SentraScan Platform" to "SentraScan" throughout the entire system.

The current system has baseline references in documentation that need to be removed, lacks proper access control for admin documentation, and uses inconsistent branding. This PRD addresses these issues to provide clean, properly secured documentation and consistent branding.

The goal is to improve documentation quality, security, and branding consistency across the entire SentraScan system.

## Goals

1. **Remove Baseline References**: Clean up all documentation to remove references to baseline functionality that is no longer relevant.

2. **Implement Documentation Access Control**: Add RBAC-based access control to ensure only authorized users can access admin-only documentation.

3. **Update Branding**: Change all references from "SentraScan Platform" to "SentraScan" throughout the codebase, documentation, and user-facing content.

4. **Improve Documentation Structure**: Organize documentation into public and admin-only sections with clear navigation.

## User Stories

### Documentation Access
- **As an admin**, I want to access admin-only documentation, so that I can understand advanced configuration options.
- **As a regular user**, I want to be prevented from accessing admin documentation, so that I don't see information I shouldn't have access to.
- **As a developer**, I want documentation to be free of outdated baseline references, so that I'm not confused by irrelevant information.

### Branding
- **As a user**, I want to see consistent "SentraScan" branding throughout the application, so that the product identity is clear.
- **As a developer**, I want all code references to use "SentraScan" consistently, so that the codebase is clean and professional.

## Functional Requirements

### 1. Baseline Reference Removal

1.1. **Documentation Cleanup**
   - The system must remove all references to "baseline" functionality from documentation.
   - The system must update user guides to remove baseline-related sections.
   - The system must update technical documentation to remove baseline API endpoints and data models.
   - The system must update glossary entries to remove baseline-related terms.
   - The system must ensure no documentation mentions baseline creation, comparison, or management.

1.2. **Files to Update**
   - Remove baseline sections from `docs/USER-GUIDE.md`
   - Remove baseline sections from `docs/TECHNICAL-DOCUMENTATION.md`
   - Remove baseline entries from `docs/glossary/README.md`
   - Remove baseline sections from `docs/faq/README.md`
   - Remove baseline references from `docs/best-practices/README.md`
   - Remove baseline references from `docs/how-to/README.md`
   - Update any other documentation files that mention baselines

1.3. **Content Updates**
   - Replace baseline-related content with relevant alternatives or remove entirely.
   - Update workflow diagrams to remove baseline steps.
   - Update API documentation to remove baseline endpoints.
   - Update code examples to remove baseline usage.

### 2. Admin-Only Documentation

2.1. **Documentation Structure**
   - The system must create separate admin-only documentation files (e.g., `ADMIN-GUIDE.md`).
   - The system must create `/docs/admin/` directory for admin-only documentation.
   - The system must keep public documentation in `/docs/` directory.
   - The system must organize admin documentation by topic (user management, policy management, etc.).

2.2. **Admin Documentation Content**
   - The system must document the new policy update workflow in admin guides.
   - The system must document tenant-level user creation policies and procedures.
   - The system must document the compliance manager role and responsibilities.
   - The system must document email service setup (Gmail SMTP configuration).
   - The system must document super admin fallback (manual user verification and password reset).
   - The system must document policy template creation and management.
   - The system must update API documentation to reflect policy approval endpoints.

2.3. **Documentation Navigation**
   - The system must update documentation navigation to filter based on user role.
   - The system must show admin documentation links only to users with admin roles (super_admin, tenant_admin).
   - The system must hide admin documentation from viewers, scanners, and compliance managers in the UI.
   - The system must provide clear indication of admin-only vs. public documentation.

### 3. Documentation Access Control

3.1. **RBAC Middleware**
   - The system must implement RBAC checks when rendering documentation pages.
   - The system must return 403 Forbidden for non-admin users attempting to access admin documentation via direct URL.
   - The system must log unauthorized documentation access attempts with full details (user_id, role, requested path, timestamp, IP address).

3.2. **UI Access Control**
   - The system must hide admin documentation links from non-admin users in navigation.
   - The system must show clear access denied messages if non-admin users attempt to access admin docs.
   - The system must consider adding a "Documentation" section in user settings showing available docs based on role.

3.3. **Documentation Filtering**
   - The system must filter documentation index based on user role.
   - The system must show only accessible documentation in documentation listings.
   - The system must provide clear visual distinction between public and admin documentation.

### 4. Branding Updates

4.1. **Application Name**
   - The system must change all references from "SentraScan Platform" to "SentraScan" throughout the codebase.
   - The system must update all user-facing text, titles, and headers.
   - The system must update all API response messages.
   - The system must update all error messages.
   - The system must update all log messages.
   - The system must update documentation titles and headers.
   - The system must update HTML page titles and meta tags.
   - The system must ensure no instance of "SentraScan Platform" remains in the codebase.

4.2. **Code References**
   - The system must update all code comments that mention "SentraScan Platform".
   - The system must update all docstrings that mention "SentraScan Platform".
   - The system must update all configuration file comments.
   - The system must update all environment variable documentation.

4.3. **Documentation References**
   - The system must update all documentation files to use "SentraScan" instead of "SentraScan Platform".
   - The system must update README files.
   - The system must update API documentation.
   - The system must update user guides.

4.4. **UI References**
   - The system must update all HTML templates to use "SentraScan" branding.
   - The system must update all page titles.
   - The system must update all navigation labels.
   - The system must update all button text and labels.

4.5. **Validation**
   - The system must perform automated search to verify no "SentraScan Platform" references remain.
   - The system must create validation script to check for remaining references.
   - The system must include branding check in CI/CD pipeline.

## Non-Goals (Out of Scope)

1. **Baseline Code Removal**: This PRD focuses on removing baseline references from documentation only. Actual removal of baseline code/data models is out of scope.

2. **Documentation Rewrite**: This PRD focuses on removing baseline references and adding access control. Complete documentation rewrite is out of scope.

3. **Multi-Language Documentation**: Documentation remains in English only. Multi-language support is out of scope.

4. **Documentation Search**: Advanced documentation search functionality is out of scope.

5. **Documentation Versioning**: Documentation versioning system is out of scope.

## Design Considerations

### Documentation Structure

1. **Directory Organization**
   ```
   /docs/
     /admin/
       ADMIN-GUIDE.md
       EMAIL_SETUP.md
       SUPER_ADMIN_FALLBACK.md
       COMPLIANCE_MANAGER_GUIDE.md
       POLICY_TEMPLATES.md
     /api/
     /user-guide/
     /getting-started/
     ...
   ```

2. **Navigation Structure**
   - Public documentation: Visible to all authenticated users
   - Admin documentation: Visible only to super_admin and tenant_admin
   - Clear visual indicators for admin-only sections

### Branding Consistency

1. **Branding Guidelines**
   - Product name: "SentraScan" (one word, capital S, capital C)
   - Never use "SentraScan Platform"
   - Use "SentraScan" in all user-facing text
   - Use "SentraScan" in all code comments and docstrings

2. **Search and Replace Strategy**
   - Use case-insensitive search to find all instances
   - Review each instance to ensure context is appropriate
   - Update code, documentation, and UI consistently
   - Validate changes don't break functionality

## Technical Considerations

### Database Schema Changes

**No database changes required** - This PRD only affects documentation and code/text references.

### API Endpoints

1. **Documentation Endpoints**
   - `GET /docs/admin/*` - Admin-only documentation (with RBAC check)
   - `GET /docs/*` - Public documentation
   - `GET /docs` - Documentation index (filtered by role)

### Code Changes

1. **Documentation Access Control**
   - Create middleware to check user role before serving documentation
   - Return 403 for unauthorized access
   - Log unauthorized access attempts

2. **Branding Updates**
   - Update all Python files (code, comments, docstrings)
   - Update all HTML templates
   - Update all documentation files
   - Update configuration files
   - Update environment variable documentation

### Testing Requirements

1. **Documentation Access Control Tests**
   - Test admin users can access admin documentation
   - Test non-admin users are blocked from admin documentation
   - Test unauthorized access attempts are logged
   - Test documentation filtering works correctly

2. **Branding Validation Tests**
   - Automated test to verify no "SentraScan Platform" references remain
   - Test all user-facing text uses "SentraScan"
   - Test API responses use "SentraScan"
   - Test error messages use "SentraScan"

## Success Metrics

1. **Documentation Access**
   - Zero unauthorized access to admin documentation (measured via audit logs)
   - 100% of admin users can access admin documentation
   - 100% of non-admin users blocked from admin documentation

2. **Branding Consistency**
   - Zero instances of "SentraScan Platform" in codebase (verified via automated search)
   - 100% of user-facing text uses "SentraScan" branding
   - 100% of API responses use "SentraScan" branding
   - 100% of documentation uses "SentraScan" branding

3. **Documentation Quality**
   - All baseline references removed from documentation
   - All admin documentation properly secured
   - Documentation structure is clear and organized

## Resolved Decisions

1. **Baseline Removal**: Remove from documentation only, not from code/data models.

2. **Documentation Access**: RBAC-based access control with clear separation of admin and public docs.

3. **Branding**: Complete change from "SentraScan Platform" to "SentraScan" everywhere.

4. **Documentation Structure**: Separate `/docs/admin/` directory for admin-only documentation.

---

**Document Version**: 1.0  
**Last Updated**: 2025-01-27  
**Status**: Ready for Implementation  
**Part of**: 4-PRD Breakdown for RBAC, User, and Tenant Management Improvements  
**Dependencies**: PRD B (for RBAC checks in documentation access control - but baseline removal can start immediately)
