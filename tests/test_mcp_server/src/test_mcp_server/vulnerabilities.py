"""
Additional vulnerability patterns for comprehensive scanner testing
WARNING: This code contains intentional security vulnerabilities for testing purposes only.
"""

import xml.etree.ElementTree as ET
import yaml
import json
import re

# ============================================================================
# XXE (XML External Entity) VULNERABILITIES
# ============================================================================

def parse_xml_unsafe(xml_string):
    """XXE vulnerability - XML parsing without entity protection"""
    # VULNERABLE: No protection against XXE
    tree = ET.fromstring(xml_string)
    return tree

def parse_xml_file_unsafe(filepath):
    """XXE vulnerability - XML file parsing"""
    # VULNERABLE: No entity protection
    tree = ET.parse(filepath)
    return tree.getroot()

# ============================================================================
# PATH TRAVERSAL VULNERABILITIES
# ============================================================================

def read_user_file(username, filename):
    """Path traversal - User-controlled path"""
    # VULNERABLE: No path validation
    filepath = f"/home/{username}/files/{filename}"
    with open(filepath, 'r') as f:
        return f.read()

def save_user_upload(username, filename, content):
    """Path traversal - File upload"""
    # VULNERABLE: No path sanitization
    upload_path = f"/uploads/{username}/{filename}"
    with open(upload_path, 'wb') as f:
        f.write(content)

# ============================================================================
# INSECURE YAML/JSON PARSING
# ============================================================================

def load_yaml_unsafe(yaml_str):
    """Insecure YAML loading - can execute code"""
    # VULNERABLE: yaml.load instead of yaml.safe_load
    return yaml.load(yaml_str, Loader=yaml.Loader)

def parse_json_unsafe(json_str):
    """Insecure JSON parsing with eval"""
    # VULNERABLE: Using eval
    return eval(f"json.loads('{json_str}')")

# ============================================================================
# REGEX INJECTION (ReDoS)
# ============================================================================

def match_pattern(user_pattern, text):
    """ReDoS vulnerability - User-controlled regex"""
    # VULNERABLE: User input in regex
    pattern = re.compile(user_pattern)
    return pattern.match(text)

# ============================================================================
# HARDCODED CREDENTIALS IN COMMENTS
# ============================================================================

# Database credentials: admin / SuperSecretPassword123!
# API Key: sk_live_51FAKE_FOR_TESTING_ONLY_NOT_REAL_KEY_1234567890abcdef
# TODO: Remove this test key before production: ghp_TEST_TOKEN_1234567890

# ============================================================================
# INSECURE COOKIE/SESSION HANDLING
# ============================================================================

def set_session_cookie(user_id):
    """Insecure session - Predictable session ID"""
    # VULNERABLE: Predictable session ID
    session_id = f"session_{user_id}_{int(time.time())}"
    return session_id

def validate_session_unsafe(session_token):
    """Insecure session validation"""
    # VULNERABLE: No proper validation
    if session_token.startswith("session_"):
        return True
    return False

# ============================================================================
# INFORMATION DISCLOSURE
# ============================================================================

def get_error_details(error):
    """Information disclosure - Detailed error messages"""
    # VULNERABLE: Exposes internal details
    return f"Error in {error.__class__.__name__}: {str(error)} at {error.__traceback__}"

def debug_response(request):
    """Information disclosure - Debug mode"""
    # VULNERABLE: Exposes internal state
    return {
        "request": str(request),
        "headers": dict(request.headers),
        "cookies": dict(request.cookies),
        "environment": dict(os.environ)
    }

