import React from 'react';
import { 
  LayoutDashboard, 
  Kanban, 
  Mail, 
  Users, 
  BarChart3, 
  MessageSquare,
  Clock,
  Github,
  Calendar,
  ArrowRight
} from 'lucide-react';
import { clsx } from 'clsx';

interface SidebarProps {
  activeTab: string;
  onTabChange: (tab: string) => void;
}

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'kanban', label: 'Kanban Board', icon: Kanban },
  { id: 'emails', label: 'Email Center', icon: Mail },
  { id: 'team', label: 'Team Members', icon: Users },
  { id: 'chat', label: 'Query Agent', icon: MessageSquare },
  { id: 'reports', label: 'Analytics', icon: BarChart3 },
  { id: 'schedule', label: 'Automation', icon: Clock },
  { id: 'github', label: 'GitHub Sync', icon: Github },
];

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, onTabChange }) => {
  return (
    <div className="w-72 bg-surface-light dark:bg-surface-dark border-r border-neutral-200 dark:border-neutral-700 h-full overflow-y-auto">
      {/* Date Section - cleaner design */}
      <div className="p-6 border-b border-neutral-200 dark:border-neutral-700">
        <div className="flex items-center space-x-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-neutral-900 dark:text-neutral-100">19</div>
            <div className="text-sm text-neutral-500 dark:text-neutral-400">
              Tue,<br />December
            </div>
          </div>
          <button className="flex-1 group bg-primary-500 hover:bg-primary-600 text-white px-4 py-3 rounded-xl font-medium transition-all duration-200 flex items-center justify-between shadow-soft">
            <span>My Tasks</span>
            <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-0.5" />
          </button>
          <button className="p-3 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-xl transition-all duration-200">
            <Calendar className="h-5 w-5" />
          </button>
        </div>
      </div>

      {/* Navigation - minimal and clean */}
      <nav className="p-6 space-y-1">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              key={item.id}
              onClick={() => onTabChange(item.id)}
              className={clsx(
                'w-full flex items-center space-x-4 px-4 py-3 rounded-xl text-left transition-all duration-200 group',
                activeTab === item.id
                  ? 'bg-primary-500 text-white shadow-soft'
                  : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 hover:text-neutral-900 dark:hover:text-neutral-100'
              )}
            >
              <Icon className={clsx(
                'h-5 w-5 transition-colors duration-200',
                activeTab === item.id 
                  ? 'text-white' 
                  : 'text-neutral-500 dark:text-neutral-500 group-hover:text-neutral-700 dark:group-hover:text-neutral-300'
              )} />
              <span className="font-medium">{item.label}</span>
            </button>
          );
        })}
      </nav>

      {/* Help Section - subtle and minimal */}
      <div className="p-6 mt-auto">
        <div className="bg-neutral-100 dark:bg-neutral-800 p-6 rounded-xl border border-neutral-200 dark:border-neutral-700">
          <div className="text-3xl mb-3">👋</div>
          <h3 className="font-semibold text-neutral-900 dark:text-neutral-100 mb-2">Need help?</h3>
          <p className="text-sm text-neutral-600 dark:text-neutral-400 mb-4">Just ask me anything!</p>
          <button className="w-full bg-primary-500 hover:bg-primary-600 text-white py-2.5 rounded-lg font-medium transition-all duration-200 text-sm">
            Get Help
          </button>
        </div>
      </div>
    </div>
  );
};