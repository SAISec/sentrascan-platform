import os
from fastapi import FastAPI, HTTPException, Depends, Request, Header, Response, Form, Body
from fastapi.responses import RedirectResponse, StreamingResponse
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.requests import Request as StarletteRequest
from starlette.middleware.base import BaseHTTPMiddleware
import json
import asyncio
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session  # ensure available for type annotations
from sqlalchemy import func, or_
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict, Any
from sentrascan.core.storage import init_db, SessionLocal
from sentrascan.modules.model.scanner import ModelScanner
from sentrascan.modules.mcp.scanner import MCPScanner
from sentrascan.core.policy import PolicyEngine
from sentrascan.core.logging import configure_logging, get_logger
from sentrascan.core.masking import mask_dict, mask_api_key, mask_email
from sentrascan.core.telemetry import get_telemetry, initialize_telemetry
from sentrascan.core.container_protection import check_container_access
from sentrascan.core.log_retention import archive_old_logs, archive_telemetry
from sentrascan.core.tenant_context import (
    get_tenant_id, set_tenant_id, extract_tenant_from_request,
    require_tenant, validate_tenant_access, TenantContextMiddleware
)
from sentrascan.core.query_helpers import filter_by_tenant, require_tenant_for_query
from sentrascan.core.auth import (
    authenticate_user, create_user, update_user_password,
    deactivate_user, activate_user, PasswordPolicy
)
from sentrascan.core.rbac import (
    require_role, require_permission, check_role, check_permission,
    can_access_tenant, get_user_role, has_permission
)
from sentrascan.core.session import (
    create_session, get_session_user as get_session_user_from_session,
    refresh_session, invalidate_session, invalidate_user_sessions,
    cleanup_expired_sessions, SESSION_COOKIE_NAME, sign as sign_session, unsign as unsign_session
)
from sentrascan.core.sharding import (
    init_sharding_metadata, get_shard_schema, create_shard_schema,
    get_shard_for_tenant, list_shards, deactivate_shard, get_shard_statistics
)
from sentrascan.core.key_management import get_key_manager, rotate_tenant_key
from sentrascan.core.transparent_encryption import enable_transparent_encryption
import csv
import io
import secrets
import random
import re
import time

# Check container access (build-time protection)
check_container_access()

# Initialize structured logging
logger = configure_logging()
logger.info("SentraScan Platform starting", version=__import__("sentrascan", fromlist=["__version__"]).__version__)

# Initialize telemetry
initialize_telemetry()
telemetry = get_telemetry()

# Archive old logs on startup (background task)
try:
    archive_old_logs()
    archive_telemetry()
except Exception:
    pass  # Don't fail startup if archiving fails

app = FastAPI(
    title="SentraScan Platform",
    docs_url=None,  # Disable automatic Swagger UI at /docs
    redoc_url=None  # Disable automatic ReDoc at /redoc
)

# Logging middleware
class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Log request
        logger.info(
            "request_started",
            method=request.method,
            path=request.url.path,
            client_ip=client_ip,
            query_params=str(request.query_params) if request.query_params else None
        )
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            
            # Log response
            logger.info(
                "request_completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                process_time_ms=round(process_time * 1000, 2),
                client_ip=client_ip
            )
            
            # Capture API call in telemetry
            try:
                api_key_id = None
                if hasattr(request.state, "api_key_id"):
                    api_key_id = request.state.api_key_id
                telemetry.capture_api_call(
                    method=request.method,
                    path=request.url.path,
                    status_code=response.status_code,
                    duration_ms=round(process_time * 1000, 2),
                    api_key_id=api_key_id
                )
            except Exception:
                pass  # Don't break request handling if telemetry fails
            
            return response
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                "request_failed",
                method=request.method,
                path=request.url.path,
                error=str(e),
                error_type=type(e).__name__,
                process_time_ms=round(process_time * 1000, 2),
                client_ip=client_ip,
                exc_info=True
            )
            raise

app.add_middleware(LoggingMiddleware)
app.add_middleware(TenantContextMiddleware)

# Security middleware
from sentrascan.core.security import (
    RateLimitMiddleware, SecurityHeadersMiddleware, RequestSizeLimitMiddleware,
    CORS_ALLOWED_ORIGINS, CORS_ALLOW_CREDENTIALS, sanitize_input, validate_email
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(RateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestSizeLimitMiddleware)

# CORS middleware
if CORS_ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=CORS_ALLOWED_ORIGINS,
        allow_credentials=CORS_ALLOW_CREDENTIALS,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

# Session management - use module functions
SESSION_COOKIE = SESSION_COOKIE_NAME  # Imported from session module

# Legacy sign/unsign functions for backward compatibility
def sign(val: str) -> str:
    """Legacy sign function - delegates to session module."""
    return sign_session(val)

def unsign(signed: str) -> str | None:
    """Legacy unsign function - delegates to session module."""
    return unsign_session(signed)

def get_session_user(request: Request, db: Session = None):
    """
    Get the authenticated user from session cookie.
    Supports both APIKey (legacy) and User (new) authentication.
    """
    cookie = request.cookies.get(SESSION_COOKIE)
    if not cookie:
        return None
    signed_value = unsign(cookie)
    if not signed_value:
        return None
    
    if db is None:
        # Create a temporary session and ensure it's closed
        db = SessionLocal()
        try:
            return _get_user_from_session(signed_value, db)
        finally:
            db.close()
    return _get_user_from_session(signed_value, db)


def _get_user_from_session(signed_cookie: str, db: Session):
    """
    Get user from session cookie (supports both APIKey and User).
    Uses new session management for User sessions, legacy for APIKey.
    Returns User object or APIKey object (which has role attribute).
    """
    # Try new session management first
    user = get_session_user_from_session(signed_cookie, db)
    if user:
        return user
    
    # Legacy: Check if it's a user session (format: "user:{user_id}")
    signed_value = unsign(signed_cookie)
    if signed_value and signed_value.startswith("user:"):
        user_id = signed_value.split(":", 1)[1]
        user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
        if user:
            # Refresh session on activity
            refresh_session(signed_cookie)
            return user
    
    # Legacy: API key session
    if signed_value:
        rec = db.query(APIKey).filter(APIKey.key_hash == APIKey.hash_key(signed_value), APIKey.is_revoked == False).first()
        if rec:
            # Check expiration
            if rec.expires_at and datetime.utcnow() > rec.expires_at:
                logger.warning("api_key_expired", api_key_id=rec.id)
                raise HTTPException(401, "API key has expired")
            # Return APIKey object - it has role attribute for RBAC
            return rec
    
    return None

# Simple API key and role enforcement (MVP)
from sentrascan.core.models import APIKey, Scan, Finding, Baseline, User, Tenant

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_db_session():
    """Get a database session that must be explicitly closed."""
    return SessionLocal()

def generate_api_key() -> str:
    """
    Generate API key with format: ss-proj-h_ + 147-character alphanumeric string (A-Z, a-z, 0-9) 
    with exactly one random hyphen inserted at random position.
    """
    prefix = "ss-proj-h_"
    # Generate 147 alphanumeric characters
    chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    random_chars = ''.join(secrets.choice(chars) for _ in range(147))
    
    # Insert exactly one hyphen at a random position (not at start or end of the 147-char string)
    hyphen_position = random.randint(1, 146)
    random_chars = random_chars[:hyphen_position] + '-' + random_chars[hyphen_position:]
    
    return prefix + random_chars

def validate_api_key_format(api_key: str) -> bool:
    """
    Validate API key format matches requirement: ss-proj-h_ prefix and 147-character 
    alphanumeric string with exactly one hyphen.
    """
    pattern = r'^ss-proj-h_[A-Za-z0-9-]{147}$'
    if not re.match(pattern, api_key):
        return False
    
    # Check that there's exactly one hyphen in the 147-character part
    key_part = api_key[10:]  # After "ss-proj-h_"
    if key_part.count('-') != 1:
        return False
    
    return True

def require_api_key(x_api_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    """
    Require and validate API key authentication.
    Returns APIKey object with tenant_id and user_id associations.
    """
    # Allow unauthenticated health
    if x_api_key is None:
        raise HTTPException(401, "Missing API key")
    
    rec = db.query(APIKey).filter(
        APIKey.key_hash == APIKey.hash_key(x_api_key),
        APIKey.is_revoked == False
    ).first()
    
    if not rec:
        raise HTTPException(403, "Invalid API key")
    
    # Check expiration
    if rec.expires_at and datetime.utcnow() > rec.expires_at:
        logger.warning("api_key_expired", api_key_id=rec.id)
        raise HTTPException(401, "API key has expired")
    
    # Check if associated tenant is active
    if rec.tenant_id:
        tenant = db.query(Tenant).filter(Tenant.id == rec.tenant_id).first()
        if tenant and not tenant.is_active:
            raise HTTPException(403, "Tenant is deactivated")
    
    # If API key has user_id, inherit role from user if user role is more permissive
    if rec.user_id:
        user = db.query(User).filter(User.id == rec.user_id, User.is_active == True).first()
        if user:
            # Inherit role from user (user role takes precedence)
            rec.role = user.role
            # Ensure tenant_id matches user's tenant
            if user.tenant_id and not rec.tenant_id:
                rec.tenant_id = user.tenant_id
    
    return rec
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "web", "templates"))

# Add version to template context
from sentrascan import __version__
templates.env.globals['app_version'] = __version__

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "web", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Exception handlers for error pages
@app.exception_handler(404)
async def not_found_handler(request: StarletteRequest, exc: StarletteHTTPException):
    """Handle 404 errors with custom error page."""
    # Only render HTML for UI routes, return JSON for API routes
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=404,
            content={"error": "Not found", "detail": str(exc.detail) if hasattr(exc, 'detail') else "Resource not found"}
        )
    # Render 404 template for UI routes
    try:
        user = get_session_user(request)
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request, "user": user},
            status_code=404
        )
    except Exception:
        # Fallback if template rendering fails
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request, "user": None},
            status_code=404
        )

@app.exception_handler(500)
async def server_error_handler(request: StarletteRequest, exc: Exception):
    """Handle 500 errors with custom error page."""
    # Only render HTML for UI routes, return JSON for API routes
    if request.url.path.startswith("/api/"):
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": "An unexpected error occurred"}
        )
    # Render 500 template for UI routes
    try:
        user = get_session_user(request)
        return templates.TemplateResponse(
            "errors/500.html",
            {"request": request, "user": user},
            status_code=500
        )
    except Exception:
        # Fallback if template rendering fails
        return templates.TemplateResponse(
            "errors/500.html",
            {"request": request, "user": None},
            status_code=500
        )

