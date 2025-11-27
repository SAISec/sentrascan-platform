"""
Tenant context middleware for multi-tenancy support.

Extracts tenant_id from authenticated user, API key, or session cookie
and makes it available throughout the request lifecycle.
"""

from typing import Optional
from contextvars import ContextVar
from fastapi import Request, HTTPException
from sqlalchemy.orm import Session

# Context variable to store tenant_id for the current request
tenant_context: ContextVar[Optional[str]] = ContextVar('tenant_id', default=None)


def get_tenant_id() -> Optional[str]:
    """
    Get the current tenant_id from context.
    
    Returns:
        Tenant ID if set, None otherwise.
    """
    return tenant_context.get()


def set_tenant_id(tenant_id: str):
    """
    Set the tenant_id in the current context.
    
    Args:
        tenant_id: The tenant ID to set.
    """
    tenant_context.set(tenant_id)


def extract_tenant_from_request(request: Request, db: Session) -> Optional[str]:
    """
    Extract tenant_id from request using multiple strategies:
    1. Authenticated user's tenant_id field
    2. API key's associated tenant_id
    3. Session cookie's tenant context
    
    Args:
        request: FastAPI request object.
        db: Database session.
    
    Returns:
        Tenant ID if found, None otherwise.
    """
    from sentrascan.core.models import User, APIKey
    from sentrascan.server import get_session_user, SESSION_COOKIE
    
    # Strategy 1: Get from authenticated user (if using email/password auth)
    # Check if there's a user in the request state (set by auth middleware)
    if hasattr(request.state, 'user') and request.state.user:
        user = request.state.user
        if hasattr(user, 'tenant_id') and user.tenant_id:
            return user.tenant_id
    
    # Strategy 2: Get from API key
    # Check X-API-Key header
    api_key_header = request.headers.get("X-API-Key") or request.headers.get("x-api-key")
    if api_key_header:
        api_key_hash = APIKey.hash_key(api_key_header)
        api_key = db.query(APIKey).filter(
            APIKey.key_hash == api_key_hash,
            APIKey.is_revoked == False
        ).first()
        if api_key:
            # If API key has user_id, get tenant from user
            if api_key.user_id:
                user = db.query(User).filter(User.id == api_key.user_id, User.is_active == True).first()
                if user and user.tenant_id:
                    return user.tenant_id
            # Otherwise, use API key's tenant_id
            if hasattr(api_key, 'tenant_id') and api_key.tenant_id:
                return api_key.tenant_id
    
    # Strategy 3: Get from session cookie (existing session auth)
    session_user = get_session_user(request, db)
    if session_user:
        # If session_user is an APIKey, get its tenant_id
        if isinstance(session_user, APIKey) and hasattr(session_user, 'tenant_id'):
            if session_user.tenant_id:
                return session_user.tenant_id
        # If session_user is a User, get its tenant_id
        elif isinstance(session_user, User) and hasattr(session_user, 'tenant_id'):
            if session_user.tenant_id:
                return session_user.tenant_id
    
    # Strategy 4: Check for tenant_id in request headers (for admin operations)
    tenant_header = request.headers.get("X-Tenant-ID") or request.headers.get("x-tenant-id")
    if tenant_header:
        # Validate that tenant exists
        from sentrascan.core.models import Tenant
        tenant = db.query(Tenant).filter(Tenant.id == tenant_header, Tenant.is_active == True).first()
        if tenant:
            return tenant.id
    
    return None


def require_tenant(request: Request, db: Session) -> str:
    """
    Require a tenant_id to be present in the request.
    Raises HTTPException if no tenant_id can be extracted.
    
    Args:
        request: FastAPI request object.
        db: Database session.
    
    Returns:
        Tenant ID.
    
    Raises:
        HTTPException: If no tenant_id can be extracted.
    """
    tenant_id = extract_tenant_from_request(request, db)
    if not tenant_id:
        raise HTTPException(
            status_code=403,
            detail="Tenant context required. Please authenticate with a tenant-scoped API key or user account."
        )
    return tenant_id


def validate_tenant_access(tenant_id: str, user_tenant_id: Optional[str], user_role: Optional[str] = None) -> bool:
    """
    Validate that a user has access to a tenant.
    
    Rules:
    - Super admins can access any tenant
    - Tenant admins can only access their own tenant
    - Viewers and scanners can only access their own tenant
    
    Args:
        tenant_id: The tenant ID being accessed.
        user_tenant_id: The tenant ID of the authenticated user.
        user_role: The role of the authenticated user.
    
    Returns:
        True if access is allowed, False otherwise.
    """
    # Super admins can access any tenant
    if user_role == "super_admin":
        return True
    
    # Other roles can only access their own tenant
    if user_tenant_id and tenant_id == user_tenant_id:
        return True
    
    return False


class TenantContextMiddleware:
    """
    Middleware to extract and set tenant context for each request.
    """
    
    async def __call__(self, request: Request, call_next):
        """
        Extract tenant_id from request and set it in context.
        """
        from sentrascan.core.storage import SessionLocal
        
        db = SessionLocal()
        try:
            # Extract tenant_id from request
            tenant_id = extract_tenant_from_request(request, db)
            
            # Set tenant_id in context
            if tenant_id:
                set_tenant_id(tenant_id)
                # Also store in request state for easy access
                request.state.tenant_id = tenant_id
            
            # Continue with request
            response = await call_next(request)
            return response
        finally:
            db.close()

