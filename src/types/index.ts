export interface TeamMember {
  id: string;
  name: string;
  email: string;
  role: string;
  avatar?: string;
  active: boolean;
  lastResponseAt?: Date;
  responseRate: number;
}

export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  assignee: TeamMember;
  dueDate?: Date;
  priority: Priority;
  createdAt: Date;
  updatedAt: Date;
  tags: string[];
  order: number;
}

export type TaskStatus = 'todo' | 'in_progress' | 'review' | 'done' | 'blocked';
export type Priority = 'low' | 'medium' | 'high' | 'urgent';

export interface EmailThread {
  id: string;
  teamMember: TeamMember;
  subject: string;
  sentAt: Date;
  responseReceived: boolean;
  responseAt?: Date;
  status: 'sent' | 'opened' | 'replied' | 'overdue';
  content: string;
  followUpCount: number;
}

export interface AgentActivity {
  id: string;
  type: 'email_sent' | 'task_updated' | 'response_received' | 'reminder_sent' | 'analysis_complete';
  message: string;
  timestamp: Date;
  teamMember?: TeamMember;
  task?: Task;
  status: 'success' | 'warning' | 'error' | 'info';
}

export interface AgentStatus {
  isActive: boolean;
  currentTask: string;
  nextScheduledAction?: Date;
  tasksCompleted: number;
  emailsSent: number;
  responsesReceived: number;
  lastActivity: Date;
}

export interface KanbanColumn {
  id: TaskStatus;
  title: string;
  tasks: Task[];
  color: string;
}

export interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  content: string;
  type: 'update_request' | 'reminder' | 'follow_up';
  variables: string[];
}

export interface WorkflowSettings {
  updateFrequency: 'daily' | 'weekly' | 'biweekly';
  reminderDays: number;
  maxFollowUps: number;
  autoApproveChanges: boolean;
  githubRepo?: string;
  githubToken?: string;
}