@app.get("/api/v1/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/models/scans")
def scan_model(payload: dict, request: Request, api_key=Depends(require_api_key), db: Session = Depends(get_db)):
    # RBAC: only admin can trigger scans
    if not check_permission(api_key, "scan.create"):
        logger.warning(
            "scan_denied",
            reason="insufficient_permission",
            required_permission="scan.create",
            user_role=get_user_role(api_key),
            api_key_id=getattr(api_key, "id", None)
        )
        raise HTTPException(403, "Permission denied: scan.create required")
    # Validate required fields
    if not payload:
        logger.warning("scan_validation_failed", reason="missing_payload", api_key_id=getattr(api_key, "id", None))
        raise HTTPException(400, "Request body is required")
    paths = payload.get("paths") or ([payload.get("model_path")] if payload.get("model_path") else None)
    
    # Require tenant context
    tenant_id = require_tenant(request, db)
    
    # Check if model scanner is enabled for this tenant
    from sentrascan.core.tenant_settings import get_tenant_setting
    scanner_settings = get_tenant_setting(db, tenant_id, "scanner", {})
    enabled_scanners = scanner_settings.get("enabled_scanners", ["mcp", "model"])
    if "model" not in enabled_scanners:
        raise HTTPException(403, "Model scanner is disabled for this tenant")
    
    logger.info(
        "model_scan_started",
        api_key_id=getattr(api_key, "id", None),
        tenant_id=tenant_id,
        paths_count=len(paths) if paths else 0,
        payload_keys=list(payload.keys())
    )
    if not paths or (isinstance(paths, list) and len(paths) == 0):
        raise HTTPException(400, "paths or model_path is required")
    sbom = payload.get("generate_sbom")
    policy_path = payload.get("policy")
    
    # Get scanner timeout from tenant settings
    scanner_timeouts = scanner_settings.get("scanner_timeouts", {})
    default_timeout = scanner_timeouts.get("model_timeout", payload.get("timeout", 0))
    timeout = payload.get("timeout", default_timeout)
    
    pe = PolicyEngine.from_file(policy_path, tenant_id=tenant_id, db=db) if policy_path else PolicyEngine.default_model(tenant_id=tenant_id, db=db)
    ms = ModelScanner(policy=pe)
    try:
        scan = ms.scan(paths=paths, sbom_path=sbom and "./sboms/auto_sbom.json", strict=payload.get("strict", False), timeout=timeout, db=db, tenant_id=tenant_id)
        
        # Capture telemetry
        telemetry.capture_scan_event(
            scan_type="model",
            scan_id=str(scan.id),
            status="completed",
            api_key_id=getattr(api_key, "id", None),
            findings_count=scan.total_findings,
            duration_ms=scan.duration_ms if hasattr(scan, "duration_ms") else None
        )
        
        logger.info(
            "model_scan_completed",
            scan_id=scan.id,
            api_key_id=getattr(api_key, "id", None),
            total_findings=scan.total_findings,
            passed=scan.passed
        )
        
        return ms.to_report(scan)
    except Exception as e:
        logger.error(
            "model_scan_failed",
            api_key_id=getattr(api_key, "id", None),
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        telemetry.capture_scan_event(
            scan_type="model",
            scan_id="unknown",
            status="failed",
            api_key_id=getattr(api_key, "id", None),
            error=str(e)
        )
        raise
@app.post("/api/v1/mcp/scans")
def scan_mcp(payload: dict, request: Request, api_key=Depends(require_api_key), db: Session = Depends(get_db)):
    # RBAC: require scan.create permission
    if not check_permission(api_key, "scan.create"):
        logger.warning(
            "scan_denied",
            reason="insufficient_role",
            required_role="admin",
            user_role=getattr(api_key, "role", "unknown"),
            api_key_id=getattr(api_key, "id", None),
            scan_type="mcp"
        )
        raise HTTPException(403, "Insufficient role: admin required")
    configs = payload.get("config_paths") or []
    auto = bool(payload.get("auto_discover", False))
    
    # Require tenant context
    tenant_id = require_tenant(request, db)
    
    # Check if MCP scanner is enabled for this tenant
    from sentrascan.core.tenant_settings import get_tenant_setting
    scanner_settings = get_tenant_setting(db, tenant_id, "scanner", {})
    enabled_scanners = scanner_settings.get("enabled_scanners", ["mcp", "model"])
    if "mcp" not in enabled_scanners:
        raise HTTPException(403, "MCP scanner is disabled for this tenant")
    
    logger.info(
        "mcp_scan_started",
        api_key_id=getattr(api_key, "id", None),
        tenant_id=tenant_id,
        config_paths_count=len(configs),
        auto_discover=auto,
        timeout=payload.get("timeout", 60)
    )
    
    # Get scanner timeout from tenant settings
    scanner_timeouts = scanner_settings.get("scanner_timeouts", {})
    default_timeout = scanner_timeouts.get("mcp_timeout", payload.get("timeout", 60))
    timeout = payload.get("timeout", default_timeout)
    
    policy_path = payload.get("policy")
    pe = PolicyEngine.from_file(policy_path, tenant_id=tenant_id, db=db) if policy_path else PolicyEngine.default_mcp(tenant_id=tenant_id, db=db)
    scanner = MCPScanner(policy=pe)
    try:
        scan = scanner.scan(config_paths=configs, auto_discover=auto, timeout=timeout, db=db, tenant_id=tenant_id)
        logger.info(
            "mcp_scan_completed",
            scan_id=scan.id,
            api_key_id=getattr(api_key, "id", None),
            total_findings=scan.total_findings,
            passed=scan.passed
        )
        return scanner.to_report(scan)
    except Exception as e:
        logger.error(
            "mcp_scan_failed",
            api_key_id=getattr(api_key, "id", None),
            error=str(e),
            error_type=type(e).__name__,
            exc_info=True
        )
        raise

# Jobs queue (simple worker)
from threading import Thread, Event
import queue, time as _time

job_queue: queue.Queue = queue.Queue()
stop_event = Event()

from sqlalchemy.exc import SQLAlchemyError

class JobRunner(Thread):
    def run(self):
        while not stop_event.is_set():
            try:
                job = job_queue.get(timeout=0.5)
            except queue.Empty:
                continue
            db = None
            try:
                db = get_db_session()
                if job["type"] == "model":
                    existing = db.query(Scan).filter(Scan.id == job.get("existing_scan_id")).first()
                    tenant_id = job.get("tenant_id") or (existing.tenant_id if existing and hasattr(existing, 'tenant_id') else None)
                    pe = PolicyEngine.default_model(tenant_id=tenant_id, db=db)
                    ms = ModelScanner(policy=pe)
                    scan = ms.scan(paths=job["paths"], sbom_path=job.get("sbom_path"), strict=job.get("strict", False), timeout=job.get("timeout", 0), db=db, tenant_id=tenant_id)
                    job["on_done"](scan.id)
                elif job["type"] == "mcp":
                    existing = db.query(Scan).filter(Scan.id == job.get("existing_scan_id")).first()
                    tenant_id = job.get("tenant_id") or (existing.tenant_id if existing and hasattr(existing, 'tenant_id') else None)
                    pe = PolicyEngine.default_mcp(tenant_id=tenant_id, db=db)
                    scanner = MCPScanner(policy=pe)
                    scan = scanner.scan(config_paths=job.get("config_paths") or [], auto_discover=job.get("auto_discover", True), timeout=job.get("timeout", 60), db=db, tenant_id=tenant_id)
                    job["on_done"](scan.id)
            except Exception:
                pass
            finally:
                if db:
                    db.close()

runner = JobRunner(daemon=True)

@app.on_event("startup")
def on_startup():
    init_db()
    # Initialize sharding metadata
    init_sharding_metadata()
    # Enable transparent encryption
    enable_transparent_encryption()
    # start job runner
    if not runner.is_alive():
        runner.start()
    
    # Start background task for session cleanup
    import threading
    def cleanup_sessions_periodically():
        import time
        while True:
            time.sleep(3600)  # Run every hour
            try:
                cleanup_expired_sessions()
            except Exception as e:
                logger.error("session_cleanup_failed", error=str(e), exc_info=True)
    
    cleanup_thread = threading.Thread(target=cleanup_sessions_periodically, daemon=True)
    cleanup_thread.start()
    logger.info("session_cleanup_started", interval_hours=1)

# Baselines API
@app.get("/api/v1/baselines")
def list_baselines(api_key=Depends(require_api_key), db: Session = Depends(get_db)):
    rows = db.query(Baseline).order_by(Baseline.created_at.desc()).limit(100).all()
    return [
        {
            "id": b.id,
            "created_at": b.created_at.isoformat(),
            "type": b.baseline_type,
            "name": b.name,
            "target_hash": b.target_hash,
            "is_active": bool(b.is_active),
        }
        for b in rows
    ]

@app.get("/api/v1/baselines/{baseline_id}")
def get_baseline(baseline_id: str, api_key=Depends(require_api_key), db: Session = Depends(get_db)):
    b = db.query(Baseline).filter(Baseline.id == baseline_id).first()
    if not b:
        raise HTTPException(404, "Baseline not found")
    return {
        "id": b.id,
        "created_at": b.created_at.isoformat(),
        "type": b.baseline_type,
        "name": b.name,
        "target_hash": b.target_hash,
        "content": b.content,
        "is_active": bool(b.is_active),
    }

@app.post("/ui/baselines")
def ui_create_baseline(request: Request, name: str = Form(...), description: str | None = Form(None), is_active: bool = Form(True), scan_id: str = Form(...), baseline_type: str = Form(...), target_hash: str | None = Form(None), db: Session = Depends(get_db)):
    # RBAC: only admin can create
    user = get_session_user(request, db)
    if not user or user.role != "admin":
        raise HTTPException(403, "Insufficient role: admin required")
    
    # Get scan report to use as baseline content
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Scan not found")
    
    # Create baseline from scan
    b = Baseline(
        baseline_type=baseline_type,
        name=name,
        description=description,
        target_hash=target_hash or scan.target_hash,
        content={},  # Will be populated from scan report
        scan_id=scan_id,
        sbom_id=scan.sbom_id,
        approved_by=getattr(user, "name", None) or "UI User",
        is_active=is_active,
    )
    
    # Get scan report for content
    try:
        from sentrascan.modules.model.scanner import ModelScanner
        from sentrascan.modules.mcp.scanner import MCPScanner
        if baseline_type == "model":
            scanner = ModelScanner()
            report = scanner.to_report(scan, db)
        else:
            scanner = MCPScanner()
            report = scanner.to_report(scan, db)
        b.content = report
    except Exception as e:
        # Fallback: use minimal content
        b.content = {"scan_id": scan_id, "type": baseline_type}
    
    db.add(b)
    db.commit()
    return RedirectResponse(url=f"/baselines", status_code=303)

@app.post("/api/v1/baselines")
def create_baseline(payload: dict, api_key=Depends(require_api_key), db: Session = Depends(get_db)):
    # RBAC: require scan.create permission (baselines are tied to scans)
    if not check_permission(api_key, "scan.create"):
        raise HTTPException(403, "Permission denied: scan.create required")
    required = ["baseline_type", "name", "content"]
    if not all(k in payload for k in required):
        raise HTTPException(400, "baseline_type, name, content required")
    b = Baseline(
        baseline_type=payload["baseline_type"],
        name=payload["name"],
        description=payload.get("description"),
        target_hash=payload.get("target_hash"),
        content=payload.get("content"),
        scan_id=payload.get("scan_id"),
        sbom_id=payload.get("sbom_id"),
        approved_by=payload.get("approved_by"),
        is_active=True,
    )
    db.add(b)
    db.commit()
    return {"id": b.id}

@app.delete("/api/v1/baselines/{baseline_id}")
def delete_baseline(baseline_id: str, api_key=Depends(require_api_key), db: Session = Depends(get_db)):
    # RBAC: require scan.delete permission (baselines are tied to scans)
    if not check_permission(api_key, "scan.delete"):
        raise HTTPException(403, "Permission denied: scan.delete required")
    
    b = db.query(Baseline).filter(Baseline.id == baseline_id).first()
    if not b:
        raise HTTPException(404, "Baseline not found")
    if b.is_active:
        raise HTTPException(400, "Cannot delete active baseline. Deactivate it first.")
    db.delete(b)
    db.commit()
    return {"status": "deleted"}
    b = db.query(Baseline).filter(Baseline.id == baseline_id).first()
    if not b:
        raise HTTPException(404, "Baseline not found")
    if b.is_active:
        raise HTTPException(400, "Cannot delete active baseline. Deactivate it first.")
    db.delete(b)
    db.commit()
    return {"status": "deleted"}

@app.post("/api/v1/baselines/compare")
def compare_baselines(payload: dict, api_key=Depends(require_api_key), db: Session = Depends(get_db)):
    left_id = payload.get("left_id")
    right_id = payload.get("right_id")
    if not (left_id and right_id):
        raise HTTPException(400, "left_id and right_id required")
    l = db.query(Baseline).filter(Baseline.id == left_id).first()
    r = db.query(Baseline).filter(Baseline.id == right_id).first()
    if not l or not r:
        raise HTTPException(404, "Baseline not found")
    def deep_diff(a, b, path=""):
        diffs = []
        if isinstance(a, dict) and isinstance(b, dict):
            keys = set(a.keys()) | set(b.keys())
            for k in sorted(keys):
                p = f"{path}.{k}" if path else k
                if k not in a:
                    diffs.append({"path": p, "change": "added", "to": b[k]})
                elif k not in b:
                    diffs.append({"path": p, "change": "removed", "from": a[k]})
                else:
                    if a[k] != b[k]:
                        diffs.extend(deep_diff(a[k], b[k], p))
        elif isinstance(a, list) and isinstance(b, list):
            la, lb = len(a), len(b)
            n = max(la, lb)
            for i in range(n):
                p = f"{path}[{i}]"
                if i >= la:
                    diffs.append({"path": p, "change": "added", "to": b[i]})
                elif i >= lb:
                    diffs.append({"path": p, "change": "removed", "from": a[i]})
                else:
                    if a[i] != b[i]:
                        diffs.extend(deep_diff(a[i], b[i], p))
        else:
            diffs.append({"path": path, "change": "changed", "from": a, "to": b})
        return diffs
    result = {"diff": deep_diff(l.content or {}, r.content or {})}
    return result

@app.get("/baselines")
def ui_baselines(request: Request, sort: str | None = None, order: str | None = None):
    db = get_db_session()
    try:
        user = get_session_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        
        # Get tenant_id and filter queries
        tenant_id = None
        if isinstance(user, User):
            tenant_id = user.tenant_id
        elif hasattr(user, 'tenant_id'):
            tenant_id = user.tenant_id
        
        if not tenant_id:
            tenant_id = extract_tenant_from_request(request, db)
        
        if not tenant_id:
            return RedirectResponse(url="/login?error=tenant_required", status_code=302)
        
        q = db.query(Baseline)
        # Filter by tenant_id
        q = filter_by_tenant(q, Baseline, tenant_id)
        
        # Apply sorting
        sort_order = order if order in ('asc', 'desc') else 'desc'
        if sort == 'time':
            q = q.order_by(Baseline.created_at.desc() if sort_order == 'desc' else Baseline.created_at.asc())
        elif sort == 'type':
            q = q.order_by(Baseline.baseline_type.desc() if sort_order == 'desc' else Baseline.baseline_type.asc())
        elif sort == 'name':
            q = q.order_by(Baseline.name.desc() if sort_order == 'desc' else Baseline.name.asc())
        elif sort == 'hash':
            q = q.order_by(Baseline.target_hash.desc() if sort_order == 'desc' else Baseline.target_hash.asc())
        elif sort == 'active':
            q = q.order_by(Baseline.is_active.desc() if sort_order == 'desc' else Baseline.is_active.asc())
        else:
            # Default sort by time descending
            q = q.order_by(Baseline.created_at.desc())
        
        rows = q.limit(50).all()
        
        # Get tenant info for display
        tenant = None
        if tenant_id:
            tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        
        breadcrumb_items = [
            {"label": "Dashboard", "url": "/"},
            {"label": "Baselines", "url": "/baselines"}
        ]
        return templates.TemplateResponse("baselines.html", {
            "request": request,
            "user": user,
            "tenant": tenant,
            "baselines": rows,
            "sort": sort or "",
            "order": order or "desc",
            "breadcrumb_items": breadcrumb_items
        })
    finally:
        db.close()

@app.get("/baseline/compare")
def ui_baseline_compare(left: str, right: str, request: Request):
    db = get_db_session()
    try:
        user = get_session_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        
        # Get tenant_id for filtering
        tenant_id = None
        if isinstance(user, User):
            tenant_id = user.tenant_id
        elif hasattr(user, 'tenant_id'):
            tenant_id = user.tenant_id
        
        if not tenant_id:
            tenant_id = extract_tenant_from_request(request, db)
        
        if not tenant_id:
            return RedirectResponse(url="/login?error=tenant_required", status_code=302)
        
        # Filter by tenant
        q_l = db.query(Baseline).filter(Baseline.id == left)
        q_l = filter_by_tenant(q_l, Baseline, tenant_id)
        l = q_l.first()
        
        q_r = db.query(Baseline).filter(Baseline.id == right)
        q_r = filter_by_tenant(q_r, Baseline, tenant_id)
        r = q_r.first()
        
        if not l or not r:
            raise HTTPException(404, "Baseline not found")
        
        # Use the same deep_diff function as the API
        def deep_diff(a, b, path=""):
            diffs = []
            if isinstance(a, dict) and isinstance(b, dict):
                keys = set(a.keys()) | set(b.keys())
                for k in sorted(keys):
                    p = f"{path}.{k}" if path else k
                    if k not in a:
                        diffs.append({"path": p, "change": "added", "to": b[k]})
                    elif k not in b:
                        diffs.append({"path": p, "change": "removed", "from": a[k]})
                    else:
                        if a[k] != b[k]:
                            diffs.extend(deep_diff(a[k], b[k], p))
            elif isinstance(a, list) and isinstance(b, list):
                la, lb = len(a), len(b)
                n = max(la, lb)
                for i in range(n):
                    p = f"{path}[{i}]"
                    if i >= la:
                        diffs.append({"path": p, "change": "added", "to": b[i]})
                    elif i >= lb:
                        diffs.append({"path": p, "change": "removed", "from": a[i]})
                    else:
                        if a[i] != b[i]:
                            diffs.extend(deep_diff(a[i], b[i], p))
            else:
                diffs.append({"path": path, "change": "changed", "from": a, "to": b})
            return diffs
        
        diff_list = deep_diff(l.content or {}, r.content or {})
        
        breadcrumb_items = [
            {"label": "Dashboard", "url": "/"},
            {"label": "Baselines", "url": "/baselines"},
            {"label": "Compare", "url": None}
        ]
        
        return templates.TemplateResponse("baseline_compare.html", {
            "request": request, 
            "left": l, 
            "right": r, 
            "diff": diff_list,
            "breadcrumb_items": breadcrumb_items
        })
    finally:
        db.close()

# Scans API
def list_scans(api_key=Depends(require_api_key), db: Session = Depends(get_db)):
    # RBAC: viewers and admins can list
    rows = db.query(Scan).order_by(Scan.created_at.desc()).limit(100).all()
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "type": r.scan_type,
            "target": r.target_path,
            "passed": bool(r.passed),
            "critical": r.critical_count,
            "high": r.high_count,
            "medium": r.medium_count,
            "low": r.low_count,
        }
        for r in rows
    ]

