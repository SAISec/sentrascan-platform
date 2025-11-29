import json
import os
import re
import subprocess
from typing import List, Dict, Any

class TruffleHogRunner:
    def available(self) -> bool:
        try:
            p = subprocess.run(["trufflehog", "--version"], capture_output=True, text=True)
            return p.returncode == 0 or p.returncode == 2  # some versions exit 2 on --version
        except FileNotFoundError:
            return False

    def run(self, repo_path: str, timeout: int = 180) -> List[Dict[str, Any]]:
        if not os.path.isdir(repo_path):
            return []
        # v3 syntax: filesystem scan; output JSON lines
        # Remove --fail flag as it causes exit code 1 when findings are detected
        # Use --only-verified=false to detect unverified secrets too
        # Disable color output to ensure clean JSON
        # Disable auto-update to avoid "mv not found" error in distroless containers
        # Try multiple environment variables as different versions use different names
        env = {
            **os.environ,
            "NO_COLOR": "1",
            "TRUFFLEHOG_SKIP_UPDATE": "1",
            "SKIP_UPDATE": "1",
            "TRUFFLEHOG_NO_UPDATE": "1",
        }
        cmd = ["trufflehog", "filesystem", repo_path, "--json", "--only-verified=false", "--no-update"]
        import structlog
        logger = structlog.get_logger()
        logger.info("trufflehog_command", cmd=" ".join(cmd), repo_path=repo_path)
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        findings: List[Dict[str, Any]] = []
        
        # TruffleHog returns exit code 1 when findings are detected, 0 when none
        # However, it outputs JSON to stdout ONLY when findings are found
        # When no findings, stdout is empty and info goes to stderr
        stdout = p.stdout or ""
        stderr = p.stderr or ""
        
        # Log detailed output for debugging
        logger.info("trufflehog_output",
                   returncode=p.returncode,
                   stdout_length=len(stdout),
                   stderr_length=len(stderr),
                   stdout_preview=stdout[:500] if stdout else "",
                   stderr_preview=stderr[:500] if stderr else "")
        
        # Remove ANSI escape codes from stdout (in case they leak through)
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        stdout_clean = ansi_escape.sub('', stdout)
        
        # Log if there are errors (but don't fail - exit code 1 is normal when findings exist)
        if p.returncode not in (0, 1) and stderr:
            logger.warning("trufflehog_error", returncode=p.returncode, stderr=stderr[:500])
        
        # TruffleHog outputs JSON lines to stdout when findings are detected
        # If stdout is empty, there are no findings (this is normal)
        lines_processed = 0
        for line in stdout_clean.splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
                lines_processed += 1
            except json.JSONDecodeError as e:
                # Log JSON parse errors for debugging
                logger.debug("trufflehog_json_parse_error", line_preview=line[:200], error=str(e))
                continue
            reason = obj.get("Reason") or obj.get("DetectorName") or "Secret"
            file = (obj.get("SourceMetadata") or {}).get("Data") or {}
            path = file.get("Filesystem") or file.get("Git") or {}
            location = None
            if isinstance(path, dict):
                location = path.get("file") or path.get("path")
            
            # Determine severity based on detector type
            # API keys and tokens are typically MEDIUM severity (hardcoded secrets)
            # Passwords and other high-value secrets are HIGH
            detector_name = (obj.get("DetectorName") or "").lower()
            severity = "HIGH"  # Default
            if "api" in detector_name or "key" in detector_name or "token" in detector_name:
                severity = "MEDIUM"  # Hardcoded API keys/tokens
            elif "password" in detector_name or "secret" in detector_name or "credential" in detector_name:
                severity = "HIGH"  # Passwords and credentials
            
            findings.append({
                "severity": severity,
                "title": f"TruffleHog: {reason}",
                "description": (obj.get("Raw") or "Secret detected"),
                "location": location,
                "engine": "sentrascan-trufflehog",
                "evidence": {"DetectorName": obj.get("DetectorName"), "Raw": obj.get("Raw")},
            })
        logger.info("trufflehog_findings_processed", lines_processed=lines_processed, findings_count=len(findings))
        return findings

