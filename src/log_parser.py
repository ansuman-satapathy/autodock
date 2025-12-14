import re
from typing import List

def scan_logs_for_issues(logs: str) -> List[str]:
    """
    Scans a raw log string for critical errors and exceptions.
    Returns a list of unique, deduplicated error lines.
    """
    if not logs:
        return ["No logs found."]

    error_pattern = re.compile(
        r"(CRITICAL|FATAL|PANIC|EXCEPTION|Traceback|Error:|Uncaught)", 
        re.IGNORECASE
    )

    suspicious_lines = []
    seen = set()

    for line in logs.splitlines():
        clean_line = line.strip()
        if error_pattern.search(clean_line) and len(clean_line) > 10:
            if clean_line not in seen:
                suspicious_lines.append(clean_line)
                seen.add(clean_line)

    return suspicious_lines[-10:] if suspicious_lines else ["No obvious errors found in logs."]