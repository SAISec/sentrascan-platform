"""
Key management module for SentraScan Platform.

Manages encryption keys for tenant-specific data encryption at rest.
Keys are never stored in the database or application code.

This module provides a local key management implementation that can be
extended to integrate with external key management systems (HashiCorp Vault,
AWS KMS, Azure Key Vault) in the future.
"""

import os
import json
import hashlib
import secrets
import base64
from typing import Optional, Dict, List
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from sqlalchemy.orm import Session

from sentrascan.core.logging import get_logger
from sentrascan.core.models import AuditLog

logger = get_logger(__name__)

# Key management configuration
# Use local directory for development, /app/keys for production
_default_keys_dir = os.path.join(os.path.expanduser("~"), ".sentrascan", "keys") if os.path.exists(os.path.expanduser("~")) else "/app/keys"
KEYS_DIR = Path(os.environ.get("ENCRYPTION_KEYS_DIR", _default_keys_dir))
try:
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
except (OSError, PermissionError):
    # Fallback to current directory if can't create default
    KEYS_DIR = Path(os.path.join(os.getcwd(), ".keys"))
    KEYS_DIR.mkdir(parents=True, exist_ok=True)
KEYS_FILE = KEYS_DIR / "tenant_keys.json"
MASTER_KEY_ENV = "ENCRYPTION_MASTER_KEY"
KEY_ROTATION_INTERVAL_DAYS = int(os.environ.get("KEY_ROTATION_INTERVAL_DAYS", "90"))


