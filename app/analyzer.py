
import ast
import re

MAX_LINE_LENGTH = 120

def get_call_name(node):
    """Return the full name of a function or method call."""

    if isinstance(node, ast.Name):
        return node.id

    if isinstance(node, ast.Attribute):
        parent_name = get_call_name(node.value)

        if parent_name:
            return f"{parent_name}.{node.attr}"

    return None

class CodeAnalyzer(ast.NodeVisitor):

    def __init__(self):
        self.findings = []
        self.os_aliases = {"os"}
        self.system_aliases = {"system"}
        self.eval_aliases = {"eval"}
        self.exec_aliases = {"exec"}

    def add_finding(self, node, severity, rule, message):
        self.findings.append({
            "line": getattr(node, "lineno", 1),
            "severity": severity,
            "rule": rule,
            "message": message
        })

    def visit_Import(self, node):
        for alias in node.names:
            if alias.name == "os":
                self.os_aliases.add(alias.asname or "os")

        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        if node.module == "os":
            for alias in node.names:
                if alias.name == "system":
                    self.system_aliases.add(alias.asname or "system")

        self.generic_visit(node)

    def visit_Call(self, node):
        call_name = get_call_name(node.func)

        if call_name in self.eval_aliases:
            self.add_finding(
                node,
                "high",
                "unsafe_eval",
                "Avoid using eval() because it can execute arbitrary code."
            )

        elif call_name in self.exec_aliases:
            self.add_finding(
                node,
                "high",
                "unsafe_exec",
                "Avoid using exec() because it can execute arbitrary code."
            )

        elif call_name in self.system_aliases:
            self.add_finding(
                node,
                "high",
                "os_system_usage",
                "Avoid os.system() and consider safer alternatives."
            )

        elif (
            isinstance(node.func, ast.Attribute)
            and node.func.attr == "system"
            and isinstance(node.func.value, ast.Name)
            and node.func.value.id in self.os_aliases
        ):
            self.add_finding(
                node,
                "high",
                "os_system_usage",
                "Avoid os.system() and consider safer alternatives."
            )

        elif call_name == "print":
            self.add_finding(
                node,
                "low",
                "debug_print",
                "Consider removing print() statements or using logging."
            )

        self.generic_visit(node)

    def visit_ExceptHandler(self, node):
        if node.type is None:
            self.add_finding(
                node,
                "medium",
                "bare_except",
                "Specify the exception type instead of using bare except."
            )

        self.generic_visit(node)

def analyze_code(code: str) -> dict:
    findings = []
    lines = code.splitlines()

    # Check line length
    for line_number, line in enumerate(lines, start=1):
        if len(line) > MAX_LINE_LENGTH:
            findings.append({
                "line": line_number,
                "severity": "low",
                "rule": "long_line",
                "message": f"Line exceeds {MAX_LINE_LENGTH} characters."
            })

    # Check TODO comments
    for line_number, line in enumerate(lines, start=1):
        if re.search(r"#.*\bTODO\b", line, re.IGNORECASE):
            findings.append({
                "line": line_number,
                "severity": "low",
                "rule": "todo_comment",
                "message": "This code contains a TODO comment."
            })

    # Parse Python code
    try:
        tree = ast.parse(code)

    except SyntaxError as error:
        return {
            "summary": {
                "total_issues": 1,
                "high": 1,
                "medium": 0,
                "low": 0
            },
            "findings": [
                {
                    "line": error.lineno or 1,
                    "severity": "high",
                    "rule": "syntax_error",
                    "message": error.msg
                }
            ],
            "syntax_error": True
        }

    analyzer = CodeAnalyzer()
    analyzer.visit(tree)

    findings.extend(analyzer.findings)

    summary = {
        "total_issues": len(findings),
        "high": sum(1 for item in findings if item["severity"] == "high"),
        "medium": sum(1 for item in findings if item["severity"] == "medium"),
        "low": sum(1 for item in findings if item["severity"] == "low")
    }

    return {
        "summary": summary,
        "findings": findings,
        "syntax_error": False
    }