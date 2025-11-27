import json
import os
import shlex
import subprocess
import tempfile
import time
from typing import List, Optional
from sentrascan.core.models import Scan, Finding, SBOM
from sentrascan.core.policy import PolicyEngine

class ModelScanner:
    def __init__(self, policy: PolicyEngine):
        self.policy = policy

    @staticmethod
    def doctor():
        try:
            out = subprocess.run(["modelaudit", "doctor"], capture_output=True, text=True, check=False)
            ok = out.returncode == 0
            return ok, out.stdout.strip()
        except FileNotFoundError:
            return False, "modelaudit CLI not found; install with `pip install modelaudit`"

    def scan(self, paths: List[str], sbom_path: Optional[str], strict: bool, timeout: int, db, tenant_id: Optional[str] = None):
        start = time.time()
        tmp_report = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        tmp_report.close()
        args = ["modelaudit", "scan"] + list(paths)
        args += ["-f", "json", "-o", tmp_report.name]
        if strict:
            args += ["--strict"]
        if sbom_path:
            os.makedirs(os.path.dirname(sbom_path) or ".", exist_ok=True)
            args += ["--sbom", sbom_path]
        if timeout and timeout > 0:
            args += ["-t", str(timeout)]
        proc = subprocess.run(args, capture_output=True, text=True)
        report = {}
        if os.path.exists(tmp_report.name):
            with open(tmp_report.name, "r") as f:
                try:
                    report = json.load(f)
                except Exception:
                    report = {}
            os.unlink(tmp_report.name)
        # Normalize report
        findings = report.get("issues") or report.get("findings") or []
        sev_counts = {"critical_count": 0, "high_count": 0, "medium_count": 0, "low_count": 0}
        issue_types = []
        scan = Scan(
            scan_type="model",
            target_path=",".join(paths),
            target_format=report.get("model_format") if isinstance(report, dict) else None,
            tenant_id=tenant_id,
        )
        db.add(scan)
        db.flush()
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
        for iss in findings:
            severity = (iss.get("severity") or iss.get("level") or "LOW").upper()
            cat = iss.get("category") or iss.get("ruleId") or "unknown"
            issue_types.append(cat)
            key = (severity.lower() + "_count")
            if key in sev_counts:
                sev_counts[key] += 1
            f = Finding(
                scan_id=scan.id,
                module="model",
                scanner="modelaudit",
                severity=severity,
                category=cat,
                title=iss.get("title") or iss.get("message", {}).get("text", "Issue"),
                description=iss.get("description") or "",
                location=iss.get("location") or None,
                evidence=iss.get("evidence") or iss.get("data") or {},
                remediation=iss.get("remediation") or "",
                tenant_id=tenant_id,
            )
            db.add(f)
        scan.duration_ms = int((time.time() - start) * 1000)
        scan.total_findings = sum(sev_counts.values())
        scan.critical_count = sev_counts["critical_count"]
        scan.high_count = sev_counts["high_count"]
        scan.medium_count = sev_counts["medium_count"]
        scan.low_count = sev_counts["low_count"]
        scan.passed = self.policy.gate(sev_counts, issue_types)
        db.commit()
        return scan

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