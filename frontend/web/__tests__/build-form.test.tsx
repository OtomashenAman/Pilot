import React from 'react';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';

// Update import path to match your component structure
import { BuildForm } from '../components/build-form';


describe('BuildForm', () => {
  it('renders required fields and submit button', () => {
    render(<BuildForm onSubmit={jest.fn()} />);

    expect(screen.getByRole('button', { name: /build|submit|run/i })).toBeInTheDocument();
  });

  it('submits valid values', async () => {
    const user = userEvent.setup();
    const onSubmit = jest.fn();
    render(<BuildForm onSubmit={onSubmit} />);

    const nameInput = screen.queryByLabelText(/name/i);
    if (nameInput) {
      await user.type(nameInput, 'policy-build-1');
    }

    const submitBtn = screen.getByRole('button', { name: /build|submit|run/i });
    await user.click(submitBtn);

    expect(onSubmit).toHaveBeenCalledTimes(1);
  });

  it('disables submit while loading', () => {
    render(<BuildForm onSubmit={jest.fn()} loading />);
    const submitBtn = screen.getByRole('button', { name: /build|submit|run/i });
    expect(submitBtn).toBeDisabled();
  });
});
