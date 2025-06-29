import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { TaskCard } from '../../components/Kanban/TaskCard';
import { Task } from '../../types';

const mockTask: Task = {
  id: '1',
  title: 'Test Task',
  description: 'Test task description',
  status: 'todo',
  assignee: {
    id: '1',
    name: 'John Doe',
    email: 'john@example.com',
    role: 'Developer',
    active: true,
    responseRate: 95,
  },
  dueDate: new Date('2024-12-31'),
  priority: 'high',
  createdAt: new Date(),
  updatedAt: new Date(),
  tags: ['frontend', 'urgent'],
  order: 0,
};

describe('TaskCard', () => {
  it('renders task information correctly', () => {
    render(<TaskCard task={mockTask} />);
    
    expect(screen.getByText('Test Task')).toBeInTheDocument();
    expect(screen.getByText('Test task description')).toBeInTheDocument();
    expect(screen.getByText('John')).toBeInTheDocument();
    expect(screen.getByText('Dec 31')).toBeInTheDocument();
  });

  it('shows priority indicator', () => {
    render(<TaskCard task={mockTask} />);
    
    const priorityDot = document.querySelector('.bg-primary-500');
    expect(priorityDot).toBeInTheDocument();
  });

  it('displays tags correctly', () => {
    render(<TaskCard task={mockTask} />);
    
    expect(screen.getByText('frontend')).toBeInTheDocument();
    expect(screen.getByText('urgent')).toBeInTheDocument();
  });

  it('calls onEdit when edit button is clicked', () => {
    const onEdit = jest.fn();
    render(<TaskCard task={mockTask} onEdit={onEdit} />);
    
    // Hover to show actions
    const card = screen.getByText('Test Task').closest('div');
    fireEvent.mouseEnter(card!);
    
    const editButton = screen.getByTitle('Edit task');
    fireEvent.click(editButton);
    
    expect(onEdit).toHaveBeenCalledWith(mockTask);
  });

  it('calls onDelete when delete button is clicked', () => {
    const onDelete = jest.fn();
    render(<TaskCard task={mockTask} onDelete={onDelete} />);
    
    // Hover to show actions
    const card = screen.getByText('Test Task').closest('div');
    fireEvent.mouseEnter(card!);
    
    const deleteButton = screen.getByTitle('Delete task');
    fireEvent.click(deleteButton);
    
    expect(onDelete).toHaveBeenCalledWith('1');
  });

  it('shows overdue styling for overdue tasks', () => {
    const overdueTask = {
      ...mockTask,
      dueDate: new Date('2020-01-01'), // Past date
      status: 'in_progress' as const,
    };
    
    render(<TaskCard task={overdueTask} />);
    
    const card = screen.getByText('Test Task').closest('div');
    expect(card).toHaveClass('border-red-300');
  });

  it('shows done status icon for completed tasks', () => {
    const completedTask = {
      ...mockTask,
      status: 'done' as const,
    };
    
    render(<TaskCard task={completedTask} />);
    
    const checkIcon = document.querySelector('.text-green-600');
    expect(checkIcon).toBeInTheDocument();
  });

  it('shows blocked status icon for blocked tasks', () => {
    const blockedTask = {
      ...mockTask,
      status: 'blocked' as const,
    };
    
    render(<TaskCard task={blockedTask} />);
    
    const alertIcon = document.querySelector('.text-red-500');
    expect(alertIcon).toBeInTheDocument();
  });

  it('handles dragging state correctly', () => {
    render(<TaskCard task={mockTask} isDragging={true} />);
    
    const card = screen.getByText('Test Task').closest('div');
    expect(card).toHaveClass('scale-105', 'rotate-1', 'cursor-grabbing');
  });

  it('truncates long tag lists', () => {
    const taskWithManyTags = {
      ...mockTask,
      tags: ['tag1', 'tag2', 'tag3', 'tag4', 'tag5'],
    };
    
    render(<TaskCard task={taskWithManyTags} />);
    
    expect(screen.getByText('tag1')).toBeInTheDocument();
    expect(screen.getByText('tag2')).toBeInTheDocument();
    expect(screen.getByText('+3')).toBeInTheDocument();
  });
});