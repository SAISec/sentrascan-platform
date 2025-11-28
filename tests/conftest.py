import os
import time
import subprocess
import requests
import pytest
import uuid
from datetime import datetime
from sentrascan.core.storage import SessionLocal
from sentrascan.core.models import Tenant, User, APIKey, Scan, Finding, Baseline, SBOM
from sentrascan.core.auth import create_user, PasswordHasher
from sentrascan.server import generate_api_key

API_BASE = os.environ.get("SENTRASCAN_API_BASE", "http://localhost:8200")
SESSION_COOKIE_NAME = os.environ.get("SENTRASCAN_SESSION_COOKIE", "ss_session")

@pytest.fixture(scope="session")
def wait_api():
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            r = requests.get(f"{API_BASE}/api/v1/health", timeout=2)
            if r.ok and r.json().get("status") == "ok":
                return
        except Exception:
            pass
        time.sleep(1)
    pytest.skip("API not ready at {API_BASE}")

@pytest.fixture(scope="session")
def test_tenant(wait_api):
    """Create a test tenant for API key creation"""
    try:
        db = SessionLocal()
        # Check if test tenant exists
        tenant = db.query(Tenant).filter(Tenant.name == "test-tenant").first()
        if not tenant:
            tenant = Tenant(
                id="test-tenant-id",
                name="test-tenant",
                is_active=True
            )
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
        db.close()
        return tenant
    except Exception as e:
        pytest.skip(f"Could not create test tenant: {e}")

@pytest.fixture(scope="session")
def test_admin_user(wait_api, test_tenant):
    """Create a test admin user for API key creation"""
    try:
        db = SessionLocal()
        # Check if test admin user exists
        user = db.query(User).filter(User.email == "test-admin@test.com").first()
        if not user:
            user = create_user(
                db,
                email="test-admin@test.com",
                password="TestPassword123!",
                name="Test Admin",
                tenant_id=test_tenant.id,
                role="tenant_admin"
            )
        db.close()
        return user
    except Exception as e:
        pytest.skip(f"Could not create test admin user: {e}")

@pytest.fixture(scope="session")
def admin_key(wait_api, test_tenant, test_admin_user):
    """Create an admin API key directly in database"""
    env_key = os.environ.get("SENTRASCAN_ADMIN_KEY")
    if env_key:
        return env_key
    
    try:
        db = SessionLocal()
        # Check if key already exists
        existing_key = db.query(APIKey).filter(
            APIKey.name == "test-admin-key",
            APIKey.tenant_id == test_tenant.id
        ).first()
        
        if existing_key:
            # Return existing key (we can't get plaintext, so generate a new one)
            db.close()
            # Create new key for testing
            new_key = generate_api_key()
            key_hash = APIKey.hash_key(new_key)
            db = SessionLocal()
            api_key_record = APIKey(
                name="test-admin-key-new",
                key_hash=key_hash,
                role="tenant_admin",
                tenant_id=test_tenant.id,
                user_id=test_admin_user.id,
                is_revoked=False
            )
            db.add(api_key_record)
            db.commit()
            db.close()
            return new_key
        
        # Create new API key
        new_key = generate_api_key()
        key_hash = APIKey.hash_key(new_key)
        api_key_record = APIKey(
            name="test-admin-key",
            key_hash=key_hash,
            role="tenant_admin",
            tenant_id=test_tenant.id,
            user_id=test_admin_user.id,
            is_revoked=False
        )
        db.add(api_key_record)
        db.commit()
        db.close()
        return new_key
    except Exception as e:
        pytest.skip(f"Could not create admin key: {e}")

@pytest.fixture(scope="session")
def viewer_key(wait_api, test_tenant):
    """Create a viewer API key"""
    env_key = os.environ.get("SENTRASCAN_VIEWER_KEY")
    if env_key:
        return env_key
    
    try:
        # Create viewer user
        db = SessionLocal()
        viewer_user = db.query(User).filter(User.email == "test-viewer@test.com").first()
        if not viewer_user:
            viewer_user = create_user(
                db,
                email="test-viewer@test.com",
                password="TestPassword123!",
                name="Test Viewer",
                tenant_id=test_tenant.id,
                role="viewer"
            )
        
        # Create API key directly in database
        new_key = generate_api_key()
        key_hash = APIKey.hash_key(new_key)
        api_key_record = APIKey(
            name="test-viewer-key",
            key_hash=key_hash,
            role="viewer",
            tenant_id=test_tenant.id,
            user_id=viewer_user.id,
            is_revoked=False
        )
        db.add(api_key_record)
        db.commit()
        db.close()
        return new_key
    except Exception as e:
        pytest.skip(f"Could not create viewer key: {e}")

@pytest.fixture(scope="session")
def api_base():
    return API_BASE
