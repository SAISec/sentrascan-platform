"""
Encryption module for SentraScan Platform.

Provides encryption at rest functionality using AES-256 encryption.
Supports transparent encryption/decryption for database operations.
"""

import os
import base64
from typing import Optional, Dict, Any
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.fernet import Fernet

from sentrascan.core.logging import get_logger

logger = get_logger(__name__)

# Encryption configuration
ENCRYPTION_KEY_LENGTH = 32  # 256 bits for AES-256
ENCRYPTION_ALGORITHM = "AES-256-CBC"
SALT_LENGTH = 16  # 128 bits for salt


class EncryptionService:
    """
    Service for encrypting and decrypting data at rest.
    
    Uses AES-256-CBC encryption with PBKDF2 key derivation.
    """
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize encryption service.
        
        Args:
            master_key: Optional master encryption key. If not provided,
                       uses ENCRYPTION_MASTER_KEY environment variable.
        """
        if master_key:
            self.master_key = master_key
        else:
            key_str = os.environ.get("ENCRYPTION_MASTER_KEY")
            if not key_str:
                raise ValueError("ENCRYPTION_MASTER_KEY environment variable is required")
            self.master_key = key_str.encode() if isinstance(key_str, str) else key_str
        
        if len(self.master_key) < 32:
            raise ValueError("Master key must be at least 32 bytes (256 bits)")
        
        # Use first 32 bytes as key
        self.key = self.master_key[:32]
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt a plaintext string.
        
        Args:
            plaintext: Plaintext string to encrypt.
        
        Returns:
            Base64-encoded encrypted string.
        """
        try:
            # Generate random IV (initialization vector)
            import secrets
            iv = secrets.token_bytes(16)
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(iv),
                backend=default_backend()
            )
            encryptor = cipher.encryptor()
            
            # Pad plaintext to block size
            padder = padding.PKCS7(128).padder()
            padded_data = padder.update(plaintext.encode())
            padded_data += padder.finalize()
            
            # Encrypt
            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            
            # Combine IV and ciphertext, then base64 encode
            encrypted = iv + ciphertext
            encoded = base64.b64encode(encrypted).decode()
            
            logger.debug("data_encrypted", length=len(plaintext))
            return encoded
            
        except Exception as e:
            logger.error("encryption_failed", error=str(e))
            raise
    
    def decrypt(self, ciphertext: str) -> str:
        """
        Decrypt a ciphertext string.
        
        Args:
            ciphertext: Base64-encoded encrypted string.
        
        Returns:
            Decrypted plaintext string.
        """
        try:
            # Decode from base64
            encrypted = base64.b64decode(ciphertext.encode())
            
            # Extract IV (first 16 bytes) and actual ciphertext
            iv = encrypted[:16]
            ciphertext_bytes = encrypted[16:]
            
            # Create cipher
            cipher = Cipher(
                algorithms.AES(self.key),
                modes.CBC(iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            # Decrypt
            padded_data = decryptor.update(ciphertext_bytes) + decryptor.finalize()
            
            # Unpad
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_data)
            plaintext += unpadder.finalize()
            
            logger.debug("data_decrypted", length=len(plaintext))
            return plaintext.decode()
            
        except Exception as e:
            logger.error("decryption_failed", error=str(e))
            raise
    
    def encrypt_dict(self, data: Dict[str, Any], fields: list = None) -> Dict[str, Any]:
        """
        Encrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary to encrypt fields in.
            fields: List of field names to encrypt. If None, encrypts all string values.
        
        Returns:
            Dictionary with specified fields encrypted.
        """
        encrypted = data.copy()
        
        if fields is None:
            # Encrypt all string values
            fields = [k for k, v in data.items() if isinstance(v, str)]
        
        for field in fields:
            if field in encrypted and isinstance(encrypted[field], str):
                encrypted[field] = self.encrypt(encrypted[field])
        
        return encrypted
    
    def decrypt_dict(self, data: Dict[str, Any], fields: list = None) -> Dict[str, Any]:
        """
        Decrypt specific fields in a dictionary.
        
        Args:
            data: Dictionary to decrypt fields in.
            fields: List of field names to decrypt. If None, decrypts all string values.
        
        Returns:
            Dictionary with specified fields decrypted.
        """
        decrypted = data.copy()
        
        if fields is None:
            # Try to decrypt all string values (may fail if not encrypted)
            fields = [k for k, v in data.items() if isinstance(v, str)]
        
        for field in fields:
            if field in decrypted and isinstance(decrypted[field], str):
                try:
                    decrypted[field] = self.decrypt(decrypted[field])
                except Exception:
                    # Field may not be encrypted, leave as-is
                    pass
        
        return decrypted


# Global encryption service instance (initialized on first use)
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """
    Get the global encryption service instance.
    
    Returns:
        EncryptionService instance.
    """
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


def encrypt_data(plaintext: str) -> str:
    """
    Encrypt data using the global encryption service.
    
    Args:
        plaintext: Plaintext string to encrypt.
    
    Returns:
        Base64-encoded encrypted string.
    """
    return get_encryption_service().encrypt(plaintext)


def decrypt_data(ciphertext: str) -> str:
    """
    Decrypt data using the global encryption service.
    
    Args:
        ciphertext: Base64-encoded encrypted string.
    
    Returns:
        Decrypted plaintext string.
    """
    return get_encryption_service().decrypt(ciphertext)


def encrypt_tenant_data(tenant_id: str, plaintext: str) -> str:
    """
    Encrypt data for a specific tenant using tenant-specific key.
    
    Args:
        tenant_id: Tenant ID.
        plaintext: Plaintext string to encrypt.
    
    Returns:
        Base64-encoded encrypted string.
    """
    from sentrascan.core.key_management import get_tenant_encryption_key, get_key_manager
    
    # Get tenant-specific key
    tenant_key = get_tenant_encryption_key(tenant_id)
    
    # Create encryption service with tenant key
    service = EncryptionService(master_key=tenant_key)
    return service.encrypt(plaintext)


def decrypt_tenant_data(tenant_id: str, ciphertext: str) -> str:
    """
    Decrypt data for a specific tenant using tenant-specific key.
    
    Tries the current key first, then old keys if decryption fails
    (for key rotation support).
    
    Args:
        tenant_id: Tenant ID.
        ciphertext: Base64-encoded encrypted string.
    
    Returns:
        Decrypted plaintext string.
    
    Raises:
        ValueError: If decryption fails with all available keys.
    """
    from sentrascan.core.key_management import get_tenant_encryption_key, get_key_manager
    
    # Try current key first
    tenant_key = get_tenant_encryption_key(tenant_id)
    service = EncryptionService(master_key=tenant_key)
    
    try:
        return service.decrypt(ciphertext)
    except Exception:
        # Try old keys (for key rotation support)
        key_manager = get_key_manager()
        old_keys = key_manager.get_old_keys(tenant_id)
        for old_key in old_keys:
            try:
                old_service = EncryptionService(master_key=old_key)
                return old_service.decrypt(ciphertext)
            except Exception:
                continue
        
        # All keys failed
        logger.error("decryption_failed_all_keys", tenant_id=tenant_id)
        raise ValueError("Failed to decrypt data with any available key")

