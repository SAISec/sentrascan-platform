import requests
import pytest

@pytest.mark.integration
def test_login_and_scan_forms(api_base, wait_api, admin_key):
    s = requests.Session()
    # login
    r = s.post(f"{api_base}/login", data={"api_key": admin_key}, allow_redirects=False)
    assert r.status_code in (302,303)
    # load dashboard
    r = s.get(f"{api_base}/")
    assert r.status_code == 200
    assert "Recent Scans" in r.text
    # load scan forms (admin only)
    r = s.get(f"{api_base}/ui/scan")
    assert r.status_code == 200
    assert "Model Scan" in r.text or "MCP Scan" in r.text
