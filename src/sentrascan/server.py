import os
from fastapi import FastAPI, HTTPException, Depends, Request, Header, Response
from fastapi.responses import RedirectResponse
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session  # ensure available for type annotations
from sqlalchemy import func
from datetime import datetime, timedelta
from sentrascan.core.storage import init_db, SessionLocal
from sentrascan.modules.model.scanner import ModelScanner
from sentrascan.modules.mcp.scanner import MCPScanner
from sentrascan.core.policy import PolicyEngine
import csv
import io

app = FastAPI(title="SentraScan Platform")

# Session auth (signed cookie)
import hmac, hashlib, base64
SESSION_COOKIE = os.environ.get("SENTRASCAN_SESSION_COOKIE", "ss_session")
SECRET = os.environ.get("SENTRASCAN_SECRET", "dev-secret-change-me")

def sign(val: str) -> str:
    mac = hmac.new(SECRET.encode(), msg=val.encode(), digestmod=hashlib.sha256).hexdigest()
    return f"{val}.{mac}"

def unsign(signed: str) -> str | None:
    try:
        val, mac = signed.rsplit(".", 1)
        if hmac.compare_digest(hmac.new(SECRET.encode(), msg=val.encode(), digestmod=hashlib.sha256).hexdigest(), mac):
            return val
    except Exception:
        pass
    return None

def get_session_user(request: Request, db: Session = None):
    cookie = request.cookies.get(SESSION_COOKIE)
    if not cookie:
        return None
    key = unsign(cookie)
    if not key:
        return None
    if db is None:
        db = next(get_db())
    rec = db.query(APIKey).filter(APIKey.key_hash == APIKey.hash_key(key), APIKey.is_revoked == False).first()
    return rec

# Simple API key and role enforcement (MVP)
from sentrascan.core.models import APIKey, Scan, Finding, Baseline

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def require_api_key(x_api_key: str | None = Header(default=None), db: Session = Depends(get_db)):
    # Allow unauthenticated health
    if x_api_key is None:
        raise HTTPException(401, "Missing API key")
    rec = db.query(APIKey).filter(APIKey.key_hash == APIKey.hash_key(x_api_key), APIKey.is_revoked == False).first()
    if not rec:
        raise HTTPException(403, "Invalid API key")
    return rec
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "web", "templates"))

# Add version to template context
from sentrascan import __version__
templates.env.globals['app_version'] = __version__

# Mount static files directory
static_dir = os.path.join(os.path.dirname(__file__), "web", "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/api/v1/health")
def health():
    return {"status": "ok"}

@app.post("/api/v1/models/scans")
def scan_model(payload: dict, api_key=Depends(require_api_key), db: Session = Depends(get_db)):
    # RBAC: only admin can trigger scans
    if getattr(api_key, "role", "viewer") != "admin":
        raise HTTPException(403, "Insufficient role: admin required")
    paths = payload.get("paths") or [payload.get("model_path")]
    if not paths:
        raise HTTPException(400, "paths or model_path is required")
    sbom = payload.get("generate_sbom")
    policy_path = payload.get("policy")
    pe = PolicyEngine.from_file(policy_path) if policy_path else PolicyEngine.default_model()
    ms = ModelScanner(policy=pe)
    scan = ms.scan(paths=paths, sbom_path=sbom and "./sboms/auto_sbom.json", strict=payload.get("strict", False), timeout=payload.get("timeout", 0), db=db)
    return ms.to_report(scan)
@app.post("/api/v1/mcp/scans")
def scan_mcp(payload: dict, api_key=Depends(require_api_key), db: Session = Depends(get_db)):
    # RBAC: only admin can trigger scans
    if getattr(api_key, "role", "viewer") != "admin":
        raise HTTPException(403, "Insufficient role: admin required")
    configs = payload.get("config_paths") or []
    auto = bool(payload.get("auto_discover", False))
    policy_path = payload.get("policy")
    pe = PolicyEngine.from_file(policy_path) if policy_path else PolicyEngine.default_mcp()
    scanner = MCPScanner(policy=pe)
    scan = scanner.scan(config_paths=configs, auto_discover=auto, timeout=payload.get("timeout", 60), db=db)
    return scanner.to_report(scan)

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
            try:
                db = next(get_db())
                if job["type"] == "model":
                    pe = PolicyEngine.default_model()
                    ms = ModelScanner(policy=pe)
                    existing = db.query(Scan).filter(Scan.id == job.get("existing_scan_id")).first()
                    scan = ms.scan(paths=job["paths"], sbom_path=job.get("sbom_path"), strict=job.get("strict", False), timeout=job.get("timeout", 0), db=db, existing_scan=existing)
                    job["on_done"](scan.id)
                elif job["type"] == "mcp":
                    pe = PolicyEngine.default_mcp()
                    scanner = MCPScanner(policy=pe)
                    existing = db.query(Scan).filter(Scan.id == job.get("existing_scan_id")).first()
                    scan = scanner.scan(config_paths=job.get("config_paths") or [], auto_discover=job.get("auto_discover", True), timeout=job.get("timeout", 60), db=db, existing_scan=existing)
                    job["on_done"](scan.id)
            except Exception:
                pass

