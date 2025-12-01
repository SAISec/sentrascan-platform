import json
import os
import re
import hashlib
import subprocess
import time
import zipfile
import tempfile
from typing import List, Optional
from urllib.parse import urlparse
try:
    import requests
except ImportError:
    requests = None
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
            import structlog
            logger = structlog.get_logger()
            logger.warning("mcp_repo_url_not_allowed", url=url)
            return None
        os.makedirs(cache_dir, exist_ok=True)
        slug = self._slug(url)
        dest = os.path.join(cache_dir, slug)
        if os.path.isdir(dest) and os.listdir(dest):
            import structlog
            logger = structlog.get_logger()
            logger.info("mcp_repo_already_cloned", url=url, dest=dest)
            return dest
        
        import structlog
        logger = structlog.get_logger()
        
        # Try git clone first (if git is available)
        try:
            env = os.environ.copy()
            # For Hugging Face, avoid pulling large LFS blobs by default
            if "huggingface.co" in url or url.startswith("hf://"):
                env["GIT_LFS_SKIP_SMUDGE"] = "1"
            cmd = ["git", "clone", "--depth", "1", url, dest]
            logger.info("mcp_cloning_repo_git", url=url, dest=dest, cmd=" ".join(cmd))
            result = subprocess.run(cmd, env=env, check=False, capture_output=True, text=True, timeout=180)
            if result.returncode == 0:
                logger.info("mcp_repo_cloned_successfully", url=url, dest=dest, method="git")
                return dest
            else:
                logger.warning("mcp_repo_git_clone_failed", url=url, returncode=result.returncode, stderr=result.stderr[:200] if result.stderr else None)
        except FileNotFoundError:
            logger.info("mcp_git_not_available", url=url, message="git not found, trying zip download")
        except subprocess.TimeoutExpired:
            logger.warning("mcp_repo_git_clone_timeout", url=url, timeout=180)
        except Exception as e:
            logger.warning("mcp_repo_git_clone_exception", url=url, error=str(e), error_type=type(e).__name__)
        
        # Fallback: Download as zip archive (for GitHub repos)
        try:
            if "github.com" in url:
                # Convert GitHub URL to zip download URL
                # https://github.com/org/repo -> https://github.com/org/repo/archive/refs/heads/master.zip
                zip_url = url.rstrip('/')
                if not zip_url.endswith('.git'):
                    zip_url = zip_url + '/archive/refs/heads/master.zip'
                else:
                    zip_url = zip_url.replace('.git', '/archive/refs/heads/master.zip')
                
                if requests is None:
                    logger.error("mcp_requests_not_available", url=url, message="requests library not installed")
                    return None
                
                logger.info("mcp_downloading_repo_zip", url=url, zip_url=zip_url, dest=dest)
                response = requests.get(zip_url, timeout=180, stream=True)
                response.raise_for_status()
                
                # Download to temp file first
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp_zip:
                    for chunk in response.iter_content(chunk_size=8192):
                        tmp_zip.write(chunk)
                    tmp_zip_path = tmp_zip.name
                
                # Extract zip to destination
                os.makedirs(dest, exist_ok=True)
                with zipfile.ZipFile(tmp_zip_path, 'r') as zip_ref:
                    zip_ref.extractall(dest)
                    # Zip files typically extract to a subdirectory, move contents up
                    extracted_dirs = [d for d in os.listdir(dest) if os.path.isdir(os.path.join(dest, d))]
                    if len(extracted_dirs) == 1:
                        subdir = os.path.join(dest, extracted_dirs[0])
                        for item in os.listdir(subdir):
                            os.rename(os.path.join(subdir, item), os.path.join(dest, item))
                        os.rmdir(subdir)
                
                os.unlink(tmp_zip_path)
                logger.info("mcp_repo_downloaded_successfully", url=url, dest=dest, method="zip")
                return dest
        except Exception as e:
            logger.error("mcp_repo_zip_download_failed", url=url, dest=dest, error=str(e), error_type=type(e).__name__, exc_info=True)
            return None
        
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

    def scan(self, config_paths: List[str], auto_discover: bool, timeout: int, db, tenant_id: Optional[str] = None, existing_scan: Optional[Scan] = None):
        start = time.time()
        scan = existing_scan  # Use existing scan if provided
        try:
            if auto_discover:
                config_paths = list(dict.fromkeys((config_paths or []) + self.auto_discover()))
            
            # Create new scan only if no existing scan provided
            if not scan:
                scan = Scan(
                    scan_type="mcp", 
                    target_path=",".join(config_paths or ["auto"]), 
                    scan_status="in_progress",  # Scan is actively running
                    tenant_id=tenant_id
                )
                db.add(scan)
            else:
                # Update existing scan
                scan.scan_status = "in_progress"
                scan.target_path = ",".join(config_paths or ["auto"])
                if tenant_id:
                    scan.tenant_id = tenant_id
            db.flush()
            sev = {"critical_count": 0, "high_count": 0, "medium_count": 0, "low_count": 0}
            issue_types: List[str] = []
            
            # Track files and their issues for file-wise reporting
            files_affected = set()
            file_categories = {}  # {file_path: {category: count}}
            file_category_issues = {}  # {file_path: {category: [issues]}}
            
            def clean_file_path(file_path: str) -> str:
                """Clean file path by removing cache prefixes"""
                if not file_path:
                    return file_path
                # Remove common cache prefixes
                cache_prefixes = [
                    "/cache/mcp_repos/",
                    "/cache/.modelaudit/cache/",
                    "/tmp/",
                ]
                for prefix in cache_prefixes:
                    if prefix in file_path:
                        # Try to find a meaningful part after the cache prefix
                        idx = file_path.find(prefix)
                        if idx >= 0:
                            after_prefix = file_path[idx + len(prefix):]
                            # If it's a git repo, try to find the repo name
                            # Format: /cache/mcp_repos/<hash>/<repo_path>
                            parts = after_prefix.split("/", 1)
                            if len(parts) > 1:
                                # Return the repo path part (skip the hash)
                                return parts[1] if parts[1] else file_path
                            return after_prefix if after_prefix else file_path
                return file_path
            
            def normalize_file_key(file_path: str) -> str:
                """Normalize file path for grouping - use basename for grouping"""
                if not file_path:
                    return file_path
                cleaned = clean_file_path(file_path)
                # Remove line numbers from path (e.g., "addon.py:33" -> "addon.py")
                if ":" in cleaned:
                    # Split on last colon to separate file path from line number
                    parts = cleaned.rsplit(":", 1)
                    if len(parts) == 2:
                        # Check if second part is a number (line number)
                        try:
                            int(parts[1])
                            cleaned = parts[0]  # Remove line number
                        except ValueError:
                            pass  # Not a line number, keep as-is
                # Extract just the filename for grouping (group by file, not path)
                import os
                basename = os.path.basename(cleaned)
                # If the cleaned path is just the filename, use it as-is
                # Otherwise, use filename for grouping but keep full path for reference
                if "/" not in cleaned or cleaned == basename:
                    return cleaned
                # For grouping, use just the filename
                # This ensures addon.py groups together regardless of path
                return basename
            
            def track_file_issue(file_path: str, category: str, issue: dict):
                """Track an issue for a specific file"""
                if not file_path:
                    return
                cleaned_path = clean_file_path(file_path)
                # Use normalized key for grouping (by filename)
                # Use cleaned_path to ensure line numbers are stripped
                group_key = normalize_file_key(cleaned_path)
                
                # Store the cleaned path in the issue for reference
                issue_with_path = issue.copy()
                issue_with_path["original_path"] = cleaned_path
                
                files_affected.add(group_key)
                if group_key not in file_categories:
                    file_categories[group_key] = {}
                if category not in file_categories[group_key]:
                    file_categories[group_key][category] = 0
                file_categories[group_key][category] += 1
                
                if group_key not in file_category_issues:
                    file_category_issues[group_key] = {}
                if category not in file_category_issues[group_key]:
                    file_category_issues[group_key][category] = []
                file_category_issues[group_key][category].append(issue_with_path)

            # Heuristic: derive repo paths from config json (look for --directory or absolute paths)
            repo_paths: List[str] = []
            actual_config_paths: List[str] = []  # Separate config files from repo URLs
            import structlog
            logger = structlog.get_logger()
            try:
                for p in (config_paths or []):
                    # If a config path is actually a repo URL, clone it
                    # Check for GitHub URLs (with or without .git), Hugging Face URLs, or git@ URLs
                    is_repo_url = False
                    if isinstance(p, str):
                        p_lower = p.lower()
                        if (p.endswith('.git') or 
                            p.startswith('git@') or 
                            p.startswith('https://github.com') or 
                            p.startswith('http://github.com') or
                            'github.com' in p_lower or
                            'huggingface.co' in p_lower or
                            p.startswith('hf://')):
                            is_repo_url = True
                    
                    if is_repo_url:
                        logger.info("mcp_scan_detected_repo_url", url=p)
                        rp = self._ensure_repo(p)
                        if rp:
                            repo_paths.append(rp)
                            logger.info("mcp_scan_repo_cloned", url=p, path=rp)
                        else:
                            logger.warning("mcp_scan_repo_clone_failed", url=p)
                        continue
                    # Otherwise treat as JSON config file or directory containing mcp.json
                    config_file = None
                    if os.path.isfile(p):
                        config_file = p
                    elif os.path.isdir(p):
                        # Look for mcp.json in the directory
                        potential_config = os.path.join(p, "mcp.json")
                        if os.path.isfile(potential_config):
                            config_file = potential_config
                            logger.info("mcp_scan_found_config_in_dir", dir=p, config_file=config_file)
                        # Also add directory itself as a potential repo path
                        repo_paths.append(p)
                    
                    if config_file:
                        actual_config_paths.append(config_file)
                        try:
                            with open(config_file, "r", encoding="utf-8", errors="ignore") as fh:
                                cfg = json.load(fh)
                            servers = (cfg or {}).get("mcpServers") or {}
                            for name, s in servers.items():
                                args = s.get("args") or []
                                for i, a in enumerate(args):
                                    if a == "--directory" and i + 1 < len(args):
                                        rp = args[i+1]
                                        # If this path doesn't exist but looks like URL, clone
                                        if not os.path.isdir(rp) and (rp.endswith('.git') or rp.startswith('git@') or rp.startswith('https://github.com') or 'huggingface.co' in rp or 'github.com' in rp):
                                            rp2 = self._ensure_repo(rp)
                                            if rp2:
                                                repo_paths.append(rp2)
                                        elif os.path.isdir(rp):
                                            repo_paths.append(rp)
                                    elif isinstance(a, str) and a.startswith("/") and os.path.isdir(a):
                                        repo_paths.append(a)

                                # Heuristic: synthetic findings for insecure MCP config env vars
                                env = s.get("env") or {}
                                if isinstance(env, dict):
                                    for env_name, env_value in env.items():
                                        if not isinstance(env_value, str):
                                            continue
                                        location = clean_file_path(config_file)
                                        # Insecure endpoints over cleartext protocols
                                        if env_value.startswith(("http://", "ws://")):
                                            severity = "MEDIUM"
                                            cat = "Config.InsecureEndpoint"
                                            title = f"Insecure endpoint in env var {env_name}"
                                            description = f"Environment variable {env_name} uses insecure protocol: {env_value}"
                                            issue = {
                                                "title": title,
                                                "severity": severity,
                                                "description": description,
                                                "location": location,
                                            }
                                            track_file_issue(location, cat, issue)
                                            db.add(Finding(
                                                scan_id=scan.id,
                                                module="mcp",
                                                scanner="sentrascan-mcpcheck",
                                                severity=severity,
                                                category=cat,
                                                title=title,
                                                description=description,
                                                location=location,
                                                evidence={"env_name": env_name, "env_value": env_value},
                                                tenant_id=tenant_id,
                                            ))
                                        # Secret-like env vars (API keys, tokens, secrets)
                                        upper_name = env_name.upper()
                                        if any(tok in upper_name for tok in ["KEY", "SECRET", "TOKEN", "PASSWORD"]) or any(sig in env_value for sig in ["sk_live_", "AKIA", "ghp_"]):
                                            severity = "MEDIUM"
                                            cat = "Config.SecretEnvVar"
                                            title = f"Potential secret in env var {env_name}"
                                            description = "Environment variable appears to contain a secret-like value."
                                            issue = {
                                                "title": title,
                                                "severity": severity,
                                                "description": description,
                                                "location": location,
                                            }
                                            track_file_issue(location, cat, issue)
                                            db.add(Finding(
                                                scan_id=scan.id,
                                                module="mcp",
                                                scanner="sentrascan-mcpyara",
                                                severity=severity,
                                                category=cat,
                                                title=title,
                                                description=description,
                                                location=location,
                                                evidence={"env_name": env_name, "env_value": env_value},
                                                tenant_id=tenant_id,
                                            ))
                        except Exception as e:
                            logger.warning("mcp_scan_config_parse_failed", config_file=config_file, error=str(e))
                            pass
            except Exception:
                pass
            repo_paths = [rp for rp in repo_paths if os.path.isdir(rp)]

            # Try mcp-checkpoint (JSON to temp file) - only if we have actual config files
            try:
                if actual_config_paths:
                    import tempfile
                    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".json", dir="/cache")
                    tmp_path = tmp.name
                    tmp.close()
                    args = ["mcp-checkpoint", "scan", "--report-type", "json", "--output", tmp_path]
                    for p in actual_config_paths:
                        args += ["--config", p]
                    logger.info("mcp_checkpoint_command", cmd=" ".join(args), config_paths=actual_config_paths)
                    proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
                    logger.info("mcp_checkpoint_output", returncode=proc.returncode, stdout_length=len(proc.stdout or ""), stderr_length=len(proc.stderr or ""), stderr_preview=(proc.stderr or "")[:500])
                    try:
                        with open(tmp_path, "r") as f:
                            data = json.load(f)
                    except Exception as e:
                        logger.warning("mcp_checkpoint_parse_failed", error=str(e), tmp_path=tmp_path)
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
                        cat = iss.get("type", "unknown")
                        file_path = iss.get("location") or iss.get("file") or iss.get("path") or ""
                        # Clean file path and track
                        cleaned_path = clean_file_path(file_path)
                        if cleaned_path:
                            track_file_issue(cleaned_path, cat, {
                                "title": iss.get("title", "Issue"),
                                "severity": severity,
                                "description": iss.get("description", ""),
                                "location": cleaned_path
                            })
                        f = Finding(scan_id=scan.id, module="mcp", scanner="sentrascan-mcpcheck", severity=severity, category=cat, title=iss.get("title", "Issue"), description=iss.get("description", ""), location=cleaned_path or file_path, evidence=iss.get("evidence") or {}, tenant_id=tenant_id)
                        db.add(f)
            except Exception:
                pass
            # Try Cisco YARA-only (raw JSON to stdout) - only if we have actual config files
            try:
                if actual_config_paths:
                    combined = {"findings": []}
                    for p in actual_config_paths:
                        args = ["mcp-scanner", "--config-path", p, "--analyzers", "yara", "--format", "raw"]
                        logger.info("mcp_scanner_yara_command", cmd=" ".join(args), config_path=p)
                        out = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
                        logger.info("mcp_scanner_yara_output", returncode=out.returncode, stdout_length=len(out.stdout or ""), stderr_length=len(out.stderr or ""), stderr_preview=(out.stderr or "")[:500])
                        try:
                            payload = json.loads(out.stdout) if out.stdout.strip() else {"findings": []}
                        except json.JSONDecodeError as e:
                            logger.warning("mcp_scanner_yara_parse_failed", error=str(e), stdout_preview=(out.stdout or "")[:500])
                            payload = {"findings": []}
                        # Normalize payload to expected structure
                        if isinstance(payload, dict) and "findings" in payload:
                            pass
                        else:
                            payload = {"findings": payload if isinstance(payload, list) else []}
                        combined["findings"].extend(payload["findings"])
                    data = combined
                elif not repo_paths:
                    # Only try auto-discovery if we have no repo paths
                    args = ["mcp-scanner", "--scan-known-configs", "--analyzers", "yara", "--format", "raw"]
                    out = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
                    payload = json.loads(out.stdout) if out.stdout.strip() else {"findings": []}
                    if isinstance(payload, dict) and "findings" in payload:
                        data = payload
                    else:
                        data = {"findings": payload if isinstance(payload, list) else []}
                else:
                    data = {"findings": []}
                for iss in data.get("findings", []):
                    severity = (iss.get("severity") or "HIGH").upper()
                    key = severity.lower() + "_count"
                    if key in sev:
                        sev[key] += 1
                    issue_types.append(iss.get("type") or "mcp_issue")
                    cat = iss.get("type", "unknown")
                    file_path = iss.get("location") or iss.get("file") or iss.get("path") or ""
                    # Clean file path and track
                    cleaned_path = clean_file_path(file_path)
                    if cleaned_path:
                        track_file_issue(cleaned_path, cat, {
                            "title": iss.get("title", "Issue"),
                            "severity": severity,
                            "description": iss.get("description", ""),
                            "location": cleaned_path
                        })
                    # Clean paths in evidence JSON
                    evidence = iss.get("evidence") or {}
                    if isinstance(evidence, dict):
                        evidence = {k: clean_file_path(v) if isinstance(v, str) and ("cache" in v or "/tmp" in v) else v for k, v in evidence.items()}
                    f = Finding(scan_id=scan.id, module="mcp", scanner="sentrascan-mcpyara", severity=severity, category=cat, title=iss.get("title", "Issue"), description=iss.get("description", ""), location=cleaned_path or file_path, evidence=evidence, tenant_id=tenant_id)
                    db.add(f)
            except Exception:
                pass
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
                        # rfind.get("location") already contains "file:line" format from rules.py
                        original_location = rfind.get("location", "")
                        cat = rfind.get("category", "Code.Pattern")
                        
                        # Extract file path and line number from original location
                        # Original location format: "file:line" (e.g., "addon.py:1641")
                        if original_location and ":" in original_location:
                            parts = original_location.rsplit(":", 1)
                            if len(parts) == 2:
                                file_part = parts[0]
                                line_part = parts[1]
                                cleaned_path = clean_file_path(file_part)
                                location_str = f"{cleaned_path}:{line_part}"
                            else:
                                cleaned_path = clean_file_path(original_location)
                                location_str = cleaned_path
                        else:
                            # Fallback if location doesn't have line number
                            file_path = original_location or ""
                            cleaned_path = clean_file_path(file_path)
                            if cleaned_path and rfind.get('line_number'):
                                location_str = f"{cleaned_path}:{rfind.get('line_number')}"
                            else:
                                location_str = cleaned_path or file_path
                        
                        # Track file issue
                        if cleaned_path:
                            track_file_issue(cleaned_path, cat, {
                                "title": rfind.get("title"),
                                "severity": rfind.get("severity"),
                                "description": rfind.get("description"),
                                "location": cleaned_path,
                                "line_number": rfind.get("line_number")
                            })
                        
                        # Clean paths in evidence
                        # Only include essential fields to avoid repetition
                        # Location already contains file:line, so we don't need to duplicate file_path
                        evidence = {
                            "rule_id": rfind.get("rule_id"),
                            "line_content": rfind.get("line_content", ""),
                        }
                        
                        db.add(Finding(
                            scan_id=scan.id,
                            module="mcp",
                            scanner=rfind.get("engine"),
                            severity=rfind.get("severity"),
                            category=cat,
                            title=rfind.get("title"),
                            description=rfind.get("description"),
                            location=location_str,
                            evidence=evidence,
                            remediation="Use parameterized queries (psycopg2 placeholders, SQLAlchemy bound params); avoid f-strings/concat; validate inputs; use least-privileged DB roles.",
                            tenant_id=tenant_id,
                        ))
            except Exception:
                pass

            # Run SAST (Semgrep) if available
            # NOTE: Semgrep requires Python shared libraries (libpython3.11.so.1.0) which
            # are not available in distroless containers. Semgrep will gracefully skip
            # if unavailable. See docs/semgrep-distroless-limitation.md for details.
            try:
                srunner = SASTRunner(custom_rules_dir=os.environ.get("SENTRASCAN_SEMGREP_RULES"))
                if srunner.available():
                    for rp in repo_paths:
                        for sf in srunner.run(rp, include_globs=["**/*.py"]):
                            sev_key = (sf["severity"].lower() + "_count")
                            if sev_key in sev:
                                sev[sev_key] += 1
                            issue_types.append("semgrep")
                            file_path = sf.get("path") or ""
                            line_num = sf.get("line")
                            cleaned_path = clean_file_path(file_path)
                            location_str = f"{cleaned_path}:{line_num}" if cleaned_path and line_num else (cleaned_path or file_path)
                            cat = "SAST"
                            # Track file issue
                            if cleaned_path:
                                track_file_issue(cleaned_path, cat, {
                                    "title": sf.get("message"),
                                    "severity": sf.get("severity"),
                                    "description": sf.get("rule_id"),
                                    "line_number": line_num,
                                    "location": location_str
                                })
                            # Clean paths in evidence
                            evidence = {
                                "rule_id": sf.get("rule_id"), 
                                "line_number": line_num, 
                                "file_path": cleaned_path or file_path,
                                "line_content": sf.get("line_content", "")
                            }
                            db.add(Finding(
                                scan_id=scan.id,
                                module="mcp",
                                scanner="sentrascan-semgrep",
                                severity=sf.get("severity"),
                                category=cat,
                                title=sf.get("message"),
                                description=sf.get("rule_id"),
                                location=location_str,
                                evidence=evidence,
                                remediation="Use parameterized queries and avoid string interpolation; apply input validation and least privilege.",
                            tenant_id=tenant_id,
                        ))
                    logger.info("mcp_scan_semgrep_completed", repo_path=rp, findings_count=len([sf for sf in srunner.run(rp, include_globs=["**/*.py"])]))
            except Exception as e:
                logger.error("mcp_scan_semgrep_failed", error=str(e), exc_info=True)
                pass

            # Handshake-like probe (static parsing of Tool defs)
            try:
                if not repo_paths:
                    logger.warning("mcp_scan_probe_skipped", reason="no repo paths")
                for rp in repo_paths:
                    logger.info("mcp_scan_probe_running", repo_path=rp)
                    probe = MCPProbe(rp)
                    tools = probe.enumerate_tools()
                    logger.info("mcp_scan_probe_tools_found", repo_path=rp, tools_count=len(tools), tool_names=[t.get("name") for t in tools])
                    findings_count = 0
                    for pf in probe.risk_assessment(tools):
                        findings_count += 1
                        sev_key = (pf["severity"].lower() + "_count")
                        if sev_key in sev:
                            sev[sev_key] += 1
                        issue_types.append("mcp_probe")
                        # MCP Probe location may contain file:line format or just file path
                        original_location = pf.get("location") or ""
                        line_number = pf.get("line_number")
                        
                        # Extract file path and line number if location contains "file:line" format
                        if original_location and ":" in original_location:
                            parts = original_location.rsplit(":", 1)
                            if len(parts) == 2:
                                file_part = parts[0]
                                line_part = parts[1]
                                cleaned_path = clean_file_path(file_part)
                                location_str = f"{cleaned_path}:{line_part}"
                            else:
                                cleaned_path = clean_file_path(original_location)
                                location_str = cleaned_path
                        elif line_number:
                            # Build from file path and line_number if available
                            file_path = original_location or ""
                            cleaned_path = clean_file_path(file_path)
                            location_str = f"{cleaned_path}:{line_number}" if cleaned_path else file_path
                        else:
                            # Just file path
                            cleaned_path = clean_file_path(original_location)
                            location_str = cleaned_path or original_location
                        
                        cat = pf.get("category", "MCP.ToolSurface")
                        # Track file issue
                        if cleaned_path:
                            track_file_issue(cleaned_path, cat, {
                                "title": pf.get("title"),
                                "severity": pf.get("severity"),
                                "description": pf.get("description"),
                                "location": cleaned_path
                            })
                        # Clean paths in evidence
                        evidence = {}
                        db.add(Finding(
                            scan_id=scan.id,
                            module="mcp",
                            scanner=pf.get("engine"),
                            severity=pf.get("severity"),
                            category=cat,
                            title=pf.get("title"),
                            description=pf.get("description"),
                            location=location_str,
                            evidence=evidence,
                            remediation="Remove or strictly gate arbitrary SQL tools; require parameterized queries and explicit allowlists.",
                            tenant_id=tenant_id,
                        ))
            except Exception:
                pass

            # Dynamic safe-run probe (best-effort) - only if we have actual config files
            try:
                for p in actual_config_paths:
                    try:
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
                                    file_path = rp or ""
                                    cleaned_path = clean_file_path(file_path)
                                    cat = rf.get("category", "MCP.ToolSurface.Dynamic")
                                    # Track file issue
                                    if cleaned_path:
                                        track_file_issue(cleaned_path, cat, {
                                            "title": rf.get("title"),
                                            "severity": rf.get("severity"),
                                            "description": rf.get("description"),
                                            "location": cleaned_path
                                        })
                                    # Clean paths in evidence
                                    evidence = rf.get("evidence") or {}
                                    if isinstance(evidence, dict):
                                        evidence = {k: clean_file_path(v) if isinstance(v, str) and ("cache" in v or "/tmp" in v) else v for k, v in evidence.items()}
                                    db.add(Finding(
                                        scan_id=scan.id,
                                        module="mcp",
                                        scanner=rf.get("engine"),
                                        severity=rf.get("severity"),
                                        category=cat,
                                        title=rf.get("title"),
                                        description=rf.get("description"),
                                        location=cleaned_path or file_path,
                                        evidence=evidence,
                                        remediation="Disable execute_sql and enforce parameterized statements; introduce strict RBAC and query whitelists.",
                                        tenant_id=tenant_id,
                                    ))
                    except Exception:
                        continue
            except Exception:
                pass

            # Secrets scanners (TruffleHog and Gitleaks for hardcoded API keys, tokens, etc.)
            try:
                th = TruffleHogRunner()
                gl = GitleaksRunner()
                if not repo_paths:
                    logger.warning("mcp_secrets_skipped", reason="no repo paths")
                for rp in repo_paths:
                    if th.available():
                        logger.info("mcp_trufflehog_running", repo_path=rp)
                        findings_count = 0
                        for s in th.run(rp, timeout=timeout):
                            findings_count += 1
                            sev_key = (s["severity"].lower() + "_count")
                            if sev_key in sev:
                                sev[sev_key] += 1
                            issue_types.append("secrets")
                            file_path = s.get("location") or ""
                            cleaned_path = clean_file_path(file_path)
                            cat = "Secrets"
                            # Track file issue
                            if cleaned_path:
                                track_file_issue(cleaned_path, cat, {
                                    "title": s.get("title"),
                                    "severity": s.get("severity"),
                                    "description": s.get("description"),
                                    "location": cleaned_path
                                })
                            # Clean paths in evidence
                            evidence = s.get("evidence") or {}
                            if isinstance(evidence, dict):
                                evidence = {k: clean_file_path(v) if isinstance(v, str) and ("cache" in v or "/tmp" in v) else v for k, v in evidence.items()}
                            db.add(Finding(
                                scan_id=scan.id,
                                module="mcp",
                                scanner=s.get("engine") or "sentrascan-trufflehog",
                                severity=s.get("severity"),
                                category=cat,
                                title=s.get("title"),
                                description=s.get("description"),
                                location=cleaned_path or file_path,
                                evidence=evidence,
                                tenant_id=tenant_id,
                            ))
                        logger.info("mcp_trufflehog_findings", repo_path=rp, findings_count=findings_count)
                        db.flush() # Persist findings
                    else:
                        logger.info("mcp_trufflehog_skipped", reason="not available")
                    if gl.available():
                        logger.info("mcp_gitleaks_running", repo_path=rp)
                        findings_count = 0
                        for s in gl.run(rp, timeout=timeout):
                            findings_count += 1
                            sev_key = (s["severity"].lower() + "_count")
                            if sev_key in sev:
                                sev[sev_key] += 1
                            issue_types.append("secrets")
                            file_path = s.get("location") or ""
                            cleaned_path = clean_file_path(file_path)
                            cat = "Secrets"
                            # Track file issue
                            if cleaned_path:
                                track_file_issue(cleaned_path, cat, {
                                    "title": s.get("title"),
                                    "severity": s.get("severity"),
                                    "description": s.get("description"),
                                    "location": cleaned_path
                                })
                            # Clean paths in evidence
                            evidence = s.get("evidence") or {}
                            if isinstance(evidence, dict):
                                # Extract code line from Match field (format: "KEY = \"value\"")
                                match_text = evidence.get("Match", "")
                                if match_text:
                                    evidence["code_line"] = match_text  # Store actual code
                                # Preserve line_number and file_path from Gitleaks
                                if "line_number" not in evidence and s.get("location"):
                                    # Try to extract line number from location if it's in format "file:line"
                                    loc = s.get("location", "")
                                    if ":" in loc:
                                        try:
                                            parts = loc.rsplit(":", 1)
                                            if len(parts) == 2:
                                                line_num = int(parts[1])
                                                evidence["line_number"] = line_num
                                        except (ValueError, IndexError):
                                            pass
                                # Also preserve existing fields and clean paths
                                evidence = {k: clean_file_path(v) if isinstance(v, str) and ("cache" in v or "/tmp" in v) else v for k, v in evidence.items()}
                            
                            # Use location from finding (which includes line number if available)
                            finding_location = s.get("location") or cleaned_path or file_path
                            
                            db.add(Finding(
                                scan_id=scan.id,
                                module="mcp",
                                scanner=s.get("engine") or "sentrascan-gitleaks",
                                severity=s.get("severity"),
                                category=cat,
                                title=s.get("title"),
                                description=s.get("description"),
                                location=finding_location,
                                evidence=evidence,
                                tenant_id=tenant_id,
                            ))
                        logger.info("mcp_gitleaks_findings", repo_path=rp, findings_count=findings_count)
                        db.flush() # Persist findings
                    else:
                        logger.info("mcp_gitleaks_skipped", reason="not available")
            except Exception as e:
                logger.error("mcp_secrets_scan_failed", error=str(e), exc_info=True)
                pass

            # ZAP baseline removed - no longer supported
            scan.duration_ms = int((time.time() - start) * 1000)
            scan.total_findings = sum(sev.values())
            scan.critical_count = sev["critical_count"]
            scan.high_count = sev["high_count"]
            scan.medium_count = sev["medium_count"]
            scan.low_count = sev["low_count"]

            # Update scan metadata with file-wise breakdown (similar to model scanner)
            scan.meta = {
                "files_affected_count": len(files_affected),
                "files_affected": sorted(list(files_affected)),
                "file_categories": file_categories,
                "file_category_issues": file_category_issues,
            }

            # Set scan result: Pass or Fail based on policy gate
            scan.passed = self.policy.gate(sev, issue_types)

            # Set scan status: completed (scan finished successfully)
            scan.scan_status = "completed"

            # Flush findings before commit to ensure they're persisted
            try:
                db.flush()
            except Exception as e:
                import structlog
                logger = structlog.get_logger()
                logger.error("mcp_scan_flush_failed", scan_id=scan.id, error=str(e), exc_info=True)
                db.rollback()
                raise

            db.commit()
            
            import structlog
            logger = structlog.get_logger()
            logger.info("mcp_scan_completed", 
                       scan_id=scan.id, 
                       total_findings=scan.total_findings,
                       critical=scan.critical_count,
                       high=scan.high_count,
                       medium=scan.medium_count,
                       low=scan.low_count,
                       passed=scan.passed,
                       repo_paths_count=len(repo_paths),
                       config_paths_count=len(actual_config_paths))
            
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