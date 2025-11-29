import ast
import json
import os
from typing import Any, Dict, List, Optional

class ToolDef(Dict[str, Any]):
    pass

class MCPProbe:
    """
    Best-effort handshake probe via static parsing:
    - Locate server.py-like files under a repo
    - Parse AST to find Tool( name=..., inputSchema=... ) definitions returned by list_tools()
    - This avoids executing untrusted code
    """

    def __init__(self, repo_path: str):
        self.repo_path = repo_path

    def find_server_files(self) -> List[str]:
        candidates = []
        # First, try to find server.py files with "mcp" in path or filename
        for root, _, files in os.walk(self.repo_path):
            for f in files:
                if f.endswith("server.py") and ("mcp" in root.lower() or "_mcp_" in root.lower() or "mcp" in f.lower()):
                    candidates.append(os.path.join(root, f))
        # Fallback: any server.py under src/ (common MCP server structure)
        if not candidates:
            src_path = os.path.join(self.repo_path, "src")
            if os.path.isdir(src_path):
                for root, _, files in os.walk(src_path):
                    for f in files:
                        if f == "server.py" or f.endswith("_server.py") or f.endswith("server.py"):
                            candidates.append(os.path.join(root, f))
        # Additional fallback: look for any Python file with "server" in name in common locations
        if not candidates:
            for root, _, files in os.walk(self.repo_path):
                # Skip hidden and build directories
                if any(skip in root for skip in [".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"]):
                    continue
                for f in files:
                    if f.endswith(".py") and ("server" in f.lower() or "mcp" in f.lower()):
                        candidates.append(os.path.join(root, f))
        return candidates

    def extract_tools_from_file(self, path: str) -> List[ToolDef]:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                code = fh.read()
            tree = ast.parse(code, filename=path)
        except Exception:
            return []
        tools: List[ToolDef] = []

        class ToolVisitor(ast.NodeVisitor):
            def visit_Call(self, node: ast.Call):
                # Look for Tool(name=..., inputSchema=...)
                try:
                    func = node.func
                    if isinstance(func, ast.Name) and func.id == "Tool" or \
                       isinstance(func, ast.Attribute) and func.attr == "Tool":
                        name_val: Optional[str] = None
                        schema_val: Optional[Any] = None
                        for kw in node.keywords or []:
                            if kw.arg == "name":
                                name_val = self.literal_or_str(kw.value)
                            if kw.arg == "inputSchema":
                                schema_val = self.literal_or_obj(kw.value)
                        if name_val:
                            tools.append({"name": name_val, "inputSchema": schema_val, "source": path})
                finally:
                    self.generic_visit(node)

            def literal_or_str(self, v: ast.AST) -> Optional[str]:
                if isinstance(v, ast.Constant) and isinstance(v.value, str):
                    return v.value
                return None

            def literal_or_obj(self, v: ast.AST) -> Any:
                try:
                    return ast.literal_eval(v)
                except Exception:
                    return None

        ToolVisitor().visit(tree)
        return tools

    def enumerate_tools(self) -> List[ToolDef]:
        tools: List[ToolDef] = []
        for f in self.find_server_files():
            tools.extend(self.extract_tools_from_file(f))
        # Deduplicate by name
        seen = set()
        uniq: List[ToolDef] = []
        for t in tools:
            if t.get("name") not in seen:
                uniq.append(t)
                seen.add(t.get("name"))
        return uniq

    @staticmethod
    def risk_assessment(tools: List[ToolDef]) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        for t in tools:
            name = (t.get("name") or "").lower()
            schema = t.get("inputSchema") or {}
            risky = False
            reasons: List[str] = []
            severity = "HIGH"
            
            # Detect arbitrary code execution tools
            if "execute" in name and ("code" in name or "script" in name or "python" in name or "blender_code" in name):
                risky = True
                severity = "HIGH"
                reasons.append("Tool name suggests arbitrary code execution (RCE risk)")
            
            # Detect SQL execution tools
            if "execute_sql" in name or (name.startswith("execute_") and name.endswith("_sql")):
                risky = True
                severity = "CRITICAL"
                reasons.append("Tool name suggests arbitrary SQL execution")
            
            # Check for free-form code/codeblock parameters
            try:
                props = (schema or {}).get("properties") or {}
                if isinstance(props, dict):
                    # Check for code, script, query, command parameters
                    for param_name in ["code", "script", "query", "command", "python_code", "blender_code"]:
                        if param_name in props:
                            p = props.get(param_name) or {}
                            if isinstance(p, dict) and p.get("type") == "string":
                                risky = True
                                if param_name in ["code", "script", "python_code", "blender_code"]:
                                    severity = "HIGH"
                                    reasons.append(f"Tool inputSchema includes free-form '{param_name}' string parameter (RCE risk)")
                                elif param_name == "query":
                                    severity = "CRITICAL"
                                    reasons.append("Tool inputSchema includes free-form 'query' string")
                                else:
                                    severity = "HIGH"
                                    reasons.append(f"Tool inputSchema includes free-form '{param_name}' string parameter")
            except Exception:
                pass
            
            # Check for file path parameters without validation
            try:
                props = (schema or {}).get("properties") or {}
                if isinstance(props, dict):
                    for param_name in ["path", "file", "file_path", "image_path", "input_image", "filename"]:
                        if param_name in props:
                            p = props.get(param_name) or {}
                            if isinstance(p, dict) and p.get("type") == "string":
                                # Check if there's a description mentioning validation or sandboxing
                                desc = (p.get("description") or "").lower()
                                if "sandbox" not in desc and "validate" not in desc and "allowlist" not in desc:
                                    risky = True
                                    severity = "HIGH"
                                    reasons.append(f"Tool accepts '{param_name}' file path parameter without apparent validation (LFI risk)")
            except Exception:
                pass
            
            # Check for URL parameters without validation
            try:
                props = (schema or {}).get("properties") or {}
                if isinstance(props, dict):
                    for param_name in ["url", "image", "uri", "link", "endpoint"]:
                        if param_name in props:
                            p = props.get(param_name) or {}
                            if isinstance(p, dict) and p.get("type") == "string":
                                desc = (p.get("description") or "").lower()
                                if "allowlist" not in desc and "whitelist" not in desc and "validate" not in desc:
                                    risky = True
                                    if severity != "CRITICAL":
                                        severity = "MEDIUM"
                                    reasons.append(f"Tool accepts '{param_name}' URL parameter without apparent validation (SSRF risk)")
            except Exception:
                pass
            
            if risky:
                findings.append({
                    "severity": severity,
                    "category": "MCP.ToolSurface",
                    "title": f"Security risk in tool '{t.get('name')}': {reasons[0] if reasons else 'Potential security vulnerability'}",
                    "description": "; ".join(reasons),
                    "location": t.get("source"),
                    "engine": "sentrascan-mcpprobe",
                })
        return findings
