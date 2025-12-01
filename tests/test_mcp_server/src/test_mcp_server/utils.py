"""
Utility functions with various vulnerabilities
WARNING: This code contains intentional security vulnerabilities for testing purposes only.
"""

import hashlib
import random
import time
import base64
import pickle
import json
import subprocess
import os

# ============================================================================
# WEAK CRYPTOGRAPHY
# ============================================================================

def hash_with_md5(data):
    """Weak cryptography - MD5"""
    # VULNERABLE: MD5 is broken
    return hashlib.md5(data.encode()).hexdigest()

def hash_with_sha1(data):
    """Weak cryptography - SHA1"""
    # VULNERABLE: SHA1 is deprecated
    return hashlib.sha1(data.encode()).hexdigest()

def encrypt_des(data, key):
    """Weak cryptography - DES"""
    from Crypto.Cipher import DES
    # VULNERABLE: DES is weak
    cipher = DES.new(key, DES.MODE_ECB)
    return cipher.encrypt(data)

# ============================================================================
# INSECURE RANDOM
# ============================================================================

def generate_id():
    """Insecure random - random()"""
    # VULNERABLE: Not cryptographically secure
    return random.randint(1000, 9999)

def generate_session_token():
    """Insecure random - time-based"""
    # VULNERABLE: Predictable
    return str(int(time.time()))

def generate_api_key():
    """Insecure random - random string"""
    # VULNERABLE: Not secure
    chars = "abcdefghijklmnopqrstuvwxyz0123456789"
    return ''.join(random.choice(chars) for _ in range(32))

# ============================================================================
# INSECURE DESERIALIZATION
# ============================================================================

def deserialize_pickle(data):
    """Insecure deserialization - pickle"""
    # VULNERABLE: Pickle can execute code
    return pickle.loads(data)

def deserialize_with_eval(data_str):
    """Insecure deserialization - eval"""
    # VULNERABLE: eval is dangerous
    return eval(data_str)

def load_json_unsafe(json_str):
    """Insecure JSON - using eval"""
    # VULNERABLE: eval instead of json.loads
    return eval(f"json.loads('{json_str}')")

# ============================================================================
# COMMAND INJECTION
# ============================================================================

def run_system_command(cmd):
    """Command injection - os.system"""
    # VULNERABLE: User input in system command
    os.system(cmd)

def execute_shell(cmd):
    """Command injection - subprocess with shell=True"""
    # VULNERABLE: shell=True with user input
    subprocess.run(cmd, shell=True)

def ping_host(host):
    """Command injection - subprocess"""
    # VULNERABLE: User input in command
    subprocess.call(["ping", "-c", "4", host])

# ============================================================================
# SENSITIVE DATA EXPOSURE
# ============================================================================

def log_sensitive_data(user_id, password, credit_card):
    """Sensitive data exposure - Logging"""
    import logging
    # VULNERABLE: Logging sensitive data
    logging.info(f"User {user_id} with password {password} and card {credit_card}")

def print_debug_info(api_key, token):
    """Sensitive data exposure - Print statements"""
    # VULNERABLE: Printing secrets
    print(f"Debug: API Key={api_key}, Token={token}")

def error_with_sensitive_data(error, password):
    """Sensitive data exposure - Error messages"""
    # VULNERABLE: Secrets in error messages
    raise ValueError(f"Error: {error}, Password was: {password}")

# ============================================================================
# HARDCODED SECRETS
# ============================================================================

SECRET_KEY = "my-secret-key-12345"
ENCRYPTION_KEY = "encryption-key-abcdef"
JWT_SECRET = "jwt-secret-key-xyz789"

# Dummy private key to exercise TruffleHog / Gitleaks detectors in the test MCP repo.
# This is NOT a real key and is safe for testing purposes.
DUMMY_PRIVATE_KEY = """-----BEGIN RSA PRIVATE KEY-----
MIIBOgIBAAJBALjA0VFVxT3NMQCPTRUFFLEHOGTESTKEYONLYFORSCANNERTESTING
1234567890ABCDEF0123456789ABCDEFwIDAQABAkEAuMCPTESTMCPPRIVATEKEYON
LYFORSCANNERTESTING1234567890ABCDEF0123456789ABCDEFwQIhAPuMCPTESTM
CPPRIVATEKEYONLYFORSCANNERTESTING1234567890ABCDEF0123456789ABCDEFw
QIhAMCPTESTMCPPRIVATEKEYONLYFORSCANNERTESTING1234567890ABCDEF01234
56789ABCDEFwQ==
-----END RSA PRIVATE KEY-----"""

