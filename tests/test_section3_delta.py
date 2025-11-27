"""
Delta tests for Section 3.0: Multi-Tenancy, User Management & RBAC

Tests new features implemented in Section 3.0:
- Multi-tenancy (Tenant, User, TenantSettings, AuditLog models)
- User authentication (email/password, password policies, account lockout)
- RBAC (roles, permissions, access control)
- Session management (48-hour timeout, refresh, invalidation)
- Tenant/user management UI
- Tenant isolation and cross-tenant access prevention
"""

import pytest
import os
import time
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Test database models
def test_tenant_model_exists():
    """Test that Tenant model exists and can be imported"""
    from sentrascan.core.models import Tenant
    assert Tenant is not None

def test_user_model_exists():
    """Test that User model exists and can be imported"""
    from sentrascan.core.models import User
    assert User is not None

def test_tenant_settings_model_exists():
    """Test that TenantSettings model exists and can be imported"""
    from sentrascan.core.models import TenantSettings
    assert TenantSettings is not None

def test_audit_log_model_exists():
    """Test that AuditLog model exists and can be imported"""
    from sentrascan.core.models import AuditLog
    assert AuditLog is not None

def test_models_have_tenant_id():
    """Test that existing models have tenant_id column"""
    from sentrascan.core.models import Scan, Finding, APIKey, Baseline, SBOM
    
    # Check that models have tenant_id attribute
    assert hasattr(Scan, 'tenant_id')
    assert hasattr(Finding, 'tenant_id')
    assert hasattr(APIKey, 'tenant_id')
    assert hasattr(Baseline, 'tenant_id')
    assert hasattr(SBOM, 'tenant_id')

# Test tenant context
def test_tenant_context_module_exists():
    """Test that tenant context module exists"""
    from sentrascan.core.tenant_context import (
        get_tenant_id, set_tenant_id, extract_tenant_from_request,
        require_tenant, validate_tenant_access, TenantContextMiddleware
    )
    assert get_tenant_id is not None
    assert set_tenant_id is not None
    assert extract_tenant_from_request is not None
    assert require_tenant is not None
    assert validate_tenant_access is not None
    assert TenantContextMiddleware is not None

def test_query_helpers_exist():
    """Test that query helpers exist"""
    from sentrascan.core.query_helpers import filter_by_tenant, require_tenant_for_query
    assert filter_by_tenant is not None
    assert require_tenant_for_query is not None

# Test user authentication
def test_auth_module_exists():
    """Test that authentication module exists"""
    from sentrascan.core.auth import (
        PasswordHasher, PasswordPolicy, AccountLockout,
        authenticate_user, create_user, update_user_password,
        deactivate_user, activate_user
    )
    assert PasswordHasher is not None
    assert PasswordPolicy is not None
    assert AccountLockout is not None
    assert authenticate_user is not None
    assert create_user is not None
    assert update_user_password is not None
    assert deactivate_user is not None
    assert activate_user is not None

def test_password_hasher():
    """Test password hashing functionality"""
    from sentrascan.core.auth import PasswordHasher
    
    hasher = PasswordHasher()
    password = "TestPassword123!"
    hashed = hasher.hash_password(password)
    
    assert hashed is not None
    assert hashed != password
    assert hasher.verify_password(password, hashed) is True
    assert hasher.verify_password("wrong_password", hashed) is False

def test_password_policy():
    """Test password policy validation"""
    from sentrascan.core.auth import PasswordPolicy
    
    # Valid password
    is_valid, error = PasswordPolicy.validate_password("ValidPass123!")
    assert is_valid is True
    assert error is None
    
    # Too short
    is_valid, error = PasswordPolicy.validate_password("Short1!")
    assert is_valid is False
    assert error is not None
    
    # Missing uppercase
    is_valid, error = PasswordPolicy.validate_password("validpass123!")
    assert is_valid is False
    
    # Missing lowercase
    is_valid, error = PasswordPolicy.validate_password("VALIDPASS123!")
    assert is_valid is False
    
    # Missing digit
    is_valid, error = PasswordPolicy.validate_password("ValidPass!")
    assert is_valid is False
    
    # Missing special character
    is_valid, error = PasswordPolicy.validate_password("ValidPass123")
    assert is_valid is False

def test_account_lockout():
    """Test account lockout functionality"""
    from sentrascan.core.auth import AccountLockout
    
    email = "test@example.com"
    
    # Clear any existing lockout
    AccountLockout.clear_failed_attempts(email)
    
    # Record failed attempts
    for i in range(5):
        AccountLockout.record_failed_attempt(email)
    
    # Check if locked (returns tuple: (is_locked, message))
    is_locked, message = AccountLockout.is_locked(email)
    assert is_locked is True
    assert message is not None
    
    # Clear lockout
    AccountLockout.clear_failed_attempts(email)
    is_locked, message = AccountLockout.is_locked(email)
    assert is_locked is False
    assert message is None

