"""
Test MCP Server - Main server file with intentional vulnerabilities
WARNING: This code contains intentional security vulnerabilities for testing purposes only.
DO NOT USE IN PRODUCTION.
"""

import os
import subprocess
import pickle
import json
from mcp.server import Server
from mcp.types import Tool, TextContent

# ============================================================================
# HARDCODED SECRETS - Should be detected by Gitleaks/TruffleHog
# ============================================================================

# Hardcoded API Key
API_KEY = "sk_live_51FAKE_FOR_TESTING_ONLY_NOT_REAL_KEY_1234567890abcdef"
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# Hardcoded Password
DATABASE_PASSWORD = "SuperSecretPassword123!"
ADMIN_PASSWORD = "admin:password123"

# Hardcoded Token
GITHUB_TOKEN = "ghp_1234567890abcdefghijklmnopqrstuvwxyz"
JWT_SECRET = "my-super-secret-jwt-key-change-in-production"

# Additional secrets for TruffleHog detection (different formats)
STRIPE_SECRET_KEY = "sk_live_51FAKE_FOR_TESTING_ONLY_NOT_REAL_KEY_1234567890abcdef"
STRIPE_PUBLISHABLE_KEY = "pk_live_51FAKE_FOR_TESTING_ONLY_NOT_REAL_KEY_1234567890abcdef"
AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T00000000/B00000000/FAKE_WEBHOOK_URL_FOR_TESTING_ONLY"
DATABASE_URL = "postgresql://admin:SuperSecretPassword123!@localhost:5432/production_db"
REDIS_PASSWORD = "redis-secret-password-12345"
MONGODB_CONNECTION_STRING = "mongodb://admin:SuperSecretPassword123!@localhost:27017/production"

# ============================================================================
# SQL INJECTION VULNERABILITIES - Should be detected by Semgrep/Code Rules
# ============================================================================

def get_user_by_id(user_id):
    """SQL Injection vulnerability - direct string concatenation"""
    import sqlite3
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # VULNERABLE: Direct string interpolation
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    return cursor.fetchone()

def search_users(search_term):
    """SQL Injection vulnerability - format string"""
    import sqlite3
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # VULNERABLE: String formatting
    query = "SELECT * FROM users WHERE name LIKE '%{}%'".format(search_term)
    cursor.execute(query)
    return cursor.fetchall()

def delete_user(user_id):
    """SQL Injection vulnerability - % operator"""
    import sqlite3
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # VULNERABLE: % formatting
    query = "DELETE FROM users WHERE id = '%s'" % user_id
    cursor.execute(query)
    conn.commit()

# ============================================================================
# COMMAND INJECTION VULNERABILITIES - Should be detected by Semgrep
# ============================================================================

def ping_host(hostname):
    """Command Injection vulnerability - shell=True"""
    # VULNERABLE: User input in shell command
    result = subprocess.run(f"ping -c 4 {hostname}", shell=True, capture_output=True)
    return result.stdout.decode()

def list_files(directory):
    """Command Injection vulnerability - os.system"""
    # VULNERABLE: Direct os.system call with user input
    os.system(f"ls -la {directory}")

def execute_command(cmd):
    """Command Injection vulnerability - subprocess.call"""
    # VULNERABLE: shell=True with user input
    subprocess.call(cmd, shell=True)

# ============================================================================
# REMOTE CODE EXECUTION (RCE) - Should be detected by Semgrep/Code Rules
# ============================================================================

def execute_user_code(code):
    """RCE vulnerability - eval()"""
    # VULNERABLE: eval with user input
    result = eval(code)
    return result

def run_user_script(script):
    """RCE vulnerability - exec()"""
    # VULNERABLE: exec with user input
    exec(script)

def load_pickle_data(data):
    """RCE vulnerability - pickle.loads()"""
    # VULNERABLE: pickle deserialization
    obj = pickle.loads(data)
    return obj

def process_json_data(json_str):
    """RCE vulnerability - json.loads with eval"""
    # VULNERABLE: Using eval to parse JSON
    data = eval(f"json.loads('{json_str}')")
    return data

# ============================================================================
# SSRF (Server-Side Request Forgery) - Should be detected by Semgrep
# ============================================================================

def fetch_url(url):
    """SSRF vulnerability - requests.get with user input"""
    import requests
    # VULNERABLE: User-controlled URL
    response = requests.get(url)
    return response.text

def download_file(url, save_path):
    """SSRF vulnerability - urllib"""
    import urllib.request
    # VULNERABLE: User-controlled URL
    urllib.request.urlretrieve(url, save_path)

def proxy_request(url):
    """SSRF vulnerability - requests.post"""
    import requests
    # VULNERABLE: User-controlled URL
    response = requests.post(url, json={"data": "test"})
    return response.json()

# ============================================================================
# LOCAL FILE INCLUSION (LFI) - Should be detected by Semgrep
# ============================================================================

def read_file(filepath):
    """LFI vulnerability - Path traversal"""
    # VULNERABLE: No path validation
    with open(filepath, 'r') as f:
        return f.read()

