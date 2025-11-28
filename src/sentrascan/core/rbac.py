"""
Role-Based Access Control (RBAC) module for SentraScan Platform.

Defines roles, permissions, and decorators for enforcing access control.
"""

from typing import List, Optional, Callable
from functools import wraps
from fastapi import HTTPException, Depends, Request
from sqlalchemy.orm import Session

from sentrascan.core.models import User, APIKey
from sentrascan.core.storage import SessionLocal
from sentrascan.core.tenant_context import get_tenant_id, validate_tenant_access

# Lazy import to avoid circular dependency
def _get_session_user(request, db):
    """Lazy import of get_session_user to avoid circular dependency"""
    from sentrascan.server import get_session_user
    return get_session_user(request, db)

def _require_api_key(request, db):
    """Lazy import of require_api_key to avoid circular dependency"""
    from sentrascan.server import require_api_key
    return require_api_key(request, db)

# Role definitions
ROLES = {
    "super_admin": {
        "name": "Super Admin",
        "description": "Full platform access across all tenants",
        "permissions": [
            "tenant.create",
            "tenant.read",
            "tenant.update",
            "tenant.delete",
            "user.create",
            "user.read",
            "user.update",
            "user.delete",
            "scan.create",
            "scan.read",
            "scan.update",
            "scan.delete",
            "finding.read",
            "api_key.create",
            "api_key.read",
            "api_key.delete",
            "settings.read",
            "settings.update",
            "tenant_settings.update",
            "tenant_settings.view",
        ],
        "tenant_scope": "all"  # Can access all tenants
    },
    "tenant_admin": {
        "name": "Tenant Admin",
        "description": "Full access within own tenant",
        "permissions": [
            "user.create",
            "user.read",
            "user.update",
            "user.delete",
            "scan.create",
            "scan.read",
            "scan.update",
            "scan.delete",
            "finding.read",
            "api_key.create",
            "api_key.read",
            "api_key.delete",
            "settings.read",
            "settings.update",
            "tenant_settings.update",
            "tenant_settings.view",
        ],
        "tenant_scope": "own"  # Can only access own tenant
    },
    "viewer": {
        "name": "Viewer",
        "description": "Read-only access within own tenant",
        "permissions": [
            "scan.read",
            "finding.read",
            "api_key.read",
            "settings.read",
            "tenant_settings.view",
        ],
        "tenant_scope": "own"
    },
    "scanner": {
        "name": "Scanner",
        "description": "Can create and read scans within own tenant",
        "permissions": [
            "scan.create",
            "scan.read",
            "finding.read",
            "api_key.read",
            "settings.read",
            "tenant_settings.view",
        ],
        "tenant_scope": "own"
    }
}

# Permission mappings for common operations
PERMISSION_MAP = {
    "GET /api/v1/scans": "scan.read",
    "POST /api/v1/models/scans": "scan.create",
    "POST /api/v1/mcp/scans": "scan.create",
    "GET /api/v1/scans/{scan_id}": "scan.read",
    "GET /api/v1/findings": "finding.read",
    "GET /api/v1/users": "user.read",
    "POST /api/v1/users": "user.create",
    "PUT /api/v1/users/{user_id}": "user.update",
    "DELETE /api/v1/users/{user_id}": "user.delete",
    "GET /api/v1/tenants": "tenant.read",
    "POST /api/v1/tenants": "tenant.create",
    "PUT /api/v1/tenants/{tenant_id}": "tenant.update",
    "DELETE /api/v1/tenants/{tenant_id}": "tenant.delete",
    "GET /api/v1/api-keys": "api_key.read",
    "POST /api/v1/api-keys": "api_key.create",
    "DELETE /api/v1/api-keys/{key_id}": "api_key.delete",
}


def get_user_role(user_or_key) -> Optional[str]:
    """
    Get the role of a user or API key.
    
    Args:
        user_or_key: User or APIKey object.
    
    Returns:
        Role string or None.
    """
    if not user_or_key:
        return None
    
    if isinstance(user_or_key, User):
        return user_or_key.role
    elif isinstance(user_or_key, APIKey):
        return getattr(user_or_key, "role", None)
    elif hasattr(user_or_key, "role"):
        return user_or_key.role
    
    return None


def has_permission(role: Optional[str], permission: str) -> bool:
    """
    Check if a role has a specific permission.
    
    Args:
        role: Role name.
        permission: Permission string (e.g., "scan.create").
    
    Returns:
        True if role has permission, False otherwise.
    """
    if not role or role not in ROLES:
        return False
    
    role_perms = ROLES[role]["permissions"]
    
    # Super admin has all permissions
    if role == "super_admin":
        return True
    
    return permission in role_perms


