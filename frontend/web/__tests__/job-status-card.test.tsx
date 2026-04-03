import React from 'react';
import { render, screen } from '@testing-library/react';

// Update import path to match your component structure
import { JobStatusCard } from '../components/job-status-card';


describe('JobStatusCard', () => {
  it('renders job metadata', () => {
    render(
      <JobStatusCard
        job={{ id: 'job_123', status: 'queued', createdAt: '2026-01-01T00:00:00Z' }}
      />,
    );

    expect(screen.getByText(/job_123/i)).toBeInTheDocument();
    expect(screen.getByText(/queued/i)).toBeInTheDocument();
  });

  it('shows success state', () => {
    render(
      <JobStatusCard
        job={{ id: 'job_456', status: 'success', createdAt: '2026-01-01T00:00:00Z' }}
      />,
    );

    expect(screen.getByText(/success/i)).toBeInTheDocument();
  });

  it('shows failed state details when provided', () => {
    render(
      <JobStatusCard
        job={{
          id: 'job_789',
          status: 'failed',
          createdAt: '2026-01-01T00:00:00Z',
          error: 'policy compilation error',
        }}
      />,
    );

    expect(screen.getByText(/failed/i)).toBeInTheDocument();
    expect(screen.getByText(/policy compilation error/i)).toBeInTheDocument();
  });
});