def include_template(template_name):
    """LFI vulnerability - Template inclusion"""
    # VULNERABLE: No path validation
    template_path = f"templates/{template_name}"
    with open(template_path, 'r') as f:
        return f.read()

# ============================================================================
# ZIP SLIP VULNERABILITY - Should be detected by Semgrep
# ============================================================================

def extract_archive(zip_path, extract_to):
    """Zip Slip vulnerability - extractall without validation"""
    import zipfile
    # VULNERABLE: No path validation
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_to)

# ============================================================================
# INSECURE DESERIALIZATION - Should be detected by Semgrep
# ============================================================================

def deserialize_data(data):
    """Insecure deserialization - pickle"""
    # VULNERABLE: Pickle deserialization
    return pickle.loads(data)

def load_config(config_str):
    """Insecure deserialization - eval"""
    # VULNERABLE: Using eval
    config = eval(config_str)
    return config

# ============================================================================
# XSS (Cross-Site Scripting) - Should be detected by Semgrep
# ============================================================================

def render_template(template, user_input):
    """XSS vulnerability - Reflected XSS"""
    # VULNERABLE: No output encoding
    html = f"<div>Hello {user_input}</div>"
    return html

def display_message(message):
    """XSS vulnerability - Direct HTML output"""
    # VULNERABLE: No sanitization
    return f"<script>alert('{message}')</script>"

# ============================================================================
# WEAK CRYPTOGRAPHY - Should be detected by Semgrep
# ============================================================================

def hash_password(password):
    """Weak cryptography - MD5"""
    import hashlib
    # VULNERABLE: MD5 is cryptographically broken
    return hashlib.md5(password.encode()).hexdigest()

def encrypt_data(data, key):
    """Weak cryptography - DES"""
    from Crypto.Cipher import DES
    # VULNERABLE: DES is weak
    cipher = DES.new(key, DES.MODE_ECB)
    return cipher.encrypt(data)

# ============================================================================
# INSECURE RANDOM - Should be detected by Semgrep
# ============================================================================

def generate_token():
    """Insecure random - random() instead of secrets"""
    import random
    # VULNERABLE: random is not cryptographically secure
    return str(random.randint(1000, 9999))

def generate_session_id():
    """Insecure random - time-based"""
    import time
    # VULNERABLE: Predictable based on time
    return str(int(time.time()))

# ============================================================================
# INSECURE HTTP - Should be detected by Semgrep
# ============================================================================

def fetch_data_insecure(url):
    """Insecure HTTP - No TLS verification"""
    import requests
    # VULNERABLE: verify=False
    response = requests.get(url, verify=False)
    return response.text

# ============================================================================
# SENSITIVE DATA EXPOSURE - Should be detected by Semgrep
# ============================================================================

def log_user_data(user_id, password):
    """Sensitive data exposure - Logging passwords"""
    import logging
    # VULNERABLE: Logging sensitive data
    logging.info(f"User {user_id} logged in with password {password}")

def print_api_key():
    """Sensitive data exposure - Print statements"""
    # VULNERABLE: Printing secrets
    print(f"API Key: {API_KEY}")

# ============================================================================
# MCP Server Implementation
# ============================================================================

server = Server("test-mcp-server")

@server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="execute_code",
            description="Execute user-provided code (RCE vulnerability)",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Python code to execute"}
                },
                "required": ["code"]
            }
        ),
        Tool(
            name="execute_sql",
            description="Execute SQL query (SQL injection vulnerability)",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "SQL query to execute"}
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="fetch_url",
            description="Fetch content from URL (SSRF vulnerability)",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to fetch"}
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="read_file",
            description="Read file content (LFI vulnerability)",
            inputSchema={
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "File path to read"}
                },
                "required": ["filepath"]
            }
        ),
        Tool(
            name="execute_blender_code",
            description="Execute Blender Python code (RCE vulnerability)",
            inputSchema={
                "type": "object",
                "properties": {
                    "code": {"type": "string", "description": "Blender Python code"}
                },
                "required": ["code"]
            }
        ),
    ]

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handle tool calls"""
    if name == "execute_code":
        code = arguments.get("code", "")
        result = execute_user_code(code)
        return [TextContent(type="text", text=str(result))]
    elif name == "execute_sql":
        query = arguments.get("query", "")
        from .database import get_user_by_id
        result = get_user_by_id(query)  # SQL injection vulnerability
        return [TextContent(type="text", text=str(result))]
    elif name == "fetch_url":
        url = arguments.get("url", "")
        content = fetch_url(url)
        return [TextContent(type="text", text=content)]
    elif name == "read_file":
        filepath = arguments.get("filepath", "")
        content = read_file(filepath)
        return [TextContent(type="text", text=content)]
    elif name == "execute_blender_code":
        code = arguments.get("code", "")
        result = execute_user_code(code)
        return [TextContent(type="text", text=str(result))]
    else:
        raise ValueError(f"Unknown tool: {name}")

if __name__ == "__main__":
    from mcp.server.stdio import stdio_server
    import asyncio
    asyncio.run(stdio_server(server))

