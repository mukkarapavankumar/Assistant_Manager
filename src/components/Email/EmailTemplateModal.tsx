import React, { useState, useEffect } from 'react';
import { X, Save, Eye, Code, AlertCircle } from 'lucide-react';
import { clsx } from 'clsx';

interface EmailTemplate {
  id: number;
  name: string;
  subject: string;
  content: string;
  template_type: string;
  variables: string[];
  active: boolean;
  usage_count: number;
  created_at: string;
  updated_at: string;
}

interface EmailTemplateModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSave: (template: any) => Promise<void>;
  template?: EmailTemplate | null;
}

const templateTypes = [
  { value: 'update_request', label: 'Update Request' },
  { value: 'reminder', label: 'Reminder' },
  { value: 'follow_up', label: 'Follow-up' },
];

const commonVariables = [
  'name', 'email', 'role', 'date', 'task_name', 'due_date', 
  'status', 'priority', 'project_name', 'subject'
];

export const EmailTemplateModal: React.FC<EmailTemplateModalProps> = ({
  isOpen,
  onClose,
  onSave,
  template,
}) => {
  const [formData, setFormData] = useState({
    name: '',
    subject: '',
    content: '',
    template_type: 'update_request',
    variables: [] as string[],
    active: true,
  });
  const [previewMode, setPreviewMode] = useState(false);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [newVariable, setNewVariable] = useState('');

  useEffect(() => {
    if (template) {
      setFormData({
        name: template.name,
        subject: template.subject,
        content: template.content,
        template_type: template.template_type,
        variables: [...template.variables],
        active: template.active,
      });
    } else {
      setFormData({
        name: '',
        subject: '',
        content: '',
        template_type: 'update_request',
        variables: [],
        active: true,
      });
    }
    setErrors({});
    setPreviewMode(false);
  }, [template, isOpen]);

  const validateForm = () => {
    const newErrors: Record<string, string> = {};

    if (!formData.name.trim()) {
      newErrors.name = 'Template name is required';
    }

    if (!formData.subject.trim()) {
      newErrors.subject = 'Subject is required';
    }

    if (!formData.content.trim()) {
      newErrors.content = 'Content is required';
    }

    // Check for variables in content that aren't in the variables list
    const contentVariables = formData.content.match(/\{\{(\w+)\}\}/g);
    if (contentVariables) {
      const missingVariables = contentVariables
        .map(v => v.replace(/[{}]/g, ''))
        .filter(v => !formData.variables.includes(v));
      
      if (missingVariables.length > 0) {
        newErrors.variables = `Missing variables: ${missingVariables.join(', ')}`;
      }
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    setIsLoading(true);
    try {
      await onSave(formData);
    } catch (error) {
      console.error('Error saving template:', error);
      setErrors({ submit: 'Failed to save template. Please try again.' });
    } finally {
      setIsLoading(false);
    }
  };

  const addVariable = (variable: string) => {
    if (variable && !formData.variables.includes(variable)) {
      setFormData(prev => ({
        ...prev,
        variables: [...prev.variables, variable],
      }));
    }
  };

  const removeVariable = (variable: string) => {
    setFormData(prev => ({
      ...prev,
      variables: prev.variables.filter(v => v !== variable),
    }));
  };

  const handleAddCustomVariable = () => {
    if (newVariable.trim()) {
      addVariable(newVariable.trim());
      setNewVariable('');
    }
  };

  const renderPreview = () => {
    let previewContent = formData.content;
    let previewSubject = formData.subject;

    // Replace variables with sample data
    const sampleData: Record<string, string> = {
      name: 'John Doe',
      email: 'john.doe@company.com',
      role: 'Senior Developer',
      date: new Date().toLocaleDateString(),
      task_name: 'User Authentication API',
      due_date: 'January 25, 2024',
      status: 'In Progress',
      priority: 'High',
      project_name: 'Web Application Redesign',
      subject: 'Weekly Update Request',
    };

    formData.variables.forEach(variable => {
      const value = sampleData[variable] || `[${variable}]`;
      previewContent = previewContent.replace(new RegExp(`\\{\\{${variable}\\}\\}`, 'g'), value);
      previewSubject = previewSubject.replace(new RegExp(`\\{\\{${variable}\\}\\}`, 'g'), value);
    });

    return (
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
            Subject Preview
          </label>
          <div className="p-3 bg-neutral-100 dark:bg-neutral-800 rounded-lg text-neutral-900 dark:text-neutral-100">
            {previewSubject}
          </div>
        </div>
        
        <div>
          <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
            Content Preview
          </label>
          <div className="p-4 bg-neutral-100 dark:bg-neutral-800 rounded-lg text-neutral-900 dark:text-neutral-100 whitespace-pre-wrap max-h-96 overflow-y-auto">
            {previewContent}
          </div>
        </div>
      </div>
    );
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
      <div className="bg-surface-light dark:bg-card-dark rounded-2xl shadow-large dark:shadow-large-dark w-full max-w-4xl max-h-[90vh] overflow-y-auto border border-neutral-200 dark:border-neutral-700">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-neutral-200 dark:border-neutral-700">
          <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100">
            {template ? 'Edit Email Template' : 'Create Email Template'}
          </h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setPreviewMode(!previewMode)}
              className={clsx(
                'flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200',
                previewMode
                  ? 'bg-primary-500 text-white'
                  : 'bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-700'
              )}
            >
              {previewMode ? <Code className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              <span>{previewMode ? 'Edit' : 'Preview'}</span>
            </button>
            <button
              onClick={onClose}
              className="p-2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-xl transition-all duration-200"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {previewMode ? (
            renderPreview()
          ) : (
            <form onSubmit={handleSubmit} className="space-y-6">
              {/* Error Message */}
              {errors.submit && (
                <div className="flex items-center space-x-3 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-xl">
                  <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400" />
                  <span className="text-sm text-red-700 dark:text-red-400">{errors.submit}</span>
                </div>
              )}

              {/* Basic Information */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                    Template Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => setFormData(prev => ({ ...prev, name: e.target.value }))}
                    className={clsx(
                      'w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100 placeholder-neutral-500 dark:placeholder-neutral-400 focus:ring-2 focus:ring-primary-500 transition-all duration-200',
                      errors.name && 'ring-2 ring-red-500'
                    )}
                    placeholder="Enter template name..."
                  />
                  {errors.name && (
                    <p className="text-sm text-red-600 dark:text-red-400 mt-1">{errors.name}</p>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                    Template Type
                  </label>
                  <select
                    value={formData.template_type}
                    onChange={(e) => setFormData(prev => ({ ...prev, template_type: e.target.value }))}
                    className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 transition-all duration-200"
                  >
                    {templateTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Subject */}
              <div>
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                  Email Subject *
                </label>
                <input
                  type="text"
                  value={formData.subject}
                  onChange={(e) => setFormData(prev => ({ ...prev, subject: e.target.value }))}
                  className={clsx(
                    'w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100 placeholder-neutral-500 dark:placeholder-neutral-400 focus:ring-2 focus:ring-primary-500 transition-all duration-200',
                    errors.subject && 'ring-2 ring-red-500'
                  )}
                  placeholder="Enter email subject..."
                />
                {errors.subject && (
                  <p className="text-sm text-red-600 dark:text-red-400 mt-1">{errors.subject}</p>
                )}
              </div>

              {/* Content */}
              <div>
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                  Email Content *
                </label>
                <textarea
                  value={formData.content}
                  onChange={(e) => setFormData(prev => ({ ...prev, content: e.target.value }))}
                  rows={12}
                  className={clsx(
                    'w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100 placeholder-neutral-500 dark:placeholder-neutral-400 focus:ring-2 focus:ring-primary-500 transition-all duration-200 resize-none font-mono text-sm',
                    errors.content && 'ring-2 ring-red-500'
                  )}
                  placeholder="Enter email content... Use {{variable}} for dynamic content."
                />
                {errors.content && (
                  <p className="text-sm text-red-600 dark:text-red-400 mt-1">{errors.content}</p>
                )}
              </div>

              {/* Variables */}
              <div>
                <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-2">
                  Template Variables
                </label>
                
                {/* Common Variables */}
                <div className="mb-3">
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mb-2">Common variables:</p>
                  <div className="flex flex-wrap gap-2">
                    {commonVariables.map(variable => (
                      <button
                        key={variable}
                        type="button"
                        onClick={() => addVariable(variable)}
                        disabled={formData.variables.includes(variable)}
                        className="px-2 py-1 text-xs bg-neutral-200 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300 rounded hover:bg-neutral-300 dark:hover:bg-neutral-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                      >
                        {variable}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Custom Variable Input */}
                <div className="flex space-x-2 mb-3">
                  <input
                    type="text"
                    value={newVariable}
                    onChange={(e) => setNewVariable(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), handleAddCustomVariable())}
                    placeholder="Add custom variable..."
                    className="flex-1 px-3 py-2 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-lg text-neutral-900 dark:text-neutral-100 placeholder-neutral-500 dark:placeholder-neutral-400 focus:ring-2 focus:ring-primary-500 transition-all duration-200 text-sm"
                  />
                  <button
                    type="button"
                    onClick={handleAddCustomVariable}
                    className="px-3 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors text-sm"
                  >
                    Add
                  </button>
                </div>

                {/* Selected Variables */}
                {formData.variables.length > 0 && (
                  <div className="flex flex-wrap gap-2">
                    {formData.variables.map(variable => (
                      <span
                        key={variable}
                        className="inline-flex items-center space-x-2 px-3 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 rounded-lg text-sm"
                      >
                        <span>{`{{${variable}}}`}</span>
                        <button
                          type="button"
                          onClick={() => removeVariable(variable)}
                          className="text-primary-500 hover:text-primary-700 dark:hover:text-primary-300"
                        >
                          <X className="h-3 w-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}

                {errors.variables && (
                  <p className="text-sm text-red-600 dark:text-red-400 mt-1">{errors.variables}</p>
                )}
              </div>

              {/* Active Toggle */}
              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="active"
                  checked={formData.active}
                  onChange={(e) => setFormData(prev => ({ ...prev, active: e.target.checked }))}
                  className="h-5 w-5 text-primary-600 focus:ring-primary-500 border-neutral-300 dark:border-neutral-600 rounded"
                />
                <label htmlFor="active" className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                  Template is active and available for use
                </label>
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
                  <span>{isLoading ? 'Saving...' : template ? 'Update Template' : 'Create Template'}</span>
                </button>
              </div>
            </form>
          )}
        </div>
      </div>
    </div>
  );
};