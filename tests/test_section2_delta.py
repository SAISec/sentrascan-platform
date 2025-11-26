"""
Delta tests for Section 2.0: Logging, Telemetry & Container Optimization

Tests new features implemented in Section 2.0:
- Structured logging (JSON format, log levels, file storage, rotation, archiving, data masking)
- OTEL telemetry
- ZAP removal
- Container optimization (size reduction, protection)
"""

import pytest
import os
import json
import gzip
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

# Test structured logging
def test_logging_module_exists():
    """Test that logging module exists and can be imported"""
    from sentrascan.core.logging import configure_logging, get_logger
    assert configure_logging is not None
    assert get_logger is not None

def test_logging_configuration():
    """Test that logging can be configured with different log levels"""
    from sentrascan.core.logging import configure_logging
    
    # Test with INFO level
    logger = configure_logging(log_level="INFO", enable_file_logging=False, enable_console_logging=True)
    assert logger is not None
    
    # Test with DEBUG level
    logger = configure_logging(log_level="DEBUG", enable_file_logging=False, enable_console_logging=True)
    assert logger is not None

def test_logging_json_output(tmp_path):
    """Test that logging outputs JSON format"""
    from sentrascan.core.logging import configure_logging
    
    log_dir = str(tmp_path / "logs")
    logger = configure_logging(log_level="INFO", log_dir=log_dir, enable_file_logging=True, enable_console_logging=False)
    
    # Log a test message
    logger.info("test_message", test_key="test_value")
    
    # Check if log file exists
    log_file = Path(log_dir) / "app-info.log"
    assert log_file.exists()
    
    # Read and verify JSON format
    with open(log_file, "r") as f:
        lines = f.readlines()
        assert len(lines) > 0
        # Last line should be valid JSON
        log_entry = json.loads(lines[-1])
        assert "event" in log_entry or "message" in log_entry or "test_key" in log_entry

def test_log_rotation(tmp_path):
    """Test that log rotation works"""
    from sentrascan.core.logging import configure_logging
    from logging.handlers import RotatingFileHandler
    
    log_dir = str(tmp_path / "logs")
    logger = configure_logging(log_level="INFO", log_dir=log_dir, enable_file_logging=True, enable_console_logging=False)
    
    # Check that RotatingFileHandler is used
    import logging
    root_logger = logging.getLogger()
    handlers = [h for h in root_logger.handlers if isinstance(h, RotatingFileHandler)]
    assert len(handlers) > 0

def test_data_masking_api_key():
    """Test that API keys are masked in logs"""
    from sentrascan.core.masking import mask_api_key
    
    api_key = "ss-proj-h_" + "A" * 147
    masked = mask_api_key(api_key, show_prefix=True)
    
    assert "ss-proj-h_" in masked
    assert "***" in masked
    assert len(masked) < len(api_key)

def test_data_masking_password():
    """Test that passwords are masked"""
    from sentrascan.core.masking import mask_password
    
    password = "secret123"
    masked = mask_password(password)
    assert masked == "***"

def test_data_masking_email():
    """Test that email addresses are masked"""
    from sentrascan.core.masking import mask_email
    
    email = "user@example.com"
    masked = mask_email(email)
    assert "***" in masked
    assert "@example.com" in masked
    assert "user" not in masked

def test_data_masking_dict():
    """Test that sensitive data in dictionaries is masked"""
    from sentrascan.core.masking import mask_dict
    
    data = {
        "username": "testuser",
        "password": "secret123",
        "api_key": "ss-proj-h_ABC123",
        "email": "user@example.com"
    }
    
    masked = mask_dict(data)
    assert masked["password"] == "***"
    assert masked["api_key"] != data["api_key"]
    assert "***" in masked["api_key"]
    assert masked["username"] == "testuser"  # Not sensitive

def test_telemetry_module_exists():
    """Test that telemetry module exists"""
    from sentrascan.core.telemetry import TelemetryCollector, get_telemetry, initialize_telemetry
    assert TelemetryCollector is not None
    assert get_telemetry is not None
    assert initialize_telemetry is not None

def test_telemetry_collector_initialization(tmp_path):
    """Test that telemetry collector can be initialized"""
    from sentrascan.core.telemetry import TelemetryCollector
    
    telemetry_dir = str(tmp_path / "telemetry")
    collector = TelemetryCollector(telemetry_dir=telemetry_dir, enabled=True)
    assert collector.enabled is True
    assert Path(telemetry_dir).exists()

