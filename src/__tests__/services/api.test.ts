import axios from 'axios';
import { agentApi, kanbanApi, emailApi } from '../../services/api';

// Mock axios
jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

// Mock axios.create
const mockAxiosInstance = {
  get: jest.fn(),
  post: jest.fn(),
  put: jest.fn(),
  delete: jest.fn(),
  interceptors: {
    request: { use: jest.fn() },
    response: { use: jest.fn() },
  },
};

mockedAxios.create.mockReturnValue(mockAxiosInstance as any);

describe('API Services', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('agentApi', () => {
    it('sends query to agent', async () => {
      const mockResponse = { data: { response: 'Agent response', confidence: 0.9 } };
      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      const result = await agentApi.query('Test query', { context: 'test' });

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/agents/query', {
        query: 'Test query',
        context: { context: 'test' },
      });
      expect(result).toEqual(mockResponse.data);
    });

    it('gets agent status', async () => {
      const mockResponse = { data: { is_active: true, current_task: 'idle' } };
      mockAxiosInstance.get.mockResolvedValue(mockResponse);

      const result = await agentApi.getStatus();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/agents/status');
      expect(result).toEqual(mockResponse.data);
    });

    it('triggers workflow', async () => {
      const mockResponse = { data: { success: true, workflow_type: 'weekly_update' } };
      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      const result = await agentApi.triggerWorkflow('weekly_update');

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/agents/trigger-workflow?workflow_type=weekly_update');
      expect(result).toEqual(mockResponse.data);
    });

    it('approves changes', async () => {
      const mockResponse = { data: { success: true } };
      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      const result = await agentApi.approveChanges([1, 2, 3]);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/agents/approve-changes', [1, 2, 3]);
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('kanbanApi', () => {
    it('gets kanban board', async () => {
      const mockResponse = { data: { columns: [] } };
      mockAxiosInstance.get.mockResolvedValue(mockResponse);

      const result = await kanbanApi.getBoard();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/kanban/board');
      expect(result).toEqual(mockResponse.data);
    });

    it('creates task', async () => {
      const mockResponse = { data: { id: 1, title: 'New Task' } };
      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      const taskData = { title: 'New Task', status: 'todo', assignee_id: 1 };
      const result = await kanbanApi.createTask(taskData);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/kanban/tasks', taskData);
      expect(result).toEqual(mockResponse.data);
    });

    it('updates task', async () => {
      const mockResponse = { data: { success: true } };
      mockAxiosInstance.put.mockResolvedValue(mockResponse);

      const updates = { title: 'Updated Task' };
      const result = await kanbanApi.updateTask(1, updates);

      expect(mockAxiosInstance.put).toHaveBeenCalledWith('/kanban/tasks/1', updates);
      expect(result).toEqual(mockResponse.data);
    });

    it('deletes task', async () => {
      const mockResponse = { data: { success: true } };
      mockAxiosInstance.delete.mockResolvedValue(mockResponse);

      const result = await kanbanApi.deleteTask(1);

      expect(mockAxiosInstance.delete).toHaveBeenCalledWith('/kanban/tasks/1');
      expect(result).toEqual(mockResponse.data);
    });

    it('gets pending changes', async () => {
      const mockResponse = { data: { changes: [] } };
      mockAxiosInstance.get.mockResolvedValue(mockResponse);

      const result = await kanbanApi.getPendingChanges();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/kanban/pending-changes');
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('emailApi', () => {
    it('gets email threads', async () => {
      const mockResponse = { data: [] };
      mockAxiosInstance.get.mockResolvedValue(mockResponse);

      const result = await emailApi.getThreads(1, 'sent', 10);

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/emails/threads?team_member_id=1&status=sent&limit=10');
      expect(result).toEqual(mockResponse.data);
    });

    it('sends update emails', async () => {
      const mockResponse = { data: { success: true, recipient_count: 3 } };
      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      const result = await emailApi.sendUpdates(1);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/emails/send-updates?template_id=1');
      expect(result).toEqual(mockResponse.data);
    });

    it('searches contacts', async () => {
      const mockResponse = { data: { contacts: [] } };
      mockAxiosInstance.get.mockResolvedValue(mockResponse);

      const result = await emailApi.searchContacts('john', 20);

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/emails/search-contacts?search_term=john&limit=20');
      expect(result).toEqual(mockResponse.data);
    });

    it('gets team members', async () => {
      const mockResponse = { data: [] };
      mockAxiosInstance.get.mockResolvedValue(mockResponse);

      const result = await emailApi.getTeamMembers(true);

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/emails/team-members?active_only=true');
      expect(result).toEqual(mockResponse.data);
    });

    it('creates email template', async () => {
      const mockResponse = { data: { id: 1, name: 'New Template' } };
      mockAxiosInstance.post.mockResolvedValue(mockResponse);

      const templateData = { name: 'New Template', subject: 'Test', content: 'Test content' };
      const result = await emailApi.createTemplate(templateData);

      expect(mockAxiosInstance.post).toHaveBeenCalledWith('/emails/templates', templateData);
      expect(result).toEqual(mockResponse.data);
    });

    it('gets email statistics', async () => {
      const mockResponse = { data: { total_threads: 10, response_rate: 80 } };
      mockAxiosInstance.get.mockResolvedValue(mockResponse);

      const result = await emailApi.getStatistics();

      expect(mockAxiosInstance.get).toHaveBeenCalledWith('/emails/statistics');
      expect(result).toEqual(mockResponse.data);
    });
  });

  describe('Error Handling', () => {
    it('handles API errors', async () => {
      const error = new Error('Network Error');
      mockAxiosInstance.get.mockRejectedValue(error);

      await expect(agentApi.getStatus()).rejects.toThrow('Network Error');
    });

    it('handles HTTP error responses', async () => {
      const error = {
        response: {
          status: 404,
          data: { detail: 'Not found' },
        },
      };
      mockAxiosInstance.get.mockRejectedValue(error);

      await expect(kanbanApi.getBoard()).rejects.toEqual(error);
    });
  });
});