@app.get("/api/v1/scans")
def list_scans(request: Request, api_key=Depends(require_api_key), db: Session = Depends(get_db), type: str | None = None, passed: str | None = None, limit: int = 50, offset: int = 0):
    # Require tenant context
    tenant_id = require_tenant(request, db)
    
    q = db.query(Scan)
    # Filter by tenant_id
    q = filter_by_tenant(q, Scan, tenant_id)
    if type:
        q = q.filter(Scan.scan_type == type)
    if passed in ("true","false"):
        q = q.filter(Scan.passed == (passed == "true"))
    rows = q.order_by(Scan.created_at.desc()).limit(min(limit, 200)).offset(offset).all()
    return [
        {
            "id": r.id,
            "created_at": r.created_at.isoformat(),
            "type": r.scan_type,
            "target": r.target_path,
            "passed": bool(r.passed),
            "critical": r.critical_count,
            "high": r.high_count,
            "medium": r.medium_count,
            "low": r.low_count,
        }
        for r in rows
    ]

@app.get("/api/v1/dashboard/stats")
def dashboard_stats(request: Request, api_key=Depends(require_api_key), db: Session = Depends(get_db), type: str | None = None, passed: str | None = None, time_range: str | None = None):
    """Get dashboard statistics (tenant-scoped)"""
    # Require tenant context
    tenant_id = require_tenant(request, db)
    
    q = db.query(Scan)
    # Filter by tenant_id
    q = filter_by_tenant(q, Scan, tenant_id)
    
    # Apply filters
    if type:
        q = q.filter(Scan.scan_type == type)
    if passed in ("true","false"):
        q = q.filter(Scan.passed == (passed == "true"))
    
    # Apply time range filter
    if time_range:
        now = datetime.utcnow()
        if time_range == "7d":
            cutoff = now - timedelta(days=7)
        elif time_range == "30d":
            cutoff = now - timedelta(days=30)
        elif time_range == "90d":
            cutoff = now - timedelta(days=90)
        else:
            cutoff = None
        if cutoff:
            q = q.filter(Scan.created_at >= cutoff)
    
    total_scans = q.count()
    passed_scans = q.filter(Scan.passed == True).count()
    total_findings = q.with_entities(
        func.sum(Scan.critical_count + Scan.high_count + Scan.medium_count + Scan.low_count)
    ).scalar() or 0
    critical_count = q.with_entities(func.sum(Scan.critical_count)).scalar() or 0
    high_count = q.with_entities(func.sum(Scan.high_count)).scalar() or 0
    medium_count = q.with_entities(func.sum(Scan.medium_count)).scalar() or 0
    low_count = q.with_entities(func.sum(Scan.low_count)).scalar() or 0
    
    return {
        "total_scans": total_scans,
        "passed_scans": passed_scans,
        "pass_rate": round((passed_scans / total_scans * 100) if total_scans > 0 else 0, 1),
        "total_findings": int(total_findings),
        "critical_count": int(critical_count),
        "high_count": int(high_count),
        "medium_count": int(medium_count),
        "low_count": int(low_count),
    }

@app.get("/api/v1/dashboard/export")
def dashboard_export(request: Request, api_key=Depends(require_api_key), db: Session = Depends(get_db), format: str = "json", type: str | None = None, passed: str | None = None, time_range: str | None = None):
    """Export dashboard data as CSV or JSON (tenant-scoped)"""
    # Require tenant context
    tenant_id = require_tenant(request, db)
    
    q = db.query(Scan)
    # Filter by tenant_id
    q = filter_by_tenant(q, Scan, tenant_id)
    
    # Apply filters
    if type:
        q = q.filter(Scan.scan_type == type)
    if passed in ("true","false"):
        q = q.filter(Scan.passed == (passed == "true"))
    
    # Apply time range filter
    if time_range:
        now = datetime.utcnow()
        if time_range == "7d":
            cutoff = now - timedelta(days=7)
        elif time_range == "30d":
            cutoff = now - timedelta(days=30)
        elif time_range == "90d":
            cutoff = now - timedelta(days=90)
        else:
            cutoff = None
        if cutoff:
            q = q.filter(Scan.created_at >= cutoff)
    
    rows = q.order_by(Scan.created_at.desc()).all()
    
    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Created At", "Type", "Target", "Passed", "Critical", "High", "Medium", "Low", "Total Findings"])
        for r in rows:
            writer.writerow([
                r.id,
                r.created_at.isoformat() if r.created_at else "",
                r.scan_type,
                r.target_path,
                "Yes" if r.passed else "No",
                r.critical_count or 0,
                r.high_count or 0,
                r.medium_count or 0,
                r.low_count or 0,
                (r.critical_count or 0) + (r.high_count or 0) + (r.medium_count or 0) + (r.low_count or 0)
            ])
        output.seek(0)
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=sentrascan-dashboard-export.csv"}
        )
    else:
        # JSON format
        return {
            "exported_at": datetime.utcnow().isoformat(),
            "filters": {
                "type": type,
                "passed": passed,
                "time_range": time_range
            },
            "total_scans": len(rows),
            "scans": [
                {
                    "id": r.id,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                    "type": r.scan_type,
                    "target": r.target_path,
                    "passed": bool(r.passed),
                    "critical": r.critical_count or 0,
                    "high": r.high_count or 0,
                    "medium": r.medium_count or 0,
                    "low": r.low_count or 0,
                    "total_findings": (r.critical_count or 0) + (r.high_count or 0) + (r.medium_count or 0) + (r.low_count or 0)
                }
                for r in rows
            ]
        }

@app.get("/api/v1/scans/{scan_id}")
def get_scan(scan_id: str, request: Request, api_key=Depends(require_api_key), db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Scan not found")
    findings = db.query(Finding).filter(Finding.scan_id == scan_id).all()
    return {
        "scan": {
            "id": scan.id,
            "created_at": scan.created_at.isoformat(),
            "type": scan.scan_type,
            "target": scan.target_path,
            "passed": bool(scan.passed),
            "critical": scan.critical_count,
            "high": scan.high_count,
            "medium": scan.medium_count,
            "low": scan.low_count,
        },
        "findings": [
            {
                "id": f.id,
                "scanner": f.scanner,
                "severity": f.severity,
                "category": f.category,
                "title": f.title,
                "description": f.description,
                "location": f.location,
            }
            for f in findings
        ],
    }

@app.get("/api/v1/scans/{scan_id}/report")
def download_report(scan_id: str, api_key=Depends(require_api_key), db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Scan not found")
    # Reconstruct a normalized report similar to to_report
    return {
        "scan_id": scan.id,
        "timestamp": scan.created_at.isoformat(),
        "gate_result": {
            "passed": bool(scan.passed),
            "total_findings": scan.total_findings,
            "critical_count": scan.critical_count,
            "high_count": scan.high_count,
            "medium_count": scan.medium_count,
            "low_count": scan.low_count,
        },
    }

@app.get("/api/v1/scans/{scan_id}/sbom")
def download_sbom(scan_id: str, api_key=Depends(require_api_key), db: Session = Depends(get_db)):
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Scan not found")
    if not scan.sbom_id:
        raise HTTPException(404, "No SBOM for this scan")
    from sentrascan.core.models import SBOM as SBOMModel
    sb = db.query(SBOMModel).filter(SBOMModel.id == scan.sbom_id).first()
    if not sb:
        raise HTTPException(404, "SBOM not found")
    return sb.content

from fastapi import Form

@app.get("/login")
def ui_login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})

@app.post("/login")
def ui_login_post(
    request: Request, 
    response: Response, 
    email: str = Form(None),
    password: str = Form(None),
    api_key: str = Form(None)
):
    """
    Handle login with either email/password or API key authentication.
    """
    db = get_db_session()
    try:
        # Determine authentication method
        if email and password:
            # User authentication with email/password
            try:
                user = authenticate_user(db, email, password)
                if not user:
                    logger.warning(
                        "login_failed",
                        reason="invalid_credentials",
                        email=mask_email(email),
                        client_ip=request.client.host if request.client else "unknown"
                    )
                    return templates.TemplateResponse(
                        "login.html", 
                        {"request": request, "error": "Invalid email or password"}, 
                        status_code=401
                    )
                
                # Create session using session management module
                signed_session = create_session(user, db)
                
                logger.info(
                    "login_success",
                    user_id=user.id,
                    email=mask_email(email),
                    role=user.role,
                    tenant_id=user.tenant_id,
                    client_ip=request.client.host if request.client else "unknown"
                )
                
                # Capture telemetry
                telemetry.capture_auth_event(
                    event_type="login",
                    success=True,
                    user_id=user.id,
                    tenant_id=user.tenant_id
                )
                
                resp = RedirectResponse(url="/", status_code=302)
                from sentrascan.core.session import SESSION_TIMEOUT_HOURS
                resp.set_cookie(
                    SESSION_COOKIE, 
                    signed_session, 
                    httponly=True, 
                    samesite="strict",
                    secure=os.environ.get("SENTRASCAN_COOKIE_SECURE", "false").lower() == "true",
                    max_age=SESSION_TIMEOUT_HOURS * 3600
                )
                return resp
            except HTTPException as e:
                return templates.TemplateResponse(
                    "login.html", 
                    {"request": request, "error": e.detail}, 
                    status_code=e.status_code
                )
        
        elif api_key:
            # API key authentication
            masked_key = mask_api_key(api_key)
            rec = db.query(APIKey).filter(
                APIKey.key_hash == APIKey.hash_key(api_key), 
                APIKey.is_revoked == False
            ).first()
            if not rec:
                logger.warning(
                    "login_failed",
                    reason="invalid_api_key",
                    api_key_masked=masked_key,
                    client_ip=request.client.host if request.client else "unknown"
                )
                return templates.TemplateResponse(
                    "login.html", 
                    {"request": request, "error": "Invalid API key"}, 
                    status_code=401
                )
            
            logger.info(
                "login_success",
                api_key_id=rec.id,
                role=rec.role,
                api_key_masked=masked_key,
                client_ip=request.client.host if request.client else "unknown"
            )
            
            # Capture telemetry
            telemetry.capture_auth_event(
                event_type="login",
                success=True,
                api_key_id=rec.id,
                role=rec.role
            )
            
            resp = RedirectResponse(url="/", status_code=302)
            resp.set_cookie(SESSION_COOKIE, sign(api_key), httponly=True, samesite="lax")
            return resp
        else:
            # No credentials provided
            return templates.TemplateResponse(
                "login.html", 
                {"request": request, "error": "Please provide either email/password or API key"}, 
                status_code=400
            )
    finally:
        db.close()

@app.get("/users")
def ui_users(request: Request):
    """User management page"""
    db = get_db_session()
    try:
        user = get_session_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        
        # Check permission
        if not check_permission(user, "user.read"):
            raise HTTPException(403, "Permission denied")
        
        # Get tenant info
        tenant = None
        if hasattr(user, 'tenant_id') and user.tenant_id:
            tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        
        breadcrumb_items = [
            {"label": "Dashboard", "url": "/"},
            {"label": "User Management", "url": "/users"}
        ]
        
        return templates.TemplateResponse(
            "users.html",
            {
                "request": request,
                "user": user,
                "tenant": tenant,
                "breadcrumb_items": breadcrumb_items
            }
        )
    finally:
        db.close()

@app.get("/docs")
def ui_docs(request: Request, page: str = "getting-started"):
    """Documentation viewer page"""
    db = get_db_session()
    try:
        user = get_session_user(request, db)
        tenant = None
        if user:
            # Handle both User and APIKey objects
            tenant_id = None
            if hasattr(user, 'tenant_id') and user.tenant_id:
                tenant_id = user.tenant_id
            
            if tenant_id:
                from sentrascan.core.models import Tenant
                tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        
        return templates.TemplateResponse(
            "docs.html",
            {"request": request, "user": user, "tenant": tenant, "page": page}
        )
    finally:
        db.close()

