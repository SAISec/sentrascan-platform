"""
Transparent encryption/decryption for database operations.

Provides SQLAlchemy event listeners that automatically encrypt data before
saving to the database and decrypt data when loading from the database.
"""

from typing import Any
from sqlalchemy import event
from sqlalchemy.orm import Session, Mapper
from sqlalchemy.orm.attributes import InstrumentedAttribute

from sentrascan.core.encryption import encrypt_tenant_data, decrypt_tenant_data
from sentrascan.core.tenant_context import get_tenant_id
from sentrascan.core.logging import get_logger

logger = get_logger(__name__)

# Fields that should be encrypted at rest
ENCRYPTED_FIELDS = {
    # Add model classes and their encrypted fields here
    # Example: "User": ["email", "name"],  # Don't encrypt these, just example
    # "Finding": ["description", "remediation"],  # Example
}

# Fields that should never be encrypted (IDs, timestamps, etc.)
EXCLUDED_FIELDS = {
    "id", "tenant_id", "created_at", "updated_at", "timestamp",
    "key_hash", "password_hash"  # Already hashed
}


def should_encrypt_field(model_class: type, field_name: str) -> bool:
    """
    Determine if a field should be encrypted.
    
    Args:
        model_class: Model class.
        field_name: Field name.
    
    Returns:
        True if field should be encrypted, False otherwise.
    """
    # Don't encrypt excluded fields
    if field_name in EXCLUDED_FIELDS:
        return False
    
    # Check if model has encrypted fields defined
    model_name = model_class.__name__
    if model_name in ENCRYPTED_FIELDS:
        return field_name in ENCRYPTED_FIELDS[model_name]
    
    # Default: don't encrypt (opt-in approach)
    return False


@event.listens_for(Session, "before_flush")
def encrypt_before_flush(session: Session, flush_context, instances):
    """
    Encrypt data before flushing to database.
    
    This event listener automatically encrypts fields marked for encryption
    before they are saved to the database.
    """
    tenant_id = get_tenant_id()
    if not tenant_id:
        # No tenant context, skip encryption
        return
    
    for instance in session.new:
        _encrypt_instance(instance, tenant_id)
    
    for instance in session.dirty:
        _encrypt_instance(instance, tenant_id)


def _encrypt_instance(instance: Any, tenant_id: str):
    """
    Encrypt fields of an instance that should be encrypted.
    
    Args:
        instance: SQLAlchemy model instance.
        tenant_id: Tenant ID for key lookup.
    """
    model_class = type(instance)
    
    for field_name in dir(instance):
        if field_name.startswith('_'):
            continue
        
        if not should_encrypt_field(model_class, field_name):
            continue
        
        try:
            field_value = getattr(instance, field_name, None)
            if field_value and isinstance(field_value, str):
                # Encrypt the value
                encrypted = encrypt_tenant_data(tenant_id, field_value)
                setattr(instance, field_name, encrypted)
                logger.debug("field_encrypted", model=model_class.__name__, field=field_name)
        except Exception as e:
            logger.error("encryption_error", model=model_class.__name__, field=field_name, error=str(e))


@event.listens_for(Session, "after_flush")
def decrypt_after_flush(session: Session, flush_context):
    """
    Decrypt data after flushing to database (for newly loaded instances).
    """
    tenant_id = get_tenant_id()
    if not tenant_id:
        return
    
    # Decrypt instances that were just loaded
    for instance in session:
        _decrypt_instance(instance, tenant_id)


def decrypt_on_load(mapper, connection, target):
    """
    Decrypt data when an instance is loaded from the database.
    
    This is called for each instance after it's loaded.
    """
    tenant_id = get_tenant_id()
    if tenant_id:
        _decrypt_instance(target, tenant_id)


def _decrypt_instance(instance: Any, tenant_id: str):
    """
    Decrypt fields of an instance that should be decrypted.
    
    Args:
        instance: SQLAlchemy model instance.
        tenant_id: Tenant ID for key lookup.
    """
    model_class = type(instance)
    
    for field_name in dir(instance):
        if field_name.startswith('_'):
            continue
        
        if not should_encrypt_field(model_class, field_name):
            continue
        
        try:
            field_value = getattr(instance, field_name, None)
            if field_value and isinstance(field_value, str):
                # Try to decrypt (may fail if not encrypted, which is OK)
                try:
                    decrypted = decrypt_tenant_data(tenant_id, field_value)
                    setattr(instance, field_name, decrypted)
                    logger.debug("field_decrypted", model=model_class.__name__, field=field_name)
                except Exception:
                    # Field may not be encrypted, leave as-is
                    pass
        except Exception as e:
            logger.error("decryption_error", model=model_class.__name__, field=field_name, error=str(e))


def enable_transparent_encryption():
    """
    Enable transparent encryption/decryption for database operations.
    
    This function registers the event listeners. It should be called
    during application startup.
    """
    # Register load event for all models
    from sentrascan.core import models
    
    # Register for all model classes
    for model_class in [models.Scan, models.Finding, models.Baseline, models.SBOM, 
                        models.User, models.Tenant, models.TenantSettings, models.AuditLog]:
        event.listen(model_class, "load", decrypt_on_load)
    
    logger.info("transparent_encryption_enabled")


def disable_transparent_encryption():
    """
    Disable transparent encryption/decryption.
    
    Note: This is mainly for testing. Event listeners cannot be easily
    unregistered, so this function is a placeholder for future implementation.
    """
    logger.info("transparent_encryption_disabled")

