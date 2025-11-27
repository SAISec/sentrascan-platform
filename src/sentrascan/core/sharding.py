"""
Database sharding module for SentraScan Platform.

Implements schema-based sharding strategy where each tenant's data is stored
in a separate database schema. Provides functions for shard routing, schema
management, and secure metadata storage.
"""

import os
import hashlib
from typing import Optional, Dict, List
from datetime import datetime
from sqlalchemy import create_engine, text, inspect, Column, String, Integer, Boolean, TIMESTAMP, Index
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from sentrascan.core.storage import Base, engine, SessionLocal
from sentrascan.core.logging import get_logger
from sentrascan.core.tenant_context import get_tenant_id

logger = get_logger(__name__)

# Sharding configuration
SHARD_COUNT = int(os.environ.get("SHARD_COUNT", "4"))  # Default 4 shards
SHARD_PREFIX = os.environ.get("SHARD_PREFIX", "shard_")  # Schema prefix
METADATA_SCHEMA = "shard_metadata"  # Schema for storing shard metadata (not tenant-accessible)


class ShardMetadata(Base):
    """
    Model for storing shard metadata.
    This table is stored in a separate schema (METADATA_SCHEMA) that is not
    accessible to tenants, ensuring security of shard routing information.
    """
    __tablename__ = "shard_metadata"
    __table_args__ = (
        Index('idx_shard_metadata_schema', 'schema_name'),
        Index('idx_shard_metadata_shard_id', 'shard_id'),
        {"schema": METADATA_SCHEMA}
    )
    
    tenant_id = Column(String, primary_key=True)
    schema_name = Column(String, nullable=False, unique=True)
    shard_id = Column(Integer, nullable=False)  # Shard number (0 to SHARD_COUNT-1)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)


def init_sharding_metadata():
    """
    Initialize the sharding metadata schema and table.
    This creates the metadata schema and ShardMetadata table if they don't exist.
    """
    try:
        with engine.connect() as conn:
            # Create metadata schema if it doesn't exist
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {METADATA_SCHEMA}"))
            conn.commit()
        
        # Create ShardMetadata table
        ShardMetadata.__table__.create(bind=engine, checkfirst=True)
        
        logger.info("sharding_metadata_initialized", schema=METADATA_SCHEMA)
        return True
    except SQLAlchemyError as e:
        logger.error("sharding_metadata_init_failed", error=str(e))
        return False


def get_shard_id(tenant_id: str) -> int:
    """
    Calculate shard ID for a tenant using consistent hashing.
    
    Uses SHA-256 hash of tenant_id, then modulo SHARD_COUNT to determine
    which shard the tenant's data should be stored in.
    
    Args:
        tenant_id: Tenant ID string.
    
    Returns:
        Shard ID (0 to SHARD_COUNT-1).
    """
    hash_obj = hashlib.sha256(tenant_id.encode())
    hash_int = int(hash_obj.hexdigest(), 16)
    shard_id = hash_int % SHARD_COUNT
    return shard_id


def get_schema_name(tenant_id: str) -> str:
    """
    Generate schema name for a tenant based on tenant_id.
    
    Args:
        tenant_id: Tenant ID string.
    
    Returns:
        Schema name in format: {SHARD_PREFIX}{shard_id}_{sanitized_tenant_id}
    """
    shard_id = get_shard_id(tenant_id)
    # Sanitize tenant_id for use in schema name (remove special chars, limit length)
    sanitized = tenant_id.replace("-", "_").replace(".", "_")[:20]
    schema_name = f"{SHARD_PREFIX}{shard_id}_{sanitized}"
    return schema_name


