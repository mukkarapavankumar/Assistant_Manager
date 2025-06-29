import React from 'react';
import { Mail, CheckCircle2, Clock, TrendingUp, Users, FileText } from 'lucide-react';

interface EmailStatisticsProps {
  statistics: {
    total_threads: number;
    responded_threads: number;
    pending_threads: number;
    response_rate: number;
    recent_activity: {
      emails_sent_week: number;
      responses_received_week: number;
    };
    template_usage: Record<string, number>;
  };
}

export const EmailStatistics: React.FC<EmailStatisticsProps> = ({ statistics }) => {
  const {
    total_threads,
    responded_threads,
    pending_threads,
    response_rate,
    recent_activity,
    template_usage
  } = statistics;

  const mostUsedTemplate = Object.entries(template_usage).reduce(
    (max, [name, count]) => count > max.count ? { name, count } : max,
    { name: 'None', count: 0 }
  );

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {/* Total Emails */}
      <div className="bg-surface-light dark:bg-card-dark rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-primary-50 dark:bg-primary-900/30 rounded-xl">
            <Mail className="h-5 w-5 text-primary-600 dark:text-primary-400" />
          </div>
          <h3 className="font-semibold text-neutral-900 dark:text-neutral-100">Total Emails</h3>
        </div>
        <div className="space-y-2">
          <p className="text-3xl font-bold text-neutral-900 dark:text-neutral-100">{total_threads}</p>
          <p className="text-sm text-neutral-500 dark:text-neutral-400">
            {recent_activity.emails_sent_week} sent this week
          </p>
        </div>
      </div>

      {/* Response Rate */}
      <div className="bg-surface-light dark:bg-card-dark rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-green-50 dark:bg-green-900/30 rounded-xl">
            <CheckCircle2 className="h-5 w-5 text-green-600 dark:text-green-400" />
          </div>
          <h3 className="font-semibold text-neutral-900 dark:text-neutral-100">Response Rate</h3>
        </div>
        <div className="space-y-2">
          <p className="text-3xl font-bold text-neutral-900 dark:text-neutral-100">{response_rate}%</p>
          <div className="w-full bg-neutral-200 dark:bg-neutral-700 rounded-full h-2">
            <div 
              className="bg-green-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${response_rate}%` }}
            ></div>
          </div>
        </div>
      </div>

      {/* Pending Responses */}
      <div className="bg-surface-light dark:bg-card-dark rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-yellow-50 dark:bg-yellow-900/30 rounded-xl">
            <Clock className="h-5 w-5 text-yellow-600 dark:text-yellow-400" />
          </div>
          <h3 className="font-semibold text-neutral-900 dark:text-neutral-100">Pending</h3>
        </div>
        <div className="space-y-2">
          <p className="text-3xl font-bold text-neutral-900 dark:text-neutral-100">{pending_threads}</p>
          <p className="text-sm text-neutral-500 dark:text-neutral-400">
            Awaiting responses
          </p>
        </div>
      </div>

      {/* Most Used Template */}
      <div className="bg-surface-light dark:bg-card-dark rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark p-6">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-purple-50 dark:bg-purple-900/30 rounded-xl">
            <FileText className="h-5 w-5 text-purple-600 dark:text-purple-400" />
          </div>
          <h3 className="font-semibold text-neutral-900 dark:text-neutral-100">Top Template</h3>
        </div>
        <div className="space-y-2">
          <p className="text-lg font-bold text-neutral-900 dark:text-neutral-100 line-clamp-1">
            {mostUsedTemplate.name}
          </p>
          <p className="text-sm text-neutral-500 dark:text-neutral-400">
            Used {mostUsedTemplate.count} times
          </p>
        </div>
      </div>
    </div>
  );
};