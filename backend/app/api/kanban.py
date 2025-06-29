"""API endpoints for kanban board management."""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
import json
from datetime import datetime

from app.models.schemas import KanbanBoard, Task, TaskCreate, TaskUpdate, APIResponse
from app.models.database import Task as TaskModel, TeamMember as TeamMemberModel, KanbanChange
from app.core.dependencies import get_assistant_agent

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/board", response_model=KanbanBoard)
async def get_kanban_board():
    """Get the current kanban board state."""
    try:
        # Get all tasks with their assignees
        tasks = list(TaskModel.select().join(TeamMemberModel))
        
        # Group tasks by status
        columns = {
            "todo": {"id": "todo", "title": "To Do", "tasks": [], "color": "neutral"},
            "in_progress": {"id": "in_progress", "title": "In Progress", "tasks": [], "color": "primary"},
            "review": {"id": "review", "title": "Review", "tasks": [], "color": "warning"},
            "done": {"id": "done", "title": "Done", "tasks": [], "color": "success"},
            "blocked": {"id": "blocked", "title": "Blocked", "tasks": [], "color": "error"}
        }
        
        for task in tasks:
            task_data = {
                "id": task.id,
                "title": task.title,
                "description": task.description,
                "status": task.status,
                "assignee_id": task.assignee.id,
                "due_date": task.due_date,
                "priority": task.priority,
                "order": task.order,
                "tags": task.tags_list,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
                "assignee": {
                    "id": task.assignee.id,
                    "name": task.assignee.name,
                    "email": task.assignee.email,
                    "role": task.assignee.role,
                    "active": task.assignee.active,
                    "response_rate": task.assignee.response_rate,
                    "last_response_at": task.assignee.last_response_at,
                    "created_at": task.assignee.created_at,
                    "updated_at": task.assignee.updated_at
                }
            }
            
            if task.status in columns:
                columns[task.status]["tasks"].append(task_data)
        
        # Sort tasks by order within each column
        for column in columns.values():
            column["tasks"].sort(key=lambda x: x["order"])
        
        return KanbanBoard(
            columns=list(columns.values()),
            last_updated=max([task.updated_at for task in tasks]) if tasks else datetime.now()
        )
        
    except Exception as e:
        logger.error(f"Error getting kanban board: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/tasks", response_model=Task)
async def create_task(task: TaskCreate):
    """Create a new task."""
    try:
        # Verify assignee exists
        assignee = TeamMemberModel.get_or_none(TeamMemberModel.id == task.assignee_id)
        if not assignee:
            raise HTTPException(status_code=404, detail="Assignee not found")
        
        # Get next order for the status column
        max_order = TaskModel.select().where(TaskModel.status == task.status).count()
        
        # Create task
        new_task = TaskModel.create(
            title=task.title,
            description=task.description,
            status=task.status,
            assignee=assignee,
            due_date=task.due_date,
            priority=task.priority,
            order=task.order if task.order is not None else max_order,
            tags=json.dumps(task.tags) if task.tags else '[]'
        )
        
        # Create change record for approval
        KanbanChange.create(
            change_type='create',
            task_id=new_task.id,
            task_data=json.dumps({
                'title': task.title,
                'assignee': assignee.email,
                'status': task.status,
                'priority': task.priority
            }),
            approved=False
        )
        
        return Task(
            id=new_task.id,
            title=new_task.title,
            description=new_task.description,
            status=new_task.status,
            assignee_id=new_task.assignee.id,
            due_date=new_task.due_date,
            priority=new_task.priority,
            order=new_task.order,
            tags=new_task.tags_list,
            created_at=new_task.created_at,
            updated_at=new_task.updated_at,
            assignee={
                "id": assignee.id,
                "name": assignee.name,
                "email": assignee.email,
                "role": assignee.role,
                "active": assignee.active,
                "response_rate": assignee.response_rate,
                "last_response_at": assignee.last_response_at,
                "created_at": assignee.created_at,
                "updated_at": assignee.updated_at
            }
        )
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: int, task_update: TaskUpdate):
    """Update an existing task."""
    try:
        # Add detailed logging for debugging
        logger.info(f"=== TASK UPDATE DEBUG ===")
        logger.info(f"Task ID: {task_id} (type: {type(task_id)})")
        logger.info(f"Raw task_update: {task_update}")
        logger.info(f"Task update dict: {task_update.dict()}")
        logger.info(f"Task update dict (exclude_unset): {task_update.dict(exclude_unset=True)}")
        
        # Get existing task
        task = TaskModel.get_or_none(TaskModel.id == task_id)
        if not task:
            logger.error(f"Task not found: {task_id}")
            raise HTTPException(status_code=404, detail="Task not found")
        
        logger.info(f"Found existing task: {task.title} (status: {task.status})")
        
        # Track changes for approval
        changes = []
        update_data = task_update.dict(exclude_unset=True)
        
        logger.info(f"Processing update data: {update_data}")
        
        if "assignee_id" in update_data:
            assignee = TeamMemberModel.get_or_none(TeamMemberModel.id == update_data["assignee_id"])
            if not assignee:
                logger.error(f"Assignee not found: {update_data['assignee_id']}")
                raise HTTPException(status_code=404, detail="Assignee not found")
            old_assignee = task.assignee.email
            task.assignee = assignee
            changes.append(f"assignee: {old_assignee} → {assignee.email}")
            del update_data["assignee_id"]
        
        if "tags" in update_data:
            task.tags = json.dumps(update_data["tags"])
            changes.append("tags updated")
            del update_data["tags"]
        
        # Track other field changes
        for field, value in update_data.items():
            if hasattr(task, field):
                old_value = getattr(task, field)
                if old_value != value:
                    logger.info(f"Updating field '{field}': {old_value} → {value}")
                    setattr(task, field, value)
                    changes.append(f"{field}: {old_value} → {value}")
            else:
                logger.warning(f"Field '{field}' not found on task model")
        
        logger.info(f"Changes to apply: {changes}")
        
        # Save the task
        task.save()
        logger.info(f"Task saved successfully with new status: {task.status}")
        
        # Create change record for approval if there were changes
        if changes:
            KanbanChange.create(
                change_type='update',
                task_id=task.id,
                task_data=json.dumps({
                    'changes': changes,
                    'title': task.title
                }),
                approved=False
            )
            logger.info("Change record created for approval")
        
        # Return updated task
        result_task = Task(
            id=task.id,
            title=task.title,
            description=task.description,
            status=task.status,
            assignee_id=task.assignee.id,
            due_date=task.due_date,
            priority=task.priority,
            order=task.order,
            tags=task.tags_list,
            created_at=task.created_at,
            updated_at=task.updated_at,
            assignee={
                "id": task.assignee.id,
                "name": task.assignee.name,
                "email": task.assignee.email,
                "role": task.assignee.role,
                "active": task.assignee.active,
                "response_rate": task.assignee.response_rate,
                "last_response_at": task.assignee.last_response_at,
                "created_at": task.assignee.created_at,
                "updated_at": task.assignee.updated_at
            }
        )
        
        logger.info(f"=== TASK UPDATE SUCCESS ===")
        return result_task
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"=== TASK UPDATE ERROR ===")
        logger.error(f"Error updating task: {e}")
        logger.error(f"Error type: {type(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/tasks/{task_id}")
