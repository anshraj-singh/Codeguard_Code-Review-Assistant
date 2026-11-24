
import re


MAX_LINE_LENGTH = 120


def analyze_code(code: str) -> dict:
    findings = []

    lines = code.splitlines()

    for line_number, line in enumerate(lines, start=1):
        stripped_line = line.strip()

        if not stripped_line:
            continue

        # Security checks
        if re.search(r"\beval\s*\(", line):
            findings.append({
                "line": line_number,
                "severity": "high",
                "rule": "unsafe_eval",
                "message": "Avoid using eval() because it can execute arbitrary code."
            })

        if re.search(r"\bexec\s*\(", line):
            findings.append({
                "line": line_number,
                "severity": "high",
                "rule": "unsafe_exec",
                "message": "Avoid using exec() because it can execute arbitrary code."
            })

        if re.search(r"\bos\s*\.\s*system\s*\(", line):
            findings.append({
                "line": line_number,
                "severity": "high",
                "rule": "os_system_usage",
                "message": "Avoid os.system() and consider safer alternatives."
            })

        # Error handling check
        if re.match(r"^\s*except\s*:", line):
            findings.append({
                "line": line_number,
                "severity": "medium",
                "rule": "bare_except",
                "message": "Specify the exception type instead of using bare except."
            })

        # Style check
        if len(line) > MAX_LINE_LENGTH:
            findings.append({
                "line": line_number,
                "severity": "low",
                "rule": "long_line",
                "message": f"Line exceeds {MAX_LINE_LENGTH} characters."
            })

        # Debugging check
        if re.search(r"\bprint\s*\(", line):
            findings.append({
                "line": line_number,
                "severity": "low",
                "rule": "debug_print",
                "message": "Consider removing print() statements or using logging."
            })

        # TODO check
        if re.search(r"\bTODO\b", stripped_line, re.IGNORECASE):
            findings.append({
                "line": line_number,
                "severity": "low",
                "rule": "todo_comment",
                "message": "This code contains a TODO comment."
            })

    summary = {
        "total_issues": len(findings),
        "high": sum(1 for f in findings if f["severity"] == "high"),
        "medium": sum(1 for f in findings if f["severity"] == "medium"),
        "low": sum(1 for f in findings if f["severity"] == "low")
    }

    return {
        "summary": summary,
        "findings": findings
    }
