from src.log_parser import scan_logs_for_issues

def test_no_logs_returns_message():
    result = scan_logs_for_issues("")
    assert result == ["No logs found."]

def test_clean_logs_return_success():
    clean_log = "Info: Server started\nDebug: Connection active"
    result = scan_logs_for_issues(clean_log)
    assert result[0].startswith("✅")

def test_detects_critical_errors():
    error_log = """
    Info: Starting process
    CRITICAL: Database connection failed
    Info: Retrying
    Exception: NullPointerException at line 40
    """
    issues = scan_logs_for_issues(error_log)
    
    assert len(issues) == 2
    assert "CRITICAL: Database connection failed" in issues
    assert "Exception: NullPointerException at line 40" in issues

def test_deduplicates_errors():
    repeat_log = """
    Error: Timeout detected
    Error: Timeout detected
    Error: Timeout detected
    """
    issues = scan_logs_for_issues(repeat_log)
    assert len(issues) == 1