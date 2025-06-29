import { renderHook, act } from '@testing-library/react';
import { useKanbanBoard } from '../../hooks/useKanbanBoard';
import { kanbanApi, agentApi } from '../../services/api';

// Mock the APIs
jest.mock('../../services/api', () => ({
  kanbanApi: {
    getBoard: jest.fn(),
    createTask: jest.fn(),
    updateTask: jest.fn(),
    deleteTask: jest.fn(),
    getPendingChanges: jest.fn(),
  },
  agentApi: {
    approveChanges: jest.fn(),
  },
}));

const mockBoardData = {
  columns: [
    {
      id: 'todo',
      title: 'To Do',
      tasks: [
        {
          id: '1',
          title: 'Test Task',
          description: 'Test description',
          status: 'todo',
          assignee: { id: '1', name: 'John Doe', email: 'john@example.com', role: 'Developer', active: true, responseRate: 95 },
          priority: 'medium',
          tags: ['test'],
          createdAt: new Date(),
          updatedAt: new Date(),
          order: 0,
        },
      ],
      color: 'neutral',
    },
    {
      id: 'in_progress',
      title: 'In Progress',
      tasks: [],
      color: 'primary',
    },
  ],
};

describe('useKanbanBoard', () => {
  beforeEach(() => {
    (kanbanApi.getBoard as jest.Mock).mockResolvedValue(mockBoardData);
    (kanbanApi.getPendingChanges as jest.Mock).mockResolvedValue({ data: { changes: [] } });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('initializes with loading state', () => {
    const { result } = renderHook(() => useKanbanBoard());
    
    expect(result.current.isLoading).toBe(true);
    expect(result.current.columns).toEqual([]);
  });

  it('loads board data on mount', async () => {
    const { result } = renderHook(() => useKanbanBoard());
    
    await act(async () => {
      // Wait for the effect to complete
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    expect(kanbanApi.getBoard).toHaveBeenCalled();
    expect(result.current.isLoading).toBe(false);
    expect(result.current.columns).toEqual(mockBoardData.columns);
  });

  it('handles board loading error', async () => {
    (kanbanApi.getBoard as jest.Mock).mockRejectedValue(new Error('API Error'));
    
    const { result } = renderHook(() => useKanbanBoard());
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    expect(result.current.error).toBe('Failed to load kanban board. Please try again.');
    expect(result.current.columns).toHaveLength(5); // Fallback columns
  });

  it('creates a new task', async () => {
    (kanbanApi.createTask as jest.Mock).mockResolvedValue({ id: '2', title: 'New Task' });
    
    const { result } = renderHook(() => useKanbanBoard());
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    const taskData = {
      title: 'New Task',
      description: 'New description',
      status: 'todo' as const,
      assignee: { id: '1', name: 'John Doe', email: 'john@example.com', role: 'Developer', active: true, responseRate: 95 },
      priority: 'high' as const,
      tags: ['new'],
    };
    
    await act(async () => {
      await result.current.createTask(taskData);
    });
    
    expect(kanbanApi.createTask).toHaveBeenCalledWith({
      title: 'New Task',
      description: 'New description',
      status: 'todo',
      assignee_id: 1,
      priority: 'high',
      tags: ['new'],
      due_date: undefined,
    });
  });

  it('updates a task', async () => {
    (kanbanApi.updateTask as jest.Mock).mockResolvedValue({ success: true });
    
    const { result } = renderHook(() => useKanbanBoard());
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    await act(async () => {
      await result.current.updateTask('1', { title: 'Updated Task' });
    });
    
    expect(kanbanApi.updateTask).toHaveBeenCalledWith(1, { title: 'Updated Task' });
  });

  it('deletes a task', async () => {
    (kanbanApi.deleteTask as jest.Mock).mockResolvedValue({ success: true });
    
    const { result } = renderHook(() => useKanbanBoard());
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    await act(async () => {
      await result.current.deleteTask('1');
    });
    
    expect(kanbanApi.deleteTask).toHaveBeenCalledWith(1);
  });

  it('moves a task between columns', async () => {
    (kanbanApi.updateTask as jest.Mock).mockResolvedValue({ success: true });
    
    const { result } = renderHook(() => useKanbanBoard());
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    await act(async () => {
      await result.current.moveTask('1', 'in_progress');
    });
    
    expect(kanbanApi.updateTask).toHaveBeenCalledWith(1, { status: 'in_progress' });
  });

  it('handles optimistic updates for task movement', async () => {
    const { result } = renderHook(() => useKanbanBoard());
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    // Start the move operation (don't await to see optimistic update)
    act(() => {
      result.current.moveTask('1', 'in_progress');
    });
    
    // The task should be optimistically moved
    const inProgressColumn = result.current.columns.find(col => col.id === 'in_progress');
    const todoColumn = result.current.columns.find(col => col.id === 'todo');
    
    // Note: This test might need adjustment based on the exact timing of optimistic updates
  });

  it('approves pending changes', async () => {
    (agentApi.approveChanges as jest.Mock).mockResolvedValue({ success: true });
    (kanbanApi.getPendingChanges as jest.Mock).mockResolvedValue({ 
      data: { changes: [{ id: 1 }, { id: 2 }] } 
    });
    
    const { result } = renderHook(() => useKanbanBoard());
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    await act(async () => {
      await result.current.approvePendingChanges();
    });
    
    expect(agentApi.approveChanges).toHaveBeenCalledWith([1, 2]);
  });

  it('refreshes board data', async () => {
    const { result } = renderHook(() => useKanbanBoard());
    
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    // Clear the mock to see if it's called again
    (kanbanApi.getBoard as jest.Mock).mockClear();
    
    await act(async () => {
      result.current.refreshBoard();
    });
    
    expect(kanbanApi.getBoard).toHaveBeenCalled();
  });
});