def create_shard_schema(tenant_id: str, db: Session) -> Optional[str]:
    """
    Create a new shard schema for a tenant.
    
    This function:
    1. Calculates the shard ID and schema name
    2. Creates the schema in the database
    3. Stores the mapping in ShardMetadata table
    
    Args:
        tenant_id: Tenant ID string.
        db: Database session.
    
    Returns:
        Schema name if successful, None otherwise.
    """
    try:
        schema_name = get_schema_name(tenant_id)
        shard_id = get_shard_id(tenant_id)
        
        # Check if schema already exists
        existing = db.query(ShardMetadata).filter(
            ShardMetadata.tenant_id == tenant_id
        ).first()
        
        if existing:
            logger.info("shard_schema_exists", tenant_id=tenant_id, schema_name=existing.schema_name)
            return existing.schema_name
        
        # Create schema in database
        with engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
            conn.commit()
        
        # Store metadata
        metadata = ShardMetadata(
            tenant_id=tenant_id,
            schema_name=schema_name,
            shard_id=shard_id,
            is_active=True
        )
        db.add(metadata)
        db.commit()
        db.refresh(metadata)
        
        logger.info(
            "shard_schema_created",
            tenant_id=tenant_id,
            schema_name=schema_name,
            shard_id=shard_id
        )
        
        return schema_name
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("shard_schema_creation_failed", tenant_id=tenant_id, error=str(e))
        return None


def get_shard_schema(tenant_id: str, db: Session) -> Optional[str]:
    """
    Get the schema name for a tenant.
    
    Args:
        tenant_id: Tenant ID string.
        db: Database session.
    
    Returns:
        Schema name if found, None otherwise.
    """
    try:
        metadata = db.query(ShardMetadata).filter(
            ShardMetadata.tenant_id == tenant_id,
            ShardMetadata.is_active == True
        ).first()
        
        if metadata:
            return metadata.schema_name
        
        # If not found, create it
        return create_shard_schema(tenant_id, db)
    except SQLAlchemyError as e:
        logger.error("shard_schema_lookup_failed", tenant_id=tenant_id, error=str(e))
        return None


def get_shard_for_tenant(tenant_id: str, db: Session) -> Optional[Dict]:
    """
    Get shard information for a tenant.
    
    Args:
        tenant_id: Tenant ID string.
        db: Database session.
    
    Returns:
        Dictionary with shard information (tenant_id, schema_name, shard_id) or None.
    """
    try:
        metadata = db.query(ShardMetadata).filter(
            ShardMetadata.tenant_id == tenant_id,
            ShardMetadata.is_active == True
        ).first()
        
        if metadata:
            return {
                "tenant_id": metadata.tenant_id,
                "schema_name": metadata.schema_name,
                "shard_id": metadata.shard_id,
                "created_at": metadata.created_at,
                "is_active": metadata.is_active
            }
        return None
    except SQLAlchemyError as e:
        logger.error("shard_lookup_failed", tenant_id=tenant_id, error=str(e))
        return None


def list_shards(db: Session) -> List[Dict]:
    """
    List all active shards.
    
    Args:
        db: Database session.
    
    Returns:
        List of dictionaries with shard information.
    """
    try:
        shards = db.query(ShardMetadata).filter(
            ShardMetadata.is_active == True
        ).all()
        
        return [
            {
                "tenant_id": s.tenant_id,
                "schema_name": s.schema_name,
                "shard_id": s.shard_id,
                "created_at": s.created_at.isoformat() if s.created_at else None,
                "is_active": s.is_active
            }
            for s in shards
        ]
    except SQLAlchemyError as e:
        logger.error("shard_list_failed", error=str(e))
        return []


def deactivate_shard(tenant_id: str, db: Session) -> bool:
    """
    Deactivate a shard (soft delete).
    
    Args:
        tenant_id: Tenant ID string.
        db: Database session.
    
    Returns:
        True if successful, False otherwise.
    """
    try:
        metadata = db.query(ShardMetadata).filter(
            ShardMetadata.tenant_id == tenant_id
        ).first()
        
        if metadata:
            metadata.is_active = False
            db.commit()
            logger.info("shard_deactivated", tenant_id=tenant_id, schema_name=metadata.schema_name)
            return True
        return False
    except SQLAlchemyError as e:
        db.rollback()
        logger.error("shard_deactivation_failed", tenant_id=tenant_id, error=str(e))
        return False


