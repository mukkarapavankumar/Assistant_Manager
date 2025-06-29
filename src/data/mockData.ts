import { TeamMember, Task, EmailThread, AgentActivity, AgentStatus, EmailTemplate, WorkflowSettings } from '../types';

export const mockTeamMembers: TeamMember[] = [
  {
    id: '1',
    name: 'Sarah Chen',
    email: 'sarah.chen@company.com',
    role: 'Senior Developer',
    active: true,
    lastResponseAt: new Date('2024-01-20T10:30:00'),
    responseRate: 95,
  },
  {
    id: '2',
    name: 'Mike Rodriguez',
    email: 'mike.rodriguez@company.com',
    role: 'Product Designer',
    active: true,
    lastResponseAt: new Date('2024-01-19T14:20:00'),
    responseRate: 88,
  },
  {
    id: '3',
    name: 'Emily Watson',
    email: 'emily.watson@company.com',
    role: 'QA Engineer',
    active: true,
    lastResponseAt: new Date('2024-01-18T09:15:00'),
    responseRate: 92,
  },
  {
    id: '4',
    name: 'David Kim',
    email: 'david.kim@company.com',
    role: 'Backend Developer',
    active: true,
    lastResponseAt: new Date('2024-01-20T16:45:00'),
    responseRate: 85,
  },
  {
    id: '5',
    name: 'Lisa Thompson',
    email: 'lisa.thompson@company.com',
    role: 'DevOps Engineer',
    active: false,
    responseRate: 0,
  },
];

export const mockTasks: Task[] = [
  {
    id: '1',
    title: 'User Authentication API',
    description: 'Implement JWT-based authentication system with refresh tokens',
    status: 'in_progress',
    assignee: mockTeamMembers[0],
    dueDate: new Date('2024-01-25T17:00:00'),
    priority: 'high',
    createdAt: new Date('2024-01-15T09:00:00'),
    updatedAt: new Date('2024-01-20T10:30:00'),
    tags: ['backend', 'security'],
    order: 0,
  },
  {
    id: '2',
    title: 'Dashboard UI Redesign',
    description: 'Create new dashboard layout with improved UX and accessibility',
    status: 'review',
    assignee: mockTeamMembers[1],
    dueDate: new Date('2024-01-22T17:00:00'),
    priority: 'medium',
    createdAt: new Date('2024-01-10T14:00:00'),
    updatedAt: new Date('2024-01-19T14:20:00'),
    tags: ['frontend', 'design'],
    order: 0,
  },
  {
    id: '3',
    title: 'API Integration Tests',
    description: 'Write comprehensive integration tests for all API endpoints',
    status: 'todo',
    assignee: mockTeamMembers[2],
    dueDate: new Date('2024-01-28T17:00:00'),
    priority: 'medium',
    createdAt: new Date('2024-01-16T11:00:00'),
    updatedAt: new Date('2024-01-18T09:15:00'),
    tags: ['testing', 'backend'],
    order: 0,
  },
  {
    id: '4',
    title: 'Database Migration Scripts',
    description: 'Create migration scripts for the new user management schema',
    status: 'done',
    assignee: mockTeamMembers[3],
    priority: 'low',
    createdAt: new Date('2024-01-12T08:00:00'),
    updatedAt: new Date('2024-01-20T16:45:00'),
    tags: ['database', 'migration'],
    order: 0,
  },
  {
    id: '5',
    title: 'CI/CD Pipeline Setup',
    description: 'Configure automated deployment pipeline with Docker and GitHub Actions',
    status: 'blocked',
    assignee: mockTeamMembers[4],
    dueDate: new Date('2024-01-30T17:00:00'),
    priority: 'high',
    createdAt: new Date('2024-01-14T13:00:00'),
    updatedAt: new Date('2024-01-17T10:00:00'),
    tags: ['devops', 'automation'],
    order: 0,
  },
];

