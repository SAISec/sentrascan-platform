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
    {
        "id": "PY.ZipSlip.ExtractAll",
        "regex": re.compile(r'zipfile\.ZipFile\([^)]+\)[\s\S]*?\.extractall\([^)]*\)', re.MULTILINE),
        "evidence": "zipfile.extractall() used without path validation - Zip Slip vulnerability",
        "severity": "CRITICAL",
        "title": "Zip Slip vulnerability: extractall() without path sanitization",
    },
    {
        "id": "PY.RCE.Exec",
        "regex": re.compile(r'\bexec\s*\([^)]*(?:code|user_input|command|script)', re.MULTILINE | re.IGNORECASE),
        "evidence": "exec() with user-controlled input - Remote Code Execution risk",
        "severity": "HIGH",
        "title": "Remote Code Execution: exec() with user-controlled input",
    },
    {
        "id": "PY.RCE.Eval",
        "regex": re.compile(r'\beval\s*\([^)]*(?:code|user_input|command)', re.MULTILINE | re.IGNORECASE),
        "evidence": "eval() with user-controlled input - Remote Code Execution risk",
        "severity": "HIGH",
        "title": "Remote Code Execution: eval() with user-controlled input",
    },
    {
        "id": "PY.LFI.Open",
        "regex": re.compile(r'open\s*\([^)]*(?:path|file|filename|image_path|input_image)[^)]*\)', re.MULTILINE | re.IGNORECASE),
        "evidence": "open() with user-controlled path - Local File Inclusion risk",
        "severity": "HIGH",
        "title": "Local File Inclusion: open() with user-controlled file path",
    },
    {
        "id": "PY.SSRF.RequestsGet",
        "regex": re.compile(r'requests\.get\s*\([^)]*(?:url|image|uri|link)', re.MULTILINE | re.IGNORECASE),
        "evidence": "requests.get() with user-controlled URL - SSRF risk",
        "severity": "MEDIUM",
        "title": "Server-Side Request Forgery: requests.get() without URL validation",
    },
    {
        "id": "PY.SSRF.URLOpen",
        "regex": re.compile(r'urllib\.(?:request\.)?urlopen\s*\([^)]*(?:url|image|uri|link)', re.MULTILINE | re.IGNORECASE),
        "evidence": "urllib.urlopen() with user-controlled URL - SSRF risk",
        "severity": "MEDIUM",
        "title": "Server-Side Request Forgery: urllib.urlopen() without URL validation",
    },
]

EXCLUDE_DIRS = {".git", "node_modules", "dist", "build", "__pycache__", ".venv", "venv"}
INCLUDE_EXT = {".py", ".json", ".ts", ".js", ".yaml", ".yml"}

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
                # Get line numbers for better reporting
                lines = text.split('\n')
                for rule in RISK_PATTERNS:
                    matches = rule["regex"].finditer(text)
                    for match in matches:
                        # Find line number
                        line_num = text[:match.start()].count('\n') + 1
                        # Get context (line content)
                        line_content = lines[line_num - 1] if line_num <= len(lines) else ""
                        findings.append({
                            "severity": rule["severity"],
                            "category": "Code.Pattern",
                            "title": rule["title"],
                            "description": f"{rule['evidence']} (line {line_num})",
                            "location": f"{path}:{line_num}",
                            "engine": "sentrascan-coderule",
                            "rule_id": rule["id"],
                            "line_number": line_num,
                            "line_content": line_content.strip()[:200],  # Truncate long lines
                        })
        return findings
