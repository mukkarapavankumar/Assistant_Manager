import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { EmailCenter } from '../../components/Email/EmailCenter';
import { emailApi } from '../../services/api';

// Mock the API
jest.mock('../../services/api', () => ({
  emailApi: {
    getTemplates: jest.fn(),
    getThreads: jest.fn(),
    getStatistics: jest.fn(),
    sendUpdates: jest.fn(),
    createTemplate: jest.fn(),
    updateTemplate: jest.fn(),
    deleteTemplate: jest.fn(),
    duplicateTemplate: jest.fn(),
    checkResponses: jest.fn(),
  },
}));

const mockTemplates = [
  {
    id: 1,
    name: 'Weekly Update',
    subject: 'Weekly Update - {{date}}',
    content: 'Hello {{name}}, please provide your update.',
    template_type: 'update_request',
    variables: ['name', 'date'],
    active: true,
    usage_count: 5,
    created_at: '2024-01-01T00:00:00Z',
    updated_at: '2024-01-01T00:00:00Z',
  },
];

const mockStatistics = {
  total_threads: 10,
  responded_threads: 8,
  pending_threads: 2,
  response_rate: 80,
  recent_activity: {
    emails_sent_week: 5,
    responses_received_week: 4,
  },
  template_usage: {
    'Weekly Update': 5,
  },
};

describe('EmailCenter', () => {
  beforeEach(() => {
    (emailApi.getTemplates as jest.Mock).mockResolvedValue(mockTemplates);
    (emailApi.getThreads as jest.Mock).mockResolvedValue([]);
    (emailApi.getStatistics as jest.Mock).mockResolvedValue({ data: mockStatistics });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  it('renders email center with tabs', async () => {
    render(<EmailCenter />);
    
    expect(screen.getByText('Email Center')).toBeInTheDocument();
    expect(screen.getByText('Overview')).toBeInTheDocument();
    expect(screen.getByText('Templates')).toBeInTheDocument();
    expect(screen.getByText('Email Threads')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
  });

  it('loads and displays templates', async () => {
    render(<EmailCenter />);
    
    // Switch to templates tab
    fireEvent.click(screen.getByText('Templates'));
    
    await waitFor(() => {
      expect(screen.getByText('Weekly Update')).toBeInTheDocument();
    });
    
    expect(emailApi.getTemplates).toHaveBeenCalled();
  });

  it('displays statistics on overview tab', async () => {
    render(<EmailCenter />);
    
    await waitFor(() => {
      expect(screen.getByText('10')).toBeInTheDocument(); // total_threads
      expect(screen.getByText('80%')).toBeInTheDocument(); // response_rate
    });
    
    expect(emailApi.getStatistics).toHaveBeenCalled();
  });

  it('handles sending emails', async () => {
    (emailApi.sendUpdates as jest.Mock).mockResolvedValue({
      success: true,
      data: { recipient_count: 3 },
    });
    
    render(<EmailCenter />);
    
    const sendButton = screen.getByText('Send Update Requests');
    fireEvent.click(sendButton);
    
    await waitFor(() => {
      expect(emailApi.sendUpdates).toHaveBeenCalled();
    });
  });

  it('opens template modal when create button is clicked', async () => {
    render(<EmailCenter />);
    
    // Switch to templates tab
    fireEvent.click(screen.getByText('Templates'));
    
    await waitFor(() => {
      const createButton = screen.getByText('New Template');
      fireEvent.click(createButton);
    });
    
    // Modal should open (we'd need to check for modal content)
    // This would require the modal to be rendered in the test
  });

  it('filters templates by search term', async () => {
    render(<EmailCenter />);
    
    // Switch to templates tab
    fireEvent.click(screen.getByText('Templates'));
    
    await waitFor(() => {
      const searchInput = screen.getByPlaceholderText('Search templates...');
      fireEvent.change(searchInput, { target: { value: 'Weekly' } });
    });
    
    expect(screen.getByText('Weekly Update')).toBeInTheDocument();
  });

  it('handles template deletion', async () => {
    (emailApi.deleteTemplate as jest.Mock).mockResolvedValue({ success: true });
    
    // Mock window.confirm
    window.confirm = jest.fn(() => true);
    
    render(<EmailCenter />);
    
    // Switch to templates tab
    fireEvent.click(screen.getByText('Templates'));
    
    await waitFor(() => {
      const deleteButton = screen.getByTitle('Delete template');
      fireEvent.click(deleteButton);
    });
    
    expect(window.confirm).toHaveBeenCalled();
    expect(emailApi.deleteTemplate).toHaveBeenCalledWith(1);
  });

  it('handles template duplication', async () => {
    (emailApi.duplicateTemplate as jest.Mock).mockResolvedValue({ success: true });
    
    render(<EmailCenter />);
    
    // Switch to templates tab
    fireEvent.click(screen.getByText('Templates'));
    
    await waitFor(() => {
      const duplicateButton = screen.getByTitle('Duplicate template');
      fireEvent.click(duplicateButton);
    });
    
    expect(emailApi.duplicateTemplate).toHaveBeenCalledWith(1);
  });

  it('shows loading state', () => {
    // Make API calls hang
    (emailApi.getTemplates as jest.Mock).mockImplementation(() => new Promise(() => {}));
    (emailApi.getThreads as jest.Mock).mockImplementation(() => new Promise(() => {}));
    (emailApi.getStatistics as jest.Mock).mockImplementation(() => new Promise(() => {}));
    
    render(<EmailCenter />);
    
    expect(screen.getByText('Loading email data...')).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    (emailApi.getTemplates as jest.Mock).mockRejectedValue(new Error('API Error'));
    (emailApi.getThreads as jest.Mock).mockRejectedValue(new Error('API Error'));
    (emailApi.getStatistics as jest.Mock).mockRejectedValue(new Error('API Error'));
    
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    render(<EmailCenter />);
    
    await waitFor(() => {
      // Component should still render even with API errors
      expect(screen.getByText('Email Center')).toBeInTheDocument();
    });
    
    consoleSpy.mockRestore();
  });
});