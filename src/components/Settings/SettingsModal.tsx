import React, { useState } from 'react';
import { X, Save, User, Mail, Calendar, Github, Lock } from 'lucide-react';

interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export const SettingsModal: React.FC<SettingsModalProps> = ({ isOpen, onClose }) => {
  const [activeTab, setActiveTab] = useState('general');

  if (!isOpen) return null;

  const tabs = [
    { id: 'general', label: 'General', icon: User },
    { id: 'email', label: 'Email', icon: Mail },
    { id: 'automation', label: 'Automation', icon: Calendar },
    { id: 'github', label: 'GitHub', icon: Github },
    { id: 'security', label: 'Security', icon: Lock },
  ];

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50">
      <div className="bg-surface-light dark:bg-card-dark rounded-3xl shadow-large dark:shadow-large-dark w-full max-w-5xl h-[85vh] flex overflow-hidden border border-neutral-200 dark:border-neutral-700">
        {/* Sidebar */}
        <div className="w-80 bg-neutral-50 dark:bg-neutral-800/50 border-r border-neutral-200 dark:border-neutral-700 p-8">
          <div className="flex items-center justify-between mb-8">
            <h2 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100">Settings</h2>
            <button
              onClick={onClose}
              className="p-2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-700 rounded-xl transition-all duration-200"
            >
              <X className="h-5 w-5" />
            </button>
          </div>

          <nav className="space-y-2">
            {tabs.map((tab) => {
              const Icon = tab.icon;
              return (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={clsx(
                    'w-full flex items-center space-x-4 px-4 py-3.5 rounded-2xl text-left transition-all duration-200',
                    activeTab === tab.id
                      ? 'bg-primary-500 text-white shadow-medium'
                      : 'text-neutral-700 dark:text-neutral-300 hover:bg-neutral-200 dark:hover:bg-neutral-700'
                  )}
                >
                  <Icon className="h-5 w-5" />
                  <span className="font-medium">{tab.label}</span>
                </button>
              );
            })}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 p-8 overflow-y-auto">
          {activeTab === 'general' && (
            <div className="space-y-8">
              <div>
                <h3 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100 mb-6">General Settings</h3>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
                      Organization Name
                    </label>
                    <input
                      type="text"
                      defaultValue="Tech Innovations Inc."
                      className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-2xl text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 transition-all duration-200"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
                      Manager Name
                    </label>
                    <input
                      type="text"
                      defaultValue="Alex Johnson"
                      className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-2xl text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 transition-all duration-200"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
                      Time Zone
                    </label>
                    <select className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-2xl text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 transition-all duration-200">
                      <option>UTC-8 (Pacific Time)</option>
                      <option>UTC-5 (Eastern Time)</option>
                      <option>UTC+0 (UTC)</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'email' && (
            <div className="space-y-8">
              <div>
                <h3 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100 mb-6">Email Configuration</h3>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
                      Outlook Integration
                    </label>
                    <div className="flex items-center space-x-4 p-4 bg-success-50 dark:bg-success-900/20 border border-success-200 dark:border-success-800 rounded-2xl">
                      <div className="h-3 w-3 bg-success-500 rounded-full animate-pulse-soft"></div>
                      <span className="text-sm font-medium text-success-700 dark:text-success-400">Connected to Outlook</span>
                    </div>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
                      Default Email Signature
                    </label>
                    <textarea
                      rows={4}
                      defaultValue="Best regards,&#10;Assistant Manager&#10;Automated Team Workflow System"
                      className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-2xl text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 transition-all duration-200 resize-none"
                    />
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'automation' && (
            <div className="space-y-8">
              <div>
                <h3 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100 mb-6">Automation Settings</h3>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
                      Update Request Frequency
                    </label>
                    <select className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-2xl text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 transition-all duration-200">
                      <option>Weekly (Monday 9:00 AM)</option>
                      <option>Bi-weekly</option>
                      <option>Daily</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
                      Reminder Days Before Deadline
                    </label>
                    <input
                      type="number"
                      defaultValue="2"
                      min="1"
                      max="7"
                      className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-2xl text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 transition-all duration-200"
                    />
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <input
                      type="checkbox"
                      id="autoApprove"
                      defaultChecked={false}
                      className="h-5 w-5 text-primary-600 focus:ring-primary-500 border-neutral-300 dark:border-neutral-600 rounded-lg"
                    />
                    <label htmlFor="autoApprove" className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                      Auto-approve Kanban board changes
                    </label>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'github' && (
            <div className="space-y-8">
              <div>
                <h3 className="text-2xl font-semibold text-neutral-900 dark:text-neutral-100 mb-6">GitHub Integration</h3>
                
                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
                      Repository URL
                    </label>
                    <input
                      type="text"
                      placeholder="https://github.com/username/repo"
                      defaultValue="https://github.com/company/team-kanban"
                      className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-2xl text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 transition-all duration-200"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-3">
                      GitHub Token
                    </label>
                    <input
                      type="password"
                      placeholder="ghp_xxxxxxxxxxxxxxxxxxxx"
                      className="w-full px-4 py-3 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-2xl text-neutral-900 dark:text-neutral-100 focus:ring-2 focus:ring-primary-500 transition-all duration-200"
                    />
                    <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-2">
                      Required for publishing Kanban board to GitHub Pages
                    </p>
                  </div>
                  
                  <div className="flex items-center space-x-4">
                    <input
                      type="checkbox"
                      id="autoPublish"
                      defaultChecked={true}
                      className="h-5 w-5 text-primary-600 focus:ring-primary-500 border-neutral-300 dark:border-neutral-600 rounded-lg"
                    />
                    <label htmlFor="autoPublish" className="text-sm font-medium text-neutral-700 dark:text-neutral-300">
                      Auto-publish approved changes
                    </label>
                  </div>
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-end space-x-4 pt-8 border-t border-neutral-200 dark:border-neutral-700 mt-8">
            <button
              onClick={onClose}
              className="px-6 py-3 text-neutral-700 dark:text-neutral-300 bg-neutral-100 dark:bg-neutral-800 hover:bg-neutral-200 dark:hover:bg-neutral-700 rounded-2xl transition-all duration-200 font-medium"
            >
              Cancel
            </button>
            <button className="px-6 py-3 bg-primary-500 text-white hover:bg-primary-600 rounded-2xl transition-all duration-200 flex items-center space-x-2 shadow-medium font-medium">
              <Save className="h-4 w-4" />
              <span>Save Changes</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};