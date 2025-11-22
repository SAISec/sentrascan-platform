from sqlalchemy import Column, String, Integer, Boolean, Text, JSON, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.sqlite import BLOB
from sqlalchemy.orm import relationship
from datetime import datetime
from sentrascan.core.storage import Base
import uuid as _uuid

class Scan(Base):
    __tablename__ = "scans"
    id = Column(String, primary_key=True, default=lambda: str(_uuid.uuid4()))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    scan_type = Column(String, nullable=False)  # 'mcp' or 'model'
    target_path = Column(String, nullable=False)
    target_format = Column(String)
    target_hash = Column(String)
    scan_status = Column(String, default="completed")
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

    findings = relationship("Finding", backref="scan", cascade="all, delete-orphan")

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

class APIKey(Base):
    __tablename__ = "api_keys"
    id = Column(String, primary_key=True, default=lambda: str(_uuid.uuid4()))
    name = Column(String)
    role = Column(String, default="viewer")
    key_hash = Column(String, unique=True)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    @staticmethod
    def hash_key(key: str) -> str:
        import hashlib
        return hashlib.sha256(key.encode()).hexdigest()

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
