"""
API client with SSRF vulnerabilities
WARNING: This code contains intentional security vulnerabilities for testing purposes only.
"""

import requests
import urllib.request
import urllib.parse
import http.client

# ============================================================================
# SSRF (Server-Side Request Forgery) VULNERABILITIES
# ============================================================================

def fetch_user_data(user_id):
    """SSRF - User-controlled URL"""
    # VULNERABLE: User input in URL
    url = f"http://api.example.com/users/{user_id}"
    response = requests.get(url)
    return response.json()

def proxy_request(url):
    """SSRF - Proxy functionality"""
    # VULNERABLE: User-controlled URL
    response = requests.get(url, allow_redirects=True)
    return response.text

def download_file(url, save_path):
    """SSRF - File download"""
    # VULNERABLE: User-controlled URL
    urllib.request.urlretrieve(url, save_path)

def make_api_call(endpoint, data):
    """SSRF - API call"""
    # VULNERABLE: User-controlled endpoint
    url = f"http://internal-api/{endpoint}"
    response = requests.post(url, json=data)
    return response.json()

def fetch_webhook(url, payload):
    """SSRF - Webhook"""
    # VULNERABLE: User-controlled URL
    response = requests.post(url, json=payload)
    return response.status_code

def check_url_status(url):
    """SSRF - URL status check"""
    # VULNERABLE: User-controlled URL
    response = requests.head(url, timeout=5)
    return response.status_code

def fetch_with_urllib(url):
    """SSRF - urllib"""
    # VULNERABLE: User-controlled URL
    with urllib.request.urlopen(url) as response:
        return response.read()

def http_connection(host, path):
    """SSRF - http.client"""
    # VULNERABLE: User-controlled host
    conn = http.client.HTTPConnection(host)
    conn.request("GET", path)
    response = conn.getresponse()
    return response.read()

# ============================================================================
# INSECURE HTTP - No TLS verification
# ============================================================================

def fetch_insecure(url):
    """Insecure HTTP - verify=False"""
    # VULNERABLE: No TLS verification
    response = requests.get(url, verify=False)
    return response.text

def post_insecure(url, data):
    """Insecure HTTP - verify=False"""
    # VULNERABLE: No TLS verification
    response = requests.post(url, json=data, verify=False)
    return response.json()

# ============================================================================
# HARDCODED API ENDPOINTS
# ============================================================================

INTERNAL_API_URL = "http://internal-api.local/api/v1"
ADMIN_API_KEY = "internal-admin-key-12345"

def call_internal_api(endpoint):
    """Hardcoded internal API"""
    url = f"{INTERNAL_API_URL}/{endpoint}"
    headers = {"X-API-Key": ADMIN_API_KEY}
    response = requests.get(url, headers=headers)
    return response.json()

