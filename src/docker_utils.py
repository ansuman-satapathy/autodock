import docker
from docker.errors import NotFound, APIError
from typing import Dict, Optional

# Initialize client once
try:
    client = docker.from_env()
except Exception:
    client = None

def get_container_details(container_id: str) -> Dict[str, str]:
    """
    Fetches detailed status of a container including healthchecks.
    """
    if not client:
        return {"error": "Docker daemon not reachable."}

    try:
        container = client.containers.get(container_id)
        attrs = container.attrs
        state = attrs.get("State", {})
        
        # internal healthcheck (if defined in Dockerfile)
        health_info = state.get("Health", {})
        health_status = health_info.get("Status", "not_configured")

        return {
            "id": container.short_id,
            "name": container.name,
            "status": state.get("Status", "unknown"),
            "health_check": health_status,
            "started_at": state.get("StartedAt", "")
        }
    except NotFound:
        return {"error": f"Container '{container_id}' not found."}
    except APIError as e:
        return {"error": f"Docker API Error: {str(e)}"}