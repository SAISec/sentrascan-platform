"""
Query helpers for tenant-scoped database queries.
"""

from typing import TypeVar, Type
from sqlalchemy.orm import Query
from sqlalchemy import Column
from sentrascan.core.tenant_context import get_tenant_id

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