export const mockEmailThreads: EmailThread[] = [
  {
    id: '1',
    teamMember: mockTeamMembers[0],
    subject: 'Weekly Update Request - Jan 20, 2024',
    sentAt: new Date('2024-01-20T09:00:00'),
    responseReceived: true,
    responseAt: new Date('2024-01-20T10:30:00'),
    status: 'replied',
    content: 'Please provide your weekly update on current tasks and any blockers.',
    followUpCount: 0,
  },
  {
    id: '2',
    teamMember: mockTeamMembers[1],
    subject: 'Weekly Update Request - Jan 20, 2024',
    sentAt: new Date('2024-01-20T09:00:00'),
    responseReceived: false,
    status: 'sent',
    content: 'Please provide your weekly update on current tasks and any blockers.',
    followUpCount: 1,
  },
  {
    id: '3',
    teamMember: mockTeamMembers[2],
    subject: 'Reminder: Task deadline approaching',
    sentAt: new Date('2024-01-19T15:00:00'),
    responseReceived: true,
    responseAt: new Date('2024-01-19T16:30:00'),
    status: 'replied',
    content: 'Your task "API Integration Tests" is due in 3 days. Please provide a status update.',
    followUpCount: 0,
  },
];

export const mockAgentActivities: AgentActivity[] = [
  {
    id: '1',
    type: 'response_received',
    message: 'Received update from Sarah Chen on User Authentication API',
    timestamp: new Date('2024-01-20T10:30:00'),
    teamMember: mockTeamMembers[0],
    task: mockTasks[0],
    status: 'success',
  },
  {
    id: '2',
    type: 'email_sent',
    message: 'Sent weekly update request to 4 team members',
    timestamp: new Date('2024-01-20T09:00:00'),
    status: 'info',
  },
  {
    id: '3',
    type: 'task_updated',
    message: 'Updated Database Migration Scripts to Done status',
    timestamp: new Date('2024-01-20T08:45:00'),
    task: mockTasks[3],
    status: 'success',
  },
  {
    id: '4',
    type: 'reminder_sent',
    message: 'Sent deadline reminder to Mike Rodriguez',
    timestamp: new Date('2024-01-19T15:00:00'),
    teamMember: mockTeamMembers[1],
    status: 'warning',
  },
];

export const mockAgentStatus: AgentStatus = {
  isActive: true,
  currentTask: 'Monitoring email responses',
  nextScheduledAction: new Date('2024-01-27T09:00:00'),
  tasksCompleted: 24,
  emailsSent: 156,
  responsesReceived: 142,
  lastActivity: new Date('2024-01-20T10:30:00'),
};

export const mockEmailTemplates: EmailTemplate[] = [
  {
    id: '1',
    name: 'Weekly Update Request',
    subject: 'Weekly Update Request - {{date}}',
    content: `Hi {{name}},

I hope you're having a great week! Could you please share a brief update on:

1. What you've been working on this week
2. Any blockers or challenges you're facing
3. Your priorities for next week

Thanks for keeping the team informed!

Best regards,
Assistant Manager`,
    type: 'update_request',
    variables: ['name', 'date'],
  },
  {
    id: '2',
    name: 'Task Deadline Reminder',
    subject: 'Reminder: {{task_name}} due {{due_date}}',
    content: `Hi {{name}},

This is a friendly reminder that your task "{{task_name}}" is due on {{due_date}}.

Current status: {{status}}
Priority: {{priority}}

If you need any assistance or if there are any blockers, please let me know.

Best regards,
Assistant Manager`,
    type: 'reminder',
    variables: ['name', 'task_name', 'due_date', 'status', 'priority'],
  },
];

export const mockWorkflowSettings: WorkflowSettings = {
  updateFrequency: 'weekly',
  reminderDays: 2,
  maxFollowUps: 3,
  autoApproveChanges: false,
  githubRepo: 'company/team-kanban',
};