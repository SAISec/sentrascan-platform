"""
Session management module for SentraScan Platform.

Provides session creation, validation, refresh, and invalidation with
configurable timeout and automatic refresh on activity.
"""

import os
import time
import hmac
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from sentrascan.core.models import User, APIKey
from sentrascan.core.logging import get_logger

logger = get_logger(__name__)

# Session configuration
SESSION_COOKIE_NAME = os.environ.get("SENTRASCAN_SESSION_COOKIE", "ss_session")
SESSION_SECRET = os.environ.get("SENTRASCAN_SECRET", "dev-secret-change-me")
SESSION_TIMEOUT_HOURS = int(os.environ.get("SESSION_TIMEOUT_HOURS", "48"))
SESSION_REFRESH_THRESHOLD = 0.8  # Refresh if less than 80% of time remaining

# In-memory session store (in production, use Redis or database)
# Format: {session_id: {"user_id": str, "tenant_id": str, "created_at": datetime, "last_activity": datetime, "expires_at": datetime}}
_sessions: Dict[str, Dict[str, Any]] = {}


def sign(value: str) -> str:
    """
    Sign a value with HMAC-SHA256.
    
    Args:
        value: Value to sign.
    
    Returns:
        Signed value in format: value.hmac
    """
    mac = hmac.new(SESSION_SECRET.encode(), msg=value.encode(), digestmod=hashlib.sha256).hexdigest()
    return f"{value}.{mac}"


def unsign(signed_value: str) -> Optional[str]:
    """
    Verify and extract value from signed string.
    
    Args:
        signed_value: Signed value in format: value.hmac
    
    Returns:
        Original value if valid, None otherwise.
    """
    try:
        if "." not in signed_value:
            return None
        value, mac = signed_value.rsplit(".", 1)
        expected_mac = hmac.new(SESSION_SECRET.encode(), msg=value.encode(), digestmod=hashlib.sha256).hexdigest()
        if not hmac.compare_digest(mac, expected_mac):
            return None
        return value
    except Exception:
        return None


def create_session(user: User, db: Session) -> str:
    """
    Create a new session for a user.
    
    Args:
        user: User object.
        db: Database session.
    
    Returns:
        Session ID (signed).
    """
    # Generate session ID
    import secrets
    session_id = f"session_{user.id}_{secrets.token_urlsafe(32)}"
    
    # Calculate expiration
    expires_at = datetime.utcnow() + timedelta(hours=SESSION_TIMEOUT_HOURS)
    
    # Store session
    _sessions[session_id] = {
        "user_id": user.id,
        "tenant_id": user.tenant_id,
        "role": user.role,
        "created_at": datetime.utcnow(),
        "last_activity": datetime.utcnow(),
        "expires_at": expires_at
    }
    
    logger.info(
        "session_created",
        user_id=user.id,
        tenant_id=user.tenant_id,
        expires_at=expires_at.isoformat()
    )
    
    # Return signed session ID
    return sign(session_id)


