import React from 'react'
import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import '@testing-library/jest-dom'
import { vi } from 'vitest'
import ListingCard from '../../src/app/components/listing-card'

describe('Listing click tracking', () => {
  test('sends track-click request and uses realtor affiliate URL', async () => {
    process.env.NEXT_PUBLIC_REALTOR_AFFILIATE_ID = 'test-id'
    const fetchSpy = vi.spyOn(global, 'fetch').mockResolvedValue({ ok: true } as unknown as Response)

    const listing = {
      id: 'l1',
      address: '123 Main St',
      source_url: 'https://www.realtor.com/realestateandhomes-detail/123',
      source: 'realtor.com',
      photo_url: null,
    }

    render(<ListingCard listing={listing} score={90} explanation="Great find" />)

    const link = screen.getByRole('link', { name: /View listing/i })
    expect(link).toHaveAttribute('href', 'https://www.realtor.com/realestateandhomes-detail/123?ref=test-id')

    await userEvent.click(link)

    await waitFor(() => {
      expect(fetchSpy).toHaveBeenCalledWith('/api/track-click', expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      }))
    })

    const call = fetchSpy.mock.calls.find(([url]) => url === '/api/track-click')
    expect(call).toBeDefined()

    const options = call?.[1] as Record<string, unknown>
    expect(options).toBeDefined()

    const body = JSON.parse(options.body as string)
    expect(body).toEqual({
      listingId: 'l1',
      source: 'realtor.com',
      sourceUrl: listing.source_url,
      affiliateNetwork: 'realtor',
    })

    fetchSpy.mockRestore()
  })
})
