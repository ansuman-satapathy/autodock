from mcp.server.fastmcp import FastMCP
import docker
import docker.errors
from .docker_utils import get_container_details
from .log_parser import scan_logs_for_issues
from .remediation import restart_container_safely
import re

def redact_sensitive_data(text: str) -> str:
    """
    Redacts sensitive information like API keys, tokens, emails, and passwords from the input text.
    """
    patterns = {
        r'(?i)(api[_-]?key|token|secret|password|passwd|pwd|auth)[ \t]*[:=][ \t]*["\']?[a-zA-Z0-9%\-_]{8,}["\']?': r'\1: [REDACTED]',
        r'Bearer\s+[a-zA-Z0-9\._\-]{20,}': 'Bearer [REDACTED]',
        r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}': '[EMAIL REDACTED]',
        r'(?i)(postgres|mysql|mongodb|redis)://[^\s]+': '[CONNECTION STRING REDACTED]'
    }
    
    redacted_text = text
    for pattern, replacement in patterns.items():
        redacted_text = re.sub(pattern, replacement, redacted_text)
        
    return redacted_text

mcp = FastMCP("AutoDock")

@mcp.tool()
def diagnose_container(container_id: str) -> str:
    """
    Performs a deep health check on a Docker container.
    Use this to check if a container is running, paused, or unhealthy.
    """
    data = get_container_details(container_id)
    
    if "error" in data:
        return f"❌ DIAGNOSIS FAILED: {data['error']}"
    
    status = (data.get('status') or 'unknown').upper()
    health = (data.get('health_check') or 'unknown').upper()
    
    return (
        f"🩺 **Container Diagnosis for: {data.get('name')}**\n"
        f"- **Status:** {status}\n"
        f"- **Healthcheck:** {health}\n"
        f"- **ID:** {data.get('id')}\n"
    )

@mcp.tool()
def analyze_logs(container_id: str, lines: int = 200) -> str:
    """
    Scans container logs for specific error keywords (Exception, Panic, Fatal).
    Use this to find the root cause of a crash.
    """
    try:
        lines = max(1, min(int(lines), 2000))

        client = docker.from_env()
        container = client.containers.get(container_id)
        
        raw_logs = container.logs(tail=lines).decode('utf-8', errors='ignore')
        
        issues = scan_logs_for_issues(raw_logs)
        
        if len(issues) == 1 and issues[0].startswith("✅"):
            return redact_sensitive_data(issues[0])
            
        return "⚠️ **Issues Found in Logs:**\n" + "\n".join([f"- {redact_sensitive_data(i)}" for i in issues])
        
    except docker.errors.NotFound:
        return f"❌ Failed to analyze logs: Container '{container_id}' not found."
    except docker.errors.APIError as e:
        return f"❌ Failed to analyze logs: Docker API error: {e}"
    except Exception as e:
        return f"❌ Failed to analyze logs: {str(e)}"

@mcp.tool()
def fix_container(container_id: str) -> str:
    """
    Restarts a crashed or unhealthy container safely. 
    Use this tool if the diagnosis shows the container is 'exited' or 'unhealthy'.
    """
    return restart_container_safely(container_id)

if __name__ == "__main__":
    mcp.run()