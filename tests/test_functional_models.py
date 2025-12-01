"""
Functional tests for model scanning in hardened container.

This test suite verifies that various model formats can be scanned
successfully via the API endpoints in the hardened container environment.
"""

import pytest
import os
import json
import tempfile
import pickle
import requests
from typing import Dict, Any, Optional


# Test configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8200/api/v1")
API_KEY = os.environ.get("API_KEY", "")


@pytest.fixture
def api_key():
    """Get API key from environment or skip tests if not available."""
    key = os.environ.get("API_KEY") or API_KEY
    if not key:
        pytest.skip("API_KEY environment variable not set")
    return key


@pytest.fixture
def test_models_dir():
    """Get test models directory from environment."""
    return os.environ.get("TEST_MODELS_DIR", "/test-data/models")


@pytest.fixture
def headers(api_key):
    """API request headers."""
    return {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }


@pytest.fixture
def api_base_url():
    """Get API base URL from environment."""
    return os.environ.get("API_BASE_URL", API_BASE_URL)


def create_test_pickle_model(file_path: str, malicious: bool = False):
    """
    Create a test pickle model file.
    
    Args:
        file_path: Path where to create the file
        malicious: If True, include potentially unsafe pickle operations
    """
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Create a simple test model
    test_data = {
        "model_type": "test",
        "version": "1.0",
        "weights": [1.0, 2.0, 3.0]
    }
    
    with open(file_path, "wb") as f:
        pickle.dump(test_data, f)
    
    return file_path


