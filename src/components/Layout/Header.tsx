import React from 'react';
import { Bot, Bell, Settings, User, Sun, Moon, Search } from 'lucide-react';
import { useTheme } from '../../contexts/ThemeContext';

interface HeaderProps {
  onSettingsClick: () => void;
}

export const Header: React.FC<HeaderProps> = ({ onSettingsClick }) => {
  const { theme, toggleTheme } = useTheme();

  return (
    <header className="bg-surface-light dark:bg-surface-dark border-b border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark">
      <div className="flex items-center justify-between px-8 py-4">
        <div className="flex items-center space-x-6">
          <div className="flex items-center space-x-4">
            <div className="p-3 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl shadow-medium">
              <Bot className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100">Assistant Manager</h1>
              <p className="text-sm text-neutral-500 dark:text-neutral-400">Team Workflow Automation</p>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-6">
          {/* Search Bar */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-neutral-400" />
            <input
              type="text"
              placeholder="Start searching here..."
              className="w-80 pl-10 pr-4 py-2.5 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-xl text-sm text-neutral-900 dark:text-neutral-100 placeholder-neutral-500 dark:placeholder-neutral-400 focus:ring-2 focus:ring-primary-500 focus:bg-white dark:focus:bg-neutral-700 transition-all duration-200"
            />
          </div>

          {/* Agent Status */}
          <div className="flex items-center space-x-3 px-4 py-2.5 bg-success-50 dark:bg-success-900/20 border border-success-200 dark:border-success-800 rounded-xl">
            <div className="h-2 w-2 bg-success-500 rounded-full animate-pulse-soft"></div>
            <span className="text-sm font-medium text-success-700 dark:text-success-400">Agent Active</span>
          </div>

          {/* Action Buttons */}
          <div className="flex items-center space-x-2">
            <button 
              onClick={toggleTheme}
              className="p-2.5 text-neutral-500 dark:text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-xl transition-all duration-200"
            >
              {theme === 'light' ? <Moon className="h-5 w-5" /> : <Sun className="h-5 w-5" />}
            </button>

            <button className="relative p-2.5 text-neutral-500 dark:text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-xl transition-all duration-200">
              <Bell className="h-5 w-5" />
              <span className="absolute -top-1 -right-1 h-5 w-5 bg-primary-500 text-white text-xs rounded-full flex items-center justify-center font-medium">
                3
              </span>
            </button>

            <button 
              onClick={onSettingsClick}
              className="p-2.5 text-neutral-500 dark:text-neutral-400 hover:text-neutral-700 dark:hover:text-neutral-200 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-xl transition-all duration-200"
            >
              <Settings className="h-5 w-5" />
            </button>

            <div className="flex items-center space-x-3 pl-4 border-l border-neutral-200 dark:border-neutral-700">
              <div className="h-9 w-9 bg-gradient-to-br from-primary-400 to-primary-600 rounded-xl flex items-center justify-center">
                <User className="h-5 w-5 text-white" />
              </div>
              <div className="hidden md:block">
                <p className="text-sm font-medium text-neutral-900 dark:text-neutral-100">Alex Johnson</p>
                <p className="text-xs text-neutral-500 dark:text-neutral-400">Manager</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};