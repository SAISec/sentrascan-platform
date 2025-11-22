import json
import os
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
        cmd = ["trufflehog", "filesystem", repo_path, "--fail", "--json"]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        findings: List[Dict[str, Any]] = []
        for line in (p.stdout or "").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            reason = obj.get("Reason") or obj.get("DetectorName") or "Secret"
            file = (obj.get("SourceMetadata") or {}).get("Data") or {}
            path = file.get("Filesystem") or file.get("Git") or {}
            location = None
            if isinstance(path, dict):
                location = path.get("file") or path.get("path")
            findings.append({
                "severity": "HIGH",
                "title": f"TruffleHog: {reason}",
                "description": (obj.get("Raw") or "Secret detected"),
                "location": location,
                "engine": "trufflehog",
                "evidence": {"DetectorName": obj.get("DetectorName"), "Raw": obj.get("Raw")},
            })
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
        # gitleaks detect -s <path> -f json -r - (print to stdout)
        cmd = ["gitleaks", "detect", "-s", repo_path, "-f", "json", "-r", "-"]
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
        findings: List[Dict[str, Any]] = []
        try:
            data = json.loads(p.stdout or "[]")
        except json.JSONDecodeError:
            data = []
        for item in data or []:
            rule = item.get("Rule") or item.get("RuleID") or "Secret"
            file = item.get("File") or item.get("Path")
            findings.append({
                "severity": "HIGH",
                "title": f"Gitleaks: {rule}",
                "description": item.get("Description") or "Secret detected",
                "location": file,
                "engine": "gitleaks",
                "evidence": {"Match": item.get("Match"), "Tags": item.get("Tags")},
            })
        return findings
