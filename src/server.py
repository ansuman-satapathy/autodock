from mcp.server.fastmcp import FastMCP
import docker
import docker.errors
from .docker_utils import get_container_details
from .log_parser import scan_logs_for_issues

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
    
    # CodeRabbit Fix: Safely handle None values before calling .upper()
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
        # CodeRabbit Fix: Guard against excessive lines
        lines = max(1, min(int(lines), 2000))

        client = docker.from_env()
        container = client.containers.get(container_id)
        
        # Get raw logs
        raw_logs = container.logs(tail=lines).decode('utf-8', errors='ignore')
        
        # Analyze using our helper logic
        issues = scan_logs_for_issues(raw_logs)
        
        if len(issues) == 1 and issues[0].startswith("✅"):
            return issues[0]
            
        return "⚠️ **Issues Found in Logs:**\n" + "\n".join([f"- {i}" for i in issues])
        
    # CodeRabbit Fix: Explicit Error Handling
    except docker.errors.NotFound:
        return f"❌ Failed to analyze logs: Container '{container_id}' not found."
    except docker.errors.APIError as e:
        return f"❌ Failed to analyze logs: Docker API error: {e}"
    except Exception as e:
        return f"❌ Failed to analyze logs: {str(e)}"

if __name__ == "__main__":
    mcp.run()