import json
import os
import shlex
import subprocess
import tempfile
from urllib.parse import urlparse
import time
from typing import List, Optional
from sentrascan.core.models import Scan, Finding, SBOM
from sentrascan.core.policy import PolicyEngine

class ModelScanner:
    def __init__(self, policy: PolicyEngine):
        self.policy = policy

    @staticmethod
    def _validate_paths(paths: List[str]) -> List[str]:
        """
        Validate scan paths to prevent SSRF by disallowing raw HTTP(S) URLs.
        
        The model scanner should operate on local files or pre-fetched content.
        Remote URLs must be fetched via a separate, SSRF-safe component.
        
        Exception: Hugging Face URLs are allowed as modelaudit supports them natively
        and they are from a trusted source.
        """
        safe_paths: List[str] = []
        for p in paths:
            if not isinstance(p, str):
                continue
            parsed = urlparse(p)
            # Allow Hugging Face URLs (modelaudit supports them natively)
            if parsed.scheme in ("http", "https"):
                host = parsed.hostname or ""
                if host == "huggingface.co" or host.endswith(".huggingface.co"):
                    # Validate Hugging Face URL format: https://huggingface.co/user/model
                    path_parts = parsed.path.strip("/").split("/")
                    if len(path_parts) >= 2:
                        safe_paths.append(p)
                        continue
                # Disallow other http/https URLs
                raise ValueError(
                    f"Remote URLs are not allowed in model scan paths: {p}. "
                    "Only Hugging Face URLs (huggingface.co) are supported. "
                    "For other sources, download artifacts to a local path first."
                )
            # Allow hf:// protocol (Hugging Face shorthand)
            if p.startswith("hf://"):
                safe_paths.append(p)
                continue
            # Allow local paths
            safe_paths.append(p)
        return safe_paths

    @staticmethod
    def doctor():
        try:
            # Use python -m modelaudit for distroless containers
            import sys
            out = subprocess.run([sys.executable, "-m", "modelaudit", "doctor"], capture_output=True, text=True, check=False)
            ok = out.returncode == 0
            return ok, out.stdout.strip()
        except FileNotFoundError:
            return False, "modelaudit CLI not found; install with `pip install modelaudit`"

    def scan(self, paths: List[str], sbom_path: Optional[str], strict: bool, timeout: int, db, tenant_id: Optional[str] = None):
        start = time.time()
        scan = None
        try:
            # Validate paths to avoid SSRF and remote fetches via subprocess
            paths = self._validate_paths(paths or [])
            
            # Create scan record with "in_progress" status at the start
            scan = Scan(
                scan_type="model",
                target_path=",".join(paths),
                scan_status="in_progress",  # Scan is actively running
                tenant_id=tenant_id,
            )
            db.add(scan)
            db.flush()  # Flush to get scan.id
            
            tmp_report = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            tmp_report.close()
            # Use python -m modelaudit for distroless containers
            # Note: modelaudit may not reliably write to -o file in subprocess context,
            # so we capture stdout instead and parse JSON from there
            import sys
            args = [sys.executable, "-m", "modelaudit", "scan"] + list(paths)
            args += ["-f", "json"]  # Remove -o flag, capture from stdout instead
            if strict:
                args += ["--strict"]
            if sbom_path:
                os.makedirs(os.path.dirname(sbom_path) or ".", exist_ok=True)
                args += ["--sbom", sbom_path]
            if timeout and timeout > 0:
                args += ["-t", str(timeout)]
            
            # Set modelaudit cache directory to writable volume (read-only filesystem in protected container)
            env = os.environ.copy()
            modelaudit_cache = os.environ.get("MODELAUDIT_CACHE_DIR", "/cache/modelaudit")
            os.makedirs(modelaudit_cache, exist_ok=True)
            env["MODELAUDIT_CACHE_DIR"] = modelaudit_cache
            # Set HOME to writable location - modelaudit uses ~/.modelaudit as fallback
            # Must be writable or modelaudit will fail with read-only filesystem error
            writable_home = "/cache"
            os.makedirs(writable_home, exist_ok=True)
            env["HOME"] = writable_home
            # Also set XDG_CACHE_HOME to ensure modelaudit uses writable cache
            env["XDG_CACHE_HOME"] = modelaudit_cache
            # Ensure we're in a writable directory
            cwd = os.getcwd()
            if not os.access(cwd, os.W_OK):
                cwd = "/tmp"
            
            proc = subprocess.run(args, capture_output=True, text=True, env=env, cwd=cwd, timeout=(timeout + 60) if timeout else 600)
            report = {}
            # modelaudit returns exit code 1 when issues are found, but still writes the report
            # Exit code 0 = no issues, 1 = issues found, 2 = error
            import structlog
            logger = structlog.get_logger()
            
            # Parse report from stdout (modelaudit writes JSON to stdout when -f json is used)
            # modelaudit returns exit code 1 when issues are found (normal), 2 = actual error
            report_data = proc.stdout if proc.stdout else None
            
            # Accept returncode 0 (no issues) or 1 (issues found), but log if 2 (error)
            if proc.returncode == 2:
                logger.warning("modelaudit_exit_code_2", 
                             stdout_length=len(proc.stdout) if proc.stdout else 0,
                             stderr_preview=proc.stderr[:500] if proc.stderr else None)
            
            if report_data and len(report_data) > 100:
                try:
                    report = json.loads(report_data)
                    issues_list = report.get("issues", []) if isinstance(report, dict) else []
                    logger.info("modelaudit_report_loaded", report_keys=list(report.keys()) if isinstance(report, dict) else [], 
                              issues_count=len(issues_list),
                              report_size_bytes=len(report_data),
                              source="stdout",
                              returncode=proc.returncode)
                except json.JSONDecodeError as e:
                    logger.error("modelaudit_report_parse_error", error=str(e), 
                               error_position=e.pos if hasattr(e, 'pos') else None,
                               report_preview=report_data[:500] if report_data else None,
                               report_size=len(report_data) if report_data else 0,
                               stderr=proc.stderr[:500] if proc.stderr else None)
                    report = {}
                except Exception as e:
                    logger.warning("modelaudit_report_parse_error", error=str(e), error_type=type(e).__name__)
                    report = {}
            else:
                logger.error("modelaudit_report_unavailable", 
                           returncode=proc.returncode,
                           stdout_length=len(proc.stdout) if proc.stdout else 0,
                           stdout_preview=proc.stdout[:200] if proc.stdout else None,
                           stderr_preview=proc.stderr[:500] if proc.stderr else None)
                # If no report available, mark scan as failed
                if scan:
                    scan.scan_status = "failed"
                    scan.passed = False
                    scan.duration_ms = int((time.time() - start) * 1000)
                    db.commit()
                raise ValueError("modelaudit scan failed: no report generated")
            
            # Cleanup temp file (not used anymore but clean up if it exists)
            if tmp_report.name and os.path.exists(tmp_report.name):
                try:
                    os.unlink(tmp_report.name)
                except:
                    pass
        
            # Normalize report - modelaudit uses "issues" key
            findings = report.get("issues") or report.get("findings") or []
            logger.info("model_scan_findings_extracted", findings_count=len(findings), 
                       report_has_issues="issues" in report if isinstance(report, dict) else False,
                       report_has_findings="findings" in report if isinstance(report, dict) else False)
            
            # Update scan with model format from report
            if isinstance(report, dict) and report.get("model_format"):
                scan.target_format = report.get("model_format")
            
            sev_counts = {"critical_count": 0, "high_count": 0, "medium_count": 0, "low_count": 0, "info_count": 0}
            issue_types = []
        # Persist SBOM if generated
        if sbom_path and os.path.exists(sbom_path):
            try:
                with open(sbom_path, "r") as f:
                    sbom_json = json.load(f)
                from sentrascan.core.models import SBOM as SBOMModel
                sb = SBOMModel(
                    model_name=report.get("model_name") if isinstance(report, dict) else None,
                    model_version=str(report.get("model_version")) if isinstance(report, dict) and report.get("model_version") is not None else None,
                    bom_format=sbom_json.get("bomFormat"),
                    spec_version=sbom_json.get("specVersion"),
                    content=sbom_json,
                    hash=None,
                    tenant_id=tenant_id,
                )
                db.add(sb)
                db.flush()
                scan.sbom_id = sb.id
            except Exception:
                pass
        
        # Process findings - modelaudit returns issues with "message" as string, not dict
        findings_processed = 0
        for iss in findings:
            try:
                severity = (iss.get("severity") or iss.get("level") or "info").upper()
                # Severity mapping: critical→critical, warning→medium, info→info (no change)
                if severity == "WARNING":
                    severity = "MEDIUM"
                # Keep "CRITICAL" and "INFO" as-is
                
                cat = iss.get("type") or iss.get("category") or iss.get("ruleId") or "unknown"
                issue_types.append(cat)
                key = (severity.lower() + "_count")
                if key in sev_counts:
                    sev_counts[key] += 1
                
                # Extract title - message can be string or dict
                title = iss.get("title")
                if not title:
                    msg = iss.get("message")
                    if isinstance(msg, dict):
                        title = msg.get("text", "Issue")
                    elif isinstance(msg, str):
                        title = msg
                    else:
                        title = "Issue"
                
                # Extract description from details if available
                description = iss.get("description") or ""
                if not description and iss.get("details"):
                    details = iss.get("details")
                    if isinstance(details, dict):
                        description = details.get("vulnerability_description") or details.get("why") or ""
                
                # Extract remediation from details
                remediation = iss.get("remediation") or ""
                if not remediation and iss.get("details"):
                    details = iss.get("details")
                    if isinstance(details, dict):
                        remediation = details.get("recommendation") or ""
                
                # Limit field lengths to avoid database errors
                title_str = (title[:500] if title else "Issue")
                description_str = (description[:2000] if description else "")
                location_str = (iss.get("location") or "")[:500] if iss.get("location") else None
                remediation_str = (remediation[:1000] if remediation else "")
                
                f = Finding(
                    scan_id=scan.id,
                    module="model",
                    scanner="modelaudit",
                    severity=severity,  # Keep original severity (CRITICAL, MEDIUM, INFO)
                    category=cat[:100] if cat else "unknown",  # Limit category length
                    title=title_str,
                    description=description_str,
                    location=location_str,
                    evidence=iss.get("details") or iss.get("evidence") or {},
                    remediation=remediation_str,
                    tenant_id=tenant_id,
                )
                db.add(f)
                findings_processed += 1
            except Exception as e:
                # Log error but continue processing other findings
                import structlog
                logger = structlog.get_logger()
                logger.warning("finding_creation_error", error=str(e), issue_keys=list(iss.keys()) if isinstance(iss, dict) else [])
                continue
        
        # Flush findings before updating scan counts to ensure they're in the session
        try:
            db.flush()
        except Exception as e:
            import structlog
            logger = structlog.get_logger()
            logger.error("model_scan_flush_failed", scan_id=scan.id, error=str(e), findings_processed=findings_processed)
            db.rollback()
            raise
        
        scan.duration_ms = int((time.time() - start) * 1000)
        # Calculate total excluding info (for backward compatibility with Scan model)
        scan.total_findings = (sev_counts["critical_count"] + sev_counts["high_count"] + 
                               sev_counts["medium_count"] + sev_counts["low_count"])
        scan.critical_count = sev_counts["critical_count"]
        scan.high_count = sev_counts["high_count"]
        scan.medium_count = sev_counts["medium_count"]
        scan.low_count = sev_counts["low_count"]
        # Note: info_count is tracked in findings but not in Scan model (for backward compatibility)
        
        # Set scan result: Pass or Fail based on policy gate
        scan.passed = self.policy.gate(sev_counts, issue_types)
        
        # Set scan status: completed (scan finished successfully)
        scan.scan_status = "completed"
        
        # Log findings processing summary
        import structlog
        logger = structlog.get_logger()
        logger.info(
            "model_scan_findings_processed",
            scan_id=scan.id,
            findings_processed=findings_processed,
            total_findings=scan.total_findings,
            critical=scan.critical_count,
            high=scan.high_count,
            medium=scan.medium_count,
            low=scan.low_count,
            info=sev_counts.get("info_count", 0),
            passed=scan.passed,
        )
        
            # Commit the transaction
            try:
                db.commit()
                logger.info("model_scan_committed", scan_id=scan.id, findings_count=findings_processed)
            except Exception as e:
                db.rollback()
                logger.error("model_scan_commit_failed", scan_id=scan.id, error=str(e), error_type=type(e).__name__)
                # Mark scan as failed due to database error
                if scan:
                    scan.scan_status = "failed"
                    scan.passed = False
                    try:
                        db.commit()
                    except:
                        db.rollback()
                raise
            
            return scan
        except subprocess.TimeoutExpired:
            # Scan timed out - mark as aborted
            if scan:
                scan.scan_status = "aborted"
                scan.passed = False
                scan.duration_ms = int((time.time() - start) * 1000)
                try:
                    db.commit()
                except:
                    db.rollback()
            import structlog
            logger = structlog.get_logger()
            logger.error("model_scan_timeout", scan_id=scan.id if scan else None, timeout=timeout)
            raise
        except ValueError as e:
            # Validation errors (e.g., SSRF prevention) - mark as failed
            if scan and scan.scan_status == "in_progress":
                scan.scan_status = "failed"
                scan.passed = False
                scan.duration_ms = int((time.time() - start) * 1000)
                try:
                    db.commit()
                except:
                    db.rollback()
            raise
        except Exception as e:
            # Any other error - mark as failed
            if scan:
                scan.scan_status = "failed"
                scan.passed = False
                scan.duration_ms = int((time.time() - start) * 1000)
                try:
                    db.commit()
                except:
                    db.rollback()
            import structlog
            logger = structlog.get_logger()
            logger.error("model_scan_error", scan_id=scan.id if scan else None, error=str(e), error_type=type(e).__name__)
            raise

    def to_report(self, scan: Scan):
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