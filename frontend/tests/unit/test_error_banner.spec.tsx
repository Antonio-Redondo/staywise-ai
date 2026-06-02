import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import '@testing-library/jest-dom'
import { vi } from 'vitest'
import ErrorBanner from '../../src/app/components/error-banner'

describe('ErrorBanner', () => {
  test('shows message and calls retry', async () => {
    const onRetry = vi.fn()
    render(<ErrorBanner message="Network error" onRetry={onRetry} />)

    expect(screen.getByText('Network error')).toBeInTheDocument()

    await userEvent.click(screen.getByRole('button', { name: /retry/i }))
    expect(onRetry).toHaveBeenCalled()
  })
})
