import docker
import time
import docker.errors

def restart_container_safely(container_id: str) -> str:
    """
    Attempts to restart a container gracefully.
    If it fails to start, it returns the error log.
    """
    try:
        client = docker.from_env()
        container = client.containers.get(container_id)
        
        container.restart(timeout=10)
        
        time.sleep(2)
        container.reload()
        
        if container.status == "running":
            return f"✅ Successfully restarted '{container.name}'."
        else:
            return f"⚠️ Restarted, but container is now '{container.status}'."
            
    except docker.errors.NotFound:
        return f"❌ Fix failed: Container '{container_id}' not found."
    except Exception as e:
        return f"❌ Fix failed: {str(e)}"