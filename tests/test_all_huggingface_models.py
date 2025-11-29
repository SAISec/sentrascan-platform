#!/usr/bin/env python3
"""
Comprehensive test script for scanning all 5 Hugging Face models.

Usage:
    python3 test_all_huggingface_models.py [API_KEY]
    
Or set environment variables:
    export API_KEY="your-api-key"
    export API_BASE_URL="http://localhost:8200/api/v1"
    python3 test_all_huggingface_models.py
"""

import requests
import os
import sys
import json
import time
from typing import Dict, List, Tuple

# Configuration
API_BASE_URL = os.environ.get("API_BASE_URL", "http://localhost:8200/api/v1")
API_KEY = os.environ.get("API_KEY") or (sys.argv[1] if len(sys.argv) > 1 else None)

# Hugging Face models to test
HUGGINGFACE_MODELS = [
    {
        "name": "yolo-world-mirror",
        "url": "https://huggingface.co/Bingsu/yolo-world-mirror",
        "repo_id": "Bingsu/yolo-world-mirror",
        "description": "YOLO World Mirror model weights"
    },
    {
        "name": "stock-trading-rl-agent",
        "url": "https://huggingface.co/Adilbai/stock-trading-rl-agent",
        "repo_id": "Adilbai/stock-trading-rl-agent",
        "description": "Stock trading reinforcement learning agent (PPO)"
    },
    {
        "name": "distilbert-sentiments",
        "url": "https://huggingface.co/lxyuan/distilbert-base-multilingual-cased-sentiments-student",
        "repo_id": "lxyuan/distilbert-base-multilingual-cased-sentiments-student",
        "description": "DistilBERT multilingual sentiment analysis model"
    },
    {
        "name": "sentence-transformers-minilm",
        "url": "https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2",
        "repo_id": "sentence-transformers/all-MiniLM-L6-v2",
        "description": "Sentence Transformers MiniLM model"
    },
    {
        "name": "deepseek-ocr",
        "url": "https://huggingface.co/deepseek-ai/DeepSeek-OCR",
        "repo_id": "deepseek-ai/DeepSeek-OCR",
        "description": "DeepSeek OCR model"
    },
]


def test_health_check(api_base_url: str) -> bool:
    """Test API health endpoint."""
    try:
        response = requests.get(f"{api_base_url}/health", timeout=5)
        return response.status_code == 200
    except Exception:
        return False


def scan_huggingface_model(api_key: str, api_base_url: str, model: Dict) -> Tuple[bool, Optional[str], Dict]:
    """
    Scan a Hugging Face model.
    
    Returns:
        (success: bool, scan_id: Optional[str], details: Dict)
    """
    model_url = model["url"]
    model_name = model["name"]
    
    payload = {
        "paths": [model_url],
        "generate_sbom": True,
        "strict": False,
        "timeout": 300  # 5 minutes
    }
    
    try:
        # Send scan request
        response = requests.post(
            f"{api_base_url}/models/scans",
            headers={"X-API-Key": api_key, "Content-Type": "application/json"},
            json=payload,
            timeout=600  # 10 minutes total timeout
        )
        
        if response.status_code != 200:
            error_data = response.json() if response.headers.get("content-type", "").startswith("application/json") else {}
            return False, None, {
                "error": f"Status {response.status_code}",
                "detail": error_data.get("detail", response.text[:200])
            }
        
        # Response might be null, so check database for scan
        # Wait a moment for scan to be created
        time.sleep(3)
        
        # Get latest scans to find our scan
        list_response = requests.get(
            f"{api_base_url}/scans?type=model&limit=10",
            headers={"X-API-Key": api_key},
            timeout=10
        )
        
        if list_response.status_code == 200:
            scans = list_response.json()
            # Find scan with matching URL
            for scan in scans:
                if model_url in scan.get("target", ""):
                    scan_id = scan.get("id")
                    if scan_id:
                        # Get detailed scan information
                        get_response = requests.get(
                            f"{api_base_url}/scans/{scan_id}",
                            headers={"X-API-Key": api_key},
                            timeout=10
                        )
                        if get_response.status_code == 200:
                            scan_data = get_response.json()
                            return True, scan_id, scan_data
        
        # Scan might still be processing
        return True, None, {"status": "scan_accepted_processing"}
        
    except requests.exceptions.Timeout:
        return False, None, {"error": "Request timeout"}
    except Exception as e:
        return False, None, {"error": str(e)}


def wait_for_scan_completion(api_key: str, api_base_url: str, scan_id: str, max_wait: int = 300) -> Dict:
    """Wait for scan to complete and return results."""
    for i in range(max_wait):
        time.sleep(1)
        try:
            response = requests.get(
                f"{api_base_url}/scans/{scan_id}",
                headers={"X-API-Key": api_key},
                timeout=10
            )
            if response.status_code == 200:
                scan_data = response.json()
                scan_info = scan_data.get("scan", {})
                # Check if scan is complete
                if scan_info.get("duration_ms") or scan_info.get("total_findings") is not None:
                    return scan_data
        except Exception:
            pass
    
    return {"status": "timeout", "message": "Scan did not complete within timeout period"}


