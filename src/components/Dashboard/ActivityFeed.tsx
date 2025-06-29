import React from 'react';
import { format } from 'date-fns';
import { CheckCircle2, Mail, AlertCircle, Info, Clock } from 'lucide-react';
import { AgentActivity } from '../../types';
import { clsx } from 'clsx';

interface ActivityFeedProps {
  activities: AgentActivity[];
}

const getActivityIcon = (type: AgentActivity['type'], status: AgentActivity['status']) => {
  switch (type) {
    case 'email_sent':
      return <Mail className="h-4 w-4" />;
    case 'response_received':
      return <CheckCircle2 className="h-4 w-4" />;
    case 'task_updated':
      return <CheckCircle2 className="h-4 w-4" />;
    case 'reminder_sent':
      return <Clock className="h-4 w-4" />;
    case 'analysis_complete':
      return <Info className="h-4 w-4" />;
    default:
      return <Info className="h-4 w-4" />;
  }
};

const getStatusColor = (status: AgentActivity['status']) => {
  switch (status) {
    case 'success':
      return 'text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800';
    case 'warning':
      return 'text-yellow-600 dark:text-yellow-400 bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800';
    case 'error':
      return 'text-red-600 dark:text-red-400 bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800';
    case 'info':
      return 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800';
    default:
      return 'text-neutral-600 dark:text-neutral-400 bg-neutral-50 dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700';
  }
};

export const ActivityFeed: React.FC<ActivityFeedProps> = ({ activities }) => {
  return (
    <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark">
      <div className="p-6 border-b border-neutral-200 dark:border-neutral-700">
        <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Activity manager</h3>
        <p className="text-sm text-neutral-500 dark:text-neutral-400 mt-1">Latest agent actions and updates</p>
      </div>
      
      <div className="p-6">
        <div className="space-y-4">
          {activities.map((activity) => (
            <div key={activity.id} className="flex items-start space-x-4 animate-fade-in">
              <div className={clsx(
                'flex items-center justify-center w-10 h-10 rounded-xl border',
                getStatusColor(activity.status)
              )}>
                {getActivityIcon(activity.type, activity.status)}
              </div>
              
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
                  {activity.message}
                </p>
                <div className="flex items-center space-x-4 mt-2">
                  <p className="text-xs text-neutral-500 dark:text-neutral-400">
                    {format(activity.timestamp, 'MMM dd, HH:mm')}
                  </p>
                  {activity.teamMember && (
                    <span className="text-xs text-neutral-500 dark:text-neutral-400">
                      • {activity.teamMember.name}
                    </span>
                  )}
                  {activity.task && (
                    <span className="text-xs text-neutral-500 dark:text-neutral-400">
                      • {activity.task.title}
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};