import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Update import path as needed for actual component location
import BuildForm from '../src/components/rules/BuildForm';


describe('BuildForm', () => {
  it('renders required fields and submit button', () => {
    render(<BuildForm />);

    expect(screen.getByLabelText(/rule slug/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/semantic version/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create build|submit|build/i })).toBeInTheDocument();
  });

  it('shows validation error for invalid semantic version', async () => {
    const user = userEvent.setup();
    render(<BuildForm />);

    await user.type(screen.getByLabelText(/rule slug/i), 'worker-classification-de');
    await user.type(screen.getByLabelText(/semantic version/i), '1.0');
    await user.click(screen.getByRole('button', { name: /create build|submit|build/i }));

    expect(await screen.findByText(/semantic version|invalid version|must match/i)).toBeInTheDocument();
  });

  it('submits valid payload and shows success', async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn().mockResolvedValue({ id: 'bld_123', status: 'queued' });
    render(<BuildForm onSubmit={onSubmit} /> as any);

    await user.type(screen.getByLabelText(/rule slug/i), 'worker-classification-us');
    await user.type(screen.getByLabelText(/semantic version/i), '1.2.3');
    await user.click(screen.getByRole('button', { name: /create build|submit|build/i }));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalled();
    });
  });
});
