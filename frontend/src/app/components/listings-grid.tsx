import React from 'react'
import ListingCard from './listing-card'

export default function ListingsGrid({ items }: { items: any[] }) {
  if (!items || items.length === 0) return <div>No listings found</div>
  return (
    <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
      {items.map((it) => (
        <ListingCard key={it.id} listing={it} score={it.score} explanation={it.explanation || ''} />
      ))}
    </div>
  )
}