def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get session data by session ID.
    
    Args:
        session_id: Session ID (signed or unsigned).
    
    Returns:
        Session data dictionary or None if not found/invalid.
    """
    # If signed, unsign it
    if "." in session_id:
        unsigned_id = unsign(session_id)
        if not unsigned_id:
            return None
        session_id = unsigned_id
    
    # Check if session exists
    if session_id not in _sessions:
        return None
    
    session_data = _sessions[session_id]
    
    # Check if session is expired
    if datetime.utcnow() > session_data["expires_at"]:
        # Remove expired session
        del _sessions[session_id]
        logger.debug("session_expired", session_id=session_id[:20])
        return None
    
    return session_data


def refresh_session(session_id: str) -> bool:
    """
    Refresh a session by updating last_activity and extending expiration if needed.
    
    Args:
        session_id: Session ID (signed or unsigned).
    
    Returns:
        True if session was refreshed, False otherwise.
    """
    session_data = get_session(session_id)
    if not session_data:
        return False
    
    # Update last activity
    session_data["last_activity"] = datetime.utcnow()
    
    # Check if we should extend expiration (if less than threshold remaining)
    time_remaining = (session_data["expires_at"] - datetime.utcnow()).total_seconds()
    total_duration = (session_data["expires_at"] - session_data["created_at"]).total_seconds()
    
    if total_duration > 0 and (time_remaining / total_duration) < SESSION_REFRESH_THRESHOLD:
        # Extend expiration
        new_expires_at = datetime.utcnow() + timedelta(hours=SESSION_TIMEOUT_HOURS)
        session_data["expires_at"] = new_expires_at
        logger.debug(
            "session_extended",
            session_id=session_id[:20],
            new_expires_at=new_expires_at.isoformat()
        )
    
    return True


def invalidate_session(session_id: str) -> bool:
    """
    Invalidate a session (logout).
    
    Args:
        session_id: Session ID (signed or unsigned).
    
    Returns:
        True if session was invalidated, False if not found.
    """
    # If signed, unsign it
    if "." in session_id:
        unsigned_id = unsign(session_id)
        if not unsigned_id:
            return False
        session_id = unsigned_id
    
    if session_id in _sessions:
        user_id = _sessions[session_id].get("user_id")
        del _sessions[session_id]
        logger.info("session_invalidated", session_id=session_id[:20], user_id=user_id)
        return True
    
    return False


def invalidate_user_sessions(user_id: str) -> int:
    """
    Invalidate all sessions for a user (e.g., on password change).
    
    Args:
        user_id: User ID.
    
    Returns:
        Number of sessions invalidated.
    """
    count = 0
    sessions_to_remove = []
    
    for session_id, session_data in _sessions.items():
        if session_data.get("user_id") == user_id:
            sessions_to_remove.append(session_id)
    
    for session_id in sessions_to_remove:
        del _sessions[session_id]
        count += 1
    
    if count > 0:
        logger.info("user_sessions_invalidated", user_id=user_id, count=count)
    
    return count


def cleanup_expired_sessions():
    """
    Clean up expired sessions from memory.
    Should be called periodically (e.g., via background task).
    """
    now = datetime.utcnow()
    expired = []
    
    for session_id, session_data in _sessions.items():
        if now > session_data["expires_at"]:
            expired.append(session_id)
    
    for session_id in expired:
        del _sessions[session_id]
    
    if expired:
        logger.debug("expired_sessions_cleaned", count=len(expired))
    
    return len(expired)


def get_session_user(session_id: str, db: Session) -> Optional[User]:
    """
    Get User object from session ID.
    
    Args:
        session_id: Session ID (signed or unsigned).
        db: Database session.
    
    Returns:
        User object or None if session invalid/expired.
    """
    session_data = get_session(session_id)
    if not session_data:
        return None
    
    user_id = session_data.get("user_id")
    if not user_id:
        return None
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user:
        # User was deactivated, invalidate session
        invalidate_session(session_id)
        return None
    
    # Refresh session on activity
    refresh_session(session_id)
    
    return user


def get_session_info(session_id: str) -> Optional[Dict[str, Any]]:
    """
    Get session information without database lookup.
    
    Args:
        session_id: Session ID (signed or unsigned).
    
    Returns:
        Session info dictionary or None.
    """
    session_data = get_session(session_id)
    if not session_data:
        return None
    
    # Return copy without internal fields
    return {
        "user_id": session_data.get("user_id"),
        "tenant_id": session_data.get("tenant_id"),
        "role": session_data.get("role"),
        "created_at": session_data.get("created_at").isoformat() if session_data.get("created_at") else None,
        "last_activity": session_data.get("last_activity").isoformat() if session_data.get("last_activity") else None,
        "expires_at": session_data.get("expires_at").isoformat() if session_data.get("expires_at") else None
    }

