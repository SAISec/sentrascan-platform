"""
Telemetry module for SentraScan Platform.

OTEL-compliant telemetry for capturing events, metrics, and traces.
Logs are stored locally in OTEL-compliant format.
"""

import os
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List
from enum import Enum


class EventType(str, Enum):
    """Event types for telemetry."""
    AUTH = "auth"
    SCAN = "scan"
    API_CALL = "api_call"
    ERROR = "error"
    CONFIG = "config"
    SYSTEM = "system"


class TelemetryCollector:
    """
    Collects telemetry events and stores them in OTEL-compliant format.
    
    Events are stored as JSON lines in local files.
    """
    
    def __init__(
        self,
        telemetry_dir: Optional[str] = None,
        enabled: bool = True
    ):
        """
        Initialize telemetry collector.
        
        Args:
            telemetry_dir: Directory for telemetry files. Defaults to /app/telemetry or ./telemetry.
            enabled: Whether telemetry collection is enabled.
        """
        self.enabled = enabled and os.environ.get("TELEMETRY_ENABLED", "true").lower() == "true"
        
        if not self.enabled:
            return
        
        # Determine telemetry directory
        if telemetry_dir is None:
            # Allow overriding via environment variable for read-only filesystems
            env_telemetry_dir = os.environ.get("TELEMETRY_DIR")
            if env_telemetry_dir:
                telemetry_dir = env_telemetry_dir
            elif os.path.exists("/app"):
                telemetry_dir = "/app/telemetry"
            else:
                telemetry_dir = "./telemetry"
        
        self.telemetry_dir = Path(telemetry_dir)
        self.telemetry_dir.mkdir(parents=True, exist_ok=True)
        
        # Event log file
        self.events_file = self.telemetry_dir / "events.jsonl"
    
    def _write_event(self, event: Dict[str, Any]):
        """
        Write an event to the telemetry log file.
        
        Args:
            event: Event dictionary to write.
        """
        if not self.enabled:
            return
        
        try:
            # OTEL-compliant event format
            otel_event = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "event": event,
                "resource": {
                    "service.name": "sentrascan-platform",
                    "service.version": os.environ.get("SENTRASCAN_VERSION", "unknown"),
                },
                "attributes": event.get("attributes", {}),
            }
            
            # Write as JSON line
            with open(self.events_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(otel_event) + "\n")
        except Exception:
            # Silently fail to avoid breaking the application
            pass
    
    def capture_auth_event(
        self,
        event_type: str,  # "login", "logout", "api_key_created", "api_key_revoked"
        success: bool,
        user_id: Optional[str] = None,
        api_key_id: Optional[int] = None,
        error: Optional[str] = None,
        **kwargs
    ):
        """
        Capture an authentication event.
        
        Args:
            event_type: Type of auth event.
            success: Whether the operation was successful.
            user_id: User identifier (if applicable).
            api_key_id: API key ID (if applicable).
            error: Error message (if failed).
            **kwargs: Additional attributes.
        """
        event = {
            "type": EventType.AUTH.value,
            "event_type": event_type,
            "success": success,
            "attributes": {
                "user_id": user_id,
                "api_key_id": api_key_id,
                "error": error,
                **kwargs
            }
        }
        self._write_event(event)
    
    def capture_scan_event(
        self,
        scan_type: str,  # "model", "mcp"
        scan_id: str,
        status: str,  # "started", "completed", "failed"
        api_key_id: Optional[int] = None,
        findings_count: Optional[int] = None,
        duration_ms: Optional[int] = None,
        error: Optional[str] = None,
        **kwargs
    ):
        """
        Capture a scan event.
        
        Args:
            scan_type: Type of scan (model, mcp).
            scan_id: Scan identifier.
            status: Scan status.
            api_key_id: API key ID that triggered the scan.
            findings_count: Number of findings (if completed).
            duration_ms: Duration in milliseconds (if completed).
            error: Error message (if failed).
            **kwargs: Additional attributes.
        """
        event = {
            "type": EventType.SCAN.value,
            "scan_type": scan_type,
            "scan_id": scan_id,
            "status": status,
            "attributes": {
                "api_key_id": api_key_id,
                "findings_count": findings_count,
                "duration_ms": duration_ms,
                "error": error,
                **kwargs
            }
        }
        self._write_event(event)
    
    def capture_api_call(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        api_key_id: Optional[int] = None,
        **kwargs
    ):
        """
        Capture an API call event.
        
        Args:
            method: HTTP method.
            path: API path.
            status_code: HTTP status code.
            duration_ms: Request duration in milliseconds.
            api_key_id: API key ID (if authenticated).
            **kwargs: Additional attributes.
        """
        event = {
            "type": EventType.API_CALL.value,
            "method": method,
            "path": path,
            "status_code": status_code,
            "duration_ms": duration_ms,
            "attributes": {
                "api_key_id": api_key_id,
                **kwargs
            }
        }
        self._write_event(event)
    
    def capture_error(
        self,
        error_type: str,
        error_message: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Capture an error event.
        
        Args:
            error_type: Type of error.
            error_message: Error message.
            context: Additional context.
            **kwargs: Additional attributes.
        """
        event = {
            "type": EventType.ERROR.value,
            "error_type": error_type,
            "error_message": error_message,
            "attributes": {
                **(context or {}),
                **kwargs
            }
        }
        self._write_event(event)
    
    def capture_config_event(
        self,
        event_type: str,  # "baseline_created", "baseline_updated", "baseline_deleted"
        baseline_id: Optional[str] = None,
        api_key_id: Optional[int] = None,
        **kwargs
    ):
        """
        Capture a configuration event.
        
        Args:
            event_type: Type of config event.
            baseline_id: Baseline ID (if applicable).
            api_key_id: API key ID (if applicable).
            **kwargs: Additional attributes.
        """
        event = {
            "type": EventType.CONFIG.value,
            "event_type": event_type,
            "attributes": {
                "baseline_id": baseline_id,
                "api_key_id": api_key_id,
                **kwargs
            }
        }
        self._write_event(event)
    
    def capture_system_event(
        self,
        event_type: str,  # "startup", "shutdown", "health_check"
        **kwargs
    ):
        """
        Capture a system event.
        
        Args:
            event_type: Type of system event.
            **kwargs: Additional attributes.
        """
        event = {
            "type": EventType.SYSTEM.value,
            "event_type": event_type,
            "attributes": kwargs
        }
        self._write_event(event)


# Global telemetry collector instance
_telemetry: Optional[TelemetryCollector] = None


def get_telemetry() -> TelemetryCollector:
    """
    Get the global telemetry collector instance.
    
    Returns:
        TelemetryCollector instance.
    """
    global _telemetry
    if _telemetry is None:
        _telemetry = TelemetryCollector()
    return _telemetry


def initialize_telemetry(telemetry_dir: Optional[str] = None, enabled: bool = True):
    """
    Initialize the global telemetry collector.
    
    Args:
        telemetry_dir: Directory for telemetry files.
        enabled: Whether telemetry is enabled.
    """
    global _telemetry
    _telemetry = TelemetryCollector(telemetry_dir=telemetry_dir, enabled=enabled)
    if enabled:
        _telemetry.capture_system_event("startup")

