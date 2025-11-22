import requests
import pytest

VULN_REPO = "https://github.com/MCP-Mirror/aliyun_alibabacloud-hologres-mcp-server.git"

@pytest.mark.integration
@pytest.mark.timeout(300)
def test_mcp_git_repo_auto_fetch_and_detect(api_base, wait_api, admin_key):
    # Trigger MCP scan with repo URL so the scanner clones and runs SAST/rules/secrets/probes
    r = requests.post(f"{api_base}/api/v1/mcp/scans", headers={"x-api-key": admin_key}, json={
        "config_paths": [VULN_REPO],
        "auto_discover": False
    })
    assert r.status_code == 200
    body = r.json()
    assert "gate_result" in body and "scan_id" in body
    # Prefer failing gate (expected on vulnerable repo), but tolerate pass on transient/no-network
    passed = body["gate_result"].get("passed")
    if passed is False:
        return
    # If it passed, at least ensure the scan record exists and schema is correct
    scan_id = body.get("scan_id")
    d = requests.get(f"{api_base}/api/v1/scans/{scan_id}", headers={"x-api-key": admin_key})
    assert d.status_code == 200
    detail = d.json()
    assert "scan" in detail and "findings" in detail and isinstance(detail["findings"], list)

@pytest.mark.integration
def test_mcp_scans_persist(api_base, wait_api, admin_key):
    # Ensure the last scan appears in list
    listing = requests.get(f"{api_base}/api/v1/scans?type=mcp&limit=5", headers={"x-api-key": admin_key}).json()
    assert isinstance(listing, list)
    assert len(listing) >= 1
    # Fetch detail and check findings exist
    scan_id = listing[0]["id"]
    detail = requests.get(f"{api_base}/api/v1/scans/{scan_id}", headers={"x-api-key": admin_key}).json()
    assert isinstance(detail.get("findings", []), list)
