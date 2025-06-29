import React, { useState, useEffect } from 'react';
import { 
  Mail, 
  Send, 
  Users, 
  FileText, 
  Settings, 
  Plus, 
  Search,
  Filter,
  RefreshCw,
  Clock,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  Edit2,
  Trash2,
  Copy,
  Eye,
  EyeOff
} from 'lucide-react';
import { EmailTemplateModal } from './EmailTemplateModal';
import { EmailThreadsList } from './EmailThreadsList';
import { EmailStatistics } from './EmailStatistics';
import { emailApi } from '../../services/api';
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

export const EmailCenter: React.FC = () => {
  const [activeTab, setActiveTab] = useState('overview');
  const [templates, setTemplates] = useState<EmailTemplate[]>([]);
  const [threads, setThreads] = useState<EmailThread[]>([]);
  const [statistics, setStatistics] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showTemplateModal, setShowTemplateModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<EmailTemplate | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');
  const [isSendingEmails, setIsSendingEmails] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      await Promise.all([
        fetchTemplates(),
        fetchThreads(),
        fetchStatistics()
      ]);
    } catch (error) {
      console.error('Error fetching email data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchTemplates = async () => {
    try {
      const response = await emailApi.getTemplates();
      setTemplates(response);
    } catch (error) {
      console.error('Error fetching templates:', error);
    }
  };

  const fetchThreads = async () => {
    try {
      const response = await emailApi.getThreads();
      setThreads(response);
    } catch (error) {
      console.error('Error fetching threads:', error);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await emailApi.getStatistics();
      setStatistics(response.data);
    } catch (error) {
      console.error('Error fetching statistics:', error);
    }
  };

  const handleSendEmails = async (templateId?: number) => {
    try {
      setIsSendingEmails(true);
      const response = await emailApi.sendUpdates(templateId);
      
      if (response.success) {
        // Refresh data after sending
        await fetchData();
        alert(`Successfully sent emails to ${response.data.recipient_count} team members`);
      } else {
        alert('Failed to send emails: ' + response.message);
      }
    } catch (error) {
      console.error('Error sending emails:', error);
      alert('Error sending emails. Please try again.');
    } finally {
      setIsSendingEmails(false);
    }
  };

  const handleCreateTemplate = () => {
    setEditingTemplate(null);
    setShowTemplateModal(true);
  };

  const handleEditTemplate = (template: EmailTemplate) => {
    setEditingTemplate(template);
    setShowTemplateModal(true);
  };

  const handleDeleteTemplate = async (templateId: number) => {
    if (!confirm('Are you sure you want to delete this template?')) return;
    
    try {
      await emailApi.deleteTemplate(templateId);
      await fetchTemplates();
    } catch (error) {
      console.error('Error deleting template:', error);
      alert('Error deleting template. Please try again.');
    }
  };

  const handleDuplicateTemplate = async (templateId: number) => {
    try {
      await emailApi.duplicateTemplate(templateId);
      await fetchTemplates();
    } catch (error) {
      console.error('Error duplicating template:', error);
      alert('Error duplicating template. Please try again.');
    }
  };

  const handleToggleTemplate = async (templateId: number, active: boolean) => {
    try {
      await emailApi.updateTemplate(templateId, { active: !active });
      await fetchTemplates();
    } catch (error) {
      console.error('Error toggling template:', error);
      alert('Error updating template. Please try again.');
    }
  };

  const handleSaveTemplate = async (templateData: any) => {
    try {
      if (editingTemplate) {
        await emailApi.updateTemplate(editingTemplate.id, templateData);
      } else {
        await emailApi.createTemplate(templateData);
      }
      
      setShowTemplateModal(false);
      setEditingTemplate(null);
      await fetchTemplates();
    } catch (error) {
      console.error('Error saving template:', error);
      throw error;
    }
  };

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         template.subject.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || 
                         (filterStatus === 'active' && template.active) ||
                         (filterStatus === 'inactive' && !template.active);
    return matchesSearch && matchesFilter;
  });

  const renderOverview = () => (
    <div className="space-y-8">
      {/* Statistics Cards */}
      {statistics && <EmailStatistics statistics={statistics} />}

      {/* Quick Actions */}
      <div className="bg-surface-light dark:bg-card-dark rounded-2xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark p-8">
        <h3 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100 mb-6">Quick Actions</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button
            onClick={() => handleSendEmails()}
            disabled={isSendingEmails}
            className="flex items-center space-x-3 p-6 bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800 rounded-xl hover:bg-primary-100 dark:hover:bg-primary-900/30 transition-all duration-200 disabled:opacity-50"
          >
            <Send className="h-6 w-6 text-primary-600 dark:text-primary-400" />
            <div className="text-left">
              <div className="font-medium text-primary-900 dark:text-primary-100">
                {isSendingEmails ? 'Sending...' : 'Send Update Requests'}
              </div>
              <div className="text-sm text-primary-600 dark:text-primary-400">
                Send to all active team members
              </div>
            </div>
          </button>

          <button
            onClick={() => emailApi.checkResponses()}
            className="flex items-center space-x-3 p-6 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-xl hover:bg-green-100 dark:hover:bg-green-900/30 transition-all duration-200"
          >
            <RefreshCw className="h-6 w-6 text-green-600 dark:text-green-400" />
            <div className="text-left">
              <div className="font-medium text-green-900 dark:text-green-100">Check Responses</div>
              <div className="text-sm text-green-600 dark:text-green-400">
                Scan for new email replies
              </div>
            </div>
          </button>

          <button
            onClick={handleCreateTemplate}
            className="flex items-center space-x-3 p-6 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-xl hover:bg-yellow-100 dark:hover:bg-yellow-900/30 transition-all duration-200"
          >
            <Plus className="h-6 w-6 text-yellow-600 dark:text-yellow-400" />
            <div className="text-left">
              <div className="font-medium text-yellow-900 dark:text-yellow-100">Create Template</div>
              <div className="text-sm text-yellow-600 dark:text-yellow-400">
                Add new email template
              </div>
            </div>
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-surface-light dark:bg-card-dark rounded-2xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark p-8">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100">Recent Email Activity</h3>
          <button
            onClick={() => setActiveTab('threads')}
            className="text-sm text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium"
          >
            View All →
          </button>
        </div>
        
        <EmailThreadsList threads={threads.slice(0, 5)} compact />
      </div>
    </div>
  );

  const renderTemplates = () => (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100">Email Templates</h3>
          <p className="text-neutral-600 dark:text-neutral-400 mt-1">
            Manage and customize email templates for automated communications
          </p>
        </div>
        <button
          onClick={handleCreateTemplate}
          className="flex items-center space-x-2 px-4 py-2.5 bg-primary-500 text-white rounded-xl hover:bg-primary-600 transition-all duration-200 font-medium shadow-medium"
        >
          <Plus className="h-4 w-4" />
          <span>New Template</span>
        </button>
      </div>

      {/* Search and Filter */}
      <div className="flex space-x-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-neutral-400" />
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search templates..."
            className="w-full pl-10 pr-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100 placeholder-neutral-500 dark:placeholder-neutral-400 focus:ring-2 focus:ring-primary-500 transition-all duration-200"
          />
        </div>
        <select
          value={filterStatus}
          onChange={(e) => setFilterStatus(e.target.value)}
          className="px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 transition-all duration-200"
        >
          <option value="all">All Templates</option>
          <option value="active">Active Only</option>
          <option value="inactive">Inactive Only</option>
        </select>
      </div>

      {/* Templates Grid */}
      <div className="grid gap-6">
        {filteredTemplates.map((template) => (
          <div
            key={template.id}
            className="bg-surface-light dark:bg-card-dark rounded-2xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark p-6"
          >
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center space-x-3 mb-3">
                  <h4 className="text-lg font-semibold text-neutral-900 dark:text-neutral-100">
                    {template.name}
                  </h4>
                  <span className={clsx(
                    'px-2 py-1 text-xs font-medium rounded-lg',
                    template.active
                      ? 'bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400'
                      : 'bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400'
                  )}>
                    {template.active ? 'Active' : 'Inactive'}
                  </span>
                  <span className="px-2 py-1 bg-primary-100 dark:bg-primary-900/30 text-primary-700 dark:text-primary-400 text-xs font-medium rounded-lg">
                    {template.template_type.replace('_', ' ')}
                  </span>
                </div>
                
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-2">
                  <strong>Subject:</strong> {template.subject}
                </p>
                
                <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4 line-clamp-2">
                  {template.content.substring(0, 150)}...
                </p>
                
                <div className="flex items-center space-x-4 text-xs text-neutral-500 dark:text-neutral-400">
                  <span>Used {template.usage_count} times</span>
                  <span>•</span>
                  <span>Variables: {Array.isArray(template.variables) ? template.variables.join(', ') : 'None'}</span>
                  <span>•</span>
                  <span>Updated {new Date(template.updated_at).toLocaleDateString()}</span>
                </div>
              </div>
              
              <div className="flex items-center space-x-2 ml-4">
                <button
                  onClick={() => handleToggleTemplate(template.id, template.active)}
                  className="p-2 text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-all duration-200"
                  title={template.active ? 'Deactivate template' : 'Activate template'}
                >
                  {template.active ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </button>
                
                <button
                  onClick={() => handleDuplicateTemplate(template.id)}
                  className="p-2 text-neutral-500 hover:text-neutral-700 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-lg transition-all duration-200"
                  title="Duplicate template"
                >
                  <Copy className="h-4 w-4" />
                </button>
                
                <button
                  onClick={() => handleEditTemplate(template)}
                  className="p-2 text-primary-600 hover:text-primary-700 hover:bg-primary-100 dark:hover:bg-primary-900/30 rounded-lg transition-all duration-200"
                  title="Edit template"
                >
                  <Edit2 className="h-4 w-4" />
                </button>
                
                <button
                  onClick={() => handleDeleteTemplate(template.id)}
                  className="p-2 text-red-600 hover:text-red-700 hover:bg-red-100 dark:hover:bg-red-900/30 rounded-lg transition-all duration-200"
                  title="Delete template"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
                
                <button
                  onClick={() => handleSendEmails(template.id)}
                  disabled={!template.active || isSendingEmails}
                  className="px-3 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 text-sm font-medium"
                  title="Send emails using this template"
                >
                  <Send className="h-4 w-4" />
                </button>
              </div>
            </div>
          </div>
        ))}
        
        {filteredTemplates.length === 0 && (
          <div className="text-center py-12">
            <FileText className="h-12 w-12 text-neutral-400 mx-auto mb-4" />
            <h4 className="text-lg font-medium text-neutral-900 dark:text-neutral-100 mb-2">
              No templates found
            </h4>
            <p className="text-neutral-500 dark:text-neutral-400 mb-4">
              {searchTerm || filterStatus !== 'all' 
                ? 'Try adjusting your search or filter criteria'
                : 'Create your first email template to get started'
              }
            </p>
            {!searchTerm && filterStatus === 'all' && (
              <button
                onClick={handleCreateTemplate}
                className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
              >
                Create Template
              </button>
            )}
          </div>
        )}
      </div>
    </div>
  );

  const tabs = [
    { id: 'overview', label: 'Overview', icon: TrendingUp },
    { id: 'templates', label: 'Templates', icon: FileText },
    { id: 'threads', label: 'Email Threads', icon: Mail },
    { id: 'settings', label: 'Settings', icon: Settings },
  ];

  return (
    <div className="p-8 bg-background-light dark:bg-background-dark min-h-screen">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">Email Center</h2>
        <p className="text-neutral-600 dark:text-neutral-400">
          Manage email automation, templates, and team communication
        </p>
      </div>

      {/* Tab Navigation */}
      <div className="flex space-x-1 mb-8 bg-neutral-100 dark:bg-neutral-800 p-1 rounded-xl">
        {tabs.map((tab) => {
          const Icon = tab.icon;
          return (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={clsx(
                'flex items-center space-x-2 px-4 py-2.5 rounded-lg font-medium transition-all duration-200',
                activeTab === tab.id
                  ? 'bg-white dark:bg-neutral-700 text-primary-600 dark:text-primary-400 shadow-soft'
                  : 'text-neutral-600 dark:text-neutral-400 hover:text-neutral-900 dark:hover:text-neutral-100'
              )}
            >
              <Icon className="h-4 w-4" />
              <span>{tab.label}</span>
            </button>
          );
        })}
      </div>

      {/* Tab Content */}
      <div className="min-h-96">
        {isLoading ? (
          <div className="flex items-center justify-center py-12">
            <RefreshCw className="h-8 w-8 animate-spin text-primary-500 mr-3" />
            <span className="text-neutral-600 dark:text-neutral-400">Loading email data...</span>
          </div>
        ) : (
          <>
            {activeTab === 'overview' && renderOverview()}
            {activeTab === 'templates' && renderTemplates()}
            {activeTab === 'threads' && <EmailThreadsList threads={threads} />}
            {activeTab === 'settings' && (
              <div className="bg-surface-light dark:bg-card-dark rounded-2xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark p-12 text-center">
                <Settings className="h-12 w-12 text-neutral-400 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100 mb-3">
                  Email Settings
                </h3>
                <p className="text-neutral-600 dark:text-neutral-400">
                  Configure email automation settings, schedules, and preferences
                </p>
              </div>
            )}
          </>
        )}
      </div>

      {/* Template Modal */}
      <EmailTemplateModal
        isOpen={showTemplateModal}
        onClose={() => {
          setShowTemplateModal(false);
          setEditingTemplate(null);
        }}
        onSave={handleSaveTemplate}
        template={editingTemplate}
      />
    </div>
  );
};