async def delete_task(task_id: int):
    """Delete a task."""
    try:
        task = TaskModel.get_or_none(TaskModel.id == task_id)
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Create change record for approval
        KanbanChange.create(
            change_type='delete',
            task_id=task.id,
            task_data=json.dumps({
                'title': task.title,
                'assignee': task.assignee.email
            }),
            approved=False
        )
        
        # Soft delete - mark as deleted but don't actually remove
        # The actual deletion will happen after approval
        
        return APIResponse(
            success=True,
            message="Task deletion queued for approval"
        )
        
    except Exception as e:
        logger.error(f"Error deleting task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pending-changes")
async def get_pending_changes():
    """Get pending kanban changes that need approval."""
    try:
        agent = get_assistant_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Agent not available")
        
        changes = await agent.kanban_tools.get_pending_changes()
        
        return APIResponse(
            success=True,
            message=f"Found {len(changes)} pending changes",
            data={"changes": changes}
        )
        
    except Exception as e:
        logger.error(f"Error getting pending changes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/approve-changes")
async def approve_changes(change_ids: List[int]):
    """Approve pending kanban changes."""
    try:
        agent = get_assistant_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Agent not available")
        
        result = await agent.kanban_tools.approve_changes(change_ids)
        
        return APIResponse(
            success=True,
            message=result,
            data={"approved_changes": change_ids}
        )
        
    except Exception as e:
        logger.error(f"Error approving changes: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/summary")
async def get_board_summary():
    """Get a summary of the kanban board."""
    try:
        agent = get_assistant_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Agent not available")
        
        # Use agent's kanban tools to get summary
        summary = agent.kanban_tools.get_board_summary._run()
        
        return APIResponse(
            success=True,
            message="Board summary generated",
            data={"summary": summary}
        )
        
    except Exception as e:
        logger.error(f"Error getting board summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/agent-update")
async def agent_update_board():
    """Trigger agent to update the kanban board based on recent activities."""
    try:
        agent = get_assistant_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Agent not available")
        
        # Trigger kanban update workflow through agent
        response = await agent.process_message(
            "Update the kanban board based on recent email responses and task changes"
        )
        
        return APIResponse(
            success=True,
            message="Agent kanban update completed",
            data={"response": response}
        )
        
    except Exception as e:
        logger.error(f"Error in agent kanban update: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/tasks/search")
async def search_tasks(
    assignee_email: Optional[str] = Query(None, description="Filter by assignee email"),
    status: Optional[str] = Query(None, description="Filter by status"),
    search_term: Optional[str] = Query(None, description="Search in title and description"),
    limit: int = Query(10, description="Maximum number of results")
):
    """Search tasks by various criteria."""
    try:
        agent = get_assistant_agent()
        if not agent:
            raise HTTPException(status_code=503, detail="Agent not available")
        
        # Use agent's kanban tools to find tasks
        result = agent.kanban_tools.find_tasks._run(
            assignee_email=assignee_email,
            status=status,
            search_term=search_term
        )
        
        return APIResponse(
            success=True,
            message="Task search completed",
            data={"results": result}
        )
        
    except Exception as e:
        logger.error(f"Error searching tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))