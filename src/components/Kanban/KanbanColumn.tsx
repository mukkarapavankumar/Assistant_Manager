import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { Plus } from 'lucide-react';
import { SortableTaskCard } from './SortableTaskCard';
import { KanbanColumn as KanbanColumnType, Task } from '../../types';
import { clsx } from 'clsx';

interface KanbanColumnProps {
  column: KanbanColumnType;
  onAddTask: (status: KanbanColumnType['id']) => void;
  onEditTask: (task: Task) => void;
  onDeleteTask: (taskId: string) => void;
}

const getColumnStyles = (id: string) => {
  switch (id) {
    case 'todo':
      return {
        header: 'text-neutral-700 dark:text-neutral-300',
        bg: 'bg-neutral-50/50 dark:bg-neutral-800/30',
        border: 'border-neutral-200 dark:border-neutral-700',
      };
    case 'in_progress':
      return {
        header: 'text-primary-700 dark:text-primary-400',
        bg: 'bg-primary-50/50 dark:bg-primary-900/20',
        border: 'border-primary-200 dark:border-primary-700',
      };
    case 'review':
      return {
        header: 'text-yellow-700 dark:text-yellow-400',
        bg: 'bg-yellow-50/50 dark:bg-yellow-900/20',
        border: 'border-yellow-200 dark:border-yellow-700',
      };
    case 'done':
      return {
        header: 'text-green-700 dark:text-green-400',
        bg: 'bg-green-50/50 dark:bg-green-900/20',
        border: 'border-green-200 dark:border-green-700',
      };
    case 'blocked':
      return {
        header: 'text-red-700 dark:text-red-400',
        bg: 'bg-red-50/50 dark:bg-red-900/20',
        border: 'border-red-200 dark:border-red-700',
      };
    default:
      return {
        header: 'text-neutral-700 dark:text-neutral-300',
        bg: 'bg-neutral-50/50 dark:bg-neutral-800/30',
        border: 'border-neutral-200 dark:border-neutral-700',
      };
  }
};

export const KanbanColumn: React.FC<KanbanColumnProps> = ({ 
  column, 
  onAddTask, 
  onEditTask, 
  onDeleteTask 
}) => {
  const { setNodeRef, isOver } = useDroppable({
    id: column.id,
  });

  const styles = getColumnStyles(column.id);

  return (
    <div className="flex flex-col h-full">
      {/* Column Header */}
      <div className={clsx(
        'flex items-center justify-between p-4 rounded-t-xl border border-b-0',
        'bg-neutral-50 dark:bg-neutral-800/50',
        styles.border
      )}>
        <div className="flex items-center space-x-3">
          <h3 className={clsx('font-semibold text-sm', styles.header)}>
            {column.title}
          </h3>
          <span className="bg-white dark:bg-neutral-700 px-2 py-1 rounded-md text-xs font-medium text-neutral-600 dark:text-neutral-400 border border-neutral-200 dark:border-neutral-600">
            {column.tasks.length}
          </span>
        </div>
        
        <button
          onClick={() => onAddTask(column.id)}
          className="p-1.5 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 hover:bg-white dark:hover:bg-neutral-700 rounded-lg transition-all duration-200"
          title={`Add task to ${column.title}`}
        >
          <Plus className="h-4 w-4" />
        </button>
      </div>

      {/* Column Content - Enhanced Drop Zone */}
      <div
        ref={setNodeRef}
        className={clsx(
          'flex-1 p-4 space-y-3 min-h-96 border border-t-0 rounded-b-xl transition-all duration-200',
          styles.bg,
          styles.border,
          isOver && 'ring-2 ring-primary-500 ring-opacity-50 bg-primary-50/20 dark:bg-primary-900/30',
          column.tasks.length === 0 && 'border-dashed'
        )}
        style={{
          // Ensure the drop zone takes full width and height for better detection
          minHeight: '400px',
          position: 'relative'
        }}
      >
        {column.tasks.length === 0 ? (
          <div className="flex items-center justify-center h-32 text-neutral-400">
            <div className="text-center">
              <div className="text-2xl mb-2">📋</div>
              <p className="text-xs font-medium">No tasks</p>
              <p className="text-xs text-neutral-400 mt-1">Drag tasks here</p>
            </div>
          </div>
        ) : (
          <SortableContext
            items={column.tasks.map(task => task.id)}
            strategy={verticalListSortingStrategy}
          >
            {column.tasks.map((task) => (
              <SortableTaskCard
                key={task.id}
                task={task}
                onEdit={onEditTask}
                onDelete={onDeleteTask}
              />
            ))}
          </SortableContext>
        )}
        
        {/* Visual drop indicator when hovering */}
        {isOver && (
          <div className="absolute inset-0 pointer-events-none border-2 border-dashed border-primary-400 rounded-b-xl opacity-50" />
        )}
      </div>
    </div>
  );
};