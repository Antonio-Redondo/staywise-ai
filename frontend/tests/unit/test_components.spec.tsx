import React from 'react'
import { render, screen } from '@testing-library/react'
import '@testing-library/jest-dom'
import IntentCard from '../../src/app/components/intent-card'
import NeighborhoodMap from '../../src/app/components/neighborhood-map'
import ListingsGrid from '../../src/app/components/listings-grid'
import ListingCard from '../../src/app/components/listing-card'

describe('UI components', () => {
  test('IntentCard renders tags and budgets', () => {
    render(<IntentCard intent={{ lifestyle_tags: ['walkable'], budget_min: 500000, budget_max: 800000 }} />)
    expect(screen.getByText(/walkable/)).toBeInTheDocument()
    expect(screen.getByText(/\$500,000/)).toBeInTheDocument()
  })

  test('NeighborhoodMap lists neighborhoods', () => {
    render(<NeighborhoodMap neighborhoods={[{ name: 'SoMa', score: 0.8 }]} />)
    expect(screen.getByText(/SoMa/)).toBeInTheDocument()
  })

  test('ListingsGrid renders items', () => {
    const items = [
      { id: '1', address: '123', source: 'src', photo_url: null, score: 75, explanation: 'Nice' },
    ]
    render(<ListingsGrid items={items} />)
    expect(screen.getByText('123')).toBeInTheDocument()
  })

  test('ListingCard uses placeholder when image missing', () => {
    const listing = { id: '1', address: '123', source_url: 'https://x/1', source: 'src', photo_url: null }
    render(<ListingCard listing={listing} score={80} explanation={'ok'} />)
    expect(screen.getByText('123')).toBeInTheDocument()
  })
})
