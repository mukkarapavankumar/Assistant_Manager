import React from 'react';
import { format } from 'date-fns';
import { Calendar, User, AlertTriangle, CheckCircle2, Edit2, Trash2, MoreVertical } from 'lucide-react';
import { Task, Priority } from '../../types';
import { clsx } from 'clsx';

interface TaskCardProps {
  task: Task;
  isDragging?: boolean;
  onEdit?: (task: Task) => void;
  onDelete?: (taskId: string) => void;
}

const getPriorityDot = (priority: Priority) => {
  switch (priority) {
    case 'urgent':
      return 'bg-red-500';
    case 'high':
      return 'bg-primary-500';
    case 'medium':
      return 'bg-yellow-500';
    case 'low':
      return 'bg-neutral-400';
    default:
      return 'bg-neutral-400';
  }
};

const getStatusIcon = (status: Task['status']) => {
  switch (status) {
    case 'done':
      return <CheckCircle2 className="h-3 w-3 text-green-600" />;
    case 'blocked':
      return <AlertTriangle className="h-3 w-3 text-red-500" />;
    default:
      return null;
  }
};

export const TaskCard: React.FC<TaskCardProps> = ({ 
  task, 
  isDragging, 
  onEdit, 
  onDelete 
}) => {
  const isOverdue = task.dueDate && new Date() > task.dueDate && task.status !== 'done';
  const [showActions, setShowActions] = React.useState(false);

  const handleEdit = (e: React.MouseEvent) => {
    e.stopPropagation();
    onEdit?.(task);
  };

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    onDelete?.(task.id);
  };

  return (
    <div
      className={clsx(
        'bg-white dark:bg-neutral-800 rounded-lg border border-neutral-200 dark:border-neutral-700 p-3 transition-all duration-200 cursor-grab group relative',
        isDragging ? 'shadow-large dark:shadow-large-dark scale-105 rotate-1 cursor-grabbing' : 'shadow-soft dark:shadow-soft-dark hover:shadow-medium dark:hover:shadow-medium-dark',
        isOverdue && 'border-red-300 dark:border-red-600'
      )}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Action Buttons */}
      {showActions && (onEdit || onDelete) && (
        <div className="absolute top-2 right-2 flex items-center space-x-1 bg-white dark:bg-neutral-800 rounded-lg shadow-medium border border-neutral-200 dark:border-neutral-700 p-1">
          {onEdit && (
            <button
              onClick={handleEdit}
              className="p-1 text-neutral-500 hover:text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/30 rounded transition-colors"
              title="Edit task"
            >
              <Edit2 className="h-3 w-3" />
            </button>
          )}
          {onDelete && (
            <button
              onClick={handleDelete}
              className="p-1 text-neutral-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 rounded transition-colors"
              title="Delete task"
            >
              <Trash2 className="h-3 w-3" />
            </button>
          )}
        </div>
      )}

      {/* Header with title and status */}
      <div className="flex items-start justify-between mb-2 pr-8">
        <h4 className="text-sm font-medium text-neutral-900 dark:text-neutral-100 line-clamp-2 leading-tight">
          {task.title}
        </h4>
        {getStatusIcon(task.status)}
      </div>

      {/* Description */}
      {task.description && (
        <p className="text-xs text-neutral-600 dark:text-neutral-400 mb-3 line-clamp-2 leading-relaxed">
          {task.description}
        </p>
      )}

      {/* Footer */}
      <div className="flex items-center justify-between">
        {/* Assignee */}
        <div className="flex items-center space-x-2">
          <div className="h-5 w-5 bg-gradient-to-br from-primary-400 to-primary-600 rounded-full flex items-center justify-center">
            <User className="h-2.5 w-2.5 text-white" />
          </div>
          <span className="text-xs text-neutral-600 dark:text-neutral-400 font-medium">
            {task.assignee.name.split(' ')[0]}
          </span>
        </div>

        {/* Priority and due date */}
        <div className="flex items-center space-x-2">
          {/* Priority dot */}
          <div className={clsx('h-2 w-2 rounded-full', getPriorityDot(task.priority))}></div>
          
          {/* Due date */}
          {task.dueDate && (
            <span className={clsx(
              'text-xs',
              isOverdue 
                ? 'text-red-600 dark:text-red-400 font-medium' 
                : 'text-neutral-500 dark:text-neutral-400'
            )}>
              {format(task.dueDate, 'MMM dd')}
            </span>
          )}
        </div>
      </div>

      {/* Tags - only show if present */}
      {task.tags.length > 0 && (
        <div className="flex flex-wrap gap-1 mt-2">
          {task.tags.slice(0, 2).map((tag) => (
            <span
              key={tag}
              className="px-1.5 py-0.5 text-xs bg-neutral-100 dark:bg-neutral-700 text-neutral-600 dark:text-neutral-400 rounded"
            >
              {tag}
            </span>
          ))}
          {task.tags.length > 2 && (
            <span className="px-1.5 py-0.5 text-xs bg-neutral-100 dark:bg-neutral-700 text-neutral-600 dark:text-neutral-400 rounded">
              +{task.tags.length - 2}
            </span>
          )}
        </div>
      )}
    </div>
  );
};