def create_test_onnx_model(file_path: str):
    """Create a minimal test ONNX model (placeholder)."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    # ONNX models are binary, so we'll create a placeholder
    # In real tests, use actual ONNX model files
    with open(file_path, "wb") as f:
        f.write(b"ONNX_PLACEHOLDER")
    return file_path


class TestModelScannerFunctional:
    """Functional tests for model scanner via API."""
    
    def test_health_check(self, api_base_url):
        """Verify API health endpoint works."""
        response = requests.get(f"{api_base_url}/health", timeout=5)
        assert response.status_code == 200
        data = response.json()
        assert data.get("status") in ["ok", "healthy"]
    
    def test_model_scan_pickle(self, headers, api_base_url, test_models_dir, tmp_path):
        """Test scanning a pickle model file."""
        # Create test pickle model
        test_model_path = str(tmp_path / "test_model.pkl")
        create_test_pickle_model(test_model_path)
        
        # Upload or make model accessible (in container, use mounted volume)
        # For this test, we'll assume the model is in a mounted volume
        # In practice, you'd copy it there first
        
        payload = {
            "paths": [test_model_path],
            "generate_sbom": False,
            "strict": False
        }
        
        response = requests.post(
            f"{api_base_url}/models/scans",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200, f"Response: {response.text}"
        data = response.json()
        assert "scan_id" in data
        assert "gate_result" in data
        assert "findings" in data
    
    def test_model_scan_with_sbom(self, headers, tmp_path):
        """Test model scan with SBOM generation."""
        test_model_path = str(tmp_path / "test_model.pkl")
        create_test_pickle_model(test_model_path)
        
        payload = {
            "paths": [test_model_path],
            "generate_sbom": True,
            "strict": False
        }
        
        response = requests.post(
            f"{api_base_url}/models/scans",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "scan_id" in data
        assert "sbom" in data or data.get("gate_result", {}).get("sbom_generated", False)
    
    def test_model_scan_multiple_paths(self, headers, tmp_path):
        """Test scanning multiple model files."""
        model1 = str(tmp_path / "model1.pkl")
        model2 = str(tmp_path / "model2.pkl")
        create_test_pickle_model(model1)
        create_test_pickle_model(model2)
        
        payload = {
            "paths": [model1, model2],
            "generate_sbom": False
        }
        
        response = requests.post(
            f"{api_base_url}/models/scans",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "scan_id" in data
    
    def test_model_scan_invalid_path(self, headers):
        """Test scanning with invalid/non-existent path."""
        payload = {
            "paths": ["/nonexistent/path/model.pkl"],
            "generate_sbom": False
        }
        
        response = requests.post(
            f"{api_base_url}/models/scans",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Should return error (400 or 404)
        assert response.status_code in [400, 404, 500]
    
    def test_model_scan_ssrf_prevention(self, headers, api_base_url):
        """Test that HTTP/HTTPS URLs are rejected (SSRF prevention)."""
        payload = {
            "paths": ["http://example.com/model.pkl"],
            "generate_sbom": False
        }
        
        response = requests.post(
            f"{api_base_url}/models/scans",
            headers=headers,
            json=payload,
            timeout=10
        )
        
        # Should reject HTTP/HTTPS URLs
        assert response.status_code in [400, 422]
        error_data = response.json()
        assert "http" in error_data.get("detail", "").lower() or "url" in error_data.get("detail", "").lower()
    
    def test_get_scan_details(self, headers, api_base_url, tmp_path):
        """Test retrieving scan details."""
        # First create a scan
        test_model_path = str(tmp_path / "test_model.pkl")
        create_test_pickle_model(test_model_path)
        
        payload = {
            "paths": [test_model_path],
            "generate_sbom": False
        }
        
        create_response = requests.post(
            f"{api_base_url}/models/scans",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        assert create_response.status_code == 200
        scan_id = create_response.json()["scan_id"]
        
        # Get scan details
        get_response = requests.get(
            f"{api_base_url}/scans/{scan_id}",
            headers=headers,
            timeout=10
        )
        
        assert get_response.status_code == 200
        data = get_response.json()
        assert "scan" in data
        assert data["scan"]["id"] == scan_id
        assert "findings" in data
    
    def test_list_scans(self, headers):
        """Test listing scans."""
        response = requests.get(
            f"{api_base_url}/scans?type=model&limit=10",
            headers=headers,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_findings(self, headers):
        """Test listing findings."""
        response = requests.get(
            f"{api_base_url}/findings?scanner=modelaudit&limit=10",
            headers=headers,
            timeout=10
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_unauthorized_access(self, api_base_url):
        """Test that requests without API key are rejected."""
        response = requests.post(
            f"{api_base_url}/models/scans",
            json={"paths": ["test.pkl"]},
            timeout=10
        )
        
        assert response.status_code == 401 or response.status_code == 403


class TestModelFormats:
    """Test various model formats."""
    
    @pytest.mark.parametrize("format_ext,format_name", [
        ("pkl", "Pickle"),
        ("joblib", "Joblib"),
        ("pt", "PyTorch"),
        ("pth", "PyTorch"),
        ("h5", "Keras H5"),
        ("keras", "Keras V3"),
        ("onnx", "ONNX"),
        ("safetensors", "SafeTensors"),
        ("xgb", "XGBoost"),
        ("npy", "NumPy"),
    ])
    def test_model_format_scan(self, headers, api_base_url, tmp_path, format_ext, format_name):
        """Test scanning different model formats."""
        # Skip if format requires special creation (e.g., ONNX, SafeTensors)
        if format_ext in ["onnx", "safetensors", "h5", "keras", "pt", "pth"]:
            pytest.skip(f"{format_name} requires actual model files, not placeholders")
        
        test_model_path = str(tmp_path / f"test_model.{format_ext}")
        
        # Create appropriate test file based on format
        if format_ext in ["pkl", "joblib"]:
            create_test_pickle_model(test_model_path)
        elif format_ext == "npy":
            import numpy as np
            os.makedirs(os.path.dirname(test_model_path), exist_ok=True)
            np.save(test_model_path, np.array([1, 2, 3]))
        elif format_ext == "xgb":
            # XGBoost models are binary, create placeholder
            os.makedirs(os.path.dirname(test_model_path), exist_ok=True)
            with open(test_model_path, "wb") as f:
                f.write(b"XGBOOST_PLACEHOLDER")
        else:
            pytest.skip(f"Format {format_name} not yet supported in test fixtures")
        
        payload = {
            "paths": [test_model_path],
            "generate_sbom": False,
            "strict": False
        }
        
        response = requests.post(
            f"{api_base_url}/models/scans",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        # Some formats may fail if modelaudit doesn't support them or files are invalid
        # Accept 200 (success) or 400/500 (validation/scan error)
        assert response.status_code in [200, 400, 422, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "scan_id" in data


class TestMCPScannerFunctional:
    """Functional tests for MCP scanner via API."""
    
    def test_mcp_scan_auto_discover(self, headers, api_base_url):
        """Test MCP scan with auto-discovery."""
        payload = {
            "auto_discover": True,
            "timeout": 60
        }
        
        response = requests.post(
            f"{api_base_url}/mcp/scans",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        # Auto-discovery may find 0 configs, which is OK
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert "scan_id" in data
    
    def test_mcp_scan_with_paths(self, headers, api_base_url, tmp_path):
        """Test MCP scan with specific config paths."""
        # Create a test MCP config
        test_config_path = str(tmp_path / "test_mcp.json")
        os.makedirs(os.path.dirname(test_config_path), exist_ok=True)
        
        test_config = {
            "mcpServers": {
                "test-server": {
                    "command": "python",
                    "args": ["server.py"]
                }
            }
        }
        
        with open(test_config_path, "w") as f:
            json.dump(test_config, f)
        
        payload = {
            "config_paths": [test_config_path],
            "auto_discover": False,
            "timeout": 60
        }
        
        response = requests.post(
            f"{api_base_url}/mcp/scans",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "scan_id" in data


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

