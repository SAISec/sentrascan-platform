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
        for root, _, files in os.walk(self.repo_path):
            for f in files:
                if f.endswith("server.py") and ("mcp" in root or "_mcp_" in root or "mcp" in f):
                    candidates.append(os.path.join(root, f))
        # Fallback: any server.py under src/
        if not candidates:
            for root, _, files in os.walk(os.path.join(self.repo_path, "src")):
                for f in files:
                    if f == "server.py":
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
            # Heuristic: any tool named execute_sql or containing a free-form 'query' string parameter
            risky = False
            reasons: List[str] = []
            if "execute_sql" in name or (name.startswith("execute_") and name.endswith("_sql")):
                risky = True
                reasons.append("Tool name suggests arbitrary SQL execution")
            try:
                props = (schema or {}).get("properties") or {}
                if isinstance(props, dict) and "query" in props:
                    p = props.get("query") or {}
                    if isinstance(p, dict) and p.get("type") == "string":
                        risky = True
                        reasons.append("Tool inputSchema includes free-form 'query' string")
            except Exception:
                pass
            if risky:
                findings.append({
                    "severity": "CRITICAL",
                    "category": "MCP.ToolSurface",
                    "title": f"Potential arbitrary SQL execution surface: tool '{t.get('name')}'",
                    "description": "; ".join(reasons),
                    "location": t.get("source"),
                    "engine": "mcp-probe",
                })
        return findings
