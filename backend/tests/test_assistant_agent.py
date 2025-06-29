"""Tests for assistant agent."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import json

from app.agents.assistant_agent import AssistantAgent, AgentState


@pytest.mark.unit
def test_agent_state_creation():
    """Test agent state creation and methods."""
    state = AgentState()
    
    assert state.current_workflow is None
    assert state.active_tasks == []
    assert state.pending_approvals == []
    assert state.error_count == 0
    assert state.workflow_step == "idle"


@pytest.mark.unit
def test_agent_state_error_tracking():
    """Test agent state error tracking."""
    state = AgentState()
    
    # Add error
    state.add_error("Test error")
    assert state.error_count == 1
    assert state.last_error == "Test error"
    
    # Add another error
    state.add_error("Another error")
    assert state.error_count == 2
    assert state.last_error == "Another error"
    
    # Reset errors
    state.reset_errors()
    assert state.error_count == 0
    assert state.last_error is None


@pytest.mark.unit
def test_agent_state_serialization():
    """Test agent state serialization."""
    state = AgentState()
    state.current_workflow = "test_workflow"
    state.active_tasks = [{"id": 1, "title": "Test Task"}]
    state.context = {"test": "value"}
    
    # Test to_dict
    state_dict = state.to_dict()
    assert state_dict['current_workflow'] == "test_workflow"
    assert state_dict['active_tasks'] == [{"id": 1, "title": "Test Task"}]
    assert state_dict['context'] == {"test": "value"}
    
    # Test from_dict
    new_state = AgentState.from_dict(state_dict)
    assert new_state.current_workflow == "test_workflow"
    assert new_state.active_tasks == [{"id": 1, "title": "Test Task"}]
    assert new_state.context == {"test": "value"}


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assistant_agent_initialization(mock_llm_service, mock_email_tools, mock_kanban_tools):
    """Test assistant agent initialization."""
    agent = AssistantAgent()
    
    # Mock the initialization methods
    with patch.object(agent.llm_service, 'initialize', new_callable=AsyncMock), \
         patch.object(agent, '_initialize_tools', new_callable=AsyncMock), \
         patch.object(agent, '_setup_workflow', new_callable=AsyncMock), \
         patch.object(agent, '_load_state', new_callable=AsyncMock):
        
        await agent.initialize()
        
        assert agent.is_active is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assistant_agent_process_message(assistant_agent):
    """Test message processing."""
    # Mock the workflow graph
    assistant_agent.graph = Mock()
    assistant_agent.graph.ainvoke = AsyncMock(return_value=assistant_agent.state)
    
    # Add a mock AI message to the state
    from langchain.schema import AIMessage
    assistant_agent.state.messages = [AIMessage(content="Test response")]
    
    result = await assistant_agent.process_message("Test message")
    
    assert result == "Test response"
    assistant_agent.graph.ainvoke.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assistant_agent_fallback_processing(assistant_agent):
    """Test fallback message processing."""
    # Disable graph to trigger fallback
    assistant_agent.graph = None
    
    result = await assistant_agent.process_message("status report")
    
    assert "fallback mode" in result.lower()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assistant_agent_analyze_request(assistant_agent):
    """Test request analysis."""
    from langchain.schema import HumanMessage
    
    # Test email-related request
    assistant_agent.state.messages = [HumanMessage(content="send email updates")]
    result_state = await assistant_agent._analyze_request(assistant_agent.state)
    assert result_state.context["action"] == "send_emails"
    
    # Test kanban-related request
    assistant_agent.state.messages = [HumanMessage(content="update kanban board")]
    result_state = await assistant_agent._analyze_request(assistant_agent.state)
    assert result_state.context["action"] == "board_status"
    
    # Test status request
    assistant_agent.state.messages = [HumanMessage(content="show me the status")]
    result_state = await assistant_agent._analyze_request(assistant_agent.state)
    assert result_state.context["action"] == "generate_report"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assistant_agent_simple_tools(assistant_agent):
    """Test simple tool implementations."""
    # Test send emails tool
    result = await assistant_agent._simple_send_emails(assistant_agent.state)
    assert "email" in result.lower()
    
    # Test board status tool
    result = await assistant_agent._simple_board_status(assistant_agent.state)
    assert isinstance(result, str)
    
    # Test generate report tool
    result = await assistant_agent._simple_generate_report(assistant_agent.state)
    assert isinstance(result, str)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assistant_agent_get_status(assistant_agent):
    """Test getting agent status."""
    status = await assistant_agent.get_status()
    
    assert 'is_active' in status
    assert 'current_workflow' in status
    assert 'workflow_step' in status
    assert 'active_tasks' in status
    assert 'pending_approvals' in status
    assert 'last_activity' in status
    assert 'error_count' in status


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assistant_agent_error_handling(assistant_agent):
    """Test agent error handling."""
    # Simulate an error in tool execution
    assistant_agent.email_tools.get_active_team_members = AsyncMock(side_effect=Exception("Test error"))
    
    result = await assistant_agent._simple_send_emails(assistant_agent.state)
    
    assert "error" in result.lower()
    assert assistant_agent.state.error_count > 0


@pytest.mark.unit
@pytest.mark.asyncio
async def test_assistant_agent_cleanup(assistant_agent):
    """Test agent cleanup."""
    assistant_agent._save_state = AsyncMock()
    
    await assistant_agent.cleanup()
    
    assert assistant_agent.is_active is False
    assistant_agent._save_state.assert_called_once()