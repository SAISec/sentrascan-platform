"""
User authentication module for SentraScan Platform.

Provides email/password authentication with secure password policies,
password hashing, and account lockout functionality.
"""

import re
import time
from typing import Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException

try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False
    try:
        from argon2 import PasswordHasher
        HAS_ARGON2 = True
    except ImportError:
        HAS_ARGON2 = False

from sentrascan.core.models import User
from sentrascan.core.logging import get_logger

try:
    import pyotp
    import qrcode
    import io
    import base64
    HAS_MFA = True
except ImportError:
    HAS_MFA = False

logger = get_logger(__name__)

# Account lockout configuration
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION_MINUTES = 30

# Password policy configuration
MIN_PASSWORD_LENGTH = 12
REQUIRE_UPPERCASE = True
REQUIRE_LOWERCASE = True
REQUIRE_DIGITS = True
REQUIRE_SPECIAL = True

# Password expiration configuration
PASSWORD_EXPIRATION_DAYS = 90  # Passwords expire after 90 days
PASSWORD_MIN_AGE_DAYS = 1  # Minimum 1 day before password can be changed


class PasswordHasher:
    """
    Password hashing utility using bcrypt (preferred) or Argon2.
    """
    
    def __init__(self):
        if HAS_BCRYPT:
            self.hasher_type = "bcrypt"
            self.bcrypt_rounds = 12
        elif HAS_ARGON2:
            self.hasher_type = "argon2"
            self.argon2_hasher = Argon2PasswordHasher()
        else:
            raise RuntimeError("Neither bcrypt nor argon2 is available. Install one: pip install bcrypt or pip install argon2-cffi")
    
    def hash_password(self, password: str) -> str:
        """
        Hash a password.
        
        Args:
            password: Plaintext password.
        
        Returns:
            Hashed password string.
        """
        if self.hasher_type == "bcrypt":
            salt = bcrypt.gensalt(rounds=self.bcrypt_rounds)
            hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
            return hashed.decode('utf-8')
        else:  # argon2
            return self.argon2_hasher.hash(password)
    
    def verify_password(self, password: str, password_hash: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            password: Plaintext password to verify.
            password_hash: Hashed password to verify against.
        
        Returns:
            True if password matches, False otherwise.
        """
        try:
            if self.hasher_type == "bcrypt":
                return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
            else:  # argon2
                try:
                    self.argon2_hasher.verify(password_hash, password)
                    return True
                except Exception:
                    return False
        except Exception:
            return False


class PasswordPolicy:
    """
    Password policy validator.
    """
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password against security policy.
        
        Policy requirements:
        - Minimum 12 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        
        Args:
            password: Password to validate.
        
        Returns:
            Tuple of (is_valid, error_message).
        """
        if len(password) < MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {MIN_PASSWORD_LENGTH} characters long"
        
        if REQUIRE_UPPERCASE and not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if REQUIRE_LOWERCASE and not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if REQUIRE_DIGITS and not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if REQUIRE_SPECIAL and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, None


class AccountLockout:
    """
    Account lockout management.
    """
    
    # In-memory lockout tracking (in production, use Redis or database)
    _lockouts: dict[str, dict] = {}
    
    @classmethod
    def record_failed_attempt(cls, email: str):
        """
        Record a failed login attempt.
        
        Args:
            email: User email address.
        """
        if email not in cls._lockouts:
            cls._lockouts[email] = {
                "attempts": 0,
                "locked_until": None
            }
        
        cls._lockouts[email]["attempts"] += 1
        
        if cls._lockouts[email]["attempts"] >= MAX_LOGIN_ATTEMPTS:
            lockout_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
            cls._lockouts[email]["locked_until"] = lockout_until
            logger.warning(
                "account_locked",
                email=email,
                attempts=cls._lockouts[email]["attempts"],
                locked_until=lockout_until.isoformat()
            )
    
    @classmethod
    def clear_failed_attempts(cls, email: str):
        """
        Clear failed login attempts (on successful login).
        
        Args:
            email: User email address.
        """
        if email in cls._lockouts:
            cls._lockouts[email]["attempts"] = 0
            cls._lockouts[email]["locked_until"] = None
    
    @classmethod
    def is_locked(cls, email: str) -> Tuple[bool, Optional[str]]:
        """
        Check if an account is locked.
        
        Args:
            email: User email address.
        
        Returns:
            Tuple of (is_locked, lockout_message).
        """
        if email not in cls._lockouts:
            return False, None
        
        lockout_info = cls._lockouts[email]
        
        # Check if lockout has expired
        if lockout_info["locked_until"]:
            if datetime.utcnow() < lockout_info["locked_until"]:
                remaining = (lockout_info["locked_until"] - datetime.utcnow()).total_seconds() / 60
                return True, f"Account locked due to too many failed login attempts. Try again in {int(remaining)} minutes."
            else:
                # Lockout expired, clear it
                cls._lockouts[email]["attempts"] = 0
                cls._lockouts[email]["locked_until"] = None
        
        # Check if attempts exceed threshold
        if lockout_info["attempts"] >= MAX_LOGIN_ATTEMPTS:
            if not lockout_info["locked_until"]:
                # Lock it now
                lockout_until = datetime.utcnow() + timedelta(minutes=LOCKOUT_DURATION_MINUTES)
                lockout_info["locked_until"] = lockout_until
                return True, f"Account locked due to too many failed login attempts. Try again in {LOCKOUT_DURATION_MINUTES} minutes."
        
        return False, None


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password.
    
    Args:
        db: Database session.
        email: User email address.
        password: Plaintext password.
    
    Returns:
        User object if authentication succeeds, None otherwise.
    """
    # Check if account is locked
    is_locked, lockout_msg = AccountLockout.is_locked(email)
    if is_locked:
        raise HTTPException(status_code=423, detail=lockout_msg)
    
    # Find user by email
    user = db.query(User).filter(User.email == email.lower()).first()
    if not user:
        AccountLockout.record_failed_attempt(email)
        logger.warning("login_failed", reason="user_not_found", email=email)
        return None
    
    # Check if user is active
    if not user.is_active:
        AccountLockout.record_failed_attempt(email)
        logger.warning("login_failed", reason="account_inactive", email=email, user_id=user.id)
        raise HTTPException(status_code=403, detail="Account is deactivated")
    
    # Verify password
    hasher = PasswordHasher()
    if not hasher.verify_password(password, user.password_hash):
        AccountLockout.record_failed_attempt(email)
        logger.warning("login_failed", reason="invalid_password", email=email, user_id=user.id)
        return None
    
    # Successful authentication - clear failed attempts
    AccountLockout.clear_failed_attempts(email)
    logger.info("login_success", email=email, user_id=user.id, tenant_id=user.tenant_id)
    
    return user


def create_user(
    db: Session,
    email: str,
    password: str,
    name: str,
    tenant_id: str,
    role: str = "viewer"
) -> User:
    """
    Create a new user with hashed password.
    
    Args:
        db: Database session.
        email: User email address.
        password: Plaintext password (will be hashed).
        name: User's full name.
        tenant_id: Tenant ID to associate user with.
        role: User role (default: "viewer").
    
    Returns:
        Created User object.
    
    Raises:
        HTTPException: If validation fails or user already exists.
    """
    # Validate password
    is_valid, error_msg = PasswordPolicy.validate_password(password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Check if user already exists
    existing = db.query(User).filter(User.email == email.lower()).first()
    if existing:
        raise HTTPException(status_code=409, detail="User with this email already exists")
    
    # Hash password
    hasher = PasswordHasher()
    password_hash = hasher.hash_password(password)
    
    # Create user
    user = User(
        email=email.lower(),
        password_hash=password_hash,
        name=name,
        tenant_id=tenant_id,
        role=role,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    logger.info("user_created", email=email, user_id=user.id, tenant_id=tenant_id, role=role)
    
    return user


def update_user_password(db: Session, user: User, new_password: str, check_min_age: bool = True) -> User:
    """
    Update a user's password.
    Invalidates all existing sessions for security.
    
    Args:
        db: Database session.
        user: User object.
        new_password: New plaintext password (will be hashed).
        check_min_age: If True, check minimum password age before allowing change.
    
    Returns:
        Updated User object.
    
    Raises:
        HTTPException: If password validation fails or minimum age not met.
    """
    # Check minimum age if required
    if check_min_age and not check_password_min_age(user):
        raise HTTPException(400, f"Password cannot be changed yet. Minimum age is {PASSWORD_MIN_AGE_DAYS} days.")
    
    # Validate password
    is_valid, error_msg = PasswordPolicy.validate_password(new_password)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)
    
    # Hash new password
    hasher = PasswordHasher()
    user.password_hash = hasher.hash_password(new_password)
    user.password_changed_at = datetime.utcnow()  # Track password change
    
    db.commit()
    db.refresh(user)
    
    # Invalidate all sessions for this user (security: force re-login after password change)
    from sentrascan.core.session import invalidate_user_sessions
    invalidated_count = invalidate_user_sessions(user.id)
    
    logger.info(
        "password_updated",
        user_id=user.id,
        email=user.email,
        sessions_invalidated=invalidated_count
    )
    
    return user


def deactivate_user(db: Session, user: User) -> User:
    """
    Deactivate a user account (soft delete).
    
    Args:
        db: Database session.
        user: User object to deactivate.
    
    Returns:
        Updated User object.
    """
    user.is_active = False
    db.commit()
    db.refresh(user)
    
    logger.info("user_deactivated", user_id=user.id, email=user.email)
    
    return user


def activate_user(db: Session, user: User) -> User:
    """
    Activate a user account.
    
    Args:
        db: Database session.
        user: User object to activate.
    
    Returns:
        Updated User object.
    """
    user.is_active = True
    db.commit()
    db.refresh(user)
    
    logger.info("user_activated", user_id=user.id, email=user.email)
    
    return user


def check_password_expiration(user: User) -> Tuple[bool, Optional[str]]:
    """
    Check if a user's password has expired.
    
    Args:
        user: User object.
    
    Returns:
        Tuple of (is_expired, expiration_message).
        If password has expired, returns (True, message).
        If password hasn't expired, returns (False, None).
    """
    if not user.password_changed_at:
        # If password was never changed, consider it expired
        return True, "Password has never been changed. Please set a new password."
    
    expiration_date = user.password_changed_at + timedelta(days=PASSWORD_EXPIRATION_DAYS)
    if datetime.utcnow() > expiration_date:
        days_expired = (datetime.utcnow() - expiration_date).days
        return True, f"Password expired {days_expired} days ago. Please change your password."
    
    return False, None


def check_password_min_age(user: User) -> bool:
    """
    Check if a user's password meets the minimum age requirement.
    
    Args:
        user: User object.
    
    Returns:
        True if password can be changed (meets minimum age), False otherwise.
    """
    if not user.password_changed_at:
        # If password was never changed, allow change
        return True
    
    min_age_date = user.password_changed_at + timedelta(days=PASSWORD_MIN_AGE_DAYS)
    return datetime.utcnow() >= min_age_date

