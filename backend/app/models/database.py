"""Enhanced database models with better indexing and validation."""

from peewee import *
from datetime import datetime
import json
import asyncio
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Database instance
db = SqliteDatabase('assistant_manager.db')

class BaseModel(Model):
    """Base model with common fields and enhanced functionality."""
    created_at = DateTimeField(default=datetime.now, index=True)
    updated_at = DateTimeField(default=datetime.now, index=True)
    
    class Meta:
        database = db
    
    def save(self, *args, **kwargs):
        self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

class TeamMember(BaseModel):
    """Enhanced team member model with better indexing."""
    email = CharField(unique=True, index=True)
    name = CharField(index=True)
    role = CharField()
    active = BooleanField(default=True, index=True)
    response_rate = FloatField(default=0.0)
    last_response_at = DateTimeField(null=True, index=True)
    timezone = CharField(default='UTC')  # Added for scheduling
    
    class Meta:
        table_name = 'team_members'
        indexes = (
            (('email', 'active'), False),  # Composite index for active member lookups
        )

class Task(BaseModel):
    """Enhanced task model with time tracking and better indexing."""
    title = CharField(index=True)
    description = TextField()
    status = CharField(index=True)  # todo, in_progress, review, done, blocked
    assignee = ForeignKeyField(TeamMember, backref='tasks', index=True)
    due_date = DateTimeField(null=True, index=True)
    priority = CharField(index=True)  # low, medium, high, urgent
    order = IntegerField(default=0)
    tags = TextField(default='[]')  # JSON array of tags
    estimated_hours = FloatField(null=True)  # Added for time tracking
    actual_hours = FloatField(null=True)  # Added for time tracking
    
    class Meta:
        table_name = 'tasks'
        indexes = (
            (('status', 'assignee'), False),  # Composite index for task queries
            (('due_date', 'status'), False),  # For overdue task queries
        )
    
    @property
    def tags_list(self):
        """Get tags as a list."""
        try:
            return json.loads(self.tags)
        except:
            return []
    
    @tags_list.setter
    def tags_list(self, value):
        """Set tags from a list."""
        self.tags = json.dumps(value)
    
    @property
    def is_overdue(self):
        """Check if task is overdue."""
        return (self.due_date and 
                datetime.now() > self.due_date and 
                self.status != 'done')

class EmailThread(BaseModel):
    """Enhanced email thread tracking with better parsing support."""
    thread_id = CharField(index=True)
    team_member = ForeignKeyField(TeamMember, backref='email_threads', index=True)
    subject = CharField()
    sent_at = DateTimeField(index=True)
    response_received = BooleanField(default=False, index=True)
    response_at = DateTimeField(null=True, index=True)
    status = CharField(index=True)  # sent, opened, replied, overdue
    content = TextField()
    parsed_content = TextField(null=True)  # Enhanced JSON storage for parsed data
    follow_up_count = IntegerField(default=0)
    template_used = CharField(null=True)  # Track which template was used
    
    class Meta:
        table_name = 'email_threads'
        indexes = (
            (('team_member', 'response_received'), False),  # For pending response queries
            (('sent_at', 'status'), False),  # For time-based queries
        )
    
    @property
    def parsed_data(self):
        """Get parsed content as dictionary."""
        try:
            return json.loads(self.parsed_content) if self.parsed_content else {}
        except:
            return {}
    
    @parsed_data.setter
    def parsed_data(self, value):
        """Set parsed content from dictionary."""
        self.parsed_content = json.dumps(value) if value else None

class KanbanChange(BaseModel):
    """Enhanced kanban board change tracking."""
    change_type = CharField(index=True)  # create, update, delete, move
    task_id = IntegerField(null=True, index=True)
    task_data = TextField()  # JSON
    approved = BooleanField(default=False, index=True)
    approved_at = DateTimeField(null=True)
    approved_by = CharField(null=True)
    published = BooleanField(default=False, index=True)
    published_at = DateTimeField(null=True)
    
    class Meta:
        table_name = 'kanban_changes'
        indexes = (
            (('approved', 'created_at'), False),  # For pending approval queries
            (('published', 'approved'), False),  # For publishing workflow
        )

class AgentState(BaseModel):
    """Enhanced agent state persistence."""
    state_key = CharField(unique=True, index=True)
    state_data = TextField()  # JSON
    
    class Meta:
        table_name = 'agent_states'

