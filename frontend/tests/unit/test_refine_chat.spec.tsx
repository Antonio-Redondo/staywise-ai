import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import '@testing-library/jest-dom'
import { vi } from 'vitest'
import RefineChat from '../../src/app/components/refine-chat'

describe('RefineChat', () => {
  test('renders suggestion buttons and custom input', async () => {
    const onRefine = vi.fn()
    render(<RefineChat onRefine={onRefine} />)

    expect(screen.getByText('Cheaper')).toBeInTheDocument()
    expect(screen.getByPlaceholderText('e.g. more sunlight, quieter street')).toBeInTheDocument()

    await userEvent.click(screen.getByText('Cheaper'))
    expect(onRefine).toHaveBeenCalledWith('Show me cheaper options')

    await userEvent.type(screen.getByPlaceholderText('e.g. more sunlight, quieter street'), 'more space')
    await userEvent.click(screen.getByRole('button', { name: /apply/i }))
    expect(onRefine).toHaveBeenCalledWith('more space')
  })
})