def get_shard_statistics(db: Session) -> Dict:
    """
    Get statistics about shard distribution.
    
    Args:
        db: Database session.
    
    Returns:
        Dictionary with shard statistics.
    """
    try:
        total_shards = db.query(ShardMetadata).filter(
            ShardMetadata.is_active == True
        ).count()
        
        # Count tenants per shard
        shard_counts = {}
        shards = db.query(ShardMetadata).filter(
            ShardMetadata.is_active == True
        ).all()
        
        for shard in shards:
            shard_id = shard.shard_id
            shard_counts[shard_id] = shard_counts.get(shard_id, 0) + 1
        
        return {
            "total_shards": total_shards,
            "configured_shard_count": SHARD_COUNT,
            "tenants_per_shard": shard_counts,
            "average_tenants_per_shard": total_shards / SHARD_COUNT if SHARD_COUNT > 0 else 0
        }
    except SQLAlchemyError as e:
        logger.error("shard_statistics_failed", error=str(e))
        return {}


# Connection pooling with shard-aware routing
_shard_engines: Dict[str, any] = {}
_shard_sessions: Dict[str, any] = {}


def get_shard_engine(schema_name: str):
    """
    Get or create a database engine for a specific shard schema.
    
    This creates a connection pool per shard for efficient routing.
    
    Args:
        schema_name: Schema name for the shard.
    
    Returns:
        SQLAlchemy engine for the shard.
    """
    if schema_name in _shard_engines:
        return _shard_engines[schema_name]
    
    # Use the same database URL but with schema search path
    db_url = os.environ.get("DATABASE_URL", "postgresql+psycopg2://sentrascan:changeme@db:5432/sentrascan")
    
    # Create engine with schema in search_path
    shard_engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_size=5,  # Smaller pool per shard
        max_overflow=10,
        pool_recycle=3600,
        connect_args={"options": f"-csearch_path={schema_name},public"}
    )
    
    _shard_engines[schema_name] = shard_engine
    logger.debug("shard_engine_created", schema_name=schema_name)
    
    return shard_engine


def get_shard_session(tenant_id: str, db: Session = None) -> Optional[Session]:
    """
    Get a database session for a specific tenant's shard.
    
    This function:
    1. Gets the schema name for the tenant
    2. Creates or retrieves the shard engine
    3. Returns a session bound to that shard
    
    Args:
        tenant_id: Tenant ID string.
        db: Optional existing session (for metadata lookup).
    
    Returns:
        SQLAlchemy session bound to the tenant's shard, or None if error.
    """
    if not tenant_id:
        return None
    
    try:
        # Get schema name for tenant
        if db:
            schema_name = get_shard_schema(tenant_id, db)
        else:
            # Create temporary session for metadata lookup
            temp_db = SessionLocal()
            try:
                schema_name = get_shard_schema(tenant_id, temp_db)
            finally:
                temp_db.close()
        
        if not schema_name:
            logger.error("shard_schema_not_found", tenant_id=tenant_id)
            return None
        
        # Get or create shard engine
        shard_engine = get_shard_engine(schema_name)
        
        # Create session factory for this shard
        if schema_name not in _shard_sessions:
            _shard_sessions[schema_name] = sessionmaker(
                bind=shard_engine,
                autoflush=False,
                autocommit=False
            )
        
        session_factory = _shard_sessions[schema_name]
        return session_factory()
        
    except Exception as e:
        logger.error("shard_session_creation_failed", tenant_id=tenant_id, error=str(e))
        return None


def route_query_to_shard(tenant_id: str, db: Session = None) -> Optional[Session]:
    """
    Route a database query to the correct shard for a tenant.
    
    This is a convenience function that wraps get_shard_session().
    
    Args:
        tenant_id: Tenant ID string.
        db: Optional existing session (for metadata lookup).
    
    Returns:
        SQLAlchemy session bound to the tenant's shard.
    """
    return get_shard_session(tenant_id, db)

