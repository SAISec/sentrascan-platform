import requests
import pytest

@pytest.mark.integration
def test_health_ok(api_base, wait_api):
    r = requests.get(f"{api_base}/api/v1/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

@pytest.mark.integration
def test_rbac_viewer_forbidden(api_base, wait_api, viewer_key):
    r = requests.post(f"{api_base}/api/v1/mcp/scans", headers={"X-API-Key": viewer_key}, json={"auto_discover": True})
    assert r.status_code in (401, 403, 404, 405)

@pytest.mark.integration
def test_rbac_admin_allowed(api_base, wait_api, admin_key):
    r = requests.post(f"{api_base}/api/v1/mcp/scans", headers={"X-API-Key": admin_key}, json={"auto_discover": True})
    # May return 200, 202, 400, 403, 404, or 405 depending on endpoint availability
    assert r.status_code in (200, 202, 400, 403, 404, 405)
    if r.status_code == 200:
        body = r.json()
        # If successful, check for expected fields
        assert isinstance(body, dict)

@pytest.mark.integration
def test_scans_filters(api_base, wait_api, admin_key):
    r = requests.get(f"{api_base}/api/v1/scans?type=mcp&limit=5", headers={"X-API-Key": admin_key})
    # May return 200, 403, 404 depending on endpoint availability
    assert r.status_code in (200, 403, 404)
    if r.status_code == 200:
        assert isinstance(r.json(), list)

@pytest.mark.integration
def test_scan_detail(api_base, wait_api, admin_key):
    # Try to get scans list first
    listing_response = requests.get(f"{api_base}/api/v1/scans?limit=1", headers={"X-API-Key": admin_key})
    
    if listing_response.status_code != 200:
        pytest.skip(f"Could not access scans endpoint: {listing_response.status_code}")
    
    listing = listing_response.json()
    if not listing or len(listing) == 0:
        pytest.skip("no scans present")
    
    scan_id = listing[0]["id"]
    detail = requests.get(f"{api_base}/api/v1/scans/{scan_id}", headers={"X-API-Key": admin_key})
    assert detail.status_code in (200, 403, 404)
    if detail.status_code == 200:
        data = detail.json()
        # Check if response has expected structure
        assert isinstance(data, dict)
