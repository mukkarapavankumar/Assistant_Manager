import React from 'react';
import { format } from 'date-fns';
import { Play, Pause, RefreshCw, Calendar, TrendingUp } from 'lucide-react';
import { AgentStatus } from '../../types';

interface AgentStatusPanelProps {
  status: AgentStatus;
}

export const AgentStatusPanel: React.FC<AgentStatusPanelProps> = ({ status }) => {
  return (
    <div className="bg-white dark:bg-neutral-800 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark">
      <div className="p-6 border-b border-neutral-200 dark:border-neutral-700">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">Agent Status</h3>
            <p className="text-sm text-neutral-500 dark:text-neutral-400 mt-1">Current activity and performance</p>
          </div>
          <div className="flex items-center space-x-2">
            <button className="p-2.5 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-xl transition-all duration-200">
              <RefreshCw className="h-4 w-4" />
            </button>
            <button className="p-2.5 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-xl transition-all duration-200">
              {status.isActive ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
            </button>
          </div>
        </div>
      </div>

      <div className="p-6 space-y-6">
        <div className="flex items-center space-x-4">
          <div className={`h-3 w-3 rounded-full ${status.isActive ? 'bg-green-500 animate-pulse-soft' : 'bg-neutral-400'}`}></div>
          <div>
            <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">
              {status.isActive ? 'Active' : 'Inactive'}
            </p>
            <p className="text-sm text-neutral-500 dark:text-neutral-400">{status.currentTask}</p>
          </div>
        </div>

        {status.nextScheduledAction && (
          <div className="flex items-center space-x-4">
            <Calendar className="h-5 w-5 text-neutral-400" />
            <div>
              <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">Next Action</p>
              <p className="text-sm text-neutral-500 dark:text-neutral-400">
                {format(status.nextScheduledAction, 'MMM dd, yyyy HH:mm')}
              </p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-3 gap-4 pt-4 border-t border-neutral-200 dark:border-neutral-700">
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <div className="p-2 bg-primary-50 dark:bg-primary-900/30 rounded-xl">
                <TrendingUp className="h-4 w-4 text-primary-600 dark:text-primary-400" />
              </div>
            </div>
            <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">{status.tasksCompleted}</p>
            <p className="text-xs text-neutral-500 dark:text-neutral-400">Tasks Completed</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <div className="p-2 bg-green-50 dark:bg-green-900/30 rounded-xl">
                <TrendingUp className="h-4 w-4 text-green-600 dark:text-green-400" />
              </div>
            </div>
            <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">{status.emailsSent}</p>
            <p className="text-xs text-neutral-500 dark:text-neutral-400">Emails Sent</p>
          </div>
          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <div className="p-2 bg-yellow-50 dark:bg-yellow-900/30 rounded-xl">
                <TrendingUp className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
              </div>
            </div>
            <p className="text-2xl font-bold text-neutral-900 dark:text-neutral-100">{status.responsesReceived}</p>
            <p className="text-xs text-neutral-500 dark:text-neutral-400">Responses</p>
          </div>
        </div>

        <div className="pt-4 border-t border-neutral-200 dark:border-neutral-700">
          <p className="text-xs text-neutral-500 dark:text-neutral-400">
            Last activity: {format(status.lastActivity, 'MMM dd, yyyy HH:mm')}
          </p>
        </div>
      </div>
    </div>
  );
};