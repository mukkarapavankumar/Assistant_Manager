"""Tests for LLM service."""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import aiohttp

from app.services.llm_service import LLMService


@pytest.mark.unit
@pytest.mark.asyncio
async def test_llm_service_initialization():
    """Test LLM service initialization."""
    service = LLMService()
    
    with patch.object(service, '_test_connection', new_callable=AsyncMock), \
         patch.object(service, '_ensure_model_available', new_callable=AsyncMock):
        
        await service.initialize()
        
        assert service.is_available is True


@pytest.mark.unit
@pytest.mark.asyncio
async def test_llm_service_initialization_failure():
    """Test LLM service initialization failure."""
    service = LLMService()
    
    with patch.object(service, '_test_connection', side_effect=Exception("Connection failed")):
        await service.initialize()
        
        assert service.is_available is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_simple_response():
    """Test simple response generation."""
    service = LLMService()
    service.is_available = True
    service.session = Mock()
    
    # Mock successful response
    mock_response = Mock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={'response': 'Test response'})
    
    service.session.post = AsyncMock(return_value=mock_response)
    
    result = await service.generate_simple_response("Test prompt")
    
    assert result == "Test response"
    service.session.post.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_generate_simple_response_unavailable():
    """Test response generation when service unavailable."""
    service = LLMService()
    service.is_available = False
    
    result = await service.generate_simple_response("Test prompt")
    
    assert "LLM service is not available" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_email_content_simple():
    """Test email content parsing."""
    service = LLMService()
    service.is_available = True
    service.session = Mock()
    
    # Mock successful response with JSON
    mock_response = Mock()
    mock_response.status = 200
    mock_response.json = AsyncMock(return_value={
        'response': '{"task_title": "Test Task", "status": "in_progress", "priority": "medium", "description": "Test desc"}'
    })
    
    service.session.post = AsyncMock(return_value=mock_response)
    
    result = await service.parse_email_content_simple("Test email content")
    
    assert result['task_title'] == "Test Task"
    assert result['status'] == "in_progress"
    assert result['priority'] == "medium"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_parse_email_content_fallback():
    """Test email content parsing fallback."""
    service = LLMService()
    service.is_available = False
    
    email_content = "I'm working on the authentication API. It's in progress and high priority."
    
    result = await service.parse_email_content_simple(email_content)
    
    assert 'task_title' in result
    assert 'status' in result
    assert 'priority' in result
    assert result['status'] == 'in_progress'  # Should detect from content


@pytest.mark.unit
def test_simplify_prompt():
    """Test prompt simplification."""
    service = LLMService()
    
    long_prompt = "This is a very long prompt " * 100
    simplified = service._simplify_prompt(long_prompt, 100)
    
    assert len(simplified) <= 1003  # 1000 + "..."
    assert simplified.endswith("...")


@pytest.mark.unit
def test_detect_status():
    """Test status detection from content."""
    service = LLMService()
    
    # Test various status keywords
    assert service._detect_status("task is done and completed") == "done"
    assert service._detect_status("I'm blocked on this issue") == "blocked"
    assert service._detect_status("ready for review") == "review"
    assert service._detect_status("starting work on this") == "todo"
    assert service._detect_status("currently working on it") == "in_progress"
    assert service._detect_status("no specific keywords") == "in_progress"  # default


@pytest.mark.unit
def test_detect_priority():
    """Test priority detection from content."""
    service = LLMService()
    
    # Test various priority keywords
    assert service._detect_priority("this is urgent and critical") == "urgent"
    assert service._detect_priority("high priority task") == "high"
    assert service._detect_priority("low priority, no rush") == "low"
    assert service._detect_priority("normal task") == "medium"  # default


@pytest.mark.unit
@pytest.mark.asyncio
async def test_health_check():
    """Test health check functionality."""
    service = LLMService()
    service.session = Mock()
    
    # Mock successful health check
    mock_response = Mock()
    mock_response.status = 200
    service.session.get = AsyncMock(return_value=mock_response)
    
    result = await service.health_check()
    
    assert result['status'] == 'healthy'
    assert 'model' in result
    assert 'available' in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_health_check_failure():
    """Test health check failure."""
    service = LLMService()
    service.session = None
    
    result = await service.health_check()
    
    assert result['status'] == 'unhealthy'
    assert 'error' in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cleanup():
    """Test service cleanup."""
    service = LLMService()
    service.session = Mock()
    service.session.close = AsyncMock()
    service.is_available = True
    
    await service.cleanup()
    
    assert service.session is None
    assert service.is_available is False
    service.session.close.assert_called_once()