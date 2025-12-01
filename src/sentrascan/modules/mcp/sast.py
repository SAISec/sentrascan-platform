import json
import os
import subprocess
from typing import List, Dict, Any

class SASTRunner:
    """
    Runs Semgrep on a given repository path with Python rules + custom rules.
    Produces a normalized list of findings.
    """

    DEFAULT_CONFIGS = [
        "p/python",           # Semgrep maintained Python rules
        "p/security-audit",  # Security-focused rules
        "p/injection",        # Injection detection patterns
    ]

    def __init__(self, custom_rules_dir: str | None = None):
        self.custom_rules_dir = custom_rules_dir

    def available(self) -> bool:
        """
        Check if Semgrep is available.
        
        Semgrep requires Python shared libraries (libpython3.11.so.1.0) which are
        now copied into the distroless container from the builder stage.
        """
        try:
            proc = subprocess.run(["semgrep", "--version"], capture_output=True, text=True, timeout=5)
            # Check if semgrep actually ran (not just missing library error)
            if proc.returncode == 0:
                return True
            # If returncode is 127 (command not found) or stderr contains library errors, semgrep is not available
            if proc.returncode == 127 or "error while loading shared libraries" in (proc.stderr or ""):
                return False
            # Other return codes might indicate semgrep exists but has issues
            return False
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def run(self, repo_path: str, include_globs: List[str] | None = None, timeout: int = 180) -> List[Dict[str, Any]]:
        if not os.path.isdir(repo_path):
            return []
        args = ["semgrep", "--json", "--timeout", str(timeout), "--error", "--no-git-ignore"]
        for cfg in self.DEFAULT_CONFIGS:
            args += ["--config", cfg]
        if self.custom_rules_dir and os.path.isdir(self.custom_rules_dir):
            args += ["--config", self.custom_rules_dir]
        if include_globs:
            for g in include_globs:
                args += ["--include", g]
        args += [repo_path]
        import structlog
        logger = structlog.get_logger()
        logger.info("semgrep_command", cmd=" ".join(args), repo_path=repo_path)
        proc = subprocess.run(args, capture_output=True, text=True, timeout=timeout)
        logger.info("semgrep_output", returncode=proc.returncode, stdout_length=len(proc.stdout or ""), stderr_length=len(proc.stderr or ""), stderr_preview=(proc.stderr or "")[:500])
        if proc.returncode not in (0, 1):  # 1==findings
            logger.warning("semgrep_failed", returncode=proc.returncode, stderr=(proc.stderr or "")[:500])
            return []
        try:
            payload = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError:
            return []
        results = payload.get("results") or []
        normalized: List[Dict[str, Any]] = []
        for r in results:
            sev = (r.get("extra", {}).get("severity") or "WARNING").upper()
            path = r.get("path")
            start = r.get("start", {})
            line = start.get("line")
            message = r.get("extra", {}).get("message") or r.get("check_id")
            rule_id = r.get("check_id")
            # Extract line content from Semgrep result
            # Semgrep provides lines in extra.metavars or we can read from file
            line_content = ""
            if path and line:
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as f:
                        lines = f.readlines()
                        if line <= len(lines):
                            line_content = lines[line - 1].strip()[:200]  # Truncate long lines
                except Exception:
                    pass
            normalized.append({
                "severity": sev,
                "path": path,
                "line": line,
                "rule_id": rule_id,
                "message": message,
                "engine": "sentrascan-semgrep",
                "line_content": line_content,
            })
        return normalized