def main():
    """Run comprehensive Hugging Face model scanning tests."""
    if not API_KEY:
        print("Error: API_KEY is required")
        print("Usage: python3 test_all_huggingface_models.py [API_KEY]")
        print("Or set API_KEY environment variable")
        sys.exit(1)
    
    print("=" * 70)
    print("HUGGING FACE MODEL SCANNING - COMPREHENSIVE TEST")
    print("=" * 70)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Models to test: {len(HUGGINGFACE_MODELS)}")
    print()
    
    # Test 1: Health check
    print("Test 0: Health Check")
    if test_health_check(API_BASE_URL):
        print("  ✓ PASSED")
    else:
        print("  ✗ FAILED - API is not healthy")
        sys.exit(1)
    print()
    
    # Test each model
    results = []
    for i, model in enumerate(HUGGINGFACE_MODELS, 1):
        print(f"Test {i}: {model['name']}")
        print(f"  Description: {model['description']}")
        print(f"  URL: {model['url']}")
        print(f"  Repo ID: {model['repo_id']}")
        
        success, scan_id, details = scan_huggingface_model(API_KEY, API_BASE_URL, model)
        
        if success:
            if scan_id:
                print(f"  ✓ Scan created: {scan_id}")
                
                # Wait for completion
                print("  Waiting for scan to complete...")
                scan_data = wait_for_scan_completion(API_KEY, API_BASE_URL, scan_id, max_wait=300)
                
                if "scan" in scan_data:
                    scan_info = scan_data["scan"]
                    findings = scan_data.get("findings", [])
                    
                    print(f"  ✓ Scan completed")
                    print(f"    Findings: {scan_info.get('critical', 0)} critical, "
                          f"{scan_info.get('high', 0)} high, "
                          f"{scan_info.get('medium', 0)} medium, "
                          f"{scan_info.get('low', 0)} low")
                    print(f"    Total Findings: {len(findings)}")
                    print(f"    Status: {'PASSED' if scan_info.get('passed') else 'FAILED'}")
                    print(f"    Duration: {scan_info.get('duration_ms', 0)} ms")
                    
                    results.append({
                        "model": model["name"],
                        "status": "completed",
                        "scan_id": scan_id,
                        "findings": {
                            "critical": scan_info.get("critical", 0),
                            "high": scan_info.get("high", 0),
                            "medium": scan_info.get("medium", 0),
                            "low": scan_info.get("low", 0),
                            "total": len(findings)
                        },
                        "passed": scan_info.get("passed", False),
                        "duration_ms": scan_info.get("duration_ms", 0)
                    })
                else:
                    print(f"  ⚠ Scan may still be processing")
                    results.append({
                        "model": model["name"],
                        "status": "processing",
                        "scan_id": scan_id
                    })
            else:
                print(f"  ⚠ Scan accepted but scan_id not immediately available")
                results.append({
                    "model": model["name"],
                    "status": "accepted",
                    "details": details
                })
        else:
            print(f"  ✗ FAILED")
            print(f"    Error: {details.get('error', 'Unknown error')}")
            if "detail" in details:
                print(f"    Detail: {details['detail']}")
            results.append({
                "model": model["name"],
                "status": "failed",
                "error": details.get("error", "Unknown")
            })
        
        print()
    
    # Summary
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)
    
    completed = sum(1 for r in results if r.get("status") == "completed")
    processing = sum(1 for r in results if r.get("status") in ["processing", "accepted"])
    failed = sum(1 for r in results if r.get("status") == "failed")
    
    print(f"Total Models Tested: {len(results)}")
    print(f"  ✓ Completed: {completed}")
    print(f"  ⏳ Processing/Accepted: {processing}")
    print(f"  ✗ Failed: {failed}")
    print()
    
    print("Detailed Results:")
    for result in results:
        status_icon = "✓" if result.get("status") == "completed" else "⏳" if result.get("status") in ["processing", "accepted"] else "✗"
        print(f"  {status_icon} {result['model']}")
        if result.get("scan_id"):
            print(f"      Scan ID: {result['scan_id']}")
        if result.get("findings"):
            findings = result["findings"]
            print(f"      Findings: {findings['critical']} critical, {findings['high']} high, "
                  f"{findings['medium']} medium, {findings['low']} low (total: {findings['total']})")
        if result.get("error"):
            print(f"      Error: {result['error']}")
    
    print()
    print("=" * 70)
    
    # Save results to file
    results_file = "huggingface_scan_results.json"
    with open(results_file, "w") as f:
        json.dump({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "api_base_url": API_BASE_URL,
            "models_tested": len(HUGGINGFACE_MODELS),
            "results": results
        }, f, indent=2)
    
    print(f"Results saved to: {results_file}")
    print()


if __name__ == "__main__":
    main()

