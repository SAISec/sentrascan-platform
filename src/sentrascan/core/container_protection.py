"""
Container protection module.

Prevents unauthorized access to the container by requiring a build-time access key.
"""

import os
import sys


def check_container_access():
    """
    Check if container access is allowed.
    
    This function is called at startup to ensure the container can only be accessed
    with the correct build-time access key.
    
    The access key is set at build time via CONTAINER_ACCESS_KEY environment variable.
    At runtime, the container checks for SENTRASCAN_ACCESS_KEY environment variable.
    
    If the keys don't match or are missing, the container will exit.
    """
    build_time_key = os.environ.get("CONTAINER_ACCESS_KEY")
    runtime_key = os.environ.get("SENTRASCAN_ACCESS_KEY")
    
    # If no build-time key is set, allow access (development mode)
    if not build_time_key:
        return True
    
    # If runtime key is not provided, deny access
    if not runtime_key:
        print("ERROR: Container access key required. Set SENTRASCAN_ACCESS_KEY environment variable.", file=sys.stderr)
        sys.exit(1)
    
    # Compare keys (constant-time comparison to prevent timing attacks)
    if not _constant_time_compare(build_time_key, runtime_key):
        print("ERROR: Invalid container access key.", file=sys.stderr)
        sys.exit(1)
    
    return True


def _constant_time_compare(a: str, b: str) -> bool:
    """
    Constant-time string comparison to prevent timing attacks.
    
    Args:
        a: First string.
        b: Second string.
    
    Returns:
        True if strings are equal, False otherwise.
    """
    if len(a) != len(b):
        return False
    
    result = 0
    for x, y in zip(a.encode(), b.encode()):
        result |= x ^ y
    
    return result == 0

