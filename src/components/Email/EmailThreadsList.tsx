import React from 'react';
import { format } from 'date-fns';
import { Mail, CheckCircle2, Clock, AlertTriangle, User, Reply } from 'lucide-react';
import { clsx } from 'clsx';

interface EmailThread {
  id: number;
  team_member_id: number;
  subject: string;
  sent_at: string;
  response_received: boolean;
  response_at?: string;
  status: string;
  content: string;
  follow_up_count: number;
  template_used?: string;
  team_member: {
    id: number;
    name: string;
    email: string;
    role: string;
  };
}

interface EmailThreadsListProps {
  threads: EmailThread[];
  compact?: boolean;
}

const getStatusIcon = (status: string, responseReceived: boolean) => {
  if (responseReceived) {
    return <CheckCircle2 className="h-4 w-4 text-green-600" />;
  }
  
  switch (status) {
    case 'sent':
      return <Mail className="h-4 w-4 text-blue-600" />;
    case 'opened':
      return <Mail className="h-4 w-4 text-yellow-600" />;
    case 'overdue':
      return <AlertTriangle className="h-4 w-4 text-red-600" />;
    default:
      return <Clock className="h-4 w-4 text-neutral-500" />;
  }
};

const getStatusColor = (status: string, responseReceived: boolean) => {
  if (responseReceived) {
    return 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800 text-green-700 dark:text-green-400';
  }
  
  switch (status) {
    case 'sent':
      return 'bg-blue-50 dark:bg-blue-900/20 border-blue-200 dark:border-blue-800 text-blue-700 dark:text-blue-400';
    case 'opened':
      return 'bg-yellow-50 dark:bg-yellow-900/20 border-yellow-200 dark:border-yellow-800 text-yellow-700 dark:text-yellow-400';
    case 'overdue':
      return 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800 text-red-700 dark:text-red-400';
    default:
      return 'bg-neutral-50 dark:bg-neutral-800 border-neutral-200 dark:border-neutral-700 text-neutral-700 dark:text-neutral-400';
  }
};

export const EmailThreadsList: React.FC<EmailThreadsListProps> = ({ threads, compact = false }) => {
  if (threads.length === 0) {
    return (
      <div className="text-center py-12">
        <Mail className="h-12 w-12 text-neutral-400 mx-auto mb-4" />
        <h4 className="text-lg font-medium text-neutral-900 dark:text-neutral-100 mb-2">
          No email threads found
        </h4>
        <p className="text-neutral-500 dark:text-neutral-400">
          Email threads will appear here once you start sending automated emails
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {threads.map((thread) => (
        <div
          key={thread.id}
          className={clsx(
            'bg-surface-light dark:bg-card-dark rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark transition-all duration-200 hover:shadow-medium dark:hover:shadow-medium-dark',
            compact ? 'p-4' : 'p-6'
          )}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1">
              {/* Header */}
              <div className="flex items-center space-x-3 mb-3">
                <div className="h-8 w-8 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center">
                  <User className="h-4 w-4 text-white" />
                </div>
                <div>
                  <h4 className="font-medium text-neutral-900 dark:text-neutral-100">
                    {thread.team_member.name}
                  </h4>
                  <p className="text-sm text-neutral-500 dark:text-neutral-400">
                    {thread.team_member.email} • {thread.team_member.role}
                  </p>
                </div>
              </div>

              {/* Subject */}
              <h5 className="font-medium text-neutral-900 dark:text-neutral-100 mb-2">
                {thread.subject}
              </h5>

              {/* Content Preview */}
              {!compact && (
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4 line-clamp-2">
                  {thread.content.substring(0, 150)}...
                </p>
              )}

              {/* Metadata */}
              <div className="flex items-center space-x-4 text-xs text-neutral-500 dark:text-neutral-400">
                <span>Sent {format(new Date(thread.sent_at), 'MMM dd, yyyy HH:mm')}</span>
                {thread.template_used && (
                  <>
                    <span>•</span>
                    <span>Template: {thread.template_used}</span>
                  </>
                )}
                {thread.follow_up_count > 0 && (
                  <>
                    <span>•</span>
                    <span>{thread.follow_up_count} follow-up{thread.follow_up_count > 1 ? 's' : ''}</span>
                  </>
                )}
                {thread.response_received && thread.response_at && (
                  <>
                    <span>•</span>
                    <span>Replied {format(new Date(thread.response_at), 'MMM dd, yyyy HH:mm')}</span>
                  </>
                )}
              </div>
            </div>

            {/* Status */}
            <div className="flex items-center space-x-3 ml-4">
              <div className={clsx(
                'flex items-center space-x-2 px-3 py-1.5 rounded-lg border text-sm font-medium',
                getStatusColor(thread.status, thread.response_received)
              )}>
                {getStatusIcon(thread.status, thread.response_received)}
                <span>
                  {thread.response_received ? 'Replied' : 
                   thread.status === 'overdue' ? 'Overdue' :
                   thread.status === 'opened' ? 'Opened' : 'Sent'}
                </span>
              </div>

              {thread.response_received && (
                <button className="p-2 text-primary-600 hover:text-primary-700 hover:bg-primary-100 dark:hover:bg-primary-900/30 rounded-lg transition-all duration-200">
                  <Reply className="h-4 w-4" />
                </button>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
};