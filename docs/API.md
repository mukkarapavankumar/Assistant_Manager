# Assistant Manager API Documentation

## Overview

The Assistant Manager API provides endpoints for managing team workflows, email automation, kanban boards, and agent interactions. All endpoints return JSON responses and follow RESTful conventions.

## Base URL

```
http://localhost:8000/api
```

## Authentication

Currently, the API does not require authentication as it's designed for local desktop use. Future versions may include token-based authentication.

## Response Format

All API responses follow this structure:

```json
{
  "success": true,
  "message": "Operation completed successfully",
  "data": {
    // Response data
  }
}
```

Error responses:

```json
{
  "success": false,
  "message": "Error description",
  "detail": "Detailed error information"
}
```

## Endpoints

### Agent Management

#### Query Agent
Send a query to the assistant agent for processing.

```http
POST /api/agents/query
```

**Request Body:**
```json
{
  "query": "What is the current team status?",
  "context": {
    "additional": "context"
  }
}
```

**Response:**
```json
{
  "response": "Team status summary with current metrics...",
  "confidence": 0.95,
  "sources": ["agent_knowledge", "database"],
  "suggested_actions": [
    "Check overdue tasks",
    "Send follow-up emails",
    "Update kanban board"
  ]
}
```

#### Get Agent Status
Retrieve current agent status and health information.

```http
GET /api/agents/status
```

**Response:**
```json
{
  "is_active": true,
  "current_task": "Monitoring email responses",
  "next_scheduled_action": "2024-01-27T09:00:00Z",
  "tasks_completed": 24,
  "emails_sent": 156,
  "responses_received": 142,
  "last_activity": "2024-01-20T10:30:00Z"
}
```

#### Trigger Workflow
Manually trigger a specific workflow.

```http
POST /api/agents/trigger-workflow?workflow_type={type}
```

**Parameters:**
- `workflow_type`: One of `weekly_update`, `deadline_check`, `kanban_sync`, `status_summary`, `check_responses`, `github_publish`

**Response:**
```json
{
  "success": true,
  "message": "Workflow 'weekly_update' completed successfully",
  "data": {
    "response": "Sent update requests to 4 team members",
    "workflow_type": "weekly_update"
  }
}
```

#### Approve Changes
Approve pending kanban board changes.

```http
POST /api/agents/approve-changes
```

**Request Body:**
```json
[1, 2, 3]  // Array of change IDs
```

**Response:**
```json
{
  "success": true,
  "message": "Approved 3 kanban changes",
  "data": {
    "approved_changes": [1, 2, 3],
    "count": 3
  }
}
```

### Kanban Board Management

#### Get Kanban Board
Retrieve the current kanban board state.

```http
GET /api/kanban/board
```

**Response:**
```json
{
  "columns": [
    {
      "id": "todo",
      "title": "To Do",
      "tasks": [
        {
          "id": 1,
          "title": "User Authentication API",
          "description": "Implement JWT-based authentication",
          "status": "todo",
          "assignee_id": 1,
          "due_date": "2024-01-25T17:00:00Z",
          "priority": "high",
          "order": 0,
          "tags": ["backend", "security"],
          "created_at": "2024-01-15T09:00:00Z",
          "updated_at": "2024-01-20T10:30:00Z",
          "assignee": {
            "id": 1,
            "name": "Sarah Chen",
            "email": "sarah.chen@company.com",
            "role": "Senior Developer"
          }
        }
      ],
      "color": "neutral"
    }
  ],
  "last_updated": "2024-01-20T10:30:00Z"
}
```

#### Create Task
Create a new task on the kanban board.

```http
POST /api/kanban/tasks
```

**Request Body:**
```json
{
  "title": "New Feature Implementation",
  "description": "Detailed task description",
  "status": "todo",
  "assignee_id": 1,
  "due_date": "2024-02-01T17:00:00Z",
  "priority": "medium",
  "tags": ["feature", "frontend"]
}
```

**Response:**
```json
{
  "id": 5,
  "title": "New Feature Implementation",
  "description": "Detailed task description",
  "status": "todo",
  "assignee_id": 1,
  "due_date": "2024-02-01T17:00:00Z",
  "priority": "medium",
  "order": 0,
  "tags": ["feature", "frontend"],
  "created_at": "2024-01-20T15:30:00Z",
  "updated_at": "2024-01-20T15:30:00Z",
  "assignee": {
    "id": 1,
    "name": "Sarah Chen",
    "email": "sarah.chen@company.com",
    "role": "Senior Developer"
  }
}
```

#### Update Task
Update an existing task.

```http
PUT /api/kanban/tasks/{task_id}
```

**Request Body:**
```json
{
  "title": "Updated Task Title",
  "status": "in_progress",
  "priority": "high"
}
```

#### Delete Task
Delete a task (queues for approval).

```http
DELETE /api/kanban/tasks/{task_id}
```

#### Get Pending Changes
Retrieve pending kanban changes that need approval.

```http
GET /api/kanban/pending-changes
```

**Response:**
```json
{
  "success": true,
  "message": "Found 2 pending changes",
  "data": {
    "changes": [
      {
        "id": 1,
        "change_type": "create",
        "task_id": 5,
        "task_data": {
          "title": "New Task",
          "assignee": "sarah.chen@company.com"
        },
        "created_at": "2024-01-20T15:30:00Z"
      }
    ]
  }
}
```

### Email Management

#### Get Email Threads
Retrieve email communication threads.

```http
GET /api/emails/threads?team_member_id={id}&status={status}&limit={limit}
```

