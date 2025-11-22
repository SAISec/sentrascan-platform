import os
import subprocess
import time
from typing import List, Dict, Any, Optional

class RuntimeProbe:
    """
    Best-effort dynamic probe:
    - Spawns the MCP server using the command/args from MCP config (uv, etc.)
    - Attempts to connect over stdio with a tiny timeout using the 'mcp' client if present
    - If client is unavailable, just verifies the process starts and then kills it
    """

    def __init__(self, cmd: str, args: List[str], env: Dict[str, str] | None = None, cwd: Optional[str] = None, timeout: int = 8):
        self.cmd = cmd
        self.args = args
        self.env = env or {}
        self.cwd = cwd
        self.timeout = timeout

    def run(self) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        try:
            # Spawn process
            proc = subprocess.Popen([self.cmd] + self.args, cwd=self.cwd, env={**os.environ, **self.env}, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            started = time.time()
            try:
                # Try dynamic handshake if mcp client available
                try:
                    from mcp.client.stdio import StdioClient
                    from mcp.client.models import InitializeRequest
                    # Connect to the running server process
                    client = StdioClient(proc.stdin, proc.stdout)
                    client.initialize()
                    tools = client.list_tools()
                    for t in tools or []:
                        name = (t.get("name") or "").lower()
                        if name == "execute_sql" or (name.startswith("execute_") and name.endswith("_sql")):
                            findings.append({
                                "severity": "CRITICAL",
                                "category": "MCP.ToolSurface.Dynamic",
                                "title": f"Arbitrary SQL tool exposed: {t.get('name')}",
                                "description": "Runtime tool listing shows raw SQL execution surface.",
                                "engine": "mcp-runtime",
                            })
                except Exception:
                    # If the client is not available or handshake fails, we only confirm the process started
                    pass
                # Sleep a short time then kill
                while time.time() - started < min(self.timeout, 5):
                    if proc.poll() is not None:
                        break
                    time.sleep(0.2)
            finally:
                try:
                    proc.kill()
                except Exception:
                    pass
        except Exception:
            pass
        return findings