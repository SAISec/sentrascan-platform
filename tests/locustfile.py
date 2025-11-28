"""
Locust load testing file for SentraScan Platform API endpoints.

To run:
    locust -f tests/locustfile.py --host=http://localhost:8200

Then open http://localhost:8089 in your browser to start the load test.

Targets:
- 1000+ concurrent requests to /api/v1/scans
- 1000+ concurrent requests to /api/v1/findings
- 1000+ concurrent requests to /api/v1/api-keys
- Verify API response time <200ms (95th percentile)
"""

import os
import random
from locust import HttpUser, task, between
from locust.contrib.fasthttp import FastHttpUser

# Get API key from environment or use default test key
API_KEY = os.environ.get("SENTRASCAN_API_KEY", "test-api-key")
API_BASE = os.environ.get("SENTRASCAN_API_BASE", "http://localhost:8200")


class SentraScanAPIUser(HttpUser):
    """Load test user for SentraScan API endpoints"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def on_start(self):
        """Set up user session"""
        self.headers = {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
    
    @task(3)
    def get_scans(self):
        """Test GET /api/v1/scans endpoint"""
        with self.client.get(
            "/api/v1/scans",
            headers=self.headers,
            name="GET /api/v1/scans",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("Authentication failed")
            else:
                response.failure(f"Unexpected status: {response.status_code}")
    
    @task(3)
    def get_findings(self):
        """Test GET /api/v1/findings endpoint"""
        with self.client.get(
            "/api/v1/findings",
            headers=self.headers,
            name="GET /api/v1/findings",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("Authentication failed")
            else:
                response.failure(f"Unexpected status: {response.status_code}")
    
    @task(2)
    def get_api_keys(self):
        """Test GET /api/v1/api-keys endpoint"""
        with self.client.get(
            "/api/v1/api-keys",
            headers=self.headers,
            name="GET /api/v1/api-keys",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("Authentication failed")
            else:
                response.failure(f"Unexpected status: {response.status_code}")
    
    @task(1)
    def get_scan_detail(self):
        """Test GET /api/v1/scans/{scan_id} endpoint"""
        # Use a test scan ID (would need to be created beforehand)
        scan_id = os.environ.get("TEST_SCAN_ID", "test-scan-id")
        with self.client.get(
            f"/api/v1/scans/{scan_id}",
            headers=self.headers,
            name="GET /api/v1/scans/{scan_id}",
            catch_response=True
        ) as response:
            if response.status_code in [200, 404]:
                response.success()
            elif response.status_code == 401:
                response.failure("Authentication failed")
            else:
                response.failure(f"Unexpected status: {response.status_code}")
    
    @task(1)
    def get_dashboard_stats(self):
        """Test GET /api/v1/dashboard/stats endpoint"""
        with self.client.get(
            "/api/v1/dashboard/stats",
            headers=self.headers,
            name="GET /api/v1/dashboard/stats",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 401:
                response.failure("Authentication failed")
            else:
                response.failure(f"Unexpected status: {response.status_code}")
    
    @task(1)
    def get_health(self):
        """Test GET /api/v1/health endpoint"""
        with self.client.get(
            "/api/v1/health",
            headers=self.headers,
            name="GET /api/v1/health",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Unexpected status: {response.status_code}")


class FastSentraScanAPIUser(FastHttpUser):
    """Fast HTTP user for higher concurrency (uses gevent)"""
    
    wait_time = between(0.5, 2)
    
    def on_start(self):
        """Set up user session"""
        self.headers = {
            "X-API-Key": API_KEY,
            "Content-Type": "application/json"
        }
    
    @task(3)
    def get_scans(self):
        """Test GET /api/v1/scans endpoint"""
        self.client.get(
            "/api/v1/scans",
            headers=self.headers,
            name="GET /api/v1/scans (fast)"
        )
    
    @task(3)
    def get_findings(self):
        """Test GET /api/v1/findings endpoint"""
        self.client.get(
            "/api/v1/findings",
            headers=self.headers,
            name="GET /api/v1/findings (fast)"
        )
    
    @task(2)
    def get_api_keys(self):
        """Test GET /api/v1/api-keys endpoint"""
        self.client.get(
            "/api/v1/api-keys",
            headers=self.headers,
            name="GET /api/v1/api-keys (fast)"
        )


# Configuration for load testing
# Run with: locust -f tests/locustfile.py --host=http://localhost:8200 --users=1000 --spawn-rate=100

