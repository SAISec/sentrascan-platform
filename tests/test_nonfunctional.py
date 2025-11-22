import requests
import pytest
from concurrent.futures import ThreadPoolExecutor, as_completed

@pytest.mark.integration
@pytest.mark.timeout(300)
def test_concurrent_scans(api_base, wait_api, admin_key):
    def run_one():
        return requests.post(f"{api_base}/api/v1/mcp/scans", headers={"x-api-key": admin_key}, json={"auto_discover": True}).status_code
    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = [ex.submit(run_one) for _ in range(3)]
        statuses = [f.result() for f in as_completed(futs)]
    assert all(s == 200 for s in statuses)
