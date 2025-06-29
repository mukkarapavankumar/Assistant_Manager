"""Pytest configuration and fixtures for Assistant Manager tests."""

import pytest
import asyncio
import tempfile
import os
from unittest.mock import Mock, AsyncMock
from pathlib import Path

from app.models.database import db, MODELS
from app.agents.assistant_agent import AssistantAgent
from app.services.llm_service import LLMService
from app.tools.email_tools import EmailTools
from app.tools.kanban_tools import KanbanTools


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_db():
    """Create a temporary database for testing."""
    # Create temporary database file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp_file.close()
    
    # Configure test database
    db.init(temp_file.name)
    db.connect()
    db.create_tables(MODELS, safe=True)
    
    yield db
    
    # Cleanup
    db.close()
    os.unlink(temp_file.name)


@pytest.fixture
def mock_llm_service():
    """Create a mock LLM service for testing."""
    mock_service = Mock(spec=LLMService)
    mock_service.is_available = True
    mock_service.initialize = AsyncMock()
    mock_service.generate_simple_response = AsyncMock(return_value="Mock LLM response")
    mock_service.parse_email_content_simple = AsyncMock(return_value={
        'task_title': 'Test Task',
        'status': 'in_progress',
        'priority': 'medium',
        'description': 'Test description'
    })
    mock_service.health_check = AsyncMock(return_value={
        'status': 'healthy',
        'model': 'test-model',
        'available': True
    })
    mock_service.cleanup = AsyncMock()
    return mock_service


@pytest.fixture
def mock_email_tools():
    """Create mock email tools for testing."""
    mock_tools = Mock(spec=EmailTools)
    mock_tools.initialize = AsyncMock()
    mock_tools.get_active_team_members = AsyncMock(return_value=[
        {
            'id': 1,
            'name': 'Test User',
            'email': 'test@example.com',
            'role': 'Developer',
            'response_rate': 95.0
        }
    ])
    mock_tools.search_outlook_contacts = Mock(return_value=[
        {
            'name': 'John Doe',
            'email': 'john@example.com',
            'company': 'Test Corp',
            'department': 'Engineering',
            'job_title': 'Senior Developer',
            'source': 'contacts'
        }
    ])
    mock_tools.cleanup = AsyncMock()
    return mock_tools


@pytest.fixture
def mock_kanban_tools():
    """Create mock kanban tools for testing."""
    mock_tools = Mock(spec=KanbanTools)
    mock_tools.initialize = AsyncMock()
    return mock_tools


@pytest.fixture
def assistant_agent(mock_llm_service, mock_email_tools, mock_kanban_tools):
    """Create an assistant agent with mocked dependencies."""
    agent = AssistantAgent()
    
    # Replace services with mocks
    agent.llm_service = mock_llm_service
    agent.email_tools = mock_email_tools
    agent.kanban_tools = mock_kanban_tools
    
    # Mock the initialization
    agent.is_active = True
    agent.graph = Mock()
    
    return agent


@pytest.fixture
def sample_task_data():
    """Sample task data for testing."""
    return {
        'title': 'Test Task',
        'description': 'Test task description',
        'status': 'todo',
        'assignee_id': 1,
        'priority': 'medium',
        'tags': ['test', 'sample']
    }


@pytest.fixture
def sample_team_member_data():
    """Sample team member data for testing."""
    return {
        'name': 'John Doe',
        'email': 'john.doe@example.com',
        'role': 'Senior Developer',
        'active': True
    }


@pytest.fixture
def sample_email_template_data():
    """Sample email template data for testing."""
    return {
        'name': 'Test Template',
        'subject': 'Test Subject - {{date}}',
        'content': 'Hello {{name}}, this is a test email.',
        'template_type': 'update_request',
        'variables': ['name', 'date'],
        'active': True
    }