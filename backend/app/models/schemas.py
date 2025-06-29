"""Enhanced Pydantic schemas for API request/response models."""

from pydantic import BaseModel, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import json

# Enums
class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    DONE = "done"
    BLOCKED = "blocked"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"

class EmailStatus(str, Enum):
    SENT = "sent"
    OPENED = "opened"
    REPLIED = "replied"
    OVERDUE = "overdue"

class ActivityStatus(str, Enum):
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    INFO = "info"

class TemplateType(str, Enum):
    UPDATE_REQUEST = "update_request"
    REMINDER = "reminder"
    FOLLOW_UP = "follow_up"

# Base schemas
class BaseSchema(BaseModel):
    created_at: datetime
    updated_at: datetime

# Team Member schemas
class TeamMemberBase(BaseModel):
    email: EmailStr
    name: str
    role: str
    active: bool = True

class TeamMemberCreate(TeamMemberBase):
    pass

class TeamMemberUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    active: Optional[bool] = None

class TeamMember(TeamMemberBase, BaseSchema):
    id: int
    response_rate: float
    last_response_at: Optional[datetime] = None

# Task schemas
class TaskBase(BaseModel):
    title: str
    description: str
    status: TaskStatus
    assignee_id: int
    due_date: Optional[datetime] = None
    priority: Priority
    order: int = 0
    tags: List[str] = []

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    assignee_id: Optional[int] = None
    due_date: Optional[datetime] = None
    priority: Optional[Priority] = None
    order: Optional[int] = None
    tags: Optional[List[str]] = None

class Task(TaskBase, BaseSchema):
    id: int
    assignee: TeamMember

# Email schemas
class EmailThreadBase(BaseModel):
    thread_id: str
    team_member_id: int
    subject: str
    sent_at: datetime
    status: EmailStatus
    content: str
    follow_up_count: int = 0
    template_used: Optional[str] = None

class EmailThreadCreate(EmailThreadBase):
    pass

class EmailThread(EmailThreadBase, BaseSchema):
    id: int
    response_received: bool
    response_at: Optional[datetime] = None
    parsed_content: Optional[Dict[str, Any]] = None
    team_member: TeamMember

# Email Template schemas
class EmailTemplateBase(BaseModel):
    name: str
    subject: str
    content: str
    template_type: TemplateType
    variables: List[str] = []
    active: bool = True

class EmailTemplateCreate(EmailTemplateBase):
    pass

class EmailTemplateUpdate(BaseModel):
    name: Optional[str] = None
    subject: Optional[str] = None
    content: Optional[str] = None
    template_type: Optional[TemplateType] = None
    variables: Optional[List[str]] = None
    active: Optional[bool] = None

class EmailTemplate(EmailTemplateBase, BaseSchema):
    id: int
    usage_count: int

# Agent Activity schemas
class AgentActivityBase(BaseModel):
    activity_type: str
    message: str
    status: ActivityStatus
    metadata: Dict[str, Any] = {}

class AgentActivityCreate(AgentActivityBase):
    team_member_id: Optional[int] = None
    task_id: Optional[int] = None

class AgentActivity(AgentActivityBase, BaseSchema):
    id: int
    team_member: Optional[TeamMember] = None
    task: Optional[Task] = None

# Kanban schemas
class KanbanColumn(BaseModel):
    id: TaskStatus
    title: str
    tasks: List[Task]
    color: str

class KanbanBoard(BaseModel):
    columns: List[KanbanColumn]
    last_updated: datetime

class KanbanChangeBase(BaseModel):
    change_type: str
    task_id: Optional[int] = None
    task_data: Dict[str, Any]

class KanbanChangeCreate(KanbanChangeBase):
    pass

class KanbanChange(KanbanChangeBase, BaseSchema):
    id: int
    approved: bool
    approved_at: Optional[datetime] = None
    approved_by: Optional[str] = None
    published: bool
    published_at: Optional[datetime] = None

# Agent schemas
class AgentStatus(BaseModel):
    is_active: bool
    current_task: str
    next_scheduled_action: Optional[datetime] = None
    tasks_completed: int
    emails_sent: int
    responses_received: int
    last_activity: datetime

class AgentQuery(BaseModel):
    query: str
    context: Optional[Dict[str, Any]] = None

class AgentResponse(BaseModel):
    response: str
    confidence: float
    sources: List[str] = []
    suggested_actions: List[str] = []

# Workflow Settings schemas
class WorkflowSettingsBase(BaseModel):
    setting_key: str
    setting_value: Any
    description: Optional[str] = None

class WorkflowSettings(WorkflowSettingsBase, BaseSchema):
    id: int

# API Response schemas
class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

class PaginatedResponse(BaseModel):
    items: List[Any]
    total: int
    page: int
    size: int
    pages: int

# Email Statistics schema
class EmailStatistics(BaseModel):
    total_threads: int
    responded_threads: int
    pending_threads: int
    response_rate: float
    recent_activity: Dict[str, int]
    template_usage: Dict[str, int]