import React from 'react';
import { StatusCard } from './StatusCard';
import { ActivityFeed } from './ActivityFeed';
import { AgentStatusPanel } from './AgentStatusPanel';
import { 
  CheckCircle2, 
  Mail, 
  Users, 
  Clock,
  TrendingUp,
  AlertTriangle,
  BarChart3,
  Target
} from 'lucide-react';
import { mockAgentActivities, mockAgentStatus, mockTasks, mockEmailThreads } from '../../data/mockData';

export const Dashboard: React.FC = () => {
  const completedTasks = mockTasks.filter(task => task.status === 'done').length;
  const pendingEmails = mockEmailThreads.filter(email => !email.responseReceived).length;
  const activeTeamMembers = 4;
  const overdueReminders = mockTasks.filter(task => 
    task.dueDate && new Date() > task.dueDate && task.status !== 'done'
  ).length;

  return (
    <div className="p-6 space-y-6 bg-background-light dark:bg-background-dark min-h-screen">
      <div>
        <h2 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">Dashboard</h2>
        <p className="text-neutral-600 dark:text-neutral-400">Overview of team activities and agent performance</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatusCard
          title="Tasks Completed"
          value={completedTasks}
          subtitle="This week"
          icon={CheckCircle2}
          color="success"
          trend={{ value: 12, isPositive: true }}
        />
        <StatusCard
          title="Pending Responses"
          value={pendingEmails}
          subtitle="Awaiting replies"
          icon={Mail}
          color="warning"
          trend={{ value: -8, isPositive: false }}
        />
        <StatusCard
          title="Active Members"
          value={activeTeamMembers}
          subtitle="Team size"
          icon={Users}
          color="primary"
        />
        <StatusCard
          title="Overdue Items"
          value={overdueReminders}
          subtitle="Need attention"
          icon={AlertTriangle}
          color="error"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <ActivityFeed activities={mockAgentActivities} />
        </div>
        <div>
          <AgentStatusPanel status={mockAgentStatus} />
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Response Rate Card */}
        <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 bg-primary-50 dark:bg-primary-900/30 rounded-xl">
              <TrendingUp className="h-5 w-5 text-primary-600 dark:text-primary-400" />
            </div>
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Response Rate</h3>
          </div>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-neutral-600 dark:text-neutral-400">Overall</span>
              <span className="text-sm font-semibold text-neutral-900 dark:text-neutral-100">91%</span>
            </div>
            <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-3">
              <div className="bg-gradient-to-r from-primary-500 to-primary-600 h-3 rounded-full transition-all duration-500" style={{ width: '91%' }}></div>
            </div>
          </div>
        </div>

        {/* Average Response Time Card */}
        <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 bg-green-50 dark:bg-green-900/30 rounded-xl">
              <Clock className="h-5 w-5 text-green-600 dark:text-green-400" />
            </div>
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Avg Response Time</h3>
          </div>
          <div className="text-center">
            <p className="text-4xl font-bold text-neutral-900 dark:text-neutral-100">2.4</p>
            <p className="text-sm text-neutral-500 dark:text-neutral-400">hours</p>
          </div>
        </div>

        {/* Task Velocity Card */}
        <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark p-6">
          <div className="flex items-center space-x-3 mb-6">
            <div className="p-2 bg-yellow-50 dark:bg-yellow-900/30 rounded-xl">
              <Target className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
            </div>
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Task Velocity</h3>
          </div>
          <div className="text-center">
            <p className="text-4xl font-bold text-neutral-900 dark:text-neutral-100">12</p>
            <p className="text-sm text-neutral-500 dark:text-neutral-400">tasks/week</p>
          </div>
        </div>
      </div>
    </div>
  );
};