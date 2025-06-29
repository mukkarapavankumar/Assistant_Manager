import { useState, useEffect, useCallback } from 'react';
import { Task, TaskStatus, KanbanColumn } from '../types';
import { kanbanApi, agentApi } from '../services/api';

export const useKanbanBoard = () => {
  const [columns, setColumns] = useState<KanbanColumn[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pendingChanges, setPendingChanges] = useState(0);

  // Initialize board
  useEffect(() => {
    fetchBoard();
  }, []);

  const fetchBoard = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      const boardData = await kanbanApi.getBoard();
      setColumns(boardData.columns || []);
      
      // Get pending changes count
      const pendingResponse = await kanbanApi.getPendingChanges();
      setPendingChanges(pendingResponse.data?.changes?.length || 0);
      
    } catch (err) {
      console.error('Error fetching kanban board:', err);
      setError('Failed to load kanban board. Please try again.');
      
      // Fallback to mock data structure
      setColumns([
        { id: 'todo', title: 'To Do', tasks: [], color: 'neutral' },
        { id: 'in_progress', title: 'In Progress', tasks: [], color: 'primary' },
        { id: 'review', title: 'Review', tasks: [], color: 'warning' },
        { id: 'done', title: 'Done', tasks: [], color: 'success' },
        { id: 'blocked', title: 'Blocked', tasks: [], color: 'error' },
      ]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const refreshBoard = useCallback(() => {
    fetchBoard();
  }, [fetchBoard]);

  const createTask = useCallback(async (taskData: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>) => {
    try {
      setError(null);
      
      const newTask = await kanbanApi.createTask({
        title: taskData.title,
        description: taskData.description,
        status: taskData.status,
        assignee_id: parseInt(taskData.assignee.id),
        due_date: taskData.dueDate?.toISOString(),
        priority: taskData.priority,
        tags: taskData.tags,
      });

      // Refresh board to get updated data
      await fetchBoard();
      
      return newTask;
    } catch (err) {
      console.error('Error creating task:', err);
      setError('Failed to create task. Please try again.');
      throw err;
    }
  }, [fetchBoard]);

  const updateTask = useCallback(async (taskId: string, updates: Partial<Task>) => {
    try {
      setError(null);
      
      const updateData: any = {};
      
      if (updates.title !== undefined) updateData.title = updates.title;
      if (updates.description !== undefined) updateData.description = updates.description;
      if (updates.status !== undefined) updateData.status = updates.status;
      if (updates.assignee !== undefined) updateData.assignee_id = parseInt(updates.assignee.id);
      if (updates.dueDate !== undefined) updateData.due_date = updates.dueDate?.toISOString();
      if (updates.priority !== undefined) updateData.priority = updates.priority;
      if (updates.tags !== undefined) updateData.tags = updates.tags;

      await kanbanApi.updateTask(parseInt(taskId), updateData);
      
      // Refresh board to get updated data
      await fetchBoard();
      
    } catch (err) {
      console.error('Error updating task:', err);
      setError('Failed to update task. Please try again.');
      throw err;
    }
  }, [fetchBoard]);

  const deleteTask = useCallback(async (taskId: string) => {
    try {
      setError(null);
      
      await kanbanApi.deleteTask(parseInt(taskId));
      
      // Refresh board to get updated data
      await fetchBoard();
      
    } catch (err) {
      console.error('Error deleting task:', err);
      setError('Failed to delete task. Please try again.');
      throw err;
    }
  }, [fetchBoard]);

  const moveTask = useCallback(async (taskId: string, newStatus: TaskStatus) => {
    try {
      setError(null);
      
      // Optimistically update the UI
      setColumns(prevColumns => {
        const newColumns = prevColumns.map(column => ({
          ...column,
          tasks: column.tasks.filter(task => task.id !== taskId)
        }));

        // Find the task and move it to the new column
        const task = prevColumns
          .flatMap(col => col.tasks)
          .find(task => task.id === taskId);

        if (task) {
          const updatedTask = { ...task, status: newStatus };
          const targetColumn = newColumns.find(col => col.id === newStatus);
          if (targetColumn) {
            targetColumn.tasks.push(updatedTask);
          }
        }

        return newColumns;
      });

      // Update on the backend
      await kanbanApi.updateTask(parseInt(taskId), { status: newStatus });
      
      // Refresh to ensure consistency
      await fetchBoard();
      
    } catch (err) {
      console.error('Error moving task:', err);
      setError('Failed to move task. Please try again.');
      
      // Revert optimistic update by refreshing
      await fetchBoard();
      throw err;
    }
  }, [fetchBoard]);

  const approvePendingChanges = useCallback(async () => {
    try {
      setError(null);
      
      // Get pending changes
      const pendingResponse = await kanbanApi.getPendingChanges();
      const changes = pendingResponse.data?.changes || [];
      
      if (changes.length > 0) {
        const changeIds = changes.map((change: any) => change.id);
        await agentApi.approveChanges(changeIds);
        
        // Refresh board and pending count
        await fetchBoard();
      }
      
    } catch (err) {
      console.error('Error approving changes:', err);
      setError('Failed to approve changes. Please try again.');
      throw err;
    }
  }, [fetchBoard]);

  return {
    columns,
    isLoading,
    error,
    pendingChanges,
    createTask,
    updateTask,
    deleteTask,
    moveTask,
    refreshBoard,
    approvePendingChanges,
  };
};