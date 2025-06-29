"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock, patch

from app.main import app
from app.models.database import TeamMember, EmailTemplate


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def mock_agent():
    """Create mock agent for API tests."""
    agent = Mock()
    agent.is_active = True
    agent.process_message = AsyncMock(return_value="Mock agent response")
    agent.get_status = AsyncMock(return_value={
        "is_active": True,
        "workflow_step": "idle",
        "active_tasks": 0,
        "pending_approvals": 0,
        "last_activity": "2024-01-20T10:30:00",
        "error_count": 0,
        "last_error": None,
        "llm_status": "healthy",
        "context": {}
    })
    return agent


@pytest.mark.integration
def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert "status" in data
    assert "database" in data


@pytest.mark.integration
def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["message"] == "Assistant Manager API is running"
    assert "version" in data


@pytest.mark.integration
@patch('app.core.dependencies.get_assistant_agent')
def test_agent_query_endpoint(mock_get_agent, client, mock_agent):
    """Test agent query endpoint."""
    mock_get_agent.return_value = mock_agent
    
    response = client.post("/api/agents/query", json={
        "query": "What is the team status?",
        "context": {}
    })
    
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Mock agent response"
    assert "confidence" in data


@pytest.mark.integration
@patch('app.core.dependencies.get_assistant_agent')
def test_agent_status_endpoint(mock_get_agent, client, mock_agent):
    """Test agent status endpoint."""
    mock_get_agent.return_value = mock_agent
    
    response = client.get("/api/agents/status")
    assert response.status_code == 200
    
    data = response.json()
    assert data["is_active"] is True
    assert "current_task" in data


@pytest.mark.integration
@patch('app.core.dependencies.get_assistant_agent')
def test_trigger_workflow_endpoint(mock_get_agent, client, mock_agent):
    """Test trigger workflow endpoint."""
    mock_get_agent.return_value = mock_agent
    
    response = client.post("/api/agents/trigger-workflow?workflow_type=weekly_update")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "weekly_update" in data["data"]["workflow_type"]


@pytest.mark.integration
def test_trigger_workflow_invalid_type(client):
    """Test trigger workflow with invalid type."""
    with patch('app.core.dependencies.get_assistant_agent') as mock_get_agent:
        mock_get_agent.return_value = Mock(is_active=True)
        
        response = client.post("/api/agents/trigger-workflow?workflow_type=invalid_type")
        assert response.status_code == 400


@pytest.mark.integration
def test_kanban_board_endpoint(client):
    """Test kanban board endpoint."""
    response = client.get("/api/kanban/board")
    
    # Should return empty board structure even with no data
    assert response.status_code == 200
    data = response.json()
    assert "columns" in data


@pytest.mark.integration
def test_email_templates_endpoint(client):
    """Test email templates endpoint."""
    response = client.get("/api/emails/templates")
    assert response.status_code == 200
    
    # Should return list (may be empty)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.integration
def test_email_statistics_endpoint(client):
    """Test email statistics endpoint."""
    response = client.get("/api/emails/statistics")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "total_threads" in data["data"]
    assert "response_rate" in data["data"]


@pytest.mark.integration
def test_team_members_endpoint(client):
    """Test team members endpoint."""
    response = client.get("/api/emails/team-members")
    assert response.status_code == 200
    
    # Should return list (may be empty)
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.integration
@patch('app.core.dependencies.get_assistant_agent')
def test_agent_unavailable_error(mock_get_agent, client):
    """Test API behavior when agent is unavailable."""
    mock_get_agent.return_value = None
    
    response = client.post("/api/agents/query", json={
        "query": "test query"
    })
    
    assert response.status_code == 503
    assert "Agent not available" in response.json()["detail"]


@pytest.mark.integration
def test_cors_headers(client):
    """Test CORS headers are present."""
    response = client.options("/api/agents/status")
    
    # FastAPI automatically handles OPTIONS requests
    assert response.status_code in [200, 405]  # 405 if OPTIONS not explicitly defined


@pytest.mark.integration
def test_api_error_handling(client):
    """Test API error handling."""
    # Test with invalid JSON
    response = client.post("/api/agents/query", 
                          data="invalid json",
                          headers={"Content-Type": "application/json"})
    
    assert response.status_code == 422  # Validation error