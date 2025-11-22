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
        "p/python",  # Semgrep maintained Python rules
    ]

    def __init__(self, custom_rules_dir: str | None = None):
        self.custom_rules_dir = custom_rules_dir

    def available(self) -> bool:
        try:
            subprocess.run(["semgrep", "--version"], capture_output=True, text=True, check=False)
            return True
        except FileNotFoundError:
            return False

    def run(self, repo_path: str, include_globs: List[str] | None = None, timeout: int = 180) -> List[Dict[str, Any]]:
        if not os.path.isdir(repo_path):
            return []
        args = ["semgrep", "--json", "--timeout", str(timeout)]
        for cfg in self.DEFAULT_CONFIGS:
            args += ["--config", cfg]
        if self.custom_rules_dir and os.path.isdir(self.custom_rules_dir):
            args += ["--config", self.custom_rules_dir]
        if include_globs:
            for g in include_globs:
                args += ["--include", g]
        args += [repo_path]
        proc = subprocess.run(args, capture_output=True, text=True)
        if proc.returncode not in (0, 1):  # 1==findings
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
            normalized.append({
                "severity": sev,
                "path": path,
                "line": line,
                "rule_id": rule_id,
                "message": message,
                "engine": "semgrep",
            })
        return normalized
