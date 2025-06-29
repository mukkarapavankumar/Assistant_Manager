import React, { useState } from 'react';
import { Send, Bot, User, Loader2, Mic } from 'lucide-react';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'agent';
  timestamp: Date;
}

export const QueryInterface: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hey, Need help? 👋\nI\'m your Assistant Manager AI. You can ask me about team status, task progress, or any other workflow-related questions. Just ask me anything!',
      sender: 'agent',
      timestamp: new Date(),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    // Simulate agent response
    setTimeout(() => {
      const agentResponse: Message = {
        id: (Date.now() + 1).toString(),
        content: generateAgentResponse(inputValue),
        sender: 'agent',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, agentResponse]);
      setIsLoading(false);
    }, 1500);
  };

  const generateAgentResponse = (query: string): string => {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('sarah') || lowerQuery.includes('authentication')) {
      return 'Sarah Chen is currently working on the User Authentication API. The task is in progress with a due date of Jan 25th. She has a 95% response rate and last updated us on Jan 20th at 10:30 AM. The task involves implementing JWT-based authentication with refresh tokens.';
    }
    
    if (lowerQuery.includes('mike') || lowerQuery.includes('dashboard')) {
      return 'Mike Rodriguez is working on the Dashboard UI Redesign. The task is currently in review status and was due on Jan 22nd. I haven\'t received a response to the latest update request sent on Jan 20th. Would you like me to send a follow-up reminder?';
    }
    
    if (lowerQuery.includes('overdue') || lowerQuery.includes('delayed')) {
      return 'Currently, there is 1 overdue task: Dashboard UI Redesign assigned to Mike Rodriguez (due Jan 22nd). The CI/CD Pipeline Setup task assigned to Lisa Thompson is at risk of being delayed as she\'s currently inactive. Would you like me to escalate these issues?';
    }
    
    if (lowerQuery.includes('team') || lowerQuery.includes('status')) {
      return 'Team Status Summary:\n• 4/5 members are active\n• 1 task completed this week\n• 2 tasks in progress\n• 1 task in review\n• 1 task blocked\n• Overall response rate: 91%\n• Average response time: 2.4 hours';
    }
    
    return 'I understand you\'re asking about team workflow. Based on current data, I can provide information about task status, team member progress, deadlines, and communication patterns. Could you be more specific about what you\'d like to know?';
  };

  return (
    <div className="p-8 h-full flex flex-col bg-background-light dark:bg-background-dark">
      <div className="mb-8">
        <h2 className="text-3xl font-bold text-neutral-900 dark:text-neutral-100 mb-2">Query Agent</h2>
        <p className="text-neutral-600 dark:text-neutral-400">Ask questions about team status, tasks, and workflow progress</p>
      </div>

      <div className="flex-1 bg-surface-light dark:bg-card-dark rounded-2xl border border-neutral-200 dark:border-neutral-700 shadow-soft dark:shadow-soft-dark flex flex-col">
        <div className="flex-1 p-8 overflow-y-auto space-y-6">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex items-start space-x-4 ${
                message.sender === 'user' ? 'flex-row-reverse space-x-reverse' : ''
              }`}
            >
              <div className={`p-3 rounded-2xl ${
                message.sender === 'agent' 
                  ? 'bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400' 
                  : 'bg-neutral-100 dark:bg-neutral-800 text-neutral-600 dark:text-neutral-400'
              }`}>
                {message.sender === 'agent' ? (
                  <Bot className="h-5 w-5" />
                ) : (
                  <User className="h-5 w-5" />
                )}
              </div>
              
              <div className={`max-w-2xl p-6 rounded-2xl ${
                message.sender === 'user'
                  ? 'bg-primary-500 text-white shadow-medium'
                  : 'bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100'
              }`}>
                <p className="whitespace-pre-line leading-relaxed">{message.content}</p>
                <p className={`text-xs mt-3 ${
                  message.sender === 'user' ? 'text-primary-200' : 'text-neutral-500 dark:text-neutral-400'
                }`}>
                  {message.timestamp.toLocaleTimeString()}
                </p>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex items-start space-x-4">
              <div className="p-3 rounded-2xl bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400">
                <Bot className="h-5 w-5" />
              </div>
              <div className="bg-neutral-100 dark:bg-neutral-800 text-neutral-900 dark:text-neutral-100 p-6 rounded-2xl">
                <div className="flex items-center space-x-3">
                  <Loader2 className="h-4 w-4 animate-spin" />
                  <span>Agent is thinking...</span>
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="p-8 border-t border-neutral-200 dark:border-neutral-700">
          <div className="flex space-x-4">
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              placeholder="Ask about team status, task progress, deadlines..."
              className="flex-1 px-6 py-4 bg-neutral-100 dark:bg-neutral-800 border-0 rounded-2xl text-neutral-900 dark:text-neutral-100 placeholder-neutral-500 dark:placeholder-neutral-400 focus:ring-2 focus:ring-primary-500 focus:bg-white dark:focus:bg-neutral-700 transition-all duration-200"
              disabled={isLoading}
            />
            <button className="p-4 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-300 hover:bg-neutral-100 dark:hover:bg-neutral-800 rounded-2xl transition-all duration-200">
              <Mic className="h-5 w-5" />
            </button>
            <button
              onClick={handleSendMessage}
              disabled={!inputValue.trim() || isLoading}
              className="px-6 py-4 bg-primary-500 text-white rounded-2xl hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-medium font-medium"
            >
              <Send className="h-5 w-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};