def require_permission(permission: str):
    """
    Decorator to require a specific permission for an endpoint.
    
    Usage:
        @app.get("/api/v1/scans")
        @require_permission("scan.read")
        def list_scans(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from kwargs
            request = kwargs.get("request")
            if not request:
                # Try to find it in args
                for arg in args:
                    if hasattr(arg, "cookies"):
                        request = arg
                        break
            
            if not request:
                raise HTTPException(500, "Request object not found")
            
            # Get user from session or API key
            db = kwargs.get("db")
            if not db:
                db = SessionLocal()
                try:
                    user = _get_session_user(request, db)
                    if not user:
                        # Try API key
                        api_key = _require_api_key(request, db)
                        user = api_key
                finally:
                    db.close()
            else:
                user = _get_session_user(request, db)
                if not user:
                    # Try API key
                    try:
                        api_key = _require_api_key(request, db)
                        user = api_key
                    except:
                        pass
            
            if not user:
                raise HTTPException(401, "Authentication required")
            
            # Get role
            role = get_user_role(user)
            if not role:
                raise HTTPException(403, "No role assigned")
            
            # Check permission
            if not has_permission(role, permission):
                raise HTTPException(403, f"Permission denied: {permission} required")
            
            # Call original function
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(*allowed_roles: str):
    """
    Decorator to require one of the specified roles.
    
    Usage:
        @app.get("/api/v1/tenants")
        @require_role("super_admin")
        def list_tenants(...):
            ...
    """
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get request from kwargs
            request = kwargs.get("request")
            if not request:
                # Try to find it in args
                for arg in args:
                    if hasattr(arg, "cookies"):
                        request = arg
                        break
            
            if not request:
                raise HTTPException(500, "Request object not found")
            
            # Get user from session or API key
            db = kwargs.get("db")
            if not db:
                db = SessionLocal()
                try:
                    user = _get_session_user(request, db)
                    if not user:
                        # Try API key
                        api_key = _require_api_key(request, db)
                        user = api_key
                finally:
                    db.close()
            else:
                user = _get_session_user(request, db)
                if not user:
                    # Try API key
                    try:
                        api_key = _require_api_key(request, db)
                        user = api_key
                    except:
                        pass
            
            if not user:
                raise HTTPException(401, "Authentication required")
            
            # Get role
            role = get_user_role(user)
            if not role:
                raise HTTPException(403, "No role assigned")
            
            # Check if role is allowed
            if role not in allowed_roles:
                raise HTTPException(403, f"Role denied: {', '.join(allowed_roles)} required")
            
            # Call original function
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_role(user_or_key, *allowed_roles: str) -> bool:
    """
    Check if a user or API key has one of the allowed roles.
    
    Args:
        user_or_key: User or APIKey object.
        *allowed_roles: Allowed role names.
    
    Returns:
        True if user has one of the allowed roles, False otherwise.
    """
    role = get_user_role(user_or_key)
    if not role:
        return False
    return role in allowed_roles


def check_permission(user_or_key, permission: str) -> bool:
    """
    Check if a user or API key has a specific permission.
    
    Args:
        user_or_key: User or APIKey object.
        permission: Permission string.
    
    Returns:
        True if user has permission, False otherwise.
    """
    role = get_user_role(user_or_key)
    return has_permission(role, permission)


def get_role_permissions(role: str) -> List[str]:
    """
    Get all permissions for a role.
    
    Args:
        role: Role name.
    
    Returns:
        List of permission strings.
    """
    if role not in ROLES:
        return []
    return ROLES[role]["permissions"].copy()


def get_all_roles() -> dict:
    """
    Get all role definitions.
    
    Returns:
        Dictionary of role definitions.
    """
    return ROLES.copy()


def get_all_permissions() -> List[str]:
    """
    Get all unique permissions across all roles.
    
    Returns:
        List of all permission strings.
    """
    permissions = set()
    for role_def in ROLES.values():
        if "permissions" in role_def:
            permissions.update(role_def["permissions"])
    return sorted(list(permissions))


# Export PERMISSIONS as a constant for convenience
PERMISSIONS = get_all_permissions()


def can_access_tenant(user_or_key, tenant_id: str) -> bool:
    """
    Check if a user or API key can access a specific tenant.
    
    Args:
        user_or_key: User or APIKey object.
        tenant_id: Tenant ID to check access for.
    
    Returns:
        True if user can access tenant, False otherwise.
    """
    role = get_user_role(user_or_key)
    if not role:
        return False
    
    # Super admin can access all tenants
    if role == "super_admin":
        return True
    
    # Other roles can only access their own tenant
    user_tenant_id = None
    if isinstance(user_or_key, User):
        user_tenant_id = user_or_key.tenant_id
    elif isinstance(user_or_key, APIKey):
        user_tenant_id = getattr(user_or_key, "tenant_id", None)
    elif hasattr(user_or_key, "tenant_id"):
        user_tenant_id = user_or_key.tenant_id
    
    return user_tenant_id == tenant_id

