import os
import json
import numpy as np
import requests
import pytest

@pytest.mark.integration
def test_model_scan_sbom(api_base, wait_api, admin_key):
    # Create a small npy file under ./data so the container sees it at /data
    host_path = os.path.abspath("data/test.npy")
    os.makedirs(os.path.dirname(host_path), exist_ok=True)
    arr = np.zeros((2,2), dtype=np.float32)
    np.save(host_path, arr)
    payload = {
        "paths": ["/data/test.npy"],
        "generate_sbom": True,
        "strict": False
    }
    r = requests.post(f"{api_base}/api/v1/models/scans", headers={"x-api-key": admin_key}, json=payload)
    assert r.status_code == 200
    body = r.json()
    assert body["gate_result"]["passed"] in (True, False)
    # Get last scan and fetch SBOM if present
    listing = requests.get(f"{api_base}/api/v1/scans?type=model&limit=1", headers={"x-api-key": admin_key}).json()
    if listing:
        scan_id = listing[0]["id"]
        sbom = requests.get(f"{api_base}/api/v1/scans/{scan_id}/sbom", headers={"x-api-key": admin_key})
        assert sbom.status_code in (200,404)
