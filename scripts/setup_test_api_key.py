#!/usr/bin/env python3
"""
Script to create a test API key for performance testing.
Usage: python scripts/setup_test_api_key.py
"""

import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sentrascan.core.storage import SessionLocal, init_db
from sentrascan.core.models import Tenant, User, APIKey
from sentrascan.core.auth import create_user

# Import generate_api_key from server
from sentrascan.server import generate_api_key

def setup_test_api_key():
    """Create a test API key for performance testing"""
    db = SessionLocal()
    try:
        # Get or create test tenant
        tenant = db.query(Tenant).filter(Tenant.name == "test-tenant").first()
        if not tenant:
            tenant = Tenant(id="test-tenant-id", name="test-tenant", is_active=True)
            db.add(tenant)
            db.commit()
            print(f"Created tenant: {tenant.id}")
        else:
            print(f"Using existing tenant: {tenant.id}")
        
        # Get or create test user
        user = db.query(User).filter(User.email == "test-admin@test.com").first()
        if not user:
            user = create_user(
                db,
                email="test-admin@test.com",
                password="TestPassword123!",
                name="Test Admin",
                tenant_id=tenant.id,
                role="tenant_admin"
            )
            print(f"Created user: {user.email}")
        else:
            print(f"Using existing user: {user.email}")
        
        # Delete existing test API keys
        existing_keys = db.query(APIKey).filter(
            APIKey.name == "test-api-perf-key",
            APIKey.tenant_id == tenant.id
        ).all()
        for key in existing_keys:
            db.delete(key)
        db.commit()
        
        # Create new API key
        new_key = generate_api_key()
        key_hash = APIKey.hash_key(new_key)
        api_key_record = APIKey(
            name="test-api-perf-key",
            key_hash=key_hash,
            role="tenant_admin",
            tenant_id=tenant.id,
            user_id=user.id,
            is_revoked=False
        )
        db.add(api_key_record)
        db.commit()
        
        print(f"\n✅ Test API key created successfully!")
        print(f"API Key: {new_key}")
        print(f"\nTo use this key, set:")
        print(f"export SENTRASCAN_API_KEY='{new_key}'")
        print(f"export SENTRASCAN_TEST_API_KEY='{new_key}'")
        
        return new_key
    except Exception as e:
        print(f"❌ Error creating API key: {e}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    key = setup_test_api_key()
    if key:
        sys.exit(0)
    else:
        sys.exit(1)

