"""
Security middleware and utilities for SentraScan Platform.

Provides rate limiting, security headers, CORS, CSRF protection,
input validation, output encoding, and request size/timeout limits.
"""

import os
import time
import secrets
import html
import re
from typing import Optional, Dict, List, Callable
from collections import defaultdict
from datetime import datetime, timedelta
from fastapi import Request, Response, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware as FastAPICORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from sentrascan.core.logging import get_logger
from sentrascan.core.tenant_context import get_tenant_id

logger = get_logger(__name__)

# Rate limiting configuration
RATE_LIMIT_API_KEY = int(os.environ.get("RATE_LIMIT_API_KEY", "100"))  # requests per minute
RATE_LIMIT_IP = int(os.environ.get("RATE_LIMIT_IP", "200"))  # requests per minute
RATE_LIMIT_TENANT = int(os.environ.get("RATE_LIMIT_TENANT", "1000"))  # requests per minute

# Request limits
MAX_REQUEST_SIZE = int(os.environ.get("MAX_REQUEST_SIZE", "10485760"))  # 10MB default
REQUEST_TIMEOUT_SECONDS = int(os.environ.get("REQUEST_TIMEOUT_SECONDS", "300"))  # 5 minutes default

# CORS configuration
CORS_ALLOWED_ORIGINS = os.environ.get("CORS_ALLOWED_ORIGINS", "").split(",") if os.environ.get("CORS_ALLOWED_ORIGINS") else []
CORS_ALLOW_CREDENTIALS = os.environ.get("CORS_ALLOW_CREDENTIALS", "true").lower() == "true"

# CSRF configuration
CSRF_TOKEN_HEADER = "X-CSRF-Token"
CSRF_COOKIE_NAME = "csrf_token"


# Rate limiting storage (in-memory, use Redis in production)
_rate_limit_storage: Dict[str, List[float]] = defaultdict(list)


def get_rate_limit_key(request: Request) -> str:
    """
    Get rate limit key for a request.
    
    Priority: API key > IP address > tenant
    """
    # Try API key first
    api_key = request.headers.get("X-API-Key")
    if api_key:
        return f"api_key:{api_key[:16]}"
    
    # Try tenant ID
    tenant_id = get_tenant_id()
    if tenant_id:
        return f"tenant:{tenant_id}"
    
    # Fall back to IP address
    client_ip = request.client.host if request.client else "unknown"
    return f"ip:{client_ip}"


def check_rate_limit(key: str, limit: int) -> bool:
    """
    Check if request is within rate limit.
    
    Args:
        key: Rate limit key.
        limit: Maximum requests per minute.
    
    Returns:
        True if within limit, False if exceeded.
    """
    now = time.time()
    minute_ago = now - 60
    
    # Clean old entries
    _rate_limit_storage[key] = [
        timestamp for timestamp in _rate_limit_storage[key]
        if timestamp > minute_ago
    ]
    
    # Check limit
    if len(_rate_limit_storage[key]) >= limit:
        return False
    
    # Add current request
    _rate_limit_storage[key].append(now)
    return True


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for rate limiting."""
    
    async def dispatch(self, request: Request, call_next):
        # Skip rate limiting for health checks
        if request.url.path == "/api/v1/health":
            return await call_next(request)
        
        key = get_rate_limit_key(request)
        
        # Determine limit based on key type
        if key.startswith("api_key:"):
            limit = RATE_LIMIT_API_KEY
        elif key.startswith("tenant:"):
            limit = RATE_LIMIT_TENANT
        else:
            limit = RATE_LIMIT_IP
        
        if not check_rate_limit(key, limit):
            logger.warning("rate_limit_exceeded", key=key[:20], limit=limit)
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": "Rate limit exceeded", "retry_after": 60}
            )
        
        return await call_next(request)


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware for adding security headers."""
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HSTS (only for HTTPS)
        if request.url.scheme == "https":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy
        # Allow trusted CDNs for Chart.js, marked, Prism.js
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
            "img-src 'self' data:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp
        
        return response


class RequestSizeLimitMiddleware(BaseHTTPMiddleware):
    """Middleware for limiting request size."""
    
    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")
        if content_length:
            try:
                size = int(content_length)
                if size > MAX_REQUEST_SIZE:
                    logger.warning("request_size_exceeded", size=size, limit=MAX_REQUEST_SIZE)
                    return JSONResponse(
                        status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                        content={"error": f"Request too large. Maximum size: {MAX_REQUEST_SIZE} bytes"}
                    )
            except ValueError:
                pass
        
        return await call_next(request)


# CSRF token management
_csrf_tokens: Dict[str, str] = {}


def generate_csrf_token() -> str:
    """Generate a CSRF token."""
    return secrets.token_urlsafe(32)


def validate_csrf_token(request: Request) -> bool:
    """
    Validate CSRF token from request.
    
    Args:
        request: FastAPI request object.
    
    Returns:
        True if token is valid, False otherwise.
    """
    # Get token from cookie
    cookie_token = request.cookies.get(CSRF_COOKIE_NAME)
    if not cookie_token:
        return False
    
    # Get token from header
    header_token = request.headers.get(CSRF_TOKEN_HEADER)
    if not header_token:
        return False
    
    # Compare tokens
    return cookie_token == header_token


def sanitize_input(value: str) -> str:
    """
    Sanitize input to prevent injection attacks.
    
    Args:
        value: Input string.
    
    Returns:
        Sanitized string.
    """
    if not isinstance(value, str):
        return value
    
    # Remove null bytes
    value = value.replace('\x00', '')
    
    # Remove control characters (except newlines and tabs)
    value = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', value)
    
    return value


def encode_output(value: str) -> str:
    """
    Encode output to prevent XSS attacks.
    
    Args:
        value: String to encode.
    
    Returns:
        HTML-encoded string.
    """
    if not isinstance(value, str):
        return str(value)
    
    return html.escape(value)


def validate_email(email: str) -> bool:
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_uuid(uuid_str: str) -> bool:
    """Validate UUID format."""
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_str, re.IGNORECASE))


def validate_api_key_format(key: str) -> bool:
    """Validate API key format."""
    pattern = r'^ss-proj-h_[A-Za-z0-9-]{147}$'
    if not re.match(pattern, key):
        return False
    
    # Check exactly one hyphen in the key part
    key_part = key[10:]
    return key_part.count('-') == 1

