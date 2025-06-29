"""Streamlined Kanban board management tools optimized for LLM usage."""

from langchain.tools import BaseTool
from typing import List, Dict, Any, Optional
import logging
import json
from datetime import datetime

from app.models.database import Task, TeamMember, KanbanChange
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)

class KanbanTools:
    """Collection of simple, LLM-friendly kanban tools."""
    
    def __init__(self):
        self.llm_service = None
    
    async def initialize(self):
        """Initialize kanban tools."""
        try:
            self.llm_service = LLMService()
            await self.llm_service.initialize()
            logger.info("Kanban tools initialized")
        except Exception as e:
            logger.error(f"Failed to initialize kanban tools: {e}")
            raise
    
    @property
    def get_board_summary(self):
        """Tool for getting a simple board summary."""
        
        class GetBoardSummaryTool(BaseTool):
            name = "get_board_summary"
            description = "Get a simple summary of the current kanban board status"
            
            def _run(self) -> str:
                try:
                    # Get task counts by status
                    todo_count = Task.select().where(Task.status == 'todo').count()
                    in_progress_count = Task.select().where(Task.status == 'in_progress').count()
                    review_count = Task.select().where(Task.status == 'review').count()
                    done_count = Task.select().where(Task.status == 'done').count()
                    blocked_count = Task.select().where(Task.status == 'blocked').count()
                    
                    total_tasks = todo_count + in_progress_count + review_count + done_count + blocked_count
                    
                    # Get overdue tasks
                    overdue_tasks = list(Task.select().where(
                        Task.due_date < datetime.now(),
                        Task.status != 'done'
                    ))
                    
                    summary = f"""Kanban Board Summary:
- Total Tasks: {total_tasks}
- To Do: {todo_count}
- In Progress: {in_progress_count}
- Review: {review_count}
- Done: {done_count}
- Blocked: {blocked_count}
- Overdue: {len(overdue_tasks)}"""
                    
                    if overdue_tasks:
                        summary += "\n\nOverdue Tasks:"
                        for task in overdue_tasks[:3]:  # Show first 3
                            summary += f"\n- {task.title} (due {task.due_date.strftime('%Y-%m-%d')})"
                        if len(overdue_tasks) > 3:
                            summary += f"\n- ... and {len(overdue_tasks) - 3} more"
                    
                    logger.info("Generated board summary")
                    return summary
                    
                except Exception as e:
                    error_msg = f"Error getting board summary: {str(e)}"
                    logger.error(error_msg)
                    return error_msg
            
            async def _arun(self) -> str:
                return self._run()
        
        return GetBoardSummaryTool()
    
    @property
    def create_task(self):
        """Tool for creating a new task."""
        
        class CreateTaskTool(BaseTool):
            name = "create_task"
            description = "Create a new task on the kanban board. Requires: title, assignee_email, status (optional), description (optional), priority (optional), due_date (optional)"
            
            def _run(self, title: str, assignee_email: str, status: str = "todo", 
                    description: str = "", priority: str = "medium", due_date: str = None) -> str:
                try:
                    # Find assignee
                    assignee = TeamMember.get_or_none(TeamMember.email == assignee_email)
                    if not assignee:
                        return f"Error: Team member not found with email: {assignee_email}"
                    
                    # Validate status
                    valid_statuses = ['todo', 'in_progress', 'review', 'done', 'blocked']
                    if status not in valid_statuses:
                        status = 'todo'
                    
                    # Validate priority
                    valid_priorities = ['low', 'medium', 'high', 'urgent']
                    if priority not in valid_priorities:
                        priority = 'medium'
                    
                    # Parse due date
                    parsed_due_date = None
                    if due_date:
                        try:
                            parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                        except:
                            logger.warning(f"Invalid due date format: {due_date}")
                    
                    # Get next order for the status column
                    max_order = Task.select().where(Task.status == status).count()
                    
                    # Create task
                    task = Task.create(
                        title=title,
                        description=description,
                        status=status,
                        assignee=assignee,
                        due_date=parsed_due_date,
                        priority=priority,
                        order=max_order
                    )
                    
                    # Log the change
                    KanbanChange.create(
                        change_type='create',
                        task_id=task.id,
                        task_data=json.dumps({
                            'title': title,
                            'assignee': assignee_email,
                            'status': status,
                            'priority': priority
                        }),
                        approved=False
                    )
                    
                    result = f"Created task '{title}' assigned to {assignee.name} ({assignee_email}) with status '{status}'"
                    logger.info(result)
                    return result
                    
                except Exception as e:
                    error_msg = f"Error creating task: {str(e)}"
                    logger.error(error_msg)
                    return error_msg
            
            async def _arun(self, title: str, assignee_email: str, status: str = "todo", 
                          description: str = "", priority: str = "medium", due_date: str = None) -> str:
                return self._run(title, assignee_email, status, description, priority, due_date)
        
        return CreateTaskTool()
    
    @property
    def update_task_status(self):
        """Tool for updating task status."""
        
        class UpdateTaskStatusTool(BaseTool):
            name = "update_task_status"
            description = "Update a task's status. Requires: task_id, new_status (todo/in_progress/review/done/blocked)"
            
            def _run(self, task_id: int, new_status: str) -> str:
                try:
                    # Validate status
                    valid_statuses = ['todo', 'in_progress', 'review', 'done', 'blocked']
                    if new_status not in valid_statuses:
                        return f"Error: Invalid status '{new_status}'. Must be one of: {', '.join(valid_statuses)}"
                    
                    # Find task
                    task = Task.get_or_none(Task.id == task_id)
                    if not task:
                        return f"Error: Task not found with ID: {task_id}"
                    
                    old_status = task.status
                    
                    # Update task
                    task.status = new_status
                    task.save()
                    
                    # Log the change
                    KanbanChange.create(
                        change_type='update',
                        task_id=task.id,
                        task_data=json.dumps({
                            'field': 'status',
                            'old_value': old_status,
                            'new_value': new_status,
                            'title': task.title
                        }),
                        approved=False
                    )
                    
                    result = f"Updated task '{task.title}' status from '{old_status}' to '{new_status}'"
                    logger.info(result)
                    return result
                    
                except Exception as e:
                    error_msg = f"Error updating task status: {str(e)}"
                    logger.error(error_msg)
                    return error_msg
            
            async def _arun(self, task_id: int, new_status: str) -> str:
                return self._run(task_id, new_status)
        
        return UpdateTaskStatusTool()
    
    @property
    def find_tasks(self):
        """Tool for finding tasks by various criteria."""
        
        class FindTasksTool(BaseTool):
            name = "find_tasks"
            description = "Find tasks by assignee email, status, or title keywords. Use assignee_email, status, or search_term parameters"
            
            def _run(self, assignee_email: str = None, status: str = None, search_term: str = None) -> str:
                try:
                    query = Task.select().join(TeamMember)
                    
                    # Filter by assignee
                    if assignee_email:
                        query = query.where(TeamMember.email == assignee_email)
                    
                    # Filter by status
                    if status:
                        query = query.where(Task.status == status)
                    
                    # Filter by search term
                    if search_term:
                        query = query.where(
                            (Task.title.contains(search_term)) |
                            (Task.description.contains(search_term))
                        )
                    
                    tasks = list(query.order_by(Task.updated_at.desc()).limit(10))
                    
                    if not tasks:
                        return "No tasks found matching the criteria"
                    
                    result = f"Found {len(tasks)} tasks:\n"
                    for task in tasks:
                        due_info = f" (due {task.due_date.strftime('%Y-%m-%d')})" if task.due_date else ""
                        result += f"- ID:{task.id} '{task.title}' - {task.status} - {task.assignee.name}{due_info}\n"
                    
                    logger.info(f"Found {len(tasks)} tasks")
                    return result.strip()
                    
                except Exception as e:
                    error_msg = f"Error finding tasks: {str(e)}"
                    logger.error(error_msg)
                    return error_msg
            
            async def _arun(self, assignee_email: str = None, status: str = None, search_term: str = None) -> str:
                return self._run(assignee_email, status, search_term)
        
        return FindTasksTool()
    
    @property
    def get_task_details(self):
        """Tool for getting detailed information about a specific task."""
        
        class GetTaskDetailsTool(BaseTool):
            name = "get_task_details"
            description = "Get detailed information about a specific task by ID"
            
            def _run(self, task_id: int) -> str:
                try:
                    task = Task.get_or_none(Task.id == task_id)
                    if not task:
                        return f"Error: Task not found with ID: {task_id}"
                    
                    due_info = f"Due: {task.due_date.strftime('%Y-%m-%d %H:%M')}" if task.due_date else "No due date"
                    
                    result = f"""Task Details:
ID: {task.id}
Title: {task.title}
Description: {task.description or 'No description'}
Status: {task.status}
Priority: {task.priority}
Assignee: {task.assignee.name} ({task.assignee.email})
{due_info}
Created: {task.created_at.strftime('%Y-%m-%d %H:%M')}
Updated: {task.updated_at.strftime('%Y-%m-%d %H:%M')}"""
                    
                    if task.tags_list:
                        result += f"\nTags: {', '.join(task.tags_list)}"
                    
                    logger.info(f"Retrieved details for task {task_id}")
                    return result
                    
                except Exception as e:
                    error_msg = f"Error getting task details: {str(e)}"
                    logger.error(error_msg)
                    return error_msg
            
            async def _arun(self, task_id: int) -> str:
                return self._run(task_id)
        
        return GetTaskDetailsTool()
    
    @property
    def update_task_info(self):
        """Tool for updating task information."""
        
        class UpdateTaskInfoTool(BaseTool):
            name = "update_task_info"
            description = "Update task information. Requires task_id and at least one of: title, description, priority, due_date"
            
            def _run(self, task_id: int, title: str = None, description: str = None, 
                    priority: str = None, due_date: str = None) -> str:
                try:
                    task = Task.get_or_none(Task.id == task_id)
                    if not task:
                        return f"Error: Task not found with ID: {task_id}"
                    
                    changes = []
                    
                    # Update title
                    if title:
                        old_title = task.title
                        task.title = title
                        changes.append(f"title: '{old_title}' → '{title}'")
                    
                    # Update description
                    if description:
                        task.description = description
                        changes.append(f"description updated")
                    
                    # Update priority
                    if priority:
                        valid_priorities = ['low', 'medium', 'high', 'urgent']
                        if priority in valid_priorities:
                            old_priority = task.priority
                            task.priority = priority
                            changes.append(f"priority: '{old_priority}' → '{priority}'")
                        else:
                            return f"Error: Invalid priority '{priority}'. Must be one of: {', '.join(valid_priorities)}"
                    
                    # Update due date
                    if due_date:
                        try:
                            parsed_due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                            old_due = task.due_date.strftime('%Y-%m-%d') if task.due_date else 'None'
                            task.due_date = parsed_due_date
                            changes.append(f"due date: {old_due} → {parsed_due_date.strftime('%Y-%m-%d')}")
                        except:
                            return f"Error: Invalid due date format: {due_date}"
                    
                    if not changes:
                        return "Error: No valid updates provided"
                    
                    task.save()
                    
                    # Log the change
                    KanbanChange.create(
                        change_type='update',
                        task_id=task.id,
                        task_data=json.dumps({
                            'changes': changes,
                            'title': task.title
                        }),
                        approved=False
                    )
                    
                    result = f"Updated task '{task.title}': {', '.join(changes)}"
                    logger.info(result)
                    return result
                    
                except Exception as e:
                    error_msg = f"Error updating task: {str(e)}"
                    logger.error(error_msg)
                    return error_msg
            
            async def _arun(self, task_id: int, title: str = None, description: str = None, 
                          priority: str = None, due_date: str = None) -> str:
                return self._run(task_id, title, description, priority, due_date)
        
        return UpdateTaskInfoTool()
    
    @property
    def get_pending_approvals(self):
        """Tool for getting pending kanban changes that need approval."""
        
        class GetPendingApprovalsTool(BaseTool):
            name = "get_pending_approvals"
            description = "Get list of pending kanban changes that need manager approval"
            
            def _run(self) -> str:
                try:
                    pending_changes = list(
                        KanbanChange.select()
                        .where(KanbanChange.approved == False)
                        .order_by(KanbanChange.created_at.desc())
                        .limit(10)
                    )
                    
                    if not pending_changes:
                        return "No pending changes requiring approval"
                    
                    result = f"Pending Approvals ({len(pending_changes)}):\n"
                    for change in pending_changes:
                        change_data = json.loads(change.task_data)
                        
                        if change.change_type == 'create':
                            result += f"- ID:{change.id} CREATE: '{change_data.get('title')}' for {change_data.get('assignee')}\n"
                        elif change.change_type == 'update':
                            if 'changes' in change_data:
                                result += f"- ID:{change.id} UPDATE: '{change_data.get('title')}' - {', '.join(change_data['changes'])}\n"
                            else:
                                result += f"- ID:{change.id} UPDATE: '{change_data.get('title')}' - {change_data.get('field')} changed\n"
                        else:
                            result += f"- ID:{change.id} {change.change_type.upper()}: {change_data}\n"
                    
                    logger.info(f"Retrieved {len(pending_changes)} pending approvals")
                    return result.strip()
                    
                except Exception as e:
                    error_msg = f"Error getting pending approvals: {str(e)}"
                    logger.error(error_msg)
                    return error_msg
            
            async def _arun(self) -> str:
                return self._run()
        
        return GetPendingApprovalsTool()
    
    async def get_pending_changes(self) -> List[Dict]:
        """Get pending kanban changes that need approval."""
        try:
            changes = list(
                KanbanChange.select()
                .where(KanbanChange.approved == False)
                .order_by(KanbanChange.created_at.desc())
            )
            
            return [
                {
                    'id': change.id,
                    'change_type': change.change_type,
                    'task_id': change.task_id,
                    'task_data': json.loads(change.task_data),
                    'created_at': change.created_at
                }
                for change in changes
            ]
        except Exception as e:
            logger.error(f"Error getting pending changes: {e}")
            return []
    
    async def approve_changes(self, change_ids: List[int]) -> str:
        """Approve specific kanban changes."""
        try:
            approved_count = 0
            
            for change_id in change_ids:
                change = KanbanChange.get_or_none(KanbanChange.id == change_id)
                if change and not change.approved:
                    change.approved = True
                    change.approved_at = datetime.now()
                    change.save()
                    approved_count += 1
            
            result = f"Approved {approved_count} kanban changes"
            logger.info(result)
            return result
            
        except Exception as e:
            error_msg = f"Error approving changes: {str(e)}"
            logger.error(error_msg)
            return error_msg