import React, { useState, useEffect } from 'react';
import { DndContext, DragEndEvent, DragOverlay, DragStartEvent, closestCenter, pointerWithin, CollisionDetection, rectIntersection } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { KanbanColumn } from './KanbanColumn';
import { TaskCard } from './TaskCard';
import { TaskModal } from './TaskModal';
import { useKanbanBoard } from '../../hooks/useKanbanBoard';
import { Task, TaskStatus } from '../../types';
import { Plus, RefreshCw, Save, AlertCircle, Github, ExternalLink, Loader2 } from 'lucide-react';

export const KanbanBoard: React.FC = () => {
  const { 
    columns, 
    isLoading, 
    error, 
    createTask, 
    updateTask, 
    deleteTask, 
    moveTask,
    refreshBoard,
    pendingChanges,
    approvePendingChanges
  } = useKanbanBoard();

  const [activeTask, setActiveTask] = useState<Task | null>(null);
  const [showTaskModal, setShowTaskModal] = useState(false);
  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [selectedStatus, setSelectedStatus] = useState<TaskStatus>('todo');
  const [isPublishing, setIsPublishing] = useState(false);
  const [publishStatus, setPublishStatus] = useState<string | null>(null);

  // Custom collision detection for better kanban column targeting
  const customCollisionDetection: CollisionDetection = (args) => {
    // First try pointer-based detection for more precise targeting
    const pointerCollisions = pointerWithin(args);
    if (pointerCollisions.length > 0) {
      return pointerCollisions;
    }

    // Fallback to closest center for better adjacent column handling
    return closestCenter(args);
  };

  const handleDragStart = (event: DragStartEvent) => {
    const task = columns
      .flatMap(col => col.tasks)
      .find(task => task.id === event.active.id);
    setActiveTask(task || null);
  };

  const handleDragEnd = (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveTask(null);

    if (!over) return;

    const taskId = active.id as string;
    const newStatus = over.id as TaskStatus;

    // Find the task being moved
    const task = columns
      .flatMap(col => col.tasks)
      .find(task => task.id === taskId);

    if (task && task.status !== newStatus) {
      moveTask(taskId, newStatus);
    }
  };

  const handleCreateTask = (status: TaskStatus) => {
    setSelectedStatus(status);
    setEditingTask(null);
    setShowTaskModal(true);
  };

  const handleEditTask = (task: Task) => {
    setEditingTask(task);
    setShowTaskModal(true);
  };

  const handleDeleteTask = async (taskId: string) => {
    if (window.confirm('Are you sure you want to delete this task?')) {
      await deleteTask(taskId);
    }
  };

  const handleSaveTask = async (taskData: Partial<Task>) => {
    try {
      if (editingTask) {
        await updateTask(editingTask.id, taskData);
      } else {
        await createTask({
          ...taskData,
          status: selectedStatus,
        } as Omit<Task, 'id' | 'createdAt' | 'updatedAt'>);
      }
      setShowTaskModal(false);
      setEditingTask(null);
    } catch (error) {
      console.error('Error saving task:', error);
    }
  };

  const handlePublishToGitHub = async () => {
    try {
      setIsPublishing(true);
      setPublishStatus(null);
      
      // Trigger GitHub publishing workflow through agent
      const response = await fetch('/api/agents/trigger-workflow?workflow_type=github_publish', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to trigger GitHub publishing workflow');
      }
      
      const result = await response.json();
      setPublishStatus(result.data?.response || 'Successfully published to GitHub Pages!');
      
    } catch (error) {
      console.error('Error publishing to GitHub:', error);
      setPublishStatus('Failed to publish to GitHub Pages. Please check your configuration.');
    } finally {
      setIsPublishing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="h-full p-6 bg-background-light dark:bg-background-dark flex items-center justify-center">
        <div className="text-center">
          <RefreshCw className="h-8 w-8 animate-spin text-primary-500 mx-auto mb-4" />
          <p className="text-neutral-600 dark:text-neutral-400">Loading kanban board...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-full p-6 bg-background-light dark:bg-background-dark flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="h-8 w-8 text-red-500 mx-auto mb-4" />
          <p className="text-red-600 dark:text-red-400 mb-4">{error}</p>
          <button
            onClick={refreshBoard}
            className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full p-6 bg-background-light dark:bg-background-dark flex flex-col">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">
              Project Kanban Board
            </h2>
            <p className="text-neutral-600 dark:text-neutral-400">
              Track and manage team tasks across different stages
            </p>
          </div>
          
          <div className="flex items-center space-x-4">
            {/* Pending Changes Indicator */}
            {pendingChanges > 0 && (
              <div className="flex items-center space-x-3 px-4 py-2 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl">
                <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
                <span className="text-sm font-medium text-yellow-700 dark:text-yellow-400">
                  {pendingChanges} changes pending approval
                </span>
                <button
                  onClick={approvePendingChanges}
                  className="px-3 py-1 bg-yellow-500 text-white text-xs rounded-lg hover:bg-yellow-600 transition-colors"
                >
                  Approve All
                </button>
              </div>
            )}

            {/* Publish Status */}
            {publishStatus && (
              <div className={`flex items-center space-x-3 px-4 py-2 rounded-xl border ${
                publishStatus.includes('Failed') || publishStatus.includes('Error')
                  ? 'bg-red-50 dark:bg-red-900/20 border-red-200 dark:border-red-800'
                  : 'bg-green-50 dark:bg-green-900/20 border-green-200 dark:border-green-800'
              }`}>
                <span className={`text-sm font-medium ${
                  publishStatus.includes('Failed') || publishStatus.includes('Error')
                    ? 'text-red-700 dark:text-red-400'
                    : 'text-green-700 dark:text-green-400'
                }`}>
                  {publishStatus}
                </span>
                <button
                  onClick={() => setPublishStatus(null)}
                  className="text-xs opacity-60 hover:opacity-100"
                >
                  ×
                </button>
              </div>
            )}

            {/* Action Buttons */}
            <button
              onClick={refreshBoard}
              className="p-2.5 text-neutral-500 dark:text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-xl transition-all duration-200"
              title="Refresh board"
            >
              <RefreshCw className="h-5 w-5" />
            </button>

            {/* GitHub Sync Button */}
            <button
              onClick={handlePublishToGitHub}
              disabled={isPublishing}
              className="flex items-center space-x-2 px-4 py-2.5 bg-neutral-900 dark:bg-neutral-700 text-white rounded-xl hover:bg-neutral-800 dark:hover:bg-neutral-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-medium"
              title="Sync to GitHub Pages"
            >
              {isPublishing ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Github className="h-4 w-4" />
              )}
              <span>{isPublishing ? 'Publishing...' : 'Sync to GitHub'}</span>
              <ExternalLink className="h-3 w-3 opacity-60" />
            </button>
            
            <button
              onClick={() => handleCreateTask('todo')}
              className="flex items-center space-x-2 px-4 py-2.5 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-all duration-200 font-medium shadow-medium"
            >
              <Plus className="h-4 w-4" />
              <span>Add Task</span>
            </button>
          </div>
        </div>
      </div>

      {/* Kanban Board */}
      <div className="flex-1 overflow-hidden">
        <DndContext
          collisionDetection={customCollisionDetection}
          onDragStart={handleDragStart}
          onDragEnd={handleDragEnd}
        >
          <div className="grid grid-cols-5 gap-6 h-full">
            {columns.map((column) => (
              <SortableContext
                key={column.id}
                items={column.tasks.map(task => task.id)}
                strategy={verticalListSortingStrategy}
              >
                <KanbanColumn
                  column={column}
                  onAddTask={handleCreateTask}
                  onEditTask={handleEditTask}
                  onDeleteTask={handleDeleteTask}
                />
              </SortableContext>
            ))}
          </div>

          {/* Drag Overlay */}
          <DragOverlay>
            {activeTask ? (
              <TaskCard task={activeTask} isDragging />
            ) : null}
          </DragOverlay>
        </DndContext>
      </div>

      {/* Task Modal */}
      <TaskModal
        isOpen={showTaskModal}
        onClose={() => {
          setShowTaskModal(false);
          setEditingTask(null);
        }}
        onSave={handleSaveTask}
        task={editingTask}
        defaultStatus={selectedStatus}
      />
    </div>
  );
};