runner = JobRunner(daemon=True)

@app.on_event("startup")
def on_startup():
    init_db()
    # start job runner
    if not runner.is_alive():
        runner.start()

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

@app.post("/api/v1/baselines")
def create_baseline(payload: dict, api_key=Depends(require_api_key), db: Session = Depends(get_db)):
    # RBAC: only admin can create
    if getattr(api_key, "role", "viewer") != "admin":
        raise HTTPException(403, "Insufficient role: admin required")
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
    return {"diff": deep_diff(l.content or {}, r.content or {})}

@app.get("/baselines")
def ui_baselines(request: Request):
    db = next(get_db())
    rows = db.query(Baseline).order_by(Baseline.created_at.desc()).limit(50).all()
    return templates.TemplateResponse("baselines.html", {"request": request, "baselines": rows})

@app.get("/baseline/compare")
def ui_baseline_compare(left: str, right: str, request: Request):
    db = next(get_db())
    l = db.query(Baseline).filter(Baseline.id == left).first()
    r = db.query(Baseline).filter(Baseline.id == right).first()
    if not l or not r:
        raise HTTPException(404, "Baseline not found")
    def diff(a, b):
        a = a or {}
        b = b or {}
        akeys = set(a.keys())
        bkeys = set(b.keys())
        added = list(sorted(bkeys - akeys))
        removed = list(sorted(akeys - bkeys))
        changed = [k for k in (akeys & bkeys) if a[k] != b[k]]
        return {"added": added, "removed": removed, "changed": changed}
    d = diff(l.content, r.content)
    return templates.TemplateResponse("baseline_compare.html", {"request": request, "left": l, "right": r, "diff": d})

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
def list_scans(api_key=Depends(require_api_key), db: Session = Depends(get_db), type: str | None = None, passed: str | None = None, limit: int = 50, offset: int = 0):
    q = db.query(Scan)
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
def dashboard_stats(api_key=Depends(require_api_key), db: Session = Depends(get_db), type: str | None = None, passed: str | None = None, time_range: str | None = None):
    """Get dashboard statistics"""
    q = db.query(Scan)
    
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
def dashboard_export(api_key=Depends(require_api_key), db: Session = Depends(get_db), format: str = "json", type: str | None = None, passed: str | None = None, time_range: str | None = None):
    """Export dashboard data as CSV or JSON"""
    q = db.query(Scan)
    
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
def get_scan(scan_id: str, api_key=Depends(require_api_key), db: Session = Depends(get_db)):
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
def ui_login_post(request: Request, response: Response, api_key: str = Form(...)):
    db = next(get_db())
    rec = db.query(APIKey).filter(APIKey.key_hash == APIKey.hash_key(api_key), APIKey.is_revoked == False).first()
    if not rec:
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid API key"}, status_code=401)
    resp = RedirectResponse(url="/", status_code=302)
    resp.set_cookie(SESSION_COOKIE, sign(api_key), httponly=True, samesite="lax")
    return resp

@app.get("/logout")
def ui_logout():
    resp = RedirectResponse(url="/login", status_code=302)
    resp.delete_cookie(SESSION_COOKIE)
    return resp

@app.get("/")
def ui_home(request: Request, type: str | None = None, passed: str | None = None, time_range: str | None = None, page: int = 1):
    db = next(get_db())
    q = db.query(Scan)
    
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
    
    page = max(page, 1)
    page_size = 20
    total = q.count()
    rows = q.order_by(Scan.created_at.desc()).limit(page_size).offset((page-1)*page_size).all()
    
    # Calculate statistics for dashboard
    stats_q = db.query(Scan)
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
    
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "scans": rows,
        "page": page,
        "has_next": (page*page_size) < total,
        "filters": {"type": type or "", "passed": passed or "", "time_range": time_range or ""},
        "stats": stats
    })

