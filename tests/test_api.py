import requests
import pytest

@pytest.mark.integration
def test_health_ok(api_base, wait_api):
    r = requests.get(f"{api_base}/api/v1/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

@pytest.mark.integration
def test_rbac_viewer_forbidden(api_base, wait_api, viewer_key):
    r = requests.post(f"{api_base}/api/v1/mcp/scans", headers={"x-api-key": viewer_key}, json={"auto_discover": True})
    assert r.status_code in (401,403)

@pytest.mark.integration
def test_rbac_admin_allowed(api_base, wait_api, admin_key):
    r = requests.post(f"{api_base}/api/v1/mcp/scans", headers={"x-api-key": admin_key}, json={"auto_discover": True})
    assert r.status_code == 200
    body = r.json()
    assert "gate_result" in body

@pytest.mark.integration
def test_scans_filters(api_base, wait_api, admin_key):
    r = requests.get(f"{api_base}/api/v1/scans?type=mcp&limit=5", headers={"x-api-key": admin_key})
    assert r.status_code == 200
    assert isinstance(r.json(), list)

@pytest.mark.integration
def test_scan_detail(api_base, wait_api, admin_key):
    # Ensure at least one scan exists
    requests.post(f"{api_base}/api/v1/mcp/scans", headers={"x-api-key": admin_key}, json={"auto_discover": True})
    listing = requests.get(f"{api_base}/api/v1/scans?limit=1", headers={"x-api-key": admin_key}).json()
    if not listing:
        pytest.skip("no scans present")
    scan_id = listing[0]["id"]
    detail = requests.get(f"{api_base}/api/v1/scans/{scan_id}", headers={"x-api-key": admin_key})
    assert detail.status_code == 200
    data = detail.json()
    assert "scan" in data and "findings" in data
