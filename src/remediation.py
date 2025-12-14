import docker
import time
import docker.errors

def restart_container_safely(container_id: str) -> str:
    """
    Attempts to restart a container gracefully with exponential backoff retry logic.
    
    After initiating the restart, this function waits for the container to reach
    a stable state using exponential backoff (starting at 0.5s, doubling up to 4s max)
    with a total timeout of 30 seconds. This prevents false warnings for slow-starting
    containers while detecting failures quickly.
    
    Returns a success message if the container reaches "running" state, a warning if
    it reaches "exited" or "dead" state, or a timeout warning if it doesn't stabilize
    within the timeout period.
    """
    client = None
    try:
        client = docker.from_env()
        container = client.containers.get(container_id)
        
        container.restart(timeout=10)
        
        max_wait = 30
        wait_interval = 0.5
        max_interval = 4
        elapsed = 0
        
        while elapsed < max_wait:
            time.sleep(wait_interval)
            elapsed += wait_interval
            
            try:
                container.reload()
            except Exception as e:
                return f"❌ Fix failed: Unable to verify container status after restart: {str(e)}"
            
            if container.status == "running":
                return f"✅ Successfully restarted '{container.name}'."
            elif container.status in ["exited", "dead"]:
                return f"⚠️ Restarted, but container is now '{container.status}'."
            
            wait_interval = min(wait_interval * 2, max_interval)
        
        return f"⚠️ Container restart initiated, but status is '{container.status}' after {max_wait}s."
            
    except docker.errors.NotFound:
        return f"❌ Fix failed: Container '{container_id}' not found."
    except Exception as e:
        return f"❌ Fix failed: {str(e)}"
    finally:
        if client is not None:
            try:
                client.close()
            except Exception:
                pass