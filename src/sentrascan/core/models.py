from sqlalchemy import Column, String, Integer, Boolean, Text, JSON, TIMESTAMP, ForeignKey, Index
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.orm import relationship
from datetime import datetime
from sentrascan.core.storage import Base
import uuid as _uuid

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(String, primary_key=True, default=lambda: str(_uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    settings = Column(JSON, default=dict)  # Tenant-specific settings
    
    # Relationships
    users = relationship("User", backref="tenant", cascade="all, delete-orphan")
    api_keys = relationship("APIKey", backref="tenant", cascade="all, delete-orphan")
    scans = relationship("Scan", backref="tenant", cascade="all, delete-orphan")
    findings = relationship("Finding", backref="tenant", cascade="all, delete-orphan")
    baselines = relationship("Baseline", backref="tenant", cascade="all, delete-orphan")
    sboms = relationship("SBOM", backref="tenant", cascade="all, delete-orphan")
    tenant_settings = relationship("TenantSettings", backref="tenant", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", backref="tenant", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=lambda: str(_uuid.uuid4()))
    email = Column(String, nullable=False, unique=True)
    password_hash = Column(String, nullable=False)
    name = Column(String, nullable=False)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    role = Column(String, nullable=False, default="viewer")  # super_admin, tenant_admin, viewer, scanner
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    mfa_enabled = Column(Boolean, default=False)
    mfa_secret = Column(String, nullable=True)  # Encrypted MFA secret
    password_changed_at = Column(TIMESTAMP, nullable=True)  # Track password changes for expiration
    
    # Relationships
    audit_logs = relationship("AuditLog", backref="user", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_users_tenant_id', 'tenant_id'),
        Index('idx_users_email', 'email'),
    )

class TenantSettings(Base):
    __tablename__ = "tenant_settings"
    id = Column(String, primary_key=True, default=lambda: str(_uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    setting_key = Column(String, nullable=False)
    setting_value = Column(JSON, nullable=False)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    
    __table_args__ = (
        Index('idx_tenant_settings_tenant_key', 'tenant_id', 'setting_key', unique=True),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=lambda: str(_uuid.uuid4()))
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action = Column(String, nullable=False)  # create, update, delete, login, logout, etc.
    resource_type = Column(String, nullable=False)  # scan, finding, user, tenant, etc.
    resource_id = Column(String, nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String, nullable=True)
    timestamp = Column(TIMESTAMP, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_audit_logs_tenant_id', 'tenant_id'),
        Index('idx_audit_logs_user_id', 'user_id'),
        Index('idx_audit_logs_timestamp', 'timestamp'),
    )

class Scan(Base):
    __tablename__ = "scans"
    id = Column(String, primary_key=True, default=lambda: str(_uuid.uuid4()))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    scan_type = Column(String, nullable=False)  # 'mcp' or 'model'
    target_path = Column(String, nullable=False)
    target_format = Column(String)
    target_hash = Column(String)
    # Scan status: waiting_to_start, in_progress, completed, aborted, failed
    scan_status = Column(String, default="waiting_to_start")
    # Scan result: True = Pass, False = Fail (based on policy gate evaluation)
    passed = Column(Boolean, default=False)
    duration_ms = Column(Integer, default=0)
    total_findings = Column(Integer, default=0)
    critical_count = Column(Integer, default=0)
    high_count = Column(Integer, default=0)
    medium_count = Column(Integer, default=0)
    low_count = Column(Integer, default=0)
    baseline_id = Column(String)
    sbom_id = Column(String)
    meta = Column(JSON)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)

    findings = relationship("Finding", backref="scan", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_scans_tenant_id', 'tenant_id'),
    )

class Finding(Base):
    __tablename__ = "findings"
    id = Column(String, primary_key=True, default=lambda: str(_uuid.uuid4()))
    scan_id = Column(String, ForeignKey("scans.id", ondelete="CASCADE"))
    module = Column(String, nullable=False)
    scanner = Column(String, nullable=False)
    severity = Column(String, nullable=False)
    category = Column(String, nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text)
    location = Column(String)
    evidence = Column(JSON)
    remediation = Column(Text)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    __table_args__ = (
        Index('idx_findings_tenant_id', 'tenant_id'),
        Index('idx_findings_scan_id', 'scan_id'),
    )

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(String, primary_key=True, default=lambda: str(_uuid.uuid4()))
    name = Column(String, nullable=True)
    role = Column(String, default="viewer")
    key_hash = Column(String, unique=True)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="SET NULL"), nullable=True)  # Optional: associate with user
    expires_at = Column(TIMESTAMP, nullable=True)  # Optional expiration date
    last_rotated_at = Column(TIMESTAMP, nullable=True)  # Track key rotation
    rotation_count = Column(Integer, default=0)  # Number of times key has been rotated
    
    __table_args__ = (
        Index('idx_api_keys_tenant_id', 'tenant_id'),
        Index('idx_api_keys_user_id', 'user_id'),
    )

    @staticmethod
    def hash_key(key: str) -> str:
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()
    
    @staticmethod
    def validate_key_format(key: str) -> bool:
        """
        Validate API key format matches requirement: ss-proj-h_ prefix and 
        147-character alphanumeric string with exactly one hyphen.
        """
        import re
        pattern = r'^ss-proj-h_[A-Za-z0-9-]{147}$'
        if not re.match(pattern, key):
            return False
        
        # Check that there's exactly one hyphen in the 147-character part
        key_part = key[10:]  # After "ss-proj-h_"
        if key_part.count('-') != 1:
            return False
        
        return True

class SBOM(Base):
    __tablename__ = "sboms"
    id = Column(String, primary_key=True, default=lambda: str(_uuid.uuid4()))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    model_name = Column(String)
    model_version = Column(String)
    bom_format = Column(String)
    spec_version = Column(String)
    content = Column(JSON)
    hash = Column(String)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    __table_args__ = (
        Index('idx_sboms_tenant_id', 'tenant_id'),
    )

class Baseline(Base):
    __tablename__ = "baselines"
    id = Column(String, primary_key=True, default=lambda: str(_uuid.uuid4()))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    baseline_type = Column(String, nullable=False)  # 'mcp' or 'model'
    name = Column(String, nullable=False)
    description = Column(Text)
    target_hash = Column(String)
    content = Column(JSON)  # baseline JSON
    scan_id = Column(String)
    sbom_id = Column(String)
    approved_by = Column(String)
    approval_date = Column(TIMESTAMP)
    is_active = Column(Boolean, default=True)
    tenant_id = Column(String, ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False)
    
    __table_args__ = (
        Index('idx_baselines_tenant_id', 'tenant_id'),
    )
