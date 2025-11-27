"""
Comprehensive audit logging for security-relevant events.

Provides functions to log all security-relevant events to the AuditLog table.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from sentrascan.core.models import AuditLog
from sentrascan.core.tenant_context import get_tenant_id
from sentrascan.core.logging import get_logger

logger = get_logger(__name__)


def log_security_event(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None
):
    """
    Log a security-relevant event to the audit log.
    
    Args:
        db: Database session.
        action: Action performed (e.g., "login", "logout", "password_change", "key_access").
        resource_type: Type of resource (e.g., "user", "api_key", "tenant", "scan").
        resource_id: ID of the resource affected.
        user_id: ID of the user performing the action.
        tenant_id: ID of the tenant (defaults to current tenant context).
        details: Additional details as dictionary.
        ip_address: IP address of the request.
    """
    try:
        if tenant_id is None:
            tenant_id = get_tenant_id()
        
        audit_log = AuditLog(
            tenant_id=tenant_id or "system",
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details or {},
            ip_address=ip_address,
            timestamp=datetime.utcnow()
        )
        
        db.add(audit_log)
        db.commit()
        
        logger.info(
            "audit_log_created",
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            tenant_id=tenant_id
        )
    except Exception as e:
        logger.error("audit_log_failed", error=str(e), action=action)
        db.rollback()


def log_authentication_event(
    db: Session,
    action: str,
    user_id: Optional[str] = None,
    success: bool = True,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Log authentication-related events."""
    log_security_event(
        db=db,
        action=action,
        resource_type="authentication",
        resource_id=user_id,
        user_id=user_id,
        details={"success": success, **(details or {})},
        ip_address=ip_address
    )


def log_authorization_event(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    success: bool = True,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Log authorization-related events."""
    log_security_event(
        db=db,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        details={"success": success, **(details or {})},
        ip_address=ip_address
    )


def log_data_access_event(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Log data access events."""
    log_security_event(
        db=db,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        details=details,
        ip_address=ip_address
    )


def log_configuration_change(
    db: Session,
    action: str,
    resource_type: str,
    resource_id: Optional[str] = None,
    user_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None
):
    """Log configuration change events."""
    log_security_event(
        db=db,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        user_id=user_id,
        details=details,
        ip_address=ip_address
    )