def test_telemetry_capture_auth_event(tmp_path):
    """Test that telemetry can capture auth events"""
    from sentrascan.core.telemetry import TelemetryCollector
    
    telemetry_dir = str(tmp_path / "telemetry")
    collector = TelemetryCollector(telemetry_dir=telemetry_dir, enabled=True)
    
    collector.capture_auth_event(
        event_type="login",
        success=True,
        api_key_id=1
    )
    
    # Check if event file exists and contains the event
    events_file = Path(telemetry_dir) / "events.jsonl"
    assert events_file.exists()
    
    with open(events_file, "r") as f:
        lines = f.readlines()
        assert len(lines) > 0
        event = json.loads(lines[-1])
        # Check OTEL structure
        assert "event" in event
        event_data = event["event"]
        assert event_data["type"] == "auth"
        assert event_data["event_type"] == "login"
        assert event_data["success"] is True

def test_telemetry_capture_scan_event(tmp_path):
    """Test that telemetry can capture scan events"""
    from sentrascan.core.telemetry import TelemetryCollector
    
    telemetry_dir = str(tmp_path / "telemetry")
    collector = TelemetryCollector(telemetry_dir=telemetry_dir, enabled=True)
    
    collector.capture_scan_event(
        scan_type="model",
        scan_id="test-scan-123",
        status="completed",
        findings_count=5
    )
    
    events_file = Path(telemetry_dir) / "events.jsonl"
    assert events_file.exists()
    
    with open(events_file, "r") as f:
        lines = f.readlines()
        assert len(lines) > 0
        event = json.loads(lines[-1])
        # Check OTEL structure
        assert "event" in event
        event_data = event["event"]
        assert event_data["type"] == "scan"
        assert event_data["scan_type"] == "model"
        assert event_data["scan_id"] == "test-scan-123"

def test_telemetry_otel_compliance(tmp_path):
    """Test that telemetry events are OTEL-compliant"""
    from sentrascan.core.telemetry import TelemetryCollector
    
    telemetry_dir = str(tmp_path / "telemetry")
    collector = TelemetryCollector(telemetry_dir=telemetry_dir, enabled=True)
    
    collector.capture_auth_event(event_type="login", success=True)
    
    events_file = Path(telemetry_dir) / "events.jsonl"
    with open(events_file, "r") as f:
        event = json.loads(f.readline())
        # Check OTEL structure
        assert "timestamp" in event
        assert "event" in event
        assert "resource" in event
        assert "attributes" in event
        assert event["resource"]["service.name"] == "sentrascan-platform"

def test_zap_removed_from_scanner():
    """Test that ZAP is removed from scanner"""
    import importlib
    import sentrascan.modules.mcp.scanner as scanner_module
    
    # Check that ZapRunner is not imported
    source = open(scanner_module.__file__).read()
    assert "ZapRunner" not in source or "# ZAP removed" in source or "ZAP removed" in source

def test_zap_removed_from_dockerfile():
    """Test that ZAP installation is removed from Dockerfile"""
    dockerfile_path = Path(__file__).parent.parent / "Dockerfile"
    if dockerfile_path.exists():
        content = dockerfile_path.read_text()
        # Should not contain ZAP installation commands
        assert "ZAP_" not in content or "# ZAP removed" in content or "ZAP removed" in content

def test_production_dockerfile_exists():
    """Test that production Dockerfile exists"""
    dockerfile_prod = Path(__file__).parent.parent / "Dockerfile.production"
    assert dockerfile_prod.exists()

def test_production_dockerfile_no_tests():
    """Test that production Dockerfile excludes test files"""
    dockerfile_prod = Path(__file__).parent.parent / "Dockerfile.production"
    if dockerfile_prod.exists():
        content = dockerfile_prod.read_text()
        # Should not copy tests directory
        assert "COPY tests/" not in content or "# NO tests" in content

def test_production_dockerfile_no_test_deps():
    """Test that production Dockerfile excludes test dependencies"""
    dockerfile_prod = Path(__file__).parent.parent / "Dockerfile.production"
    if dockerfile_prod.exists():
        content = dockerfile_prod.read_text()
        # Should not install pytest or playwright in RUN commands
        # Check that pytest and playwright are not in pip install commands
        lines = content.split('\n')
        in_run_section = False
        has_pytest = False
        has_playwright = False
        for line in lines:
            if line.strip().startswith('RUN'):
                in_run_section = True
            if in_run_section and 'pip install' in line.lower():
                if 'pytest' in line.lower():
                    has_pytest = True
                if 'playwright' in line.lower():
                    has_playwright = True
            if line.strip() and not line.strip().startswith('#') and not line.strip().startswith('RUN'):
                in_run_section = False
        # Should not have pytest or playwright in pip install
        assert not has_pytest, "Production Dockerfile should not install pytest"
        assert not has_playwright, "Production Dockerfile should not install playwright"