@app.get("/api/v1/docs/raw/{file_path:path}")
def get_docs_file(file_path: str):
    """Serve raw markdown documentation files"""
    import os
    from pathlib import Path
    
    # Security: prevent path traversal
    if '..' in file_path or file_path.startswith('/'):
        raise HTTPException(400, "Invalid file path")
    
    # Construct file path
    docs_dir = Path(__file__).parent.parent.parent / "docs"
    file_path_obj = docs_dir / file_path
    
    # Ensure file is within docs directory
    try:
        file_path_obj.resolve().relative_to(docs_dir.resolve())
    except ValueError:
        raise HTTPException(400, "Invalid file path")
    
    # Check if file exists
    if not file_path_obj.exists() or not file_path_obj.is_file():
        raise HTTPException(404, "File not found")
    
    # Read and return file
    try:
        content = file_path_obj.read_text(encoding='utf-8')
        return Response(content=content, media_type="text/markdown; charset=utf-8")
    except Exception as e:
        logger.error("error_reading_docs_file", file_path=file_path, error=str(e))
        raise HTTPException(500, "Error reading file")

@app.get("/api/v1/docs/raw/{file_path:path}")
def get_docs_file(file_path: str):
    """Serve raw markdown documentation files"""
    import os
    from pathlib import Path
    
    # Security: prevent path traversal
    if '..' in file_path or file_path.startswith('/'):
        raise HTTPException(400, "Invalid file path")
    
    # Construct file path
    docs_dir = Path(__file__).parent.parent.parent / "docs"
    file_path_obj = docs_dir / file_path
    
    # Ensure file is within docs directory
    try:
        file_path_obj.resolve().relative_to(docs_dir.resolve())
    except ValueError:
        raise HTTPException(400, "Invalid file path")
    
    # Check if file exists
    if not file_path_obj.exists() or not file_path_obj.is_file():
        raise HTTPException(404, "File not found")
    
    # Read and return file
    try:
        content = file_path_obj.read_text(encoding='utf-8')
        return Response(content=content, media_type="text/markdown; charset=utf-8")
    except Exception as e:
        logger.error("error_reading_docs_file", file_path=file_path, error=str(e))
        raise HTTPException(500, "Error reading file")

@app.get("/tenant-settings")
def ui_tenant_settings(request: Request):
    """Tenant Settings management page"""
    db = get_db_session()
    try:
        user = get_session_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        
        # Check permission (tenant admin required for update, but viewer can view)
        if not check_permission(user, "tenant_settings.view"):
            raise HTTPException(403, "Permission denied: tenant_settings.view required")
        
        # Get tenant info
        tenant = None
        if hasattr(user, 'tenant_id') and user.tenant_id:
            tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        
        breadcrumb_items = [
            {"label": "Dashboard", "url": "/"},
            {"label": "Tenant Settings", "url": "/tenant-settings"}
        ]
        
        return templates.TemplateResponse(
            "tenant_settings.html",
            {
                "request": request,
                "user": user,
                "tenant": tenant,
                "breadcrumb_items": breadcrumb_items
            }
        )
    finally:
        db.close()

@app.get("/analytics")
def ui_analytics(request: Request):
    """Analytics dashboard page"""
    db = get_db_session()
    try:
        user = get_session_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        
        # Get tenant info
        tenant = None
        if hasattr(user, 'tenant_id') and user.tenant_id:
            tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        
        breadcrumb_items = [
            {"label": "Dashboard", "url": "/"},
            {"label": "Analytics", "url": "/analytics"}
        ]
        
        return templates.TemplateResponse(
            "analytics.html",
            {
                "request": request,
                "user": user,
                "tenant": tenant,
                "breadcrumb_items": breadcrumb_items
            }
        )
    finally:
        db.close()

@app.get("/tenants")
def ui_tenants(request: Request):
    """Tenant management page (super admin only)"""
    db = get_db_session()
    try:
        user = get_session_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        
        # Check super_admin role
        if not check_role(user, "super_admin"):
            raise HTTPException(403, "Super admin access required")
        
        breadcrumb_items = [
            {"label": "Dashboard", "url": "/"},
            {"label": "Tenant Management", "url": "/tenants"}
        ]
        
        return templates.TemplateResponse(
            "tenants.html",
            {
                "request": request,
                "user": user,
                "breadcrumb_items": breadcrumb_items
            }
        )
    finally:
        db.close()

@app.get("/api-keys")
def ui_api_keys(request: Request):
    """API Keys management page"""
    db = get_db_session()
    try:
        user = get_session_user(request, db)
        if not user or user.role != "admin":
            return RedirectResponse(url="/login", status_code=302)
        
        breadcrumb_items = [
            {"label": "Dashboard", "url": "/"},
            {"label": "API Keys", "url": "/api-keys"}
        ]
        
        return templates.TemplateResponse(
            "api_keys.html",
            {
                "request": request,
                "breadcrumb_items": breadcrumb_items
            }
        )
    finally:
        db.close()

@app.get("/findings")
def ui_findings_aggregate(request: Request):
    """Aggregate findings view across all scans"""
    db = get_db_session()
    try:
        user = get_session_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        
        # Get query parameters
        severity = request.query_params.get("severity")
        category = request.query_params.get("category")
        scanner = request.query_params.get("scanner")
        scan_id = request.query_params.get("scan_id")
        page = int(request.query_params.get("page", 1))
        page_size = int(request.query_params.get("page_size", 50))
        sort = request.query_params.get("sort", "created_at")
        order = request.query_params.get("order", "desc")
        
        offset = (page - 1) * page_size
        
        # Get tenant_id for filtering
        tenant_id = None
        if isinstance(user, User):
            tenant_id = user.tenant_id
        elif hasattr(user, 'tenant_id'):
            tenant_id = user.tenant_id
        
        if not tenant_id:
            tenant_id = extract_tenant_from_request(request, db)
        
        if not tenant_id:
            return RedirectResponse(url="/login?error=tenant_required", status_code=302)
        
        # Get unique values for filter dropdowns (tenant-scoped)
        q_findings = db.query(Finding)
        q_findings = filter_by_tenant(q_findings, Finding, tenant_id)
        all_findings = q_findings.all()
        categories = sorted(set(f.category for f in all_findings if f.category))
        scanners = sorted(set(f.scanner for f in all_findings if f.scanner))
        severities = ["critical", "high", "medium", "low"]
        
        # Get scans for scan filter (tenant-scoped)
        q_scans = db.query(Scan)
        q_scans = filter_by_tenant(q_scans, Scan, tenant_id)
        scans = q_scans.order_by(Scan.created_at.desc()).limit(100).all()
        
        # Get tenant info for display
        tenant = None
        if tenant_id:
            tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
        
        breadcrumb_items = [
            {"label": "Dashboard", "url": "/"},
            {"label": "All Findings", "url": "/findings"}
        ]
        
        return templates.TemplateResponse(
            "findings_aggregate.html",
            {
                "request": request,
                "user": user,
                "tenant": tenant,
                "breadcrumb_items": breadcrumb_items,
                "categories": categories,
                "scanners": scanners,
                "severities": severities,
                "scans": scans,
                "filters": {
                    "severity": severity,
                    "category": category,
                    "scanner": scanner,
                    "scan_id": scan_id
                },
                "pagination": {
                    "page": page,
                    "page_size": page_size,
                    "sort": sort,
                    "order": order
                }
            }
        )
    finally:
        db.close()

@app.get("/logout")
def ui_logout():
    resp = RedirectResponse(url="/login", status_code=302)
    resp.delete_cookie(SESSION_COOKIE)
    return resp

@app.get("/")
def ui_home(request: Request, type: str | None = None, passed: str | None = None, time_range: str | None = None, date_from: str | None = None, date_to: str | None = None, search: str | None = None, sort: str | None = None, order: str | None = None, page: int = 1, page_size: int = 20):
    db = get_db_session()
    try:
        user = get_session_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        
        # Get tenant_id and filter queries
        tenant_id = None
        if isinstance(user, User):
            tenant_id = user.tenant_id
        elif hasattr(user, 'tenant_id'):
            tenant_id = user.tenant_id
        
        if not tenant_id:
            tenant_id = extract_tenant_from_request(request, db)
        
        if not tenant_id:
            return RedirectResponse(url="/login?error=tenant_required", status_code=302)
        
        q = db.query(Scan)
        # Filter by tenant_id
        q = filter_by_tenant(q, Scan, tenant_id)
        
        # Apply filters
        if type:
            q = q.filter(Scan.scan_type == type)
        if passed in ("true","false"):
            q = q.filter(Scan.passed == (passed == "true"))
        
        # Apply search filter
        if search:
            search_term = f"%{search}%"
            q = q.filter(
                or_(
                    Scan.target_path.ilike(search_term),
                    Scan.id.ilike(search_term),
                    Scan.scan_type.ilike(search_term)
                )
            )
        
        # Apply time range filter
        cutoff = None
        if time_range:
            now = datetime.utcnow()
            if time_range == "7d":
                cutoff = now - timedelta(days=7)
            elif time_range == "30d":
                cutoff = now - timedelta(days=30)
            elif time_range == "90d":
                cutoff = now - timedelta(days=90)
            else:
                cutoff = None
            if cutoff:
                q = q.filter(Scan.created_at >= cutoff)
        
        # Apply sorting
        sort_order = order if order in ('asc', 'desc') else 'desc'
        if sort == 'time':
            q = q.order_by(Scan.created_at.desc() if sort_order == 'desc' else Scan.created_at.asc())
        elif sort == 'type':
            q = q.order_by(Scan.scan_type.desc() if sort_order == 'desc' else Scan.scan_type.asc())
        elif sort == 'target':
            q = q.order_by(Scan.target_path.desc() if sort_order == 'desc' else Scan.target_path.asc())
        elif sort == 'status':
            q = q.order_by(Scan.passed.desc() if sort_order == 'desc' else Scan.passed.asc())
        elif sort == 'critical':
            q = q.order_by(Scan.critical_count.desc() if sort_order == 'desc' else Scan.critical_count.asc())
        elif sort == 'high':
            q = q.order_by(Scan.high_count.desc() if sort_order == 'desc' else Scan.high_count.asc())
        elif sort == 'medium':
            q = q.order_by(Scan.medium_count.desc() if sort_order == 'desc' else Scan.medium_count.asc())
        elif sort == 'low':
            q = q.order_by(Scan.low_count.desc() if sort_order == 'desc' else Scan.low_count.asc())
        else:
            # Default sort by time descending
            q = q.order_by(Scan.created_at.desc())
        
        page = max(page, 1)
        page_size = min(max(page_size, 10), 100)  # Clamp between 10 and 100
        total = q.count()
        rows = q.limit(page_size).offset((page-1)*page_size).all()
        
        # Calculate statistics for dashboard (tenant-scoped)
        stats_q = db.query(Scan)
        stats_q = filter_by_tenant(stats_q, Scan, tenant_id)
        if type:
            stats_q = stats_q.filter(Scan.scan_type == type)
        if passed in ("true","false"):
            stats_q = stats_q.filter(Scan.passed == (passed == "true"))
        if time_range and cutoff:
            stats_q = stats_q.filter(Scan.created_at >= cutoff)
        
        total_scans = stats_q.count()
        passed_scans = stats_q.filter(Scan.passed == True).count()
        total_findings = stats_q.with_entities(
            func.sum(Scan.critical_count + Scan.high_count + Scan.medium_count + Scan.low_count)
        ).scalar() or 0
        critical_count = stats_q.with_entities(func.sum(Scan.critical_count)).scalar() or 0
        high_count = stats_q.with_entities(func.sum(Scan.high_count)).scalar() or 0
        medium_count = stats_q.with_entities(func.sum(Scan.medium_count)).scalar() or 0
        low_count = stats_q.with_entities(func.sum(Scan.low_count)).scalar() or 0
        
        stats = {
            "total_scans": total_scans,
            "passed_scans": passed_scans,
            "total_findings": int(total_findings),
            "critical_count": int(critical_count),
            "high_count": int(high_count),
            "medium_count": int(medium_count),
            "low_count": int(low_count),
        }
        
        # Check if this is a dashboard request (no explicit page or sort params, or dashboard template requested)
        use_dashboard = not sort and page == 1
        
        if use_dashboard:
            # Get tenant info for display
            tenant = None
            if tenant_id:
                tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
            
            return templates.TemplateResponse("dashboard.html", {
                "request": request,
                "user": user,
                "tenant": tenant,
                "scans": rows,
                "page": page,
                "has_next": (page*page_size) < total,
                "filters": {
                    "type": type or "", 
                    "passed": passed or "", 
                    "time_range": time_range or "",
                    "date_from": date_from or "",
                    "date_to": date_to or "",
                    "search": search or ""
                },
                "stats": stats
            })
        else:
            # Use index.html for scan list view
            return templates.TemplateResponse("index.html", {
                "request": request,
                "scans": rows,
                "page": page,
                "has_next": (page*page_size) < total,
                "total": total,
                "page_size": page_size,
                "filters": {
                    "type": type or "", 
                    "passed": passed or "", 
                    "time_range": time_range or "",
                    "date_from": date_from or "",
                    "date_to": date_to or "",
                    "search": search or ""
                },
                "sort": sort or "",
                "order": order or "desc"
            })
    finally:
        db.close()

@app.get("/ui/scan")
def ui_scan_form(request: Request):
    db = get_db_session()
    try:
        user = get_session_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        
        # Check permission
        if not check_permission(user, "scan.create"):
            raise HTTPException(403, "Permission denied: scan.create required")
        
        breadcrumb_items = [
            {"label": "Dashboard", "url": "/"},
            {"label": "Run Scan", "url": "/ui/scan"}
        ]
        
        # Get tenant info for display
        tenant = None
        if hasattr(user, 'tenant_id') and user.tenant_id:
            tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
        
        return templates.TemplateResponse("scan_forms.html", {
            "request": request,
            "user": user,
            "tenant": tenant,
            "breadcrumb_items": breadcrumb_items
        })
    finally:
        db.close()

