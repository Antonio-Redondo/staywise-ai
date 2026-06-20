import React from 'react'
import ListingCard from './listing-card'

export default function ListingsGrid({ items }: { items: any[] }) {
  if (!items || items.length === 0) {
    return <div className="empty">No listings matched yet — try broadening your search.</div>
  }
  return (
    <div className="listings-grid">
      {items.map((it) => (
        <ListingCard key={it.id} listing={it} score={it.score} explanation={it.explanation || ''} />
      ))}
    </div>
  )
}