def test_container_protection_module_exists():
    """Test that container protection module exists"""
    from sentrascan.core.container_protection import check_container_access, _constant_time_compare
    assert check_container_access is not None
    assert _constant_time_compare is not None

def test_container_protection_constant_time_compare():
    """Test constant-time string comparison"""
    from sentrascan.core.container_protection import _constant_time_compare
    
    # Test equal strings
    assert _constant_time_compare("test", "test") is True
    
    # Test unequal strings
    assert _constant_time_compare("test", "test2") is False
    assert _constant_time_compare("test1", "test2") is False

def test_container_protection_with_key():
    """Test container protection with access key"""
    from sentrascan.core.container_protection import check_container_access
    
    # Test with matching keys
    with patch.dict(os.environ, {"CONTAINER_ACCESS_KEY": "test-key", "SENTRASCAN_ACCESS_KEY": "test-key"}):
        # Should not raise
        try:
            check_container_access()
            result = True
        except SystemExit:
            result = False
        assert result is True

def test_container_protection_without_key():
    """Test container protection without access key"""
    from sentrascan.core.container_protection import check_container_access
    
    # Test without runtime key
    with patch.dict(os.environ, {"CONTAINER_ACCESS_KEY": "test-key"}, clear=False):
        if "SENTRASCAN_ACCESS_KEY" in os.environ:
            del os.environ["SENTRASCAN_ACCESS_KEY"]
        # Should exit
        with pytest.raises(SystemExit):
            check_container_access()

def test_container_protection_mismatched_keys():
    """Test container protection with mismatched keys"""
    from sentrascan.core.container_protection import check_container_access
    
    # Test with mismatched keys
    with patch.dict(os.environ, {"CONTAINER_ACCESS_KEY": "test-key", "SENTRASCAN_ACCESS_KEY": "wrong-key"}):
        # Should exit
        with pytest.raises(SystemExit):
            check_container_access()

def test_log_retention_module_exists():
    """Test that log retention module exists"""
    from sentrascan.core.log_retention import archive_old_logs, archive_telemetry, cleanup_old_archives
    assert archive_old_logs is not None
    assert archive_telemetry is not None
    assert cleanup_old_archives is not None

def test_log_archiving(tmp_path):
    """Test that old logs are archived"""
    from sentrascan.core.log_retention import archive_old_logs
    
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    
    # Create an old log file (8 days ago)
    old_log = log_dir / "app-info.log"
    old_time = (datetime.now() - timedelta(days=8)).timestamp()
    old_log.write_text("old log content")
    os.utime(old_log, (old_time, old_time))
    
    # Archive old logs
    archived_count = archive_old_logs(log_dir=str(log_dir), retention_days=7)
    
    # Check that log was archived
    assert archived_count > 0
    archive_dir = log_dir / "archive"
    assert archive_dir.exists()
    archived_files = list(archive_dir.glob("*.log.gz"))
    assert len(archived_files) > 0

def test_telemetry_archiving(tmp_path):
    """Test that old telemetry files are archived"""
    from sentrascan.core.log_retention import archive_telemetry
    
    telemetry_dir = tmp_path / "telemetry"
    telemetry_dir.mkdir()
    
    # Create an old telemetry file (8 days ago)
    old_telemetry = telemetry_dir / "events.jsonl"
    old_time = (datetime.now() - timedelta(days=8)).timestamp()
    old_telemetry.write_text('{"test": "data"}\n')
    os.utime(old_telemetry, (old_time, old_time))
    
    # Archive old telemetry
    archived_count = archive_telemetry(telemetry_dir=str(telemetry_dir), retention_days=7)
    
    # Check that telemetry was archived
    assert archived_count > 0
    archive_dir = telemetry_dir / "archive"
    assert archive_dir.exists()
    archived_files = list(archive_dir.glob("*.jsonl.gz"))
    assert len(archived_files) > 0

def test_log_archiving_compression(tmp_path):
    """Test that archived logs are compressed"""
    from sentrascan.core.log_retention import archive_old_logs
    
    log_dir = tmp_path / "logs"
    log_dir.mkdir()
    
    # Create an old log file
    old_log = log_dir / "app-info.log"
    old_time = (datetime.now() - timedelta(days=8)).timestamp()
    old_log.write_text("old log content")
    os.utime(old_log, (old_time, old_time))
    
    # Archive old logs
    archive_old_logs(log_dir=str(log_dir), retention_days=7)
    
    # Check that archived file is gzipped
    archive_dir = log_dir / "archive"
    archived_files = list(archive_dir.glob("*.log.gz"))
    assert len(archived_files) > 0
    
    # Verify it's actually gzipped
    with gzip.open(archived_files[0], "rt") as f:
        content = f.read()
        assert "old log content" in content

