"""
API Performance Tests for SentraScan Platform.

These tests require the API server to be running (via Docker).
Run: docker compose up -d
Then: pytest tests/test_api_performance.py -v
"""

import pytest
import requests
import time
import statistics
from typing import List, Dict, Any
import os

API_BASE = os.environ.get("SENTRASCAN_API_BASE", "http://localhost:8200")
API_RESPONSE_TIME_TARGET_MS = 200  # 95th percentile target

# Wait for API to be ready
def wait_for_api(max_wait=60):
    """Wait for API server to be ready"""
    deadline = time.time() + max_wait
    while time.time() < deadline:
        try:
            response = requests.get(f"{API_BASE}/api/v1/health", timeout=2)
            if response.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


def measure_response_time(url: str, headers: Dict[str, str] = None) -> float:
    """Measure response time in milliseconds"""
    start = time.perf_counter()
    try:
        response = requests.get(url, headers=headers, timeout=10)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return elapsed_ms, response.status_code
    except Exception as e:
        elapsed_ms = (time.perf_counter() - start) * 1000
        return elapsed_ms, None


def percentile(data: List[float], percentile: float) -> float:
    """Calculate percentile of a list of values"""
    if not data:
        return 0.0
    sorted_data = sorted(data)
    index = int(len(sorted_data) * percentile / 100)
    return sorted_data[min(index, len(sorted_data) - 1)]


@pytest.fixture(scope="session")
def api_ready():
    """Ensure API is ready before running tests"""
    if not wait_for_api():
        pytest.skip("API server not ready. Start with: docker compose up -d")
    return True


@pytest.fixture(scope="session")
def test_api_key(api_ready):
    """Create or get a test API key"""
    # Try to get from environment first
    test_key = os.environ.get("SENTRASCAN_TEST_API_KEY")
    if test_key:
        return test_key
    
    # Try to use admin_key from conftest
    try:
        from tests.conftest import admin_key
        # This will create the key via the fixture
        # We need to call it differently - let's create it directly
        from sentrascan.core.storage import SessionLocal
        from sentrascan.core.models import Tenant, User, APIKey
        from sentrascan.core.auth import create_user
        from sentrascan.core.models import generate_api_key
        
        db = SessionLocal()
        try:
            # Get or create test tenant
            tenant = db.query(Tenant).filter(Tenant.name == "test-tenant").first()
            if not tenant:
                tenant = Tenant(id="test-tenant-id", name="test-tenant", is_active=True)
                db.add(tenant)
                db.commit()
            
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
            
            # Get or create API key
            api_key_record = db.query(APIKey).filter(
                APIKey.name == "test-api-perf-key",
                APIKey.tenant_id == tenant.id
            ).first()
            
            if api_key_record:
                # Key exists but we can't get plaintext, create new one
                db.delete(api_key_record)
                db.commit()
            
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
            return new_key
        finally:
            db.close()
    except Exception as e:
        pytest.skip(f"Could not create test API key: {e}")


@pytest.fixture
def api_headers(test_api_key):
    """Get API headers with authentication"""
    return {
        "X-API-Key": test_api_key,
        "Content-Type": "application/json"
    }


