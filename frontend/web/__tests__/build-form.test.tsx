import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Adjust import path to actual component location
import BuildForm from '../src/components/build-form';

describe('BuildForm', () => {
  it('renders required fields', () => {
    render(<BuildForm onSubmit={jest.fn()} />);

    expect(screen.getByLabelText(/rule key/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/version/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /create build/i })).toBeInTheDocument();
  });

  it('shows validation errors for invalid semver', async () => {
    const user = userEvent.setup();
    render(<BuildForm onSubmit={jest.fn()} />);

    await user.type(screen.getByLabelText(/rule key/i), 'onboarding_compliance');
    await user.type(screen.getByLabelText(/version/i), 'v2');
    await user.click(screen.getByRole('button', { name: /create build/i }));

    expect(await screen.findByText(/invalid version|semver/i)).toBeInTheDocument();
  });

  it('submits valid payload', async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn().mockResolvedValue(undefined);
    render(<BuildForm onSubmit={onSubmit} />);

    await user.type(screen.getByLabelText(/rule key/i), 'onboarding_compliance');
    await user.type(screen.getByLabelText(/version/i), '2.1.0');
    await user.click(screen.getByRole('button', { name: /create build/i }));

    await waitFor(() => expect(onSubmit).toHaveBeenCalledTimes(1));
    expect(onSubmit).toHaveBeenCalledWith(
      expect.objectContaining({ rule_key: 'onboarding_compliance', version: '2.1.0' })
    );
  });
});
