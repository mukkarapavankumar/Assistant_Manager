/**
 * Enhanced API service for communicating with the backend.
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
    return config;
  },
  (error) => {
    console.error('API Request Error:', error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    console.log(`API Response: ${response.status} ${response.config.url}`);
    return response;
  },
  (error) => {
    console.error('API Response Error:', error.response?.data || error.message);
    return Promise.reject(error);
  }
);

// Agent API
export const agentApi = {
  query: async (query: string, context?: any) => {
    const response = await api.post('/agents/query', { query, context });
    return response.data;
  },

  getStatus: async () => {
    const response = await api.get('/agents/status');
    return response.data;
  },

  triggerWorkflow: async (workflowType: string) => {
    const response = await api.post(`/agents/trigger-workflow?workflow_type=${workflowType}`);
    return response.data;
  },

  approveChanges: async (changeIds: number[]) => {
    const response = await api.post('/agents/approve-changes', changeIds);
    return response.data;
  },
};

// Kanban API
export const kanbanApi = {
  getBoard: async () => {
    const response = await api.get('/kanban/board');
    return response.data;
  },

  createTask: async (task: any) => {
    const response = await api.post('/kanban/tasks', task);
    return response.data;
  },

  updateTask: async (taskId: number, updates: any) => {
    const response = await api.put(`/kanban/tasks/${taskId}`, updates);
    return response.data;
  },

  deleteTask: async (taskId: number) => {
    const response = await api.delete(`/kanban/tasks/${taskId}`);
    return response.data;
  },

  getPendingChanges: async () => {
    const response = await api.get('/kanban/pending-changes');
    return response.data;
  },

  approveChanges: async (changeIds: number[]) => {
    const response = await api.post('/kanban/approve-changes', { change_ids: changeIds });
    return response.data;
  },

  getTaskDetails: async (taskId: number) => {
    const response = await api.get(`/kanban/tasks/${taskId}`);
    return response.data;
  },

  searchTasks: async (params: any) => {
    const searchParams = new URLSearchParams();
    Object.keys(params).forEach(key => {
      if (params[key]) searchParams.append(key, params[key]);
    });
    
    const response = await api.get(`/kanban/tasks/search?${searchParams.toString()}`);
    return response.data;
  },
};

// Enhanced Email API
export const emailApi = {
  getThreads: async (teamMemberId?: number, status?: string, limit?: number) => {
    const params = new URLSearchParams();
    if (teamMemberId) params.append('team_member_id', teamMemberId.toString());
    if (status) params.append('status', status);
    if (limit) params.append('limit', limit.toString());
    
    const response = await api.get(`/emails/threads?${params.toString()}`);
    return response.data;
  },

  sendUpdates: async (templateId?: number) => {
    const params = templateId ? `?template_id=${templateId}` : '';
    const response = await api.post(`/emails/send-updates${params}`);
    return response.data;
  },

  searchContacts: async (searchTerm: string, limit?: number) => {
    const params = new URLSearchParams();
    params.append('search_term', searchTerm);
    if (limit) params.append('limit', limit.toString());
    
    const response = await api.get(`/emails/search-contacts?${params.toString()}`);
    return response.data;
  },

  getTeamMembers: async (activeOnly: boolean = true) => {
    const params = new URLSearchParams();
    params.append('active_only', activeOnly.toString());
    
    const response = await api.get(`/emails/team-members?${params.toString()}`);
    return response.data;
  },

  addTeamMember: async (memberData: any) => {
    const response = await api.post('/emails/team-members', memberData);
    return response.data;
  },

  updateTeamMember: async (memberId: number, updates: any) => {
    const response = await api.put(`/emails/team-members/${memberId}`, updates);
    return response.data;
  },

  removeTeamMember: async (memberId: number, permanent: boolean = false) => {
    const params = new URLSearchParams();
    params.append('permanent', permanent.toString());
    
    const response = await api.delete(`/emails/team-members/${memberId}?${params.toString()}`);
    return response.data;
  },

  checkResponses: async () => {
    const response = await api.post('/emails/check-responses');
    return response.data;
  },

  getStatistics: async () => {
    const response = await api.get('/emails/statistics');
    return response.data;
  },

  // Template Management
  getTemplates: async (templateType?: string, activeOnly: boolean = true) => {
    const params = new URLSearchParams();
    if (templateType) params.append('template_type', templateType);
    params.append('active_only', activeOnly.toString());
    
    const response = await api.get(`/emails/templates?${params.toString()}`);
    return response.data;
  },

  createTemplate: async (templateData: any) => {
    const response = await api.post('/emails/templates', templateData);
    return response.data;
  },

  updateTemplate: async (templateId: number, templateData: any) => {
    const response = await api.put(`/emails/templates/${templateId}`, templateData);
    return response.data;
  },

  deleteTemplate: async (templateId: number) => {
    const response = await api.delete(`/emails/templates/${templateId}`);
    return response.data;
  },

  duplicateTemplate: async (templateId: number) => {
    const response = await api.post(`/emails/templates/${templateId}/duplicate`);
    return response.data;
  },

  // Settings
  getEmailSettings: async () => {
    const response = await api.get('/emails/settings');
    return response.data;
  },

  updateEmailSettings: async (settings: any) => {
    const response = await api.put('/emails/settings', settings);
    return response.data;
  },
};

// Reports API
export const reportsApi = {
  getTeamStatus: async () => {
    const response = await api.get('/reports/team-status');
    return response.data;
  },
};

// WebSocket connection for real-time updates
export class WebSocketService {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;

  connect(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    try {
      this.ws = new WebSocket('ws://localhost:8000/ws/agent-updates');

      this.ws.onopen = () => {
        console.log('WebSocket connected');
        this.reconnectAttempts = 0;
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage(data);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };

      this.ws.onclose = () => {
        console.log('WebSocket disconnected');
        this.attemptReconnect(onMessage, onError);
      };

      this.ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        if (onError) {
          onError(error);
        }
      };
    } catch (error) {
      console.error('Error creating WebSocket connection:', error);
      if (onError) {
        onError(error as Event);
      }
    }
  }

  private attemptReconnect(onMessage: (data: any) => void, onError?: (error: Event) => void) {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(`Attempting to reconnect... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
      
      setTimeout(() => {
        this.connect(onMessage, onError);
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('Max reconnection attempts reached');
    }
  }

  send(data: any) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }
}

export default api;