class AgentActivity(BaseModel):
    """Enhanced agent activity logging with better categorization."""
    activity_type = CharField(index=True)  # email_sent, task_updated, response_received, etc.
    message = TextField()
    team_member = ForeignKeyField(TeamMember, null=True, backref='activities')
    task = ForeignKeyField(Task, null=True, backref='activities')
    status = CharField(index=True)  # success, warning, error, info
    metadata = TextField(default='{}')  # JSON
    duration_ms = IntegerField(null=True)  # Added for performance tracking
    
    class Meta:
        table_name = 'agent_activities'
        indexes = (
            (('activity_type', 'status'), False),  # For activity analysis
            (('created_at', 'status'), False),  # For time-based queries
        )

class EmailTemplate(BaseModel):
    """Enhanced email template management."""
    name = CharField(index=True)
    subject = CharField()
    content = TextField()
    template_type = CharField(index=True)  # update_request, reminder, follow_up
    variables = TextField(default='[]')  # JSON array
    active = BooleanField(default=True, index=True)
    usage_count = IntegerField(default=0)  # Added for analytics
    
    class Meta:
        table_name = 'email_templates'
        indexes = (
            (('template_type', 'active'), False),  # For template selection
        )
    
    @property
    def variables_list(self):
        """Get variables as a list."""
        try:
            return json.loads(self.variables)
        except:
            return []
    
    @variables_list.setter
    def variables_list(self, value):
        """Set variables from a list."""
        self.variables = json.dumps(value)

class WorkflowSettings(BaseModel):
    """Enhanced workflow configuration."""
    setting_key = CharField(unique=True, index=True)
    setting_value = TextField()  # JSON
    description = CharField(null=True)
    setting_type = CharField(default='string')  # string, number, boolean, json
    
    class Meta:
        table_name = 'workflow_settings'

# All models
MODELS = [
    TeamMember,
    Task,
    EmailThread,
    KanbanChange,
    AgentState,
    AgentActivity,
    EmailTemplate,
    WorkflowSettings
]

async def initialize_database():
    """Initialize database with enhanced error handling and indexing."""
    try:
        logger.info("Initializing database...")
        
        # Connect to database
        db.connect()
        
        # Create tables with safe mode
        db.create_tables(MODELS, safe=True)
        
        # Create additional indexes for performance
        await create_performance_indexes()
        
        # Insert default data
        await create_default_data()
        
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise

async def create_performance_indexes():
    """Create additional performance indexes."""
    try:
        # Additional indexes for common queries
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_tasks_overdue ON tasks(due_date, status) WHERE due_date IS NOT NULL",
            "CREATE INDEX IF NOT EXISTS idx_email_pending ON email_threads(team_member_id, response_received) WHERE response_received = 0",
            "CREATE INDEX IF NOT EXISTS idx_activities_recent ON agent_activities(created_at DESC, status)",
        ]
        
        for index_sql in indexes:
            try:
                db.execute_sql(index_sql)
            except Exception as e:
                logger.warning(f"Failed to create index: {e}")
        
        logger.info("Performance indexes created")
        
    except Exception as e:
        logger.error(f"Error creating performance indexes: {e}")

