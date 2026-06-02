import React from 'react'

export default function NeighborhoodMap({ neighborhoods }: { neighborhoods?: any[] }) {
  // Simple fallback: render neighborhood names as list. Mapbox integration added later.
  if (!neighborhoods || neighborhoods.length === 0) return <div>No neighborhoods</div>
  return (
    <ul>
      {neighborhoods.map((n) => (
        <li key={n.name}>{n.name} — score: {n.score}</li>
      ))}
    </ul>
  )
}