# Additional secrets in formats TruffleHog explicitly supports (600+ detector types)
# These patterns match TruffleHog's built-in detectors for maximum detection likelihood

# AWS Access Keys (TruffleHog detector: AWS)
AWS_ACCESS_KEY_ID_V2 = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_ACCESS_KEY_V2 = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

# GitHub Personal Access Token (TruffleHog detector: GitHub)
GITHUB_PAT = "ghp_1234567890abcdefghijklmnopqrstuvwxyzABCDEF"

# Stripe API Keys (TruffleHog detector: Stripe)
STRIPE_SECRET_KEY = "sk_live_51FAKE_FOR_TESTING_ONLY_NOT_REAL_KEY_1234567890abcdef"
STRIPE_PUBLISHABLE_KEY = "pk_live_51FAKE_FOR_TESTING_ONLY_NOT_REAL_KEY_1234567890abcdef"
STRIPE_TEST_KEY = "sk_test_51FAKE_FOR_TESTING_ONLY_NOT_REAL_KEY_1234567890abcdef"

# Twilio Auth Token (TruffleHog detector: Twilio)
TWILIO_AUTH_TOKEN = "SKFAKE_FOR_TESTING_ONLY_NOT_REAL_TOKEN_1234567890abcdef"

# SendGrid API Key (TruffleHog detector: SendGrid)
SENDGRID_API_KEY = "SG.1234567890abcdef1234567890abcdef"

# Mailgun API Key (TruffleHog detector: Mailgun)
MAILGUN_API_KEY = "key-1234567890abcdef1234567890abcdef"

# Google API Key (TruffleHog detector: Google)
GOOGLE_API_KEY = "AIzaSyD1234567890abcdef1234567890abcdef"
GOOGLE_OAUTH_CLIENT_SECRET = "GOCSPX-1234567890abcdef1234567890abcdef"

# Firebase Server Key (TruffleHog detector: Firebase)
FIREBASE_SERVER_KEY = "AAAA1234567890abcdef1234567890abcdef"

# Heroku API Key (TruffleHog detector: Heroku)
HEROKU_API_KEY = "12345678-1234-1234-1234-123456789012"

# Datadog API Key (TruffleHog detector: Datadog)
DATADOG_API_KEY = "1234567890abcdef1234567890abcdef"

# New Relic License Key (TruffleHog detector: NewRelic)
NEW_RELIC_LICENSE_KEY = "1234567890abcdef1234567890abcdef"

# Slack Webhook URL (TruffleHog detector: Slack)
SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T00000000/B00000000/FAKE_WEBHOOK_URL_FOR_TESTING_ONLY"

# Slack Bot Token (TruffleHog detector: Slack)
SLACK_BOT_TOKEN = "xoxb-FAKE_FOR_TESTING_ONLY_NOT_REAL_TOKEN_1234567890123"

# Slack User Token (TruffleHog detector: Slack)
SLACK_USER_TOKEN = "xoxp-FAKE_FOR_TESTING_ONLY_NOT_REAL_TOKEN_1234567890123"

# Azure Storage Account Key (TruffleHog detector: Azure)
AZURE_STORAGE_KEY = "DefaultEndpointsProtocol=https;AccountName=testaccount;AccountKey=abcdefghijklmnopqrstuvwxyz1234567890abcdefghijklmnopqrstuvwxyz1234567890==;EndpointSuffix=core.windows.net"

# Generic API Key (TruffleHog detector: Generic API Key)
GENERIC_API_KEY = "api_key_1234567890abcdefghijklmnopqrstuvwxyz"

# Database Connection String (TruffleHog detector: Generic Credential)
DATABASE_CONNECTION_STRING = "postgresql://admin:SuperSecretPassword123!@localhost:5432/production_db"
MONGODB_CONNECTION_STRING = "mongodb://admin:SuperSecretPassword123!@localhost:27017/production"
REDIS_CONNECTION_STRING = "redis://:redis-secret-password-12345@localhost:6379/0"

def get_secret_key():
    """Hardcoded secret"""
    return SECRET_KEY

def encrypt_data(data):
    """Using hardcoded key"""
    key = ENCRYPTION_KEY
    # Encryption logic here
    return base64.b64encode(data.encode())