@app.post("/ui/scan/model")
def ui_scan_model(request: Request, api_key: str = Form(None), model_path: str = Form(...), strict: bool = Form(False), generate_sbom: bool = Form(True), policy: str | None = Form(None), run_async: bool = Form(False)):
    # prefer session user; fallback to form
    db = get_db_session()
    try:
        user = get_session_user(request, db)
        rec = user
        if not rec and api_key:
            rec = db.query(APIKey).filter(APIKey.key_hash == APIKey.hash_key(api_key), APIKey.is_revoked == False).first()
        if not rec or rec.role != "admin":
            return RedirectResponse(url="/login", status_code=302)
        
        # Get tenant_id from user or API key
        tenant_id = None
        if hasattr(rec, 'tenant_id') and rec.tenant_id:
            tenant_id = rec.tenant_id
        elif isinstance(rec, APIKey) and hasattr(rec, 'tenant_id') and rec.tenant_id:
            tenant_id = rec.tenant_id
        
        if not tenant_id:
            # Try to extract from request
            tenant_id = extract_tenant_from_request(request, db)
        
        if not tenant_id:
            return RedirectResponse(url="/login?error=tenant_required", status_code=302)
        
        pe = PolicyEngine.from_file(policy, tenant_id=tenant_id, db=db) if policy else PolicyEngine.default_model(tenant_id=tenant_id, db=db)
        ms = ModelScanner(policy=pe)
        if run_async:
            from sentrascan.core.models import Scan as ScanModel
            scan = ScanModel(scan_type="model", target_path=model_path, scan_status="queued", tenant_id=tenant_id)
            db.add(scan); db.commit()
            def _done(scan_id: str):
                pass
            job_queue.put({
                "type": "model",
                "paths": [model_path],
                "sbom_path": "./sboms/ui_sbom.json" if generate_sbom else None,
                "strict": strict,
                "timeout": 0,
                "existing_scan_id": scan.id,
                "tenant_id": tenant_id,
                "on_done": _done,
            })
            return RedirectResponse(url=f"/scan/{scan.id}", status_code=303)
        else:
            scan = ms.scan(paths=[model_path], sbom_path="./sboms/ui_sbom.json" if generate_sbom else None, strict=strict, timeout=0, db=db, tenant_id=tenant_id)
            return RedirectResponse(url=f"/scan/{scan.id}", status_code=303)
    finally:
        db.close()

@app.post("/ui/scan/mcp")
def ui_scan_mcp(request: Request, api_key: str = Form(None), auto_discover: bool = Form(True), config_paths: str | None = Form(None), policy: str | None = Form(None), run_async: bool = Form(False)):
    db = get_db_session()
    try:
        user = get_session_user(request, db)
        rec = user
        # Get tenant_id from user or API key
        tenant_id = None
        if hasattr(rec, 'tenant_id') and rec.tenant_id:
            tenant_id = rec.tenant_id
        elif isinstance(rec, APIKey) and hasattr(rec, 'tenant_id') and rec.tenant_id:
            tenant_id = rec.tenant_id
        
        if not tenant_id:
            # Try to extract from request
            tenant_id = extract_tenant_from_request(request, db)
        
        if not tenant_id:
            return RedirectResponse(url="/login?error=tenant_required", status_code=302)
        if not rec and api_key:
            rec = db.query(APIKey).filter(APIKey.key_hash == APIKey.hash_key(api_key), APIKey.is_revoked == False).first()
        if not rec or rec.role != "admin":
            return RedirectResponse(url="/login", status_code=302)
        pe = PolicyEngine.from_file(policy, tenant_id=tenant_id, db=db) if policy else PolicyEngine.default_mcp(tenant_id=tenant_id, db=db)
        scanner = MCPScanner(policy=pe)
        paths = [p.strip() for p in (config_paths or "").split("\n") if p.strip()] or []
        if run_async:
            from sentrascan.core.models import Scan as ScanModel
            scan = ScanModel(scan_type="mcp", target_path=",".join(paths or ["auto"]), scan_status="queued", tenant_id=tenant_id)
            db.add(scan); db.commit()
            def _done(scan_id: str):
                pass
            job_queue.put({
                "type": "mcp",
                "config_paths": paths,
                "auto_discover": auto_discover,
                "timeout": 60,
                "existing_scan_id": scan.id,
                "tenant_id": tenant_id,
                "on_done": _done,
            })
            return RedirectResponse(url=f"/scan/{scan.id}", status_code=303)
        else:
            scan = scanner.scan(config_paths=paths, auto_discover=auto_discover, timeout=60, db=db, tenant_id=tenant_id)
            return RedirectResponse(url=f"/scan/{scan.id}", status_code=303)
    finally:
        db.close()

@app.get("/api/v1/findings")
def list_all_findings(
    request: Request,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db),
    severity: str | None = None,
    category: str | None = None,
    scanner: str | None = None,
    scan_id: str | None = None,
    limit: int = 100,
    offset: int = 0,
    sort: str = "created_at",
    order: str = "desc"
):
    """List all findings across all scans with filtering and pagination"""
    # Require tenant context
    tenant_id = require_tenant(request, db)
    
    query = db.query(Finding).join(Scan)
    # Filter by tenant_id
    query = filter_by_tenant(query, Finding, tenant_id)
    
    # Apply filters
    if severity:
        query = query.filter(Finding.severity == severity)
    if category:
        query = query.filter(Finding.category == category)
    if scanner:
        query = query.filter(Finding.scanner == scanner)
    if scan_id:
        query = query.filter(Finding.scan_id == scan_id)
    
    # Apply sorting
    if sort == "created_at":
        # Sort by scan created_at
        sort_column = Scan.created_at
    elif sort == "severity":
        sort_column = Finding.severity
    elif sort == "category":
        sort_column = Finding.category
    elif sort == "scanner":
        sort_column = Finding.scanner
    elif sort == "title":
        sort_column = Finding.title
    else:
        sort_column = Scan.created_at  # Default
    
    if order == "desc":
        query = query.order_by(sort_column.desc())
    else:
        query = query.order_by(sort_column.asc())
    
    # Get total count before pagination
    total = query.count()
    
    # Apply pagination
    findings = query.offset(offset).limit(limit).all()
    
    return {
        "findings": [
            {
                "id": f.id,
                "scan_id": f.scan_id,
                "scan_type": f.scan.scan_type if f.scan else None,
                "scan_target": f.scan.target_path if f.scan else None,
                "scan_created_at": f.scan.created_at.isoformat() if f.scan and f.scan.created_at else None,
                "severity": f.severity,
                "category": f.category,
                "scanner": f.scanner,
                "title": f.title,
                "description": f.description,
                "location": f.location,
                "remediation": f.remediation,
                "evidence": f.evidence
            }
            for f in findings
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
        "has_more": (offset + limit) < total
    }

@app.get("/api/v1/scans/{scan_id}/findings/export")
def export_findings(scan_id: str, request: Request, api_key=Depends(require_api_key), db: Session = Depends(get_db), format: str = "csv"):
    """Export findings for a scan as CSV or JSON"""
    # Require tenant context
    tenant_id = require_tenant(request, db)
    
    q = db.query(Scan).filter(Scan.id == scan_id)
    q = filter_by_tenant(q, Scan, tenant_id)
    scan = q.first()
    if not scan:
        raise HTTPException(404, "Scan not found")
    
    q = db.query(Finding).filter(Finding.scan_id == scan_id)
    q = filter_by_tenant(q, Finding, tenant_id)
    findings = q.all()
    
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(["ID", "Severity", "Category", "Scanner", "Title", "Description", "Location"])
        for f in findings:
            writer.writerow([
                f.id,
                f.severity,
                f.category or "",
                f.scanner or "",
                f.title or "",
                (f.description or "").replace("\n", " ").replace("\r", " ")[:500],  # Truncate long descriptions
                f.location or ""
            ])
        output.seek(0)
        return Response(
            content=output.getvalue(),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=sentrascan-findings-{scan_id[:8]}.csv"}
        )
    else:
        return {
            "scan_id": scan_id,
            "exported_at": datetime.utcnow().isoformat(),
            "total_findings": len(findings),
            "findings": [
                {
                    "id": f.id,
                    "severity": f.severity,
                    "category": f.category,
                    "scanner": f.scanner,
                    "title": f.title,
                    "description": f.description,
                    "location": f.location
                }
                for f in findings
            ]
        }

@app.get("/scan/{scan_id}")
def ui_scan_detail(scan_id: str, request: Request):
    db = get_db_session()
    try:
        user = get_session_user(request, db)
        if not user:
            return RedirectResponse(url="/login", status_code=302)
        
        # Get tenant_id for filtering
        tenant_id = None
        if isinstance(user, User):
            tenant_id = user.tenant_id
        elif hasattr(user, 'tenant_id'):
            tenant_id = user.tenant_id
        
        if not tenant_id:
            tenant_id = extract_tenant_from_request(request, db)
        
        if not tenant_id:
            return RedirectResponse(url="/login?error=tenant_required", status_code=302)
        
        # Filter by tenant
        q_scan = db.query(Scan).filter(Scan.id == scan_id)
        q_scan = filter_by_tenant(q_scan, Scan, tenant_id)
        scan = q_scan.first()
        
        if not scan:
            raise HTTPException(404, "Scan not found")
        
        q_findings = db.query(Finding).filter(Finding.scan_id == scan_id)
        q_findings = filter_by_tenant(q_findings, Finding, tenant_id)
        findings = q_findings.all()
        
        # Get existing baseline for this scan if any
        existing_baseline = db.query(Baseline).filter(Baseline.scan_id == scan_id).first()
        
        breadcrumb_items = [
            {"label": "Dashboard", "url": "/"},
            {"label": "Scans", "url": "/"},
            {"label": f"Scan {scan_id[:8]}...", "url": f"/scan/{scan_id}"}
        ]
        
        return templates.TemplateResponse(
            "scan_detail.html",
            {
                "request": request, 
                "scan": scan, 
                "findings": findings,
                "existing_baseline": existing_baseline,
                "breadcrumb_items": breadcrumb_items
            },
        )
    finally:
        db.close()

@app.get("/api/v1/scans/{scan_id}/status/stream")
async def stream_scan_status(scan_id: str, request: Request):
    """Server-Sent Events endpoint for real-time scan status updates"""
    async def event_generator():
        last_status = None
        last_findings_count = None
        
        while True:
            # Check if client disconnected
            if await request.is_disconnected():
                break
            
            db = get_db_session()
            try:
                scan = db.query(Scan).filter(Scan.id == scan_id).first()
                if not scan:
                    yield f"data: {json.dumps({'error': 'Scan not found'})}\n\n"
                    break
                
                # Check if status changed
                current_status = scan.scan_status
                current_findings = scan.total_findings or 0
                
                if current_status != last_status or current_findings != last_findings_count:
                    data = {
                        "scan_id": scan_id,
                        "status": current_status,
                        "passed": bool(scan.passed),
                        "total_findings": current_findings,
                        "critical_count": scan.critical_count or 0,
                        "high_count": scan.high_count or 0,
                        "medium_count": scan.medium_count or 0,
                        "low_count": scan.low_count or 0,
                        "duration_ms": scan.duration_ms or 0,
                        "timestamp": scan.created_at.isoformat() if scan.created_at else None
                    }
                    
                    yield f"data: {json.dumps(data)}\n\n"
                    
                    last_status = current_status
                    last_findings_count = current_findings
                    
                    # Stop streaming if scan is completed or failed
                    if current_status in ('completed', 'failed'):
                        yield f"data: {json.dumps({'status': 'completed', 'scan_id': scan_id})}\n\n"
                        break
                
                # Wait before next check
                await asyncio.sleep(2)  # Poll every 2 seconds
                
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                await asyncio.sleep(5)
            finally:
                db.close()
    
    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"  # Disable buffering in nginx
        }
    )

@app.get("/api/v1/scans/{scan_id}/status")
def get_scan_status(scan_id: str, db: Session = Depends(get_db)):
    """Get current scan status (REST endpoint for polling)"""
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    if not scan:
        raise HTTPException(404, "Scan not found")
    
    return {
        "scan_id": scan_id,
        "status": scan.scan_status,
        "passed": bool(scan.passed),
        "total_findings": scan.total_findings or 0,
        "critical_count": scan.critical_count or 0,
        "high_count": scan.high_count or 0,
        "medium_count": scan.medium_count or 0,
        "low_count": scan.low_count or 0,
        "duration_ms": scan.duration_ms or 0,
        "timestamp": scan.created_at.isoformat() if scan.created_at else None
    }