class TestAPIResponseTime:
    """Test API response time targets"""
    
    def test_health_endpoint_response_time(self, api_ready):
        """Test /api/v1/health endpoint response time"""
        times = []
        for _ in range(50):
            elapsed_ms, status_code = measure_response_time(f"{API_BASE}/api/v1/health")
            if status_code == 200:
                times.append(elapsed_ms)
        
        if not times:
            pytest.fail("Health endpoint not responding")
        
        avg_time = statistics.mean(times)
        p95 = percentile(times, 95)
        
        assert p95 < API_RESPONSE_TIME_TARGET_MS, \
            f"95th percentile response time {p95:.2f}ms exceeds target {API_RESPONSE_TIME_TARGET_MS}ms"
        assert avg_time < API_RESPONSE_TIME_TARGET_MS * 0.7, \
            f"Average response time {avg_time:.2f}ms should be <{API_RESPONSE_TIME_TARGET_MS * 0.7}ms"
    
    def test_scans_endpoint_response_time(self, api_ready, api_headers):
        """Test /api/v1/scans endpoint response time"""
        times = []
        status_codes = []
        
        for _ in range(30):
            elapsed_ms, status_code = measure_response_time(
                f"{API_BASE}/api/v1/scans",
                headers=api_headers
            )
            times.append(elapsed_ms)
            if status_code:
                status_codes.append(status_code)
        
        if not times:
            pytest.fail("Scans endpoint not responding")
        
        # Accept 200, 401 (auth required), or 403 (forbidden)
        valid_responses = [s for s in status_codes if s in [200, 401, 403]]
        if not valid_responses:
            pytest.skip(f"Scans endpoint returned unexpected status codes: {set(status_codes)}")
        
        avg_time = statistics.mean(times)
        p95 = percentile(times, 95)
        
        assert p95 < API_RESPONSE_TIME_TARGET_MS, \
            f"95th percentile response time {p95:.2f}ms exceeds target {API_RESPONSE_TIME_TARGET_MS}ms"
    
    def test_findings_endpoint_response_time(self, api_ready, api_headers):
        """Test /api/v1/findings endpoint response time"""
        times = []
        status_codes = []
        
        for _ in range(30):
            elapsed_ms, status_code = measure_response_time(
                f"{API_BASE}/api/v1/findings",
                headers=api_headers
            )
            times.append(elapsed_ms)
            if status_code:
                status_codes.append(status_code)
        
        if not times:
            pytest.fail("Findings endpoint not responding")
        
        valid_responses = [s for s in status_codes if s in [200, 401, 403]]
        if not valid_responses:
            pytest.skip(f"Findings endpoint returned unexpected status codes: {set(status_codes)}")
        
        avg_time = statistics.mean(times)
        p95 = percentile(times, 95)
        
        assert p95 < API_RESPONSE_TIME_TARGET_MS, \
            f"95th percentile response time {p95:.2f}ms exceeds target {API_RESPONSE_TIME_TARGET_MS}ms"
    
    def test_api_keys_endpoint_response_time(self, api_ready, api_headers):
        """Test /api/v1/api-keys endpoint response time"""
        times = []
        status_codes = []
        
        for _ in range(30):
            elapsed_ms, status_code = measure_response_time(
                f"{API_BASE}/api/v1/api-keys",
                headers=api_headers
            )
            times.append(elapsed_ms)
            if status_code:
                status_codes.append(status_code)
        
        if not times:
            pytest.fail("API keys endpoint not responding")
        
        valid_responses = [s for s in status_codes if s in [200, 401, 403]]
        if not valid_responses:
            pytest.skip(f"API keys endpoint returned unexpected status codes: {set(status_codes)}")
        
        avg_time = statistics.mean(times)
        p95 = percentile(times, 95)
        
        assert p95 < API_RESPONSE_TIME_TARGET_MS, \
            f"95th percentile response time {p95:.2f}ms exceeds target {API_RESPONSE_TIME_TARGET_MS}ms"
    
    def test_dashboard_stats_endpoint_response_time(self, api_ready, api_headers):
        """Test /api/v1/dashboard/stats endpoint response time"""
        times = []
        status_codes = []
        
        for _ in range(30):
            elapsed_ms, status_code = measure_response_time(
                f"{API_BASE}/api/v1/dashboard/stats",
                headers=api_headers
            )
            times.append(elapsed_ms)
            if status_code:
                status_codes.append(status_code)
        
        if not times:
            pytest.fail("Dashboard stats endpoint not responding")
        
        valid_responses = [s for s in status_codes if s in [200, 401, 403]]
        if not valid_responses:
            pytest.skip(f"Dashboard stats endpoint returned unexpected status codes: {set(status_codes)}")
        
        avg_time = statistics.mean(times)
        p95 = percentile(times, 95)
        
        assert p95 < API_RESPONSE_TIME_TARGET_MS, \
            f"95th percentile response time {p95:.2f}ms exceeds target {API_RESPONSE_TIME_TARGET_MS}ms"


class TestAPIConcurrentLoad:
    """Test API under concurrent load"""
    
    def test_concurrent_requests(self, api_ready, api_headers):
        """Test API handles concurrent requests"""
        import threading
        
        results = []
        errors = []
        
        def make_request():
            try:
                elapsed_ms, status_code = measure_response_time(
                    f"{API_BASE}/api/v1/health",
                    headers={}
                )
                results.append((elapsed_ms, status_code))
            except Exception as e:
                errors.append(str(e))
        
        # Create 20 concurrent requests
        threads = []
        for _ in range(20):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        assert len(results) > 0, f"No successful responses. Errors: {errors}"
        assert len(errors) == 0, f"Errors occurred: {errors}"
        
        # Verify response times are reasonable
        times = [r[0] for r in results]
        avg_time = statistics.mean(times)
        assert avg_time < API_RESPONSE_TIME_TARGET_MS * 2, \
            f"Average concurrent response time {avg_time:.2f}ms exceeds reasonable limit"