@app.get("/ui/scan")
def ui_scan_form(request: Request):
    user = get_session_user(request)
    if not user or user.role != "admin":
        return RedirectResponse(url="/login", status_code=302)
    return templates.TemplateResponse("scan_forms.html", {"request": request, "user": user})

@app.post("/ui/scan/model")
def ui_scan_model(request: Request, api_key: str = Form(None), model_path: str = Form(...), strict: bool = Form(False), generate_sbom: bool = Form(True), policy: str | None = Form(None), run_async: bool = Form(False)):
    # prefer session user; fallback to form
    db = next(get_db())
    user = get_session_user(request, db)
    rec = user
    if not rec and api_key:
        rec = db.query(APIKey).filter(APIKey.key_hash == APIKey.hash_key(api_key), APIKey.is_revoked == False).first()
    if not rec or rec.role != "admin":
        return RedirectResponse(url="/login", status_code=302)
    pe = PolicyEngine.from_file(policy) if policy else PolicyEngine.default_model()
    ms = ModelScanner(policy=pe)
    if run_async:
        from sentrascan.core.models import Scan as ScanModel
        scan = ScanModel(scan_type="model", target_path=model_path, scan_status="queued")
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
            "on_done": _done,
        })
        return templates.TemplateResponse("scan_submitted.html", {"request": request, "scan_id": scan.id, "message": "Model scan enqueued.", "link": f"/scan/{scan.id}"})
    else:
        scan = ms.scan(paths=[model_path], sbom_path="./sboms/ui_sbom.json" if generate_sbom else None, strict=strict, timeout=0, db=db)
        return templates.TemplateResponse("scan_submitted.html", {"request": request, "scan_id": scan.id, "message": "Model scan completed.", "link": f"/scan/{scan.id}"})

@app.post("/ui/scan/mcp")
def ui_scan_mcp(request: Request, api_key: str = Form(None), auto_discover: bool = Form(True), config_paths: str | None = Form(None), policy: str | None = Form(None), run_async: bool = Form(False)):
    db = next(get_db())
    user = get_session_user(request, db)
    rec = user
    if not rec and api_key:
        rec = db.query(APIKey).filter(APIKey.key_hash == APIKey.hash_key(api_key), APIKey.is_revoked == False).first()
    if not rec or rec.role != "admin":
        return RedirectResponse(url="/login", status_code=302)
    pe = PolicyEngine.from_file(policy) if policy else PolicyEngine.default_mcp()
    scanner = MCPScanner(policy=pe)
    paths = [p.strip() for p in (config_paths or "").split("\n") if p.strip()] or []
    if run_async:
        from sentrascan.core.models import Scan as ScanModel
        scan = ScanModel(scan_type="mcp", target_path=",".join(paths or ["auto"]), scan_status="queued")
        db.add(scan); db.commit()
        def _done(scan_id: str):
            pass
        job_queue.put({
            "type": "mcp",
            "config_paths": paths,
            "auto_discover": auto_discover,
            "timeout": 60,
            "existing_scan_id": scan.id,
            "on_done": _done,
        })
        return templates.TemplateResponse("scan_submitted.html", {"request": request, "scan_id": scan.id, "message": "MCP scan enqueued.", "link": f"/scan/{scan.id}"})
    else:
        scan = scanner.scan(config_paths=paths, auto_discover=auto_discover, timeout=60, db=db)
        return templates.TemplateResponse("scan_submitted.html", {"request": request, "scan_id": scan.id, "message": "MCP scan completed.", "link": f"/scan/{scan.id}"})

@app.get("/scan/{scan_id}")
def ui_scan_detail(scan_id: str, request: Request):
    db = next(get_db())
    scan = db.query(Scan).filter(Scan.id == scan_id).first()
    findings = db.query(Finding).filter(Finding.scan_id == scan_id).all()
    if not scan:
        raise HTTPException(404, "Scan not found")
    return templates.TemplateResponse(
        "scan_detail.html",
        {"request": request, "scan": scan, "findings": findings},
    )

def run_server(host: str, port: int):
    import uvicorn
    uvicorn.run(app, host=host, port=port)