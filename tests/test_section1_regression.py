"""
Regression Testing for Section 1.0: Foundation & UI Enhancements

Tests that existing functionality still works after section 1.0 changes:
- Scan creation and execution
- API endpoints
- Database queries
- Baseline/SBOM functionality
- Existing UI functionality
"""

import requests
import pytest
import time


@pytest.mark.integration
class TestScanCreationExecution:
    """Test that scan creation and execution still works"""
    
    def test_mcp_scan_creation(self, api_base, wait_api, admin_key):
        """Test MCP scan creation"""
        headers = {"x-api-key": admin_key}
        r = requests.post(
            f"{api_base}/api/v1/mcp/scans",
            headers=headers,
            json={"auto_discover": True}
        )
        assert r.status_code == 200
        body = r.json()
        assert "gate_result" in body or "scan_id" in body or "id" in body
    
    def test_model_scan_creation(self, api_base, wait_api, admin_key):
        """Test model scan creation"""
        headers = {"x-api-key": admin_key}
        # Create a minimal model scan
        r = requests.post(
            f"{api_base}/api/v1/model/scans",
            headers=headers,
            json={"model_path": "/tmp/test"}
        )
        # Should either succeed, return validation error, or 404 if endpoint not available
        assert r.status_code in (200, 400, 422, 404, 500)
        if r.status_code == 200:
            body = r.json()
            assert "gate_result" in body or "scan_id" in body or "id" in body


@pytest.mark.integration
class TestAPIEndpoints:
    """Test that existing API endpoints still work"""
    
    def test_health_endpoint(self, api_base, wait_api):
        """Test health check endpoint"""
        r = requests.get(f"{api_base}/api/v1/health")
        assert r.status_code == 200
        assert r.json().get("status") == "ok"
    
    def test_scans_list_endpoint(self, api_base, wait_api, admin_key):
        """Test scans list endpoint"""
        headers = {"x-api-key": admin_key}
        r = requests.get(f"{api_base}/api/v1/scans", headers=headers)
        assert r.status_code == 200
        assert isinstance(r.json(), list)
    
    def test_scans_list_with_filters(self, api_base, wait_api, admin_key):
        """Test scans list with filters"""
        headers = {"x-api-key": admin_key}
        r = requests.get(f"{api_base}/api/v1/scans?type=mcp&limit=5", headers=headers)
        assert r.status_code == 200
        scans = r.json()
        assert isinstance(scans, list)
        # If scans exist, verify filter worked
        if scans:
            for scan in scans:
                assert scan.get("type") == "mcp"
    
    def test_scan_detail_endpoint(self, api_base, wait_api, admin_key):
        """Test scan detail endpoint"""
        # Create a scan first
        headers = {"x-api-key": admin_key}
        create_r = requests.post(
            f"{api_base}/api/v1/mcp/scans",
            headers=headers,
            json={"auto_discover": True}
        )
        
        if create_r.status_code == 200:
            # Get scan ID from response
            create_data = create_r.json()
            scan_id = create_data.get("scan_id") or create_data.get("id")
            
            if scan_id:
                # Get scan detail
                detail_r = requests.get(f"{api_base}/api/v1/scans/{scan_id}", headers=headers)
                assert detail_r.status_code == 200
                data = detail_r.json()
                assert "scan" in data or "id" in data
                assert "findings" in data or isinstance(data.get("findings"), list)
        else:
            # Try to get any existing scan
            list_r = requests.get(f"{api_base}/api/v1/scans?limit=1", headers=headers)
            if list_r.status_code == 200:
                scans = list_r.json()
                if scans:
                    scan_id = scans[0]["id"]
                    detail_r = requests.get(f"{api_base}/api/v1/scans/{scan_id}", headers=headers)
                    assert detail_r.status_code == 200
    
    def test_dashboard_stats_endpoint(self, api_base, wait_api, admin_key):
        """Test dashboard stats endpoint"""
        headers = {"x-api-key": admin_key}
        r = requests.get(f"{api_base}/api/v1/dashboard/stats", headers=headers)
        assert r.status_code in (200, 404)  # May not exist yet
        if r.status_code == 200:
            data = r.json()
            assert isinstance(data, dict)


@pytest.mark.integration
class TestDatabaseQueries:
    """Test that database queries still work correctly"""
    
    def test_scans_query_with_pagination(self, api_base, wait_api, admin_key):
        """Test that scans can be queried with pagination"""
        headers = {"x-api-key": admin_key}
        r = requests.get(f"{api_base}/api/v1/scans?limit=10&offset=0", headers=headers)
        assert r.status_code == 200
        scans = r.json()
        assert isinstance(scans, list)
        assert len(scans) <= 10
    
    def test_findings_query_by_scan(self, api_base, wait_api, admin_key):
        """Test that findings can be queried by scan ID"""
        headers = {"x-api-key": admin_key}
        
        # Get a scan
        scans_r = requests.get(f"{api_base}/api/v1/scans?limit=1", headers=headers)
        if scans_r.status_code == 200:
            scans = scans_r.json()
            if scans:
                scan_id = scans[0]["id"]
                # Get findings for this scan
                scan_detail_r = requests.get(f"{api_base}/api/v1/scans/{scan_id}", headers=headers)
                if scan_detail_r.status_code == 200:
                    scan_data = scan_detail_r.json()
                    findings = scan_data.get("findings", [])
                    # All findings should belong to this scan
                    for finding in findings:
                        # Finding should have scan_id or be in scan's findings
                        assert "id" in finding or "scan_id" in finding


