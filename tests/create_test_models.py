#!/usr/bin/env python3
"""
Script to create test model files for functional testing.
Run this before executing functional tests.
"""

import os
import pickle
import json
import numpy as np
from pathlib import Path

TEST_DATA_DIR = os.environ.get("TEST_DATA_DIR", "test-data")
MODELS_DIR = os.path.join(TEST_DATA_DIR, "models")
MCP_DIR = os.path.join(TEST_DATA_DIR, "mcp")


def create_pickle_model(file_path: str):
    """Create a test pickle model."""
    model_data = {
        "model_type": "test_classifier",
        "version": "1.0.0",
        "weights": [1.0, 2.0, 3.0, 4.0, 5.0],
        "metadata": {
            "created_by": "test_script",
            "description": "Test pickle model for functional testing"
        }
    }
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    with open(file_path, "wb") as f:
        pickle.dump(model_data, f)
    print(f"✓ Created pickle model: {file_path}")


def create_numpy_model(file_path: str):
    """Create a test NumPy array model."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    arr = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], dtype=np.float32)
    np.save(file_path, arr)
    print(f"✓ Created NumPy model: {file_path}")


def create_joblib_model(file_path: str):
    """Create a test joblib model."""
    try:
        import joblib
        from sklearn.linear_model import LinearRegression
        
        # Create a simple linear regression model
        model = LinearRegression()
        X = np.array([[1], [2], [3], [4], [5]])
        y = np.array([1, 2, 3, 4, 5])
        model.fit(X, y)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        joblib.dump(model, file_path)
        print(f"✓ Created joblib model: {file_path}")
    except ImportError:
        print(f"⚠ Skipped joblib model (joblib/scikit-learn not available): {file_path}")


def create_mcp_config(file_path: str, has_secret: bool = False):
    """Create a test MCP configuration file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    if has_secret:
        config = {
            "mcpServers": {
                "test-server": {
                    "command": "python",
                    "args": ["server.py"],
                    "env": {
                        "API_KEY": "sk-1234567890abcdefghijklmnopqrstuvwxyz",
                        "SECRET_TOKEN": "test-secret-12345"
                    }
                }
            }
        }
    else:
        config = {
            "mcpServers": {
                "test-server": {
                    "command": "python",
                    "args": ["server.py"],
                    "env": {}
                }
            }
        }
    
    with open(file_path, "w") as f:
        json.dump(config, f, indent=2)
    print(f"✓ Created MCP config: {file_path}")


def main():
    """Create all test model files."""
    print("Creating test model files...")
    print(f"Output directory: {TEST_DATA_DIR}")
    print()
    
    # Create model files
    create_pickle_model(os.path.join(MODELS_DIR, "test_model.pkl"))
    create_pickle_model(os.path.join(MODELS_DIR, "test_model2.pkl"))
    create_numpy_model(os.path.join(MODELS_DIR, "test_model.npy"))
    create_joblib_model(os.path.join(MODELS_DIR, "test_model.joblib"))
    
    # Create MCP config files
    create_mcp_config(os.path.join(MCP_DIR, "valid_mcp.json"), has_secret=False)
    create_mcp_config(os.path.join(MCP_DIR, "secrets_mcp.json"), has_secret=True)
    
    print()
    print("✓ Test model files created successfully!")
    print(f"  Models: {MODELS_DIR}")
    print(f"  MCP configs: {MCP_DIR}")


if __name__ == "__main__":
    main()

