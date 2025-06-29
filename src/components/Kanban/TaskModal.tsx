import React, { useState, useEffect } from 'react';
import { X, Save, Calendar, User, Tag, AlertCircle } from 'lucide-react';
import { Task, TaskStatus, Priority, TeamMember } from '../../types';
import { mockTeamMembers } from '../../data/mockData';
import { clsx } from 'clsx';

interface TaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (task: Partial<Task>) => void;
  task?: Task | null;
  defaultStatus?: TaskStatus;
}

const statusOptions: { value: TaskStatus; label: string; color: string }[] = [
  { value: 'todo', label: 'To Do', color: 'bg-neutral-100 text-neutral-700' },
  { value: 'in_progress', label: 'In Progress', color: 'bg-primary-100 text-primary-700' },
  { value: 'review', label: 'Review', color: 'bg-yellow-100 text-yellow-700' },
  { value: 'done', label: 'Done', color: 'bg-green-100 text-green-700' },
  { value: 'blocked', label: 'Blocked', color: 'bg-red-100 text-red-700' },
];

const priorityOptions: { value: Priority; label: string; color: string }[] = [
  { value: 'low', label: 'Low', color: 'bg-neutral-100 text-neutral-700' },
  { value: 'medium', label: 'Medium', color: 'bg-yellow-100 text-yellow-700' },
  { value: 'high', label: 'High', color: 'bg-primary-100 text-primary-700' },
  { value: 'urgent', label: 'Urgent', color: 'bg-red-100 text-red-700' },
];

