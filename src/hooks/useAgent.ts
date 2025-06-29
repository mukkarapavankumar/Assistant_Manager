/**
 * React hook for agent communication and state management.
 */

import { useState, useEffect, useCallback } from 'react';
import { agentApi, WebSocketService } from '../services/api';

interface AgentState {
  isActive: boolean;
  currentTask: string;
  nextScheduledAction?: string;
  tasksCompleted: number;
  emailsSent: number;
  responsesReceived: number;
  lastActivity: string;
}

interface AgentResponse {
  response: string;
  confidence: number;
  sources: string[];
  suggestedActions: string[];
}

export const useAgent = () => {
  const [agentState, setAgentState] = useState<AgentState | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [wsService] = useState(() => new WebSocketService());

  // Initialize WebSocket connection
  useEffect(() => {
    const handleMessage = (data: any) => {
      console.log('Received WebSocket message:', data);
      if (data.type === 'agent_status_update') {
        setAgentState(data.status);
      }
    };

    const handleError = (error: Event) => {
      console.error('WebSocket error:', error);
      setIsConnected(false);
      setError('WebSocket connection failed');
    };

    wsService.connect(handleMessage, handleError);
    setIsConnected(true);

    return () => {
      wsService.disconnect();
    };
  }, [wsService]);

  // Fetch initial agent status
  useEffect(() => {
    fetchAgentStatus();
  }, []);

  const fetchAgentStatus = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      const status = await agentApi.getStatus();
      setAgentState(status);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch agent status');
      console.error('Error fetching agent status:', err);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const sendQuery = useCallback(async (query: string, context?: any): Promise<AgentResponse> => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await agentApi.query(query, context);
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to send query';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const triggerWorkflow = useCallback(async (workflowType: string) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await agentApi.triggerWorkflow(workflowType);
      
      // Refresh agent status after triggering workflow
      await fetchAgentStatus();
      
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to trigger workflow';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [fetchAgentStatus]);

  const approveKanbanChanges = useCallback(async (changeIds: number[]) => {
    try {
      setIsLoading(true);
      setError(null);
      const response = await agentApi.approveChanges(changeIds);
      
      // Refresh agent status after approval
      await fetchAgentStatus();
      
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to approve changes';
      setError(errorMessage);
      throw new Error(errorMessage);
    } finally {
      setIsLoading(false);
    }
  }, [fetchAgentStatus]);

  const sendWebSocketMessage = useCallback((data: any) => {
    wsService.send(data);
  }, [wsService]);

  return {
    agentState,
    isConnected,
    isLoading,
    error,
    sendQuery,
    triggerWorkflow,
    approveKanbanChanges,
    fetchAgentStatus,
    sendWebSocketMessage,
    clearError: () => setError(null),
  };
};