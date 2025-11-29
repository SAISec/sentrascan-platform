import json
import os
import re
import hashlib
import subprocess
import time
from typing import List, Optional
from urllib.parse import urlparse
from sentrascan.core.models import Scan, Finding
from sentrascan.core.policy import PolicyEngine
from sentrascan.modules.mcp.sast import SASTRunner
from sentrascan.modules.mcp.rules import RuleScanner
from sentrascan.modules.mcp.handshake import MCPProbe
from sentrascan.modules.mcp.secrets import TruffleHogRunner, GitleaksRunner
# ZAP removed - no longer used
from sentrascan.modules.mcp.probe_runtime import RuntimeProbe

DEFAULT_DISCOVERY_PATHS = [
    os.path.expanduser("~/Library/Application Support/Claude/"),
    os.path.expanduser("~/.cursor/mcp.json"),
    os.path.expanduser("~/.codeium/windsurf/mcp_config.json"),
    os.path.expanduser("~/.vscode/mcp.json"),
]

class MCPScanner:
    def __init__(self, policy: PolicyEngine):
        self.policy = policy
        # Optional external tools: semgrep, trufflehog, gitleaks, zap-baseline.py
        # If not present in PATH, corresponding steps are skipped.

    def _slug(self, s: str) -> str:
        return hashlib.sha1(s.encode()).hexdigest()[:12]

    def _is_allowed_repo_url(self, url: str) -> bool:
        """
        Restrict which remote repositories can be cloned to reduce SSRF / supply-chain risk.
        
        - Allow only well-known hosts (GitHub, Hugging Face) over HTTPS or git+ssh.
        - Reject arbitrary hosts and non-HTTPS schemes.
        """
        # Basic patterns for git@ style URLs
        if url.startswith("git@"):
            # git@github.com:org/repo.git
            host = url.split(":", 1)[0].split("@", 1)[-1]
            return host in {"github.com"}
        parsed = urlparse(url)
        if parsed.scheme not in {"https", "http", ""}:
            return False
        host = parsed.hostname or ""
        # Allow only specific hosts by default
        if host in {"github.com", "huggingface.co"}:
            return True
        # For backward compatibility, explicit Hugging Face URIs like hf://
        if url.startswith("hf://"):
            return True
        return False

    def _ensure_repo(self, url: str, cache_dir: str = "/cache/mcp_repos") -> Optional[str]:
        # Enforce allowlist for remote repositories
        if not self._is_allowed_repo_url(url):
            return None
        os.makedirs(cache_dir, exist_ok=True)
        slug = self._slug(url)
        dest = os.path.join(cache_dir, slug)
        if os.path.isdir(dest) and os.listdir(dest):
            return dest
        try:
            env = os.environ.copy()
            # For Hugging Face, avoid pulling large LFS blobs by default
            if "huggingface.co" in url or url.startswith("hf://"):
                env["GIT_LFS_SKIP_SMUDGE"] = "1"
            cmd = ["git", "clone", "--depth", "1", url, dest]
            subprocess.run(cmd, env=env, check=True, capture_output=True, text=True, timeout=180)
            return dest
        except Exception:
            return None

    def auto_discover(self) -> List[str]:
        paths = []
        for p in DEFAULT_DISCOVERY_PATHS:
            if os.path.isdir(p):
                # Find json files
                for root, _, files in os.walk(p):
                    for f in files:
                        if f.endswith(".json"):
                            paths.append(os.path.join(root, f))
            elif os.path.isfile(p):
                paths.append(p)
        return list(dict.fromkeys(paths))

    def scan(self, config_paths: List[str], auto_discover: bool, timeout: int, db, tenant_id: Optional[str] = None):
        start = time.time()
        scan = None
        try:
            if auto_discover:
                config_paths = list(dict.fromkeys((config_paths or []) + self.auto_discover()))
            scan = Scan(
                scan_type="mcp", 
                target_path=",".join(config_paths or ["auto"]), 
                scan_status="in_progress",  # Scan is actively running
                tenant_id=tenant_id
            )
            db.add(scan)
            db.flush()
            sev = {"critical_count": 0, "high_count": 0, "medium_count": 0, "low_count": 0}
            issue_types: List[str] = []

            # Heuristic: derive repo paths from config json (look for --directory or absolute paths)
            repo_paths: List[str] = []
            try:
                for p in (config_paths or []):
                    # If a config path is actually a repo URL, clone it
                    if isinstance(p, str) and (p.endswith('.git') or p.startswith('git@') or p.startswith('https://github.com') or 'huggingface.co' in p):
                        rp = self._ensure_repo(p)
                        if rp:
                            repo_paths.append(rp)
                        continue
                    # Otherwise treat as JSON config
                    with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                        cfg = json.load(fh)
                    servers = (cfg or {}).get("mcpServers") or {}
                    for name, s in servers.items():
                        args = s.get("args") or []
                        for i, a in enumerate(args):
                            if a == "--directory" and i + 1 < len(args):
                                rp = args[i+1]
                                # If this path doesn't exist but looks like URL, clone
                                if not os.path.isdir(rp) and (rp.endswith('.git') or rp.startswith('git@') or rp.startswith('https://github.com') or 'huggingface.co' in rp):
                                    rp2 = self._ensure_repo(rp)
                                    if rp2:
                                        repo_paths.append(rp2)
                                elif os.path.isdir(rp):
                                    repo_paths.append(rp)
                            elif isinstance(a, str) and a.startswith("/") and os.path.isdir(a):
                                repo_paths.append(a)
            except Exception:
                pass
            repo_paths = [rp for rp in repo_paths if os.path.isdir(rp)]

            # Try mcp-checkpoint (JSON to temp file)
            try:
            import tempfile
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            tmp_path = tmp.name
            tmp.close()
            args = ["mcp-checkpoint", "scan", "--report-type", "json", "--output", tmp_path]
            for p in (config_paths or []):
                args += ["--config", p]
            subprocess.run(args, capture_output=True, text=True, timeout=timeout)
            try:
                with open(tmp_path, "r") as f:
                    data = json.load(f)
            except Exception:
                data = {"findings": []}
            try:
                os.unlink(tmp_path)
            except Exception:
                pass
            for iss in data.get("findings", []):
                severity = (iss.get("severity") or "HIGH").upper()
                key = severity.lower() + "_count"
                if key in sev:
                    sev[key] += 1
                issue_types.append(iss.get("type") or "mcp_issue")
                f = Finding(scan_id=scan.id, module="mcp", scanner="mcp-checkpoint", severity=severity, category=iss.get("type", "unknown"), title=iss.get("title", "Issue"), description=iss.get("description", ""), evidence=iss.get("evidence") or {}, tenant_id=tenant_id)
                db.add(f)
                cp_ok = True
            except Exception:
                pass
            # Try Cisco YARA-only (raw JSON to stdout)
            try:
            if config_paths:
                combined = {"findings": []}
                for p in config_paths:
                    args = ["mcp-scanner", "--config-path", p, "--analyzers", "yara", "--format", "raw"]
                    out = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
                    payload = json.loads(out.stdout) if out.stdout.strip() else {"findings": []}
                    # Normalize payload to expected structure
                    if isinstance(payload, dict) and "findings" in payload:
                        pass
                    else:
                        payload = {"findings": payload if isinstance(payload, list) else []}
                    combined["findings"].extend(payload["findings"])
                data = combined
            else:
                args = ["mcp-scanner", "--scan-known-configs", "--analyzers", "yara", "--format", "raw"]
                out = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
                payload = json.loads(out.stdout) if out.stdout.strip() else {"findings": []}
                if isinstance(payload, dict) and "findings" in payload:
                    data = payload
                else:
                    data = {"findings": payload if isinstance(payload, list) else []}
            for iss in data.get("findings", []):
                severity = (iss.get("severity") or "HIGH").upper()
                key = severity.lower() + "_count"
                if key in sev:
                    sev[key] += 1
                issue_types.append(iss.get("type") or "mcp_issue")
                f = Finding(scan_id=scan.id, module="mcp", scanner="cisco-yara", severity=severity, category=iss.get("type", "unknown"), title=iss.get("title", "Issue"), description=iss.get("description", ""), evidence=iss.get("evidence") or {}, tenant_id=tenant_id)
                db.add(f)
            except Exception:
                pass

            # Run regex rules on repo(s)
            try:
            rs = RuleScanner()
            for rp in repo_paths:
                for rfind in rs.scan_repo(rp):
                    sev_key = (rfind["severity"].lower() + "_count")
                    if sev_key in sev:
                        sev[sev_key] += 1
                    issue_types.append("code_rule")
                    db.add(Finding(
                        scan_id=scan.id,
                        module="mcp",
                        scanner=rfind.get("engine"),
                        severity=rfind.get("severity"),
                        category=rfind.get("category"),
                        title=rfind.get("title"),
                        description=rfind.get("description"),
                        location=rfind.get("location"),
                        evidence={"rule_id": rfind.get("rule_id")},
                        remediation="Use parameterized queries (psycopg2 placeholders, SQLAlchemy bound params); avoid f-strings/concat; validate inputs; use least-privileged DB roles.",
                        tenant_id=tenant_id,
                    ))
            except Exception:
                pass

            # Run SAST (Semgrep) if available
            try:
            srunner = SASTRunner(custom_rules_dir=os.environ.get("SENTRASCAN_SEMGREP_RULES"))
            if srunner.available():
                for rp in repo_paths:
                    for sf in srunner.run(rp, include_globs=["**/*.py"]):
                        sev_key = (sf["severity"].lower() + "_count")
                        if sev_key in sev:
                            sev[sev_key] += 1
                        issue_types.append("semgrep")
                        db.add(Finding(
                            scan_id=scan.id,
                            module="mcp",
                            scanner="semgrep",
                            severity=sf.get("severity"),
                            category="SAST",
                            title=sf.get("message"),
                            description=sf.get("rule_id"),
                            location=f"{sf.get('path')}:{sf.get('line')}",
                            evidence={"rule_id": sf.get("rule_id")},
                            remediation="Use parameterized queries and avoid string interpolation; apply input validation and least privilege.",
                            tenant_id=tenant_id,
                        ))
            except Exception:
                pass

            # Handshake-like probe (static parsing of Tool defs)
            try:
            for rp in repo_paths:
                probe = MCPProbe(rp)
                tools = probe.enumerate_tools()
                for pf in probe.risk_assessment(tools):
                    sev_key = (pf["severity"].lower() + "_count")
                    if sev_key in sev:
                        sev[sev_key] += 1
                    issue_types.append("mcp_probe")
                    db.add(Finding(
                        scan_id=scan.id,
                        module="mcp",
                        scanner=pf.get("engine"),
                        severity=pf.get("severity"),
                        category=pf.get("category"),
                        title=pf.get("title"),
                        description=pf.get("description"),
                        location=pf.get("location"),
                        evidence={},
                        remediation="Remove or strictly gate arbitrary SQL tools; require parameterized queries and explicit allowlists.",
                        tenant_id=tenant_id,
                    ))
            except Exception:
                pass

            # Dynamic safe-run probe (best-effort)
            try:
            for p in (config_paths or []):
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    cfg = json.load(fh)
                for name, s in (cfg.get("mcpServers") or {}).items():
                    cmd = s.get("command")
                    args = s.get("args") or []
                    env = s.get("env") or {}
                    if cmd:
                        rp = None
                        for i, a in enumerate(args):
                            if a == "--directory" and i + 1 < len(args):
                                rp = args[i+1]
                                break
                        rtp = RuntimeProbe(cmd=cmd, args=args, env=env, cwd=rp or None, timeout=8)
                        for rf in rtp.run():
                            sev_key = (rf["severity"].lower() + "_count")
                            if sev_key in sev:
                                sev[sev_key] += 1
                            issue_types.append("mcp_runtime")
                            db.add(Finding(
                                scan_id=scan.id,
                                module="mcp",
                                scanner=rf.get("engine"),
                                severity=rf.get("severity"),
                                category=rf.get("category"),
                                title=rf.get("title"),
                                description=rf.get("description"),
                                location=rp,
                                evidence={},
                                remediation="Disable execute_sql and enforce parameterized statements; introduce strict RBAC and query whitelists.",
                                tenant_id=tenant_id,
                            ))
            except Exception:
                pass

            # Secrets scanners
            try:
            th = TruffleHogRunner()
            gl = GitleaksRunner()
            for rp in repo_paths:
                if th.available():
                    for s in th.run(rp):
                        sev_key = (s["severity"].lower() + "_count")
                        if sev_key in sev:
                            sev[sev_key] += 1
                        issue_types.append("secrets")
                        db.add(Finding(
                            scan_id=scan.id,
                            module="mcp",
                            scanner=s.get("engine"),
                            severity=s.get("severity"),
                            category="Secrets",
                            title=s.get("title"),
                            description=s.get("description"),
                            location=s.get("location"),
                            evidence=s.get("evidence"),
                            tenant_id=tenant_id,
                        ))
                if gl.available():
                    for s in gl.run(rp):
                        sev_key = (s["severity"].lower() + "_count")
                        if sev_key in sev:
                            sev[sev_key] += 1
                        issue_types.append("secrets")
                        db.add(Finding(
                            scan_id=scan.id,
                            module="mcp",
                            scanner=s.get("engine"),
                            severity=s.get("severity"),
                            category="Secrets",
                            title=s.get("title"),
                            description=s.get("description"),
                            location=s.get("location"),
                            evidence=s.get("evidence"),
                            tenant_id=tenant_id,
                        ))
            except Exception:
                pass

            # ZAP baseline removed - no longer supported
            scan.duration_ms = int((time.time() - start) * 1000)
            scan.total_findings = sum(sev.values())
            scan.critical_count = sev["critical_count"]
            scan.high_count = sev["high_count"]
            scan.medium_count = sev["medium_count"]
            scan.low_count = sev["low_count"]
            
            # Set scan result: Pass or Fail based on policy gate
            scan.passed = self.policy.gate(sev, issue_types)
            
            # Set scan status: completed (scan finished successfully)
            scan.scan_status = "completed"
            
            db.commit()
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