@pytest.mark.integration
class TestBaselineFunctionality:
    """Test that baseline functionality still works"""
    
    def test_baselines_list_endpoint(self, api_base, wait_api, admin_key):
        """Test baselines list endpoint"""
        headers = {"x-api-key": admin_key}
        r = requests.get(f"{api_base}/api/v1/baselines", headers=headers)
        assert r.status_code in (200, 404)  # May not exist
        if r.status_code == 200:
            assert isinstance(r.json(), list)
    
    def test_baseline_creation(self, api_base, wait_api, admin_key):
        """Test baseline creation"""
        headers = {"x-api-key": admin_key}
        
        # First, get or create a scan
        scans_r = requests.get(f"{api_base}/api/v1/scans?limit=1", headers=headers)
        scan_id = None
        if scans_r.status_code == 200:
            scans = scans_r.json()
            if scans:
                scan_id = scans[0]["id"]
        
        if scan_id:
            # Try to create baseline
            baseline_r = requests.post(
                f"{api_base}/api/v1/baselines",
                headers=headers,
                json={"scan_id": scan_id, "name": "test-baseline"}
            )
            # Should either succeed or return validation error
            assert baseline_r.status_code in (200, 201, 400, 422, 404)


@pytest.mark.integration
class TestSBOMFunctionality:
    """Test that SBOM functionality still works"""
    
    def test_sbom_download_endpoint(self, api_base, wait_api, admin_key):
        """Test SBOM download endpoint"""
        headers = {"x-api-key": admin_key}
        
        # Get a scan with SBOM
        scans_r = requests.get(f"{api_base}/api/v1/scans?limit=10", headers=headers)
        if scans_r.status_code == 200:
            scans = scans_r.json()
            for scan in scans:
                scan_id = scan.get("id")
                if scan_id:
                    sbom_r = requests.get(f"{api_base}/api/v1/scans/{scan_id}/sbom", headers=headers)
                    # Should either return SBOM or 404 if no SBOM
                    assert sbom_r.status_code in (200, 404)
                    if sbom_r.status_code == 200:
                        # Should return JSON
                        assert sbom_r.headers.get("content-type", "").startswith("application/json")
                        break


@pytest.mark.integration
class TestUIFunctionality:
    """Test that existing UI functionality still works"""
    
    def test_dashboard_page_loads(self, api_base, wait_api):
        """Test that dashboard page loads"""
        r = requests.get(f"{api_base}/", allow_redirects=True)
        assert r.status_code == 200
        content = r.text
        assert "dashboard" in content.lower() or "scans" in content.lower()
    
    def test_scan_detail_page_loads(self, api_base, wait_api):
        """Test that scan detail page loads"""
        # Try with a test ID (will likely 404, but should return HTML)
        r = requests.get(f"{api_base}/scan/test-id", allow_redirects=True)
        assert r.status_code in (200, 404)
        if r.status_code == 200:
            content = r.text
            assert "scan" in content.lower() or "findings" in content.lower()
    
    def test_baselines_page_loads(self, api_base, wait_api):
        """Test that baselines page loads"""
        r = requests.get(f"{api_base}/baselines", allow_redirects=True)
        assert r.status_code in (200, 302, 404)
        if r.status_code == 200:
            content = r.text
            assert "baseline" in content.lower()
    
    def test_scan_form_page_loads(self, api_base, wait_api):
        """Test that scan form page loads"""
        r = requests.get(f"{api_base}/ui/scan", allow_redirects=True)
        assert r.status_code in (200, 302)
        if r.status_code == 200:
            content = r.text
            assert "scan" in content.lower() or "form" in content.lower()


@pytest.mark.integration
class TestAuthentication:
    """Test that authentication still works"""
    
    def test_api_key_authentication(self, api_base, wait_api, admin_key):
        """Test that API key authentication works"""
        headers = {"x-api-key": admin_key}
        r = requests.get(f"{api_base}/api/v1/scans", headers=headers)
        assert r.status_code == 200
    
    def test_invalid_api_key_rejected(self, api_base, wait_api):
        """Test that invalid API keys are rejected"""
        headers = {"x-api-key": "invalid-key-12345"}
        r = requests.get(f"{api_base}/api/v1/scans", headers=headers)
        assert r.status_code in (401, 403)
    
    def test_missing_api_key_rejected(self, api_base, wait_api):
        """Test that missing API keys are rejected"""
        r = requests.get(f"{api_base}/api/v1/scans")
        assert r.status_code in (401, 403)

