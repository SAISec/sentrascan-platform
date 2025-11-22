import os
import re
from typing import List, Dict, Any

RISK_PATTERNS = [
    {
        "id": "PY.SQL.Execute.FString",
        "regex": re.compile(r"cursor\.execute\(\s*([a-zA-Z_][\w]*)\s*\)\s*\n", re.MULTILINE),
        "evidence": "cursor.execute(query)",
        "severity": "HIGH",
        "title": "SQL executed from variable; check for parameterization",
    },
    {
        "id": "PY.SQL.Execute.FString",
        "regex": re.compile(r'\b(query|sql)\s*=\s*f"[^"]*\{[^"]*\}', re.MULTILINE),
        "evidence": "f-string used to build SQL",
        "severity": "HIGH",
        "title": "f-string used to build SQL",
    },
    {
        "id": "PY.SQL.Concat",
        "regex": re.compile(r"cursor\.execute\(\s*\w+\s*\+\s*\w+", re.MULTILINE),
        "evidence": "String concatenation used to build SQL",
        "severity": "HIGH",
        "title": "Concatenation used to build SQL",
    },
    {
        "id": "PY.SQL.Format",
        "regex": re.compile(r"cursor\.execute\(\s*\w+\.format\(.*\)\s*\)", re.MULTILINE),
        "evidence": "str.format used to build SQL",
        "severity": "HIGH",
        "title": "str.format used to build SQL",
    },
    {
        "id": "PY.SQLAlchemy.Text.FString",
        "regex": re.compile(r"sqlalchemy\.text\(f\".*\{.*\}.*\)"),
        "evidence": "sqlalchemy.text with f-string",
        "severity": "HIGH",
        "title": "SQLAlchemy text() with f-string",
    },
    {
        "id": "PY.SQLite.Raw",
        "regex": re.compile(r"sqlite3\.connect\(.*\)[\s\S]*?execute\(\s*\w+\s*\)"),
        "evidence": "sqlite3 execute with composed string",
        "severity": "HIGH",
        "title": "sqlite3 execute from variable",
    },
    {
        "id": "MCP.Tool.ExecuteSQL",
        "regex": re.compile(r"Tool\s*\(\s*name\s*=\s*['\"]execute_sql['\"]", re.MULTILINE),
        "evidence": "Tool(name='execute_sql')",
        "severity": "CRITICAL",
        "title": "MCP tool exposes arbitrary SQL execution",
    },
    {
        "id": "MCP.Tool.QueryStringParam",
        "regex": re.compile(r'inputSchema[\s\S]*?\{[\s\S]*?"query"\s*:\s*\{[\s\S]*?"type"\s*:\s*"string"', re.MULTILINE),
        "evidence": "inputSchema includes free-form 'query' string",
        "severity": "CRITICAL",
        "title": "Tool accepts free-form SQL query string",
    },
]

EXCLUDE_DIRS = {".git", "node_modules", "dist", "build", "__pycache__"}
INCLUDE_EXT = {".py", ".json", ".ts", ".js"}

class RuleScanner:
    def scan_repo(self, repo_path: str) -> List[Dict[str, Any]]:
        findings: List[Dict[str, Any]] = []
        for root, dirs, files in os.walk(repo_path):
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
            for f in files:
                _, ext = os.path.splitext(f)
                if ext.lower() not in INCLUDE_EXT:
                    continue
                path = os.path.join(root, f)
                try:
                    with open(path, "r", encoding="utf-8", errors="ignore") as fh:
                        text = fh.read()
                except Exception:
                    continue
                for rule in RISK_PATTERNS:
                    if rule["regex"].search(text):
                        findings.append({
                            "severity": rule["severity"],
                            "category": "Code.Pattern",
                            "title": rule["title"],
                            "description": rule["evidence"],
                            "location": path,
                            "engine": "regex-rules",
                            "rule_id": rule["id"],
                        })
        return findings