export const TaskModal: React.FC<TaskModalProps> = ({
  isOpen,
  onClose,
  onSave,
  task,
  defaultStatus = 'todo',
}) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: defaultStatus,
    assigneeId: '',
    dueDate: '',
    priority: 'medium' as Priority,
    tags: [] as string[],
  });
  const [tagInput, setTagInput] = useState('');
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title,
        description: task.description,
        status: task.status,
        assigneeId: task.assignee.id,
        dueDate: task.dueDate ? task.dueDate.toISOString().split('T')[0] : '',
        priority: task.priority,
        tags: [...task.tags],
      });
    } else {
      setFormData({
        title: '',
        description: '',
        status: defaultStatus,
        assigneeId: '',
        dueDate: '',
        priority: 'medium',
        tags: [],
      });
    }
    setErrors({});
  }, [task, defaultStatus, isOpen]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }

    if (!formData.assigneeId) {
      newErrors.assigneeId = 'Assignee is required';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      const assignee = mockTeamMembers.find(member => member.id === formData.assigneeId);
      if (!assignee) throw new Error('Assignee not found');

      const taskData: Partial<Task> = {
        title: formData.title.trim(),
        description: formData.description.trim(),
        status: formData.status,
        assignee,
        dueDate: formData.dueDate ? new Date(formData.dueDate) : undefined,
        priority: formData.priority,
        tags: formData.tags,
      };

      await onSave(taskData);
    } catch (error) {
      console.error('Error saving task:', error);
      setErrors({ submit: 'Failed to save task. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const addTag = () => {
    const tag = tagInput.trim();
    if (tag && !formData.tags.includes(tag)) {
      setFormData(prev => ({
        ...prev,
        tags: [...prev.tags, tag],
      }));
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setFormData(prev => ({
      ...prev,
      tags: prev.tags.filter(tag => tag !== tagToRemove),
    }));
  };

  const handleTagInputKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addTag();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface-light dark:bg-card-dark rounded-2xl shadow-large dark:shadow-large-dark w-full max-w-2xl max-h-[90vh] overflow-y-auto border border-neutral-200 dark:border-neutral-700">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-neutral-200 dark:border-neutral-700">
          <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100">
            {task ? 'Edit Task' : 'Create New Task'}
          </h2>
          <button
            onClick={onClose}
            className="p-2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-xl transition-all duration-200"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Error Message */}
          {errors.submit && (
            <div className="flex items-center space-x-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
              <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
              <span className="text-sm text-red-700 dark:text-red-400">{errors.submit}</span>
            </div>
          )}

          {/* Title */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              Task Title *
            </label>
            <input
              type="text"
              value={formData.title}
              onChange={(e) => setFormData(prev => ({ ...prev, title: e.target.value }))}
              className={clsx(
                'w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100 placeholder-neutral-500 dark:placeholder-neutral-400 focus:ring-2 focus:ring-primary-500 transition-all duration-200',
                errors.title && 'ring-2 ring-red-500'
              )}
              placeholder="Enter task title..."
            />
            {errors.title && (
              <p className="text-sm text-red-600 dark:text-red-400 mt-1">{errors.title}</p>
            )}
          </div>

          {/* Description */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              Description
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData(prev => ({ ...prev, description: e.target.value }))}
              rows={3}
              className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100 placeholder-neutral-500 dark:placeholder-neutral-400 focus:ring-2 focus:ring-primary-500 transition-all duration-200 resize-none"
              placeholder="Enter task description..."
            />
          </div>

          {/* Status and Priority */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                Status
              </label>
              <select
                value={formData.status}
                onChange={(e) => setFormData(prev => ({ ...prev, status: e.target.value as TaskStatus }))}
                className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 transition-all duration-200"
              >
                {statusOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                Priority
              </label>
              <select
                value={formData.priority}
                onChange={(e) => setFormData(prev => ({ ...prev, priority: e.target.value as Priority }))}
                className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 transition-all duration-200"
              >
                {priorityOptions.map(option => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>

          {/* Assignee and Due Date */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                Assignee *
              </label>
              <select
                value={formData.assigneeId}
                onChange={(e) => setFormData(prev => ({ ...prev, assigneeId: e.target.value }))}
                className={clsx(
                  'w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 transition-all duration-200',
                  errors.assigneeId && 'ring-2 ring-red-500'
                )}
              >
                <option value="">Select assignee...</option>
                {mockTeamMembers.filter(member => member.active).map(member => (
                  <option key={member.id} value={member.id}>
                    {member.name} ({member.role})
                  </option>
                ))}
              </select>
              {errors.assigneeId && (
                <p className="text-sm text-red-600 dark:text-red-400 mt-1">{errors.assigneeId}</p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                Due Date
              </label>
              <input
                type="date"
                value={formData.dueDate}
                onChange={(e) => setFormData(prev => ({ ...prev, dueDate: e.target.value }))}
                className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 transition-all duration-200"
              />
            </div>
          </div>

          {/* Tags */}
          <div>
            <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
              Tags
            </label>
            <div className="flex space-x-2 mb-3">
              <input
                type="text"
                value={tagInput}
                onChange={(e) => setTagInput(e.target.value)}
                onKeyPress={handleTagInputKeyPress}
                className="flex-1 px-4 py-2 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-lg text-neutral-900 dark:text-neutral-100 placeholder-neutral-500 dark:placeholder-neutral-400 focus:ring-2 focus:ring-primary-500 transition-all duration-200"
                placeholder="Add a tag..."
              />
              <button
                type="button"
                onClick={addTag}
                className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
              >
                <Tag className="h-4 w-4" />
              </button>
            </div>
            {formData.tags.length > 0 && (
              <div className="flex flex-wrap gap-2">
                {formData.tags.map((tag) => (
                  <span
                    key={tag}
                    className="inline-flex items-center space-x-2 px-3 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded-lg text-sm"
                  >
                    <span>{tag}</span>
                    <button
                      type="button"
                      onClick={() => removeTag(tag)}
                      className="text-primary-500 hover:text-primary-700 dark:hover:text-primary-300"
                    >
                      <X className="h-3 w-3" />
                    </button>
                  </span>
                ))}
              </div>
            )}
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-4 pt-4 border-t border-neutral-200 dark:border-neutral-700">
            <button
              type="button"
              onClick={onClose}
              className="px-6 py-3 text-neutral-700 dark:text-neutral-300 bg-neutral-100 dark:bg-neutral-800 hover:bg-neutral-200 dark:hover:bg-neutral-700 rounded-xl transition-all duration-200 font-medium"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="px-6 py-3 bg-primary-500 text-white hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl transition-all duration-200 flex items-center space-x-2 shadow-medium font-medium"
            >
              <Save className="h-4 w-4" />
              <span>{isLoading ? 'Saving...' : task ? 'Update Task' : 'Create Task'}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};