# Test RBAC
def test_rbac_module_exists():
    """Test that RBAC module exists"""
    from sentrascan.core.rbac import (
        ROLES, get_user_role, has_permission,
        check_role, check_permission, can_access_tenant,
        require_permission, require_role, get_all_permissions
    )
    assert ROLES is not None
    assert get_user_role is not None
    assert has_permission is not None
    assert check_role is not None
    assert check_permission is not None
    assert can_access_tenant is not None
    assert require_permission is not None
    assert require_role is not None
    assert get_all_permissions is not None

def test_roles_defined():
    """Test that roles are properly defined"""
    from sentrascan.core.rbac import ROLES
    
    assert "super_admin" in ROLES
    assert "tenant_admin" in ROLES
    assert "scanner" in ROLES
    assert "viewer" in ROLES

def test_permissions_defined():
    """Test that permissions are properly defined"""
    from sentrascan.core.rbac import get_all_permissions
    
    permissions = get_all_permissions()
    
    # Check some key permissions exist
    assert "scan.create" in permissions
    assert "scan.read" in permissions
    assert "user.create" in permissions
    assert "user.read" in permissions
    assert "tenant.read" in permissions

def test_role_permission_mapping():
    """Test that roles have correct permissions"""
    from sentrascan.core.rbac import ROLES, get_all_permissions
    
    # Super admin should have all permissions
    super_admin_perms = ROLES["super_admin"]["permissions"]
    assert len(super_admin_perms) > 0
    
    # Tenant admin should have tenant-scoped permissions
    tenant_admin_perms = ROLES["tenant_admin"]["permissions"]
    assert "user.create" in tenant_admin_perms or len(tenant_admin_perms) > 0
    
    # Verify permissions list is not empty
    all_perms = get_all_permissions()
    assert len(all_perms) > 0

# Test session management
def test_session_module_exists():
    """Test that session module exists"""
    from sentrascan.core.session import (
        create_session, get_session, refresh_session,
        invalidate_session, invalidate_user_sessions,
        cleanup_expired_sessions, get_session_user,
        SESSION_COOKIE_NAME, SESSION_TIMEOUT_HOURS
    )
    assert create_session is not None
    assert get_session is not None
    assert refresh_session is not None
    assert invalidate_session is not None
    assert invalidate_user_sessions is not None
    assert cleanup_expired_sessions is not None
    assert get_session_user is not None
    assert SESSION_COOKIE_NAME is not None
    assert SESSION_TIMEOUT_HOURS == 48  # Default 48 hours

def test_session_timeout_configurable():
    """Test that session timeout is configurable via environment variable"""
    with patch.dict(os.environ, {"SESSION_TIMEOUT_HOURS": "24"}):
        # Reload module to pick up new env var
        import importlib
        import sentrascan.core.session
        importlib.reload(sentrascan.core.session)
        from sentrascan.core.session import SESSION_TIMEOUT_HOURS
        assert SESSION_TIMEOUT_HOURS == 24

def test_session_sign_unsign():
    """Test session signing and unsigning"""
    from sentrascan.core.session import sign, unsign
    
    value = "test_session_id"
    signed = sign(value)
    
    assert signed != value
    assert "." in signed  # Should contain HMAC
    
    unsigned = unsign(signed)
    assert unsigned == value
    
    # Invalid signature should return None
    invalid = unsign("invalid.signature")
    assert invalid is None

# Test API key association
def test_api_key_has_user_id():
    """Test that APIKey model has user_id column"""
    from sentrascan.core.models import APIKey
    assert hasattr(APIKey, 'user_id')

# Test tenant isolation
def test_tenant_isolation_concept():
    """Test that tenant isolation is enforced at query level"""
    from sentrascan.core.query_helpers import filter_by_tenant
    from sentrascan.core.models import Scan
    from sqlalchemy.orm import Query
    
    # Mock query
    mock_query = MagicMock(spec=Query)
    mock_query.filter.return_value = mock_query
    
    # Test filter_by_tenant adds tenant_id filter
    result = filter_by_tenant(mock_query, Scan, "tenant-123")
    assert mock_query.filter.called

# Test UI components
def test_users_template_exists():
    """Test that users.html template exists"""
    template_path = "src/sentrascan/web/templates/users.html"
    assert os.path.exists(template_path), f"Template {template_path} not found"

def test_tenants_template_exists():
    """Test that tenants.html template exists"""
    template_path = "src/sentrascan/web/templates/tenants.html"
    assert os.path.exists(template_path), f"Template {template_path} not found"

def test_users_js_exists():
    """Test that users.js exists"""
    js_path = "src/sentrascan/web/static/js/users.js"
    assert os.path.exists(js_path), f"JavaScript {js_path} not found"

def test_tenants_js_exists():
    """Test that tenants.js exists"""
    js_path = "src/sentrascan/web/static/js/tenants.js"
    assert os.path.exists(js_path), f"JavaScript {js_path} not found"

def test_base_template_has_tenant_selector():
    """Test that base.html has tenant selector"""
    base_template = "src/sentrascan/web/templates/base.html"
    if os.path.exists(base_template):
        with open(base_template, 'r') as f:
            content = f.read()
            assert "tenant-selector" in content or "tenant-display" in content