@app.post("/api/v1/api-keys")
def create_api_key(request: Request, name: str | None = Form(None), db: Session = Depends(get_db)):
    """
    Create a new API key with optional name.
    Returns the generated API key (plaintext) and key metadata.
    Associates the key with the current user and tenant.
    """
    # Check if user is authenticated (via session or API key)
    user = get_session_user(request, db)
    if not user or not check_permission(user, "api_key.create"):
        raise HTTPException(403, "Permission denied: api_key.create required")
    
    # Get tenant_id from user
    tenant_id = None
    user_role = None
    
    if isinstance(user, User):
        tenant_id = user.tenant_id
        user_role = user.role
    elif hasattr(user, 'tenant_id'):
        tenant_id = user.tenant_id
        user_role = getattr(user, 'role', 'viewer')
    
    # If no tenant_id, try to extract from request
    if not tenant_id:
        tenant_id = extract_tenant_from_request(request, db)
    
    if not tenant_id:
        raise HTTPException(400, "Tenant context required to create API key")
    
    # Generate new API key
    new_key = generate_api_key()
    key_hash = APIKey.hash_key(new_key)
    
    # Check for hash collision (very unlikely but possible)
    existing = db.query(APIKey).filter(APIKey.key_hash == key_hash).first()
    if existing:
        # Retry generation (extremely rare case)
        new_key = generate_api_key()
        key_hash = APIKey.hash_key(new_key)
    
    # Determine role: inherit from user if available, otherwise default to viewer
    api_key_role = user_role if user_role else "viewer"
    
    # Create API key record with user and tenant association
    api_key_record = APIKey(
        name=name,
        key_hash=key_hash,
        role=api_key_role,
        tenant_id=tenant_id,
        user_id=user.id if isinstance(user, User) else None,
        is_revoked=False
    )
    db.add(api_key_record)
    db.commit()
    db.refresh(api_key_record)
    
    # Capture telemetry
    telemetry.capture_auth_event(
        event_type="api_key_created",
        success=True,
        api_key_id=api_key_record.id,
        created_by=user.id if user else None,
        key_name=name
    )
    
    logger.info(
        "api_key_created",
        api_key_id=api_key_record.id,
        created_by=user.id if user else None,
        key_name=name
    )
    
    return {
        "id": api_key_record.id,
        "name": api_key_record.name,
        "key": new_key,  # Return plaintext key (only shown once)
        "created_at": api_key_record.created_at.isoformat() if api_key_record.created_at else None
    }

@app.get("/api/v1/api-keys")
def list_api_keys(request: Request, db: Session = Depends(get_db)):
    """List all API keys (metadata only, no plaintext keys) - filtered by tenant"""
    user = get_session_user(request, db)
    if not user or not check_permission(user, "api_key.read"):
        raise HTTPException(403, "Permission denied: api_key.read required")
    
    # Get tenant_id from user or request
    tenant_id = None
    if isinstance(user, User):
        tenant_id = user.tenant_id
    elif hasattr(user, 'tenant_id'):
        tenant_id = user.tenant_id
    
    if not tenant_id:
        tenant_id = require_tenant(request, db)
    
    # Filter by tenant_id (unless super_admin)
    q = db.query(APIKey).filter(APIKey.is_revoked == False)
    if get_user_role(user) != "super_admin":
        q = q.filter(APIKey.tenant_id == tenant_id)
    
    # If user is associated, also filter by user_id
    if isinstance(user, User):
        q = q.filter(APIKey.user_id == user.id)
    
    keys = q.order_by(APIKey.created_at.desc()).all()
    return [
        {
            "id": key.id,
            "name": key.name,
            "role": key.role,
            "tenant_id": key.tenant_id,
            "user_id": key.user_id,
            "created_at": key.created_at.isoformat() if key.created_at else None,
            "is_revoked": key.is_revoked
        }
        for key in keys
    ]

@app.delete("/api/v1/api-keys/{key_id}")
def revoke_api_key(key_id: str, request: Request, db: Session = Depends(get_db)):
    """Revoke an API key"""
    user = get_session_user(request, db)
    if not user or not check_permission(user, "api_key.delete"):
        raise HTTPException(403, "Permission denied: api_key.delete required")
    
    key = db.query(APIKey).filter(APIKey.id == key_id).first()
    if not key:
        raise HTTPException(404, "API key not found")
    
    key.is_revoked = True
    db.commit()
    
    # Log security event
    log_security_event(
        db, "api_key_revoked", "api_key", key_id,
        user.id if user else None,
        key.tenant_id,
        {"key_name": key.name},
        request.client.host if request.client else None
    )
    
    # Capture telemetry
    telemetry.capture_auth_event(
        event_type="api_key_revoked",
        success=True,
        api_key_id=key_id,
        revoked_by=user.id if user else None
    )
    
    logger.info(
        "api_key_revoked",
        api_key_id=key_id,
        revoked_by=user.id if user else None
    )
    
    return {"message": "API key revoked", "id": key_id}

# User Authentication Endpoints
@app.post("/api/v1/users/register")
def register_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    tenant_id: str = Form(None),
    role: str = Form("viewer"),
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    Requires tenant_id (either from request context or provided).
    """
    # Sanitize and validate inputs
    email = sanitize_input(email)
    name = sanitize_input(name)
    password = sanitize_input(password)
    
    if not validate_email(email):
        raise HTTPException(400, "Invalid email format")
    
    # Get tenant_id from request context or form
    if not tenant_id:
        tenant_id = extract_tenant_from_request(request, db)
    
    if not tenant_id:
        raise HTTPException(400, "tenant_id is required")
    
    # Validate tenant_id format (UUID)
    if not validate_uuid(tenant_id):
        raise HTTPException(400, "Invalid tenant_id format")
    
    # Validate tenant exists and is active
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id, Tenant.is_active == True).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found or inactive")
    
    try:
        user = create_user(
            db=db,
            email=email,
            password=password,
            name=name,
            tenant_id=tenant_id,
            role=role
        )
        
        # Capture telemetry
        telemetry.capture_auth_event(
            event_type="user_registered",
            success=True,
            user_id=user.id,
            tenant_id=tenant_id
        )
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "tenant_id": user.tenant_id,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("user_registration_failed", error=str(e), exc_info=True)
        raise HTTPException(500, "Failed to create user")


@app.post("/api/v1/users/login")
def login_user(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Login a user with email and password.
    Returns a session cookie.
    """
    try:
        user = authenticate_user(db, email, password)
        if not user:
            raise HTTPException(401, "Invalid email or password")
        
        # Create session using session management module
        signed_session = create_session(user, db)
        
        # Capture telemetry
        telemetry.capture_auth_event(
            event_type="login",
            success=True,
            user_id=user.id,
            tenant_id=user.tenant_id
        )
        
        response = JSONResponse({
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "tenant_id": user.tenant_id,
                "role": user.role
            }
        })
        
        # Set session cookie with secure settings
        from sentrascan.core.session import SESSION_TIMEOUT_HOURS
        from sentrascan.core.security import generate_csrf_token, CSRF_COOKIE_NAME
        
        # Generate CSRF token
        csrf_token = generate_csrf_token()
        
        response.set_cookie(
            SESSION_COOKIE,
            signed_session,
            httponly=True,
            samesite="strict",  # Changed to strict for better CSRF protection
            secure=os.environ.get("SENTRASCAN_COOKIE_SECURE", "false").lower() == "true",  # HTTPS only in production
            max_age=SESSION_TIMEOUT_HOURS * 3600  # Configurable timeout
        )
        
        # Set CSRF token cookie
        response.set_cookie(
            CSRF_COOKIE_NAME,
            csrf_token,
            httponly=False,  # CSRF token must be accessible to JavaScript
            samesite="strict",
            secure=os.environ.get("SENTRASCAN_COOKIE_SECURE", "false").lower() == "true",
            max_age=SESSION_TIMEOUT_HOURS * 3600
        )
        
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error("login_failed", error=str(e), exc_info=True)
        raise HTTPException(500, "Login failed")


@app.post("/api/v1/users/logout")
def logout_user(request: Request, db: Session = Depends(get_db)):
    """
    Logout a user by clearing the session cookie.
    """
    # Capture telemetry and audit log before clearing session
    user = get_session_user(request, db)
    if user:
        log_authentication_event(
            db, "logout", user.id if hasattr(user, 'id') else None, True,
            request.client.host if request.client else None
        )
        telemetry.capture_auth_event(
            event_type="logout",
            success=True,
            user_id=user.id if hasattr(user, 'id') else None
        )
    
    # Clear session cookie
    response = JSONResponse({"message": "Logged out successfully"})
    response.delete_cookie(SESSION_COOKIE, httponly=True, samesite="lax")
    
    return response


# User Management Endpoints
@app.get("/api/v1/users")
def list_users(
    request: Request,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db),
    tenant_id: str | None = None,
    active_only: bool = True
):
    """
    List users. Requires admin role.
    Filters by tenant_id if provided, otherwise uses request tenant context.
    """
    # RBAC: require user.read permission
    if not check_permission(api_key, "user.read"):
        raise HTTPException(403, "Permission denied: user.read required")
    
    # Get tenant_id
    if not tenant_id:
        tenant_id = require_tenant(request, db)
    
    # Validate tenant access
    user_tenant_id = getattr(api_key, "tenant_id", None)
    if not validate_tenant_access(tenant_id, user_tenant_id, getattr(api_key, "role", None)):
        raise HTTPException(403, "Access denied to this tenant")
    
    # Query users
    q = db.query(User).filter(User.tenant_id == tenant_id)
    if active_only:
        q = q.filter(User.is_active == True)
    
    users = q.all()
    
    return [
        {
            "id": u.id,
            "email": u.email,
            "name": u.name,
            "role": u.role,
            "is_active": u.is_active,
            "created_at": u.created_at.isoformat() if u.created_at else None
        }
        for u in users
    ]


