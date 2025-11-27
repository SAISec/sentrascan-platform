"""
Query helpers for tenant-scoped database queries.
"""

from typing import TypeVar, Type, Optional
from sqlalchemy.orm import Query, Session
from sqlalchemy import Column
from sentrascan.core.tenant_context import get_tenant_id
from sentrascan.core.sharding import get_shard_session, route_query_to_shard

T = TypeVar('T')


def filter_by_tenant(query: Query, model_class: Type[T], tenant_id: str = None) -> Query:
    """
    Add tenant_id filtering to a query.
    
    Args:
        query: SQLAlchemy query object.
        model_class: The model class being queried.
        tenant_id: Optional tenant_id. If not provided, uses get_tenant_id().
    
    Returns:
        Query with tenant_id filter applied.
    """
    if tenant_id is None:
        tenant_id = get_tenant_id()
    
    if tenant_id and hasattr(model_class, 'tenant_id'):
        query = query.filter(model_class.tenant_id == tenant_id)
    
    return query


def get_tenant_db_session(tenant_id: str = None, db: Session = None) -> Optional[Session]:
    """
    Get a database session routed to the correct shard for a tenant.
    
    This function automatically routes queries to the correct shard based on tenant_id.
    If sharding is not enabled or tenant_id is not available, returns the default session.
    
    Args:
        tenant_id: Optional tenant ID. If not provided, uses get_tenant_id().
        db: Optional existing session (for metadata lookup).
    
    Returns:
        SQLAlchemy session bound to the tenant's shard, or None if error.
    """
    if tenant_id is None:
        tenant_id = get_tenant_id()
    
    if not tenant_id:
        # No tenant context, return default session
        return db
    
    # Route to shard
    shard_session = route_query_to_shard(tenant_id, db)
    return shard_session if shard_session else db


def require_tenant_for_query(query: Query, model_class: Type[T], tenant_id: str = None) -> Query:
    """
    Require tenant_id for a query (raises error if no tenant_id).
    
    Args:
        query: SQLAlchemy query object.
        model_class: The model class being queried.
        tenant_id: Optional tenant_id. If not provided, uses get_tenant_id().
    
    Returns:
        Query with tenant_id filter applied.
    
    Raises:
        ValueError: If no tenant_id is available.
    """
    if tenant_id is None:
        tenant_id = get_tenant_id()
    
    if not tenant_id:
        raise ValueError("Tenant context required for this query")
    
    if hasattr(model_class, 'tenant_id'):
        query = query.filter(model_class.tenant_id == tenant_id)
    
    return query

