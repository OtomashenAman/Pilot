import React from 'react';
import { render, screen } from '@testing-library/react';

// Update import path as needed for actual component location
import JobStatusCard from '../src/components/decisions/JobStatusCard';


describe('JobStatusCard', () => {
  it('renders queued state', () => {
    render(<JobStatusCard job={{ id: 'job_1', status: 'queued' }} /> as any);
    expect(screen.getByText(/queued/i)).toBeInTheDocument();
  });

  it('renders running state with progress', () => {
    render(<JobStatusCard job={{ id: 'job_2', status: 'running', progress: 42 }} /> as any);
    expect(screen.getByText(/running/i)).toBeInTheDocument();
    expect(screen.getByText(/42%|42/i)).toBeInTheDocument();
  });

  it('renders success state', () => {
    render(<JobStatusCard job={{ id: 'job_3', status: 'succeeded' }} /> as any);
    expect(screen.getByText(/succeeded|completed|success/i)).toBeInTheDocument();
  });

  it('renders failed state', () => {
    render(<JobStatusCard job={{ id: 'job_4', status: 'failed', error: 'Sandbox timeout' }} /> as any);
    expect(screen.getByText(/failed/i)).toBeInTheDocument();
    expect(screen.getByText(/sandbox timeout/i)).toBeInTheDocument();
  });
});