@app.post("/api/v1/users")
def create_user_endpoint(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
    name: str = Form(...),
    role: str = Form("viewer"),
    tenant_id: str = Form(None),
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """
    Create a new user. Requires admin role.
    """
    # RBAC: require user.read permission
    if not check_permission(api_key, "user.read"):
        raise HTTPException(403, "Permission denied: user.read required")
    
    # Get tenant_id
    if not tenant_id:
        tenant_id = require_tenant(request, db)
    
    # Validate tenant access
    user_tenant_id = getattr(api_key, "tenant_id", None)
    if not validate_tenant_access(tenant_id, user_tenant_id, getattr(api_key, "role", None)):
        raise HTTPException(403, "Access denied to this tenant")
    
    try:
        user = create_user(
            db=db,
            email=email,
            password=password,
            name=name,
            tenant_id=tenant_id,
            role=role
        )
        
        # Capture telemetry
        telemetry.capture_auth_event(
            event_type="user_created",
            success=True,
            user_id=user.id,
            tenant_id=tenant_id,
            created_by=getattr(api_key, "id", None)
        )
        
        return {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "tenant_id": user.tenant_id,
            "role": user.role,
            "created_at": user.created_at.isoformat() if user.created_at else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error("user_creation_failed", error=str(e), exc_info=True)
        raise HTTPException(500, "Failed to create user")


@app.put("/api/v1/users/{user_id}")
def update_user_endpoint(
    user_id: str,
    request: Request,
    name: str = Form(None),
    role: str = Form(None),
    password: str = Form(None),
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """
    Update a user. Requires admin role.
    """
    # RBAC: require user.read permission
    if not check_permission(api_key, "user.read"):
        raise HTTPException(403, "Permission denied: user.read required")
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    # Validate tenant access
    tenant_id = require_tenant(request, db)
    user_tenant_id = getattr(api_key, "tenant_id", None)
    if not validate_tenant_access(user.tenant_id, user_tenant_id, getattr(api_key, "role", None)):
        raise HTTPException(403, "Access denied to this user")
    
    # Update fields
    if name is not None:
        user.name = name
    if role is not None:
        user.role = role
    if password is not None:
        user = update_user_password(db, user, password)
        # Log password change
        log_security_event(
            db, "password_changed", "user", user.id,
            getattr(api_key, "id", None),
            user.tenant_id,
            {"changed_by": "admin"},
            request.client.host if request.client else None
        )
    
    db.commit()
    db.refresh(user)
    
    # Log security event
    log_security_event(
        db, "user_updated", "user", user.id,
        getattr(api_key, "id", None),
        user.tenant_id,
        {"updated_fields": ["name" if name else None, "role" if role else None, "password" if password else None]},
        request.client.host if request.client else None
    )
    
    # Capture telemetry
    telemetry.capture_auth_event(
        event_type="user_updated",
        success=True,
        user_id=user.id,
        updated_by=getattr(api_key, "id", None)
    )
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "role": user.role,
        "is_active": user.is_active
    }


@app.delete("/api/v1/users/{user_id}")
def deactivate_user_endpoint(
    user_id: str,
    request: Request,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """
    Deactivate a user (soft delete). Requires admin role.
    """
    # RBAC: require user.read permission
    if not check_permission(api_key, "user.read"):
        raise HTTPException(403, "Permission denied: user.read required")
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    # Validate tenant access
    tenant_id = require_tenant(request, db)
    user_tenant_id = getattr(api_key, "tenant_id", None)
    if not validate_tenant_access(user.tenant_id, user_tenant_id, getattr(api_key, "role", None)):
        raise HTTPException(403, "Access denied to this user")
    
    # Prevent deactivating yourself
    if hasattr(api_key, 'user_id') and api_key.user_id == user_id:
        raise HTTPException(400, "Cannot deactivate your own account")
    
    user = deactivate_user(db, user)
    
    # Capture telemetry
    telemetry.capture_auth_event(
        event_type="user_deactivated",
        success=True,
        user_id=user.id,
        deactivated_by=getattr(api_key, "id", None)
    )
    
    return {
        "id": user.id,
        "email": user.email,
        "is_active": False,
        "message": "User deactivated"
    }


@app.post("/api/v1/users/{user_id}/activate")
def activate_user_endpoint(
    user_id: str,
    request: Request,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """
    Activate a user account. Requires admin role.
    """
    # RBAC: require user.read permission
    if not check_permission(api_key, "user.read"):
        raise HTTPException(403, "Permission denied: user.read required")
    
    # Get user
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    # Validate tenant access
    tenant_id = require_tenant(request, db)
    user_tenant_id = getattr(api_key, "tenant_id", None)
    if not validate_tenant_access(user.tenant_id, user_tenant_id, getattr(api_key, "role", None)):
        raise HTTPException(403, "Access denied to this user")
    
    user = activate_user(db, user)
    
    # Capture telemetry
    telemetry.capture_auth_event(
        event_type="user_activated",
        success=True,
        user_id=user.id,
        activated_by=getattr(api_key, "id", None)
    )
    
    return {
        "id": user.id,
        "email": user.email,
        "is_active": True,
        "message": "User activated"
    }

# Tenant Management Endpoints (Super Admin only)
@app.get("/api/v1/tenants")
def list_tenants(
    request: Request,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db),
    active_only: bool = False
):
    """
    List all tenants. Requires super_admin role.
    """
    # RBAC: require super_admin role
    if not check_role(api_key, "super_admin"):
        raise HTTPException(403, "Super admin access required")
    
    # Query tenants
    q = db.query(Tenant)
    if active_only:
        q = q.filter(Tenant.is_active == True)
    
    tenants = q.order_by(Tenant.created_at.desc()).all()
    
    return [
        {
            "id": t.id,
            "name": t.name,
            "is_active": t.is_active,
            "created_at": t.created_at.isoformat() if t.created_at else None,
            "settings": t.settings or {}
        }
        for t in tenants
    ]


@app.post("/api/v1/tenants")
def create_tenant(
    request: Request,
    name: str = Form(...),
    settings: str = Form(None),  # JSON string
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """
    Create a new tenant. Requires super_admin role.
    """
    # RBAC: require super_admin role
    if not check_role(api_key, "super_admin"):
        raise HTTPException(403, "Super admin access required")
    
    # Check if tenant name already exists
    existing = db.query(Tenant).filter(Tenant.name == name).first()
    if existing:
        raise HTTPException(409, "Tenant with this name already exists")
    
    # Parse settings if provided
    tenant_settings = {}
    if settings:
        try:
            tenant_settings = json.loads(settings)
        except json.JSONDecodeError:
            raise HTTPException(400, "Invalid JSON in settings field")
    
    # Create tenant
    tenant = Tenant(
        name=name,
        is_active=True,
        settings=tenant_settings
    )
    
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    
    # Capture telemetry
    telemetry.capture_auth_event(
        event_type="tenant_created",
        success=True,
        tenant_id=tenant.id,
        created_by=getattr(api_key, "id", None)
    )
    
    logger.info(
        "tenant_created",
        tenant_id=tenant.id,
        tenant_name=name,
        created_by=getattr(api_key, "id", None)
    )
    
    return {
        "id": tenant.id,
        "name": tenant.name,
        "is_active": tenant.is_active,
        "created_at": tenant.created_at.isoformat() if tenant.created_at else None,
        "settings": tenant.settings or {}
    }


@app.get("/api/v1/tenants/{tenant_id}")
def get_tenant(
    tenant_id: str,
    request: Request,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """
    Get tenant details. Requires super_admin role.
    """
    # RBAC: require super_admin role
    if not check_role(api_key, "super_admin"):
        raise HTTPException(403, "Super admin access required")
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    
    # Get user count
    user_count = db.query(User).filter(User.tenant_id == tenant_id, User.is_active == True).count()
    
    # Get scan count
    scan_count = db.query(Scan).filter(Scan.tenant_id == tenant_id).count()
    
    return {
        "id": tenant.id,
        "name": tenant.name,
        "is_active": tenant.is_active,
        "created_at": tenant.created_at.isoformat() if tenant.created_at else None,
        "settings": tenant.settings or {},
        "stats": {
            "user_count": user_count,
            "scan_count": scan_count
        }
    }


@app.put("/api/v1/tenants/{tenant_id}")
def update_tenant(
    tenant_id: str,
    request: Request,
    name: str = Form(None),
    is_active: bool = Form(None),
    settings: str = Form(None),  # JSON string
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """
    Update a tenant. Requires super_admin role.
    """
    # RBAC: require super_admin role
    if not check_role(api_key, "super_admin"):
        raise HTTPException(403, "Super admin access required")
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    
    # Update name if provided
    if name is not None:
        # Check if new name conflicts with existing tenant
        existing = db.query(Tenant).filter(Tenant.name == name, Tenant.id != tenant_id).first()
        if existing:
            raise HTTPException(409, "Tenant with this name already exists")
        tenant.name = name
    
    # Update is_active if provided
    if is_active is not None:
        tenant.is_active = is_active
    
    # Update settings if provided
    if settings is not None:
        try:
            tenant_settings = json.loads(settings)
            # Merge with existing settings
            if tenant.settings:
                tenant.settings.update(tenant_settings)
            else:
                tenant.settings = tenant_settings
        except json.JSONDecodeError:
            raise HTTPException(400, "Invalid JSON in settings field")
    
    db.commit()
    db.refresh(tenant)
    
    # Capture telemetry
    telemetry.capture_auth_event(
        event_type="tenant_updated",
        success=True,
        tenant_id=tenant.id,
        updated_by=getattr(api_key, "id", None)
    )
    
    logger.info(
        "tenant_updated",
        tenant_id=tenant.id,
        updated_by=getattr(api_key, "id", None)
    )
    
    return {
        "id": tenant.id,
        "name": tenant.name,
        "is_active": tenant.is_active,
        "created_at": tenant.created_at.isoformat() if tenant.created_at else None,
        "settings": tenant.settings or {}
    }


@app.delete("/api/v1/tenants/{tenant_id}")
def deactivate_tenant(
    tenant_id: str,
    request: Request,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """
    Deactivate a tenant (soft delete). Requires super_admin role.
    This will also deactivate all users in the tenant.
    """
    # RBAC: require super_admin role
    if not check_role(api_key, "super_admin"):
        raise HTTPException(403, "Super admin access required")
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    
    # Deactivate tenant
    tenant.is_active = False
    
    # Deactivate all users in the tenant
    users = db.query(User).filter(User.tenant_id == tenant_id).all()
    for user in users:
        user.is_active = False
    
    db.commit()
    db.refresh(tenant)
    
    # Capture telemetry
    telemetry.capture_auth_event(
        event_type="tenant_deactivated",
        success=True,
        tenant_id=tenant.id,
        deactivated_by=getattr(api_key, "id", None),
        users_deactivated=len(users)
    )
    
    logger.info(
        "tenant_deactivated",
        tenant_id=tenant.id,
        users_deactivated=len(users),
        deactivated_by=getattr(api_key, "id", None)
    )
    
    return {
        "id": tenant.id,
        "name": tenant.name,
        "is_active": False,
        "message": f"Tenant deactivated. {len(users)} users also deactivated."
    }


@app.post("/api/v1/tenants/{tenant_id}/activate")
def activate_tenant(
    tenant_id: str,
    request: Request,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """
    Activate a tenant. Requires super_admin role.
    """
    # RBAC: require super_admin role
    if not check_role(api_key, "super_admin"):
        raise HTTPException(403, "Super admin access required")
    
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    
    tenant.is_active = True
    db.commit()
    db.refresh(tenant)
    
    # Capture telemetry
    telemetry.capture_auth_event(
        event_type="tenant_activated",
        success=True,
        tenant_id=tenant.id,
        activated_by=getattr(api_key, "id", None)
    )
    
    logger.info(
        "tenant_activated",
        tenant_id=tenant.id,
        activated_by=getattr(api_key, "id", None)
    )
    
    return {
        "id": tenant.id,
        "name": tenant.name,
        "is_active": True,
        "message": "Tenant activated"
    }

# Analytics API Endpoints
@app.get("/api/v1/analytics/trends")
def get_analytics_trends(
    request: Request,
    days: int = 30,
    group_by: str = "day",
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Get trend analysis for findings over time"""
    tenant_id = require_tenant(request, db)
    
    from sentrascan.core.analytics import get_trend_analysis
    from datetime import datetime, timedelta
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return get_trend_analysis(db, tenant_id, start_date, end_date, group_by)


@app.get("/api/v1/analytics/severity-distribution")
def get_analytics_severity_distribution(
    request: Request,
    days: int = 30,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Get severity distribution of findings"""
    tenant_id = require_tenant(request, db)
    
    from sentrascan.core.analytics import get_severity_distribution
    from datetime import datetime, timedelta
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return get_severity_distribution(db, tenant_id, start_date, end_date)


@app.get("/api/v1/analytics/scanner-effectiveness")
def get_analytics_scanner_effectiveness(
    request: Request,
    days: int = 30,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Get scanner effectiveness metrics"""
    tenant_id = require_tenant(request, db)
    
    from sentrascan.core.analytics import get_scanner_effectiveness
    from datetime import datetime, timedelta
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return get_scanner_effectiveness(db, tenant_id, start_date, end_date)


@app.get("/api/v1/analytics/remediation-progress")
def get_analytics_remediation_progress(
    request: Request,
    days: int = 90,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Get remediation progress tracking"""
    tenant_id = require_tenant(request, db)
    
    from sentrascan.core.analytics import get_remediation_progress
    from datetime import datetime, timedelta
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return get_remediation_progress(db, tenant_id, start_date, end_date)


@app.get("/api/v1/analytics/risk-scores")
def get_analytics_risk_scores(
    request: Request,
    days: int = 30,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Get risk scores and prioritization"""
    tenant_id = require_tenant(request, db)
    
    from sentrascan.core.analytics import get_risk_scores
    from datetime import datetime, timedelta
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return get_risk_scores(db, tenant_id, start_date, end_date)


@app.get("/api/v1/analytics/export")
def export_analytics(
    request: Request,
    format: str = "json",
    days: int = 30,
    include_trends: bool = True,
    include_severity: bool = True,
    include_scanner: bool = True,
    include_remediation: bool = True,
    include_risk: bool = True,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Export analytics data in CSV, JSON, or PDF format"""
    tenant_id = require_tenant(request, db)
    
    from sentrascan.core.analytics import (
        get_trend_analysis, get_severity_distribution,
        get_scanner_effectiveness, get_remediation_progress, get_risk_scores
    )
    from sentrascan.core.analytics_export import (
        export_trends_csv, export_severity_distribution_csv,
        export_scanner_effectiveness_csv, export_remediation_progress_csv,
        export_risk_scores_csv, export_analytics_pdf, export_analytics_json
    )
    from datetime import datetime, timedelta
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get tenant name for PDF
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    tenant_name = tenant.name if tenant else "Unknown"
    
    # Fetch analytics data
    trend_data = None
    severity_data = None
    scanner_data = None
    remediation_data = None
    risk_data = None
    
    if include_trends:
        trend_data = get_trend_analysis(db, tenant_id, start_date, end_date)
    if include_severity:
        severity_data = get_severity_distribution(db, tenant_id, start_date, end_date)
    if include_scanner:
        scanner_data = get_scanner_effectiveness(db, tenant_id, start_date, end_date)
    if include_remediation:
        remediation_data = get_remediation_progress(db, tenant_id, start_date, end_date)
    if include_risk:
        risk_data = get_risk_scores(db, tenant_id, start_date, end_date)
    
    # Export based on format
    if format.lower() == "csv":
        # Combine all CSV exports
        csv_parts = []
        if trend_data:
            csv_parts.append("=== TREND ANALYSIS ===\n")
            csv_parts.append(export_trends_csv(trend_data))
            csv_parts.append("\n\n")
        if severity_data:
            csv_parts.append("=== SEVERITY DISTRIBUTION ===\n")
            csv_parts.append(export_severity_distribution_csv(severity_data))
            csv_parts.append("\n\n")
        if scanner_data:
            csv_parts.append("=== SCANNER EFFECTIVENESS ===\n")
            csv_parts.append(export_scanner_effectiveness_csv(scanner_data))
            csv_parts.append("\n\n")
        if remediation_data:
            csv_parts.append("=== REMEDIATION PROGRESS ===\n")
            csv_parts.append(export_remediation_progress_csv(remediation_data))
            csv_parts.append("\n\n")
        if risk_data:
            csv_parts.append("=== RISK SCORES ===\n")
            csv_parts.append(export_risk_scores_csv(risk_data))
        
        return Response(
            content="".join(csv_parts),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename=sentrascan-analytics-{datetime.utcnow().strftime('%Y%m%d')}.csv"}
        )
    elif format.lower() == "pdf":
        try:
            pdf_content = export_analytics_pdf(
                trend_data=trend_data if include_trends else None,
                severity_data=severity_data if include_severity else None,
                scanner_data=scanner_data if include_scanner else None,
                remediation_data=remediation_data if include_remediation else None,
                risk_data=risk_data if include_risk else None,
                tenant_name=tenant_name
            )
            return Response(
                content=pdf_content,
                media_type="application/pdf",
                headers={"Content-Disposition": f"attachment; filename=sentrascan-analytics-{datetime.utcnow().strftime('%Y%m%d')}.pdf"}
            )
        except ValueError as e:
            raise HTTPException(500, f"PDF export not available: {str(e)}")
    else:
        # JSON format (default)
        json_content = export_analytics_json(
            trend_data=trend_data if include_trends else None,
            severity_data=severity_data if include_severity else None,
            scanner_data=scanner_data if include_scanner else None,
            remediation_data=remediation_data if include_remediation else None,
            risk_data=risk_data if include_risk else None
        )
        return Response(
            content=json_content,
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename=sentrascan-analytics-{datetime.utcnow().strftime('%Y%m%d')}.json"}
        )


# Tenant Settings API Endpoints
@app.get("/api/v1/tenant-settings")
def get_tenant_settings_endpoint(
    request: Request,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Get all settings for the current tenant"""
    tenant_id = require_tenant(request, db)
    
    from sentrascan.core.tenant_settings import get_tenant_settings
    
    settings = get_tenant_settings(db, tenant_id)
    return settings


@app.get("/api/v1/tenant-settings/{setting_key:path}")
def get_tenant_setting_endpoint(
    setting_key: str,
    request: Request,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Get a specific setting for the current tenant"""
    tenant_id = require_tenant(request, db)
    
    from sentrascan.core.tenant_settings import get_tenant_setting
    
    value = get_tenant_setting(db, tenant_id, setting_key)
    return {"key": setting_key, "value": value}


@app.put("/api/v1/tenant-settings/{setting_key:path}")
def update_tenant_setting_endpoint(
    setting_key: str,
    request: Request,
    setting_value: dict = Body(...),
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Update a specific setting for the current tenant"""
    tenant_id = require_tenant(request, db)
    
    # Check permission (tenant admin required)
    if not check_permission(api_key, "tenant_settings.update"):
        raise HTTPException(403, "Permission denied: tenant_settings.update required")
    
    from sentrascan.core.tenant_settings import set_tenant_setting
    from sentrascan.core.models import User
    
    # Get user ID for audit logging
    user_id = None
    if isinstance(api_key, User):
        user_id = api_key.id
    elif hasattr(api_key, "user_id"):
        user_id = api_key.user_id
    
    set_tenant_setting(db, tenant_id, setting_key, setting_value, user_id=user_id)
    
    return {"key": setting_key, "value": setting_value, "updated": True}


@app.put("/api/v1/tenant-settings")
def update_tenant_settings_endpoint(
    request: Request,
    settings: dict = Body(...),
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Update multiple settings for the current tenant"""
    tenant_id = require_tenant(request, db)
    
    # Check permission (tenant admin required)
    if not check_permission(api_key, "tenant_settings.update"):
        raise HTTPException(403, "Permission denied: tenant_settings.update required")
    
    from sentrascan.core.tenant_settings import set_tenant_settings
    from sentrascan.core.models import User
    
    # Get user ID for audit logging
    user_id = None
    if isinstance(api_key, User):
        user_id = api_key.id
    elif hasattr(api_key, "user_id"):
        user_id = api_key.user_id
    
    set_tenant_settings(db, tenant_id, settings, user_id=user_id)
    
    return {"settings": settings, "updated": True}


@app.post("/api/v1/tenant-settings/reset")
def reset_tenant_settings_endpoint(
    request: Request,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Reset all settings to defaults for the current tenant"""
    tenant_id = require_tenant(request, db)
    
    # Check permission (tenant admin required)
    if not check_permission(api_key, "tenant_settings.update"):
        raise HTTPException(403, "Permission denied: tenant_settings.update required")
    
    from sentrascan.core.tenant_settings import reset_tenant_settings_to_defaults
    from sentrascan.core.models import User
    
    # Get user ID for audit logging
    user_id = None
    if isinstance(api_key, User):
        user_id = api_key.id
    elif hasattr(api_key, "user_id"):
        user_id = api_key.user_id
    
    reset_tenant_settings_to_defaults(db, tenant_id, user_id=user_id)
    
    return {"reset": True}

# ML Insights API Endpoints
@app.get("/api/v1/ml-insights/status")
def get_ml_insights_status(
    request: Request,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Get ML insights feature status"""
    from sentrascan.core.ml_insights import is_ml_insights_enabled
    
    return {
        "enabled": is_ml_insights_enabled(),
        "message": "ML insights are enabled" if is_ml_insights_enabled() else "ML insights are disabled (set ML_INSIGHTS_ENABLED=true and install scikit-learn)"
    }


@app.get("/api/v1/ml-insights")
def get_ml_insights(
    request: Request,
    days: int = 30,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Get ML insights (anomaly detection, correlations, remediation prioritization)"""
    tenant_id = require_tenant(request, db)
    
    from sentrascan.core.ml_insights import (
        detect_anomalies, analyze_correlations, prioritize_remediations, is_ml_insights_enabled
    )
    from datetime import datetime, timedelta
    
    if not is_ml_insights_enabled():
        raise HTTPException(503, "ML insights are not enabled. Set ML_INSIGHTS_ENABLED=true and install scikit-learn.")
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Get all ML insights
    anomalies = detect_anomalies(db, tenant_id, start_date, end_date)
    correlations = analyze_correlations(db, tenant_id, start_date, end_date)
    remediations = prioritize_remediations(db, tenant_id, start_date, end_date)
    
    return {
        "enabled": True,
        "period": {"start": start_date.isoformat(), "end": end_date.isoformat()},
        "anomaly_detection": anomalies,
        "correlations": correlations,
        "remediation_prioritization": remediations
    }


@app.get("/api/v1/ml-insights/anomalies")
def get_ml_anomalies(
    request: Request,
    days: int = 30,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Get anomaly detection results"""
    tenant_id = require_tenant(request, db)
    
    from sentrascan.core.ml_insights import detect_anomalies, is_ml_insights_enabled
    from datetime import datetime, timedelta
    
    if not is_ml_insights_enabled():
        raise HTTPException(503, "ML insights are not enabled")
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return detect_anomalies(db, tenant_id, start_date, end_date)


@app.get("/api/v1/ml-insights/correlations")
def get_ml_correlations(
    request: Request,
    days: int = 30,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Get finding correlation analysis"""
    tenant_id = require_tenant(request, db)
    
    from sentrascan.core.ml_insights import analyze_correlations, is_ml_insights_enabled
    from datetime import datetime, timedelta
    
    if not is_ml_insights_enabled():
        raise HTTPException(503, "ML insights are not enabled")
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return analyze_correlations(db, tenant_id, start_date, end_date)


@app.get("/api/v1/ml-insights/remediations")
def get_ml_remediations(
    request: Request,
    days: int = 90,
    api_key=Depends(require_api_key),
    db: Session = Depends(get_db)
):
    """Get prioritized remediation recommendations"""
    tenant_id = require_tenant(request, db)
    
    from sentrascan.core.ml_insights import prioritize_remediations, is_ml_insights_enabled
    from datetime import datetime, timedelta
    
    if not is_ml_insights_enabled():
        raise HTTPException(503, "ML insights are not enabled")
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    return prioritize_remediations(db, tenant_id, start_date, end_date)

# Shard Management API Endpoints (Super Admin only)
@app.get("/api/v1/sharding/shard")
def get_shard_info(tenant_id: str, request: Request, db: Session = Depends(get_db)):
    """Get shard information for a tenant (super admin only)"""
    user = get_session_user(request, db)
    if not user or not check_role(user, "super_admin"):
        raise HTTPException(403, "Permission denied: super_admin role required")
    
    shard_info = get_shard_for_tenant(tenant_id, db)
    if not shard_info:
        raise HTTPException(404, "Shard not found for tenant")
    
    return shard_info

@app.get("/api/v1/sharding/shards")
def list_all_shards(request: Request, db: Session = Depends(get_db)):
    """List all active shards (super admin only)"""
    user = get_session_user(request, db)
    if not user or not check_role(user, "super_admin"):
        raise HTTPException(403, "Permission denied: super_admin role required")
    
    shards = list_shards(db)
    return {"shards": shards}

@app.post("/api/v1/sharding/shards")
def create_shard_for_tenant(tenant_id: str, request: Request, db: Session = Depends(get_db)):
    """Create a shard schema for a tenant (super admin only)"""
    user = get_session_user(request, db)
    if not user or not check_role(user, "super_admin"):
        raise HTTPException(403, "Permission denied: super_admin role required")
    
    # Verify tenant exists
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    
    schema_name = create_shard_schema(tenant_id, db)
    if not schema_name:
        raise HTTPException(500, "Failed to create shard schema")
    
    return {
        "message": "Shard created",
        "tenant_id": tenant_id,
        "schema_name": schema_name
    }

@app.delete("/api/v1/sharding/shards/{tenant_id}")
def remove_shard(tenant_id: str, request: Request, db: Session = Depends(get_db)):
    """Deactivate a shard for a tenant (super admin only)"""
    user = get_session_user(request, db)
    if not user or not check_role(user, "super_admin"):
        raise HTTPException(403, "Permission denied: super_admin role required")
    
    success = deactivate_shard(tenant_id, db)
    if not success:
        raise HTTPException(404, "Shard not found for tenant")
    
    return {"message": "Shard deactivated", "tenant_id": tenant_id}

@app.get("/api/v1/sharding/statistics")
def get_sharding_statistics(request: Request, db: Session = Depends(get_db)):
    """Get sharding statistics (super admin only)"""
    user = get_session_user(request, db)
    if not user or not check_role(user, "super_admin"):
        raise HTTPException(403, "Permission denied: super_admin role required")
    
    stats = get_shard_statistics(db)
    return stats

# Key Management API Endpoints (Super Admin only)
@app.post("/api/v1/tenants/{tenant_id}/rotate-key")
def rotate_tenant_encryption_key(tenant_id: str, request: Request, db: Session = Depends(get_db)):
    """Rotate encryption key for a tenant (super admin only)"""
    user = get_session_user(request, db)
    if not user or not check_role(user, "super_admin"):
        raise HTTPException(403, "Permission denied: super_admin role required")
    
    # Verify tenant exists
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    
    try:
        new_key = rotate_tenant_key(tenant_id)
        
        logger.info(
            "tenant_key_rotated_via_api",
            tenant_id=tenant_id,
            rotated_by=user.id if hasattr(user, 'id') else None
        )
        
        return {
            "message": "Encryption key rotated successfully",
            "tenant_id": tenant_id,
            "note": "Old key retained for decrypting existing data"
        }
    except Exception as e:
        logger.error("key_rotation_failed", tenant_id=tenant_id, error=str(e))
        raise HTTPException(500, f"Failed to rotate key: {str(e)}")

@app.get("/api/v1/tenants/{tenant_id}/key-metadata")
def get_key_metadata(tenant_id: str, request: Request, db: Session = Depends(get_db)):
    """Get encryption key metadata for a tenant (super admin only)"""
    user = get_session_user(request, db)
    if not user or not check_role(user, "super_admin"):
        raise HTTPException(403, "Permission denied: super_admin role required")
    
    # Verify tenant exists
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(404, "Tenant not found")
    
    from sentrascan.core.key_management import get_key_manager
    key_manager = get_key_manager()
    metadata = key_manager.get_key_metadata(tenant_id)
    
    if not metadata:
        raise HTTPException(404, "No encryption key found for tenant")
    
    # Add rotation status
    metadata["rotation_needed"] = key_manager.check_key_rotation_needed(tenant_id)
    
    return metadata

# MFA Endpoints
@app.post("/api/v1/users/mfa/setup")
def setup_mfa(request: Request, db: Session = Depends(get_db)):
    """Setup MFA for the current user"""
    user = get_session_user(request, db)
    if not user:
        raise HTTPException(401, "Authentication required")
    
    if not HAS_MFA:
        raise HTTPException(501, "MFA is not available (pyotp/qrcode not installed)")
    
    from sentrascan.core.auth import generate_mfa_secret, generate_mfa_qr_code
    from sentrascan.core.encryption import encrypt_tenant_data
    
    # Generate secret
    secret = generate_mfa_secret()
    
    # Encrypt and store secret
    encrypted_secret = encrypt_tenant_data(user.tenant_id, secret)
    user.mfa_secret = encrypted_secret
    db.commit()
    
    # Generate QR code
    qr_code = generate_mfa_qr_code(secret, user.email)
    
    # Log security event
    log_security_event(
        db, "mfa_setup", "user", user.id,
        user.id, user.tenant_id,
        {},
        request.client.host if request.client else None
    )
    
    logger.info("mfa_setup_initiated", user_id=user.id)
    
    return {
        "secret": secret,  # Return plaintext secret for initial setup
        "qr_code": qr_code,
        "message": "Scan QR code with authenticator app, then verify with /api/v1/users/mfa/verify"
    }

@app.post("/api/v1/users/mfa/verify")
def verify_mfa(request: Request, token: str = Form(...), db: Session = Depends(get_db)):
    """Verify MFA token and enable MFA"""
    user = get_session_user(request, db)
    if not user:
        raise HTTPException(401, "Authentication required")
    
    if not HAS_MFA:
        raise HTTPException(501, "MFA is not available")
    
    if not user.mfa_secret:
        raise HTTPException(400, "MFA not set up. Call /api/v1/users/mfa/setup first")
    
    from sentrascan.core.auth import verify_mfa_token
    from sentrascan.core.encryption import decrypt_tenant_data
    
    # Decrypt secret
    secret = decrypt_tenant_data(user.tenant_id, user.mfa_secret)
    
    # Verify token
    if not verify_mfa_token(secret, token):
        logger.warning("mfa_verification_failed", user_id=user.id)
        raise HTTPException(401, "Invalid MFA token")
    
    # Enable MFA
    user.mfa_enabled = True
    db.commit()
    
    # Log security event
    log_security_event(
        db, "mfa_enabled", "user", user.id,
        user.id, user.tenant_id,
        {},
        request.client.host if request.client else None
    )
    
    logger.info("mfa_enabled", user_id=user.id)
    
    return {"message": "MFA enabled successfully"}

@app.post("/api/v1/users/mfa/disable")
def disable_mfa(request: Request, token: str = Form(...), db: Session = Depends(get_db)):
    """Disable MFA for the current user"""
    user = get_session_user(request, db)
    if not user:
        raise HTTPException(401, "Authentication required")
    
    if not user.mfa_enabled:
        raise HTTPException(400, "MFA is not enabled")
    
    if not HAS_MFA:
        raise HTTPException(501, "MFA is not available")
    
    from sentrascan.core.auth import verify_mfa_token
    from sentrascan.core.encryption import decrypt_tenant_data
    
    # Verify token before disabling
    secret = decrypt_tenant_data(user.tenant_id, user.mfa_secret)
    if not verify_mfa_token(secret, token):
        raise HTTPException(401, "Invalid MFA token")
    
    # Disable MFA
    user.mfa_enabled = False
    user.mfa_secret = None
    db.commit()
    
    # Log security event
    log_security_event(
        db, "mfa_disabled", "user", user.id,
        user.id, user.tenant_id,
        {},
        request.client.host if request.client else None
    )
    
    logger.info("mfa_disabled", user_id=user.id)
    
    return {"message": "MFA disabled successfully"}

# API Key expiration and rotation
API_KEY_EXPIRATION_DAYS = int(os.environ.get("API_KEY_EXPIRATION_DAYS", "365"))
API_KEY_ROTATION_INTERVAL_DAYS = int(os.environ.get("API_KEY_ROTATION_INTERVAL_DAYS", "90"))

def check_api_key_expiration(api_key) -> Tuple[bool, Optional[datetime]]:
    """Check if API key has expired"""
    if not api_key.expires_at:
        return False, None
    
    is_expired = datetime.utcnow() > api_key.expires_at
    return is_expired, api_key.expires_at

def run_server(host: str, port: int):
    import uvicorn
    uvicorn.run(app, host=host, port=port)