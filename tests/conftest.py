import os
import time
import subprocess
import requests
import pytest

API_BASE = os.environ.get("SENTRASCAN_API_BASE", "http://localhost:8200")

@pytest.fixture(scope="session")
def wait_api():
    deadline = time.time() + 60
    while time.time() < deadline:
        try:
            r = requests.get(f"{API_BASE}/api/v1/health", timeout=2)
            if r.ok and r.json().get("status") == "ok":
                return
        except Exception:
            pass
        time.sleep(1)
    pytest.skip("API not ready at {API_BASE}")

@pytest.fixture(scope="session")
def admin_key(wait_api):
    env_key = os.environ.get("SENTRASCAN_ADMIN_KEY")
    if env_key:
        return env_key
    # Check if running inside Docker (check for /app directory which is Docker WORKDIR)
    if os.path.exists("/app"):
        # Running inside Docker - use sentrascan CLI directly
        out = subprocess.check_output(
            ["sentrascan", "auth", "create", "--name", "test-admin", "--role", "admin"],
            text=True, stderr=subprocess.STDOUT
        ).strip()
        # Extract key from output (last line)
        key = out.split("\n")[-1].strip()
    else:
        # Running on host - use docker compose
        cmd = ["bash", "-lc", "docker compose exec -T api sh -lc 'sentrascan auth create --name test-admin --role admin | tail -1' "]
        key = subprocess.check_output(" ".join(cmd), shell=True, text=True).strip()
    assert key, "Failed to create admin key"
    return key

@pytest.fixture(scope="session")
def viewer_key(wait_api):
    env_key = os.environ.get("SENTRASCAN_VIEWER_KEY")
    if env_key:
        return env_key
    # Check if running inside Docker
    if os.path.exists("/app"):
        # Running inside Docker - use sentrascan CLI directly
        out = subprocess.check_output(
            ["sentrascan", "auth", "create", "--name", "test-viewer", "--role", "viewer"],
            text=True, stderr=subprocess.STDOUT
        ).strip()
        # Extract key from output (last line)
        key = out.split("\n")[-1].strip()
    else:
        # Running on host - use docker compose
        cmd = ["bash", "-lc", "docker compose exec -T api sh -lc 'sentrascan auth create --name test-viewer --role viewer | tail -1' "]
        key = subprocess.check_output(" ".join(cmd), shell=True, text=True).strip()
    assert key, "Failed to create viewer key"
    return key

@pytest.fixture(scope="session")
def api_base():
    return API_BASE
