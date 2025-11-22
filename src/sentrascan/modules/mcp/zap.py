import os
import subprocess
from typing import List, Dict, Any

class ZapRunner:
    """
    Runs OWASP ZAP baseline scan against provided targets. Requires ZAP installed or a zap.sh available in PATH.
    In container, we expect 'zap-baseline.py' to be accessible if ZAP is installed; otherwise we skip.
    Targets are read from SENTRASCAN_ZAP_TARGETS (comma-separated) unless provided explicitly.
    """

    def available(self) -> bool:
        try:
            p = subprocess.run(["zap-baseline.py", "-h"], capture_output=True, text=True)
            return p.returncode in (0, 2)
        except FileNotFoundError:
            return False

    def run(self, targets: List[str] | None = None, timeout: int = 600) -> List[Dict[str, Any]]:
        if targets is None:
            env_targets = os.environ.get("SENTRASCAN_ZAP_TARGETS", "").strip()
            if env_targets:
                targets = [t.strip() for t in env_targets.split(",") if t.strip()]
            else:
                targets = []
        findings: List[Dict[str, Any]] = []
        for t in targets:
            # Use JSON output if available; fallback to HTML parse would be complex, so we map exit code to severity.
            cmd = ["zap-baseline.py", "-t", t, "-I", "-m", "3", "-J", "/tmp/zap.json"]
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
            sev = "LOW"
            # ZAP baseline exit codes: 0=pass, 1=warns, 2=fail
            if p.returncode == 2:
                sev = "HIGH"
            elif p.returncode == 1:
                sev = "MEDIUM"
            findings.append({
                "severity": sev,
                "category": "DAST",
                "title": f"ZAP baseline scan for {t}",
                "description": (p.stderr or p.stdout or "ZAP baseline completed").splitlines()[-1:][0:1][0] if (p.stderr or p.stdout) else "",
                "location": t,
                "engine": "owasp-zap",
                "evidence": {},
            })
        return findings
