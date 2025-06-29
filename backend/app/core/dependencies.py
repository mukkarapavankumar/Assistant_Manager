"""
Dependency injection module to avoid circular imports.
"""

from typing import Optional
from app.agents.assistant_agent import AssistantAgent
from app.services.scheduler_service import SchedulerService

# Global instances
_assistant_agent: Optional[AssistantAgent] = None
_scheduler_service: Optional[SchedulerService] = None
_connection_manager = None

def set_assistant_agent(agent: AssistantAgent):
    """Set the global assistant agent instance."""
    global _assistant_agent
    _assistant_agent = agent

def get_assistant_agent() -> Optional[AssistantAgent]:
    """Get the global assistant agent instance."""
    return _assistant_agent

def set_scheduler_service(service: SchedulerService):
    """Set the global scheduler service instance."""
    global _scheduler_service
    _scheduler_service = service

def get_scheduler_service() -> Optional[SchedulerService]:
    """Get the global scheduler service instance."""
    return _scheduler_service

def set_connection_manager(manager):
    """Set the global connection manager instance."""
    global _connection_manager
    _connection_manager = manager

def get_connection_manager():
    """Get the global connection manager instance."""
    return _connection_manager 