class GitleaksRunner:
    def available(self) -> bool:
        try:
            p = subprocess.run(["gitleaks", "version"], capture_output=True, text=True)
            return p.returncode == 0
        except FileNotFoundError:
            return False

    def run(self, repo_path: str, timeout: int = 180) -> List[Dict[str, Any]]:
        if not os.path.isdir(repo_path):
            return []
        import tempfile
        import structlog
        logger = structlog.get_logger()
        
        # Gitleaks requires -r with a writable file path to output JSON
        # Use a temp file in /cache (writable volume) instead of stdout
        # Gitleaks outputs JSON to the file specified by -r flag
        tmp_report = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json', dir='/cache')
        tmp_report.close()
        tmp_report_path = tmp_report.name
        
        findings: List[Dict[str, Any]] = []
        try:
            # gitleaks detect -s <path> -f json -r <temp_file> --no-git
            # Use --no-git to scan filesystem (not git history)
            # DO NOT use --verbose as it outputs colored text instead of JSON
            cmd = ["gitleaks", "detect", "-s", repo_path, "-f", "json", "-r", tmp_report_path, "--no-git"]
            logger.info("gitleaks_command", cmd=" ".join(cmd), repo_path=repo_path, report_path=tmp_report_path)
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env={**os.environ, "NO_COLOR": "1"})
            
            # Gitleaks returns exit code 1 when findings are detected, 0 when none
            # We need to read from the report file regardless of exit code
            stdout = p.stdout or ""
            stderr = p.stderr or ""
            
            # Log detailed output for debugging
            logger.info("gitleaks_output", 
                       returncode=p.returncode,
                       stdout_length=len(stdout),
                       stderr_length=len(stderr),
                       stdout_preview=stdout[:500] if stdout else "",
                       stderr_preview=stderr[:500] if stderr else "",
                       report_file_exists=os.path.exists(tmp_report_path))
            
            # Log if there are errors (but don't fail - exit code 1 is normal when findings exist)
            if p.returncode not in (0, 1) and stderr:
                logger.warning("gitleaks_error", returncode=p.returncode, stderr=stderr[:500])
            
            # Read JSON from the report file
            data = []
            if os.path.exists(tmp_report_path):
                try:
                    with open(tmp_report_path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                        if content:
                            # Remove ANSI escape codes (in case they leak through)
                            ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
                            content_clean = ansi_escape.sub('', content)
                            data = json.loads(content_clean)
                            logger.info("gitleaks_json_parsed", findings_count=len(data) if isinstance(data, list) else 0)
                        else:
                            logger.info("gitleaks_no_output", message="report file was empty")
                except json.JSONDecodeError as e:
                    logger.warning("gitleaks_json_parse_error", 
                                 error=str(e),
                                 error_position=getattr(e, 'pos', None),
                                 content_preview=content[:1000] if 'content' in locals() else "",
                                 returncode=p.returncode)
                except Exception as e:
                    logger.warning("gitleaks_file_read_error", error=str(e), report_path=tmp_report_path)
            else:
                logger.warning("gitleaks_report_file_missing", report_path=tmp_report_path, returncode=p.returncode)
            
            for item in data or []:
                rule = item.get("Rule") or item.get("RuleID") or "Secret"
                file = item.get("File") or item.get("Path")
                
                # Determine severity based on rule/tags
                # API keys and tokens are typically MEDIUM severity (hardcoded secrets)
                # Passwords and other high-value secrets are HIGH
                rule_lower = rule.lower()
                tags = item.get("Tags") or []
                tags_lower = [t.lower() if isinstance(t, str) else str(t).lower() for t in tags]
                severity = "HIGH"  # Default
                if any(tag in ["api", "key", "token"] for tag in tags_lower) or "api" in rule_lower or "key" in rule_lower or "token" in rule_lower:
                    severity = "MEDIUM"  # Hardcoded API keys/tokens
                elif any(tag in ["password", "secret", "credential"] for tag in tags_lower) or "password" in rule_lower or "secret" in rule_lower:
                    severity = "HIGH"  # Passwords and credentials
                
                findings.append({
                    "severity": severity,
                    "title": f"Gitleaks: {rule}",
                    "description": item.get("Description") or "Secret detected",
                    "location": file,
                    "engine": "sentrascan-gitleaks",
                    "evidence": {"Match": item.get("Match"), "Tags": item.get("Tags"), "RuleID": item.get("RuleID")},
                })
        finally:
            # Clean up temp file
            try:
                if os.path.exists(tmp_report_path):
                    os.unlink(tmp_report_path)
            except Exception:
                pass
        return findings