**Parameters:**
- `team_member_id` (optional): Filter by team member
- `status` (optional): Filter by email status
- `limit` (optional): Maximum results (default: 50)

**Response:**
```json
[
  {
    "id": 1,
    "team_member_id": 1,
    "subject": "Weekly Update Request - Jan 20, 2024",
    "sent_at": "2024-01-20T09:00:00Z",
    "response_received": true,
    "response_at": "2024-01-20T10:30:00Z",
    "status": "replied",
    "content": "Please provide your weekly update...",
    "follow_up_count": 0,
    "template_used": "Weekly Update Request",
    "team_member": {
      "id": 1,
      "name": "Sarah Chen",
      "email": "sarah.chen@company.com",
      "role": "Senior Developer"
    }
  }
]
```

#### Send Update Requests
Send update request emails to all active team members.

```http
POST /api/emails/send-updates?template_id={id}
```

**Parameters:**
- `template_id` (optional): Specific template to use

**Response:**
```json
{
  "success": true,
  "message": "Update requests sent to 4 team members",
  "data": {
    "response": "Sent weekly update requests...",
    "recipient_count": 4,
    "template": "Weekly Update Request"
  }
}
```

#### Search Outlook Contacts
Search Outlook contacts and address book.

```http
GET /api/emails/search-contacts?search_term={term}&limit={limit}
```

**Response:**
```json
{
  "success": true,
  "message": "Found 3 contacts",
  "data": {
    "contacts": [
      {
        "name": "John Doe",
        "email": "john.doe@company.com",
        "company": "Tech Corp",
        "department": "Engineering",
        "job_title": "Senior Developer",
        "source": "contacts"
      }
    ]
  }
}
```

#### Team Member Management

##### Get Team Members
```http
GET /api/emails/team-members?active_only={boolean}
```

##### Add Team Member
```http
POST /api/emails/team-members
```

**Request Body:**
```json
{
  "name": "John Doe",
  "email": "john.doe@company.com",
  "role": "Senior Developer",
  "active": true
}
```

##### Update Team Member
```http
PUT /api/emails/team-members/{member_id}
```

##### Remove Team Member
```http
DELETE /api/emails/team-members/{member_id}?permanent={boolean}
```

#### Email Templates

##### Get Templates
```http
GET /api/emails/templates?template_type={type}&active_only={boolean}
```

##### Create Template
```http
POST /api/emails/templates
```

**Request Body:**
```json
{
  "name": "Custom Update Request",
  "subject": "Project Update - {{project_name}}",
  "content": "Hi {{name}}, please provide an update on {{project_name}}...",
  "template_type": "update_request",
  "variables": ["name", "project_name"],
  "active": true
}
```

##### Update Template
```http
PUT /api/emails/templates/{template_id}
```

##### Delete Template
```http
DELETE /api/emails/templates/{template_id}
```

##### Duplicate Template
```http
POST /api/emails/templates/{template_id}/duplicate
```

#### Email Statistics
Get email communication statistics.

```http
GET /api/emails/statistics
```

**Response:**
```json
{
  "success": true,
  "message": "Email statistics retrieved",
  "data": {
    "total_threads": 156,
    "responded_threads": 142,
    "pending_threads": 14,
    "response_rate": 91.0,
    "recent_activity": {
      "emails_sent_week": 20,
      "responses_received_week": 18
    },
    "template_usage": {
      "Weekly Update Request": 45,
      "Task Reminder": 23,
      "Follow-up": 12
    }
  }
}
```

### Health and Monitoring

#### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "agent_initialized": true,
  "scheduler_running": true,
  "database": "connected"
}
```

#### Agent Health
```http
GET /api/agents/health
```

**Response:**
```json
{
  "status": "healthy",
  "agent_available": true,
  "is_active": true,
  "workflow_step": "idle",
  "error_count": 0,
  "last_error": null,
  "llm_status": "healthy",
  "last_activity": "2024-01-20T10:30:00Z"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Bad Request - Invalid parameters |
| 404 | Not Found - Resource doesn't exist |
| 422 | Validation Error - Invalid request body |
| 500 | Internal Server Error |
| 503 | Service Unavailable - Agent not available |

## Rate Limiting

Currently, no rate limiting is implemented as the API is designed for local use. Future versions may include rate limiting for security.

## WebSocket Events

The application supports real-time updates via WebSocket connection:

```javascript
const ws = new WebSocket('ws://localhost:8000/ws/agent-updates');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  // Handle real-time updates
};
```

### Event Types
- `agent_status_update`: Agent status changes
- `kanban_update`: Board changes
- `email_received`: New email responses
- `task_completed`: Task status updates

## SDK Usage Examples

### JavaScript/TypeScript

```typescript
import { agentApi, kanbanApi, emailApi } from './services/api';

// Query the agent
const response = await agentApi.query('What tasks are overdue?');

// Create a task
const task = await kanbanApi.createTask({
  title: 'New Feature',
  description: 'Implement new feature',
  status: 'todo',
  assignee_id: 1,
  priority: 'high'
});

// Send emails
await emailApi.sendUpdates();
```

### Python

```python
import requests

base_url = "http://localhost:8000/api"

# Query agent
response = requests.post(f"{base_url}/agents/query", json={
    "query": "Show me team status"
})

# Get kanban board
board = requests.get(f"{base_url}/kanban/board")
```

## Changelog

### v1.0.0
- Initial API release
- Agent management endpoints
- Kanban board CRUD operations
- Email automation and templates
- Team member management
- Real-time WebSocket updates