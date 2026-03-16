import React from 'react';
import { render, screen } from '@testing-library/react';

// Adjust import path to actual component location
import JobStatusCard from '../src/components/job-status-card';

describe('JobStatusCard', () => {
  it('renders job id and queued status', () => {
    render(<JobStatusCard job={{ id: 'job_123', status: 'queued' }} />);

    expect(screen.getByText(/job_123/i)).toBeInTheDocument();
    expect(screen.getByText(/queued/i)).toBeInTheDocument();
  });

  it('renders running status indicator', () => {
    render(<JobStatusCard job={{ id: 'job_456', status: 'running' }} />);
    expect(screen.getByText(/running/i)).toBeInTheDocument();
  });

  it('renders terminal success status', () => {
    render(<JobStatusCard job={{ id: 'job_789', status: 'completed' }} />);
    expect(screen.getByText(/completed|success/i)).toBeInTheDocument();
  });

  it('renders terminal failure status', () => {
    render(<JobStatusCard job={{ id: 'job_999', status: 'failed', error: 'Rule evaluation failed' }} />);
    expect(screen.getByText(/failed/i)).toBeInTheDocument();
    expect(screen.getByText(/rule evaluation failed/i)).toBeInTheDocument();
  });
});
