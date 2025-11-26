"""
Data masking utilities for logging and telemetry.

Masks sensitive data like API keys, passwords, and PII before logging.
"""

import re
from typing import Any, Dict, List, Union


def mask_api_key(api_key: str, show_prefix: bool = True) -> str:
    """
    Mask an API key, showing only the prefix if requested.
    
    Args:
        api_key: The API key to mask.
        show_prefix: If True, show the prefix (e.g., "ss-proj-h_") and mask the rest.
                    If False, mask the entire key.
    
    Returns:
        Masked API key string.
    """
    if not api_key:
        return "***"
    
    # Check if it matches the expected format
    if api_key.startswith("ss-proj-h_") and len(api_key) > 10:
        if show_prefix:
            # Show first 10 chars (prefix) and mask the rest
            return f"{api_key[:10]}***{api_key[-4:]}"
        else:
            return "ss-proj-h_***"
    
    # Generic masking for other formats
    if len(api_key) > 8:
        return f"{api_key[:4]}***{api_key[-4:]}"
    return "***"


def mask_password(password: str) -> str:
    """
    Mask a password completely.
    
    Args:
        password: The password to mask.
    
    Returns:
        Always returns "***".
    """
    return "***"


def mask_email(email: str) -> str:
    """
    Mask an email address, showing only the domain.
    
    Args:
        email: The email address to mask.
    
    Returns:
        Masked email (e.g., "***@example.com").
    """
    if not email or "@" not in email:
        return "***"
    
    parts = email.split("@", 1)
    if len(parts) == 2:
        return f"***@{parts[1]}"
    return "***"


def mask_url(url: str) -> str:
    """
    Mask sensitive parts of a URL (credentials, query params).
    
    Args:
        url: The URL to mask.
    
    Returns:
        Masked URL with credentials and query params removed.
    """
    if not url:
        return "***"
    
    try:
        from urllib.parse import urlparse, urlunparse, parse_qs, urlencode
        
        parsed = urlparse(url)
        
        # Mask user:password in netloc
        if "@" in parsed.netloc:
            netloc_parts = parsed.netloc.split("@")
            if len(netloc_parts) == 2:
                netloc = f"***@{netloc_parts[1]}"
            else:
                netloc = "***"
        else:
            netloc = parsed.netloc
        
        # Remove query string
        query = ""
        
        # Reconstruct URL
        return urlunparse((
            parsed.scheme,
            netloc,
            parsed.path,
            parsed.params,
            query,
            ""  # fragment
        ))
    except Exception:
        # Fallback: simple masking
        if "@" in url:
            return re.sub(r'://[^@]+@', '://***@', url)
        return url.split("?")[0] if "?" in url else url


def mask_dict(data: Dict[str, Any], sensitive_keys: List[str] = None) -> Dict[str, Any]:
    """
    Recursively mask sensitive values in a dictionary.
    
    Args:
        data: Dictionary to mask.
        sensitive_keys: List of keys that should be masked. Defaults to common sensitive keys.
    
    Returns:
        Dictionary with sensitive values masked.
    """
    if sensitive_keys is None:
        sensitive_keys = [
            "password", "passwd", "pwd", "secret", "token", "api_key", "apikey",
            "api-key", "access_token", "refresh_token", "authorization", "auth",
            "credential", "credentials", "key", "private_key", "private-key",
            "session", "cookie", "ssn", "social_security", "credit_card", "cc",
            "email", "e-mail", "phone", "telephone", "address"
        ]
    
    masked = {}
    for key, value in data.items():
        key_lower = key.lower()
        
        # Check if this key should be masked
        should_mask = any(sk in key_lower for sk in sensitive_keys)
        
        if should_mask:
            if isinstance(value, str):
                if "password" in key_lower or "passwd" in key_lower or "pwd" in key_lower:
                    masked[key] = mask_password(value)
                elif "api_key" in key_lower or "apikey" in key_lower or "token" in key_lower:
                    masked[key] = mask_api_key(value, show_prefix=True)
                elif "email" in key_lower or "e-mail" in key_lower:
                    masked[key] = mask_email(value)
                elif "url" in key_lower or "uri" in key_lower:
                    masked[key] = mask_url(value)
                else:
                    masked[key] = "***"
            else:
                masked[key] = "***"
        elif isinstance(value, dict):
            masked[key] = mask_dict(value, sensitive_keys)
        elif isinstance(value, list):
            masked[key] = [mask_dict(item, sensitive_keys) if isinstance(item, dict) else item for item in value]
        else:
            masked[key] = value
    
    return masked


def mask_string(text: str, patterns: List[str] = None) -> str:
    """
    Mask sensitive patterns in a string.
    
    Args:
        text: String to mask.
        patterns: List of regex patterns to match and mask. Defaults to common patterns.
    
    Returns:
        String with sensitive patterns masked.
    """
    if patterns is None:
        patterns = [
            r'ss-proj-h_[A-Za-z0-9-]{147}',  # API key format
            r'password\s*[:=]\s*["\']?[^"\'\s]+["\']?',  # password: value
            r'api[_-]?key\s*[:=]\s*["\']?[^"\'\s]+["\']?',  # api_key: value
            r'token\s*[:=]\s*["\']?[^"\'\s]+["\']?',  # token: value
            r'secret\s*[:=]\s*["\']?[^"\'\s]+["\']?',  # secret: value
        ]
    
    masked_text = text
    for pattern in patterns:
        masked_text = re.sub(pattern, "***", masked_text, flags=re.IGNORECASE)
    
    return masked_text