class KeyManager:
    """
    Manages encryption keys for tenants.
    
    Keys are stored encrypted in a secure file (or can be extended to use
    external key management systems). Keys are never stored in plaintext
    in the database or application code.
    """
    
    def __init__(self):
        """Initialize key manager with master key."""
        self.master_key = self._get_master_key()
        self._keys_cache: Dict[str, Dict] = {}
        self._load_keys()
    
    def _get_master_key(self) -> bytes:
        """
        Get master key from environment variable.
        
        The master key is used to encrypt tenant-specific keys.
        In production, this should be provided via secure secrets management.
        
        Returns:
            Master key bytes.
        
        Raises:
            ValueError: If master key is not set.
        """
        master_key_str = os.environ.get(MASTER_KEY_ENV)
        if not master_key_str:
            raise ValueError(
                f"{MASTER_KEY_ENV} environment variable is required. "
                "This should be set via secure secrets management, never in code."
            )
        
        # Ensure key is at least 32 bytes (256 bits)
        master_key_bytes = master_key_str.encode() if isinstance(master_key_str, str) else master_key_str
        if len(master_key_bytes) < 32:
            raise ValueError(f"Master key must be at least 32 bytes (256 bits). Current length: {len(master_key_bytes)}")
        
        return master_key_bytes[:32]
    
    def _derive_key(self, salt: bytes, password: bytes) -> bytes:
        """
        Derive a key using PBKDF2.
        
        Args:
            salt: Salt bytes.
            password: Password bytes.
        
        Returns:
            Derived key bytes (32 bytes for Fernet).
        """
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        return kdf.derive(password)
    
    def _encrypt_key(self, plaintext_key: bytes) -> Dict[str, str]:
        """
        Encrypt a tenant key using the master key.
        
        Args:
            plaintext_key: Plaintext key bytes to encrypt.
        
        Returns:
            Dictionary with encrypted key data (salt, encrypted_key).
        """
        salt = secrets.token_bytes(16)
        derived_key = self._derive_key(salt, self.master_key)
        fernet = Fernet(base64.urlsafe_b64encode(derived_key))
        encrypted = fernet.encrypt(plaintext_key)
        
        return {
            "salt": base64.b64encode(salt).decode(),
            "encrypted_key": base64.b64encode(encrypted).decode()
        }
    
    def _decrypt_key(self, encrypted_data: Dict[str, str]) -> bytes:
        """
        Decrypt a tenant key using the master key.
        
        Args:
            encrypted_data: Dictionary with salt and encrypted_key.
        
        Returns:
            Decrypted key bytes.
        """
        import base64
        salt = base64.b64decode(encrypted_data["salt"].encode())
        encrypted = base64.b64decode(encrypted_data["encrypted_key"].encode())
        
        derived_key = self._derive_key(salt, self.master_key)
        fernet = Fernet(base64.urlsafe_b64encode(derived_key))
        return fernet.decrypt(encrypted)
    
    def _load_keys(self):
        """Load encrypted keys from secure storage."""
        if not KEYS_FILE.exists():
            logger.info("keys_file_not_found", path=str(KEYS_FILE), message="Creating new keys file")
            self._save_keys()
            return
        
        try:
            with open(KEYS_FILE, 'r') as f:
                data = json.load(f)
                self._keys_cache = data.get("keys", {})
            logger.debug("keys_loaded", tenant_count=len(self._keys_cache))
        except Exception as e:
            logger.error("keys_load_failed", error=str(e))
            self._keys_cache = {}
    
    def _save_keys(self):
        """Save encrypted keys to secure storage."""
        try:
            # Ensure directory exists and has proper permissions
            KEYS_DIR.mkdir(parents=True, exist_ok=True)
            KEYS_DIR.chmod(0o700)  # Only owner can read/write/execute
            
            data = {
                "keys": self._keys_cache,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            # Write to temporary file first, then rename (atomic operation)
            temp_file = KEYS_FILE.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            temp_file.chmod(0o600)  # Only owner can read/write
            temp_file.replace(KEYS_FILE)
            
            logger.debug("keys_saved", tenant_count=len(self._keys_cache))
        except Exception as e:
            logger.error("keys_save_failed", error=str(e))
            raise
    
    def get_tenant_key(self, tenant_id: str, create_if_missing: bool = True, user_id: Optional[str] = None, db: Optional[Session] = None) -> Optional[bytes]:
        """
        Get encryption key for a tenant.
        
        Args:
            tenant_id: Tenant ID.
            create_if_missing: If True, create a new key if not found.
            user_id: Optional user ID for audit logging.
            db: Optional database session for audit logging.
        
        Returns:
            Encryption key bytes, or None if not found and create_if_missing is False.
        """
        # Log key access for audit
        if db and user_id:
            try:
                audit = AuditLog(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    action="key_access",
                    resource_type="encryption_key",
                    resource_id=tenant_id,
                    details={"operation": "get_key"}
                )
                db.add(audit)
                db.commit()
            except Exception as e:
                logger.warning("audit_log_failed", error=str(e))
        
        if tenant_id in self._keys_cache:
            key_data = self._keys_cache[tenant_id]
            try:
                decrypted_key = self._decrypt_key(key_data["encrypted"])
                return decrypted_key
            except Exception as e:
                logger.error("key_decryption_failed", tenant_id=tenant_id, error=str(e))
                # If decryption fails, generate new key
                if create_if_missing:
                    return self.create_tenant_key(tenant_id, user_id=user_id, db=db)
                return None
        
        if create_if_missing:
            return self.create_tenant_key(tenant_id, user_id=user_id, db=db)
        
        return None
    
    def create_tenant_key(self, tenant_id: str, user_id: Optional[str] = None, db: Optional[Session] = None) -> bytes:
        """
        Create a new encryption key for a tenant.
        
        Args:
            tenant_id: Tenant ID.
        
        Returns:
            New encryption key bytes.
        """
        # Generate a new 32-byte key
        new_key = secrets.token_bytes(32)
        
        # Encrypt the key
        encrypted_data = self._encrypt_key(new_key)
        
        # Store in cache
        self._keys_cache[tenant_id] = {
            "encrypted": encrypted_data,
            "created_at": datetime.utcnow().isoformat(),
            "last_rotated": datetime.utcnow().isoformat(),
            "rotation_count": 0
        }
        
        # Save to file
        self._save_keys()
        
        # Log key creation for audit
        if db and user_id:
            try:
                audit = AuditLog(
                    tenant_id=tenant_id,
                    user_id=user_id,
                    action="key_created",
                    resource_type="encryption_key",
                    resource_id=tenant_id,
                    details={"operation": "create_key"}
                )
                db.add(audit)
                db.commit()
            except Exception as e:
                logger.warning("audit_log_failed", error=str(e))
        
        logger.info("tenant_key_created", tenant_id=tenant_id)
        return new_key
    
    def rotate_tenant_key(self, tenant_id: str) -> bytes:
        """
        Rotate encryption key for a tenant.
        
        This creates a new key while keeping the old key for decryption
        of existing data. The old key is marked as deprecated.
        
        Args:
            tenant_id: Tenant ID.
        
        Returns:
            New encryption key bytes.
        """
        # Get current key info
        if tenant_id not in self._keys_cache:
            # No existing key, create new one
            return self.create_tenant_key(tenant_id)
        
        key_info = self._keys_cache[tenant_id]
        
        # Store old key for decryption
        if "old_keys" not in key_info:
            key_info["old_keys"] = []
        
        key_info["old_keys"].append({
            "encrypted": key_info["encrypted"],
            "deprecated_at": datetime.utcnow().isoformat()
        })
        
        # Generate new key
        new_key = secrets.token_bytes(32)
        encrypted_data = self._encrypt_key(new_key)
        
        # Update key info
        key_info["encrypted"] = encrypted_data
        key_info["last_rotated"] = datetime.utcnow().isoformat()
        key_info["rotation_count"] = key_info.get("rotation_count", 0) + 1
        
        # Save
        self._save_keys()
        
        logger.info("tenant_key_rotated", tenant_id=tenant_id, rotation_count=key_info["rotation_count"])
        return new_key
    
    def get_old_keys(self, tenant_id: str) -> List[bytes]:
        """
        Get old (deprecated) keys for a tenant.
        
        These are used for decrypting data encrypted with previous keys.
        
        Args:
            tenant_id: Tenant ID.
        
        Returns:
            List of old key bytes.
        """
        if tenant_id not in self._keys_cache:
            return []
        
        key_info = self._keys_cache[tenant_id]
        old_keys = []
        
        if "old_keys" in key_info:
            for old_key_data in key_info["old_keys"]:
                try:
                    decrypted = self._decrypt_key(old_key_data["encrypted"])
                    old_keys.append(decrypted)
                except Exception as e:
                    logger.warning("old_key_decryption_failed", tenant_id=tenant_id, error=str(e))
        
        return old_keys
    
    def list_tenants_with_keys(self) -> List[str]:
        """
        List all tenant IDs that have encryption keys.
        
        Returns:
            List of tenant IDs.
        """
        return list(self._keys_cache.keys())
    
    def get_key_metadata(self, tenant_id: str) -> Optional[Dict]:
        """
        Get metadata about a tenant's encryption key.
        
        Args:
            tenant_id: Tenant ID.
        
        Returns:
            Dictionary with key metadata, or None if not found.
        """
        if tenant_id not in self._keys_cache:
            return None
        
        key_info = self._keys_cache[tenant_id].copy()
        # Remove encrypted key from metadata
        key_info.pop("encrypted", None)
        if "old_keys" in key_info:
            # Just count old keys, don't include encrypted data
            key_info["old_keys_count"] = len(key_info["old_keys"])
            key_info.pop("old_keys", None)
        
        return key_info
    
    def check_key_rotation_needed(self, tenant_id: str) -> bool:
        """
        Check if key rotation is needed for a tenant.
        
        Args:
            tenant_id: Tenant ID.
        
        Returns:
            True if rotation is needed, False otherwise.
        """
        if tenant_id not in self._keys_cache:
            return False
        
        key_info = self._keys_cache[tenant_id]
        last_rotated_str = key_info.get("last_rotated")
        if not last_rotated_str:
            return False
        
        last_rotated = datetime.fromisoformat(last_rotated_str)
        rotation_due = last_rotated + timedelta(days=KEY_ROTATION_INTERVAL_DAYS)
        
        return datetime.utcnow() >= rotation_due
    
    def cleanup_old_keys(self, tenant_id: str, keep_count: int = 2):
        """
        Clean up old keys, keeping only the most recent ones.
        
        Args:
            tenant_id: Tenant ID.
            keep_count: Number of old keys to keep.
        """
        if tenant_id not in self._keys_cache:
            return
        
        key_info = self._keys_cache[tenant_id]
        if "old_keys" not in key_info:
            return
        
        old_keys = key_info["old_keys"]
        if len(old_keys) > keep_count:
            # Keep only the most recent old keys
            key_info["old_keys"] = old_keys[-keep_count:]
            self._save_keys()
            logger.info("old_keys_cleaned", tenant_id=tenant_id, kept=keep_count, removed=len(old_keys) - keep_count)


# Global key manager instance
_key_manager: Optional[KeyManager] = None


def get_key_manager() -> KeyManager:
    """
    Get the global key manager instance.
    
    Returns:
        KeyManager instance.
    """
    global _key_manager
    if _key_manager is None:
        _key_manager = KeyManager()
    return _key_manager


def reset_key_manager():
    """
    Reset the global key manager instance.
    
    This is primarily for testing purposes to allow reinitialization
    with different environment variables.
    """
    global _key_manager
    _key_manager = None


def get_tenant_encryption_key(tenant_id: str) -> bytes:
    """
    Get encryption key for a tenant.
    
    Args:
        tenant_id: Tenant ID.
    
    Returns:
        Encryption key bytes.
    """
    return get_key_manager().get_tenant_key(tenant_id)


def rotate_tenant_key(tenant_id: str) -> bytes:
    """
    Rotate encryption key for a tenant.
    
    Args:
        tenant_id: Tenant ID.
    
    Returns:
        New encryption key bytes.
    """
    return get_key_manager().rotate_tenant_key(tenant_id)

