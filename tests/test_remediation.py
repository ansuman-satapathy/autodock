from unittest.mock import MagicMock, patch
import docker.errors
import pytest
from remediation import restart_container_safely


def test_successful_restart():
    """
    Verifies that a container successfully restarts and reaches running status.
    """
    with patch("remediation.docker.from_env") as mock_docker:
        mock_client = MagicMock()
        mock_container = MagicMock()
        
        mock_docker.return_value = mock_client
        mock_client.containers.get.return_value = mock_container
        
        mock_container.name = "test-container"
        mock_container.status = "running"
        
        result = restart_container_safely("test-id")
        
        mock_container.restart.assert_called_once_with(timeout=10)
        assert mock_container.reload.call_count >= 1
        
        assert "✅" in result
        assert "test-container" in result


def test_container_not_found():
    """
    Verifies proper error handling when the container does not exist.
    """
    with patch("remediation.docker.from_env") as mock_docker:
        mock_client = MagicMock()
        mock_docker.return_value = mock_client
        
        mock_client.containers.get.side_effect = docker.errors.NotFound("Container not found")
        
        result = restart_container_safely("nonexistent-id")
        
        assert "❌" in result
        assert "not found" in result


def test_restart_exception():
    """
    Verifies proper error handling when restart fails with a generic exception.
    """
    with patch("remediation.docker.from_env") as mock_docker:
        mock_client = MagicMock()
        mock_container = MagicMock()
        
        mock_docker.return_value = mock_client
        mock_client.containers.get.return_value = mock_container
        
        mock_container.restart.side_effect = Exception("Restart timeout")
        
        result = restart_container_safely("test-id")
        
        assert "❌" in result
        assert "Restart timeout" in result


def test_restart_but_not_running():
    """
    Verifies warning message when container restarts but does not reach running status.
    """
    with patch("remediation.docker.from_env") as mock_docker:
        mock_client = MagicMock()
        mock_container = MagicMock()
        
        mock_docker.return_value = mock_client
        mock_client.containers.get.return_value = mock_container
        
        mock_container.name = "test-container"
        mock_container.status = "exited"
        
        result = restart_container_safely("test-id")
        
        mock_container.restart.assert_called_once_with(timeout=10)
        assert mock_container.reload.call_count >= 1
        
        assert "⚠️" in result
        assert "exited" in result


def test_restart_timeout():
    """
    Verifies timeout message when container does not reach running state within max_wait period.
    """
    with patch("remediation.docker.from_env") as mock_docker, \
         patch("remediation.time.sleep"):
        mock_client = MagicMock()
        mock_container = MagicMock()
        
        mock_docker.return_value = mock_client
        mock_client.containers.get.return_value = mock_container
        
        mock_container.name = "test-container"
        mock_container.status = "starting"
        
        result = restart_container_safely("test-id")
        
        mock_container.restart.assert_called_once_with(timeout=10)
        assert mock_container.reload.call_count > 1
        
        assert "⚠️" in result
        assert "30s" in result
        assert "starting" in result

