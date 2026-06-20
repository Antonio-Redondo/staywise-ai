import React from 'react'
import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import '@testing-library/jest-dom'
import { vi } from 'vitest'
import RecommendFlow from '../../src/app/components/recommend-flow'

describe('RecommendFlow', () => {
  beforeEach(() => {
    window.history.replaceState({}, '', '/')
    vi.restoreAllMocks()
  })

  test('creates a session threadId and sends it with the recommendation request', async () => {
    const mockFetch = vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce({
      ok: true,
      json: async () => ({ intent: null, listings: [], scored: [], explained: [] }),
    } as unknown as Response)

    render(<RecommendFlow />)

    const queryInput = screen.getByLabelText('Describe what you want') as HTMLTextAreaElement
    const submitButton = screen.getByRole('button', { name: /find recommendations/i })

    await userEvent.type(queryInput, 'One bedroom in the Mission')
    await userEvent.click(submitButton)

    expect(mockFetch).toHaveBeenCalledTimes(1)
    const requestBody = JSON.parse((mockFetch.mock.calls[0][1] as any).body)
    expect(requestBody.userQuery).toBe('One bedroom in the Mission')
    expect(typeof requestBody.threadId).toBe('string')
    expect(requestBody.threadId.length).toBeGreaterThan(0)
    expect(screen.getByText(/session/i)).toBeInTheDocument()
  })

  test('refinement appends message to existing query and resubmits', async () => {
    const mockFetch = vi.spyOn(globalThis, 'fetch').mockResolvedValue({
      ok: true,
      json: async () => ({ intent: null, listings: [], scored: [], explained: [] }),
    } as unknown as Response)

    render(<RecommendFlow />)

    const queryInput = screen.getByLabelText('Describe what you want') as HTMLTextAreaElement
    await userEvent.type(queryInput, 'near good transit')

    await userEvent.click(screen.getByText(/Quieter/))

    expect(mockFetch).toHaveBeenCalledTimes(1)
    const requestBody = JSON.parse((mockFetch.mock.calls[0][1] as any).body)
    expect(requestBody.userQuery).toBe('near good transit Show me quieter neighborhoods')
    expect(typeof requestBody.threadId).toBe('string')
  })
})