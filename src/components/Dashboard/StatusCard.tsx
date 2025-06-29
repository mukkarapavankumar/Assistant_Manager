import React from 'react';
import { DivideIcon as LucideIcon } from 'lucide-react';
import { clsx } from 'clsx';

interface StatusCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: number;
    isPositive: boolean;
  };
  color: 'primary' | 'success' | 'warning' | 'error' | 'neutral';
}

const colorClasses = {
  primary: {
    bg: 'bg-primary-50 dark:bg-primary-900/20',
    icon: 'text-primary-600 dark:text-primary-400',
    text: 'text-primary-900 dark:text-primary-100',
    border: 'border-primary-200 dark:border-primary-800',
  },
  success: {
    bg: 'bg-green-50 dark:bg-green-900/20',
    icon: 'text-green-600 dark:text-green-400',
    text: 'text-green-900 dark:text-green-100',
    border: 'border-green-200 dark:border-green-800',
  },
  warning: {
    bg: 'bg-yellow-50 dark:bg-yellow-900/20',
    icon: 'text-yellow-600 dark:text-yellow-400',
    text: 'text-yellow-900 dark:text-yellow-100',
    border: 'border-yellow-200 dark:border-yellow-800',
  },
  error: {
    bg: 'bg-red-50 dark:bg-red-900/20',
    icon: 'text-red-600 dark:text-red-400',
    text: 'text-red-900 dark:text-red-100',
    border: 'border-red-200 dark:border-red-800',
  },
  neutral: {
    bg: 'bg-neutral-50 dark:bg-neutral-800',
    icon: 'text-neutral-600 dark:text-neutral-400',
    text: 'text-neutral-900 dark:text-neutral-100',
    border: 'border-neutral-200 dark:border-neutral-700',
  },
};

export const StatusCard: React.FC<StatusCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  color,
}) => {
  const colors = colorClasses[color];

  return (
    <div className="bg-white dark:bg-neutral-800 p-6 rounded-xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark transition-all duration-200 hover:shadow-medium dark:hover:shadow-medium-dark">
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-neutral-600 dark:text-neutral-400 mb-2">{title}</p>
          <p className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-1">{value}</p>
          {subtitle && (
            <p className="text-sm text-neutral-500 dark:text-neutral-400">{subtitle}</p>
          )}
          {trend && (
            <div className="flex items-center mt-3">
              <span className={clsx(
                'text-sm font-semibold px-2 py-1 rounded-lg',
                trend.isPositive 
                  ? 'text-green-700 dark:text-green-400 bg-green-100 dark:bg-green-900/30' 
                  : 'text-red-700 dark:text-red-400 bg-red-100 dark:bg-red-900/30'
              )}>
                {trend.isPositive ? '+' : ''}{trend.value}%
              </span>
              <span className="text-sm text-neutral-500 dark:text-neutral-400 ml-2">vs last week</span>
            </div>
          )}
        </div>
        <div className={clsx('p-3 rounded-xl', colors.bg, colors.border, 'border')}>
          <Icon className={clsx('h-6 w-6', colors.icon)} />
        </div>
      </div>
    </div>
  );
};