"""Enhanced API endpoints for agent interactions with better error handling."""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, Optional
import logging
import asyncio

from app.models.schemas import AgentQuery, AgentResponse, AgentStatus, APIResponse
from app.core.dependencies import get_assistant_agent

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/query", response_model=AgentResponse)
async def query_agent(query: AgentQuery):
    """Send a query to the assistant agent with enhanced error handling."""
    try:
        agent = get_assistant_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Agent not available")
        
        if not agent.is_active:
            raise HTTPException(status_code=503, detail="Agent is not active")
        
        # Process query with timeout
        try:
            response = await asyncio.wait_for(
                agent.process_message(query.query, query.context),
                timeout=60  # 1 minute timeout
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Query processing timed out")
        
        # Determine confidence based on agent state
        confidence = 0.9 if agent.state.error_count == 0 else max(0.3, 0.9 - (agent.state.error_count * 0.1))
        
        return AgentResponse(
            response=response,
            confidence=confidence,
            sources=["agent_knowledge", "database"],
            suggested_actions=_get_suggested_actions(query.query, response)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing agent query: {e}")
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

@router.get("/status", response_model=AgentStatus)
async def get_agent_status():
    """Get current agent status with health information."""
    try:
        agent = get_assistant_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Agent not available")
        
        status = await agent.get_status()
        
        return AgentStatus(
            is_active=status["is_active"],
            current_task=status.get("workflow_step", "idle"),
            next_scheduled_action=None,  # TODO: Implement scheduling
            tasks_completed=status.get("active_tasks", 0),
            emails_sent=0,  # TODO: Get from email service
            responses_received=0,  # TODO: Get from email service
            last_activity=status["last_activity"]
        )
        
    except Exception as e:
        logger.error(f"Error getting agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/trigger-workflow")
async def trigger_workflow(workflow_type: str):
    """Manually trigger a specific workflow with validation."""
    try:
        agent = get_assistant_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Agent not available")
        
        if not agent.is_active:
            raise HTTPException(status_code=503, detail="Agent is not active")
        
        # Validate workflow type
        valid_workflows = {
            "weekly_update": "Please send weekly update requests to all team members",
            "deadline_check": "Check for overdue tasks and send reminders",
            "kanban_sync": "Update and synchronize the kanban board",
            "status_summary": "Generate a status summary for all active projects",
            "check_responses": "Check for new email responses from team members",
            "github_publish": "Publish the current kanban board to GitHub Pages"
        }
        
        if workflow_type not in valid_workflows:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid workflow type. Valid options: {list(valid_workflows.keys())}"
            )
        
        message = valid_workflows[workflow_type]
        
        # Execute workflow with timeout
        try:
            response = await asyncio.wait_for(
                agent.process_message(message),
                timeout=120  # 2 minute timeout for workflows
            )
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Workflow execution timed out")
        
        return APIResponse(
            success=True,
            message=f"Workflow '{workflow_type}' completed successfully",
            data={"response": response, "workflow_type": workflow_type}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approve-changes")
async def approve_changes(change_ids: list[int]):
    """Approve pending kanban changes with validation."""
    try:
        agent = get_assistant_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Agent not available")
        
        if not change_ids:
            raise HTTPException(status_code=400, detail="No change IDs provided")
        
        # Validate change IDs
        if len(change_ids) > 50:  # Reasonable limit
            raise HTTPException(status_code=400, detail="Too many changes to approve at once")
        
        # Use kanban tools directly for approval
        result = await agent.kanban_tools.approve_changes(change_ids)
        
        return APIResponse(
            success=True,
            message=result,
            data={"approved_changes": change_ids, "count": len(change_ids)}
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving changes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def get_agent_health():
    """Get detailed agent health information."""
    try:
        agent = get_assistant_agent()
        if not agent:
            return {
                "status": "unhealthy",
                "agent_available": False,
                "error": "Agent not initialized"
            }
        
        status = await agent.get_status()
        
        health_info = {
            "status": "healthy" if status["is_active"] else "unhealthy",
            "agent_available": True,
            "is_active": status["is_active"],
            "workflow_step": status.get("workflow_step", "unknown"),
            "error_count": status.get("error_count", 0),
            "last_error": status.get("last_error"),
            "llm_status": status.get("llm_status", "unknown"),
            "last_activity": status["last_activity"]
        }
        
        return health_info
        
    except Exception as e:
        logger.error(f"Error getting agent health: {e}")
        return {
            "status": "unhealthy",
            "agent_available": False,
            "error": str(e)
        }

@router.post("/reset-errors")
async def reset_agent_errors():
    """Reset agent error count and state."""
    try:
        agent = get_assistant_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Agent not available")
        
        agent.state.reset_errors()
        await agent._save_state()
        
        return APIResponse(
            success=True,
            message="Agent errors reset successfully"
        )
        
    except Exception as e:
        logger.error(f"Error resetting agent errors: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _get_suggested_actions(query: str, response: str) -> list[str]:
    """Generate suggested actions based on query and response."""
    suggestions = []
    query_lower = query.lower()
    
    if "email" in query_lower:
        suggestions.extend([
            "Check email responses",
            "Send follow-up reminders",
            "View email statistics"
        ])
    
    if "task" in query_lower or "kanban" in query_lower:
        suggestions.extend([
            "Update kanban board",
            "Create new task",
            "Check pending approvals"
        ])
    
    if "status" in query_lower or "report" in query_lower:
        suggestions.extend([
            "Generate detailed report",
            "Analyze team performance",
            "Check overdue tasks"
        ])
    
    if "github" in query_lower or "publish" in query_lower:
        suggestions.extend([
            "Sync to GitHub Pages",
            "Check GitHub status",
            "View published board"
        ])
    
    # Limit to 3 suggestions
    return suggestions[:3]