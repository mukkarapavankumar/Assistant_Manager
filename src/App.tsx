import React, { useState } from 'react';
import { ThemeProvider } from './contexts/ThemeContext';
import { Header } from './components/Layout/Header';
import { Sidebar } from './components/Layout/Sidebar';
import { Dashboard } from './components/Dashboard/Dashboard';
import { KanbanBoard } from './components/Kanban/KanbanBoard';
import { QueryInterface } from './components/Chat/QueryInterface';
import { TeamManagement } from './components/Team/TeamManagement';
import { EmailCenter } from './components/Email/EmailCenter';
import { SettingsModal } from './components/Settings/SettingsModal';

function AppContent() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [showSettings, setShowSettings] = useState(false);

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard />;
      case 'kanban':
        return <KanbanBoard />;
      case 'chat':
        return <QueryInterface />;
      case 'team':
        return <TeamManagement />;
      case 'emails':
        return <EmailCenter />;
      case 'reports':
        return (
          <div className="p-8 bg-background-light dark:bg-background-dark min-h-screen">
            <h2 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">Analytics & Reports</h2>
            <p className="text-neutral-600 dark:text-neutral-400 mb-8">Performance metrics and workflow analytics</p>
            <div className="bg-surface-light dark:bg-card-dark rounded-2xl border border-neutral-200 dark:border-neutral-700 p-12 text-center shadow-soft dark:shadow-soft-dark">
              <div className="text-6xl mb-6">📊</div>
              <h3 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100 mb-3">Analytics Dashboard</h3>
              <p className="text-neutral-600 dark:text-neutral-400">Track team performance, response rates, and workflow efficiency</p>
            </div>
          </div>
        );
      case 'schedule':
        return (
          <div className="p-8 bg-background-light dark:bg-background-dark min-h-screen">
            <h2 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">Automation Schedule</h2>
            <p className="text-neutral-600 dark:text-neutral-400 mb-8">Configure automated workflows and timing</p>
            <div className="bg-surface-light dark:bg-card-dark rounded-2xl border border-neutral-200 dark:border-neutral-700 p-12 text-center shadow-soft dark:shadow-soft-dark">
              <div className="text-6xl mb-6">⏰</div>
              <h3 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100 mb-3">Workflow Automation</h3>
              <p className="text-neutral-600 dark:text-neutral-400">Set up automated email schedules and reminder workflows</p>
            </div>
          </div>
        );
      case 'github':
        return (
          <div className="p-8 bg-background-light dark:bg-background-dark min-h-screen">
            <h2 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">GitHub Synchronization</h2>
            <p className="text-neutral-600 dark:text-neutral-400 mb-8">Manage Kanban board publishing to GitHub Pages</p>
            <div className="bg-surface-light dark:bg-card-dark rounded-2xl border border-neutral-200 dark:border-neutral-700 p-12 text-center shadow-soft dark:shadow-soft-dark">
              <div className="text-6xl mb-6">🔄</div>
              <h3 className="text-xl font-semibold text-neutral-900 dark:text-neutral-100 mb-3">GitHub Integration</h3>
              <p className="text-neutral-600 dark:text-neutral-400">Sync and publish your Kanban board to GitHub Pages</p>
            </div>
          </div>
        );
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="h-screen bg-background-light dark:bg-background-dark flex flex-col">
      <Header onSettingsClick={() => setShowSettings(true)} />
      
      <div className="flex-1 flex overflow-hidden">
        <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
        
        <main className="flex-1 overflow-y-auto">
          {renderContent()}
        </main>
      </div>

      <SettingsModal 
        isOpen={showSettings} 
        onClose={() => setShowSettings(false)} 
      />
    </div>
  );
}

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;