async def create_default_data():
    """Create enhanced default data for the application."""
    
    # Enhanced default email templates
    default_templates = [
        {
            'name': 'Weekly Update Request',
            'subject': 'Weekly Update Request - {{date}}',
            'content': '''Hi {{name}},

I hope you're having a great week! Could you please share a brief update on:

1. What you've been working on this week
2. Any blockers or challenges you're facing  
3. Your priorities for next week
4. Estimated completion dates for current tasks

Thanks for keeping the team informed!

Best regards,
Assistant Manager''',
            'template_type': 'update_request',
            'variables': '["name", "date"]',
            'active': True,
            'usage_count': 0
        },
        {
            'name': 'Task Deadline Reminder',
            'subject': 'Reminder: {{task_name}} due {{due_date}}',
            'content': '''Hi {{name}},

This is a friendly reminder that your task "{{task_name}}" is due on {{due_date}}.

Current status: {{status}}
Priority: {{priority}}

If you need any assistance or if there are any blockers, please let me know.

Best regards,
Assistant Manager''',
            'template_type': 'reminder',
            'variables': '["name", "task_name", "due_date", "status", "priority"]',
            'active': True,
            'usage_count': 0
        },
        {
            'name': 'Follow-up Request',
            'subject': 'Follow-up: {{subject}}',
            'content': '''Hi {{name}},

I haven't received a response to my previous email about {{subject}}.

Could you please provide an update when you have a moment?

Thanks!

Best regards,
Assistant Manager''',
            'template_type': 'follow_up',
            'variables': '["name", "subject"]',
            'active': True,
            'usage_count': 0
        },
        {
            'name': 'Project Status Update',
            'subject': 'Project Status Update - {{project_name}}',
            'content': '''Hi {{name}},

Could you please provide a status update for the {{project_name}} project?

Please include:
- Current progress percentage
- Completed milestones
- Upcoming deliverables
- Any risks or issues

Thanks for your time!

Best regards,
Assistant Manager''',
            'template_type': 'update_request',
            'variables': '["name", "project_name"]',
            'active': True,
            'usage_count': 0
        },
        {
            'name': 'Overdue Task Alert',
            'subject': 'URGENT: Overdue Task - {{task_name}}',
            'content': '''Hi {{name}},

Your task "{{task_name}}" was due on {{due_date}} and is now overdue.

Please provide an immediate update on:
- Current status
- Expected completion date
- Any blockers preventing completion

This is important for project timeline management.

Best regards,
Assistant Manager''',
            'template_type': 'reminder',
            'variables': '["name", "task_name", "due_date"]',
            'active': True,
            'usage_count': 0
        }
    ]
    
    for template_data in default_templates:
        EmailTemplate.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )
    
    # Enhanced default workflow settings
    default_settings = [
        {
            'setting_key': 'update_frequency',
            'setting_value': '"weekly"',
            'description': 'How often to send update requests',
            'setting_type': 'string'
        },
        {
            'setting_key': 'reminder_days',
            'setting_value': '2',
            'description': 'Days before deadline to send reminders',
            'setting_type': 'number'
        },
        {
            'setting_key': 'max_follow_ups',
            'setting_value': '3',
            'description': 'Maximum number of follow-up emails',
            'setting_type': 'number'
        },
        {
            'setting_key': 'auto_approve_changes',
            'setting_value': 'false',
            'description': 'Automatically approve Kanban changes',
            'setting_type': 'boolean'
        },
        {
            'setting_key': 'email_check_interval',
            'setting_value': '300',
            'description': 'Email check interval in seconds',
            'setting_type': 'number'
        },
        {
            'setting_key': 'llm_timeout',
            'setting_value': '30',
            'description': 'LLM request timeout in seconds',
            'setting_type': 'number'
        },
        {
            'setting_key': 'email_signature',
            'setting_value': '"Best regards,\\nAssistant Manager\\nAutomated Team Workflow System"',
            'description': 'Default email signature',
            'setting_type': 'string'
        },
        {
            'setting_key': 'business_hours_start',
            'setting_value': '9',
            'description': 'Business hours start (24h format)',
            'setting_type': 'number'
        },
        {
            'setting_key': 'business_hours_end',
            'setting_value': '17',
            'description': 'Business hours end (24h format)',
            'setting_type': 'number'
        }
    ]
    
    for setting_data in default_settings:
        WorkflowSettings.get_or_create(
            setting_key=setting_data['setting_key'],
            defaults=setting_data
        )
    
    logger.info("Enhanced default data created successfully")

def get_database():
    """Get database instance."""
    return db

# Database utility functions
async def cleanup_old_data(days_to_keep: int = 90):
    """Cleanup old data to maintain performance."""
    try:
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # Cleanup old agent activities
        deleted_activities = AgentActivity.delete().where(
            AgentActivity.created_at < cutoff_date
        ).execute()
        
        # Cleanup old email threads (keep only if no response received)
        deleted_threads = EmailThread.delete().where(
            EmailThread.created_at < cutoff_date,
            EmailThread.response_received == True
        ).execute()
        
        logger.info(f"Cleaned up {deleted_activities} old activities and {deleted_threads} old email threads")
        
    except Exception as e:
        logger.error(f"Error during data cleanup: {e}")

async def get_database_stats():
    """Get database statistics for monitoring."""
    try:
        stats = {
            'team_members': TeamMember.select().count(),
            'active_members': TeamMember.select().where(TeamMember.active == True).count(),
            'total_tasks': Task.select().count(),
            'pending_tasks': Task.select().where(Task.status != 'done').count(),
            'email_threads': EmailThread.select().count(),
            'pending_responses': EmailThread.select().where(EmailThread.response_received == False).count(),
            'pending_approvals': KanbanChange.select().where(KanbanChange.approved == False).count(),
            'email_templates': EmailTemplate.select().where(EmailTemplate.active == True).count(),
        }
        
        return stats
        
    except Exception as e:
        logger.error(f"Error getting database stats: {e}")
        return {}